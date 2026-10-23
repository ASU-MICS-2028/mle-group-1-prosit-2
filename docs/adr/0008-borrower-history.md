# 0008 · How borrower history is built (time-safe)

- **Status:** Accepted (window choice and the extra clues are decided in step 5.5)
- **Date:** 23 Oct 2026 · **Owner:** Joseph · **Step:** 5.2, 5.4b

## Context
Past behaviour is the best clue about a borrower, but only what NkwaPay knew **on the day** may be used. 21% of loans were sent the same day as another loan to the same customer. 7.4% of loans have earlier loans whose outcomes weren't known yet.

## Options we tested
| Question | Options | Result |
|---|---|---|
| Count loans or rows? | rows / **loans** | 2,134 loans are split across lenders; counting rows would double them |
| When does a past outcome count? | once sent (leaky) / **once due (safe)** | The leaky version changes counts for 60% of loans; the model cost is measured in 5.5 |
| Same-day loans? | include / **exclude** (`allow_exact_matches=False`) | Same-day loans can't know each other's outcome |
| No finished loans: what default rate? | 0 / average / **empty + `no_known_history` flag** | 0 would falsely mean "perfect record" |
| How far back? | all / last 3 / last 5 / last 90 days | Barely differs (only 89 loans have any past default); decided in 5.5 |
| Extra clues | past amounts (mean, last), loans in last 7/30 days | Added; their value is measured in 5.5. Today's amount is never used. |

## Decision
`borrower_history()` in `src/features.py`, using backward `merge_asof` with no exact matches, keyed on due dates for outcomes. Checked on a made-up borrower and against a slow loop on 2,000 real loans (0 mismatches).

## Consequences
- **Experience is the strongest clue** (previous loans alone: ROC-AUC 0.76).
- **Only 12% of defaulters ever borrow again,** so past default rate is nearly useless. That's **selection bias** (the lender cuts defaulters off), and it must be stated in the report.
- **No Ghanaian applicant has any history,** so the model treats all of Ghana as first-timers. This is a fairness issue for step 11.

## Links
[`src/features.py`](../../src/features.py) · `learnings/05_features.md` (step 5.6)
