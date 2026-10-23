# 0005 · Which columns the model may use (feature audit)

- **Status:** Accepted
- **Date:** 20–21 Oct 2026 · **Owner:** Liza · **Step:** 3

## Context
A column filled in after the loan was given secretly contains the answer (leakage). The brief requires an audit of all 16 columns of `Train.csv`.

## Options we tested (PR-AUC, grouped by customer, logistic / LightGBM)
| Column set | Default (Task 2) | Verdict |
|---|---|---|
| loan_type, lender_id, duration, New_versus_Repeat, calendar | 0.200 / 0.170 | — |
| **the same without lender_id** | **0.199** / 0.169 | **chosen** |
| also without loan_type | 0.151 / 0.148 | loan_type matters |
| + loan amount | 0.200 / 0.168 | adds nothing to Task 2; it's Task 1's answer |
| everything, including leaky columns | **0.749 / 0.913** | the cheat ceiling |

Key test: on the *same* product from the *same* lender, the price (repay ÷ amount) is 1.007 for repayers and 1.412 for defaulters (ROC-AUC 0.991). So penalties were added after default.

## Decision
- **Clues:** `loan_type`, `duration`, `New_versus_Repeat`, and calendar parts of `disbursement_date`.
- **Targets:** `Total_Amount` (Task 1), `target` (Task 2).
- **Dropped:**
  - `Total_Amount_to_Repay` and `Lender_portion_to_be_repaid`: leaks, carrying post-default penalties;
  - the two lender-funding columns: calculated from the Task 1 answer;
  - `lender_id`: adds nothing and reveals the country;
  - IDs, `due_date` and `country_id`: no new information.

## Consequences
- The leak inflates PR-AUC from about 0.20 to 0.91. That's the before/after number for the leakage audit.
- `loan_type` reveals the country, so it is checked in the fairness work.

## Links
[`learnings/03_feature_audit.md`](../../learnings/03_feature_audit.md) · `notebooks/00_feature_audit.ipynb`
