# Lecture 6: Unsupervised Learning (k-means Clustering and PCA)

> Study notes written in our own words from the "Unsupervised Learning" deck (42 slides; .pptx and .pdf both read).
> Slide numbers refer to the original deck. Many slides are diagrams; we read them from the PDF.

## What this lecture is about

Unsupervised learning finds structure in data **without labels**. This lecture covers the two workhorse methods. **k-means clustering** groups points so that each point belongs to the cluster with the nearest centre; it alternates between assigning points and moving centres, always lowering a "within-cluster squared distance" objective, but it can get stuck in local optima, depends on initialisation (fixed by k-means++), assumes roundish clusters, and needs you to choose $k$ (elbow method). **Principal Component Analysis (PCA)** compresses many correlated features into a few uncorrelated "principal components" that keep as much variance as possible, by computing eigenvectors and eigenvalues of the covariance matrix of standardised data; you decide how many components to keep using the explained variance ratio.

---

## 1. Learning objectives (slide 2)

1. Distinguish **clustering** (discovering groups) from **dimensionality reduction** (compressing data).
2. Do k-means **by hand**: distances, assignments, centroid updates.
3. Explain why k-means converges, and critique its sensitivity to initialisation and fixed cluster shapes.
4. Describe PCA as finding principal axes via **eigen-decomposition of the covariance matrix** to capture maximum variance.
5. Interpret PCA on real data (e.g. MNIST), using variance explained and the need for standardisation.

(Note: objective 5 mentions MNIST, the handwritten-digit dataset, but no MNIST slides appear in the deck we have.)

---

## 2. Supervised vs unsupervised pipelines (slides 3–7)

**Supervised pipeline** (slides 3–5): training data with inputs $X$ (e.g. emails) and labels $Y$ ("spam"/"ham") → learning method → predictor $f: X \to Y$ → predictions on test data. Three stages: representation, model fitting and selection, prediction and generalisation.

**Unsupervised pipeline** (slide 6): same picture, but **there are no labels $Y$** (the diagram crosses them out). The training data are just $X$ (e.g. images of faces and motorbikes).

**Unsupervised learning = learning without labels** (slide 7):

- Examples: **clustering** ("unsupervised classification"), **dimension reduction** ("unsupervised regression"), **generative modelling** (topic models, autoencoders, GANs, LLMs, diffusion models).
- Common objectives: compact representation / compression; finding **latent variables** (hidden factors that explain the data).
- Use cases: exploratory data analysis, feature learning / embeddings, **anomaly detection**.

---

## 3. Clustering (slides 8–10)

**Clustering** (slide 9): group data points so that **similar** points are in the same cluster and **dissimilar** points are in different clusters. Points live in (often high-dimensional) Euclidean space, or we have a distance / (dis)similarity function between them.

Related: **anomaly / outlier detection**, finding points that don't fit well in any cluster.

Example (slide 10): unlabelled photos of birds, landscapes and lions; clustering recovers the three groups ("infer labels").

---

## 4. k-means clustering (slides 11–28)

### 4.1 Setup (slide 11)

Input: $D = \{x_1, \dots, x_n\}$, $x_i \in \mathbb{R}^d$. Choose $k$. Represent each cluster by one **centre** (centroid) $\mu_j \in \mathbb{R}^d$. Assign each point to its closest centre:

$$z_i = \arg\min_j \|x_i - \mu_j\|$$

($z_i$ is the cluster label of point $i$.) This splits space into a **Voronoi partition**: each region is the set of points closer to one centre than to any other.

### 4.2 The algorithm, step by step (slides 12–17, pictures)

This is **Lloyd's algorithm**:

1. **Initialise** $k$ centres (slide 12: two stars placed among the points).
2. **Assignment step**: give every point to its nearest centre (slide 13: a line separates the two groups).
3. **Update step**: move each centre to the **mean** of its assigned points (slide 14).
4. Repeat assignment (slide 15) and update (slide 16) until the assignments stop changing (slide 17: the boundary now cleanly separates two natural groups).

### 4.3 Worked example (slide 18)

Partition into two clusters: A(1,1), B(2,1), C(4,3), D(5,4), E(1,2), starting with $\mu_1 = (1,1)$ and $\mu_2 = (5,5)$. The slide lists the steps; the numbers below are our working.

**Iteration 1: distances** (Euclidean):

| Point | to $\mu_1=(1,1)$ | to $\mu_2=(5,5)$ | Assigned |
|---|---|---|---|
| A(1,1) | 0 | $\sqrt{32}\approx5.66$ | 1 |
| B(2,1) | 1 | $\sqrt{25}=5$ | 1 |
| C(4,3) | $\sqrt{13}\approx3.61$ | $\sqrt{5}\approx2.24$ | 2 |
| D(5,4) | $\sqrt{25}=5$ | 1 | 2 |
| E(1,2) | 1 | $\sqrt{25}=5$ | 1 |

**Update centroids:**

- $\mu_1 = \text{mean}(A,B,E) = \left(\tfrac{1+2+1}{3}, \tfrac{1+1+2}{3}\right) = (1.33, 1.33)$
- $\mu_2 = \text{mean}(C,D) = (4.5, 3.5)$

**Iteration 2:** recompute distances; every point stays in the same cluster (e.g. C is $\approx0.71$ from $\mu_2$ but $\approx3.14$ from $\mu_1$). Assignments unchanged → **converged**. Clusters: {A, B, E} and {C, D}.

Final objective $J$ (sum of squared distances to centres): A 0.22 + B 0.56 + E 0.56 + C 0.50 + D 0.50 ≈ **2.33**.

### 4.4 Why it converges: the objective (slides 19–20)

k-means minimises the **within-cluster sum of squared distances**:

$$J = \sum_{i=1}^{n} \|x_i - \mu_{z_i}\|^2 = \sum_{j=1}^{k}\sum_{x \in C_j}\|x - \mu_j\|^2$$

Smaller $J$ = points closer to their centres (tighter clusters).

- **Assignment step**: each point moves to the centre that minimises its squared distance → $J$ can only go down (or stay).
- **Update step**: the mean is the point that minimises the sum of squared distances to a set → $J$ can only go down.

Since $J$ never increases and there are finitely many possible assignments, the algorithm stops. But it reaches a **local** optimum, not necessarily the global one.

### 4.5 Local minima (slide 21)

Picture: the same data (three groups) clustered two ways. Left: one centre per group (good). Right: two centres share the big group and one centre sits between the two small groups (bad), yet neither step can fix it. That's a **local minimum**.

### 4.6 Challenges (slides 22 and 28)

1. Usually converges only to a **local optimum**; result depends strongly on initialisation.
2. The number of iterations **can be exponential** in the worst case (in practice it converges quickly).
3. **Cannot model clusters of arbitrary shape** (it favours round, similar-sized blobs because it uses distance to a centre).
4. **Choosing $k$ is difficult.**

Slide 28's verdict: 1 and 2 are not big issues in practice; **4 (choosing $k$) is the biggest problem.**

### 4.7 Initialisation (slides 23–25)

Lloyd's heuristic doesn't generally find the optimum; it depends on the starting centres. Options:

- **Multiple random restarts**: run many times, keep the lowest $J$.
- **Farthest-points heuristic**: pick centres far apart; works well but is pulled toward outliers.
- **k-means++** (the standard).

Random seeding problems (slide 24): (1) two centres land in the same true cluster; (2) a true cluster gets no centre at all.

**k-means++** (slide 25):

1. Pick the first centre uniformly at random from the data points.
2. For centres $2, \dots, k$: pick a data point at random with probability **proportional to its squared distance to the nearest centre already chosen**.

Far-away points are more likely to become centres, so centres spread out across clusters.

### 4.8 Choosing $k$: the elbow heuristic (slides 26–27)

Plot $J$ against $k$. $J$ always decreases as $k$ grows (with $k = n$, $J = 0$), so you can't just minimise it. Look for **diminishing returns**: pick the $k$ after which increasing $k$ gives a negligible drop (the "elbow"). In the slide's example (four blobs), the elbow is at $k = 4$.

---

## 5. Dimensionality reduction and PCA (slides 29–41)

### 5.1 Goal (slide 30)

Given $D = \{x_1, \dots, x_n\}$, $x_i \in \mathbb{R}^d$, find an **embedding** (low-dimensional representation) $z_1, \dots, z_n \in \mathbb{R}^k$ with $k \ll d$.

Why: **visualisation** ($k$ = 1, 2, 3), **regularisation** (fewer inputs → less overfitting, a form of model selection), **unsupervised feature discovery** (learn features from the data).

### 5.2 What PCA is and why (slides 31–32)

**PCA** reduces the number of features while preserving as much **information (variance)** as possible, by turning many correlated variables into a smaller set of **uncorrelated** variables called **principal components**.

Problems with high-dimensional data that PCA helps with: computational cost, storage, hard to visualise, redundant/correlated features, overfitting risk.

### 5.3 Core concepts (slides 33–34)

- **Variance**: spread of data; in PCA, more variance = more information.
- **Covariance**: how two variables move together (positive = together, negative = opposite).
- **Eigenvectors**: directions of maximum variance. **Eigenvalues**: how much variance lies along each direction.

**Principal components** are new axes built from the original features. They are **orthogonal** (at right angles), **uncorrelated**, and **ordered by importance**: PC1 captures the most variance, PC2 the next most, and so on.

### 5.4 The maths (slides 35–38)

**Step 1, standardise** (slide 35): $z = \dfrac{x - \mu}{\sigma}$ for each feature. Otherwise large-scale features dominate (e.g. income 0–10,000 vs age 18–70: income would swamp PC1 purely because of its units).

**Step 2, covariance** (slide 36):

$$\mathrm{Cov}(X, Y) = \frac{\sum (X - \bar X)(Y - \bar Y)}{n-1}$$

For two features the **covariance matrix** is

$$C = \begin{bmatrix} \mathrm{Var}(X_1) & \mathrm{Cov}(X_1,X_2) \\ \mathrm{Cov}(X_2,X_1) & \mathrm{Var}(X_2) \end{bmatrix}$$

**Step 3, eigen-decomposition** (slide 37): solve $Cv = \lambda v$. Each eigenvector $v$ is a principal direction; its eigenvalue $\lambda$ is the variance along it (its importance).

**Step 4, explained variance** (slide 38): sort $\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_p$ (the slide has a typo writing $\lambda_1$ three times). The **explained variance ratio** of component $i$ is

$$\text{EVR}_i = \frac{\lambda_i}{\sum_{j=1}^{p}\lambda_j}$$

Use the cumulative EVR to decide how many components to keep (e.g. enough to explain 90–95%; the threshold is our example, not on the slide).

> **Intuition (ours).** If two standardised features are highly correlated (say "monthly inflow" and "monthly outflow"), the data form a narrow diagonal cloud. PC1 points along the diagonal (both features together) and carries most of the variance; PC2 is the thin perpendicular direction. Keeping only PC1 loses little information.

### 5.5 Algorithm steps (slide 39)

1. Collect the dataset.
2. Standardise features.
3. Compute the covariance matrix.
4. Compute eigenvalues and eigenvectors.
5. Sort components by eigenvalue.
6. Keep the top $k$.
7. Project the data onto them: $z = V_k^T x$ (new feature space).

### 5.6 Benefits and limitations (slides 40–41)

| Benefits | Challenges |
|---|---|
| reduces dimensionality and redundancy | components are hard to interpret |
| speeds up ML algorithms | **sensitive to scaling** |
| reduces storage | captures **only linear** relationships |
| improves visualisation | some information is lost |
| extracts meaningful patterns | **outliers** can distort it |

Key take-aways: PCA is **unsupervised** (ignores labels), converts correlated variables into uncorrelated components, maximises preserved variance, and is used widely (finance, healthcare, image processing).

---

## How this applies to Prosit 2

Unsupervised learning is **not the core** of Prosit 2 (which is supervised: default probability and loan amount), but it supports several tasks:

- **EDA and segmentation.** k-means on standardised borrower features (e.g. activity, loan history) can reveal borrower segments; check default rates per segment for insight. Remember k-means needs scaling and assumes round clusters; use k-means++ and multiple restarts; justify $k$ with the elbow plot.
- **Distribution shift (Kenya → Ghana).** Fit PCA (or clustering) on Kenyan training features and project Ghana data into the same space. If Ghana points fall in regions with few Kenyan points, or cluster proportions differ a lot, that is visual and quantitative evidence of **covariate shift**. Also a simple anomaly score (distance to the nearest Kenyan centroid) can flag Ghana applicants the model has never "seen" anything like.
- **Leakage still applies.** Scalers, PCA and k-means are *fitted* transforms: fit them on training folds only, inside the pipeline. Fitting PCA on all data (including test or Ghana) is train-test contamination (Lecture 3).
- **Cluster labels as features.** If you add "segment ID" as a feature, fit the clustering inside each training fold.
- **PCA vs reason codes.** PCA components mix many original features, which makes per-applicant **reason codes** hard to explain ("component 3 was high" means nothing to a borrower). Prefer original features in the deployed scorer; use PCA for diagnostics and visualisation.
- **Fairness.** Clustering can surface groups that are proxies for protected attributes (e.g. region); check whether segments correlate with sensitive groups before using them as model inputs.
- **Anomaly detection.** Unusual transaction patterns may indicate fraud rather than credit risk; consider flagging them separately rather than letting them distort the default model.

### Slide content we could not read

The .pptx versions of slides 3–7, 9–10, 12–19, 21, 24, 26–27 and 30 are images or diagrams. We read them from the PDF, so their content is described above. The worked k-means example on slide 18 gives only the data and the steps; the numerical working is ours. MNIST results promised in the learning objectives do not appear in the deck.
