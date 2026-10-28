# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

**New to the project?** Read [`knowledge/README.md`](knowledge/README.md) first. **The plan and progress tracker** are in [`docs/plan.md`](docs/plan.md).

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## Now

| | |
|---|---|
| **Stage** | Steps 8–10 of 13 (two people in parallel) |
| **Responsible** | **Alice:** step 9 (loan-amount model), then step 10 (Kenya → Ghana transfer) · **Germain:** step 8 (reason codes) and 7b (Zindi submission) |
| **Due** | Steps 8, 7b and 9: **Thu 29 Oct** · Step 10: **Fri 30 Oct** |
| **Waiting on these** | Liza (step 11, fairness) needs 9 and 10 · Joseph (step 12, scorer) needs 8 and 9 |
| **Just finished** | Step 7: logistic regression + Platt, cost cut-off 2.1% Kenya / 3.2% Ghana ([ADR 0016](docs/adr/0016-final-classification.md), [learnings/07](learnings/07_classification.md)) |

### Alice · step 9: loan-amount model (Task 1) → `notebooks/03_regression.ipynb`
1. Use `build()`, `FEATURES` and `preprocessor()` from `src/features.py`; target is `Total_Amount`. Step 5 already found log amount works best: future-loan error 0.58 (LightGBM) / 0.63 (linear) vs 0.97 for "guess the average".
2. Models: mean baseline, OLS, Ridge, Lasso, k-NN, tree / random forest / LightGBM, SVR (on a sample if slow).
3. Test: raw vs log target; local currency vs USD; all three tests (`splits(df, "fold_shuffled" / "fold_customer" / "time_block")`), future loans as the main one.
4. Report RMSE and MAE on log and original scales, a residual plot, and how a predicted amount becomes a loan limit.
5. Save predictions locally under `data/` (never committed). Write `learnings/09_regression.md` and an ADR.

### Alice · step 10: Kenya → Ghana transfer → `notebooks/04_transfer_and_fairness.ipynb`
1. Compare Kenya (train) and Ghana (test) on loan types, durations, lenders, amounts and new vs repeat. **Remember:** no Ghanaian applicant has borrowing history, so history, speed and amounts are empty for all of them.
2. Domain classifier: can the clues tell Ghana from Kenya? Turn it into importance weights.
3. Test: different clue sets; with and without currency conversion; with and without weights; weight-clipping levels; unseen loan types and lenders.
4. Say what NkwaPay would need to see before trusting the model in Ghana. Benchmark: borrowers with no history get lift ~2.7, against ~8 overall ([ADR 0015](docs/adr/0015-history-fixes-from-review.md)).
5. Write `learnings/10_transfer.md` and an ADR.

### Germain · step 8: reason codes, and 7b: Zindi
1. **Step 8:** a function giving the top 3 reasons behind each decision from the step 7 model (`fit_integration_model` in `src/classification_experiments.py`). Compare coefficient × value against SHAP; write each reason in words a borrower understands. Joseph's scorer will call it.
2. **Step 7b:** submit the step 7 model to Zindi (late submissions are still scored, 10 a day max) and log every score in `02_classification`.
3. Write `learnings/08_reason_codes.md` and update ADR 0016 or add a new one.

## Run it from a fresh clone

```sh
git clone https://github.com/ASU-MICS-2028/mle-group-1-prosit-2.git && cd mle-group-1-prosit-2
uv venv --python 3.12 && uv pip install -r requirements.txt     # brew install libomp if lightgbm fails on macOS
# put the data in data/zindi/ (Zindi: African Credit Scoring Challenge) and data/worldbank/micro_gha.csv (Findex Ghana 2021)
.venv/bin/python src/features.py                               # self-checks
for nb in notebooks/0*.ipynb; do .venv/bin/jupyter nbconvert --to notebook --execute --inplace "$nb"; done
```

**Where things are:**
- Rules for people and AI agents: [`AGENTS.md`](AGENTS.md)
- Plan and tracker: [`docs/plan.md`](docs/plan.md)
- Decisions: [`docs/adr/`](docs/adr/README.md)
- What we learned: [`learnings/`](learnings/README.md)
- Course material: [`knowledge/`](knowledge/README.md)
- Data sources: [`docs/01_data.md`](docs/01_data.md)
