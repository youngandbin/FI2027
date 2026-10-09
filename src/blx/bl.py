"""Covariance, equilibrium prior and the Black-Litterman posterior (P = I)."""
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf


def sigma_estimate(window: pd.DataFrame, method: str = "ledoit_wolf") -> np.ndarray:
    x = window.values
    x = x[~np.isnan(x).any(axis=1)]
    if method == "sample":
        return np.cov(x.T)
    if method == "ledoit_wolf":
        return LedoitWolf().fit(x).covariance_
    raise ValueError(method)


def market_weights(market_caps: pd.DataFrame, asof: pd.Timestamp, tickers: list[str]) -> np.ndarray:
    """Cap weights from the last available market caps at or before `asof` (point in time)."""
    row = market_caps.loc[:asof].iloc[-1][tickers]
    w = row.values.astype(float)
    return w / w.sum()


def risk_aversion(returns: pd.DataFrame, market_caps: pd.DataFrame, rf: pd.Series, asof: pd.Timestamp,
                  tickers: list[str], window_days: int = 252, fixed: float | None = 2.5) -> float:
    """
    delta. Fixed (He & Litterman use 2.5) by default; otherwise the market price of risk
    E[r_m - rf] / Var(r_m) over the trailing window, using point-in-time cap weights at `asof`.
    """
    if fixed is not None:
        return fixed
    w = market_weights(market_caps, asof, tickers)
    r = returns.loc[:asof, tickers].tail(window_days)
    rm = (r.values @ w) - rf.reindex(r.index).ffill().values
    return float(rm.mean() / rm.var(ddof=1))


def equilibrium(sigma: np.ndarray, w_m: np.ndarray, delta: float) -> np.ndarray:
    return delta * sigma @ w_m


def posterior_mean(pi: np.ndarray, sigma: np.ndarray, tau: float, q: np.ndarray, omega: np.ndarray) -> np.ndarray:
    """mu = [(tau Sigma)^-1 + Omega^-1]^-1 [(tau Sigma)^-1 pi + Omega^-1 q], solved without explicit inverses."""
    ts = tau * sigma
    prec_prior = np.linalg.solve(ts, np.eye(len(pi)))
    prec_view = np.diag(1.0 / np.diag(omega))
    a = prec_prior + prec_view
    b = prec_prior @ pi + prec_view @ q
    return np.linalg.solve(a, b)
