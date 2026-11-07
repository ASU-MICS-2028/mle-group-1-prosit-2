"""Step 12 tests: made-up applicants only. Run: PYTHONPATH=. .venv/bin/python tests/test_scorer.py. Needs `src/scorer.py --fit`. Writes learnings/tables/12_*.csv, including failures."""
import time, traceback
from pathlib import Path
import numpy as np, pandas as pd
from src.features import FEATURES, build
from src.scorer import BUNDLE, FIELDS, load, score

ROOT = Path(__file__).resolve().parent.parent; T = ROOT / "learnings" / "tables"
AMA = dict(country="Kenya", loan_type="Type_1", duration=7, New_versus_Repeat="Repeat Loan", n_prev_loans=12, n_finished=11, n_defaults=0, past_default_rate=0.0, no_known_history=0, days_since_last_loan=14.0, n_loans_last_7d=0, n_loans_last_30d=1, mean_prev_amount=4000.0, last_amount=5000.0)  # made up
NEW = {**AMA, "New_versus_Repeat": "New Loan", "n_prev_loans": 0, "n_finished": 0, "past_default_rate": None, "no_known_history": 1, "days_since_last_loan": None, "n_loans_last_30d": 0, "mean_prev_amount": None, "last_amount": None}
GH = {**NEW, "country": "Ghana", "loan_type": "Type_3"}


def shape_ok(r):
    assert 0 <= r["probability"] <= 1 and r["decision"] in ("approve", "starter", "decline") and 1 <= len(r["reasons"]) <= 3 and r["limit"] >= 0 and (r["limit"] == 0) == (r["decision"] == "decline")
    for s in r["reasons"]: assert "nan" not in s.lower().split() and "borrow more" not in s and "regular borrowers" not in s, s


def rejects(a, word):
    try: score(a)
    except ValueError as e: assert word in str(e), e; return
    raise AssertionError("accepted a bad application")


def t_repeat():
    r = score(AMA); shape_ok(r); assert r["decision"] == "approve" and r["limit"] > 0 and r["currency"] == "KES" and r["probability_source"] == "model"
def t_new_kenya():
    r = score(NEW); shape_ok(r); assert r["decision"] == "starter" and r["limit"] == 500, r
def t_defaulter_declined():
    r = score({**AMA, "n_defaults": 3, "past_default_rate": 1.0, "n_finished": 3, "n_prev_loans": 3}); shape_ok(r); assert r["decision"] == "decline" and any("did not repay" in s for s in r["reasons"]), r
def t_half_defaulted_declined():
    r = score({**AMA, "n_defaults": 1, "n_finished": 2, "n_prev_loans": 2, "past_default_rate": .5}); shape_ok(r); assert r["decision"] == "decline"
def t_one_default_in_long_record_goes_to_model():
    r = score({**AMA, "n_defaults": 1, "n_finished": 20, "n_prev_loans": 20, "past_default_rate": .05}); shape_ok(r); assert r["probability_source"] == "model" and not any("You did not repay 1 of" in s for s in r["reasons"])
def t_ghana_type_3_new():
    r = score(GH); shape_ok(r); assert (r["decision"], r["limit"], r["currency"], r["probability"]) == ("starter", 300, "GHS", .07)
def t_ghana_type_3_repeat_gets_no_more():
    r = score({**AMA, "country": "Ghana", "loan_type": "Type_3"}); shape_ok(r); assert (r["decision"], r["limit"]) == ("starter", 300)
def t_ghana_type_2():
    r = score({**GH, "loan_type": "Type_2"}); shape_ok(r); assert r["decision"] == "decline" and r["probability"] == .503 and any("starter" in s for s in r["reasons"])
def t_ghana_unseen():
    r = score({**GH, "loan_type": "Type_99"}); shape_ok(r); assert r["decision"] == "decline" and "Type_99" in r["reasons"][0]
def t_kenya_unseen():
    r = score({**AMA, "loan_type": "Type_99"}); shape_ok(r); assert r["decision"] == "decline" and "Type_99" in r["reasons"][0] and r["notes"]
def t_missing_field():
    for f in FIELDS: rejects({k: v for k, v in AMA.items() if k != f}, f"missing: {f}")
def t_empty_required():
    rejects({**AMA, "duration": None}, "empty: duration")
def t_bad_values():
    for bad, word in [({"country": "Nigeria"}, "country"), ({"duration": -7}, "duration"), ({"duration": float("nan")}, "duration"), ({"duration": "7"}, "duration"), ({"n_prev_loans": -1}, "n_prev_loans"), ({"n_prev_loans": 1.5}, "n_prev_loans"), ({"n_prev_loans": True}, "n_prev_loans"), ({"past_default_rate": 1.5}, "past_default_rate"), ({"n_finished": 99}, "n_finished"), ({"New_versus_Repeat": "Old"}, "New_versus_Repeat"), ({"no_known_history": 2}, "no_known_history"), ({"last_amount": -5.0}, "last_amount"), ({"loan_type": ""}, "loan_type")]:
        rejects({**AMA, **bad}, word)
def t_extra_field_rejected():
    rejects({**AMA, "gender": "F"}, "unknown field: gender")
def t_lists_every_problem():
    try: score({**AMA, "duration": -1, "country": "X"})
    except ValueError as e: assert "duration" in str(e) and "country" in str(e); return
    raise AssertionError
def t_same_answer_twice():
    assert score(AMA) == score(AMA)
def t_input_not_changed():
    a = dict(AMA); score(a); assert a == AMA
def t_never_reveals_weights():
    r = score(AMA); assert "coef" not in str(r) and "log-odds" not in str(r)


def timing(n=1000):
    rows = []
    for label, a in (("Kenya, repeat", AMA), ("Kenya, first-timer", NEW), ("Ghana", GH)):
        s = []
        for _ in range(n):
            t = time.perf_counter(); score(a); s.append(time.perf_counter() - t)
        rows.append(dict(case=label, calls=n, median_ms=np.median(s) * 1e3, p95_ms=np.quantile(s, .95) * 1e3, max_ms=max(s) * 1e3))
    return pd.DataFrame(rows)


def real_applicants():
    """Every Zindi test applicant through score(), one at a time. Aggregates only. Are they all accepted, and do the shares match the Model Card?"""
    _, te = build(str(ROOT / "data" / "zindi")); out, refused, odd = [], {}, 0
    for rec in te[["country_id", *FEATURES]].rename(columns={"country_id": "country"}).to_dict("records"):
        a = {k: (None if isinstance(v, float) and np.isnan(v) else v) for k, v in rec.items()}
        try:
            r = score(a); out.append((a["country"], r["decision"], r["limit"], len(r["reasons"]), a["n_prev_loans"] == 0))
            shape_ok(r)
        except ValueError as e:
            k = str(e).split(";")[0]; refused[k] = refused.get(k, 0) + 1
        except AssertionError: odd += 1
    d = pd.DataFrame(out, columns=["country", "decision", "limit", "reasons", "first"])
    t = d.groupby("country").decision.value_counts(normalize=True).rename("share").reset_index().merge(d.groupby(["country", "decision"]).agg(applicants=("limit", "size"), median_limit=("limit", "median"), mean_reasons=("reasons", "mean")).reset_index())
    f = d[d["first"]].groupby("country").decision.value_counts(normalize=True).rename("share").reset_index().assign(group="first-timers")
    pd.concat([t.assign(group="all"), f]).to_csv(T / "12_decisions_on_zindi_applicants.csv", index=False)
    pd.DataFrame([dict(refused=k, count=v) for k, v in refused.items()] or [dict(refused="none", count=0)]).to_csv(T / "12_refused_on_zindi_applicants.csv", index=False)
    return t, f, refused, odd, len(te)


if __name__ == "__main__":
    t0 = time.perf_counter(); load.cache_clear(); load(); cold = time.perf_counter() - t0
    res = []
    for name, f in sorted((k, v) for k, v in dict(globals()).items() if k.startswith("t_")):
        try: f(); res.append(dict(test=name[2:], passed=True, detail=""))
        except Exception: res.append(dict(test=name[2:], passed=False, detail=traceback.format_exc(limit=1).strip().splitlines()[-1][:200]))
    r = pd.DataFrame(res); r.to_csv(T / "12_tests.csv", index=False); print(r.to_string(index=False))
    tm = timing(); tm.assign(cold_load_s=cold, bundle_mb=BUNDLE.stat().st_size / 1e6).to_csv(T / "12_latency.csv", index=False); print(tm.round(2).to_string(index=False), "cold load s", round(cold, 2), "MB", round(BUNDLE.stat().st_size / 1e6, 2))
    t, f, refused, odd, n = real_applicants(); print(t.round(3).to_string(index=False)); print(f.round(3).to_string(index=False)); print("refused", refused, "odd", odd, "of", n)
    assert r.passed.all() and not refused and not odd
    print("Scorer checks passed")
