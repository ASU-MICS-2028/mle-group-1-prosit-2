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


def exact_counts(f_pub, f_pri, k, N_pub, P_pub, N_pri, P_pri, tol=2e-9):
    """Group size k and two F1 scores -> (k in public, defaults in public, defaults in private). F1 = 2d / (k_part + P_part), and d must be whole.
    Returns None if no split fits, so a wrong score can't produce a number. Two fits can occur (H5); the public part is a random 25%, so take the one nearest that."""
    hits = []
    for a in range(int(k) + 1):
        d1, d2 = f_pub * (a + P_pub) / 2, f_pri * (k - a + P_pri) / 2
        r1, r2 = round(d1), round(d2)
        if abs(2 * r1 / (a + P_pub) - f_pub) < tol and abs(2 * r2 / (k - a + P_pri) - f_pri) < tol: hits.append((a, r1, r2))
    return min(hits, key=lambda h: abs(h[0] - k * N_pub / (N_pub + N_pri))) if hits else None


def wilson(d, n, z=1.96):
    p = d / n; c = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n); m = (p + z * z / (2 * n)) / (1 + z * z / n)
    return m - c, m + c


def read_exact(n=18594, fn=2716, fee=90, typical=3000, recovered=.1, chase=16):
    """Both batches -> exact default counts per group, then every full / starter / decline policy over Ghana's segments.
    Ghana has 446 customers, so each group also gets a cautious range that counts customers, not loans. Group totals only."""
    T = ROOT / "learnings" / "tables"
    s = pd.concat([pd.read_csv(T / "11b_ghana_probe.csv"), pd.read_csv(T / "11b_ghana_probe_2.csv")])
    s["group"] = s.file.str.replace(".csv", "").str[3:]; s = s.set_index("group")
    e_pub, e_pri = s.zindi_public["everyone"], s.zindi_private["everyone"]
    fits = [(a, round(e_pub * a / (2 - e_pub)), n - a, round(e_pri * (n - a) / (2 - e_pri))) for a in range(1, n)]
    fits = [x for x in fits if abs(2 * x[1] / (x[0] + x[1]) - e_pub) < 2e-9 and abs(2 * x[3] / (x[2] + x[3]) - e_pri) < 2e-9]
    # several sizes can fit; the true one is the one that lets every group split into whole numbers
    fits = [x for x in fits if all(exact_counts(r.zindi_public, r.zindi_private, r.flagged, *x) for g, r in s.iterrows() if g != "everyone")]
    assert len(fits) == 1, fits
    N_pub, P_pub, N_pri, P_pri = fits[0]
    tr, te = build(str(ROOT / "data" / "zindi")); gh = te.country_id == "Ghana"; first = te.n_prev_loans == 0; t3 = gh & (te.loan_type == "Type_3"); t2 = gh & (te.loan_type == "Type_2")
    p13 = pd.Series(final_model(tr, FEATURES).predict_proba(te[FEATURES])[:, 1], index=te.index)
    pfin = pd.Series(final_model(tr, GHANA_CLUES).predict_proba(te[FEATURES])[:, 1], index=te.index)
    edges = p13[t3].quantile([.2, .4, .6, .8]).to_numpy(); band = pd.cut(p13, [-np.inf, *edges, np.inf], labels=False)
    assert ((t3 & (pfin > .032)) == (t3 & first)).all()  # H0 and H4 are the same loans
    masks = {"ghana_all": gh, "ghana_first_loans": gh & first, "ghana_earlier_loans": gh & ~first, "ghana_type_3": t3, "ghana_type_2": t2, "type_3_first_loans": t3 & first, "type_2_first_loans": t2 & first}
    masks.update({f"type_3_risk_band_{b + 1}_of_5": t3 & (band == b) for b in range(4)})
    masks["ghana_over_90_days"] = gh & (te.duration > 90)
    rows = []
    for g, r in s.iterrows():
        d = (P_pub, P_pri) if g == "everyone" else exact_counts(r.zindi_public, r.zindi_private, r.flagged, N_pub, P_pub, N_pri, P_pri)[1:]
        cust = te.customer_id[masks[g]].nunique() if g in masks else np.nan
        lo, hi = wilson(sum(d), r.flagged); row = dict(group=g, loans=int(r.flagged), defaults=sum(d), public=d[0], private=d[1], rate=sum(d) / r.flagged, range_loans_lo=lo, range_loans_hi=hi, customers=cust)
        if cust == cust: row["range_customers_lo"], row["range_customers_hi"] = wilson(sum(d) / r.flagged * cust, cust)
        rows.append(row)
    c = pd.DataFrame(rows).set_index("group"); c.loc["KENYA (everyone minus Ghana)"] = dict(loans=n - 3525, defaults=c.defaults["everyone"] - c.defaults["ghana_all"], public=P_pub - c.public["ghana_all"], private=P_pri - c.private["ghana_all"], rate=(c.defaults["everyone"] - c.defaults["ghana_all"]) / (n - 3525))
    c.to_csv(T / "11b_ghana_exact.csv")
    G = c.defaults["ghana_all"]; models = {"approve everyone": (0, 0), "decline everyone": (3525, G)}
    models.update({x: (c.loans[g], c.defaults[g]) for x, g in {"13 clues": "ghana_13_clues_flagged", "13, unseen types as Type_1": "ghana_unseen_as_type_1_flagged", "no 'borrow often' (Kenya's clues)": "ghana_keep_type_no_often_flagged",
                   "no loan_type (ADR 0019)": "ghana_no_type_flagged", "no loan_type, no 'borrow often' (ADR 0020)": "ghana_final_flagged"}.items()})
    pd.DataFrame([dict(policy=x, declined=k / 3525, defaults_caught=d / G, cost_ghs=((G - d) * fn + (k - d) * fee) / 3525) for x, (k, d) in models.items()]).to_csv(T / "11b_ghana_models.csv", index=False)
    # Segments that don't overlap. Type_3 first loans all sit in the riskiest band, checked here, so the rest of that band is a subtraction.
    assert (band[t3 & first] == 4).all()
    get = lambda g: c.loc[g, ["loans", "public", "private"]].to_numpy(float)
    seg = {"Type_2": get("ghana_type_2"), "Type_3 first loans": get("type_3_first_loans"), "Type_3 earlier, riskiest 10%": None, "Type_3 band 4": get("type_3_risk_band_4_of_5"),
           "Type_3 bands 1-3": get("type_3_risk_band_1_of_5") + get("type_3_risk_band_2_of_5") + get("type_3_risk_band_3_of_5")}
    seg["Type_3 earlier, riskiest 10%"] = get("ghana_type_3") - sum(seg[x] for x in ("Type_3 first loans", "Type_3 band 4", "Type_3 bands 1-3"))
    seg["Other types"] = get("ghana_all") - get("ghana_type_3") - get("ghana_type_2")
    assert all(v[0] > 0 and v[1] >= 0 and v[2] >= 0 for v in seg.values())
    names = list(seg); ks = np.array([seg[x][0] for x in names]); share = N_pub / n
    cost_start = typical * .1 * (1 - recovered) + chase
    def cost(actions, future):
        """Actions: F full, S starter, D decline. A good payer declined loses the fee and future business; a starter keeps the future, and 10% of the fee."""
        out = {}
        for part, i, w in (("public", 1, share), ("private", 2, 1 - share)):
            t = 0.
            for x, a in zip(names, actions):
                k = seg[x][0] * w; d = seg[x][i]; good = k - d
                t += d * fn if a == "F" else d * cost_start + good * fee * .9 if a == "S" else good * (fee + future)
            out[part] = t / (3525 * w)
        out["all"] = share * out["public"] + (1 - share) * out["private"]
        return out
    import itertools
    rows = []
    for future in (0, 16, 180, 360):
        for acts in itertools.product("FSD", repeat=len(names)):
            cc = cost(acts, future)
            rows.append(dict(future=future, **dict(zip(names, acts)), cost=cc["all"], public=cc["public"], private=cc["private"], full_share=sum(k for k, a in zip(ks, acts) if a == "F") / 3525, offered_share=sum(k for k, a in zip(ks, acts) if a != "D") / 3525))
    g = pd.DataFrame(rows); g.to_csv(T / "11b_ghana_policies.csv", index=False)
    riskiest = t3 & (band == 4) & ~first; low = t3 & band.isin([0, 1, 2])
    where = {"Type_2": t2, "Type_3 first loans": t3 & first, "Type_3 earlier, riskiest 10%": riskiest, "Type_3 band 4": t3 & (band == 3), "Type_3 bands 1-3": low, "Other types": gh & ~t2 & ~t3}
    pd.DataFrame([dict(segment=x, loans=seg[x][0], public=seg[x][1], private=seg[x][2], customers=te.customer_id[where[x]].nunique(), mean_amount=te.Total_Amount[where[x]].mean(), median_amount=te.Total_Amount[where[x]].median(), share_public=share) for x in names]).to_csv(T / "11b_ghana_segments.csv", index=False)
    print(N_pub, P_pub, N_pri, P_pri); print(c.round(3).to_string())
    print(pd.DataFrame({x: dict(loans=seg[x][0], defaults=seg[x][1] + seg[x][2], rate=(seg[x][1] + seg[x][2]) / seg[x][0]) for x in names}).T.round(3).to_string())
    for future in (0, 16, 180, 360):
        b = g[g.future == future].sort_values("cost")
        print("future", future, "breakeven", round((fee + future) / (fee + future + fn), 3)); print(b.head(3).round(2).to_string(index=False))
        print(b[(b[names] == "D").all(axis=1) | (b[names] == "F").all(axis=1)].round(2).to_string(index=False))


if __name__ == "__main__":
    import sys
    (read_exact if "--read-exact" in sys.argv else ghana_probe if "--ghana-probe" in sys.argv else ghana_probe_2 if "--ghana-probe-2" in sys.argv else read_probe if "--read-probe" in sys.argv else run)()
