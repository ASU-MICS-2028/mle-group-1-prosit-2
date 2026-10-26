# ADR Draft ? Classification Model Selection

**Date:** 26 October 2026
**Owner:** Germain
**Status:** Proposed, not accepted

## Context

NkwaPay loan-default classification requires
probability estimates and lending decisions under
asymmetric error costs.

## Alternatives

1. Logistic Regression with Platt calibration
2. Random Forest with Platt calibration

## Evidence

Customer-cluster bootstrap results favor LR
on PR-AUC.

RF has slightly lower observed cost under the
main country thresholds.

LR has lower observed costs in several
approval-constrained scenarios.

Cost assumptions are partly hypothetical,
especially for repeat-business opportunity costs.

## Proposed Decision

Retain both calibrated candidates pending
additional checks.

Do not authorize a production lending threshold.

## Consequences

Final selection must consider:

- PR-AUC and uncertainty
- Probability calibration
- Lending cost assumptions
- Approval constraints
- Temporal stability
- Fairness and country transfer limitations

## Outstanding Questions

Why were 54,463 loans evaluated instead of
all 68,464 processed training records?

Has the proposed model been assessed on a
genuinely independent temporal holdout?

Are probabilities reliable around the chosen
decision thresholds?


## Final methodological limitations

The shared temporal splitter was inspected and uses
only earlier blocks with outcomes known before each
evaluation period.

However, the exact fitting provenance for all 18
Checkpoint 7.2 calibration configurations has not
been independently verified.

The pooled OOF diagnostics are descriptive; they do
not establish chronological calibration stability.

The final model comparison remains experimental.
Neither LR nor RF is authorized for production
deployment.

Further work should independently verify calibration
fit boundaries, prospective performance, fairness,
and the assumed business cost matrix.
