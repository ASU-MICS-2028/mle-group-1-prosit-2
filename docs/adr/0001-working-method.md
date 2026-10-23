# 0001 · How we work: steps, owners, tests, write-ups

- **Status:** Accepted
- **Date:** 18–23 Oct 2026 · **Owner:** Joseph (agreed by the group) · **Step:** all

## Context
Four people, 16 days, one graded debrief where each of us must defend the *whole* project without AI. Nobody has time to redo anyone else's work, so we must be able to trust and understand each other's results quickly.

## Options we considered
| Option | Problem |
|---|---|
| Everyone works on everything | Duplicate work; in Prosit 1 all commits came from one account, which costs "even contribution" marks |
| Split work, share only final results | Others can't defend what they don't understand |
| **Split into numbered steps with one owner each; every step tested, decided, and explained in plain words** | Chosen |

## Decision
1. **Work is split into 13 numbered steps,** each with one owner, tracked in [`docs/plan.md`](../plan.md).
2. **The README shows only the current step and its owner** (the **Now** box), so one glance tells anyone where we are. The brief also requires the README to say how to reproduce the work, so a short "Run it" section stays.
3. **Every choice is tested, not assumed:** each step compares the reasonable options in a table and picks a winner with numbers.
4. **Five kinds of writing, each with one home:**
   - decisions → `docs/adr/` (this format);
   - actions → `docs/log.md`;
   - AI use → `docs/ai_use.md`;
   - what we learned → `learnings/NN_<step>.md`, in the simplest possible language;
   - course knowledge → `knowledge/`.
5. **Work happens one small step at a time,** each explained before moving on, so the owner learns it well enough to defend it.

## Consequences
- More writing, but anyone can present any part.
- A step isn't done until its `learnings/` file exists and the README's Now box has moved on.

## Links
[`AGENTS.md`](../../AGENTS.md) · [`learnings/README.md`](../../learnings/README.md)
