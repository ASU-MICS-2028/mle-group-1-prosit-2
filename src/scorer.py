"""Step 12: the scoring service (ADR 0022). One application in; probability, decision, limit and up to 3 plain reasons out.

    python src/scorer.py --fit       # once: fits the models, saves the bundle to the ignored data/models/
    from src.scorer import score
    score({"country": "Kenya", "loan_type": "Type_1", "duration": 7, "New_versus_Repeat": "Repeat Loan", "n_prev_loans": 12, "n_finished": 11,
           "n_defaults": 0, "past_default_rate": 0.0, "no_known_history": 0, "days_since_last_loan": 14.0, "n_loans_last_7d": 0, "n_loans_last_30d": 1,
           "mean_prev_amount": 4000.0, "last_amount": 5000.0})

Kenya (ADRs 0020, 0022): model at 2.1%; first-timers above it get a 500 KES starter below 24% risk; loan types never seen in Kenya are declined, as is anyone with 2+ past defaults or a past default rate of 50%+.
Ghana (ADR 0021): a rule by loan type, using rates measured from Zindi's scores; the Kenyan model decides nothing there yet.
Only load a bundle you made yourself: joblib files can run code when opened.
"""
import math
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.features import DEFAULT_CLUES, FEATURES, build
from src.reasons import MIN_PUSH, THEMES, pushes, reasons, reference

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "data" / "models" / "scorer.joblib"
KENYA_CUT, RISK_CAP, KENYA_STARTER, GHANA_STARTER = .021, .24, 500, 300
GHANA_RATE = {"Type_2": .503, "Type_3": .070}; GHANA_OTHER_RATE = .216  # learnings/tables/11b_ghana_exact.csv, 11b_ghana_segments.csv
GHANA_NOTE = "Ghana pilot: rate measured for this loan type as a group, not for this person. Not yet checked on real pilot repayments (ADR 0021)."
COUNTS = ["n_prev_loans", "n_finished", "n_defaults", "n_loans_last_7d", "n_loans_last_30d"]
CAN_BE_EMPTY = ["past_default_rate", "days_since_last_loan", "mean_prev_amount", "last_amount"]  # unknown for a first-timer, or until an earlier loan's outcome is known
FIELDS = ["country", "loan_type", "duration", "New_versus_Repeat", *COUNTS, "no_known_history", *CAN_BE_EMPTY]
GOOD = {"repayment record": "You have repaid your earlier loans with us.", "borrowing history": "You have a record of earlier loans with us.",
        "loan sizes": "Your earlier loan sizes fit the pattern of borrowers who repay.", "loan length": "The length of this loan is one that is usually repaid."}


def check(a):
    """Reject anything we can't score, listing every problem at once. Raises ValueError."""
    if not isinstance(a, dict): raise ValueError("application must be a dict")
    bad = [f"missing: {f}" for f in FIELDS if f not in a] + [f"unknown field: {f}" for f in a if f not in FIELDS]
    bad += [f"empty: {f}" for f in FIELDS if f in a and f not in CAN_BE_EMPTY and a[f] is None]
    def number(f):
        v = a.get(f)
        return isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool) and math.isfinite(v)
    if a.get("country") is not None and a.get("country") not in ("Kenya", "Ghana"): bad.append("country must be Kenya or Ghana")
    if a.get("loan_type") is not None and (not isinstance(a["loan_type"], str) or not a["loan_type"].strip()): bad.append("loan_type must be text")
    if a.get("New_versus_Repeat") is not None and a.get("New_versus_Repeat") not in ("New Loan", "Repeat Loan"): bad.append("New_versus_Repeat must be New Loan or Repeat Loan")
    if a.get("duration") is not None and (not number("duration") or a["duration"] <= 0): bad.append("duration must be a positive number of days")
    for f in COUNTS:
        if a.get(f) is not None and (not number(f) or a[f] < 0 or a[f] != int(a[f])): bad.append(f"{f} must be a whole number, 0 or more")
    if a.get("no_known_history") is not None and a.get("no_known_history") not in (0, 1): bad.append("no_known_history must be 0 or 1")
    for f in CAN_BE_EMPTY:
        if a.get(f) is not None and (not number(f) or a[f] < 0): bad.append(f"{f} must be a number, 0 or more, or empty")
    if number("past_default_rate") and a["past_default_rate"] > 1: bad.append("past_default_rate must be between 0 and 1")
    if number("n_finished") and number("n_prev_loans") and a["n_finished"] > a["n_prev_loans"]: bad.append("n_finished can't be above n_prev_loans")
    if number("n_defaults") and number("n_finished") and a["n_defaults"] > a["n_finished"]: bad.append("n_defaults can't be above n_finished")
    if bad: raise ValueError("; ".join(bad))


def fit(data_dir=ROOT / "data" / "zindi", path=BUNDLE):
    """Fit on every labelled Kenyan loan and save one file."""
    from src.amounts import final_amount_model
    from src.classification_experiments import final_model
    train, _ = build(str(data_dir)); model = final_model(train, DEFAULT_CLUES)
    b = dict(model=model, amount=final_amount_model(train), reference=reference(model, train[FEATURES]), known_types=set(train.loan_type))
    Path(path).parent.mkdir(parents=True, exist_ok=True); joblib.dump(b, path, compress=3); load.cache_clear()
    return path


@lru_cache(maxsize=1)
def load(path=BUNDLE):
    if not Path(path).exists(): raise FileNotFoundError(f"{path} not found: run python src/scorer.py --fit")
    return joblib.load(path)


def result(a, p, source, decision, limit, currency, why, notes=()):
    return dict(country=a["country"], probability=round(float(p), 4), probability_source=source, decision=decision, limit=int(limit), currency=currency, reasons=list(why)[:3], notes=list(notes))


def ghana(a):
    t = a["loan_type"]
    if t == "Type_3":
        return result(a, GHANA_RATE[t], "group rate", "starter", GHANA_STARTER, "GHS", ["We don't yet have enough repayment records in Ghana to offer larger loans.", "This starter loan lets you build a record with us."], [GHANA_NOTE])
    if t == "Type_2":
        return result(a, GHANA_RATE[t], "group rate", "decline", 0, "GHS", ["About half of loans of this kind (Type_2) have not been repaid in Ghana.", "We aren't offering this kind of loan yet. This is about the product, not about you.", "You can ask for a Type_3 starter loan of GHS 300 instead."], [GHANA_NOTE])
    return result(a, GHANA_OTHER_RATE, "group rate", "decline", 0, "GHS", [f"We have too few repayment records for this kind of loan ({t}) in Ghana.", "We aren't offering this kind of loan yet. This is about the product, not about you.", "You can ask for a Type_3 starter loan of GHS 300 instead."], [GHANA_NOTE])


def kenya(a, b):
    X = pd.DataFrame([{f: (np.nan if a[f] is None else a[f]) for f in FEATURES}])[FEATURES].astype({f: float for f in FEATURES if f not in ("loan_type", "New_versus_Repeat")})
    p = b["model"].predict_proba(X)[0, 1]; risk = reasons(b["model"], X, b["reference"], known_types=b["known_types"])[0]; first = a["n_prev_loans"] == 0
    if a["n_defaults"] >= 2 or (a["past_default_rate"] or 0) >= .5:  # the model barely weighs these (weights 0.07, -0.06), so unusual inputs can slip past it. Costs nothing on history (12_past_default_options.csv)
        return result(a, p, "model", "decline", 0, "KES", [f"You did not repay {a['n_defaults']} of your earlier loans.", *[s for s in risk if "did not repay" not in s]])
    if a["loan_type"] not in b["known_types"]:
        return result(a, p, "model", "decline", 0, "KES", [f"We have no repayment record for this kind of loan ({a['loan_type']}), so we can't offer it yet.", *risk], ["Unseen loan type: the probability is less reliable (learnings/12)."])
    if p <= KENYA_CUT:
        t = pushes(b["model"], X, b["reference"], "theme").iloc[0]; t = t[t <= -MIN_PUSH].sort_values()
        why = [f"Loans of this kind ({a['loan_type']}) have been repaid more often than others." if th == "loan product" else GOOD[th] for th in t.index[:3]]
        return result(a, p, "model", "approve", b["amount"].limit(X)[0], "KES", why or ["Nothing in your application raised our main risk checks."])
    if first: risk = [s for s in risk if not s.startswith("This is a first loan")] or risk  # says the same as "This is your first loan" (ponytail: real fix is merging the two sentences in reasons.py)
    why = risk or ["Taken together, your application is above the risk level we can accept."]
    if first and p < RISK_CAP: return result(a, p, "model", "starter", KENYA_STARTER, "KES", why)
    return result(a, p, "model", "decline", 0, "KES", why)


def score(application, path=BUNDLE):
    """Application dict -> dict with probability, probability_source, decision (approve / starter / decline), limit, currency, reasons, notes."""
    check(application)
    return ghana(application) if application["country"] == "Ghana" else kenya(application, load(path))


if __name__ == "__main__":
    import sys
    if "--fit" in sys.argv: print("saved", fit())
