# Lecture 5: A Survey of Supervised Learning Algorithms

> Study notes written in our own words from the "A Survey of Supervised Learning Algorithms" deck (50 slides; .pptx and .pdf both read).
> Covers: Decision Trees, Random Forests, Gradient Boosting, SVM, KNN, Naive Bayes. Slide numbers refer to the original deck.

## What this lecture is about

Lecture 4 built linear and logistic regression. This lecture surveys six other classic supervised algorithms and shows they all follow the same recipe: **choose a hypothesis space** (the family of functions the model can represent) → **define a loss** → **optimise** → **validate with cross-validation**. For each algorithm it gives the core idea, how it is trained, its key hyperparameters, and its strengths and weaknesses. It explains the two big ensemble ideas, **bagging** (random forests: many independent deep trees averaged to cut variance) and **boosting** (gradient boosting: many shallow trees added one after another, each fixing the previous errors, to cut bias). It closes with a side-by-side comparison, a practical guide to choosing an algorithm, and common pitfalls (scaling, class imbalance, leakage, tuning on the test set).

---

## 1. Objectives, recap and taxonomy (slides 2–6)

**Objectives** (slide 2): describe the idea, training and hyperparameters of six algorithms; contrast them (hypothesis space, scalability, interpretability, robustness to noise); explain bagging vs boosting; choose and justify an algorithm; compare candidates with train/validation/test splits, k-fold CV and proper metrics.

**Recap** (slide 3): learn $f: X \to y$ from labelled examples. Classification = finite classes; regression = continuous values. Every algorithm today: hypothesis space → loss → optimise → validate with k-fold CV.

**Taxonomy** (slide 4):

| Family | Algorithms |
|---|---|
| Tree-based | decision tree, random forest, gradient boosting |
| Margin-based | support vector machine (SVM) |
| Distance-based | k-nearest neighbours (KNN) |
| Probabilistic | naive Bayes |

**Ensembles** combine many weak models into one strong model.

**What separates algorithms?** (slide 5)

- Hypothesis space: line, tree, kernel, neighbourhood, distribution?
- Training: closed form, greedy splitting, gradient descent, or none at all?
- Assumptions about the data.
- Practical: training vs prediction cost; **interpretability** (white box like a tree vs black box like boosting or kernel SVM); sensitivity to scaling, noise, outliers, missing values; how much data/features it needs.

**Evaluation recap** (slide 6):

- Never evaluate on training data; hold out train/validation/test.
- k-fold CV: train $k$ times, average the score.
- Tune hyperparameters only inside the validation loop.
- Classification metrics: accuracy, precision, recall, F1, ROC-AUC. Regression: MAE, MSE/RMSE, $R^2$.
- Overfitting pattern: low training error, high validation error.
- **Leakage**: fit scaling/encoding inside each fold.

---

## 2. Decision trees (slides 7–16)

### 2.1 What a tree is (slides 8–9)

A **decision tree** works for classification and regression. Structure: **root** (first question) → **internal nodes** (more questions) → **branches** (answers) → **leaves** (predictions). It splits the data so each leaf is as **pure** as possible (a pure leaf contains examples that all have the same label). Needs little preprocessing: **no feature scaling**, mixed feature types are fine.

Worked example (slide 9): "will the customer purchase?"

- Root: Income > \$50K? No → No purchase.
- Yes → Age > 30? No → No purchase.
- Yes → Previous purchases > 0? Yes → Purchase; No → No purchase.

**Building it (recursive splitting):** start with all data at the root; pick the question that best separates classes; repeat on each subset until pure or a stopping rule fires. **Predicting:** walk from root to leaf.

### 2.2 Choosing the best split: entropy and information gain (slide 10)

**Entropy** measures how mixed a node is:

$$H(S) = -\sum_{c} p(c)\log_2 p(c)$$

where $p(c)$ is the fraction of class $c$ in node $S$. $H = 0$: pure. $H = 1$: 50/50 mix (binary).

**Information gain** = uncertainty before − weighted uncertainty after:

$$IG = H(\text{parent}) - \sum_k \frac{|S_k|}{|S|}\,H(S_k)$$

Choose the split with the highest gain (equivalently, the lowest weighted child impurity). Regression trees use the same idea with **variance / MSE** instead of entropy.

### 2.3 Gini impurity (slide 11)

$$\text{Gini}(S) = 1 - \sum_c p(c)^2$$

The probability of mislabelling a random item if you labelled it randomly according to the node's class mix. Pure → 0; balanced binary → 0.5. **CART** (what scikit-learn uses) uses Gini; **ID3/C4.5** use information gain. They give very similar trees; Gini is slightly cheaper (no logs). For regression, pick the split minimising MSE in the leaves.

### 2.4 Worked example: will a student pass? (slides 12–14)

| Student | Studied | Attendance | Pass |
|---|---|---|---|
| 1 | Yes | High | Yes |
| 2 | Yes | High | Yes |
| 3 | Yes | Low | Yes |
| 4 | Yes | Low | Yes |
| 5 | No | High | Yes |
| 6 | No | High | No |
| 7 | No | Low | No |
| 8 | No | Low | No |

**Root entropy**: 5 Yes, 3 No.
$H(S) = -\tfrac58\log_2\tfrac58 - \tfrac38\log_2\tfrac38 \approx 0.954$.

**Split on Studied:**

- Yes: 4 Yes, 0 No → $H = 0$ (pure).
- No: 1 Yes, 3 No → $H = -\tfrac14\log_2\tfrac14 - \tfrac34\log_2\tfrac34 \approx 0.811$.
- Weighted: $\tfrac48(0) + \tfrac48(0.811) = 0.4055$. **IG ≈ 0.954 − 0.4055 = 0.549.**

**Split on Attendance:**

- High (1, 2, 5, 6): 3 Yes, 1 No → $H \approx 0.811$.
- Low (3, 4, 7, 8): 2 Yes, 2 No → $H = 1$.
- Weighted: $\tfrac48(0.811) + \tfrac48(1) = 0.9055$. **IG ≈ 0.954 − 0.9055 = 0.049.**

→ **Studied** removes much more uncertainty, so it becomes the root.

**Recurse on Studied = No** (students 5–8; parent $H = 0.811$). Only Attendance is left:

- High (5, 6): 1 Yes, 1 No → $H = 1$.
- Low (7, 8): 0 Yes, 2 No → $H = 0$.
- Weighted: $\tfrac24(1) + \tfrac24(0) = 0.5$. IG $= 0.811 - 0.5 = 0.311$.

Final tree:

```
Studied?
├── Yes → Pass
└── No → Attendance?
         ├── High → mixed 50/50 (can't separate further with these features)
         └── Low  → Fail
```

### 2.5 Growing, stopping and pruning (slide 15)

- **Stopping rules**: node is pure; `max_depth`; `min_samples_split`; `min_samples_leaf`; minimum gain threshold.
- A deep tree **memorises noise** (high variance).
- **Pre-pruning**: stop growth early using those hyperparameters.
- **Post-pruning (cost-complexity)**: grow fully, then cut branches that don't help on validation data.
- Pruning is **model selection for trees**.

### 2.6 Strengths and limits (slide 16)

| Strengths | Limitations |
|---|---|
| very interpretable (IF–THEN rules) | **high variance**: small data change → different tree |
| little preprocessing; unaffected by monotone transforms (e.g. log) | axis-aligned splits struggle with diagonal boundaries |
| classification, regression, mixed types | greedy splits are locally, not globally, optimal |
| fast predictions; free feature-importance ranking | overfits without pruning; biased toward high-cardinality features |

---

## 3. Random forests (slides 17–22)

### 3.1 From one tree to many (slide 18)

A single deep tree has low bias but **high variance**. Idea: grow many *different* trees and combine them. Averaging many diverse trees cuts variance without adding much bias. **Random forest = bagged decision trees + random feature subsets.** Diversity is the engine: different data + different features → errors that don't line up (are uncorrelated), so they cancel.

### 3.2 Bagging (bootstrap aggregating) (slide 19)

- **Bootstrap sample**: draw $n$ rows *with replacement* from $n$ rows. Each sample contains about **63%** unique rows (because the chance a row is never picked is $(1 - 1/n)^n \approx e^{-1} \approx 0.37$).
- Train one full tree per sample.
- At each split, consider only a **random subset of features** (e.g. $\sqrt{p}$ of $p$ features) → **decorrelated** trees.
- Combine: **majority vote** (classification) or **average** (regression).
- Trees are independent → training parallelises.

### 3.3 Algorithm and hyperparameters (slide 20)

1. Draw $B$ bootstrap samples.
2. Grow a deep tree on each; at each node consider only a random feature subset.
3. Grow fully; pruning is unnecessary.
4. Aggregate (vote or average).

scikit-learn `RandomForestClassifier` / `RandomForestRegressor`:

- `n_estimators` ($B$): more trees → more stable; diminishing returns.
- `max_depth`, `min_samples_leaf`: tree complexity.
- `max_features`: how much randomness.
- `class_weight='balanced'`: for **imbalanced classes**.

### 3.4 Out-of-bag error and feature importance (slide 21)

- **Out-of-bag (OOB) error**: about 37% of rows are left out of each bootstrap sample. Each tree can be tested on its own left-out rows; averaging gives an OOB score ≈ cross-validated accuracy, with no separate validation split. (*Caveat, ours:* OOB treats rows as independent; with repeated customers it leaks just like random k-fold.)
- **Impurity-based importance**: total Gini reduction from a feature's splits.
- **Permutation importance**: shuffle one feature, measure how much the score drops. More reliable when features are correlated.
- Importances are for **screening, not causal claims**.

### 3.5 Strengths and limits (slide 22)

Strengths: robust with little tuning; handles non-linearity and interactions without scaling; OOB error and importances built in.
Limits: memory-heavy and slow with many deep trees; less interpretable than one tree; can overfit very noisy labels; **regression forests cannot extrapolate** beyond the training range (they can only average seen targets).

---

## 4. Gradient boosting (slides 23–29)

### 4.1 The boosting idea (slide 24)

Build models **sequentially**; each new model targets the current ensemble's errors. Each new model is fitted to the **negative gradient of the loss** (for squared error this is just the **residuals** $y - \hat y$). Works with any differentiable loss (MSE, log-loss, ...). Base learners are **shallow trees** (depth 1–8). Contrast: bagging trains trees independently; boosting trains them one after another.

### 4.2 Step by step (slide 25)

1. Start with a constant $F_0$: mean of the labels (regression) or the base rate (classification).
2. Compute the loss gradient (residuals for squared loss; "pseudo-residuals" otherwise).
3. Fit a shallow tree $h_m$ to the negative gradient.
4. Update $F_m(x) = F_{m-1}(x) + \eta\, h_m(x)$; repeat for $M$ trees.

Final prediction: $\hat y = F_0 + \sum_{m=1}^{M} \eta\, h_m(x)$. Each tree moves the ensemble a small step downhill on the loss surface: it is gradient descent in "function space".

> **Tiny worked example (ours).** Targets 10, 20, 30. $F_0 = 20$. Residuals: −10, 0, +10. A tree fits these residuals; with $\eta = 0.1$ predictions become 19, 20, 21. New residuals −9, 0, +9 are fitted by the next tree, and so on, slowly closing the gap.

### 4.3 Learning rate vs number of trees (slide 26)

- **Learning rate** $\eta \in (0, 1]$ (shrinkage): small $\eta$ is safer but needs more trees; large $\eta$ is fast but risks overfitting. Typical: $\eta = 0.01$–$0.1$ with 100–1000+ trees.
- Many weak trees ≈ few strong trees.
- **Subsample** (stochastic GB): train each tree on a fraction of rows.
- **Depth**: stumps (depth 1) give an additive model; deeper trees capture interactions.
- **Early stopping**: stop when validation error starts rising.
- Regularisation: `max_depth`, `min_samples_leaf`.

### 4.4 AdaBoost vs gradient boosting (slide 27)

| Aspect | AdaBoost | Gradient boosting |
|---|---|---|
| What the next learner fixes | re-weights misclassified points | fits the negative gradient of the loss |
| Base learners | stumps (depth 1) | shallow trees (depth 3–8) or linear models |
| Loss | exponential (implicit) | explicit differentiable loss (MSE, log-loss) |
| Noise sensitivity | high (chases outliers) | lower (gradients smooth updates) |
| Optimisation | no explicit loss | directly minimises chosen loss |
| Best for | clean data, simple learners | large tabular data, top accuracy |

### 4.5 Strengths and limits (slide 28)

Strengths: state of the art on many **tabular** problems; flexible losses; captures interactions and non-linearity; built-in regularisation ($\eta$, depth, subsample); feature importances.
Limits: many hyperparameters to tune; sequential (harder to parallelise); overfits noisy data if pushed; slower predictions (every tree runs).

### 4.6 Bagging vs boosting (slide 29)

| Bagging (random forest) | Boosting (gradient boosting) |
|---|---|
| trees trained independently, in parallel | trees trained sequentially, each fits residuals |
| deep trees; goal = **cut variance** | shallow trees; goal = **cut bias** |
| many uncorrelated voters → stable | errors corrected one after another |
| minimal tuning; insensitive to noise | more tuning; sensitive to noise and outliers |

---

## 5. Support vector machines (slides 30–35)

### 5.1 Maximum margin (slides 31–32)

Many lines can separate two classes; an **SVM** picks the one **farthest from the nearest points** of either class. A wider **margin** (gap) absorbs more noise in new points. Only the closest points, the **support vectors**, determine the boundary. Works well in high dimensions (text, gene expression).

- Hyperplane: $w \cdot x + b = 0$; predict $\text{sign}(w\cdot x + b)$.
- Margin width $= 2/\|w\|$, so maximising the margin = minimising $\|w\|^2$.
- Objective: $\tfrac12\|w\|^2 + C\sum_i \xi_i$ where $\xi_i$ are slack variables (hinge-loss penalty).
- **Hinge loss** $\max(0, 1 - y(w\cdot x + b))$: zero when correct and outside the margin; grows linearly otherwise.
- **Dual form**: the data appear only as dot products → enables the kernel trick.
- Multiclass via one-vs-one or one-vs-rest. Predictions depend only on support vectors → memory-efficient.

### 5.2 Hard vs soft margin (slide 33)

- **Hard margin**: needs perfectly separable data; one outlier can ruin it.
- **Soft margin**: slack $\xi$ allows violations. Hyperparameter $C$: large $C$ = strict (narrow margin, few training errors); small $C$ = tolerant (wide margin, more errors allowed). Choose $C$ by cross-validation.

### 5.3 Kernel trick (slide 34)

If data aren't linearly separable, map them to a higher-dimensional space $\phi(x)$ where they are. A **kernel** $K(x, z) = \phi(x)\cdot\phi(z)$ computes the similarity without ever building $\phi$. Common kernels: linear, polynomial, **RBF (Gaussian)** $K = \exp(-\gamma\|x - z\|^2)$ ($\gamma$ = how far each point's influence reaches), sigmoid. Tune $C$ and $\gamma$ together by CV.

### 5.4 Strengths and limits (slide 35)

Strengths: effective in high dimensions; kernels handle non-linear boundaries; soft margin is robust to outliers; memory-efficient.
Limits: training cost grows steeply (roughly quadratically or worse) with $n$; kernel, $C$, $\gamma$ need tuning; **needs feature standardisation**; noisy overlapping classes hurt; hard to interpret. (Also, ours: SVM scores are not probabilities; they need calibration.)

---

## 6. k-nearest neighbours (slides 36–40)

### 6.1 Lazy, instance-based learning (slide 37)

Stores the whole training set and learns nothing up front (**lazy learner**); all work happens at prediction time. **Non-parametric**: no assumption about the data distribution. Predict by majority vote (classification) or average (regression) of the $k$ nearest neighbours. Assumption: similar points have similar labels.

### 6.2 Algorithm and distances (slide 38)

1. Choose a distance metric (Euclidean by default).
2. Compute distance from the new point to all training points.
3. Take the $k$ nearest; vote/average. (Weighted variant: closer neighbours count more.)

- Euclidean $\sqrt{\sum_i (x_i - z_i)^2}$: default for continuous features.
- Manhattan $\sum_i |x_i - z_i|$: more robust to outliers.
- Hamming: categorical. Minkowski generalises Euclidean and Manhattan.
- **Scale features first**: distance is scale-sensitive.

### 6.3 Choosing $k$ (slide 39)

- Small $k$: wiggly boundary, noise-sensitive → overfitting.
- Large $k$: smooth boundary, misses local structure → underfitting.
- Odd $k$ avoids ties in binary problems.
- Choose by the elbow of error vs $k$, or by CV.
- **Curse of dimensionality**: in high dimensions everything is nearly equidistant. Remedies: feature selection, PCA, feature weighting.
- Prediction cost $O(n\cdot d)$ per query; KD-trees / approximate nearest neighbours speed it up.

### 6.4 Strengths and limits (slide 40)

Strengths: simplest baseline; no training; handles multiclass naturally; captures irregular boundaries; no distribution assumptions.
Limits: slow predictions; memory-heavy; sensitive to scaling and irrelevant features; degrades in high dimensions; **needs balanced data** (with a rare class the neighbours are almost always the majority).

---

## 7. Naive Bayes (slides 41–45)

### 7.1 Bayes' theorem and the naive assumption (slide 42)

$$P(y \mid x) = \frac{P(y)\,P(x \mid y)}{P(x)} \quad\Rightarrow\quad \text{posterior} \propto \text{prior} \times \text{likelihood}$$

**Naive assumption**: features are **conditionally independent given the class**, so $P(x\mid y) = \prod_i P(x_i \mid y)$. A hard joint probability becomes simple one-feature counting. Learn priors and likelihoods from training frequencies; predict the class with the highest posterior (**MAP**).

### 7.2 Variants (slide 43)

- **Gaussian**: continuous features, $P(x_i\mid y) \sim \text{Normal}(\mu, \sigma)$.
- **Multinomial**: word counts (documents, sentiment).
- **Bernoulli**: binary presence/absence (spam keyword flags).

Shines with high-dimensional sparse text, small training sets, and real-time prediction (training is just counting). Discretise continuous features if Gaussian fits badly.

### 7.3 Worked example: spam (slide 44)

Email contains {free, offer}.

| | Prior | P(free \| class) | P(offer \| class) | Score |
|---|---|---|---|---|
| spam | 0.4 | 0.6 | 0.4 | 0.4 × 0.6 × 0.4 = 0.096 |
| ham | 0.6 | 0.1 | 0.2 | 0.6 × 0.1 × 0.2 = 0.012 |

Normalise: $P(\text{spam}\mid x) = 0.096 / (0.096 + 0.012) \approx 0.89$ → classify as spam.

Practical details: multiplying many small probabilities underflows → **sum logs** instead. **Laplace smoothing** (+1 to counts) stops an unseen word from zeroing the product. Independence is almost never true, yet the *ranking* still works well. **Probabilities are often poorly calibrated**; the decision boundary is what matters.

### 7.4 Strengths and limits (slide 45)

Strengths: very fast; works with tiny data and huge feature spaces; natural for text; simple, interpretable, probabilistic.
Limits: independence assumption usually violated; zero probabilities without smoothing; ignores interactions/correlations; loses to logistic regression/boosting when features are correlated.

---

## 8. Comparison, choosing, pitfalls (slides 46–49)

### 8.1 Side by side (slide 46)

| Algorithm | Family | Training | Key hyperparameters | Strength | Watch out |
|---|---|---|---|---|---|
| Decision tree | tree | greedy recursive splits | max_depth, min_samples_leaf, criterion | interpretable rules; little preprocessing | high variance; overfits |
| Random forest | bagging ensemble | parallel deep trees on bootstraps | n_estimators, max_features, max_depth | robust, low tuning, importances | slow; memory-heavy |
| Gradient boosting | boosting ensemble | sequential trees on residuals | learning_rate, n_estimators, max_depth | top accuracy on tabular data | many knobs; noise-sensitive |
| SVM | margin | convex optimisation | C, kernel, γ | great in high dimensions; kernels | needs scaling; slow for large n |
| KNN | instance | none (stores data) | k, distance, weighting | simple; instant "training" | slow predictions; curse of dimensionality |
| Naive Bayes | probabilistic | counting / MLE | smoothing α, variant | fast; small data; text | independence assumption |

### 8.2 Choosing an algorithm (slide 47)

- Need explainability → decision tree.
- Tabular data, maximum accuracy → gradient boosting (XGBoost / LightGBM / CatBoost).
- Robust with minimal tuning → random forest.
- Text / spam / tiny data → naive Bayes.
- High dimensions, clean margin → SVM.
- Small data, quick baseline → KNN; **always keep logistic regression as a baseline.**
- Irrelevant/redundant features → select features first.
- Unsure → try 2–3 candidates and let cross-validation decide.

### 8.3 Common pitfalls (slide 48)

- Forgetting to scale (SVM and KNN need it; trees don't).
- **Class imbalance: accuracy lies** → use F1 / PR-AUC, class weights, resampling.
- Leakage: fit scalers, encoders and selectors inside CV folds only.
- **Tuning on the test set** → optimistic bias; use **nested CV** (an inner CV loop for tuning inside an outer CV loop for evaluation) for honest estimates.
- Ignoring training cost and inference latency.
- More complexity ≠ better: start simple, add complexity only if CV improves.

### 8.4 Summary (slide 49)

Six ways to carve up feature space: single splits (tree), random splits + votes (forest), sequential error correction (boosting), maximum margin (SVM), neighbourhoods (KNN), Bayes probabilities (naive Bayes). Ensembles trade interpretability for accuracy and robustness. **No free lunch**: no algorithm is best everywhere; match assumptions, data size, dimensionality and latency to the task.

---

## How this applies to Prosit 2

- **Candidate models.** The lecture's own guide points to: logistic regression (baseline, interpretable, reason codes), random forest (robust), and gradient boosting (best accuracy on tabular data, e.g. LightGBM/XGBoost/`HistGradientBoostingClassifier`). Compare them under the *same* GroupKFold-by-customer CV and report bootstrap CIs on the differences.
- **Imbalance (1.83% defaults).** Slide 48 says it directly: accuracy lies. Use PR-AUC, recall/precision at the chosen threshold, and cost. Try `class_weight='balanced'` (forests/LR) or `scale_pos_weight` (boosting), then **recalibrate**.
- **Calibration.** Trees, forests, boosting with reweighting, SVMs and naive Bayes all tend to give poorly calibrated probabilities. Since the lender needs real default probabilities (for pricing and expected loss), fit an isotonic or Platt calibrator on out-of-fold predictions and check reliability curves / Brier score.
- **Reason codes.** Logistic regression gives reason codes directly from $\theta_j x_j$. For tree ensembles you need post-hoc methods (e.g. SHAP or per-feature contribution); permutation importance (slide 21) is for global screening, not individual explanations. Mind slide 21's warning: importance is not causation.
- **Out-of-bag error is not enough.** OOB assumes independent rows; with repeated customers, it leaks like random k-fold. Use GroupKFold scores, not OOB, for model selection.
- **Loan amount regression.** Forests can't extrapolate beyond the training range (slide 22); boosting has the same limitation with trees. For Ghana, where loan sizes may differ, check whether predictions hit the training range boundaries.
- **Hyperparameter tuning.** Use nested CV (or a CV for tuning + a separate temporal test set) to avoid optimistic bias. Early stopping for boosting must use a validation fold, not the test set.
- **Scaling.** Needed for logistic regression (with regularisation), SVM and KNN; not for trees. Put scalers inside the pipeline.
- **High-cardinality features.** Trees are biased toward high-cardinality features (slide 16); be cautious with IDs, phone models, locations. Customer ID must **never** be a feature.
- **Fairness.** Simpler, interpretable models make it easier to audit whether protected or proxy features drive decisions; weigh any accuracy gain from boosting against explainability needs.

### Slide content we could not read

All slides had extractable text. A few slides (4, 8, 19, 24, 31, 34, 37, 42) also contain illustrative images that are described only through their text.
