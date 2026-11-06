"""Step 7b: Zindi submission files (late submissions are still scored, 10 a day). Run from the repo root.

Zindi scores F1 on 0/1 labels (1 = predicted default), which is NOT our business rule: F1 balances catching
defaulters against false alarms, while our cost cut-off (2.1% / 3.2%) accepts many false alarms because a missed
defaulter costs 47x more. So we submit both, and an F1-tuned LightGBM to see whether the leaderboard (mostly 2022
loans, like a shuffled test) rewards a different model than our future-loan test did.
Files go to data/submissions/ (ignored: loan-level predictions are never committed); the summary goes to
learnings/tables/07b_zindi_submissions.csv, where the Zindi scores are filled in by hand after uploading.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.pipeline import make_pipeline

from src.features import build, DEFAULT_CLUES, FEATURES, GHANA_CLUES, preprocessor
from src.classification_experiments import final_model, SEED

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "submissions"


def best_f1(y, p):
    """The cut-off with the highest F1 on out-of-fold scores."""
    ts = np.unique(np.quantile(p, np.linspace(.5, .999, 400)))
    f = [f1_score(y, p > t) for t in ts]
    return float(ts[int(np.argmax(f))]), float(max(f))


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    tr, te = build(str(ROOT / "data" / "zindi"))
    X, y, ghana = tr[FEATURES], tr.target.astype(int), (te.country_id == "Ghana").to_numpy()
    cv = list(StratifiedGroupKFold(5, shuffle=True, random_state=SEED).split(X, y, tr.customer_id))
    lgbm = make_pipeline(preprocessor(FEATURES), LGBMClassifier(n_estimators=180, learning_rate=.05, num_leaves=15,
                         min_child_samples=80, verbosity=-1, random_state=SEED, n_jobs=4))
    # Out-of-fold scores (customer folds) to pick F1 cut-offs; the LR one reuses the final model's recipe.
    lr_oof = np.empty(len(X))
    for a, b in cv:
        lr_oof[b] = final_model(tr.iloc[a]).predict_proba(X.iloc[b])[:, 1]
    oof = {"LR + Platt": lr_oof, "LightGBM": cross_val_predict(lgbm, X, y, cv=cv, method="predict_proba")[:, 1]}
    yo = y.to_numpy()
    test = {"LR + Platt": final_model(tr).predict_proba(te[FEATURES])[:, 1],
            "LightGBM": lgbm.fit(X, y).predict_proba(te[FEATURES])[:, 1]}
    cost = np.where(ghana, .032, .021)
    plans = [("A_lr_cost_cutoff", "LR + Platt", "cost cut-off 2.1% Kenya / 3.2% Ghana (our decision)", cost),
             ("B_lr_best_f1", "LR + Platt", "best F1 on customer folds", None),
             ("C_lgbm_best_f1", "LightGBM", "best F1 on customer folds", None)]
    rows = []
    for name, model, rule, t in plans:
        if t is None:
            t, f = best_f1(yo, oof[model])
        else:
            f = f1_score(yo, oof[model] > np.full(len(yo), .021))  # Kenya cut-off on the (Kenyan) training rows
        pred = (test[model] > t).astype(int)
        pd.DataFrame({"ID": te.ID, "target": pred}).to_csv(OUT / f"{name}.csv", index=False)
        rows.append(dict(file=f"{name}.csv", model=model, rule=rule, threshold=float(np.max(t)) if np.ndim(t) else t,
                         oof_f1_customer_folds=round(f, 4), flagged_kenya=round(pred[~ghana].mean(), 4),
                         flagged_ghana=round(pred[ghana].mean(), 4), zindi_public="", zindi_private=""))
    s = pd.DataFrame(rows)
    path = ROOT / "learnings" / "tables" / "07b_zindi_submissions.csv"
    if path.exists():  # keep scores already typed in by hand
        old = pd.read_csv(path, dtype=str).set_index("file")[["zindi_public", "zindi_private"]]
        s = s.set_index("file"); s.update(old); s = s.reset_index()
    s.to_csv(path, index=False)
    sample = pd.read_csv(ROOT / "data" / "zindi" / "SampleSubmission.csv")
    for name, *_ in plans:
        sub = pd.read_csv(OUT / f"{name}.csv")
        assert list(sub.columns) == list(sample.columns) and set(sub.ID) == set(sample.ID) and sub.target.isin([0, 1]).all()
    print(s.to_string(index=False))


def ghana_probe():
    """Group-level evidence on Ghana. Each file flags one Ghanaian group and nobody else, so F1 = 2 x defaults in the group / (group size + all defaults).
    The all-flagged file gives all defaults. Upload them and read off default rates per group, never per person. Kenyan rows stay unflagged."""
    tr, te = build(str(ROOT / "data" / "zindi"))
    gh = te.country_id == "Ghana"; first = te.n_prev_loans == 0
    groups = {"G0_everyone": pd.Series(True, index=te.index), "G1_ghana_all": gh, "G2_ghana_first_loans": gh & first, "G3_ghana_earlier_loans": gh & ~first,
              "G4_ghana_type_3": gh & (te.loan_type == "Type_3"), "G5_ghana_type_2": gh & (te.loan_type == "Type_2"), "G6_ghana_over_90_days": gh & (te.duration > 90)}
    for name, clues in {"G7_ghana_13_clues_flagged": FEATURES, "G8_ghana_no_type_flagged": [c for c in FEATURES if c != "loan_type"], "G9_ghana_final_flagged": GHANA_CLUES}.items():
        groups[name] = gh & (final_model(tr, clues).predict_proba(te[FEATURES])[:, 1] > .032)
    rows = []
    for name, mask in groups.items():
        pd.DataFrame({"ID": te.ID, "target": mask.astype(int)}).to_csv(OUT / f"{name}.csv", index=False)
        rows.append(dict(file=f"{name}.csv", flagged=int(mask.sum()), zindi_public="", zindi_private=""))
    s = pd.DataFrame(rows); path = ROOT / "learnings" / "tables" / "11b_ghana_probe.csv"
    if path.exists():  # keep scores already typed in by hand
        old = pd.read_csv(path, dtype=str).set_index("file")[["zindi_public", "zindi_private"]]
        s = s.set_index("file"); s.update(old); s = s.reset_index()
    s.to_csv(path, index=False)
    print(s.to_string(index=False))


def ghana_probe_2():
    """Second batch, for the questions the first one opened (learnings/11 section 10). Same method; H0 is the Type_3 / first-loan overlap."""
    tr, te = build(str(ROOT / "data" / "zindi"))
    gh = te.country_id == "Ghana"; first = te.n_prev_loans == 0; t3 = gh & (te.loan_type == "Type_3")
    p13 = pd.Series(final_model(tr, FEATURES).predict_proba(te[FEATURES])[:, 1], index=te.index)
    pok = pd.Series(final_model(tr, DEFAULT_CLUES).predict_proba(te[FEATURES])[:, 1], index=te.index)
    mapped = te.assign(loan_type=te.loan_type.where(te.loan_type.isin(set(tr.loan_type)), "Type_1"))
    pmap = pd.Series(final_model(tr, FEATURES).predict_proba(mapped[FEATURES])[:, 1], index=te.index)
    pfin = pd.Series(final_model(tr, GHANA_CLUES).predict_proba(te[FEATURES])[:, 1], index=te.index)
    edges = p13[t3].quantile([.2, .4, .6, .8]).to_numpy()
    band = pd.cut(p13, [-np.inf, *edges, np.inf], labels=False)
    groups = {"H0_type_3_first_loans": t3 & first, "H1_type_2_first_loans": gh & (te.loan_type == "Type_2") & first,
              "H2_ghana_keep_type_no_often_flagged": gh & (pok > .032), "H3_ghana_unseen_as_type_1_flagged": gh & (pmap > .032),
              "H4_type_3_final_flagged": t3 & (pfin > .032), "H5_type_3_13_clues_flagged": t3 & (p13 > .032)}
    for b in range(4):
        groups[f"H{6 + b}_type_3_risk_band_{b + 1}_of_5"] = t3 & (band == b)
    rows = []
    for name, mask in groups.items():
        pd.DataFrame({"ID": te.ID, "target": mask.astype(int)}).to_csv(OUT / f"{name}.csv", index=False)
        rows.append(dict(file=f"{name}.csv", flagged=int(mask.sum()), zindi_public="", zindi_private=""))
    s = pd.DataFrame(rows); path = ROOT / "learnings" / "tables" / "11b_ghana_probe_2.csv"
    if path.exists():
        old = pd.read_csv(path, dtype=str).set_index("file")[["zindi_public", "zindi_private"]]
        s = s.set_index("file"); s.update(old); s = s.reset_index()
    s.to_csv(path, index=False)
    print(s.to_string(index=False))


def read_probe(fn=2716, fp=90, n=18594, n_ghana=3525):
    """Turn the uploaded scores into default rates. F1 = 2 x defaults in the group / (group size + all defaults), and flagging everyone gives all defaults.
    Assumes Zindi's public and private parts are random samples. Checks: first + earlier loans must add up to Ghana, and Kenya must look like the training data."""
    s = pd.read_csv(ROOT / "learnings" / "tables" / "11b_ghana_probe.csv")
    s["group"] = s.file.str.replace(".csv", "").str[3:]; s = s.set_index("group")
    rows, costs = [], []
    for part in ("zindi_public", "zindi_private"):
        f = s[part].astype(float); P = f["everyone"] * n / (2 - f["everyone"]); d = f * (s.flagged + P) / 2; G = d["ghana_all"]
        assert abs(d["ghana_first_loans"] + d["ghana_earlier_loans"] - G) < 5 and .015 < (P - G) / (n - n_ghana) < .021, part
        rows.append(pd.DataFrame({"part": part, "flagged": s.flagged, "defaults": d, "default rate": d / s.flagged, "share of Ghana's defaults": d / G}))
        rows.append(pd.DataFrame({"part": part, "flagged": [n - n_ghana], "defaults": [P - G], "default rate": [(P - G) / (n - n_ghana)], "share of Ghana's defaults": [np.nan]}, index=["KENYA (everyone minus Ghana)"]))
        policy = {"approve everyone": (0, 0.), "13 clues at 3.2%": (s.flagged["ghana_13_clues_flagged"], d["ghana_13_clues_flagged"]),
                  "no loan_type at 3.2%": (s.flagged["ghana_no_type_flagged"], d["ghana_no_type_flagged"]),
                  "no loan_type, no 'borrow often' at 3.2%": (s.flagged["ghana_final_flagged"], d["ghana_final_flagged"]), "decline everyone": (n_ghana, G)}
        for name, (k, tp) in policy.items():
            costs.append({"part": part, "policy": name, "declined": k / n_ghana, "defaults caught": tp / G, "default rate if declined": tp / k if k else np.nan,
                          "default rate if approved": (G - tp) / (n_ghana - k) if k < n_ghana else np.nan, "cost per applicant (GHS)": ((G - tp) * fn + (k - tp) * fp) / n_ghana})
    t, c = pd.concat(rows).rename_axis("group"), pd.DataFrame(costs)
    t.to_csv(ROOT / "learnings" / "tables" / "11b_ghana_rates.csv"); c.to_csv(ROOT / "learnings" / "tables" / "11b_ghana_costs.csv", index=False)
    print(t.round(3).to_string()); print(c.round(3).to_string())


if __name__ == "__main__":
    import sys
    (ghana_probe if "--ghana-probe" in sys.argv else ghana_probe_2 if "--ghana-probe-2" in sys.argv else read_probe if "--read-probe" in sys.argv else run)()
