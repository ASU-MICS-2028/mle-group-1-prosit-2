# 0022 · The scoring service

- **Status:** Accepted (Joseph told the AI to proceed, 7 Nov 2026; review before the demo).
- **Date:** 7 Nov 2026 · **Owner:** Joseph · **Step:** 12

## Context
Part E asks for a saved model and one function: application in, probability, decision and top 3 reasons out, with latency and required data documented. The scorer applies [ADR 0020](0020-fairness-mitigation.md) in Kenya and [ADR 0021](0021-ghana-rules.md) in Ghana. Testing raised two choices nobody had decided.

## Options we tested
**A Kenyan loan type the model has never seen.** We hid each of 6 types from training (100+ loans each, leaving out Type_1), then scored them as new. KES per loan, `learnings/tables/12_unseen_loan_type.csv`:

| Option | Cost | Verdict |
|---|---:|---|
| Trust the model (it declines 94% anyway) | 94.1 | close, but gives false comfort |
| Starter loan for all | 141.9 | costs most after approving all |
| **Decline all** | **90.7** | **chosen** |
| Approve all | 435.4 | |

Hidden types default 9.3% against a predicted 12.0%, but single types miss badly (Type_10: 2.6% vs 15.7%).

**Past defaulters.** A test applicant who defaulted on all 3 earlier loans was approved at 1.9%: the model's weights on `n_defaults` (0.07) and `past_default_rate` (−0.06) are tiny, and only 122 labelled loans follow a default. Honest scores, cost per loan, `12_past_default_options.csv`:

| Option | Newly declined | Cost change, customer folds | Cost change, future loans |
|---|---:|---:|---:|
| Leave it to the model | 0 | 0 | 0 |
| Decline any past default | under 0.05% of loans; none defaulted | +0.02 (0.00, 0.04) | +0.03 (0.01, 0.05) |
| Decline 2+ past defaults, or a rate of 50%+ (**chosen**) | 0 | 0 | 0 |

## Decision
1. **One function, `score(application)`, and one saved file,** `data/models/scorer.joblib` (ignored by git), built by `python src/scorer.py --fit`.
2. **It rejects bad input** and lists every problem. Unknown fields are refused too, so sensitive fields can't slip in.
3. **Kenya, in order:** 2+ past defaults or a rate of 50%+ → decline; unseen loan type → decline; at or below 2.1% → approve with the amount model's limit; first-timer below 24% → 500 KES starter; otherwise decline.
4. **Ghana:** Type_3 → 300 GHS starter; everything else → decline. The probability is the group's rate and is labelled as such.
5. **First-timer means `n_prev_loans == 0`,** not the `New_versus_Repeat` label: 1,864 Zindi test loans are labelled "Repeat Loan" with no earlier loan on record.

## Why
- The past-default rule changes nothing on history, because the model already declines those people. It only stops odd inputs getting through, and a regulator would expect it.
- Declining unseen types is cheapest, and matches Ghana's rule.

## Consequences
- **Results:** all 18 tests pass. All 18,594 Zindi applicants are accepted. Kenya: 82.1% approve, 8.8% starter, 9.1% decline. Ghana: 86.2% starter, 13.8% decline. These match the Model Card. Median 29 ms (Kenya, repeat), 95% under 37 ms; Ghana under 0.1 ms; about 1.6 s to load.
- **The past-default rule rests on thin data:** 30 loans from 9 customers with 2+ defaults.
- **Approved applicants mostly get one general line,** "Nothing in your application raised our main risk checks", as few stand out from the average.
- **Not built:**
  - the credit-bureau check required before every decision (Act 726 s.26(4));
  - calculating the history fields: the caller must supply them, using the rules in `src/features.py`;
  - a web service, as the brief asks only for a function.
- **Would change our mind:** more loans after a default; a real Kenyan launch of a new loan type.

## Links
`src/scorer.py` · `tests/test_scorer.py` · `src/unseen_type_test.py` · `src/past_default_test.py` · [learnings/12](../../learnings/12_scorer.md) · `learnings/tables/12_*`
