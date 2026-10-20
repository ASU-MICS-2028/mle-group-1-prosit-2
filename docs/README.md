# Docs

Everything we do on Prosit 2, and how we did it, is written down here. If it isn't in `docs/`, the rest of the group can't rely on it.

| File | What it covers |
|---|---|
| [`log.md`](log.md) | Dated, one-line-per-action record of everything done, by whom |
| [`00_project_setup.md`](00_project_setup.md) | The brief in plain words, the plan, roles, who waits on whom, the repo and environment |
| [`01_data.md`](01_data.md) | Where each dataset came from, how we got it, licence terms, and what our checks found |

New topics get their own numbered file (`02_feature_audit.md`, `03_cost_matrix.md`, ...).

## How to write in here

1. **Add a line to `log.md` every time you do something:** date, who, what, and a link to the file or commit.
2. **Explain it so someone who wasn't there could redo it:** the steps you took, the commands or code you ran, the numbers you got, and what they mean in plain English.
3. **Record decisions with their reasons and the options you rejected.** "We chose X because Y; we also tried Z, which gave W."
4. **No raw data in here.** Column names, counts and aggregates are fine; individual rows are not.
