# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## What to read

| | |
|---|---|
| **Report** | [`report/report.pdf`](report/report.pdf) (Word: [`report.docx`](report/report.docx)) |
| **Ethics and regulation audit** | [`report/audit.pdf`](report/audit.pdf) |
| **Model Card and datasheet** | [`docs/model_card.md`](docs/model_card.md), [`docs/datasheet.md`](docs/datasheet.md) |
| **Scoring service** | [`src/scorer.py`](src/scorer.py), tests in [`tests/test_scorer.py`](tests/test_scorer.py), write-up in [`learnings/12_scorer.md`](learnings/12_scorer.md) |
| **AI-use declaration** | Report section 11; every use logged in [`docs/ai_use.md`](docs/ai_use.md) |

## Run it from a fresh clone

```sh
git clone https://github.com/ASU-MICS-2028/mle-group-1-prosit-2.git && cd mle-group-1-prosit-2
uv venv --python 3.12 && uv pip install -r requirements.txt     # brew install libomp if lightgbm fails on macOS
# put the data in data/zindi/ (Zindi: African Credit Scoring Challenge) and data/worldbank/micro_gha.csv (Findex Ghana 2021)
.venv/bin/python src/features.py                               # self-checks
for nb in notebooks/0*.ipynb; do .venv/bin/jupyter nbconvert --to notebook --execute --inplace "$nb"; done
PYTHONPATH=. .venv/bin/python src/scorer.py --fit                 # fit and save the scorer
PYTHONPATH=. .venv/bin/python tests/test_scorer.py                # scorer tests (a few minutes)
```

**Where things are:**
- Plan, roles and who did each step: [`docs/plan.md`](docs/plan.md); action log: [`docs/log.md`](docs/log.md)
- Rules we worked by (people and AI agents): [`AGENTS.md`](AGENTS.md)
- Decisions: [`docs/adr/`](docs/adr/README.md)
- What we learned: [`learnings/`](learnings/README.md); every result: [`learnings/results_index.md`](learnings/results_index.md)
- Course material: [`knowledge/`](knowledge/README.md)
- Data sources: [`docs/01_data.md`](docs/01_data.md)
