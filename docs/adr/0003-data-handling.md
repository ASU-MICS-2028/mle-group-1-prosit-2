# 0003 · How we handle the data

- **Status:** Accepted
- **Date:** 20 Oct 2026 · **Owner:** Joseph · **Step:** 1–2

## Context
- **Zindi:** the data is "private property of the client".
- **World Bank (Findex):** for the registered user only, aggregate reporting only, no linking that could identify people.
- **Course AI policy:** never upload provided private datasets into generative AI tools.

## Decision
1. **Data lives only in `data/`,** which `.gitignore` keeps out of git.
2. **Layout:** `data/zindi/` (Train, Test, economic_indicators, SampleSubmission, VariableDefinitions) and `data/worldbank/micro_gha.csv`.
3. **Never show raw rows to an AI tool,** and that includes AI coding agents. Shapes, counts, value counts, means and model scores are fine; `df.head()` on real data is not. Use made-up rows (like "Ama" in `src/features.py`) to explain or test logic.
4. **Findex:** each person who analyses it registers for their own copy. Results are always survey-weighted (`wgt`) aggregates.
5. **Cite both datasets** in the report.

## Consequences
- AI help is limited to code, concepts and aggregate results. That's slower, but within the rules.
- Anyone can rebuild everything from the two downloads plus the repo.

## Links
[`docs/01_data.md`](../01_data.md)
