"""
Backtest engine with a point-in-time, per-period universe (WRDS data).

Timeline (as in the EAAI study): periods are two-week windows anchored on pandas '2W' Sundays.
At the end of period i the universe is the top-N index members by market cap, LLM draws made
with information up to the end of period i give (q, Omega), weights are decided, and they are
held over period i+1 (weights drift; the one-way turnover against the drifted weights is charged
at rate psi on the first holding day). A stock that leaves the universe is sold at the next rebalance.
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from . import bl, views as V
from .wrds import MarketData

LAMBDA = 0.1  # objective: w'Sigma w - LAMBDA * w'mu (EAAI convention)


def mvo_long_only(mu: np.ndarray, sigma: np.ndarray, lam: float = LAMBDA, wmax: float | None = None) -> np.ndarray:
    n = len(mu)
    w0 = np.ones(n) / n
    ub = 1.0 if wmax is None else max(wmax, 1.0 / n)
    res = minimize(lambda w: w @ sigma @ w - lam * w @ mu, w0, method="SLSQP",
                   jac=lambda w: 2 * sigma @ w - lam * mu,
                   bounds=[(0.0, ub)] * n, constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1.0}],
                   options={"maxiter": 500, "ftol": 1e-12})
    w = np.clip(res.x, 0, None)
    return w / w.sum()


def rebalance_periods(start: str, end: str) -> list[tuple[str, str]]:
    out = []
    for d in pd.date_range(start=start, end=end, freq="2W"):
        e = d + pd.DateOffset(weeks=2) - pd.Timedelta(days=1)
        out.append((d.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")))
    return out


@dataclass
class Config:
    """
    strategy: ew | cap | mvo_hist | prior | bl | llm_mvo | llm_topk | mom_bl | mom_topk | stat_bl
      bl       q, Omega from LLM draws (omega variant below)
      mom_bl   q = trailing mom_window mean return, Omega = constant (level = tau*mean(Sigma_ii))
      stat_bl  q = trailing sigma_window mean, Omega = Var(mean) = Sigma_ii / sigma_window
      llm_*    LLM q without BL: long-only MVO on q, or equal-weight top-k by q
      mom_topk equal-weight top-k by trailing mean return
    omega_level: raw  Omega as produced by make_omega
                 hl   rescaled so that its cross-sectional mean equals tau * mean(Sigma_ii), the He-Litterman
                      level; only the SHAPE across assets then differs between Omega variants
    wmax: per-asset weight cap for the optimizer (None = long-only, no cap)
    q_center: diagnostic; shift the LLM views so their cross-sectional mean equals that of the prior Pi
              (removes the common level bias of q and keeps only its cross-sectional ranking information)
    delta: fixed risk aversion, or None = trailing 252-day estimate E[r_m - rf] / Var(r_m)
    """
    strategy: str = "bl"
    omega: str = "empirical"
    tau: float = 0.05
    sigma_window: int = 126
    sigma_method: str = "ledoit_wolf"
    delta: float | None = 2.5
    n_draws: int | None = None
    topk: int = 10
    mom_window: int = 10
    seed: int = 0
    omega_level: str = "raw"
    wmax: float | None = None
    q_center: bool = False
    calib: object = field(default=None, repr=False)   # callable(s2)->Omega_ii, or dict period->callable
    label: str = ""


class Engine:
    def __init__(self, md: MarketData, top_n: int | None = 50):
        self.md, self.top_n = md, top_n
        self._univ = {}

    # ---- universe and data windows -------------------------------------------------------------
    def universe(self, period: tuple[str, str]) -> list[str]:
        if period not in self._univ:
            self._univ[period] = self.md.universe(pd.Timestamp(period[1]), self.top_n)
        return self._univ[period]

    def hist(self, period: tuple[str, str], tickers: list[str], window: int) -> pd.DataFrame:
        r = self.md.returns.loc[:pd.Timestamp(period[1]), tickers].tail(window)
        return r.fillna(0.0)

    def _delta(self, period, tickers, sigma, cfg):
        if cfg.delta is not None:
            return cfg.delta
        asof = pd.Timestamp(period[1])
        w = self._cap_weights(period, tickers)
        r = self.md.returns.loc[:asof, tickers].tail(252).fillna(0.0)
        rm = r.values @ w - self.md.rf.reindex(r.index).ffill().values
        return float(rm.mean() / rm.var(ddof=1))

    def _cap_weights(self, period, tickers):
        cap = self.md.mktcap.loc[self.md._last_date(pd.Timestamp(period[1])), tickers].values.astype(float)
        cap = np.nan_to_num(cap)
        return cap / cap.sum()

    # ---- one rebalance decision ----------------------------------------------------------------
    def decide(self, cfg: Config, period: tuple[str, str], views: dict | None, rng: np.random.Generator) -> pd.Series:
        tick = self.universe(period)
        n = len(tick)
        if cfg.strategy == "ew":
            return pd.Series(np.ones(n) / n, index=tick)
        if cfg.strategy == "cap":
            return pd.Series(self._cap_weights(period, tick), index=tick)
        hist = self.hist(period, tick, cfg.sigma_window)
        sigma = bl.sigma_estimate(hist, cfg.sigma_method)
        if cfg.strategy == "mvo_hist":
            return pd.Series(mvo_long_only(hist.mean().values, sigma, wmax=cfg.wmax), index=tick)
        if cfg.strategy == "mom_topk":
            mom = self.hist(period, tick, cfg.mom_window).mean().values
            w = np.zeros(n); w[np.argsort(-mom)[:cfg.topk]] = 1.0 / cfg.topk
            return pd.Series(w, index=tick)
        w_m = self._cap_weights(period, tick)
        delta = self._delta(period, tick, sigma, cfg)
        pi = bl.equilibrium(sigma, w_m, delta)
        if cfg.strategy == "prior":
            return pd.Series(mvo_long_only(pi, sigma, wmax=cfg.wmax), index=tick)
        if cfg.strategy == "mom_bl":
            q = self.hist(period, tick, cfg.mom_window).mean().values
            omega = np.diag(np.full(n, np.mean(np.diag(sigma))))
            return pd.Series(mvo_long_only(bl.posterior_mean(pi, sigma, cfg.tau, q, omega), sigma, wmax=cfg.wmax), index=tick)
        if cfg.strategy == "stat_bl":
            q = hist.mean().values
            omega = np.diag(np.maximum(np.diag(sigma) / cfg.sigma_window, V.VAR_FLOOR))
            return pd.Series(mvo_long_only(bl.posterior_mean(pi, sigma, cfg.tau, q, omega), sigma, wmax=cfg.wmax), index=tick)
        # LLM-based strategies
        if views is None or period not in views:
            raise KeyError(f"no views for {period}")
        q, s2 = V.view_stats(views[period], tick, n=cfg.n_draws, rng=rng)
        if cfg.q_center:
            q = q - q.mean() + pi.mean()
        if cfg.strategy == "llm_mvo":
            return pd.Series(mvo_long_only(q, sigma, wmax=cfg.wmax), index=tick)
        if cfg.strategy == "llm_topk":
            w = np.zeros(n); w[np.argsort(-q)[:cfg.topk]] = 1.0 / cfg.topk
            return pd.Series(w, index=tick)
        calib = cfg.calib.get(period) if isinstance(cfg.calib, dict) else cfg.calib
        omega_kind = cfg.omega if not (cfg.omega in ("calibrated", "linear") and calib is None) else "empirical"
        omega = V.make_omega(s2, omega_kind, sigma_diag=np.diag(sigma), tau=cfg.tau, calib=calib, rng=rng)
        if cfg.omega_level == "hl":
            omega = omega * (cfg.tau * np.mean(np.diag(sigma)) / np.mean(np.diag(omega)))
        mu = bl.posterior_mean(pi, sigma, cfg.tau, q, omega)
        return pd.Series(mvo_long_only(mu, sigma, wmax=cfg.wmax), index=tick)

    def weights(self, cfg: Config, views: dict | None, periods: list[tuple[str, str]]) -> dict:
        rng = np.random.default_rng(cfg.seed)
        return {p: self.decide(cfg, p, views, rng) for p in periods}

    # ---- holding-period returns ----------------------------------------------------------------
    def portfolio_returns(self, weights: dict, periods: list[tuple[str, str]], psi: float = 0.001) -> pd.DataFrame:
        out, prev = [], None   # prev: drifted weights (Series) at the end of the last holding period
        for i in range(len(periods) - 1):
            decided, (hs, he) = periods[i], periods[i + 1]
            if decided not in weights:
                continue
            w = weights[decided]
            r = self.md.returns.loc[hs:he, w.index].fillna(0.0)
            if prev is None:
                turnover = float(w.abs().sum())
            else:
                allidx = w.index.union(prev.index)
                turnover = float((w.reindex(allidx).fillna(0) - prev.reindex(allidx).fillna(0)).abs().sum())
            wv = w.values.copy()
            for k, (d, row) in enumerate(r.iterrows()):
                rv = row.values
                gross = float(wv @ rv)
                cost = psi * turnover if k == 0 else 0.0
                out.append((d, gross, cost, gross - cost))
                wv = wv * (1 + rv); wv = wv / wv.sum()
            prev = pd.Series(wv, index=w.index)
        return pd.DataFrame(out, columns=["date", "gross", "cost", "net"]).set_index("date")

    # ---- forecast/realization pairs for calibration ------------------------------------------
    def forecast_pairs(self, views: dict, periods: list[tuple[str, str]], n_draws=None, seed=0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        rows = []
        for i in range(len(periods) - 1):
            per = periods[i]
            if per not in views:
                continue
            tick = self.universe(per)
            q, s2 = V.view_stats(views[per], tick, n=n_draws, rng=rng)
            hs, he = periods[i + 1]
            hold = self.md.returns.loc[hs:he, tick]
            realized, nday = hold.mean().values, hold.notna().sum().values
            mom = self.hist(per, tick, 10).mean().values
            vol2 = self.hist(per, tick, 126).var(ddof=1).values
            for k, t in enumerate(tick):
                rows.append((per[0], t, q[k], s2[k], realized[k], mom[k], vol2[k], nday[k]))
        df = pd.DataFrame(rows, columns=["period", "ticker", "q", "s2", "realized", "mom10", "vol2", "nday"]).dropna(subset=["q", "realized"])
        # realized = mu + holding-period noise with variance ~ vol2 / nday (design doc 6.0)
        df["noise"] = df["vol2"] / df["nday"].clip(lower=1)
        df["err"] = df["q"] - df["realized"]
        df["sq_err"] = df["err"] ** 2
        df["z"] = df["err"] / np.sqrt(df["s2"].clip(lower=V.VAR_FLOOR))
        return df
