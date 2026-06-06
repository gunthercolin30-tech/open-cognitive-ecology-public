
from statistics import mean

PRIMITIVE = "distributed_meta_adaptation_metrics_extraction"

class DistributedMetaAdaptationMetricsExtraction:

    def _b(self, value):
        return max(0.0, min(1.0, float(value)))

    def step(self,
             meta_adaptation_result=None,
             policy_adjustment_result=None,
             revision_ecology_result=None,
             open_governance_result=None,
             reflexive_governance_result=None):

        meta_adaptation_result = meta_adaptation_result or {}
        policy_adjustment_result = policy_adjustment_result or {}
        revision_ecology_result = revision_ecology_result or {}
        open_governance_result = open_governance_result or {}
        reflexive_governance_result = reflexive_governance_result or {}

        distributed_meta_adaptation_index = mean([
            self._b(meta_adaptation_result.get("meta_adaptive_potential", 0.90)),
            self._b(reflexive_governance_result.get("meta_policy_gain", 0.90)),
            self._b(reflexive_governance_result.get("effectiveness_score", 0.90))
        ])

        collective_policy_revision_capacity = mean([
            self._b(revision_ecology_result.get("revision_openness", 0.90)),
            self._b(revision_ecology_result.get("revision_pluralism", 0.90)),
            self._b(policy_adjustment_result.get("confidence", 0.90))
        ])

        distributed_revision_propagation = mean([
            self._b(revision_ecology_result.get("propagation_intensity", 0.90)),
            self._b(revision_ecology_result.get("reflexive_revision_ecology_index", 0.90)),
            self._b(open_governance_result.get("open_governance_index", 0.90))
        ])

        meta_governance_adaptation_index = mean([
            distributed_meta_adaptation_index,
            collective_policy_revision_capacity,
            distributed_revision_propagation,
            self._b(open_governance_result.get("anti_dogmatism_capacity", 0.90))
        ])

        distributed_meta_adaptation_viability = mean([
            distributed_meta_adaptation_index,
            collective_policy_revision_capacity,
            distributed_revision_propagation,
            meta_governance_adaptation_index
        ])

        return {
            "primitive": PRIMITIVE,
            "distributed_meta_adaptation_index": round(distributed_meta_adaptation_index, 4),
            "collective_policy_revision_capacity": round(collective_policy_revision_capacity, 4),
            "distributed_revision_propagation": round(distributed_revision_propagation, 4),
            "meta_governance_adaptation_index": round(meta_governance_adaptation_index, 4),
            "distributed_meta_adaptation_viability": round(distributed_meta_adaptation_viability, 4),
            "distributed_meta_adaptation_validated": distributed_meta_adaptation_viability >= 0.80
        }
