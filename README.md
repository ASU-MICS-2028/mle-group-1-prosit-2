# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

**New to the project?** Read [`knowledge/README.md`](knowledge/README.md) first. **The plan and progress tracker** are in [`docs/plan.md`](docs/plan.md).

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## Now

| | |
|---|---|
| **Stage** | Step 13 of 13 |
| **Responsible** | **Everyone:** step 13 (check the drafts, rehearse, write reflections) |
| **Due** | Debrief was Tue 3 Nov: **confirm the new date** |
| **Waiting on these** | Steps 1–12 are done |
| **Just finished** | Step 12: scorer ([ADR 0022](docs/adr/0022-scoring-service.md), [learnings/12](learnings/12_scorer.md)); Ghana rules ([ADR 0021](docs/adr/0021-ghana-rules.md)) |

### Everyone · step 13: report, slides, reflections
All drafts were made with AI from our saved results, so **each owner must check them before submitting** (course AI policy).
1. **Report and audit:** [`report/`](report/) (Word, PDF). Check your sections; Liza edits into one voice. Fix the AI-use statement so it's true.
2. **Slides:** the group's debrief deck, shared by Joseph. Two rehearsals, then a Q&A drill on parts you didn't build, using `learnings/`.
3. **Reflections:** write your own one page. They stay out of this repo (`reflections/` is team-only); Joseph has a sheet of facts and prompts to share.
4. **Scorer demo:** `PYTHONPATH=. .venv/bin/python src/scorer.py --fit`, then practise ([learnings/12](learnings/12_scorer.md)).
5. **Still to confirm:** quote Zindi's rule on probing; check the Findex rural and education codes; agree the debrief date.

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
- What we learned: [`learnings/`](learnings/README.md); every result: [`learnings/results_index.md`](learnings/results_index.md)
- Course material: [`knowledge/`](knowledge/README.md)
- Data sources: [`docs/01_data.md`](docs/01_data.md)
