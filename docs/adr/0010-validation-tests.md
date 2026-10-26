# 0010 · How we test models fairly (validation)

- **Status:** Accepted; the `time_block` test was corrected by [0014](0014-time-test-known-outcomes.md) (learn only from finished loans; whole days per block)
- **Date:** 23 Oct 2026 · **Owner:** Joseph · **Step:** 5.4, 5.4b

## Context
Customers take about 10 loans each, and default rates shift a lot over time (about 1% in Jul–Dec 2022, which is 92% of the loans, vs 5–15% in other periods). The brief asks for shuffled vs grouped vs temporal tests side by side.

## Options we tested (PR-AUC, base + calendar + history; logistic / LightGBM)
| Test | Score | What it shows |
|---|---|---|
| Shuffled (`fold_shuffled`) | 0.207 / **0.310** | Inflated: LightGBM recognises customers |
| Grouped by customer (`fold_customer`) | 0.194 / 0.209 | New customers |
| Older → newer (`time_block`, 5 blocks) | **0.112** / 0.099 | Future loans: closest to real use |
| Older → newer, new customers only (`time_new_customers`) | added in 5.4b | Closest Kenyan stand-in for Ghana |

## Decision
- **Trust for deployment:** older → newer first, grouped by customer second. Shuffled is only reported to show how much it misleads.
- **Divide PR-AUC by the test part's default rate** when comparing across time blocks, because the rate differs by block.
- **Fit every scaler, encoder and imputer inside the fold** (a scikit-learn `Pipeline`).
- **Run 3 random seeds** to see the noise.

## Consequences
- Scores on future loans are much lower than shuffled ones. That's honest, not a failure.
- The simple model holds up better over time, which supports the committee's preference.

## Links
[`src/features.py`](../../src/features.py) (`add_folds`, `splits`)
