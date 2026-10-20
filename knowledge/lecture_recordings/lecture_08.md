# Lecture 8: Unsupervised Learning and K-Means Clustering
> Summary of an audio recording of the lecture. The full transcript is not published. Speech-to-text was imperfect, so check important details against the slide notes in `../lectures/`.

## Recording summary
### Flow Summary
This session covered the fundamental differences between supervised and unsupervised learning, specifically focusing on clustering techniques, dimensionality reduction, and the mechanics of the K-means algorithm.

### Supervised vs. Unsupervised Learning
- Supervised learning involves learning from labeled data to predict targets or underlying relations.
    - Example: Identifying spam emails or predicting house prices based on historical sales.
- Unsupervised learning uses unlabeled data to find patterns, identify latent variables, or achieve data compression.
    - Examples include topic modeling (inferring themes in news) and autoencoders for compact representations.
- Dimensionality reduction is used to handle high-dimensional data where many features may be noise.

### Clustering and K-Means Algorithm
- Clustering groups data points based on similarity, typically measured by Euclidean distance or Manhattan distance.
- K-means clustering:
    - Requires a predetermined number of clusters (K).
    - Process involves choosing centroids, assigning points to the closest centroid, and recalculating the mean of those points until convergence.
    - Objective function: Minimizing the within-cluster sum of squares (J), which measures how spread out points are from their respective centroids.
- Challenges with K-means:
    - Random initialization can lead to local minima rather than global optima.
    - The "Elbow Method" is used to determine the optimal number of clusters by plotting the cost function and finding the point where the rate of decline levels off.

### Initialization Techniques
- Random initialization: Choosing random points as initial centroids, which may result in poor convergence or multiple local minima.
- K-means++: A more optimal initialization method where centers are chosen to be spread out across the data distribution.
    - Starts with one random point and adds subsequent centers with probability proportional to their squared distance from the nearest existing center.

### Next Steps
- Explain concepts like design choices and the "why" behind specific actions (supervised learning assessment).
- Proceed to the next prosit, focusing on supervised learning.

### Decisions Made
- None stated.

## Our summary

The first ~8 minutes of the recording are pre-class chatter and are unusable.

### 1. Learning objectives
- Distinguish clustering from dimensionality reduction.
- Be able to run k-means by hand.

### 2. Supervised vs unsupervised learning
- **Supervised** learning is "learning with labels" or learning by example. Examples: spam/not spam, or house prices learned from historical sales.
- **Unsupervised** learning is "learning without labels". You have the features (images, text, tabular data) but no target, so the goal is to find structure in the data.
  - In the house-price example, you would have the house features but not the sale prices.
- Main aims:
  - a **compact representation** (compression)
  - discovering **latent variables** (hidden common factors)
- Examples given:
  - **Topic models**: a generative approach that infers themes such as sports or politics from newspaper pages.
  - **Autoencoders**: encode inputs into a lower-dimensional latent space and reconstruct them. Mainly used for compression and feature extraction; the encoder can feed a downstream task network.
  - The lecturer mentioned their own past work transforming images to the frequency domain and dropping unimportant frequencies to get compact representations.
- Typical uses: exploratory data analysis (cluster to explore the data), feature learning/extraction, and **anomaly detection**.
- The two main areas are **clustering** and **dimensionality reduction**.
- The lecturer briefly referred back to other paradigms from earlier lectures: semi-supervised and self-supervised learning. LLMs were described as self-supervised, since they predict masked or next words, which creates labels from the data itself. This passage is garbled.

### 3. Dimensionality reduction
- More features do not always mean a better model (curse of dimensionality). With thousands of features, many may be noise that the model still tries to learn, which makes it more complex.
- Common practice: use an unsupervised method to reduce dimensions first, then train a supervised model on the reduced features.
- Dimensionality reduction methods were not covered in detail in this session; see the slides.

### 4. Clustering and distance
- **Clustering** (also called unsupervised classification) groups points by similarity, measured by distance:
  - **Euclidean**: √((x₁−x₂)² + (y₁−y₂)²), the high-school straight-line distance.
  - **Manhattan**: |x₁−x₂| + |y₁−y₂|.
- Points that are close together are likely to be in the same group; points far apart are likely to be in different groups.
- **Scaling matters.** The lecturer tied this back to the data preparation lecture: standardise (z-score) or min-max normalise first. Otherwise features with large ranges dominate the distance and are treated as more important.

### 5. K-means algorithm
- K is the number of clusters. It is a **hyperparameter** fixed in advance. Each cluster is represented by its mean, the **centroid**.
- Steps:
  1. **Initialise** K centroids. In the basic version they are random; they can be existing data points or any points in the space.
  2. **Assign** each point to its nearest centroid. Assignments are **exclusive**: each point belongs to exactly one cluster, and ties go to one of them.
  3. **Update** each centroid to the mean (coordinate-wise average) of the points assigned to it.
  4. Repeat steps 2 and 3 until assignments and centroids stop changing (**convergence**).
- **Analogy**: the government wants to build 3 markets. It places them randomly. Residents go to the nearest market. Each market is then moved to the centre of its users. Some residents switch to a market that is now closer, and the markets move again, until nothing changes.
- A student asked whether a random start could give all points to one centroid. The lecturer agreed that this is the weakness of random initialisation, and covered better initialisation next.
- K cannot change during a run. The lecturer called this a disadvantage: if the data naturally has more groups than K, the algorithm forces them into K.
- K-means is **sensitive to outliers**. A far-away point pulls its cluster's mean toward it. This was raised in a student question.
- Non-numeric data must first be converted to numeric values (encoded), because k-means works on distances.

**Worked example (K = 2).**
- Points: A(1,1), B(2,1), C(4,3), D(5,4), E(1,2).
- Initial centroids: μ₁ = (1,1) and μ₂ = (5,4). The recording says "one five" for the second centroid, but the distances worked on the board only make sense with (5,4).
- Squared distances to μ₁: A 0, B 1, C 13, D 25, E 1.
- Squared distances to μ₂: A 25, B 18, C 2, D 0, E 20. Only some of these were clearly audible.
- Assignment: cluster 1 = {A, B, E}, cluster 2 = {C, D}.
- New centroids: μ₁ = ((1+2+1)/3, (1+1+2)/3) ≈ (1.33, 1.33) and μ₂ = (4.5, 3.5).
- Reassigning with the new centroids gives the same clusters, so the algorithm has **converged**.
- The lecturer stressed that a centroid is a **coordinate**: average the x values and the y values separately, not a single number.

### 6. Objective function and local minima
- K-means minimises the **within-cluster sum of squares (WCSS)**: J = Σ_k Σ_{x∈C_k} ‖x − μ_k‖².
  - Small J means points are tight around their centroids.
  - Large J means the clusters are spread out.
- The alternating assign/update steps reduce J, but usually reach only a **local minimum**. The lecturer showed an example clustering with 3 clusters where some points were far from their centroids, compared with the better optimum.
- Challenges:
  - The result depends on initialisation, so different random starts (different people or runs) can give different clusters. The lecturer said this can be controlled, which presumably means fixing the random seed (garbled).
  - The number of iterations can in the worst case be exponential.
  - Choosing K is hard.
  - Clusters tend to be round blobs, so k-means handles odd cluster shapes poorly.

### 7. Initialisation: random vs k-means++
- **Random initialisation**:
  - Two centroids may land close together.
  - Some natural groups may get no centroid at all.
  - Convergence is slow, or the result is a poor local minimum.
- A manual heuristic is to pick points that are far apart, e.g. the two extremes of the data.
- **K-means++** is what libraries (e.g. scikit-learn's `KMeans`) use by default:
  1. Pick the first centre uniformly at random from the data.
  2. Add centres 2 to K one at a time, choosing each new centre with probability proportional to its **squared distance from the nearest centre already chosen**. Points far from the existing centres are more likely to be picked.
- Result: initial centres spread across the data, which gives faster convergence and better solutions.
- In the market analogy, purely random placement might put all three markets at the same station.
- The lecturer described this partly as "equal distances", which is not precise. The probabilistic squared-distance rule above is the correct one.

### 8. Choosing K: the elbow method
- Run k-means for a range of K values (2, 3, 4, ...) and compute J (WCSS) for each, using k-means++ initialisation. Plot J against K.
- The curve decays as K grows. The **elbow** is the point after which adding clusters only reduces J slightly. Use that K.
- Illustrative numbers from the board: K = 2 gives J = 1000 and K = 4 gives 500. Around K = 5, J is about 90. K = 6 gives 85 and K = 7 gives 80, a flat tail, so K ≈ 5. Some intermediate numbers were garbled.
- The lecturer treated this as hyperparameter tuning, done before the final clustering run.

### What the lecturer said about the prosits
- The ending is partly garbled. The gist: the next assessment, apparently on **Friday**, will be on **supervised learning**. It will have a structure similar to the first one but probably more questions. Students will be asked to **explain concepts and design choices** ("why do we do this, why do we do that"), not just compute.
- After that, the **second prosit** will be launched, also on supervised learning.
- No rubric, grading weights or deadlines were stated beyond this.

### Relevance to Prosit 2
- **Explain design choices.** The lecturer explicitly wants the reasoning behind each step. In the Prosit 2 report, justify each choice: why GroupKFold or temporal CV, why that threshold, why that calibration method, and why each fairness metric.
- **Scaling and leakage**: distance-based methods (k-means, kNN, PCA) need standardised features. Fit scalers, PCA or any clustering **inside each CV fold** on training data only, otherwise they leak information from the validation fold.
- **EDA and segmentation**: k-means on borrower features (after scaling and encoding) can reveal segments for EDA or for checking subgroup performance in the fairness audit. Treat cluster labels as unsupervised features that must also be fit within folds.
- **Kenya to Ghana shift**: comparing cluster membership or centroid distances between the Kenyan training data and the Ghanaian data is a simple way to show covariate shift, i.e. Ghanaian applicants falling far from every Kenyan centroid.
- **Outliers**: k-means' sensitivity to outliers is a reminder that heavy-tailed loan amounts or incomes should be log-transformed or clipped before any distance-based step, and before the loan-amount regression.
- **Anomaly detection**: the lecturer listed it as an unsupervised use case. Distance to the nearest centroid could flag unusual applications for the scorer, but this is optional and not a required deliverable.
