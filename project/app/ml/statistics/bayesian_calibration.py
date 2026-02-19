#project/app/ml/statistics/bayesian_calibration.py
"""
modular bayesian calibration layer (phase 1)

Analytical conjugate priors only.
No sampling.
No MCMC.
Statistically grounded and extensible.
"""

from typing import Dict
import math


# -----------------------------
# Accuracy (Beta Posterior)
# -----------------------------

def beta_posterior(
    accuracy_mean: float,
    n: int,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
) -> Dict:
    """
    Compute Beta posterior for accuracy.
    """

    if n <= 0:
        return {
            "posterior_mean": accuracy_mean,
            "posterior_variance": 0.0,
            "credible_interval_95": (accuracy_mean, accuracy_mean),
        }

    successes = accuracy_mean * n
    failures = (1 - accuracy_mean) * n

    alpha = prior_alpha + successes
    beta = prior_beta + failures

    posterior_mean = alpha / (alpha + beta)
    posterior_variance = (
        alpha * beta
    ) / (((alpha + beta) ** 2) * (alpha + beta + 1))

    ci_lower = max(0.0, posterior_mean - 1.96 * math.sqrt(posterior_variance))
    ci_upper = min(1.0, posterior_mean + 1.96 * math.sqrt(posterior_variance))

    return {
        "posterior_mean": posterior_mean,
        "posterior_variance": posterior_variance,
        "credible_interval_95": (ci_lower, ci_upper),
    }


# -----------------------------
# Time / Continuous Signals
# -----------------------------

def normal_posterior(
    sample_mean: float,
    sample_variance: float,
    n: int,
    prior_mean: float = 0.0,
    prior_precision: float = 1.0,
) -> Dict:
    """
    Analytical normal posterior.
    """

    if n <= 0:
        return {
            "posterior_mean": sample_mean,
            "posterior_variance": 0.0,
            "credible_interval_95": (sample_mean, sample_mean),
        }

    posterior_mean = (
        (n * sample_mean + prior_precision * prior_mean)
        / (n + prior_precision)
    )

    posterior_variance = sample_variance / n if n > 0 else 0.0

    ci_lower = posterior_mean - 1.96 * math.sqrt(posterior_variance)
    ci_upper = posterior_mean + 1.96 * math.sqrt(posterior_variance)

    return {
        "posterior_mean": posterior_mean,
        "posterior_variance": posterior_variance,
        "credible_interval_95": (ci_lower, ci_upper),
    }


