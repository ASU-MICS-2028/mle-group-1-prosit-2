# Lecture 4: Supervised Learning (Linear Regression, Linear Classification, Logistic Loss, Cross-Validation)

> Study notes written in our own words from the "Supervised Learning" deck (56 slides; both the .pptx and .pdf versions were read).
> Slide numbers refer to the original deck. Formulas are re-typed in LaTeX.

## What this lecture is about

This is the core "how do models actually learn" lecture. It sets up supervised learning (learning a mapping from inputs to labelled outputs), then builds **linear regression** from scratch: the hypothesis $h_\theta(x) = \theta^T x$, the **mean squared error** loss, and two ways to find the best parameters: the **closed-form ordinary least squares** solution $\theta^* = (X^TX)^{-1}X^Ty$ and **gradient descent** (including step-size choice and batch vs mini-batch). It then moves to **binary classification** with linear classifiers, explains why the natural 0-1 loss can't be optimised with calculus, and argues step by step for a smooth, convex surrogate: the **logistic loss** $\log(1 + e^{-y\hat y})$, which is what logistic regression minimises. It ends with **model selection**: why training error is misleading, train/validation/test splits, and **k-fold cross-validation**.

---

## 1. Learning objectives (slide 2)

By the end you should be able to:

1. Write a linear regression model and its MSE cost function.
2. Explain gradient descent and compute update steps by hand.
3. Tell linear regression and logistic regression (classification) apart.
4. Explain what a classification loss needs and write down the logistic regression loss.
5. Use k-fold cross-validation to estimate generalisation and avoid overfitting.

---

## 2. Supervised learning foundations (slides 3–9)

**Supervised learning** (slide 3): learn to map an input $x$ to an output $y$ from a training set of examples $(x, y)$. What makes it "supervised" is that the dataset contains **labelled outputs (targets)**.

Five core concepts (slides 4–8):

- **Data.** Tables of numbers/words, pixels, audio waveforms. A dataset is made of **examples**, each with **features** (inputs) and a **label** (output). Datasets are described by **size** (number of examples), **diversity** (how much of the possible range they cover) and **number of features**. More features *can* reveal more patterns, but features with no real relationship to the label don't help and can hurt.
- **Model.** A collection of numbers (parameters) defining the mathematical relationship between features and label.
- **Training.** The process of finding those numbers from data.
- **Evaluation.** Give a trained model only the *features* of labelled examples, then compare its predictions with the true labels.
- **Inference.** Using the trained model on new, real-world inputs.

Two kinds of supervised task (slide 9):

- **Regression**: output is continuous (house price, temperature).
- **Classification**: output is one of a small set of classes (spam/not spam, disease positive/negative).

---

## 3. Regression and linear regression (slides 10–21)

### 3.1 The regression problem (slides 10–16)

**Regression** finds the relationship between a dependent variable (the label) and one or more independent variables (the features). Goal: learn $f : \mathbb{R}^d \to \mathbb{R}$, a function taking $d$ numeric features and returning one number (slide 15).

Two big design choices (slide 16):

1. What **family of functions** $f$ do we allow (lines, curves, ...)?
2. How do we **measure goodness of fit**?

Slides 11–14 are example scatter plots (images only).

### 3.2 Problem formulation (slide 17)

Dataset $D = \{(x^{(1)}, y^{(1)}), \dots, (x^{(n)}, y^{(n)})\}$ with

- $x^{(i)} \in \mathbb{R}^d$: the feature vector of example $i$, $x^{(i)} = [x^{(i)}_1, \dots, x^{(i)}_d]^T$,
- $y^{(i)} \in \mathbb{R}$: its real-valued target.

Find $h_\theta(x)$ mapping features to a prediction $\hat y$, assuming a **linear** relationship.

### 3.3 The hypothesis (slide 18)

$$h(x; \theta, \theta_0) = \theta^T x + \theta_0$$

$\theta$ (the weights) and $\theta_0$ (the intercept or bias) are the **parameters**. The prediction is written $\hat y = f(x) = h_\theta(x)$.

- 1 feature: $h_\theta(x) = \theta x + \theta_0$ (a line).
- 2 features: $h_\theta(x) = \theta_1 x_1 + \theta_2 x_2 + \theta_0$ (a plane).
- $d$ features: $h_\theta(x) = \sum_{i=1}^d \theta_i x_i + \theta_0$.

**Trick:** add a constant feature $x_0 = 1$, so $\theta_0$ becomes just another weight: $h_\theta(x) = \sum_{i=0}^{d} \theta_i x_i = \theta^T x$.

### 3.4 The loss: mean squared error (slide 19)

A **loss function** scores how bad the predictions are. Linear regression usually uses **MSE**:

$$J(\theta) = \frac{1}{n}\sum_{i=1}^{n} \big(y^{(i)} - h_\theta(x^{(i)})\big)^2$$

Goal: find $\theta$ that **minimises** $J(\theta)$ over the training data.

Why squared? It is smooth (easy to differentiate), punishes big errors more than small ones, and corresponds to assuming Gaussian noise (Lecture 1).

### 3.5 Method 1: closed-form solution (ordinary least squares) (slides 20–21)

$$\theta^* = \arg\min_{\theta \in \mathbb{R}^{d+1}} \frac{1}{n}\sum_{i=1}^{n}\big(y^{(i)} - h_\theta(x^{(i)})\big)^2$$

Take the derivative, set it to zero, solve. This is **ordinary least squares (OLS)**.

**Derivation** (slide 21). Stack the examples as rows of a matrix $X$ ($n \times (d+1)$, including the column of 1s) and the targets in a vector $y$. Dropping the constant $\tfrac{1}{n}$ (it doesn't change where the minimum is):

$$J(\theta) = \|y - X\theta\|^2 = (y - X\theta)^T(y - X\theta)$$

Expand:

$$J(\theta) = y^Ty - 2\theta^TX^Ty + \theta^TX^TX\theta$$

Differentiate with respect to $\theta$ (matrix calculus):

$$\frac{dJ}{d\theta} = -2X^Ty + 2X^TX\theta$$

Set to zero: $X^TX\theta = X^Ty$ (the "normal equations"), so

$$\boxed{\theta^* = (X^TX)^{-1}X^Ty}$$

This needs $X^TX$ to be invertible (e.g. no perfectly duplicated features). Ridge regularisation fixes non-invertibility (see the MIT notes file).

### 3.6 Method 2: gradient descent (slides 22–24)

**Gradient descent (GD)**: start somewhere and repeatedly step downhill.

$$\theta_{t+1} = \theta_t - \eta\, \nabla_\theta J(\theta_t)$$

- $\nabla_\theta J$ (the **gradient**) is the vector of partial derivatives $\left[\frac{\partial J}{\partial \theta_1}, \dots, \frac{\partial J}{\partial \theta_d}\right]$; it points uphill, so we subtract it.
- $\eta$ (eta) is the **learning rate / step size**.

Algorithm (slide 23):

1. Start with a guess $\theta_0$.
2. Compute the gradient $\nabla J(\theta_0)$.
3. Step: $\theta_1 = \theta_0 - \eta \nabla J(\theta_0)$.
4. Repeat until convergence, e.g. $\|\theta_{t+1} - \theta_t\| < \epsilon$.

Under mild conditions GD reaches a **stationary point** ($\nabla J = 0$). Because MSE is **convex** (bowl-shaped, a single minimum), GD finds the **global** minimum.

**Gradient of MSE** (slide 24; one feature, no intercept for simplicity):

$$\nabla_\theta J(\theta) = \frac{d}{d\theta}\,\frac{1}{n}\sum_{i=1}^{n}(y_i - \theta x_i)^2 = -\frac{2}{n}\sum_{i=1}^{n} x_i\,(y_i - \theta x_i)$$

> **Worked example (ours).** Data: $(x, y) = (1, 2), (2, 4)$; model $\hat y = \theta x$; $\eta = 0.1$; start $\theta = 0$.
> - Step 1: gradient $= -\frac{2}{2}[1\cdot(2-0) + 2\cdot(4-0)] = -10$, so $\theta = 0 - 0.1(-10) = 1$.
> - Step 2: residuals are $2-1=1$ and $4-2=2$; gradient $= -[1\cdot1 + 2\cdot2] = -5$, so $\theta = 1 + 0.5 = 1.5$.
> - The steps keep halving and $\theta \to 2$, the exact fit $y = 2x$.

### 3.7 Choosing the step size (slide 25)

- **Too small**: converges very slowly.
- **Too large**: overshoots the minimum, zig-zags, may **diverge**.
- **Line search**: choose the step adaptively at each iteration, $\eta_t = \arg\min_\eta R(\theta_t - \eta\nabla_\theta R(\theta_t))$, i.e. the step that most reduces the loss along the downhill direction.

### 3.8 Batch vs stochastic / mini-batch (slides 26–28)

- **Batch GD**: each update uses the gradient over **all $n$** examples. Stable but slow on big data.
- **Stochastic / mini-batch GD**: each update uses a small random batch of $B \ll n$ examples (stochastic = $B=1$). Noisier but much faster; balances speed and stability.

Why use GD when a closed form exists? (slide 27)

- **Computation**: inverting $X^TX$ costs roughly $O(d^3)$, painful with many features.
- **Non-linear models** (e.g. logistic regression, neural nets) have **no** closed form.
- You may **not need** the exact optimum.

| Algorithm | Many examples ($m$ large) | Many features ($n$ large) |
|---|---|---|
| Normal equation (closed form) | fast | slow |
| Batch GD | slow | fast |
| Stochastic GD | fast | fast |
| Mini-batch GD | fast | fast |

(Note the slide uses $m$ for examples and $n$ for features here, unlike earlier slides where $n$ is the number of examples.)

---

## 4. Classification (slides 29–46)

### 4.1 Setup (slides 30–31)

**Classification**: supervised learning where $y$ is discrete. We start with **binary** classification: map $\mathbb{R}^d$ to two classes, conveniently encoded $y \in \{-1, +1\}$ (the classes have no real order). Input: labelled examples; output: a **decision rule** (classifier).

### 4.2 Linear classifiers (slides 33–36)

$$h_\theta(x) = \text{sign}(\theta^T x + \theta_0)$$

- The **separator** (decision boundary) is the set of points where $\theta^Tx + \theta_0 = 0$: a line in 2D, a plane/hyperplane in higher dimensions.
- If all positives are on one side and all negatives on the other, the data are **linearly separable**.
- Slides 34–36 show spam/no-spam pictures where a line does or doesn't separate the classes (images only).

### 4.3 Why not just count mistakes? Problems with the 0-1 loss (slide 37)

The **0-1 loss** gives 1 for a wrong prediction and 0 for a right one. Minimising it directly is hard because:

- it is **not smooth**: tiny changes to $\theta$ usually don't change the count, so the gradient is zero almost everywhere;
- two different parameter settings with the same number of mistakes look equally good even if one is much closer to the optimum;
- predictions are hard yes/no; there is **no notion of uncertainty**.

### 4.4 The margin $y\,h_\theta(x)$ (slides 38–39)

$$\ell_{0\text{-}1}(h_\theta(x), y) = \mathbb{1}\big(\text{sign}(h_\theta(x)) \ne y\big) = \mathbb{1}\big(y\,h_\theta(x) < 0\big)$$

because a prediction has the same sign as $y$ exactly when $y\,h_\theta(x) > 0$. So the error depends only on $z = y\,h_\theta(x)$ (often called the **margin**):

- $z > 0$: correct; larger $z$ = more confidently correct.
- $z < 0$: wrong; more negative = more confidently wrong.

So we want a loss $\ell = g(z)$ where $g(z)$ grows as $z$ becomes very negative.

### 4.5 Desired properties and candidate losses (slides 40–46)

To use gradient methods, $g(z)$ should be **decreasing**, **convex** and **differentiable**. Candidates:

| Loss | Formula in $z = y\hat y$ | Behaviour |
|---|---|---|
| Linear | $L_{lin} = \max(0, -y\hat y)$ (slide 41; slide 40 writes $-z$) | correct, far-away points keep contributing; outliers can dominate |
| Logistic | $L_{log} = \log(1 + e^{-y\hat y})$ | large when wrong, → 0 when confidently right; diminishing returns |
| Exponential | $L_{exp} = e^{-y\hat y}$ | explodes for wrong points; unstable, chases noisy outliers |

(Here $\hat y = \theta^Tx + \theta_0$ is the raw score.)

**Logistic loss** (slide 42): misclassified points ($y\hat y < 0$) get large loss; confidently correct points ($y\hat y \gg 0$) get loss near 0. Once a point is safely correct, pushing it further barely helps, so training focuses on **mistakes and points near the boundary** rather than rewarding extreme distances.

**Linear vs logistic** (slide 43, four linearly separable pictures):

- Spread-out classes with far outliers: **logistic ≫ linear** (linear loss is too influenced by far points we don't care about).
- Concentrated, well-separated classes: logistic ≈ linear.
- **Imbalanced classes (a big majority cluster and a small minority):** **logistic ≫ linear** in one picture, because the linear loss maximises distance to the majority class at the expense of mistakes on the minority class. (This is directly relevant to our 1.83% default rate.)

**Logistic vs exponential** (slides 44–45): both are decreasing, convex, differentiable and near zero for correct points. But:

- Exponential's derivative **explodes** for badly misclassified points → unstable optimisation and huge weight on noisy outliers.
- Logistic's derivative magnitude stays between $\tfrac12$ and $1$ for misclassified points → **robust to noisy outliers**.

**Conclusion** (slide 46): wanting decreasing + convex + differentiable + ~zero for correct points + robust to outliers → **logistic loss is the best choice**. Using it with a linear score is **logistic regression**.

### 4.6 Bridging to probability and MLE (our addition, not on the slides)

The slides motivate the logistic loss from its shape. The same loss falls out of **maximum likelihood** (Lecture 0/1):

- Define the **sigmoid** $\sigma(z) = \dfrac{1}{1+e^{-z}}$, which squashes any score into $(0,1)$, and model $P(y = +1 \mid x) = \sigma(\theta^Tx + \theta_0)$.
- Because $1 - \sigma(z) = \sigma(-z)$, for $y \in \{-1,+1\}$ we can write $P(y \mid x) = \sigma(y\,\hat y)$.
- Negative log-likelihood of one example: $-\log \sigma(y\hat y) = \log(1 + e^{-y\hat y})$, exactly the logistic loss.
- With labels $y \in \{0,1\}$ and $p = \sigma(\hat y)$, the same thing reads $-[y\log p + (1-y)\log(1-p)]$ (binary cross-entropy / log-loss). The MIT notes file derives the gradient.

So **minimising logistic loss = maximum likelihood for a Bernoulli model with sigmoid probabilities.** That is why logistic regression outputs (roughly) probabilities, which we then **calibrate** and **threshold**.

---

## 5. Model selection and cross-validation (slides 47–54)

### 5.1 Don't evaluate on training data (slides 48–49)

We want a good model $\hat f_D$ and an estimate of how well it predicts $y$ for *new* $x$. Using the training loss for both training and evaluation is **bad**: it rewards memorisation. Instead, split $D_{full}$ into a **training set** $D$ and a **test set** $D'$, train on $D$, evaluate on $D'$.

### 5.2 The model-selection problem (slide 50)

We often try many models (different features, algorithms, settings) and pick the best by test loss. Problem: picking by test loss makes the test score **optimistically biased** (you tuned to it). Solution: split again:

1. **Training set** $D$: fit each candidate.
2. **Validation set** $D''$: choose the candidate with the smallest error.
3. **Test set** $D'$: compute the error of the chosen model, once.

### 5.3 k-fold cross-validation (slides 51–53)

Problem: with small data it's wasteful to set aside both a validation and a test set.

**k-fold CV**:

1. Set aside the test set $D'$.
2. Split the remaining data into $K$ equal parts $D_1, \dots, D_K$.
3. For split $k$: train on all parts except $D_k$, validate on $D_k$.
4. Average the $K$ validation errors.
5. Pick the model/setting with the lowest average; then evaluate once on $D'$.

### 5.4 How big should $K$ be? (slide 54)

- **Too small**: each model trains on less data (risk of underfitting), and estimates are noisy (risk of overfitting your choice to a particular split).
- **Too large**: generally better estimates, but **more computation** (train $K$ times).

Common choices are $K = 5$ or $10$ (not stated on the slide).

---

## 6. Summary (slide 55)

- Goal: learn $\theta$ that **generalises** to unseen data.
- Choose regression for continuous outputs (minimise distance) and classification for discrete outputs (maximise separation).
- Optimisation is the engine: closed-form OLS or iterative gradient descent.
- Move from the intuitive but un-optimisable 0-1 loss to a **convex surrogate** (logistic loss) so calculus works.
- **Don't trust training error**: use cross-validation and a held-out test set.

---

## How this applies to Prosit 2

- **Default model = logistic regression baseline.** Score $\hat y = \theta^Tx + \theta_0$, probability $p = \sigma(\hat y)$, trained by minimising log-loss. This is our interpretable baseline and the source of **reason codes** (each feature's contribution $\theta_j x_j$ to the score tells the applicant which factors pushed their risk up).
- **Required derivation.** Use section 4.6: start from the Bernoulli likelihood $\prod_i p_i^{y_i}(1-p_i)^{1-y_i}$, take the negative log, show it equals the log-loss, and derive the gradient $\frac{1}{n}\sum_i (p_i - y_i)x_i$ (see the MIT notes file). Mention convexity → gradient descent finds the global optimum.
- **Imbalance and slide 43.** The lecture's own example shows logistic loss handling a small minority class better than linear loss. Still, with 1.83% defaults, consider `class_weight='balanced'` or reweighting; then **recalibrate**, because reweighting distorts predicted probabilities.
- **Thresholds.** Logistic regression gives probabilities; the default 0.5 threshold is meaningless at a 1.83% base rate. Choose the threshold that minimises expected cost (cost of a missed default vs cost of rejecting a good borrower) on validation data.
- **Loan amount = regression.** Start with linear regression (OLS or ridge) on $\log(\text{amount})$, evaluated by MAE/RMSE. MSE assumes roughly symmetric noise; raw amounts are skewed.
- **Gradient descent knobs.** If training with SGD (e.g. `SGDClassifier`), scale features first and watch the learning rate; for `LogisticRegression` sklearn's solvers handle this, but scaling still matters for convergence and for L2 regularisation to be fair across features.
- **Model selection.** Use a three-way structure: CV for choosing models/hyperparameters, a final untouched test set (ideally the latest time period) for the one honest number. Our CV must be **GroupKFold by customer** (Lecture 3), not plain k-fold, and all preprocessing goes in a pipeline.
- **Choosing K.** With only ~1.83% positives, each fold must contain enough defaults; check the number of defaults per fold (consider `StratifiedGroupKFold`) and report the spread of metrics across folds, not just the mean.

### Slide content we could not read

Slides 11–14 and 32 are images only (example plots). Slides 18, 19, 21, 25, 26, 43 and 48–53 have formulas or diagrams stored as pictures; we read these from the PDF version, so their content is included above.
