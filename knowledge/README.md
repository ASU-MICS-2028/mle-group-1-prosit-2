# Knowledge

Everything you need to understand Prosit 2 and do your part, without needing anyone else's laptop or folders. All of it is markdown written for this repo. The original slides, books and PDFs are **not** here: the repo is public and they are copyrighted or contain staff contact details.

**Rule:** if something here is wrong or unclear, fix it and log the fix in [`docs/log.md`](../docs/log.md).

## What's here

| File | What it is |
|---|---|
| [`prosit2_brief.md`](prosit2_brief.md) | **The assignment, in full.** Start here. |
| [`course_essentials.md`](course_essentials.md) | The syllabus rules that affect us: late penalty, **AI policy (never upload the raw data to AI tools)**, grading, readings |
| [`derivations.md`](derivations.md) | Step-by-step derivations: linear regression (MLE → normal equations, Ridge), logistic regression (log-odds, MLE, gradient, why class weights distort probabilities), gradient boosting, tree splits and pruning, SVM |
| [`books.md`](books.md) | Chapter map of ISLR/ISLP and Hands-On ML: what each chapter covers, which step it serves, who needs it |
| [`regulation.md`](regulation.md) | BoG Digital Credit Directive, Data Protection Act 843, Credit Reporting Act 726: section-by-section requirements, what each means for our model, and what we can't satisfy |
| [`fairness_reading.md`](fairness_reading.md) | Model Cards, Datasheets, Gender Shades, *Fairness and ML*: what to use and how it applies to our groups |
| [`lectures/`](lectures/) | Plain-language notes on each lecture's slides, each ending with "How this applies to Prosit 2" |
| [`lecture_recordings/`](lecture_recordings/) | Summaries of the recorded lectures: the recording's auto-summary plus our own summary, including what the lecturer said about the prosits. The full transcripts are not published. |

## Read this first (everyone, ~1 hour)
1. [`prosit2_brief.md`](prosit2_brief.md)
2. [`course_essentials.md`](course_essentials.md), especially the AI policy.
3. [`lectures/03_preprocessing_and_leakage.md`](lectures/03_preprocessing_and_leakage.md). Leakage is the main trap in this prosit.
4. [`../docs/01_data.md`](../docs/01_data.md): what the data actually contains.

## Then, by role

| Who | Read | For |
|---|---|---|
| **Liza** (framing, feature audit, cost matrix, fairness, compliance) | `lectures/03_preprocessing_and_leakage.md` · `regulation.md` · `fairness_reading.md` · `prosit2_brief.md` Appendix A (cost matrix) · `books.md` (ISLR Ch 4 on classification errors) | Steps 3, 4, 11 |
| **Germain** (classification) | `derivations.md` §b (logistic) and §c (boosting) · `lectures/04_supervised_learning.md` · `lectures/05_supervised_learning_survey.md` · `lectures/01_probability_and_sampling.md` (bootstrap) · `books.md` (ISLR Ch 4, 5, 8, 9) | Steps 6–8 |
| **Alice** (regression, transfer) | `derivations.md` §a (linear) · `lectures/04_supervised_learning.md` · `lectures/07_mit_6390_relevant_chapters.md` · `books.md` (ISLR Ch 3, 6) · `fairness_reading.md` (proxies, for the domain classifier) | Steps 9, 10 |
| **Joseph** (pipeline, validation, scorer) | `lectures/03_preprocessing_and_leakage.md` · `lectures/05_supervised_learning_survey.md` · `books.md` (ISLR Ch 5 on cross-validation) · `regulation.md` (what the scorer must output) | Steps 5, 12 |

## Known gaps
- **Hands-On ML:** our PDF copy is only a 38-page online appendix, not the book. The HOMLP notes in `books.md` come from the official chapter list and need checking against a library copy. ISLR is complete and free at <https://www.statlearning.com>.
- **Some regulation instruments are unverified:** the Borrowers and Lenders Act 2020 (Act 1052), the Credit Reporting Regulations 2020 (L.I. 2394) and BoG's 2017 disclosure rules were not read. They are marked unverified in `regulation.md`.
- **Errors in the slides:** the lecture notes flag slide mistakes they found (e.g. the one-hot example, the binomial exponent) rather than silently copying them.
- **Some intro slides were images only** and couldn't be read; they're listed in `lectures/00_introduction.md`.
- **Lecture numbering:** the recording summaries are numbered by recording date and don't line up with the slide decks. Each file's title says what it covers.
