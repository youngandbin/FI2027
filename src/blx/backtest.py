"""Rebalancing loop, long-only mean-variance step and portfolio return construction."""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from . import bl, views as V

LAMBDA = 0.1  # objective: w'Sigma w - LAMBDA * w'mu (as in the EAAI code)


def mvo_long_only(mu: np.ndarray, sigma: np.ndarray, lam: float = LAMBDA) -> np.ndarray:
    n = len(mu)
    w0 = np.ones(n) / n
    res = minimize(lambda w: w @ sigma @ w - lam * w @ mu, w0, method="SLSQP",
                   jac=lambda w: 2 * sigma @ w - lam * mu,
                   bounds=[(0.0, 1.0)] * n, constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1.0}],
                   options={"maxiter": 500, "ftol": 1e-12})
    w = np.clip(res.x, 0, None)
    return w / w.sum()


@dataclass
class Config:
    """One backtest configuration. strategy in {bl, prior, ew, cap, mvo_hist, llm_mvo, llm_topk}."""
    strategy: str = "bl"
    omega: str = "empirical"           # see views.make_omega
    tau: float = 0.05
    sigma_window: int = 126            # trading days of trailing returns for Sigma
    sigma_method: str = "ledoit_wolf"
    delta: float | None = 2.5          # None -> estimated from trailing 252 days
    n_draws: int | None = None         # subsample of LLM draws (N sensitivity)
    topk: int = 10
    seed: int = 0
    calib: object = field(default=None, repr=False)   # callable s2 -> Omega_ii for omega="calibrated"
    label: str = ""


class Market:
    """Data bundle shared across configurations."""

    def __init__(self, returns: pd.DataFrame, market_caps: pd.DataFrame, rf: pd.Series):
        self.returns, self.market_caps, self.rf = returns, market_caps, rf
        self.tickers = list(returns.columns)


def _period_views(views, period, tickers, cfg, rng):
    if views is None or period not in views:
        return None, None
    return V.view_stats(views[period], tickers, n=cfg.n_draws, rng=rng)


def compute_weights(cfg: Config, mkt: Market, views: dict | None, periods: list[tuple[str, str]]) -> pd.DataFrame:
    """Weights decided at the end of each period (using information up to period end)."""
    rng = np.random.default_rng(cfg.seed)
    tick = mkt.tickers
    rows = {}
    for (ps, pe) in periods:
        asof = pd.Timestamp(pe)
        hist = mkt.returns.loc[:asof, tick].tail(cfg.sigma_window)
        if cfg.strategy == "ew":
            rows[ps] = np.ones(len(tick)) / len(tick)
            continue
        if cfg.strategy == "cap":
            rows[ps] = bl.market_weights(mkt.market_caps, asof, tick)
            continue
        sigma = bl.sigma_estimate(hist, cfg.sigma_method)
        if cfg.strategy == "mvo_hist":
            rows[ps] = mvo_long_only(hist.mean().values, sigma)
            continue
        w_m = bl.market_weights(mkt.market_caps, asof, tick)
        delta = bl.risk_aversion(mkt.returns, mkt.market_caps, mkt.rf, asof, tick, fixed=cfg.delta)
        pi = bl.equilibrium(sigma, w_m, delta)
        if cfg.strategy == "prior":
            rows[ps] = mvo_long_only(pi, sigma)
            continue
        q, s2 = _period_views(views, (ps, pe), tick, cfg, rng)
        if q is None:
            raise KeyError(f"no views for period {ps}..{pe}")
        if cfg.strategy == "llm_mvo":
            rows[ps] = mvo_long_only(q, sigma)
            continue
        if cfg.strategy == "llm_topk":
            w = np.zeros(len(tick)); w[np.argsort(-q)[:cfg.topk]] = 1.0 / cfg.topk
            rows[ps] = w
            continue
        omega = V.make_omega(s2, cfg.omega, sigma_diag=np.diag(sigma), tau=cfg.tau, calib=cfg.calib, rng=rng)
        mu = bl.posterior_mean(pi, sigma, cfg.tau, q, omega)
        rows[ps] = mvo_long_only(mu, sigma)
    return pd.DataFrame.from_dict(rows, orient="index", columns=tick)


def portfolio_returns(weights: pd.DataFrame, mkt: Market, periods: list[tuple[str, str]], psi: float = 0.001) -> pd.DataFrame:
    """
    Weights decided at period i are held over period i+1 (as in the EAAI code). Daily gross return
    = w . r; weights drift within the holding period; at each rebalance the one-way turnover
    against the drifted weights is charged at rate psi on the first holding day.
    Returns a DataFrame with gross, cost, net columns indexed by date.
    """
    tick = list(weights.columns)
    out = []
    prev_drift = None
    starts = [ps for ps, _ in periods]
    for i in range(len(periods) - 1):
        decided = starts[i]
        hold_start, hold_end = periods[i + 1]
        if decided not in weights.index:
            continue
        w = weights.loc[decided].values
        r = mkt.returns.loc[hold_start:hold_end, tick]
        turnover = np.abs(w - prev_drift).sum() if prev_drift is not None else np.abs(w).sum()
        for k, (d, row) in enumerate(r.iterrows()):
            rv = np.nan_to_num(row.values)
            gross = float(w @ rv)
            cost = psi * turnover if k == 0 else 0.0
            out.append((d, gross, cost, gross - cost))
            w = w * (1 + rv); w = w / w.sum()
        prev_drift = w
    return pd.DataFrame(out, columns=["date", "gross", "cost", "net"]).set_index("date")
