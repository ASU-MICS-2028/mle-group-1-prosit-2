# 0016 · Final classification model and cut-off

**Date:** 27 October 2026
**Owner:** Germain
**Status:** Accepted (model: Germain; cut-off and review: Joseph, 28 Oct). Replaces [0013](0013-provisional-logistic-calibration.md). Not approved for real lending.

## Context

NkwaPay requires a calibrated default-risk score and an explainable decision process. We tested a majority baseline and six classifier configurations under shuffled, customer-grouped and chronological validation.

## Decision

Select **standard Logistic Regression with Platt calibration** as the integration candidate for Joseph's scorer and Liza's fairness analysis.

**Cut-off: Liza's cost cut-off, 2.1% (Kenya) and 3.2% (Ghana)**; the repeat-business cut-offs 9.6% / 14.2% are reported as the alternative.

## Evidence

| Model | Shuffled | Customer-grouped | Future loans |
|---|---:|---:|---:|
| Majority baseline | 0.0184 | 0.0184 | 0.0182 |
| Logistic Regression | 0.2215 | 0.2156 | 0.1075 |
| Logistic balanced | 0.2173 | 0.2098 | 0.1054 |
| k-NN | 0.1811 | 0.1685 | 0.0638 |
| Pruned Decision Tree | 0.1261 | 0.1364 | 0.0530 |
| Random Forest | 0.2227 | 0.2083 | 0.0683 |
| LightGBM | 0.2381 | 0.1949 | 0.0569 |

LR minus RF on future loans, block by block: +0.013, +0.077, +0.062, +0.004 (mean **+0.039**, LR ahead in 4/4, above the ±0.0263 noise floor). Pooled over all blocks: +0.015, customer-bootstrap 95% CI [+0.001, +0.033], which is inside the noise because the large 2022 blocks dominate. Both point to Logistic Regression. Future-loan lift (PR-AUC ÷ default rate, averaged over blocks): LR 7.6, RF 3.9, LightGBM 3.5, which agrees with step 5 (7.97).

## Threshold and temporal limitations

The 2.1% cut-off approves 94–98% of 2022 loans but 2–37% of 2023–24 loans. Those later loans defaulted at 7–14%, so declining most of them is the cheaper choice, not a fault.

Tested on each future-loan block (`learnings/tables/07_operating_points.csv`) against approving everyone, 9.6%, and approving the lowest-risk 70 / 80 / 90%:

| Policy | Approved | Cost/loan, main (KES) | Cost/loan, repeat-business (KES) |
|---|---:|---:|---:|
| Approve everyone | 100% | 85.3 | 85.3 |
| **2.1%** | 91% | **51.1** | 82.9 |
| 9.6% | 98% | 69.0 | **76.5** |
| Lowest-risk 90% / 80% / 70% | 90 / 80 / 70% | 62.1 / 57.1 / 54.5 | 99.1 / 133.1 / 169.4 |

Fixed approval targets lose because they can't tighten when risk rises.

The Ghana 3.2% threshold was tested on Kenyan labelled loans. This is a scenario calculation, not validated Ghanaian performance.

## Reproducibility

Implementation: `src/classification_experiments.py`.

Notebook: `notebooks/02_classification.ipynb`.

Tables and figures: `learnings/tables/` and `learnings/figures/`.

The saved model and individual loan predictions remain in ignored local storage.

**Update 29 Oct ([ADR 0017](0017-reason-codes.md)):** the first saved model was calibrated on the newest 20% of dates, which on the full data is May–Nov 2024 only (9% default), so it declined 89% of Kenyan test applicants. The final model now fits Platt on out-of-fold scores from all loans (`final_model()`): Kenya 19% declined, 2022 loans priced at 1.3% (actual 1.3%). The model choice and cut-off are unchanged.

## Remaining acceptance conditions

- Verify the final training/calibration boundaries.
- Review future-period calibration and lending costs.
- Complete fairness and Ghana transfer assessment.
- Confirm the scorer's input/output contract with Joseph.

This ADR approves an integration candidate, not real-world lending deployment.
