
from statistics import mean

PRIMITIVE = "distributed_historical_branching"

DEPENDENCIES = [
    "real_multi_machine_historical_divergence",
    "distributed_historical_mutation",
    "trajectory_bifurcation",
    "trajectory_path_dependency",
    "trajectory_hysteresis",
    "trajectory_metastability",
    "distributed_attractor_speciation",
    "trajectory_regime",
    "trajectory_coordination",
    "trajectory_synchronization",
    "structural_transition_operator",
    "future_openness",
    "anti_closure_metaconstraint",
]


class DistributedHistoricalBranching:

    def _bounded(self, value):

        return max(0.0, min(1.0, float(value)))

    def evaluate(self, state=None):

        state = state or {}

        branch_generation_capacity = self._bounded(
            state.get(
                "branch_generation_capacity",
                0.0,
            )
        )

        historical_divergence = self._bounded(
            state.get(
                "historical_divergence",
                0.0,
            )
        )

        interoperability = self._bounded(
            state.get(
                "interoperability",
                0.0,
            )
        )

        metastability = self._bounded(
            state.get(
                "metastability",
                0.0,
            )
        )

        attractor_speciation = self._bounded(
            state.get(
                "attractor_speciation",
                0.0,
            )
        )

        synchronization_pressure = self._bounded(
            state.get(
                "synchronization_pressure",
                0.0,
            )
        )

        historical_openness = self._bounded(
            state.get(
                "historical_openness",
                0.0,
            )
        )

        branching_viability = self._bounded(
            (
                branch_generation_capacity
                + historical_divergence
                + historical_openness
            ) / 3.0
        )

        anti_fusion_branching = self._bounded(
            (
                attractor_speciation
                + metastability
                + (1.0 - synchronization_pressure)
            ) / 3.0
        )

        distributed_branch_ecology = self._bounded(
            (
                branching_viability
                + anti_fusion_branching
                + interoperability
            ) / 3.0
        )

        distributed_historical_branching_index = (
            self._bounded(
                mean([
                    branching_viability,
                    anti_fusion_branching,
                    distributed_branch_ecology,
                ])
            )
        )

        if (
            synchronization_pressure >= 0.90
            and historical_divergence <= 0.25
        ):

            classification = (
                "historical_branch_collapse_risk"
            )

        elif (
            distributed_historical_branching_index
            >= 0.90
        ):

            classification = (
                "fully_pluralistic_branch_ecology"
            )

        elif (
            distributed_historical_branching_index
            >= 0.70
        ):

            classification = (
                "stable_distributed_branching"
            )

        elif (
            distributed_historical_branching_index
            >= 0.50
        ):

            classification = (
                "fragile_distributed_branching"
            )

        else:

            classification = (
                "historical_branch_instability"
            )

        return {
            "branching_viability":
                round(branching_viability, 4),
            "anti_fusion_branching":
                round(anti_fusion_branching, 4),
            "distributed_branch_ecology":
                round(distributed_branch_ecology, 4),
            "distributed_historical_branching_index":
                round(
                    distributed_historical_branching_index,
                    4,
                ),
            "classification":
                classification,
            "distributed_branching_viable":
                (
                    distributed_historical_branching_index
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

    _original_branching_step = DistributedHistoricalBranching.step

    def _wired_branching_step(self, state=None):
        state = state or {}

        population = PopulationEcologicalExtraction().step()

        state.setdefault(
            "historical_divergence",
            population.get("historical_divergence_mean", 0.0),
        )

        state.setdefault(
            "branch_generation_capacity",
            population.get("lineage_diversity", 0.0),
        )

        return self.evaluate(state)

    DistributedHistoricalBranching.step = _wired_branching_step

except Exception:
    pass

