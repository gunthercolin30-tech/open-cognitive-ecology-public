
from __future__ import annotations

PRIMITIVE = "attractor_desaturation"

DEPENDENCIES = [
    "structural_attractor",
    "attractor_basin",
    "adaptive_symbolic_pruning",
    "distributed_symbolic_ecology",
    "semantic_field",
    "evolutionary_drift",
    "semantic_collapse",
    "distributed_semantic_recycling",
    "innovation_retention",
    "semantic_propagation",
    "symbolic_fragmentation",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class AttractorDesaturation:

    def __init__(
        self,
        desaturation_gain: float = 0.08,
        perturbation_micro_gain: float = 0.03,
        rigidity_threshold: float = 0.72,
    ):
        self.desaturation_gain = desaturation_gain
        self.perturbation_micro_gain = (
            perturbation_micro_gain
        )
        self.rigidity_threshold = rigidity_threshold

    def step(
        self,
        attractor_strengths=None,
        innovation_scores=None,
        openness_score: float = 1.0,
    ):

        attractor_strengths = (
            attractor_strengths or {}
        )

        innovation_scores = (
            innovation_scores or {}
        )

        openness_score = _bounded(
            openness_score
        )

        if not attractor_strengths:

            return {
                "primitive": PRIMITIVE,
                "desaturation_active": False,
                "future_openness_preserved": True,
            }

        dominant_strength = max(
            attractor_strengths.values()
        )

        basin_size = (
            sum(
                attractor_strengths.values()
            )
            / len(attractor_strengths)
        )

        attractor_saturation = _bounded(
            (
                dominant_strength
                + basin_size
            ) / 2.0
        )

        basin_rigidity = _bounded(
            attractor_saturation
            * (1.0 - openness_score * 0.5)
        )

        desaturation_pressure = _bounded(
            (
                basin_rigidity
                + attractor_saturation
            ) / 2.0
        )

        desaturation_active = (
            basin_rigidity
            >= self.rigidity_threshold * 0.5
        )

        desaturated_attractors = {}

        preserved_bifurcations = []

        for attractor, strength in (
            attractor_strengths.items()
        ):

            innovation_score = (
                innovation_scores.get(
                    attractor,
                    0.0,
                )
            )

            if innovation_score >= 0.75:

                preserved_bifurcations.append(
                    attractor
                )

                desaturated_attractors[
                    attractor
                ] = round(
                    strength,
                    4,
                )

                continue

            reduction = (
                desaturation_pressure
                * self.desaturation_gain
            )

            micro_perturbation = (
                desaturation_pressure
                * self.perturbation_micro_gain
            )

            adjusted_strength = max(
                0.05,
                strength
                - reduction
                + micro_perturbation,
            )

            desaturated_attractors[
                attractor
            ] = round(
                adjusted_strength,
                4,
            )

        topological_openness = _bounded(
            openness_score
            + (
                1.0 - basin_rigidity
            ) * 0.25
        )

        attractor_breathability = _bounded(
            (
                topological_openness
                + (1.0 - basin_rigidity)
            ) / 2.0
        )

        historical_inertia = _bounded(
            attractor_saturation
            * basin_rigidity
        )

        bifurcation_preservation = _bounded(
            (
                len(
                    preserved_bifurcations
                )
                / max(
                    1,
                    len(
                        attractor_strengths
                    )
                )
            )
            + openness_score * 0.25
        )

        distributed_topological_stability = (
            _bounded(
                (
                    attractor_breathability
                    + bifurcation_preservation
                ) / 2.0
            )
        )

        critical_amplitude_margin = _bounded(
            1.0
            - historical_inertia
        )

        future_openness_preservation = (
            _bounded(
                (
                    distributed_topological_stability
                    + topological_openness
                ) / 2.0
            )
        )

        return {
            "primitive": PRIMITIVE,
            "desaturation_active":
                desaturation_active,
            "attractor_saturation":
                round(
                    attractor_saturation,
                    4,
                ),
            "basin_rigidity":
                round(
                    basin_rigidity,
                    4,
                ),
            "desaturation_pressure":
                round(
                    desaturation_pressure,
                    4,
                ),
            "topological_openness":
                round(
                    topological_openness,
                    4,
                ),
            "attractor_breathability":
                round(
                    attractor_breathability,
                    4,
                ),
            "historical_inertia":
                round(
                    historical_inertia,
                    4,
                ),
            "critical_amplitude_margin":
                round(
                    critical_amplitude_margin,
                    4,
                ),
            "bifurcation_preservation":
                round(
                    bifurcation_preservation,
                    4,
                ),
            "distributed_topological_stability":
                round(
                    distributed_topological_stability,
                    4,
                ),
            "preserved_bifurcations":
                preserved_bifurcations,
            "desaturated_attractors":
                desaturated_attractors,
            "future_openness_preserved":
                future_openness_preservation
                >= 0.70,
            "future_openness_preservation":
                round(
                    future_openness_preservation,
                    4,
                ),
        }
