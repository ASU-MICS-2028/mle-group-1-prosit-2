# Lecture 0: Introduction to Machine Learning

> Study notes written in our own words from the course's introductory slide deck (59 slides).
> Slide numbers refer to the original deck. Formulas are re-typed in LaTeX.

## What this lecture is about

This is the "map of the territory" lecture. It explains what machine learning (ML) is, when it is worth using, and the standard step-by-step workflow (the *pipeline*) for an ML project. It then introduces the three main kinds of learning (supervised, unsupervised, reinforcement) plus semi-supervised learning, gives some example applications, and covers the statistics ideas that sit underneath every model: descriptive statistics, maximum likelihood (MLE), maximum a posteriori (MAP), the bias-variance trade-off, over/underfitting and regularisation. It finishes with feature engineering: turning raw columns into inputs a model can actually use (encoding, scaling, missing values, outliers, feature selection).

---

## 1. Learning objectives and outline (slides 1–4)

The lecture has three goals:

1. Understand the basic concepts of ML.
2. Understand the data-science and statistical principles behind ML.
3. Understand **feature engineering** (building and choosing the inputs to a model) and why it improves performance.

It is split into three parts: Introduction, Data Science for ML, Feature Engineering.

Slide 5 is an image only (no text could be extracted).

---

## 2. What are AI and ML? (slides 6–9)

**Artificial Intelligence (AI)** (slide 6): a computer's ability to imitate human *cognitive functions*, which are mental abilities such as:

- *learning* (getting better with experience),
- *problem-solving*,
- *decision-making* (choosing between options using the information available),
- *understanding language*,
- *reasoning* (drawing logical conclusions),
- *perception* (making sense of images, sound, etc.).

**Machine Learning (ML)** (slides 7–8): the part of AI where algorithms *learn patterns from training data* and then make predictions about new data, without someone hand-writing the rules. Two classic definitions:

- *Arthur Samuel (1959)*: ML gives computers the ability to learn without being explicitly programmed.
- *Tom Mitchell (1998)*: a program **learns** from experience **E**, for a task **T**, measured by performance **P**, if its performance on T (as measured by P) improves with E.

> **Worked intuition (Mitchell's definition for our Prosit):**
> T = "predict whether a mobile-money borrower will default"; E = historical loans with known outcomes; P = e.g. PR-AUC or expected cost on held-out loans. The program "learns" if more/better historical loans make P better.

**When is ML useful?** (slide 9)

| Use ML when... | Don't bother when... |
|---|---|
| there is a lot of data to learn from | simple rules already work (payroll, sorting numbers) |
| the problem is too complex to write rules for (images, speech) | there is little data, or the data is poor quality |
| the environment changes over time and the system must adapt | |

Slide 10 ("How machine learning works") is a diagram only; its content could not be extracted.

---

## 3. Example and the ML pipeline (slides 11–18)

**Handwritten digits** (slide 11): given a small image of a handwritten digit, decide which digit it is. The difficulty is that people write in many different ways, so the model must **generalise**: perform well on new examples it has never seen, not just on the training images.

**The ML pipeline** (slides 12–18) is the structured route from a vague problem to a deployed system. The slides list these steps (the numbering on the slides repeats "Step 9" twice; we renumber here):

1. **Problem formulation.** Say exactly what you are solving, what the *target variable* is (the thing you predict), and what "success" means.
2. **Data collection.** Gather relevant data (databases/SQL, APIs, sensors/IoT).
3. **Data preprocessing (cleaning).** Handle missing values, remove duplicates, fix inconsistent formats.
4. **Exploratory Data Analysis (EDA).** Summary statistics (mean, standard deviation), plots (histograms, scatter plots), outlier detection. Purpose: spot relationships and problems early.
5. **Feature engineering.** Turn raw data into useful inputs: encode categories (e.g. one-hot), scale numbers (normalisation/standardisation), create new features, select features.
6. **Data splitting.** Divide the data so that evaluation is honest. The slides suggest roughly 70–80% training, 10–15% validation (optional), 15–30% test.
   - *Training set*: what the model learns from.
   - *Validation set*: used to choose between models/settings.
   - *Test set*: touched once at the end to estimate real-world performance.
7. **Model selection.** Pick a suitable algorithm. Regression → linear regression, decision trees/random forests. Classification → logistic regression, support vector machines, neural networks.
8. **Model training.** Feed in training data; the model adjusts its *parameters* (internal numbers) to minimise error.
9. **Model evaluation.** Measure performance on unseen data. Regression metrics: MSE (mean squared error), RMSE (its square root). Classification metrics: accuracy, precision, recall, F1-score.
10. **Hyperparameter tuning.** *Hyperparameters* are settings you choose rather than learn (e.g. maximum tree depth). Tune them to improve performance.
11. **Deployment.** Put the model into production so it serves real predictions.

---

## 4. Types of machine learning (slides 19–28)

All ML methods fall into one of three paradigms, based on what they are trained to do and what data they need (slide 19).

### 4.1 Supervised learning (slides 20–21)

Trained on a **labelled dataset**: every example has both the *input features* and the *correct output* (the label or target). The model learns to predict the output from the input and is judged against an external "ground truth".

- **Regression**: predict a continuous number (house price, tomorrow's temperature).
- **Classification**: predict a category (spam / not spam; disease positive / negative).

### 4.2 Unsupervised learning (slides 22–23)

No labels. The model looks for structure, patterns and correlations in the inputs on their own. There is no ground truth to compare against.

- **Clustering**: group similar points (e.g. customer segmentation).
- **Anomaly detection**: find unusual points (e.g. fraudulent transactions).
- **Dimensionality reduction**: reduce the number of features while keeping the important information (e.g. image compression).

### 4.3 Reinforcement learning (RL) (slides 24–26)

Learning by **reward and punishment**. An *agent* (the decision maker) acts in an *environment* and tries to collect as much reward as possible. There is no single correct answer, only better and worse actions.

At each time step $t = 0, 1, 2, \dots$:

- the agent observes the **state** $s_t$,
- chooses an **action** $a_t$ from the allowed actions $A(s_t)$,
- receives a **reward** $r_{t+1}$ and moves to the next state $s_{t+1}$.

The speaker notes describe the loop as perception → action → feedback → learning. Slide 26 is a video of an agent learning to play a platform game level; no extractable content.

### 4.4 Semi-supervised learning (slide 27)

A mix of the two: a **small labelled set** plus a **large unlabelled set**. The labelled data guides learning on the unlabelled data. Example: use clustering (unsupervised) to find groups, then use the few labels to name the groups (supervised).

Slide 28 ("Machine Learning Algorithms") is an image only.

---

## 5. Applications (slides 29–32)

- **Recommendations on streaming platforms.** *Collaborative filtering* finds patterns across many users ("people who watched X also watched Y"). *Content-based filtering* uses the features of what you already watched (genre, actors, director).
- **Quality control / defect detection.** Inspecting products for cracks or scratches; faster and more consistent than people.
- **Signal processing and communications.** Image and speech recognition; telecoms.
- **Robotics and control.** Adaptive control, robots that learn tasks, human-robot interaction.

---

## 6. Data science for ML (slides 33–48)

### 6.1 Statistical machine learning (slide 34)

ML sits where **statistics** (describing data and inferring from it), **machine learning** (learning patterns) and **optimisation** (finding the best parameters) meet. Its focus is probabilistic modelling, quantifying uncertainty, and inference from data.

### 6.2 Descriptive statistics (slides 35–38)

*Descriptive statistics* summarise a dataset. You need them to build good models and choose suitable algorithms.

**Central tendency** (where the "middle" of the data is):

- **Mean** $\mu = \frac{1}{n}\sum_{i=1}^{n} x_i$. Sensitive to outliers. Used in normalisation.
- **Median**: the middle value after sorting. Robust to outliers (a few extreme values barely move it).
- **Mode**: the most frequent value. Useful for categorical data.

**Dispersion** (how spread out the data is):

- **Variance** $\sigma^2 = \frac{1}{n}\sum_{i=1}^{n}(x_i - \mu)^2$: the average squared distance from the mean.
- **Standard deviation** $\sigma = \sqrt{\sigma^2}$: same idea, in the original units.
- **Range** $= \max(x) - \min(x)$.
- **Interquartile range** $\text{IQR} = Q_3 - Q_1$: the spread of the middle 50% (between the 25th and 75th percentiles). Used for outlier detection. Example on the slide: a high IQR in customer spending suggests very different behaviour across subgroups.

**Shape**:

- **Skewness**: how lopsided the distribution is. Positive skew = long right tail (typical of incomes and loan amounts); negative skew = long left tail.
- **Kurtosis**: how "heavy" the tails are, i.e. how likely extreme values are. High kurtosis → more outliers; low kurtosis → flatter.

### 6.3 Maximum Likelihood Estimation (MLE) (slide 39)

MLE asks: *which parameter value makes the data we actually observed most probable?*

Given data $x_1, \dots, x_n$ and a model with parameter $\theta$, the **likelihood** is the probability of the data under that parameter:

$$L(\theta) = p(x_1, x_2, \dots, x_n \mid \theta)$$

and the MLE is

$$\theta^* = \arg\max_\theta L(\theta).$$

($\arg\max$ means "the value of $\theta$ that makes this as large as possible".) Intuition from the notes: imagine you are trying to explain how your data were generated; MLE picks the explanation under which your data look least surprising. The slide figure shows several candidate curves with the green one fitting best.

In practice (not on the slide, but standard): if the data points are independent, $L(\theta) = \prod_i p(x_i \mid \theta)$, and we maximise the **log-likelihood** $\sum_i \log p(x_i\mid\theta)$ instead because sums are easier than products.

### 6.4 Maximum A Posteriori (MAP) (slide 40)

MAP combines the data with a **prior** belief about the parameter (what you believed before seeing data):

$$\theta^* = \arg\max_\theta P(\theta \mid X)$$

By Bayes' rule $P(\theta\mid X) \propto P(X\mid\theta)\,P(\theta)$, so MAP = likelihood × prior. (The slide only gives the first formula; the Bayes step is our addition.) A useful fact: MAP with a Gaussian prior on the weights is the same as MLE plus **L2 regularisation**, and a Laplace prior gives **L1 regularisation**.

### 6.5 Bias-variance trade-off (slides 41–46)

- **Bias**: error from the model's assumptions being too simple (it systematically misses the true pattern).
- **Variance**: error from the model being too sensitive to the particular training sample (retrain on slightly different data and it changes a lot).

As model complexity goes **up**, bias goes down and variance goes up. As complexity goes **down**, bias goes up and variance goes down.

- High bias → **underfitting** (too simple, misses the signal).
- High variance → **overfitting** (fits the noise in the training data).

**Worked example on the slides** (slides 42–45): the true relationship between X and Y is curved and unknown; we only see noisy points.

| Model | Behaviour | Bias / Variance | MSE on slide |
|---|---|---|---|
| Straight line | assumes linear, misses the curve | high bias, low variance | 0.2929 |
| Degree-4 polynomial | captures the curve, ignores noise | moderate / moderate | 0.0714 |
| Degree-25 polynomial | wiggles through the noise | low bias, high variance | 0.0596 |

Note: the slides do not say whether these MSEs are on training or held-out data. The degree-25 model having the *lowest* MSE only makes sense if it is the training MSE; on fresh data an overfit model would normally do worse than the degree-4 one. Treat the table as illustrating the shapes of the fits, not as a test-set comparison.

The goal (slide 46) is a balance that **generalises**.

### 6.6 Regularisation (slides 47–48)

**Regularisation** prevents overfitting by adding a **penalty for complexity** to what the model minimises, so it balances fitting the data against staying simple.

- **L2 / Ridge**: penalty proportional to the *squared* weights, $\lambda\sum_j \theta_j^2$. Keeps all features but shrinks them; spreads importance across features.
- **L1 / Lasso**: penalty proportional to the *absolute* weights, $\lambda\sum_j |\theta_j|$. Can push some weights to exactly zero, so it effectively does **feature selection** (sparsity).

$\lambda$ (lambda) is a hyperparameter: bigger $\lambda$ = stronger penalty = simpler model. (The slides describe the penalties in words; the formulas are the standard ones.)

---

## 7. Feature engineering (slides 49–59)

### 7.1 What and why (slides 50–51)

**Feature engineering** turns raw data into meaningful inputs and selects the useful ones. It directly affects accuracy, training speed and generalisation. Pipeline: collect → clean → transform → create → extract/select → validate → train. It is **context-dependent** and needs domain knowledge.

### 7.2 Feature transformation (slides 52–55)

*Feature transformation* converts a feature into a form a model can use better: it makes patterns visible, can improve accuracy and speed, and helps meet algorithm assumptions.

- **Binning (discretisation)**: continuous → categories (Age → Young / Middle-aged / Old).
- **Scaling**:
  - Min-max: $x' = \dfrac{x - \min}{\max - \min}$ (maps to [0, 1]).
  - Standardisation (z-score): $z = \dfrac{x - \mu}{\sigma}$ (mean 0, std 1).
- **Shape transforms**: log, square root (to tame right-skewed data).

**Categorical features** (slide 55):

- **Label encoding**: give each category an integer (Red=1, Blue=2, Green=3). Implies a fake order, so be careful with linear models.
- **One-hot encoding**: one binary column per category (Red=[1,0,0], Blue=[0,1,0], Green=[0,0,1]). (The slide has a typo, listing Green as [0,1,0].)
- **Ordinal encoding**: integers when there is a real order (small < medium < large).
- **Target encoding**: replace each category with the average target for that category (e.g. City → average house price). *Warning, not on the slide:* this uses the label, so it must be computed on training folds only or it leaks the answer (see Lecture 3).

### 7.3 Missing data (slide 56)

- **Deletion** of rows/columns.
- **Mean/median imputation** (fill with a simple statistic).
- **KNN imputation** (fill using similar rows).
- **Model-based imputation** (predict the missing value from other columns).

### 7.4 Outliers (slide 57)

An *outlier* is a point far from the rest that can distort learning.

- Detect: **z-score** (e.g. $|z| > 3$) or the **IQR rule** (outside $[Q_1 - 1.5\,\text{IQR},\ Q_3 + 1.5\,\text{IQR}]$; the 1.5 factor is the usual convention, not stated on the slide).
- Treat: remove, **cap** (clip to a limit, also called winsorising), or transform (e.g. log).

### 7.5 Feature extraction vs selection (slide 58)

- A **feature** is one measurable property of a data point.
- **Feature extraction**: build a *new* set of features from raw data (e.g. PCA components, aggregates).
- **Feature selection**: keep a *subset* of the original features to improve performance, interpretability and efficiency, and to reduce overfitting.

### 7.6 Discussion questions (slide 59)

1. *When does feature engineering hurt performance?* (Our answer: when features leak the target, when they are built using test data, when too many noisy features cause overfitting, or when a transform throws away real signal.)
2. *Explain how model complexity relates to bias and variance, and how this affects over- vs underfitting.* (See section 6.5.)

---

## How this applies to Prosit 2

- **Problem formulation (pipeline step 1).** Write down the two targets explicitly: (a) probability of default (binary classification, ~1.83% positives) and (b) loan amount (regression). Define "success" in business terms (expected cost of errors), not just accuracy. With 1.83% defaults, a model that always says "no default" is 98.17% accurate and useless.
- **Data splitting (step 6).** The slide's random 70/15/15 split is the textbook default, but it is *wrong* for our data: the same customer appears in many loans, and loans happen over time. Use **GroupKFold by customer** and a **temporal (train-on-past, test-on-future) split** instead. See Lecture 3 (leakage).
- **Evaluation metrics (step 9).** Accuracy is misleading under imbalance; prefer precision, recall, F1, PR-AUC, plus calibration and cost-based thresholds. For loan amount, report MAE/RMSE (and consider a log transform because amounts are right-skewed).
- **Descriptive statistics / skewness.** Loan amounts and transaction values are right-skewed with heavy tails: use the median and IQR in EDA, log-transform the amount target, and use IQR/z-score rules carefully for outliers (a big borrower is not an error).
- **MLE.** Logistic regression is fitted by maximum likelihood; the Prosit's required derivation starts from $L(\theta) = \prod_i p_i^{y_i}(1-p_i)^{1-y_i}$ (see Lecture 4 and the MIT notes file).
- **MAP / regularisation.** L2 (ridge) logistic regression is a MAP estimate with a Gaussian prior; L1 can drop useless features. Tune $\lambda$ (in sklearn, `C = 1/λ`) inside cross-validation.
- **Bias-variance.** Compare a simple logistic regression (higher bias, stable, interpretable reason codes) with gradient boosting (lower bias, higher variance). Use CV variance across folds and bootstrap CIs to see which differences are real.
- **Feature engineering.** Customer-history features (previous loans, past repayment behaviour) are likely the strongest signal, but must use *only information available before the loan decision*. Target encoding of categories (e.g. region, product) must be fitted inside each training fold.
- **Missing data.** Missing values in mobile-money data may themselves be informative (e.g. a new customer with no history); consider adding "is missing" indicator features rather than only imputing.
- **Unsupervised ideas.** Anomaly detection and clustering are optional extras (e.g. segmenting borrowers), not the core task.

### Slide content we could not read

Slides 5, 10, 26 and 28 are images, video or diagrams with no extractable text. Several other slides contain pictures (e.g. the MLE curve figure on slide 39 and the polynomial-fit plots on slides 43–45) that are described only through their text.
