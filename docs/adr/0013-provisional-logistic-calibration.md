# 0013 · Provisional Logistic Regression and Calibration

- Status: Provisional
- Date: 26 Oct 2026
- Owner: Germain
- Step: 6

## Context

The classification task requires default probabilities that
can support NkwaPay's lending decisions. Defaults are rare,
and historical default rates change considerably over time.

## Options tested

Initial future-validation calibration comparison:

| Method | PR-AUC | Brier |
|---|---:|---:|
| Unweighted, none | 0.15769 | 0.08755 |
| Unweighted, Platt | 0.15769 | 0.08585 |
| Unweighted, isotonic | 0.13626 | 0.08664 |
| Balanced, none | 0.15375 | 0.16595 |
| Balanced, Platt | 0.15375 | 0.08825 |
| Balanced, isotonic | 0.12906 | 0.08865 |

## Provisional decision

Use unweighted Logistic Regression with Platt scaling
as the provisional candidate.

Platt scaling gave the best Brier score of the six
initial combinations, while preserving PR-AUC.

This does not establish that its probabilities are
adequately calibrated or ready for lending decisions.

## Maturity-corrected chronological validation

- Model fitting: 62,189 records.
- Calibration: 1,718 records.
- Future validation: 2,486 records.
- PR-AUC: 0.157661.
- ROC-AUC: 0.647583.
- Brier: 0.086013.
- Log loss: 0.318063.
- Mean predicted default risk: 5.1713%.
- Observed default rate: 9.4127%.

Historical constant baseline:
- Brier: 0.085578.
- Log loss: 0.313628.

The baseline still has slightly better probability
scores, but cannot distinguish borrowers by risk.

## Reproducible artifacts

Source:
- src/provisional_logistic.py
- src/provisional_oof.py

Local outputs (ignored by Git):
- data/models/provisional_logistic.joblib
- data/predictions/provisional_logistic.csv
- data/predictions/provisional_logistic_oof.csv

OOF verification:
- Customer-grouped: 68,464 predictions, 5 folds.
- Chronological: 54,771 predictions, 4 folds.

## Limitations and next steps

1. Due dates are proxies for label availability.
2. The model underpredicts future default rates.
3. Repeated lender records require clear interpretation.
4. The model artifact is not a final full-data refit.
5. The temporal holdout has been used for development.
6. Final model selection requires broader comparisons,
   cost-based thresholds and uncertainty analysis.
7. The Ghana transfer evaluation remains outstanding.

## Consequences

Retain Logistic Regression as a provisional benchmark.
Do not use its current probabilities as approved credit
decisions. Complete the final classification comparison
before approving a model for the scoring service.

## Full-data provisional refit

On 26 October 2026, Germain completed the
provisional full-data fitting procedure.

- Labeled records: 68,464.
- Unlabeled test records: 18,594.
- Approved features: 13.
- Temporal OOF calibration records: 54,771.
- Calibration method: Platt scaling.
- Average predicted test default risk: 3.9289%.

The complete model was saved to:
data/models/provisional_logistic_full.joblib

Test predictions were saved to:
data/predictions/provisional_logistic_test.csv

Model serialization and prediction consistency
checks passed successfully.

The calibrator was fitted using raw temporal
out-of-fold predictions from earlier models,
then applied to a base model refitted on all
retained labeled records.

Limitations:
- Calibration may change after full-data refitting.
- The full-data model has no independent test score.
- Ghanaian outcome performance remains unknown.
- Due dates are proxies for label availability.
- The full-data model is provisional, not approved.
- Competition submission formatting is separate
  from the saved probability prediction file.

Step 7 will compare additional models and
establish the final operating decision.
