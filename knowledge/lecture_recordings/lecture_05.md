# Lecture 5: Machine Learning Model Concepts

> Summary of an audio recording of the lecture. The full transcript is not published. Speech-to-text was imperfect, so check important details against the slide notes in `../lectures/`.

## Recording summary

### Flow summary
This session provided an overview of different types of machine learning, including supervised, unsupervised, self-supervised, and weakly supervised learning. It then detailed the structure of a model, focusing on linear regression, training, evaluation, and the distinction between regression and classification tasks.

### Types of learning
- Supervised learning:
    - Uses inputs and correct outputs (labels) to learn a mapping.
    - Example: Predicting house prices using features like size and location as inputs and price as the label.
- Unsupervised learning:
    - Does not create labels; clusters data points based on similarities.
- Self-supervised learning:
    - Model creates its own labels (pseudo labels) by studying the input data.
- Weakly supervised learning:
    - Uses a dataset where only a few examples have labels, allowing training on the whole distribution.

### Data and models
- Dataset components: Examples (pair of feature and label), features, and labels.
- Dataset characteristics: Size (number of examples) and diversity.
- Model representation: A complex collection of numbers defining the mathematical relationship between input features and output.
- Linear Regression model structure: $Y = BX + C$, where B is a coefficient/parameter and C is an intercept/bias term.

### Training and evaluation
- Training: Learning the best parameters (coefficients) for the model to make it more accurate.
- Loss function: A function used to determine model performance; training aims to minimize this loss.
- Mean Squared Error (MSE): One way to numerically characterize the loss by taking the mean of the squared differences between predicted ($\hat{Y}$) and actual ($Y$) values.
- Objectives: Two types—one for training (minimizing mathematical losses) and one for evaluation (human-readable).

### Regression vs classification
- Regression: Predicting continuous numerical values (e.g., temperature, house prices, salary).
- Classification: Selecting among a discrete set of classes based on input (e.g., dog, cat, goat).
    - A process can involve both: using regression to predict a value and then classifying that prediction into a class.

## Our summary

A short (about 50-minute) session that sets up the vocabulary for supervised learning. It ends partway through the linear-regression maths, which Lecture 6 picks up.

### 1. Kinds of supervision (it depends on where the labels come from)
The lecturer framed the different "types of learning" by **where the labels come from and how far you can trust them**:
- **Supervised:** every example has a good-quality label. The model sees inputs and correct outputs and learns the mapping ("learning by example").
- **Unsupervised:** there are no labels. The model groups inputs by similarity (clustering) to find patterns. It does *not* invent labels.
- **Self-supervised:** there are no labels, so the model generates pseudo-labels from the inputs and then trains on them as if it were supervised.
- **Weakly supervised:** labels exist but are scarce (for example, 10 of 100 houses have sale prices) or noisy/partly wrong. The model uses the few labels to learn the whole distribution.
- Reinforcement learning was mentioned only in passing.

The running example was house prices: the features are size, location, number of storeys and nearby facilities, and the label is the sale price. If you have historical features but no prices, the problem becomes unsupervised (cluster similar houses).

### 2. The building blocks: data, model, training, evaluation, inference
- **Data:** a tabular dataset is a set of **examples** (rows). Each one is a (features, label) pair. All columns except the target are features. The example on the slide predicted rainfall from date, latitude/longitude, temperature, humidity, cloud cover, wind direction and pressure.
- Features can have mixed types (numeric, categorical such as wind direction). Images, audio and text are also turned into numbers. Combining text, image and audio is **multimodal** learning.
- A dataset is characterised by **size** (number of examples) and **diversity** (how much of the space the examples cover). Low diversity limits what the model can learn. Performance also depends on size.
- **Model:** "a collection of numbers" (parameters) that defines the mathematical relationship from features to output. Linear regression is the equation of a line, `y = b·x + c`: `b` is the coefficient (slope or weight) and `c` the intercept or bias.
- **Training** means finding the parameter values that make the model most accurate. The model *structure* (for example, "linear") is chosen first, and training fills in the numbers.
- A student asked about designing your own algorithm. The lecturer said that is what research does: you change an existing architecture only after you have *empirically* shown that existing models fall short. Don't invent a new model when an existing one works.

### 3. Loss: measure the errors
- The lecturer used an analogy: when marking 50 MCQs it is easier to count the wrong answers. Models are evaluated the same way, by measuring **error**, called **loss**. Training drives the loss down. The "best student" makes the fewest mistakes.
- **There are two objectives in a pipeline:**
  - a **training loss**, which is mathematically convenient (for example, squared error, whose units are squared); and
  - an **evaluation metric**, which is human-readable and ideally in the same units as the target.
  - The two **must be correlated**: improving one should improve the other.
- **MSE** is the mean over examples of `(y − ŷ)²`. Taking its square root gives **RMSE**, which is back in the target's units. (The transcript garbles the end of this passage.)
- `y` is the true label and `ŷ` ("y-hat") the prediction.

### 4. Regression vs classification
- **Regression** predicts a continuous number: temperature, house price, salary, or a student's raw exam score on a 0–600 scale.
- **Classification** picks one of a discrete set of classes (dog, cat, goat, sheep, snake; or house type such as studio, apartment or bungalow).
- The same domain can be framed either way depending on the labels. You can also chain the two: predict a score by regression, then bin it into classes (for example, scores 0–200 = "low performer").

### 5. Linear regression set-up (started, not finished)
- **Worked example (pricing your own house):** go round the neighbourhood and record each similar house's size in m² and its sale price (for example, GHS 500,000). Plot price against size as a scatter plot. Fitting a line through the points gives a model that can price a new house, say 105 m².
- The relationship need not be linear. A quadratic or polynomial fit can capture curvature. The question "how do we measure how good a fit is?" leads to loss and training.
- **Notation:** `X` holds the examples, each with `d` features, and `y` is a real-valued target. The **hypothesis** `h_θ(x)` maps features to `ŷ` under a linear assumption. Each feature gets one learnable parameter, and there is one extra bias.
- **The intercept's meaning:** it is the prediction when all features are zero. In the salary example (feature = years of experience), a new hire with zero experience still earns a base salary, and that base is the intercept. The lecturer noted the bias shifts the line up or down. It does not change the slope.
- **Why the transpose (θᵀx)?** Parameters and inputs are both stored as n×1 column vectors. Multiplying them requires matching inner dimensions, so one is transposed to 1×n, giving a 1×1 scalar prediction. A 3×2 matrix transposes to 2×3.

### What the lecturer said about the prosits
- **Feature choice is yours:** groups may pick different features for the same problem and may combine raw features into new ones (feature engineering). "The quality of the features you select would also determine the quality of your model."
- Choosing a structure (model family) is a justified, empirical decision. Show why a model is or isn't adequate before reaching for something more complex.
- Keep the training loss and the reported metric distinct, and make sure they move together. Report a human-readable metric (same units as the target) for evaluation.
- No deadlines or grading details were mentioned in this session.

### Relevance to Prosit 2
- **Default classification vs loan-amount regression:** this is exactly the regression-vs-classification split from section 4. Default is a discrete label. Loan amount is continuous, so it should be evaluated with RMSE or MAE in currency units, not MSE alone.
- **Training loss vs evaluation metric:** for the default model we train on log-loss but evaluate on business-readable measures (cost at a threshold, PR-AUC, calibration). The lecturer's rule that the two must correlate is why we check calibration and expected cost, not just the training loss.
- **Supervision quality:** default labels may be noisy or partly missing (loans still open, unclear write-offs). That is the weak-supervision situation, so document how labels were defined.
- **Diversity and shift:** the point about dataset diversity bears directly on the Kenya→Ghana shift. A model trained on a narrow Kenyan population will not cover Ghanaian borrowers, so quantify the covariate shift.
- **Intercept intuition:** in a logistic model the bias is the baseline log-odds of default when all features are zero (or at their mean, if standardised). This matters when explaining the scorer's reason codes relative to a baseline.
- **Feature engineering:** this is where leakage creeps in. Any feature built from post-origination information must be excluded.
