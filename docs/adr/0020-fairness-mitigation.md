# 0020 · Fairness: what we measure first, and the two fixes

- **Status:** Accepted for Kenya (Joseph, 6 Nov 2026). **The Ghana parts are replaced by [ADR 0021](0021-ghana-rules.md).** Changes [0016](0016-final-classification.md) (which clues the default model uses) and adds to [0019](0019-kenya-to-ghana-transfer.md) (first loans in Kenya too).
- **Date:** 5 Nov 2026 · **Owner:** Joseph (took over step 11 from Liza) · **Step:** 11

## Context
The brief (Part D) asks who the model treats worse and what to do about it. On future Kenyan loans:

- **First loans:** 53% of good payers are wrongly declined, against 8% of borrowers with known outcomes (gap 45 points, 95% range 43–48). But first loans really do default more often (10.9% vs 1.3%).
- **On launch it's worse:** the model fitted on all labelled loans declines **100%** of first-time applicants, in Kenya and in Ghana. Nobody could ever get a first loan, so nobody could ever build a record.
- **"Borrow more" message:** 31% of declined Kenyans and 34% of declined Ghanaians (on the no-`loan_type` model) are told they haven't borrowed recently. The model rewards frequent borrowing, which pushes against responsible lending.

## Options we tested
Every setting is chosen on older loans only. Cost change is against no fix, with a customer-bootstrap 95% range. Full table: `learnings/tables/11_mitigations.csv`.

| Option | First loans offered any loan | Their good payers refused | Other good payers refused | Cost change, main (KES per loan) | Cost change, with repeat business | Verdict |
|---|---|---|---|---|---|---|
| No fix (cost 47.9 / 86.7) | 45% | 53% | 8% | — | — | the baseline |
| Starter loan, 10% of a typical loan | 100% | 0% | 8% | +2.2 [1.8, 2.6] | −6.5 [−7.3, −5.8] | **chosen, combined below** |
| Starter loan, 25% | 100% | 0% | 8% | +4.4 [3.6, 5.3] | −4.3 [−5.3, −3.3] | costs more than 10% |
| Starter loan, 50% | 100% | 0% | 8% | +8.0 [6.6, 9.6] | −0.7 [−2.3, 1.0] | costs more than 10% |
| Own cut-off for first loans, equal wrongly declined | 65% | 33% | 8% | +4.3 [2.7, 6.0] | +1.0 [−0.7, 2.7] | costs more, and doesn't reach equal |
| Own cut-off for first loans, equal approval | 70% | 28% | 8% | +4.7 [3.1, 6.6] | +0.6 [−1.1, 2.5] | same |
| **Drop the 3 "borrow often" clues** | 47% | 51% | 8% | −0.6 [−2.0, 0.7] | −1.6 [−3.3, 0.1] | **chosen: free** |
| Hide tenure (drop 3 tenure clues) | 41% | 57% | 8% | −0.2 [−1.3, 0.9] | +1.9 [0.7, 3.1] | **backfires:** the other clues still show tenure |
| Reweigh tenure and outcome | 68% | 30% | 12% | +4.0 [1.9, 6.2] | +13.6 [11.1, 16.1] | breaks honest scores (first loans priced at 0.28× their risk) and hurts others |
| Drop `loan_type` (for comparison) | 35% | 63% | 12% | +3.9 [1.4, 6.4] | +19.6 [16.6, 22.8] | worse in Kenya; Ghana only (ADR 0019) |
| Drop "borrow often" + starter at 10%, no cap | 100% | 0% | 8% | +1.6 [0.1, 3.0] | −7.7 [−9.5, −6.0] | fails on main costs; see the scenario test |

| Which fairness measure comes first? | Result | Verdict |
|---|---|---|
| Sufficiency: one score means one risk for everyone | No group is priced unfairly high; first loans are priced a little *low* | **first** |
| Separation: equal mistakes, especially good payers wrongly declined | Very unequal for first loans, so this is the harm to fix | **second; what we fix** |
| Independence: equal approval | Reported; forcing it would ignore a real 8× difference in default rates | **reported only** |

## The scenario test (1,224 combinations)
`src/fairness_scenarios.py`, tables `learnings/tables/11b_*.csv`: every way of dropping the 3 clues × 17 starter policies (none, 4 sizes, 5 risk caps at 2 sizes, 2 wider groups) × 3 cut-offs × 3 validation tests. The pass rules were set before seeing results: no cost rise beyond noise on any view; fewer good first-timers refused and no harm to others; consistent across tests; survives pessimistic assumptions.

**We also measured the guess behind "repeat business".** Step 4 assumed a good customer is worth 400 KES later. Among Kenyan first-timers who repaid, those starting at or below 2,500 KES brought in **a mean net of 174–228 KES** later (fees minus later losses), so we use **200 KES**. The median is far lower, about 60–110 KES. 78–84% came back whatever the first-loan size, and smaller first loans defaulted less (4.1% at 500–1,000 KES vs 8.4% over 10,000 KES), though borrowers chose those sizes.

Cost change against no fix, 95% range:

| Candidate | Test | Main costs | Measured repeat value (200 KES) | Step 4 guess (400 KES) |
|---|---|---|---|---|
| Drop clues only | future loans | −0.6 [−2.0, 0.8] | −1.1 [−2.5, 0.3] | −1.6 [−3.2, 0.1] |
| | future loans, new customers | −2.6 [−9.4, 3.8] | +2.1 [−5.6, 9.3] | +6.7 [−2.3, 15.5] |
| | new customers | −0.3 [−1.0, 0.3] | −2.3 [−3.0, −1.6] | −4.3 [−5.2, −3.4] |
| Drop clues + starter, no cap | future loans | **+1.6 [0.1, 3.0]** | −3.1 [−4.6, −1.6] | −7.7 [−9.5, −6.0] |
| | future loans, new customers | **+11.2 [3.9, 18.9]** | −10.6 [−19.2, −3.0] | −32.4 [−43.4, −22.7] |
| | new customers | **+2.9 [2.1, 3.6]** | −16.4 [−17.4, −15.5] | −35.7 [−37.1, −34.3] |
| **Drop clues + starter below 24% risk** | future loans | **+0.9 [−0.5, 2.4]** | **−3.4 [−4.9, −1.9]** | −7.7 [−9.5, −6.0] |
| | future loans, new customers | **+7.0 [−0.4, 14.7]** | **−12.5 [−20.7, −5.1]** | −32.1 [−42.6, −22.5] |
| | new customers | **+1.7 [0.9, 2.3]** | **−17.3 [−18.2, −16.4]** | −36.2 [−37.7, −34.9] |

| Other scenarios | Result | Verdict |
|---|---|---|
| Dropping only 1 or 2 of the clues | All within noise, but the "borrow more" message stays | Drop all 3 |
| Cut-off 6% or 9.6% (with the clue drop and capped starter, future loans) | Main cost 57.9 / 67.9 vs 48.9; at the measured value 63.7 / 70.6 vs 64.0; defaulters stopped among other loans 27% / 15% vs 49% | **Keep 2.1%** |
| Starter at 25% or 50% | Costs more on every view | Keep 10% |
| Starter at 5% | About 0.5 KES cheaper, but 250 KES is below nearly all loans we can observe | Keep 10% |
| Risk cap 15–39% | Differences under 1 KES, within noise | 24%: break-even at the measured value |
| Starter for everyone above the cut-off | Cheapest at the measured value (52.9), but +5 KES on main costs, and stops no defaulter at all | Rejected |
| Starter also for no-known-outcome loans | Main +2.1 vs +0.9; no better at the measured value | Rejected |

**The verdict against our rules:** no policy that helps first-timers is free. The capped starter costs about 1 KES per loan on main costs in every future block, and its 1.7 KES on the new-customers test is above noise, so it **misses the "no cost rise" rule narrowly** there. It's the closest pass, and the only starter policy within noise on both future-loan tests. Across 720 assumption combinations it saves money in 63%. It always costs a little (+0.2 to +2.4 KES) if future business is worth nothing, and breaks even at about 50–130 KES of future business, depending on how much of it a starter keeps; the measured median is 60–110 KES.

## Decision
1. **Primary measure:** sufficiency (an honest score), then the wrongly-declined rate as the harm we act on. Approval rates are reported.
2. **Drop `n_loans_last_7d`, `n_loans_last_30d` and `days_since_last_loan` from the default model** in both countries (`DEFAULT_CLUES` and `GHANA_CLUES` in `src/features.py`). The amount model keeps all 13: it doesn't decide who gets a loan.
3. **First-time applicants above the cut-off get a starter loan of about 10% of a typical loan** (about 500 KES / 300 GHS), not a decline.
   - **Kenya:** only below **24% predicted risk**, the break-even at the measured repeat value (`RISK_CAP` in `src/fairness_scenarios.py`). 97% of first-timers qualify at launch.
   - **Ghana:** no cap. A cap would refuse 55% of first-timers on Kenyan scores we can't check, which ADR 0019 rules out.
   - **The 2.1% and 3.2% cut-offs stay.**
4. **No group cut-offs, no reweighing, no country-specific thresholds.**

## Why
- The clue drop is free. Cost is within noise, Kenyan lift only moves from 7.78 to 7.72, and "you haven't borrowed recently" disappears. Declines fall from 19.2% to 17.9% in Kenya.
- The starter loan is the only option that closes the first-loan gap. A first loan is how a borrower gets a record at all.
- With the cap, it costs about 1 KES per loan on the narrow view, and saves about 3 at the measured repeat value. The earlier claim of −7.7 relied on step 4's guess of 400 KES, which was about twice what we measured.
- First-timers' good payers refused fall from 53% to 4%; nobody else is refused more on average.
- A 10% loan beats larger ones because the risk is on a first-timer the model can't rank well (lift 2.5).

## Consequences
- **Scorer (step 12):** use `final_model(train, DEFAULT_CLUES)` for Kenya and `final_model(train, GHANA_CLUES)` for Ghana. First loans above the cut-off → starter loan (Kenya: only below 24% risk).
- **Reasons:** same-top-3 stability on refits falls from 90.5% to 85.4%, the price of the clue drop. Step 8's headline numbers describe the 13-clue model.
- **The clue drop isn't free for everyone:** Lender B's good payers go from 80% to 87% wrongly declined, because more of the model's weight falls on `loan_type`. The no-known-outcome group moves from 13% to 16%.
- **Starter loans stop few first-time defaulters** (20% are stopped by the cap); they shrink each loss from 4,700 to 650 KES. They need a cap on total first-loan exposure.
- **Mean future value is fragile.** Across all repaid first-timers it is **negative** (−2,761 KES, 95% range −5,287 to −962), because customers who start large go on to lose a lot on big later loans. The positive figure holds only for small starters, and comes from lending that had no limit model.
- **Ghana:** with the clue drop plus ADR 0019's routing, the model **declines nobody** (78% full loan, 22% starter or review). That matches "no auto-decline yet", but it means nothing screens Ghanaian repeat borrowers until outcomes exist. The pilot needs a total exposure cap.
- **"Manual review" must be digital:** BoG Directive para. 2.3(1) bars manual approval from the physical office.
- **Would change our mind:** real repeat-business value below about 100 KES; starter-loan outcomes showing default far above about 11%; or a clue-drop cost outside noise on new data.

## Links
`notebooks/04_transfer_and_fairness.ipynb` Part 2 · [learnings/11](../../learnings/11_fairness.md) · `learnings/tables/11_*.csv` · [Model Card](../model_card.md) · [compliance](../compliance.md)
