# 07 ? Classification Technical Development Log

**Project:** MLE Group 1 ? Prosit 2
**Owner:** Germain
**Date:** 26 October 2026

## Ownership

- Germain: classification experiments, calibration,
  uncertainty, thresholds and technical evaluation.
- Joseph: shared features and validation infrastructure.
- Liza: cost matrix and underlying business assumptions.

## Checkpoint 7.0A?7.0C

Initial classification experiment setup and validation
work completed previously.

Exact numerical evidence remains in original artifacts.

## Checkpoint 7.1A?7.1C

Model comparison and validation strategy investigated.

## Checkpoint 7.2A

Calibration and class-imbalance comparisons completed.

Previously reported Brier scores:

- LR Platt: 0.01715
- RF Platt: 0.01699

## Checkpoint 7.2B

Customer-cluster bootstrap uncertainty evaluation.

- LR minus RF PR-AUC: +0.03035
- 95% interval: [+0.0150, +0.0482]
- 300 valid replicates

## Checkpoint 7.3A

Lending threshold scenarios evaluated on
54,463 observations.

Main thresholds:

- Kenya: 2.1%
- Ghana: 3.2%

Repeat-business thresholds:

- Kenya: 9.6%
- Ghana: 14.2%

## Checkpoint 7.3B.1

Verified repository, branch and experiment artifacts.

## Checkpoint 7.3B.2

Confirmed all 20 reported cost-per-loan divisions.

## Checkpoint 7.3B.3

Independently reconstructed all 20 saved cost totals.

Identified that Repeat business decision scenarios
were still evaluated with main cost assumptions.

Calculated separate repeat-business cost sensitivity.

## Checkpoint 7.3C

Prepared pooled OOF calibration diagnostics from
existing predictions without retraining.

These are descriptive calculations, not proof of
chronological calibration stability.

## Checkpoint 7.4

Consolidated saved classification evidence into
the classification notebook.

Notebook execution remains subject to verification.

## Decisions

Model discrimination, probability calibration,
cost-sensitive utility and temporal robustness
must be evaluated separately.

Neither candidate is approved for deployment.

## Pending

- Chronological validation audit
- Evaluation sample reconciliation
- Full notebook execution
- Assignment requirements verification
- ADR acceptance
- Git commit


## Checkpoint 7.6B ? Evaluation Population Reconciliation

Germain inspected Joseph's shared `add_folds()` and `splits()`
implementations without modifying them.

Processed training population: 68,464 observations.

- Block 0: 14,001 initial historical observations
- Block 1: 13,850 evaluation observations
- Block 2: 13,250 evaluation observations
- Block 3: 13,776 evaluation observations
- Block 4: 13,587 evaluation observations

Total evaluation population: 54,463 observations.

The temporal splitter trains on earlier blocks and requires
`outcome_known_at < evaluation_start`. This guards against
using outcomes unavailable at prediction time.

The OOF experiment produced predictions for 18 configurations,
with 54,463 unique loans per configuration and no duplicate
loan predictions within a configuration.

Fold 4 showed 533 defaults in 13,587 loans (3.92%), substantially
higher than preceding folds. Temporal drift and fold-level
calibration therefore remain important limitations.

Calibration fitting procedures still require provenance
verification for the Checkpoint 7.2 experiment.

No modification was made to Joseph's feature pipeline.


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
