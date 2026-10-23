# AGENTS.md: how to work in this repo (for people and their AI agents)

This file is the rulebook. Claude Code (via `CLAUDE.md`), Codex, Cursor, Copilot and most other coding agents read it. If you're a human, read it too: it's the same rules.

## The project in one paragraph

ICS553 Prosit 2 (Ashesi University), MLE Group 1: Alice, Germain, Joseph, Liza.
- **The client:** NkwaPay, a mobile-money lender with labelled loans from Kenya, moving into Ghana where it has none. About 1 in 50 loans default.
- **The tool we build:** (Task 2) the chance each applicant defaults; (Task 1) a loan amount; fair, explainable decisions with 3 plain reasons, honest about the Kenya → Ghana gap, and compliant with Ghanaian law.
- **Due:** debrief **Tue 3 Nov 2026**.
- **Read before doing anything:**
  - [`README.md`](README.md): the current step and who owns it;
  - [`docs/plan.md`](docs/plan.md): all steps and the tracker;
  - [`knowledge/prosit2_brief.md`](knowledge/prosit2_brief.md): the brief;
  - [`docs/adr/`](docs/adr/README.md): decisions already made. **Don't reopen a decision without writing a new ADR.**

## The working rules

1. **One step at a time, explained.** Work in small steps. For each one, first explain to the human in plain words what you're about to do and why. Do it, then explain what the result means. Then **stop and let them confirm** before the next step. The humans must defend every number in a live Q&A *without AI*, so they have to understand each step, not just receive it.
2. **Test every diverging path.** Whenever there's more than one reasonable way (a clue, a fill-in rule, a model, a setting, a threshold), try them all and put the results side by side in a table. Pick the winner with numbers, not opinion. Include the "naive" or "cheating" version when it shows how much a mistake would cost.
3. **Decisions go in `docs/adr/` as ADRs.** Copy [`docs/adr/0000-template.md`](docs/adr/0000-template.md), take the next number, fill in context / options tested / decision / why / consequences, and add it to the index. A changed decision gets a new ADR that replaces the old one.
4. **What we learn goes in `learnings/`, in the simplest possible words.** One file per step, `learnings/NN_<step>.md`, following [`learnings/README.md`](learnings/README.md):
   - short sentences and everyday words;
   - every term explained;
   - real numbers pasted in;
   - the options tried;
   - likely Q&A questions.
   Someone who never ran the code must be able to understand and present it.
5. **Course knowledge lives in `knowledge/`.** Check it before explaining a concept, and cite it (e.g. "see `knowledge/derivations.md` §b"). New useful course material goes in there **in our own words**.
6. **The README shows only the current stage and its owner.** When a step finishes:
   - tick it in the [`docs/plan.md`](docs/plan.md#progress-tracker) tracker;
   - move the README's **Now** box to the next step and owner;
   - replace the "current step in detail" section.
   No history in the README.
7. **Log every action** as one line in [`docs/log.md`](docs/log.md) (date · who · what · where), and **log AI use** in [`docs/ai_use.md`](docs/ai_use.md). Both feed the report's AI declaration, which is required.

## Data rules (hard rules)

- **`data/` is never committed** (it's in `.gitignore`).
  - `data/zindi/`: Train.csv, Test.csv, economic_indicators.csv, SampleSubmission.csv, VariableDefinitions.txt.
  - `data/worldbank/micro_gha.csv`: Findex Ghana.
- **Never put raw data rows into an AI conversation.** That's the course rule and the data licence. Agents must not print `df.head()`, `df.sample()` or individual rows of real data. Shapes, counts, value counts, summary statistics and model scores are fine. To explain logic, use made-up rows (see the "Ama" example in `src/features.py`).
- **Findex:** survey-weighted (`wgt`) aggregates only. Each analyst registers for their own copy.
- **The repo is public:** no original course files, no personal data, no staff contacts ([ADR 0002](docs/adr/0002-public-repo.md)).

## ML rules (to avoid fooling ourselves)

- **Get features only from `src/features.py`:** `train, test = build("data/zindi")`, then choose columns from `BASE`, `CALENDAR`, `HISTORY`, `MACRO.values()`. Never re-derive features in a notebook ([ADR 0004](docs/adr/0004-shared-feature-code.md)).
- **Never use the dropped columns as clues:** `Total_Amount_to_Repay` and `Lender_portion_to_be_repaid` (they leak post-default penalties), the lender-funding columns, `lender_id`, IDs ([ADR 0005](docs/adr/0005-feature-audit.md)). `Total_Amount` is Task 1's target and is never a clue.
- **Fit every scaler, encoder, imputer, sampler (SMOTE) and calibrator inside the training fold,** using a scikit-learn `Pipeline`.
- **Validate with the fold columns from `build()`:** `fold_customer`, `time_block` and `time_new_customers` (via `splits()`). Report `fold_shuffled` only to show how it inflates. Trust older → newer first ([ADR 0010](docs/adr/0010-validation-tests.md)).
- **Report PR-AUC, ROC-AUC, and PR-AUC ÷ the test part's default rate.** Use bootstrap 95% CIs before claiming one model beats another; the noise floor is ±0.0263.
- **The cut-off (2.1% Kenya / 3.2% Ghana) only applies to calibrated probabilities** ([ADR 0007](docs/adr/0007-cost-matrix-and-cutoff.md)).
- **Fix random seeds,** and make sure notebooks run top to bottom from a fresh clone.

## Commands

```sh
uv venv --python 3.12 && uv pip install -r requirements.txt      # setup (brew install libomp if lightgbm fails on macOS)
.venv/bin/python src/features.py                                # self-checks: must print 3 "passed" lines before committing src/ changes
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/<nb>.ipynb   # run a notebook end to end
```

New dependency: `uv pip install <pkg>`, then pin it in `requirements.txt`.

## Repo map

| Path | What |
|---|---|
| `README.md` | **Now:** the current step and its owner; how to run |
| `AGENTS.md` / `CLAUDE.md` | These rules |
| `docs/plan.md` | Plan, progress tracker, roles, timeline, sign-off |
| `docs/adr/` | Decisions (ADRs) |
| `docs/log.md` · `docs/ai_use.md` | Action log · AI-use log |
| `docs/01_data.md` | Where the data came from, licence terms, checks |
| `learnings/` | Plain-language write-up of every step |
| `knowledge/` | The brief, course rules, lecture notes, derivations, regulation, fairness readings |
| `src/features.py` | All shared feature and fold code (+ self-checks) |
| `notebooks/` | `00_*` Liza's audit and cost matrix · `01_eda` · `02_classification` · `03_regression` · `04_transfer_and_fairness` |

## Git

- **Work on your own branch, commit from your own account** ([ADR 0011](docs/adr/0011-git-workflow.md)).
- **Small commits with clear messages,** e.g. "Step 5.2: time-safe borrower history".
- **A step is merged into `main` after someone else reviews it:** reruns it fresh and spot-checks the numbers.
- **Don't change another member's step outputs silently.** Propose the change in an ADR or log line and tell them.
- **Never force-push `main`** without the group agreeing.

## Done means

A step is done when:
- [ ] the code runs from a fresh clone;
- [ ] every reasonable option was compared in a table;
- [ ] decisions are in ADRs;
- [ ] `learnings/NN_*.md` exists in simple words;
- [ ] the log and AI-use lines are written;
- [ ] the tracker is ticked;
- [ ] the README's Now box has moved to the next step and owner.
