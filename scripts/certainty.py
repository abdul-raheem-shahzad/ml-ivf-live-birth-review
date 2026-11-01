"""Certainty of the main pooled findings, GRADE adapted for prognostic evidence (Iorio et al. 2015).
Writes supplement/S9_certainty_of_evidence.csv from build/ma_results.json. Judgements are the author's."""
import csv, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
R = json.loads((ROOT / "build" / "ma_results.json").read_text())
f = lambda a: f"{a['auc']:.3f} ({a['lo']:.3f}-{a['hi']:.3f}); PI {a['pi_lo']:.3f}-{a['pi_hi']:.3f}"
w = R["within_pairs"]; pp = R["paired_pool"]["0.5"]; mr = [c for c in R["metareg"]["coef"] if c["name"] == "dp_unstated"][0]
nh = lambda keys: sum(1 for k in keys if k)  # placeholder
rows = [
 ["AUC of models validated on a later period or another centre", f"{R['external']['k']} studies", f(R["external"]),
  "Serious: 6 of 9 at high overall risk of bias", f"Serious: I2 {round(100*R['external']['i2'])}%, wide prediction interval",
  "Not serious (endpoint mix counted under inconsistency)", "Not serious", "Not detected (few studies)", "Low"],
 ["AUC of models validated only internally", f"{R['internal']['k']} studies", f(R["internal"]),
  "Very serious: most at high risk of bias; best-of-several selection", f"Very serious: I2 {round(100*R['internal']['i2'])}%",
  "Not serious (endpoint mix counted under inconsistency)", "Not serious", f"Not detected (effective-sample-size test p = {R['ess_test_internal']['p']:.2f})", "Very low"],
 ["Change from internal to external validation within the same study", f"{w['k']} studies",
  f"{w['auc_d']:+.3f} AUC ({w['auc_lo']:+.3f} to {w['auc_hi']:+.3f}) at an internal AUC of 0.80",
  "Serious: 6 of 7 at high overall risk of bias", "Serious: changes range from -0.19 to +0.02", "Not serious", "Serious: interval includes no change", "Not assessed (k < 10)", "Very low"],
 ["Higher AUC when the decision point is not stated (meta-regression)", f"{R['metareg']['k']} studies",
  f"+{mr['b']:.2f} logit AUC ({mr['lo']:.2f} to {mr['hi']:.2f}); permutation p = {R['metareg_perm']['dp_unstated']:.3f}",
  "Serious: between-study comparison; confounded by design", "Serious: I2 above 99% among the 9 studies without a stated decision point", "Not serious", "Not serious", "Not applicable", "Low"],
 ["Gain of the best machine-learning model over logistic regression on the same data", f"{pp['k']} studies",
  f"+{pp['auc_d']:.3f} AUC ({pp['auc_lo']:.3f} to {pp['auc_hi']:.3f}) at a logistic-regression AUC of 0.75",
  "Very serious: 13 of 16 at high risk of bias; tuned learners against untuned regression", f"Serious: I2 {round(100*pp['i2'])}%",
  "Not serious", "Not serious", "Not assessed", "Very low"],
]
# certainty starts high for cohort-based prognostic evidence and is lowered one level per serious and two per very serious concern
hdr = ["Finding", "Evidence", "Estimate (95% CI)", "Risk of bias", "Inconsistency", "Indirectness", "Imprecision", "Publication bias", "Certainty"]
with open(ROOT / "supplement" / "S9_certainty_of_evidence.csv", "w", newline="") as fh:
    wr = csv.writer(fh); wr.writerow(hdr); wr.writerows(rows)
(ROOT / "build" / "certainty.json").write_text(json.dumps(dict(header=hdr, rows=rows), indent=1))
print("ok")
