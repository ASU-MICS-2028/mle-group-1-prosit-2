# Lecture 7: Supervised Learning Algorithms Survey (Decision Trees, Random Forests, Boosting)
> Summary of an audio recording of the lecture. The full transcript is not published. Speech-to-text was imperfect, so check important details against the slide notes in `../lectures/`.

## Recording summary
### Flow Summary
This session provided a survey of supervised machine learning algorithms, starting with concepts like logistic regression and moving through decision trees, random forests, and gradient boosting. The discussion covered the general pipeline for these models, including hypothesis space selection, loss definition, optimization, and validation.

### Supervised Learning Concepts
- Goal: finding a mapping function from an input to an output ($X$ to $Y$) using labeled examples.
    - Classification: output is one of a finite set of classes (e.g., spam or not spam).
    - Regression: output is a continuous value (e.g., temperature tomorrow).
- Model Pipeline Steps:
    - Choose hypothesis space (the model, e.g., linear regression).
    - Define a loss function.
    - Select an optimization technique (e.g., gradient descent).
    - Validate using cross-validation to ensure generalization.

### Decision Trees and Impurity Measures
- Decision Tree Structure: A tree upside down, with the root at the top and leaves at the bottom.
- Splitting Process: Recursively splitting the dataset based on features until leaves are as pure as possible (all examples in a leaf belong to one class).
    - Greedy Splitting: Splitting data sequentially; only splitting what is left after previous splits.
- Measures of Uncertainty/Gain:
    - Entropy: A measure of uncertainty; higher entropy means more equal chance between classes.
        - Pure Node: Entropy ($H$) is zero (probability of one class is 1).
        - Balanced Binary Node: Entropy is 1 for a balanced (50/50) binary node. *(The auto-summary said "pure" here; that is an error.)*
    - Information Gain: Calculated as the parent's entropy minus the sum of weighted entropies of the branches; higher gain means better feature selection.
    - Gini Impurity: Defined as $1 - \sum_i p_i^2$; zero for pure nodes, and 0.5 for balanced binary nodes. *(The auto-summary wrote $1 - P^2$.)*

### Ensemble Methods Comparison
- Random Forest: An ensemble of many decision trees (a "forest").
    - Classification Prediction: Majority vote among all trees.
    - Regression Prediction: Simple averaging of predictions from all trees.
    - Randomization: At each stage, a random subset of features is considered for splitting, which improves diversity and generalizability.
- Gradient Boosting: Builds trees sequentially; the next tree is built based on the output of the previous tree to minimize its errors.

### Next Steps
- The lecturer will share the slides.
- The lecturer will share the next prosit so students can start working on it.

### Decisions Made
- None stated.

## Our summary

### 1. Recap: logistic regression and the general supervised pipeline
- Last lecture covered linear regression (minimising MSE with gradient descent) and binary classification. The lecturer reminded the class that the preferred classification loss was the **logistic (log) loss**, and that the algorithm is called **logistic regression** even though it is a classifier.
- Every supervised algorithm follows the same pipeline:
  1. **Choose a hypothesis space** H (the model family, e.g. all linear functions). A specific model h_θ is one member of that family, picked by its parameters θ.
  2. **Define a loss** suited to that model.
  3. **Choose an optimiser** (batch / stochastic / mini-batch gradient descent; fancier optimisers for neural nets; closed-form "normal equation" for linear regression; greedy splitting for trees; or no training at all for some methods).
  4. **Validate**, with k-fold cross-validation recommended.
- Why validate? (Answers collected from students and endorsed by the lecturer.) To monitor performance during training, to choose between models, and to tune hyperparameters, all so the model **generalises** to a test set it has never seen. The test set is used only for the final evaluation.
- The same problem can be solved by models from different hypothesis spaces (linear model, tree, forest). They give different kinds of functions.

### 2. Families of supervised models (roadmap)
- **Tree-based**: decision tree, then random forest, then gradient boosting and other boosting methods.
- **Margin-based**: SVM, which uses kernels.
- **Instance-based**: k-nearest neighbours.
- **Probabilistic**: naive Bayes.
- Only the tree-based family was covered in this session. SVM, kNN and naive Bayes were on the slides but not reached.

### 3. Questions to ask when choosing a model
- What does the decision boundary look like (line, tree, kernel, neighbourhood, distribution)? How is it trained? What does it assume about the data?
- Consequences to weigh:
  - training cost vs prediction cost
  - **interpretability**: white-box models (decision trees, where you can trace each decision) vs black-box models (e.g. neural nets). The lecturer linked this to explainable AI (XAI) and to **fairness and bias**, using the example of explaining why a model diagnosed a patient with cancer.
  - scaling with more rows and more features
  - robustness to noise, outliers and missing values (does it overfit noise?)
  - how much data it needs
- **Two objectives.** The training loss (e.g. MSE, log loss) is what the optimiser minimises. The evaluation metrics (accuracy, precision, recall, F1, ROC) are what you actually care about. The lecturer called these "secondary objectives".

### 4. Decision trees
- An upside-down tree: the **root** at the top, **branches** are the answers to questions, **internal nodes**, and **leaves** at the bottom that give the prediction.
- Works for classification and regression. For regression, the lecturer said leaf values are averaged to produce a number. A depth limit (a hyperparameter) stops the tree growing. A regression example was promised for later.
- Little preprocessing is needed: **no feature scaling** (scaling mattered for gradient descent, not here), and mixed feature types are fine.
- In practice you use the scikit-learn class rather than writing a tree from scratch. The lecturer still wants the class to understand the mechanics.
- **Building the tree**: start with the whole dataset at the root. Pick the feature (and threshold) that best separates the classes, then split. Recurse only on the **impure** branches, using what is left. This is **greedy** splitting. Stop when the leaves are pure (or you hit the depth limit). Features become yes/no questions via thresholds, e.g. "income > 50k?".
- A student asked whether a human picks the questions. Answer: no, the algorithm picks them by computation; the lecturer was only demonstrating by hand.
- **Purchase example (illustrative, 10 customers).** Root "income > 50k?": all 5 with lower income did not buy, so that leaf is pure. The 5 higher-income customers were mixed, so the next split was "age > 30?". Under 30: 2 did not buy (pure). Over 30: 2 bought and 1 did not, so the last split was "previous purchases > 0?", which gave pure leaves. The tree also tells you which feature to ask about first, since income was the most informative. The whiteboard numbers were partly garbled in the recording, but this is the overall structure.
- On **class imbalance**, a student asked whether splits must be even. The lecturer said no: a split separates the classes, not equal counts. The lecturer noted that datasets can be highly imbalanced (e.g. 80/20, or about 10% anomalies in anomaly detection).

### 5. Entropy, information gain, Gini
- **Entropy** measures uncertainty: H = −Σ p_i log₂ p_i.
  - A **pure** node has H = 0 (for example, every customer under 50k did not buy, so p = 1 and log₂1 = 0).
  - A 50/50 binary node has H = 1, the maximum uncertainty. A student checked that an age > 30 node with 3 buyers and 3 non-buyers would have H = 1, and the lecturer confirmed.
  - The minus sign in front makes H non-negative, because log of a probability is ≤ 0. Students had asked about this.
  - For multi-class problems the same formula applies, and a split can have more than two branches.
- **Information gain** = H(parent) − Σ (n_child / n) · H(child), i.e. the uncertainty before the split minus the weighted uncertainty after it. Pick the feature with the highest gain.
- **Gini impurity** = 1 − Σ p_i², the probability of mislabelling a random draw. It is 0 for a pure node and 0.5 for a balanced binary node, whereas entropy gives 1 for the balanced case.
- Trees give a form of **feature importance** for free: the more useful features are chosen earlier. A student asked whether this could guide feature selection in preprocessing, and the lecturer said yes.

**Worked example (8 students; features Studied and Attendance; target Pass with 5 yes / 3 no):**
- Parent entropy: −(5/8)log₂(5/8) − (3/8)log₂(3/8) ≈ 0.954. The recording says "0.94", but 0.954 is what the gains below are based on.
- Split on **Studied**:
  - Studied = yes: 4 passed, 0 failed, so H = 0.
  - Studied = no: 1 passed, 3 failed, so H ≈ 0.811.
  - Weighted entropy = 0.5·0 + 0.5·0.811 ≈ 0.406, so **gain ≈ 0.549**.
- Split on **Attendance**:
  - High: 3 passed, 1 failed, so H ≈ 0.811.
  - Low: 2 passed, 2 failed, so H = 1.
  - Weighted entropy ≈ 0.906, so **gain ≈ 0.049**.
- Studied wins and becomes the root. The Studied = yes branch is pure, so it is left alone.
- The Studied = no branch (4 students, parent H ≈ 0.811) is split on Attendance:
  - High: 1 passed, 1 failed, so H = 1.
  - Low: 0 passed, 2 failed, so H = 0.
  - Weighted entropy = 0.5, so gain ≈ 0.311.
- Final tree: Studied? yes → Pass. No → Attendance? low → Fail; high → 50/50 (no features left to split on).
- New students are classified by following the tree.

### 6. Random forests
- An **ensemble** of many decision trees. The number of trees is a hyperparameter that trades off accuracy against time and memory.
- Classification uses a **majority vote** across trees. Regression uses a **simple average**.
- The "random" part: at each split, each tree considers only a **random subset of features** (e.g. 5 of them) and picks the best-gain feature among those. A plain decision tree considers every remaining feature.
- The lecturer said this improves **diversity** and therefore **generalisability**, and makes the forest more robust than a single tree. The lecturer also said a random forest has a kind of built-in validation, so a separate validation set is not needed. This most likely refers to out-of-bag estimates; see the caution in "Relevance to Prosit 2" below.
- Trees can be trained in parallel.

### 7. Gradient boosting
- Also an ensemble of trees, but built **sequentially**. Each new tree is fitted to reduce the errors of the ensemble so far, adding a small correction each time.
- So random forest = parallel and independent trees; boosting = sequential, error-correcting trees. Both are tree-based.
- Boosting was only introduced briefly at the end of the session.

### What the lecturer said about the prosits
- At the end of the session, the lecturer said the **second prosit** would be released and shared so students could start working on it. That passage of the recording is heavily garbled.
- The lecturer also stressed **cross-validation** (k-fold recommended) for hyperparameter tuning and model selection, with the test set kept unseen.
- The lecturer emphasised separating the **training loss** from the **evaluation metrics** (precision, recall, F1, ROC), and **interpretability / fairness** as model-choice criteria.
- No grading or deadline details were given in this recording.

### Relevance to Prosit 2
- **Model choice**: tree ensembles (random forest, gradient boosting) are natural candidates for tabular loan default data. They need no scaling and handle mixed feature types, which suits the Kenyan loan features. Keep logistic regression as an interpretable baseline.
- **Imbalance**: splits are driven by class purity, not equal counts. Still, a heavily imbalanced default rate means you should use class weights or cost-based thresholds and report precision, recall, F1 and PR-AUC rather than accuracy, in line with the lecturer's "secondary objectives" point.
- **Validation**: the lecturer's "random forests have built-in validation" comment (out-of-bag) does **not** replace leakage-free CV in our setting. OOB samples are random rows, so the same borrower can appear in both the bag and the out-of-bag set, and future loans can be used to predict past ones. Use GroupKFold by borrower and temporal CV.
- **Loan-amount regression**: regression trees and forests average leaf or tree outputs. Forest predictions are bounded by the training target range, which matters when moving from Kenya to Ghana.
- **Calibration**: forest vote fractions and boosting scores are usually not well-calibrated probabilities. Calibrate them (Platt or isotonic, inside the CV) before applying a cost-based threshold.
- **Reason codes / fairness**: the white-box vs black-box discussion maps directly onto the scorer's reason codes and the fairness audit. Tree feature importances help, but per-applicant reasons need something like a shallow tree, a linear model, or SHAP-style attributions.
- **Feature importance for selection**: if trees are used to pick features, do it inside each CV fold to avoid selection leakage.
