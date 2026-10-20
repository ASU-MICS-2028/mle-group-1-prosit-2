# 03 · Feature audit (Liza)

Notebook with all the code: [`notebooks/00_feature_audit.ipynb`](../notebooks/00_feature_audit.ipynb).
It runs top to bottom in about a minute. You don't need to run it: every result is pasted below.

## What the team needs to know

1. **The models may use only these columns:** `loan_type`, `duration`, `New_versus_Repeat`, and the month, day of the week and day of the month taken from `disbursement_date`. Nothing else from Train.csv.
2. **The answers the models learn to predict:** Task 1 (how much to lend) = `Total_Amount`. Task 2 (will they pay back) = `target`. The brief calls these `IsDefaulted` and `ProductCategory`, but those names don't exist in the data. They are `target` and `loan_type`.
3. **`Total_Amount_to_Repay` cheats.** Penalties were added to it *after* people failed to pay. Never use it. Also never use `Lender_portion_to_be_repaid` (built from it) or the "price" (repay ÷ amount).
4. **How much cheating would have faked our results:** the default score (PR-AUC, explained below) jumps from **0.20 to 0.91** when the cheating columns are included. Use this number in the report.
5. **Leave out 190 loans that weren't due yet** when the data was collected. Their "paid" label isn't real yet.
6. **`lender_id` and `loan_type` give away the country perfectly.** Also, most Ghanaian loans use lenders and loan types that never appear in the Kenyan data. Alice: the Ghana study must decide how to handle these unseen values.
7. **`lender_id` is not a clue for the model** (it adds nothing). But it **is** one of the groups for the fairness checks, along with `country_id`, `loan_type`, `New_versus_Repeat` and loan size.
8. **Predicting the loan amount is hard** with these columns: only slightly better than guessing the average. Borrower history (step 5) should help most.
9. **Joseph, for borrower history:** you only find out whether a past loan was repaid after its `due_date`. So "past default rate" should only count earlier loans whose `due_date` is before the current loan's `disbursement_date`. Also, rows with the same `tbl_loan_id` are one loan split between lenders, not separate past loans.
10. **On a Mac,** LightGBM needs `brew install libomp`.

## The question

The spreadsheet of past loans (`Train.csv`) has 16 columns. For each one we had to decide: **is the model allowed to look at it when deciding on a loan?**

The danger is **leakage**: a column that was filled in *after* the loan was given, so it secretly contains the answer.

Think of a student who saw the answer sheet before a practice exam. They score 100%, then fail the real exam. A model trained with a leaky column is the same: it looks brilliant in testing, then fails in real use, because on decision day that value doesn't exist yet.

The brief (Part A.1) asks for three things. Here is where each one is in this file:

| The brief asks for | Where it is |
|---|---|
| **a.** A timeline of a loan, showing when NkwaPay decides | [Step 2](#step-2-the-timeline-brief-a1a) |
| **b.** A definition of "default" | [Step 3](#step-3-what-default-means-brief-a1b) |
| **c.** A table of all 16 columns: known at decision time (yes/no), role (feature, target or dropped), and a one-line reason | [Decision](#the-feature-audit-table-brief-a1c) |

## Words used in this file

- **Feature:** a column the model uses as a clue.
- **Target** (or **label**): the answer the model learns to predict.
- **Default:** the customer didn't pay back.
- **Decision moment:** the point when NkwaPay says yes or no to a loan.
- **Proxy:** a column that quietly stands in for something else. For example, the bus route a student takes can give away which neighbourhood they live in.
- **Baseline:** the simplest possible guess, such as "guess the same for everyone". A useful model must beat it.
- **ROC-AUC:** a score for how well something separates two groups (e.g. payers and non-payers). 0.5 = a coin flip, 1.0 = perfect.
- **PR-AUC:** a score for how well the model finds the rare defaulters. Random guessing scores 0.018 (because 1.8% of loans default), and 1.0 is perfect. This is the main score the brief asks for, because defaulters are so rare.
- **Grouped by customer:** when testing, all of one customer's loans go either in the learning part or in the testing part, never both. Customers take about 10 loans each, so otherwise the model could "recognise" a customer instead of learning anything general.
- **Log:** a way of shrinking big numbers so huge values don't dominate. For example, the log turns 100, 1,000 and 10,000 into evenly spaced steps.

## What I did

1. **Looked at every column:** its meaning, how many different values it has, and its smallest and largest values.
2. **Drew the timeline** and checked that the dates add up.
3. **Defined "default"** and checked whether every loan's answer was actually known.
4. **Maths check:** is a column just a calculation from other columns?
5. **Defaulters vs repayers:** do people who didn't pay have values that could only exist after the fact?
6. **One column at a time:** how well does each column *alone* predict default? A column that's almost perfect is suspicious.
7. **Country check:** could a column secretly reveal the country (Ghana vs Kenya)?
8. **Built the real model with different sets of columns** and compared the scores, including one set that deliberately cheats.

## What I tried and what happened

### Step 1: The columns

There are 68,654 loans from 6,540 customers, with no empty cells. All are from Kenya. 1,258 loans (1.83%, about 2 in 100) were not paid back.

Some things looked odd at first, and the later steps explain them:
- `Total_Amount_to_Repay` can be 0.
- `Lender_portion_Funded` (a percentage) goes up to 117%.
- Some loans last 3 years.
- Amounts range from 2 to 23 million.

`customer_id`, `lender_id` and `tbl_loan_id` contain only digits, but they are **name tags, not amounts**. Customer 300,000 isn't "bigger" than customer 145.

### Step 2: The timeline (brief A.1a)

```
 1. Customer   2. NkwaPay   3. Money sent           4. Due date     5. Outcome
    applies ──►  decides ──►  (disbursement_date) ──► (due_date) ──► repaid (target=0)
                    ▲                                                or not (target=1)
           THE DECISION MOMENT
```

NkwaPay decides just before the money is sent. The data has no "application date" or "approval date", so the closest column is **`disbursement_date`** (the day the money was sent).

**The question for every column: would NkwaPay know this value on that day?**

**Check:** on **100%** of loans, `due_date` = `disbursement_date` + `duration`. For example, money sent on 1 March for a 7-day loan is due on 8 March. So the due date is fixed on day 1 and is safe, but it only repeats the other two columns.

### Step 3: What "default" means (brief A.1b)

**Definition:**
- `target` = 1 (default): the customer didn't repay as agreed, as recorded when the data was collected. That was around 14 November 2024, the last date a loan was sent.
- `target` = 0: they repaid, or hadn't failed to repay by then.
- **The period:** from the day the money is sent until the data was collected.

**A problem I found:** 190 loans weren't due until after 14 November 2024, some as late as October 2025. **All 190 are marked "paid".**

Based on similar loans that *were* due, we'd expect about **5** of them to be unpaid. So their "paid" really means "not unpaid *yet*". It's like a teacher marking exams before some students have finished.

**These 190 loans are left out of training.**

Two more facts found here:

| Loan length | Share of all loans | Share not paid back |
|---|---|---|
| 1–7 days | 94.7% | 1.2% (about 1 in 80) |
| 8–14 days | 2.3% | 8.2% |
| 15–30 days | 1.7% | 13.3% |
| 31–90 days | 1.1% | 15.9% |
| over 90 days | 0.2% | 44.7% (nearly 1 in 2) |

- **Longer loans go unpaid much more often**, so `duration` is a strong clue.
- **The share of unpaid loans changes a lot over time.** 63,000 of the 68,654 loans were sent in July–December 2022, and only about 1% of those went unpaid. The other periods have only a few hundred loans each, with 5–15% unpaid. This matters for Joseph's "learn from older loans, test on newer ones" check.

### Step 4: Maths check (is a column just a calculation?)

| Formula | Loans where it's true |
|---|---|
| `due_date` = `disbursement_date` + `duration` | 100% |
| `ID` = "ID_" + customer number + loan number + lender number, glued together | 100% |
| `Lender_portion_Funded` = `Amount_Funded_By_Lender` ÷ `Total_Amount` | 100% |
| `Lender_portion_to_be_repaid` = this lender's share of `Total_Amount_to_Repay` (e.g. a lender who funded 30% of the loan is owed 30% of the repay amount) | 96.2% |

**What this means:**
- `due_date`, `ID` and `Lender_portion_Funded` tell us nothing new.
- The two lender-funding columns are calculated from the loan amount, which is the Task 1 answer.
- `Lender_portion_to_be_repaid` is calculated from the repay amount.

### Step 5: Defaulters vs repayers (the big finding)

The **price** of a loan = what you must repay ÷ what you borrowed. A price of 1.10 means you pay back 10% extra.

I compared people who took the **exact same kind of loan**: Type_1, 7 days, same lender. That's 61,723 loans, about 90% of all loans.

| | Loans | Middle price (half pay more, half pay less) | Share who pay back exactly what they borrowed |
|---|---|---|---|
| Paid back | 61,203 | 1.007 (about 1% extra) | 39% |
| Didn't pay back | 520 | 1.412 (about 41% extra) | 0.2% |

Price alone picks out the defaulters almost perfectly (ROC-AUC **0.991**).

**What this means:** these people got the same product from the same lender, so on day 1 their prices should be similar. The only sensible explanation is that **late fees and penalties were added after they failed to pay.** So `Total_Amount_to_Repay` was updated after the loan went wrong. It's the answer sheet in disguise.

**A second, weaker clue:** in 12.6% of repaid loans, the lender put in nothing (`Amount_Funded_By_Lender` = 0). This never happens for unpaid loans. It's suspicious, but it isn't proof.

### Step 6: One column at a time

**The question:** if this column were all you knew, how well could you guess who won't pay?

**How:**
1. Split the loans into 5 parts, grouped by customer.
2. Learn from 4 parts what share of loans went unpaid for each value of the column. (Numbers are first sorted into 20 bands, e.g. the smallest 5% of amounts, the next 5%, and so on.)
3. Use those shares to guess on the 5th, hidden part.
4. Repeat so each part is hidden once.

Above about 0.9 ROC-AUC is a red flag.

| Column | ROC-AUC | PR-AUC |
|---|---|---|
| price (repay ÷ amount) | **0.971** 🚩 | 0.308 |
| `Lender_portion_Funded` | 0.745 | 0.065 |
| `loan_type` | 0.745 | 0.159 |
| `due_date` | 0.732 | 0.059 |
| `disbursement_date` | 0.731 | 0.058 |
| `Lender_portion_to_be_repaid` | 0.710 | 0.045 |
| `Amount_Funded_By_Lender` | 0.690 | 0.042 |
| `Total_Amount_to_Repay` | 0.669 | 0.040 |
| `Total_Amount` | 0.660 | 0.037 |
| `lender_id` | 0.655 | 0.096 |
| `duration` | 0.653 | 0.072 |
| `New_versus_Repeat` | 0.537 | 0.037 |
| `ID`, `customer_id`, `country_id`, `tbl_loan_id` | 0.492 | 0.018 |

**What this means:**
- **Only price is a red flag**, which confirms Step 5.
- **An important lesson:** `Total_Amount_to_Repay` on its own scores only 0.67, yet it *is* the leak. The penalties only show up once you divide by the loan amount, because big loans always owe big amounts. So this test alone would have missed the leak. That's why we used several different tests.
- **The dates score fairly well (0.73)**, but this isn't a leak. The unpaid share changed over time (Step 3), so *when* a loan was sent tells you something.
- **Name tags and country are a coin flip (0.49).** The hidden part only contains customers the test has never seen, and every row says "Kenya".

### Step 7: Country check (does a column give away Ghana vs Kenya?)

This uses `Test.csv`, which has both countries: 3,525 of its 18,594 loans are from Ghana. It's the same one-column test as Step 6, but now the thing being guessed is "is this loan from Ghana?". 1.0 means the column reveals the country perfectly.

| Column | ROC-AUC (Ghana vs Kenya) |
|---|---|
| `loan_type`, `lender_id` | **1.000** |
| `Lender_portion_Funded` | 0.940 |
| `Lender_portion_to_be_repaid` | 0.786 |
| `Amount_Funded_By_Lender` | 0.784 |
| `due_date`, `disbursement_date` | 0.772, 0.755 |
| `Total_Amount_to_Repay`, `Total_Amount` | 0.742, 0.736 |
| `duration` | 0.550 |
| `New_versus_Repeat` | 0.493 |

**Unseen values:**
- Ghana uses 5 lenders. Only 1 of them appears in the Kenyan training data, and it covers just 116 of the 3,525 Ghanaian loans.
- Ghana uses 3 loan types. Only 1 appears in training (`Type_2`), and it covers 449 Ghanaian loans.

**What this means:**
- `loan_type` and `lender_id` are perfect proxies for country.
- For most Ghanaian loans, the model has learned nothing about their lender or loan type. It's like learning to judge Kenyan football teams, then being asked about Ghanaian teams you've never heard of.
- The money columns and dates differ partly because amounts are in different currencies (cedis vs shillings) and the loans were sent at different times.
- `duration` and `New_versus_Repeat` look the same in both countries, so they should carry over to Ghana most safely.

### Step 8: Building the model with different sets of columns

**The question:** for the columns we weren't sure about, how much do they actually add? We measured instead of guessing.

**The sets of columns.** "F0" is our name for the safe starting set. "Calendar parts" means the month, day of the week and day of the month from `disbursement_date`.

| Set | What's in it |
|---|---|
| F0 | `loan_type`, `lender_id`, `duration`, `New_versus_Repeat`, calendar parts |
| F0 without `lender_id` | the same, minus `lender_id` |
| F0 without `lender_id` and `loan_type` | only the clues that look the same in both countries |
| F0 + loan amount | adds `Total_Amount` |
| F0 + loan amount + lender funding | adds the two lender-funding columns too |
| Everything | every column except name tags, **including the cheating ones**. Only for comparison, never used for real. |

**Two models:**
- **Logistic regression:** simple and explainable. It adds up a score from each clue. It was told to pay extra attention to the rare defaulters.
- **LightGBM:** more powerful. It builds many small decision trees ("if the loan is over 30 days, then...").

Both were tested grouped by customer.

**Task 2: will they pay back?** Each cell shows PR-AUC / ROC-AUC. Higher is better.

| Set of columns | Logistic regression | LightGBM |
|---|---|---|
| F0 | 0.200 / 0.794 | 0.170 / 0.773 |
| **F0 without `lender_id` (the chosen set)** | **0.199 / 0.795** | 0.169 / 0.775 |
| F0 without `lender_id` and `loan_type` | 0.151 / 0.728 | 0.148 / 0.756 |
| F0 + loan amount | 0.200 / 0.797 | 0.168 / 0.796 |
| F0 + loan amount + lender funding | 0.201 / 0.818 | 0.166 / 0.815 |
| **Everything, including the cheating columns** | **0.749 / 0.990** | **0.913 / 0.995** |
| Baseline: same guess for everyone | 0.018 / 0.500 | |

**Task 1: how much to lend?** The score is the average error on the log of the amount. Lower is better.

An error of 0.91 means a typical guess is off by a factor of about 2.5. For example, if the real loan was 5,000, a typical guess would be around 2,000 or 12,500.

| Set of columns | Linear regression | LightGBM |
|---|---|---|
| F0 | 0.911 | 0.910 |
| **F0 without `lender_id` (the chosen set)** | **0.911** | 0.910 |
| F0 without `lender_id` and `loan_type` | 0.923 | 0.913 |
| F0 + lender funding (cheats for Task 1) | 0.631 | **0.141** |
| Baseline: guess the average for everyone | 0.977 | |

**What this means:**
1. **Cheating columns fake the results enormously.** The default score goes from 0.20 to 0.91, and the amount error drops from 0.91 to 0.14. Both look impressive, and both would fail in real use.
2. **`lender_id` adds nothing** (PR-AUC 0.200 with it, 0.199 without).
3. **`loan_type` helps** (PR-AUC 0.20 with it, 0.15 without).
4. **The loan amount and the lender-funding columns add nothing honest to Task 2.** For Task 1, the funding columns just let the model work the amount back out, because funding = share × amount.
5. **The simple model does as well as the powerful one, or better.** As the brief predicts, choosing columns carefully matters more than a fancy model.
6. **Every honest set beats the baseline easily for default** (0.15–0.20 vs 0.018), so the clues carry real information. For the amount, the gain over guessing is small (0.91 vs 0.98).

## Decision

### The feature audit table (brief A.1c)

"Dropped" means *not given to the model as a clue*. The column can still be kept in the data for other jobs, like labelling rows or fairness checks.

| Column | Known at decision time? | Role | Reason |
|---|---|---|---|
| `ID` | yes | dropped | Customer + loan + lender glued together. Different on every row, so there's no pattern to learn. Kept only to match predictions to loans for Zindi. |
| `customer_id` | yes | dropped | A name tag (a coin flip on its own). Used to keep each customer together when testing, and to build borrower history. |
| `country_id` | yes | dropped | Kenya on every training row, so there's nothing to learn. Kept for fairness checks. |
| `tbl_loan_id` | yes | dropped | A name tag. Used to group the rows of one loan shared between lenders. |
| `lender_id` | yes | dropped | Adds nothing (PR-AUC 0.200 with, 0.199 without) and reveals the country. Kept for fairness checks. |
| `loan_type` | yes | **feature** | Chosen when applying. The strongest safe clue (PR-AUC 0.20 with, 0.15 without). It reveals the country, so it's checked for fairness. |
| `Total_Amount` | yes | **target (Task 1)** | The amount to predict. Not a Task 2 clue: it adds nothing there, and both tasks must use the same clues. |
| `Total_Amount_to_Repay` | **no** | dropped (**leak**) | Penalties added after default. On the same loan, repayers owe about 1% extra and defaulters about 41%. |
| `disbursement_date` | yes | **feature** (calendar parts) | It *is* the decision day. Used as month, day of week and day of month. Not the year, because the model will always meet future years. |
| `due_date` | yes | dropped | Always send date + duration, so it adds nothing new. |
| `duration` | yes | **feature** | Agreed before the money is sent. Longer loans default far more. Same in both countries. |
| `New_versus_Repeat` | yes | **feature** | NkwaPay knows whether someone has borrowed before. Same in both countries. Also a fairness group. |
| `Amount_Funded_By_Lender` | yes | dropped | Calculated from the amount, so it leaks the Task 1 answer (error 0.91 → 0.14). Adds nothing to Task 2. |
| `Lender_portion_Funded` | yes | dropped | Exactly funded ÷ amount, so it has the same problem. |
| `Lender_portion_to_be_repaid` | **no** | dropped (**leak**) | This lender's share of `Total_Amount_to_Repay`, so it carries the same penalties. |
| `target` | **no** | **target (Task 2)** | 1 = didn't repay. The 190 loans not yet due are left out of training. |

### The tricky decisions, explained

Some columns weren't obvious, so we tested both options. Here is what we asked, what we decided, and why.

| The question | Our answer | Why |
|---|---|---|
| Should the model use `lender_id`? | **No** | The score is the same with or without it (0.200 vs 0.199). It also gives away the country. So it brings risk and no benefit. |
| Should the model use `loan_type`? | **Yes** | It clearly helps: the score drops from 0.20 to 0.15 without it. It also gives away the country, so we check it in the fairness work. |
| Should the default model (Task 2) use the loan amount? | **No** | It doesn't improve the score (0.200 either way). And the brief asks for the same clues in both tasks, while the amount is the *answer* in Task 1. |
| Should the model use the two lender-funding columns? | **No** | They're calculated from the loan amount, so they give away the Task 1 answer. They don't help Task 2. |
| Should we keep the 190 loans that weren't due yet? | **No, leave them out** | Their "paid" label isn't real yet. Nobody knew whether they'd be paid. |
| Should the model use the year? | **No** | The model will be used on future years it has never seen, so what it learns about past years won't apply. |

## What I'm unsure of / limits

- **Grace period:** Zindi doesn't say how many days after the due date a loan counts as unpaid.
- **Data collection date:** I *worked out* about 14 November 2024 from the last loan date. Zindi doesn't say.
- **The lender-funding columns:** the "never 0 for defaulters" pattern might mean they were also changed after the loan. I couldn't prove it. They're dropped anyway, for a different reason (they leak the amount).
- **Small groups:** only 567 "New" (first-time) loans in training, so any result about first-time borrowers is shaky.
- **Ghana:** `loan_type` helps in Kenya, but most Ghanaian loan types are unseen, so its help may not carry over.
- **This was run without borrower history.** Once Joseph adds history and economic features (step 5), this comparison should be run again.

## Likely Q&A questions and answers

**Q: How do you know `Total_Amount_to_Repay` is a leak, not just riskier people being charged more?**
A: Risk-based pricing would differ between products or customers, not by outcome on the *same* product from the *same* lender. On Type_1 7-day loans from one lender, repayers pay about 1% extra and defaulters about 41%. Price alone separates them with ROC-AUC 0.99. No price set on day 1 can predict the future that well.

**Q: How much would the leak have inflated your results?**
A: PR-AUC from about 0.20 to 0.91 for default, and the amount error from 0.91 to 0.14.

**Q: `lender_id` and `loan_type` both reveal the country. Why drop one and keep the other?**
A: The brief doesn't forbid proxies; it asks us to find them and check them for fairness. `lender_id` added nothing, so it was all risk and no gain. `loan_type` raised PR-AUC from 0.15 to 0.20, so we keep it and check it in the fairness audit.

**Q: Why test grouped by customer?**
A: Customers take about 10 loans each. If the same customer appeared in both learning and testing, the model could "recognise" them and look better than it really is on new customers.

**Q: Why leave out 190 loans?**
A: They weren't due yet when the data was collected. All 190 are marked "paid", when about 5 would be expected to be unpaid. Their answer simply isn't known yet.

**Q: Why did the simple model do as well as the powerful one?**
A: With only a few safe columns, there isn't much complex pattern for LightGBM to find, so logistic regression scored as well or better (PR-AUC 0.20 vs 0.17). The final model choice is Germain's step (7), but this supports the committee's preference for a simple, explainable model.
