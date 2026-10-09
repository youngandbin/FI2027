"""
Collect repeated LLM return forecasts (views) from a local vLLM OpenAI-compatible server.

For each two-week period and each stock in the point-in-time universe, the model is asked N times
(one request with n=N completions) for the average daily return (%) over the next two weeks.
Output: data/views/{market}/{model_tag}/{prompt}/{start}_{end}.json
  {uid: {"draws": [...], "n_fail": int, "ticker": ..., "company_name": ...}}

Prompts:
  A  EAAI prompt 4 adapted: last 10 trading days of stock and market returns (%), name, ticker/ISIN, country, index
  B  A + 60-day summary (mean, volatility, max drawdown, return vs market, market-cap rank)
"""
import argparse
import asyncio
import json
import os
import re
import time

import numpy as np
import pandas as pd
from openai import AsyncOpenAI

from blx import engine as E, wrds
from paths import VIEWS_DIR

SCHEMA = {"type": "object", "properties": {"expected_return": {"type": "number"}}, "required": ["expected_return"],
          "additionalProperties": False}
NUM = re.compile(r"-?\d+(?:\.\d+)?")


def system_prompt(asof: str, market: str, prompt: str) -> str:
    _, country, index, currency, _ = wrds.MARKETS[market]
    s = (f"You are providing analysis on {asof}. Predict the average daily return (in percent) of a stock over the next "
         f"two weeks (10 trading days) from its recent performance. The stock is a constituent of the {index} index ({country}); "
         f"prices are in {currency}.\n\n# Inputs\n"
         "- Company Information: name, identifier, country and index.\n"
         "- Daily Returns: the stock's daily returns (%) over the past two weeks, oldest first.\n"
         "- Market Returns: the cap-weighted daily returns (%) of the index's largest constituents over the same days.\n")
    if prompt == "B":
        s += ("- 60-Day Summary: the stock's mean daily return, daily volatility, maximum drawdown (all %), its 60-day return "
              "minus the market's, and its market-cap rank within the universe.\n")
    s += ("\n# Steps\n1. Assess the recent trend and volatility of the stock relative to the market.\n"
          "2. Consider mean reversion and momentum over a two-week horizon.\n"
          "3. Estimate the average daily return over the next two weeks.\n\n"
          "# Output\nReturn only a JSON object: {\"expected_return\": <number>} where the number is the predicted average daily "
          "return in percent (e.g. 0.12 means +0.12% per day). No other text.")
    return s


def user_prompt(uid, names, stock_ret, mkt_ret, prompt, summary=None) -> str:
    nm = names.loc[uid]
    ident = nm["ticker"] if isinstance(nm["ticker"], str) else (nm["isin"] if isinstance(nm["isin"], str) else uid)
    fmt = lambda a: "[" + ", ".join(f"{x * 100:.2f}" for x in a) + "]"
    u = (f"# Company Information\n- Name: {nm['company_name']}\n- Identifier: {ident}\n\n"
         f"# Daily Returns (%)\n{fmt(stock_ret)}\n\n# Market Returns (%)\n{fmt(mkt_ret)}\n")
    if prompt == "B" and summary is not None:
        u += ("\n# 60-Day Summary\n- Mean daily return: %.3f%%\n- Daily volatility: %.2f%%\n- Max drawdown: %.1f%%\n"
              "- 60-day return minus market: %.1f%%\n- Market-cap rank: %d of %d\n" % summary)
    return u


def parse(text: str):
    try:
        return float(json.loads(text)["expected_return"])
    except Exception:
        m = NUM.search(text or "")
        return float(m.group()) if m else None


async def ask(client, model, sys_p, usr_p, n, temperature, sem, max_tokens):
    async with sem:
        for attempt in range(3):
            try:
                r = await client.chat.completions.create(
                    model=model, n=n, temperature=temperature, max_tokens=max_tokens,
                    messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": usr_p}],
                    response_format={"type": "json_schema", "json_schema": {"name": "view", "schema": SCHEMA}})
                vals = [parse(c.message.content) for c in r.choices]
                return [v for v in vals if v is not None], sum(v is None for v in vals)
            except Exception as e:
                err = e
                await asyncio.sleep(2 * (attempt + 1))
        print(f"request failed: {err}")
        return [], n


async def run(args):
    md = wrds.load_market(args.market, start="2023-01-01")
    eng = E.Engine(md, top_n=args.top_n)
    periods = E.rebalance_periods(args.start, args.end)
    client = AsyncOpenAI(base_url=args.base_url, api_key=os.environ.get("VLLM_API_KEY", "EMPTY"))
    sem = asyncio.Semaphore(args.concurrency)
    out_dir = VIEWS_DIR / args.market / args.model_tag / args.prompt
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for ps, pe in periods:
        f = out_dir / f"{ps}_{pe}.json"
        if f.exists() and not args.overwrite:
            continue
        tick = eng.universe((ps, pe))
        asof = md._last_date(pd.Timestamp(pe))
        hist = md.returns.loc[:asof, tick].tail(10).fillna(0.0)
        mkt = wrds.cap_weighted_market_return(md, tick, hist.index)
        summ = {}
        if args.prompt == "B":
            h60 = md.returns.loc[:asof, tick].tail(60).fillna(0.0)
            m60 = wrds.cap_weighted_market_return(md, tick, h60.index)
            eq = (1 + h60).cumprod(); dd = (eq / eq.cummax() - 1).min()
            caps = md.mktcap.loc[asof, tick].rank(ascending=False)
            for t in tick:
                summ[t] = (h60[t].mean() * 100, h60[t].std() * 100, dd[t] * 100,
                           ((1 + h60[t]).prod() - (1 + m60).prod()) * 100, int(caps[t]), len(tick))
        sys_p = system_prompt(str(asof.date()), args.market, args.prompt)
        tasks = [ask(client, args.model, sys_p, user_prompt(t, md.names, hist[t].values, mkt.values, args.prompt, summ.get(t)),
                     args.n, args.temperature, sem, args.max_tokens) for t in tick]
        res = await asyncio.gather(*tasks)
        payload = {t: {"draws": d, "n_fail": nf, "ticker": md.names.loc[t, "ticker"], "company_name": md.names.loc[t, "company_name"]}
                   for t, (d, nf) in zip(tick, res)}
        f.write_text(json.dumps(payload, ensure_ascii=False))
        nd = np.mean([len(v["draws"]) for v in payload.values()]); nf = sum(v["n_fail"] for v in payload.values())
        print(f"{args.market} {args.model_tag} {args.prompt} {ps}..{pe}: {len(tick)} stocks, mean draws {nd:.1f}, failures {nf}, {time.time() - t0:.0f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", default="US", choices=list(wrds.MARKETS))
    ap.add_argument("--model", required=True, help="model name as served by vLLM")
    ap.add_argument("--model_tag", required=True, help="short name for the output folder")
    ap.add_argument("--base_url", default="http://localhost:8001/v1")
    ap.add_argument("--prompt", default="A", choices=["A", "B"])
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max_tokens", type=int, default=64)
    ap.add_argument("--start", default="2024-09-01")
    ap.add_argument("--end", default="2025-12-31")
    ap.add_argument("--top_n", type=int, default=50)
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--overwrite", action="store_true")
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
