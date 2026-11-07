# Step 12: the scorer

*Joseph, 7 Nov 2026. Decision: [ADR 0022](../docs/adr/0022-scoring-service.md).*

## What the others need to know
- **`score(application)` takes one application** and returns a probability, a decision, a limit and up to 3 reasons.
- **Three decisions:** approve, starter, decline.
- **All 18 tests pass, and all 18,594 Zindi applicants go through.** About 29 ms per Kenyan call.
- **A test found a real gap:** the model approved a made-up borrower who had defaulted on all 3 earlier loans. We added a rule.

## The question
Can a credit team use the models on one application at a time, and does it behave safely on bad or unusual input?

## How to run it
```sh
PYTHONPATH=. .venv/bin/python src/scorer.py --fit        # once, about a minute
PYTHONPATH=. .venv/bin/python tests/test_scorer.py       # all the tests; a few minutes
```
```python
from src.scorer import score
score({"country": "Ghana", "loan_type": "Type_2", "duration": 90, "New_versus_Repeat": "New Loan", "n_prev_loans": 0, "n_finished": 0, "n_defaults": 0,
       "past_default_rate": None, "no_known_history": 1, "days_since_last_loan": None, "n_loans_last_7d": 0, "n_loans_last_30d": 0, "mean_prev_amount": None, "last_amount": None})
```

## The data the application must send
All 14 fields are required. Any other field is refused.

| Field | Meaning | Allowed |
|---|---|---|
| `country` | Where the loan is | Kenya or Ghana |
| `loan_type` | The product | any text; unseen types are declined |
| `duration` | Loan length in days | above 0 |
| `New_versus_Repeat` | The lender's label | New Loan or Repeat Loan |
| `n_prev_loans` | Earlier loans | whole number, 0 or more |
| `n_finished` | Earlier loans whose outcome is known | whole number, at most `n_prev_loans` |
| `n_defaults` | Earlier loans not repaid | whole number, at most `n_finished` |
| `no_known_history` | 1 if no earlier outcome is known | 0 or 1 |
| `n_loans_last_7d`, `n_loans_last_30d` | Recent loans. Used for the limit only, not the default decision | whole number, 0 or more |
| `past_default_rate` | `n_defaults` ÷ `n_finished` | 0 to 1, or empty |
| `days_since_last_loan` | Days since the last loan | 0 or more, or empty |
| `mean_prev_amount`, `last_amount` | Usual and latest loan size, local currency | 0 or more, or empty |

## What comes back
These applicants are made up.

| Applicant | Probability | Decision | Limit | First reason |
|---|---:|---|---:|---|
| Kenya, 12 earlier loans, none defaulted | 0.8% | approve | 5,434 KES | Nothing in your application raised our main risk checks. |
| Kenya, first-timer | 4.4% | starter | 500 KES | This is your first loan with us, so we have no borrowing history to go on. |
| Kenya, 3 of 3 defaulted | 1.9% | decline | 0 | You did not repay 3 of your earlier loans. |
| Kenya, Type_7, 30 days | 17.7% | decline | 0 | Loans of this kind (Type_7) have been repaid less often than others. |
| Ghana, Type_3 | 7.0% (group) | starter | 300 GHS | We don't yet have enough repayment records in Ghana to offer larger loans. |
| Ghana, Type_2 | 50.3% (group) | decline | 0 | About half of loans of this kind (Type_2) have not been repaid in Ghana. |

In the third row the probability is under the cut-off, but the rule still declines. The model doesn't weigh past defaults much (see below).

## What I tried and what happened
**Speed** (`12_latency.csv`, 1,000 calls each):

| Case | Median | 95% of calls under |
|---|---:|---:|
| Kenya, repeat | 29 ms | 37 ms |
| Kenya, first-timer | 20 ms | 25 ms |
| Ghana | under 0.1 ms | under 0.1 ms |

Loading takes about 1.6 seconds once, and the file is 0.3 MB. Ghana is instant because it only looks up the loan type.

**Every real test applicant, one at a time** (`12_decisions_on_zindi_applicants.csv`): none refused.

| | Approve | Starter | Decline |
|---|---:|---:|---:|
| Kenya (15,069) | 82.1% | 8.8% | 9.1% |
| Ghana (3,525) | 0% | 86.2% | 13.8% |
| Kenyan first-timers | 0% | 96.6% | 3.4% |
| Ghanaian first-timers | 0% | 44.7% | 55.3% |

**The past-defaulter gap.** My test expected a decline, and the scorer approved. On real data the problem is small: nobody with 2+ past defaults or a past default rate of 50%+ was approved. But only 122 labelled loans follow a default, so the model has barely learned this. The new rule changes no decision on past loans, so it costs nothing.

**Unseen loan types.** Hiding 6 types from training showed that declining is cheapest (90.7 KES per loan, model 94.1, starter 141.9). Ghana already works this way.

## Decision
See ADR 0022.

## What I'm unsure of / limits
- **Starter limits and Ghana's rule aren't validated by real starter-loan repayments.**
- **The credit-bureau check isn't built** (Act 726 s.26(4)), a known gap.
- **Approved applicants mostly get one general reason.** It's honest but less useful than the brief's "top three".
- **The caller works out the history fields.** Wrong history gives a wrong decision, and the scorer can only catch impossible values.
- **Only load a bundle you made yourself.** joblib files can run code when opened.

## Likely Q&A questions and answers
**Q: Why does the 3-of-3 defaulter show 1.9% but get declined?**
A: The model has seen only 122 loans after a default, so it weighs them lightly. The rule catches that, and costs nothing on history. It rests on 30 loans from 9 customers.

**Q: Why is Ghana so fast?**
A: The model decides nothing there yet, so it's a lookup by loan type.

**Q: Why not use New_versus_Repeat to find first-timers?**
A: 1,864 Zindi loans are labelled "Repeat Loan" with no earlier loan on record. We use `n_prev_loans == 0`.

**Q: What happens with a missing field?**
A: It's refused, with every problem listed. Empty values are only allowed in the four fields that are naturally unknown for a new borrower.

**Q: Can someone send gender?**
A: No. Unknown fields are refused.
