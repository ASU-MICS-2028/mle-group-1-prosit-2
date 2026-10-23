# 0012 · The final feature set (step 5.5)

- **Status:** Accepted. Replaces the calendar part of [0005](0005-feature-audit.md); settles the open questions in [0008](0008-borrower-history.md) (window) and [0009](0009-macro-clues.md) (macro).
- **Date:** 23 Oct 2026 · **Owner:** Joseph · **Step:** 5.5

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
| base | +4.65 | 31/31 | essential |
| history | +0.87 | 31/31 | keep |
| speed | +0.64 | 31/31 | keep |
| amounts | +0.21 | 18/31 | small for Task 2, **huge for Task 1** (below) |
| calendar | −0.17 | 7/31 | **hurts on future loans** (helps only on the mixed-time test) |
| macro | −0.16 | 4/31 | **hurts**; LightGBM ignores it entirely |

| Clues | Task 2 future-loan lift (logistic) [95% CI] | Task 1 error on future loans (log amount, LightGBM / linear) |
|---|---|---|
| Liza's set (base + calendar) | 6.67 [5.25, 8.83] | 0.917 / 0.918 |
| base + history + speed | **8.36** [6.81, 10.56] | 0.939 / 0.914 |
| **base + history + speed + amounts** | **8.14** [6.66, 10.31] | **0.575 / 0.612** |
| everything except macro | 7.93 [6.43, 10.04] | 0.569 / **0.762** (calendar breaks the linear model on future loans) |
| guess the average | — | 0.971 |

Variants (logistic, full set without macro):
- **Leaky history:** same overall score (7.93), but the score for borrowers with no history drops from 3.51 to 2.92. The cheat buys nothing and distorts the borrowers who matter most for Ghana.
- **Look-back windows:** last 3 / last 5 / 90 days are all within ±0.3 of "all past loans", which is noise.

## Decision
**The shared clues, for both tasks, are base + history + speed + amounts.** That's 13 columns, `FEATURES` in `src/features.py`:
- history is the safe version, counted after the due date, over all past loans;
- **no calendar, no macro.**

## Why
- **History and speed** help on future loans in every combination tested.
- **Amounts** cut the Task 1 error from 0.91 to 0.58, meaning a typical guess is off by about 1.8× instead of 2.5×. Their cost to Task 2 is tiny: 8.36 → 8.14, a paired difference with 95% CI [+0.02, +0.38].
- **Calendar and macro only look useful** when old and new loans are mixed. On future loans they hurt, because they learn *which period* a loan came from. That confirms the concern in [learnings/03](../../learnings/03_feature_audit.md). Macro also has only 4 training values, and Ghana's inflation is far outside them.
- **The simplest choices win:** the safe history beats the leaky one, all past loans beat any window, and **logistic regression matches or beats LightGBM** on future loans.

## Consequences
- **Germain and Alice start from `FEATURES`.** Germain may report Task 2 with and without amounts, since the difference is within noise.
- **For Ghana:** history, speed and amounts are all empty for every Ghanaian applicant, so the model has only base clues for them. In this test, borrowers with no history score lift 3.5 against 8+ overall. That's the main fairness and transfer problem for steps 10–11.
- **What would change this:** a future-loan test where calendar or macro helps beyond the noise, for example with more years of data.

## Links
`src/features.py` (`FEATURES`) · `learnings/05_features.md` · ADRs [0005](0005-feature-audit.md), [0008](0008-borrower-history.md), [0009](0009-macro-clues.md), [0010](0010-validation-tests.md)
