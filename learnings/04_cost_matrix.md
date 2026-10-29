# 04 · Cost matrix (Liza)

Notebook with all the code: [`notebooks/00b_cost_matrix.ipynb`](../notebooks/00b_cost_matrix.ipynb). It runs top to bottom in a few seconds. You don't need to run it: every result is pasted below.

## What the team needs to know

1. **The rule for Germain (step 7):** decline a loan if its chance of default is above **2.1% in Kenya** or **3.2% in Ghana**.
2. **Where that comes from (Kenya):** approving someone who won't pay back costs **4,700 KES**. Turning away someone who would pay back costs **100 KES**. One bad loan wipes out the fees of 47 good ones, so NkwaPay breaks even at **1 bad borrower in 48** (= 2.1%).
3. **Ghana:** 2,716 GHS vs 90 GHS, so the break-even is **1 in 31** (= 3.2%). Ghana's cut-off is higher because its fee is higher (3% vs 2%).
4. **⚠️ The cut-off only works on honest (calibrated) probabilities.** A model trained with `class_weight="balanced"` gives inflated chances. Germain: calibrate (Platt or isotonic) *before* applying 2.1% / 3.2%. Or pick the cut-off on validation data that gives the lowest total cost.
5. **Our guesses about bad loans hardly matter:** changing how much is recovered (0–30%) or doubling the chasing cost keeps the cut-off at **1.9–2.6% (Kenya)** and **2.9–4.1% (Ghana)**.
6. **What matters most is what a good customer is worth over time.** Counting lost repeat business raises the cut-off to **9.6% (Kenya)** and **14.2% (Ghana)**. Germain: show the total cost at both the main and the repeat-business cut-offs.
7. **Longer loans charge much higher fees** (5.5% to 15%), so they deserve higher cut-offs (about 6% to 14%). One cut-off per country is fine for 7-day loans, which are 95% of Kenyan loans.
8. **Two numbers are our own assumptions, not from the data:** 10% of a bad loan is recovered, and chasing it costs about $1.50 (200 KES / 16 GHS). Replace them if real figures turn up.
9. **For the regulation work:** a 2% fee per week is about 104% a year for someone who keeps borrowing. Compare this with the Bank of Ghana Directive.

## The question

Every time NkwaPay's model judges a loan application, it can be wrong in two ways:

| | The person **would pay back** | The person **won't pay back** |
|---|---|---|
| NkwaPay **approves** | ✅ Good: NkwaPay earns the fee | ❌ **False negative (FN):** NkwaPay loses the money lent |
| NkwaPay **declines** | ❌ **False positive (FP):** NkwaPay loses the fee, and the person goes without credit | ✅ Good: the loss is avoided |

**How to remember the names:** the model's job is to *flag risky borrowers*. "Positive" = flagged as risky.
- **False negative (FN)** = the model *didn't* flag someone, but should have. NkwaPay **approved someone who won't pay back**.
- **False positive (FP)** = the model flagged someone, but shouldn't have. NkwaPay **turned away someone who would have paid back**.

The two mistakes don't cost the same. The brief (Part A.3) asks us to put a **money value** on each one (in shillings and cedis, not just a ratio). Those two values then set the **cut-off**: the chance of default above which NkwaPay should say no.

## What I did

1. **Found the typical loan:** its size and length, in Kenya and Ghana.
2. **Found the fee** NkwaPay earns when a loan is repaid.
3. **Worked out the cost of each mistake:** the cost of FN (approving someone who won't pay back) and the cost of FP (turning away someone who would pay back).
4. **Turned the two costs into a cut-off:** "decline if the chance of default is above X%".
5. **Tested other assumptions** to see how much the cut-off moves.

**Words used below:**
- **Median (middle value):** the value in the middle when everything is sorted. Half are bigger, half are smaller. We use it instead of the average, because a few huge loans pull the average up.
- **Fee:** the extra money a borrower pays back on top of what they borrowed. Fee % = (amount to repay − amount borrowed) ÷ amount borrowed.
- **Recovery:** money NkwaPay gets back later from someone who didn't pay on time.
- **Chance of default (*p*):** what the model will give each applicant. *p* = 3% means "out of 100 people like this, about 3 won't pay back".
- **Cut-off (threshold):** the chance of default above which NkwaPay declines.
- **Calibrated:** the model's chances are honest. When it says 2%, about 2 in 100 such people really don't pay back.

Amounts are assumed to be **Kenyan shillings (KES)** for Kenya and **Ghana cedis (GHS)** for Ghana. The files don't say (see [`docs/01_data.md`](../docs/01_data.md)). Dollar figures use 139.8 KES and 11.0 GHS per US dollar.

## What I tried and what happened

### Step 1: The typical loan

| | Kenya (`Train.csv`) | Ghana (Ghanaian rows of `Test.csv`) |
|---|---|---|
| Loans | 68,654 | 3,525 |
| Middle loan size | **5,249 KES** (about $38) | **3,002 GHS** (about $270) |
| Average loan size | 14,837 KES | 15,537 GHS |
| Middle loan length | 7 days | 7 days |
| Loans lasting a week or less | 95% | 86% |

Loan sizes vary hugely:

| | Kenya (KES) | Ghana (GHS) |
|---|---|---|
| 1 in 10 loans are smaller than | 1,069 | 1,193 |
| 1 in 4 loans are smaller than | 2,295 | 1,581 |
| Middle loan | 5,249 | 3,002 |
| 3 in 4 loans are smaller than | 11,450 | 5,924 |
| 9 in 10 loans are smaller than | 25,051 | 55,321 |

And longer loans are much bigger (Kenya):

| Loan length | Share of loans | Middle loan (KES) |
|---|---|---|
| 1–7 days | 94.7% | 5,000 |
| 8–14 days | 2.3% | 17,800 |
| 15–30 days | 1.7% | 18,000 |
| 31–90 days | 1.1% | 80,000 |
| over 90 days | 0.2% | 258,717 |

**What this means:**
- **Our typical loan is a 7-day loan of 5,000 KES (Kenya) or 3,000 GHS (Ghana).**
- If the currency assumption is right, a typical Ghanaian loan is about **7 times bigger in dollars** than a Kenyan one. That's surprising for mobile-money loans, so we flag it.

### Step 2: The fee

We used **only repaid loans**. The feature audit ([`03_feature_audit.md`](03_feature_audit.md)) found that unpaid loans have penalties added to their repay amount, so for them it doesn't show the real fee.

| Kenya, repaid loans (67,396) | Fee |
|---|---|
| Middle fee | **0.76%** (32 KES) |
| Average fee | 1.68% (504 KES), pulled up by big, long loans |
| Loans with **no fee at all** | **36%** |

| Loan length | Middle fee | Share with no fee |
|---|---|---|
| 1–7 days | 0.7% | 37% |
| 8–14 days | 5.5% | 1% |
| 15–30 days | 7.0% | 1% |
| 31–90 days | 11.2% | 4% |
| over 90 days | 15.0% | 0% |

Among **7-day loans that do charge a fee** (62% of them), the middle fee is **2.0%**. A quarter pay under 0.8%, and a quarter pay over 3.1%.

**Ghana:** **86% of loans charge exactly 3%**, and only 1% are free. That's 90 GHS on a 3,000-GHS loan. Ghana has no labels, so we couldn't keep only repaid loans. But with only about 2% defaulting, the middle value isn't affected.

**What this means:**
- **The "free loan" puzzle:** a lender doesn't usually lend for free. Almost all free loans are 7-day Kenyan loans. Most likely, the fee was collected some other way (e.g. taken off the money before it was sent, or charged by the mobile-money platform), or these were special offers. The data can't tell us.
- So the 0.7% middle fee probably **understates** what NkwaPay earns. **2.0% is our main fee for Kenya**, and 0.7% is tested in Step 5.
- **Ghana's main fee is 3.0%.**

### Step 3: The cost of each mistake

**Cost of FN** (approving someone who won't pay back) = money lent − money recovered later + cost of chasing the debt.
**Cost of FP** (turning away someone who would pay back) = the fee NkwaPay would have earned.

The data gives us the money lent and the fee. It doesn't give us the other two, so we had to assume them:

| Assumption | Our value | Why |
|---|---|---|
| Money recovered from someone who doesn't pay | **10%** of the loan | No collateral (nothing to take back, like a car) and tiny loans, so chasing hard isn't worth much |
| Cost of chasing the debt | **About $1.50** (200 KES / 16 GHS) | A few weeks of SMS reminders, a few phone calls, an agent follow-up. The work is similar in both countries, so we use the same dollar cost. |

| | Kenya (KES) | Ghana (GHS) |
|---|---|---|
| Money lent | 5,000 | 3,000 |
| Fee earned if repaid | 100 (2%) | 90 (3%) |
| Recovered after a default | 500 (10%) | 300 (10%) |
| Cost of chasing | 200 | 16 |
| **Cost of FN** (approve someone who won't pay back) | 5,000 − 500 + 200 = **4,700** | 3,000 − 300 + 16 = **2,716** |
| **Cost of FP** (turn away someone who would pay back) | **100** | **90** |
| Cost of FN ÷ cost of FP | **47×** | **30×** |

**The repeat-customer question.** Customers keep coming back. After a typical loan, the same customer takes **8 more loans** (middle value), and that only counts loans inside our data window. If NkwaPay turns away a good customer and half of such customers leave for good, the cost of FP (turning away someone who would pay back) becomes:
- **Kenya:** 100 + 0.5 × 8 × 100 = **500 KES**
- **Ghana:** 90 + 0.5 × 8 × 90 = **450 GHS** (assuming Ghanaians return as often as Kenyans)

(Why 8, when the middle customer has only 6 loans? (The average is 10, pulled up by heavy borrowers.) Frequent borrowers have many loans, so a "typical loan" more often belongs to a frequent borrower.)

**The cost the money doesn't show:** someone turned away goes without credit they may badly need, for school fees, shop stock or an emergency. It isn't NkwaPay's cost, but it's why being too strict is harmful. It comes back in the fairness work (step 11).

### Step 4: From costs to the cut-off

**The easy way to see it: "1 in 48" (Kenya).** One bad loan loses 4,700 KES. Each good loan earns 100 KES. So one bad loan wipes out the fees from **47 good loans** (4,700 ÷ 100 = 47).

Picture 48 similar applicants:
- If **exactly 1** won't pay back, the 47 good loans earn 4,700 and the 1 bad loan loses 4,700. **NkwaPay breaks even.**
- If **fewer than 1 in 48** won't pay back, NkwaPay makes money → **approve**.
- If **more than 1 in 48** won't pay back, NkwaPay loses money → **decline**.

**1 in 48 = 2.1%.** For Ghana: 2,716 ÷ 90 = 30.2, so break-even is about **1 in 31 = 3.2%**.

**The same thing as a formula.** For an applicant with chance *p* of not paying back:

| Choice | What could go wrong | Expected (average) cost |
|---|---|---|
| Approve | they don't pay back (chance *p*), costing 4,700 | *p* × 4,700 |
| Decline | they would have paid back (chance 1 − *p*), costing 100 | (1 − *p*) × 100 |

The cut-off is where both cost the same:

```
p × 4,700           = (1 − p) × 100
p × 4,700 + p × 100 = 100
p × 4,800           = 100
p                   = 100 ÷ 4,800 = 2.1%
```

Check at 2.1%: approving costs 0.021 × 4,700 ≈ 98, and declining costs 0.979 × 100 ≈ 98. They're equal.

> **Decline when the chance of default is above: cost of FP ÷ (cost of FP + cost of FN)**
> (what turning away a good borrower costs) ÷ (that + what approving a bad borrower costs)

This is the formula in the brief's Appendix A.

**A worked example (Kenya):**

| Chance of default | Expected cost if approved | Expected cost if declined | Decision |
|---|---|---|---|
| 1% | 0.01 × 4,700 = **47** | 0.99 × 100 = **99** | ✅ approve |
| 5% | 0.05 × 4,700 = **235** | 0.95 × 100 = **95** | ❌ decline |

**Does the loan size change the cut-off?** Barely. The collection cost (200 KES) is the same for every loan, so small loans get a slightly stricter cut-off:

| Kenyan loan size | 1,000 | 2,500 | 5,000 | 11,500 | 25,000 |
|---|---|---|---|---|---|
| Cut-off | 1.79% | 2.00% | 2.08% | 2.13% | 2.16% |

**Longer loans charge more, so they get higher cut-offs.** Here is a rough check that pretends the model only knows the loan length, so its chance of default is the actual default share for that length:

| Loan length | Fee | Its own cut-off | Actual default share | Decision |
|---|---|---|---|---|
| 1–7 days | 2.0% | 2.08% | 1.22% | ✅ approve |
| 8–14 days | 5.5% | 5.72% | 8.21% | ❌ decline |
| 15–30 days | 7.0% | 7.14% | 13.25% | ❌ decline |
| 31–90 days | 11.3% | 11.08% | 15.90% | ❌ decline |
| over 90 days | 15.0% | 14.28% | 44.74% | ❌ decline |

Even this rough version approves 95% of loans, so the rule isn't too harsh. The real model knows more than the length, so it can also find safe borrowers among the longer loans.

### Step 5: What if our assumptions are wrong?

The brief asks for at least two alternative assumptions. Each row changes the cost of FN (approving someone who won't pay back) or the cost of FP (turning away someone who would pay back). The cut-off is then cost of FP ÷ (cost of FP + cost of FN).

The last column is the rough check from Step 4. Ordinary 7-day loans default 1.22% of the time. If the cut-off falls below that, NkwaPay would turn away almost everyone.

| Scenario | Country | Cost of FN | Cost of FP | Cut-off | 7-day loans |
|---|---|---|---|---|---|
| **Main** | Kenya | 4,700 | 100 | **2.08%** | approved |
| | Ghana | 2,716 | 90 | **3.21%** | approved |
| Nothing recovered (0%) | Kenya | 5,200 | 100 | 1.89% | approved |
| | Ghana | 3,016 | 90 | 2.90% | approved |
| More recovered (30%) | Kenya | 3,700 | 100 | 2.63% | approved |
| | Ghana | 2,116 | 90 | 4.08% | approved |
| Chasing costs double | Kenya | 4,900 | 100 | 2.00% | approved |
| | Ghana | 2,732 | 90 | 3.19% | approved |
| Low fee (0.7%: free loans earn nothing) | Kenya | 4,700 | 35 | 0.74% | **declined** |
| Lost repeat business | Kenya | 4,700 | 500 | **9.62%** | approved |
| | Ghana | 2,716 | 450 | **14.21%** | approved |
| Strictest (low fee + nothing recovered) | Kenya | 5,200 | 35 | 0.67% | **declined** |
| Most lenient (repeat business + 30% recovered) | Kenya | 3,700 | 500 | 11.90% | approved |
| | Ghana | 2,116 | 450 | 17.54% | approved |

**What this means:**
1. **Our guesses about bad loans hardly matter.** Recovery from 0% to 30%, or double the chasing cost, keeps the cut-off at 1.9–2.6% (Kenya) and 2.9–4.1% (Ghana). Every one of those still approves ordinary loans.
2. **The fee matters a lot.** At 0.7%, NkwaPay would decline almost everyone. No real lender works like that, which supports 2.0% as the main fee.
3. **Repeat customers matter most.** Counting their future fees raises the cut-off to about 10% (Kenya) and 14% (Ghana).
4. **So the biggest open question isn't what a bad loan costs. It's what a good customer is worth over time.**

## Decision

| | Kenya | Ghana |
|---|---|---|
| Typical loan | 5,000 KES, 7 days | 3,000 GHS, 7 days |
| Fee | 2.0% = 100 KES | 3.0% = 90 GHS |
| **Cost of FN** (approve someone who won't pay back) | **4,700 KES** | **2,716 GHS** |
| **Cost of FP** (turn away someone who would pay back) | **100 KES** | **90 GHS** |
| Break-even | 1 bad borrower in 48 | 1 bad borrower in 31 |
| **Decline if the chance of default is above** | **2.1%** | **3.2%** |
| Range under other recovery / chasing guesses | 1.9%–2.6% | 2.9%–4.1% |
| Most important alternative (lost repeat business) | 9.6% | 14.2% |

**Why the simple version (one lost fee) is the main one:** it's what the brief's example uses, and it rests on fewer guesses. The repeat-business version is fuller, but it needs a guess about how many declined customers leave. So we report it alongside, and the committee can choose.

## What I'm unsure of / limits

- **Recovery (10%) and collection cost ($1.50) are our own estimates**, not from the data or a published source. Step 5 shows they barely move the answer, but real NkwaPay figures should replace them.
- **The free Kenyan loans:** we don't know how NkwaPay earns on them. If they really earn nothing, the Kenyan cut-off is far too high.
- **Currencies are assumed** (KES and GHS). If Ghana's amounts aren't in cedis, the Ghanaian money figures change, but the cut-off barely does, because it depends mostly on percentages.
- **Repeat business:** "half of declined customers leave" is a guess. The 8 future loans only counts loans inside the data window, so it may be an underestimate.
- **Ghana's repeat behaviour** is assumed to match Kenya's, since Ghana's repayment outcomes aren't in the data (Ghanaian borrowers do have a median of 5 earlier loans, so how often they return could be checked).
- **The cut-off assumes calibrated probabilities.** If Germain's model isn't calibrated, 2.1% means nothing.

## Likely Q&A questions and answers

**Q: Why is the cost of FN (approving someone who won't pay back) so much bigger than the cost of FP (turning away someone who would pay back)?**
A: When someone doesn't pay, NkwaPay loses most of the money it lent (5,000 KES, minus about 10% recovered, plus chasing costs). When it turns away a good borrower, it only loses the fee on that loan, which is about 2% of the loan (100 KES).

**Q: Where does 2.1% come from?**
A: One bad loan (4,700 KES) wipes out the fees of 47 good loans (100 KES each). So NkwaPay breaks even when 1 in 48 borrowers doesn't pay back, and 1 ÷ 48 = 2.1%. The formula is cost of FP ÷ (cost of FP + cost of FN) = 100 ÷ 4,800.

**Q: Your recovery and collection numbers are guesses. Doesn't that make the result unreliable?**
A: We tested them. Recovery from 0% to 30%, and double the chasing cost, only move the cut-off between 1.9% and 2.6%. The result is safe against those guesses. What does move it a lot is the fee and the value of repeat customers, and we report both.

**Q: Why use a 2.0% fee when the middle Kenyan fee is 0.7%?**
A: Over a third of 7-day loans show no fee, which a real lender wouldn't do. The fee was probably collected another way. Among loans that do charge a fee, the middle is 2.0%. At 0.7%, the rule would decline almost every applicant, which no real lender would do.

**Q: Isn't 2% a week very expensive for borrowers?**
A: Yes. Repeated weekly, it's about 104% a year. That's a fairness and regulation question we come back to with the Bank of Ghana Directive.
