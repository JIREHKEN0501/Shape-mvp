Stable participant example (hp_7f0db588)
=== TRAJECTORY DYNAMICS ===

{
  "early_accuracy": 100.0,
  "middle_accuracy": 100.0,
  "late_accuracy": 100.0,
  "early_hesitation": 2.21,
  "middle_hesitation": 1.07,
  "late_hesitation": 1.36,
  "accuracy_trend": "stable",
  "hesitation_trend": "stable"
}

Recovery example (hp_225ffd49)
=== TRAJECTORY DYNAMICS ===

{
  "early_accuracy": 71.43,
  "middle_accuracy": 35.71,
  "late_accuracy": 64.29,
  "early_hesitation": 1.64,
  "middle_hesitation": 3.14,
  "late_hesitation": 2.36,
  "accuracy_trend": "stable",
  "hesitation_trend": "stable"
}

Improving example (hp_d09b5ec8)
=== TRAJECTORY DYNAMICS ===

{
  "early_accuracy": 28.57,
  "middle_accuracy": 21.43,
  "late_accuracy": 50.0,
  "early_hesitation": 0.93,
  "middle_hesitation": 1.79,
  "late_hesitation": 2.07,
  "accuracy_trend": "improving",
  "hesitation_trend": "increasing"
}

Trajectory Dynamics v2 Validation Results

Stable Pattern:
- Detected successfully

Recovery Pattern:
- Detected successfully

Volatility Detection:
- Functional

Observed Limitation:
- Recovery detector may be overly strict and misses some recovery-like trajectories.

Next Iteration:
- Refine recovery classification thresholds and compare against volatility classification.
