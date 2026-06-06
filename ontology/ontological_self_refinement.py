
from __future__ import annotations

from statistics import mean

PRIMITIVE = "ontological_self_refinement"

DEPENDENCIES = [
    "self_evolving_ontology_architect",
    "ontology_gap_detector",
    "meta_concepts_registry",
    "changes_of_status_of_concepts",
    "semantic_canonicalization_layer",
    "adaptive_symbolic_pruning",
    "distributed_semantic_recycling",
    "ontological_attractor_mapping",
    "distributed_open_ended_pluralistic_evolution",
    "emergent_modularity",
    "structural_transition_operator",
    "distributed_symbolic_ecology",
    "novelty_emergence",
    "morphospace_exploration",
    "distributed_topological_self_adaptation",
    "latent_topological_instability",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class OntologicalSelfRefinement:

    def __init__(
        self,
        openness_floor: float = 0.65,
        attractor_limit: float = 0.72,
    ):
        self.openness_floor = openness_floor
        self.attractor_limit = attractor_limit
        self.history = []

    def step(self, state=None):

        state = state or {}

        ontological_openness = _bounded(
            state.get(
                "ontological_openness",
                0.5,
            )
        )

        attractor_capture_risk = _bounded(
            state.get(
                "attractor_capture_risk",
                0.5,
            )
        )

        semantic_diversity = _bounded(
            state.get(
                "semantic_diversity",
                0.5,
            )
        )

        morphospace_coverage = _bounded(
            state.get(
                "morphospace_coverage",
                0.5,
            )
        )

        novelty_emergence = _bounded(
            state.get(
                "novelty_emergence",
                0.5,
            )
        )

        modularity_strength = _bounded(
            state.get(
                "modularity_strength",
                0.5,
            )
        )

        distributed_pluralism = _bounded(
            state.get(
                "distributed_pluralism",
                0.5,
            )
        )

        semantic_recycling = _bounded(
            state.get(
                "semantic_recycling",
                0.5,
            )
        )

        pruning_stability = _bounded(
            state.get(
                "pruning_stability",
                0.5,
            )
        )

        canonicalization_pressure = _bounded(
            state.get(
                "canonicalization_pressure",
                0.5,
            )
        )

        ontology_gap_pressure = _bounded(
            state.get(
                "ontology_gap_pressure",
                0.5,
            )
        )

        future_space_contraction = _bounded(
            state.get(
                "future_space_contraction",
                0.5,
            )
        )

        ontological_refinement_capacity = _bounded(
            mean(
                [
                    ontological_openness,
                    semantic_diversity,
                    morphospace_coverage,
                    novelty_emergence,
                    distributed_pluralism,
                    semantic_recycling,
                ]
            )
        )

        anti_fossilization_capacity = _bounded(
            mean(
                [
                    semantic_diversity,
                    novelty_emergence,
                    1.0 - attractor_capture_risk,
                    1.0 - canonicalization_pressure,
                    1.0 - future_space_contraction,
                ]
            )
        )

        distributed_refinement_viability = _bounded(
            mean(
                [
                    ontological_refinement_capacity,
                    anti_fossilization_capacity,
                    pruning_stability,
                    modularity_strength,
                    1.0 - ontology_gap_pressure,
                ]
            )
        )

        refinement_singularity_risk = _bounded(
            mean(
                [
                    attractor_capture_risk,
                    canonicalization_pressure,
                    future_space_contraction,
                ]
            )
        )

        if (
            refinement_singularity_risk
            >= self.attractor_limit
        ):

            classification = (
                "ontological_refinement_capture_risk"
            )

        elif (
            distributed_refinement_viability
            >= self.openness_floor
        ):

            classification = (
                "distributed_open_ontological_refinement"
            )

        else:

            classification = (
                "transitional_ontological_refinement"
            )

        self.history.append({
            "classification": classification,
            "viability":
                distributed_refinement_viability,
        })

        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        return {
            "primitive": PRIMITIVE,
            "classification":
                classification,
            "ontological_refinement_capacity":
                round(
                    ontological_refinement_capacity,
                    4,
                ),
            "anti_fossilization_capacity":
                round(
                    anti_fossilization_capacity,
                    4,
                ),
            "distributed_refinement_viability":
                round(
                    distributed_refinement_viability,
                    4,
                ),
            "refinement_singularity_risk":
                round(
                    refinement_singularity_risk,
                    4,
                ),
            "future_openness_preserved":
                anti_fossilization_capacity
                >= 0.70,
            "distributed_refinement_viable":
                distributed_refinement_viability
                >= 0.65,
            "history_size":
                len(self.history),
        }
