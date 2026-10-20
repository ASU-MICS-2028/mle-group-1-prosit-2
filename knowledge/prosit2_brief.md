# Prosit 2 brief: Responsible credit scoring for digital micro-lending

*ICS553 Machine Learning Essentials, MSc/MPhil Intelligent Computing Systems, Ashesi University. This is the assignment brief rewritten in markdown so it can be searched and linked. If anything here seems to disagree with the official PDF, the PDF wins.*

**Driving question:** How can a mobile-money lender decide fairly, transparently and sustainably whom to lend to, when its labelled data come from another country, defaulters are only a small fraction of borrowers, and a wrong decision could either push a family into debt or deny them credit altogether?

## 1. The problem situation

**NkwaPay** is a digital lender based in Accra that operates across Africa.
- **The loans:** small, typically 7–90 days, disbursed and repaid via mobile money (mostly through agent networks). They need little or no collateral and often no formal credit history.
- **The expansion:** NkwaPay has worked in Kenya for years and now wants to offer its services in Ghana.

For every application the credit team decides **whether to approve, how much to lend, and at what interest rate**. Two challenges:
1. **Labels:** Kenya has a large labelled portfolio (each loan marked repaid or defaulted). Ghana's portfolio is new and has **no labels** yet.
2. **Rare defaults:** about **1 in 50** loans default. A model that approves almost everyone can look accurate yet lose money. A model that is too strict denies credit to low-income borrowers who need it.

A junior analyst gathered the data for the African Credit Scoring Challenge: Kenyan loan records with default labels, a test set covering Kenya and Ghana, macro indicators, and public Global Findex data for Ghana. The credit committee wants a scoring tool that will:
1. **Estimate the probability of default** for each application, to decide approve/decline, set limits and price.
2. **Estimate the appropriate loan amount** (expected disbursement), to set limits and manage reserves.
3. **Be fair and explainable.** Borrowers get clear reasons; regulators can check the model; no group (by country, region, product or credit history) is unfairly excluded or overcharged.
4. **Be transparent about uncertainty.** It is trained in Kenya and used in Ghana, so it must account for population differences.
5. **Comply** with the Bank of Ghana Directive for Digital Credit Services Providers, the Data Protection Act 2012 and the Credit Reporting Act 2007, and avoid predatory lending or excessive debt.

The committee **prefers a simple model it can justify** to regulators and borrowers over a complex, high-accuracy model that is hard to explain.

## 2. Learning outcomes assessed

| LO | What it means here | Where it's evidenced |
|---|---|---|
| LO1 Formulate real problems as ML tasks | The committee's ask turned into a default-classification task and a limit-setting regression task; the decision point, the label and the cost of errors defined | Part A + initial action plan |
| LO2 Implement end-to-end pipelines | Reproducible EDA → preprocessing → feature engineering → model selection → evaluation → a scoring service with reason codes | Notebooks + GitHub repo + the shipped scorer |
| LO3 Derive core algorithms | **Logistic regression (log-odds/MLE)** and **linear regression (MLE/normal equations)**, plus at least one of decision trees / SVM / gradient boosting, with the maths | Technical documentation |
| LO4 Evaluate with metrics, diagnostics, validation | PR-AUC, ROC-AUC, precision/recall/F1 at a chosen threshold, calibration, **GroupKFold by customer** and temporal CV, and the noise floor | Analysis section + debrief |
| LO5 Design bias/fairness/ethical mitigations | Datasheet + Model Card, metrics by country/product/tenure, proxy analysis, a mitigation; compliance with the BoG Directive and Act 843 | Ethical and regulatory audit |
| LO6 Communicate to technical and non-technical audiences | 15-min group debrief; a borrower-facing reason-code explainer | Debrief |

## 3. The data

| Dataset | What it is | Size | Access |
|---|---|---|---|
| African Credit Scoring Challenge, `Train.csv` | Kenyan loan-level records with a default label | 68,654 rows; 1,258 defaults (1.83%) | Zindi (free account) |
| `Test.csv` | Applications to score; **no labels** | 18,594 rows (~81% Kenya / ~19% Ghana) | Zindi |
| `SampleSubmission.csv` | Submission template (ID, default flag) | — | Zindi |
| `economic_indicators.csv` | FRED macro indicators per country-year (inflation, exchange rate, interest rates, precipitation, unemployment, etc.) | — | Zindi |
| Global Findex Ghana 2021 | Ghana financial-inclusion microdata (account ownership, mobile money, borrowing, saving) | n = 1,000 | World Bank Microdata Library (free registration) |

**Things you must notice before you model:**
- **Overlap.** About 4,306 customers appear in both train and test, and about 920 loans overlap by loan ID. Decide how to handle this.
- **Metric.** The competition scores F1, but also report your own validation using **PR-AUC**.
- **Fairness groups.** There is no gender column. Use `country_id`, `loan_type`, `lender_id` and borrower tenure (new vs repeat) as the fairness groups. For gender and region inclusion, use the Findex Ghana data.

## 4. Your task

Parts A–B are the core supervised learning; Parts C–E make the model a responsible, compliant, usable tool.

### Part A: Frame the problem (LO1)
1. **Timeline, label and leakage audit.**
   a. Draw a simple timeline of one loan: application → approval → disbursement → due date → repayment or default. Mark when NkwaPay must decide, and which column is closest to that moment.
   b. Define the label clearly: what counts as a default, and over what period it is measured.
   c. Produce a **feature audit table** listing every column in Train.csv: *available at decision time (yes/no)*, *used as feature, target, or dropped*, and a one-line reason. Any column recorded or derived after the loan is issued (e.g. repayment outcomes, final payback flags, due-date results) must be marked invalid and excluded. Identify the targets for Task 1 and Task 2.
2. **Specify two tasks using the same features:**
   - **Task 1 (regression):** predict the loan amount to approve, for limit-setting and provisioning.
   - **Task 2 (classification):** predict whether a borrower will default (`target`). Define a business goal, e.g. "mark as high-risk if the predicted chance of default is above the threshold that keeps expected loss within budget while approving at least X% of applicants."
3. **Write a cost matrix.** State the cost of a false negative (approving a loan that defaults) versus a false positive (rejecting a good borrower). Justify the difference **in cedis/shillings**, not just as ratios.

### Part B: Build and evaluate the pipelines (LO2, LO3, LO4)
1. **EDA and preprocessing.** Class imbalance (1.83%), missing values, skew (log transforms), cardinality of the categorical fields (`lender_id`, `loan_type`, "ProductCategory"*).
2. **Feature engineering.** A decision-safe borrower history (number of past loans, past default rate, recency) using a backward `merge_asof` **without exact matches**. Calendar features from the transaction date. FRED macro indicators joined by country-year.
3. **Validating without leakage.** Compare stratified k-fold with **GroupKFold by `customer_id`**, and also a temporal split (train on older loans, test on newer). Report how much the naive score was inflated.
4. **Model comparison.** At least **five** syllabus models, including a majority-class baseline.
5. **Evaluation.**
   - *Classification:* PR-AUC, ROC-AUC, precision, recall, F1 at swept thresholds, confusion matrix, calibration (reliability curve; isotonic or Platt scaling). Pick the operating threshold from the cost matrix.
   - *Regression:* RMSE and MAE on both log and original scales; residual diagnostics.
6. **Noise floor.** Bootstrap a 95% CI on F1 and check whether the model beats the baseline.
7. **Interpretation.** Use coefficients, tree importances or SHAP to produce reasons borrowers can understand.

*\*The data has no `ProductCategory` or `IsDefaulted` column; the real names are `loan_type` and `target`. See [`docs/01_data.md`](../docs/01_data.md).*

### Part C: Cross-market transfer (LO2, LO4)
- Train on Kenya and evaluate on Ghana.
- Ghana has no labels, so compare feature distributions between the two (loan types, durations, lenders, amounts).
- Use importance weighting or a domain classifier to analyse the shift.
- Say what evidence the lender would need before trusting the model's predictions for Ghana.

### Part D: Ethical and regulatory audit (LO5)
1. Complete a **Model Card** (Mitchell et al.) for the chosen model.
2. Report **PR-AUC, F1 and selection rates** by country, loan_type, lender_id, borrower tenure (new vs repeat) and loan-size band, and identify gaps:
   - **Country:** does the Kenyan model systematically score Ghanaian applicants differently?
   - **loan_type and lender_id:** do some products or lenders absorb most of the risk?
   - **Borrower tenure:** does the model punish thin-file (new) borrowers?
   - **Loan-size band:** is the tool regressive?
3. **Compliance.** Map the design against the BoG Digital Credit Directive, the Data Protection Act 2012 and the Credit Reporting Act 2007. Point out requirements you cannot currently satisfy.
4. **Debt and access.** Using Findex Ghana, describe who cannot access credit in Ghana, and whether the model narrows or widens that gap.
5. **Reason codes.** Write a simple explanation for a borrower whose application was declined, avoiding complex language.

### Part E: Make it deployable (LO2, LO6)
Ship a **scoring service**: a saved model (e.g. joblib) and a small function that takes one application and returns:
- the probability of default;
- a decision: approve, decline, or set a limit;
- the top three reasons for that decision.

Also document the latency and the data the application must send.

## 5. Methods to consider

| Family | Models | Where it's taught |
|---|---|---|
| Baselines | Majority class (T2); mean value (T1). **Always report these.** | — |
| Linear | Linear regression (OLS), Ridge, Lasso (T1) | ISLR Ch 3, 6 · HOMLP Ch 4 |
| Logistic | Logistic regression (T2), with class weights | ISLR Ch 4 · HOMLP Ch 4 |
| Instance-based | k-Nearest Neighbours | ISLR Ch 2 · HOMLP Ch 3 |
| Trees | Decision tree with pruning | ISLR Ch 8 · HOMLP Ch 6 |
| Ensembles | Random Forest, Gradient Boosting / LightGBM / XGBoost | ISLR Ch 8 · HOMLP Ch 7 |
| Margins | SVM: SVC with RBF (T2), SVR (T1) | ISLR Ch 9 |
| Optional | Small PyTorch MLP | HOMLP Ch 10 |

**Expected outcome.**
- On an imbalanced, grouped problem, gradient boosting with class weighting often performs best.
- But the gap to a well-tuned logistic regression is often small, and can fall within the margin of error. Report this honestly, using calibration and grouped cross-validation.
- The key success factors are usually **leakage-free validation and time-safe features**, not complex models.

## 6. Evaluation requirements (minimum)
- **Classification (T2):** PR-AUC · ROC-AUC · precision/recall/F1 at the chosen threshold · confusion matrix · threshold sweep · calibration curve (reliability diagram) · a **cost-weighted** justification of the operating point.
- **Regression (T1):** RMSE and MAE on the **log** and **original** scales · residual-vs-fitted plot.
- **Validation integrity:** stratified k-fold vs GroupKFold by `customer_id` vs temporal split, side by side, stating which you trust for deployment and why.
- **Uncertainty and statistics:** bootstrap 95% CIs on F1 and PR-AUC; say whether the model beats the baseline beyond the **noise floor (±0.0263 at leaderboard size)**.

## 7. Deliverables
One submission per group, plus one individual file per member.

**Group:**
1. **GitHub repository:** a README (how to reproduce end to end), the data-loading code, and notebooks `01_eda`, `02_classification`, `03_regression`, `04_transfer_and_fairness`.
2. **Technical report (~6–10 pages):** problem framing and cost matrix (Part A), data, methods with derivations, results, diagnostics, the cross-market transfer study, limitations, a reproducibility statement, and an AI-use declaration.
3. **Ethical and regulatory audit:** the Model Card, the disaggregated fairness results, the proxy analysis, and the regulatory mapping (Part D).
4. **Scoring service + reason-code explainer** (Part E).
5. **Debrief slides.**

**Individual:**
6. **One-page reflection:** your contribution, what you learned, what you would do differently.

## 8. Resources
- **Data:**
  - [African Credit Scoring Challenge (Zindi)](https://zindi.africa/competitions/african-credit-scoring-challenge)
  - [Global Findex Ghana 2021](https://microdata.worldbank.org/index.php/catalog/4646) (DOI [10.48529/gs06-7r65](https://doi.org/10.48529/gs06-7r65))
  - Fallback: Financial Inclusion in Africa (Zindi 2019)
- **Regulation:**
  - [BoG Directive for Digital Credit Services Providers](https://www.bog.gov.gh/notice/directive-for-digital-credit-services-providers-in-ghana/)
  - Data Protection Act 2012 (Act 843); Credit Reporting Act 2007 (Act 726). See [`regulation.md`](regulation.md).
- **Fairness and ethics (must-reads):**
  - Gebru et al. 2021, *Datasheets for Datasets*
  - Mitchell et al. 2019, *Model Cards for Model Reporting*
  - Buolamwini & Gebru 2018, *Gender Shades*
  - Barocas, Hardt & Narayanan, *Fairness and Machine Learning*
  - See [`fairness_reading.md`](fairness_reading.md).
- **Textbooks and tools:**
  - ISLR (Ch 3, 4, 6, 8, 9) · HOMLP (Ch 4, 6, 7) · Molnar, *Interpretable Machine Learning*. See [`books.md`](books.md).
  - scikit-learn, pandas, LightGBM/XGBoost, imbalanced-learn, shap, joblib.

## Appendix A: Cost matrix example
*Do not reuse these numbers. Derive and justify our own from the data and the Ghanaian market.*

|  | Actually repays | Actually defaults |
|---|---|---|
| **Approve** | True negative: lender earns the fee/interest | False negative: lender loses the money lent |
| **Decline** | False positive: lender loses the profit, and the borrower is denied credit | True positive: loss avoided |

Worked example: a 30-day GHS 300 loan with a 15% fee.

| Item | GHS | Basis |
|---|---|---|
| Average principal | 300 | Typical 30-day loan in the training data |
| Fee if repaid | 45 | 15% flat fee |
| Recovered after default | 60 | Assume 20% recovered via collections |
| Collection cost | 25 | Agent follow-up, SMS, airtime |
| **Cost of FN** | **265** | 300 − 60 + 25 |
| **Cost of FP** | **45** | Fee forgone from a good borrower |
| FN:FP ratio | ≈ 5.9:1 | Reported only after the cedi figures |

**Setting the threshold.**
- If the predicted probability $p$ is **calibrated**, declining is cheaper than approving when $p \cdot C_{FN} > (1-p) \cdot C_{FP}$.
- That rearranges to: decline when $p > \dfrac{C_{FP}}{C_{FP}+C_{FN}}$.
- In this example, $45/(45+265) \approx 0.145$: decline when the predicted default probability is above about 14.5%.

**Sensitivity.**
- With 0% recovery, $C_{FN}=325$ and the threshold falls to about 0.12.
- With 40% recovery, $C_{FN}=205$ and it rises to about 0.18.
- Our report must show how the operating point moves under **at least two** alternative assumptions.

## Appendix B: Rubric, timeline, AI policy

| Criterion | Weight | LO | What "excellent" looks like |
|---|---|---|---|
| A. Problem framing and cost matrix | 10 | LO1, LO2 | Label defined; feature audit complete with leakage correctly identified; money-denominated cost matrix |
| B. Modelling and pipeline quality | 30 | LO2, LO3 | Reproducible pipeline; ≥5 models; ≥2 derivations correct; time-safe feature engineering |
| C. Evaluation and validation | 20 | LO4 | PR-AUC + calibration; stratified vs grouped vs temporal CV compared; noise floor respected |
| D. Ethical and regulatory audit | 20 | LO5 | Model Card; disaggregated metrics; proxy analysis; regulatory mapping; a mitigation |
| E. Deployment and presentation | 15 | LO6 | Working scoring service with reason codes; strong defence |
| F. Process and individual contribution | 5 | — | Even contribution; thoughtful reflection |

| Week | Session | Activity | Milestone |
|---|---|---|---|
| 6 (Oct 12–16) | Fri | Launch Prosit 2 | Initial action plan |
| 7 (Oct 19–23) | Fri | Group work | — |
| 8 (Oct 26–30) | — | — | — |
| 9 (Nov 2–6) | **Tue** | Debrief: group presentations | **Portfolio due** (slides + repo + report + audit + reflection) |

**AI-use policy:**
- **Permitted:** using AI to clarify concepts, debug code you understand, or generate practice questions.
- **Not permitted:** submitting deliverables substantially generated by AI without critical evaluation, or blindly copying AI output.
- **Required:** an AI-use declaration in the report, and the ability to explain, defend and reproduce the work **without AI** during the presentation.
