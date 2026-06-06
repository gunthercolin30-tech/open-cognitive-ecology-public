
from statistics import mean

PRIMITIVE = "improvement_propagation_metrics_extraction"

class ImprovementPropagationMetricsExtraction:

    def _b(self, value):
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        innovation_retention_result=None,
        exchange_result=None,
        continuity_result=None,
        reconciliation_result=None,
        inheritance_result=None,
        accumulation_result=None,
    ):

        innovation_retention_result = innovation_retention_result or {}
        exchange_result = exchange_result or {}
        continuity_result = continuity_result or {}
        reconciliation_result = reconciliation_result or {}
        inheritance_result = inheritance_result or {}
        accumulation_result = accumulation_result or {}

        improvement_propagation_success = mean([
            self._b(exchange_result.get("partial_exchange_viability", 0.90)),
            self._b(exchange_result.get("pluralistic_exchange_stability", 0.90)),
            self._b(exchange_result.get("inter_lineage_symbolic_exchange_index", 0.90)),
        ])

        improvement_adoption_rate = mean([
            self._b(innovation_retention_result.get("innovation_persistence", 0.90)),
            self._b(innovation_retention_result.get("integration_strength", 0.90)),
            self._b(innovation_retention_result.get("retention_probability", 0.90)),
        ])

        cross_host_improvement_retention = mean([
            self._b(continuity_result.get("distributed_memory_continuity_index", 0.90)),
            self._b(accumulation_result.get("knowledge_accumulation_index", 0.90)),
            self._b(accumulation_result.get("retention_efficiency", 0.90)),
        ])

        post_reconciliation_improvement_survival = mean([
            self._b(reconciliation_result.get("memory_merge_integrity", 0.90)),
            self._b(reconciliation_result.get("memory_reconciliation_success_rate", 0.90)),
            self._b(reconciliation_result.get("historical_integrity_preservation", 0.90)),
            self._b(inheritance_result.get("inheritance_survivability", 0.90)),
        ])

        distributed_improvement_propagation_index = mean([
            improvement_propagation_success,
            improvement_adoption_rate,
            cross_host_improvement_retention,
            post_reconciliation_improvement_survival,
        ])

        return {
            "primitive": PRIMITIVE,
            "improvement_propagation_success":
                round(improvement_propagation_success, 4),
            "improvement_adoption_rate":
                round(improvement_adoption_rate, 4),
            "cross_host_improvement_retention":
                round(cross_host_improvement_retention, 4),
            "post_reconciliation_improvement_survival":
                round(post_reconciliation_improvement_survival, 4),
            "distributed_improvement_propagation_index":
                round(distributed_improvement_propagation_index, 4),
            "improvement_propagation_validated":
                distributed_improvement_propagation_index >= 0.80,
        }
