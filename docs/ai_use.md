# AI-use log

The course requires an AI-use declaration in the report and in each reflection, and we must be able to explain and reproduce everything without AI. Every time you use an AI tool for project work, add a line: what the AI did, and what **you** checked or changed. This becomes the declaration.

**Never** give an AI tool raw rows of the Zindi or Findex data ([ADR 0003](adr/0003-data-handling.md)).

| Date | Who | Tool | What the AI did | What the human checked / changed |
|---|---|---|---|---|
| 18 Oct 2026 | Joseph | Claude Code | Read the brief; drafted the plan, roles and timeline; set up the repo skeleton | Reviewed the plan and changed the roles and rules |
| 20 Oct 2026 | Joseph | Claude Code | Wrote `knowledge/` (brief and syllabus as markdown, lecture notes, derivations, regulation and fairness notes, recording summaries) using subagents | Chose what to include; asked for transcripts to be replaced by summaries. **Each owner still needs to check the files on their reading list.** |
| 20 Oct 2026 | Joseph | Claude Code | Data checks (counts and aggregates only, run locally) and `docs/01_data.md` | Downloaded the data; confirmed the checks |
| 21 Oct 2026 | Joseph | Claude Code | Reviewed Liza's steps 3–4: reran the notebooks and recomputed the headline numbers | Decided the merge and the review notes |
| 23 Oct 2026 | Joseph | Claude Code | Step 5 code in `src/features.py` (history, calendar, macro, folds, self-checks) and the first validation comparison | Made each design decision (history definition, fill-in rule, windows, extra cases); learning each part step by step |
| 23 Oct 2026 | Joseph | Claude Code | `AGENTS.md`, `CLAUDE.md`, ADRs 0001–0011, this log | Set the rules the files encode |
| — | Liza | *(please add)* | Steps 3–4 | |
