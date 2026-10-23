# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

**New to the project?** Read [`knowledge/README.md`](knowledge/README.md) first. **The plan and progress tracker** are in [`docs/plan.md`](docs/plan.md).

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## Now

| | |
|---|---|
| **Stage** | Step 6 of 13: provisional default model (plain logistic regression) |
| **Responsible** | **Germain** |
| **Due** | Sat 24 Oct |
| **Waiting on it** | Liza (fairness, step 11) and Joseph (scorer, step 12) can start building against it |
| **Next after this** | Step 7: Germain's full classification comparison |

Everything else (all 13 steps, who owns them, what's done) is in the [progress tracker](docs/plan.md#progress-tracker).

**While you wait:**
- **Alice:** step 9 (loan amount) can start now: it also only needs step 5. Read [`learnings/05_features.md`](learnings/05_features.md) first; past amounts are your key clue.
- **Liza:** Findex analysis; read the BoG Directive and Acts 843 and 726 ([`knowledge/regulation.md`](knowledge/regulation.md)); set up the Model Card skeleton.
- **Joseph:** the scorer's interface and its edge-case tests.

## Current step in detail: 6 · Provisional model (Germain)

**Why this step exists:** a quick, honest first model, so Liza and Joseph can build the fairness checks and the scorer *now*. Your full comparison of models (step 7) can then replace it without anyone redoing work.

**Before you start:**
1. Pull `main` into your branch.
2. Read [`learnings/05_features.md`](learnings/05_features.md) (about 10 minutes) and [`AGENTS.md`](AGENTS.md).
3. **Review step 5** ([ADR 0011](docs/adr/0011-git-workflow.md)): rerun `notebooks/01_eda.ipynb` (about 6 min) and check a few numbers against the learnings file.

**Do:**
1. **Get the data and the recipe.** Use the 13 shared clues and the shared preparation recipe:
   ```python
   import sys; sys.path.insert(0, "../src")
   from features import build, splits, FEATURES, preprocessor
   from sklearn.pipeline import make_pipeline
   from sklearn.linear_model import LogisticRegression
   train, test = build("../data/zindi")
   model = make_pipeline(preprocessor(FEATURES), LogisticRegression(class_weight="balanced", max_iter=3000))
   ```
2. **Score it** on `splits(train, "time_block")` (main) and `"fold_customer"`: PR-AUC, ROC-AUC, lift. Step 5 got a future-loan lift of about 8.1 with this setup, so yours should be close.
3. **Calibrate it.** Class weights inflate probabilities, and Liza's cut-off (decline above **2.1%**, [ADR 0007](docs/adr/0007-cost-matrix-and-cutoff.md)) only works on honest ones. Try none / Platt / isotonic and compare reliability curves and Brier scores. Calibrate inside the training part only.
4. **Save for the others** (never commit these: they contain IDs):
   - `data/predictions/provisional_logistic.csv`: `ID`, the fold scheme, out-of-fold calibrated probability, `target`;
   - `data/models/provisional_logistic.joblib`: the calibrated pipeline fitted on all training loans.
5. **Write it up:**
   - `learnings/06_provisional_model.md` in the simplest words;
   - an ADR for the calibration choice;
   - log lines in `docs/log.md` and `docs/ai_use.md`.
   Then tick step 6 in the tracker and move this **Now** box to step 7.

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
