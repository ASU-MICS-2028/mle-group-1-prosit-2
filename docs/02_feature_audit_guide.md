# 02 · Feature audit guide (step 3)

*The instructions Liza followed for the feature audit. Moved here from the README once the step was done. Her results are in [`learnings/03_feature_audit.md`](../learnings/03_feature_audit.md).*

**Liza owns this step from start to finish:** the tests, the decisions, and the write-up. Everyone else will build on the column list you freeze here and won't recheck it, so every decision needs the evidence behind it.

**Goal.** A table with one row per column of `Train.csv` (16 columns), showing:
- whether it is available at decision time (yes/no);
- its role: feature, target, or dropped;
- a one-line reason that points to evidence.

It also states which column is the target for Task 1 (loan amount) and for Task 2 (default).

**Where:**
- the tests go in `notebooks/00_feature_audit.ipynb`;
- the final table, results and reasoning go in `learnings/03_feature_audit.md` (use the template in [`learnings/README.md`](../learnings/README.md));
- log each action in `docs/log.md`.

**The principle:** don't decide uncertain columns by opinion. Turn each one into a question, test it, and where the answer is still unclear, keep **both** options as separate feature sets and compare their results.

### 3.1 Fix the decision moment
Draw one loan's timeline: application → approval → disbursement → due date → repaid or defaulted. NkwaPay decides just before disbursement, so `disbursement_date` is the anchor. The question for every column is: **would NkwaPay know this value at that moment?**

### 3.2 Sort the columns
Column definitions are in `data/zindi/VariableDefinitions.txt` and [`docs/01_data.md`](01_data.md).

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
