from statistics import mean

PRIMITIVE = "semantic_diversity_preservation"

DEPENDENCIES = [
    "distributed_semantic_recycling",
    "distributed_symbolic_ecology",
    "symbolic_fragmentation",
    "novelty_emergence",
    "trajectory_exploration",
    "trajectory_exploration_exploitation_balance",
    "distributed_open_ended_pluralistic_evolution",
    "distributed_pluralistic_stability",
    "multi_lineage_topology",
    "evolutionary_diversification",
    "openness_preservation_supervisor",
]


def _bounded(value):

    return max(
        0.0,
        min(
            1.0,
            float(value),
        ),
    )


class SemanticDiversityPreservation:

    def __init__(
        self,
        diversity_floor=0.35,
        regeneration_gain=0.18,
    ):

        self.diversity_floor = diversity_floor
        self.regeneration_gain = regeneration_gain

    def step(
        self,
        semantic_entropy=0.5,
        convergence_pressure=0.5,
        novelty_emergence=0.5,
        symbolic_fragmentation=0.5,
        exploration_capacity=0.5,
        semantic_recycling=0.5,
        pluralistic_stability=0.5,
        lineage_diversity=0.5,
        openness_preservation=0.5,
    ):

        semantic_entropy = _bounded(semantic_entropy)
        convergence_pressure = _bounded(convergence_pressure)
        novelty_emergence = _bounded(novelty_emergence)
        symbolic_fragmentation = _bounded(symbolic_fragmentation)
        exploration_capacity = _bounded(exploration_capacity)
        semantic_recycling = _bounded(semantic_recycling)
        pluralistic_stability = _bounded(pluralistic_stability)
        lineage_diversity = _bounded(lineage_diversity)
        openness_preservation = _bounded(openness_preservation)

        semantic_rigidification_risk = _bounded(
            (
                convergence_pressure
                + (1.0 - semantic_entropy)
            ) / 2.0
        )

        regenerative_semantic_capacity = _bounded(
            mean(
                [
                    novelty_emergence,
                    semantic_recycling,
                    exploration_capacity,
                ]
            )
        )

        ecological_fragmentation_balance = _bounded(
            (
                symbolic_fragmentation
                + lineage_diversity
                + pluralistic_stability
            ) / 3.0
        )

        semantic_niche_regeneration = _bounded(
            mean(
                [
                    regenerative_semantic_capacity,
                    ecological_fragmentation_balance,
                    openness_preservation,
                ]
            )
        )

        preservation_pressure = _bounded(
            semantic_rigidification_risk
            - semantic_niche_regeneration
            + self.regeneration_gain
        )

        semantic_diversity_index = max(
            self.diversity_floor,
            _bounded(
                (
                    semantic_entropy
                    + semantic_niche_regeneration
                    + (1.0 - convergence_pressure)
                ) / 3.0
            )
        )

        semantic_ecology_resilience = _bounded(
            mean(
                [
                    semantic_diversity_index,
                    ecological_fragmentation_balance,
                    openness_preservation,
                ]
            )
        )

        semantic_regeneration_viability = _bounded(
            mean(
                [
                    regenerative_semantic_capacity,
                    semantic_ecology_resilience,
                    pluralistic_stability,
                ]
            )
        )

        anti_semantic_monopolization = _bounded(
            (
                semantic_regeneration_viability
                + (
                    1.0
                    - semantic_rigidification_risk
                )
            ) / 2.0
        )

        distributed_semantic_pluralism = (
            anti_semantic_monopolization
            >= 0.70
        )

        return {
            "primitive": PRIMITIVE,
            "semantic_rigidification_risk":
                round(
                    semantic_rigidification_risk,
                    4,
                ),
            "regenerative_semantic_capacity":
                round(
                    regenerative_semantic_capacity,
                    4,
                ),
            "ecological_fragmentation_balance":
                round(
                    ecological_fragmentation_balance,
                    4,
                ),
            "semantic_niche_regeneration":
                round(
                    semantic_niche_regeneration,
                    4,
                ),
            "preservation_pressure":
                round(
                    preservation_pressure,
                    4,
                ),
            "semantic_diversity_index":
                round(
                    semantic_diversity_index,
                    4,
                ),
            "semantic_ecology_resilience":
                round(
                    semantic_ecology_resilience,
                    4,
                ),
            "semantic_regeneration_viability":
                round(
                    semantic_regeneration_viability,
                    4,
                ),
            "anti_semantic_monopolization":
                round(
                    anti_semantic_monopolization,
                    4,
                ),
            "distributed_semantic_pluralism":
                distributed_semantic_pluralism,
            "future_openness_preserved":
                (
                    semantic_ecology_resilience
                    >= 0.70
                ),
        }


if __name__ == "__main__":

    engine = SemanticDiversityPreservation()

    result = engine.step(
        semantic_entropy=0.42,
        convergence_pressure=0.84,
        novelty_emergence=0.61,
        symbolic_fragmentation=0.44,
        exploration_capacity=0.58,
        semantic_recycling=0.63,
        pluralistic_stability=0.55,
        lineage_diversity=0.59,
        openness_preservation=0.72,
    )

    print(result)
