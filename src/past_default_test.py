"""Step 12: the scorer approved a made-up borrower who had defaulted on all 3 earlier loans. Is that real? Does a rule for past defaulters help?
Honest scores: each loan is scored by a model that never saw its customer (fold_customer), or only older loans (time_block). Writes learnings/tables/12_past_default*.csv."""
from pathlib import Path
import numpy as np, pandas as pd
from src.classification_experiments import final_model
from src.features import DEFAULT_CLUES, FEATURES, build
from src.reasons import _parts, _prepared

ROOT = Path(__file__).resolve().parent.parent; T = ROOT / "learnings" / "tables"
FN, FP, CUT, START_D, START_G = 4700, 100, .021, 650, 90


def boot(d, f, n=1000, seed=553):
    """Customer bootstrap of the cost change."""
    rng = np.random.default_rng(seed); g = [x.to_numpy() for _, x in d.groupby("customer_id")["v"]]; c = np.array([x.sum() for x in g]); k = np.array([len(x) for x in g]); s = []
    for _ in range(n):
        i = rng.integers(0, len(g), len(g)); s.append(c[i].sum() / k[i].sum())
    return np.quantile(s, [.025, .975])


def run():
    tr, te = build(str(ROOT / "data" / "zindi")); out = tr.assign(p=np.nan, p_t=np.nan); y = tr.target.astype(int)
    for f in sorted(tr.fold_customer.unique()):
        m = tr.fold_customer == f; out.loc[m, "p"] = final_model(tr[~m], DEFAULT_CLUES).predict_proba(tr[m][FEATURES])[:, 1]
    print("time blocks", sorted(tr.time_block.unique()))
    blocks = sorted(b for b in tr.time_block.unique() if b >= 0)
    for b in blocks[1:]:
        m = tr.time_block == b; old = tr.disbursement_date < tr.disbursement_date[m].min(); out.loc[m, "p_t"] = final_model(tr[old], DEFAULT_CLUES).predict_proba(tr[m][FEATURES])[:, 1]
    rows = []
    groups = {"no past default": tr.n_defaults == 0, "1+ past defaults": tr.n_defaults > 0, "1 past default": tr.n_defaults == 1, "2+ past defaults": tr.n_defaults >= 2, "past default rate 50%+": tr.past_default_rate >= .5, "1+ past defaults, past default rate under 10%": (tr.n_defaults > 0) & (tr.past_default_rate < .1)}
    for g, m in groups.items():
        for test, col in (("customer folds", "p"), ("future loans", "p_t")):
            d = out[m & out[col].notna()]; yy = d.target.astype(int); rows.append(dict(group=g, test=test, loans=len(d), customers=d.customer_id.nunique(), defaults=int(yy.sum()), actual=yy.mean() if len(d) else np.nan, mean_predicted=d[col].mean(), approved=(d[col] <= CUT).mean(), default_if_approved=yy[d[col] <= CUT].mean() if (d[col] <= CUT).any() else np.nan))
    a = pd.DataFrame(rows); a.to_csv(T / "12_past_default_groups.csv", index=False)
    lr = _parts(final := final_model(tr, DEFAULT_CLUES))[1]; pre = _parts(final)[0]; names = pre.get_feature_names_out()
    co = pd.DataFrame(dict(column=names, weight=lr.coef_[0])); co = co[co.column.str.contains("n_defaults|past_default|no_known|n_finished|n_prev")]; co.to_csv(T / "12_past_default_weights.csv", index=False)
    # options, on labelled loans: only people with a past default change
    pol = {"a. leave it to the model": lambda d, col: d[col] > CUT, "b. decline any past default": lambda d, col: (d[col] > CUT) | (d.n_defaults > 0), "c. decline 2+ past defaults": lambda d, col: (d[col] > CUT) | (d.n_defaults >= 2), "d. decline past default rate 50%+": lambda d, col: (d[col] > CUT) | (d.past_default_rate >= .5), "e. decline past default rate 25%+": lambda d, col: (d[col] > CUT) | (d.past_default_rate >= .25), "f. decline 1+ past default in a short record (under 10 loans)": lambda d, col: (d[col] > CUT) | ((d.n_defaults > 0) & (d.n_prev_loans < 10)), "g. chosen: decline 2+ past defaults or past default rate 50%+": lambda d, col: (d[col] > CUT) | (d.n_defaults >= 2) | (d.past_default_rate >= .5)}
    rows = []
    for test, col in (("customer folds", "p"), ("future loans", "p_t")):
        d = out[out[col].notna()]; yy = d.target.astype(int); base = None
        for nm, f in pol.items():
            dec = f(d, col).to_numpy(); v = np.where(dec, (1 - yy) * FP, yy * FN); c = v.mean()
            if base is None: base = v
            lo, hi = boot(d.assign(v=v - base), None) if nm[0] != "a" else (0, 0)
            rows.append(dict(option=nm, test=test, cost=c, change=c - base.mean(), low=lo, high=hi, declined=dec.mean(), newly_declined=(dec & (d[col] <= CUT)).mean(), newly_declined_default_rate=yy[dec & (d[col] <= CUT).to_numpy()].mean() if (dec & (d[col] <= CUT).to_numpy()).any() else np.nan))
    o = pd.DataFrame(rows); o.to_csv(T / "12_past_default_options.csv", index=False)
    k = te[te.country_id == "Kenya"]; p = final.predict_proba(k[FEATURES])[:, 1]
    pd.DataFrame([dict(group=g, applicants=int(m.sum()), approved=(p[m] <= CUT).mean() if m.any() else np.nan) for g, m in {"1+ past defaults": (k.n_defaults > 0).to_numpy(), "2+ past defaults": (k.n_defaults >= 2).to_numpy(), "past default rate 50%+": (k.past_default_rate >= .5).to_numpy()}.items()]).to_csv(T / "12_past_default_zindi.csv", index=False)
    pd.set_option("display.width", 220)
    for x in (a, co, o, pd.read_csv(T / "12_past_default_zindi.csv")): print(x.round(3).to_string(index=False)); print()


if __name__ == "__main__":
    run()
