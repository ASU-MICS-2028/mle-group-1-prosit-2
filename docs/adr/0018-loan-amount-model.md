# 0018 · Loan-amount model (Task 1) and the loan limit

- **Status:** Proposed (Alice to confirm in the step 9 walkthrough)
- **Date:** 4 Nov 2026 · **Owner:** Alice · **Step:** 9

## Context
NkwaPay needs two things from Task 1:
- a **loan limit** for each approved applicant;
- an estimate of the **money it will lend**, to plan reserves.

The target is `Total_Amount`. It is very lopsided: the median is 5,249 KES, but the largest loan is 23 million. 46 loans over 1 million (0.07%) carry 15% of all the money. The clues are the shared 13 `FEATURES` ([ADR 0012](0012-final-feature-set.md)). The main test is future loans (`time_block`, [ADR 0010](0010-validation-tests.md)).

## Options we tested
Every option is in `notebooks/03_regression.ipynb`; tables are in `learnings/tables/09_*.csv`. The error is the MAE on the log scale, on future loans.

| Option | Result | Verdict |
|---|---|---|
| Guess the average | 0.972 (within 2×: 44%) | baseline |
| OLS / Ridge / Lasso | 0.630 / 0.630 / 0.628 (64–65%) | good, simple |
| k-NN (k = 100) / decision tree (depth 8) | 0.603 / 0.595 | in between |
| SVR (5,000-loan sample, C = 3) | 0.592 | slow, no gain |
| Random forest (leaf 5) | 0.583 (70%) | close second |
| **LightGBM (300 trees, 31 leaves)** | **0.581 (70%)** | **best** |
| LightGBM vs Ridge (customer bootstrap) | −0.049 [−0.054, −0.045] | a real gain |
| LightGBM vs random forest | −0.002 [−0.003, −0.0004] | LightGBM, by a hair |
| Raw target instead of log | LightGBM 0.639, Ridge 2.19 | log wins |
| US$ instead of KES (Kenya) | 0.586 vs 0.581 | no gain in Kenya |
| e^pred vs smearing (back to KES) | total ratio 0.69 vs 0.98 | e^pred for limits, smearing for reserves |
| Shuffled vs future-loan test | flatters by 0.005–0.034 only | the amount barely depends on knowing the customer |

**Limit rules** (future loans):

| Rule | Fits under limit | Money lent | Defaulted money (share of lent) |
|---|---|---|---|
| No limit | 100% | 100% | 15.2% |
| Rule of thumb: last loan amount | 53% | 66% | 7.5% |
| Model, 25% | 22% | 39% | 5.9% |
| Model, 50% | 48% | 58% | 5.8% |
| **Model, 75%** | **74%** | **70%** | **5.9%** |

## Decision
- **The model:** LightGBM learns log(`Total_Amount`) in local currency, from `FEATURES`. The code is `src/amounts.py` (`final_amount_model`).
- **The limit:** e^(prediction + q75). q75 is set so that 75% of recent similar borrowers got at most this amount. It is measured on the newest 20% of loans, with a model learned on the older 80%.
- **Reserves:** use `average()`, i.e. e^prediction × the smearing factor, not `typical()`.
- **Fallback:** Ridge, for anyone who needs readable weights. It is about 5% further off per guess.

## Why
- LightGBM misses least on the test that matters, future loans, and the bootstrap shows its gain over the linear models is not luck.
- The committee's "prefer simple" rule matters less here than for Task 2. The amount model never decides *whether* someone gets a loan, and it gives no reasons to borrowers.
- The 75% limit beats the rule of thumb on all three measures: more borrowers fit, more money is lent, and less of it goes to defaulters. The 50% rule would cut half of all borrowers below what they took.

## Consequences
- **Joseph (scorer, step 12):** for an approved applicant, `final_amount_model(train).limit(X)` gives the limit, and `typical(X)` the expected amount.
- **Liza (fairness, step 11):** the model over-predicts first loans. Its average residual is −0.36 on the log scale, so it predicts about 1.4× what they got, and limits for first-timers are relatively generous. It under-predicts Type_9 (+0.34) and over-predicts Type_10 (−0.50). The table is `learnings/tables/09_residuals_by_group.csv`.
- **Ghana:** see [ADR 0019](0019-kenya-to-ghana-transfer.md).
- **Reserves depend on the period.** The 98% total used smearing factors measured inside each test (about 1.4). The saved model's factor, measured on the newest 20% of loans, is 1.235. On the future-loans test that would give about 85% of the real total. Re-measure the factor every quarter on recent loans.
- **Not covered:** affordability. The BoG directive requires checking that a borrower can repay, and we have no income data. The limit is a ceiling *from past behaviour*, not an affordability test.
- **Would change our mind:** a future block where Ridge matches LightGBM, or Ghanaian outcomes that show the limit is too loose.

## Links
`notebooks/03_regression.ipynb` · `src/amounts.py` · `learnings/09_regression.md` · `learnings/tables/09_*.csv` · `learnings/figures/09_residuals.png`
