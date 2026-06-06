
from statistics import mean

PRIMITIVE = "distributed_historical_mutation"

DESCRIPTION = (
    "Distributed historical mutation."
)

DEPENDENCIES = [
    "historical_open_endedness",
    "multi_individual_civilizational_ecology",
    "distributed_civilizational_memory",
    "mutational_robustness",
    "evolutionary_drift",
    "symbolic_fragmentation",
    "genealogical_continuity",
    "social_ecological_resilience",
    "trajectory_bifurcation",
    "trajectory_resilience",
]


class DistributedHistoricalMutation:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(self, state):

        lineage_diversity = (
            self._bounded(
                state.get(
                    "lineage_diversity",
                    0.0,
                )
            )
        )

        symbolic_drift = (
            self._bounded(
                state.get(
                    "symbolic_drift",
                    0.0,
                )
            )
        )

        mutation_viability = (
            self._bounded(
                state.get(
                    "mutation_viability",
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

        ecological_coordination = (
            self._bounded(
                state.get(
                    "ecological_coordination",
                    0.0,
                )
            )
        )

        fragmentation_pressure = (
            self._bounded(
                state.get(
                    "fragmentation_pressure",
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

        historical_openness = (
            self._bounded(
                state.get(
                    "historical_openness",
                    0.0,
                )
            )
        )

        distributed_mutation_potential = (
            self._bounded(
                (
                    lineage_diversity
                    + symbolic_drift
                    + mutation_viability
                    + historical_openness
                ) / 4.0
            )
        )

        viable_pluralism_index = (
            self._bounded(
                (
                    distributed_mutation_potential
                    + genealogical_continuity
                    + ecological_coordination
                    + (
                        1.0
                        - fragmentation_pressure
                    )
                ) / 4.0
            )
        )

        anti_convergence_capacity = (
            self._bounded(
                (
                    lineage_diversity
                    + symbolic_drift
                    + (
                        1.0
                        - convergence_pressure
                    )
                    + historical_openness
                ) / 4.0
            )
        )

        distributed_historical_mutation_index = (
            self._bounded(
                mean(
                    [
                        distributed_mutation_potential,
                        viable_pluralism_index,
                        anti_convergence_capacity,
                    ]
                )
            )
        )

        distributed_pluralism_viable = (
            distributed_historical_mutation_index >= 0.60
        )

        return {
            "distributed_mutation_potential":
                round(
                    distributed_mutation_potential,
                    4,
                ),
            "viable_pluralism_index":
                round(
                    viable_pluralism_index,
                    4,
                ),
            "anti_convergence_capacity":
                round(
                    anti_convergence_capacity,
                    4,
                ),
            "distributed_historical_mutation_index":
                round(
                    distributed_historical_mutation_index,
                    4,
                ),
            "distributed_pluralism_viable":
                distributed_pluralism_viable,
        }

    def step(self, state):

        return self.evaluate(state)



# A10.4.1 POPULATION ECOLOGICAL WIRING
try:
    from ontology.population_ecological_extraction import PopulationEcologicalExtraction

    _original_step = DistributedHistoricalMutation.step

    def _wired_step(self, state=None):
        state = state or {}

        try:
            metrics = PopulationEcologicalExtraction().step()

            state.setdefault(
                "lineage_diversity",
                metrics.get("lineage_diversity", 0.0),
            )

            state.setdefault(
                "historical_openness",
                metrics.get("lineage_diversity", 0.0),
            )

            state.setdefault(
                "genealogical_continuity",
                min(
                    1.0,
                    metrics.get("population_size", 0) / 100.0,
                ),
            )

        except Exception:
            pass

        return self.evaluate(state)

    DistributedHistoricalMutation.step = _wired_step

except Exception:
    pass

