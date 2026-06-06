
from statistics import mean

PRIMITIVE = "distributed_attractor_speciation"

DESCRIPTION = (
    "Distributed attractor speciation."
)

DEPENDENCIES = [
    "distributed_historical_mutation",
    "distributed_meta_stability",
    "open_ended_historical_navigation",
    "ontological_attractor_mapping",
    "topological_pressure_monitor",
    "trajectory_bifurcation",
    "non_convergent_intelligence_dynamics",
    "civilizational_semantic_drift",
]


class DistributedAttractorSpeciation:

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

        symbolic_drift = self._bounded(
            state.get(
                "symbolic_drift",
                0.0,
            )
        )

        convergence_pressure = self._bounded(
            state.get(
                "convergence_pressure",
                0.0,
            )
        )

        distributed_meta_stability = self._bounded(
            state.get(
                "distributed_meta_stability",
                state.get(
                    "open_stability_index",
                    0.0,
                ),
            )
        )

        trajectory_diversity = self._bounded(
            state.get(
                "trajectory_diversity",
                0.0,
            )
        )

        ecological_coordination = self._bounded(
            state.get(
                "ecological_coordination",
                0.0,
            )
        )

        historical_openness = self._bounded(
            state.get(
                "historical_openness",
                0.0,
            )
        )

        lineage_separation_index = self._bounded(
            (
                lineage_diversity
                + symbolic_drift
                + (
                    1.0
                    - convergence_pressure
                )
            ) / 3.0
        )

        distributed_niche_diversity = self._bounded(
            (
                trajectory_diversity
                + ecological_coordination
                + historical_openness
            ) / 3.0
        )

        anti_fusion_capacity = self._bounded(
            (
                lineage_separation_index
                + distributed_meta_stability
                + (
                    1.0
                    - convergence_pressure
                )
            ) / 3.0
        )

        pluralistic_topological_stability = (
            self._bounded(
                (
                    anti_fusion_capacity
                    + distributed_niche_diversity
                    + distributed_meta_stability
                ) / 3.0
            )
        )

        distributed_attractor_speciation_index = (
            self._bounded(
                mean(
                    [
                        lineage_separation_index,
                        distributed_niche_diversity,
                        anti_fusion_capacity,
                        pluralistic_topological_stability,
                    ]
                )
            )
        )

        if (
            distributed_attractor_speciation_index
            >= 0.90
        ):

            classification = (
                "fully_pluralistic_open_ecology"
            )

        elif (
            distributed_attractor_speciation_index
            >= 0.70
        ):

            classification = (
                "distributed_open_speciation"
            )

        elif (
            distributed_attractor_speciation_index
            >= 0.50
        ):

            classification = (
                "fragile_pluralistic_divergence"
            )

        else:

            classification = (
                "attractor_fusion_risk"
            )

        return {
            "lineage_separation_index":
                round(
                    lineage_separation_index,
                    4,
                ),
            "distributed_niche_diversity":
                round(
                    distributed_niche_diversity,
                    4,
                ),
            "anti_fusion_capacity":
                round(
                    anti_fusion_capacity,
                    4,
                ),
            "pluralistic_topological_stability":
                round(
                    pluralistic_topological_stability,
                    4,
                ),
            "distributed_attractor_speciation_index":
                round(
                    distributed_attractor_speciation_index,
                    4,
                ),
            "classification":
                classification,
            "pluralistic_speciation_viable":
                (
                    distributed_attractor_speciation_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)



# A10.5 AUTOMATIC ECOLOGICAL PRODUCERS
try:
    from ontology.population_ecological_extraction import PopulationEcologicalExtraction
    from ontology.semantic_ecology_extraction import SemanticEcologyExtraction

    def automatic_ecological_inputs():
        population = PopulationEcologicalExtraction().step()
        semantic = SemanticEcologyExtraction().step()

        return {
            "lineage_diversity": population.get("lineage_diversity", 0.0),
            "historical_divergence": population.get(
                "historical_divergence_mean", 0.0
            ),
            "symbolic_drift": semantic.get("semantic_drift", 0.0),
            "convergence_pressure": semantic.get(
                "convergence_pressure", 1.0
            ),
            "fragmentation_pressure": semantic.get(
                "fragmentation_pressure", 0.0
            ),
        }

except Exception:
    pass




# A10.5.1 ECOLOGICAL PRODUCER WIRING
try:
    from ontology.population_ecological_extraction import PopulationEcologicalExtraction
    from ontology.semantic_ecology_extraction import SemanticEcologyExtraction

    _original_speciation_step = DistributedAttractorSpeciation.step

    def _wired_speciation_step(self, state=None):
        state = state or {}

        population = PopulationEcologicalExtraction().step()
        semantic = SemanticEcologyExtraction().step()

        state.setdefault(
            "lineage_diversity",
            population.get("lineage_diversity", 0.0),
        )

        state.setdefault(
            "symbolic_drift",
            semantic.get("semantic_drift", 0.0),
        )

        state.setdefault(
            "convergence_pressure",
            semantic.get("convergence_pressure", 1.0),
        )

        return self.evaluate(state)

    DistributedAttractorSpeciation.step = _wired_speciation_step

except Exception:
    pass

