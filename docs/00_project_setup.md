# 00 · Project setup: the brief, the plan, the repo

**The full plan is in [`plan.md`](plan.md)** (kept up to date). The sign-off table is still in the Google Doc **[MLE-GROUP-1-PROSIT-2 Plan](https://docs.google.com/document/d/16AOzssRkISRfICwckw1Q6OZXXJYGGTe4fnw9fxffBx0/edit)** (Drive: `MLE-GROUP-1 / prosit 2`). This file is the short version.

## The brief in plain words

NkwaPay, a mobile-money lender, has labelled loans from Kenya (repaid or defaulted) and is launching in Ghana, where it has none. About 1 in 50 loans default. The credit committee wants one tool that:

1. gives each applicant a **probability of default** (Task 2, classification);
2. suggests a **loan amount** (Task 1, regression), using the same features;
3. is **fair and explainable**, with plain reasons for every decision;
4. is **honest about uncertainty**, because it is trained in Kenya and used in Ghana;
5. **complies** with the Bank of Ghana Digital Credit Directive, the Data Protection Act 2012 (Act 843) and the Credit Reporting Act 2007 (Act 726).

The committee prefers a simple model it can justify over a slightly better black box.

**Due:** debrief **Tue 3 Nov 2026**: repo, 6–10 page report, ethics audit, scoring service, slides, and a one-page reflection each.

**Marks:** framing 10 · modelling 30 · evaluation 20 · ethics 20 · deployment and defence 15 · process 5.

## The two team rules

1. **Explain everything as blatantly and simply as possible.** Nobody redoes anyone else's part; we rely on each other's findings and must defend them without AI.
2. **Test every reasonable scenario.** Each step compares the alternatives in a table and says which one wins and why.

## Roles

| Member | Owns |
|---|---|
| Joseph | Repo, shared feature code, validation setup, 01_eda, scoring service |
| Germain | 02_classification (Task 2), calibration, threshold, reason codes, Zindi submissions; derives logistic regression and gradient boosting |
| Alice | 03_regression (Task 1), Kenya → Ghana transfer study; derives linear regression |
| Liza | Framing (timeline, label, feature audit, cost matrix), fairness, Model Card, compliance, Findex analysis, borrower explainer; report editor |

## Who waits on whom

```
Zindi data ──► Part A feature audit + cost matrix (Liza)        
                     │                     │
                     ▼                     │
            Shared features + folds        │
                 (Joseph)                  │
         ┌───────────┼──────────┐          │
         ▼           ▼          ▼          ▼
   03 regression  04 transfer  02 classification ◄── cost matrix sets its threshold
     (Alice)       (Alice)       (Germain)
         │           │          │
         │           │          ├──► chosen model + saved predictions
         │           │          ├──► reason codes
         ▼           ▼          ▼
   loan limits   proxy features  04 fairness (Liza) · scorer (Joseph) · Model Card
         └───────────┴──────────┴──► report + slides (everyone)

Findex ──► Liza's access-gap analysis (nothing else depends on it)
```

- The critical path is data → feature audit → shared features → Germain's model → fairness and scorer → report.
- Germain hands over a **provisional logistic model** around 24 Oct, so the fairness and scorer work can start before the final model exists.
- The live step-by-step checklist (what has to be done now, by whom) is in the [main README](../README.md#what-has-to-be-done-now-and-who-does-it).

## Repo and environment

- GitHub: `ASU-MICS-2028/mle-group-1-prosit-2`.
- Python 3.12 via [uv](https://docs.astral.sh/uv/). Every package is pinned in `requirements.txt`, so everyone runs identical versions.
- Setup:
  ```sh
  uv venv --python 3.12 && uv pip install -r requirements.txt
  ```
- `data/` is in `.gitignore`: it must never be committed. Both data licences forbid redistributing it (see [01_data.md](01_data.md)).
- Notebooks: `01_eda`, `02_classification`, `03_regression`, `04_transfer_and_fairness`, as the brief requires. Each starts with its owner and the two team rules.
- Shared code (feature building, the scorer) will live in `src/`. It hasn't been created yet; it comes at step 5, once the feature audit decides which columns are allowed.
