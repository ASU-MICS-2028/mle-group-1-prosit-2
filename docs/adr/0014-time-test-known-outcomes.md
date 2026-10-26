# 0014 · The future-loans test only learns from finished loans

- **Status:** Accepted. Corrects the `time_block` test from [0010](0010-validation-tests.md).
- **Date:** 26 Oct 2026 · **Owner:** Joseph (found through Germain's step 6 work) · **Step:** 5 (fix)

## Context
The "older → newer" test is meant to copy real life: on the day NkwaPay starts using a model, it can only learn from loans whose outcome is already known. Germain's step 6 work used a stricter split, which exposed two problems in step 5's version:

1. **Learning from unfinished loans.** The model learned from older loans even if their due date was *after* the test period began, so their outcome wouldn't have been known yet. The share of such loans was 37% in the first fold, then 13%, 10% and 5%.
2. **Days split across blocks.** The cut between blocks sometimes fell in the middle of a day. For example, 1 Aug 2022 had 576 loans on one side and 308 on the other, with 54 customers on both sides.

## Options
| Option | Problem |
|---|---|
| Keep the old split | Slightly optimistic: it uses outcomes that weren't known yet |
| **Whole days per block; learn only from loans due before the test's first day** | Chosen. This matches what NkwaPay could actually do. |

## Decision
- **`add_folds()`:** a whole day always goes into one time block.
- **`splits()`:** for the time tests, the learning part is limited to loans with `due_date` < the first disbursement date of the test block.
- **Self-checks** in `src/features.py` now assert both rules.

## What changed when step 5 was rerun
| | Before | After |
|---|---|---|
| Logistic, `FEATURES`, future-loan lift | 8.14 | 8.07 |
| LightGBM, `FEATURES`, future-loan lift | 7.16 | 6.08 |
| Logistic vs LightGBM (bootstrap difference) | overlapping | logistic clearly better (−3.0 to −0.9) |
| Calendar's average effect on future lift | −0.17 | −0.40 |
| Leaky history, overall / no-history (safe version: 7.58 / 3.54) | 7.93 / 2.92 | 7.86 / 2.95 |
| Task 1 error with `FEATURES` (future loans, LightGBM) | 0.575 | 0.583 |

**No decision in [0012](0012-final-feature-set.md) changes:**
- calendar and macro stay out, and the case is now stronger;
- `FEATURES` stays;
- the logistic preference is now clearer.

## Consequences
- Every number in [`learnings/05_features.md`](../../learnings/05_features.md) and ADR 0012 has been updated to the corrected test.
- Germain's step 6 scripts already applied this rule themselves. Their temporal out-of-fold row count now comes from `splits()` rather than a fixed number.

## Links
[`src/features.py`](../../src/features.py) (`add_folds`, `splits`) · [`notebooks/01_eda.ipynb`](../../notebooks/01_eda.ipynb)
