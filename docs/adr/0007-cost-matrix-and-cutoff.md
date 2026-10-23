# 0007 · The cost of each mistake and the decline cut-off

- **Status:** Accepted
- **Date:** 21 Oct 2026 · **Owner:** Liza · **Step:** 4

## Context
Approving someone who won't repay (FN) and declining someone who would (FP) cost different amounts. The brief wants these costs in money and a cut-off derived from them.

## Options we tested (Kenya / Ghana cut-off)
| Scenario | Cut-off |
|---|---|
| **Main: 2% / 3% fee, 10% recovered, ~$1.50 chasing cost** | **2.1% / 3.2%** |
| 0% or 30% recovered; double chasing cost | 1.9–2.6% / 2.9–4.1% |
| Fee 0.7% (free loans earn nothing) | 0.74%: declines almost everyone, so rejected as unrealistic |
| Count lost repeat business | 9.6% / 14.2% |

## Decision
- **Rule:** decline when the chance of default > cost FP ÷ (cost FP + cost FN).
- **Kenya:** FN 4,700 KES vs FP 100 KES → **2.1%**.
- **Ghana:** FN 2,716 GHS vs FP 90 GHS → **3.2%**.
- **Germain also reports** total cost at the repeat-business cut-offs.

## Consequences
- **Only valid on calibrated probabilities.** Class weights inflate probabilities, so calibrate first (Platt or isotonic).
- Recovery (10%) and collection cost are our assumptions.

## Links
[`learnings/04_cost_matrix.md`](../../learnings/04_cost_matrix.md) · `notebooks/00b_cost_matrix.ipynb`
