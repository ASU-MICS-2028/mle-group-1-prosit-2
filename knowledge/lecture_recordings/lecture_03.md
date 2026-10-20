# Lecture 3: Probability Distributions and Sampling

> Summary of an audio recording of the lecture. The full transcript is not published. Speech-to-text was imperfect, so check important details against the slide notes in `../lectures/`.

The recording did not capture a title slide. The title above describes the content.

## Recording summary

### Flow summary
A lecture on probability distributions (Bernoulli, binomial, Poisson, negative binomial, normal), using malaria and treated-net data as examples, plus a brief intro to sampling techniques.

### Framing: distributions and random variables
- Malaria in Ghana used as the running example; about 4.3M cases in 2024
- Two guiding questions: what produced the data (distribution), and how much to trust estimates (sampling)
- A random variable quantifies the outcome of interest; a distribution gives the probability of each value; parameters shape it

### Discrete distributions
- Discrete uses a PMF, continuous uses a PDF; density gives probability over an interval, not a point
- Bernoulli for a single binary event; binomial for N independent trials with a shared P
    - Mean = NP, variance = NP(1-P); assumptions: independence and constant P
- Poisson counts events in a window; mean = variance = lambda; large lambda approaches a normal shape
- Over-dispersion (variance/mean well above 1) breaks Poisson; use negative binomial instead
    - Nets-per-household example: mean 1.70, variance 2.59, ratio about 1.59

### Continuous distributions and sampling
- Normal: symmetric bell, about 68% within 1 SD, about 95% within 2 SD; used in BECE-style grade curving
- Uniform for equal probabilities, exponential for waiting times; log-normal and beta also mentioned
- Sampling techniques: random, stratified (pick from every group), cluster/PSU (pick a subset of groups)

### Next steps
- Cover data purposes briefly next session, then use the rest of the session for prosit work
- Wrap up the prosit the following week and start the machine learning module

## Our summary

### Why distributions and sampling
The lecture used malaria in Ghana (about 4.3 million cases in 2024) and data on treated mosquito nets as the running example. It was framed around two questions:
1. **What produced the data?** That is the distribution: the shape a histogram of the data would take. The lecturer said a fitted distribution is itself a model, comparable to a linear regression. You fit the data to it and then make inferences and estimates from it, such as "20% of people in the north had malaria this year".
2. **How much should we trust the numbers we compute?** That is sampling: how the data was collected decides how much confidence the estimates deserve.

### Core vocabulary
- **Random variable** (uppercase, e.g. X): a number that measures an outcome of interest, e.g. "number of heads in 10 tosses" or "number of nets in a household". A lowercase x is the realised (observed) value. In the lecturer's words, the random variable is the question and x is the answer.
- **Distribution**: the rule that gives the probability of each possible value.
- **Parameter**: a number that sets the shape of a distribution (p = probability of success, lambda = rate, mean, standard deviation). The lecturer compared this to hyperparameters in ML.
- **Discrete vs continuous**: discrete outcomes can be counted (nets, patients, cases) and are described by a **PMF**, which gives probabilities. Continuous outcomes such as temperature, weight, blood pressure or waiting time are described by a **PDF**, which gives densities. For continuous data only intervals have probabilities: P(X = exactly some value) = 0. A student asked how to choose the interval. The lecturer said there is no standard and that it depends on the domain (e.g. the known fever threshold for temperature).
- **Expectation** = the long-run average (mean). **Variance** = spread around the mean. Deviations are squared so that positive and negative deviations do not cancel out.

### Discrete distributions
- **Bernoulli(p)**: one trial with two outcomes. Mean p, variance p(1-p). Examples: sick/well, household owns a net or not, transaction succeeds/fails. In the net data about 70.96% of households own at least one net, so p ≈ 0.71 and 1-p ≈ 0.29. A later slide was read as 0.79, which is probably a transcription error.
- **Binomial(n, p)**: the number of successes in n trials. Mean np, variance np(1-p). It needs two assumptions: the trials are **independent** (each one is fresh) and they **share the same p**. The event stays the same (the question "does this household have a net?"). Only the number of trials changes. The example used 30 households (the dataset had 17,930). Changing n or p changes the shape. To get "at least k" probabilities you can use the complement (1 - P(...)). If the outcome you care about is the "negative" one, simply define it as the success.
- **Geometric**: the number of failures before the first success. The example was resitting an exam until you pass.
- **Poisson(lambda)**: counts of events in a **window** of time or area, e.g. malaria cases per day at a health centre. lambda is the average rate per unit of exposure. **Mean = variance = lambda.** Assumptions: events are independent, the rate is constant across the window, and two events cannot happen at the same instant. PMF: e^(-lambda) lambda^x / x!. With lambda = 1 the mass piles up at low counts: P(0) ≈ 0.37, P(1) ≈ 0.37, P(2) ≈ 0.18, P(3) ≈ 0.06. The spoken numbers were garbled, but these are the standard values. As lambda grows (e.g. 5 in the rainy season, then larger) the shape moves toward a bell (normal) curve.
- **Over-dispersion**: when variance > mean. Quick check: the variance/mean ratio. If it is about 1, Poisson is fine. If it is much greater than 1, the data is over-dispersed. Causes: **clustering**, where observations come in groups that share traits, and **heterogeneous rates**, where different units have different underlying rates. You can still fit a Poisson to over-dispersed data, but the **intervals come out too narrow and the conclusions are overconfident**. Worked example: nets per household had mean 1.70 and variance 2.59. The lecturer quoted the ratio as 1.59, but 2.59/1.70 ≈ 1.52 and the slide figure should be checked. A Poisson fitted to this data visibly mismatched the histogram.
- **Negative binomial**: the count model for over-dispersed data, because it allows the rate to vary. It has a dispersion parameter linked to the mean and variance. The lecturer did not give the formula. Typical uses: insurance claims, hospital admissions, malaria case counts. Suggested practice: fit both Poisson and negative binomial and compare them.
- **Choosing a distribution** (slide guide):
  - single yes/no → Bernoulli
  - count out of a fixed n → binomial (beta-binomial if p varies between units)
  - count of events in a window → Poisson
  - count with variance above the mean → negative binomial
  - one of K categories → categorical/multinomial

### Continuous distributions
- **Uniform**: flat; every value is equally likely, as in random initialisation.
- **Normal / Gaussian (mu, sigma)**: symmetric, bell-shaped and unbounded. About 68% of values fall within 1 SD and about 95% within 2 SD. The example was BECE-style grading on a curve, where fixed percentages get each grade (roughly the top 4% get grade 1, from memory). A score of 89 can therefore get a lower grade if the top slice is filled by scores of 90.
- **Exponential**: waiting times, e.g. how long until a trotro or train arrives.
- **Log-normal and beta** were only mentioned.

### Sampling (brief)
- **Simple random sampling**: the baseline.
- **Stratified sampling**: split the population into groups (strata) and sample from **every** group so each one is represented.
- **Cluster sampling / PSUs** (the transcript renders this as "pasta"): split the population into groups and then select a **subset of the groups**, e.g. 10 of 20, as the sample.
- **Post-stratification** was named as part of the course concepts but not explained. The lecturer suggested the prosit dataset involves stratified sampling.

### What the lecturer said about the prosits
- Prosit 1 asks you to do a **mean-variance check before choosing a distribution**. The lecturer called this "the first check you have to do": if the mean and variance are about equal, fit a Poisson with lambda = the mean. If the variance is much larger (over-dispersion), use a negative binomial. Fitting a Poisson anyway gives overconfident (too-narrow) intervals.
- At the Prosit 1 presentations the lecturer plans to ask how the computed values would have differed **without** fitting a distribution, i.e. why a fitted model gives better estimates than describing the raw data. Be ready to answer that.
- The lecturer noted that the prosit data probably involves stratified sampling, which affects how much the estimates can be trusted.
- Plan: one more short data topic next session, then time to finish the prosit. The prosit wraps up the following week and the ML module begins.

### Relevance to Prosit 2
- **Clustering breaks independence.** Correlated observations from the same cluster are the same idea that motivates **GroupKFold** for Prosit 2. If borrowers repeat or share groups, random splits underestimate uncertainty and overstate performance.
- **Avoid overconfident intervals.** Fitting a model whose assumptions fail gives intervals that are too narrow. Our **bootstrap CIs** should resample at the right unit (e.g. per group, not per row) for the same reason.
- **Bernoulli/binomial is the model behind default.** Default is a Bernoulli outcome, and the base rate p is small because the data is **imbalanced**. Calibration checks whether predicted p matches observed frequencies.
- **Skewed loan amounts.** Loan amounts are positive and right-skewed, so log-normal is a natural reference for the **regression** target (consider a log transform).
- **Sampling design sets transferability.** Stratified vs cluster sampling decides how far estimates carry over. **Kenya → Ghana shift** is a population that was never sampled, so treat Ghana estimates with caution.
- **Fairness audit.** Per-group metrics in the fairness audit are only as reliable as each group's sample size, so stratification matters.
