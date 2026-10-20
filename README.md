# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## What has to be done now, and who does it

Work top to bottom. A step can only start when the steps it waits on are ticked. Tick yours (`[x]`) and push when done.

| # | Step | Who | Waits on | Due |
|---|---|---|---|---|
| 1 | [x] Download the Zindi data into `data/zindi/` | Joseph | — | Tue 20 Oct |
| 2 | [x] Register for and download Findex Ghana into `data/worldbank/` | Joseph | — | Tue 20 Oct |
| 3 | [ ] Feature audit: every column in Train.csv marked allowed or not, with a reason | Liza + Joseph | 1 | Tue 20 Oct |
| 4 | [ ] Cost matrix in cedis and shillings → the decline threshold | Liza | 1 | Tue 20 Oct |
| 5 | [ ] Shared features and validation folds in `src/` | Joseph | 3 | Fri 23 Oct |
| 6 | [ ] Provisional model (plain logistic regression) so others can start building | Germain | 5 | Sat 24 Oct |
| 7 | [ ] Task 2: final classification model, threshold, saved predictions | Germain | 4, 5 | Tue 27 Oct |
| 7b | [ ] Zindi late submission of the final model (still scored, 10/day max); log every score in 02 | Germain | 7 | Tue 27 Oct |
| 8 | [ ] Reason codes (top 3 reasons per decision) | Germain | 7 | Tue 27 Oct |
| 9 | [ ] Task 1: loan-amount model | Alice | 5 | Tue 27 Oct |
| 10 | [ ] Kenya → Ghana transfer study, domain classifier | Alice | 5 | Thu 29 Oct |
| 11 | [ ] Fairness metrics, proxy analysis, mitigation, Model Card | Liza | 7, 9, 10 | Thu 29 Oct |
| 12 | [ ] Scoring service | Joseph | 7, 8, 9 | Sat 31 Oct |
| 13 | [ ] Report, slides, reflections | Everyone | all above | Mon 2 Nov |

**While you wait on a step, do the work that doesn't need it:**
- **Germain:** logistic regression and gradient boosting derivations.
- **Alice:** linear regression derivation; Kenya vs Ghana comparisons on the raw data.
- **Liza:** Findex analysis; read the BoG Directive and Acts 843 and 726; set up the Model Card skeleton.
- **Joseph:** the scorer's interface and its edge-case tests.

## Run it from a fresh clone

Requires [uv](https://docs.astral.sh/uv/) (`brew install uv`).

```sh
git clone https://github.com/ASU-MICS-2028/mle-group-1-prosit-2.git
cd mle-group-1-prosit-2
uv venv --python 3.12 && uv pip install -r requirements.txt
# put the data in data/ (see below), then run the notebooks in order:
for nb in notebooks/0*.ipynb; do .venv/bin/jupyter nbconvert --to notebook --execute --inplace "$nb"; done
```

## Layout

| Path | What | Owner |
|---|---|---|
| `notebooks/01_eda.ipynb` | Imbalance, missingness, skew, cardinality, overlap, Kenya vs Ghana | Joseph |
| `notebooks/02_classification.ipynb` | Task 2: default probability, validation comparison, calibration, threshold | Germain |
| `notebooks/03_regression.ipynb` | Task 1: loan amount | Alice |
| `notebooks/04_transfer_and_fairness.ipynb` | Kenya to Ghana shift; disaggregated fairness, proxies, mitigation | Alice, Liza |
| `src/` | Shared loading and time-safe feature code, and the scorer (added in Phase 2) | Joseph |

## Data

`data/` is **never committed**. Download from [Zindi](https://zindi.africa/competitions/african-credit-scoring-challenge) (free account) and the [Global Findex Ghana 2021](https://microdata.worldbank.org/index.php/catalog/4646) (free registration):

```
data/
  zindi/     # Train.csv  Test.csv  SampleSubmission.csv  economic_indicators.csv  VariableDefinitions.txt
  worldbank/ # micro_gha.csv, Global Findex Ghana 2021 microdata (each user registers for their own copy, per World Bank terms)
```

## Team rules

1. **Explain everything plainly.** Nobody else will redo your part; they will rely on what you write. Each step needs a markdown cell saying what, why, and what the result means.
2. **Test every reasonable alternative** for each step and compare them in a table before picking one.
3. Commit your own work from your own account.

## Adding a dependency

`uv pip install <package>`, then add it with its version to `requirements.txt`.
