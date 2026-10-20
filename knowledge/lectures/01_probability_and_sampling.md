# Lecture 1: Probability Distributions and Sampling for ML

> Study notes written in our own words from the "Lecture 1: Probability Distribution & Sampling for ML" deck (48 slides).
> Slide numbers refer to the original deck. The running example uses real data on insecticide-treated bed nets (ITNs) from the Ghana 2022 Demographic and Health Survey (DHS).

## What this lecture is about

This lecture lays the statistical foundation for the rest of the course. It answers two questions: **(1) What process produced the data?** (which probability distribution fits it, especially for counts and yes/no outcomes) and **(2) How much should we trust the numbers we compute from a sample?** (sampling distributions, standard errors, confidence intervals, the bootstrap, sampling design and sampling bias). Everything is illustrated with malaria and bed-net data from Ghana. The big lessons: choose a distribution from how the data were generated, check whether variance matches the mean for counts, remember that the Central Limit Theorem is about your estimator not your data, and that bias does not shrink with more data.

---

## 1. Where this fits and the motivating example (slides 2–4)

- Most models quietly assume some distribution; most numbers you report come from a sample (slide 2).
- Context (slide 3): malaria is a major public-health problem in Ghana (about 5.4 million cases in 2021, 4.3 million in 2024). Bed nets are distributed through mass campaigns, clinics and schools.
- The two guiding questions (slide 4):
  1. *What produced the data?* If you count rare events the shape will not be a bell curve. Fit the wrong distribution and both your estimates and your stated confidence are quietly wrong.
  2. *How much do we trust our numbers?* We never see the whole population, only a sample. A different sample gives a different answer.

---

## 2. Basic vocabulary (slides 5–7)

**Random variable $X$** (slide 5): a number describing the outcome of a process that varies. E.g. "how many nets does this household have?" or "does this household own a net at all (1/0)?"

| Term | Meaning |
|---|---|
| Realised value $x$ | the number we actually observe |
| Distribution | the rule giving the probability of each possible value |
| Parameter | the "knob" that shapes the distribution, e.g. $p, \lambda, \mu, \sigma$ |
| Support | the set of possible values (0, 1, 2, ... or any real number) |

**Discrete vs continuous** (slide 6):

- **Discrete**: outcomes can be counted (nets, patients). Described by a **probability mass function (PMF)** $p(x) = P(X = x)$. All probabilities add up to 1.
- **Continuous**: any value in a range (temperature, weight, waiting time). Described by a **density** $f(x)$. A density is *not* a probability: $P(X = \text{exactly one value}) = 0$; only intervals have probability (you integrate the density over the interval).
- Both have a **cumulative distribution function (CDF)** $F(x) = P(X \le x)$.
- Caution: a number with a decimal point may still be a count underneath (e.g. a rate per 1,000).

**Expectation and variance** (slide 7):

- **Expectation** $E[X]$: the long-run average, the balance point.
- **Variance** $\mathrm{Var}(X) = E\big[(X - E[X])^2\big]$: typical squared distance from the mean.
- **Standard deviation** $\mathrm{SD}(X) = \sqrt{\mathrm{Var}(X)}$: back in the original units.
- Some distributions tie the variance to the mean (Bernoulli, Binomial, Poisson). Real data often break that tie.

---

## 3. Discrete distributions (slides 8–21)

### 3.1 Bernoulli: a single yes/no (slides 9–11)

$X \sim \text{Bernoulli}(p)$: $X=1$ with probability $p$ ("success"), $X=0$ with probability $1-p$.

$$P(X = x) = p^x (1-p)^{1-x}, \quad x \in \{0,1\},\ 0<p<1$$

- Mean $= p$, variance $= p(1-p)$.
- Examples: sick/well, owns a net or not, a transaction succeeds or fails.
- Data: 70.96% of 17,933 households own at least one net, so $\hat p \approx 0.7096$.
- **Binary classification losses are built from this distribution** (slide 9). Taking $-\log$ of the PMF gives the log-loss / cross-entropy used in logistic regression.

### 3.2 Binomial: number of successes in $n$ trials (slide 12)

$X \sim \text{Bin}(n, p)$: $n$ independent trials, each with the same $p$; count the successes.

$$P(X = x) = \binom{n}{x} p^x (1-p)^{n-x}, \quad x = 0,1,\dots,n$$

- Mean $\mu = np$, variance $\sigma^2 = np(1-p)$.
- Variance is largest at $p = 0.5$ and shrinks as $p \to 0$ or $1$.
- Two assumptions carry everything: trials are **independent** and share **one** $p$. Break either and the Binomial *understates* how spread out real data are.

(The slide's PMF has a small typo, writing the exponent as $n-r$ instead of $n-x$.)

### 3.3 Other discrete distributions (slide 13)

| Distribution | Answers | Where you meet it |
|---|---|---|
| Geometric | how many failures before the first success? | time to first conversion, first case |
| Categorical / Multinomial | which of $k$ categories, repeatedly? | class labels, next-word prediction, dice |
| Hypergeometric | sampling *without* replacement | audits, quality control, small populations |

### 3.4 Poisson: counts of events in a window (slides 14–16)

$X \sim \text{Poisson}(\lambda)$, where $\lambda$ is the average rate per unit of exposure (per household, per month, ...).

$$P(X = x) = \frac{e^{-\lambda}\lambda^x}{x!}, \quad x = 0,1,2,\dots$$

- Defining property: **mean = variance = $\lambda$**.
- Conditions: events independent; constant rate across the window; no two events at exactly the same instant.
- Break any condition and counts become **over-dispersed** (variance > mean).
- As $\lambda$ grows the Poisson becomes more symmetric (slide 16 figure).

### 3.5 Over-dispersion (slides 17–19)

**Over-dispersion**: $\mathrm{Var}(X) > E[X]$. Real count data almost always show it.

Quick check: $\dfrac{\text{sample variance}}{\text{sample mean}}$. Near 1 → Poisson is plausible. Much bigger than 1 → over-dispersed.

Where does extra variation come from?

- **Clustering**: observations come in groups that share conditions.
- **Heterogeneity**: the underlying rate itself differs between units.

Fitting a Poisson anyway gives intervals that are **too narrow** and conclusions that are **over-confident**.

Examples:

- Nets per household (slide 18): mean 1.70, variance 2.59, ratio 1.53, i.e. variance about 53% above the mean. Poisson cannot produce that; Negative Binomial can.
- Monthly malaria-positive counts in 50 districts (slide 19): every district is far above the variance = mean line, because districts differ in population, transmission, environment and underlying rate.

### 3.6 Negative Binomial (slide 20)

Same kind of count data as Poisson, but the **rate is allowed to vary**. Two parameters: a mean and a **dispersion** parameter. As dispersion shrinks to zero, it converges back to the Poisson. It is the standard choice for real count data (insurance claims, hospital admissions, case counts). Practical advice: fit both; if the Negative Binomial wins clearly, that is evidence the rate genuinely varies.

The slide states it in the "number of failures before the $n$-th success" form: $X \sim NB(n, p)$ with $P(X = x) = \binom{x+n-1}{x} p^n (1-p)^x$ (the slide's typeset formula is garbled in extraction and appears to swap the roles of $p$ and $1-p$; the conventions differ between textbooks, so check which one your software uses).

### 3.7 Choosing a discrete distribution (slide 21)

| If the data is... | Use | Because |
|---|---|---|
| one yes/no per unit | Bernoulli | one trial, one probability |
| a count out of fixed $n$ | Binomial | $n$ independent trials sharing one $p$ |
| a count out of $n$, but $p$ wobbles | Beta-Binomial | the shared-$p$ assumption failed |
| count of events in a window | Poisson | rare independent events at constant rate |
| a count with variance > mean | Negative Binomial | allows over-dispersion |
| which of $k$ categories | Categorical / Multinomial | outcomes are labels, not counts |

---

## 4. Continuous distributions (slides 22–27)

### 4.1 Why they matter in ML (slide 23)

- Most ML inputs/outputs are *measured*, not counted.
- They give you the **likelihood**: how probable the data are under a model.
- They describe the **noise**: if $y = f(x) + \epsilon$, then $\epsilon$ is the part the model cannot explain, often assumed $\epsilon \sim N(0, \sigma^2)$.
- They explain why averages behave well (sums/means tend to normal).
- They provide **priors** and **regularisation** in probabilistic models.

### 4.2 Normal (Gaussian) (slides 24–25)

$X \sim N(\mu, \sigma)$ (mean $\mu$, standard deviation $\sigma$):

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$$

- Symmetric, bell-shaped, unbounded.
- About 68% of values within $1\sigma$ of the mean, about 95% within $2\sigma$.
- Why it is everywhere: measurement error is a sum of many small effects; the **Central Limit Theorem** makes averages roughly normal; and **linear regression with squared error is equivalent to assuming Gaussian noise** (minimising MSE = maximising the Gaussian likelihood).

### 4.3 Other continuous distributions (slides 25–26)

| Distribution | Shape | Typical use |
|---|---|---|
| Uniform | flat over an interval | "no preference", random initialisation |
| Exponential | positive, decaying | waiting time to the next event |
| Log-normal | positive, right-skewed | incomes, concentrations, durations |
| Beta | between 0 and 1 | probabilities, rates, proportions |

### 4.4 How distributions connect (slide 27)

- Poisson events in time → Exponential gaps between them.
- Binomial with varying $p$ → Beta-Binomial.
- Gamma is to the Exponential what the Negative Binomial is to the Poisson (lets the rate vary).
- General rule: **when one fixed parameter is not enough, put a distribution over that parameter.**

---

## 5. Sampling (slides 28–43)

### 5.1 Key words (slide 29)

| Term | Meaning (bed-net example) |
|---|---|
| Population | the full group of interest: all households in Ghana |
| Sample | the subset observed: 17,933 households |
| Parameter | a fact about the population: the true national ownership rate |
| Statistic | a number calculated from the sample: 70.96% |

We use the statistic to estimate the parameter, and must say how wrong it might be.

### 5.2 Sampling distribution and standard error (slides 30–31)

Imagine repeating the whole study with a fresh sample many times. Each run gives a different statistic, so the statistic has its own distribution: the **sampling distribution**. Its standard deviation is the **standard error (SE)**.

- SE measures **precision** (how repeatable the estimate is), **not correctness**. A small SE does not mean the sample was fair.
- Slide 31 shows malaria prevalence by region with 95% confidence intervals (whiskers).

### 5.3 Law of Large Numbers (slides 32–33)

The sample average converges to the population average as $n$ grows. It applies to whatever estimator you used, but it does **not** guarantee that:

- a biased estimator becomes unbiased,
- dependence between observations disappears,
- you converge to the quantity you *meant* to measure.

### 5.4 Central Limit Theorem (CLT) (slides 34–35)

The **mean** of a sample becomes approximately normal as $n$ grows, even if the data are not. Slide 34: nets per household are right-skewed, but the mean of 30 households over 5,000 samples is close to normal.

- The CLT is about the **estimator**, not the data.
- It needs independent observations, each with limited influence.
- Skewed or heavy-tailed data need a bigger $n$.
- It is why standard errors and t-tests work, and why averaged metrics are more dependable than single observations.

### 5.5 Sampling techniques (slides 36–37)

| Design | How | Trade-off |
|---|---|---|
| Simple random | every unit equally likely, drawn independently | clean theory, but costly to reach scattered units |
| Stratified | split population into groups (strata), sample each | more precise when groups differ; you must know the groups |
| Cluster | sample groups, measure everyone inside | cheap, but units in a cluster are **not independent** |

Slide 37: in the DHS, cluster sizes are similar by design, but net ownership per cluster ranges from about 20% to almost 100%. Households in the same cluster resemble each other.

### 5.6 Sampling weights (slides 38–39)

In stratified/cluster designs units are not drawn with equal probability. A **weight** is the number of population units each sampled unit stands for.

- *Weighted* estimates describe the **population**; *unweighted* estimates describe the **sample as drawn**.
- Here: 70.96% unweighted vs 66.77% weighted. Neither is an error; they answer different questions. Always say which you used.

### 5.7 Sampling bias (slide 40)

- **Selection bias**: the way you sample favours some units.
- **Coverage bias**: part of the population is not in the sampling frame (the list you sample from) at all.
- **Non-response bias**: people who don't respond differ from those who do.

**Bias does not shrink as the sample grows.** Averaging more of the wrong thing does not help. Always ask: *who is missing, and would they look different?* This is where **fairness** work starts: groups you never sampled are invisible in every metric you report.

### 5.8 Confidence intervals and the bootstrap (slides 41–42)

- A **confidence interval (CI)** is a range of plausible values for the parameter with a stated coverage (e.g. 95%).
- The **bootstrap** estimates that range by **resampling your own data with replacement** many times, recomputing the statistic each time, and reading off percentiles (e.g. 2.5th and 97.5th for a 95% CI). It works because resampling mimics the variability of drawing a fresh sample.
- **The catch: resampling must respect the design.** Resampling households independently assumes they are independent. If they came in clusters, **resample whole clusters**.

Slide 42 (2,000 resamples of household net ownership):

- *Naive bootstrap*: resamples households independently → narrow interval (falsely precise).
- *Cluster bootstrap*: resamples whole clusters, keeping within-cluster dependence → wider, honest interval. Design effect ≈ 4.2.

### 5.9 Design effect (slide 43)

$$\text{DEFF} = \frac{\text{variance under the actual design}}{\text{variance under simple random sampling}}$$

- $\text{DEFF} > 1$: your sample carries less information than its size suggests.
- **Effective sample size** $n_{\text{effective}} \approx \dfrac{n_{\text{raw}}}{\text{DEFF}}$.

Example: with DEFF ≈ 4.2, 17,933 households carry roughly the information of 17,933 / 4.2 ≈ 4,270 independent households.

---

## 6. Pitfalls and wrap-up (slides 44–46)

| Pitfall | What goes wrong | Do this instead |
|---|---|---|
| Poisson on over-dispersed counts | intervals too narrow, significance overstated | check variance vs mean; try Negative Binomial |
| Treating a density as a probability | nonsense probabilities | integrate over an interval |
| Ignoring the survey design | answer about the sample passed off as about the population | use weights and say so |
| Assuming independence inside clusters | standard errors too small | check the design effect |
| Trusting a big sample to fix bias | confidently wrong result | ask who is missing from the frame |

Seven take-aways (slide 45):

1. Choose the distribution from how the data were generated, not from convenience.
2. Always look at mean vs variance in count data.
3. Over-dispersion signals that some parameter varies.
4. The CLT is about your estimator, not your data.
5. Weights and design effects decide whether your number describes the population.
6. Bias does not shrink with sample size; precision is not correctness.
7. Write down your assumptions (distribution and design).

**Checkpoint questions** (slide 46) with the answers given in the speaker notes, paraphrased:

1. Daily admissions: mean 12, variance 41. Poisson? No: 41 ≫ 12, strongly over-dispersed; try Negative Binomial.
2. Survey: 30% ownership, 95% CI 29.4–30.6%, design = 200 villages × 15 households. Suspect? The interval was probably computed assuming independent households; clustering means it should be much wider.
3. Strongly skewed income averaged with a normal-based CI: acceptable only if the sample is large and well-behaved enough for the CLT to apply to the mean.
4. Model trained on two large referral hospitals: coverage/selection bias; rural clinics, other facilities and people who never reach referral hospitals are missing.

Reading suggested: *An Introduction to Statistical Learning* ch. 2 and *Hands-On ML* ch. 3 (slide 47).

---

## How this applies to Prosit 2

- **Default is a Bernoulli outcome.** Each loan is $y \in \{0,1\}$ with $P(y=1) = p(x)$. Logistic regression models $p(x)$ and is fitted by maximising the Bernoulli likelihood; the log-loss is $-\log$ of the Bernoulli PMF. This is the starting point of the required **logistic-regression MLE derivation**.
- **Base rate ≈ 1.83% is a sample statistic.** Report it with a CI. Because $p$ is small, variance $p(1-p)$ is small in absolute terms but the *relative* uncertainty of estimates involving defaults is large: with ~1.83% positives, the number of defaults (not the number of loans) is what limits precision.
- **Clustering = customers.** Multiple loans per customer are like households in a DHS cluster: not independent. That is exactly why we use **GroupKFold by customer** for validation, and why a **bootstrap CI on F1 / PR-AUC should resample customers (clusters), not individual loans**. A naive loan-level bootstrap would give an over-narrow "noise floor".
- **Bootstrap noise floor.** Before claiming model A beats model B, compute bootstrap (customer-cluster) CIs of the metric; if they overlap heavily, the difference is within noise.
- **Design effect thinking.** If many customers have many loans, the *effective* sample size is smaller than the row count. Mention this when interpreting CIs and fairness metrics for small subgroups.
- **Count features.** Features like "number of previous loans" or "number of late repayments" are counts, likely over-dispersed; log or rank transforms help linear models. If ever modelling counts as targets, prefer Negative Binomial over Poisson.
- **Loan amount is right-skewed (log-normal-like).** Model $\log(\text{amount})$ or use MAE/median-based metrics; normal-based CIs on raw amounts need large $n$.
- **Sampling bias and fairness.** Our Kenyan data only contain people who were *given* loans (a selection/coverage issue sometimes called "reject inference"). Groups rarely approved are almost invisible. State this in the fairness audit.
- **Kenya → Ghana shift.** Ghana is outside the Kenyan sampling frame: a textbook coverage problem. More Kenyan data will not fix it (bias doesn't shrink with $n$). Flag it, measure covariate shift where possible, and be explicit about assumptions.
- **Weighted vs unweighted.** If we reweight samples (e.g. class weights for imbalance or importance weights for shift), say so explicitly and report which numbers are weighted.
