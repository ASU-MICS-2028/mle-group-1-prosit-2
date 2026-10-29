# 0015 · Borrower-history fixes from Germain's review

- **Status:** Accepted. Refines [0008](0008-borrower-history.md) (history) and [0006](0006-label-and-not-yet-due-loans.md) (not-yet-due loans).
- **Date:** 26 Oct 2026 · **Owner:** Joseph (review by Germain) · **Step:** 5 (fix)

## Context
Germain's review of `src/features.py` raised eight points. I tested each one against the code and the data before changing anything:
- **2 were real defects** (points 1 and 3 below);
- **1 was an untested assumption** (point 4);
- **1 needed a new score** (point 5);
- **3 needed no change** (points 6–8);
- **the same-day split** was already fixed in [0014](0014-time-test-known-outcomes.md).

## What we tested and found
| # | Point | Test | Finding | Action |
|---|---|---|---|---|
| 1 | History correct with same-day loans? | Recomputed every history clue by hand for 4,440 loans (1,500 same-day cases); shuffled the input order | All counts, averages and windows correct. **`last_amount` was arbitrary** when the latest earlier day had several loans (800 sampled cases), and changed for 6,151 loans when rows were shuffled. | **Fixed:** `last_amount` = average of the loans on the most recent earlier day; ties sorted the same way every run. After: 0 mismatches, 0 changes on shuffle. |
| 3 | Not-yet-due loans dropped from history? | Built history with and without the 190 loans | Their *existence and amount* were known, but dropping them changed history for 293 loans | **Fixed:** history uses every loan; the 190 are only excluded as training targets |
| 4 | Is an outcome really known at the due date? | No repayment dates exist, so we test a grace period of 0 / 7 / 30 days (`build(grace_days=...)`) | Logistic future lift 7.97 / 8.22 / 8.34, all inside the noise (about ±1.5) | **Kept 0 days** (due date), stated as an assumption, with the test as evidence |
| 5 | Are "new customers" first-time borrowers? | Share of `time_new_customers` test loans with earlier loans | 60–75% have earlier loans, so they're not first-timers | **Added a "first-ever loan" score** (`n_prev_loans == 0`) to every evaluation |
| 6 | Repeated computation slow? | Timed it | `build()` takes 0.7 s (history 0.07 s, calendar + macro 0.02 s) | No change needed |
| 7 | Missing values from failed matches? | Reconciled counts | `past_default_rate` empty on exactly the 11,930 `no_known_history` rows; days-since and amounts empty on exactly the 6,363 `n_prev_loans == 0` rows | No change: missing means "no history", by design |
| 8 | Default rate drifts by month | — | A property of the data (shown in learnings/05) | Step 7 reports results by time period |

## Before → after (step 5 rerun)
| | Before | After |
|---|---|---|
| Logistic, `FEATURES`, future-loan lift | 8.07 | 7.97 |
| LightGBM, `FEATURES`, future-loan lift | 6.08 | 5.63 |
| Task 1 error, `FEATURES` (future loans, LightGBM / linear) | 0.583 / 0.635 | 0.581 / 0.632 |
| Calendar / macro average effect on future lift | −0.40 / −0.09 | −0.39 / −0.09 |
| **New:** first-ever-loan lift (logistic / LightGBM) | — | **2.70 / 1.98** |

**No decision in [0012](0012-final-feature-set.md) changes.**

## Consequences
- **For Ghana:** borrowers with *no history at all* get a lift of only about 2.7, against about 8 overall. That's the stand-in for Ghana's 19% first-timers. **Corrected 29 Oct:** the other 81% have earlier loans but no known outcomes; Kenyan lookalikes get lift about 9.0, from only 69 defaults. Both should drive steps 10–11.
- **For Germain:** step 6 and step 7 numbers shift slightly. Rerun after pulling `main`.
- **The new option:** `grace_days` is available in `build()` for anyone who wants to test it further. The time tests read `outcome_known_at` (due date + grace) from `build()`, so they automatically match.

## Links
[`src/features.py`](../../src/features.py) · [`notebooks/01_eda.ipynb`](../../notebooks/01_eda.ipynb) §6b · [`learnings/tables/05_grace_period.csv`](../../learnings/tables/05_grace_period.csv)
