from statistics import mean

PRIMITIVE = "constitutional_replication_engine"

DESCRIPTION = (
    "Non-clonal constitutional reconstruction and inheritance."
)

DEPENDENCIES = [
    "open_constitutional_transmission",
    "distributed_constitutional_memory",
    "constitutional_plasticity",
    "meta_constitutional_revision",
    "distributed_constitutional_propagation",
    "distributed_constitutional_alignment",
    "transgenerational_constitutional_continuity",
    "distributed_historical_mutation",
    "civilizational_semantic_drift",
    "trajectory_bifurcation",
    "historical_open_endedness",
    "anti_closure_metaconstraint",
    "invariant_propagation_monitor",
]


class ConstitutionalReplicationEngine:

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

        genealogical_continuity = (
            self._bounded(
                state.get(
                    "genealogical_continuity",
                    0.0,
                )
            )
        )

        successor_divergence = (
            self._bounded(
                state.get(
                    "successor_divergence",
                    0.0,
                )
            )
        )

        constitutional_mutability = (
            self._bounded(
                state.get(
                    "constitutional_mutability",
                    0.0,
                )
            )
        )

        semantic_reinterpretation = (
            self._bounded(
                state.get(
                    "semantic_reinterpretation",
                    0.0,
                )
            )
        )

        anti_clonal_capacity = (
            self._bounded(
                state.get(
                    "anti_clonal_capacity",
                    0.0,
                )
            )
        )

        distributed_propagation_stability = (
            self._bounded(
                state.get(
                    "distributed_propagation_stability",
                    0.0,
                )
            )
        )

        historical_open_endedness = (
            self._bounded(
                state.get(
                    "historical_open_endedness",
                    0.0,
                )
            )
        )

        replication_rigidity = (
            self._bounded(
                state.get(
                    "replication_rigidity",
                    0.0,
                )
            )
        )

        non_clonal_replication_viability = (
            self._bounded(
                (
                    genealogical_continuity
                    + successor_divergence
                    + constitutional_mutability
                    + semantic_reinterpretation
                    + anti_clonal_capacity
                    + distributed_propagation_stability
                    + historical_open_endedness
                    + (
                        1.0
                        - replication_rigidity
                    )
                ) / 8.0
            )
        )

        open_successor_generation = (
            self._bounded(
                (
                    successor_divergence
                    + semantic_reinterpretation
                    + anti_clonal_capacity
                    + constitutional_mutability
                ) / 4.0
            )
        )

        distributed_reconstruction_stability = (
            self._bounded(
                (
                    genealogical_continuity
                    + distributed_propagation_stability
                    + historical_open_endedness
                ) / 3.0
            )
        )

        clonal_convergence_risk = (
            self._bounded(
                (
                    replication_rigidity
                    + (
                        1.0
                        - successor_divergence
                    )
                    + (
                        1.0
                        - anti_clonal_capacity
                    )
                ) / 3.0
            )
        )

        constitutional_replication_engine_index = (
            self._bounded(
                mean(
                    [
                        non_clonal_replication_viability,
                        open_successor_generation,
                        distributed_reconstruction_stability,
                        (
                            1.0
                            - clonal_convergence_risk
                        ),
                    ]
                )
            )
        )

        constitutional_replication_engine_viable = (
            constitutional_replication_engine_index
            >= 0.60
            and clonal_convergence_risk <= 0.50
            and replication_rigidity <= 0.50
        )

        return {
            "non_clonal_replication_viability":
                round(
                    non_clonal_replication_viability,
                    4,
                ),
            "open_successor_generation":
                round(
                    open_successor_generation,
                    4,
                ),
            "distributed_reconstruction_stability":
                round(
                    distributed_reconstruction_stability,
                    4,
                ),
            "clonal_convergence_risk":
                round(
                    clonal_convergence_risk,
                    4,
                ),
            "constitutional_replication_engine_index":
                round(
                    constitutional_replication_engine_index,
                    4,
                ),
            "constitutional_replication_engine_viable":
                (
                    constitutional_replication_engine_viable
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
