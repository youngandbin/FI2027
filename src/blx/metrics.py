"""Performance metrics and block-bootstrap inference for dependent daily returns."""
import numpy as np
import pandas as pd

ANN = 252


def performance(net: pd.Series, rf: pd.Series) -> dict:
    ex = net - rf.reindex(net.index).ffill().fillna(0.0)
    n = len(net)
    equity = (1 + net).cumprod()
    cagr = equity.iloc[-1] ** (ANN / n) - 1 if n > 0 else np.nan
    std = net.std(ddof=1)
    sharpe_ann = ex.mean() / std * np.sqrt(ANN) if std > 0 else np.nan
    dd = equity / equity.cummax() - 1
    var95 = net.quantile(0.05)
    return {
        "n_days": n, "CAGR": cagr, "mean_ann": net.mean() * ANN, "std_ann": std * np.sqrt(ANN),
        "Sharpe_ann": sharpe_ann, "MDD": dd.min(), "VaR95": var95, "CVaR95": net[net <= var95].mean(),
    }


def sharpe_of(x: np.ndarray) -> float:
    s = x.std(ddof=1)
    return x.mean() / s * np.sqrt(ANN) if s > 0 else np.nan


def circular_block_indices(n: int, block: int, rng: np.random.Generator) -> np.ndarray:
    starts = rng.integers(0, n, size=int(np.ceil(n / block)))
    idx = np.concatenate([(s + np.arange(block)) % n for s in starts])[:n]
    return idx


def bootstrap_sharpe_diff(a: pd.Series, b: pd.Series, rf: pd.Series, n_boot: int = 2000, block: int = 10,
                          seed: int = 0) -> dict:
    """
    Paired circular block bootstrap of Sharpe(a) - Sharpe(b) on excess returns, same dates resampled
    for both series. Returns the point estimate, 95% percentile CI and a two-sided bootstrap p-value.
    """
    idx = a.index.intersection(b.index)
    rfv = rf.reindex(idx).ffill().fillna(0.0).values
    xa, xb = a.loc[idx].values - rfv, b.loc[idx].values - rfv
    rng = np.random.default_rng(seed)
    point = sharpe_of(xa) - sharpe_of(xb)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        ii = circular_block_indices(len(idx), block, rng)
        diffs[i] = sharpe_of(xa[ii]) - sharpe_of(xb[ii])
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    p = 2 * min((diffs <= 0).mean(), (diffs >= 0).mean())
    return {"diff": point, "ci_lo": lo, "ci_hi": hi, "p_value": min(p, 1.0)}
