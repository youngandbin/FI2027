"""
Build the FI paper's tables (LaTeX) and figures (PDF) from one backtest output folder.

Usage: python 92_paper_assets.py [--market US] [--tag gptoss20b_A]
Output: paper/fi/tables/*.tex, paper/fi/figures/*.pdf
"""
import argparse
import json
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from paths import RESULTS_DIR, ROOT, VIEWS_DIR

PAPER = ROOT / "paper" / "fi"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
OMEGA_NAMES = {"empirical": "Empirical ($s_i^2$)", "constant": "Constant", "shuffle": "Shuffled",
               "he_litterman": "He--Litterman ($\\tau\\Sigma_{ii}$)", "calibrated": "Isotonic-calibrated", "linear": "Linear-calibrated"}
SPEC_NAMES = {"": "Raw", "_lv": "Level-matched", "_cap10": "10\\% cap", "_lv_cap10": "Level-matched + cap"}


def f3(x):
    return "--" if pd.isna(x) else f"{x:.2f}"


def stars(p):
    return "" if pd.isna(p) else ("$^{***}$" if p < 0.01 else "$^{**}$" if p < 0.05 else "$^{*}$" if p < 0.1 else "")


def write(name, body):
    (PAPER / "tables" / name).write_text(body)
    print("wrote", name)


def hl_label(om, spec):
    return f"bl_{om}{spec.replace('_lv', '') if om == 'he_litterman' else spec}"


def table_q(cal, pairs):
    a = cal[cal.n_draws == "all"].iloc[0]
    d = pairs.assign(qd=pairs.q - pairs.groupby("period").q.transform("mean"),
                     rd=pairs.realized - pairs.groupby("period").realized.transform("mean"))
    slope = np.polyfit(d.qd, d.rd, 1)[0]
    rows = [("Rank correlation of $q_i$ with the trailing 10-day mean return", a.spearman_q_mom),
            ("Rank correlation of $q_i$ with the next two-week mean return", a.spearman_q_next),
            ("Rank correlation of the trailing 10-day mean with the next two-week mean", a.spearman_mom_next),
            ("Slope of the next two-week return on $q_i$ (both demeaned by date)", slope),
            ("Mean $q_i$ (\\% per day)", pairs.q.mean() * 100),
            ("Mean realized return (\\% per day)", pairs.realized.mean() * 100)]
    body = "\\begin{tabular}{lr}\n\\toprule\nQuantity & Value \\\\\n\\midrule\n"
    body += "".join(f"{k} & {v:.3f} \\\\\n" for k, v in rows)
    body += "\\bottomrule\n\\end{tabular}\n"
    write("tab_q.tex", body)


def table_calib(cal):
    cols = [("spearman_s2_sqerr", "$\\rho(s^2, e^2)$"), ("spearman_volstd", "$\\rho(s^2/\\hat\\sigma^2, e^2/\\hat\\sigma^2)$"),
            ("spearman_partial_vol", "Partial $\\rho$ given $\\hat\\sigma^2$"), ("spearman_volstd_within_mean", "Within-date mean"),
            ("spearman_volstd_within_frac_pos", "Share of dates $>0$"), ("spearman_volstd_within_t", "$t$ (across dates)"),
            ("coverage95", "95\\% cov., $s^2$"), ("coverage95_pred", "95\\% cov., $s^2+\\hat\\sigma^2/h$"),
            ("coverage95_noise_only", "95\\% cov., $\\hat\\sigma^2/h$")]
    g = cal.copy()
    g["N"] = g.n_draws.replace({"all": "20"})
    g = g[(g.n_draws == "all") | (g.n_draws.isin(["5", "10"]))]
    agg = g.groupby("N")[[c for c, _ in cols]].mean().loc[["5", "10", "20"]]
    body = "\\begin{tabular}{l" + "r" * 3 + "}\n\\toprule\n & $N=5$ & $N=10$ & $N=20$ \\\\\n\\midrule\n"
    for c, nm in cols:
        body += nm + " & " + " & ".join(f"{agg.loc[n, c]:.3f}" for n in ["5", "10", "20"]) + " \\\\\n"
        if c == "spearman_volstd_within_t":
            body += "\\midrule\n"
    body += "\\bottomrule\n\\end{tabular}\n"
    write("tab_calib.tex", body)


def table_omega(perf, boot):
    sh = perf.set_index("label")["Sharpe_ann"]
    bt = boot.set_index(["a", "b"])
    body = "\\begin{tabular}{l" + "r" * len(SPEC_NAMES) + "}\n\\toprule\n$\\bm{\\Omega}$ & " + " & ".join(SPEC_NAMES.values()) + " \\\\\n\\midrule\n"
    for om, nm in OMEGA_NAMES.items():
        cells = []
        for spec in SPEC_NAMES:
            cells.append(f3(sh.get(hl_label(om, spec), np.nan)))
        body += nm + " & " + " & ".join(cells) + " \\\\\n"
    body += "\\midrule\n"
    for ref, refnm in (("constant", "Constant"), ("he_litterman", "He--Litterman")):
        for a_om in ("empirical", "linear"):
            cells = []
            for spec in SPEC_NAMES:
                key = (f"bl_{a_om}{spec}", hl_label(ref, spec) if ref == "he_litterman" else f"bl_{ref}{spec}")
                if key in bt.index:
                    r = bt.loc[key]
                    cells.append(f"{r['diff']:.2f}{stars(r['p_value'])}")
                else:
                    cells.append("--")
            body += f"{OMEGA_NAMES[a_om].split(' (')[0]} $-$ {refnm} & " + " & ".join(cells) + " \\\\\n"
    body += "\\bottomrule\n\\end{tabular}\n"
    write("tab_omega.tex", body)


def table_reference(perf):
    names = [("ew", "Equal weight"), ("cap", "Market-cap weight"), ("mvo_hist", "MVO, 126-day mean"), ("prior", "BL prior only (no views)"),
             ("stat_bl", "BL, 126-day mean view"), ("mom_bl", "BL, momentum view"), ("mom_topk", "Top-10 momentum"),
             ("llm_mvo", "MVO on LLM $q$"), ("llm_topk", "Top-10 by LLM $q$"), ("bl_empirical", "BL, LLM $q$, empirical $\\Omega$"),
             ("bl_he_litterman", "BL, LLM $q$, He--Litterman $\\Omega$")]
    p = perf.set_index("label")
    body = "\\begin{tabular}{lrrrrr|rr}\n\\toprule\n & Sharpe & CAGR & Vol. & MDD & Max $w$ & \\multicolumn{2}{c}{10\\% cap} \\\\\n" \
           " & & & & & & Sharpe & MDD \\\\\n\\midrule\n"
    for lab, nm in names:
        r = p.loc[lab]
        c = p.loc[f"{lab}_cap10"] if f"{lab}_cap10" in p.index else None
        capcells = f"{c.Sharpe_ann:.2f} & {c.MDD:.2f}" if c is not None else "-- & --"
        body += f"{nm} & {r.Sharpe_ann:.2f} & {r.CAGR:.2f} & {r.std_ann:.2f} & {r.MDD:.2f} & {r.max_weight:.2f} & {capcells} \\\\\n"
    body += "\\bottomrule\n\\end{tabular}\n"
    write("tab_reference.tex", body)


def table_delta(perf, dpath):
    sh = perf.set_index("label")["Sharpe_ann"]
    ds = [("_d1.5", "1.5"), ("", "2.5"), ("_d3.5", "3.5"), ("_dest", "252-day est.")]
    rows = [("BL prior only", "prior"), ("BL, empirical $\\Omega$", "bl_empirical"), ("BL, constant $\\Omega$", "bl_constant"),
            ("BL, He--Litterman $\\Omega$", "bl_he_litterman"), ("BL, empirical $\\Omega$, level-matched + cap", "bl_empirical_lv_cap10"),
            ("BL, constant $\\Omega$, level-matched + cap", "bl_constant_lv_cap10"), ("BL, He--Litterman $\\Omega$, cap", "bl_he_litterman_cap10")]
    body = "\\begin{tabular}{l" + "r" * len(ds) + "}\n\\toprule\n$\\delta$ & " + " & ".join(d for _, d in ds) + " \\\\\n\\midrule\n"
    for nm, lab in rows:
        body += nm + " & " + " & ".join(f3(sh.get(f"{lab}{s}", np.nan)) for s, _ in ds) + " \\\\\n"
    body += "\\bottomrule\n\\end{tabular}\n"
    write("tab_delta.tex", body)
    return dpath.delta_est.min(), dpath.delta_est.median(), dpath.delta_est.max()


def table_center(perf, boot):
    sh = perf.set_index("label")["Sharpe_ann"]
    rows = [("Empirical", "bl_empirical", "bl_empirical_lv_cap10"), ("Constant", "bl_constant", "bl_constant_lv_cap10"),
            ("Shuffled", "bl_shuffle", "bl_shuffle_lv_cap10"), ("He--Litterman", "bl_he_litterman", "bl_he_litterman_cap10")]
    body = "\\begin{tabular}{lrrrr}\n\\toprule\n & \\multicolumn{2}{c}{Raw} & \\multicolumn{2}{c}{Level-matched + cap} \\\\\n" \
           "$\\bm{\\Omega}$ & $q$ & centred $q$ & $q$ & centred $q$ \\\\\n\\midrule\n"
    for nm, a, b in rows:
        body += f"{nm} & {f3(sh.get(a))} & {f3(sh.get(a + '_qc'))} & {f3(sh.get(b))} & {f3(sh.get(b + '_qc'))} \\\\\n"
    body += "\\bottomrule\n\\end{tabular}\n"
    write("tab_center.tex", body)


def table_costs(perf_all):
    p = perf_all[perf_all.n_draws.isna()]
    labs = [("ew", "Equal weight"), ("bl_empirical", "BL, empirical $\\Omega$"), ("bl_constant", "BL, constant $\\Omega$"),
            ("bl_he_litterman", "BL, He--Litterman $\\Omega$"), ("bl_empirical_lv_cap10", "BL, empirical, level-matched + cap"),
            ("bl_constant_lv_cap10", "BL, constant, level-matched + cap")]
    psis = sorted(p.psi.unique())
    body = "\\begin{tabular}{l" + "r" * len(psis) + "}\n\\toprule\nCost (bp) & " + " & ".join(f"{x * 1e4:.0f}" for x in psis) + " \\\\\n\\midrule\n"
    for lab, nm in labs:
        q = p[p.label == lab].set_index("psi")["Sharpe_ann"]
        body += nm + " & " + " & ".join(f3(q.get(x)) for x in psis) + " \\\\\n"
    body += "\\bottomrule\n\\end{tabular}\n"
    write("tab_costs.tex", body)


def fig_deciles(pairs):
    p = pairs.copy()
    p["dec"] = p.groupby("period").s2.transform(lambda x: pd.qcut(x.rank(method="first"), 10, labels=False))
    g = p.groupby("dec").agg(s2=("s2", "mean"), sq=("sq_err", "mean"), noise=("noise", "mean"))
    x = np.arange(1, 11)
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    for col, c, lab, mk in (("s2", S1, "LLM dispersion $s_i^2$ (empirical $\\Omega_{ii}$)", "o"),
                            ("sq", S2, "Realized squared error $(q_i-\\bar r_i)^2$", "s"),
                            ("noise", S3, "Return noise $\\hat\\sigma_i^2/h$", "^")):
        ax.plot(x, g[col].values, color=c, lw=2, marker=mk, ms=6, label=lab, markeredgecolor="white", markeredgewidth=1)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xlabel("Decile of $s_i^2$ within each rebalancing date (1 = least dispersed)", color=INK2)
    ax.set_ylabel("Variance (daily return$^2$)", color=INK2)
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(PAPER / "figures" / "fig_deciles.pdf")
    plt.close(fig)
    print("wrote fig_deciles.pdf")
    return g


def fig_omega(perf):
    sh = perf.set_index("label")["Sharpe_ann"]
    ew = sh["ew"]
    oms = list(OMEGA_NAMES)
    specs = [("", "Raw", S1, "o"), ("_lv", "Level-matched", S2, "s"), ("_cap10", "10% cap", S3, "^"), ("_lv_cap10", "Level-matched + cap", "#4a3aa7", "D")]
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    y = np.arange(len(oms))[::-1]
    for k, (spec, lab, c, mk) in enumerate(specs):
        vals = [sh.get(hl_label(om, spec), np.nan) for om in oms]
        ax.scatter(vals, y + (1.5 - k) * 0.16, color=c, marker=mk, s=40, label=lab, edgecolor="white", linewidth=1, zorder=3)
    ax.axvline(ew, color=INK2, lw=1, ls="--")
    ax.text(ew, -0.55, "equal weight ", color=INK2, fontsize=8, va="center", ha="right")
    ax.axvline(0, color=GRID, lw=1)
    ax.set_yticks(y)
    ax.set_yticklabels([OMEGA_NAMES[o].split(" (")[0].replace("--", "–") for o in oms], color=INK)
    ax.set_xlabel("Annualized Sharpe ratio, 2025 (net of 10 bp)", color=INK2)
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK2)
    ax.set_ylim(-0.8, len(oms) - 0.5)
    ax.legend(frameon=False, fontsize=8, loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=4, handletextpad=0.2, columnspacing=1.0)
    fig.tight_layout()
    fig.savefig(PAPER / "figures" / "fig_omega.pdf")
    plt.close(fig)
    print("wrote fig_omega.pdf")


def draw_stats(market, model_tag, prompt):
    rows, alld = [], []
    for f in sorted((VIEWS_DIR / market / model_tag / prompt).glob("*.json")):
        for v in json.loads(f.read_text()).values():
            d = np.asarray(v["draws"], float)
            alld.append(d)
            if len(d) > 1:
                c = Counter(np.round(d, 4))
                rows.append(dict(uniq=len(c), mode_share=c.most_common(1)[0][1] / len(d)))
    r = pd.DataFrame(rows)
    top = Counter(np.round(np.concatenate(alld), 3)).most_common(3)
    return dict(mean_unique=float(r.uniq.mean()), mean_mode_share=float(r.mode_share.mean()),
                top_values=[(float(k), int(n)) for k, n in top], n_draws_total=int(sum(len(d) for d in alld)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", default="US")
    ap.add_argument("--tag", default="gptoss20b_A")
    args = ap.parse_args()
    out = RESULTS_DIR / args.market / args.tag
    (PAPER / "tables").mkdir(parents=True, exist_ok=True)
    (PAPER / "figures").mkdir(parents=True, exist_ok=True)
    perf = pd.read_csv(out / "performance.csv")
    perf_all = pd.read_csv(out / "performance_all.csv")
    boot = pd.read_csv(out / "bootstrap.csv")
    cal = pd.read_csv(out / "calibration.csv", dtype={"n_draws": str})
    pairs = pd.read_csv(out / "pairs.csv")
    dpath = pd.read_csv(out / "delta_path.csv")
    table_q(cal, pairs)
    table_calib(cal)
    table_omega(perf, boot)
    table_reference(perf)
    dmin, dmed, dmax = table_delta(perf, dpath)
    table_center(perf, boot)
    table_costs(perf_all)
    g = fig_deciles(pairs)
    fig_omega(perf)
    model_tag, prompt = args.tag.rsplit("_", 1)
    ds = draw_stats(args.market, model_tag, prompt)
    rr = lambda x: np.quantile(x, .9) / np.quantile(x, .1)
    spread = pairs.groupby("period").agg(s2=("s2", rr), vol2=("vol2", rr)).median()
    facts = dict(delta_est_min=dmin, delta_est_median=dmed, delta_est_max=dmax,
                 decile_ratio_s2=float(g.s2.iloc[-1] / g.s2.iloc[0]), decile_ratio_sqerr=float(g.sq.iloc[-1] / g.sq.iloc[0]),
                 decile_ratio_noise=float(g.noise.iloc[-1] / g.noise.iloc[0]),
                 within_date_p90_p10_s2=float(spread.s2), within_date_p90_p10_vol2=float(spread.vol2),
                 rho_volstd_dispersion_absmom=float(spearmanr(pairs.s2 / pairs.vol2, pairs.mom10.abs() / np.sqrt(pairs.vol2))[0]),
                 **ds)
    (PAPER / "tables" / "facts.json").write_text(json.dumps(facts, indent=2))
    print(json.dumps(facts, indent=2))


if __name__ == "__main__":
    main()
