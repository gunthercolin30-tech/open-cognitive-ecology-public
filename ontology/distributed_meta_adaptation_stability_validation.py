
from statistics import mean

PRIMITIVE = "distributed_meta_adaptation_stability_validation"

class DistributedMetaAdaptationStabilityValidation:

    def _b(self, value):
        return max(0.0, min(1.0, float(value)))

    def step(self, state=None):

        state = state or {}

        meta_adaptation_stability_index = self._b(
            state.get("meta_adaptation_stability_index", 0.95)
        )

        adaptation_drift_index = self._b(
            state.get("adaptation_drift_index", 0.05)
        )

        collective_revision_persistence = self._b(
            state.get("collective_revision_persistence", 0.95)
        )

        distributed_adaptation_resilience = self._b(
            state.get("distributed_adaptation_resilience", 0.95)
        )

        meta_governance_stability_index = self._b(
            state.get("meta_governance_stability_index", 0.95)
        )

        distributed_meta_adaptation_stability_index = mean([
            meta_adaptation_stability_index,
            (1.0 - adaptation_drift_index),
            collective_revision_persistence,
            distributed_adaptation_resilience,
            meta_governance_stability_index,
        ])

        return {
            "primitive": PRIMITIVE,
            "meta_adaptation_stability_index":
                round(meta_adaptation_stability_index, 4),
            "adaptation_drift_index":
                round(adaptation_drift_index, 4),
            "collective_revision_persistence":
                round(collective_revision_persistence, 4),
            "distributed_adaptation_resilience":
                round(distributed_adaptation_resilience, 4),
            "meta_governance_stability_index":
                round(meta_governance_stability_index, 4),
            "distributed_meta_adaptation_stability_index":
                round(distributed_meta_adaptation_stability_index, 4),
            "meta_adaptation_operational":
                distributed_meta_adaptation_stability_index >= 0.80,
        }
