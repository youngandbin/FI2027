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
    and the same within each period (cross-sectional, averaged). When the pair table carries the trailing
    variance vol2 and the holding-period noise variance (Engine.forecast_pairs), also the volatility-controlled
    versions: Spearman of s2/vol2 vs sq_err/vol2, and the partial rank correlation given vol2.
    Level: coverage of q +/- z*sigma, PIT uniformity (KS statistic vs U(0,1)), Gaussian CRPS, using the view
    variance alone (s2) and the predictive variance s2 + noise (realized return = mu + noise, design doc 6.0).
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
    out = {
        "n_pairs": len(df), "spearman_s2_sqerr": rho_all, "spearman_within_period_mean": by_period.mean(),
        "spearman_within_period_frac_pos": float((by_period > 0).mean()),
        "coverage95": cover95, "pit_ks": ks, "crps_gauss": crps,
        "rmse": float(np.sqrt(df["sq_err"].mean())), "mean_s2": float(df["s2"].mean()),
        "mean_sq_err": float(df["sq_err"].mean()),
    }
    if {"vol2", "noise"}.issubset(df.columns):
        d = df[df["vol2"] > 0]
        out["spearman_volstd"] = stats.spearmanr(d["s2"] / d["vol2"], d["sq_err"] / d["vol2"]).statistic
        r = d[["s2", "sq_err", "vol2"]].rank()
        res = lambda y, x: y - np.polyval(np.polyfit(x, y, 1), x)
        out["spearman_partial_vol"] = float(np.corrcoef(res(r["s2"], r["vol2"]), res(r["sq_err"], r["vol2"]))[0, 1])
        wp = d.groupby("period").apply(
            lambda g: stats.spearmanr(g["s2"] / g["vol2"], g["sq_err"] / g["vol2"]).statistic if len(g) > 5 else np.nan,
            include_groups=False).dropna()
        out["spearman_volstd_within_mean"] = float(wp.mean())
        out["spearman_volstd_within_frac_pos"] = float((wp > 0).mean())
        out["spearman_volstd_within_t"] = float(wp.mean() / wp.std(ddof=1) * np.sqrt(len(wp)))
        out["spearman_vol_sqerr"] = stats.spearmanr(d["vol2"], d["sq_err"]).statistic
        out["spearman_vol_s2"] = stats.spearmanr(d["vol2"], d["s2"]).statistic
        zp = d["err"].values / np.sqrt(d["s2"].clip(lower=V.VAR_FLOOR).values + d["noise"].values)
        zn = d["err"].values / np.sqrt(d["noise"].values)
        for lv, zc in ((50, 0.674), (80, 1.282), (95, 1.96)):
            out[f"coverage{lv}_pred"] = float((np.abs(zp) <= zc).mean())
            out[f"coverage{lv}_noise_only"] = float((np.abs(zn) <= zc).mean())
        out["pit_ks_pred"] = stats.kstest(stats.norm.cdf(zp), "uniform").statistic
        out["mean_noise"] = float(d["noise"].mean())
        out["view_err_var_net"] = float((d["sq_err"] - d["noise"]).mean())   # E[(q - mu)^2] estimate
    return out


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


def fit_linear_map(df_valid: pd.DataFrame):
    """
    Omega_ii = a + b * s2_i, fitted by OLS of the view error net of return noise, (q - r)^2 - noise, on s2
    over past pairs (design doc 6.3). b is constrained >= 0 (refit as a constant when OLS gives b < 0).
    """
    y = (df_valid["sq_err"] - df_valid["noise"]).values
    x = df_valid["s2"].values
    b, a = np.polyfit(x, y, 1)
    if b < 0:
        b, a = 0.0, float(y.mean())

    def f(s2):
        return np.maximum(a + b * np.asarray(s2), V.VAR_FLOOR)

    f.a, f.b = float(a), float(b)
    return f
