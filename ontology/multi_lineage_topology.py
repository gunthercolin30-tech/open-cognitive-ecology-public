
from statistics import mean

PRIMITIVE = "multi_lineage_topology"

DESCRIPTION = (
    "Multi lineage topology."
)

DEPENDENCIES = [
    "ontological_attractor_mapping",
    "trajectory_bifurcation",
    "attractor_basin",
    "structural_attractor",
    "meta_trajectory_navigation",
    "possible_worlds_navigation",
    "non_convergent_intelligence_dynamics",
    "trajectory_metastability",
    "distributed_attractor_speciation",
    "inter_lineage_symbolic_exchange",
]


class MultiLineageTopology:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(self, state=None):

        state = state or {}

        lineage_diversity = self._bounded(
            state.get(
                "lineage_diversity",
                0.0,
            )
        )

        attractor_dispersion = self._bounded(
            state.get(
                "attractor_dispersion",
                0.0,
            )
        )

        corridor_stability = self._bounded(
            state.get(
                "corridor_stability",
                0.0,
            )
        )

        topological_navigation_openness = (
            self._bounded(
                state.get(
                    "topological_navigation_openness",
                    0.0,
                )
            )
        )

        metastability = self._bounded(
            state.get(
                "trajectory_metastability",
                0.0,
            )
        )

        exchange_viability = self._bounded(
            state.get(
                "inter_lineage_symbolic_exchange_index",
                0.0,
            )
        )

        convergence_pressure = self._bounded(
            state.get(
                "convergence_pressure",
                0.0,
            )
        )

        basin_separation_index = self._bounded(
            (
                lineage_diversity
                + attractor_dispersion
                + (
                    1.0 - convergence_pressure
                )
            ) / 3.0
        )

        corridor_navigation_capacity = (
            self._bounded(
                (
                    corridor_stability
                    + topological_navigation_openness
                    + exchange_viability
                ) / 3.0
            )
        )

        ecological_topology_resilience = (
            self._bounded(
                (
                    basin_separation_index
                    + metastability
                    + corridor_navigation_capacity
                ) / 3.0
            )
        )

        pluralistic_topology_stability = (
            self._bounded(
                (
                    ecological_topology_resilience
                    + (
                        1.0 - convergence_pressure
                    )
                    + lineage_diversity
                ) / 3.0
            )
        )

        multi_lineage_topology_index = (
            self._bounded(
                mean(
                    [
                        basin_separation_index,
                        corridor_navigation_capacity,
                        ecological_topology_resilience,
                        pluralistic_topology_stability,
                    ]
                )
            )
        )

        if (
            multi_lineage_topology_index
            >= 0.90
        ):

            classification = (
                "fully_structured_pluralistic_topology"
            )

        elif (
            multi_lineage_topology_index
            >= 0.70
        ):

            classification = (
                "stable_multi_lineage_topology"
            )

        elif (
            multi_lineage_topology_index
            >= 0.50
        ):

            classification = (
                "fragile_multi_lineage_topology"
            )

        else:

            classification = (
                "topological_collapse_risk"
            )

        return {
            "basin_separation_index":
                round(
                    basin_separation_index,
                    4,
                ),
            "corridor_navigation_capacity":
                round(
                    corridor_navigation_capacity,
                    4,
                ),
            "ecological_topology_resilience":
                round(
                    ecological_topology_resilience,
                    4,
                ),
            "pluralistic_topology_stability":
                round(
                    pluralistic_topology_stability,
                    4,
                ),
            "multi_lineage_topology_index":
                round(
                    multi_lineage_topology_index,
                    4,
                ),
            "classification":
                classification,
            "multi_lineage_viable":
                (
                    multi_lineage_topology_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
