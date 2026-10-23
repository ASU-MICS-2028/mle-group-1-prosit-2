"""Shared feature code. Every notebook and the scorer import from here, so they all build features the same way."""
import numpy as np
import pandas as pd


def to_loans(rows):
    """One row per loan. A loan split across several lenders appears as several rows with the same tbl_loan_id."""
    agg = {"customer_id": "first", "disbursement_date": "first", "due_date": "first"}
    if "target" in rows:
        agg["target"] = "max"  # NaN for loans without a label (Test.csv)
    return rows.groupby("tbl_loan_id", as_index=False).agg(agg)


def borrower_history(loans, known_when="due", window=None):
    """For each loan, what NkwaPay already knew about this borrower on its disbursement_date.

    known_when: "due"  -> a past loan's outcome counts once its due_date has passed (safe).
                "sent" -> it counts as soon as the loan was sent (LEAKY, only to measure the cheat).
    window:     None = all past loans, an int k = only the last k finished loans,
                a string like "90D" = only loans that finished in the last 90 days.

    Everything is strictly before the day (allow_exact_matches=False): a loan sent the same day can't see the others.
    """
    loans = loans.sort_values("disbursement_date").reset_index(drop=True)
    t = loans[["tbl_loan_id", "customer_id", "disbursement_date"]]

    # 1. How many loans had this customer taken before today, and when was the latest?
    sent = loans[["customer_id", "disbursement_date"]].copy()
    sent["n_prev_loans"] = sent.groupby("customer_id").cumcount() + 1
    sent["last_sent"] = sent["disbursement_date"]
    out = pd.merge_asof(t, sent.rename(columns={"disbursement_date": "known_at"}),
                        left_on="disbursement_date", right_on="known_at", by="customer_id",
                        allow_exact_matches=False).drop(columns="known_at")
    out["n_prev_loans"] = out["n_prev_loans"].fillna(0)
    out["days_since_last_loan"] = (out["disbursement_date"] - out["last_sent"]).dt.days
    out = out.drop(columns="last_sent")

    # 2. Outcomes of past loans, each one "known" from the moment chosen by known_when. Only labelled loans count.
    when = "due_date" if known_when == "due" else "disbursement_date"
    ev = loans.loc[loans["target"].notna(), ["customer_id", when, "target"]].rename(columns={when: "known_at"})
    ev = ev.sort_values("known_at")
    g = ev.groupby("customer_id")["target"]
    if isinstance(window, int):
        ev["n_finished"] = g.transform(lambda s: s.rolling(window, min_periods=1).count())
        ev["n_defaults"] = g.transform(lambda s: s.rolling(window, min_periods=1).sum())
    else:
        ev["n_finished"] = g.cumcount() + 1
        ev["n_defaults"] = g.cumsum()
    keep = ["customer_id", "known_at", "n_finished", "n_defaults"]
    out = pd.merge_asof(out, ev[keep], left_on="disbursement_date", right_on="known_at",
                        by="customer_id", allow_exact_matches=False).drop(columns="known_at")

    if isinstance(window, str):  # time window: subtract what was already known before (today - window)
        out["start"] = out["disbursement_date"] - pd.Timedelta(window)
        old = pd.merge_asof(out[["start", "customer_id"]].sort_values("start").reset_index(),
                            ev[keep], left_on="start", right_on="known_at", by="customer_id",
                            allow_exact_matches=False).set_index("index").sort_index()
        for c in ["n_finished", "n_defaults"]:
            out[c] = out[c].fillna(0) - old[c].fillna(0)
        out = out.drop(columns="start")

    out[["n_finished", "n_defaults"]] = out[["n_finished", "n_defaults"]].fillna(0)
    # Unknown is not the same as "never defaulted": leave the rate empty and say so with a flag.
    out["past_default_rate"] = (out["n_defaults"] / out["n_finished"]).where(out["n_finished"] > 0)
    out["no_known_history"] = (out["n_finished"] == 0).astype(int)
    return out.drop(columns=["customer_id", "disbursement_date"])


if __name__ == "__main__":
    # Ama: three 7-day loans. Loan C is sent on 10 March, when loan A (due 8 Mar) is finished but B (due 12 Mar) is not.
    d = pd.to_datetime
    ama = pd.DataFrame({
        "tbl_loan_id": ["A", "B", "C", "D"],
        "customer_id": [1, 1, 1, 1],
        "disbursement_date": d(["2024-03-01", "2024-03-05", "2024-03-10", "2024-03-10"]),
        "due_date": d(["2024-03-08", "2024-03-12", "2024-03-17", "2024-03-17"]),
        "target": [1, 0, 0, np.nan],  # A defaulted; D has no label (a Test.csv loan)
    })
    h = borrower_history(ama).set_index("tbl_loan_id")
    assert h.loc["A", "n_prev_loans"] == 0 and h.loc["A", "no_known_history"] == 1
    assert h.loc["B", "n_finished"] == 0 and np.isnan(h.loc["B", "past_default_rate"])  # A not due yet on 5 Mar
    assert h.loc["C", "n_prev_loans"] == 2  # A and B; D was sent the same day, so it doesn't count
    assert h.loc["C", "n_finished"] == 1 and h.loc["C", "past_default_rate"] == 1.0  # only A is known
    assert h.loc["C", "days_since_last_loan"] == 5
    leaky = borrower_history(ama, known_when="sent").set_index("tbl_loan_id")
    assert leaky.loc["C", "n_finished"] == 2  # the leaky version already "knows" B's outcome
    assert borrower_history(ama, window=1).set_index("tbl_loan_id").loc["C", "n_finished"] == 1
    assert borrower_history(ama, window="3D").set_index("tbl_loan_id").loc["C", "n_finished"] == 1  # A finished 8 Mar
    assert borrower_history(ama, window="1D").set_index("tbl_loan_id").loc["C", "n_finished"] == 0
    print("Ama check passed")
