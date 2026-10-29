# 07 · Final loan-default classification (Germain)

## What the others need to know

- We predict whether a borrower may fail to repay a loan.
- The evaluation compared six classifier variants and a majority-class baseline.
- The models used Joseph's shared 13 approved features.
- Future-loan testing is the main measure because lending decisions concern future applicants.
- Standard Logistic Regression performed best on future-loan PR-AUC.
- Platt calibration is the selected approach for producing lending-risk probabilities.
- The cost-based 2.1% threshold has very different approval rates across periods.
- Ghana has no observed default labels in the supplied test data.
- Logistic Regression + Platt is selected for integration, not live deployment.
- The experiment runner and notebook must remain reproducible.

## The question

NkwaPay needs to estimate the chance that a borrower will default.
Because defaults are uncommon, an apparently accurate model might simply predict that nobody defaults.

We therefore compared different models, checked how their predictions behave on future loans, and studied the cost of lending decisions.

## What I did

1. Used the shared feature-building code prepared by Joseph.
2. Compared a majority baseline with Logistic Regression, balanced Logistic Regression, k-NN, a pruned decision tree, Random Forest and LightGBM.
3. Tested the models using shuffled, customer-grouped and chronological validation.
4. Evaluated precision-recall performance, probability calibration and decision metrics.
5. Compared lending thresholds using the cost assumptions prepared by Liza.
6. Investigated uncertainty using customer-grouped bootstrap resampling.
7. Examined approvals and lending costs separately by time period.
8. Generated an integration model and predictions for the unlabelled test data.

Experiment code: `src/classification_experiments.py`.

Notebook: `notebooks/02_classification.ipynb`.

## What I tried and what happened

PR-AUC measures how well the model identifies uncommon defaults while balancing precision and recall. Higher values are better.

| Model | Shuffled | Customer-grouped | Future loans |
|---|---:|---:|---:|
| Majority baseline | 0.0184 | 0.0184 | 0.0182 |
| Logistic Regression | 0.2215 | 0.2156 | 0.1075 |
| Logistic balanced | 0.2173 | 0.2098 | 0.1054 |
| k-NN | 0.1811 | 0.1685 | 0.0638 |
| Pruned Decision Tree | 0.1261 | 0.1364 | 0.0530 |
| Random Forest | 0.2227 | 0.2083 | 0.0683 |
| LightGBM | 0.2381 | 0.1949 | 0.0569 |

The more complex models generally looked stronger when loans were shuffled. Their performance dropped on future loans. Standard Logistic Regression gave the highest future-loan PR-AUC in this comparison.

### Does Logistic Regression clearly beat Random Forest?

Yes, on future loans. Scored one time block at a time, logistic regression beats random forest in **all 4 blocks**, by +0.039 PR-AUC on average. That's above our ±0.0263 noise floor.

If you pool all four blocks together the gap shrinks to +0.015 (95% CI +0.001 to +0.033), because the big 2022 blocks dominate the pool. Either way it points the same direction. Details: `learnings/tables/07_noise_floor_comparison.md`.

### How did the lending threshold behave over time?

The table below combines chronological evaluation rows within each quarter using loan-count weighting.

| Quarter | Loans | Approval rate | Cost per loan (KES) |
|---|---:|---:|---:|
| 2022Q3 | 27,656 | 98.4% | 50.88 |
| 2022Q4 | 22,784 | 94.4% | 36.74 |
| 2023Q1 | 346 | 13.3% | 103.18 |
| 2023Q2 | 182 | 9.3% | 128.57 |
| 2023Q3 | 372 | 7.8% | 104.57 |
| 2023Q4 | 339 | 5.3% | 86.73 |
| 2024Q1 | 97 | 2.1% | 83.51 |
| 2024Q2 | 201 | 9.5% | 85.57 |
| 2024Q3 | 1,665 | 29.2% | 115.38 |
| 2024Q4 | 821 | 37.5% | 235.81 |

Approval rates varied considerably. A single overall approval rate would hide the deterioration in later periods.

See `learnings/figures/07_reliability_curve.png` and `learnings/figures/07_confusion_matrix.png` for the calibration and decision plots.

All rows described as applying Ghana's 3.2% threshold were evaluated on Kenyan loans, not Ghanaian default outcomes.

## Which cut-off? (added by Joseph, 28 Oct)

The table above made 2.1% look broken in 2023–24. It isn't: those later loans defaulted far more often (about 7% in Jul–Sep 2024 and 14% in Oct–Nov 2024, against about 1% in 2022). When defaults are that common, turning most people away **is** the cheaper choice.

To check, each future-loan block was scored with six policies. "Approve the lowest-risk X%" uses only that block's own scores (no outcomes), so NkwaPay could really do it on the day. Cost is per loan, in KES, using Liza's costs.

| Policy | Loans approved | Cost per loan, main costs (4,700 / 100) | Cost per loan, repeat-business costs (4,700 / 500) |
|---|---:|---:|---:|
| Approve everyone (no model) | 100% | 85.3 | 85.3 |
| **Cost cut-off 2.1%** | **91%** | **51.1** (lowest) | 82.9 |
| Repeat-business cut-off 9.6% | 98% | 69.0 | **76.5** (lowest) |
| Approve lowest-risk 90% | 90% | 62.1 | 99.1 |
| Approve lowest-risk 80% | 80% | 57.1 | 133.1 |
| Approve lowest-risk 70% | 70% | 54.5 | 169.4 |

In the riskiest block (Nov 2022 – Nov 2024, 3.9% default), 2.1% tightened by itself to 71% approved and still caught 78% of defaulters. A fixed "approve 90%" kept approving 90% and cost twice as much.

**Decision:** use the **cost cut-off** (2.1% Kenya, 3.2% Ghana) as the main rule. Report 9.6% / 14.2% as the "we value repeat customers" alternative. Don't use a fixed approval-rate target, because it can't react when risk goes up. Full table: `learnings/tables/07_operating_points.csv`; notebook section 5.

## Decision

Use standard Logistic Regression with Platt calibration as the **integration candidate** for the scorer and fairness audit.

This choice prioritizes chronological performance and explanations that are easier to communicate than those of more complex models.

The selected architecture does not mean the 2.1% threshold is approved for every period, or that the model is safe for real Ghanaian lending.

## What I'm unsure of / limits

- The historical training and calibration windows need an independent audit.
- The reliability plot needs interpretation by period, not only in aggregate.
- The exact performance on Ghanaian borrowers is unknown because outcome labels are unavailable.
- Performance and approval rates change substantially across periods.
- Pooled over all periods, the gain over random forest is within the noise; block by block it is above it.
- Fresh-clone run checked by Joseph on 28 Oct: about 50 s, results match to within 0.001.
- The business cost assumptions are scenarios, not confirmed real-world costs.

## Likely Q&A questions and answers

**Why did you choose Logistic Regression?**

It performed best on future loans in our new comparison and is comparatively easy to explain.

**Why not LightGBM?**

It performed better on shuffled data but much worse on future loans. Future-loan evaluation is closer to the intended use.

**Why calibrate probabilities?**

A score used with a lending cut-off must represent risk as reliably as possible, not merely rank borrowers.

**Does the model work in Ghana?**

We cannot establish that from this dataset. We have Ghanaian applications without actual default labels.

**Why not use the 2.1% threshold automatically?**

We do use it, and we tested it against approval-rate targets (section above). Its approval rate drops in 2023–24 because defaults really rose then, and declining risky loans was the cheaper choice. It had the lowest cost of every policy tested.

## Model handover

**Updated 29 Oct (Joseph, [ADR 0017](../docs/adr/0017-reason-codes.md)).** The first saved model was calibrated on May–Nov 2024 loans only (9% default), so it declined 89% of Kenyan test applicants. It's now fitted on all 68,464 labelled loans, with Platt fitted on out-of-fold scores from 5 customer folds: it declines 19% of Kenyan and 47% of Ghanaian test applicants. Saved locally (never committed) to `data/experiments/step7_reproducible/lr_platt_integration.joblib`. Ghana has no default labels, so its predictions can't be checked.

## Technical record

The earlier checkpoint-by-checkpoint log is preserved at `docs/07_classification_technical_log.md`.
