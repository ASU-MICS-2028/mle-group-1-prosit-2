"""Step 8: the top reasons behind a decision, in words a borrower understands (ADR 0017).

For logistic regression the risk score (log-odds) is a sum: intercept + weight x prepared value, column by column.
A clue's push on one applicant = weight x (their prepared value - the reference applicant's). Platt calibration
multiplies every push by the same positive number, so it never reorders reasons. Pushes are added up per THEME,
because clues that move together (past loans and finished loans, last and usual loan size) otherwise cancel each
other out and give contradicting reasons (learnings/08). Each theme is worded with the applicant's own numbers.

    ref = reference(model, train[FEATURES])                                   # once, from training rows
    reasons(model, applicants[FEATURES], ref, known_types=set(train.loan_type))  # up to 3 sentences each
"""
import numpy as np
import pandas as pd

from src.features import FEATURES

# Each of the 13 clues belongs to one plain theme; clues that move together share a theme.
THEMES = {
    "loan_type": "loan product", "New_versus_Repeat": "loan product",
    "duration": "loan length",
    "n_prev_loans": "borrowing history", "n_finished": "borrowing history", "days_since_last_loan": "borrowing history",
    "n_loans_last_7d": "borrowing history", "n_loans_last_30d": "borrowing history",
    "mean_prev_amount": "loan sizes", "last_amount": "loan sizes",
    "n_defaults": "repayment record", "past_default_rate": "repayment record", "no_known_history": "repayment record",
}
MIN_PUSH = 0.2  # a reason must raise the log-odds by at least this much (about +22% odds); tested in learnings/08


def _parts(model):
    """(preparation step, logistic regression, Platt slope) from a Pipeline or a step 7 PlattCalibratedModel."""
    pipe = getattr(model, "base", model)
    slope = model.calibrator.coef_[0, 0] if hasattr(model, "calibrator") else 1.0
    return pipe[0], pipe[-1], slope


def _prepared(model, X):
    pre = _parts(model)[0]
    Z = pre.transform(X)
    return pd.DataFrame(Z.toarray() if hasattr(Z, "toarray") else Z, columns=pre.get_feature_names_out(), index=X.index)


def clue_of(column):
    """Prepared column name -> the clue it came from ('onehotencoder__loan_type_Type_1' -> 'loan_type')."""
    name = column.split("__", 1)[1].replace("missingindicator_", "")
    return next(c for c in sorted(FEATURES, key=len, reverse=True) if name.startswith(c))


def reference(model, X, kind="average", threshold=None):
    """The applicant everyone is compared with, in prepared-column space.
    average: the average loan. approved: the average loan the model approves (needs threshold).
    best: each column at its least risky value seen in X (the 'maximum points' method)."""
    Z, lr = _prepared(model, X).to_numpy(), _parts(model)[1]
    if kind == "approved":
        Z = Z[model.predict_proba(X)[:, 1] <= threshold]
    if kind == "best":
        return np.where(lr.coef_[0] > 0, Z.min(0), Z.max(0))
    return Z.mean(0)


def pushes(model, X, ref, level="theme", themes=THEMES):
    """How much each column / clue / theme pushes each applicant's calibrated log-odds above the reference."""
    _, lr, slope = _parts(model)
    Z = _prepared(model, X)
    P = slope * lr.coef_[0] * (Z - ref)
    if level == "column":
        return P
    clues = P.T.groupby(P.columns.map(clue_of)).sum().T
    return clues if level == "clue" else clues.T.groupby(clues.columns.map(themes)).sum().T


def _n(x, word):
    return f"{x:.0f} {word}" + ("" if round(x) == 1 else "s")


def sentence(theme, row, clue_push, high, known_types=None):
    """One plain sentence for a risk-raising theme, from the clue inside it that pushes hardest.
    high[c] says whether the applicant's value of clue c is above the reference applicant's."""
    c = clue_push.idxmax()
    v = row[c]
    if theme == "loan product":
        if c == "New_versus_Repeat":
            return "This is a first loan with this lender; first loans are repaid less often than repeat loans."
        if known_types is not None and v not in known_types:
            return f"We have no repayment record for this kind of loan ({v}), so we treat it with caution."
        return f"Loans of this kind ({v}) have been repaid less often than others."
    if theme == "loan length":
        return (f"The loan is for {_n(v, 'day')}; longer loans are repaid less often." if high[c]
                else f"The loan is for only {_n(v, 'day')}; loans this short have been repaid less often.")
    if theme == "borrowing history":
        if pd.isna(row["days_since_last_loan"]) or row["n_prev_loans"] == 0:
            return "This is your first loan with us, so we have no borrowing history to go on."
        if c == "days_since_last_loan":
            return (f"Your last loan was {_n(v, 'day')} ago; a long gap gives us less recent information." if high[c]
                    else f"Your last loan was only {_n(v, 'day')} ago.")
        if c in ("n_loans_last_7d", "n_loans_last_30d"):
            span = "7" if c == "n_loans_last_7d" else "30"
            return (f"You took {_n(v, 'loan')} in the last {span} days, more than most borrowers." if high[c]
                    else f"You took {'no loans' if v == 0 else 'only ' + _n(v, 'loan')} in the last {span} days; "
                         "regular borrowers have repaid more reliably.")
        n = row["n_prev_loans"]
        return (f"You have only {_n(n, 'earlier loan')} with us, so we know little about how you repay." if not high[c]
                else f"You have taken {_n(n, 'earlier loan')}; borrowing this much has been linked to more defaults.")
    if theme == "loan sizes":
        if pd.isna(row["last_amount"]):
            return "You have no earlier loans with us, so we cannot compare loan sizes."
        if row["last_amount"] > row["mean_prev_amount"]:
            return (f"Your most recent loan ({row['last_amount']:,.0f}) was larger than your usual loan "
                    f"({row['mean_prev_amount']:,.0f}).")
        return f"Your usual loan ({row['mean_prev_amount']:,.0f}) is smaller than most; small loans were repaid less often."
    # repayment record
    if row["n_defaults"] > 0:
        return f"You did not repay {_n(row['n_defaults'], 'earlier loan')}."
    return ("We do not yet know how your earlier loans ended, so we have no repayment record for you."
            if row["no_known_history"] == 1 else "Your repayment record with us is short.")


def reasons(model, X, ref, k=3, known_types=None, min_push=MIN_PUSH):
    """Up to k plain sentences per applicant, strongest first; only themes that raise risk by at least min_push."""
    themes, clues = pushes(model, X, ref, "theme"), pushes(model, X, ref, "clue")
    dev = _prepared(model, X) - ref
    main = {c: next(col for col in dev.columns if clue_of(col) == c and "missingindicator" not in col)
            for c in FEATURES if c not in ("loan_type", "New_versus_Repeat")}
    out = []
    for i in X.index:
        t = themes.loc[i]
        top = t[t >= min_push].sort_values(ascending=False).index[:k]
        high = {c: dev.loc[i, col] > 0 for c, col in main.items()}
        out.append([sentence(th, X.loc[i], clues.loc[i, [c for c in FEATURES if THEMES[c] == th]], high, known_types)
                    for th in top])
    return out


if __name__ == "__main__":
    # Self-check on a tiny made-up model: pushes add up exactly to the change in log-odds, and the clue that
    # really drives risk comes out as the top reason, worded in the right direction.
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from src.features import preprocessor
    rng = np.random.default_rng(0)
    n = 400
    X = pd.DataFrame({"loan_type": rng.choice(["Type_1", "Type_7"], n), "duration": rng.choice([7, 30], n),
                      "New_versus_Repeat": rng.choice(["Repeat Loan", "New Loan"], n), "n_prev_loans": rng.integers(1, 20, n),
                      "n_finished": rng.integers(0, 10, n), "n_defaults": rng.integers(0, 2, n),
                      "past_default_rate": rng.random(n), "no_known_history": rng.integers(0, 2, n),
                      "days_since_last_loan": rng.integers(1, 60, n).astype(float), "n_loans_last_7d": rng.integers(0, 5, n),
                      "n_loans_last_30d": rng.integers(0, 10, n), "mean_prev_amount": rng.uniform(1e3, 1e4, n),
                      "last_amount": rng.uniform(1e3, 1e4, n)})[FEATURES]
    y = (X.n_loans_last_7d + rng.random(n) * 2 < 2).astype(int)  # FEW recent loans = risky, as in the real data
    pipe = make_pipeline(preprocessor(FEATURES), LogisticRegression(max_iter=2000)).fit(X, y)
    ref = reference(pipe, X)
    p = pipe.predict_proba(X)[:, 1]
    gap = np.log(p / (1 - p)) - (pipe[-1].intercept_[0] + pipe[-1].coef_[0] @ ref)  # applicant minus reference
    for level in ("column", "clue", "theme"):
        assert np.allclose(pushes(pipe, X, ref, level).sum(axis=1), gap), level
    r = reasons(pipe, X, ref, known_types={"Type_1"})
    assert all(len(x) <= 3 and all("nan" not in s for s in x) for x in r)
    first = pd.Series([x[0] if x else "" for x in r])[(y == 1).to_numpy()]
    assert first.str.contains("in the last 7 days; regular borrowers").mean() > .8, first.value_counts().head()
    print("Reasons check passed")
