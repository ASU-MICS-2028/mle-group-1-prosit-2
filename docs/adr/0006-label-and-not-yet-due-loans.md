# 0006 · What "default" means, and the 190 loans that weren't due yet

- **Status:** Accepted; refined by [0015](0015-history-fixes-from-review.md): the 190 loans still count as *history* for later loans, just not as training targets
- **Date:** 20 Oct 2026 · **Owner:** Liza · **Step:** 3

## Context
`target` = 1 means the loan wasn't repaid as of data collection (around 14 Nov 2024, the last disbursement date). 190 training loans were due *after* that date, some as late as Oct 2025. All 190 are labelled "paid", when about 5 would be expected to default.

## Options
| Option | Problem |
|---|---|
| Keep them as "paid" | Teaches the model that unfinished loans are safe |
| **Drop them from training** | Chosen. Their answer isn't known yet. |

## Decision
`build()` drops training loans whose `due_date` is after the last `disbursement_date`.

## Consequences
- Training has 68,464 rows, not 68,654.
- Zindi doesn't state the grace period after the due date, which is a stated limitation.

## Links
[`learnings/03_feature_audit.md`](../../learnings/03_feature_audit.md#step-3-what-default-means-brief-a1b)
