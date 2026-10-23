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


def calendar(rows):
    """Month, weekday (0 = Monday) and day of month the money was sent. No year: the model will only ever meet future years."""
    d = rows["disbursement_date"]
    return pd.DataFrame({"month": d.dt.month, "weekday": d.dt.weekday, "day_of_month": d.dt.day}, index=rows.index)


# The only indicators that exist for both Kenya and Ghana in 2019-2023. The others are empty for Ghana, or stop in 2021.
MACRO = {
    "Inflation, consumer prices (annual %)": "inflation",
    "Deposit interest rate (%)": "deposit_rate",
    "Official exchange rate (LCU per US$, period average)": "fx_per_usd",
    "Unemployment rate": "unemployment",
}


def load_macro(path):
    """economic_indicators.csv (one column per year) -> one row per country-year."""
    ec = pd.read_csv(path)
    ec = ec[ec["Indicator"].isin(MACRO)].melt(id_vars=["Country", "Indicator"], var_name="year")
    ec["year"] = ec["year"].str[2:].astype(int)
    ec["Indicator"] = ec["Indicator"].map(MACRO)
    return ec.pivot_table(index=["Country", "year"], columns="Indicator", values="value").reset_index()


def add_macro(rows, macro, lag=1):
    """Macro clues for each row's country and year.

    lag=1: use last year's figures. Annual statistics for a year are only published after it ends,
           so on decision day only last year's numbers are actually known (safe; 2024 loans use 2023).
    lag=0: use the same year's figures (slightly leaky), with 2024 filled by carrying 2023 forward.
    """
    key = pd.DataFrame({"Country": rows["country_id"].values,
                        "year": rows["disbursement_date"].dt.year.values - lag})
    if lag == 0:
        key["year"] = key["year"].clip(upper=macro["year"].max())
    return key.merge(macro, on=["Country", "year"], how="left").drop(columns=["Country", "year"]).set_index(rows.index)


BASE = ["loan_type", "duration", "New_versus_Repeat"]  # frozen by the feature audit (learnings/03)
CALENDAR = ["month", "weekday", "day_of_month"]
HISTORY = ["n_prev_loans", "n_finished", "n_defaults", "past_default_rate", "no_known_history", "days_since_last_loan"]


def build(data_dir, known_when="due", window=None, macro_lag=1):
    """Train and test tables with every clue, one row per Zindi row. Pick the columns you need from BASE, CALENDAR,
    HISTORY and MACRO.values(). Train also gets the fold columns (see add_folds)."""
    p = ["disbursement_date", "due_date"]
    tr = pd.read_csv(f"{data_dir}/Train.csv", parse_dates=p)
    te = pd.read_csv(f"{data_dir}/Test.csv", parse_dates=p)
    # Loans not due when the data was collected: "paid" really means "not unpaid yet" (learnings/03), so not used to train.
    tr = tr[tr["due_date"] <= tr["disbursement_date"].max()]
    # History uses train and test loans together, so test customers get their earlier train loans as history.
    hist = borrower_history(to_loans(pd.concat([tr, te])), known_when, window).set_index("tbl_loan_id")
    macro = load_macro(f"{data_dir}/economic_indicators.csv")
    out = []
    for df in (tr, te):
        df = df.reset_index(drop=True)
        df = pd.concat([df, calendar(df), add_macro(df, macro, macro_lag)], axis=1)
        out.append(df.join(hist, on="tbl_loan_id"))
    return add_folds(out[0]), out[1]


def add_folds(df, k=5, seed=0):
    """Three ways to split into learning and testing parts. Each column gives every row a fold number 0..k-1.

    fold_shuffled: rows shuffled at random (keeps the default share equal). The naive way: one customer's loans
                   land on both sides, so the model can partly recognise the customer.
    fold_customer: all of a customer's loans stay together (StratifiedGroupKFold by customer_id).
    time_block:    loans cut into k equal-sized blocks by date. Learn from blocks < i, test on block i (newer loans).
    """
    from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
    df = df.copy()
    y, groups = df["target"], df["customer_id"]
    for name, splitter, g in [("fold_shuffled", StratifiedKFold(k, shuffle=True, random_state=seed), None),
                              ("fold_customer", StratifiedGroupKFold(k, shuffle=True, random_state=seed), groups)]:
        for i, (_, test_idx) in enumerate(splitter.split(df, y, g)):
            df.loc[df.index[test_idx], name] = i
    order = df["disbursement_date"].rank(method="first")
    df["time_block"] = np.minimum((order - 1) * k // len(df), k - 1)
    return df.astype({"fold_shuffled": int, "fold_customer": int, "time_block": int})


def splits(df, scheme):
    """Yield (learn_index, test_index) for a fold column made by add_folds."""
    f = df[scheme]
    if scheme == "time_block":  # only ever learn from the past
        for i in range(1, f.max() + 1):
            yield df.index[f < i], df.index[f == i]
    else:
        for i in range(f.max() + 1):
            yield df.index[f != i], df.index[f == i]


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

    # Macro: a 2024 Kenyan loan must get 2023 figures with lag=1, and also with lag=0 (2024 isn't published).
    m = pd.DataFrame({"Country": ["Kenya"] * 2, "year": [2022, 2023], "inflation": [7.66, 7.67]})
    r = pd.DataFrame({"country_id": ["Kenya"] * 2, "disbursement_date": d(["2023-06-01", "2024-06-01"])})
    assert add_macro(r, m, lag=1)["inflation"].tolist() == [7.66, 7.67]
    assert add_macro(r, m, lag=0)["inflation"].tolist() == [7.67, 7.67]
    assert calendar(r).loc[0, "month"] == 6
    print("Macro and calendar check passed")

    # Folds: a customer never on both sides of fold_customer; time splits only ever learn from older loans.
    rng = np.random.default_rng(0)
    f = pd.DataFrame({"customer_id": rng.integers(0, 40, 400), "target": rng.random(400) < 0.1,
                      "disbursement_date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 365, 400), "D")})
    f = add_folds(f)
    assert (f.groupby("customer_id")["fold_customer"].nunique() == 1).all()
    for learn, test in splits(f, "time_block"):
        assert f.loc[learn, "disbursement_date"].max() <= f.loc[test, "disbursement_date"].min()
    print("Folds check passed")
