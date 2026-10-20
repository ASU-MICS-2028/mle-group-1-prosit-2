# MIT 6.390 Lecture Notes (Spring 2024): Chapters Relevant to Prosit 2

> Focused study notes in our own words on selected parts of the MIT 6.390 *Introduction to Machine Learning* lecture notes (Spring 2024), which the course provides as background reading.
> We cover only what Prosit 2 needs: **§1.2–1.3** (assumptions, evaluation criteria), **Ch. 2** (regression, OLS, ridge, evaluating algorithms, cross-validation), **Ch. 3** (gradient descent, SGD), **Ch. 4** (linear logistic classifiers, NLL loss, gradient, convexity, accuracy), **§5.3** (encoding real-world features) and **§9.2** (trees, bagging, random forests).
> Skipped on purpose: neural networks, CNNs, transformers, MDPs/RL, most of unsupervised learning (the course's own Lecture 6 covers k-means and PCA).

## What this reading is about

The MIT notes give a cleaner, more mathematical version of what our Lectures 4 and 5 cover. The key idea throughout is that ML is **optimisation**: choose a hypothesis class, write an objective $J(\Theta) = \text{average loss} + \lambda \times \text{regulariser}$, and minimise it (analytically for least squares, by gradient descent otherwise). For us the most valuable parts are: the **derivation of logistic regression as maximum likelihood** (negative log-likelihood loss and its gradient), the treatment of **prediction thresholds** and asymmetric losses, the idea that **(cross-)validation evaluates a learning algorithm, not one fitted model**, the **i.i.d. assumption** that distribution shift violates, feature-encoding advice, and the tree/ensemble algorithms.

---

## 1. Assumptions and evaluation criteria (§1.2–1.3)

### 1.1 Assumptions (§1.2)

Learning is only possible if you assume a link between training data and future data. Common assumptions:

- the data are **independent and identically distributed (i.i.d.)**: every example is drawn independently from the *same* probability distribution;
- the data come from a Markov chain;
- the data source may be adversarial;
- the true model is in our hypothesis class.

Assumptions shrink the space of hypotheses, so less data is needed. Chapter 2 makes the key one explicit: **training and test data are drawn independently from the same distribution.**

### 1.2 Loss functions (§1.3)

A **loss** $L(g, a)$ is the penalty for guessing $g$ when the actual answer is $a$:

- **0-1 loss**: $0$ if $g = a$, else $1$.
- **Squared loss**: $(g - a)^2$.
- **Absolute loss**: $|g - a|$.
- **Asymmetric loss**: different mistakes cost different amounts. The notes' heart-attack example: $L = 1$ for a false alarm ($g=1, a=0$), $L = 10$ for a miss ($g=0, a=1$), $0$ otherwise.

At the level of the whole predictor we may want to minimise **expected loss (risk)**, minimise the worst-case loss, bound **regret** (how much worse than the best predictor in a class), study behaviour as data grow, or be "probably approximately correct".

---

## 2. Regression (Ch. 2)

### 2.1 Training error vs test error (§2.1)

Hypothesis $h: \mathbb{R}^d \to \mathbb{R}$ with parameters $\Theta$.

- **Training error**: $E_n(h;\Theta) = \frac{1}{n}\sum_{i=1}^{n} L(h(x^{(i)};\Theta), y^{(i)})$.
- **Test error**: the same average over $n'$ **new** examples not used to find $h$.

We fit using training error, but what we care about is test error.

### 2.2 Regression as optimisation (§2.2)

General objective:

$$J(\Theta) = \underbrace{\frac{1}{n}\sum_{i=1}^{n} L\big(h(x^{(i)};\Theta), y^{(i)}\big)}_{\text{fit the data}} + \underbrace{\lambda R(\Theta)}_{\text{prefer simple}}, \qquad \Theta^* = \arg\min_\Theta J(\Theta)$$

The regulariser $R$ encodes a preference among hypotheses (e.g. small weights); $\lambda \ge 0$ sets the trade-off.

### 2.3 Linear regression and OLS (§2.3–2.5)

Hypothesis $h(x;\theta,\theta_0) = \theta^Tx + \theta_0$ with squared loss. §2.4 shows a deliberately silly algorithm (try $k$ random $\theta$'s, keep the best) to make the point that *any* search method is a "learning algorithm", and that more search ($k$) isn't automatically better.

**Analytical solution (§2.5).** Append a constant 1 feature so $\theta_0$ is absorbed. Let $\tilde X$ be the $n\times d$ data matrix and $\tilde Y$ the $n\times1$ targets.

$$J(\theta) = \frac1n(\tilde X\theta - \tilde Y)^T(\tilde X\theta - \tilde Y), \qquad \nabla_\theta J = \frac2n\tilde X^T(\tilde X\theta - \tilde Y)$$

Setting the gradient to zero: $\tilde X^T\tilde X\theta = \tilde X^T\tilde Y$, so

$$\theta = (\tilde X^T\tilde X)^{-1}\tilde X^T\tilde Y$$

(dimensions: $d\times d$ times $d\times n$ times $n\times1$). Same result as Lecture 4, with the $\tfrac1n$ kept.

### 2.4 Regularisation and ridge regression (§2.6)

**Why regularise.** If two features are highly correlated, there is no unique best plane; $\tilde X^T\tilde X$ is nearly singular, its inverse has huge entries, and the fitted slopes become huge and unstable. Also, pure loss minimisation overfits.

A default regulariser pulls weights toward zero: $R(\Theta) = \|\Theta\|^2$ (more generally toward a prior guess, $\|\Theta - \Theta_{prior}\|^2$, which links to Bayesian/MAP ideas).

**Ridge objective** (note $\theta_0$ is **not** penalised; it just sets the overall level):

$$J_{ridge}(\theta,\theta_0) = \frac1n\sum_{i=1}^n\big(\theta^Tx^{(i)} + \theta_0 - y^{(i)}\big)^2 + \lambda\|\theta\|^2$$

If we ignore the special treatment of $\theta_0$:

$$\nabla_\theta J_{ridge} = \frac2n\tilde X^T(\tilde X\theta - \tilde Y) + 2\lambda\theta = 0 \;\Rightarrow\; \theta_{ridge} = (\tilde X^T\tilde X + n\lambda I)^{-1}\tilde X^T\tilde Y$$

Adding $n\lambda$ to the diagonal (the "ridge") makes the matrix **invertible whenever $\lambda > 0$**, fixing both instability and overfitting.

### 2.5 Evaluating hypotheses and learning algorithms (§2.7)

**Two sources of test error** (§2.7.1):

- **Structural error**: no hypothesis in our class can fit the truth (e.g. fitting a line to a sine wave). Also called **bias**.
- **Estimation error**: not enough (or unhelpful) data to pick a good hypothesis, or the optimisation was not solved well. Also called **variance**.

Increasing $\lambda$ tends to **increase structural error and decrease estimation error**, and vice versa.

**Learning algorithms vs hypotheses** (§2.7.2). A **learning algorithm** maps a dataset to a hypothesis: $D_n \to$ learning alg$(\mathcal{H}) \to h$. Settings of the algorithm (like $\lambda$) are **hyperparameters**. Test error varies because of which training examples you happened to get, which test examples, and randomness inside the algorithm.

- **Validation**: repeatedly train on one subset and evaluate on a non-overlapping validation subset.
- **Cross-validation**:

```
CROSS-VALIDATE(D, k)
  split D into k chunks D_1..D_k of roughly equal size
  for i = 1..k:
      train h_i on D minus D_i
      compute error E_i of h_i on D_i
  return (1/k) * sum(E_i)
```

- **Crucial point:** *(cross-)validation neither delivers nor evaluates one particular hypothesis $h$. It evaluates the learning algorithm* (including its hyperparameters) that produces hypotheses.
- **Hyperparameter tuning**: each hyperparameter value is effectively a different learning algorithm; try many and pick the best by validation/CV.

---

## 3. Gradient descent (Ch. 3)

### 3.1 Batch gradient descent (§3.1–3.3)

Repeat $\Theta^{(t)} = \Theta^{(t-1)} - \eta\nabla_\Theta f(\Theta^{(t-1)})$ until the change in $f$ is below a tolerance $\epsilon$. If $f$ is **convex** and $\eta$ is small enough, GD gets arbitrarily close to the global minimum. Too large $\eta$ can oscillate or diverge (as in Lecture 4). For ridge regression the gradients are:

$$\nabla_\theta J_{ridge} = \frac2n\sum_i\big(\theta^Tx^{(i)} + \theta_0 - y^{(i)}\big)x^{(i)} + 2\lambda\theta, \qquad \frac{\partial J_{ridge}}{\partial\theta_0} = \frac2n\sum_i\big(\theta^Tx^{(i)} + \theta_0 - y^{(i)}\big)$$

### 3.2 Stochastic gradient descent (§3.4)

When the objective is a sum over data points, $f(\Theta) = \sum_i f_i(\Theta)$, **SGD** picks one random $i$ per step and uses only $\nabla f_i$:

$$\Theta^{(t)} = \Theta^{(t-1)} - \eta(t)\,\nabla_\Theta f_i(\Theta^{(t-1)})$$

Each step is noisy but points in the right direction on average. For convergence the step size must shrink over time; a sufficient condition (for convex $f$) is

$$\sum_{t=1}^\infty \eta(t) = \infty \quad\text{and}\quad \sum_{t=1}^\infty \eta(t)^2 < \infty$$

(e.g. $\eta(t) = 1/t$): steps must be able to travel arbitrarily far in total, yet get smaller and smaller. Mini-batches sit between batch GD and single-example SGD.

---

## 4. Classification and logistic regression (Ch. 4)

### 4.1 Linear classifiers and why 0-1 loss is hard (§4.2–4.3)

Linear classifier: $h(x) = \text{sign}(\theta^Tx + \theta_0)$; boundary $\theta^Tx + \theta_0 = 0$. Minimising the 0-1 training error is **NP-hard** in general, because the objective is not smooth: nearby parameters often have identical error, and predictions carry no degree of certainty. So we change the hypothesis class.

### 4.2 Linear logistic classifiers (§4.3.1)

$$h(x;\theta,\theta_0) = \sigma(\theta^Tx + \theta_0), \qquad \sigma(z) = \frac{1}{1+e^{-z}}$$

The **sigmoid** maps any real $z$ into $(0,1)$, with $\sigma(0) = 0.5$. Interpret the output as $P(y = 1 \mid x)$. The size of $\theta$ controls how steep the curve is; $\theta_0$ shifts where it crosses 0.5.

**Prediction threshold.** To output a class, predict 1 if $\sigma(\theta^Tx+\theta_0) > 0.5$. But the notes stress the threshold is a choice: **decision theory** says if one type of error is much worse, move the threshold. E.g. if false positives are much worse, raise it above 0.5.

### 4.3 Maximum likelihood → negative log-likelihood loss (§4.3.2)

Use labels $y \in \{0,1\}$ and write the guess $g^{(i)} = \sigma(\theta^Tx^{(i)} + \theta_0)$. Assuming independent examples, the probability the model assigns to the observed labels is

$$\prod_{i=1}^n \begin{cases} g^{(i)} & y^{(i)} = 1\\ 1 - g^{(i)} & y^{(i)} = 0\end{cases} \;=\; \prod_{i=1}^n \big(g^{(i)}\big)^{y^{(i)}}\big(1 - g^{(i)}\big)^{1-y^{(i)}}$$

(the exponent trick picks the right factor because one of $y$, $1-y$ is always 0). We want to **maximise** this. Since $\log$ is increasing, maximise its log instead:

$$\sum_{i=1}^n\Big[y^{(i)}\log g^{(i)} + (1 - y^{(i)})\log\big(1 - g^{(i)}\big)\Big]$$

Flip the sign to get a loss to **minimise**, the **negative log-likelihood (NLL)**, also called **log loss** or **cross-entropy**:

$$L_{nll}(g, a) = -\big(a\log g + (1-a)\log(1-g)\big)$$

Add ridge regularisation to get the **logistic regression objective**:

$$J_{lr}(\theta,\theta_0) = \frac1n\sum_{i=1}^n L_{nll}\big(\sigma(\theta^Tx^{(i)} + \theta_0), y^{(i)}\big) + \lambda\|\theta\|^2$$

**Why regularise here?** On linearly separable data with $\lambda = 0$, $J_{lr}$ keeps decreasing as $\|\theta\| \to \infty$: the sigmoid becomes a step, claiming total certainty about a sharp boundary even in a wide gap with no data. A small $\lambda > 0$ keeps $\theta$ finite and the model less over-confident, and makes the fit less sensitive to small changes in the training data.

### 4.4 Gradient (§4.4)

Using $\sigma'(z) = \sigma(z)(1-\sigma(z))$, the gradient simplifies beautifully:

$$\nabla_\theta J_{lr} = \frac1n\sum_{i=1}^n\big(g^{(i)} - y^{(i)}\big)x^{(i)} + 2\lambda\theta, \qquad \frac{\partial J_{lr}}{\partial\theta_0} = \frac1n\sum_{i=1}^n\big(g^{(i)} - y^{(i)}\big)$$

> **Mini-derivation for one example (ours, following the notes' study questions).** Let $z = \theta^Tx + \theta_0$, $g = \sigma(z)$. Then
> $\dfrac{\partial L_{nll}}{\partial g} = -\dfrac{y}{g} + \dfrac{1-y}{1-g}$, and $\dfrac{\partial g}{\partial z} = g(1-g)$.
> Chain rule: $\dfrac{\partial L_{nll}}{\partial z} = -y(1-g) + (1-y)g = g - y$. Since $\dfrac{\partial z}{\partial\theta} = x$, we get $\nabla_\theta L_{nll} = (g - y)\,x$.
> Intuition: the update is "prediction error × input", exactly like linear regression's gradient.

Gradient descent algorithm (LR-Gradient-Descent): repeat $\theta \leftarrow \theta - \eta\big[\tfrac1n\sum_i(\sigma(\theta^Tx^{(i)}+\theta_0) - y^{(i)})x^{(i)} + 2\lambda\theta\big]$ and $\theta_0 \leftarrow \theta_0 - \eta\,\tfrac1n\sum_i(\sigma(\cdot) - y^{(i)})$ until $J_{lr}$ stops changing. There is **no closed-form solution** for logistic regression, which is why we need GD/SGD. Logistic regression is also a one-layer neural network with a sigmoid activation.

### 4.5 Convexity (§4.4.1)

The NLL loss is **convex** in $(\theta, \theta_0)$, so GD with a sensible step size converges to the global minimum. Proof sketch: with $z$ affine in the parameters, it suffices that $f_1(z) = -\log\sigma(z)$ and $f_2(z) = -\log(1-\sigma(z))$ are convex in $z$. Their derivatives are $f_1'(z) = \sigma(z) - 1$ and $f_2'(z) = \sigma(z)$, both monotonically increasing, so both functions are convex; sums of convex functions, and convex functions of affine functions, are convex.

### 4.6 Multiple classes (§4.5)

Generalise with a $d\times K$ weight matrix and the **softmax** $g_k = e^{z_k}/\sum_j e^{z_j}$ (non-negative, sums to 1); loss $L_{nllm}(g,y) = -\sum_k y_k\log g_k$ with one-hot $y$. For $K = 2$ this reduces to $L_{nll}$. (Not needed for our binary default problem.)

### 4.7 Accuracy and the optimisation/evaluation mismatch (§4.6)

Accuracy $A(h;D) = 1 - \frac1n\sum_i L_{01}(g^{(i)}, y^{(i)})$ after thresholding. Note we **train** with NLL but often **evaluate** with a different metric: a deliberate compromise for computational convenience.

---

## 5. Encoding real-world features (§5.3)

**Discrete features** (a variable taking one of $k$ values):

- **Numeric** codes $1/k, 2/k, \dots, 1$: only if the values really are quantities.
- **Thermometer code**: for *ordered* categories without meaningful spacing; value $j$ becomes a length-$k$ vector with the first $j$ entries 1 (e.g. education level, risk band).
- **Factored code**: split a value into meaningful parts and encode each (car → maker + model; blood type → {A, B, AB, O} and {+, −}).
- **One-hot code**: when there is no order or structure.
- **Binary code** (compressing $k$ values into $\log k$ bits): **a bad idea**: the model would have to learn to decode it.

**Text**: bag-of-words, a binary vector with one entry per vocabulary word.

**Numeric features**: keep them numeric, except where there are natural **breakpoints** (e.g. under/over 18) or the relationship is non-monotonic (then bin and one-hot). Scale features, e.g. **standardise** $\phi(x) = (x - \bar x)/\sigma$ to mean 0, standard deviation 1 ("z-scores"), so no feature dominates just by its units. Polynomial features raise structural capacity: higher order tends to decrease structural error but increase estimation error.

---

## 6. Trees, bagging and random forests (§9.2)

### 6.1 Tree models (§9.2)

Partition the input space into regions and fit a very simple model (usually a constant) in each. Methods differ in the split types, the leaf predictors, how complexity is controlled, and the fitting algorithm. Trees are **easy for humans to interpret** (important where experts make the final call; example: a hospital risk tree using blood pressure, age, and tachycardia). Best when inputs are not very high-dimensional and features are individually meaningful (good for patient measurements, bad for raw images). We focus on **CART/ID3**: greedy, axis-aligned splits, constant leaves.

### 6.2 Regression trees (§9.2.1)

Regions $R_1..R_M$, each predicting the average $O_m$ of its training targets; region error $E_m = \sum_{i\in I_m}(y^{(i)} - O_m)^2$. Ideal objective $\lambda M + \sum_m E_m$ is NP-complete to optimise, so build **greedily**:

```
BUILDTREE(I, k):
  if |I| <= k: return LEAF(average of y in I)
  for each feature j and split value s:
      I+ = points with x_j >= s ;  I- = points with x_j < s
      E_js = SSE(I+) + SSE(I-)        # each around its own mean
  pick (j*, s*) with smallest E_js
  return NODE(j*, s*, BUILDTREE(I-, k), BUILDTREE(I+, k))
```

$k$ (max leaf size) is a hyperparameter. Each call checks $O(dn)$ candidate splits (only splits between adjacent data values matter).

**Pruning (§9.2.1.2).** Short-sighted stopping can miss splits that only pay off after a further split (e.g. XOR). Better: grow a big tree, then prune using **cost complexity**

$$C_\alpha(T) = \sum_{m=1}^{|T|} E_m(T) + \alpha|T|$$

where $|T|$ is the number of leaves. "Weakest-link" pruning removes, one at a time, the split whose removal increases error least, giving a sequence of trees; keep the one minimising $C_\alpha$. **Choose $\alpha$ by cross-validation.**

### 6.3 Classification trees (§9.2.2)

Leaf predicts the **majority class**. With $\hat P_{m,k}$ the fraction of class $k$ in region $m$, impurity measures:

- Misclassification error: $1 - \hat P_{m,O_m}$
- Gini index: $\sum_k \hat P_{m,k}(1 - \hat P_{m,k})$
- Entropy: $H = -\sum_k \hat P_{m,k}\log_2\hat P_{m,k}$ (with $0\log0 = 0$)

Choose the split minimising the **weighted average entropy** of the children $\frac{|I^-|}{N_m}H(I^-) + \frac{|I^+|}{N_m}H(I^+)$, equivalently maximising **information gain** $H(I_m) - [\cdot]$. Common practice: entropy for growing, misclassification error for pruning.

### 6.4 Bagging (§9.2.3)

Trees have high **estimation error** (small data changes → very different trees). **Bootstrap aggregation**:

1. Make $B$ datasets of size $n$ by sampling **with replacement** from $D$ (bootstrap samples).
2. Train a predictor $\hat f^b$ on each.
3. Regression: average, $\hat f_{bag}(x) = \frac1B\sum_b\hat f^b(x)$. Classification: each tree votes (one-hot); $\hat f_{bag}(x)$ is the vector of vote proportions and the prediction is the class with the most votes.

Bagging provably reduces estimation error, but simple interpretability is lost.

### 6.5 Random forests (§9.2.4)

Bagging plus **decorrelation**: for $b = 1..B$, draw a bootstrap sample and grow a tree where **at each split only $m$ randomly chosen features** (out of $d$) are considered. Vote to predict. Hyperparameters $B$, $m$, $n$. Often excellent out of the box.

### 6.6 Variants and trade-offs (§9.2.5)

Leaves can hold linear models; splits can use several features (non-axis-parallel); "soft" trees / mixtures of experts can be trained by gradient descent; **gradient-boosted trees (e.g. XGBoost)** combine trees with boosting. Strengths: interpretable, fast, naturally multi-class, flexible losses, feature-importance measures, often competitive. The notes recommend random forests or boosted trees as a strong **baseline**.

---

## How this applies to Prosit 2

- **Required logistic-regression MLE derivation.** §4.3–4.5 is essentially the derivation we must write up: Bernoulli likelihood $\prod_i g_i^{y_i}(1-g_i)^{1-y_i}$ → log → negate → NLL/log-loss → add $\lambda\|\theta\|^2$ → gradient $\frac1n\sum_i(g_i - y_i)x_i + 2\lambda\theta$ → convexity argument → no closed form, so solve with GD/SGD (or Newton-type solvers in sklearn). Use labels $\{0,1\}$ as the notes insist. Note sklearn's `C` is an inverse regularisation strength (roughly $1/\lambda$, up to scaling).
- **Cost-based thresholds.** §1.3's asymmetric loss and §4.3.1's decision-theory remark justify choosing a threshold from costs. With cost $c_{FN}$ for approving a defaulter and $c_{FP}$ for rejecting a good borrower, and *calibrated* probabilities $p$, approving when $p\,c_{FN} < (1-p)\,c_{FP}$ gives threshold $t^* = \frac{c_{FP}}{c_{FP} + c_{FN}}$. (This formula is our application, not in the notes.)
- **Calibration matters because of that formula.** The threshold rule assumes $p$ is a true probability; regularisation, class weights and tree ensembles all distort it, so calibrate on validation folds.
- **Cross-validation evaluates the pipeline, not the model (§2.7.2).** Our GroupKFold scores describe "logistic regression + this preprocessing + this $\lambda$" as a procedure. The final deployed model is refit on all training data; its own performance is estimated by the held-out temporal test set.
- **i.i.d. assumption (§1.2, §2.1).** Repeated customers break independence (→ GroupKFold by customer); changes over time break "identically distributed" (→ temporal split); **Kenya → Ghana** is a direct violation of the same-distribution assumption, so Kenyan CV scores are not a guarantee for Ghana. Say this explicitly in the shift section.
- **Bias/variance language.** Use "structural vs estimation error" to explain model choice: logistic regression may have more structural error; boosted trees more estimation error, especially with few defaults. Tune $\lambda$ / depth / learning rate by CV.
- **Ridge for unstable features.** Many mobile-money features are highly correlated (inflow, outflow, balance, counts). §2.6 explains why unregularised fits become unstable; use L2 and standardise first, and remember $\theta_0$ is not penalised.
- **Feature encoding (§5.3).** Thermometer coding for ordered categories (e.g. loan tenure bands), factored codes for compound categories, one-hot otherwise; never binary-code categories. Standardise numeric features for logistic regression. Bin variables with natural breakpoints (e.g. age bands) if a fairness or regulatory rule requires it.
- **Trees and ensembles (§9.2).** Cost-complexity $\alpha$, depth and leaf size are tuned by (Group)CV. Bagging/RF reduce variance, valuable with only ~1.83% defaults; boosted trees are the notes' recommended strong baseline. Interpretability is lost with ensembles, so reason codes for the deployed scorer are easier with the logistic model.
- **Loan-amount regression.** Ridge regression closed form $\theta = (\tilde X^T\tilde X + n\lambda I)^{-1}\tilde X^T\tilde Y$ is a quick, stable baseline; compare against a regression forest / boosted trees under the same validation scheme.
