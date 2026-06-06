
from statistics import mean

PRIMITIVE = "distributed_governance_metrics_extraction"

class DistributedGovernanceMetricsExtraction:

    def _b(self, v):
        return max(0.0, min(1.0, float(v)))

    def step(self,
             distributed_runtime_result=None,
             council_result=None,
             constitutional_result=None,
             reflexive_result=None,
             asynchronous_result=None):

        distributed_runtime_result = distributed_runtime_result or {}
        council_result = council_result or {}
        constitutional_result = constitutional_result or {}
        reflexive_result = reflexive_result or {}
        asynchronous_result = asynchronous_result or {}

        governance_coherence = mean([
            self._b(distributed_runtime_result.get("consensus_stability", 0.90)),
            self._b(distributed_runtime_result.get("synchronization_quality", 0.90)),
            self._b(constitutional_result.get("constitutional_governance_score", 0.90)),
        ])

        decision_consistency = mean([
            self._b(council_result.get("consensus", 1.0)),
            self._b(reflexive_result.get("governance_activation_score", 0.90)),
            self._b(reflexive_result.get("effectiveness_score", 0.90)),
        ])

        inter_node_alignment = mean([
            self._b(distributed_runtime_result.get("node_health", 0.90)),
            self._b(asynchronous_result.get("distributed_alignment", 0.90)),
            self._b(distributed_runtime_result.get("replication_integrity", 0.90)),
        ])

        fragmentation_resistance = mean([
            governance_coherence,
            inter_node_alignment,
            self._b(distributed_runtime_result.get("failover_readiness", 0.90)),
        ])

        distributed_governance_viability = mean([
            governance_coherence,
            decision_consistency,
            inter_node_alignment,
            fragmentation_resistance,
        ])

        return {
            "primitive": PRIMITIVE,
            "distributed_governance_coherence_index":
                round(governance_coherence, 4),
            "distributed_decision_consistency_index":
                round(decision_consistency, 4),
            "inter_node_governance_alignment":
                round(inter_node_alignment, 4),
            "governance_fragmentation_resistance":
                round(fragmentation_resistance, 4),
            "distributed_governance_viability":
                round(distributed_governance_viability, 4),
            "distributed_governance_validated":
                distributed_governance_viability >= 0.80,
        }
