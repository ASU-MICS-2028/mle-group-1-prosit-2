# Learnings

Each member fully explains here what they did and what they found, so everyone else can **read it and understand it without rerunning anything**. We present and defend each other's work in the debrief, so these write-ups are what the rest of us learn from.

- `docs/` records **what was done and how** (the log and the procedure).
- `learnings/` explains **what it means**: results, decisions and lessons, in plain words.

## The rule

**Every step you own ends with a file here, `NN_<step>.md` (step number from the main README), before you tick the step.** For example: `03_feature_audit.md`, `04_cost_matrix.md`, `07_classification.md`.

**Write in the simplest language you can.** Imagine explaining it to a smart friend who has never taken this course:
- Short sentences, everyday words, one idea per sentence.
- No jargon unless you need it, and if you do, explain it in one plain sentence right there.
- Use a small concrete example ("a borrower who took 3 loans before...") whenever an idea is abstract.
- Steps in order, numbered, so the reader can follow them.
- If a teammate has to read a paragraph twice, rewrite it.

It must also be readable on its own:
- **Paste in the actual results.** Tables, key numbers and figures (save figures to `learnings/figures/` and embed them), so nobody has to open or run the notebook.
- **Explain every term** the first time it's used, as if to a teammate who missed the lecture.
- **Show the alternatives you tried,** not just the winner: what each gave, and why the winner won.
- **Say what you're unsure of** and what would change your conclusion.

## Template

```markdown
# NN · <Step name> (<your name>)

## What the others need to know
<5–10 bullets. If someone reads only this, they can present your part.>

## The question
<What this step had to answer, and why it matters for NkwaPay.>

## What I did
<The approach in plain steps. Link the notebook for anyone who wants the code.>

## What I tried and what happened
| Option | Result | Verdict |
|---|---|---|
| ... | ... | ... |
<Then a paragraph: what the table means in plain English.>

## Decision
<What we're going with, and why.>

## What I'm unsure of / limits
<Caveats, small samples, assumptions.>

## Likely Q&A questions and answers
<3–5 questions the panel might ask about this step, with short answers.>
```
