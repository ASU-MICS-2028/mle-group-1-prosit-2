# Derivations for Prosit 2 (credit scoring)

These are the derivations the report has to contain, worked step by step so each of us can redo them on a whiteboard and defend them in the oral Q&A without notes. Every algebra step comes with a plain-English line saying what just happened.

**Book references.**
- **ISLP** = James, Witten, Hastie, Tibshirani & Taylor, *An Introduction to Statistical Learning, with Applications in Python* (2023). This is the Python edition of ISLR. Section and equation numbers are the same as in ISLR 2nd ed. for the chapters we use. Page numbers are the printed book pages, and a few are ±1.
- **HOMLP** = Géron, *Hands-On Machine Learning with Scikit-Learn and PyTorch* (2025). Chapter numbers come from the book's official notebook list. We do not have the full HOMLP PDF; our file is only the online bonus Appendix E on state-space models. So HOMLP citations give chapter and topic only, with no page numbers.

**Notation used throughout.**

| Symbol | Meaning |
|---|---|
| $n$ | number of loans (rows) |
| $p$ | number of features |
| $x_i$ | feature vector of loan $i$, with a leading 1 for the intercept, so $x_i\in\mathbb R^{p+1}$ |
| $X$ | the $n\times(p+1)$ design matrix; row $i$ is $x_i^T$ |
| $y$ | the target vector: log loan amount (Task 1), or default 0/1 (Task 2) |
| $\beta$ | the coefficient vector, $(p+1)\times 1$ |
| $\lVert v\rVert^2$ | $v^Tv$, the sum of squared entries |

Two matrix-calculus rules carry nearly all of the algebra below. Learn them by heart:

1. $\dfrac{\partial}{\partial\beta}(a^T\beta) = a$ (the derivative of a linear function is its coefficient vector).
2. $\dfrac{\partial}{\partial\beta}(\beta^T A\beta) = (A+A^T)\beta = 2A\beta$ when $A$ is symmetric (this is the matrix version of $\frac{d}{db}ab^2 = 2ab$).

---

## a. Linear regression (Task 1: loan amount)

*Sources: ISLP §3.1.1 (least squares for one predictor, eq. 3.3–3.4, pp. 71–72); §3.2.1 (multiple regression RSS, eq. 3.22, pp. 81–82); §6.2.1–6.2.2 (ridge eq. 6.5 p. 240, lasso eq. 6.7 p. 244, and the simple special case eq. 6.14–6.15). ISLP §4.3.2 (p. 141) mentions that least squares is a special case of maximum likelihood but does not prove it. We prove it below. HOMLP Ch 4 "Training Linear Models" covers the normal equation, gradient descent and ridge/lasso/elastic net.*

### a.1 The model

$$y_i = x_i^T\beta + \varepsilon_i,\qquad \varepsilon_i \overset{\text{iid}}{\sim} \mathcal N(0,\sigma^2)$$

The target equals a weighted sum of the features plus random noise. We assume the noise is Gaussian, has mean zero, has the same spread $\sigma^2$ for every loan, and is independent across loans. In matrix form this is $y = X\beta + \varepsilon$.

**Prosit link.** In Task 1, $y_i = \log(\text{amount}_i)$ (or $\log(1+\text{amount}_i)$). Loan amounts are right-skewed and their spread grows with their size. Taking logs makes the "same spread everywhere" (homoscedastic) assumption more believable. ISLP §3.3.3 (p. 100ff) shows heteroscedasticity in a residual plot and fixes it with a log transform. That plot is exactly the residual plot we must show.

### a.2 Likelihood and log-likelihood

Because $\varepsilon_i = y_i - x_i^T\beta$ is normal, each $y_i$ has density

$$f(y_i\mid x_i;\beta,\sigma^2) = \frac{1}{\sqrt{2\pi\sigma^2}}\exp\!\left(-\frac{(y_i-x_i^T\beta)^2}{2\sigma^2}\right).$$

The loans are independent, so the probability of the whole dataset (the **likelihood**) is the product of these densities:

$$L(\beta,\sigma^2) = \prod_{i=1}^n \frac{1}{\sqrt{2\pi\sigma^2}}\exp\!\left(-\frac{(y_i-x_i^T\beta)^2}{2\sigma^2}\right).$$

Products are awkward, so we take the log. The log is increasing, so whatever maximises $L$ also maximises $\log L$. The log turns the product into a sum, and $\log\exp(u)=u$:

$$\ell(\beta,\sigma^2)=\log L = -\frac n2\log(2\pi\sigma^2) \;-\; \frac{1}{2\sigma^2}\sum_{i=1}^n (y_i-x_i^T\beta)^2 .$$

The first term comes from the $n$ copies of $\log\frac{1}{\sqrt{2\pi\sigma^2}} = -\tfrac12\log(2\pi\sigma^2)$. The second term is the sum of the exponents.

### a.3 MLE = least squares

Call the sum in the second term the residual sum of squares, $\text{RSS}(\beta)=\sum_i (y_i-x_i^T\beta)^2$ (ISLP eq. 3.22). Then

$$\ell(\beta,\sigma^2) = -\frac n2\log(2\pi\sigma^2) - \frac{\text{RSS}(\beta)}{2\sigma^2}.$$

Look at $\ell$ as a function of $\beta$ only:
- The first term does not involve $\beta$.
- The second term is $-\text{RSS}(\beta)$ times a positive constant $1/(2\sigma^2)$.

So **maximising the likelihood over $\beta$ is exactly the same as minimising RSS.** Under Gaussian noise, the maximum-likelihood estimate *is* the least-squares estimate. This is why "least squares" is not an arbitrary choice: it is the right estimator when the noise is Gaussian.

*Bonus (for $\sigma^2$).* Set $\partial\ell/\partial\sigma^2 = -\frac{n}{2\sigma^2}+\frac{\text{RSS}}{2\sigma^4}=0$. This gives $\hat\sigma^2_{\text{MLE}} = \text{RSS}/n$. The unbiased version divides by $n-p-1$ instead; that is ISLP's RSE², eq. 3.25.

### a.4 The normal equations

Write RSS in matrix form and expand it, the same way you expand $(a-b)^2$:

$$\text{RSS}(\beta) = (y-X\beta)^T(y-X\beta) = y^Ty - y^TX\beta - \beta^TX^Ty + \beta^TX^TX\beta .$$

The two middle terms are both scalars (single numbers). A scalar equals its own transpose, so $y^TX\beta = (y^TX\beta)^T = \beta^TX^Ty$. Combining them gives

$$\text{RSS}(\beta) = y^Ty - 2\beta^TX^Ty + \beta^TX^TX\beta .$$

Differentiate with respect to $\beta$:
- $y^Ty$ has no $\beta$, so its derivative is 0.
- Rule 1 with $a = X^Ty$ gives $-2X^Ty$.
- Rule 2 with the symmetric matrix $A = X^TX$ gives $2X^TX\beta$.

$$\frac{\partial\,\text{RSS}}{\partial\beta} = -2X^Ty + 2X^TX\beta .$$

At the minimum the slope is zero in every direction. Set the derivative to zero and divide by 2:

$$\boxed{X^TX\hat\beta = X^Ty}\qquad\text{(the normal equations)}$$

If $X^TX$ is invertible, multiply both sides on the left by its inverse:

$$\boxed{\hat\beta = (X^TX)^{-1}X^Ty}$$

**Is it a minimum and not a maximum?** The second derivative (Hessian) is $2X^TX$. For any vector $v$, $v^TX^TXv = \lVert Xv\rVert^2 \ge 0$, so the Hessian is positive semi-definite. That makes RSS a convex "bowl", and any point where the slope is zero is a global minimum.

**Why the name "normal".** Rewrite the equations as $X^T(y - X\hat\beta) = 0$. The residual vector $e = y - X\hat\beta$ is orthogonal ("normal") to every column of $X$. Two useful consequences follow:
- Because $X$ has a column of ones, the residuals sum to zero.
- Residuals have zero correlation with every feature *in the training set*. A pattern in a residual-vs-fitted plot therefore means the model is mis-specified (for example, a missing non-linearity), not just noisy.

**Sanity check with one predictor (ISLP eq. 3.4).** With $y_i=\beta_0+\beta_1x_i+\varepsilon_i$, the two normal equations are:
- $\sum_i (y_i-\beta_0-\beta_1x_i)=0$, which gives $\hat\beta_0=\bar y-\hat\beta_1\bar x$.
- $\sum_i x_i(y_i-\beta_0-\beta_1x_i)=0$. Substituting $\hat\beta_0$ gives $\hat\beta_1=\dfrac{\sum_i(x_i-\bar x)(y_i-\bar y)}{\sum_i(x_i-\bar x)^2}$.

This is the textbook simple-regression formula.

### a.5 When $X^TX$ is not invertible

$X^TX$ is invertible exactly when the columns of $X$ are **linearly independent** (full column rank $p+1$). It fails, or nearly fails, in these cases:

| Cause | Prosit example | What happens |
|---|---|---|
| Perfect collinearity | One-hot encoding *all* levels of `region` **and** keeping an intercept (the "dummy-variable trap"): the dummies sum to the intercept column | Infinitely many $\hat\beta$ fit equally well, so the coefficients are not identifiable |
| More features than rows, $p+1>n$ | A rare category level with only a few loans, or a fold that is too small after GroupKFold | Same as above |
| Constant or duplicated columns | A feature that is constant inside a training fold; the same amount stored in two currencies | Same as above |
| Near-collinearity | Income and total transaction volume strongly correlated | Inverse exists but is numerically huge, so the coefficients have enormous variance and can flip sign (ISLP §3.3.3, "Collinearity") |

**Fixes.**
- Drop one dummy per categorical (`OneHotEncoder(drop="first")`) or drop duplicate columns.
- Use the pseudo-inverse or least-squares solver (`np.linalg.lstsq`, which is what scikit-learn's `LinearRegression` uses). It returns the minimum-norm solution.
- **Use ridge**, which is always invertible (next section).

### a.6 Ridge regression closed form

Ridge minimises RSS plus a penalty on the size of the coefficients (ISLP eq. 6.5):

$$J(\beta) = \lVert y-X\beta\rVert^2 + \lambda\lVert\beta\rVert^2,\qquad \lambda\ge0 .$$

The intercept is normally *not* penalised. In practice we centre $y$ and standardise the features, then drop the intercept from $\beta$. So take $X$ here as the standardised features without a ones column.

Differentiate exactly as in a.4. The new term $\lambda\beta^T\beta$ has derivative $2\lambda\beta$ (Rule 2 with $A = \lambda I$):

$$\frac{\partial J}{\partial\beta} = -2X^Ty + 2X^TX\beta + 2\lambda\beta = 0
\;\Longrightarrow\; (X^TX+\lambda I)\beta = X^Ty$$

$$\boxed{\hat\beta_{\text{ridge}} = (X^TX+\lambda I)^{-1}X^Ty}$$

**Why ridge is always invertible for $\lambda>0$.** For any $v\neq0$:

$$v^T(X^TX+\lambda I)v=\lVert Xv\rVert^2+\lambda\lVert v\rVert^2>0 .$$

So the matrix is positive definite and has no zero eigenvalue. In plain words, ridge adds $\lambda$ to every eigenvalue of $X^TX$, which lifts the flat directions caused by collinearity. This is the formal answer to "what do you do when $X^TX$ is singular?"

**Intuition with orthonormal features ($X^TX=I$).**
- Ridge gives $\hat\beta_j = \hat\beta^{\text{OLS}}_j/(1+\lambda)$: every coefficient shrinks by the same factor and none becomes exactly zero.
- Lasso minimises $\lVert y-X\beta\rVert^2+\lambda\sum_j|\beta_j|$. Per coordinate this becomes $(\beta_j-b_j)^2+\lambda|\beta_j|$ with $b_j=\hat\beta_j^{\text{OLS}}$, and the solution is the **soft-threshold** $\hat\beta_j=\operatorname{sign}(b_j)\,(|b_j|-\lambda/2)_+$. Coefficients smaller than $\lambda/2$ become exactly 0, which is why the lasso selects variables. This is ISLP eq. 6.14–6.15, where the special case uses $X=I$.
- The lasso has **no general closed form** because $|\beta_j|$ has no derivative at 0. It is solved by coordinate descent.

**Practical notes for Task 1.**
1. Standardise features before ridge or lasso; otherwise the penalty depends on the units. ISLP §6.2.1 makes this point.
2. Choose $\lambda$ by cross-validation (ISLP §6.2.3), using *our* GroupKFold or temporal folds.
3. Ridge is the MAP estimate under a Gaussian prior $\beta_j\sim\mathcal N(0,\sigma^2/\lambda)$. Lasso is the MAP estimate under a Laplace prior.
4. **Back-transforming a log target.** If $\log y$ is Gaussian with mean $\mu$ and variance $\sigma^2$, then $e^{\hat\mu}$ estimates the **median** amount, not the mean. The mean is $e^{\mu+\sigma^2/2}$. Report RMSE/MAE on the original scale (cedis) as well as on the log scale, and say which one you used.

---

## b. Logistic regression (Task 2: probability of default)

*Sources: ISLP §4.3.1–4.3.4 (logistic function eq. 4.2, odds eq. 4.3, logit eq. 4.4, likelihood eq. 4.5; pp. 139–143); §9.5 (logistic loss vs hinge loss). HOMLP Ch 4 "Training Linear Models" (logistic regression, its cost function and gradient, softmax); HOMLP Ch 3 "Classification" (precision/recall, PR curve, thresholds). ISLP stops at the likelihood ("details beyond the scope of this book"). Everything from b.4 onward is our own work.*

### b.1 From log-odds to the sigmoid

Let $p(x)=P(Y=1\mid x)$ be the probability that a loan defaults. A linear function $x^T\beta$ can take any value in $(-\infty,\infty)$, but a probability must lie in $(0,1)$. Logistic regression connects the two by modelling the **log-odds** (logit) as linear:

$$\log\frac{p(x)}{1-p(x)} = x^T\beta =: z .$$

Odds $p/(1-p)$ range over $(0,\infty)$, and log-odds over $(-\infty,\infty)$, so the ranges now match. Solve for $p$:

$$\frac{p}{1-p}=e^z \;\Rightarrow\; p = e^z(1-p) \;\Rightarrow\; p(1+e^z)=e^z \;\Rightarrow\; \boxed{p=\frac{e^z}{1+e^z}=\frac{1}{1+e^{-z}}=\sigma(z)}$$

The last form comes from dividing the top and bottom by $e^z$. $\sigma$ is the **sigmoid** (logistic) function (ISLP eq. 4.2).

**Interpreting coefficients (Prosit interpretation step).** Increasing feature $j$ by one unit, with everything else fixed, adds $\beta_j$ to the log-odds. Equivalently, it **multiplies the odds of default by $e^{\beta_j}$** (the odds ratio). It does *not* change $p$ by a fixed amount, because the curve is S-shaped (ISLP p. 140). With standardised features, "one unit" means one standard deviation.

**A derivative used later.** We need the derivative of the sigmoid:

$$\sigma'(z)=\frac{d}{dz}(1+e^{-z})^{-1} = \frac{e^{-z}}{(1+e^{-z})^2} = \underbrace{\frac{1}{1+e^{-z}}}_{\sigma(z)}\cdot\underbrace{\frac{e^{-z}}{1+e^{-z}}}_{1-\sigma(z)} = \sigma(z)\,(1-\sigma(z)).$$

### b.2 Bernoulli likelihood

Each label $y_i\in\{0,1\}$ is a coin flip with probability $p_i=\sigma(x_i^T\beta)$. One formula covers both outcomes:

$$P(y_i\mid x_i)=p_i^{\,y_i}(1-p_i)^{1-y_i}$$

If $y_i=1$ this reads $p_i$; if $y_i=0$ it reads $1-p_i$.

The loans are independent, so the likelihood is the product. This is ISLP eq. 4.5 written in one line:

$$L(\beta)=\prod_{i=1}^n p_i^{\,y_i}(1-p_i)^{1-y_i}.$$

### b.3 Negative log-likelihood = cross-entropy (log-loss)

Take logs, which turns the product into a sum and brings the powers down in front:

$$\ell(\beta)=\sum_{i=1}^n\Big[y_i\log p_i+(1-y_i)\log(1-p_i)\Big].$$

Maximising $\ell$ is the same as minimising its negative, the **negative log-likelihood**:

$$\boxed{\text{NLL}(\beta)= -\sum_{i=1}^n\Big[y_i\log p_i+(1-y_i)\log(1-p_i)\Big]}$$

Divided by $n$, this is the **binary cross-entropy / log-loss**, the metric scikit-learn calls `log_loss`.

**Plain meaning.** Each loan contributes $-\log(\text{probability the model gave to what actually happened})$.
- A confident correct prediction costs almost nothing: $-\log 0.99\approx0.01$.
- A confident wrong prediction is punished hard: $-\log 0.01\approx4.6$.

### b.4 The gradient $X^T(p-y)$

First simplify each term using $z_i=x_i^T\beta$ and $p_i=e^{z_i}/(1+e^{z_i})$:

$$\log p_i = z_i-\log(1+e^{z_i}),\qquad \log(1-p_i)=\log\frac{1}{1+e^{z_i}}=-\log(1+e^{z_i}).$$

Substitute these into $\ell$. The $-\log(1+e^{z_i})$ parts appear with total weight $y_i+(1-y_i)=1$:

$$\ell(\beta)=\sum_i\Big[y_iz_i-\log(1+e^{z_i})\Big].$$

Differentiate with respect to $\beta$, using the chain rule with $\partial z_i/\partial\beta=x_i$:

$$\frac{\partial\ell}{\partial\beta}=\sum_i\Big[y_ix_i-\frac{e^{z_i}}{1+e^{z_i}}x_i\Big]=\sum_i (y_i-p_i)\,x_i = X^T(y-p).$$

Flip the sign for the NLL:

$$\boxed{\nabla_\beta\,\text{NLL}=X^T(p-y)}$$

**Plain meaning.** Each loan pushes $\beta$ in the direction of its own features, weighted by its prediction error $p_i-y_i$. The formula has the same shape as linear regression's gradient, $X^T(X\beta-y)$; only the prediction changes from $X\beta$ to $\sigma(X\beta)$.

**A free calibration fact.** At the optimum, $X^T(y-\hat p)=0$. The first column of $X$ is all ones, so

$$\sum_i \hat p_i=\sum_i y_i .$$

In words, an *unweighted* logistic regression with an intercept always predicts, on average over the training set, exactly the observed default rate (here 1.83%). This is called "calibration-in-the-large", and b.7 shows how class weights break it.

### b.5 Why there is no closed form, and how it is solved

Setting the gradient to zero gives $X^T\big(y-\sigma(X\beta)\big)=0$. Unlike the normal equations, $\beta$ sits *inside* the non-linear sigmoid, so no algebra can isolate it. We solve it numerically, which is safe because the problem is convex.

**Convexity (the Hessian).** Differentiate the gradient $\sum_i(p_i-y_i)x_i$ again. Only $p_i$ depends on $\beta$, and $\partial p_i/\partial\beta=\sigma'(z_i)x_i=p_i(1-p_i)x_i$ (from b.1). So

$$\nabla^2\text{NLL}=\sum_i p_i(1-p_i)\,x_ix_i^T = X^TWX,\qquad W=\operatorname{diag}\big(p_i(1-p_i)\big).$$

Every $p_i(1-p_i)>0$, so $v^TX^TWXv=\sum_i p_i(1-p_i)(x_i^Tv)^2\ge0$. The NLL is therefore convex: there are no bad local minima, and any optimiser that converges finds the global minimum.

**Option 1: gradient descent** (HOMLP Ch 4). Repeat

$$\beta\leftarrow\beta-\eta\,\tfrac1n X^T(p-y)$$

with learning rate $\eta$. It is simple but can be slow.

**Option 2: Newton–Raphson, also called IRLS.** Use the curvature as well as the slope:

$$\beta^{\text{new}}=\beta-(X^TWX)^{-1}X^T(p-y).$$

Algebra shows this is the same as a *weighted least-squares* fit:

$$\beta^{\text{new}}=(X^TWX)^{-1}X^TW\,\tilde z,\qquad \tilde z=X\beta+W^{-1}(y-p).$$

*Check:* $(X^TWX)^{-1}X^TW X\beta=\beta$, and $(X^TWX)^{-1}X^TWW^{-1}(y-p)=(X^TWX)^{-1}X^T(y-p)$. Adding these gives the Newton step. ✓

So each iteration solves a normal-equations problem with weights $W$ and a "working response" $\tilde z$, and the weights are recomputed every round. That is why it is called *iteratively re-weighted least squares*. statsmodels uses IRLS. scikit-learn's default solver `lbfgs` is a quasi-Newton method that approximates the Hessian.

**Separation warning (relevant with 1.83% positives).** Suppose some feature, or a rare one-hot category, perfectly separates defaulters from non-defaulters in the training data. Then the likelihood keeps increasing as $|\beta|\to\infty$, and the MLE does not exist. Regularisation fixes this. scikit-learn's `LogisticRegression` uses L2 by default and minimises

$$\tfrac12\lVert\beta\rVert^2 + C\sum_i \text{loss}_i ,$$

so $C$ behaves like $1/\lambda$: a **smaller $C$ means stronger regularisation**.

### b.6 Class weights: what they change in the loss

With weights $w_1$ for defaulters and $w_0$ for non-defaulters, the loss becomes

$$\text{NLL}_w(\beta)=-\sum_i\Big[w_1\,y_i\log p_i+w_0\,(1-y_i)\log(1-p_i)\Big],$$

and the gradient becomes $X^T\,\Omega\,(p-y)$ with $\Omega=\operatorname{diag}(w_{y_i})$.

scikit-learn's `class_weight="balanced"` sets $w_c=\dfrac{n}{2\,n_c}$. With default rate $\pi=0.0183$:

- $w_1=\dfrac{1}{2\pi}=\dfrac{1}{0.0366}\approx27.3$
- $w_0=\dfrac{1}{2(1-\pi)}=\dfrac{1}{1.9634}\approx0.509$
- the ratio is $\dfrac{w_1}{w_0}=\dfrac{1-\pi}{\pi}=\dfrac{0.9817}{0.0183}\approx53.6$

Plain meaning: each defaulter counts as about 54 non-defaulters. This is the same as duplicating every defaulter about 54 times. It stops the model from "winning" by predicting 0 for everyone.

### b.7 Why class weights distort calibrated probabilities

Take one feature value $x$ whose true default probability is $q$. What probability $p$ minimises the *expected* weighted loss at that point?

$$g(p)=-\Big[w_1\,q\log p+w_0(1-q)\log(1-p)\Big]$$

Set $g'(p)=-\dfrac{w_1q}{p}+\dfrac{w_0(1-q)}{1-p}=0$, then cross-multiply:

$$w_1q(1-p)=w_0(1-q)p \;\Longrightarrow\; \frac{p}{1-p}=\frac{w_1}{w_0}\cdot\frac{q}{1-q}.$$

$$\boxed{\text{odds}_{\text{weighted}}=\frac{w_1}{w_0}\times\text{odds}_{\text{true}}\qquad\Longleftrightarrow\qquad \operatorname{logit}(p)=\operatorname{logit}(q)+\log\frac{w_1}{w_0}}$$

Without weights ($w_1=w_0$), the best prediction is $p=q$: the log-loss rewards honest probabilities. With weights, the best prediction is **inflated**: every log-odds is pushed up by $\log(w_1/w_0)=\log 53.6\approx3.98$.

*Worked example.* A weighted model outputs $p=0.5$ (odds 1). The true odds are $1/53.6\approx0.0187$, so $q=0.0187/1.0187\approx0.018$. A "50% risk" from a balanced model is really about the base rate. Using 0.5 as a cut-off, or putting such numbers in front of a credit officer as probabilities, would be badly wrong. The b.4 identity also changes: now $\sum_i w_{y_i}(y_i-\hat p_i)=0$, so the *weighted* average of $\hat p$ matches the weighted default rate (about 50%), not 1.83%.

**Consequences for Task 2.**
- **Ranking is (nearly) unaffected.** For a correctly specified logistic model the shift is only in the intercept, and adding a constant to every log-odds does not change the order of borrowers. So ROC-AUC and PR-AUC barely move. In practice, regularisation and mis-specification mean the slopes change a little too.
- **Probabilities and thresholds are affected.** Brier score, log-loss, reliability curves, and any threshold taken from a cost matrix all need *calibrated* probabilities.
- **Fixes:**
  1. Analytic correction: $\operatorname{logit}(q)=\operatorname{logit}(p)-\log(w_1/w_0)$.
  2. Recalibrate on held-out data with Platt scaling (sigmoid) or isotonic regression (`CalibratedClassifierCV`, fitted inside our CV, never on the test fold).
  3. Train without weights and handle the imbalance through the threshold (b.8).
- Report a reliability diagram and the Brier score both before and after calibration.

### b.8 (Bonus) Threshold from a cost matrix

This one is short and is asked about constantly. Let:
- $C_{FN}$ = cost of approving a borrower who then defaults (lost principal minus any recovery).
- $C_{FP}$ = cost of rejecting a borrower who would have repaid (lost interest/fee margin, plus customer churn).

Correct decisions cost 0. For a borrower with calibrated default probability $p$:
- Expected cost if we **approve** is $p\,C_{FN}$.
- Expected cost if we **reject** is $(1-p)\,C_{FP}$.

Reject when approving is costlier:

$$p\,C_{FN}>(1-p)\,C_{FP}\iff p\,(C_{FN}+C_{FP})>C_{FP}\iff \boxed{p>t^*=\frac{C_{FP}}{C_{FP}+C_{FN}}}$$

*Example.* If a default loses 10× what a wrongly rejected good customer would have earned, $t^*=1/11\approx0.091$.

This formula only works if $p$ is a true probability, which is the practical reason b.7 matters. If you use an uncalibrated or weighted model, choose the threshold empirically by minimising total cost on validation folds. ISLP §4.4.2 (pp. 152–154, Default data, ROC curve) shows how changing the threshold trades false positives against false negatives. HOMLP Ch 3 covers precision/recall trade-offs and choosing a threshold.

---

## c. Gradient boosting (Task 1 and Task 2; LightGBM/XGBoost)

*Sources: ISLP §8.2.3, Algorithm 8.2 "Boosting for Regression Trees" (p. 349, eq. 8.10–8.12). ISLP covers only the squared-loss/residual version and says the classification details are omitted. HOMLP Ch 6 "Ensemble Learning and Random Forests" covers gradient boosting, learning rate/shrinkage, early stopping and histogram-based boosting. The general "fit to negative gradients" form below is Friedman (2001), *Greedy function approximation: a gradient boosting machine*. The second-order leaf formula is Chen & Guestrin (2016), *XGBoost*.*

### c.1 The additive model

Boosting builds the prediction as a sum of many small trees, added one at a time:

$$F_M(x)=F_0(x)+\nu\sum_{m=1}^M h_m(x)$$

- $F_0$ is a constant starting guess.
- Each $h_m$ is a shallow regression tree (a few splits).
- $0<\nu\le1$ is the **learning rate** (shrinkage); ISLP calls it $\lambda$.

The goal is to minimise the training loss $\sum_i L\big(y_i,F(x_i)\big)$. Trees are not differentiable in their structure, so instead of moving parameters downhill we move the *function's values* downhill.

### c.2 Fitting to negative gradients (pseudo-residuals)

Think of the current predictions $F_{m-1}(x_1),\dots,F_{m-1}(x_n)$ as $n$ numbers we are free to change. The direction that decreases the loss fastest is the **negative gradient** with respect to each prediction:

$$r_{im}=-\left[\frac{\partial L(y_i,F)}{\partial F}\right]_{F=F_{m-1}(x_i)}\qquad\text{(pseudo-residual of loan }i\text{)}$$

We cannot just add $r_{im}$ directly, because that would memorise the training set and could not be applied to new loans. So each round:

1. Compute the pseudo-residuals $r_{im}$ for all training loans.
2. Fit a small regression tree $h_m$ to the pairs $(x_i,r_{im})$ using squared error. The tree *generalises* the gradient to any $x$, including unseen loans.
3. Optionally reset each leaf's value $\gamma_{jm}$ to the best constant step for that leaf: $\gamma_{jm}=\arg\min_\gamma\sum_{x_i\in R_{jm}}L\big(y_i,F_{m-1}(x_i)+\gamma\big)$.
4. Update $F_m(x)=F_{m-1}(x)+\nu\,h_m(x)$.

This is gradient descent in "function space": each tree is one small downhill step.

### c.3 Squared loss: pseudo-residuals are ordinary residuals (Task 1)

Take $L(y,F)=\tfrac12(y-F)^2$. The ½ is only there so the 2 cancels. Then

$$-\frac{\partial L}{\partial F}=-\tfrac12\cdot2(y-F)\cdot(-1)=y-F .$$

So the pseudo-residual is just the **ordinary residual** $y_i-F_{m-1}(x_i)$. Each new tree is fitted to what the current model still gets wrong. This is exactly ISLP Algorithm 8.2: set $r_i=y_i$, fit a tree to $r$, then update $\hat f\leftarrow\hat f+\lambda\hat f_b$ and $r_i\leftarrow r_i-\lambda\hat f_b(x_i)$.
- ISLP starts at $\hat f=0$. Friedman starts at the constant that minimises the loss, which for squared loss is $F_0=\bar y$.
- Each leaf's best constant is the mean residual in that leaf.

For Task 1, $y$ is log-amount, so these are residuals on the log scale.

### c.4 Log-loss: classification (Task 2)

For classification the model's output $F$ is a **log-odds**, and $p=\sigma(F)$. Using the b.4 simplification with $z=F$, the per-loan log-loss is

$$L(y,F)=-\big[y\log p+(1-y)\log(1-p)\big]=\log(1+e^{F})-yF .$$

Differentiate with respect to $F$:

$$\frac{\partial L}{\partial F}=\frac{e^F}{1+e^F}-y=p-y\quad\Longrightarrow\quad r_{im}=y_i-p_i .$$

The pseudo-residual is "actual 0/1 minus current predicted probability". It is the same quantity that drove the logistic-regression gradient in b.4.

- **Starting value.** $F_0$ is the constant log-odds that minimises the loss, which is the logit of the base rate: $F_0=\log\frac{\bar y}{1-\bar y}=\log\frac{0.0183}{0.9817}\approx-3.98$.
- **Leaf values (one Newton step).** The second derivative is $\partial^2L/\partial F^2=p(1-p)$, the same $W$ as in IRLS. One Newton step for a leaf gives

$$\gamma_{jm}=\frac{\sum_{i\in R_{jm}}(y_i-p_i)}{\sum_{i\in R_{jm}}p_i(1-p_i)} .$$

- **XGBoost and LightGBM** generalise this. Write $g_i=\partial L/\partial F$ and $h_i=\partial^2L/\partial F^2$, and add a penalty $\tfrac12\lambda w^2$ on each leaf weight $w$. A second-order Taylor expansion of the loss for a leaf is $Gw+\tfrac12(H+\lambda)w^2$, where $G=\sum g_i$ and $H=\sum h_i$ over the leaf's loans. Setting its derivative to 0:

$$w^*=-\frac{G}{H+\lambda},\qquad \text{loss reduction from that leaf}=\tfrac12\frac{G^2}{H+\lambda}.$$

  The **split gain** they maximise is

$$\tfrac12\left[\frac{G_L^2}{H_L+\lambda}+\frac{G_R^2}{H_R+\lambda}-\frac{(G_L+G_R)^2}{H_L+H_R+\lambda}\right]-\gamma ,$$

  where $\gamma$ is the minimum gain needed to make a split.

- **Class weights.** `scale_pos_weight` (XGBoost), or `class_weight`/`is_unbalance` (LightGBM), multiplies $g_i$ and $h_i$ for positives. The result is the same probability inflation as in b.7, so recalibrate.

### c.5 Learning rate (shrinkage) and the other knobs

- **Learning rate $\nu$.** Each tree's contribution is shrunk. A smaller $\nu$ needs more trees $M$ but usually generalises better: the model "learns slowly" and no single tree, possibly fitted to noise, dominates (ISLP p. 349). Typical values are 0.01–0.1.
- **Number of trees $M$.** Unlike a random forest, boosting *can* overfit if $M$ is too large. Pick $M$ by **early stopping** on a validation fold (HOMLP Ch 6), using our temporal or group split, not a random one.
- **Tree size.** ISLP's $d$ is the number of splits per tree; LightGBM uses `num_leaves`/`max_depth`. With $d=1$ (stumps) the model is additive with no interactions. Larger $d$ allows interactions up to order $d$.
- **Subsampling.** Fitting each tree on a random fraction of rows (and/or columns) is "stochastic gradient boosting". It adds regularisation and speed.
- **Why it beats a single tree.** Boosting mainly reduces **bias** by fitting many weak learners in sequence. Random forests mainly reduce **variance** by averaging many deep, decorrelated trees fitted in parallel.

---

## d. Decision trees: split criteria and cost-complexity pruning

*Sources: ISLP §8.1.1 (regression trees: RSS over boxes eq. 8.1 p. 333; recursive binary splitting; Algorithm 8.1; cost complexity eq. 8.4, pp. 335–336); §8.1.2 (classification error eq. 8.5, Gini eq. 8.6, entropy eq. 8.7, pp. 337–338); §8.2.2 (variable importance, mean decrease in Gini/RSS, p. 345). HOMLP Ch 5 "Decision Trees" covers CART, Gini vs entropy, regularisation hyperparameters and instability. Ch 5 is not in the brief's citation list but is the natural reference for this section.*

### d.1 How a tree grows

A tree splits the feature space into boxes $R_1,\dots,R_J$ and predicts a constant in each box:
- the **mean** $y$ for regression;
- the **class proportion** (or the majority class) for classification.

Finding the globally best set of boxes is computationally infeasible, so CART uses **greedy recursive binary splitting**. At each node it tries every feature $j$ and every cut point $s$, and picks the split $\{x_j<s\}$ / $\{x_j\ge s\}$ that reduces impurity the most. It then repeats inside each child. "Greedy" means each split is the best right now, with no look-ahead.

The **impurity decrease** of a split of node $P$ (with $n_P$ loans) into children $L$ and $R$ is

$$\Delta I = I(P)-\frac{n_L}{n_P}I(L)-\frac{n_R}{n_P}I(R).$$

That is, the parent's impurity minus the size-weighted average impurity of the children.

### d.2 Regression: variance reduction (Task 1)

Use $I(\text{node})=\frac1{n_{\text{node}}}\sum_{i\in\text{node}}(y_i-\bar y_{\text{node}})^2$, the within-node variance (MSE around the node mean). Then

$$n_P\,\Delta I=\text{RSS}(P)-\big[\text{RSS}(L)+\text{RSS}(R)\big].$$

So "maximise variance reduction" and ISLP's "choose $j,s$ to minimise $\sum_{i\in R_1}(y_i-\hat y_{R_1})^2+\sum_{i\in R_2}(y_i-\hat y_{R_2})^2$" (eq. 8.1–8.3) are **the same thing**: the parent's RSS is fixed, so minimising the children's RSS maximises the drop. Each leaf predicts its mean because the mean is the constant that minimises squared error.

### d.3 Classification: Gini and entropy (Task 2)

Let $\hat p_{k}$ be the proportion of class $k$ in the node.

| Criterion | Formula | Two classes, $\hat p$ = share of defaulters | Value for a pure node |
|---|---|---|---|
| Misclassification error (ISLP 8.5) | $E=1-\max_k\hat p_k$ | $\min(\hat p,1-\hat p)$ | 0 |
| **Gini** (ISLP 8.6) | $G=\sum_k\hat p_k(1-\hat p_k)=1-\sum_k\hat p_k^2$ | $2\hat p(1-\hat p)$ | 0 |
| **Entropy** (ISLP 8.7) | $D=-\sum_k\hat p_k\log\hat p_k$ | $-\hat p\log\hat p-(1-\hat p)\log(1-\hat p)$ | 0 |

All three are 0 for a pure node and largest at a 50/50 node.

**Plain meanings.**
- Gini is the probability that two loans drawn at random from the node (with replacement) have different labels.
- Entropy is the average "surprise", in nats or bits, of a label drawn from the node.
- Gini and entropy behave very similarly in practice.

**Worked example (why ISLP says error rate is "not sensitive enough").** A node has 1,000 loans, 18 of them defaults ($\hat p=0.018$). A candidate split sends 100 loans (15 defaults) left and 900 loans (3 defaults) right.

| | Parent | Left (100 loans, $\hat p=0.15$) | Right (900 loans, $\hat p=0.00\overline3$) | Weighted children | Decrease |
|---|---|---|---|---|---|
| Error | 0.018 | 0.15 | 0.00333 | $0.1(0.15)+0.9(0.00333)=0.018$ | **0** |
| Gini | $2(0.018)(0.982)=0.03535$ | $2(0.15)(0.85)=0.255$ | $2(0.00333)(0.99667)=0.00664$ | $0.1(0.255)+0.9(0.00664)=0.03148$ | **0.00387** |

Both children still have "non-default" as the majority class, so the error rate sees no improvement. Yet the split clearly isolates a high-risk group (15% versus 0.3%). Gini rewards the split; the error rate does not. With 1.83% positives this matters a lot. Class weights in trees work by replacing the counts with weighted counts in $\hat p_k$.

### d.4 Cost-complexity (weakest-link) pruning

A fully grown tree overfits. Stopping early is short-sighted: a weak split can enable a strong one below it. So we grow a large tree $T_0$, then prune it back. For each $\alpha\ge0$, find the subtree $T\subseteq T_0$ that minimises (ISLP eq. 8.4)

$$C_\alpha(T)=\sum_{m=1}^{|T|}\sum_{i:\,x_i\in R_m}(y_i-\hat y_{R_m})^2+\alpha|T| .$$

- The first term is training error. For classification, use Gini or error weighted by node size.
- $|T|$ is the number of leaves.
- $\alpha$ is the price we pay per leaf. $\alpha=0$ keeps $T_0$; a larger $\alpha$ gives a smaller tree. It plays the same role as $\lambda$ in ridge/lasso.

**How the sequence is found (weakest link).** For each internal node $t$, compare:
- $R(t)$: the error if the branch below $t$ were collapsed into a single leaf;
- $R(T_t)$: the error of the branch as it stands, which has $|T_t|$ leaves.

Collapsing removes $|T_t|-1$ leaves and increases error by $R(t)-R(T_t)$. So the "error increase per leaf removed" is

$$g(t)=\frac{R(t)-R(T_t)}{|T_t|-1}.$$

Repeatedly collapse the node with the smallest $g(t)$, the weakest link. Each collapse happens at $\alpha=g(t)$, which produces a *nested* sequence of subtrees indexed by increasing $\alpha$. Then pick $\alpha$ by K-fold CV (ISLP Algorithm 8.1, steps 2–4). In scikit-learn, use `cost_complexity_pruning_path()` to get the candidate $\alpha$s, then tune `ccp_alpha` in our GroupKFold/temporal CV.

### d.5 Tree-based importance (interpretation step)

ISLP §8.2.2 (p. 345) computes importance as the total decrease in RSS (regression) or Gini (classification) from splits on a feature, averaged over trees. This is scikit-learn's `feature_importances_`, also called MDI.

Caveats to state in the report:
- MDI is computed on training data.
- It favours features with many possible cut points (continuous or high-cardinality).
- It spreads credit unpredictably between correlated features.

Complement it with **permutation importance on held-out folds** and **SHAP** values. SHAP explains individual decisions, which is also what a declined applicant would need. For linear models, compare with standardised coefficients and odds ratios (b.1).

---

## e. (Optional) SVM in one paragraph

ISLP §9.5 (eq. 9.25, pp. 384–385) rewrites the support vector classifier as "loss + penalty":

$$\min_\beta\ \sum_i\max\big[0,\,1-y_if(x_i)\big]+\lambda\lVert\beta\rVert^2,\qquad y_i\in\{-1,+1\}.$$

The **hinge loss** is exactly zero for points correctly classified beyond the margin. So only the points on or inside the margin (the support vectors) shape the solution. Logistic regression uses $\log(1+e^{-y_if(x_i)})$ instead, which is never exactly zero, and the two losses look similar (ISLP Fig. 9.12).

The RBF kernel $K(x,x')=\exp(-\gamma\lVert x-x'\rVert^2)$ makes the boundary non-linear (ISLP §9.3.2). For credit scoring the key fact is that **an SVC outputs a signed distance, not a probability**. `SVC(probability=True)` fits a Platt-scaling sigmoid with an internal CV on top. So any probability claims or cost thresholds from an SVC rely on that calibration step.

HOMLP: SVMs moved to online **Appendix C** in this edition. They are not one of the numbered chapters.
