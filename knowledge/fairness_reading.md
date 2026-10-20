# Fairness readings, summarised for Part D

These are the four readings Part D relies on, written in plain words. For each one: the core idea, the parts we actually use, and how it applies to the NkwaPay credit model. All four were read from the original papers or book chapter (links below). Quotes are kept to a few words.

**Our setting, which every section below refers back to**
- **Target:** `target = 1` means the loan defaulted. The model gives a score R = estimated P(default), and we **decline** when R ≥ threshold t.
  - Defaults are rare, about 1 in 50.
  - Training data is all Kenya; NkwaPay will lend in Ghana.
- **Groups we can measure:**
  - `country_id`: Kenya vs Ghana. Only in Test, and Ghana rows have no labels.
  - `loan_type`
  - `lender_id`
  - `New_versus_Repeat`
  - loan-size band, which we build by bucketing `Total_Amount`
- **Group we cannot measure per borrower:** gender. We only have the World Bank Findex Ghana survey, which gives population-level gender gaps.

**Watch the sign convention.** In fairness texts, the "positive" outcome is usually the good one, such as being hired or getting a loan. In our data the positive class `target = 1` is the **bad** one (default). This guide always says in words which error it means:
- **Wrongly declined** = a good payer we said no to (a false positive for "default"). This is the harm to the borrower: they are shut out of credit.
- **Wrongly approved** = a defaulter we said yes to (a false negative). This is a harm to the lender, and to the borrower too, because it adds debt they can't repay.

---

## 1. Mitchell et al. (2019), "Model Cards for Model Reporting"

Link: <https://arxiv.org/abs/1810.03993>. Published at FAT* 2019.

**Core idea.** A trained model should ship with a short document, like a nutrition label. It says what the model is for and not for, and how well it works **for each relevant group of people**, not just on average. Their two examples are a smile detector and a toxic-comment classifier, but they say the format fits any model.

**The section list.** Use this exact structure for our Model Card (paper, Fig. 1):

| Section | Sub-items | What we put there |
|---|---|---|
| **Model Details** | Who built it; date; version; model type; training algorithm, parameters, **fairness constraints**, features; paper or link; citation; licence; contact | Group 1, Ashesi ICS553, Oct 2026. Logistic regression or gradient boosting (name the final one). Feature list from `docs/02_feature_audit.md`. Any mitigation applied |
| **Intended Use** | Primary uses; primary users; **out-of-scope uses** | Use: approve or decline a short (7–90 day) mobile-money loan for NkwaPay in Ghana, with reasons. Out of scope: other countries or products, loans over 90 days, business loans, setting interest rates, collections, marketing. Also out of scope: Ghana use **without** local monitoring |
| **Factors** | **Relevant factors** (groups where performance might differ, and how we chose them) vs **evaluation factors** (the ones actually reported, and why any differ) | Relevant: country, new vs repeat, loan type, lender, loan size, **gender**. Evaluated: all except gender, which has no column. We must say this gap openly; the paper asks for exactly that |
| **Metrics** | Performance measures and why; **decision thresholds** and why; how uncertainty was measured | ROC-AUC, PR-AUC (better for 2% defaults), wrongly-declined rate, wrongly-approved rate, and expected cost from our cost matrix. Explain the threshold from the cost matrix. Bootstrap CIs |
| **Evaluation Data** | Datasets; why chosen; preprocessing | Held-out Kenyan folds, plus the Ghana Test rows (unlabelled, so only score distributions and approval rates) |
| **Training Data** | Same as above if possible; at least the group distribution | Zindi Train: counts per group and default rate per group |
| **Quantitative Analyses** | **Unitary results** (each factor alone) and **intersectional results** (combinations) | Tables per group and per pair of groups (see "Disaggregated evaluation" below) |
| **Ethical Considerations** | Sensitive data? Affects human life? Mitigations? Risks and harms? Fraught use cases? | Credit access, debt traps, Kenya-to-Ghana shift, new-borrower penalty, proxies for country |
| **Caveats and Recommendations** | Further tests needed? Groups missing from evaluation? Ideal evaluation set? | No gender, no Ghana labels, no bureau data; retrain on Ghanaian outcomes |

**Parts we must actually use**
- **Disaggregation.** Results must be "broken down by the chosen factors" (s.4.7). An overall AUC alone is not enough.
- **Intersectional results.** For example, new **and** Ghana, or a large loan **and** a new borrower. Problems often hide where groups overlap.
- **Classification error types** (s.4.4.1): false positive rate, false negative rate, false discovery rate, false omission rate.
  - The paper notes that equal false negative rates across groups is "equality of opportunity", and equal FNR **and** FPR is "equalized odds" (both from Hardt et al. 2016).
  - Report all four, and say which one we prioritised and why.
- **Score-based analysis** (s.4.4.2). For a risk score, compare the score **distributions** across groups (median, quartiles), not only the yes/no outcomes.
- **Confidence intervals** (s.4.4.3). The more finely you split the data, the more you need CIs.
  - This is critical for us. At 2% defaults, a group of 2,000 loans has about 40 defaults, so a group's TPR comes with a wide interval.
  - Bootstrap each metric and show error bars.
- **Thresholds.** Say what the threshold is and why. The paper even suggests a threshold slider; a plot of metrics against threshold does the same job.

---

## 2. Gebru et al. (2021), "Datasheets for Datasets"

Link: <https://arxiv.org/abs/1803.09010>. Published in *Communications of the ACM*, 64(12), 2021; arXiv v8 dated Dec 2021.

**Core idea.** Electronic parts come with a datasheet saying how they were made, what they're tested for and where they shouldn't be used. Datasets should too. The **creator** answers a fixed set of questions so the **user** can decide whether the data fits their task, and to expose hidden biases and legal limits. The authors say the questions are a guide, not a form: skip what doesn't apply, but answer as many as possible. "Unknown" is an acceptable answer, and they use it themselves in their worked example for a dataset they didn't create.

**The seven question groups** (paper ss.3.1–3.7). Each line gives a few key questions, then **what to write for Zindi + Findex**:

1. **Motivation.** Why was it made, by whom, and who paid for it?
   → Zindi "African Credit Scoring Challenge". Find and record who supplied the loan book. Findex was made by the World Bank to measure financial inclusion.
2. **Composition.**
   - What is one row? How many rows? Is it a sample, and is it representative?
   - What is the label? What's missing? Are there recommended splits, errors, noise or redundancy?
   - Does it depend on external resources? Is anything confidential?
   - Does it identify **subpopulations**? Could individuals be **re-identified**? Is there **sensitive** data (the paper explicitly lists **financial data** and government ID numbers)?

   → One row is one loan–lender pair. Several rows can share a `tbl_loan_id`, and one customer can have many loans. Train is Kenya only. Default rate about 2%. Subpopulations: country, loan type, lender, new/repeat. No gender or age. `customer_id` is pseudonymous, but linking it with dates and amounts may allow re-identification.
3. **Collection process.**
   - How was the data acquired and over what period? Who collected it?
   - Was there ethical review? Were people **notified** and did they **consent**, and could they revoke consent?
   - Was a **data protection impact analysis** done?

   → Mostly "unknown to us" for Zindi. Say so. This links to Act 843 s.18(2) (Kenyan law applies) and the DPIA the BoG Directive requires (para. 2.1(5)(d)(x)).
4. **Preprocessing, cleaning and labelling.** What was done? Is the raw data kept? Is the code available?
   → Our feature audit and leak removals, the date features, the bucketing into size bands. Everything is in `src/` and the notebooks. Raw data stays in `data/` and is not committed.
5. **Uses.** What has it been used for? What else could it be used for? Could its composition cause unfair treatment, and how can that be mitigated? **What tasks should it not be used for?**
   → Should not be used for: scoring borrowers outside East Africa without checking, pricing, or anything identifying.
6. **Distribution.** Is it shared, how, and under what licence? Are there IP restrictions or export controls?
   → Zindi competition terms; Findex terms (registration required). We redistribute nothing.
7. **Maintenance.** Who maintains it? Is there an erratum? How are updates made? Are there **retention limits** on people's data? Are old versions kept?
   → We don't maintain the source data. Our derived files follow Act 843 s.24 retention.

**How it applies.** We write **one datasheet**, covering the Zindi data as we used it, with a short Findex section. Many answers will be "unknown". That is honest and useful: the unknowns (consent, collection period, which lenders) are exactly the risks we should name in Part D.

---

## 3. Buolamwini & Gebru (2018), "Gender Shades"

Link: <https://proceedings.mlr.press/v81/buolamwini18a.html>. Published in PMLR 81 (FAT* 2018). Project site: <http://gendershades.org>.

**Core idea.** The authors tested three commercial face-analysis services that guess a person's gender.
- On average the services looked accurate. Split by **gender × skin type**, the picture changed:
  - Darker-skinned women had error rates **up to 34.7%**.
  - Lighter-skinned men had at most **0.8%**.
- The averages hid the gap because the standard benchmark datasets were mostly lighter-skinned people:
  - IJB-A was 79.6% lighter-skinned.
  - Adience was 86.2% lighter-skinned.
- To fix the measurement, they built a balanced test set, the **Pilot Parliaments Benchmark**: 1,270 parliamentarians from Rwanda, Senegal, South Africa, Iceland, Finland and Sweden.

**What to take from it**
1. **Audit the dataset first.** Before testing the model, they counted who was in the benchmarks. For us that means: how many rows per group, and how many **defaults** per group? A group with few defaults gives an unreliable error rate.
2. **Aggregate accuracy hides subgroup failure.** Always disaggregate.
3. **Intersectional analysis.** The worst group, darker-skinned women, only showed up when two factors were crossed. Either factor alone understated it.
4. **Report several metrics per subgroup.** They reported TPR, FPR, PPV and error rate (1 − TPR) for each subgroup.
5. **Use a measurable, stable attribute.** They chose a dermatology skin-type scale rather than race labels, because race categories are unstable across countries. For us: audit on groups that are observable and well defined (country, new/repeat, loan type), and be explicit about what each group really stands for.

**How it applies to us.** Our situation has the same shape:
- **Training data dominated by one population.** Kenya here, lighter-skinned faces there.
- **Deployment on another population.** Ghana here.
- **A strong overall score that may hide subgroup failure.** A model with a high AUC on Kenyan folds can still decline Ghanaian or new borrowers far more often for no good reason.

What to do:
- Check our test sets for Ghana, new borrowers and small loan types.
- Cross the groups:
  - `country × New_versus_Repeat`
  - `New_versus_Repeat × loan-size band`
  - `loan_type × country`
- Report several metrics per cell.

---

## 4. Barocas, Hardt & Narayanan, *Fairness and Machine Learning*, ch. 3 "Classification"

Link: <https://fairmlbook.org/classification.html>. Book: <https://fairmlbook.org> (MIT Press, 2023).

**Core idea.** A classifier usually works by putting a threshold on a **score** R. Once you add a sensitive group attribute A, the true outcome Y and the decision Ŷ, almost every proposed fairness definition turns out to be one of **three** statistical conditions, or a relaxed version of one. The three generally **cannot all hold at once**, so you have to choose.

**Notation**
- A = group
- Y = true outcome
- R = score
- Ŷ = decision
- "⊥" = "is independent of"
- "| Y" = "within each value of Y"

### The three criteria

| Criterion | Formula | Binary-decision version | In plain words | Our version (Ŷ = 1 means decline) |
|---|---|---|---|---|
| **Independence** (demographic parity) | R ⊥ A | P(Ŷ = 1 \| A = a) = P(Ŷ = 1 \| A = b) | Every group gets the same **approval rate**, whatever its real default rate | Equal approval rates for new vs repeat, Kenya vs Ghana, and so on |
| **Separation** (equalized odds; *equal opportunity* is the one-sided version) | R ⊥ A \| Y | Equal **TPR** and equal **FPR** across groups | Among people who **did** repay, every group is wrongly declined at the same rate. Among people who **didn't**, every group is caught at the same rate | Equal **wrongly-declined rate among good payers** (FPR for default) and equal **catch rate among defaulters** (TPR). The borrower-protecting half is equal FPR |
| **Sufficiency** (calibration by group, predictive parity) | Y ⊥ A \| R | Equal **PPV** and **NPV**. For scores: P(Y = 1 \| R = r, A = a) = r in every group | A given score **means the same thing** in every group: "5% risk" is really about 5% for each group | A predicted 5% default chance should match about 5% actual defaults among new **and** repeat borrowers. Check with a calibration curve per group |

Notes:
- **Calibration by group implies sufficiency.** The chapter shows that any sufficient score can be relabelled so it is calibrated by group.
- **Unconstrained risk scores tend to be roughly sufficient already**, because a good model learns the group effect from the features.
- **Separation is what you have to work for.**

### Why you can't have all three (the impossibility results)

All three results hinge on one thing: **unequal base rates**, meaning P(Y = 1 | A) differs between groups. For us, new and repeat borrowers almost certainly default at different rates, and Kenya and Ghana may too.

- **Independence vs sufficiency.** If the base rates differ (A and Y are dependent), both can't hold.
  - Equal approval rates force the score to mean different things in different groups.
- **Independence vs separation.** With a binary Y, if base rates differ and the score is at all useful (R depends on Y), both can't hold.
- **Separation vs sufficiency.** If base rates differ, both can't hold for a score where every event has positive probability.
  - For a binary classifier they also can't both hold if the false positive rate is non-zero.
  - Consequence: **a calibrated, accurate score will usually have unequal error rates across groups with different default rates.**

**What this means for the decision.** We must **pick a primary criterion and justify it**, then report the others so readers can see the trade-off:
- A reasonable choice for a lender bound by "responsible" credit and consumer-protection rules:
  - Keep **sufficiency/calibration**, so a score means the same risk for everyone.
  - Then check **separation's borrower-protecting half**: is the **wrongly-declined rate among good payers** much higher for new borrowers or for Ghana?
  - If it is, that is the harm to fix.
- **Independence** (equal approval rates) is usually not the right target when real default rates differ. It would approve risky loans in one group or refuse good ones in another. It is still worth **reporting**, because large approval-rate gaps are what borrowers and regulators see.

### Proxies and redundant encodings (the "just delete the column" fallacy)

- **Removing A from the features does not remove A from the model.** The chapter calls ignoring the attribute "fairness through unawareness" and argues it usually fails.
  - In a large feature space, many weak signals together can **redundantly encode** the group.
  - Their example: visiting a particular website is only slightly more common for one gender, but many such signals combined predict gender well.
- **Test for proxies by trying to predict the group from the other features.** If a classifier recovers A well (AUC well above 0.5), the model can effectively "see" A.
- **Not every correlate is illegitimate.** Forcing all features to be uncorrelated with A can hurt people when the correlation reflects a real cause.
  - For us: past repayment history correlates with new/repeat status, and it is a legitimate signal.
  - The question is whether a feature is **only** a stand-in for the group, or carries real information about repayment.

**Proxy analysis for our data**

| Group | Likely proxies | Check |
|---|---|---|
| Country (Ghana vs Kenya) | `lender_id` (Ghana uses different lenders), currency-scale amounts, `loan_type` mix, date ranges | In `Test.csv`: AUC of each feature alone, and of all features together, at predicting `country_id`. Also the domain classifier from the transfer study |
| New vs repeat | Any "past loans" history feature by construction; amount (first loans are often small) | Predict `New_versus_Repeat` from features excluding history. Report AUC |
| Gender | Not observable. Findex Ghana shows population-level gender gaps in mobile-money use and borrowing, so loan size, loan type or product choice *could* act as proxies | Cannot test per borrower. State this as a limitation. Optionally compare the model's approval rate by loan-size band with Findex gender patterns, as context only |

### The worked credit example in the chapter

- **The data.** The chapter compares decision rules on US FICO-based credit scores, about 174,000 people in four race groups (Federal Reserve data from 2003). Several rules are compared:
  - maximum profit with group-specific thresholds
  - a single threshold
  - independence
  - separation
- **The result.** Each rule produced visibly different error rates across groups.
  - Under the profit-maximising rule, one group's true positive rate was about twice another's.
- **The calibration lesson.** The score was roughly calibrated by group, but **turning a score into a yes/no at a threshold** can break calibration and change PPV across groups.
- **Applied to us.** Check fairness **at our chosen threshold**, not only on the raw score.

### Mitigation options

The chapter itself is about definitions. The standard families of fixes:
- **Pre-processing:** reweight or resample training rows so groups and outcomes are balanced.
- **In-processing:** add a fairness constraint or penalty while training.
- **Post-processing:** use **group-specific thresholds** chosen to equalise FPR and/or TPR. This is how the chapter's separation rule is built for the FICO data.

For us:
- **Post-processing by `New_versus_Repeat`** is simple and easy to explain. Using new/repeat status in a credit decision is ordinary practice and not a protected trait.
- **Thresholds by country** would mean treating Ghanaians differently by nationality. Harder to defend; avoid.
- **Whichever fix we choose, report before-and-after:**
  - the fairness metric
  - overall AUC and PR-AUC
  - expected cost from the cost matrix
  - approval rate per group

---

## 5. Checklist: what Part D needs from these readings

- [ ] Model Card with all 9 Mitchell sections, factors listed as relevant vs evaluated, and gender named as relevant but not evaluated.
- [ ] Datasheet using the 7 Gebru groups, with honest "unknown" answers on consent and collection.
- [ ] Group counts, default counts and default rate for each group before any modelling (the Gender Shades step: audit the data first).
- [ ] Per group, and for the main intersections:
  - [ ] approval rate (independence)
  - [ ] wrongly-declined rate among good payers, and catch rate among defaulters (separation)
  - [ ] PPV/NPV and a calibration curve (sufficiency)
  - [ ] AUC and PR-AUC
  - [ ] bootstrap 95% CIs on all of these
- [ ] A one-paragraph statement of which criterion we prioritise and why, citing the impossibility results.
- [ ] Proxy table: AUC for predicting country and new/repeat from the features.
- [ ] One mitigation, with before/after metrics and its cost.
- [ ] Link to `knowledge/regulation.md` for the legal side: Act 843 s.35(1)(d) for reason codes, and Act 726 s.21(1)(p) for the new-borrower principle.
