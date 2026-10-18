# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

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
  Train.csv  Test.csv  SampleSubmission.csv  economic_indicators.csv  VariableDefinitions.txt
  findex/    # Global Findex Ghana 2021 microdata
```

## Team rules

1. **Explain everything plainly.** Nobody else will redo your part; they will rely on what you write. Each step needs a markdown cell saying what, why, and what the result means.
2. **Test every reasonable alternative** for each step and compare them in a table before picking one.
3. Commit your own work from your own account.

## Adding a dependency

`uv pip install <package>`, then add it with its version to `requirements.txt`.
