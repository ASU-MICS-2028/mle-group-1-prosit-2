# 0011 · Git workflow: own branch, review, merge

- **Status:** Accepted
- **Date:** 21 Oct 2026 · **Owner:** group · **Step:** all

## Context
"Even contribution" is graded, and it shows in commit history. In Prosit 1, all commits came from one account. Liza worked on her own branch, and it was reviewed and merged cleanly.

## Decision
1. **Each member works on their own branch** (`liza`, `alice`, `feature/germain-classification`, ...) and commits from their own GitHub account.
2. **When a step is done,** another member reviews it: they rerun the notebook from a fresh checkout and spot-check the headline numbers. Then they merge it into `main` (fast-forward if possible) and log the review.
3. **Never rewrite `main`'s history** without telling the group. We did it once (20 Oct) to remove the transcripts; anyone who had pulled needed `git fetch && git reset --hard origin/main`.
4. **Pull `main` into your branch** before starting a new step.

## Links
[`docs/log.md`](../log.md)
