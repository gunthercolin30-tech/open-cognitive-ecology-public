
from statistics import mean


PRIMITIVE = (
    "reflexive_identity_hysteresis"
)

DESCRIPTION = (
    "Distributed reflexive hysteresis under cumulative perturbations."
)

DEPENDENCIES = [
    "trajectory_hysteresis",
    "trajectory_persistence",
    "civilizational_state_persistence",
    "dialogue_memory_persistence",
    "distributed_meta_stability",
    "ecological_decay",
    "ecological_fatigue_analyzer",
    "attractor_persistence_analyzer",
    "critical_transitions",
    "semantic_collapse",
    "refined_long_duration_civilizational_resilience",
]


class ReflexiveIdentityHysteresis:

    def __init__(self):

        self.cumulative_memory = 0.0
        self.historical_scars = 0.0

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

        historical_stress = self._bounded(
            state.get(
                "historical_stress",
                0.0,
            )
        )

        fragmentation_pressure = self._bounded(
            state.get(
                "fragmentation_pressure",
                0.0,
            )
        )

        semantic_decay = self._bounded(
            state.get(
                "semantic_decay",
                0.0,
            )
        )

        recovery_capacity = self._bounded(
            state.get(
                "recovery_capacity",
                0.0,
            )
        )

        fatigue_accumulation = self._bounded(
            state.get(
                "fatigue_accumulation",
                0.0,
            )
        )

        attractor_persistence = self._bounded(
            state.get(
                "attractor_persistence",
                0.0,
            )
        )

        distributed_meta_stability = self._bounded(
            state.get(
                "distributed_meta_stability",
                0.0,
            )
        )

        perturbation_pressure = (
            self._bounded(
                mean(
                    [
                        historical_stress,
                        fragmentation_pressure,
                        semantic_decay,
                        fatigue_accumulation,
                    ]
                )
            )
        )

        hysteresis_memory = (
            self._bounded(
                (
                    self.cumulative_memory * 0.7
                )
                + (
                    perturbation_pressure * 0.3
                )
            )
        )

        self.cumulative_memory = (
            hysteresis_memory
        )

        historical_scarring = (
            self._bounded(
                (
                    self.historical_scars * 0.8
                )
                + (
                    perturbation_pressure * 0.2
                )
            )
        )

        self.historical_scars = (
            historical_scarring
        )

        adaptive_recovery = (
            self._bounded(
                recovery_capacity
                * (
                    1.0
                    - historical_scarring
                )
            )
        )

        reflexive_continuity = (
            self._bounded(
                mean(
                    [
                        distributed_meta_stability,
                        attractor_persistence,
                        adaptive_recovery,
                        (
                            1.0
                            - hysteresis_memory
                        ),
                    ]
                )
            )
        )

        reflexive_debt = (
            self._bounded(
                mean(
                    [
                        hysteresis_memory,
                        historical_scarring,
                        fatigue_accumulation,
                    ]
                )
            )
        )

        irreversible_transformation = (
            self._bounded(
                mean(
                    [
                        historical_scarring,
                        semantic_decay,
                        fragmentation_pressure,
                    ]
                )
            )
        )

        open_continuity_viability = (
            reflexive_continuity >= 0.55
        )

        if reflexive_continuity >= 0.85:

            classification = (
                "persistent_open_reflexive_hysteresis"
            )

        elif reflexive_continuity >= 0.65:

            classification = (
                "adaptive_reflexive_hysteresis"
            )

        elif reflexive_continuity >= 0.45:

            classification = (
                "fragile_reflexive_hysteresis"
            )

        else:

            classification = (
                "reflexive_degradation_risk"
            )

        return {
            "perturbation_pressure":
                round(
                    perturbation_pressure,
                    4,
                ),
            "hysteresis_memory":
                round(
                    hysteresis_memory,
                    4,
                ),
            "historical_scarring":
                round(
                    historical_scarring,
                    4,
                ),
            "adaptive_recovery":
                round(
                    adaptive_recovery,
                    4,
                ),
            "reflexive_continuity":
                round(
                    reflexive_continuity,
                    4,
                ),
            "reflexive_debt":
                round(
                    reflexive_debt,
                    4,
                ),
            "irreversible_transformation":
                round(
                    irreversible_transformation,
                    4,
                ),
            "open_continuity_viability":
                open_continuity_viability,
            "classification":
                classification,
        }

    def step(self, state=None):

        return self.evaluate(state)
