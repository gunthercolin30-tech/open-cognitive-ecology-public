from __future__ import annotations

from statistics import mean

PRIMITIVE = "closure_pressure_regulator"

DEPENDENCIES = [
    "ontological_pressure_regulation",
    "topological_pressure_monitor",
    "semantic_density_tracker",
    "attractor_basin",
    "withdrawal_activation_controller",
    "structural_withdrawal",
    "architectural_non_closure_index",
    "distributed_meta_stability",
    "trajectory_bifurcation",
    "trajectory_metastability",
    "adaptive_civilizational_bifurcation",
    "trajectory_resilience",
]


def _bounded(value: float) -> float:
    return max(
        0.0,
        min(
            1.0,
            float(value),
        ),
    )


class ClosurePressureRegulator:

    def __init__(
        self,
        redistribution_gain: float = 0.18,
        minimal_coherence_floor: float = 0.30,
        anti_closure_floor: float = 0.35,
    ):
        self.redistribution_gain = redistribution_gain
        self.minimal_coherence_floor = (
            minimal_coherence_floor
        )
        self.anti_closure_floor = (
            anti_closure_floor
        )

    def step(
        self,
        closure_pressure: float = 0.5,
        semantic_saturation: float = 0.5,
        basin_size: float = 0.5,
        metastability: float = 0.5,
        resilience: float = 0.5,
        bifurcation_capacity: float = 0.5,
        openness_index: float = 0.5,
    ):

        closure_pressure = _bounded(
            closure_pressure
        )

        semantic_saturation = _bounded(
            semantic_saturation
        )

        basin_size = _bounded(
            basin_size
        )

        metastability = _bounded(
            metastability
        )

        resilience = _bounded(
            resilience
        )

        bifurcation_capacity = _bounded(
            bifurcation_capacity
        )

        openness_index = _bounded(
            openness_index
        )

        monopolization_risk = _bounded(
            mean(
                [
                    closure_pressure,
                    semantic_saturation,
                    basin_size,
                ]
            )
        )

        distributed_bifurcation_capacity = (
            _bounded(
                mean(
                    [
                        bifurcation_capacity,
                        metastability,
                        openness_index,
                    ]
                )
            )
        )

        adaptive_redistribution_strength = (
            _bounded(
                mean(
                    [
                        resilience,
                        distributed_bifurcation_capacity,
                        (
                            1.0
                            - monopolization_risk
                        ),
                    ]
                )
            )
        )

        regulation_intensity = (
            _bounded(
                monopolization_risk
                - adaptive_redistribution_strength
                + self.redistribution_gain
            )
        )

        redistributed_pressure = max(
            self.anti_closure_floor,
            closure_pressure
            - (
                adaptive_redistribution_strength
                * self.redistribution_gain
            )
        )

        polycentric_recovery = (
            _bounded(
                mean(
                    [
                        distributed_bifurcation_capacity,
                        resilience,
                        (
                            1.0
                            - redistributed_pressure
                        ),
                    ]
                )
            )
        )

        controlled_divergence = (
            _bounded(
                mean(
                    [
                        bifurcation_capacity,
                        metastability,
                        (
                            1.0
                            - semantic_saturation
                        ),
                    ]
                )
            )
        )

        viable_pluralism = (
            _bounded(
                mean(
                    [
                        polycentric_recovery,
                        controlled_divergence,
                        openness_index,
                    ]
                )
            )
        )

        continuity_preservation = max(
            self.minimal_coherence_floor,
            _bounded(
                mean(
                    [
                        resilience,
                        metastability,
                        viable_pluralism,
                    ]
                )
            )
        )

        anti_closure_viable = (
            viable_pluralism >= 0.65
        )

        return {
            "primitive": PRIMITIVE,
            "monopolization_risk":
                round(
                    monopolization_risk,
                    4,
                ),
            "distributed_bifurcation_capacity":
                round(
                    distributed_bifurcation_capacity,
                    4,
                ),
            "adaptive_redistribution_strength":
                round(
                    adaptive_redistribution_strength,
                    4,
                ),
            "regulation_intensity":
                round(
                    regulation_intensity,
                    4,
                ),
            "redistributed_pressure":
                round(
                    redistributed_pressure,
                    4,
                ),
            "polycentric_recovery":
                round(
                    polycentric_recovery,
                    4,
                ),
            "controlled_divergence":
                round(
                    controlled_divergence,
                    4,
                ),
            "viable_pluralism":
                round(
                    viable_pluralism,
                    4,
                ),
            "continuity_preservation":
                round(
                    continuity_preservation,
                    4,
                ),
            "anti_closure_viable":
                anti_closure_viable,
        }


if __name__ == "__main__":

    engine = ClosurePressureRegulator()

    result = engine.step(
        closure_pressure=0.91,
        semantic_saturation=0.88,
        basin_size=0.90,
        metastability=0.52,
        resilience=0.61,
        bifurcation_capacity=0.67,
        openness_index=0.48,
    )

    print(result)
