# 07 ? Final loan-default classification (Germain)

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
| Logistic Regression | 0.2211 | 0.2146 | 0.1075 |
| Logistic balanced | 0.2163 | 0.2095 | 0.1054 |
| k-NN | 0.1809 | 0.1675 | 0.0635 |
| Pruned Decision Tree | 0.1261 | 0.1364 | 0.0530 |
| Random Forest | 0.2225 | 0.2085 | 0.0682 |
| LightGBM | 0.2381 | 0.1949 | 0.0569 |

The more complex models generally looked stronger when loans were shuffled. Their performance dropped on future loans. Standard Logistic Regression gave the highest future-loan PR-AUC in this comparison.

### Does Logistic Regression clearly beat Random Forest?

LR minus RF pooled chronological PR-AUC = +0.01514. Paired customer-bootstrap 95% interval [+0.00057, +0.03219], 300 valid replicates. Noise floor ±0.0263. Point estimate exceeds noise floor: False. Interval wholly above positive floor: False. The bootstrap describes uncertainty for this validation procedure, not Ghana performance.

This provides evidence in favour of Logistic Regression, but it does not prove that the advantage exceeds the project's noise floor.

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

## Decision

Use standard Logistic Regression with Platt calibration as the **integration candidate** for the scorer and fairness audit.

This choice prioritizes chronological performance and explanations that are easier to communicate than those of more complex models.

The selected architecture does not mean the 2.1% threshold is approved for every period, or that the model is safe for real Ghanaian lending.

## What I'm unsure of / limits

- The historical training and calibration windows need an independent audit.
- The reliability plot needs interpretation by period, not only in aggregate.
- The exact performance on Ghanaian borrowers is unknown because outcome labels are unavailable.
- Performance and approval rates change substantially across periods.
- The bootstrap improvement does not clearly exceed the noise floor.
- The full notebook still requires an independent fresh-clone reproduction test.
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

Its approval rates changed dramatically over time. The operating policy must be reviewed separately from the model architecture.

## Model handover

Integration candidate: standard Logistic Regression + Platt. Historical fit rows: 65793; later calibration rows: 2625. Serialized locally to ignored data/experiments/step7_reproducible/lr_platt_integration.joblib. The frozen training/calibration split must be externally validated before deployment. Ghana test probabilities have no observed Ghanaian default labels.

## Technical record

The earlier checkpoint-by-checkpoint log is preserved at `docs/07_classification_technical_log.md`.
