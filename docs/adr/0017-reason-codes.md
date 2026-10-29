# 0017 · Reason codes, and the final model's calibration

- **Status:** Accepted. Refines [0016](0016-final-classification.md) (how the final model is calibrated).
- **Date:** 29 Oct 2026 · **Owner:** Joseph (took over step 8 from Germain) · **Step:** 8

## Context
The scorer must give each declined applicant the top 3 reasons, in plain words, true to the model and stable.

While building them I found that step 7's saved model was calibrated on the newest 20% of dates. On the full data that's May–Nov 2024 only (2,625 loans, 9% default). It priced 2022 loans at 4.9% risk against a real 1.3%, and declined 89% of Kenyan test applicants. Step 7's tests calibrated each block separately, so they didn't show it.

## Options we tested
Full numbers: [learnings/08](../../learnings/08_reason_codes.md), tables `learnings/tables/08_*.csv`.

| Choice | Options | Result | Verdict |
|---|---|---|---|
| Final calibration | none / Platt on newest 20% of dates / newest 20% of rows / random 25% / out-of-fold, 5 customer folds | Cost per loan 47.3–48.5 KES, all within noise; newest-dates worst on log loss (0.095 vs 0.079–0.080) and breaks on the full data | **Out-of-fold, customer folds** |
| Method | weight × (value − reference) / SHAP standard / SHAP correlation-aware | Standard SHAP identical; correlation-aware agrees on top reason 71%, top 3 53% | **weight × (value − reference)** |
| Reference | average / average approved / best possible | Approved agrees 98% with average; best-possible gives "loan product" as top reason to 100% | **average** |
| Grouping | 13 clues / themes draft 1 / final themes | Clues: 8.7% of reasons mostly cancelled by a partner, top 3 stable 53%; final themes: 0%, 94% | **5 themes** |
| Minimum push | 0 / 0.05 / 0.1 / 0.2 | Top-3 stability 63% / 61% / 78% / 94%; reasons per person 2.4 → 1.9; nobody left with none | **0.2** |

## Decision
1. **Final model:** logistic regression on all labelled loans. Platt is fitted on out-of-fold scores from 5 customer-grouped folds (`final_model()` in `src/classification_experiments.py`).
2. **Reasons:** `src/reasons.py`. Each theme's push is weight × (value − average applicant), summed over 5 themes. A theme is shown if its push is ≥ 0.2 log-odds; the top 3 are shown, worded with the applicant's own numbers.

## Why
- The pushes add up exactly to the model's score, and they equal standard SHAP, so the reasons are faithful and can be checked by hand.
- Themes remove contradicting reasons and make the reasons far more stable.
- The calibration fix uses every period; on the future-loan blocks it is as good as any option.

## Consequences
- **Scorer (step 12):** call `final_model` (or load the saved model) and `reasons(model, X, reference(model, train[FEATURES]), known_types=set(train.loan_type))`.
- **Decline rates on the Zindi test:** Kenya 19%, Ghana 47%. Platt slope is 0.99, so plain logistic regression was already honest.
- **Fairness (step 11):** the most common reason is "you haven't borrowed recently". The model rewards frequent borrowing, which is a responsible-lending concern.
- **Transfer (step 10):** Ghana's "no record for this kind of loan" reason comes from `Type_3` having no weight. How unseen loan types should be scored needs deciding.
- **What would change this:** a model that isn't linear (pushes would need SHAP proper), or a regulator's template for adverse-action reasons.

## Links
[`src/reasons.py`](../../src/reasons.py) · [`notebooks/02b_reason_codes.ipynb`](../../notebooks/02b_reason_codes.ipynb) · [learnings/08](../../learnings/08_reason_codes.md) · [`src/classification_experiments.py`](../../src/classification_experiments.py) (`final_model`)
