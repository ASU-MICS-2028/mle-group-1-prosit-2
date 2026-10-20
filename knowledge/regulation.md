# Ghanaian regulation that applies to the NkwaPay model

Read this instead of the three source documents. It covers the Bank of Ghana Digital Credit Directive, the Data Protection Act (Act 843) and the Credit Reporting Act (Act 726). For each one it says what the rule is, where it sits in the source, and what it means for our model and scoring service. The last part lists what our current design **cannot** satisfy, which Part D asks us to name.

**How this was checked (20 Oct 2026).** All three documents were read in full from the copies linked below. Every section number here was seen in those texts. Where a rule is missing from a document, the table says "not found" rather than guessing. This is a student summary, not legal advice.

**Words used below**
- **DCSP**: Digital Credit Services Provider, the Bank of Ghana's name for a lender like NkwaPay.
- **Data controller**: whoever decides why and how personal data is processed. Here that is NkwaPay.
- **Data subject**: the person the data is about, i.e. the borrower.
- **Credit bureau / credit reference bureau**: a licensed company that holds people's credit histories. Ghana's current bureaus are XDS Data, Dun & Bradstreet and My Credit Score, according to a 2026 BoG notice reported in secondary sources (not checked).
- **"s."** means section, and **"para."** means a numbered item in the Directive.

---

## 1. The three instruments at a glance

| | BoG Directive for Digital Credit Services Providers | Data Protection Act, 2012 (Act 843) | Credit Reporting Act, 2007 (Act 726) |
|---|---|---|---|
| **What it is** | A Bank of Ghana directive that sets the licensing and conduct rules for lenders who lend **only** through digital channels | Ghana's general privacy law. It set up the Data Protection Commission (DPC) and governs any processing of personal data | The law that sets up and regulates credit bureaus, and governs how lenders send data to them and use their reports |
| **Legal basis** | Issued under the Non-Bank Financial Institutions Act, 2008 (Act 774) (para. 1.4) | Act of Parliament | Act of Parliament. Partly amended by Act 843: s.98(3) of Act 843 repealed ss.34(1), 38 and 40 of Act 726 |
| **Who it applies to** | (1) A company that wants to operate only as a DCSP, and (2) a licensed DCSP (para. 1.6). "Digital credit" means short-term (under 12 months), low-value credit delivered through digital channels (para. 1.8). NkwaPay's 7–90-day mobile-money loans fit this definition | Every data controller that is set up in Ghana, uses equipment in Ghana, or processes data that comes wholly or partly from Ghana (s.45) | Credit bureaus, "data providers" (financial institutions and public sources) and credit report recipients (s.1, s.61). A BoG-licensed DCSP is a licensed non-bank financial institution, so we read it as a "financial institution" here. The s.61 definition still names older laws, so this is our interpretation |
| **Date** | Dated September 2025, in force **1 November 2025** (para. 1.7) | Assented 10 May 2012. Gazette notification 18 May 2012 | Assented 5 April 2007. Gazette notification 13 April 2007 |
| **Regulator** | Bank of Ghana | Data Protection Commission | Bank of Ghana |
| **Official link** | Notice: <https://www.bog.gov.gh/notice/directive-for-digital-credit-services-providers-in-ghana/>. PDF: <https://www.bog.gov.gh/wp-content/uploads/2025/09/FINAL-DIRECTIVE-FOR-DIGITAL-CREDIT-SERVICES-PROVIDERS_After-Stakeholder_15_09_25-NOTICE-30.pdf> | DPC: <https://dpc.gov.gh/>. Copy we read: <https://extranet.who.int/cpcd/sites/default/files/public_file_repository/GHA_Ghana_Data-Protection-Act_2012.pdf> (WHO legislation repository, scanned Act). Official record: <https://ghalii.org/akn/gh/act/2012/843> | Parliament record: <https://ir.parliament.gh/handle/123456789/1794>. Copy we read: <https://www.brr.gov.gh/acc/registry/docs/Credit%20Reporting%20Act,%202007%20(Act%20726)%20.pdf> (Registrar copy, **original 2007 text**, which does not show the 2012 repeals) |

**Related instruments we did not read.** The Directive tells DCSPs to read it together with several other instruments (para. 1.5). We did not open these, so nothing below depends on them:
- Borrowers and Lenders Act, 2020 (Act 1052). The Directive's credit policy must follow it (para. 7.1(1)). This is the most likely home of any affordability or over-indebtedness rule. **Unverified.**
- Credit Reporting Regulations, 2020 (L.I. 2394). This probably holds the dispute deadlines and data-submission formats. **Unverified.**
- BoG "Disclosure and product transparency rules for credit products and services", February 2017. This is the most likely home of any APR or effective-rate rule. **Unverified.**
- Cybersecurity Act, 2020 (Act 1038) and the BoG Cyber and Information Security Directive.
- Reports say a Data Protection Bill, 2025 is in draft. As far as we found, **Act 843 is still the law in force**.

---

## 2. BoG Directive for Digital Credit Services Providers (2025)

| Topic | Clause | What it says (plain English) | What it means for our model |
|---|---|---|---|
| Scope | 1.6, 1.8 | Applies to companies that lend only digitally. Digital credit means short-term (under 12 months), low-value credit | NkwaPay is in scope. Every rule below applies to the scoring service |
| Purpose | 1.3 | Objectives include consumer protection, "cost effective and responsible" digital credit, and better data privacy and security | We can cite "responsible" lending as the reason we care about wrongly approving people who then default |
| Licence file | 2.1(5)(d) | The licence application must include, among other things: a risk management policy (ii), ICT and information security controls (iii), terms and conditions (vii), a list of partners and third parties (viii), a **Data Protection Impact Assessment approved by the DPC** (x), a **Data Protection certificate** (xi), third-party certification against BoG standards (xii), and a **Digital Credit Policy** (xiv) | Our Model Card and datasheet are inputs to the DPIA and to the Digital Credit Policy. We have not done a DPIA, and DPC approval is outside our control |
| Approval must be digital | 2.3(1) | The physical office in Ghana is for operations, complaints and contact with BoG. It **must not** be used for manual onboarding, approval, disbursement, collection or recovery | Loan approval has to happen in software, so automated decisions are expected. Any human review of a decline also has to run through a digital channel |
| Single-customer limit | 3.5(5) | A DCSP must not lend one customer more than the limit set by the Bank | The loan-amount model (Task 1) must clip its output at the BoG limit. The limit is not stated in the Directive, so it is **unknown to us** |
| Technology | 3.5(1)–(4) | Systems must be tested, have fraud monitoring and third-party certification, give BoG access to accurate supervisory information, have backups and business continuity, and come with written operating procedures | The scorer needs logging, versioning and a documented runbook. The Model Card helps meet the documentation part |
| Outsourcing | 3.6 | Any outsourcing or partnership linked to providing credit needs **prior written BoG approval**. The DCSP stays responsible for the outsourced function | If the model is built or hosted by a third party (a vendor, a cloud scoring API, or us as contractors), BoG must approve it first. NkwaPay is still accountable for the model's decisions |
| Supervisor access | 3.7(4) | The DCSP must give BoG access to its premises, its core lending platforms and its operational systems | BoG can inspect the model. It must be explainable and documented, not a black box nobody can describe |
| Record keeping | 3.8(3) | Books of account and accounting records must be kept for at least 10 years | This covers accounting records, not model inputs. We may still want to keep decision logs for a similar period (see Act 843 s.24(4) and Act 726 s.35) |
| Risk management | 4(1)–(4) | Identify risks on an ongoing basis, put controls in place, protect customers against cyber attack, and follow BoG's Cyber and Information Security Directive | Model risk counts as one of these risks: drift, Kenya-to-Ghana shift and unfair outcomes. Monitoring after deployment is expected |
| KYC | 5(5)–(6) | Do know-your-customer and customer due diligence checks, and follow BoG's guidance on the Ghana Card | Identity checks come before scoring. They are not a model feature |
| Clear information | 6(1)(a), (d) | Give clear, comprehensive and accurate information about the credit and the customer's **rights and responsibilities**. Do not mislead | Our plain-language decline reasons must be accurate. Do not imply a reason that the model did not actually use |
| Pre-agreement | 6(1)(b) | Before the loan is concluded, send a digital pre-agreement showing (i) the principal, (ii) the disbursement schedule, (iii) the basis of any cost charged if the borrower fails to pay, (iv) fees and (v) any insurance | The scorer's "approve" output has to feed a pre-agreement screen. That is product work, not model work |
| Interest | 6(1)(c), 7.1(3)(b) | Disclose interest for the full tenure. Interest **must not be compounded** | If the model or pricing logic varies the price, it must be simple interest over the tenure. In our data, repay ÷ amount is the price |
| Total cost disclosure | 7.1(3)(a)–(d) | Disclose charges and fees and when they apply, the interest rate, the **total cost of credit** (principal + interest + fees + charges), and the due date | The disclosure is total cost in cedis. **"APR" is not used anywhere in the Directive.** An APR rule, if one exists, is probably in the 2017 transparency rules (unverified) |
| Complaints | 6(1)(e) | Provide ways to receive complaints and **resolve them within twenty days** | A borrower who disputes a decline needs a route in, with a 20-day clock. The scorer must log enough to answer the complaint |
| Receipts, no bundling | 6(1)(f)–(g) | Send electronic receipts for transactions. Do not force borrowers to buy bundled products | Do not make approval depend on buying insurance or other products |
| Credit policy and limits | 7.1(1)–(2) | The credit policy must follow the Borrowers and Lenders Act 2020. The DCSP may set credit limits, which must comply with BoG requirements | The threshold, cost matrix and limits we choose are part of the "credit policy" and should be written down as such |
| Debt collection | 7.2 (items 4a–f in the PDF) | During collection: no threats or violence, no obscene language, **no unauthorised calls or messages to the customer's contacts**, no unauthorised posts in public or on social media, no unconscionable tactics, no harassment | Do not build features or workflows that rely on a borrower's phone contacts or social graph. Our Zindi features do not use them, so we are fine. Collection is outside the model |
| Report to bureaus | 7.3 (items 5–9 in the PDF) | Submit customer information to licensed credit bureaus **daily**. Make it complete and accurate. **Get the customer's consent before sharing.** Consent may be oral, print or electronic, as long as the DCSP is satisfied an electronic consent is genuine | The scoring service needs a consent flag and a daily bureau export. That is outside the model, but the Model Card should mention it |
| Penalties | 8 | Breaches are punished under the related Acts | — |

**Not found in the Directive** (we searched the whole text): any rule on algorithms, automated decision-making, explainability, non-discrimination or fairness; any rule naming loan stacking or a debt-to-income or affordability test; any cooling-off period. The nearest rules are the "responsible digital credit" objective (1.3), the single-customer limit (3.5(5)) and credit limits (7.1(2)).

*Formatting note.* The PDF's clause numbers restart oddly: section 7.2 starts at item "4" and 7.3 at item "5". Cite them as "para. 7.2(c)", "para. 7.3, item 8" and so on.

---

## 3. Data Protection Act, 2012 (Act 843)

| Topic | Section | What it says (plain English) | What it means for our model |
|---|---|---|---|
| Principles | s.17 | Eight principles: accountability, lawful processing, purpose specification, compatible further use, data quality, openness, security safeguards, data subject participation | These work as a checklist for the datasheet |
| Lawful and reasonable | s.18(1) | Processing must be lawful and reasonable and must not infringe privacy | — |
| **Foreign data** | **s.18(2)** | When personal data from another country is sent to Ghana for processing, it must be processed in line with **that country's** data protection law | Our training data is **Kenyan**. Using it in Ghana means following Kenya's law as well (Kenya's Data Protection Act, 2019, which we did not read). The Zindi data is presented as anonymised. The datasheet must record what we know about consent and licence, and admit what we do not |
| Minimality | s.19 | Process only data that is necessary, relevant and not excessive | Every feature needs a reason to exist. Drop columns that add nothing, and do not collect phone contacts, SMS or location "just in case" |
| Consent and objection | s.20 | Process personal data only with **prior consent**, unless an exception applies: it is needed for a contract with the data subject, required by law, protects the subject's interests, performs a statutory duty, or serves the **legitimate interest** of the controller (s.20(1)(a)–(e)). Data subjects may object, and processing must then stop (s.20(2)–(3)) | Scoring a loan application is probably covered by "necessary for a contract". Using past borrowers' data to **train** a model is a different purpose (see s.25) |
| Collect directly | s.21 | Collect data from the person directly, unless an exception applies, such as the person consenting to collection from another source | Alternative data from telcos or other third parties would need consent or another exception |
| Specific purpose | s.22–23 | Collect for a specific, explicit, lawful purpose, and make sure the person knows that purpose | The application screen must say the data is used for credit scoring |
| **Retention** | **s.24** | Keep data no longer than needed, unless the law, a contract, consent or a lawful purpose requires it (s.24(1)). There is an exemption for historical, statistical and research records, which must be protected (s.24(2)–(3)). **If you use a record to make a decision about someone, keep it long enough for them to ask for access** (s.24(4)). When the period ends, destroy, delete or de-identify the data so it cannot be rebuilt (s.24(5)–(6)) | The scorer must store each decision's inputs, score, threshold, model version and reasons for at least as long as a borrower could ask about it. Set a deletion date |
| **Reuse of data** | **s.25** | Any further processing must fit the original purpose (s.25(1)). Factors to weigh include the link between the two purposes and the effect on the person (s.25(2)). Reuse counts as compatible if, among other options, the person consents, or it is for **historical, statistical or research purposes** and the data is not published in an identifying form (s.25(3)(a), (e)) | Training a scoring model on past loans is reuse. It is defensible as statistical or research use if outputs cannot identify anyone. **Our repo is public, so never commit row-level data** |
| Data quality | s.26 | Data must be complete, accurate, up to date and not misleading | Feeds the datasheet's "errors and noise" questions, and the leak and label checks in our feature audit |
| **Registration and notice** | **s.27, s.46–56** | A data controller must **register with the DPC** before processing (s.27(1), s.46(3)). Processing while unregistered is prohibited (s.53) and is an offence (s.56). The application lists the data, its purposes, its recipients and **the countries the data may be transferred to** (s.47(1)(g)). Registration is renewed every two years (s.50), and changes must be notified within 14 days (s.55). At collection, tell the person 9 things: what data is collected, who is collecting it, the purpose, whether supplying it is optional, what happens if they don't, the legal basis, the recipients, the category of data, and their rights of access and correction (s.27(2)) | NkwaPay must be registered and must list Kenya and Ghana (and any cloud host's country) as transfer countries. The 9-item notice belongs in the app |
| Assessable processing | s.57 | The Minister can name high-risk "assessable" processing. The DPC then has 28 days to assess it before it may start | We did not check whether credit scoring has been named. **Unverified** |
| Security | s.28 | Use reasonable technical and organisational measures. Identify risks, add safeguards, check them regularly, and update them | Covers access control on the scorer and its logs, encryption, and no secrets in the public repo |
| Processors | s.29–30 | A processor (for example a cloud host or outsourced scorer) needs a **written contract** with security terms. If the processor is outside Ghana, the controller must make sure it follows Ghanaian law (s.30(4)) | Hosting the model outside Ghana is allowed, but needs a contract and a check that the host complies |
| Breach notice | s.31 | If data is accessed without authorisation, notify the DPC and the data subject as soon as reasonably practicable | — |
| Access and correction | s.32–33 | A person can ask whether we hold their data, get a description of it, and have it corrected or deleted if it is inaccurate, irrelevant, excessive, out of date, incomplete, misleading or unlawfully obtained. Corrections must be passed on to anyone the data was disclosed to (s.33(4)) | We need to be able to find a borrower's records and correct an input that turns out to be wrong. A correction can change the score, so allow re-scoring |
| **Right of access, incl. logic of the decision** | **s.35** | On request, tell the person what data is processed, why, who receives it and where it came from (s.35(1)(a)–(c)). **If a decision that significantly affects them was based *solely* on that processing, tell them the "logic or rationale" behind it** (s.35(1)(d)). There is a trade-secret exception for the logic (s.35(2)). Reply within **40 days** (s.35(10)) | **This is the legal hook for our reason codes.** A fully automated decline must be explainable on request. The trade-secret exception lets NkwaPay keep the weights private, but not refuse to explain altogether. Three plain-language reasons per decision is a reasonable way to meet this |
| Credit bureaus | s.36, s.90 | Bureaus are data controllers under this Act. Requests to bureaus may be limited to financial standing and history from the last 12 months | Affects bureau data we might later use, not our model directly |
| **Special personal data** | **s.37** | Do not process data on children, religion or philosophy, **ethnic origin, race**, union membership, political opinions, health, sex life or criminal behaviour, unless an exception applies (s.37(1)–(2)). **Race or ethnic-origin data may be processed only if it is needed to identify and eliminate discrimination, with safeguards** (s.37(8)) | The model must not use these as features. If we ever audited fairness by ethnicity, s.37(8) would allow it **only** for that purpose. **Gender is not on the special list**, and Act 726 actually requires gender to be reported to bureaus (s.24(2)(f)(ii) of Act 726) |
| Right to stop harmful processing | s.39 | A person may require us to stop processing that causes unwarranted damage or distress. We must reply within 21 days | — |
| Direct marketing | s.40 | Prior written consent is needed for direct marketing, and the person can opt out at any time | Do not reuse model scores to push loan offers by SMS without consent |
| **Automated decisions** | **s.41** | A person can ask in writing that significant decisions about them are **not based solely on automated processing** (s.41(1)). Even without a request, they must be **told** when a significant decision was solely automated, and may ask for it to be **reconsidered** within 21 days (s.41(2)). The controller replies within 21 days (s.41(3)). **But the section does not apply to a decision made while considering whether to enter a contract with the person, with a view to entering it, or while performing it** (s.41(4)(a)–(c)) | A loan decision is a decision about entering a contract, so **s.41 probably does not apply to our approve/decline decision**. s.35(1)(d) (explain the logic) still applies. Good practice, and safer if a regulator reads s.41(4) narrowly: tell people the decision was automated and give them a reconsideration route anyway. That route also satisfies the Directive's complaint rule (para. 6(1)(e)) |
| Compensation | s.43 | Anyone who suffers damage or distress from a breach can claim compensation. Defence: reasonable care | Documentation (Model Card, datasheet, fairness audit) is evidence of reasonable care |
| Rectification by DPC | s.44 | The DPC can order inaccurate data to be corrected, blocked, erased or destroyed, and others must be told | — |
| No buying or selling data | s.88–89 | Buying, or knowingly obtaining or disclosing, another person's personal data is an offence (s.88). **Selling** it is an offence carrying up to 2,500 penalty units or 5 years (s.89) | Buying "alternative data" lists for features is dangerous. Use data the borrower supplies or consents to |
| **Cross-border transfer** | **No general section found** | Act 843 has no stand-alone rule restricting transfer of data out of Ghana. The related provisions are s.18(2) (foreign-origin data), s.30(4) (foreign processors) and s.47(1)(g) (declare transfer countries at registration) | Transfers abroad are not banned, but must be declared at registration and covered by a processor contract |

---

## 4. Credit Reporting Act, 2007 (Act 726)

The copy we read is the original 2007 text. **Act 843 s.98(3) repealed ss.34(1), 38 and 40 of Act 726**, so treat those three as no longer in force. They are marked below.

| Topic | Section | What it says (plain English) | What it means for our model |
|---|---|---|---|
| Regulator | s.1 | BoG licenses and supervises bureaus, data providers and report recipients | — |
| **No penalty for having no file** | **s.21(1)(p)** | A credit bureau must not harm a person's creditworthiness assessment **just because it has no credit information on them** | The duty is on bureaus, but the principle matters to us: a **new borrower** with no history must not be treated as risky merely for being new. Check this directly in our fairness audit, using the new-vs-repeat group |
| Data provider duties | s.22 | Confirm to the bureau that the borrower consented to (i) their data being submitted and (ii) a report being pulled. Tell the bureau about changes | The scorer needs a stored consent record |
| Report recipient duties | s.23 | Keep reports confidential, use them only for purposes the Act allows, and **show or give the borrower a copy of their report on request** | If bureau data ever feeds the model, borrowers can ask to see it |
| What to report and when | s.24(1)–(3) | Report each credit agreement, including amount, outstanding balance, dates, collateral and borrower identity details (name, **gender**, date of birth, residence, ID, TIN, SSNIT number). Report **within 72 hours** of the agreement and send repayment status **monthly** | The Directive is stricter and requires **daily** reporting (para. 7.3) |
| **Prohibited data** | **s.24(4)** | A financial institution **must not require** a borrower to provide race, ethnic origin, political, religious or union affiliation. Providing such information is a breach, with a penalty of up to 2,500 penalty units | We must not collect these, let alone use them as features. This lines up with Act 843 s.37 |
| Reporting without consent | s.25 | Defaults can be reported without consent if the loan is **90+ days past due**, the amount is not disputed, no satisfactory repayment proposal was made, and the borrower had **28 days' notice** | Relevant to our default label. "Default" in a bureau sense means 90+ days, which may differ from the Zindi `target`. Note this in the Model Card |
| **Consent, and a duty to search the bureau** | **s.26** | Report data to a bureau only with the borrower's **prior written consent** (s.26(1)), asked for in the account form, loan application or loan agreement (s.26(2)). BoG may allow electronic consent (s.26(3)). **Before deciding to grant or refuse credit, the lender must search the borrower's record at one or more licensed bureaus** (s.26(4)). The lender is not obliged to deny credit because the borrower refuses consent (s.26(5)). Do not pressure people into consenting (s.26(7)). Consent lasts until revoked (s.26(8)) | **Our design does not do the bureau search.** It uses only Zindi loan-book features (see section 5) |
| Offence | s.27 | Disclosing information in breach of ss.24–26, or failing to report, is an offence | — |
| Bureau retention | s.30 | Bureaus keep records for at most **6 years** (10 years for criminal convictions) | An upper bound on how far back any bureau-based feature could look |
| Security | s.31 | Bureaus, data providers and recipients must use international best practice for privacy, secrecy and security | — |
| Permitted use of reports | s.32(1) | Credit reports go only to registered recipients who hold written consent and need them to evaluate credit risk, changes in credit terms, deferred-payment deals, accuracy checks, or insurance | Do not reuse bureau reports for marketing or other purposes |
| Principles | s.34(1) **(repealed by Act 843 s.98(3))** | Listed principles including "equality of credit information subjects", confidentiality and accuracy | Repealed. **Do not cite it as current law.** The BoG power to issue statements of principle (s.34(2)–(3)) was not repealed |
| Keep consent records | s.35 | Keep borrowers' consent records, electronic or paper, for **at least 10 years** | The consent flag must be stored for 10 years |
| Confidentiality | s.36 | Use credit information only for permitted purposes, and disclose it in good faith | — |
| **Borrower's right to see and challenge** | **s.37** | A borrower may: get a **copy of what the lender plans to send** to the bureau (s.37(1)(a)); inspect their bureau file **free once every 12 months**, when a court orders it, and once after a challenge (s.37(1)(b)); and inspect it at other times for a nominal fee (s.37(1)(c)). They may **challenge the accuracy** of bureau data and have it investigated free (s.37(2)) | The scoring service must be able to show the borrower the data held on them |
| Modification and cancellation | s.38 **(repealed by Act 843 s.98(3))** | Original text: a challenge procedure with evidence, removal of unsupported data, and appeal to BoG within 20 working days | Repealed. The current procedure is probably in Act 843 and L.I. 2394 (**unverified**) |
| Unfounded claims | s.39 | A bureau can charge for verifying a claim that turns out to be unfounded | — |
| Refusal of inspection | s.40 **(repealed by Act 843 s.98(3))** | — | — |
| Legal action | s.41 | A person harmed by inaccurate or incomplete information can sue the data provider or bureau, and ask a court to stop its publication or remove it | Inaccurate data sent to a bureau is a legal risk for NkwaPay |
| Complaints | s.42–43 | Each bureau has an Inquiry Service Unit (s.42). Complaints go to **BoG in writing before any court case**, BoG investigates, and appeals go to the High Court (s.43) | Borrowers can complain to BoG as well as to NkwaPay (Directive para. 6(1)(e)) |
| Relation to other laws | s.62 | Act 726 adds to privacy and data-protection law and does not override it | Act 843 and Act 726 both apply at once |

---

## 5. Requirements our current design cannot satisfy (for Part D)

Our design is one model trained on the Kenyan Zindi data, fairness-audited, served with a probability, a decision and three reasons. Measured against the rules above, it falls short in these ways:

| # | Requirement | Why we can't meet it now | What would fix it |
|---|---|---|---|
| 1 | **Search a credit bureau before every decision**: Act 726 s.26(4) | Our features come only from the lender's own loan records. There is no bureau data feed | Add a bureau-check step before scoring and use bureau fields as features. This needs a data-sharing agreement and borrower consent (s.26(1), Directive para. 7.3) |
| 2 | **Process Kenyan data in line with Kenyan law**: Act 843 s.18(2) | We don't know the consent terms under which Zindi's Kenyan borrowers' data was collected or shared | Record this as unknown in the datasheet. Before production, retrain on NkwaPay's own consented Ghanaian data |
| 3 | **Register with the DPC and get a DPC-approved DPIA**: Act 843 s.27/s.46/s.53, Directive para. 2.1(5)(d)(x)–(xi) | These are organisational steps that a student project cannot complete | The Model Card and datasheet are inputs to the DPIA |
| 4 | **Explain the logic of a solely automated decision**: Act 843 s.35(1)(d) | **Can be met**: the reason codes do this. Risk: reasons that are wrong or misleading would also break Directive para. 6(1)(d) | Test that the reasons match the model's real feature contributions |
| 5 | **Human reconsideration route / notice of automated decision**: Act 843 s.41(2) (probably exempt under s.41(4)) and the 20-day complaint rule in Directive para. 6(1)(e) | The scorer has no appeal or review path | Add an "ask for review" endpoint and a log so staff can re-run and override a decision. The review must still be digital (para. 2.3) |
| 6 | **Keep decision records so people can request access**: Act 843 s.24(4), s.35; Act 726 s.35 (consent records 10 years) | The planned scorer does not persist inputs, outputs or consent | Append-only decision log: inputs, model version, score, threshold, reasons, consent flag and timestamp |
| 7 | **Single-customer loan limit**: Directive para. 3.5(5) | The BoG limit is not published in the Directive. Our loan-amount model has no cap | Make the cap a config value, set from BoG's figure once known |
| 8 | **Avoid over-indebtedness / loan stacking**: Directive objective 1.3(3), credit limits in 7.1(2); detail probably in Act 1052 (**unverified**) | Without bureau data we cannot see loans from other lenders, so we cannot measure total debt | Same fix as row 1. Until then, say in the Model Card that the model cannot detect stacking |
| 9 | **Fairness by gender** (not a legal requirement found in these texts, but the assignment asks for it) | The Zindi data has no gender column. Findex Ghana gives only survey-level gender gaps, not gender per borrower | Report gender only as a context comparison using Findex. If NkwaPay collects gender (Act 726 s.24(2)(f) requires it for bureau reporting anyway), audit the model on it |
| 10 | **Valid for Ghanaian borrowers**: Directive 3.5(1) "tested" systems, 4(2) ongoing risk control | Train is all Kenya. Ghana appears only in Test, without labels | Do the transfer study (domain classifier), monitor after launch, and retrain once Ghanaian outcomes exist |
| 11 | **Total-cost and non-compounded disclosure**: Directive 6(1)(b)–(c), 7.1(3) | This is outside the model. The pre-agreement screen does not exist yet | The scorer's approval output should carry the amount, due date and total repayable so the app can show them |

**Satisfied by design:**
- No features from phone contacts or social media (Directive para. 7.2(c)–(d)).
- No race, ethnicity, religion or politics features (Act 843 s.37, Act 726 s.24(4)).
- No row-level data in the public repo (Act 843 s.25(3)(e), s.28).

---

## 6. Reason codes: what the law asks and a template

- **Act 843 s.35(1)(d)** gives a declined borrower the right to the "logic or rationale" of a solely automated decision, answered within 40 days. **Directive para. 6(1)(a) and (d)** require clear, accurate, not-misleading information. Nothing in these texts sets a fixed format, so use plain language and the top three factors that actually pushed the score toward "decline".
- **Avoid:** naming protected or special traits; reasons the borrower can do nothing about worded as blame; "you are a new customer" as the only reason (see Act 726 s.21(1)(p) in spirit); revealing model weights (the trade-secret exception in s.35(2) lets us keep them private).

Template (fill in from the model's top contributions):

> We could not approve this loan today. This was an automated decision. The main reasons were:
> 1. *The amount requested is large compared with the loans you have repaid before.*
> 2. *A recent loan was repaid after its due date.*
> 3. *The repayment period requested is longer than your usual loans.*
>
> You can ask us to explain this decision or to review it. Reply HELP or call [number]; we answer within 20 days. You can also ask to see the data we hold on you and correct it. You may complain to the Bank of Ghana.

(The example reasons are placeholders. Map each real feature to one sentence in `src/` once the final model exists.)
