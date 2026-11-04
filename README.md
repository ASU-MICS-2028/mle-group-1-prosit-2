# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

**New to the project?** Read [`knowledge/README.md`](knowledge/README.md) first. **The plan and progress tracker** are in [`docs/plan.md`](docs/plan.md).

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## Now

| | |
|---|---|
| **Stage** | Steps 11 and 12 of 13 (in parallel) |
| **Responsible** | **Liza:** step 11 (fairness, Model Card) · **Joseph:** step 12 (scoring service) |
| **Due** | Was Sat 31 Oct: **overdue, new date to agree** |
| **Waiting on these** | Everyone (step 13: report, slides, reflections) |
| **Just finished** | Step 9: loan-amount model, LightGBM on log amount, limit = 75% level ([ADR 0018](docs/adr/0018-loan-amount-model.md), [learnings/09](learnings/09_regression.md)) · Step 10: Kenya → Ghana transfer, no weighting, no auto-decline in Ghana yet ([ADR 0019](docs/adr/0019-kenya-to-ghana-transfer.md), [learnings/10](learnings/10_transfer.md)). Both ADRs are *Proposed* until Alice's walkthrough. |

### Liza · step 11: fairness → `notebooks/04_transfer_and_fairness.ipynb`, Part 2
1. PR-AUC, F1 and selection rates by country, `loan_type`, `lender_id`, tenure (new vs repeat) and loan-size band (brief Part D.2).
2. **Start from step 10:** the variable `PD` in notebook 04 has Ghanaian probabilities for every option. The step 7 model declines 47% of Ghana (Kenya 19%), including **every first loan and every Type_2 loan** ([learnings/10](learnings/10_transfer.md) §5).
3. **From step 9:** the amount model over-predicts first loans (about 1.4× in Kenya, 3.4× in Ghana) ([learnings/09](learnings/09_regression.md), `learnings/tables/09_residuals_by_group.csv`).
4. Proxy analysis, one mitigation tested against the unmitigated model, Model Card, regulatory mapping, Findex access gaps.
5. Write `learnings/11_fairness.md` and an ADR.

### Joseph · step 12: scoring service
1. One function: application in → probability, decision, limit, top 3 reasons, with latency documented.
2. **Default:** step 7 model ([ADR 0016](docs/adr/0016-final-classification.md)) with reasons from `src/reasons.py`. **Limit:** `src/amounts.py` (`final_amount_model(train).limit(X)`), only for approved applicants.
3. **Country switch ([ADR 0019](docs/adr/0019-kenya-to-ghana-transfer.md)):** Kenya uses the step 7 model at 2.1%. Ghana uses the model without `loan_type` at 3.2%, with first loans, Type_2 and loans over 90 days routed to a starter limit or review.
4. Write `learnings/12_scorer.md`.

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
