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

from src.features import build, FEATURES, preprocessor
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


if __name__ == "__main__":
    run()
