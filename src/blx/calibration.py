"""Is repeated-sampling dispersion informative about realized forecast error?"""
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.isotonic import IsotonicRegression

from . import views as V


def forecast_pairs(views: dict, returns: pd.DataFrame, periods: list[tuple[str, str]],
                   n_draws: int | None = None, seed: int = 0) -> pd.DataFrame:
    """
    One row per (decision period, ticker): q, s2 from the draws made at the end of period i, and the
    realized average daily return over period i+1 (the quantity the prompt asks for).
    """
    rng = np.random.default_rng(seed)
    tick = list(returns.columns)
    rows = []
    for i in range(len(periods) - 1):
        per = periods[i]
        if per not in views:
            continue
        q, s2 = V.view_stats(views[per], tick, n=n_draws, rng=rng)
        hs, he = periods[i + 1]
        realized = returns.loc[hs:he, tick].mean().values
        for k, t in enumerate(tick):
            rows.append((per[0], t, q[k], s2[k], realized[k]))
    df = pd.DataFrame(rows, columns=["period", "ticker", "q", "s2", "realized"]).dropna()
    df["err"] = df["q"] - df["realized"]
    df["sq_err"] = df["err"] ** 2
    df["z"] = df["err"] / np.sqrt(df["s2"].clip(lower=V.VAR_FLOOR))
    return df


def calibration_metrics(df: pd.DataFrame) -> dict:
    """
    Shape: Spearman rank correlation between s2 and squared error (is larger dispersion -> larger error?),
    and the same within each period (cross-sectional, averaged).
    Level: coverage of q +/- 1.96 sigma, PIT uniformity (KS statistic vs U(0,1)), Gaussian CRPS.
    """
    rho_all = stats.spearmanr(df["s2"], df["sq_err"]).statistic
    by_period = df.groupby("period").apply(
        lambda g: stats.spearmanr(g["s2"], g["sq_err"]).statistic if len(g) > 5 else np.nan, include_groups=False)
    z = df["z"].values
    pit = stats.norm.cdf(z)
    ks = stats.kstest(pit, "uniform").statistic
    cover95 = float((np.abs(z) <= 1.96).mean())
    sig = np.sqrt(df["s2"].clip(lower=V.VAR_FLOOR).values)
    crps = float(np.mean(sig * (z * (2 * stats.norm.cdf(z) - 1) + 2 * stats.norm.pdf(z) - 1 / np.sqrt(np.pi))))
    return {
        "n_pairs": len(df), "spearman_s2_sqerr": rho_all, "spearman_within_period_mean": by_period.mean(),
        "spearman_within_period_frac_pos": float((by_period > 0).mean()),
        "coverage95": cover95, "pit_ks": ks, "crps_gauss": crps,
        "rmse": float(np.sqrt(df["sq_err"].mean())), "mean_s2": float(df["s2"].mean()),
        "mean_sq_err": float(df["sq_err"].mean()),
    }


def fit_calibration_map(df_valid: pd.DataFrame, min_bins: int = 5):
    """
    Monotone map s2 -> E[sq_err | s2] fitted on validation pairs by isotonic regression on log s2.
    Changes the SHAPE of Omega (tau sets the level). Returns a callable on arrays of s2.
    """
    x = np.log(df_valid["s2"].clip(lower=V.VAR_FLOOR).values)
    y = df_valid["sq_err"].values
    iso = IsotonicRegression(increasing=True, out_of_bounds="clip").fit(x, y)

    def f(s2):
        return np.maximum(iso.predict(np.log(np.clip(s2, V.VAR_FLOOR, None))), V.VAR_FLOOR)

    f.n_unique_levels = int(len(np.unique(iso.predict(x))))
    return f
