
from __future__ import annotations

PRIMITIVE = "civilizational_runtime_speciation"

DEPENDENCIES = [
    "anti_reconvergence_instrumentation",
    "distributed_historical_mutation",
    "distributed_historical_branching",
    "trajectory_irreversibility",
    "trajectory_bifurcation",
    "distributed_population_runtime",
    "multi_history_runtime",
    "multi_lineage_topology",
    "non_convergent_intelligence_dynamics",
    "distributed_attractor_speciation",
    "symbolic_fragmentation",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class CivilizationalRuntimeSpeciation:

    def __init__(self):

        self.primitive = PRIMITIVE

        self.lineages = []

    def step(
        self,
        runtime_divergence: float = 0.5,
        scheduler_mutation: float = 0.5,
        symbolic_incompatibility: float = 0.5,
        historical_branching: float = 0.5,
        reconvergence_pressure: float = 0.5,
    ) -> dict:

        runtime_divergence = _clamp(
            runtime_divergence
        )

        scheduler_mutation = _clamp(
            scheduler_mutation
        )

        symbolic_incompatibility = _clamp(
            symbolic_incompatibility
        )

        historical_branching = _clamp(
            historical_branching
        )

        reconvergence_pressure = _clamp(
            reconvergence_pressure
        )

        lineage_divergence_index = _clamp(
            (
                runtime_divergence
                + scheduler_mutation
                + historical_branching
            ) / 3.0
        )

        runtime_speciation_index = _clamp(
            (
                lineage_divergence_index
                + symbolic_incompatibility
            ) / 2.0
        )

        irreversibility_pressure = _clamp(
            (
                symbolic_incompatibility
                + historical_branching
            ) / 2.0
        )

        reunification_resistance = _clamp(
            (
                runtime_speciation_index
                + irreversibility_pressure
                + (1.0 - reconvergence_pressure)
            ) / 3.0
        )

        lineage_survivability = _clamp(
            (
                runtime_divergence
                + historical_branching
                + reunification_resistance
            ) / 3.0
        )

        if runtime_speciation_index >= 0.85:
            classification = (
                "Persistent Runtime Speciation"
            )

        elif reunification_resistance >= 0.70:
            classification = (
                "Distributed Divergent Civilization"
            )

        elif reconvergence_pressure >= 0.75:
            classification = (
                "Reconvergence Dominated Runtime"
            )

        else:
            classification = (
                "Transitional Runtime Divergence"
            )

        lineage_snapshot = {
            "runtime_speciation_index":
                runtime_speciation_index,
            "reunification_resistance":
                reunification_resistance,
            "lineage_survivability":
                lineage_survivability,
        }

        self.lineages.append(
            lineage_snapshot
        )

        return {
            "primitive": self.primitive,
            "lineage_divergence_index":
                round(
                    lineage_divergence_index,
                    4,
                ),
            "runtime_speciation_index":
                round(
                    runtime_speciation_index,
                    4,
                ),
            "irreversibility_pressure":
                round(
                    irreversibility_pressure,
                    4,
                ),
            "reunification_resistance":
                round(
                    reunification_resistance,
                    4,
                ),
            "lineage_survivability":
                round(
                    lineage_survivability,
                    4,
                ),
            "historical_lineage_count":
                len(self.lineages),
            "classification":
                classification,
            "diagnostics": {
                "anti_recanonicalization": True,
                "persistent_divergence": (
                    reunification_resistance >= 0.7
                ),
                "dependencies": DEPENDENCIES,
            },
        }
