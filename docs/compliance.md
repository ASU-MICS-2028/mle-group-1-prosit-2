# Compliance map and borrower letter

*What the design meets and doesn't meet under Ghanaian law. Clause detail and sources are in [`knowledge/regulation.md`](../knowledge/regulation.md). We are students, so this isn't legal advice. We did not read Act 1052, L.I. 2394 or BoG's 2017 disclosure rules, which may add requirements.*

**Worth noting:** the BoG Directive has no rule on algorithms, fairness or automated decisions. Fairness here rests on its consumer-protection goals and on Act 843.

## What the design meets

| Requirement | Source | How |
|---|---|---|
| Explain the logic of an automated decision | Act 843 s.35(1)(d) | Up to 3 plain reasons per decision; they add up exactly to the model's score ([ADR 0017](adr/0017-reason-codes.md)) |
| Clear, accurate, not misleading information | Directive 6(1)(a), (d) | Reasons use the applicant's own numbers; every sentence is tested in `src/reasons.py` |
| No contacts or social-media data | Directive 7.2(c)–(d) | Not used |
| No race, ethnicity, religion or politics | Act 843 s.37; Act 726 s.24(4) | Not in the data or the clues |
| Don't penalise new borrowers unfairly | Act 726 s.21(1)(p), in spirit | Starter loan rather than a decline ([ADR 0020](adr/0020-fairness-mitigation.md)) |
| Responsible credit | Directive 1.3 | "Borrow often" clues removed; capped first loans |
| Keep personal data secure | Act 843 s.28 | No rows in the public repository; aggregates only |

## What the design doesn't meet yet

| # | Requirement | Source | Gap | What would fix it |
|---|---|---|---|---|
| 1 | **Search a credit bureau before every decision** | Act 726 s.26(4) | **The clearest gap.** No bureau feed; only the lender's own records | A bureau check before scoring, with consent (s.26(1); Directive 7.3) |
| 2 | Handle foreign data under its own law | Act 843 s.18(2) | Consent for the Kenyan data is unknown | Retrain on NkwaPay's own consented data |
| 3 | Register with the DPC; an approved DPIA | Act 843 s.27, s.46; Directive 2.1(5)(d) | Organisational; can't be done by a student project | The Model Card and datasheet feed the DPIA |
| 4 | Review route; complaints resolved in 20 days | Act 843 s.41; Directive 6(1)(e) | The scorer has no appeal path | A digital "ask for review" step and a log |
| 5 | **Review must be digital** | Directive 2.3(1) | ADR 0019 says "manual review"; the physical office can't do it | Use a starter loan or digital review only |
| 6 | Keep decision records | Act 843 s.24, s.35; Act 726 s.35 | The scorer returns a result but stores nothing | An append-only log of inputs, version, score, cut-off, reasons, consent |
| 7 | Single-customer limit | Directive 3.5(5) | BoG's figure isn't published in the Directive; the limit has no cap | A configurable cap, once known |
| 8 | Avoid over-indebtedness and stacking | Directive 1.3(3), 7.1(2); Act 1052 unverified | Can't see other lenders' loans; no income data | Bureau data; affordability check |
| 9 | Valid for Ghanaian borrowers | Directive 3.5(1), 4(2) | Never tested on Ghanaian outcomes | Capped pilot; the [ADR 0019](adr/0019-kenya-to-ghana-transfer.md) trust gates |
| 10 | Total-cost and no-compounding disclosure | Directive 6(1)(b)–(c), 7.1(3) | Outside the model | The app shows amount, due date and total repayable |
| 11 | Gender fairness (asked by the brief, not found in these laws) | Brief Part D | No gender in the data | Audit it if collected (Act 726 s.24(2)(f)) |

## Letter to a declined borrower

The reasons come from `src/reasons.py`. This applicant is made up.

> **We could not approve this loan today.**
>
> This was an automated decision. The main reasons were:
> 1. This kind of loan (Type_7) has been repaid less often than others.
> 2. The loan is for 30 days; longer loans are repaid less often.
> 3. Your most recent loan (9,000) was larger than your usual loan (3,000).
>
> **What you can do**
> - You can ask us to explain or review this decision. Reply HELP. We will answer within 20 days.
> - You can ask to see the information we hold about you, and to correct it.
> - You may complain to the Bank of Ghana.
>
> This decision doesn't stop you from applying again.

**And for a first-time applicant,** who gets a smaller loan rather than a no:

> **We can offer you a starter loan of GHS 300 today.**
>
> This was an automated decision. This is your first loan with us, so we have no borrowing history to go on. Repaying on time helps us offer you more.
>
> Before you accept, we will show you the amount, the due date and the total you must repay. You can ask us to explain or review this decision by replying HELP, and we will answer within 20 days.

**Why the first-time letter is a loan, not a no:** our notes warn against "you are a new customer" as the only reason for a decline (Act 726 s.21(1)(p), in spirit). Without the starter loan, that is what first-timers would get. With it, the sentence explains a smaller amount, not a refusal.

**Wording rules:** no blame; no protected traits; never tell someone to borrow more to qualify; never reveal the model's weights (Act 843 s.35(2) allows this).
