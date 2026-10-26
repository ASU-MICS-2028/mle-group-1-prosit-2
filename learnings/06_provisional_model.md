# 06 - Provisional Classification Model (Germain)

> *The two sections below were added in review by Joseph (26 Oct), summarising Germain's results further down, plus two review findings. Germain's own write-up follows unchanged.*

## What the others need to know

1. **A first, simple default model exists.** It's logistic regression on the 13 shared clues (`FEATURES`), then "Platt" calibration (explained below). It's **provisional**: good enough to build the fairness checks and the scorer against, not to make real lending decisions.
2. **It ranks borrowers well on older loans:** about 8× better than random at finding defaulters. That matches step 5.
3. **On the newest loans (Jul–Nov 2024) it's weaker:**
   - ROC-AUC 0.65 (0.5 = coin flip, 1.0 = perfect);
   - 9.4% of those loans defaulted, but the model predicted only 5.2% on average, so it **underestimates the risk**, because defaults rose over time.
4. **Class weights ("pay extra attention to defaulters") don't help ranking here, and they inflate the probabilities.** Without weights, plus Platt, gave the most honest probabilities of the six setups tried.
5. **Files for Liza and Joseph** (on Germain's machine, never committed). Rerun the scripts to make your own copy:
   - `data/models/provisional_logistic_full.joblib`;
   - `data/predictions/provisional_logistic_test.csv`;
   - `data/predictions/provisional_logistic_oof.csv`.
6. **Review finding: Liza's cut-off doesn't fit the newest loans.** On Jul–Nov 2024, declining above **2.1%** approves almost nobody, 3.2% approves 7%, and 9.6% approves 99%. Step 7 must test cut-offs together with an **approval-rate target** (the brief: "approve at least X% of applicants").
7. **Review finding: Germain's stricter time test exposed a leak in step 5's test.** It learned from older loans whose outcomes weren't known yet. That's now fixed in `src/features.py` ([ADR 0014](../docs/adr/0014-time-test-known-outcomes.md)).

## Words used in this file

- **Calibration:** making the model's probabilities honest. If it says "5% chance of default" for 100 people, about 5 should default.
- **Platt scaling:** a simple calibration. It fits a small logistic regression that maps the model's raw score to a corrected probability, using loans the model wasn't trained on.
- **Isotonic calibration:** a more flexible calibration (a staircase-shaped mapping). It needs more data and can overfit.
- **Brier score:** the average of (predicted probability − what happened)², where what happened is 1 = defaulted, 0 = repaid. Lower is better; it rewards honest probabilities.
- **Log loss:** like Brier, but it punishes confident wrong guesses much harder. Lower is better.
- **Class weights ("balanced"):** telling the model each default counts many times more than a repayment. It helps the model notice rare defaults, but makes its probabilities too high.
- **Out-of-fold (OOF) predictions:** predictions for each loan from a model that never saw that loan while learning.
- **Holdout:** a set of loans kept aside and only used for the final check.


## Objective
Build a Logistic Regression classifier to estimate the
probability that a loan will default.

## Checkpoint 6.3 - Dataset Verification

- Raw training records: 68,654
- Processed training records: 68,464
- Processed test records: 18,594
- Approved model features: 13
- Defaults in processed training data: 1,258
- Non-defaults: 67,206
- Default rate: 1.84%

Joseph's pipeline excludes 190 training records
whose loans had not yet reached their due dates.

Four history-based features contain missing values.
These will be handled by the shared preprocessing pipeline,
without fitting preprocessing on validation data.

## Checkpoint 6.4 - Validation Verification

All 13 approved features are available.

Time-block default rates:
- Block 0: 1.89%
- Block 1: 1.31%
- Block 2: 1.14%
- Block 3: 0.94%
- Block 4: 3.90%

Four chronological validation folds passed the time-order check.

Customer-group validation confirmed zero customer overlap
between the training and validation partitions.

## Key Learning

Loan defaults are rare, so accuracy alone is misleading.
We will use PR-AUC, ROC-AUC and lift.

The large increase in defaults in the final time block
makes future-loan testing particularly important.

## Next Steps

- Train provisional Logistic Regression.
- Compare model performance across validation folds.
- Compare probability calibration methods.
- Apply Liza's approved cost thresholds only after calibration.

## Questions for the Presentation

Q: Why not use accuracy alone?
A: Almost all loans do not default. A model could achieve
high accuracy while missing every default.

Q: Why use time-based validation?
A: The lender must make future decisions using past information.
Random splits may produce unrealistically optimistic scores.

Q: Why does the default-rate change matter?
A: The risk pattern changes over time, so good performance
on historical loans may not guarantee future performance.


## Checkpoint 6.5 - Provisional Logistic Regression

### Model setup

- Algorithm: Logistic Regression
- Class weighting: balanced
- Maximum iterations: 3000
- Random state: 42
- Approved features: 13
- Preprocessing: shared preprocessor(FEATURES)
- Validation: four chronological folds
- Calibration: not yet applied

The preprocessor and classifier were fitted separately
inside the training portion of every fold.

### Chronological validation results

| Fold | PR-AUC | ROC-AUC | Lift | Actual default rate | Mean predicted risk |
|---|---:|---:|---:|---:|---:|
| 1 | 0.0698 | 0.7774 | 5.31x | 1.31% | 13.86% |
| 2 | 0.1193 | 0.8135 | 10.47x | 1.14% | 18.95% |
| 3 | 0.1159 | 0.7985 | 12.30x | 0.94% | 22.93% |
| 4 | 0.1760 | 0.7876 | 4.51x | 3.90% | 33.13% |
| **Mean** | **0.1202** | **0.7942** | **8.15x** | | |

These are arithmetic averages of fold metrics,
not metrics from pooled predictions.

### Interpretation

The classifier ranks defaulting borrowers above
non-defaulting borrowers better than random ranking.

Its average lift of 8.15x closely reproduces Joseph's
earlier feature-engineering result of approximately 8.14x.

However, the raw mean predicted probabilities are much
higher than the actual default rates.

Balanced class weights may contribute to this difference.
Changes in default rates across time may also contribute.

The model requires probability calibration before
Liza's lending decision threshold can be used.

### Limitations

- The model has only been evaluated on Kenyan labelled loans.
- Model calibration has not yet been tested.
- The model has not been tested on new customers separately.
- No bootstrap confidence intervals have been computed.
- No final lending threshold has been selected.

### Questions for the presentation

**Q: What does 8.15x lift mean?**

A: The model's average PR-AUC divided by the
validation default rate is approximately 8.15.
This indicates better ranking performance than random.

**Q: Why not use the predicted probabilities immediately?**

A: The mean predicted risks are substantially higher than
observed default frequencies. We must evaluate calibration
before treating the scores as actual risk probabilities.

**Q: Why validate over four different time periods?**

A: Defaults change over time. Testing on future loans helps
us examine how the model performs under changing conditions.

### Next experiment

Compare uncalibrated Logistic Regression with
Platt scaling and isotonic calibration, using calibration
data drawn only from each training fold.


## Checkpoint 6.6 - Calibration Investigation

### 6.6A: Initial experiment

The initial chronological split accidentally gave 885 records
to model training and 12,808 to calibration.

This happened because the cutoff was based on unique dates,
not the number of records.

Platt and isotonic improved the Brier score in this preliminary
experiment, but the experiment cannot determine our final choice.

### 6.6B: Corrected record-count split

The revised split contained 9,606 training records and
4,087 calibration records.

The calibration period had a substantially lower default rate
than the training period.

### 6.6C: Boundary audit

August 1, 2022 appeared on both sides of the original
chronological validation boundary.

There were 576 historical and 308 validation records on
that date, with 54 overlapping customers and zero shared
loan IDs.

This did not prove target leakage, but it motivated
a stricter date-based validation experiment.

### 6.6D: Strict chronological diagnostic

Historical: 13,117 records, 246 defaults.
Boundary excluded: 884 records, 24 defaults.
Future: 54,463 records, 988 defaults.

All records were accounted for and the partitions were
strictly separated by date.

The excluded boundary date was a diagnostic choice,
not a final decision to discard those records.

### 6.6E: Calibration split comparison

| Training share | Training defaults | Calibration defaults |
|---|---:|---:|
| 50% | 219 | 27 |
| 60% | 225 | 21 |
| 70% | 234 | 12 |
| 80% | 237 | 9 |

Later calibration periods contained comparatively few
defaults, suggesting a strong temporal distribution shift.

### Current decision

No calibration method or final partition has been selected.

We will inspect monthly default patterns before designing
the next calibration experiment.


## Checkpoint 6.6F - Monthly Default Audit

Germain ran a monthly aggregation of 68,464 processed
training records containing 1,258 defaults.

Key observations:
- June 2022: 232 loans, 11.21% defaults.
- July 2022: 12,014 loans, 0.42% defaults.
- August 2022: 13,660 loans, 1.39% defaults.
- October 2024: 671 loans, 13.26% defaults.

Default prevalence changes substantially across time.
This motivates chronological calibration and evaluation.
The audit alone does not prove the cause of the change.

## Checkpoint 6.6G - Calibration Comparison

Experimental periods:
- Training: before December 2022.
- Calibration: December 2022 through June 2024.
- Validation: July 2024 onward.

Records:
- Training: 64,163, with 824 defaults (1.28%).
- Calibration: 1,815, with 200 defaults (11.02%).
- Validation: 2,486, with 234 defaults (9.41%).

| Weights | Calibration | PR-AUC | ROC-AUC | Brier | Log loss | Mean risk % |
|---|---|---:|---:|---:|---:|---:|
| None | None | 0.15769 | 0.65735 | 0.08755 | 0.33705 | 3.54 |
| None | Platt | 0.15769 | 0.65735 | 0.08585 | 0.31666 | 5.25 |
| None | Isotonic | 0.13626 | 0.63173 | 0.08664 | 0.36673 | 4.17 |
| Balanced | None | 0.15375 | 0.66335 | 0.16595 | 0.51995 | 36.48 |
| Balanced | Platt | 0.15375 | 0.66335 | 0.08825 | 0.34164 | 3.42 |
| Balanced | Isotonic | 0.12906 | 0.62753 | 0.08865 | 0.40951 | 3.35 |

Interpretation:
Unweighted Logistic Regression with Platt calibration had
the lowest Brier score and log loss on this holdout.

However, its mean predicted risk (5.25%) was below the
actual default rate (9.41%).

A lower Brier score does not prove reliable calibration
in every risk band or across future populations.

Decision:
- Keep unweighted + Platt as a provisional candidate.
- Do not declare a final calibration winner.
- Do not apply the lending threshold yet.
- Design further time-based validation without repeatedly
  selecting settings against this same holdout.
- Retain the original balanced model as a comparison baseline.

Presentation defence:
We compared weighted and unweighted models, with and
without calibration. Platt improved the unweighted model's
probability scores in this experiment, but the remaining
probability mismatch required further investigation.

## Step 6 artifact delivery — 26 October 2026

I generated and reloaded the provisional Logistic
Regression model and verified its predictions.

I also produced out-of-fold predictions using
customer-grouped and chronological evaluation.

Customer-grouped ROC-AUC ranged from 0.84665 to
0.85513. Chronological ROC-AUC ranged from
0.76530 to 0.82199.

The separate July–November 2024 holdout achieved
ROC-AUC 0.647583 and PR-AUC 0.157661.

These tests use different periods and populations,
so their scores are not directly interchangeable.

The model demonstrates some useful ranking ability,
but its default probabilities remain unreliable.

The decision and limitations are documented in ADR 0013.

The final full-data model, full classification
comparison and deployment handoff remain outstanding.

## Full-data provisional refit completed

I trained the provisional classifier on all
68,464 retained labeled records.

I used 54,771 predictions from four earlier
chronological folds to fit a Platt calibrator.

I then generated predictions for 18,594
unlabeled competition records.

The average predicted default risk was 3.9289%.

The saved model was reloaded and verified.
This proves reproducibility of the saved predictions,
not that the probabilities are perfectly calibrated.

The next assignment milestone is the five-model
comparison, decision thresholds and uncertainty
analysis required in Step 7.
