"""
WRDS market data: CRSP (US S&P 500) and Compustat Global (KOSPI 200, Nikkei 225, DAX) with
point-in-time index membership. Files: data/wrds/{MARKET}_daily.parquet, {MARKET}_members.parquet.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from paths import RF_DIR, WRDS_DIR

MARKETS = {
    # key: (file prefix, country, index name, currency, FRED risk-free series)
    "US": ("US_SP500", "United States", "S&P 500", "USD", "DTB3"),
    "KR": ("KR_KOSPI_200", "Korea", "KOSPI 200", "KRW", "IR3TIB01KRM156N"),
    "JP": ("JP_Nikkei_225", "Japan", "Nikkei 225", "JPY", "IR3TIB01JPM156N"),
    "DE": ("DE_DAX", "Germany", "DAX", "EUR", "IR3TIB01DEM156N"),
}


@dataclass
class MarketData:
    key: str
    returns: pd.DataFrame      # date x uid, total daily simple returns (NaN when not traded / not covered)
    mktcap: pd.DataFrame       # date x uid, local currency
    member: pd.DataFrame       # date x uid, bool: index member on that date
    names: pd.DataFrame        # uid -> ticker, company_name, isin, currency
    rf: pd.Series              # date -> daily simple risk-free rate

    def universe(self, asof: pd.Timestamp, top_n: int | None = 50) -> list[str]:
        """Point-in-time universe: index members at `asof`, ranked by market cap at `asof`."""
        asof = self._last_date(asof)
        mem = self.member.loc[asof]
        cap = self.mktcap.loc[asof]
        ok = mem[mem].index.intersection(cap.dropna().index)
        ranked = cap.loc[ok].sort_values(ascending=False)
        return list(ranked.index[:top_n] if top_n else ranked.index)

    def _last_date(self, asof: pd.Timestamp) -> pd.Timestamp:
        idx = self.returns.index
        pos = idx.searchsorted(asof, side="right") - 1
        if pos < 0:
            raise KeyError(f"no data on or before {asof.date()}")
        return idx[pos]


def _load_raw(key: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    prefix = MARKETS[key][0]
    d = pd.read_parquet(WRDS_DIR / f"{prefix}_daily.parquet")
    m = pd.read_parquet(WRDS_DIR / f"{prefix}_members.parquet")
    return d, m


def load_market(key: str, start: str = "2015-01-01") -> MarketData:
    d, _ = _load_raw(key)
    d = d[d["date"] >= pd.Timestamp(start)].copy()
    if key == "US":
        d["uid"] = d["permno"].astype(str)
        ret, cap = d["ret"].astype(float), d["mktcap"].astype(float) * 1e3   # CRSP mktcap is in thousands
        names = d.groupby("uid").agg(ticker=("ticker", "last"), company_name=("company_name", "last"))
        names["isin"] = None
    else:
        d["uid"] = d["gvkey"].astype(str) + "_" + d["iid"].astype(str)
        ret, cap = d["ret_local"].astype(float), d["mktcap_local"].astype(float)
        names = d.groupby("uid").agg(ticker=("ticker", "last"), company_name=("company_name", "last"), isin=("isin", "last"))
    names = names.astype(object).where(names.notna(), None)   # plain Python values (JSON-safe)
    names["currency"] = MARKETS[key][3]
    d["ret_"], d["cap_"] = ret.values, cap.values
    d["member_"] = (d["member_start"] <= d["date"]) & (d["date"] <= d["member_end"])
    # a security can appear under several membership spells on one date; keep the row that is a member if any
    d = d.sort_values(["date", "uid", "member_"]).drop_duplicates(["date", "uid"], keep="last")
    returns = d.pivot(index="date", columns="uid", values="ret_").sort_index()
    mktcap = d.pivot(index="date", columns="uid", values="cap_").sort_index()
    member = d.pivot(index="date", columns="uid", values="member_").astype("boolean").fillna(False).astype(bool).sort_index()
    rf = load_rf(MARKETS[key][4]).reindex(returns.index).ffill().bfill()
    return MarketData(key, returns, mktcap, member, names, rf)


def load_rf(series: str) -> pd.Series:
    """FRED series (annualized percent) -> daily simple rate. Daily (DTB3) or monthly (OECD 3M interbank)."""
    f = RF_DIR / f"{series}.csv"
    s = pd.read_csv(f, index_col=0, parse_dates=True).iloc[:, 0]
    s = pd.to_numeric(s, errors="coerce").dropna()
    return (s / 100.0 / 252.0).rename("rf")


def cap_weighted_market_return(md: MarketData, tickers: list[str], dates: pd.DatetimeIndex) -> pd.Series:
    r = md.returns.loc[dates, tickers]
    w = md.mktcap.loc[dates, tickers].shift(1).bfill().ffill()   # previous-day caps; first day uses its own caps
    w = w.div(w.sum(axis=1), axis=0)
    return (r * w).sum(axis=1)
