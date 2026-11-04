# 0019 · Using the Kenyan models in Ghana

- **Status:** Accepted (reviewed and rerun from a fresh clone by Joseph, 4 Nov 2026; affects Liza's step 11 and Joseph's step 12)
- **Date:** 4 Nov 2026 · **Owner:** Alice · **Step:** 10

## Context
All labelled loans are Kenyan. Ghana's 3,525 test loans (446 customers) differ in five ways:
- **no known repayment outcome** for anyone;
- 87% use a **loan type never seen in Kenya** (Type_3 86%, Type_8 1%);
- 97% come from **lenders never seen in Kenya**;
- 14% run **over 90 days** (Kenya: 0.2%);
- loans are about **8× bigger in US$** (median $349 vs $44).

13% are **Type_2**, which Kenya has only 74 loans of, 61% defaulted.

For Task 2 there are no Ghanaian labels. For Task 1, `Test.csv` holds the real Ghanaian amounts, so that model *can* be scored on Ghana.

## Options we tested
Every option is in `notebooks/04_transfer_and_fairness.ipynb` Part 1; tables are in `learnings/tables/10_*.csv`.

| Test | Result | Verdict |
|---|---|---|
| Domain classifier, all clues (Ghana vs Kenya) | ROC-AUC 1.00; control (Kenya test vs Kenya) 0.50 | no overlap |
| … without `loan_type` and outcome clues | 0.95 (logistic) / 0.97 (LightGBM) | still almost separable |
| Importance weights, no cap | ESS 19 of 68,464 loans | useless |
| Weights, best cap (99th percentile) | ESS 2,757 (4%) | still tiny |
| **Task 1 on real Ghanaian amounts** (MAE log) | as is (cedis as shillings) **0.45**; US$ 0.51; no `loan_type` 0.51; US$ + weights 0.72–0.75; guess the average 1.09; same as last loan 0.52 | as is wins, weights hurt |
| Task 1 bias by group (predicted ÷ real) | earlier loans 1.15; first loans 3.4; over 90 days 3.1; Type_2 2.8 | first, long and Type_2 loans: limits far too high |
| **Task 2 share declined in Ghana** (3.2% cut-off) | as is 47% (first loans 100%, Type_2 100%); unseen types → Type_1 15%; drop `loan_type` 28% / 24% (US$); weighted 68–100% | as is is far stricter than Kenya's 19% |
| Task 2 Kenya future-loan lift | as is 7.8; drop `loan_type` 6.9; weighted 4.7–5.2 | dropping the type costs 0.9 |
| Kenyan stand-ins (lift on future loans) | first loans 2.5 [2.1, 3.0]; earlier loans, no outcome 6.5 [4.5, 10.4]; all 7.1 | the model ranks these less well |
| Labelled loans needed (lift 95% range) | 2,000 → 4.5–15.2; 5,000 → 4.9–10.9; 10,000 → 5.7–9.1 | about 5,000–10,000 |

## Decision
1. **No importance weighting.** Kenya and Ghana barely overlap. The weighted data is worth at most 4% of Kenya, and every weighted model is worse.
2. **The amount model is used in Ghana in local currency, as is**, but only for **repeat borrowers on loans up to 90 days**. First loans, loans over 90 days, and Type_2 / Type_8 loans get a **starter limit set by NkwaPay policy**, not by the model, until Ghanaian data exists. For those groups the model over-predicts 2.8–3.4×.
3. **The default model must not auto-decline in Ghana yet.**
   - **The Kenyan model as it stands is unsafe.** It would decline 47% of applicants, including every first-timer and every Type_2 loan. Type_2's high risk rests on 74 Kenyan loans.
   - **For a pilot,** score with the model **without `loan_type`** (lift 6.9 in Kenya; 28% declined in Ghana). It makes no claim about products Kenya has never seen.
   - Send first loans and Type_2 to **small starter loans or manual review** instead of declining them.
4. **Trust gates before full automatic use in Ghana:**
   - at least **5,000 labelled Ghanaian loans** (about 90 defaults), with the PR-AUC lift's 95% range reported;
   - Platt recalibrated on Ghanaian outcomes;
   - PSI checked monthly, with clues above 0.25 investigated;
   - the pilot's real default rate compared with the predicted one (about 8.7%), overall and for Type_3, Type_2 and first loans.

## Why
- The domain classifier shows Ghana is a different population, not Kenya in another currency. Weighting only works where the two overlap, and here they don't.
- Task 1 is the one place we can check against real Ghanaian answers. There, local currency beats US$, and weights make it worse.
- For Task 2, the model's view of Ghana is driven by things that are *missing*, not risky:
  - no Ghanaian has a known outcome, so `no_known_history = 1` for all of them;
  - their loan types are unknown to the model.

  Auto-declining people for missing data would shut out exactly the borrowers the brief worries about.
- The sample-size test says that below about 5,000 labelled loans, a Ghanaian accuracy check can't tell a good model from a weak one.

## Consequences
- **Liza (step 11):** the country gap is the main fairness finding. `PD` in notebook 04 holds the Ghanaian probabilities for every option, for the selection-rate tables. First-time borrowers are declined everywhere, in Kenya and in Ghana.
- **Joseph (step 12):** the scorer needs a country switch:
  - Kenya: the step 7 model, 2.1% cut-off;
  - Ghana: the model without `loan_type`, 3.2% cut-off, with first loans, Type_2 and long loans routed to starter limits or review.
- **The Credit Reporting Act** route (Ghanaian bureau data) would give Ghanaian outcomes and fix the biggest gap.
- **Would change our mind:** Ghanaian outcomes showing that Type_3 behaves like Kenya's Type_1. Mapping Type_3 to Type_1 would then give 15% declined at lift 7.8.

## Links
`notebooks/04_transfer_and_fairness.ipynb` · `learnings/10_transfer.md` · `learnings/tables/10_*.csv` · ADRs [0007](0007-cost-matrix-and-cutoff.md), [0016](0016-final-classification.md), [0018](0018-loan-amount-model.md)
