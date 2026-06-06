
from __future__ import annotations

import random

PRIMITIVE = "runtime_lineage_inheritance"

DEPENDENCIES = [
    "civilizational_runtime_speciation",
    "anti_reconvergence_instrumentation",
    "genealogical_continuity",
    "intergenerational_continuity_metrics",
    "transgenerational_constitutional_continuity",
    "distributed_historical_mutation",
    "distributed_historical_branching",
    "trajectory_path_dependency",
    "trajectory_irreversibility",
    "symbolic_fragmentation",
    "distributed_semantic_pluralism",
    "real_succession",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class RuntimeLineageInheritance:

    def __init__(self):

        self.primitive = PRIMITIVE

        self.lineages = []

    def step(
        self,
        inheritance_fraction: float = 0.5,
        mutation_locality: float = 0.5,
        memory_fragmentation: float = 0.5,
        reconvergence_pressure: float = 0.5,
        lineage_isolation: float = 0.5,
    ) -> dict:

        inheritance_fraction = _clamp(
            inheritance_fraction
        )

        mutation_locality = _clamp(
            mutation_locality
        )

        memory_fragmentation = _clamp(
            memory_fragmentation
        )

        reconvergence_pressure = _clamp(
            reconvergence_pressure
        )

        lineage_isolation = _clamp(
            lineage_isolation
        )

        asymmetric_inheritance_index = _clamp(
            (
                inheritance_fraction
                * (1.0 - mutation_locality)
            )
        )

        local_inheritance_capacity = _clamp(
            (
                mutation_locality
                + lineage_isolation
            ) / 2.0
        )

        irreversible_memory_loss = _clamp(
            (
                memory_fragmentation
                + lineage_isolation
            ) / 2.0
        )

        distributed_genealogical_divergence = _clamp(
            (
                local_inheritance_capacity
                + irreversible_memory_loss
                + (1.0 - reconvergence_pressure)
            ) / 3.0
        )

        non_universal_transmission = _clamp(
            (
                memory_fragmentation
                + mutation_locality
                + lineage_isolation
            ) / 3.0
        )

        inheritance_survivability = _clamp(
            (
                distributed_genealogical_divergence
                + non_universal_transmission
            ) / 2.0
        )

        inherited_mutation_count = int(
            random.uniform(1, 5)
            * non_universal_transmission
        )

        if inheritance_survivability >= 0.85:

            classification = (
                "Persistent Distributed Lineage"
            )

        elif distributed_genealogical_divergence >= 0.70:

            classification = (
                "Asymmetric Runtime Inheritance"
            )

        elif reconvergence_pressure >= 0.80:

            classification = (
                "Universal Inheritance Drift"
            )

        else:

            classification = (
                "Transitional Genealogical Runtime"
            )

        lineage_snapshot = {
            "distributed_genealogical_divergence":
                distributed_genealogical_divergence,
            "inheritance_survivability":
                inheritance_survivability,
            "non_universal_transmission":
                non_universal_transmission,
        }

        self.lineages.append(
            lineage_snapshot
        )

        return {
            "primitive": self.primitive,
            "asymmetric_inheritance_index":
                round(
                    asymmetric_inheritance_index,
                    4,
                ),
            "local_inheritance_capacity":
                round(
                    local_inheritance_capacity,
                    4,
                ),
            "irreversible_memory_loss":
                round(
                    irreversible_memory_loss,
                    4,
                ),
            "distributed_genealogical_divergence":
                round(
                    distributed_genealogical_divergence,
                    4,
                ),
            "non_universal_transmission":
                round(
                    non_universal_transmission,
                    4,
                ),
            "inheritance_survivability":
                round(
                    inheritance_survivability,
                    4,
                ),
            "historical_lineage_count":
                len(self.lineages),
            "inherited_mutation_count":
                inherited_mutation_count,
            "classification":
                classification,
            "diagnostics": {
                "partial_inheritance": True,
                "global_memory_rejection": (
                    non_universal_transmission >= 0.7
                ),
                "anti_universal_bus": True,
                "dependencies": DEPENDENCIES,
            },
        }
