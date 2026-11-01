"""Random-effects meta-analysis of logit(AUC) for live-birth prediction models, forest plot and taxonomy figure.

Inputs : content/studies.json and content/studies_meta.json (from scripts/export_data.js),
         build/manuscript.bbl (citation labels, optional; so that letters such as 2024a match the reference list)
Outputs: build/ma_results.json, build/figs/fig_forest.pdf, build/figs/fig_taxonomy.pdf (+ preview png),
         supplement/S2_meta_analysis_estimates.csv
Method : logit(AUC) with SE from the reported 95% CI or the Hanley-McNeil formula (delta method);
         primary: REML tau^2 with Hartung-Knapp-Sidik-Jonkman CI (DerSimonian-Laird as sensitivity); Higgins-Thompson I^2; 95% prediction interval with t_{k-2} (Higgins et al. 2009);
         Egger regression test for small-study effects.
Selection rules (one estimate per study in every analysis):
  * estimates without a variance and estimates made after a pregnancy test ("post_transfer") are shown, not pooled;
  * validation-design analyses: the study's estimate of that design at its earliest decision point;
  * risk-of-bias and overall analyses: the external estimate where one exists, otherwise the internal one,
    each at the earliest decision point;
  * decision-point analyses: for each decision point, the external estimate where one exists, otherwise the internal one.
"""
import json, math, re, csv
from pathlib import Path
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
est = json.loads((ROOT / "content" / "studies.json").read_text())
meta = json.loads((ROOT / "content" / "studies_meta.json").read_text())
bibkey_of = json.loads((ROOT / "content" / "bibkeys.json").read_text())

labels = {}
bbl = ROOT / "build" / "manuscript.bbl"
if bbl.exists():
    for m in re.finditer(r"\\bibitem\[\{(.+?)\((\d{4}[a-z]?)\)(.*?)\}\]\{([^}]+)\}", bbl.read_text(), re.S):
        auth, year, _, bk = m.groups()
        auth = auth.replace("~", " ").replace("{", "").replace("}", "").replace("\\", "").strip()
        labels[bk] = f"{auth} ({year})"
label = lambda s: labels.get(bibkey_of.get(s["key"], s["key"]), s["label"])

logit = lambda p: math.log(p / (1 - p))
inv = lambda x: 1 / (1 + math.exp(-x))
Z = 1.959964
DP_ORDER = {"pre_treatment": 0, "post_stimulation": 1, "pre_transfer": 2, "post_cycle": 3, "unclear": 4, "post_transfer": 5}

def hanley_mcneil(a, n1, n0):
    q1, q2 = a / (2 - a), 2 * a * a / (1 + a)
    return math.sqrt((a * (1 - a) + (n1 - 1) * (q1 - a * a) + (n0 - 1) * (q2 - a * a)) / (n1 * n0))

for s in est:
    a = s["auc"]; s["theta"] = logit(a); s["se_theta"] = None; s["ci_source"] = "reported"
    if s["se"] == "ci" and s["hi"] < 1:
        s["se_theta"] = (logit(s["hi"]) - logit(s["lo"])) / (2 * Z)
    elif s["se"] in ("hm", "hm_approx", "hm_assumed") or (s["se"] == "ci" and s["hi"] >= 1):
        n = s["evalN"]; n1 = s.get("events") or round(0.40 * n); n0 = n - n1
        s["se_theta"] = hanley_mcneil(a, n1, n0) / (a * (1 - a))
        if s["se"] != "ci":
            s["lo"], s["hi"] = inv(s["theta"] - Z * s["se_theta"]), inv(s["theta"] + Z * s["se_theta"]); s["ci_source"] = "derived"
    s["poolable"] = s["se_theta"] is not None and s["decision"] != "post_transfer"

def pool_dl(rows):
    rows = [r for r in rows if r["poolable"]]
    k = len(rows)
    if k == 0:
        return None
    y = np.array([r["theta"] for r in rows]); v = np.array([r["se_theta"] ** 2 for r in rows]); w = 1 / v
    fe = np.sum(w * y) / np.sum(w); q = float(np.sum(w * (y - fe) ** 2)); c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (q - (k - 1)) / c) if k > 1 else 0.0
    ws = 1 / (v + tau2); mu = float(np.sum(ws * y) / np.sum(ws)); se = float(math.sqrt(1 / np.sum(ws)))
    i2 = max(0.0, (q - (k - 1)) / q) if (k > 1 and q > 0) else 0.0
    out = dict(k=k, auc=inv(mu), lo=inv(mu - Z * se), hi=inv(mu + Z * se), tau2=tau2, i2=i2, q=q, mu=mu, se=se,
               keys=[r["key"] for r in rows])
    if k >= 3:
        t = stats.t.ppf(0.975, k - 2); half = t * math.sqrt(tau2 + se * se)
        out.update(pi_lo=inv(mu - half), pi_hi=inv(mu + half))
    return out

def pool_reml_hk(rows):
    """Sensitivity: REML tau^2 (Fisher-scoring fixed point) with Hartung-Knapp-Sidik-Jonkman CI (Debray et al. 2017)."""
    rows = [r for r in rows if r["poolable"]]
    k = len(rows)
    if k < 2:
        return None
    y = np.array([r["theta"] for r in rows]); v = np.array([r["se_theta"] ** 2 for r in rows])
    w0 = 1 / v; fe = np.sum(w0 * y) / np.sum(w0); q = float(np.sum(w0 * (y - fe) ** 2)); c = np.sum(w0) - np.sum(w0 ** 2) / np.sum(w0)
    tau2 = max(0.0, (q - (k - 1)) / c)
    for _ in range(500):
        w = 1 / (v + tau2); mu = np.sum(w * y) / np.sum(w)
        new = max(0.0, float(np.sum(w ** 2 * ((y - mu) ** 2 - v)) / np.sum(w ** 2) + 1 / np.sum(w)))
        if abs(new - tau2) < 1e-10:
            tau2 = new; break
        tau2 = new
    w = 1 / (v + tau2); mu = float(np.sum(w * y) / np.sum(w))
    qhk = float(np.sum(w * (y - mu) ** 2) / (k - 1)); se = math.sqrt(max(qhk, 1.0) / np.sum(w))
    t = stats.t.ppf(0.975, k - 1)
    i2 = max(0.0, (q - (k - 1)) / q) if q > 0 else 0.0
    out = dict(k=k, auc=inv(mu), lo=inv(mu - t * se), hi=inv(mu + t * se), tau2=tau2, mu=mu, se=se, i2=i2)
    if k >= 3:
        t2 = stats.t.ppf(0.975, k - 2); half = t2 * math.sqrt(tau2 + se * se)
        out.update(pi_lo=inv(mu - half), pi_hi=inv(mu + half))
    out.update(q=q, keys=[r["key"] for r in rows])
    return out

def pool(rows):
    """Primary estimator: REML with Hartung-Knapp-Sidik-Jonkman CI; a single estimate is returned with its own CI."""
    rr = [r for r in rows if r["poolable"]]
    if len(rr) == 0:
        return None
    if len(rr) == 1:
        r = rr[0]
        return dict(k=1, auc=inv(r["theta"]), lo=inv(r["theta"] - Z * r["se_theta"]), hi=inv(r["theta"] + Z * r["se_theta"]),
                    tau2=0.0, i2=0.0, q=0.0, mu=r["theta"], se=r["se_theta"], keys=[r["key"]])
    return pool_reml_hk(rr)

def pick(rows, prefer_external=False, latest=False):
    """One poolable estimate per study."""
    by = {}
    for r in rows:
        if not r["poolable"]:
            continue
        cur = by.get(r["key"])
        rank = lambda x: ((0 if x["valid"] == "external" else 1) if prefer_external else 0,
                          -DP_ORDER[x["decision"]] if latest else DP_ORDER[x["decision"]])
        if cur is None or rank(r) < rank(cur):
            by[r["key"]] = r
    return list(by.values())

R = {}
internal = pick([s for s in est if s["valid"] == "internal"])
external = pick([s for s in est if s["valid"] == "external"])
overall = pick(est, prefer_external=True)
R["internal"] = pool(internal); R["external"] = pool(external); R["overall"] = pool(overall)
for lev in ["low", "unclear", "high"]:
    R["overall_" + lev] = pool([s for s in overall if s["overall"] == lev])
R["overall_not_high"] = pool([s for s in overall if s["overall"] != "high"])
R["internal_not_high"] = pool([s for s in internal if s["overall"] != "high"])
R["internal_high"] = pool([s for s in internal if s["overall"] == "high"])
def pdiff(a, b):
    z = (a["mu"] - b["mu"]) / math.sqrt(a["se"] ** 2 + b["se"] ** 2); return float(2 * (1 - stats.norm.cdf(abs(z))))
R["dl_internal"] = pool_dl(internal); R["dl_external"] = pool_dl(external)
R["dl_not_high"] = pool_dl([s for s in overall if s["overall"] != "high"]); R["dl_high"] = pool_dl([s for s in overall if s["overall"] == "high"])
R["p_int_vs_ext_dl"] = pdiff(R["dl_internal"], R["dl_external"]); R["p_high_vs_not_dl"] = pdiff(R["dl_high"], R["dl_not_high"])
R["reml_internal"] = pool_reml_hk(internal); R["reml_external"] = pool_reml_hk(external)
R["reml_not_high"] = pool_reml_hk([s for s in overall if s["overall"] != "high"]); R["reml_high"] = pool_reml_hk([s for s in overall if s["overall"] == "high"])
def pdiff_t(a, b):
    z = (a["mu"] - b["mu"]) / math.sqrt(a["se"] ** 2 + b["se"] ** 2); df = min(a["k"], b["k"]) - 1
    return float(2 * (1 - stats.t.cdf(abs(z), df)))
R["p_int_vs_ext_reml"] = pdiff_t(R["reml_internal"], R["reml_external"])
R["p_high_vs_not_reml"] = pdiff_t(R["reml_high"], R["reml_not_high"])
R["p_int_vs_ext"] = R["p_int_vs_ext_reml"]; R["p_high_vs_not"] = R["p_high_vs_not_reml"]
for d in ["pre_treatment", "post_stimulation", "pre_transfer", "post_cycle", "unclear"]:
    R["dp_" + d] = pool(pick([s for s in est if s["decision"] == d], prefer_external=True))
# within-study internal-to-external change, where a study reports both at the same decision point
pairs = []
for s in est:
    if s["valid"] != "external" or not s["poolable"]:
        continue
    for t in est:
        if t["key"] == s["key"] and t["valid"] == "internal" and t["decision"] == s["decision"] and t["poolable"]:
            pairs.append(dict(key=s["key"], decision=s["decision"], internal=t["auc"], external=s["auc"], change=s["auc"] - t["auc"]))
R["paired_int_ext"] = pairs
# pooled within-study change (external minus internal, logit scale); internal and external sets are different patients,
# so the variances add; one pair per study, at its earliest decision point
pp_rows = {}
for s in est:
    if s["valid"] != "external" or not s["poolable"]:
        continue
    for t_ in est:
        if t_["key"] == s["key"] and t_["valid"] == "internal" and t_["decision"] == s["decision"] and t_["poolable"]:
            cur = pp_rows.get(s["key"])
            if cur is None or DP_ORDER[s["decision"]] < cur["_dp"]:
                pp_rows[s["key"]] = dict(key=s["key"], theta=s["theta"] - t_["theta"], se_theta=math.sqrt(s["se_theta"] ** 2 + t_["se_theta"] ** 2),
                                         poolable=True, _dp=DP_ORDER[s["decision"]])
_wp = pool_reml_hk(list(pp_rows.values()))
_tq = stats.t.ppf(0.975, _wp["k"] - 1)
_conv = lambda d: inv(logit(0.80) + d) - 0.80
R["within_pairs"] = dict(k=_wp["k"], d=_wp["mu"], lo=_wp["mu"] - _tq * _wp["se"], hi=_wp["mu"] + _tq * _wp["se"],
                         auc_d=_conv(_wp["mu"]), auc_lo=_conv(_wp["mu"] - _tq * _wp["se"]), auc_hi=_conv(_wp["mu"] + _tq * _wp["se"]),
                         p=float(2 * stats.t.sf(abs(_wp["mu"] / _wp["se"]), _wp["k"] - 1)), n_fall=sum(1 for r in pp_rows.values() if r["theta"] < 0),
                         keys=sorted(pp_rows))
# sensitivity analyses
R["sens_external_latest"] = pool(pick([s for s in est if s["valid"] == "external"], latest=True))
R["sens_external_n100"] = pool([s for s in external if (s.get("evalN") or 1e9) >= 100])
R["sens_internal_fulltext"] = pool([s for s in internal if s["source"] == "full text"])
R["sens_internal_no_assumed"] = pool([s for s in internal if s["se"] != "hm_assumed"])
REBALANCED = ("goyal2020", "zhang2022", "bras2020", "ortiz2026", "nowak2026")  # evaluated on rebalanced or synthetic-augmented data
R["sens_internal_no_rebalanced"] = pool([s for s in internal if s["key"] not in REBALANCED])
R["sens_internal_no_overlap"] = pool([s for s in internal if s.get("group") not in ("guangxi", "xiamen") or s["key"] in ("fu2026", "cai2024")])
R["sens_internal_known_dp"] = pool([s for s in internal if s["decision"] != "unclear"])
R["sens_external_fulltext"] = pool([s for s in external if s["source"] == "full text"])
# estimates whose variance comes from a reported confidence interval only (no Hanley-McNeil approximation)
R["sens_internal_ci_only"] = pool([s for s in internal if s["se"] == "ci"])
R["sens_external_ci_only"] = pool([s for s in external if s["se"] == "ci"])
# endpoint: cumulative live birth vs live birth per cycle or per transfer
CUM = lambda s: ("umulative" in s["pop"]) or ("CLB" in s["pop"])
R["sens_internal_cumulative"] = pool([s for s in internal if CUM(s)])
R["sens_internal_per_cycle"] = pool([s for s in internal if not CUM(s)])
R["cumulative_keys"] = sorted({s["key"] for s in est if CUM(s)})
# leave-one-out range of the primary pooled estimates
def loo(rows):
    vals = [pool([r for j, r in enumerate(rows) if j != i])["auc"] for i in range(len(rows))]
    return dict(min=min(vals), max=max(vals))
R["loo_internal"] = loo(internal); R["loo_external"] = loo(external)
# Egger regression test (standardised effect on precision) for small-study effects among internal estimates
def egger(rows):
    rows = [r for r in rows if r["poolable"]]
    y = np.array([r["theta"] / r["se_theta"] for r in rows]); x = np.array([1 / r["se_theta"] for r in rows])
    res = stats.linregress(x, y)
    t = res.intercept / res.intercept_stderr
    return dict(k=len(rows), intercept=float(res.intercept), se=float(res.intercept_stderr), p=float(2 * stats.t.sf(abs(t), len(rows) - 2)))
R["egger_internal"] = egger(internal)
R["p_egger_no_lantzi"] = egger([s for s in internal if s["key"] != "lantzi2025"])["p"]  # influence of the single most precise estimate
# small-study test that avoids the dependence of SE(logit AUC) on the AUC itself: weighted regression of logit AUC on
# 1/sqrt(effective sample size), ESS = 4 n1 n0 / (n1 + n0), weights ESS (Peters et al. 2006; Debray et al. 2018);
# only estimates with reported (not assumed) evaluation-set size and events
def ess_test(rows):
    rows = [r for r in rows if r["poolable"] and r.get("evalN") and r.get("events") and r["se"] != "hm_assumed"]
    n1 = np.array([r["events"] for r in rows], float); n0 = np.array([r["evalN"] - r["events"] for r in rows], float)
    ess = 4 * n1 * n0 / (n1 + n0); x = 1 / np.sqrt(ess); y = np.array([r["theta"] for r in rows]); w = ess
    X = np.column_stack([np.ones(len(y)), x]); W = np.diag(w)
    b = np.linalg.solve(X.T @ W @ X, X.T @ W @ y); res = y - X @ b
    s2 = float(res @ W @ res) / (len(y) - 2); cov = s2 * np.linalg.inv(X.T @ W @ X)
    tval = b[1] / math.sqrt(cov[1, 1])
    return dict(k=len(y), slope=float(b[1]), p=float(2 * stats.t.sf(abs(tval), len(y) - 2)))
R["ess_test_internal"] = ess_test(internal)
R["ess_test_internal_no_lantzi"] = ess_test([s for s in internal if s["key"] != "lantzi2025"])
# paired comparisons of the best machine-learning model with logistic regression on the same data
paired = []
for m in meta:
    if m.get("lr") is None:
        continue
    sel = [e for e in est if e["key"] == m["key"] and e["valid"] == "internal"]
    if m["family"] == "Regression":
        ml = m.get("mlbest")
        paired.append(dict(key=m["key"], lr=m["lr"], ml=ml, diff=None if ml is None else round(ml - m["lr"], 3)))
    elif m.get("mlpair") is not None:
        paired.append(dict(key=m["key"], lr=m["lr"], ml=m["mlpair"], diff=round(m["mlpair"] - m["lr"], 3)))
    elif sel:
        paired.append(dict(key=m["key"], lr=m["lr"], ml=sel[0]["auc"], diff=round(sel[0]["auc"] - m["lr"], 3)))
R["paired_ml_lr"] = paired
q = [p["diff"] for p in paired if p["diff"] is not None]
R["paired_ml_lr_summary"] = dict(n=len(paired), n_quant=len(q), median=float(np.median(q)), min=min(q), max=max(q),
                                 n_le_0025=sum(1 for d in q if d <= 0.025), n_lr_best=sum(1 for p in paired if p["diff"] is None or p["diff"] <= 0))
# ---------- added analyses (reviewer requests): multivariable meta-regression, pooled paired ML-LR difference, trim-and-fill ----------
from scipy import optimize
def metareg(rows, cols):
    """Random-effects meta-regression of logit AUC: REML tau^2, Knapp-Hartung standard errors (t with k-p df)."""
    rows = [r for r in rows if r["poolable"]]
    y = np.array([r["theta"] for r in rows]); v = np.array([r["se_theta"] ** 2 for r in rows])
    X = np.column_stack([np.ones(len(rows))] + [np.array([c(r) for r in rows], float) for _, c in cols])
    k, p = X.shape
    def fit(t2):
        W = np.diag(1 / (v + t2)); XtWX = X.T @ W @ X; b = np.linalg.solve(XtWX, X.T @ W @ y); res = y - X @ b
        return W, XtWX, b, res
    def nll(t2):
        W, XtWX, b, res = fit(t2)
        return 0.5 * (np.sum(np.log(v + t2)) + np.linalg.slogdet(XtWX)[1] + res @ W @ res)
    t2 = optimize.minimize_scalar(nll, bounds=(0, 20), method="bounded").x
    W, XtWX, b, res = fit(t2)
    qkh = max(1.0, float(res @ W @ res) / (k - p))
    se = np.sqrt(np.diag(np.linalg.inv(XtWX)) * qkh)
    tcrit = stats.t.ppf(0.975, k - p)
    # residual heterogeneity explained: compare with intercept-only REML tau^2
    def nll0(t2):
        w = 1 / (v + t2); mu = np.sum(w * y) / np.sum(w)
        return 0.5 * (np.sum(np.log(v + t2)) + np.log(np.sum(w)) + np.sum(w * (y - mu) ** 2))
    t20 = optimize.minimize_scalar(nll0, bounds=(0, 20), method="bounded").x
    coef = []
    for j, name in enumerate(["intercept"] + [n for n, _ in cols]):
        coef.append(dict(name=name, b=float(b[j]), lo=float(b[j] - tcrit * se[j]), hi=float(b[j] + tcrit * se[j]),
                         p=float(2 * stats.t.sf(abs(b[j] / se[j]), k - p))))
    return dict(k=k, p=p, tau2=float(t2), tau2_null=float(t20), r2=float(max(0.0, 1 - t2 / t20)) if t20 > 0 else 0.0, coef=coef)
MODS = [("external", lambda r: r["valid"] == "external"),
        ("high_rob", lambda r: r["overall"] == "high"),
        ("dp_unstated", lambda r: r["decision"] == "unclear"),
        ("log_se", lambda r: math.log(r["se_theta"]))]
R["metareg"] = metareg(overall, MODS[:3])
R["metareg_size"] = metareg(overall, MODS)
# permutation test for the meta-regression (Higgins and Thompson 2004): permute the rows of the moderator matrix
def metareg_perm(rows, cols, n_perm=1000, seed=20261031):
    rows = [r for r in rows if r["poolable"]]
    obs = metareg(rows, cols)
    t_obs = [abs(c["b"]) / ((c["hi"] - c["lo"]) / 2) for c in obs["coef"][1:]]
    rng = np.random.default_rng(seed)
    mods = [[c(r) for _, c in cols] for r in rows]
    cnt = np.zeros(len(cols))
    for _ in range(n_perm):
        perm = rng.permutation(len(rows))
        shuffled = [dict(r, _m=mods[perm[i]]) for i, r in enumerate(rows)]
        pc = [(n, (lambda j: (lambda r: r["_m"][j]))(j)) for j, (n, _) in enumerate(cols)]
        f = metareg(shuffled, pc)
        tp = [abs(c["b"]) / ((c["hi"] - c["lo"]) / 2) for c in f["coef"][1:]]
        cnt += np.array([tp[j] >= t_obs[j] - 1e-12 for j in range(len(cols))])
    return {n: float((cnt[j] + 1) / (n_perm + 1)) for j, (n, _) in enumerate(cols)}
R["metareg_perm"] = metareg_perm(overall, MODS[:3])
# pooled paired difference (best ML minus logistic regression) on the logit scale, with assumed within-study correlation r
def paired_pool(r_corr, keep=lambda k: True):
    rows = []
    for p_ in paired:
        if not keep(p_["key"]):
            continue
        if p_["diff"] is None:
            continue
        sel = [e for e in est if e["key"] == p_["key"] and e["valid"] == "internal" and e["poolable"]]
        if not sel:
            continue
        s = sel[0]
        def v_of(a):
            if s.get("evalN") and s.get("events"):
                n1 = s["events"]; n0 = s["evalN"] - s["events"]
                return (hanley_mcneil(a, n1, n0) / (a * (1 - a))) ** 2
            return s["se_theta"] ** 2
        v1, v2 = v_of(p_["ml"]), v_of(p_["lr"])
        d = logit(p_["ml"]) - logit(p_["lr"])
        vd = max(v1 + v2 - 2 * r_corr * math.sqrt(v1 * v2), 1e-6)
        rows.append(dict(key=p_["key"], theta=d, se_theta=math.sqrt(vd), poolable=True))
    re_ = pool_reml_hk(rows); dl = pool_dl(rows)
    # back-transform at an LR AUC of 0.75: AUC_ML = inv(logit(0.75)+d)
    conv = lambda d: inv(logit(0.75) + d) - 0.75
    return dict(k=len(rows), d=re_["mu"], lo=re_["mu"] - stats.t.ppf(0.975, re_["k"] - 1) * re_["se"], hi=re_["mu"] + stats.t.ppf(0.975, re_["k"] - 1) * re_["se"],
                auc_d=conv(re_["mu"]), auc_lo=conv(re_["mu"] - stats.t.ppf(0.975, re_["k"] - 1) * re_["se"]), auc_hi=conv(re_["mu"] + stats.t.ppf(0.975, re_["k"] - 1) * re_["se"]),
                i2=dl["i2"], tau2=re_["tau2"])
R["paired_pool"] = {str(rc): paired_pool(rc) for rc in (0.25, 0.5, 0.75)}
ROB = {m["key"]: m["overall"] for m in meta}
R["paired_pool_high"] = paired_pool(0.5, lambda k: ROB[k] == "high")
R["paired_pool_not_high"] = paired_pool(0.5, lambda k: ROB[k] != "high")
R["paired_pool_keys"] = sorted({p_["key"] for p_ in paired if p_["diff"] is not None and any(e["key"] == p_["key"] and e["valid"] == "internal" and e["poolable"] for e in est)})
# trim-and-fill (Duval-Tweedie L0 estimator, missing studies on the left) for internal estimates
def trimfill(rows, side="left"):
    rows = [r for r in rows if r["poolable"]]
    y = np.array([r["theta"] for r in rows]); v = np.array([r["se_theta"] ** 2 for r in rows])
    def re_mu(y, v):
        w = 1 / v; fe = np.sum(w * y) / np.sum(w); q = np.sum(w * (y - fe) ** 2); c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
        t2 = max(0, (q - (len(y) - 1)) / c); ws = 1 / (v + t2); return np.sum(ws * y) / np.sum(ws), np.sqrt(1 / np.sum(ws)), t2
    sign = -1 if side == "left" else 1
    k0 = 0
    for _ in range(50):
        order = np.argsort(sign * y)  # most extreme on the opposite side are trimmed
        keep = order[: len(y) - k0] if k0 > 0 else order
        mu, _, _ = re_mu(y[np.sort(keep)], v[np.sort(keep)])
        dev = y - mu; ranks = stats.rankdata(np.abs(dev)); n = len(y)
        Tn = np.sum(ranks[np.sign(dev) == -sign])
        L0 = max(0, int(round((4 * Tn - n * (n + 1)) / (2 * n - 1))))
        if L0 == k0:
            break
        k0 = L0
    idx = np.argsort(-sign * y)[:k0]  # the k0 most extreme on the heavy side are mirrored
    yf = np.concatenate([y, 2 * mu - y[idx]]); vf = np.concatenate([v, v[idx]])
    mu_f, se_f, _ = re_mu(yf, vf)
    return dict(k0=k0, auc=inv(mu_f), lo=inv(mu_f - Z * se_f), hi=inv(mu_f + Z * se_f))
R["trimfill_internal"] = trimfill(internal)
# counts used in the text
keys = [m["key"] for m in meta]
R["counts"] = dict(
    n_studies=len(meta), n_estimates=len(est), n_pooled_estimates=sum(1 for s in est if s["poolable"]),
    n_external=len({s["key"] for s in est if s["valid"] == "external"}),
    n_dp_unclear=len({s["key"] for s in est if s["decision"] == "unclear"} - {s["key"] for s in est if s["decision"] != "unclear"}),
    n_abstract=sum(1 for m in meta if m["source"] == "abstract"),
    n_rob_low=sum(1 for m in meta if m["overall"] == "low"), n_rob_unclear=sum(1 for m in meta if m["overall"] == "unclear"),
    n_rob_high=sum(1 for m in meta if m["overall"] == "high"),
    n_cal=sum(1 for m in meta if m["m"][3] not in ("No", "None", "n.a.", "Not reported")),
    n_cal_slope=sum(1 for m in meta if "slope" in m["m"][3].lower()),
    n_cal_quant=sum(1 for m in meta if any(w in m["m"][3].lower() for w in ("brier", "ece", "ibs", "slope"))),
    n_dca=sum(1 for m in meta if m["m"][4].startswith("Yes") or m["m"][4].startswith("Application")),
    n_code=sum(1 for m in meta if m["m"][6].startswith("Code")),
    n_lr_fitted=len(paired),
    n_studies_pooled=len({s["key"] for s in est if s["poolable"]}),
    analysis_domain_high=sum(1 for m in meta if m["rob"][3] == "high"),
    n_since_2024=sum(1 for m in meta if re.search(r"20(2[4-9])", m["label"])),
)
out = ROOT / "build"; (out / "figs").mkdir(parents=True, exist_ok=True)
(out / "ma_results.json").write_text(json.dumps(R, indent=1))
print("metareg", json.dumps(R["metareg"])); print("metareg_size", json.dumps(R["metareg_size"])); print("paired_pool", json.dumps(R["paired_pool"])); print("pp_high", json.dumps(R["paired_pool_high"])); print("pp_not", json.dumps(R["paired_pool_not_high"])); print("ppkeys", R["paired_pool_keys"]); print("trimfill", R["trimfill_internal"])
sup = ROOT / "supplement"; sup.mkdir(exist_ok=True)
with open(sup / "S4_meta_analysis_estimates.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["study", "key", "decision", "validation", "auc", "lo", "hi", "ci_source", "se_method", "eval_n", "events", "logit_auc", "se_logit", "pooled",
                "in_internal", "in_external", "in_overall", "risk_of_bias", "source"])
    ids = lambda L: {id(x) for x in L}
    I, E, O = ids(internal), ids(external), ids(overall)
    for s in est:
        ev = s.get("events") or (round(0.40 * s["evalN"]) if s["se"] == "hm_assumed" and s.get("evalN") else None)
        w.writerow([s["label"], s["key"], s["decision"], s["valid"], s["auc"], s.get("lo"), s.get("hi"), s["ci_source"], s["se"], s.get("evalN"), ev, round(s["theta"], 4),
                    None if s["se_theta"] is None else round(s["se_theta"], 4), s["poolable"], id(s) in I, id(s) in E, id(s) in O, s["overall"], s["source"]])

# ---------------------------------------------------------------- forest plot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
plt.rcParams.update({"font.family": "DejaVu Sans"})
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1f2328", "#59636e", "#d0d7de"
DPN = {"pre_treatment": "before treatment", "post_stimulation": "after stimulation", "pre_transfer": "before transfer",
       "post_cycle": "after a complete cycle", "unclear": "not stated", "post_transfer": "after pregnancy test"}
def shown(valid):
    sel = [s for s in est if s["valid"] == valid]
    chosen = internal if valid == "internal" else external
    cid = {id(x) for x in chosen}
    rows = [s for s in sel if id(s) in cid]
    # studies with no poolable estimate of this design: show their earliest estimate, marked not pooled
    have = {s["key"] for s in rows}
    for s in sorted(sel, key=lambda x: DP_ORDER[x["decision"]]):
        if s["key"] not in have:
            rows.append(s); have.add(s["key"])
    return sorted(rows, key=lambda s: (not s["poolable"], s["auc"]))
blocks = [("External or temporal validation", "external", BLUE, "o"), ("Internal validation only", "internal", ORANGE, "D")]
rows = []
for title, g, col, mk in blocks:
    rows.append(("header", title))
    for s in shown(g):
        rows.append(("est", s, col, mk))
    rows.append(("pool", R[g], col))
    rows.append(("gap", None))
rows = rows[:-1]
RH = 0.160
fig_h = RH * len(rows) + 1.0
fig, ax = plt.subplots(figsize=(7.2, fig_h))
ax.set_xlim(0.40, 1.0); ax.set_ylim(len(rows) - 0.4, -0.7)
for x in np.arange(0.5, 1.01, 0.1):
    ax.axvline(x, color=GRID, lw=0.6, zorder=0)
ax.axvline(0.5, color=MUTED, lw=0.8, zorder=0)
for i, r in enumerate(rows):
    if r[0] == "header":
        ax.text(-0.02, i, r[1], ha="right", va="center", fontsize=7.6, fontweight="bold", color=INK, transform=ax.get_yaxis_transform())
    elif r[0] == "est":
        s, col, mk = r[1], r[2], r[3]
        showtag = s.get("tag") and s["key"] != "guo2026" and not re.search(r"before first cycle|pre-treatment|pre-ART|stage", s["tag"])
        name = f"{label(s)}, {DPN[s['decision']]}" + (f" ({s['tag']})" if showtag else "")
        if s["source"] == "abstract":
            name += "\u2020"
        if s["key"] in REBALANCED:
            name += " \u00a7"
        ax.text(-0.02, i, name, ha="right", va="center", fontsize=6.3, color=INK if s["poolable"] else MUTED, transform=ax.get_yaxis_transform())
        if s["se_theta"]:
            ax.plot([s["lo"], min(s["hi"], 0.999)], [i, i], color=col if s["poolable"] else MUTED, lw=1.2, solid_capstyle="round", zorder=2)
        hollow = s["overall"] == "high"
        c = col if s["poolable"] else MUTED
        ax.plot(s["auc"], i, marker=mk, ms=4.6 if mk == "o" else 4.0, mfc="white" if hollow else c, mec=c, mew=1.1, zorder=3)
        if s["poolable"]:
            txt = f"{s['auc']:.3f} ({s['lo']:.3f}\u2013{s['hi']:.3f})"
        elif s["decision"] == "post_transfer":
            txt = f"{s['auc']:.3f} (not pooled: after test)"
        else:
            txt = f"{s['auc']:.3f} (not pooled: no variance)"
        ax.text(1.01, i, txt, ha="left", va="center", fontsize=6.0, color=MUTED, transform=ax.get_yaxis_transform())
    elif r[0] == "pool":
        p, col = r[1], r[2]
        ax.text(-0.02, i, f"Random-effects summary (k = {p['k']}; I\u00b2 = {100 * p['i2']:.0f}%)", ha="right", va="center", fontsize=6.6,
                fontweight="bold", color=INK, transform=ax.get_yaxis_transform())
        if "pi_lo" in p:
            ax.plot([max(p["pi_lo"], 0.401), p["pi_hi"]], [i, i], color=INK, lw=0.9, ls=(0, (2, 1.5)), zorder=2)
        d = 0.36
        ax.fill([p["lo"], p["auc"], p["hi"], p["auc"]], [i, i - d, i, i + d], color=col, alpha=0.95, zorder=3, lw=0)
        ax.text(1.01, i, f"{p['auc']:.3f} ({p['lo']:.3f}\u2013{p['hi']:.3f})", ha="left", va="center", fontsize=6.2, fontweight="bold",
                color=INK, transform=ax.get_yaxis_transform())
ax.set_yticks([]); ax.set_xticks(np.arange(0.5, 1.01, 0.1))
ax.tick_params(axis="x", labelsize=7, colors=MUTED, length=2)
for sp in ["left", "right", "top"]:
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.set_xlabel("AUC for live birth (95% CI)", fontsize=7.5, color=INK)
ax.text(1.01, -0.7, "AUC (95% CI)", ha="left", va="center", fontsize=6.4, color=MUTED, transform=ax.get_yaxis_transform())
handles = [Line2D([], [], marker="o", ls="", mfc=BLUE, mec=BLUE, ms=4.6, label="External or temporal"),
           Line2D([], [], marker="D", ls="", mfc=ORANGE, mec=ORANGE, ms=4.0, label="Internal only"),
           Line2D([], [], marker="o", ls="", mfc="white", mec=INK, ms=4.6, label="High risk of bias (hollow)"),
           Line2D([], [], marker="o", ls="", mfc=MUTED, mec=MUTED, ms=4.6, label="Shown, not pooled (grey)"),
           Line2D([], [], color=INK, lw=0.9, ls=(0, (2, 1.5)), label="95% prediction interval")]
fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=6.0, frameon=False, handletextpad=0.3, columnspacing=1.0,
           bbox_to_anchor=(0.5, 0.0))
fig.subplots_adjust(left=0.37, right=0.80, top=1 - 0.12 / fig_h, bottom=0.62 / fig_h)
fig.savefig(out / "figs" / "fig_forest.pdf")
fig.savefig(out / "figs" / "fig_forest_preview.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------- taxonomy: model family x decision point x validation design
FAM = ["Regression", "Bagged trees", "Boosted trees", "Kernel methods", "Neural networks", "Ensembles", "Discrete-time survival",
       "Centre-specific", "Foundation and language models"]
FAMDESC = {"Regression": "LR selected over ML", "Bagged trees": "random forest", "Boosted trees": "GBM, XGBoost, LightGBM, CatBoost",
           "Kernel methods": "SVM", "Neural networks": "MLP, transformer", "Ensembles": "stacking, weighted, selected",
           "Discrete-time survival": "BART, RF over cycles", "Centre-specific": "per-clinic models",
           "Foundation and language models": "TabPFN, LLMs"}
COLS = ["pre_treatment", "post_stimulation", "pre_transfer", "post_cycle", "post_transfer", "unclear"]
COLN = ["Before\ntreatment", "After\nstimulation", "Before\ntransfer", "After a\ncomplete cycle", "After\npregnancy test", "Not\nstated"]
fam_of = {m["key"]: m["family"] for m in meta}
cell = {}
for s in est:
    cell.setdefault((fam_of[s["key"]], s["decision"]), {}).setdefault(s["key"], []).append(s)
LH = 0.165  # height of one entry line (axis units)
nx = len(COLS); x0 = 1.95
UNIT_IN = 7.2 * 0.98 / (x0 + nx)
AVAIL_IN = (0.94 - 0.17) * UNIT_IN
def entries(f, c):
    out = []
    for k, ss in cell.get((f, c), {}).items():
        ext = [s for s in ss if s["valid"] == "external"]
        show = ext[0] if ext else ss[0]
        lab = labels.get(bibkey_of.get(k, k), ss[0]["label"])
        mm = re.match(r"(.+?)(?: et al\.| and .+?)? \((\d{4}[a-z]?)\)", lab)
        nm, yr = (mm.group(1), mm.group(2)) if mm else (ss[0]["label"], "")
        txt = f"{nm} {yr}: {show['auc']:.2f}"
        # long labels wrap after the name so that no label crosses its cell border
        wrap = len(txt) * 0.0076 * 4.8 > AVAIL_IN
        out.append(dict(lines=[nm, f"{yr}: {show['auc']:.2f}"] if wrap else [txt], auc=show["auc"], ext=bool(ext), hi=ss[0]["overall"] == "high"))
    return sorted(out, key=lambda e: e["auc"])
def n_items(f):
    return max([sum(len(e["lines"]) for e in entries(f, c)) for c in COLS] + [1])
heights = [max(0.62, 0.22 + LH * n_items(f)) for f in FAM]
tops = np.concatenate([[0], np.cumsum(heights)])
fig, ax = plt.subplots(figsize=(7.2, 0.62 + 0.62 * tops[-1]))
ax.set_xlim(0, x0 + nx); ax.set_ylim(tops[-1] + 0.05, -0.75); ax.axis("off")
for j, c in enumerate(COLN):
    ax.text(x0 + j + 0.5, -0.38, c, ha="center", va="center", fontsize=6.8, fontweight="bold", color=INK, linespacing=1.05)
FAMSHOW = {"Foundation and language models": "Foundation models"}
FAMDESC["Foundation and language models"] = "tabular foundation models, LLMs"
for i, f in enumerate(FAM):
    y0, hgt = tops[i], heights[i]
    n_st = len({m["key"] for m in meta if m["family"] == f})
    ax.add_patch(plt.Rectangle((0.02, y0 + 0.04), x0 - 0.1, hgt - 0.08, fc="#f3f5f7", ec="#c9ced3", lw=0.5))
    ax.text(0.1, y0 + hgt / 2 - 0.1, FAMSHOW.get(f, f) + f"  ({n_st})", ha="left", va="center", fontsize=6.7, fontweight="bold", color=INK)
    ax.text(0.1, y0 + hgt / 2 + 0.12, FAMDESC[f], ha="left", va="center", fontsize=5.9, color=MUTED)
    if f == "Foundation and language models":
        ax.add_patch(plt.Rectangle((x0 + 0.03, y0 + 0.04), nx - 0.06, hgt - 0.08, fc="white", ec=GRID, lw=0.5))
        ax.text(x0 + nx / 2, y0 + hgt / 2, "No eligible peer-reviewed study evaluated a tabular foundation model or a language model for live birth",
                ha="center", va="center", fontsize=6.0, color=MUTED)
        continue
    for j, c in enumerate(COLS):
        ax.add_patch(plt.Rectangle((x0 + j + 0.03, y0 + 0.04), 0.94, hgt - 0.08, fc="white", ec=GRID, lw=0.5))
        row = 0
        for e in entries(f, c):
            cx = x0 + j + 0.1; cy = y0 + 0.2 + row * LH
            col = BLUE if e["ext"] else ORANGE
            ax.plot(cx, cy, marker="o" if e["ext"] else "D", ms=2.8 if e["ext"] else 2.5, mfc="white" if e["hi"] else col, mec=col, mew=0.7)
            for ln in e["lines"]:
                ax.text(cx + 0.06, y0 + 0.2 + row * LH, ln, ha="left", va="center", fontsize=4.8, color=INK)
                row += 1
        if f == "Centre-specific" and j == 0:
            ax.text(x0 + j + 0.5, y0 + hgt / 2, "Yao 2025: ROC AUC\nnot extracted", ha="center", va="center", fontsize=4.9, color=MUTED, linespacing=1.0)
h = [Line2D([], [], marker="o", ls="", mfc=BLUE, mec=BLUE, ms=4, label="External or temporal AUC"),
     Line2D([], [], marker="D", ls="", mfc=ORANGE, mec=ORANGE, ms=3.6, label="Internal AUC only"),
     Line2D([], [], marker="o", ls="", mfc="white", mec=INK, ms=4, label="High risk of bias (hollow)")]
fig.legend(handles=h, loc="lower center", ncol=3, fontsize=6.4, frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.30 / fig.get_size_inches()[1])
fig.savefig(out / "figs" / "fig_taxonomy.pdf"); fig.savefig(out / "figs" / "fig_taxonomy_preview.png", dpi=170)

fmt = lambda p: None if p is None else (round(p["auc"], 3), round(p["lo"], 3), round(p["hi"], 3), p["k"],
                                         round(p.get("pi_lo", float("nan")), 3), round(p.get("pi_hi", float("nan")), 3), round(100 * p["i2"]))
for k, v in R.items():
    if isinstance(v, dict) and "auc" in v and "i2" in v:
        print(f"{k:30s}", fmt(v))
print("p int vs ext", round(R["p_int_vs_ext"], 4), "p high vs not", round(R["p_high_vs_not"], 4))
print("egger", R["egger_internal"])
print("paired ML-LR", R["paired_ml_lr"], R["paired_ml_lr_summary"])
print("int->ext pairs", R["paired_int_ext"])
print("counts", R["counts"])
