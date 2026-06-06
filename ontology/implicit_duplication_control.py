from statistics import mean

PRIMITIVE = "implicit_duplication_control"

DEPENDENCIES = [
    "trajectory_convergence",
    "structural_attractor",
    "distributed_meta_stability",
    "trajectory_attractor_transition",
    "distributed_symbolic_ecology",
    "attractor_persistence_analyzer",
    "multi_lineage_topology",
    "heterogeneous_node_coordination",
    "distributed_open_ended_pluralistic_evolution",
    "semantic_diversity_preservation",
]


def _bounded(value):

    return max(
        0.0,
        min(
            1.0,
            float(value),
        ),
    )


class ImplicitDuplicationControl:

    def __init__(
        self,
        duplication_floor=0.35,
        anti_convergence_gain=0.14,
    ):

        self.duplication_floor = duplication_floor
        self.anti_convergence_gain = anti_convergence_gain

    def step(
        self,
        trajectory_similarity=0.5,
        attractor_overlap=0.5,
        meta_stability=0.5,
        corridor_diversity=0.5,
        symbolic_ecology_dispersion=0.5,
        lineage_separation=0.5,
        convergence_pressure=0.5,
        exploratory_variability=0.5,
        semantic_regeneration=0.5,
    ):

        trajectory_similarity = _bounded(
            trajectory_similarity
        )

        attractor_overlap = _bounded(
            attractor_overlap
        )

        meta_stability = _bounded(
            meta_stability
        )

        corridor_diversity = _bounded(
            corridor_diversity
        )

        symbolic_ecology_dispersion = _bounded(
            symbolic_ecology_dispersion
        )

        lineage_separation = _bounded(
            lineage_separation
        )

        convergence_pressure = _bounded(
            convergence_pressure
        )

        exploratory_variability = _bounded(
            exploratory_variability
        )

        semantic_regeneration = _bounded(
            semantic_regeneration
        )

        latent_duplication_risk = _bounded(
            (
                trajectory_similarity
                + attractor_overlap
                + convergence_pressure
            ) / 3.0
        )

        ecological_dispersion_capacity = (
            _bounded(
                (
                    corridor_diversity
                    + symbolic_ecology_dispersion
                    + exploratory_variability
                ) / 3.0
            )
        )

        distributed_differentiation_index = (
            _bounded(
                (
                    lineage_separation
                    + semantic_regeneration
                    + ecological_dispersion_capacity
                ) / 3.0
            )
        )

        anti_duplication_viability = (
            _bounded(
                mean(
                    [
                        ecological_dispersion_capacity,
                        distributed_differentiation_index,
                        meta_stability,
                    ]
                )
            )
        )

        implicit_reconvergence_pressure = (
            _bounded(
                latent_duplication_risk
                - anti_duplication_viability
                + self.anti_convergence_gain
            )
        )

        authentic_pluralism_index = (
            max(
                self.duplication_floor,
                _bounded(
                    (
                        anti_duplication_viability
                        + (
                            1.0
                            - latent_duplication_risk
                        )
                        + distributed_differentiation_index
                    ) / 3.0
                )
            )
        )

        hidden_convergence_detected = (
            implicit_reconvergence_pressure
            >= 0.60
        )

        authentic_pluralism_viable = (
            authentic_pluralism_index
            >= 0.70
        )

        return {
            "primitive": PRIMITIVE,
            "latent_duplication_risk":
                round(
                    latent_duplication_risk,
                    4,
                ),
            "ecological_dispersion_capacity":
                round(
                    ecological_dispersion_capacity,
                    4,
                ),
            "distributed_differentiation_index":
                round(
                    distributed_differentiation_index,
                    4,
                ),
            "anti_duplication_viability":
                round(
                    anti_duplication_viability,
                    4,
                ),
            "implicit_reconvergence_pressure":
                round(
                    implicit_reconvergence_pressure,
                    4,
                ),
            "authentic_pluralism_index":
                round(
                    authentic_pluralism_index,
                    4,
                ),
            "hidden_convergence_detected":
                hidden_convergence_detected,
            "authentic_pluralism_viable":
                authentic_pluralism_viable,
            "future_openness_preserved":
                authentic_pluralism_viable,
        }


if __name__ == "__main__":

    engine = ImplicitDuplicationControl()

    result = engine.step(
        trajectory_similarity=0.82,
        attractor_overlap=0.79,
        meta_stability=0.63,
        corridor_diversity=0.58,
        symbolic_ecology_dispersion=0.61,
        lineage_separation=0.57,
        convergence_pressure=0.84,
        exploratory_variability=0.66,
        semantic_regeneration=0.62,
    )

    print(result)
