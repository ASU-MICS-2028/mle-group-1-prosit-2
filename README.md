# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

**New to the project?** Read [`knowledge/README.md`](knowledge/README.md) first. **The plan and progress tracker** are in [`docs/plan.md`](docs/plan.md).

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## Now

| | |
|---|---|
| **Stage** | Step 12 of 13 |
| **Responsible** | **Joseph:** step 12 (scoring service) |
| **Due** | Was Sat 31 Oct: **overdue, new date to agree** |
| **Waiting on these** | Everyone (step 13: report, slides, reflections) |
| **Just finished** | Step 11: fairness audit. Dropped 3 "borrow often" clues; first-timers get a capped starter loan instead of a no; 1,224 scenarios tested ([ADR 0020](docs/adr/0020-fairness-mitigation.md), [learnings/11](learnings/11_fairness.md), [Model Card](docs/model_card.md)) |

### Joseph · step 12: scoring service
1. One function: application in → probability, decision, limit, top 3 reasons, with latency documented.
2. **Default model:** `final_model(train, DEFAULT_CLUES)` for Kenya at 2.1% ([ADR 0020](docs/adr/0020-fairness-mitigation.md)). **Ghana** ([ADR 0021](docs/adr/0021-ghana-rules.md)): decline Type_2 and other unseen types; Type_3 gets a 300 GHS starter loan and no full-size loans; the probability shown is the group's measured rate. Reasons from `src/reasons.py`. **Limit:** `src/amounts.py`.
3. **First-timers above the cut-off:** a starter loan of about 10% of a typical loan (Kenya: only below 24% risk; Ghana: see ADR 0021).
4. Test a new customer, a repeat customer, a Ghanaian applicant, missing fields, an unseen loan type, and timing over 1,000 calls.
5. Write `learnings/12_scorer.md`.

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
