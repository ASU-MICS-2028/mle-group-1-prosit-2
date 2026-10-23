@AGENTS.md

## Claude Code specifics

- **Follow `AGENTS.md` exactly.** It's imported above. The most important rules:
  - one step at a time, explained in plain words, then wait for the human;
  - test every diverging path in a comparison table;
  - decisions → `docs/adr/`;
  - learnings → `learnings/` in the simplest words;
  - the README shows only the current step and owner.
- **Never print real data rows.** When exploring `data/` with Bash or Python, print only shapes, counts, value counts, summary statistics or scores. Run Python on data files with `-I` and pass paths as arguments.
- **Before committing any change to `src/`,** run `.venv/bin/python src/features.py` and confirm all checks pass.
- **When you finish a step:** add the `docs/log.md` line, add a `docs/ai_use.md` line saying what Claude did and what the human checked, update the README's Now box, and tick the tracker.
- **Subagents:** fine for reading or summarising course material and searching. Never give them raw data rows, and review what they write before committing it.
- **Explain like a patient teacher.** Use a small made-up example whenever an idea is abstract. The human will be questioned on it without you.
