# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

**New to the project?** Read [`knowledge/README.md`](knowledge/README.md) first. **The plan and progress tracker** are in [`docs/plan.md`](docs/plan.md).

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## Now

| | |
|---|---|
| **Stage** | Step 5 of 13: shared features and fair tests |
| **Responsible** | **Joseph** |
| **Due** | Fri 23 Oct |
| **Waiting on it** | Germain (step 6, provisional model, Sat 24) and Alice (steps 9–10) |
| **Next after this** | Step 6: Germain's provisional logistic model |

Everything else (all 13 steps, who owns them, what's done) is in the [progress tracker](docs/plan.md#progress-tracker).

**While you wait:**
- **Germain:** logistic regression and gradient boosting derivations ([`knowledge/derivations.md`](knowledge/derivations.md)).
- **Alice:** linear regression derivation; Kenya vs Ghana comparisons on the raw data.
- **Liza:** Findex analysis; read the BoG Directive and Acts 843 and 726 ([`knowledge/regulation.md`](knowledge/regulation.md)); set up the Model Card skeleton.

## Current step in detail: 5 · Features and fair tests (Joseph)

| Part | What | Status |
|---|---|---|
| 5.1 | Look at the shape of loan histories | ✅ |
| 5.2 | Borrower history (`borrower_history` in `src/features.py`), checked on a made-up example and against a slow loop on 2,000 real loans | ✅ |
| 5.3 | Calendar and macro clues (`calendar`, `add_macro`) | ✅ |
| 5.4 | Three kinds of test (`add_folds`, `splits`) and `build()`, which gives everyone the full table in one call | ✅ |
| 5.4b | Extra cases: past loan amounts and borrowing speed (loans in last 7/30 days) as clues; a fourth test, newer loans from never-seen customers (closest stand-in for Ghana) | ✅ |
| 5.5 | Compare every option in a table: history safe vs leaky, windows, amounts and speed on/off, calendar on/off, macro on/off; all four tests; 3 random seeds to see the noise; separate score for borrowers with no history | ⏳ next |
| 5.6 | Write-up in `learnings/05_features.md` | ☐ |

**What the others need to know already:**
- **Experience is the strongest clue:** previous loans alone score ROC-AUC 0.76.
- **Past default rate is almost useless:** only 12% of defaulters ever borrow again, so there's rarely a past default to learn from (selection bias, to state in the report).
- **No Ghanaian applicant has any history**, so the model sees all of Ghana as first-timers.
- **Macro clues only take 4 values in training** (one per year), and Ghana's inflation is far outside Kenya's range.
- **The shuffled test lies, mostly for complex models:** LightGBM's PR-AUC is 0.31 shuffled vs 0.21 grouped by customer. On newer loans (the most realistic test), logistic regression beats LightGBM (0.11 vs 0.10).
- **To get the data:** `from features import build; train, test = build('data/zindi')` (run from `src/` or add it to `sys.path`).

Run the checks yourself with `.venv/bin/python src/features.py`.

## Run it from a fresh clone

Requires [uv](https://docs.astral.sh/uv/) (`brew install uv`).

```sh
git clone https://github.com/ASU-MICS-2028/mle-group-1-prosit-2.git
cd mle-group-1-prosit-2
uv venv --python 3.12 && uv pip install -r requirements.txt
brew install libomp   # macOS, only if `import lightgbm` fails
# put the data in data/ (see below), then run the notebooks in order:
for nb in notebooks/0*.ipynb; do .venv/bin/jupyter nbconvert --to notebook --execute --inplace "$nb"; done
```

## Layout

| Path | What | Owner |
|---|---|---|
| `notebooks/00_feature_audit.ipynb` | Leakage tests and feature-set comparison behind the feature audit | Liza |
| `notebooks/00b_cost_matrix.ipynb` | Cost of each mistake in KES and GHS, the decline cut-off, and the sensitivity check | Liza |
| `notebooks/01_eda.ipynb` | Imbalance, missingness, skew, cardinality, overlap, Kenya vs Ghana | Joseph |
| `notebooks/02_classification.ipynb` | Task 2: default probability, validation comparison, calibration, threshold | Germain |
| `notebooks/03_regression.ipynb` | Task 1: loan amount | Alice |
| `notebooks/04_transfer_and_fairness.ipynb` | Kenya to Ghana shift; disaggregated fairness, proxies, mitigation | Alice, Liza |
| `knowledge/` | **Everything you need to know**: the brief, course rules, lecture notes and lecture-recording summaries, derivations, regulation, fairness readings. [Start here](knowledge/README.md). | Everyone |
| `docs/` | The full plan ([`plan.md`](docs/plan.md)), and everything we did and how: dated log, setup, data sources and checks | Everyone |
| `learnings/` | Each member's full explanation of their step and findings, readable without rerunning anything | Everyone |
| `src/features.py` | Shared feature code: loans, borrower history, calendar, macro. Every notebook and the scorer import from here. | Joseph |

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
3. **Document everything in [`docs/`](docs/README.md)**: a line in `docs/log.md` for every action, and how you did it.
4. **Fully explain your work in [`learnings/`](learnings/README.md).** Every step you own ends with a write-up there (results, tables, figures, the options you tried, your decision, Q&A prep), so the others can understand it without rerunning anything. **Use the simplest language possible**: short sentences, everyday words, every term explained, examples where it helps. A step isn't ticked until its learnings file exists.
5. Commit your own work from your own account.

## Adding a dependency

`uv pip install <package>`, then add it with its version to `requirements.txt`.
