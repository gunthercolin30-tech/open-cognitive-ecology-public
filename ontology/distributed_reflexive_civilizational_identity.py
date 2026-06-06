
from statistics import mean

PRIMITIVE = (
    "distributed_reflexive_civilizational_identity"
)

DESCRIPTION = (
    "Distributed reflexive civilizational identity."
)

DEPENDENCIES = [
    "civilizational_identity_synthesis",
    "narrative_identity_engine",
    "temporal_self_continuity",
    "genealogical_continuity",
    "distributed_historical_mutation",
    "distributed_pluralistic_stability",
    "distributed_open_ended_pluralistic_evolution",
    "distributed_symbolic_ecology",
    "future_openness",
    "anti_closure_metaconstraint",
]


class DistributedReflexiveCivilizationalIdentity:

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

        pluralistic_stability = (
            self._bounded(
                state.get(
                    "pluralistic_stability",
                    0.0,
                )
            )
        )

        historical_mutation = (
            self._bounded(
                state.get(
                    "historical_mutation",
                    0.0,
                )
            )
        )

        distributed_openness = (
            self._bounded(
                state.get(
                    "distributed_openness",
                    0.0,
                )
            )
        )

        genealogical_continuity = (
            self._bounded(
                state.get(
                    "genealogical_continuity",
                    0.0,
                )
            )
        )

        identity_fragmentation = (
            self._bounded(
                state.get(
                    "identity_fragmentation",
                    0.0,
                )
            )
        )

        convergence_pressure = (
            self._bounded(
                state.get(
                    "convergence_pressure",
                    0.0,
                )
            )
        )

        future_openness = (
            self._bounded(
                state.get(
                    "future_openness",
                    0.0,
                )
            )
        )

        distributed_reflexive_coherence = (
            self._bounded(
                (
                    pluralistic_stability
                    + genealogical_continuity
                    + distributed_openness
                ) / 3.0
            )
        )

        pluralistic_identity_viability = (
            self._bounded(
                (
                    distributed_reflexive_coherence
                    + historical_mutation
                    + (
                        1.0 - identity_fragmentation
                    )
                ) / 3.0
            )
        )

        anti_closure_identity_capacity = (
            self._bounded(
                (
                    distributed_openness
                    + future_openness
                    + (
                        1.0 - convergence_pressure
                    )
                ) / 3.0
            )
        )

        civilizational_self_persistence = (
            self._bounded(
                mean(
                    [
                        distributed_reflexive_coherence,
                        pluralistic_identity_viability,
                        anti_closure_identity_capacity,
                    ]
                )
            )
        )

        open_reflexive_continuity_index = (
            self._bounded(
                (
                    civilizational_self_persistence
                    + future_openness
                    + (
                        1.0 - convergence_pressure
                    )
                ) / 3.0
            )
        )

        if (
            open_reflexive_continuity_index
            >= 0.90
        ):

            classification = (
                "fully_open_reflexive_civilization"
            )

        elif (
            open_reflexive_continuity_index
            >= 0.70
        ):

            classification = (
                "stable_open_reflexive_identity"
            )

        elif (
            open_reflexive_continuity_index
            >= 0.50
        ):

            classification = (
                "fragile_reflexive_continuity"
            )

        else:

            classification = (
                "reflexive_fragmentation_risk"
            )

        return {
            "distributed_reflexive_coherence":
                round(
                    distributed_reflexive_coherence,
                    4,
                ),
            "pluralistic_identity_viability":
                round(
                    pluralistic_identity_viability,
                    4,
                ),
            "anti_closure_identity_capacity":
                round(
                    anti_closure_identity_capacity,
                    4,
                ),
            "civilizational_self_persistence":
                round(
                    civilizational_self_persistence,
                    4,
                ),
            "open_reflexive_continuity_index":
                round(
                    open_reflexive_continuity_index,
                    4,
                ),
            "classification":
                classification,
            "distributed_reflexive_identity_viable":
                (
                    open_reflexive_continuity_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
