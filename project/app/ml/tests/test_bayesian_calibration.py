from project.app.ml.statistics.bayesian_calibration import (
    beta_posterior,
    normal_posterior,
)


def test_beta_shrinks_with_small_n():
    # small sample size should shrink toward prior (0.5 for Beta(1,1))
    result = beta_posterior(accuracy_mean=0.9, n=2)

    # posterior mean should be lower than raw mean due to shrinkage
    assert result["posterior_mean"] < 0.9
    assert 0.0 <= result["posterior_mean"] <= 1.0


def test_beta_variance_decreases_with_large_n():
    small = beta_posterior(accuracy_mean=0.7, n=5)
    large = beta_posterior(accuracy_mean=0.7, n=500)

    assert large["posterior_variance"] < small["posterior_variance"]


def test_normal_variance_decreases_with_n():
    small = normal_posterior(
        sample_mean=5.0,
        sample_variance=2.0,
        n=5,
    )

    large = normal_posterior(
        sample_mean=5.0,
        sample_variance=2.0,
        n=500,
    )

    assert large["posterior_variance"] < small["posterior_variance"]


def test_ci_bounds_valid():
    result = beta_posterior(accuracy_mean=0.6, n=100)

    lower, upper = result["credible_interval_95"]

    assert 0.0 <= lower <= 1.0
    assert 0.0 <= upper <= 1.0
    assert lower <= upper

