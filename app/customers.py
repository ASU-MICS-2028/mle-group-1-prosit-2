"""Four made-up customers for the demo. The history fields are what a lender would look up; no real person or Zindi row."""
import re

AMINA = dict(New_versus_Repeat="Repeat Loan", n_prev_loans=12, n_finished=11, n_defaults=0, past_default_rate=0.0, no_known_history=0,
             days_since_last_loan=14.0, n_loans_last_7d=0, n_loans_last_30d=1, mean_prev_amount=4000.0, last_amount=5000.0)  # tests/test_scorer.py AMA
FIRST = dict(AMINA, New_versus_Repeat="New Loan", n_prev_loans=0, n_finished=0, past_default_rate=None, no_known_history=1,
             days_since_last_loan=None, n_loans_last_30d=0, mean_prev_amount=None, last_amount=None)  # tests/test_scorer.py NEW
MISSED = dict(AMINA, n_prev_loans=3, n_finished=3, n_defaults=3, past_default_rate=1.0)

KENYA_TYPES = [{"code": "Type_1", "label": "Type 1", "note": "Our most common loan"}, {"code": "Type_7", "label": "Type 7", "note": "A less common product"}]
GHANA_TYPES = [{"code": "Type_3", "label": "Type 3", "note": "Starter pilot in Ghana"}, {"code": "Type_2", "label": "Type 2", "note": "Not yet offered in Ghana"}]

CUSTOMERS = {
    "0712000001": dict(name="Amina", country="Kenya", currency="KES", loan_types=KENYA_TYPES, history=AMINA,
                       summary=["12 loans with us", "11 repaid", "Last loan 14 days ago"]),
    "0712000002": dict(name="Brian", country="Kenya", currency="KES", loan_types=KENYA_TYPES, history=FIRST,
                       summary=["This is your first loan with us"]),
    "0712000003": dict(name="Wanjiru", country="Kenya", currency="KES", loan_types=KENYA_TYPES, history=MISSED,
                       summary=["3 loans with us", "3 not repaid"]),
    "0244000004": dict(name="Kofi", country="Ghana", currency="GHS", loan_types=GHANA_TYPES, history=FIRST,
                       summary=["This is your first loan with us"]),
}


def normalise_phone(raw: str) -> str:
    """Keep digits; turn a Kenyan (254) or Ghanaian (233) country code into a leading 0."""
    d = re.sub(r"\D", "", raw or "")
    return "0" + d[3:] if d[:3] in ("254", "233") and len(d) == 12 else d
