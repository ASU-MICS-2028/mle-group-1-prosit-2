# Lecture 3: Data Preprocessing and Leakage for ML

> Study notes written in our own words from the "Lecture 3: Data Preprocessing and Leakage for ML" deck (36 slides).
> Slide numbers refer to the original deck.

## What this lecture is about

Real data are messy, and even a perfect algorithm learns nothing useful from bad inputs ("garbage in, garbage out"). The first half of the lecture covers the four classic preprocessing tasks: **cleaning** (missing values, noise, outliers), **integration** (merging sources), **transformation** (scaling, building new features) and **reduction** (fewer features or records). The second half, which matters most for our Prosit, is about **data leakage**: when information that would not be available at prediction time sneaks into training, making the model look brilliant in testing and fail in production. It lists four types of leakage (target, train-test contamination, temporal, duplicate), red flags, and one golden rule: **split first, fit every preprocessing step on training data only, then apply it unchanged to validation and test data**.

---

## 1. Why preprocessing matters (slides 2–5)

- Real-world data are rarely ready to model: incomplete, noisy and inconsistent (slide 3).
- No quality data → no quality results, regardless of algorithm.
- Preprocessing is one of the most important and most time-consuming steps.

**The four major tasks** (slide 4):

1. **Cleaning**: fill missing values, smooth noise, fix inconsistencies.
2. **Integration**: combine multiple sources into one consistent dataset.
3. **Transformation**: normalise, aggregate, construct new attributes.
4. **Reduction**: reduce volume and dimensionality while keeping the signal.

**Pay-offs** (slide 5): faster training (less redundant data), higher accuracy (better generalisation), simpler/more explainable models, and fewer attributes to collect in future.

---

## 2. Data cleaning (slides 6–11)

### 2.1 Why data are "dirty" (slide 7)

- **Incomplete**: missing values or whole fields (sensor failures, unanswered forms, lost records).
- **Noisy**: errors, typos, outliers from collection, entry or transmission.
- **Inconsistent**: the same fact recorded differently across sources (codes, units, naming).

### 2.2 Handling missing values (slide 8)

1. **Ignore the record** (drop the row): fine only when few rows are affected.
2. **Fill in manually**: accurate but slow; doesn't scale.
3. **Global constant**: a placeholder like "Unknown".
4. **Attribute mean**: replace with the column average.
5. **Class mean**: replace with the average *for that class/category*. (Careful: if "class" means the target label, this uses the answer and is leakage at prediction time, where the label is unknown. It is only safe if the grouping variable is a feature, not the target.)
6. **Predict the value**: use a model (e.g. regression) to estimate it.

### 2.3 Smoothing noisy data (slides 9–10)

- **Binning**: sort values, group into equal-sized bins, replace each value by the bin mean/median/boundary.
- **Regression**: fit a function and use it to smooth values that don't follow the trend.
- **Clustering**: group similar values; points outside any cluster are flagged as outliers.

**Worked binning example** (slide 10). Sorted values: 4, 8, 9, 15, 21, 21, 24, 25, 26, 28, 29, 34. Three bins of four values each, smoothed by the bin mean:

| Bin | Values | Mean (replacement) |
|---|---|---|
| 1 | 4, 8, 9, 15 | (4+8+9+15)/4 = 9 |
| 2 | 21, 21, 24, 25 | 91/4 = 22.75 |
| 3 | 26, 28, 29, 34 | 117/4 = 29.25 |

Each value is replaced by its bin's mean, removing small fluctuations while keeping the overall shape.

### 2.4 Spotting outliers with clustering (slide 11)

1. Group points into clusters by closeness.
2. Each cluster has a **centroid** (the average location of its members).
3. Points not near any cluster are likely outliers or noise.

---

## 3. Data integration (slides 12–13)

Merging sources without creating duplicates, conflicts or noise.

- **Entity identification**: the same real thing may have different names across systems (e.g. `cust_id` vs `customer_number`).
- **Schema and value conflicts**: different encodings for the same fact (e.g. pay type "H"/"S" vs 1/2).
- **Redundant attributes**: two columns carrying the same information under different names; correlation analysis helps find and drop one.

Rule of thumb: resolve conflicts *before* training; duplicated or contradictory signals confuse a model.

---

## 4. Data transformation (slides 14–16)

### 4.1 Normalisation (slide 15)

Features in different units (age in years, income in dollars) can make distance-based or gradient-based algorithms (k-NN, gradient descent) over-weight the larger-scale feature.

- **Min-max normalisation**: $x' = \dfrac{x - \min}{\max - \min}$, rescales to [0, 1].
- **Z-score normalisation (standardisation)**: $x' = \dfrac{x - \text{mean}}{\text{std. dev.}}$, gives mean 0 and standard deviation 1.

Worked example: income ranges from \$12,000 to \$98,000. Min-max for \$42,000: $(42{,}000 - 12{,}000)/(98{,}000 - 12{,}000) = 30{,}000/86{,}000 \approx 0.35$.

Note the min, max, mean and std used here are **statistics of the data**. Which data they are computed on is exactly where leakage enters (section 7).

### 4.2 Attribute construction (slide 16)

Build new attributes from existing ones so the model can see patterns it could not detect from raw features (e.g. height × width → area). This is what modern ML calls **feature engineering**. A good constructed attribute can improve accuracy and make structure easier to understand.

---

## 5. Data reduction (slides 17–20)

### 5.1 Why reduce dimensionality: the curse of dimensionality (slide 18)

As the number of features grows, data become **sparse**:

- To keep the same density of points, the dataset must grow **exponentially** with each added dimension.
- **Distances blur**: in high dimensions nearly every point is about the same distance from every other point.
- **Everything looks unusual**: almost any point can look like an outlier.

### 5.2 Feature selection (slide 19)

Keep only inputs that help; improves speed, accuracy and interpretability.

1. **Forward selection**: start empty; add the most useful feature one at a time.
2. **Backward elimination**: start with all; remove the least useful one at a time.
3. **Bidirectional**: combine both moves.
4. **Tree-based**: use a decision tree's splits/importances to rank features.

### 5.3 Discretisation (slide 20)

Divide a continuous range into intervals and replace values by interval labels, e.g. age 0–25 "Young", 26–55 "Middle-aged", 56+ "Senior". Approaches: binning, entropy-based splitting, merging intervals by statistical tests. Goal: keep as much useful information as possible in fewer, cleaner categories.

### 5.4 Checkpoint (slide 21)

Cleaning → Integration → Transformation → Reduction. But: *even perfectly clean data can ruin a model if information leaks from outside the training set.*

---

## 6. Data leakage: definition and danger (slides 22–24)

**Data leakage**: information that would **not be available at prediction time** (often from the target itself, or from the test set) accidentally gets into training. The model looks brilliant in testing because it is quietly cheating. It doesn't crash your code; it just makes your results a lie.

Why it is dangerous (slide 24):

- **Scores look amazing**: near-perfect validation/test numbers, better than the problem allows.
- **It fails in production**: the leaked information isn't there in the real world, so performance collapses.
- **Wastes time and trust**: teams chase a model that was never good.
- **Hard to catch**: it hides inside ordinary-looking preprocessing.

---

## 7. Four common types of leakage (slides 25–29)

### 7.1 Target leakage (slide 26)

A feature exists, or takes its value, **because of the outcome**. Example: predicting whether a patient *will be diagnosed* with diabetes using a feature "took diabetes medication", which only gets filled in after diagnosis.

Test to apply to every feature: **"Would I actually know this value at the moment I need to make the prediction?"** If not, drop it.

### 7.2 Train-test contamination (slide 27)

Preprocessing statistics (mean, min, max for normalisation; imputation values; encodings) computed on the **whole dataset before splitting**.

| Leaky order | Correct order |
|---|---|
| 1. normalise using stats from ALL data | 1. split into train/test FIRST |
| 2. then split into train/test | 2. fit the normaliser on train only |
| 3. test set already influenced the training scale | 3. apply that same fitted transform to test |

The fix is the order of operations: **always split before you fit anything.**

### 7.3 Temporal leakage (slide 28)

Information from **after** the prediction point is used to predict something earlier. Example: predicting Monday's purchase using a feature computed from Thursday's sales.

Fix: split time-based data **chronologically**: train on the past, validate and test on the future.

### 7.4 Duplicate / near-duplicate leakage (slide 29)

The same (or almost the same) record is in both train and test. Common with images, resampled/augmented data, and records re-scraped over time. The model memorises instead of generalising, and the test score is inflated.

---

## 8. Detecting and preventing leakage (slides 30–34)

### 8.1 Red flags (slide 30)

1. **Suspiciously perfect accuracy** (99%+ on a hard, noisy, real problem).
2. **One feature dominates** feature importance.
3. **Production performance drops sharply** compared with test results.
4. **The feature wouldn't exist yet** at prediction time.

### 8.2 The golden rule: fit on train, apply to test (slide 31)

Raw data → **Split** → **Fit on train** → **Apply to test** → Evaluate.

Every statistic a preprocessing step needs (means, mins, maxes, category encodings, feature rankings) is learned **only** from training data, then applied unchanged to validation and test data. *If the test set could influence any number used during training, that is leakage.*

### 8.3 Leakage inside cross-validation (slide 32)

Cross-validation (CV, repeatedly splitting the training data into "train folds" and a "validation fold") does **not** automatically protect you. Preprocessing must be **refit inside every fold**: for each fold, fit scalers, imputers and encoders on that fold's training portion only, then apply them to its validation portion. **scikit-learn `Pipeline`s do this automatically** when you pass the whole pipeline to `cross_val_score` / `GridSearchCV`.

### 8.4 Prevention checklist (slide 33)

1. Split before you preprocess.
2. Fit on train only (scalers, imputers, encoders).
3. Use pipelines (bundle preprocessing + model).
4. Respect time order (chronological splits, never random shuffles for time data).
5. Check for duplicates across splits.
6. Question great results.

### 8.5 The correct end-to-end workflow (slides 34–35)

Raw data → Split (train/test) → Clean, transform, reduce, **fit on train** → apply the same steps to test → train model → evaluate on test.

Key idea: **think of preprocessing as part of the model**, not a step that happens before it. Preprocessing and leakage prevention are the same discipline.

Take-aways (slide 35): preprocessing is not optional; reducing dimensionality and redundancy gives faster, simpler, more accurate models; leakage silently makes results worthless; and the fix is almost always the same: split first, fit only on training data, question results that look too good.

---

## How this applies to Prosit 2

This lecture is the backbone of our **validation-without-leakage** requirement.

- **Feature audit (target leakage).** Go through every column and ask "would the lender know this at the moment of the loan decision?" Likely suspects in mobile-money loan data: repayment dates, days past due, amount repaid, loan status/closure fields, penalties, anything updated after disbursement. Document each decision in a feature-audit table (keep / drop / reason).
- **History features (temporal leakage).** Customer-history features (number of past loans, past default rate, average past amount) must be computed using **only loans that were completed before the current loan's application date**. A naive `groupby(customer).mean()` over the full table uses the future, including the current loan's own outcome. Use cumulative/expanding windows sorted by time and shifted by one (exclude the current loan), and only count past loans whose outcome was *known* by then.
- **Duplicate leakage → GroupKFold by customer.** The same customer appearing in train and validation is a near-duplicate problem: the model can recognise the person rather than learn risk. **GroupKFold (groups = customer ID)** guarantees each customer is in only one fold.
- **Temporal split.** In addition to GroupKFold, hold out the latest period as a test set (train on earlier months, test on later months). This mimics deployment and detects drift over time.
- **Train-test contamination.** Put imputers, scalers, one-hot/target encoders, feature selection and any resampling (e.g. SMOTE, undersampling) **inside an sklearn `Pipeline`** so they are refit in every fold. Resampling before splitting is a classic leak with imbalanced data like our ~1.83% defaults.
- **Calibration and thresholds are also "fitted" steps.** Fit calibrators (Platt/isotonic) and choose the cost-based decision threshold on validation data (or inside CV), never on the final test set.
- **Red flags to watch.** If PR-AUC or recall look implausibly high for credit risk, or one feature dominates importance, investigate it as leakage first.
- **Kenya → Ghana.** Any scaling or encoding statistics should come from Kenyan training data and be applied unchanged to Ghana data. Unseen Ghanaian categories need a defined fallback (e.g. "other" bucket); don't refit on Ghana data and then claim it as an out-of-distribution test.
- **Curse of dimensionality.** One-hot encoding high-cardinality columns (e.g. many locations or device types) explodes dimensionality; group rare levels or use target encoding fitted inside folds.
- **Missing values.** Decide imputation strategy from training data only; consider "missing" indicator features (e.g. first-time borrowers have no history, which is itself informative).

### Slide content we could not read

All slides had extractable text. Slides 1 and 36 contain only title/contact information (omitted on purpose).
