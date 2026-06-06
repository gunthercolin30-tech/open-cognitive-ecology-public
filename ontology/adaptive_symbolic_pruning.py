
from __future__ import annotations

PRIMITIVE = "adaptive_symbolic_pruning"

DEPENDENCIES = [
    "adaptive_civilizational_forgetting",
    "distributed_semantic_recycling",
    "symbolic_fragmentation",
    "structural_attractor",
    "innovation_retention",
    "semantic_collapse",
    "distributed_symbolic_ecology",
    "semantic_field",
    "evolutionary_drift",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class AdaptiveSymbolicPruning:

    def __init__(
        self,
        pruning_gain: float = 0.12,
        diversity_floor: float = 0.40,
    ):
        self.pruning_gain = pruning_gain
        self.diversity_floor = diversity_floor

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
                "pruning_active": False,
                "future_openness_preserved": True,
            }

        dominant_strength = max(
            attractor_strengths.values()
        )

        average_strength = (
            sum(
                attractor_strengths.values()
            )
            / len(attractor_strengths)
        )

        attractor_density = _bounded(
            (
                dominant_strength
                + average_strength
            ) / 2.0
        )

        pruning_pressure = _bounded(
            (
                attractor_density
                + (1.0 - openness_score)
            ) / 2.0
        )

        pruning_active = (
            pruning_pressure >= 0.15
        )

        pruned_attractors = {}

        preserved_innovations = []

        for attractor, strength in (
            attractor_strengths.items()
        ):

            innovation_score = (
                innovation_scores.get(
                    attractor,
                    0.0,
                )
            )

            if innovation_score >= 0.70:

                preserved_innovations.append(
                    attractor
                )

                pruned_attractors[
                    attractor
                ] = strength

                continue

            reduction = (
                pruning_pressure
                * self.pruning_gain
            )

            pruned_strength = max(
                0.05,
                strength - reduction,
            )

            pruned_attractors[
                attractor
            ] = round(
                pruned_strength,
                4,
            )

        adaptive_pruning_ratio = _bounded(
            pruning_pressure
            * self.pruning_gain
        )

        symbolic_diversity_preservation = max(
            self.diversity_floor,
            1.0
            - adaptive_pruning_ratio,
        )

        regenerative_viability_score = _bounded(
            (
                symbolic_diversity_preservation
                + openness_score
            ) / 2.0
        )

        distributed_pruning_stability = _bounded(
            (
                regenerative_viability_score
                + (1.0 - pruning_pressure)
            ) / 2.0
        )

        future_openness_preservation = _bounded(
            (
                distributed_pruning_stability
                + openness_score
            ) / 2.0
        )

        return {
            "primitive": PRIMITIVE,
            "pruning_active":
                pruning_active,
            "pruning_pressure":
                round(
                    pruning_pressure,
                    4,
                ),
            "attractor_density":
                round(
                    attractor_density,
                    4,
                ),
            "adaptive_pruning_ratio":
                round(
                    adaptive_pruning_ratio,
                    4,
                ),
            "symbolic_diversity_preservation":
                round(
                    symbolic_diversity_preservation,
                    4,
                ),
            "preserved_innovations":
                preserved_innovations,
            "pruned_attractors":
                pruned_attractors,
            "regenerative_viability_score":
                round(
                    regenerative_viability_score,
                    4,
                ),
            "distributed_pruning_stability":
                round(
                    distributed_pruning_stability,
                    4,
                ),
            "future_openness_preserved":
                future_openness_preservation
                >= 0.70,
            "future_openness_preservation":
                round(
                    future_openness_preservation,
                    4,
                ),
        }
