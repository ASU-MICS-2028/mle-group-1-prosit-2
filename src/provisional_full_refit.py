"""Step 6: Full-data provisional model with temporal OOF calibration."""

from pathlib import Path
import subprocess
import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

from src.features import build, FEATURES, preprocessor, splits
from src.provisional_logistic import (
    logit,
    ProvisionalCalibratedModel
)


def base_model():
    return make_pipeline(
        preprocessor(FEATURES),
        LogisticRegression(
            class_weight=None,
            max_iter=3000,
            random_state=42
        )
    )


def main():
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        text=True
    ).strip()
    assert branch == "feature/germain-classification"

    print("=== STEP 6: FULL-DATA PROVISIONAL REFIT ===")

    model_path = Path(
        "data/models/provisional_logistic_full.joblib"
    )
    test_path = Path(
        "data/predictions/provisional_logistic_test.csv"
    )

    assert not model_path.exists(), "Full model already exists"
    assert not test_path.exists(), "Test predictions already exist"

    train, test = build("data/zindi")

    print("Labeled records:", len(train))
    print("Unlabeled test records:", len(test))
    print("Approved features:", len(FEATURES))

    # Collect raw predictions on future-held-out folds.
    # These predictions were not made by models trained
    # on their own target labels.
    oof_scores = []
    oof_targets = []

    print("\n=== TEMPORAL OOF CALIBRATION DATA ===")

    for number, (learn_idx, test_idx) in enumerate(
        splits(train, "time_block"), start=1
    ):
        learning = train.loc[learn_idx].copy()
        holdout = train.loc[test_idx].copy()

        cutoff = holdout["disbursement_date"].min()

        eligible = learning[
            (learning["disbursement_date"] < cutoff) &
            (learning["due_date"] < cutoff)
        ].copy()

        # Guard against one underlying loan appearing
        # in both sides of a fold boundary.
        eligible = eligible[
            ~eligible["tbl_loan_id"].isin(
                holdout["tbl_loan_id"]
            )
        ].copy()

        assert eligible["target"].nunique() == 2
        assert holdout["target"].nunique() == 2
        assert eligible["due_date"].max() < cutoff

        fold_model = base_model()
        fold_model.fit(
            eligible[FEATURES],
            eligible["target"]
        )

        probabilities = fold_model.predict_proba(
            holdout[FEATURES]
        )[:, 1]

        assert np.isfinite(probabilities).all()

        oof_scores.append(probabilities)
        oof_targets.append(
            holdout["target"].to_numpy()
        )

        print(
            f"Fold {number}:",
            f"fit={len(eligible)}",
            f"holdout={len(holdout)}",
            f"PR-AUC={average_precision_score(holdout['target'], probabilities):.5f}",
            f"ROC-AUC={roc_auc_score(holdout['target'], probabilities):.5f}"
        )

    oof_scores = np.concatenate(oof_scores)
    oof_targets = np.concatenate(oof_targets)

    print("\nTemporal OOF records:", len(oof_scores))
    assert len(oof_scores) == 54771

    # Calibrate using predictions generated without
    # training on their corresponding target labels.
    calibrator = LogisticRegression(max_iter=3000)
    calibrator.fit(
        logit(oof_scores),
        oof_targets
    )

    print("Platt calibrator fitted.")

    # Refit the base classifier on the full labeled set.
    # All retained labels satisfy the dataset's
    # November 14, 2024 due-date maturity proxy.
    full_base = base_model()
    full_base.fit(
        train[FEATURES],
        train["target"]
    )

    final_model = ProvisionalCalibratedModel(
        full_base,
        calibrator
    )

    test_probs = final_model.predict_proba(
        test[FEATURES]
    )[:, 1]

    assert len(test_probs) == len(test)
    assert np.isfinite(test_probs).all()
    assert ((test_probs >= 0) & (test_probs <= 1)).all()

    predictions = pd.DataFrame({
        "ID": test["ID"].to_numpy(),
        "probability_default": test_probs
    })

    assert predictions["ID"].is_unique

    # Save only after all numerical checks pass.
    model_path.parent.mkdir(
        parents=True, exist_ok=True
    )
    test_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    joblib.dump(final_model, model_path)
    predictions.to_csv(test_path, index=False)

    # Verify serialization.
    restored = joblib.load(model_path)

    check_probs = restored.predict_proba(
        test[FEATURES]
    )[:, 1]

    assert np.allclose(
        check_probs, test_probs,
        rtol=1e-10,
        atol=1e-12
    )

    saved = pd.read_csv(test_path)
    assert len(saved) == len(test)
    assert np.allclose(
        saved["probability_default"],
        test_probs
    )

    print("\n=== FINAL ARTIFACT CHECK ===")
    print("Full-data model:", model_path)
    print("Test predictions:", test_path)
    print("Prediction records:", len(saved))
    print(
        "Average test predicted risk:",
        f"{test_probs.mean():.4%}"
    )
    print("Model reload verified: YES")
    print("All predictions finite and in [0,1]: YES")
    print("Existing research artifacts unchanged.")

    print("\nIMPORTANT:")
    print("OOF-based calibration is provisional.")
    print("No independent evaluation of this refit was performed.")
    print("Ghana performance is unverified.")
    print("No raw data or models should be committed.")

    print("\n=== PROVISIONAL FULL REFIT COMPLETE ===")


if __name__ == "__main__":
    main()
