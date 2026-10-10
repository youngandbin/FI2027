"""View vector q and view-uncertainty Omega from repeated LLM draws."""
import numpy as np

VAR_FLOOR = 1e-10  # decimal daily-return variance floor (sigma >= 1e-5, i.e. 0.001%)


def view_stats(draws_by_ticker: dict[str, np.ndarray], tickers: list[str], n: int | None = None,
               rng: np.random.Generator | None = None) -> tuple[np.ndarray, np.ndarray]:
    """
    q_i = mean of draws, s2_i = unbiased (N-1) variance of draws, in decimal daily returns.
    With n, a random subset of n draws is used (N-sensitivity); missing tickers get q=0, s2=NaN.
    """
    q = np.zeros(len(tickers))
    s2 = np.full(len(tickers), np.nan)
    for k, t in enumerate(tickers):
        d = draws_by_ticker.get(t)
        if d is None or len(d) == 0:
            continue
        if n is not None and n < len(d):
            d = rng.choice(d, size=n, replace=False)
        q[k] = d.mean()
        s2[k] = d.var(ddof=1) if len(d) > 1 else np.nan
    return q, s2


def make_omega(s2: np.ndarray, kind: str, sigma_diag: np.ndarray | None = None, tau: float | None = None,
               calib=None, rng: np.random.Generator | None = None) -> np.ndarray:
    """
    Diagonal Omega (P = I) under one of:
      empirical     Omega_ii = s2_i                      (EAAI mapping)
      constant      Omega_ii = mean_i s2_i               (level only; tau then sets the scale)
      shuffle       Omega_ii = s2_perm(i)                (same values, random assignment across assets)
      he_litterman  Omega_ii = tau * Sigma_ii            (He & Litterman 1999 convention)
      calibrated    Omega_ii = calib(s2_i)               (past-fit isotonic map s2 -> realized squared error)
      linear        Omega_ii = calib(s2_i)               (past-fit a + b*s2 for the view error net of return noise)
    Missing s2 (NaN) are replaced by the cross-sectional mean before mapping.
    """
    s2 = np.where(np.isnan(s2), np.nanmean(s2), s2)
    if kind == "empirical":
        om = s2
    elif kind == "constant":
        om = np.full_like(s2, s2.mean())
    elif kind == "shuffle":
        om = rng.permutation(s2)
    elif kind == "he_litterman":
        om = tau * sigma_diag
    elif kind in ("calibrated", "linear"):
        om = calib(s2)
    else:
        raise ValueError(kind)
    return np.diag(np.maximum(om, VAR_FLOOR))
