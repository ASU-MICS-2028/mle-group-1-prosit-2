# Architecture Decision Records (ADRs)

Every real decision gets a short record: what we decided, which options we tested (with numbers), and why. Copy [`0000-template.md`](0000-template.md), give it the next number, and add a row below. If a decision changes, write a new ADR and mark the old one **Replaced by NNNN**.

| # | Decision | Owner | Status |
|---|---|---|---|
| [0001](0001-working-method.md) | How we work: steps, owners, tests, write-ups | Joseph | Accepted |
| [0002](0002-public-repo.md) | The repo is public: what may and may not go in it | Joseph | Accepted |
| [0003](0003-data-handling.md) | How we handle the data | Joseph | Accepted |
| [0004](0004-shared-feature-code.md) | All features come from one file: `src/features.py` | Joseph | Accepted |
| [0005](0005-feature-audit.md) | Which columns the model may use (feature audit) | Liza | Accepted; calendar part replaced by 0012 |
| [0006](0006-label-and-not-yet-due-loans.md) | What "default" means, and the 190 loans that weren't due yet | Liza | Accepted |
| [0007](0007-cost-matrix-and-cutoff.md) | The cost of each mistake and the decline cut-off | Liza | Accepted |
| [0008](0008-borrower-history.md) | How borrower history is built (time-safe) | Joseph | Accepted |
| [0009](0009-macro-clues.md) | Macro clues (inflation, interest, exchange rate, unemployment) | Joseph | Accepted; not used in the model (see 0012) |
| [0010](0010-validation-tests.md) | How we test models fairly (validation) | Joseph | Accepted; time test corrected by 0014 |
| [0011](0011-git-workflow.md) | Git workflow: own branch, review, merge | Group | Accepted |
| [0012](0012-final-feature-set.md) | The final feature set (step 5.5) | Joseph | Accepted |
| [0014](0014-time-test-known-outcomes.md) | The future-loans test only learns from finished loans | Joseph | Accepted |
