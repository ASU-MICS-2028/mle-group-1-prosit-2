# 0012 · The final feature set (step 5.5)

- **Status:** Accepted. Replaces the calendar part of [0005](0005-feature-audit.md); settles the open questions in [0008](0008-borrower-history.md) (window) and [0009](0009-macro-clues.md) (macro).
- **Date:** 23 Oct 2026 (numbers updated 26 Oct after the [0014](0014-time-test-known-outcomes.md) test fix) · **Owner:** Joseph · **Step:** 5.5

## Context
Step 5 built six groups of clues:

| Group | Columns |
|---|---|
| **base** | `loan_type`, `duration`, `New_versus_Repeat` |
| **calendar** | month, weekday, day of month |
| **history** | past loans, finished, defaults, default rate, no-history flag, days since last loan |
| **speed** | loans in the last 7 / 30 days |
| **amounts** | average and last past loan amount |
| **macro** | inflation, deposit rate, exchange rate, unemployment |

Both tasks must use the same clues, and the choice should be made by testing every option, not by opinion.

## Options we tested
About 1,700 model fits; the full table is in `learnings/05_features.md`.
- every one of the 63 combinations of the six groups;
- every column dropped one at a time;
- leaky vs safe history; look-back windows of all loans, last 3, last 5 and 90 days; macro using same-year vs last-year figures;
- logistic regression and LightGBM;
- three tests: new customers, future loans, and future loans from new customers;
- 3 random seeds plus a bootstrap to measure the noise.

**Main score:** lift on future loans, meaning PR-AUC ÷ the default rate in that period. Higher is better.

| What we added | Average change in future-loan lift (logistic) | Helped in | Verdict |
|---|---|---|---|
| base | +4.68 | 31/31 | essential |
| history | +0.68 | 22/31 | keep |
| speed | +0.61 | 24/31 | keep |
| amounts | +0.30 | 23/31 | helps Task 2 a little, **huge for Task 1** (below) |
| calendar | −0.40 | 4/31 | **hurts on future loans** (helps only on the mixed-time test) |
| macro | −0.09 | 11/31 | **doesn't help**; LightGBM ignores it entirely |

| Clues | Task 2 future-loan lift (logistic) [95% CI] | Task 1 error on future loans (log amount, LightGBM / linear) |
|---|---|---|
| Liza's set (base + calendar) | 6.35 [4.85, 8.63] | 0.924 / 0.924 |
| base + history + speed | 8.15 [6.55, 10.33] | 0.952 / 0.921 |
| **base + history + speed + amounts** | **8.07** [6.57, 10.22] | **0.583 / 0.635** |
| everything except macro | 7.58 [6.08, 9.76] | 0.576 / **0.788** (calendar breaks the linear model on future loans) |
| LightGBM, base + history + speed + amounts | 6.08 [4.98, 7.84]: **clearly below logistic** | — |
| guess the average | — | 0.972 |

Variants (logistic, full set without macro):
- **Leaky history:** looks slightly better overall (7.86 vs 7.58), which is the cheat working, but the score for borrowers with no history drops from 3.54 to 2.95. It distorts the borrowers who matter most for Ghana.
- **Look-back windows:** last 3 / last 5 / 90 days are all within ±0.2 of "all past loans", which is noise.

## Decision
**The shared clues, for both tasks, are base + history + speed + amounts.** That's 13 columns, `FEATURES` in `src/features.py`:
- history is the safe version, counted after the due date, over all past loans;
- **no calendar, no macro.**

## Why
- **History and speed** help on future loans in every combination tested.
- **Amounts** cut the Task 1 error from 0.92 to 0.58, meaning a typical guess is off by about 1.8× instead of 2.5×. They cost Task 2 nothing measurable: 8.15 vs 8.07, a paired difference with 95% CI [−0.10, +0.30].
- **Calendar and macro only look useful** when old and new loans are mixed. On future loans they hurt, because they learn *which period* a loan came from. That confirms the concern in [learnings/03](../../learnings/03_feature_audit.md). Macro also has only 4 training values, and Ghana's inflation is far outside them.
- **The simplest choices win:** the safe history over the leaky one, all past loans over any window, and **logistic regression clearly beats LightGBM** on future loans.

## Consequences
- **Germain and Alice start from `FEATURES`.** Germain may report Task 2 with and without amounts, since the difference is within noise.
- **For Ghana:** history, speed and amounts are all empty for every Ghanaian applicant, so the model has only base clues for them. In this test, borrowers with no history score lift 3.5 against 8+ overall. That's the main fairness and transfer problem for steps 10–11.
- **What would change this:** a future-loan test where calendar or macro helps beyond the noise, for example with more years of data.

## Links
`src/features.py` (`FEATURES`) · `learnings/05_features.md` · ADRs [0005](0005-feature-audit.md), [0008](0008-borrower-history.md), [0009](0009-macro-clues.md), [0010](0010-validation-tests.md)
