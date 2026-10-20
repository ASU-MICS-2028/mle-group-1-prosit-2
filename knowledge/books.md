# Book chapter map for Prosit 2

What each cited chapter covers, which Prosit 2 step it serves, who on the team needs it, and the key ideas in plain words. The summaries are our own paraphrases. Go to the book for figures and worked examples.

**Roles**
- **Germain**: Task 2 classification (probability of default, imbalance, calibration, PR-AUC, threshold).
- **Alice**: Task 1 regression (loan amount, log target, residuals) and transfer to new settings.
- **Liza**: problem framing, costs, fairness, responsible use.
- **Joseph**: pipeline, validation (GroupKFold, temporal CV, bootstrap CIs), final scorer.

**Derivations** live in `derivations.md`. This file only points to them.

---

## The books

| Book | Edition we use | Access |
|---|---|---|
| **ISLP**: James, Witten, Hastie, Tibshirani, Taylor, *An Introduction to Statistical Learning, with Applications in Python* (Springer, 2023) | Our PDF is the Python edition (ISLP, first printing July 2023). The brief says "ISLR"; chapters 2–9 have the same numbering and content in ISLR 2nd ed. (R) and ISLP. | **Free and legal** from the authors: https://www.statlearning.com |
| **HOMLP**: Aurélien Géron, *Hands-On Machine Learning with Scikit-Learn and PyTorch* (O'Reilly, Oct 2025) | Chapter list confirmed from the author's official notebook repo. **Our local PDF is only the free online bonus Appendix E (State-Space Models, 38 pp.); it does not contain chapters 3–10.** The HOMLP notes below come from the chapter titles and the book's known content, not from reading our copy. Check them against the library copy. | **Not free.** Use the Ashesi library or O'Reilly access. The companion Jupyter notebooks are free on the author's GitHub. |

**HOMLP chapter numbers in this edition** (they differ from the older TensorFlow 3rd edition, so check which edition the brief means):
1 ML Landscape · 2 End-to-End Project · **3 Classification** · **4 Training (Linear) Models** · 5 Decision Trees · **6 Ensemble Learning & Random Forests** · **7 Dimensionality Reduction** · 8 Unsupervised Learning · 9 Artificial Neural Networks · **10 Neural Nets with PyTorch** · 11–19 deep learning topics. Appendix C covers SVMs.

> If the brief was written against the older HOML 3rd edition (TensorFlow), its numbering was: 3 Classification, 4 Training Models, 5 SVMs, 6 Decision Trees, 7 Ensembles, 10 Intro to ANNs with Keras. Under that numbering, "Ch 3, 4, 6, 7, 10" means classification, linear models, **trees, ensembles**, and neural nets, which fits Prosit 2 better. Either way, read **trees + ensembles** (Ch 5–6 in the new edition).

---

## ISLP chapters

### ISLP Ch 2: Statistical Learning (pp. 15–68)
- **Covers:** what $f$ in $Y=f(X)+\varepsilon$ means; prediction vs inference; parametric vs non-parametric models; flexibility vs interpretability; training vs test error; the bias–variance trade-off; the Bayes classifier; KNN.
- **Prosit step:** problem framing and model-family choice (why we compare linear, kNN, trees and boosting); baselines.
- **Who:** Liza (framing), with all four needing the basics. Joseph for the train/test logic.
- **Key ideas:**
  1. We want low **test** error. Training error always falls as flexibility rises, so it is a misleading guide.
  2. Expected test MSE = variance + bias² + irreducible noise (eq. 2.7). Flexible models trade bias for variance.
  3. Some error ($\varepsilon$) cannot be removed by any model. Defaults are partly random events.
  4. **Prediction** (rank applicants) and **inference** (explain why someone was declined) may favour different models. Credit scoring needs both.
  5. KNN shows how "closeness" defines a model, and how $K$ controls flexibility. Its scale-dependence is why features must be standardised.
  6. The Bayes classifier (pick the most probable class) is the theoretical best. With 1.83% positives it predicts "no default" for almost everyone, which is why accuracy is useless here.
  7. Interpretable models (linear, small trees) matter when decisions affect people.

### ISLP Ch 3: Linear Regression (pp. 69–134)
- **Covers:** least squares for one and many predictors; standard errors, t-tests, $R^2$, RSE; qualitative predictors and dummies; interactions and non-linear terms; diagnostics (non-linearity, correlated errors, heteroscedasticity, outliers, leverage, collinearity); a comparison with KNN regression.
- **Prosit step:** Task 1 regression (OLS baseline, log target, residual analysis, coefficient interpretation).
- **Who:** Alice (primary). Joseph for the dummy encoding in the pipeline.
- **Key ideas:**
  1. OLS picks the coefficients that minimise the sum of squared residuals (§3.1.1, eq. 3.4; §3.2.1, eq. 3.22). Derivation in `derivations.md` §a.
  2. A coefficient is the change in $Y$ per unit of $X_j$ *holding the other predictors fixed*.
  3. Categorical variables become $k-1$ dummies (§3.3.1). Using all $k$ plus an intercept makes $X^TX$ singular.
  4. **Residual plots** show non-linearity (a curved pattern) and heteroscedasticity (a funnel shape). A log transform of $Y$ often fixes a funnel (§3.3.3). This is our case with loan amounts.
  5. Outliers (unusual $y$) and high-leverage points (unusual $x$) can pull the fit. Check them.
  6. Collinearity inflates coefficient variance. Measure it with the VIF (§3.3.3) and use it to decide what to drop or when to use ridge.
  7. Linear regression beats KNN when the true relationship is close to linear, or when $p$ is large relative to $n$ (§3.5).

### ISLP Ch 4: Classification (pp. 135–200)
- **Covers:** why not to use linear regression for a 0/1 outcome; logistic regression (odds, logit, maximum likelihood, multiple and multinomial); LDA, QDA, naive Bayes; confusion matrix, thresholds, ROC/AUC; a comparison of methods; GLMs.
- **Prosit step:** Task 2 (the logistic model, interpreting odds ratios, the threshold trade-off, the ROC curve). The running "Default" example is credit risk.
- **Who:** Germain (primary). Liza for thresholds and error costs.
- **Key ideas:**
  1. Logistic regression models the **log-odds** as linear in $X$ (eq. 4.4). $e^{\beta_j}$ is an odds ratio. Derivation in `derivations.md` §b.
  2. The model is fitted by **maximum likelihood** (eq. 4.5). There is no closed form, so it is solved iteratively.
  3. On the Default data, the 0.5 threshold gives low overall error but misses most defaulters. Lowering the threshold to 0.2 catches more defaulters at the cost of more false alarms (§4.4.2). This is exactly our cost-matrix question.
  4. Sensitivity, specificity, precision, the confusion matrix, and the ROC curve with its AUC (§4.4.2, Tables 4.6–4.7, Fig. 4.8).
  5. **Confounding** (§4.3.4): a variable's sign can flip once another variable is added ("students" example). This is relevant to fairness arguments about proxies.
  6. LDA and naive Bayes are alternative probabilistic classifiers. Logistic regression and LDA usually give similar linear boundaries.
  7. Which method wins depends on the true boundary: linear favours logistic/LDA, moderately non-linear favours QDA/naive Bayes, highly non-linear favours KNN (§4.5).

### ISLP Ch 5: Resampling Methods (pp. 201–228)
- **Covers:** the validation-set approach; LOOCV; k-fold CV and its bias–variance; CV for classification; the bootstrap.
- **Prosit step:** model selection and honest evaluation (GroupKFold and temporal CV are variants of k-fold); **bootstrap confidence intervals** for PR-AUC, RMSE, etc.
- **Who:** Joseph (primary). Everyone reporting a metric.
- **Key ideas:**
  1. A single train/validation split is noisy and wastes data. k-fold (k = 5 or 10) is the standard compromise.
  2. CV estimates test error so you can choose hyperparameters ($\lambda$, tree size, $K$).
  3. **Everything learned from data (scaling, encoding, feature selection, calibration) must happen inside each fold.** Otherwise information leaks and the scores are optimistic. Build it as a `Pipeline`.
  4. Plain k-fold assumes rows are independent. When rows share a borrower (or a time order), use **GroupKFold** (no borrower in both train and test) or **forward-chaining temporal splits** (train on the past, test on the future). This is our extension of the chapter's logic.
  5. The **bootstrap** resamples the data *with replacement* to estimate the variability of any statistic (§5.2). Resample the test predictions about 1,000 times and take the 2.5th–97.5th percentiles for a 95% CI.
  6. With only 1.83% positives, a fold may hold very few defaulters. Stratify (`StratifiedGroupKFold`), and expect PR-AUC CIs to be wide.

### ISLP Ch 6: Linear Model Selection and Regularization (pp. 229–288)
- **Covers:** best-subset and stepwise selection; $C_p$/AIC/BIC/adjusted $R^2$; **ridge** and **lasso**; choosing $\lambda$ by CV; PCR and PLS; high-dimensional problems.
- **Prosit step:** Task 1 Ridge/Lasso models; L2/L1 penalties in logistic regression (Task 2); feature selection.
- **Who:** Alice (primary). Germain (regularised logistic regression).
- **Key ideas:**
  1. Ridge adds $\lambda\sum\beta_j^2$ and shrinks all coefficients smoothly (eq. 6.5). It always has a unique solution (`derivations.md` §a.6).
  2. Lasso adds $\lambda\sum|\beta_j|$ and sets some coefficients exactly to zero (eq. 6.7). This is automatic variable selection and makes models easier to read.
  3. Shrinkage trades a little bias for a large drop in variance, which helps most when predictors are many or collinear.
  4. **Standardise predictors first.** The penalty is unfair to features with large units.
  5. Choose $\lambda$ by cross-validation (§6.2.3). Prefer the simplest model within one standard error of the best.
  6. Ridge suits many small effects; lasso suits a few strong effects (§6.2.2 comparison).
  7. When $p$ is large relative to $n$, OLS fails ($R^2\to1$ on training data while test error explodes). Regularise.

### ISLP Ch 8: Tree-Based Methods (pp. 331–366)
- **Covers:** regression and classification trees; recursive binary splitting; Gini/entropy; cost-complexity pruning; bagging; out-of-bag error; random forests; variable importance; **boosting**; BART.
- **Prosit step:** pruned decision tree, random forest and gradient-boosting models for both tasks; tree importance.
- **Who:** Germain and Alice (models). Joseph (tuning inside CV). Liza (whether the trees are interpretable).
- **Key ideas:**
  1. Trees split the feature space into boxes and predict the box mean (regression) or class share (classification).
  2. Splits are chosen greedily to reduce RSS or Gini/entropy (eq. 8.1, 8.6, 8.7). Error rate is too insensitive for growing a tree (`derivations.md` §d).
  3. Grow big, then **prune** with cost complexity, $\text{RSS}+\alpha|T|$ (eq. 8.4), choosing $\alpha$ by CV.
  4. Single trees are easy to explain but unstable (high variance).
  5. **Bagging** averages trees fitted on bootstrap samples. **Random forests** also consider only a random $m\approx\sqrt p$ features at each split, which decorrelates the trees and lowers variance further.
  6. Out-of-bag samples give a free validation estimate. Importance is the mean decrease in RSS or Gini (p. 345).
  7. **Boosting** fits small trees one after another to the current residuals, scaled by a learning rate (Algorithm 8.2, p. 349). Its tuning knobs are the number of trees $B$ (it can overfit), the shrinkage $\lambda$, and the depth $d$.

### ISLP Ch 9: Support Vector Machines (pp. 367–398)
- **Covers:** the maximal-margin classifier; the soft-margin support vector classifier with budget $C$; kernels (polynomial, radial); multi-class extensions; the link to logistic regression (hinge loss); ROC curves for SVMs.
- **Prosit step:** the SVC (RBF) model in the ≥5-model comparison. SVR is the regression analogue, which ISLP does not cover in depth.
- **Who:** Germain (SVC), Alice (SVR).
- **Key ideas:**
  1. An SVM looks for the boundary with the widest margin. Only points on or inside the margin (the support vectors) matter.
  2. $C$ (budget/penalty) trades margin width against violations. It is a bias–variance knob; tune it by CV.
  3. Kernels such as RBF, $\exp(-\gamma\lVert x-x'\rVert^2)$, give non-linear boundaries without building features explicitly.
  4. "Loss + penalty" view: hinge loss + ridge penalty (eq. 9.25). Hinge and logistic losses look alike, so SVMs and logistic regression often perform similarly (§9.5).
  5. **SVMs output scores, not probabilities.** Calibrate them (Platt) before using a cost threshold.
  6. Fitting scales roughly quadratically or worse with $n$, so on a large loan book subsample or use a linear SVM.
  7. Standardise features first, because the RBF kernel uses distances.

---

## HOMLP chapters (Scikit-Learn & PyTorch edition, 2025)

*No pages are cited: our PDF does not contain these chapters. Section titles below are paraphrased from the chapter topics.*

### HOMLP Ch 3: Classification
- **Covers:** binary classifiers in scikit-learn; cross-validated predictions; the confusion matrix; precision, recall, F1; the **precision/recall trade-off** and choosing a decision threshold; PR curve vs ROC curve; multiclass and multilabel classification.
- **Prosit step:** Task 2 evaluation (PR-AUC as the headline metric, threshold selection, `cross_val_predict`).
- **Who:** Germain (primary), Joseph (scorer).
- **Key ideas:**
  1. Accuracy misleads on skewed classes: "always predict non-default" scores 98.2% here.
  2. Precision = share of flagged loans that truly default; recall = share of defaulters we catch.
  3. Moving the threshold trades precision against recall. Use `decision_function` or `predict_proba` plus your own threshold rather than `predict()`.
  4. **Prefer the PR curve over ROC when positives are rare** (Géron's rule of thumb). ROC can look great while precision is poor.
  5. `cross_val_predict` gives clean out-of-fold scores for plotting curves and choosing thresholds without touching the test set.
  6. Choose the threshold from business requirements (here, the cost matrix in `derivations.md` §b.8), not by default.

### HOMLP Ch 4: Training Linear Models
- **Covers:** linear regression via the **normal equation** and SVD; computational complexity; batch, stochastic and mini-batch **gradient descent**; polynomial regression; learning curves; **ridge, lasso, elastic net**; early stopping; **logistic regression** (estimating probabilities, the log-loss cost, its gradient, decision boundaries); softmax regression.
- **Prosit step:** derivations (a) and (b); the Ridge/Lasso/logistic models; diagnosing over- or under-fitting with learning curves.
- **Who:** Alice (linear/ridge/lasso), Germain (logistic). All four for the oral derivations.
- **Key ideas:**
  1. The closed form $\hat\theta=(X^TX)^{-1}X^Ty$. In practice libraries use the SVD/pseudo-inverse, which also handles singular $X^TX$.
  2. Gradient descent needs feature scaling and a sensible learning rate. Too large diverges; too small is slow.
  3. Learning curves (error against training-set size) separate high bias (both curves high) from high variance (a gap between them).
  4. Regularised models: ridge (L2), lasso (L1, gives sparsity), elastic net (a mix). Scale inputs first.
  5. The logistic cost is the log-loss. It is convex and its gradient is "error × feature", so gradient descent finds the global minimum.
  6. In scikit-learn, regularisation strength in `LogisticRegression` is `C`, the *inverse* of $\alpha$/$\lambda$.

### HOMLP Ch 5: Decision Trees (not in the brief's list; recommended)
- **Covers:** training and visualising trees; class probabilities; the CART algorithm; Gini vs entropy; regularisation hyperparameters (`max_depth`, `min_samples_leaf`, …); regression trees; sensitivity to axis orientation; high variance.
- **Prosit step:** the pruned decision tree; derivation (d).
- **Who:** Germain, Alice.
- **Key ideas:**
  1. CART is greedy and binary, and minimises weighted child impurity.
  2. Gini is slightly faster to compute; entropy gives slightly more balanced trees. Results are usually similar.
  3. An unrestricted tree overfits. Restrict depth or leaf size, or prune with `ccp_alpha`.
  4. Trees need no feature scaling and handle mixed feature types.
  5. Trees are unstable: small data changes give very different trees. This motivates ensembles.

### HOMLP Ch 6: Ensemble Learning and Random Forests
- **Covers:** voting classifiers; bagging and pasting; out-of-bag evaluation; random patches/subspaces; **random forests** and Extra-Trees; **feature importance**; boosting (AdaBoost, **gradient boosting**, histogram-based GB); stacking.
- **Prosit step:** the random forest and GBM/LightGBM/XGBoost models (the likely best performers); derivation (c); tree-importance interpretation.
- **Who:** Germain and Alice (models), Joseph (early stopping and tuning inside CV).
- **Key ideas:**
  1. Combining many diverse, reasonably good models beats any single one (the "wisdom of the crowd").
  2. Bagging and random forests reduce variance; OOB scores give free validation.
  3. Gradient boosting fits each new tree to the **residual errors** of the current ensemble (for general losses, the negative gradient).
  4. **Learning rate (shrinkage):** smaller values need more trees but generalise better. Use **early stopping** to choose the number of trees.
  5. Histogram-based boosting (scikit-learn's `HistGradientBoosting*`, LightGBM) bins features and is very fast on large tabular data. It handles missing values and categoricals natively.
  6. Impurity-based importance is a quick first look. Confirm with permutation importance or SHAP.
  7. Stacking learns how to combine models. Usually it is not worth the complexity for this Prosit.

### HOMLP Ch 7: Dimensionality Reduction
- **Covers:** the curse of dimensionality; projection vs manifold learning; **PCA** (explained variance, choosing dimensions, incremental and randomised PCA); random projection; LLE and other techniques.
- **Prosit step:** optional feature engineering and EDA. Use it to compress many correlated transaction-behaviour features or to visualise borrower segments. It also connects to ISLP §6.3 (PCR).
- **Who:** Joseph (pipeline option), Alice (if PCR is tried).
- **Key ideas:**
  1. In high dimensions points are far apart, so distance-based models (kNN, RBF-SVM) weaken.
  2. PCA finds orthogonal directions of maximum variance. Keep enough components to explain about 95% of the variance.
  3. PCA needs standardised inputs and must be fitted inside CV folds.
  4. PCA components are hard to explain to a declined applicant. That is an interpretability and fairness cost, so prefer it only if it clearly helps.
  5. Reducing dimensions can speed up training and remove noise, but it loses some information.

### HOMLP Ch 10: Neural Nets with PyTorch
- **Covers:** PyTorch tensors and autograd; building and training MLPs for regression and classification; loss functions (MSE, BCE-with-logits); optimisers; training loops; saving and loading models.
- **Prosit step:** optional extra model. Its main value is conceptual: **autograd computes exactly the gradients we derive by hand** ($X^T(p-y)$). A logistic regression *is* a one-neuron network with a sigmoid and BCE loss.
- **Who:** Germain (optional MLP), Joseph (if a PyTorch scorer is used).
- **Key ideas:**
  1. An MLP stacks linear layers with non-linear activations.
  2. Binary classification uses one output logit with `BCEWithLogitsLoss`, which equals the log-loss in `derivations.md` §b.3. Its `pos_weight` argument is the class-weight mechanism of §b.6 (same calibration caveat).
  3. Training loop: forward, loss, `backward()`, optimiser step, zero the gradients.
  4. Scale inputs, use early stopping, and watch for overfitting on small tabular data. Gradient boosting usually beats MLPs on tabular credit data.

### HOMLP Appendix C: Support Vector Machines (online)
- In this edition SVMs are an online appendix, not a chapter. It covers linear and soft-margin SVC, kernels (RBF), SVR and the hinge loss. Use it together with ISLP Ch 9.

---

## Quick lookup: Prosit step → where to read

| Prosit step | ISLP | HOMLP | Owner |
|---|---|---|---|
| Framing, costs, why accuracy fails | 2.1–2.2, 4.4.2 | 3 | Liza |
| Baselines (majority, mean) | 2.2 | 3 | Joseph |
| OLS / Ridge / Lasso, log target, residuals | 3.1–3.3, 6.2 | 4 | Alice |
| Logistic regression + class weights | 4.3 | 4 | Germain |
| kNN | 2.2.3, 3.5, 4.7.6 | (Ch 1–3 examples) | Germain/Alice |
| Pruned tree | 8.1 | 5 | Germain/Alice |
| Random forest, gradient boosting | 8.2 | 6 | Germain/Alice |
| SVC (RBF) / SVR | 9 | App. C | Germain/Alice |
| PR-AUC, thresholds | 4.4.2, 9.6.3 | 3 | Germain/Joseph |
| CV, GroupKFold, temporal CV | 5.1 | 2 (pipelines), 3 | Joseph |
| Bootstrap CIs | 5.2 | — | Joseph |
| Interpretation (coefficients, importance, SHAP) | 3.1–3.2, 4.3, 8.2.2 | 4, 6 | All; Liza for fairness reading |
| Calibration | (not covered) | 3 (probabilities) | Germain |

Not well covered in either book, so we need outside sources: **probability calibration** in depth (scikit-learn user guide, "Probability calibration"), **SHAP** (Lundberg & Lee, 2017), **fairness metrics** (for example demographic parity and equal opportunity; Barocas, Hardt & Narayanan, *Fairness and Machine Learning*, free online), and **temporal/grouped CV** (scikit-learn `TimeSeriesSplit`, `GroupKFold`, `StratifiedGroupKFold` docs).
