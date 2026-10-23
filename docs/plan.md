# The plan

*The plan and the progress tracker live here, in the repo. This replaces the old Google Doc, which is no longer used. The README's **Now** box shows only the current step.*

**Due:** debrief and full portfolio on **Tue 3 Nov 2026**.

## Progress tracker

Work top to bottom. A step can only start when the steps it waits on are ticked. Tick yours (`[x]`) and push when done.

| # | Step | Who | Waits on | Due |
|---|---|---|---|---|
| 1 | [x] Download the Zindi data into `data/zindi/` | Joseph | — | Tue 20 Oct |
| 2 | [x] Register for and download Findex Ghana into `data/worldbank/` | Joseph | — | Tue 20 Oct |
| 3 | [x] Feature audit: every column in Train.csv marked allowed or not, with evidence ([guide](02_feature_audit_guide.md)) | Liza | 1 | Wed 21 Oct |
| 4 | [x] Cost matrix in cedis and shillings → the decline threshold | Liza | 1 | Tue 20 Oct |
| 5 | [ ] Shared features and fair tests in `src/` ([progress](../README.md#current-step-in-detail-5--features-and-fair-tests-joseph)) | Joseph | 3 | Fri 23 Oct |
| 6 | [ ] Provisional model (plain logistic regression) so others can start building | Germain | 5 | Sat 24 Oct |
| 7 | [ ] Task 2: final classification model, threshold, saved predictions | Germain | 4, 5 | Tue 27 Oct |
| 7b | [ ] Zindi late submission of the final model (still scored, 10/day max); log every score in 02 | Germain | 7 | Tue 27 Oct |
| 8 | [ ] Reason codes (top 3 reasons per decision) | Germain | 7 | Tue 27 Oct |
| 9 | [ ] Task 1: loan-amount model | Alice | 5 | Tue 27 Oct |
| 10 | [ ] Kenya → Ghana transfer study, domain classifier | Alice | 5 | Thu 29 Oct |
| 11 | [ ] Fairness metrics, proxy analysis, mitigation, Model Card | Liza | 7, 9, 10 | Thu 29 Oct |
| 12 | [ ] Scoring service | Joseph | 7, 8, 9 | Sat 31 Oct |
| 13 | [ ] Report, slides, reflections | Everyone | all above | Mon 2 Nov |

When you finish a step: tick it here, update the **Now** box at the top of the README to the next step and its owner, add your `learnings/` write-up, and log it.


## 1. The rules for everyone

They're in [`AGENTS.md`](../AGENTS.md) (for people and AI agents alike). In short: one step at a time, explained; test every diverging path; decisions in [`adr/`](adr/README.md); learnings in plain words; the README shows only the current step; log actions and AI use; never paste raw data into AI tools.

## 2. What we're asked to do

NkwaPay lends small amounts by mobile money. It has years of labelled loans from **Kenya** (paid back or not) and is starting in **Ghana**, where it has none. Only about **1 in 50** loans goes unpaid. It wants **one tool** that:

1. gives each applicant a **chance of default** (Task 2, classification);
2. suggests a **loan amount** (Task 1, regression), using the same clues;
3. is **fair and explainable**: plain reasons for each decision, no group unfairly shut out;
4. is **honest about uncertainty**, because it's trained on Kenya and used in Ghana;
5. **follows Ghanaian law:** the BoG Digital Credit Directive, Act 843 (data protection) and Act 726 (credit reporting).

The committee prefers a **simple model it can explain** to a slightly more accurate black box.

| Criterion | Points | Main owner |
|---|---|---|
| A. Framing and cost matrix | 10 | Liza |
| B. Modelling and pipeline (≥5 models, ≥2 derivations, time-safe features) | 30 | Joseph, Germain, Alice |
| C. Evaluation (PR-AUC, calibration, 3 kinds of test, noise floor) | 20 | Germain, Joseph |
| D. Ethics and regulation audit | 20 | Liza, Alice |
| E. Scorer and presentation | 15 | Joseph, everyone |
| F. Process and individual reflection | 5 | Everyone |

**Deliverables:**
- **Group:** GitHub repo (README + data code + notebooks `01_eda`, `02_classification`, `03_regression`, `04_transfer_and_fairness`), technical report (6–10 pages), ethics and regulation audit, scoring service + borrower explainer, debrief slides (15 min).
- **Individual:** a one-page reflection each.

The full brief is in [`knowledge/prosit2_brief.md`](../knowledge/prosit2_brief.md).

## 3. Roles

| Member | Owns | Brief parts | Derivation | Presents |
|---|---|---|---|---|
| **Liza** | Framing (timeline, label, feature audit, cost matrix), fairness, Model Card, compliance, Findex, borrower explainer. **Report editor.** | A, D | Writes the ethics section | Opening, costs, fairness and compliance, close |
| **Joseph** | Repo, shared feature code (`src/`), the three kinds of test, `01_eda`, scoring service | B1–B3, E | Reviews all derivations | Pipeline, how leaky testing inflates scores, live scorer demo |
| **Germain** | `02_classification`: ≥5 models, calibration, threshold, bootstrap, reason codes, Zindi submissions | B4–B7 (Task 2) | Logistic regression + gradient boosting | Model results, noise floor, why a simple model |
| **Alice** | `03_regression`, Kenya → Ghana transfer study | B (Task 1), C | Linear regression | Loan amounts and the transfer study |

## 4. Who waits on whom

```
Data ──► Feature audit + cost matrix (Liza) ✅
               │                  │
               ▼                  │
     Shared features + folds      │
          (Joseph, step 5)        │
   ┌───────────┼──────────┐       │
   ▼           ▼          ▼       ▼
 Regression  Transfer   Classification ◄── cost matrix gives its cut-off
 (Alice)     (Alice)    (Germain)
   │           │          ├──► chosen model + saved predictions
   │           │          ├──► reason codes
   ▼           ▼          ▼
 loan limits  proxies    Fairness (Liza) · Scorer (Joseph) · Model Card
   └───────────┴──────────┴──► Report + slides (everyone)
```

- **Germain hands over a provisional logistic model** (step 6) as soon as step 5 lands, so the fairness and scorer work can start before the final model exists.
- **While waiting:** Germain and Alice do their derivations; Liza does Findex, the regulation reading and the Model Card skeleton; Joseph does the scorer interface.

## 5. Timeline

| Phase | Dates | Done when |
|---|---|---|
| 0. Setup | 18–20 Oct | ✅ Repo, data, Findex, `knowledge/`, `docs/`, `learnings/` |
| 1. Framing | by 21 Oct | ✅ Feature audit and cost matrix (Liza) |
| 2. Data foundation | by **Fri 23 Oct** | Step 5: history, calendar and macro clues, folds, first comparison (Joseph) |
| 3. Modelling | 24–27 Oct | Steps 6–9: provisional model Sat 24; final models, threshold, reason codes, saved predictions Tue 27 |
| 4. Transfer and audit | 27–29 Oct | Steps 10–11: shift study, fairness, Model Card, compliance, Findex |
| 5. Ship | 29–31 Oct | Step 12: scorer working; report and audit complete. **Code freeze Sat 31.** |
| 6. Defend | 1–2 Nov | Slides, 2 rehearsals, Q&A drill (everyone answers on parts they didn't build), reflections, AI declaration |

## 6. What we've learned so far (shapes the rest of the plan)

From [`docs/01_data.md`](01_data.md), [`learnings/03`](../learnings/03_feature_audit.md), [`learnings/04`](../learnings/04_cost_matrix.md) and step 5 so far:

1. **`Total_Amount_to_Repay` cheats.** Penalties are added after a default. With the cheating columns, PR-AUC jumps from 0.20 to 0.91.
2. **Allowed columns:** `loan_type`, `duration`, `New_versus_Repeat`, calendar parts. Plus borrower history from step 5.
3. **Cut-off:** decline above **2.1% (Kenya)** / **3.2% (Ghana)**, on *calibrated* probabilities.
4. **Experience is the strongest clue:** the number of previous loans alone scores ROC-AUC 0.76. A customer's first loan defaults 6.1% of the time, later ones 1.1%.
5. **Defaulters get cut off.** Only 12% of defaulters ever borrow again, so "past default rate" is almost always 0 or unknown. Our data only contains people the lender kept lending to (**selection bias**), which must be stated as a limit.
6. **No Ghanaian applicant has any history** in the data, so the model sees all of Ghana as first-timers. This is a key fairness issue.
7. **`loan_type` and `lender_id` perfectly reveal the country**, and most Ghanaian loan types and lenders never appear in training.
8. **Macro clues are the year in disguise** (4 values in training), and Ghana's inflation (10–31%) is far outside Kenya's (5–8%). Default: left out, but tested.
9. **Time matters.** 92% of loans are from Jul–Dec 2022 at about 1% default; everything else runs at 5–15%. The older-vs-newer test will be hard, and calendar clues may only be standing in for the period.
10. **Amounts:** Ghana's typical loan is about 7× Kenya's in dollars, if the currencies are cedis and shillings.
11. **Zindi** still scores late submissions (10/day). It's our only feedback that includes Ghana.

## 7. The work by step, with the options each one must test

### Step 5 · Features and fair tests (Joseph)
- **Borrower history:** number of past loans, finished loans, past defaults, past default rate (empty if unknown, plus a flag), days since last loan.
  - Test: safe (outcome counts after the due date) vs leaky (counts once sent); all past loans / last 3 / last 5 / last 90 days.
- **Calendar clues:** test with vs without, on the older-vs-newer test.
- **Macro clues:** test with vs without; last year's figures vs same year's.
- **Three kinds of test:** shuffled (stratified k-fold) vs grouped by customer vs older-vs-newer, plus StratifiedGroupKFold. Report how much the naive one inflates the score.
- **Write-up:** `learnings/05_features.md`.

### Step 6–8 · Task 2: classification (Germain)
- **Models:** majority baseline, logistic regression (class weights), k-NN, pruned tree, random forest, LightGBM/XGBoost, SVC (on a sample if slow); optional small MLP.
- **Test these options:**
  - imbalance handling: none / balanced weights / custom weights / undersampling / SMOTE (inside folds only);
  - tuning of each model;
  - calibration: none / Platt / isotonic;
  - threshold rule: cost-based / best F1 / fixed approval rate;
  - each model under all three kinds of test;
  - loss functions (the lecturer asked for this);
  - reason codes: coefficients vs SHAP.
- **Report:** PR-AUC, ROC-AUC, precision/recall/F1 sweep, confusion matrix, reliability curve, bootstrap 95% CIs, and whether the best model beats logistic regression beyond the ±0.0263 noise floor.
- **Zindi:** submit and log every score.

### Step 9 · Task 1: regression (Alice)
- **Models:** mean baseline, OLS, Ridge, Lasso, k-NN, tree / random forest / LightGBM, SVR.
- **Test:** raw vs log target; local currency vs USD; feature-set variants; all three kinds of test.
- **Report:** RMSE and MAE on log and original scales, residual plot, and how the predicted amount becomes a limit.

### Step 10 · Kenya → Ghana transfer (Alice)
- Compare distributions: loan types, durations, lenders, amounts, new vs repeat.
- Domain classifier (can the clues tell Ghana from Kenya?) and importance weighting.
- **Test:** different clue sets; with/without currency conversion; with/without weights; weight clipping levels; how to handle unseen loan types and lenders.
- Write what evidence NkwaPay would need before trusting the model in Ghana.

### Step 11 · Fairness and regulation (Liza)
- **Model Card and datasheet.**
- **Metrics by group:** PR-AUC, F1 and approval rate by country, loan_type, lender_id, new vs repeat, loan-size band.
- **Proxy analysis**, reusing Alice's domain classifier.
- **Mitigations, compared before and after:** drop proxies / starter limit for first-timers / reweighting / group thresholds (and whether they're legal).
- **Compliance mapping:** see [`knowledge/regulation.md`](../knowledge/regulation.md). The clearest gap is that Act 726 s.26(4) requires a credit-bureau check before every decision.
- **Findex:** who can't get credit in Ghana, and does our model help or hurt?
- **Plain-language decline explanation** for a borrower.

### Step 12 · Scoring service (Joseph)
- A saved model plus one function: application in → chance of default, decision (approve / lower limit / decline), top 3 reasons out.
- **Test:** a new customer, a repeat customer, a Ghanaian applicant, missing fields, unseen loan type or lender, and timing over 1,000 calls.

### Step 13 · Report, slides, reflections (everyone)
- **Report:** each owner writes their own section; Liza edits it into one voice.
- **Slides:** each owner makes the slides for their part, presented as a 15-minute relay, with two rehearsals.
- **Q&A drill:** everyone answers on parts they didn't build, using the `learnings/` files.
- **AI-use declaration** in the report, plus one in each reflection.

## 8. What the lecturer said to watch for (from the recordings)
- Back every claim with a number or a plot, and be ready to "defend every number".
- Fit encoders and scalers on training data only.
- A leakage-audit section with before/after numbers, in the report *and* the slides.
- Code that runs top to bottom from a fresh clone.
- Expect "why did you do this?" questions on every choice.
- Reflections "are really important".

## Sign-off

Edit your row and commit it from your own account. If you disagree with something, open an issue or change it here and say so in `docs/log.md`.

| Member | Agree with the plan? (Yes / Yes, with changes / No) | Happy with my role? | Comments | Date |
|---|---|---|---|---|
| Alice | | | | |
| Germain | | | | |
| Joseph | | | | |
| Liza | | | | |
