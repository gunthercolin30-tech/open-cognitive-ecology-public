
from __future__ import annotations

import random

PRIMITIVE = (
    "post_fragmentation_civilizational_ecology"
)

DEPENDENCIES = [
    "civilizational_scheduler_ecosystem",
    "scheduler_mutation_ecology",
    "runtime_lineage_inheritance",
    "civilizational_runtime_speciation",
    "network_fragmentation_resilience",
    "distributed_historical_branching",
    "symbolic_fragmentation",
    "real_multi_machine_historical_divergence",
    "distributed_semantic_pluralism",
    "distributed_population_runtime",
    "distributed_runtime_coordination",
    "asynchronous_civilizational_governance",
    "distributed_meta_stability",
    "social_ecological_resilience",
    "anti_reconvergence_instrumentation",
]


def _clamp(value: float) -> float:

    return max(
        0.0,
        min(
            1.0,
            float(value),
        ),
    )


class PostFragmentationCivilizationalEcology:

    def __init__(self):

        self.primitive = PRIMITIVE

        self.fragmented_ecologies = []

    def step(
        self,
        fragmentation_persistence: float = 0.5,
        post_reconnection_divergence: float = 0.5,
        local_governance_stability: float = 0.5,
        reunification_pressure: float = 0.5,
        historical_incompatibility: float = 0.5,
    ) -> dict:

        fragmentation_persistence = _clamp(
            fragmentation_persistence
        )

        post_reconnection_divergence = _clamp(
            post_reconnection_divergence
        )

        local_governance_stability = _clamp(
            local_governance_stability
        )

        reunification_pressure = _clamp(
            reunification_pressure
        )

        historical_incompatibility = _clamp(
            historical_incompatibility
        )

        post_fragmentation_viability = _clamp(
            (
                fragmentation_persistence
                + local_governance_stability
                + historical_incompatibility
            ) / 3.0
        )

        divergence_after_reconnection = _clamp(
            (
                post_reconnection_divergence
                + historical_incompatibility
            ) / 2.0
        )

        ecological_separation_resilience = _clamp(
            (
                post_fragmentation_viability
                + (1.0 - reunification_pressure)
            ) / 2.0
        )

        civilization_reunification_risk = _clamp(
            (
                reunification_pressure
                + (1.0 - historical_incompatibility)
            ) / 2.0
        )

        distributed_historical_hysteresis = _clamp(
            (
                fragmentation_persistence
                + post_reconnection_divergence
                + historical_incompatibility
            ) / 3.0
        )

        open_fragmented_ecology_index = _clamp(
            (
                ecological_separation_resilience
                + distributed_historical_hysteresis
                + (1.0 - civilization_reunification_risk)
            ) / 3.0
        )

        fragmented_civilization_count = int(
            random.uniform(2, 9)
            * fragmentation_persistence
        )

        irreversible_divergence_clusters = int(
            random.uniform(1, 6)
            * historical_incompatibility
        )

        forced_reunification_failures = int(
            random.uniform(0, 4)
            * (1.0 - reunification_pressure)
        )

        if open_fragmented_ecology_index >= 0.85:

            classification = (
                "Persistent Post-Fragmentation Civilization"
            )

        elif civilization_reunification_risk >= 0.80:

            classification = (
                "Civilizational Reunification Drift"
            )

        elif distributed_historical_hysteresis >= 0.70:

            classification = (
                "Irreversible Distributed Civilization Divergence"
            )

        else:

            classification = (
                "Transitional Fragmented Civilization"
            )

        ecology_snapshot = {
            "post_fragmentation_viability":
                post_fragmentation_viability,
            "distributed_historical_hysteresis":
                distributed_historical_hysteresis,
            "open_fragmented_ecology_index":
                open_fragmented_ecology_index,
        }

        self.fragmented_ecologies.append(
            ecology_snapshot
        )

        return {
            "primitive": self.primitive,
            "post_fragmentation_viability":
                round(
                    post_fragmentation_viability,
                    4,
                ),
            "divergence_after_reconnection":
                round(
                    divergence_after_reconnection,
                    4,
                ),
            "ecological_separation_resilience":
                round(
                    ecological_separation_resilience,
                    4,
                ),
            "civilization_reunification_risk":
                round(
                    civilization_reunification_risk,
                    4,
                ),
            "distributed_historical_hysteresis":
                round(
                    distributed_historical_hysteresis,
                    4,
                ),
            "open_fragmented_ecology_index":
                round(
                    open_fragmented_ecology_index,
                    4,
                ),
            "fragmented_civilization_count":
                fragmented_civilization_count,
            "irreversible_divergence_clusters":
                irreversible_divergence_clusters,
            "forced_reunification_failures":
                forced_reunification_failures,
            "fragmented_ecology_history_length":
                len(self.fragmented_ecologies),
            "classification":
                classification,
            "diagnostics": {
                "anti_global_reunification": True,
                "persistent_fragmented_ecology":
                    (
                        open_fragmented_ecology_index
                        >= 0.85
                    ),
                "historical_hysteresis_active":
                    (
                        distributed_historical_hysteresis
                        >= 0.70
                    ),
                "dependencies": DEPENDENCIES,
            },
        }
