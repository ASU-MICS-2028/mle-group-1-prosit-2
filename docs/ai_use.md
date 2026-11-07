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
| 27 Oct 2026 | Germain | ChatGPT | Generated experiment-runner and documentation drafts; assisted with debugging and interpreting model comparisons | Executed scripts and notebook locally, verified reported outputs, corrected variable collision and reviewed limitations |
| 28 Oct 2026 | Joseph | Claude Code | Reran Germain's step 7 from a clean copy; added the cut-off policy test and per-block model comparison; updated ADR 0016, learnings/07, tracker and README | Accepted LR + Platt and the 2.1% / 3.2% cost cut-off; set new due dates for steps 8–11 |
| 29 Oct 2026 | Joseph | Claude Code | Found the Ghana-history error and the step 7 calibration bug; wrote src/reasons.py, the 02b notebook, learnings/08 and ADR 0017 | Took over step 8 from Germain; approved the calibration fix, 5 themes and the 0.2 minimum push |
| 4 Nov 2026 | Alice | Claude Code | At Alice's request, built steps 9 and 10 in full: notebooks 03 and 04 (Part 1), `src/amounts.py`, ADRs 0018–0019, learnings 09–10, tables and figures. Only aggregates were shown to the AI; no data rows | Alice to review every part step by step in a walkthrough and confirm or change the two Proposed ADRs before merging |
| 5 Nov 2026 | Joseph | Claude Code | Built step 11 in full: notebook 04 Part 2, ADR 0020, learnings/11, Model Card, datasheet, compliance map, borrower letter. Only aggregates were shown to the AI; no data rows. Findex codes checked against published figures by web search | Took over step 11; approved the plan; reviews the choice of fairness priority and the two fixes |
| 6 Nov 2026 | Joseph | Claude Code | Wrote `src/fairness_scenarios.py` (1,224 scenarios) and the Ghana probe; turned Zindi scores into group default rates; updated ADRs, learnings and the Model Card. Only aggregates were shown to the AI | Asked for every scenario to be tested; accepted the Kenyan decision; uploaded the probe files |
| 7 Nov 2026 | Joseph | Claude Code | Wrote `read_exact` in `src/zindi_submissions.py` (exact counts, 2,916 Ghana scenarios) and drafted ADR 0021 and learnings/11 §10b. Only aggregates were shown to the AI | Uploaded batch 2; decides on ADR 0021 |
| 7 Nov 2026 | Joseph | Claude Code | Wrote `src/ghana_rule_tests.py`, the pass rules, the results index and the ADR 0021 test write-up. Only aggregates were shown to the AI | Set the condition that the rule must be shown to work; decides whether 4 of 6 is enough |
