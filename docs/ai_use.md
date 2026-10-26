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
| 23 Oct 2026 | Joseph | Claude Code | Wrote and ran the step 5.5 comparison grid and bootstrap; drafted ADR 0012 | Asked for every combination to be tested; reviewing results and the decision |
| 23 Oct 2026 | Joseph | Claude Code | Built and ran `notebooks/01_eda.ipynb`, made the figures, drafted `learnings/05_features.md` and the step 6 handover | Reviewing the write-up; learned each part step by step; needs a teammate review of step 5 (ADR 0011) |
| 2026-10-26 | Germain | ChatGPT | Explained dataset checks, validation results and drafted initial documentation | Executed verification code locally and reviewed the reported counts and split checks |
| 2026-10-26 | Germain | ChatGPT | Explained four-fold classification metrics and drafted the result interpretation | Ran training and validation locally; checked outputs against the recorded metrics |
| 2026-10-26 | Germain | ChatGPT | Assisted with calibration diagnostics, interpretation and documentation | Executed checks locally and reviewed the reported counts; calibration decision pending |
| 2026-10-26 | Germain | ChatGPT | Helped interpret monthly default patterns and calibration results; drafted documentation | Executed experiments locally and supplied actual results; final model decision pending |
| 26 Oct 2026 | Germain | ChatGPT assisted with provisional classification implementation, diagnostic interpretation, OOF generation and ADR drafting; Germain executed and verified the scripts locally. | Step 6 |
| 26 Oct 2026 | Germain | ChatGPT assisted with full-data provisional refit code and documentation; Germain executed and verified results locally. | Step 6 |
| 26 Oct 2026 | Joseph | Claude Code | Reviewed Germain's branch; found and fixed the time-split leak; reran step 5 and updated learnings/05 and ADRs 0010, 0012, 0014 | Decided to fix the leak and accept the review changes; Germain's extension set to end of 26 Oct |
| 26 Oct 2026 | Joseph | Claude Code | Tested each of Germain's review points against code and data; implemented ADR 0015 fixes; reran step 5; updated learnings/05 and ADRs | Approved the four fixes; reviewing the results before replying to Germain |
