# 0004 · All features come from one file: `src/features.py`

- **Status:** Accepted
- **Date:** 23 Oct 2026 · **Owner:** Joseph · **Step:** 5

## Context
Four notebooks and the scoring service all need the same clues. If each builds its own, they drift apart, and the scorer could compute clues differently from how the model was trained. That's a classic deployment bug.

## Options
| Option | Problem |
|---|---|
| Each notebook builds its own features | Drift; hard to audit for leakage |
| A big package with classes | Overkill for 4 people and 2 weeks |
| **One module of plain functions, plus `build()` that returns the full train/test tables** | Chosen |

## Decision
- **Get the tables with:** `from features import build; train, test = build("data/zindi")`.
- **Pick columns from** the lists `BASE`, `CALENDAR`, `HISTORY` and `MACRO.values()`.
- **Self-checks** live at the bottom of the file. `python src/features.py` must print three "passed" lines before any change to `src/` is committed.

## Consequences
- A change to `src/features.py` affects everyone, so it gets an ADR (if it changes a decision) and a log line.

## Links
[`src/features.py`](../../src/features.py)
