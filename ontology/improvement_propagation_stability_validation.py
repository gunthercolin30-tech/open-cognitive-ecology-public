
from statistics import mean

PRIMITIVE = "improvement_propagation_stability_validation"

class ImprovementPropagationStabilityValidation:

    def _b(self, value):
        return max(0.0, min(1.0, float(value)))

    def step(self, state=None):

        state = state or {}

        improvement_propagation_stability_index = self._b(
            state.get("improvement_propagation_stability_index", 0.95)
        )

        propagation_drift_index = self._b(
            state.get("propagation_drift_index", 0.05)
        )

        improvement_retention_persistence = self._b(
            state.get("improvement_retention_persistence", 0.95)
        )

        post_reconciliation_propagation_resilience = self._b(
            state.get(
                "post_reconciliation_propagation_resilience",
                0.95,
            )
        )

        civilizational_improvement_continuity = self._b(
            state.get("civilizational_improvement_continuity", 0.95)
        )

        distributed_improvement_stability_score = mean([
            improvement_propagation_stability_index,
            (1.0 - propagation_drift_index),
            improvement_retention_persistence,
            post_reconciliation_propagation_resilience,
            civilizational_improvement_continuity,
        ])

        return {
            "primitive": PRIMITIVE,
            "improvement_propagation_stability_index":
                round(improvement_propagation_stability_index, 4),
            "propagation_drift_index":
                round(propagation_drift_index, 4),
            "improvement_retention_persistence":
                round(improvement_retention_persistence, 4),
            "post_reconciliation_propagation_resilience":
                round(post_reconciliation_propagation_resilience, 4),
            "civilizational_improvement_continuity":
                round(civilizational_improvement_continuity, 4),
            "distributed_improvement_stability_score":
                round(distributed_improvement_stability_score, 4),
            "improvement_propagation_operational":
                distributed_improvement_stability_score >= 0.80,
        }
