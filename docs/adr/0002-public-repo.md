# 0002 · The repo is public: what may and may not go in it

- **Status:** Accepted
- **Date:** 20 Oct 2026 · **Owner:** Joseph · **Step:** setup

## Context
`ASU-MICS-2028/mle-group-1-prosit-2` is **public**. Anything committed can be read by anyone, and git keeps it in history even after deletion. We wanted teammates to have all course context without depending on one person's laptop.

## Options we tested
| Option | Problem |
|---|---|
| Commit the original slides, books, syllabus, brief PDF | Copyright; the syllabus has staff contact details; ~80MB of binaries |
| Make the repo private | Needs org admin; graders need access |
| Commit full lecture transcripts | Everything said in class becomes public, including classmates. We did this briefly, then reversed it. |
| **Write our own markdown summaries in `knowledge/`; keep originals out** | Chosen |

## Decision
- `knowledge/` holds **our own-words markdown** only: the brief, course rules (no contact details), lecture notes, recording summaries, derivations, regulation and fairness readings.
- **Never commit** original course files, data, personal data or staff contacts.
- The full transcripts were removed and the commit rewritten (force-push, 20 Oct). The old commit may still be reachable on GitHub by its exact ID until GitHub support purges it.

## Consequences
- Some summaries were written with AI help, so each owner should check the ones on their reading list (see [`docs/ai_use.md`](../ai_use.md)).
- Our copy of *Hands-On ML* turned out to be a 38-page appendix only, so those notes come from the chapter list.

## Links
[`knowledge/README.md`](../../knowledge/README.md)
