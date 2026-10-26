# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

**New to the project?** Read [`knowledge/README.md`](knowledge/README.md) first. **The plan and progress tracker** are in [`docs/plan.md`](docs/plan.md).

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## Now

| | |
|---|---|
| **Stage** | Step 7 of 13: final classification comparison |
| **Responsible** | **Germain** |
| **Due** | **End of Mon 26 Oct 2026** (extended) |
| **Completed** | Step 6 provisional logistic regression and temporal calibration |
| **Next after this** | Step 7b Zindi submission; Step 8 reason codes |

The full plan and progress tracker are in
[`docs/plan.md`](docs/plan.md).

The Step 6 decision and limitations are documented in
[`ADR 0013`](docs/adr/0013-provisional-logistic-calibration.md).

## Current step in detail: 7 · Final classification (Germain)

**Purpose:** Compare candidate classifiers fairly and select
an explainable model using future-loan performance, uncertainty,
probability calibration and lending costs.

**Required work:**

1. Use the 13 approved features and shared preprocessing from
   `src/features.py`.
2. Compare a constant baseline and at least five classifiers:
   Logistic Regression, k-NN, pruned Decision Tree,
   Random Forest and LightGBM. Additional models are optional.
3. Treat chronological validation as primary; include
   customer-grouped and shuffled comparisons.
4. Compare imbalance handling and tuning alternatives
   inside training folds.
5. Evaluate PR-AUC, ROC-AUC, lift, calibration,
   Brier score and log loss.
6. Compare appropriate calibration methods without
   using the evaluation holdout for calibration fitting.
7. Evaluate F1, confusion matrices, approval rates
   and cost-based thresholds using calibrated probabilities.
   **Choose the operating point by testing:** sweep cut-offs
   and report, for each, the approval rate, the default rate
   among approved loans and the total cost (Liza's FN/FP costs).
   Liza's 2.1% approves almost nobody on Jul–Nov 2024 loans,
   so compare cost-based, approval-rate-target (e.g. approve
   70% / 80% / 90%) and repeat-business (9.6%) cut-offs.
8. Calculate bootstrap 95% confidence intervals and
   compare improvements against the documented noise floor.
9. Write results into `notebooks/02_classification.ipynb`,
   `learnings/07_classification.md`, and an ADR.
10. Save the selected model and predictions locally,
    excluding private artifacts from Git.

**Important limitations:** The Step 6 model remains provisional.
The observed future default rate exceeded predicted risk, and
Ghanaian outcome performance remains unknown. Do not approve
a lending threshold merely because the model was serialized.

## Run it from a fresh clone

```sh
git clone https://github.com/ASU-MICS-2028/mle-group-1-prosit-2.git && cd mle-group-1-prosit-2
uv venv --python 3.12 && uv pip install -r requirements.txt     # brew install libomp if lightgbm fails on macOS
# put the data in data/zindi/ (Zindi: African Credit Scoring Challenge) and data/worldbank/micro_gha.csv (Findex Ghana 2021)
.venv/bin/python src/features.py                               # self-checks
for nb in notebooks/0*.ipynb; do .venv/bin/jupyter nbconvert --to notebook --execute --inplace "$nb"; done
```

**Where things are:**
- Rules for people and AI agents: [`AGENTS.md`](AGENTS.md)
- Plan and tracker: [`docs/plan.md`](docs/plan.md)
- Decisions: [`docs/adr/`](docs/adr/README.md)
- What we learned: [`learnings/`](learnings/README.md)
- Course material: [`knowledge/`](knowledge/README.md)
- Data sources: [`docs/01_data.md`](docs/01_data.md)
