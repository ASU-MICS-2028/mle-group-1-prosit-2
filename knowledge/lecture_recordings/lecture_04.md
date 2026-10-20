# Lecture 4: Machine Learning Data Preprocessing Steps

> Summary of an audio recording of the lecture. The full transcript is not published. Speech-to-text was imperfect, so check important details against the slide notes in `../lectures/`.

## Recording summary

### Flow summary
This session covered why data preprocessing matters for machine learning and the steps it involves, stressing that much of a traditional ML project is preparing the data. The discussion moved through cleaning, integration, transformation and reduction.

### Data cleaning issues
- Handling missing values:
    - Ignore records if missing values are few (e.g. fewer than 5 or 6 out of thousands).
    - Fill in manually for a small number of missing entries.
    - Use a global constant to replace all missing values.
    - Use the attribute mean: the mean of the entered values replaces the missing ones.
    - Use the class mean: replace missing values with the average for that record's class (e.g. Class A).
- Dealing with noise/outliers:
    - Outliers are points that do not fit the general distribution.
    - Strategies for smoothing noisy data:
        - Binning: group records into bins and replace the original values with the bin average.
        - Sort the data before binning to minimise distortion.

### Data integration issues
- Merging data from multiple sources without introducing duplicates or conflicts.
- Entity identification: the same feature appears under different names across sources (e.g. "cust ID" vs "customer number").
- Schema and value conflicts: different encodings for the same fact in different sources (e.g. 'H'/'S' vs 1/0).
- Redundant attributes: two columns carrying the same information under different names, found via correlation analysis.

### Data transformation and reduction
- Normalisation: scaling features to a similar range so that distance-sensitive models do not give a feature undue importance because of its raw magnitude (e.g. scaling income to be comparable with age).
    - Min-max normalisation: rescale values into a fixed range, usually 0 to 1.
    - Standardisation: transform data to mean 0 and standard deviation 1.
    - De-normalisation: applied at inference time to get the actual value back from the scaled feature.
- Feature engineering: building new attributes from existing ones (e.g. combining height and weight) to reveal patterns.
- Dimensionality reduction: reducing features, because in high dimensions it is hard to measure distance between points accurately and the data appears close together.
    - Feature selection methods:
        - Forward selection: start with one feature and keep adding the most useful ones.
        - Backward selection: start with all features and keep removing the least important ones.
        - Bidirectional selection: add and remove features as the process moves forward.

### Next steps
- The next section will cover data leakage.
- Friday: Prosit presentations for four or five groups, a maximum of 30 minutes per group, with 15 to 20 minutes for each presentation.

## Our summary

### Framing
This lecture closed the "data" part of the course before supervised learning. The lecturer previewed the rest of the course: supervised ML, then an introduction to neural networks (training, common architectures, autoencoders, transformers), with deep learning and computer vision covered in more depth in other courses.

Main message: **about 60 to 70% of a traditional ML pipeline is working on the data**, and "garbage in, garbage out". Model choice matters less than data quality. Real-world data is rarely ready to model. Sensors fail and leave gaps, survey fields are skipped, and records get lost. Preprocessing gives faster training (no redundant rows or columns), higher accuracy and simpler models with fewer attributes.

The four stages are **cleaning → integration → transformation → reduction**, with **data leakage** covered as a final topic.

### 1. Cleaning
Data is dirty in three ways: **incomplete** (missing values), **noisy** (typos, outliers such as an age of 600 in a class of 18 to 30 year olds) and **inconsistent** (the same fact recorded with different codes, units or names across sources).

**Missing values**, from crudest to best:
- **Ignore/drop the record**: fine only if very few are affected (e.g. about 10 of 1,000 rows). How few is "few" depends on the application. If more than half the records are missing, the lecturer suggested collecting the data again.
- **Fill in manually**: only practical for a handful of records, e.g. by contacting survey respondents.
- **Global constant**: e.g. a salary floor of 2,000, or an explicit "unknown" category.
- **Attribute mean**: the mean of the observed values for that feature.
- **Class mean**: the mean within the record's class (e.g. salary class A/B/C) instead of the overall mean. Round it if the feature holds integers.
- A student pointed out that a skewed feature such as salary distorts the mean (one very high earner pulls it up), so the **median** is better there. The lecturer agreed: check the distribution first and pick the mean, median or a constant to suit it.
- **Predict the missing value** with a simple model, e.g. a linear regression of salary on years of experience. The model is fitted on complete rows and used to predict the missing ones. The lecturer called this the most accurate option.
- A column that is mostly empty and seems unimportant is a feature-engineering question. Check its importance (e.g. with a decision tree), and consider combining it with another feature before dropping it.

**Noise/outliers (smoothing):**
- **Binning**: sort the values, split them into equal-size bins (e.g. 4 per bin) and replace each value with its bin mean. Worked example: a bin of 4, 8, 9, 15 has a sum of 36, so its mean is 9 and all four values become 9. **Sort first.** If an outlier (34) lands in a bin with small values, its replacement drops to about 16. In a sorted bin of similar values the mean (about 29) stays close to it. A student asked whether this loses information. The lecturer said the individual values change, but the feature still carries its information while the model learns less from noise.
- **Clustering**: used to **detect** outliers, i.e. points far from every cluster. Deciding what to do with them is a separate step. If there are few outliers, drop them; otherwise smooth them toward the clusters. If you are unsure whether an outlier matters, check feature importance.
- The lecturer said the slide listed three smoothing strategies. Only binning and clustering were clearly explained. The third may have been regression, but the transcript is unclear.
- Whether a data engineer or the ML engineer does this depends on the organisation. Often you have to do all of it yourself.

### 2. Integration
This means merging sources (e.g. admissions records plus LMS data) without creating duplicates or conflicts:
- **Entity identification**: the same feature under different names, e.g. "cust ID" vs "customer number". Date of birth vs age is a derivable duplicate, so keep only one. If two ID columns look alike but mean different things (e.g. student number vs applicant number), resolve that at integration time.
- **Schema/value conflicts**: the same fact encoded differently, e.g. pay type as H/S in one source and 1/0 in another, or height in cm vs m. Convert to one unit or encoding before merging.
- **Redundant attributes**: two columns that carry the same information. Detect them with correlation analysis and drop one if the correlation is very high. The lecturer's reasoning: information is highest where uncertainty is highest, so the model learns more from varied features than from near-duplicates.
- Rule of thumb: when two sources describe the same entity, **resolve the conflict before training**.

### 3. Transformation
- **Why scale**: distance- and gradient-based models (nearest neighbour, linear regression, gradient descent in neural networks) treat large-magnitude features as more important. In the example, income ran from 12,000 to 90,000 while age ran from 25 to 60. Scaling changes the range, not the information, and it can be applied to one column or to all of them. A student noted that huge values are also a numerical problem for floating-point training on GPUs.
- **Min-max**: (x − min) / (max − min) → [0, 1].
- **Z-score (standardisation)**: (x − mean) / sd → mean 0, sd 1.
- The choice between them depends on the features and is largely **empirical**.
- **Fit on train only.** Compute the scaling statistics (min/max or mean/sd) **from the training set alone**, then apply that same transform to the test set and to every new input at inference. For example, a new age of 32 is scaled with the training statistics. Predictions on a scaled target are mapped back (de-normalised) at inference.
- **Feature construction / engineering**: build new attributes from existing ones. Height + weight → a combined feature; the transcript says "material" but BMI is likely meant. Another example was area from two dimensions. A well-built feature can improve accuracy and **interpretability**, which the lecturer linked to explainable AI.

### 4. Reduction
- **Curse of dimensionality**: as features increase, the data needed to keep the same density of points grows exponentially, and in high dimensions all points become nearly the same distance apart. Features should grow only together with records.
- **Feature selection** keeps only the inputs that help, which improves speed, accuracy and interpretability and removes noise:
  - **Forward selection**: start with the most useful feature and add one at a time. Stop when adding more no longer improves performance (e.g. at 15 of 20 features). It is the faster option.
  - **Backward elimination**: start with all features and remove them one at a time while performance holds. It costs more compute. Stop before you remove so much that the model lacks information.
  - **Bidirectional**: add and remove as you go.
  - **Decision-tree importance**: let the splits show which features matter.
- Adding features endlessly leads to **overfitting**.
- **Discretisation**: split a continuous feature (e.g. age) into intervals to shrink the data and simplify the model.

### 5. Data leakage (preview; the full treatment is next lecture)
- Even after careful preprocessing, **leakage breaks the model**. If any information from the test set reaches training, test scores (e.g. 98 to 99%) are inflated because the model has effectively seen the test data. **Split first, then preprocess.** Fitting imputation or scaling on the full dataset before splitting is **train/test contamination**.
- A student described a leakage problem from Prosit 1: features measured years later (net data from 2022) were used to predict earlier malaria outcomes (2014/2017). The lecturer called this **temporal leakage**, where future information is used to predict the past, and said it must be identified and addressed.

### What the lecturer said about the prosits
- **Prosit 1 presentations on Friday**: four or five groups, a maximum of 30 minutes each, so present for about 15 to 20 minutes. Any format is allowed: slides, a printed poster or anything else. The most important things to describe are your methods, your results and the issues you found in the data.
- **Reflections are individual**: a personal response of about **one page**. Cover your own contributions, what you did and how, and something new you learned during the prosit. The lecturer also mentioned some scenario-style questions; the transcript is too garbled to say exactly what they were.
- The lecturer said they were looking forward to groups' "interesting, serious recommendations", so recommendations are expected to be substantive.
- The lecturer explicitly asked whether groups ran into **data leakage** in the prosit, and treated **temporal leakage** as a real problem to find and address.
- On missing data in the malaria set, the lecturer hinted that how groups handled it would show up in their scores ("we see on Friday"). This part of the transcript is garbled.
- **Common mistake highlighted**: preprocessing (imputation, scaling) before the train/test split, which leaks test information and gives overconfident results.

### Relevance to Prosit 2
- **Leakage-free validation.** Put every imputer, scaler and encoder inside a scikit-learn `Pipeline` so it is refit within each CV fold (GroupKFold / temporal CV) and never sees validation or test rows.
- **Temporal leakage.** The temporal leakage warning applies directly: features recorded after loan origination (repayment status, later balances) must not be used, and temporal CV must train on the past and validate on the future.
- **Missing values.** Use the median for skewed amounts and incomes, and add missing-indicator flags. Model-based imputation must also be fitted only on training folds.
- **Integration and redundancy.** Watch for duplicate IDs (the same borrower under different keys, which also decides the GroupKFold group), unit and currency mismatches, and highly correlated redundant columns. Currency and units matter especially for the **Kenya → Ghana** transfer.
- **Scaling.** Scaling matters for logistic regression and distance-based models. Trees are largely insensitive to it. For the **loan-amount regression**, scale or log-transform the target with training statistics and invert the transform for reported predictions.
- **Interpretable features.** Engineered, understandable features (e.g. amount-to-income ratios) support the **reason codes** in the scorer. Avoid binning or aggregating protected attributes in ways that hide disparities in the **fairness audit**.
- **Outliers.** Smoothing or dropping outliers changes the class balance of an already **imbalanced** default target, so check what you remove.
