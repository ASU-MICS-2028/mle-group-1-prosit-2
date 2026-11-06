# Datasheet: the data behind the NkwaPay models

*Following Gebru et al. (2021). We didn't create these datasets, so many answers are "unknown". Those unknowns are findings in their own right. Counts come from [`docs/01_data.md`](01_data.md).*

## Part 1: Zindi African Credit Scoring Challenge

### Motivation
- **Why was it made?** For a machine-learning competition on predicting loan default. We use it as NkwaPay's stand-in loan book.
- **Who made and funded it?** Hosted by Zindi. The competition terms call the data "private property of the client". The client's identity is **unknown to us**.

### Composition
- **What is one row?** One loan and lender pair. A loan shared between lenders has several rows (920 loan IDs appear in both files).
- **How many?** Train: 68,654 rows, 1,258 defaults (1.83%), Kenya only. After removing 190 loans not yet due: 68,464 loans, 6,508 customers. Test: 18,594 rows, no labels: 15,069 Kenyan and 3,525 Ghanaian (446 customers).
- **Representative?** **Unknown, and probably not.** Sampling isn't described. 92% of loans were sent in Jul–Dec 2022, and it holds only people lenders chose to lend to.
- **Label:** `target`, 1 = defaulted. The exact definition (days late, recoveries) is **not documented**.
- **Missing:** no blank cells in the raw files. In practice, **no Ghanaian has a known repayment outcome**.
- **Known errors or traps:**
  - `Total_Amount_to_Repay` and `Lender_portion_to_be_repaid` include post-default penalties, so they leak the answer (PR-AUC 0.20 → 0.91);
  - currency isn't stated: we assume local currency;
  - the brief's `ProductCategory` and `IsDefaulted` don't exist in the data.
- **Subpopulations:** country, loan type, lender, new or repeat, loan size. **No gender, age, income or location.**
- **Could people be re-identified?** Customer IDs are anonymous, but repeated dates and amounts make a loan history fairly distinctive. So we treat rows as personal financial data.
- **Sensitive?** Yes, financial data.

### Collection
- **How, when, by whom?** Loans sent Oct 2021 – Nov 2024. Method and collector **unknown**.
- **Consent and notice?** **Unknown.** We don't know whether borrowers were told or agreed to this use, or could withdraw. Ghana's Act 843 s.18(2) requires data about foreign people to be handled under their own law, which we can't confirm.
- **Ethical review or impact assessment?** **Unknown.** The BoG Directive requires a DPIA for a licensed lender (para. 2.1(5)(d)).

### Preprocessing
- **What we did:** a feature audit (`learnings/03`); removed leaky columns and 190 not-yet-due loans; built borrower history counting a past loan only after its due date (`src/features.py`).
- **Raw data kept?** Yes, in `data/`, which is never committed.
- **Code:** public, in `src/` and `notebooks/`.

### Uses
- **Used for:** this project's default and amount models, and the fairness audit.
- **Could cause unfair treatment:** first-time borrowers and small products are thin in the data, and Kenyan patterns may not apply elsewhere ([ADR 0019](adr/0019-kenya-to-ghana-transfer.md)).
- **Should not be used for:** scoring real borrowers without new consent and validation; pricing; identifying anyone; judging groups it doesn't record, like gender.

### Distribution
- Zindi account and competition rules. We redistribute nothing: the repository is public, and only aggregates are published. Raw rows aren't uploaded to AI tools.

### Maintenance
- We don't maintain the source. No known errata process. The competition closed on 12 Jan 2025; late scoring still works. Local copies should be deleted when the course ends.

## Part 2: Global Findex Ghana 2021

- **Motivation:** made by the World Bank to measure financial inclusion. We use it to describe who lacks credit in Ghana (Part D4).
- **Composition:** one row per surveyed adult; 1,000 people, 120 columns, with weights (`wgt`). Includes gender, age, education, income quintile and rural/urban. **No region.**
- **Collection:** a national survey, 2021. Weighted shares match published figures (68% any account, 60% mobile money, 74.2% of men with an account).
- **Preprocessing:** none beyond recoding answers. All results are weighted.
- **Uses:** population context only. **It can't be linked to borrowers** and doesn't test our model.
- **Distribution:** World Bank Microdata Library; registration required. We publish aggregates only.
- **Maintenance:** by the World Bank. Rural/urban and education codes should be confirmed with the codebook, which we haven't downloaded.
