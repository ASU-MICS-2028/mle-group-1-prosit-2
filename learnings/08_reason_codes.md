# 08 · Reason codes (Joseph, taking over from Germain)

## What the others need to know
- **Every declined applicant gets 1–3 plain reasons**, worded with their own numbers. Example: "You took no loans in the last 7 days; regular borrowers have repaid more reliably." The code is `src/reasons.py`, which the scorer (step 12) calls.
- **How it works:** our model adds up points. Each clue pushes the risk up or down by *weight × how far you are from the average applicant*. The themes that push your risk up the most are your reasons.
- **This is exactly SHAP** (the standard explanation method). We checked: the two match to 16 decimal places.
- **Reasons are given per theme, not per clue,** because clues that move together cancel each other out. There are 5 themes: borrowing history, loan product, loan length, loan sizes, repayment record.
- **A reason is only shown if it matters:** it must raise the odds of default by at least about 22%. With that rule, the same person gets the same reasons in 94% of refits of the model.
- **Bug found and fixed in step 7's saved model:** it was calibrated on 2024 loans only, so it turned away 89% of Kenyan applicants. Fixed, it turns away 19% (it approves 85% of 2022 loans, whose real default rate is 1.3%).
- **Plain logistic regression already gives honest chances.** Platt calibration changes almost nothing (slope 0.99).
- **For Liza (fairness):** the most common reason is "you haven't borrowed recently". The model rewards frequent borrowing. That could push people to borrow more just to get approved, which is a responsible-lending question.
- **For Alice (transfer):** 47% of Ghanaian test applicants are declined, against 19% of Kenyans. Their most common reasons are borrowing history, loan length, and "we have no record for this kind of loan" (`Type_3`).

## The question
When NkwaPay says no, it must say why, in words a borrower understands. The brief asks for the **top 3 reasons** behind each decision. The reasons must be **true to the model** (the actual drivers of the score), **stable** (the same person shouldn't get different reasons from a slightly different model), and **understandable**.

## What I did
1. **Fixed the saved model first** (section 0 of the notebook), because explaining a broken model would be pointless.
2. Wrote `src/reasons.py`: it works out each applicant's pushes and turns the strongest into sentences.
3. Explained every declined Zindi test applicant (2.1% cut-off in Kenya, 3.2% in Ghana): 2,894 Kenyans and 1,672 Ghanaians, of whom 2,033 were first-timers.
4. Tested every choice along the way: the method, who the reference applicant is, how to group clues, how strong a reason must be, stability, which groups get which reasons, and the wording.

Notebook: `notebooks/02b_reason_codes.ipynb` (about 2 minutes). Tables: `learnings/tables/08_*.csv`.

**Words used:**
- **Push:** how much one clue raises (or lowers) your risk compared with the reference applicant, measured in log-odds. A push of 0.2 multiplies your odds of default by about 1.22.
- **Reference applicant:** the person you are compared with.
- **SHAP:** a standard method that splits a prediction into one share per clue.
- **Theme:** a group of clues that belong together.

## What I tried and what happened

### 0. The saved model was calibrated on the wrong loans
Step 7 calibrated the final model on the newest 20% of *dates*. On the full data that's May–Nov 2024 only: 2,625 loans at 9% default, so the model thought every loan was a 2024 loan.

| Year | Loans | Old: predicted / approved at 2.1% | Fixed: predicted / approved | Actual default rate |
|---|---:|---|---|---:|
| 2022 | 64,402 | 4.9% / 12% | **1.3% / 85%** | 1.3% |
| 2024 | 2,784 | 9.9% / 0% | 9.5% / 0% | 9.3% |

I tested five ways to calibrate on every future-loan block:

| Option | Log loss (lower = better) | Cost per loan (KES) |
|---|---:|---:|
| Platt, random 25% of loans | 0.0785 | 47.3 |
| Platt, newest 20% of loans (by count) | 0.0791 | 47.8 |
| No calibration (plain logistic regression) | 0.0801 | 47.9 |
| **Chosen:** Platt on out-of-fold scores from 5 customer folds, all loans | 0.0799 | 47.9 |
| Platt, newest 20% of dates (step 7's way) | **0.0949** (worst) | 48.5 |

They're all within noise on cost. Step 7's way was worst on log loss, and on the full data it's the one that breaks. I chose the customer-fold version: it uses every loan, keeps one model (reason codes need that), and stays faithful to the step 7 decision of LR + Platt.

### 1. How to compute a push
| Method | Same top reason as ours | Same top 3 |
|---|---:|---:|
| SHAP, standard | 100% (identical to 16 decimals) | 100% |
| SHAP, correlation-aware (shares credit between clues that move together) | 71% | 53% |

The correlation-aware version gives much more credit to *loan product* (top reason for 41% of people, against 14% for ours). It doesn't follow the model's actual weights, it can't be checked by hand, and it's slow. Grouping into themes already deals with the clues that move together. **Kept: weight × (value − reference).**

### 2. Who is the reference applicant?
| Reference | Same top 3 as "average" | Most common top reason |
|---|---:|---|
| **Average loan** | — | borrowing history (70%) |
| Average approved loan | 98% | borrowing history (73%) |
| Best possible value of every clue | 19% | loan product (**100%**) |

"Best possible" makes *everyone's* top reason "your loan type isn't the safest type", which tells a borrower nothing. Average and approved agree almost completely. **Kept: the average loan.**

### 3. Group by clue or by theme?
The model has pairs of clues that move together but pull opposite ways. Your *last* loan's size pushes risk up and your *usual* loan's size pushes it down (0.89 correlated); past loans and finished loans are 0.97 correlated. Listed separately, a reason like "your last loan was large" is often mostly undone by its partner.

| Grouping | Reasons more than half cancelled by a partner | Same top reason after refitting | Same top 3 after refitting |
|---|---:|---:|---:|
| 13 separate clues | 8.7% | 77% | 53% |
| Themes, draft 1 (finished loans under "repayment record") | ~0% | 91% | 86% |
| **Themes, final** (finished loans under "borrowing history") | 0% | **91%** | **94%** |

(Refitting columns use the 0.2 minimum push.)

### 4. How strong must a reason be?
| Minimum push | Same top 3 after refitting (average / worst refit) | Reasons per person |
|---|---|---:|
| 0 (any push up) | 63% / 27% | 2.4 |
| 0.05 | 61% / 28% | 2.1 |
| 0.1 | 78% / 41% | 2.0 |
| **0.2** | **94% / 64%** | **1.9** |

Weak reasons flip order between refits. Dropping them makes the list much more stable and costs almost nothing: every declined person still gets at least one reason. **Kept: 0.2.**

"Refitting" means retraining the model on each future-loan block's learning data (4 refits) and on 10 resamples of customers. Then we check whether the same applicant gets the same reasons.

### 5. Who gets which reasons?
| Top reason | Kenya (2,894 declined) | Ghana (1,672) | First-timers (2,033) |
|---|---:|---:|---:|
| Borrowing history | 69% | 71% | 78% |
| Loan product | 22% | 0% | 3% |
| Loan length | 8% | 29% | 20% |
| Repayment record | 0% | 0% | 0% |

- **"You defaulted before" almost never appears** (18 times), because defaulters rarely come back to borrow (0.2% of returning borrowers have a past default).
- **Loan sizes is rarely a reason** (51 times) once its two clues are added together.

### 6. Wording
Every declined applicant gets 1–3 sentences (1,497 got 1, 2,180 got 2, 889 got 3), with no blanks. Three **made-up** applicants:

> **Kenyan repeat borrower, risk 3.8%:**
> - You took no loans in the last 7 days; regular borrowers have repaid more reliably.
> - Your most recent loan (9,000) was larger than your usual loan (3,000).
>
> **Ghanaian on an unseen loan type, risk 13.2%:**
> - The loan is for 30 days; longer loans are repaid less often.
> - You took no loans in the last 7 days; regular borrowers have repaid more reliably.
> - We have no repayment record for this kind of loan (Type_3), so we treat it with caution.
>
> **First-ever loan, risk 4.8%:**
> - This is your first loan with us, so we have no borrowing history to go on.
> - This is a first loan with this lender; first loans are repaid less often than repeat loans.

## Decision
- **Reasons:** weight × (value − average applicant), added up into 5 themes, shown only if the push is ≥ 0.2, top 3, each worded with the applicant's own numbers.
- **Final model:** LR + Platt, with Platt fitted on out-of-fold scores from all loans (replaces step 7's 2024-only calibration).

Recorded in [ADR 0017](../docs/adr/0017-reason-codes.md).

## What I'm unsure of / limits
- **The reasons describe the model, not the world.** "Regular borrowers repaid more reliably" is what the model learned from Kenya 2022. Whether it's fair to tell someone that is Liza's question.
- **Ghana's "unseen loan type" reason is partly a side effect.** The model has no weight for `Type_3`, so it scores it like a loan type with zero weight, which happens to look riskier than the common Kenyan types. How unseen types should be scored is Alice's step 10.
- **Amounts aren't in a currency.** The sentences show the number as it appears in the data (KES or GHS). The scorer should add the currency.
- **Stability is 94% on average but 64% for the worst refit,** which used only the first time block (little data).

## Likely Q&A questions and answers
**How do you know the reasons are faithful to the model?** For logistic regression the pushes add up *exactly* to the score. The self-check in `src/reasons.py` tests this, and they match SHAP to 16 decimals.

**Why not use SHAP?** We do, in effect: for a linear model our method *is* standard SHAP. The correlation-aware version spreads credit between linked clues, but grouping into themes does that more simply.

**Why only reasons that raise risk?** A declined borrower needs to know what counted against them. What helped them doesn't explain a "no".

**Why might someone get only one reason?** Because their other themes barely matter (push under 0.2). Listing weak reasons would make the list change every time the model is retrained.

**Isn't "borrow more often" a bad message?** It's honestly what the model learned, and it's a fair concern. We flag it for the fairness and regulation review (step 11) rather than hiding it.
