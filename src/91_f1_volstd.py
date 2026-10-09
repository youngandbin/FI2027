"""F1 check: volatility-standardized dispersion-error rank correlation and noise-adjusted 95% coverage (design §6.0, §8a)."""
import os, sys
os.environ["OMP_NUM_THREADS"] = "1"
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import numpy as np, pandas as pd
from scipy.stats import spearmanr, norm
from blx.wrds import load_market

md = load_market("US", "2023-06-01")
p = pd.read_csv(str(__import__("pathlib").Path(__file__).resolve().parents[1] / "results/US/gptoss20b_A/pairs.csv"), dtype={"ticker": str})
p["start"] = pd.to_datetime(p["period"])
p["asof"] = p["start"] + pd.Timedelta(days=13)
p["hs"] = p["start"] + pd.Timedelta(days=14); p["he"] = p["start"] + pd.Timedelta(days=27)
vol, nday = [], []
for (a, hs, he), g in p.groupby(["asof", "hs", "he"]):
    r = md.returns.loc[:a, g["ticker"]].tail(126)
    vol.append(pd.Series(r.std().values, index=g.index))
    n = len(md.returns.loc[hs:he].index)
    nday.append(pd.Series(n, index=g.index))
p["vol"] = pd.concat(vol); p["nday"] = pd.concat(nday)
p["noise"] = p["vol"]**2 / p["nday"]

def rk(x): return x.rank()
raw = spearmanr(p.s2, p.sq_err)[0]
std = spearmanr(p.s2 / p.vol**2, p.sq_err / p.vol**2)[0]
# partial Spearman controlling vol
R = p[["s2", "sq_err", "vol"]].rank()
def resid(y, x): b = np.polyfit(x, y, 1); return y - np.polyval(b, x)
part = np.corrcoef(resid(R.s2, R.vol), resid(R.sq_err, R.vol))[0, 1]
vol_err = spearmanr(p.vol, p.sq_err)[0]; vol_s2 = spearmanr(p.vol, p.s2)[0]
# within-period vol-standardized
wp = p.groupby("period").apply(lambda g: spearmanr(g.s2 / g.vol**2, g.sq_err / g.vol**2)[0])
# He-Litterman comparator: does vol^2 alone predict sq_err better than s2?
cov_raw = (np.abs(p.err) <= 1.96 * np.sqrt(p.s2)).mean()
cov_noise = (np.abs(p.err) <= 1.96 * np.sqrt(p.s2 + p.noise)).mean()
cov_noise_only = (np.abs(p.err) <= 1.96 * np.sqrt(p.noise)).mean()
print(f"n={len(p)} periods={p.period.nunique()}")
print(f"Spearman(s2, sq_err) raw            {raw:.3f}")
print(f"Spearman vol-standardized           {std:.3f}")
print(f"partial Spearman | vol              {part:.3f}")
print(f"within-period vol-std mean {wp.mean():.3f}, frac>0 {(wp>0).mean():.2f}, t={wp.mean()/wp.std()*np.sqrt(len(wp)):.2f}")
print(f"Spearman(vol, sq_err) {vol_err:.3f}   Spearman(vol, s2) {vol_s2:.3f}")
print(f"coverage95: s2 only {cov_raw:.3f}  s2+noise {cov_noise:.3f}  noise only {cov_noise_only:.3f}")
print(f"mean s2 {p.s2.mean():.2e}  mean noise {p.noise.mean():.2e}  mean sq_err {p.sq_err.mean():.2e}")
# outliers
print("max |q|", p.q.abs().max(), " q quantiles", p.q.quantile([.01,.5,.99]).round(5).tolist())
