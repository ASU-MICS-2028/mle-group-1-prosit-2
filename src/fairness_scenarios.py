"""Step 11b: test every combination behind ADR 0020, not just the ones we guessed. Run from the repo root (a few minutes).

Grid: clue set x who gets a starter loan x its size x risk cap x cut-off x validation test, costed under pessimistic and
optimistic assumptions. Also checks the starter loan's two assumptions against what Kenyan first-timers really did:
do repaid first-timers come back, and do smaller first loans default less? Only summaries are written, to learnings/tables/11b_*.
"""
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline

from src.classification_experiments import logit
from src.features import BORROW_OFTEN, FEATURES, build, preprocessor, splits

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "learnings" / "tables"
TYPICAL, FEE, CHASE, RECOVERED, FUTURE, MEASURED = 5000, 100, 200, .10, 400, 200  # KES. FUTURE: step 4's guess of the repeat business lost when a good payer is refused; MEASURED: what small-first-loan customers really brought in (11b_first_timers.csv)
RISK_CAP = .24  # above this, a starter loan loses money even counting MEASURED repeat business: p / (1 - p) = (10 + 200) / (450 + 200)
CUTOFFS = {"2.1% (main)": .021, "6.0% (measured repeat value)": .06, "9.6% (step 4 repeat value)": .096}
TESTS = {"future loans": "time_block", "future loans, new customers": "time_new_customers", "new customers": "fold_customer"}


def clue_sets():
    """Every way of dropping the three 'borrow often' clues."""
    out = {}
    for k in range(len(BORROW_OFTEN) + 1):
        for drop in combinations(BORROW_OFTEN, k):
            out["keep all 13" if not drop else "drop " + " + ".join(drop)] = [c for c in FEATURES if c not in drop]
    return out


def scores(tr, clues, scheme):
    """Out-of-sample calibrated scores with step 7's recipe. Each row is scored once (per test block, its last one)."""
    out = []
    for k, (a, b) in enumerate(splits(tr, scheme)):
        t = tr.loc[a]; X, y = t[clues], t.target.astype(int)
        base = lambda: make_pipeline(preprocessor(clues), LogisticRegression(max_iter=2000))
        oof = np.zeros(len(X))
        for i, j in StratifiedGroupKFold(5, shuffle=True, random_state=17).split(X, y, t.customer_id):
            oof[j] = base().fit(X.iloc[i], y.iloc[i]).predict_proba(X.iloc[j])[:, 1]
        cal = LogisticRegression(max_iter=1000, random_state=17).fit(logit(oof).reshape(-1, 1), y)
        p = cal.predict_proba(logit(base().fit(X, y).predict_proba(tr.loc[b, clues])[:, 1]).reshape(-1, 1))[:, 1]
        out.append(pd.DataFrame({"block": k, "p": p}, index=b))
    return pd.concat(out)


def cost(d, over, small, size=0., recovered=RECOVERED, chase=CHASE, future=0., retained=1., risk=1.):
    """KES lost per loan. risk scales how often a starter loan defaults; retained = share of future business a starter loan keeps."""
    fn = TYPICAL * (1 - recovered) + chase
    y, refused = d.y.to_numpy(), over & ~small
    n_small, bad_small = small.sum(), min(risk * (y & small).sum(), small.sum())
    total = fn * (y & ~over).sum() + (FEE + future) * (~y & refused).sum()
    total += (size * TYPICAL * (1 - recovered) + chase) * bad_small
    total += ((1 - size) * FEE + future * (1 - retained)) * (n_small - bad_small)
    return total / len(d)


def policies(d, cutoff):
    """(name, starter size, who gets one). Anyone else above the cut-off is refused."""
    over, first, thin = (d.p > cutoff).to_numpy(), d["first"].to_numpy(), d.thin.to_numpy()
    yield "no starter loans", 0., np.zeros(len(d), bool)
    for s in (.05, .10, .25, .50):
        yield f"first loans, {s:.0%}", s, over & first
    for s in (.05, .10):
        for cap in (.15, .20, .24, .30, .39):
            yield f"first loans, {s:.0%}, only below {cap:.0%} risk", s, over & first & (d.p < cap).to_numpy()
    yield "first loans and no-known-outcome, 10%", .10, over & thin
    yield "everyone above the cut-off, 10%", .10, over


def grid(tr):
    rows, kept = [], {}
    for test, scheme in TESTS.items():
        for name, clues in clue_sets().items():
            s = scores(tr, clues, scheme)
            d = s.join(tr[["target", "n_prev_loans", "no_known_history", "customer_id"]])
            d["y"], d["first"], d["thin"] = d.target.astype(bool), d.n_prev_loans == 0, d.no_known_history == 1
            kept[test, name] = d
            lift = np.mean([average_precision_score(g.y, g.p) / g.y.mean() for _, g in d.groupby("block")])
            for cname, c in CUTOFFS.items():
                over = (d.p > c).to_numpy()
                for pname, size, small in policies(d, c):
                    refused, y, f = over & ~small, d.y.to_numpy(), d["first"].to_numpy()
                    rows.append({"test": test, "clues": name, "cut-off": cname, "starter policy": pname, "lift": lift,
                                 "cost, main": cost(d, over, small, size), "cost, measured repeat value": cost(d, over, small, size, future=MEASURED),
                                 "cost, step 4 repeat value": cost(d, over, small, size, future=FUTURE),
                                 "any loan": (~refused).mean(), "first: good refused": refused[f & ~y].mean(),
                                 "others: good refused": refused[~f & ~y].mean(), "others: defaulters stopped": refused[~f & y].mean(),
                                 "first: defaulters refused": refused[f & y].mean()})
    return pd.DataFrame(rows), kept


def boot_change(d, a, b, n=500):
    """Customer bootstrap of (cost per loan under a) - (cost per loan under b); a, b give each loan's cost."""
    cs, inv = np.unique(d.customer_id.to_numpy(), return_inverse=True)
    diff, cnt = np.bincount(inv, a - b, len(cs)), np.bincount(inv, minlength=len(cs))
    x = [(w * diff).sum() / (w * cnt).sum() for w in np.random.default_rng(0).multinomial(len(cs), np.full(len(cs), 1 / len(cs)), n)]
    return np.mean(a - b), *np.percentile(x, [2.5, 97.5])


def loan_costs(d, over, small, size, future):
    y, refused = d.y.to_numpy(), over & ~small
    return ((TYPICAL * (1 - RECOVERED) + CHASE) * (y & ~over) + (FEE + future) * (~y & refused)
            + (size * TYPICAL * (1 - RECOVERED) + CHASE) * (y & small) + (1 - size) * FEE * (~y & small))


def finalists(kept):
    """The candidates against no fix: overall with a range, then block by block on future loans."""
    drop = "drop " + " + ".join(BORROW_OFTEN)
    cands = [("keep all 13", "first, 10%", .10, 1.), (drop, "no starter loans", 0., 1.), (drop, "first, 10%", .10, 1.), (drop, "first, 10%, below 24% risk", .10, RISK_CAP)]
    rows = []
    for test in TESTS:
        base = kept[test, "keep all 13"]; over0 = (base.p > .021).to_numpy()
        for clues, pol, size, cap in cands:
            d = kept[test, clues]; over = (d.p > .021).to_numpy(); small = over & d["first"].to_numpy() & (d.p < cap).to_numpy() if size else np.zeros(len(d), bool)
            for view, fut in [("main", 0.), ("measured repeat value", MEASURED), ("step 4 repeat value", FUTURE)]:
                a, b = loan_costs(d, over, small, size, fut), loan_costs(base.loc[d.index], over0, np.zeros(len(d), bool), 0., fut)
                rows.append({"test": test, "block": "all", "clues": clues, "starter": pol, "costs": view,
                             **dict(zip(["change", "95% low", "95% high"], boot_change(d, a, b)))})
                for k, g in d.groupby("block").groups.items():
                    i = d.index.get_indexer(g)
                    rows.append({"test": test, "block": k, "clues": clues, "starter": pol, "costs": view, "change": (a[i] - b[i]).mean()})
    return pd.DataFrame(rows)


def assumptions(kept):
    """How wrong can step 4's guesses be? Each row changes the assumptions for the chosen policy vs no fix, on future loans."""
    d = kept["future loans", "drop " + " + ".join(BORROW_OFTEN)]; base = kept["future loans", "keep all 13"].loc[d.index]
    over, over0 = (d.p > .021).to_numpy(), (base.p > .021).to_numpy()
    small, none = over & d["first"].to_numpy() & (d.p < RISK_CAP).to_numpy(), np.zeros(len(d), bool)
    rows = []
    for size in (.05, .10, .25):
        for future in (0, 100, 200, 400, 800):
            for retained in (1., .5, .25):
                for risk in (.5, 1., 1.5, 2.):
                    for rec, ch in [(.10, 200), (0., 200), (.30, 200), (.10, 400)]:
                        new = cost(d, over, small, size, rec, ch, future, retained, risk)
                        rows.append({"starter size": size, "future business (KES)": future, "share a starter keeps": retained, "starter default risk x": risk,
                                     "recovered": rec, "chasing (KES)": ch, "change vs no fix": new - cost(base, over0, none, 0., rec, ch, future)})
    return pd.DataFrame(rows)


def what_first_timers_did(tr):
    """Facts from the labelled loans. One row per customer's first loan in the data; later loans come from the same customer."""
    o = tr.sort_values("disbursement_date", kind="mergesort")
    first = o[o.n_prev_loans == 0].drop_duplicates("customer_id")
    later = o[o.n_prev_loans > 0].merge(first[["customer_id", "disbursement_date"]], on="customer_id", suffixes=("", "_first"))
    later = later[later.disbursement_date > later.disbursement_date_first]
    money = later.assign(earned=.02 * later.Total_Amount, lost=later.target * (.9 * later.Total_Amount + CHASE))
    per = money.groupby("customer_id").agg(later_loans=("target", "size"), later_defaults=("target", "sum"), earned=("earned", "sum"), lost=("lost", "sum"))
    f = first.set_index("customer_id").join(per).fillna({"later_loans": 0, "later_defaults": 0, "earned": 0, "lost": 0})
    f["months_seen"] = (o.disbursement_date.max() - f.disbursement_date).dt.days / 30.4
    f["came_back"], f["net"] = f.later_loans > 0, f.earned - f.lost
    size = pd.cut(f.Total_Amount, [0, 500, 1000, 2500, 5000, 10000, np.inf], labels=["up to 500", "500-1,000", "1,000-2,500", "2,500-5,000", "5,000-10,000", "over 10,000"])

    def summary(g):
        cs, rng = g.index.to_numpy(), np.random.default_rng(0)
        draws = [g.loc[rng.choice(cs, len(cs))].net.mean() for _ in range(300)] if len(g) else [np.nan]
        return pd.Series({"first-timers": len(g), "defaulted on first loan": g.target.mean(), "came back": g.came_back.mean(), "later loans (mean)": g.later_loans.mean(),
                          "later default rate": g.later_defaults.sum() / max(g.later_loans.sum(), 1), "later fees (KES, mean)": g.earned.mean(), "later losses (KES, mean)": g.lost.mean(),
                          "net future value (KES, mean)": g.net.mean(), "net future value (KES, median)": g.net.median(), "net 95% low": np.percentile(draws, 2.5), "net 95% high": np.percentile(draws, 97.5)})
    repaid = f[f.target == 0]
    a = pd.concat({"repaid first loan": repaid.pipe(summary), "defaulted on first loan": f[f.target == 1].pipe(summary)}, axis=1).T
    b = f.groupby(size, observed=True).apply(summary, include_groups=False)
    c = repaid.groupby(size, observed=True).apply(summary, include_groups=False)
    d = repaid.groupby(repaid.months_seen.gt(12).map({True: "seen 12+ months", False: "seen under 12 months"})).apply(summary, include_groups=False)
    return pd.concat({"by outcome of first loan": a, "all first-timers, by first-loan size (KES)": b, "repaid first-timers, by first-loan size (KES)": c, "repaid first-timers, by time we can see": d})


def launch(tr, te):
    """What the chosen rules do to applicants the models never saw."""
    from src.classification_experiments import final_model
    from src.features import DEFAULT_CLUES, GHANA_CLUES
    rows = []
    for name, d, clues, cut in [("Kenya", te[te.country_id == "Kenya"], DEFAULT_CLUES, .021), ("Ghana", te[te.country_id == "Ghana"], GHANA_CLUES, .032)]:
        p = final_model(tr, clues).predict_proba(d[FEATURES])[:, 1]
        first, over = (d.n_prev_loans == 0).to_numpy(), p > cut
        for cap in (1., RISK_CAP):
            starter = over & first & (p < cap)
            rows.append({"country": name, "starter loans": "no cap" if cap == 1 else f"below {cap:.0%} risk", "full loan": (~over).mean(), "starter": starter.mean(), "above the cut-off, no starter": (over & ~starter).mean(),
                         "first-timers: starter": starter[first].mean(), "first-timers: no starter": (over & ~starter)[first].mean(), "earlier loans: above the cut-off": over[~first].mean()})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    tr, te = build(str(ROOT / "data" / "zindi"))
    launch(tr, te).to_csv(TABLES / "11b_launch.csv", index=False)
    table, kept = grid(tr)
    table.to_csv(TABLES / "11b_grid.csv", index=False)
    finalists(kept).to_csv(TABLES / "11b_finalists.csv", index=False)
    assumptions(kept).to_csv(TABLES / "11b_assumptions.csv", index=False)
    what_first_timers_did(tr).to_csv(TABLES / "11b_first_timers.csv")
    print(len(table), "scenarios written")
