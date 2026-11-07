# Model Card: NkwaPay default model

*Following Mitchell et al. (2019). The evidence is in [`notebooks/04_transfer_and_fairness.ipynb`](../notebooks/04_transfer_and_fairness.ipynb) Part 2 and [`learnings/tables/11_*.csv`](../learnings/tables/). This is a student project, not a licensed product.*

## 1. Model details
- **Built by:** MLE Group 1 (Alice, Germain, Joseph, Liza), ICS553, Ashesi University, for the fictional lender NkwaPay.
- **Date and version:** November 2026, v1.
- **Type:** logistic regression with Platt calibration, fitted on out-of-fold scores from 5 customer-grouped folds ([ADR 0016](adr/0016-final-classification.md), [0017](adr/0017-reason-codes.md)).
- **Clues:**
  - **Kenya (10):** `loan_type`, `duration`, `New_versus_Repeat`, `n_prev_loans`, `n_finished`, `n_defaults`, `past_default_rate`, `no_known_history`, `mean_prev_amount`, `last_amount`.
  - **Ghana:** the model doesn't decide anything yet. A rule by loan type does, using group default rates measured from Zindi's scores ([ADR 0021](adr/0021-ghana-rules.md)).
- **Fairness choices:** none inside the training. Three "borrow often" clues were removed, and first-time applicants above the cut-off get a starter loan ([ADR 0020](adr/0020-fairness-mitigation.md)).
- **Companion model:** LightGBM on log loan amount, for limits ([ADR 0018](adr/0018-loan-amount-model.md)). Not covered in the tables below.
- **Licence and contact:** course work; see the repository.

## 2. Intended use
- **Primary use:** estimate the chance that a short-term mobile-money loan defaults, to support an approve / starter loan / decline decision with up to 3 plain reasons.
- **Primary users:** NkwaPay's credit team, and borrowers through the reasons they receive.
- **Out of scope:**
  - automatic decisions in Ghana before about 5,000 labelled Ghanaian loans exist;
  - other countries, products, or business lending;
  - setting prices;
  - affordability checks: there is no income data;
  - detecting loans from other lenders: there is no bureau data.

## 3. Factors
| Factor | Relevant? | Evaluated? |
|---|---|---|
| Country | Yes | Partly: Ghana has no outcomes, so approval rates only |
| Tenure (first loan / earlier, no known outcome / known outcomes) | Yes | Yes |
| Loan type | Yes | Yes |
| Lender | Yes | Yes |
| Loan size | Yes | Yes |
| Time period | Yes | Yes |
| **Gender** | **Yes** | **No: not in the data.** Findex gives population context only |
| Age, income, region | Yes | No: not in the data |

## 4. Metrics
- **Measures:** PR-AUC and lift (suited to about 2% defaults), ROC-AUC, F1, approval rate, good payers wrongly declined, defaulters caught, PPV and NPV, predicted vs actual default, cost per loan.
- **Cut-offs:** decline above 2.1% in Kenya and 3.2% in Ghana. These come from the cost of each mistake: 4,700 vs 100 KES, and 2,716 vs 90 GHS ([ADR 0007](adr/0007-cost-matrix-and-cutoff.md)).
- **Uncertainty:** customer-bootstrap 95% ranges.
- **Fairness priority:** sufficiency (an honest score) first, then good payers wrongly declined. Approval rates are reported but not forced equal, because groups' real default rates differ.

## 5. Evaluation data
- **Future Kenyan loans:** 54,463 loans, 988 defaults, 5,718 customers. Learn from older loans, score the next block.
- **Zindi test applicants:** 15,069 Kenyan and 3,525 Ghanaian loans; decisions only, as outcomes aren't available to us.
- **Preparation:** shared code in `src/features.py`; every step is fitted inside the training part.

## 6. Training data
68,464 labelled Kenyan loans, 6,508 customers, 2021–2024; 1.8% defaulted. See the [datasheet](datasheet.md).

| Group | Loans | Default rate |
|---|---:|---:|
| First loan | 6,363 | 6.7% |
| Earlier loans, no known outcome | 5,567 | 1.7% |
| Earlier loans, known outcomes | 56,534 | 1.3% |
| Type_1 | 61,723 | 0.8% |
| Other types | 6,741 | 10.9% |
| Lender A | 64,568 | 1.2% |
| Other lenders | 3,896 | 12.2% |

## 7. Quantitative analyses
**Each factor alone,** future loans at the 2.1% cut-off. These are for the 13-clue model, the baseline we audited. The chosen 10-clue model is within about 3 points on the tenure, size and Lender A rows; **Lender B gets worse**, from 80% to 87% wrongly declined (`11_fairness_after.csv`).

| Group | Approved | Wrongly declined (95% range) | Defaulters caught | PR-AUC | Lift | Predicted / actual |
|---|---:|---|---:|---:|---:|---|
| All | 89% | 10% (9–11) | 55% | 0.13 | 7.1 | 1.3% / 1.8% |
| Known outcomes | 92% | 8% (7–9) | 47% | 0.08 | 5.9 | 1.0% / 1.3% |
| No known outcome | 85% | 13% (11–15) | 61% | 0.31 | 6.4 | 2.4% / 4.8% |
| First loan | 45% | 53% (51–56) | 74% | 0.27 | 2.5 | 7.4% / 10.9% |
| Smallest quarter | 93% | 7% (6–8) | 21% | 0.03 | 2.5 | 0.7% / 1.4% |
| Largest quarter | 84% | 15% (13–17) | 69% | 0.20 | 6.7 | 2.8% / 3.0% |
| Type_1 | 97% | 3% (3–3) | 11% | 0.02 | 2.6 | 0.5% / 0.9% |
| Type_7 | 25% | 74% (69–79) | 87% | 0.15 | 1.7 | 3.8% / 8.9% |
| Lender A | 93% | 6% (6–7) | 40% | 0.08 | 6.2 | 0.9% / 1.4% |
| Lender B | 19% | 80% (77–84) | 91% | 0.12 | 1.4 | 7.7% / 8.4% |
| 2022 | 95% | 5% (4–5) | 31% | 0.10 | 8.8 | 0.8% / 1.2% |
| 2023 | 15% | 84% (78–91) | 95% | 0.21 | 1.8 | 15.3% / 11.5% |
| 2024 | 23% | 76% (71–80) | 88% | 0.15 | 1.6 | 5.1% / 9.3% |

**Where factors overlap** (full table: `11_fairness_intersections.csv`):

| Group | Loans | Defaults | Approved | Wrongly declined |
|---|---:|---:|---:|---:|
| First loan, largest quarter | 456 | 92 | 15% | 82% |
| First loan, smallest quarter | 872 | 67 | 74% | 27% |
| First loan, Lender A | 1,883 | 163 | 60% | 39% |
| First loan, Lender B | 476 | 57 | 0.2% | 99.8% |
| Known outcomes, Lender B | 1,959 | 140 | 23% | 77% |

**After the fixes** ([ADR 0020](adr/0020-fairness-mitigation.md)), same future loans:

| | Before | After |
|---|---:|---:|
| Cost per loan, main costs | 47.9 KES | 48.9 KES |
| Cost per loan, at the measured repeat value (200 KES) | 67.3 KES | 64.0 KES |
| Lift | 7.78 | 7.72 |
| First-loan good payers refused | 53% | 4% (starter loan below 24% risk) |
| Other good payers refused | 8% | 8% |
| Declined applicants told to borrow more often (Zindi test, Kenya) | 31% | 0% |

**Applicants never seen by the model:**

| | Full loan | Starter or review | Declined |
|---|---:|---:|---:|
| Kenya | 82% | 9% | 9% (3% of first-timers) |
| Ghana ([ADR 0021](adr/0021-ghana-rules.md)) | 0% | 86% | 14% |

## 8. Ethical considerations
- **Sensitive data:** financial records. There are no names or ID numbers beyond anonymous customer IDs. Nothing at row level leaves `data/`.
- **Effect on people:** a decision affects access to credit, and a loan can cause over-indebtedness.
- **Harms found and what we did:**
  - first-time borrowers shut out completely → starter loan;
  - the model rewarded frequent borrowing → clues removed.
- **Harms still open:**
  - a starter loan can still push someone into debt;
  - the limit model offers small borrowers up to 2.8× their usual loan;
  - in Ghana, Type_3 borrowers aren't screened individually, and half of first-time applicants are refused because they ask for Type_2;
  - the Ghana pilot loses about 10,000 GHS per 1,000 applicants unless good customers come back;
  - the data covers only people lenders chose to lend to.
- **Risky uses:** using this model to decline Ghanaians at scale, or to chase repeat borrowing.

## 9. Caveats and recommendations
- **Barely validated on Ghana.** Group-level evidence from Zindi's scores puts Ghana's default rate at about 13% and Type_3's at 7%, above the 3.2% break-even ([learnings/11](../learnings/11_fairness.md) §10). The Ghana rule ([ADR 0021](adr/0021-ghana-rules.md)) passes 4 of 6 stress tests: it's the best of 729 policies tested, not proven. Trust gates are in [ADR 0019](adr/0019-kenya-to-ghana-transfer.md): about 5,000 labelled loans, recalibration, monthly drift checks, and a capped pilot.
- **Scores drift.** Default rates moved from about 1% (2022) to 9–12% (2023–24). Recalibrate often.
- **The starter loan is costed, not tested.** Its value rests on repeat business measured at about 200 KES, from Kenyan lending with no limit model. It breaks even at about 50–130 KES. Run it as a controlled pilot, and track outcomes.
- **Repeat the audit with gender** if NkwaPay collects it for bureau reporting.
- **The law asks for things this model can't do alone:** a bureau check, an affordability view, and appeal and record-keeping systems. See the [compliance map](compliance.md).
