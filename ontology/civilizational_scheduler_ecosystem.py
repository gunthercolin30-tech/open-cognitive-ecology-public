
from __future__ import annotations

import random

PRIMITIVE = "civilizational_scheduler_ecosystem"

DEPENDENCIES = [
    "scheduler_mutation_ecology",
    "runtime_lineage_inheritance",
    "civilizational_runtime_speciation",
    "anti_reconvergence_instrumentation",
    "distributed_scheduler_ecology",
    "meta_scheduler_fragmentation_governance",
    "distributed_population_runtime",
    "distributed_runtime_coordination",
    "ecological_niche_construction",
    "adaptive_ecological_regulation_engine",
    "ecological_decay",
    "ecological_fatigue_analyzer",
    "selective_pressure",
    "coevolutionary_dynamics",
    "social_ecological_resilience",
    "distributed_open_ended_pluralistic_evolution",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class CivilizationalSchedulerEcosystem:

    def __init__(self):

        self.primitive = PRIMITIVE

        self.scheduler_ecosystems = []

    def step(
        self,
        ecological_diversity: float = 0.5,
        scheduler_competition: float = 0.5,
        scheduler_cooperation: float = 0.5,
        dominance_saturation: float = 0.5,
        niche_fragmentation: float = 0.5,
    ) -> dict:

        ecological_diversity = _clamp(
            ecological_diversity
        )

        scheduler_competition = _clamp(
            scheduler_competition
        )

        scheduler_cooperation = _clamp(
            scheduler_cooperation
        )

        dominance_saturation = _clamp(
            dominance_saturation
        )

        niche_fragmentation = _clamp(
            niche_fragmentation
        )

        scheduler_niche_diversity = _clamp(
            (
                ecological_diversity
                + niche_fragmentation
            ) / 2.0
        )

        coevolutionary_scheduler_pressure = _clamp(
            (
                scheduler_competition
                + scheduler_cooperation
            ) / 2.0
        )

        ecological_metastability = _clamp(
            (
                scheduler_niche_diversity
                + (1.0 - dominance_saturation)
                + scheduler_cooperation
            ) / 3.0
        )

        scheduler_ecological_resilience = _clamp(
            (
                ecological_metastability
                + scheduler_niche_diversity
            ) / 2.0
        )

        ecosystem_recanonicalization_risk = _clamp(
            (
                dominance_saturation
                + (1.0 - niche_fragmentation)
            ) / 2.0
        )

        ecosystem_open_endedness = _clamp(
            (
                scheduler_niche_diversity
                + coevolutionary_scheduler_pressure
                + (1.0 - ecosystem_recanonicalization_risk)
            ) / 3.0
        )

        emergent_niche_count = int(
            random.uniform(2, 10)
            * ecological_diversity
        )

        extinct_scheduler_species = int(
            random.uniform(0, 4)
            * dominance_saturation
        )

        cooperative_scheduler_clusters = int(
            random.uniform(1, 6)
            * scheduler_cooperation
        )

        if ecosystem_open_endedness >= 0.85:

            classification = (
                "Persistent Open Scheduler Civilization"
            )

        elif ecosystem_recanonicalization_risk >= 0.80:

            classification = (
                "Scheduler Ecosystem Collapse Risk"
            )

        elif ecological_metastability >= 0.70:

            classification = (
                "Distributed Coevolutionary Scheduler Ecology"
            )

        else:

            classification = (
                "Transitional Scheduler Ecosystem"
            )

        ecosystem_snapshot = {
            "scheduler_niche_diversity":
                scheduler_niche_diversity,
            "ecological_metastability":
                ecological_metastability,
            "ecosystem_open_endedness":
                ecosystem_open_endedness,
        }

        self.scheduler_ecosystems.append(
            ecosystem_snapshot
        )

        return {
            "primitive": self.primitive,
            "scheduler_niche_diversity":
                round(
                    scheduler_niche_diversity,
                    4,
                ),
            "coevolutionary_scheduler_pressure":
                round(
                    coevolutionary_scheduler_pressure,
                    4,
                ),
            "ecological_metastability":
                round(
                    ecological_metastability,
                    4,
                ),
            "scheduler_ecological_resilience":
                round(
                    scheduler_ecological_resilience,
                    4,
                ),
            "ecosystem_recanonicalization_risk":
                round(
                    ecosystem_recanonicalization_risk,
                    4,
                ),
            "ecosystem_open_endedness":
                round(
                    ecosystem_open_endedness,
                    4,
                ),
            "emergent_niche_count":
                emergent_niche_count,
            "extinct_scheduler_species":
                extinct_scheduler_species,
            "cooperative_scheduler_clusters":
                cooperative_scheduler_clusters,
            "ecosystem_history_length":
                len(self.scheduler_ecosystems),
            "classification":
                classification,
            "diagnostics": {
                "anti_ecosystem_centralization": True,
                "coevolutionary_scheduler_ecology": True,
                "persistent_open_scheduler_ecology":
                    (
                        ecosystem_open_endedness
                        >= 0.85
                    ),
                "dependencies": DEPENDENCIES,
            },
        }
