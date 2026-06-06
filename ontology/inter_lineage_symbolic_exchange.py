
from statistics import mean

PRIMITIVE = "inter_lineage_symbolic_exchange"

DESCRIPTION = (
    "Inter lineage symbolic exchange."
)

DEPENDENCIES = [
    "distributed_symbolic_ecology",
    "distributed_semantic_recycling",
    "shared_symbolic_reference",
    "civilizational_semantic_drift",
    "symbolic_fragmentation",
    "intersubjective_alignment",
    "distributed_attractor_speciation",
    "semantic_propagation",
    "semantic_field",
]


class InterLineageSymbolicExchange:

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

        semantic_interoperability = self._bounded(
            state.get(
                "semantic_interoperability",
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

        fragmentation_pressure = self._bounded(
            state.get(
                "fragmentation_pressure",
                0.0,
            )
        )

        attractor_speciation = self._bounded(
            state.get(
                "distributed_attractor_speciation_index",
                0.0,
            )
        )

        semantic_recycling_stability = self._bounded(
            state.get(
                "semantic_recycling_stability",
                0.0,
            )
        )

        intersubjective_alignment = self._bounded(
            state.get(
                "intersubjective_alignment_index",
                0.0,
            )
        )

        exchange_selectivity = self._bounded(
            (
                semantic_interoperability
                + (
                    1.0 - convergence_pressure
                )
            ) / 2.0
        )

        symbolic_translation_friction = self._bounded(
            (
                symbolic_drift
                + fragmentation_pressure
            ) / 2.0
        )

        partial_exchange_viability = self._bounded(
            (
                exchange_selectivity
                + semantic_recycling_stability
                + (
                    1.0 - symbolic_translation_friction
                )
            ) / 3.0
        )

        anti_homogenization_capacity = self._bounded(
            (
                attractor_speciation
                + (
                    1.0 - convergence_pressure
                )
                + symbolic_drift
            ) / 3.0
        )

        pluralistic_exchange_stability = self._bounded(
            (
                partial_exchange_viability
                + anti_homogenization_capacity
                + intersubjective_alignment
            ) / 3.0
        )

        inter_lineage_symbolic_exchange_index = (
            self._bounded(
                mean(
                    [
                        exchange_selectivity,
                        symbolic_translation_friction,
                        partial_exchange_viability,
                        anti_homogenization_capacity,
                        pluralistic_exchange_stability,
                    ]
                )
            )
        )

        if (
            inter_lineage_symbolic_exchange_index
            >= 0.90
        ):

            classification = (
                "pluralistic_exchange_ecology"
            )

        elif (
            inter_lineage_symbolic_exchange_index
            >= 0.70
        ):

            classification = (
                "stable_partial_exchange"
            )

        elif (
            inter_lineage_symbolic_exchange_index
            >= 0.50
        ):

            classification = (
                "fragile_exchange_corridor"
            )

        else:

            classification = (
                "homogenization_or_fragmentation_risk"
            )

        return {
            "exchange_selectivity":
                round(
                    exchange_selectivity,
                    4,
                ),
            "symbolic_translation_friction":
                round(
                    symbolic_translation_friction,
                    4,
                ),
            "partial_exchange_viability":
                round(
                    partial_exchange_viability,
                    4,
                ),
            "anti_homogenization_capacity":
                round(
                    anti_homogenization_capacity,
                    4,
                ),
            "pluralistic_exchange_stability":
                round(
                    pluralistic_exchange_stability,
                    4,
                ),
            "inter_lineage_symbolic_exchange_index":
                round(
                    inter_lineage_symbolic_exchange_index,
                    4,
                ),
            "classification":
                classification,
            "exchange_corridor_viable":
                (
                    inter_lineage_symbolic_exchange_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)



# A10.4.2.b SEMANTIC ECOLOGICAL WIRING
try:
    from ontology.semantic_ecology_extraction import SemanticEcologyExtraction

    _original_step = InterLineageSymbolicExchange.step

    def _wired_step(self, state=None):
        state = state or {}

        try:
            metrics = SemanticEcologyExtraction().step()

            state.setdefault(
                "symbolic_drift",
                metrics.get("semantic_drift", 0.0),
            )

            state.setdefault(
                "fragmentation_pressure",
                metrics.get("fragmentation_pressure", 0.0),
            )

            state.setdefault(
                "convergence_pressure",
                metrics.get("convergence_pressure", 1.0),
            )

            state.setdefault(
                "semantic_interoperability",
                max(
                    0.0,
                    1.0 - metrics.get("semantic_drift", 0.0),
                ),
            )

        except Exception:
            pass

        return self.evaluate(state)

    InterLineageSymbolicExchange.step = _wired_step

except Exception:
    pass

