"""Step 7 add-on: bootstrap 95% ranges on F1 (at our 2.1% cut-off) and PR-AUC for every model and test.

Reads the saved out-of-fold predictions from src/classification_experiments.py (local, never committed),
resamples whole customers (repeat loans are not independent) and writes learnings/tables/07_f1_intervals.csv.
Each model is also compared with logistic regression on the same resamples (paired).
Run: PYTHONPATH=. .venv/bin/python src/f1_intervals.py
"""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score
from src.classification_experiments import LOCAL, TABLES, SEED

CUTOFF, REPS, REF = 0.021, 500, 'Logistic Regression'


def scores(y, p):
    return f1_score(y, (p > CUTOFF).astype(int), zero_division=0), average_precision_score(y, p)


def run():
    oof = pd.read_csv(LOCAL / 'oof_predictions.csv')
    rows = []
    for scheme, s in oof.groupby('scheme'):
        wide = s.pivot(index='ID', columns='model', values='probability')
        meta = s.drop_duplicates('ID').set_index('ID').loc[wide.index, ['customer_id', 'target']]
        y = meta.target.to_numpy()
        groups = list(meta.reset_index().groupby('customer_id', sort=False).indices.values())
        rng = np.random.default_rng(SEED)
        draws = [np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))]) for _ in range(REPS)]
        boot = {m: np.array([scores(y[d], wide[m].to_numpy()[d]) for d in draws]) for m in wide.columns}
        for m in wide.columns:
            f1, pr = scores(y, wide[m].to_numpy())
            lo, hi = np.quantile(boot[m], [.025, .975], axis=0)
            dlo, dhi = np.quantile(boot[m] - boot[REF], [.025, .975], axis=0)
            rows.append(dict(test=scheme, model=m, loans=len(y), defaults=int(y.sum()),
                             f1=f1, f1_low=lo[0], f1_high=hi[0], pr_auc=pr, pr_auc_low=lo[1], pr_auc_high=hi[1],
                             f1_minus_lr_low=dlo[0], f1_minus_lr_high=dhi[0],
                             pr_auc_minus_lr_low=dlo[1], pr_auc_minus_lr_high=dhi[1]))
    out = pd.DataFrame(rows).round(4)
    out.to_csv(TABLES / '07_f1_intervals.csv', index=False)
    print(out.to_string(index=False))


if __name__ == '__main__':
    run()
