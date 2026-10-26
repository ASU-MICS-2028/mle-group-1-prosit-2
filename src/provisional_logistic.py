"""Step 6: Reproducible provisional default classifier."""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    brier_score_loss,
    log_loss
)

from src.features import build, FEATURES, preprocessor


def logit(p):
    p = np.clip(np.asarray(p), 1e-10, 1 - 1e-10)
    return np.log(p / (1 - p)).reshape(-1, 1)


class ProvisionalCalibratedModel:
    """Fitted preprocessing + logistic model + Platt scaling."""

    def __init__(self, base_model, calibrator):
        self.base_model = base_model
        self.calibrator = calibrator
        self.features = list(FEATURES)
        self.classes_ = np.array([0, 1])

    def predict_proba(self, X):
        raw = self.base_model.predict_proba(X)[:, 1]
        p = self.calibrator.predict_proba(logit(raw))[:, 1]
        return np.column_stack((1 - p, p))


def main():

    print("=== STEP 6: PROVISIONAL MODEL ===")

    train, _ = build("data/zindi")
    dates = pd.to_datetime(train["disbursement_date"])
    due = pd.to_datetime(train["due_date"])

    fit_end = pd.Timestamp("2022-12-01")
    cal_end = pd.Timestamp("2024-07-01")

    fit = train[
        (dates < fit_end) &
        (due < fit_end)
    ].copy()

    cal = train[
        (dates >= fit_end) &
        (dates < cal_end) &
        (due < cal_end)
    ].copy()

    valid = train[dates >= cal_end].copy()

    assert fit["target"].nunique() == 2
    assert cal["target"].nunique() == 2
    assert valid["target"].nunique() == 2

    print("Training records:", len(fit))
    print("Calibration records:", len(cal))
    print("Holdout records:", len(valid))
    print("Approved features:", len(FEATURES))

    base = make_pipeline(
        preprocessor(FEATURES),
        LogisticRegression(
            class_weight=None,
            max_iter=3000,
            random_state=42
        )
    )

    base.fit(fit[FEATURES], fit["target"])

    cal_scores = base.predict_proba(
        cal[FEATURES]
    )[:, 1]

    platt = LogisticRegression(max_iter=3000)
    platt.fit(logit(cal_scores), cal["target"])

    model = ProvisionalCalibratedModel(base, platt)

    probabilities = model.predict_proba(
        valid[FEATURES]
    )[:, 1]

    assert np.isfinite(probabilities).all()
    assert ((probabilities >= 0) &
            (probabilities <= 1)).all()

    actual = valid["target"].to_numpy()

    print("\n=== HOLDOUT METRICS ===")
    print(
        "PR-AUC:",
        round(average_precision_score(actual, probabilities), 6)
    )
    print(
        "ROC-AUC:",
        round(roc_auc_score(actual, probabilities), 6)
    )
    print(
        "Brier:",
        round(brier_score_loss(actual, probabilities), 6)
    )
    print(
        "Log loss:",
        round(log_loss(actual, probabilities), 6)
    )
    print(
        "Mean predicted risk:",
        f"{probabilities.mean():.4%}"
    )
    print(
        "Actual default rate:",
        f"{actual.mean():.4%}"
    )

    model_path = Path(
        "data/models/provisional_logistic.joblib"
    )
    predictions_path = Path(
        "data/predictions/provisional_logistic.csv"
    )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    predictions_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    predictions = pd.DataFrame({
        "ID": valid["ID"].to_numpy(),
        "fold_scheme": "chronological_holdout",
        "fold": "2024-07-onward",
        "calibrated_probability": probabilities,
        "target": actual
    })

    assert len(predictions) == len(valid)
    assert predictions["ID"].is_unique

    joblib.dump(model, model_path)
    predictions.to_csv(predictions_path, index=False)

    # Reload to verify the handoff artifact works.
    restored = joblib.load(model_path)

    restored_probs = restored.predict_proba(
        valid[FEATURES]
    )[:, 1]

    assert np.allclose(
        restored_probs, probabilities,
        rtol=1e-10, atol=1e-12
    )

    saved = pd.read_csv(predictions_path)
    assert len(saved) == len(valid)

    print("\n=== ARTIFACT VERIFICATION ===")
    print("Saved model:", model_path)
    print("Saved predictions:", predictions_path)
    print("Prediction rows:", len(saved))
    print("Reloaded model predictions match: YES")
    print("Private data files must not be committed.")
    print("=== STEP 6 ARTIFACT GENERATION COMPLETE ===")


if __name__ == "__main__":
    main()
