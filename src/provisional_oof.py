"""Step 6: provisional out-of-fold classification predictions."""

from pathlib import Path
import subprocess
import numpy as np
import pandas as pd

from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

from src.features import build, FEATURES, preprocessor, splits
from src.provisional_logistic import logit


def fit_and_predict(fit, cal, holdout):
    for name, df in [
        ("fit", fit),
        ("calibration", cal),
        ("holdout", holdout)
    ]:
        if df["target"].nunique() != 2:
            raise ValueError(
                f"{name} needs both target classes"
            )

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

    calibrator = LogisticRegression(max_iter=3000)
    calibrator.fit(logit(cal_scores), cal["target"])

    holdout_scores = base.predict_proba(
        holdout[FEATURES]
    )[:, 1]

    probabilities = calibrator.predict_proba(
        logit(holdout_scores)
    )[:, 1]

    assert np.isfinite(probabilities).all()
    assert ((probabilities >= 0) &
            (probabilities <= 1)).all()

    return probabilities


def partitions(df, scheme, fold_number, holdout):
    if scheme == "fold_customer":
        splitter = GroupShuffleSplit(
            n_splits=1,
            test_size=0.20,
            random_state=42 + fold_number
        )

        a, b = next(splitter.split(
            df,
            df["target"],
            groups=df["customer_id"]
        ))

        fit = df.iloc[a].copy()
        cal = df.iloc[b].copy()

        assert set(fit["customer_id"]).isdisjoint(
            set(cal["customer_id"])
        )
        assert set(df["customer_id"]).isdisjoint(
            set(holdout["customer_id"])
        )

        return fit, cal

    # Chronological fold: only historically mature labels.
    evaluation_start = holdout["disbursement_date"].min()

    eligible = df[
        (df["disbursement_date"] < evaluation_start) &
        (df["due_date"] < evaluation_start)
    ].copy()

    ordered = eligible.sort_values("disbursement_date")
    if len(ordered) < 100:
        raise ValueError(
            "Insufficient mature chronological training records"
        )

    split_position = int(len(ordered) * 0.75)
    calibration_start = ordered.iloc[
        split_position
    ]["disbursement_date"]

    fit = eligible[
        (eligible["disbursement_date"] < calibration_start) &
        (eligible["due_date"] < calibration_start)
    ].copy()

    cal = eligible[
        eligible["disbursement_date"] >= calibration_start
    ].copy()

    assert fit["due_date"].max() < calibration_start
    assert cal["due_date"].max() < evaluation_start
    assert fit["disbursement_date"].max() < (
        cal["disbursement_date"].min()
    )

    return fit, cal


def main():
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        text=True
    ).strip()
    assert branch == "feature/germain-classification"

    print("=== STEP 6: OUT-OF-FOLD PREDICTIONS ===")

    train, _ = build("data/zindi")
    frames = []

    for scheme in ["fold_customer", "time_block"]:
        print(f"\n=== {scheme} ===")

        for number, (learn_idx, test_idx) in enumerate(
            splits(train, scheme)
        ):
            learning = train.loc[learn_idx].copy()
            holdout = train.loc[test_idx].copy()

            fit, cal = partitions(
                learning, scheme, number, holdout
            )

            probabilities = fit_and_predict(
                fit, cal, holdout
            )

            actual = holdout["target"].to_numpy()

            result = pd.DataFrame({
                "ID": holdout["ID"].to_numpy(),
                "fold_scheme": scheme,
                "fold": number,
                "calibrated_probability": probabilities,
                "target": actual
            })

            frames.append(result)

            pr = average_precision_score(
                actual, probabilities
            )
            roc = roc_auc_score(
                actual, probabilities
            )

            print(
                f"Fold {number}:",
                f"fit={len(fit)}",
                f"cal={len(cal)}",
                f"holdout={len(holdout)}",
                f"PR-AUC={pr:.5f}",
                f"ROC-AUC={roc:.5f}"
            )

    output = pd.concat(frames, ignore_index=True)

    for scheme, group in output.groupby("fold_scheme"):
        assert group["ID"].is_unique
        assert group["calibrated_probability"].between(
            0, 1
        ).all()
        print(
            f"\n{scheme}:",
            f"{len(group):,} OOF predictions"
        )

    destination = Path(
        "data/predictions/provisional_logistic_oof.csv"
    )

    if destination.exists():
        raise FileExistsError(
            f"Review existing file before replacing: {destination}"
        )

    destination.parent.mkdir(
        parents=True, exist_ok=True
    )

    output.to_csv(destination, index=False)

    saved = pd.read_csv(destination)
    assert len(saved) == len(output)

    print("\n=== OOF ARTIFACT ===")
    print("Saved:", destination)
    print("Total prediction rows:", len(saved))
    print("Fold schemes:", saved["fold_scheme"].unique().tolist())
    print("Existing holdout artifacts remain unchanged.")
    print("No raw data committed.")
    print("=== OOF GENERATION COMPLETE ===")


if __name__ == "__main__":
    main()
