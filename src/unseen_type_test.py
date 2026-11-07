"""Step 12: what should the scorer do with a loan type it has never seen, in Kenya? Hide each type from training, then treat its loans as new.
Options: trust the model, starter for all, decline all, approve all. Writes learnings/tables/12_unseen_loan_type.csv."""
from pathlib import Path
import numpy as np, pandas as pd
from src.classification_experiments import final_model
from src.features import DEFAULT_CLUES, FEATURES, build

ROOT = Path(__file__).resolve().parent.parent
FN, FP, START_DEFAULT, START_GOOD, CUT = 4700, 100, 650, 90, .021


def run():
    tr, _ = build(str(ROOT / "data" / "zindi")); rows = []
    types = [t for t, n in tr.loan_type.value_counts().items() if n >= 100 and t != "Type_1"]  # Type_1 is 90% of loans: hiding it leaves no model worth testing
    for t in types:
        out = tr.loan_type == t; hid = tr[out]; y = hid.target.astype(int).to_numpy()
        p = final_model(tr[~out], DEFAULT_CLUES).predict_proba(hid[FEATURES])[:, 1]; over = p > CUT
        rows.append(dict(loan_type=t, loans=len(hid), defaults=int(y.sum()), actual=y.mean(), mean_predicted=p.mean(), share_above_cutoff=over.mean(),
                         cost_model=(y[~over].sum() * FN + (1 - y[over]).sum() * FP) / len(y), cost_starter=(y.sum() * START_DEFAULT + (1 - y).sum() * START_GOOD) / len(y),
                         cost_decline=(1 - y).sum() * FP / len(y), cost_approve=y.sum() * FN / len(y)))
    d = pd.DataFrame(rows); w = d.loans / d.loans.sum()
    d.loc[len(d)] = dict(loan_type="ALL, weighted by loans", loans=d.loans.sum(), defaults=d.defaults.sum(), actual=d.defaults.sum() / d.loans.sum(), mean_predicted=(d.mean_predicted * w).sum(), share_above_cutoff=(d.share_above_cutoff * w).sum(),
                         **{c: (d[c] * w).sum() for c in ("cost_model", "cost_starter", "cost_decline", "cost_approve")})
    d.loc[len(d)] = dict(loan_type="ALL, each type counted equally", loans=len(types), actual=d.actual[:len(types)].mean(), mean_predicted=d.mean_predicted[:len(types)].mean(), share_above_cutoff=d.share_above_cutoff[:len(types)].mean(), **{c: d[c][:len(types)].mean() for c in ("cost_model", "cost_starter", "cost_decline", "cost_approve")})
    d.to_csv(ROOT / "learnings" / "tables" / "12_unseen_loan_type.csv", index=False)
    pd.set_option("display.width", 200); print(d.round(3).to_string(index=False))


if __name__ == "__main__":
    run()
