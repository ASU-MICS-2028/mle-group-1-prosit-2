# Lecture 2: Prosit 1 Launch: Malaria Data Analysis (ITN Allocation in Ghana)

> Summary of an audio recording of the lecture. The full transcript is not published. Speech-to-text was imperfect, so check important details against the slide notes in `../lectures/`.

## Recording summary

### Flow Summary
This session covered course instruction and kicked off the first project. It explained how problem-based learning is structured and introduced a malaria data-analysis case study in Ghana. It then went through the deliverables, the analytical concepts required and the first steps for the student groups.

### Course Structure and Goals
- Underlying idea: students should do more and listen to lectures less.
    - Less teaching time; more time spent thinking through problems and building solutions.
- Problem type: ill-structured problems, meaning there is no single correct answer.
- Case study focus: data-driven allocation of insecticide-treated nets (ITNs) in Ghana.
    - Question: how confident can we be in the district-level malaria estimates behind a decision to allocate a limited ITN supply?

### Project Deliverables and Timeline
- Final deliverables expected at the end of the project:
    - A report with the full pipeline, from cleaning the data to the leakage audit.
    - A resource allocation proposal answering where nets should go to do the most good and be distributed most fairly.
    - A presentation of fifteen minutes or less to a mock Ministry of Health panel.
    - A one-page individual reflection uploaded to Canvas.
- Initial focus (first three weeks):
    - Exploring probability distributions and sampling:
        - Study the data, then plot and describe the discrete case counts.
        - Test the counts against Poisson and Negative Binomial distributions.
        - Quantify the uncertainty in the data distributions.
    - Preprocessing and leakage:
        - Map raw prevalence to reveal undersampled rural areas (heat map).
        - Handle missing values with simple imputation methods.
        - Avoid data leakage when splitting the data.

### Data Provided
- Two main files: Ghana district cases, and MIS household data (a sampled subset).
- A data dictionary explains the datasets.
- Key covariates include rainfall, temperature, elevation, distance to water and net coverage.

### Next Steps
- The lecturer will upload the malaria materials to Canvas.
- Students should start by understanding the problem question thoroughly.
- Students should plan daily goals for the deliverables.

### Decisions Made
- The project will analyse the data to decide where mosquito nets should be distributed.

## Our summary

Only about the first 25 minutes of the recording are lecture. The rest is group formation, sorting out a broken dataset upload, and in-group work with mostly off-topic conversation. Below is what the lecturer actually said, with a few brief clarifications the lecturer gave while walking between groups.

### 1. Why the course runs this way
- The course is deliberately hands-on: about 1h45 of lecture per session at most, with the rest spent working through problems. Lecture-style ML is freely available online. The value of this course is building things.
- Prosits are **ill-structured problems**: there is no single correct answer, so you must think through the problem before solving it. Reading to understand the problem comes first, then analysis, then your own innovation.

### 2. The Prosit 1 problem (malaria / ITNs)
- Africa carries the large majority of global malaria deaths (the lecturer quoted roughly 95%). Ghana's **National Malaria Elimination Programme (NMEP)** distributes insecticide-treated nets. The latest distribution in the data was 2023.
- Burden varies widely. Interior and some urban districts, including poorer pockets of Accra, can carry high burden. **Rural and border communities tend to be under-represented in surveys**, which is the crux of the problem.
- Framing: each group is an analytics consulting team. A new, limited ITN delivery has arrived, and you must advise the NMEP allocation committee where the nets will do the most good **and** be distributed most fairly. You must "be ready to defend every number".
- Core question: where should Ghana's limited ITNs go, **and how confident can we be in the district-level malaria estimates behind that decision?**

### 3. Data
- **Ghana district cases:** malaria counts per district plus covariates (rainfall, temperature, elevation, distance to water, net coverage) for fitting models.
- **MIS household data (Malaria Indicator Survey):** a large proprietary dataset from which the lecturer sampled a relevant subset. Students discussing it noted fields such as region (16 regions), cluster, urban/rural residence, a wealth index, **sample weights**, nets owned and children eligible for nets. On sample weights, a student's reading was that households from under-sampled groups carry larger weights, so treating every household equally would bias results.
- A **data dictionary** (datasheet) explains the columns.
- **Data-use restriction:** the proprietary data must **not be uploaded to any AI tool**. Using AI to understand the column structure is acceptable, but not uploading the data itself. The other files are open.
- The lecturer said the dataset was **intentionally tweaked to contain problems** (missingness, leakage traps and so on). It is not clean.

### 4. Tasks, in two themes
**Theme A: probability and sampling**
1. Plot and describe the district case counts. They are expected to be right-skewed and **overdispersed** (variance much larger than the mean). A plot plus a quick mean-vs-variance check is enough; no formal test is needed.
2. Fit a **Poisson** distribution and ask whether it actually matches the shape of the data. (Poisson assumes mean = variance.)
3. Fit a **Negative Binomial**, which allows extra variance. Library functions are fine; there is no need to implement from scratch.
4. **Quantify uncertainty** (confidence intervals) on the estimates.

Throughout, back every claim with a number or a simple plot. The lecturer strongly encouraged visuals, and the final recommendation must rest on data and plots.

**Theme B: preprocessing and leakage**
1. Map raw prevalence. Build a geospatial map that shades districts by data availability so undersampled rural and border areas stand out (heat-map style).
2. Handle missing values with **simple imputation only**.
3. Encode categoricals simply (e.g., one-hot).
4. **Avoid leakage**: use a sensible split. The lecturer suggested stratified splits.

### 5. Timeline (stated as tentative)
- Week 1: launch, team formation, lecture on distributions and sampling, environment setup, action plan and a start on the report.
- Week 2: something to show, namely EDA and a **data-gap map**, possibly as a gallery walk with physical posters (or shown digitally on the TV), plus a lecture on data preprocessing.
- Final milestone: report, distribution confidence intervals, leakage audit and the presentation.

### What the lecturer said about the prosits
- **Deliverables:** (1) a report plus code covering the full pipeline from cleaning to the leakage audit; (2) a resource-allocation proposal that answers the question; (3) a presentation of 15 minutes or less to a mock Ministry of Health panel, with the lecturer and invited colleagues on the panel; (4) a **one-page individual reflection** on what you learned and how you used it, uploaded individually to Canvas. The lecturer said reflections "are really important".
- **Code format:** a notebook is fine. Modular Python scripts are also allowed. Any language or framework is acceptable, with Python suggested.
- **Grading:** the prosit is marked out of 100 using a rubric tied to the course learning outcomes, then scaled to its share of the 20% PBL component. Use the rubric as a checklist before submitting.
- **Pre-submission checklist (stated explicitly):**
  - **No cell may fit an encoder or scaler on train and test data together.** Fit on the training data only, then transform test. A student explained why in class: otherwise the model is shown information it should not have, and the reported results are inflated.
  - Include a short **leakage audit** section that names each leak found with **before/after numbers**. This is also part of the presentation.
  - Include statistics, sources and an **AI-use declaration**.
  - The work must **run top to bottom from a fresh clone or kernel**. With multiple scripts, cloning the repo and running must work. With one notebook, all cells must run in order.
- The lecturer warned that leakage makes a model look highly accurate because it has effectively already seen the test data. Leakage is the "key hazard".
- Later in the session the lecturer acknowledged that this early part of the course is closer to data science than ML. A data science course would normally come first but had been moved to next semester, and supervised learning comes later in the syllabus.
- The lecturer asked each group to summarise its understanding of the problem by the end of the session.

### Relevance to Prosit 2
- **Leakage rules carry over directly.** Fit every imputer, encoder and scaler inside the CV pipeline on training folds only. Keep a leakage-audit section that names each leak with before/after metrics. For Prosit 2 that means GroupKFold by borrower or customer (no customer in both train and validation) and temporal CV (no training on loans issued after the validation period).
- **Expect a deliberately dirty dataset.** Look for injected traps: post-outcome columns, ID-like predictors, duplicates and target proxies.
- **Uncertainty is expected.** Prosit 1 asked for confidence intervals on estimates. Prosit 2's bootstrap CIs on AUC, recall and cost play the same role, so report intervals, not point estimates.
- **Sample weights and under-representation** foreshadow the fairness audit and the Kenya-to-Ghana shift. Check which groups are under-represented in the Kenyan loan data and how that affects per-group error rates and transfer to Ghana.
- **Defend every number to a non-technical panel.** The cost-based threshold, calibration and reason codes all need plain-language justification backed by plots.
- **Reproducibility and process:** runs top to bottom from a fresh clone, includes an AI-use declaration and sources, and each member writes a one-page individual reflection. Check whether the Prosit 2 data carries any AI-tool upload restriction like the one on Prosit 1's survey data.
- **Overdispersion and Negative Binomial** are less central to Prosit 2. The habit of checking whether a distributional assumption fits (e.g., for loan amounts, which are right-skewed, so consider a log target for regression) still applies.
