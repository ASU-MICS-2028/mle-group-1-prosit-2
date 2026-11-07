# 0021 · Ghana's rules: no full-size loans yet

- **Status:** Accepted as a capped, unproven pilot (Joseph, 7 Nov 2026). It passes 4 of 6 stress tests and no tested policy passes more (see below). Joseph checked that Zindi's rules allow the probe; the report still discloses it. Replaces the Ghana parts of [0019](0019-kenya-to-ghana-transfer.md) (dropping `loan_type`, no auto-decline) and [0020](0020-fairness-mitigation.md) (Ghana's clue set and uncapped starter). Kenya is unchanged.
- **Date:** 7 Nov 2026 · **Owner:** Joseph · **Step:** 11, for step 12

## Context
Two batches of Zindi scores, each file flagging one Ghanaian group, give the real number of defaults per group. Totals only, never per person. Zindi's split is 4,649 public and 13,945 private loans, with 181 and 541 defaults. That is the only split that lets all 19 group files come out as whole numbers, and their public and private parts add up to each group's size. Kenya comes out at 275 of 15,069 (1.8%), matching the training data.

Ghana has only 446 customers, so "range" below counts customers rather than loans. It is deliberately cautious.

| Group | Loans | Defaults | Rate | Cautious range |
|---|---|---|---|---|
| Ghana, all | 3,525 | 447 | 12.7% | 9.9–16.1% |
| Type_2 | 449 | 226 | 50.3% | 43.8–56.8% |
| Type_3 | 3,039 | 213 | 7.0% | 4.2–11.4% |
| Type_3 first loans | 296 | 29 | 9.8% | 6.4–14.6% |
| Type_3 risk bands 1, 2, 3 (safest 60%) | 1,823 | 88 | 4.8% | each band reaches from about 2% to 11–13% |
| Type_3 riskiest 40% (bands 4, 5) | 1,216 | 125 | 10.3% | band 4: 6.2–16.8% |
| Other types | 37 | 8 | 22% | too few to rely on |

Type_2 first loans default as often as Type_2 repeat loans (about 50%), so tenure doesn't explain Type_2. The three safest Type_3 bands are flat (5.1%, 4.4%, 4.9%): inside them the Kenyan model can't rank.

## Options we tested
**Model rules.** Cost per Ghanaian applicant on main costs (`learnings/tables/11b_ghana_models.csv`):

| Rule at 3.2% | Declined | Defaults caught | Cost (GHS) |
|---|---|---|---|
| Approve everyone | 0% | 0% | 344 |
| 13 clues as they are | 47% | 79% | 105 |
| No `loan_type` (ADR 0019) | 28% | 64% | 142 |
| No "borrow often" clues | 30% | 63% | 147 |
| No `loan_type`, no "borrow often" (ADR 0020) | 22% | 59% | 156 |
| Unseen types treated as Type_1 | 15% | 53% | 170 |
| Decline everyone | 100% | 100% | 79 |

**Every full / starter / decline choice** over six groups, 729 policies, at 4 values of repeat business per good payer: 2,916 scenarios (`11b_ghana_policies.csv`). Starter = 300 GHS. The same policy wins on the public and the private part in all four.

| Repeat value | Where it comes from | Cheapest policy | Its cost | Decline everyone | Type_3 starter, rest declined | Bands 1–3 full, rest declined |
|---|---|---|---|---|---|---|
| 0 GHS | fee only | Decline everyone | 79 | 79 | 89 | 102 |
| 16 GHS | Kenya's measured 200 KES, same US$ | Starter for bands 1–3 only | 87 | 93 | 90 | 108 |
| 180 GHS | Kenya's measured 2× the fee | Starter for all but Type_2 | 101 | 236 | 102 | 171 |
| 360 GHS | Step 4's guess | Starter for everyone | 107 | 393 | 114 | 239 |

**No full-size loan is in the cheapest policy at any repeat value.**

## Stress tests
`src/ghana_rule_tests.py`, tables `learnings/tables/11c_*.csv`. The pass rules were written before these tests ran, though the main cost table above was already known. The rate ranges count customers, not loans, which is deliberately harsh: the safest 60% of Type_3 comes from only 112 customers.

| Rule | Result | Pass? |
|---|---|---|
| A. Beats every policy giving full-size loans to 10%+ of applicants, on public and private, and in 95%+ of draws | Wins on both parts at all 4 repeat values, but in only **77–87%** of draws. The rival wins if Type_3's safest 60% really default near or below break-even, and we can't rule that out | **Fail** |
| B. Against declining everyone: at most 15 GHS extra with no repeat value; wins 50%+ of draws at 16 GHS, 95%+ at 180 and 360 | +10.1 GHS; 63%; 100%; 100% | Pass |
| C. Beats the full-size policies in 90%+ of 2,880 assumption combinations | **78%.** Weakest when a typical loan is 1,500 GHS (47%), starters are 600 GHS (68%), or starters default 3× as often (57%) | **Fail** |
| D. Beats them on Ghana's real amounts, mean and median per group | Yes at all 4 repeat values | Pass |
| E. Beats them if starters default twice as often | Yes, narrowly at 0 repeat value (101 vs 102); loses at 3× | Pass |
| F. At most 15 GHS above the cheapest policy, including one picked on the other data part | At most 10.1 above the cheapest | Pass |

**All 729 policies against the same rules** (`11c_ghana_all_policies.csv`): **none passes A or C, and none passes more than 4.** This policy and its near-twin (also a starter for the 37 other-type loans) are the only two at 4. So it is the best we tested, not proven.

**It loses money without repeat business** (`11c_ghana_money.csv`). Per 1,000 Ghanaian applicants: 258,638 GHS lent, 7,215 in fees, 17,282 lost, **net −10,066**, or 6.7% of money lent. Every policy that lends loses money on fees alone; full-size versions lose 2–9 times as much. The pilot is a capped cost of learning, justified only if repeat business arrives.

**New finding: Type_2 is a different kind of loan.** Its median is 76,970 GHS, against 1,500–3,200 GHS for Type_3 groups. So the 3,000 GHS assumption badly understates Type_2's losses, which strengthens declining it.

## Decision
1. **Type_2 and other unseen types: decline.** About half of Type_2 loans default, in every tenure group.
2. **Type_3: starter loan only, 300 GHS, for every applicant,** in a pilot with a cap on total exposure. No full-size loans in Ghana yet.
3. **Probability shown is the group's measured rate** (Type_2 50%, Type_3 7%, other 22%), not the Kenyan model's score, which prices Type_3 at 3.2% on average.
4. **The Kenyan model doesn't decide anything in Ghana yet.** So the clue question falls away for Ghana.
5. ADR 0019's trust gates stay: full-size loans only after about 5,000 labelled Ghanaian loans.

## Why
- A starter limits a default from 2,716 to 286 GHS. At Type_3's rates that matters more than the fee given up.
- Declining everyone is cheapest only if a good customer is worth nothing later. The Type_3 pilot beats it above **about 13 GHS** (about US$1.15) of repeat business per good payer. Kenya measured about US$1.43, or 2× the fee, depending on how it's converted. It costs about 10 GHS per applicant if there is no repeat business at all: the price of learning.
- It's simple, explainable to a regulator, and doesn't rest on a Kenyan ranking that is flat across most of Type_3.

## Consequences
- **We rejected keeping the riskiest 40% of Type_3 out,** although at 16 GHS that's cheaper by about 3 GHS. The bands come from a model we're not otherwise trusting there, and they'd refuse first-timers (all in the top band) who need a record. Worth reopening with pilot data.
- **Half of first-time applicants (333 of 662) are refused,** because they're asking for Type_2. Report this as a product decision, with its real default rate, not as a fairness win.
- **Declines are on product, so letters must say so** (`docs/compliance.md`), with a way to ask for a Type_3 starter instead.
- **Pricing alternative, not proposed:** at 7% default, full-size Type_3 needs a fee of about 6.8% instead of 3%; the safest 60% need about 4.6%. Worse for borrowers; needs a check against the BoG Directive.
- **Limits of this evidence:**
  - Costs assume a typical 3,000 GHS loan, though the mean is 15,537, so full-size losses are probably understated. That favours this decision.
  - Repeat value is Kenyan, untested in Ghana.
  - Starters are assumed to default as often as the requested loans did; the rate is measured on larger loans.
  - These rates came from the test set. Any later Zindi score of a model built using them is contaminated (the three scores in `07b_zindi_submissions.csv` predate the probe).
- **Would change our mind:** pilot default on starters far from 7%; Ghanaian repeat value under about 13 GHS; pilot data showing Type_3's safest 60% below the 3.2% break-even, which would make full-size loans for them the better choice.

## Links
`src/zindi_submissions.py` (`--read-exact`) · `learnings/tables/11b_ghana_{exact,models,policies}.csv` · [learnings/11](../../learnings/11_fairness.md) §10
