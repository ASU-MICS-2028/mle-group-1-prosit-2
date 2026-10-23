# 0009 · Macro clues (inflation, interest, exchange rate, unemployment)

- **Status:** Accepted for how they're built. **Not used in the model**, per [0012](0012-final-feature-set.md): they hurt on future loans.
- **Date:** 23 Oct 2026 · **Owner:** Joseph · **Step:** 5.3

## Context
The brief asks to join FRED macro indicators by country-year. The file has 9 indicators for 2001–2023. Our loans run to Nov 2024.

## Options
| Question | Options | Choice |
|---|---|---|
| Which indicators? | all 9 / **the 4 present for both countries** | Inflation, deposit rate, exchange rate, unemployment. The others are empty for Ghana or stop in 2021. |
| Which year's figures? | same year (slightly leaky: annual stats are published after the year ends; 2024 missing) / **last year's** | Last year's is time-safe, and 2024 loans get 2023 figures |

## Decision
`add_macro(rows, macro, lag=1)` by default; `lag=0` kept for comparison.

## Consequences
- **In training (all Kenya), each macro clue takes only 4 values,** one per year, so it can only act as "the year in disguise".
- **Ghana's inflation (9.9–31.3%) is far outside Kenya's training range (5.4–7.7%),** so the model would be guessing.
- **Expected outcome:** left out of the model unless 5.5 shows a real gain on the older-vs-newer test.

## Links
[`src/features.py`](../../src/features.py)
