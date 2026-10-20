# Lecture 6: Regression and Classification Methods

> Summary of an audio recording of the lecture. The full transcript is not published. Speech-to-text was imperfect, so check important details against the slide notes in `../lectures/`.

## Recording summary

### Flow summary
This session covered the mathematical representation of linear regression, including hypothesis functions and loss measurement. It then transitioned to classification methods, comparing zero-one loss with smoother surrogate losses like logistic and linear loss, before concluding with model selection techniques such as cross-validation.

### Linear regression concepts
- Hypothesis is a mathematical representation or model function
    - Uses features ($x$) each with an applied weight ($\theta$ or parameters)
- Training involves finding optimal parameters for each feature to contribute to the prediction
- General equation for linear hypothesis: $h(x)$
    - In one dimension, $h(x) = \theta_1 x + \theta_0$, where $\theta_0$ is a bias (y-intercept/constant in normal equation of a line)
- Number of $X$'s relates to data features; columns refer to features ($D$ is the number of features/dimension)
    - Hypothesis is a weighted sum of model parameters and features
- Bias can be incorporated by setting $x_0 = 1$, so that the term $\theta_0 x_0$ equals the bias

### Model representation and loss
- Vector representation: Product of parameters ($\theta$) and examples ($X^T$)
    - Data set is an $M \times N$ matrix, where $M$ is number of examples and $N$ is number of features
- Mean Squared Error (MSE) is typically used for linear regression loss
    - Compares prediction ($\hat{y}$) to actual label ($y$) by checking the squared difference: $(y - \hat{y})^2$
- Goal in training is to minimize the objective loss function, aiming for zero error

### Classification losses and techniques
- Binary classification involves assigning data points to a label $y$, which can be encoded as $-1$ or $1$
- Zero-one loss: gives 0 if prediction matches actual label, and 1 otherwise (strictly binary)
    - Disadvantage: does not indicate how wrong the model is during training
- Surrogate losses are used for training to provide gradient information
    - Linear Loss (Perceptron Loss): penalizes errors by a magnitude related to the difference between $y$ and $\hat{y}$
        - Correct prediction yields loss of 0; incorrect prediction yields positive loss proportional to error.
    - Logistic Loss (Binary Cross Entropy): performs better than linear loss regarding outliers
        - If misclassified, the product $(-y \cdot \hat{y})$ is positive and large, leading to a very large loss value.
        - If correctly predicted, the loss approaches zero.

### Model selection and optimization methods
- **Model Selection:** Using a validation set for model or hyperparameter selection before final testing on a test set
    - Cross-validation: Splitting training data into $K$ folds; training on $K-1$ folds and validating on one fold, repeated $K$ times
        - Leave one out cross-validation: Leaves only one example for validation.
- **Optimization Methods:** Two primary ways to find optimal parameters ($\theta$)
    - Ordinary Least Squares (Closed Form/Normal Solution): Directly calculates optimal parameters using matrix manipulation without training iterations.
    - Gradient Descent: Iteratively updates parameters based on the gradient of the loss function
        - Update Rule: $\text{next step} = \text{current parameters} - (\text{gradient of loss}) \times (\text{learning rate})$
        - Convergence occurs when the change between consecutive model parameters is minimal.
    - Variants of Gradient Descent:
        - Batch Gradient Descent: Computes gradient on the entire training dataset (stable but slow for large datasets).
        - Stochastic Gradient Descent (SGD): Computes gradient on a single random example per update (fast updates, less stable).
        - Mini Batch Gradient Descent: Calculates gradient on a small set of examples at a time (balances speed and stability).

### Next steps
- A ten-minute break was taken mid-session.

### Decisions made
- None stated.

## Our summary

This is a long (about 3-hour) session. Part 1 finishes linear regression (hypothesis, MSE, normal equation, gradient descent). Part 2 introduces binary classification and its losses. Part 3 is a quick pass over model selection and cross-validation. About ten minutes in the middle is break-time chatter and is unusable.

### 1. Linear regression recap: the hypothesis
- `h_θ(x) = θ₀ + θ₁x₁ + … + θ_d x_d`: a **weighted sum** of the features, one weight (parameter) per feature, plus a bias. `d` is the number of features (the "dimension"). Training means finding the weights, which say how much each feature contributes.
- **Bias trick:** add a constant feature `x₀ = 1` so that the bias becomes `θ₀·x₀` and the whole thing is a single sum from 0 to d. In matrix form this is `ŷ = Xθ`, where `X` is the m×n data matrix (m examples, n features) and the transpose is there only to make the dimensions line up.
- The lecturer said the weights are "usually between zero and one". That is not generally true for linear models: weights can be any real number, and their scale depends on the feature scaling.

### 2. MSE and why we square
- `J(θ) = (1/m) Σ (yᵢ − ŷᵢ)²`. The goal is to find the θ that minimises J.
- **Why square instead of taking the absolute value?** A student asked this. Absolute error (MAE) is also valid. Squaring penalises large errors more heavily. Example: true value 3, prediction 5 gives absolute error 2 but squared error 4.
- **Zero training loss is not the goal in itself.** With few examples, or a model too complex for the data, the model memorises noise in the training set and does badly on test data. That is **overfitting**. It is handled *during* training (for example, with regularisation and good feature selection), not afterwards. Non-linear models are more prone to it because they bend towards outliers.
- A student asked how text in the assignment datasets fits into this. All features must be **transformed into numbers** (encoding, from the preprocessing lecture), because the model is matrix multiplication.

### 3. Solving for θ: two routes
**(a) Closed form / normal equation (ordinary least squares).**
- MSE is **convex** (bowl-shaped; any chord lies above the curve), so it has a single minimum. That minimum is where the gradient is zero.
- Write the loss in vector form, `‖y − Xθ‖²`, and expand it into `yᵀy − 2θᵀXᵀy + θᵀXᵀXθ`. (The two cross terms are equal 1×1 scalars, which is why they merge into `−2…`. Much of class time went on this dimension check.) Differentiating, setting the result to zero and solving gives `θ = (XᵀX)⁻¹Xᵀy`.
- The normal equation needs no iterations: you compute the optimal θ directly from the data and labels. The lecturer said you will not be asked to prove it.

**(b) Gradient descent.**
- Picture standing on a hill and taking small steps downhill. Start from random θ. Repeat: compute the gradient of the loss (one partial derivative per parameter), then step `θ ← θ − α·∇J(θ)`. Stop when the change in θ between iterations is smaller than some ε. That is **convergence**. At the minimum the gradient is zero, so updates stop.
- For a convex loss, a zero gradient means the global minimum. Non-convex losses (for example, in neural networks) have **local minima**, so a zero gradient does not guarantee the global one.
- **Learning rate α (step size)** is a **hyperparameter**:
  - too small and convergence is slow;
  - too large and the steps bounce back and forth and can overshoot the minimum.
  - Options include a **line search** (try several α values per update, such as 0.1, 0.01, 0.001, and keep the best) or a **decaying schedule** (big steps when far from the minimum, smaller ones near it). The lecturer's analogy was taking a bus most of the way and then a short ride for the last stretch.
- **Variants:**
  - **Batch GD:** the gradient uses the whole training set. It is stable but slow on large m.
  - **Stochastic GD (SGD):** the gradient uses one random example. Each update is cheap, but updates are noisy and bounce around, so overall convergence can still take a while. It does still converge.
  - **Mini-batch GD:** the gradient uses B examples at a time; SGD is the case B = 1. It balances stability and cost, parallelises well on GPUs, and is where "batch size" comes from.
- **Comparison (from the slide):**
  - The normal equation always gives the exact optimum and handles large m fine, but the matrix inversion becomes expensive with many features.
  - Gradient descent needs no inversion, scales better with many features and extends to non-linear models, but it may stop at a "good enough" point rather than the exact optimum.
  - The lecturer named other optimisers: Adam, AdamW and RMSProp (the last is garbled as "R and Trol"). They follow the same principle.
  - A complexity remark ("O of n cube") is garbled in the transcript. Matrix inversion costs roughly cubic in the number of features.

### 4. Binary classification
- The output is discrete. Examples include spam detection and classifying CT scans into disease subtypes. Multi-label problems (an item can have several classes) also count.
- Labels are encoded as **−1 / +1**. The lecturer's reason was that the two classes sit on opposite sides with equal magnitude, so the model does not read 1 as "more important" than 0. With more than two classes, use one-hot encoding. (In practice libraries such as scikit-learn use 0/1 labels with no problem. The ±1 convention mainly makes the margin `y·ŷ` formulas below neat.)
- The model computes a raw **score** `h(x) = θᵀx`, which can be any real number (20, −35 and so on). The predicted class is `sign(h(x))`: +1 if the score is greater than 0, otherwise −1. This differs from regression, where the score *is* the prediction. A sigmoid plays a similar role later (neural networks and logistic regression).
- A **linear classifier** draws one line (or a plane or hyperplane in higher dimensions) to separate the classes. It does not move the data points; it only places the boundary. It fails when the data are not linearly separable (the classes are interleaved). In high dimensions you cannot visualise the data, and distance-based models (for example, nearest neighbours) suffer from the **curse of dimensionality**. PCA can reduce the number of dimensions.

### 5. Classification losses
- **0-1 loss:** 0 if `sign(score) = y`, otherwise 1.
  - It is fine as an **evaluation** metric: for example, 8 of 100 wrong gives 8% error and 92% accuracy.
  - It is useless for **training**. It is a step function, so it is not smooth or differentiable and gives no gradient. Two models making the same number of mistakes look identical even if one is much closer to the right boundary.
- **A good training (surrogate) loss should be:** (1) decreasing in the margin, (2) convex and (3) differentiable. The lecturer also said in passing that a decreasing loss would be convex; that is not true in general.
- **Linear / perceptron loss:** `max(0, −y·ŷ)`, where `ŷ` is the raw score.
  - Correct prediction (`y·ŷ > 0`) gives loss 0.
  - Wrong prediction gives loss equal to how far wrong it is. Example: `y = +1` with score −20 gives loss 20.
  - This tells you *how wrong* you are, but **outliers can dominate** the optimisation.
- **Exponential loss:** `exp(−y·ŷ)`. It blows up for badly misclassified points (for example, e²⁰), which makes gradients unstable, and it is also sensitive to noisy outliers.
- **Logistic loss = binary cross-entropy:** `log(1 + exp(−y·ŷ))`.
  - A badly misclassified point gets a large loss, but the log tames it.
  - A confidently correct point gets a loss near 0.
  - It is less dominated by outliers than the linear or exponential loss.
  - The lecturer's conclusion: **logistic loss (BCE) is usually the best choice for binary classification.**

### 6. Model selection and cross-validation
- Training and testing on the same data is like memorising past exam questions when the lecturer reuses them: it is cheating, and leakage. Split into train and test.
- To compare models or tune hyperparameters, use a **validation set** carved out of the training data, never the test set. Pick the best configuration, retrain on the full training set, then test once.
- With small data, a fixed validation split starves training. Example: 100 rows split 40/30/30 leaves only 40% for training. Use **K-fold CV** instead: split the training data into K equal folds, train on K−1 and validate on the remaining one, rotating K times. **Leave-one-out** is the case K = m.
- **Choosing K:**
  - Too small (for example, 3 folds) and each model trains on too little data.
  - Too large (for example, 100) and each model trains on nearly all the data, but you pay a high compute cost (100 fits). It is a trade-off.
- A student asked about **sequential / time-ordered data**. The lecturer said that ordinary shuffled CV may introduce **temporal leakage**, and that the splits should preserve the sequence. This answer is partly garbled.
- For very small datasets (the example was low-resource languages), choose K carefully. Leave-one-out is an option.

### What the lecturer said about the prosits
- **"You would play with this in your next prosit":** test the different classification losses and see which performs best. Logistic loss (BCE) is the expected default for binary classification, so be ready to justify the loss you use.
- Text or categorical columns in the prosit datasets must be encoded into numbers first, as covered in the preprocessing lecture.
- Use a validation set or K-fold CV for model and hyperparameter selection. Never touch the test set during selection. Training and testing on the same data was explicitly called cheating.
- For time-ordered data, watch out for temporal leakage when splitting.
- The slides are on Canvas. Coming next: an overview of other algorithms (decision trees, XGBoost and others).
- No deadlines or grading criteria were stated in this session.

### Relevance to Prosit 2
- **Default model loss:** logistic loss / BCE is the right training loss for default vs non-default. Report the 0-1-style metrics (accuracy and error rate) only alongside imbalance-aware ones. On imbalanced Kenyan loan data, 0-1 loss and accuracy are misleading: a model that predicts "no default" for everyone looks good.
- **Raw score, then threshold:** the lecture's `sign(score)` uses a fixed threshold at 0 (probability 0.5). Prosit 2 asks us to replace this with a **cost-based threshold** on calibrated probabilities. BCE is also a proper scoring rule, which is why it pairs naturally with **calibration** checks.
- **Outlier sensitivity:** the lecturer's warning that linear and exponential losses let outliers dominate also applies to the **loan-amount regression**. MSE squares errors, so a few huge loans can drive the fit. Consider MAE, Huber loss or a log-transformed target, and report errors in currency units.
- **Leakage-free validation:** the lecture's K-fold applies, but our data needs **GroupKFold** (no borrower in both train and validation) and **temporal CV** (train on earlier loans, validate on later ones). This is the "temporal leakage" the student asked about.
- **Hyperparameters and solvers:** the learning rate, regularisation strength and choice of solver are selected on validation folds only. Scikit-learn's LogisticRegression uses iterative solvers (gradient-based optimisation). The closed-form solution applies only to plain least-squares regression.
- **Overfitting / regularisation:** relevant to keeping the scorer simple and stable enough to transfer from **Kenya to Ghana**. A model that memorises Kenyan noise will degrade under shift.
- **Linear model interpretability:** in a linear or logistic model each feature's contribution is `θⱼ·xⱼ`, which is the basis for **reason codes** in the scorer. It is also why consistent feature scaling matters.
