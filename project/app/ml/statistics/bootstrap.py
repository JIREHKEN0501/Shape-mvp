import numpy as np
from typing import List, Tuple


def bootstrap_confidence_interval(
    values: List[float],
    n_resamples: int = 1000,
    confidence: float = 0.95,
    random_seed: int | None = 42,
) -> Tuple[float, float]:
    """
    Non-parametric bootstrap confidence interval for the mean.

    Args:
        values: list of numeric observations
        n_resamples: number of bootstrap samples
        confidence: confidence level (default 95%)
        random_seed: for deterministic testing

    Returns:
        (lower_bound, upper_bound)
    """

    if not values or len(values) < 2:
        if values:
            return (values[0], values[0])
        return (0.0, 0.0)

    if random_seed is not None:
        np.random.seed(random_seed)

    values_array = np.array(values)
    n = len(values_array)

    bootstrap_means = []

    for _ in range(n_resamples):
        sample = np.random.choice(values_array, size=n, replace=True)
        bootstrap_means.append(np.mean(sample))

    alpha = 1 - confidence
    lower = np.percentile(bootstrap_means, 100 * (alpha / 2))
    upper = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))

    return (float(lower), float(upper))
