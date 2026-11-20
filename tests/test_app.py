"""Loan demo API checks: made-up customers only. Run: PYTHONPATH=. .venv/bin/python tests/test_app.py. Needs `src/scorer.py --fit`."""
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.customers import normalise_phone
from app.main import app

client = TestClient(app)


def apply(phone, loan_type, duration, amount, status=200):
    r = client.post("/api/apply", json=dict(phone=phone, loan_type=loan_type, duration=duration, amount=amount))
    assert r.status_code == status, (phone, loan_type, duration, amount, r.status_code, r.text)
    return r.json() if status == 200 else True


def run():
    assert normalise_phone("+254 712 000 001") == "0712000001"
    assert normalise_phone("0712-000-001") == "0712000001"
    assert normalise_phone("233244000004") == "0244000004"
    assert normalise_phone("712 000 001") == "0712000001"  # no leading 0, as many people type it
    assert normalise_phone("+254 0712 000 001") == "0712000001"
    assert normalise_phone("00254712000001") == "0712000001"
    amina = client.get("/api/customers/0712000001")
    assert amina.json()["name"] == "Amina" and amina.json()["first_loan"] is False
    assert "past_default_rate" not in amina.text  # raw model inputs never leave the server
    assert client.get("/api/customers/0712 000 001").json()["name"] == "Amina"
    assert client.get("/api/customers/0799999999").status_code == 404
    assert client.get("/").status_code == 200

    r = apply("0712000001", "Type_1", 7, 3000)
    assert r["decision"] == "approve" and r["offer"] == 3000 and r["cutoff"] == 0.021 and r["currency"] == "KES"
    assert r["repay"] == 3060 and r["due_date"] == (date.today() + timedelta(7)).isoformat()
    r = apply("0712000001", "Type_1", 7, 999_999)
    assert r["decision"] == "approve" and 0 < r["offer"] < 999_999  # capped at the limit
    assert apply("0712000001", "Type_1", 30, 3000)["decision"] == "decline"
    r = apply("0712000002", "Type_1", 7, 3000)
    assert r["decision"] == "starter" and r["offer"] == 500
    r = apply("0712000002", "Type_1", 7, 100)
    assert r["decision"] == "starter" and r["offer"] == 100  # never offer more than was asked for
    apply("0712000001", "Type_1", 7, 0.4, status=422)  # rounds to 0: would be "approved" for nothing
    r = apply("0712000003", "Type_1", 7, 3000)
    assert r["decision"] == "decline" and r["offer"] == 0 and r["reasons"]
    r = apply("0244000004", "Type_3", 7, 1000)
    assert r["decision"] == "starter" and r["offer"] == 300 and r["cutoff"] is None and r["currency"] == "GHS" and r["repay"] == 309
    assert apply("0244000004", "Type_2", 7, 1000)["decision"] == "decline"

    apply("0712000001", "Type_3", 7, 1000, status=422)  # the other country's loan type
    for bad in (0, -5, 2_000_000):
        apply("0712000001", "Type_1", 7, bad, status=422)
    apply("0712000001", "Type_1", 10, 1000, status=422)  # only 7, 14 or 30 days
    apply("0799999999", "Type_1", 7, 1000, status=404)
    print("App checks passed")


if __name__ == "__main__":
    run()
