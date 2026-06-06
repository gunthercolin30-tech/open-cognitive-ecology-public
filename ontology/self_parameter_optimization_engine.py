
"""
self_parameter_optimization_engine.py

Explores candidate parameter configurations and selects the best one
according to performance scores.
"""

from datetime import datetime


class SelfParameterOptimizationEngine:
    """Automatic internal parameter optimization."""

    def __init__(self):
        self.optimization_counter = 0

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))

    def step(self, inputs):
        self.optimization_counter += 1

        parameter_space = inputs.get(
            "parameter_space",
            {
                "learning_rate": [0.05, 0.1, 0.2],
                "exploration_weight": [0.2, 0.5, 0.8],
            },
        )

        candidate_configurations = inputs.get("candidate_configurations")
        if not candidate_configurations:
            candidate_configurations = [
                {
                    key: values[0] if isinstance(values, list) and values else values
                    for key, values in parameter_space.items()
                }
            ]

        performance_scores = inputs.get(
            "performance_scores",
            [0.8 + 0.02 * i for i in range(len(candidate_configurations))]
        )

        if len(performance_scores) < len(candidate_configurations):
            last = performance_scores[-1] if performance_scores else 0.0
            performance_scores = performance_scores + [last] * (
                len(candidate_configurations) - len(performance_scores)
            )

        best_index = max(
            range(len(candidate_configurations)),
            key=lambda i: performance_scores[i]
        )

        selected_configuration = candidate_configurations[best_index]
        best_score = self._clamp(performance_scores[best_index])
        baseline_score = self._clamp(performance_scores[0])

        optimization_gain = max(0.0, best_score - baseline_score)
        parameter_stability_index = best_score

        optimization_trace = {
            "optimization_id": f"SPOE-{self.optimization_counter:04d}",
            "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "candidate_count": len(candidate_configurations),
            "best_index": best_index,
        }

        return {
            "primitive": "SELF_PARAMETER_OPTIMIZATION_ENGINE",
            "parameter_space": parameter_space,
            "candidate_configurations": candidate_configurations,
            "performance_scores": performance_scores,
            "selected_configuration": selected_configuration,
            "optimization_gain": optimization_gain,
            "optimization_trace": optimization_trace,
            "parameter_stability_index": parameter_stability_index,
        }
