# Results index

Every saved result, for the report and slides. Rule: [AGENTS.md](../AGENTS.md) rule 8. All files are in `tables/` or `figures/` unless a path is given.

Steps 1–4 (audit, cost matrix, data checks) have no tables: their results are in the notebooks' saved outputs (`notebooks/00_feature_audit`, `00b_cost_matrix`, `01_eda`) and in `learnings/03`, `04`.

## Step 5: features and fair tests ([learnings/05](05_features.md))
- `05_feature_comparison.csv`: clue sets compared
- `05_bootstrap.csv`: bootstrap ranges
- `05_grace_period.csv`: grace-period test
- `05_group_effects.csv`, `05_group_effects.png`: effect of keeping customers together
- `05_task1_check.csv`: clues checked on Task 1
- `05_default_rate_by_quarter.png`, `05_three_tests.png`: time drift, and the three validation tests

## Step 7: classification ([learnings/07](07_classification.md))
- `07_model_fold_metrics.csv`, `07_validation_comparison.csv`, `07_bootstrap_differences.csv`, `07_noise_floor_comparison.md`: models compared, and whether differences beat noise
- `07_lr_threshold_sweep.csv`, `07_operating_points.csv`, `07_approval_by_period.csv`, `07_cost_sensitivity_verified.csv`: cut-offs and costs
- `07_calibration_diagnostic.csv`, `07_reliability_curve.png`, `07_confusion_matrix.png`: calibration and errors
- `07_model_handover.md`: handover notes
- `07b_zindi_submissions.csv`: our three real Zindi scores, all from before the probe

## Step 8: reason codes ([learnings/08](08_reason_codes.md))
- `08_method.csv`, `08_grouping.csv`, `08_groups.csv`, `08_reference.csv`, `08_wording.csv`: options tested
- `08_stability.csv`: same top 3 reasons after a refit
- `08_final_calibration.csv`: the calibration fix

## Step 9: loan amounts ([learnings/09](09_regression.md))
- `09_models.csv`, `09_raw_vs_log.csv`, `09_back_transform.csv`, `09_currency.csv`, `09_settings.csv`, `09_bootstrap.csv`: options tested
- `09_limits.csv`: limit levels
- `09_residuals_by_group.csv`, `09_residuals.png`: errors by group

## Step 10: Kenya to Ghana ([learnings/10](10_transfer.md))
- `10_profile.csv`, `10_loan_types.csv`, `10_psi.csv`, `10_amounts_kenya_vs_ghana.png`: how the countries differ
- `10_domain_classifier.csv`, `10_weights.csv`: can Ghana be told apart; do weights help
- `10_amount_on_ghana.csv`, `10_amount_on_ghana_by_group.csv`: amount model on real Ghanaian amounts
- `10_default_model_on_ghana.csv`, `10_kenyan_standins.csv`, `10_sample_size.csv`: default model, stand-ins, labels needed

## Step 11: fairness ([learnings/11](11_fairness.md))
- `11_group_counts.csv`, `11_fairness_by_group.csv`, `11_fairness_intersections.csv`, `11_gaps.csv`, `11_calibration_by_group.csv`, `11_wrongly_declined.png`, `11_calibration_by_tenure.png`: the audit
- `11_proxies.csv`, `11_proxies_single_clue.csv`: can clues stand in for groups
- `11_mitigations.csv`, `11_mitigation_cost_change.csv`, `11_fairness_after.csv`: fixes tested
- `11_limit_by_group.csv`, `11_country_policies.csv`, `11_findex.csv`, `11_reasons_summary.csv`, `11_reasons_top.csv`: limits, countries, Findex, reasons

## Step 11b: 1,224 Kenyan scenarios (ADR 0020)
- `11b_grid.csv`, `11b_finalists.csv`, `11b_assumptions.csv`, `11b_launch.csv`: every scenario, the finalists, their assumptions, launch behaviour
- `11b_first_timers.csv`: measured repeat business

## Step 11b: Ghana evidence from Zindi (ADR 0021)
- `11b_ghana_probe.csv`, `11b_ghana_probe_2.csv`: raw scores of the 20 files
- `11b_ghana_rates.csv`, `11b_ghana_costs.csv`: first estimates from batch 1 (replaced by the exact counts below)
- `11b_ghana_exact.csv`: **use this:** exact defaults per group, with ranges
- `11b_ghana_segments.csv`: the six non-overlapping groups, with real amounts
- `11b_ghana_models.csv`: model rules and their costs
- `11b_ghana_policies.csv`: all 2,916 policy scenarios

## Step 11c: stress tests of ADR 0021
- `11c_ghana_verdict.csv`: the six rules, pass or fail
- `11c_ghana_parts.csv`: public against private, and picking on one part, testing on the other
- `11c_ghana_uncertainty.csv`: 5,000 draws of the rates
- `11c_ghana_assumptions.csv`, `11c_ghana_assumptions_summary.csv`: 2,880 assumption combinations, full and summarised
- `11c_ghana_real_amounts.csv`: on real amounts
- `11c_ghana_starter_default.csv`: if starters default more
- `11c_ghana_money.csv`: money lent, fees, losses per 1,000 applicants
- `11c_ghana_all_policies.csv`: the six rules applied to all 729 policies
- `11c_leaderboard_context.csv`: our scores against the leaderboard

## Step 12: scorer ([learnings/12](12_scorer.md))
- `12_tests.csv`: every scorer test, pass or fail
- `12_latency.csv`: timing over 1,000 calls, load time, file size
- `12_decisions_on_zindi_applicants.csv`, `12_refused_on_zindi_applicants.csv`: all 18,594 applicants through the scorer
- `12_unseen_loan_type.csv`: hiding each type from training, options compared
- `12_past_default_groups.csv`, `12_past_default_weights.csv`, `12_past_default_options.csv`, `12_past_default_zindi.csv`: past defaulters, the model's weights, rule options

## Other documents with results
`docs/model_card.md`, `docs/datasheet.md`, `docs/compliance.md`, `docs/adr/`.
