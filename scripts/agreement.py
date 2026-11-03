"""Inter-rater agreement between the author's original PROBAST+AI ratings and two independent second appraisals,
and the adjudicated final ratings.

Inputs : content/rob_original.json (author's ratings before adjudication), content/studies.js via content/studies_meta.json
         (final ratings), content/adjudication_log.csv, supplement/second_appraisals/rater{A,B}/second_assessor_ratings.csv
Outputs: supplement/S7_inter_rater_agreement.csv, supplement/S8_second_appraisals_and_adjudication.csv, build/agreement.json
Statistics: raw agreement, Cohen's kappa (unweighted) and Gwet's AC1 over the three categories low / unclear / high;
a study that a rater did not rate is left out of that rater's comparisons.
"""
import csv, json, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATS = ["low", "unclear", "high"]
DOMS = ["Participants", "Predictors", "Outcome", "Analysis", "Overall"]


def norm(x):
    return unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().lower().replace("-", " ").strip()


# Study labels whose year was corrected after the second appraisals were made (online 2023, journal issue 2024).
ALIAS = {"mourad 2024": "mourad 2023"}


def load_rater(p):
    out = {}
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        out[norm(r["Study"])] = [r[f].strip().lower() for f in ["D1", "D2", "D3", "D4", "Overall"]]
    return out


def stats(x, y):
    P = [(a, b) for a, b in zip(x, y) if a in CATS and b in CATS]
    n = len(P)
    po = sum(a == b for a, b in P) / n
    pa = {c: sum(a == c for a, _ in P) / n for c in CATS}
    pb = {c: sum(b == c for _, b in P) / n for c in CATS}
    pe = sum(pa[c] * pb[c] for c in CATS)
    kappa = (po - pe) / (1 - pe)
    pi = {c: (pa[c] + pb[c]) / 2 for c in CATS}
    pe_g = sum(pi[c] * (1 - pi[c]) for c in CATS) / (len(CATS) - 1)
    ac1 = (po - pe_g) / (1 - pe_g)
    return {"n": n, "agreement": round(po, 2), "kappa": round(kappa, 2), "ac1": round(ac1, 2)}


orig = json.loads((ROOT / "content" / "rob_original.json").read_text())
final = {m["key"]: m for m in json.loads((ROOT / "content" / "studies_meta.json").read_text())}
A = load_rater(ROOT / "supplement" / "second_appraisals" / "raterA" / "second_assessor_ratings.csv")
B = load_rater(ROOT / "supplement" / "second_appraisals" / "raterB" / "second_assessor_ratings.csv")
adj = {r["study_key"]: r["basis"] for r in csv.DictReader(open(ROOT / "content" / "adjudication_log.csv"))}

rows = []
for s in orig:
    k = norm(s["label"])
    f = final[s["key"]]
    rows.append(dict(key=s["key"], label=s["label"], au=s["rob"] + [s["overall"]],
                     A=A.get(k) or A.get(ALIAS.get(k, ""), ["not rated"] * 5), B=B.get(k) or B.get(ALIAS.get(k, ""), ["not rated"] * 5),
                     fin=f["rob"] + [f["overall"]], basis=adj.get(s["key"], "")))
assert len(rows) == 48

res = {}
pairs = {"author_vs_A": ("au", "A"), "author_vs_B": ("au", "B"), "A_vs_B": ("A", "B"),
         "final_vs_A": ("fin", "A"), "final_vs_B": ("fin", "B")}
for i, d in enumerate(DOMS):
    res[d] = {p: stats([r[x][i] for r in rows], [r[y][i] for r in rows]) for p, (x, y) in pairs.items()}
res["All four domains"] = {p: stats([r[x][i] for r in rows for i in range(4)], [r[y][i] for r in rows for i in range(4)])
                           for p, (x, y) in pairs.items()}
dist = {w: {c: sum(r[w][4] == c for r in rows) for c in CATS + ["not rated"]} for w in ("au", "A", "B", "fin")}
changed_dom = sum(r["au"][i] != r["fin"][i] for r in rows for i in range(4))
changed_ov = [r["key"] for r in rows if r["au"][4] != r["fin"][4]]
order = {c: j for j, c in enumerate(CATS)}
up = sum(order[r["fin"][4]] > order[r["au"][4]] for r in rows if r["key"] in changed_ov)
summary = dict(stats=res, overall_distribution=dist, changed_domain_judgements=changed_dom, changed_overall=len(changed_ov),
               changed_overall_upward=up, changed_overall_keys=changed_ov,
               not_rated={"A": [r["label"] for r in rows if r["A"][4] not in CATS], "B": [r["label"] for r in rows if r["B"][4] not in CATS]})
(ROOT / "build" / "agreement.json").write_text(json.dumps(summary, indent=1))

with open(ROOT / "supplement" / "S7_inter_rater_agreement.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Domain", "Comparison", "Studies compared", "Raw agreement", "Cohen's kappa", "Gwet's AC1"])
    lab = {"author_vs_A": "Original (first author) vs second appraisal A", "author_vs_B": "Original (first author) vs second appraisal B",
           "A_vs_B": "Second appraisal A vs B", "final_vs_A": "Final (adjudicated) vs A", "final_vs_B": "Final (adjudicated) vs B"}
    for d, v in res.items():
        for p, s in v.items():
            w.writerow([d, lab[p], s["n"], s["agreement"], s["kappa"], s["ac1"]])

with open(ROOT / "supplement" / "S8_second_appraisals_and_adjudication.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    hdr = ["Study", "Key"]
    for who in ("Original (first author)", "Appraisal A", "Appraisal B", "Final"):
        hdr += [f"{who}: {d}" for d in DOMS]
    w.writerow(hdr + ["Adjudication"])
    for r in rows:
        w.writerow([r["label"], r["key"]] + r["au"] + r["A"] + r["B"] + r["fin"] +
                   [r["basis"] or ("No change" if r["au"] == r["fin"] else "")])
print(json.dumps({k: summary[k] for k in summary if k != "stats"}, indent=0))
for d in ("All four domains", "Overall", "Participants"):
    print(d, res[d])
