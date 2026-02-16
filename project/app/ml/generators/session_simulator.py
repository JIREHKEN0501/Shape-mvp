import numpy as np
from typing import Dict, List


class SyntheticSessionSimulator:
    """
    Statistically grounded synthetic session generator.
    Designed for stress-testing ML aggregation and difficulty estimation.
    """

    def __init__(
        self,
        base_time: float = 4.0,
        discrimination: float = 1.2,
        cognitive_load: float = 1.0,
        beta_concentration: float = 20.0,
    ):
        self.base_time = base_time
        self.discrimination = discrimination
        self.cognitive_load = cognitive_load
        self.beta_concentration = beta_concentration

    @staticmethod
    def _sigmoid(x):
        return 1 / (1 + np.exp(-x))

    def _sample_ability(self):
        return np.random.normal(0, 1)

    def _assign_strategy(self):
        r = np.random.rand()
        if r < 0.3:
            return "careful"
        elif r < 0.8:
            return "balanced"
        return "impulsive"

    def _strategy_modifiers(self, strategy):
        if strategy == "careful":
            return {"accuracy_boost": 0.1, "time_multiplier": 1.3}
        if strategy == "impulsive":
            return {"accuracy_boost": -0.1, "time_multiplier": 0.7}
        return {"accuracy_boost": 0.0, "time_multiplier": 1.0}

    def simulate_session(self, task_metadata: Dict) -> Dict:
        """
        Simulate one session.
        """

        declared_difficulty = task_metadata["declared_difficulty"]

        ability = self._sample_ability()
        strategy = self._assign_strategy()
        mods = self._strategy_modifiers(strategy)

        # Accuracy modeling
        base_prob = self._sigmoid(
            self.discrimination * (ability - declared_difficulty)
        )

        adjusted_prob = np.clip(base_prob + mods["accuracy_boost"], 0.01, 0.99)

        alpha = adjusted_prob * self.beta_concentration
        beta = (1 - adjusted_prob) * self.beta_concentration

        accuracy_sample = np.random.beta(alpha, beta)

        # Response time modeling
        ability_inverse = np.maximum(0.1, 1 - base_prob)
        mean_time = (
            self.base_time
            + declared_difficulty * 4
            + ability_inverse * 3
        )

        log_time = np.random.lognormal(
            mean=np.log(mean_time),
            sigma=0.4 * self.cognitive_load,
        )

        response_time = log_time * mods["time_multiplier"]

        return {
            "accuracy": float(accuracy_sample),
            "response_time": float(response_time),
            "strategy": strategy,
            "ability": float(ability),
        }

    def simulate_cohort(
        self,
        task_metadata: Dict,
        num_sessions: int = 1000,
    ) -> List[Dict]:

        return [
            self.simulate_session(task_metadata)
            for _ in range(num_sessions)
        ]

# ------------------------------------------------------------
# Public wrapper function (used by tests and integration layer)
# ------------------------------------------------------------

def simulate_sessions(
    n_sessions: int = 1000,
    true_difficulty: float = 0.5,
    variance: float = 0.1,
    time_mean: float = 4.0,
    time_std: float = 1.0,
) -> List[Dict]:
    """
    Parametric synthetic cohort generator for ML stress testing.

    This function provides a stable public interface expected by tests.
    Internally maps parameters into simulator configuration.
    """

    simulator = SyntheticSessionSimulator(
        base_time=time_mean,
        discrimination=1.2,
        cognitive_load=time_std,
        beta_concentration=20.0 / max(variance, 0.01),
    )

    task_metadata = {
        "declared_difficulty": true_difficulty
    }

    return simulator.simulate_cohort(
        task_metadata=task_metadata,
        num_sessions=n_sessions,
    )
