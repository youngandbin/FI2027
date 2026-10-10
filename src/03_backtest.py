"""
Backtest one (market, model, prompt) view set with the corrected BL pipeline and walk-forward tau.

For every Omega variant, weights are computed for every tau on the grid over all periods once.
tau is then chosen per calendar quarter from the expanding window of earlier out-of-sample holding
periods (initial window = the first `burn_in` quarters); the selected-tau weight paths are spliced
and evaluated with transaction costs. The calibrated-Omega map is likewise fitted on earlier pairs only.

Specifications (label suffixes), all with the same walk-forward tau:
  (none)     EAAI mapping, Omega at its raw level
  _lv        Omega rescaled to the He-Litterman level tau*mean(Sigma_ii), so Omega variants differ only in shape
  _cap10     10% per-asset weight cap in the optimizer
  _lv_cap10  both
  _qc        diagnostic: views centred on the prior's cross-sectional mean (common bias of q removed)
  _d1.5 / _d3.5 / _dest   risk aversion delta = 1.5, 3.5, or the trailing 252-day estimate (default 2.5),
             on the raw and the _lv_cap10 specifications

Output: results/{market}/{model_tag}_{prompt}/ {performance.csv, omega_matrix.csv, tau_path.csv, delta_path.csv,
calibration.csv, n_sensitivity.csv, bootstrap.csv, pairs.csv, weights_*.csv, run_meta.json}
"""
import argparse
import json
import os
import subprocess
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from blx import calibration as C, engine as E, metrics as M, wrds
from paths import RESULTS_DIR, VIEWS_DIR

TAU_GRID = [float(x) for x in np.logspace(-3, 1, 13)]
OMEGAS = ["empirical", "constant", "shuffle", "he_litterman", "calibrated", "linear"]
SPECS = {"": {}, "_lv": dict(omega_level="hl"), "_cap10": dict(wmax=0.1), "_lv_cap10": dict(omega_level="hl", wmax=0.1)}
DELTAS = {"_d1.5": 1.5, "_d3.5": 3.5, "_dest": None}
DELTA_OMEGAS = ["empirical", "constant", "he_litterman", "linear"]
CAP_BASELINES = ["mvo_hist", "prior", "mom_bl", "stat_bl", "llm_mvo"]
BASELINES = ["ew", "cap", "mvo_hist", "prior", "mom_topk", "mom_bl", "stat_bl", "llm_mvo", "llm_topk"]
TAU_STRATS = {"mom_bl", "stat_bl"}
PSI_GRID = [0.0, 0.0005, 0.001, 0.0025]
N_GRID = [5, 10, 20]

_G = {}


def load_views(market, model_tag, prompt):
    d = VIEWS_DIR / market / model_tag / prompt
    views = {}
    for f in sorted(d.glob("*.json")):
        ps, pe = f.stem.split("_")
        raw = json.loads(f.read_text())
        views[(ps, pe)] = {k: np.asarray(v["draws"], dtype=float) / 100.0 for k, v in raw.items() if len(v["draws"]) > 1}
    if not views:
        raise FileNotFoundError(d)
    return views


def _init(market, model_tag, prompt, top_n, start, end):
    md = wrds.load_market(market, start="2023-01-01")
    _G["eng"] = E.Engine(md, top_n=top_n)
    _G["views"] = load_views(market, model_tag, prompt) if model_tag else None
    _G["periods"] = E.rebalance_periods(start, end)


def _job(cd):
    cfg = E.Config(**cd)
    eng, periods, views = _G["eng"], _G["periods"], _G["views"]
    if cfg.omega in ("calibrated", "linear") and cfg.strategy == "bl":
        if "calib" not in _G:
            pairs = eng.forecast_pairs(views, periods)
            _G["calib"] = {"calibrated": expanding_calib(pairs, periods, C.fit_calibration_map),
                           "linear": expanding_calib(pairs, periods, C.fit_linear_map)}
        cfg.calib = _G["calib"][cfg.omega]
    w = eng.weights(cfg, views, periods)
    return cd, w


def expanding_calib(pairs: pd.DataFrame, periods, fitter, min_pairs: int = 200) -> dict:
    """period -> calibration map fitted on pairs whose decision period is strictly earlier
    (their holding period ends by the decision date p[1], so no later realized return is used)."""
    out = {}
    for i, p in enumerate(periods):
        earlier = pairs[pairs["period"] < p[0]]
        out[p] = fitter(earlier) if len(earlier) >= min_pairs else None
    return out


def git_revision() -> str:
    try:
        root = str(RESULTS_DIR.parent)
        rev = subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", root, "status", "--porcelain", "--", "src"], capture_output=True, text=True).stdout.strip()
        return rev + ("-dirty" if dirty else "")
    except Exception:
        return "unknown"


def quarter_of(ps: str) -> str:
    t = pd.Timestamp(ps)
    return f"{t.year}Q{(t.month - 1) // 3 + 1}"


def walk_forward(eng, weights_by_tau: dict, periods, rf, burn_in_quarters: int, psi: float):
    """Pick tau per quarter from earlier holding-period Sharpe; return spliced weights and the tau path."""
    quarters = []
    for p in periods:
        q = quarter_of(p[0])
        if q not in quarters:
            quarters.append(q)
    nets = {tau: eng.portfolio_returns(w, periods, psi=psi)["net"] for tau, w in weights_by_tau.items()}
    chosen, path = {}, {}
    for qi, q in enumerate(quarters):
        if qi < burn_in_quarters:
            tau = None
        else:
            cutoff = pd.Timestamp(min(p[0] for p in periods if quarter_of(p[0]) == q))
            best, tau = -np.inf, TAU_GRID[0]
            for t_, net in nets.items():
                hist = net[net.index < cutoff]
                sh = M.performance(hist, rf)["Sharpe_ann"] if len(hist) > 20 else -np.inf
                if sh > best:
                    best, tau = sh, t_
        path[q] = tau
        for p in periods:
            if quarter_of(p[0]) == q and tau is not None:
                chosen[p] = weights_by_tau[tau][p]
    return chosen, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", default="US")
    ap.add_argument("--model_tag", default=None, help="omit to run baselines only")
    ap.add_argument("--prompt", default="A")
    ap.add_argument("--start", default="2024-09-01")
    ap.add_argument("--end", default="2025-12-31")
    ap.add_argument("--top_n", type=int, default=50)
    ap.add_argument("--burn_in", type=int, default=2, help="quarters used only for the first tau choice")
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--n_boot", type=int, default=2000)
    args = ap.parse_args()
    tag = f"{args.model_tag}_{args.prompt}" if args.model_tag else "baselines"
    out = RESULTS_DIR / args.market / tag
    out.mkdir(parents=True, exist_ok=True)
    _init(args.market, args.model_tag, args.prompt, args.top_n, args.start, args.end)
    eng, periods, views, rf = _G["eng"], _G["periods"], _G["views"], _G["eng"].md.rf

    t_start = time.time()
    jobs = []

    def add(strategy, label, **kw):
        if strategy in TAU_STRATS or strategy == "bl":
            jobs.extend(dict(strategy=strategy, tau=t, label=label, **kw) for t in TAU_GRID)
        else:
            jobs.append(dict(strategy=strategy, label=label, **kw))

    for s_ in BASELINES:
        if s_.startswith("llm") and views is None:
            continue
        add(s_, s_)
        if s_ in CAP_BASELINES:
            add(s_, f"{s_}_cap10", wmax=0.1)
    for dsuf, dval in DELTAS.items():
        for s_ in ("prior", "mom_bl", "stat_bl"):
            add(s_, f"{s_}{dsuf}", delta=dval)
        add("prior", f"prior_cap10{dsuf}", delta=dval, wmax=0.1)
    if views is not None:
        for suf, kw in SPECS.items():
            for om in OMEGAS:
                if om == "he_litterman" and "lv" in suf:
                    continue   # already at the He-Litterman level
                add("bl", f"bl_{om}{suf}", omega=om, **kw)
        for dsuf, dval in DELTAS.items():
            for om in DELTA_OMEGAS:
                add("bl", f"bl_{om}{dsuf}", omega=om, delta=dval)
                if om != "linear":
                    kw = SPECS["_cap10"] if om == "he_litterman" else SPECS["_lv_cap10"]
                    add("bl", f"bl_{om}{'_cap10' if om == 'he_litterman' else '_lv_cap10'}{dsuf}", omega=om, delta=dval, **kw)
        for om in ("empirical", "constant", "shuffle", "he_litterman"):
            add("bl", f"bl_{om}_qc", omega=om, q_center=True)
            if om == "he_litterman":
                add("bl", f"bl_{om}_cap10_qc", omega=om, q_center=True, **SPECS["_cap10"])
            else:
                add("bl", f"bl_{om}_lv_cap10_qc", omega=om, q_center=True, **SPECS["_lv_cap10"])
        for n in N_GRID:
            for seed in range(3):
                add("bl", f"bl_empirical_N{n}", omega="empirical", n_draws=n, seed=seed)
    print(f"jobs: {len(jobs)}")
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init,
                             initargs=(args.market, args.model_tag, args.prompt, args.top_n, args.start, args.end)) as ex:
        res = list(ex.map(_job, jobs, chunksize=4))

    # group by label (+ n/seed) and apply walk-forward tau where a grid exists
    groups = {}
    for cd, w in res:
        key = (cd["label"], cd.get("n_draws"), cd.get("seed", 0))
        groups.setdefault(key, {})[cd.get("tau", 0.0)] = w
    rows, tau_rows, nets_main, weights_main = [], [], {}, {}
    for (label, n, seed), by_tau in groups.items():
        if len(by_tau) > 1:
            w, path = walk_forward(eng, by_tau, periods, rf, args.burn_in, psi=0.001)
            tau_rows += [dict(label=label, n_draws=n, seed=seed, quarter=q, tau=t) for q, t in path.items()]
        else:
            w = next(iter(by_tau.values()))
            # drop the burn-in quarters so every strategy is evaluated on the same holding periods
            qs = sorted({quarter_of(p[0]) for p in periods})[: args.burn_in]
            w = {p: v for p, v in w.items() if quarter_of(p[0]) not in qs}
        eval_periods = [p for p in periods if p in w or p == periods[-1]]
        for psi in PSI_GRID:
            net = eng.portfolio_returns(w, periods, psi=psi)["net"]
            r = dict(market=args.market, model=args.model_tag or "-", prompt=args.prompt, label=label, n_draws=n, seed=seed, psi=psi,
                     max_weight=float(max(s.max() for s in w.values())), n_rebalances=len(w))
            r.update(M.performance(net, rf))
            rows.append(r)
            if psi == 0.001 and n is None:
                nets_main[label] = net
                weights_main[label] = w
    perf = pd.DataFrame(rows)
    perf.to_csv(out / "performance_all.csv", index=False)
    main_tbl = perf[(perf.psi == 0.001) & perf.n_draws.isna()].drop(columns=["psi", "n_draws", "seed"])
    main_tbl.to_csv(out / "performance.csv", index=False)
    perf[perf.n_draws.notna() & (perf.psi == 0.001)].to_csv(out / "n_sensitivity.csv", index=False)
    pd.DataFrame(tau_rows).to_csv(out / "tau_path.csv", index=False)
    if views is not None:
        sh = main_tbl.set_index("label")["Sharpe_ann"]
        hl_label = lambda om, spec: f"bl_{om}{spec.replace('_lv', '') if om == 'he_litterman' else spec}"
        mat = pd.DataFrame({spec or "raw": {om: sh.get(hl_label(om, spec), np.nan) for om in OMEGAS} for spec in SPECS})
        mat.to_csv(out / "omega_matrix.csv")
    dl = []
    for p in periods:
        dl.append(dict(period=p[0], delta_est=eng._delta(p, eng.universe(p), None, E.Config(delta=None))))
    pd.DataFrame(dl).to_csv(out / "delta_path.csv", index=False)
    for label, w in weights_main.items():
        pd.DataFrame({p[0]: s for p, s in w.items()}).T.to_csv(out / f"weights_{label}.csv")

    if views is not None:
        pairs = eng.forecast_pairs(views, periods)
        pairs.to_csv(out / "pairs.csv", index=False)
        cal = []
        for n in [None] + N_GRID:
            for seed in ([0] if n is None else [0, 1, 2]):
                df = eng.forecast_pairs(views, periods, n_draws=n, seed=seed)
                m = C.calibration_metrics(df)
                m.update(spearman_q_mom=float(df.groupby("period").apply(lambda g: g[["q", "mom10"]].corr("spearman").iloc[0, 1], include_groups=False).mean()),
                         spearman_q_next=float(df.groupby("period").apply(lambda g: g[["q", "realized"]].corr("spearman").iloc[0, 1], include_groups=False).mean()),
                         spearman_mom_next=float(df.groupby("period").apply(lambda g: g[["mom10", "realized"]].corr("spearman").iloc[0, 1], include_groups=False).mean()))
                cal.append(dict(model=args.model_tag, prompt=args.prompt, n_draws=n or "all", seed=seed, **m))
        pd.DataFrame(cal).to_csv(out / "calibration.csv", index=False)

    comparisons = [("bl_empirical", "ew"), ("bl_empirical", "mom_bl"), ("bl_empirical", "mvo_hist"), ("bl_empirical", "stat_bl"),
                   ("llm_topk", "mom_topk"), ("llm_topk", "ew")]
    for spec in SPECS:
        hl = f"bl_he_litterman{spec.replace('_lv', '')}"
        comparisons += [(f"bl_empirical{spec}", f"bl_constant{spec}"), (f"bl_empirical{spec}", hl), (f"bl_empirical{spec}", f"bl_shuffle{spec}"),
                        (f"bl_calibrated{spec}", f"bl_constant{spec}"), (f"bl_linear{spec}", f"bl_constant{spec}"), (f"bl_linear{spec}", hl)]
    comparisons += [("bl_empirical_qc", "bl_constant_qc"), ("bl_empirical_qc", "bl_he_litterman_qc"), ("bl_empirical_qc", "bl_empirical"),
                    ("bl_empirical_lv_cap10_qc", "bl_constant_lv_cap10_qc"), ("bl_empirical_lv_cap10_qc", "bl_he_litterman_cap10_qc"),
                    ("bl_empirical_lv_cap10_qc", "bl_empirical_lv_cap10")]
    comparisons += [("bl_empirical_lv_cap10", "ew"), ("bl_empirical_lv_cap10", "mom_bl_cap10"), ("bl_empirical_lv_cap10", "prior_cap10")]
    for dsuf in DELTAS:
        comparisons += [(f"bl_empirical{dsuf}", f"bl_constant{dsuf}"), (f"bl_empirical{dsuf}", f"bl_he_litterman{dsuf}"),
                        (f"bl_empirical_lv_cap10{dsuf}", f"bl_constant_lv_cap10{dsuf}"), (f"bl_empirical_lv_cap10{dsuf}", f"bl_he_litterman_cap10{dsuf}")]
    boots = [dict(a=a, b=b, **M.bootstrap_sharpe_diff(nets_main[a], nets_main[b], rf, n_boot=args.n_boot))
             for a, b in comparisons if a in nets_main and b in nets_main]
    pd.DataFrame(boots).to_csv(out / "bootstrap.csv", index=False)
    (out / "run_meta.json").write_text(json.dumps(dict(revision=git_revision(), args=vars(args), n_jobs=len(jobs),
                                                       finished=time.strftime("%Y-%m-%d %H:%M:%S"),
                                                       elapsed_s=round(time.time() - t_start, 1)), indent=2))
    print(main_tbl[["label", "n_rebalances", "Sharpe_ann", "CAGR", "std_ann", "MDD", "max_weight"]].round(3).to_string(index=False))
    if boots:
        print(pd.DataFrame(boots).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
