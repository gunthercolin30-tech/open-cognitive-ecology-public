
from __future__ import annotations

from statistics import mean

PRIMITIVE = "ontology_topology_governance"

DEPENDENCIES = [
    "dependency_registry",
    "hierarchical_registry",
    "semantic_field",
    "civilizational_semantic_drift",
    "adaptive_symbolic_pruning",
    "attractor_desaturation",
    "architectural_non_closure_index",
    "openness_preservation_supervisor",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class OntologyTopologyGovernance:

    def __init__(self):
        self.primitive = PRIMITIVE

    def _dependency_density(self):
        from ontology.dependency_registry import (
            DEPENDENCY_REGISTRY,
        )

        if not DEPENDENCY_REGISTRY:
            return 0.0

        dependency_sizes = [
            len(v)
            for v in DEPENDENCY_REGISTRY.values()
        ]

        return _bounded(
            mean(dependency_sizes) / 10.0
        )

    def _hierarchical_convergence(self):
        from ontology.hierarchical_registry import (
            HIERARCHICAL_LEVELS,
        )

        if not HIERARCHICAL_LEVELS:
            return 0.0

        levels = list(
            HIERARCHICAL_LEVELS.values()
        )

        max_level = max(levels)

        if max_level <= 0:
            return 0.0

        return _bounded(
            mean(levels) / max_level
        )

    def step(
        self,
        simulated_closure_pressure: float = 0.0,
        simulated_density: float = 0.0,
    ):

        dependency_density = (
            self._dependency_density()
        )

        hierarchical_convergence = (
            self._hierarchical_convergence()
        )

        semantic_density = _bounded(
            (
                dependency_density
                + hierarchical_convergence
                + simulated_density
            ) / 3.0
        )

        closure_pressure = _bounded(
            (
                semantic_density
                + simulated_closure_pressure
            ) / 2.0
        )

        attractor_rigidity = _bounded(
            closure_pressure
            * semantic_density
        )

        topological_openness = _bounded(
            1.0
            - closure_pressure
        )

        distributed_stability = _bounded(
            (
                topological_openness
                + (1.0 - attractor_rigidity)
            ) / 2.0
        )

        closure_pressure_detected = (
            closure_pressure >= 0.70
        )

        future_openness_preserved = (
            distributed_stability >= 0.70
        )

        return {
            "primitive": PRIMITIVE,
            "topological_governance_active": True,
            "dependency_density":
                round(
                    dependency_density,
                    4,
                ),
            "hierarchical_convergence":
                round(
                    hierarchical_convergence,
                    4,
                ),
            "semantic_density":
                round(
                    semantic_density,
                    4,
                ),
            "closure_pressure":
                round(
                    closure_pressure,
                    4,
                ),
            "attractor_rigidity":
                round(
                    attractor_rigidity,
                    4,
                ),
            "topological_openness":
                round(
                    topological_openness,
                    4,
                ),
            "distributed_stability":
                round(
                    distributed_stability,
                    4,
                ),
            "closure_pressure_detected":
                closure_pressure_detected,
            "future_openness_preserved":
                future_openness_preserved,
        }


if __name__ == "__main__":

    engine = OntologyTopologyGovernance()

    print(
        engine.step()
    )
