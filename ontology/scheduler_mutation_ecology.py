
from __future__ import annotations

import random

PRIMITIVE = "scheduler_mutation_ecology"

DEPENDENCIES = [
    "runtime_lineage_inheritance",
    "civilizational_runtime_speciation",
    "anti_reconvergence_instrumentation",
    "distributed_scheduler_ecology",
    "meta_scheduler_fragmentation_governance",
    "runtime_scheduler_pluralization",
    "distributed_historical_mutation",
    "evolutionary_drift",
    "evolutionary_diversification",
    "trajectory_regime",
    "regime_emergence",
    "distributed_population_runtime",
    "non_convergent_intelligence_dynamics",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class SchedulerMutationEcology:

    def __init__(self):

        self.primitive = PRIMITIVE

        self.scheduler_lineages = []

    def step(
        self,
        scheduler_mutation_rate: float = 0.5,
        ecological_diversification: float = 0.5,
        scheduler_dominance_pressure: float = 0.5,
        mutation_locality: float = 0.5,
        orchestration_fragmentation: float = 0.5,
    ) -> dict:

        scheduler_mutation_rate = _clamp(
            scheduler_mutation_rate
        )

        ecological_diversification = _clamp(
            ecological_diversification
        )

        scheduler_dominance_pressure = _clamp(
            scheduler_dominance_pressure
        )

        mutation_locality = _clamp(
            mutation_locality
        )

        orchestration_fragmentation = _clamp(
            orchestration_fragmentation
        )

        scheduler_speciation_index = _clamp(
            (
                scheduler_mutation_rate
                + ecological_diversification
                + orchestration_fragmentation
            ) / 3.0
        )

        orchestration_diversity = _clamp(
            (
                ecological_diversification
                + mutation_locality
            ) / 2.0
        )

        scheduler_recanonicalization_risk = _clamp(
            (
                scheduler_dominance_pressure
                + (1.0 - orchestration_fragmentation)
            ) / 2.0
        )

        orchestration_irreversibility = _clamp(
            (
                scheduler_speciation_index
                + mutation_locality
                + (1.0 - scheduler_dominance_pressure)
            ) / 3.0
        )

        ecological_scheduler_viability = _clamp(
            (
                orchestration_diversity
                + orchestration_irreversibility
            ) / 2.0
        )

        dominant_scheduler_fatigue = _clamp(
            (
                scheduler_dominance_pressure
                * orchestration_fragmentation
            )
        )

        emergent_scheduler_count = int(
            random.uniform(2, 8)
            * ecological_diversification
        )

        extinct_scheduler_count = int(
            random.uniform(0, 3)
            * scheduler_dominance_pressure
        )

        if ecological_scheduler_viability >= 0.85:

            classification = (
                "Persistent Evolutionary Scheduler Ecology"
            )

        elif scheduler_recanonicalization_risk >= 0.80:

            classification = (
                "Scheduler Canonicalization Drift"
            )

        elif orchestration_irreversibility >= 0.70:

            classification = (
                "Distributed Divergent Orchestration"
            )

        else:

            classification = (
                "Transitional Scheduler Ecology"
            )

        scheduler_snapshot = {
            "scheduler_speciation_index":
                scheduler_speciation_index,
            "ecological_scheduler_viability":
                ecological_scheduler_viability,
            "scheduler_recanonicalization_risk":
                scheduler_recanonicalization_risk,
        }

        self.scheduler_lineages.append(
            scheduler_snapshot
        )

        return {
            "primitive": self.primitive,
            "scheduler_speciation_index":
                round(
                    scheduler_speciation_index,
                    4,
                ),
            "orchestration_diversity":
                round(
                    orchestration_diversity,
                    4,
                ),
            "scheduler_recanonicalization_risk":
                round(
                    scheduler_recanonicalization_risk,
                    4,
                ),
            "orchestration_irreversibility":
                round(
                    orchestration_irreversibility,
                    4,
                ),
            "ecological_scheduler_viability":
                round(
                    ecological_scheduler_viability,
                    4,
                ),
            "dominant_scheduler_fatigue":
                round(
                    dominant_scheduler_fatigue,
                    4,
                ),
            "emergent_scheduler_count":
                emergent_scheduler_count,
            "extinct_scheduler_count":
                extinct_scheduler_count,
            "scheduler_lineage_count":
                len(self.scheduler_lineages),
            "classification":
                classification,
            "diagnostics": {
                "anti_scheduler_centralization": True,
                "evolutionary_scheduler_ecology": True,
                "persistent_orchestration_divergence":
                    (
                        orchestration_irreversibility
                        >= 0.70
                    ),
                "dependencies": DEPENDENCIES,
            },
        }
