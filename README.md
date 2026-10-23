# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

**New to the project?** Read [`knowledge/README.md`](knowledge/README.md) first. **The full plan** is in [`docs/plan.md`](docs/plan.md).

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## What has to be done now, and who does it

Work top to bottom. A step can only start when the steps it waits on are ticked. Tick yours (`[x]`) and push when done.

| # | Step | Who | Waits on | Due |
|---|---|---|---|---|
| 1 | [x] Download the Zindi data into `data/zindi/` | Joseph | — | Tue 20 Oct |
| 2 | [x] Register for and download Findex Ghana into `data/worldbank/` | Joseph | — | Tue 20 Oct |
| 3 | [x] Feature audit: every column in Train.csv marked allowed or not, with evidence ([guide below](#step-3-feature-audit-liza)) | Liza | 1 | Wed 21 Oct |
| 4 | [x] Cost matrix in cedis and shillings → the decline threshold | Liza | 1 | Tue 20 Oct |
| 5 | [ ] Shared features and fair tests in `src/` ([progress below](#step-5-features-and-fair-tests-joseph)) | Joseph | 3 | Fri 23 Oct |
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

## Step 5: Features and fair tests (Joseph)

| Part | What | Status |
|---|---|---|
| 5.1 | Look at the shape of loan histories | ✅ |
| 5.2 | Borrower history (`borrower_history` in `src/features.py`), checked on a made-up example and against a slow loop on 2,000 real loans | ✅ |
| 5.3 | Calendar and macro clues (`calendar`, `add_macro`) | ✅ |
| 5.4 | Three kinds of test (`add_folds`, `splits`) and `build()`, which gives everyone the full table in one call | ✅ |
| 5.5 | Compare every option in a table (history safe vs leaky, windows, calendar on/off, macro on/off) | ⏳ next |
| 5.6 | Write-up in `learnings/05_features.md` | ☐ |

**What the others need to know already:**
- **Experience is the strongest clue:** previous loans alone score ROC-AUC 0.76.
- **Past default rate is almost useless:** only 12% of defaulters ever borrow again, so there's rarely a past default to learn from (selection bias, to state in the report).
- **No Ghanaian applicant has any history**, so the model sees all of Ghana as first-timers.
- **Macro clues only take 4 values in training** (one per year), and Ghana's inflation is far outside Kenya's range.
- **The shuffled test lies, mostly for complex models:** LightGBM's PR-AUC is 0.31 shuffled vs 0.21 grouped by customer. On newer loans (the most realistic test), logistic regression beats LightGBM (0.11 vs 0.10).
- **To get the data:** `from features import build; train, test = build('data/zindi')` (run from `src/` or add it to `sys.path`).

Run the checks yourself with `.venv/bin/python src/features.py`.

## Step 3: Feature audit (Liza)

**Liza owns this step from start to finish:** the tests, the decisions, and the write-up. Everyone else will build on the column list you freeze here and won't recheck it, so every decision needs the evidence behind it.

**Goal.** A table with one row per column of `Train.csv` (16 columns), showing:
- whether it is available at decision time (yes/no);
- its role: feature, target, or dropped;
- a one-line reason that points to evidence.

It also states which column is the target for Task 1 (loan amount) and for Task 2 (default).

**Where:**
- the tests go in `notebooks/00_feature_audit.ipynb`;
- the final table, results and reasoning go in `learnings/03_feature_audit.md` (use the template in [`learnings/README.md`](learnings/README.md));
- log each action in `docs/log.md`.

**The principle:** don't decide uncertain columns by opinion. Turn each one into a question, test it, and where the answer is still unclear, keep **both** options as separate feature sets and compare their results.

### 3.1 Fix the decision moment
Draw one loan's timeline: application → approval → disbursement → due date → repaid or defaulted. NkwaPay decides just before disbursement, so `disbursement_date` is the anchor. The question for every column is: **would NkwaPay know this value at that moment?**

### 3.2 Sort the columns
Column definitions are in `data/zindi/VariableDefinitions.txt` and [`docs/01_data.md`](docs/01_data.md).

| Group | Columns | Starting view (confirm or overturn it) |
|---|---|---|
| Clear-cut | `ID`, `tbl_loan_id` | Identifiers, so dropped. `tbl_loan_id` is still needed to group the multi-lender rows of one loan. |
| | `customer_id` | Not a feature; used to group folds and build borrower history |
| | `target` | Task 2 target |
| | `loan_type`, `duration`, `New_versus_Repeat` | Known at application, so features. `New_versus_Repeat` is also a fairness group. |
| | `disbursement_date` | Not used raw; calendar features come from it |
| Constant in training | `country_id` | Train is all Kenya, so the model can learn nothing from it. Keep it as a fairness group. |
| **Contested** | `Total_Amount` | Task 1 target. For Task 2: is it the amount *asked for* (known at application) or the amount *approved* (decided by NkwaPay)? |
| | `Total_Amount_to_Repay` | Amount plus fees, so repay ÷ amount is the price. Pricing is part of the decision; is it a fair input? |
| | `Amount_Funded_By_Lender`, `Lender_portion_Funded` | Calculated from the amount? Then they leak into Task 1. |
| | `Lender_portion_to_be_repaid` | Defined as the portion of the "**outstanding**" loan. Measured after the loan was issued? Then it's a leak. |
| | `due_date` | Probably `disbursement_date + duration`. Check. It's also the cutoff for "past defaults" in the history features. |
| | `lender_id` | Known at decision time, but may stand in for country (Ghana uses different lenders) |

### 3.3 Test each contested column

| Test | What it catches | How |
|---|---|---|
| **Arithmetic** | Columns that are just recombinations of others | Is `due_date − disbursement_date == duration`? Is `Lender_portion_Funded == Amount_Funded_By_Lender / Total_Amount`? Is repay ÷ amount fixed per `loan_type`? Report the % of rows where each holds. |
| **Single-column power** | Leaks | Predict `target` from each column alone and report ROC-AUC and PR-AUC (`sklearn.metrics.roc_auc_score`, `average_precision_score`). A single column above roughly 0.9 ROC-AUC is a red flag. |
| **Defaulters vs repayers** | Hindsight values | Compare each column's distribution for `target==1` vs `target==0`. Look for patterns only possible after the fact, e.g. "to be repaid" being 0 for every loan that was repaid. |
| **Proxy check** | Columns that encode country | In `Test.csv` (which has both countries), how well does each column alone separate Ghana from Kenya? Report ROC-AUC. |

### 3.4 Run the competing feature sets
Run each set the same way: logistic regression (`class_weight="balanced"`, scaled numbers, one-hot categories) and LightGBM, with 5-fold `GroupKFold` grouped by `customer_id`. Report PR-AUC and ROC-AUC for Task 2, and MAE of log amount for Task 1 where the amount isn't in the set.

| Set | Contents | Purpose |
|---|---|---|
| **F0 Strict** | `loan_type`, `duration`, `New_versus_Repeat`, `lender_id`, calendar features from `disbursement_date` | The brief's "same features for both tasks". **Default for deployment.** |
| **F0 − lender** | F0 without `lender_id` | What the lender proxy costs and buys (for the fairness work later) |
| **F1 + requested amount** | F0 + log `Total_Amount` (Task 2 only) | Tests the "amount asked for" reading |
| **F2 + price and shares** | F1 + repay ÷ amount, lender share | Does pricing information help, and is it fair to use? |
| **F3 Everything** | All columns except IDs | **A leakage ceiling, never deployed.** The F3 − F0 gap shows how much leakage would have inflated our results. |

Add more sets if the tests suggest them. Borrower history and macro features come in step 5; this comparison gets rerun then.

### 3.5 Done when
- [x] Timeline drawn, with the decision moment and its closest column.
- [x] Label defined: what counts as a default, and over what period.
- [x] Every one of the 16 columns has a row: available? · role · reason with evidence.
- [x] Tables for the four tests, and the feature-set comparison table, each followed by a plain-English "what this means".
- [x] A final frozen column list for step 5, plus a 5–10 bullet "what the others need to know" summary at the top of `learnings/03_feature_audit.md`.
- [x] Notebook runs top to bottom; doc and log updated; committed from your own account; step 3 ticked above.

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
