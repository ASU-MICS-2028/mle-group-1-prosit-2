# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## What to read

| | |
|---|---|
| **Report** | [`report/report.pdf`](report/report.pdf) (Word: [`report.docx`](report/report.docx)) |
| **Ethics and regulation audit** | [`report/audit.pdf`](report/audit.pdf) |
| **Model Card and datasheet** | [`docs/model_card.md`](docs/model_card.md), [`docs/datasheet.md`](docs/datasheet.md) |
| **Live demo** | [nkwapay-demo-148128233281.africa-south1.run.app](https://nkwapay-demo-148128233281.africa-south1.run.app): a borrower signs in, asks for a loan and sees the decision with reasons (made-up customers). Video: `NkwaPay demo.mp4` in the group Drive. Code in [`app/`](app/) |
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
PYTHONPATH=. .venv/bin/python tests/test_app.py                   # demo API tests
PYTHONPATH=. .venv/bin/uvicorn app.main:app --port 8080            # demo at http://localhost:8080
```

**Redeploy the demo** (Cloud Run, project `agroconnect-highlanders`; needs Docker and the fitted `data/models/scorer.joblib`). The image is built locally because Cloud Build lacks permission in that project:

```sh
IMG=africa-south1-docker.pkg.dev/agroconnect-highlanders/cloud-run-source-deploy/nkwapay-demo:$(git rev-parse --short HEAD)
gcloud auth configure-docker africa-south1-docker.pkg.dev
docker build --platform linux/amd64 -t $IMG . && docker push $IMG
gcloud run deploy nkwapay-demo --image $IMG --region africa-south1 --allow-unauthenticated --min-instances 0 --max-instances 2 --memory 1Gi --project agroconnect-highlanders
```

**Where things are:**
- Plan, roles and who did each step: [`docs/plan.md`](docs/plan.md); action log: [`docs/log.md`](docs/log.md)
- Rules we worked by (people and AI agents): [`AGENTS.md`](AGENTS.md)
- Decisions: [`docs/adr/`](docs/adr/README.md)
- What we learned: [`learnings/`](learnings/README.md); every result: [`learnings/results_index.md`](learnings/results_index.md)
- Course material: [`knowledge/`](knowledge/README.md)
- Data sources: [`docs/01_data.md`](docs/01_data.md)
