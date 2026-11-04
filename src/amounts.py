"""Step 9 (Task 1): predict the loan amount, and turn the prediction into a loan limit (ADR 0018).

The model learns log(Total_Amount) from the shared FEATURES. The log is used because amounts are very lopsided
(2 to 23 million shillings): on the log scale "10x bigger" is the same step whatever the size (learnings/09).

    model = final_amount_model(train)     # once, from every labelled Kenyan loan
    model.typical(applicants[FEATURES])   # the amount similar borrowers usually got (local currency)
    model.limit(applicants[FEATURES])     # the limit to offer: typical x a cautious factor (see LIMIT_QUANTILE)
    model.average(applicants[FEATURES])   # for adding up reserves: the average, not the typical, amount
"""
import numpy as np
import pandas as pd

from src.features import FEATURES, load_macro, preprocessor

AMOUNT_CLUES = ["mean_prev_amount", "last_amount"]  # the clues measured in money (need converting like the target)
LIMIT_QUANTILE = 0.75  # the limit = the amount 75% of similar recent borrowers got at most (tested in learnings/09)


def usd_rate(rows, data_dir):
    """Local currency per US dollar for each row: the average rate of the year the loan was sent.
    2024 has no published rate yet, so it uses 2023's."""
    fx = load_macro(f"{data_dir}/economic_indicators.csv").set_index(["Country", "year"])["fx_per_usd"]
    year = rows["disbursement_date"].dt.year.clip(upper=fx.index.get_level_values("year").max())
    return pd.Series(fx.reindex(list(zip(rows["country_id"], year))).to_numpy(), index=rows.index)


def regressor():
    """The chosen model (ADR 0018), with the settings picked in notebooks/03_regression.ipynb section 3."""
    from lightgbm import LGBMRegressor
    from sklearn.pipeline import make_pipeline
    return make_pipeline(preprocessor(FEATURES),
                         LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=31, verbose=-1, random_state=0))


class AmountModel:
    """A fitted log-amount model plus two numbers measured on loans it did not learn from:
    offset = the LIMIT_QUANTILE of (real log amount - predicted), smear = mean of e^(real - predicted)."""

    def __init__(self, pipe, offset, smear):
        self.pipe, self.offset, self.smear = pipe, offset, smear

    def predict_log(self, X):
        return self.pipe.predict(X[FEATURES])

    def typical(self, X):
        return np.exp(self.predict_log(X))

    def average(self, X):
        return np.exp(self.predict_log(X)) * self.smear

    def limit(self, X):
        return np.exp(self.predict_log(X) + self.offset)


def final_amount_model(train, quantile=LIMIT_QUANTILE, make=regressor):
    """Measure the offset and smearing on the newest 20% of loans with a model learned on the older 80%,
    then learn the final model on every loan."""
    o = train.sort_values("disbursement_date", kind="mergesort")
    cut = o["disbursement_date"].iloc[int(0.8 * len(o))]
    old, new = o[o["disbursement_date"] < cut], o[o["disbursement_date"] >= cut]
    m = make().fit(old[FEATURES], np.log(old["Total_Amount"]))
    resid = np.log(new["Total_Amount"]) - m.predict(new[FEATURES])
    pipe = make().fit(train[FEATURES], np.log(train["Total_Amount"]))
    return AmountModel(pipe, float(np.quantile(resid, quantile)), float(np.mean(np.exp(resid))))
