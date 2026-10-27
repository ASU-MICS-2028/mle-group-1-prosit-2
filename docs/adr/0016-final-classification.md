# ADR 0016 ? Classification model for integration

**Date:** 27 October 2026
**Owner:** Germain
**Status:** Accepted for integration evaluation; not approved for production

## Context

NkwaPay requires a calibrated default-risk score and an explainable decision process. We tested a majority baseline and six classifier configurations under shuffled, customer-grouped and chronological validation.

## Decision

Select **standard Logistic Regression with Platt calibration** as the integration candidate for Joseph's scorer and Liza's fairness analysis.

Keep the operating threshold subject to separate review.

## Evidence

| Model | Shuffled | Customer-grouped | Future loans |
|---|---:|---:|---:|
| Majority baseline | 0.0184 | 0.0184 | 0.0182 |
| Logistic Regression | 0.2211 | 0.2146 | 0.1075 |
| Logistic balanced | 0.2163 | 0.2095 | 0.1054 |
| k-NN | 0.1809 | 0.1675 | 0.0635 |
| Pruned Decision Tree | 0.1261 | 0.1364 | 0.0530 |
| Random Forest | 0.2225 | 0.2085 | 0.0682 |
| LightGBM | 0.2381 | 0.1949 | 0.0569 |

LR minus RF pooled chronological PR-AUC = +0.01514. Paired customer-bootstrap 95% interval [+0.00057, +0.03219], 300 valid replicates. Noise floor ±0.0263. Point estimate exceeds noise floor: False. Interval wholly above positive floor: False. The bootstrap describes uncertainty for this validation procedure, not Ghana performance.

The chronological results favour Logistic Regression. However, the estimated advantage over Random Forest does not reliably exceed the project noise floor.

## Threshold and temporal limitations

The Kenya 2.1% lending threshold yields widely varying approval rates across quarters. Its pooled average is not sufficient evidence for a stable operating policy.

The Ghana 3.2% threshold was tested on Kenyan labelled loans. This is a scenario calculation, not validated Ghanaian performance.

## Reproducibility

Implementation: `src/classification_experiments.py`.

Notebook: `notebooks/02_classification.ipynb`.

Tables and figures: `learnings/tables/` and `learnings/figures/`.

The saved model and individual loan predictions remain in ignored local storage.

## Remaining acceptance conditions

- Verify the final training/calibration boundaries.
- Confirm notebook execution independently on a fresh clone with the required local data.
- Review future-period calibration and lending costs.
- Complete fairness and Ghana transfer assessment.
- Confirm the scorer's input/output contract with Joseph.

This ADR approves an integration candidate, not real-world lending deployment.
