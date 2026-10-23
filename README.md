# MLE Group 1 – Prosit 2

How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from Kenya, defaults are about 1 in 50, and a wrong decision either pushes a family into debt or shuts them out of credit?

**New to the project?** Read [`knowledge/README.md`](knowledge/README.md) first. **The plan and progress tracker** are in [`docs/plan.md`](docs/plan.md).

We build one feature set and two models on the African Credit Scoring Challenge data: a default classifier (Task 2) and a loan-amount regressor (Task 1). Then we test how the Kenyan model transfers to Ghana, audit it for fairness and Ghanaian regulation, and ship a scorer that returns a probability, a decision and three plain-language reasons.

## Now

| | |
|---|---|
| **Stage** | Step 5 of 13: shared features and fair tests |
| **Responsible** | **Joseph** |
| **Due** | Fri 23 Oct |
| **Waiting on it** | Germain (step 6, provisional model, Sat 24) and Alice (steps 9–10) |
| **Next after this** | Step 6: Germain's provisional logistic model |

Everything else (all 13 steps, who owns them, what's done) is in the [progress tracker](docs/plan.md#progress-tracker).

**While you wait:**
- **Germain:** logistic regression and gradient boosting derivations ([`knowledge/derivations.md`](knowledge/derivations.md)).
- **Alice:** linear regression derivation; Kenya vs Ghana comparisons on the raw data.
- **Liza:** Findex analysis; read the BoG Directive and Acts 843 and 726 ([`knowledge/regulation.md`](knowledge/regulation.md)); set up the Model Card skeleton.

## Current step in detail: 5 · Features and fair tests (Joseph)

| Part | What | Status |
|---|---|---|
| 5.1 | Look at the shape of loan histories | ✅ |
| 5.2 | Borrower history (`borrower_history` in `src/features.py`), checked on a made-up example and against a slow loop on 2,000 real loans | ✅ |
| 5.3 | Calendar and macro clues (`calendar`, `add_macro`) | ✅ |
| 5.4 | Three kinds of test (`add_folds`, `splits`) and `build()`, which gives everyone the full table in one call | ✅ |
| 5.4b | Extra cases: past loan amounts and borrowing speed (loans in last 7/30 days) as clues; a fourth test, newer loans from never-seen customers (closest stand-in for Ghana) | ✅ |
| 5.5 | Compared every option: all 63 combinations of clue groups, each column dropped, leaky vs safe, windows, macro years; both models; seeds + bootstrap. **Result: `FEATURES` = base + history + speed + amounts** ([ADR 0012](docs/adr/0012-final-feature-set.md)) | ✅ |
| 5.6 | Write-up in `learnings/05_features.md` + experiment in `notebooks/01_eda.ipynb` | ⏳ next |

**What the others need to know already:**
- **Experience is the strongest clue:** previous loans alone score ROC-AUC 0.76.
- **Past default rate is almost useless:** only 12% of defaulters ever borrow again, so there's rarely a past default to learn from (selection bias, to state in the report).
- **No Ghanaian applicant has any history**, so the model sees all of Ghana as first-timers.
- **Macro clues only take 4 values in training** (one per year), and Ghana's inflation is far outside Kenya's range.
- **The shuffled test lies, mostly for complex models:** LightGBM's PR-AUC is 0.31 shuffled vs 0.21 grouped by customer. On newer loans (the most realistic test), logistic regression beats LightGBM (0.11 vs 0.10).
- **Use `FEATURES`** (13 columns) for both tasks: no calendar, no macro, because they hurt on future loans. Past amounts cut Task 1's error from 0.91 to 0.58.
- **To get the data:** `from features import build; train, test = build('data/zindi')` (run from `src/` or add it to `sys.path`).

Run the checks yourself with `.venv/bin/python src/features.py`.

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
