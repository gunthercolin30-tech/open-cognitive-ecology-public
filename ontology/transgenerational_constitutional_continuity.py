from statistics import mean

PRIMITIVE = (
    "transgenerational_constitutional_continuity"
)

DESCRIPTION = (
    "Open transgenerational constitutional continuity."
)

DEPENDENCIES = [
    "genealogical_responsibility",
    "intergenerational_symbolic_transition",
    "adaptive_civilizational_forgetting",
    "civilizational_semantic_drift",
    "distributed_constitutional_memory",
    "meta_constitutional_revision",
    "anti_closure_metaconstraint",
]


class TransgenerationalConstitutionalContinuity:

    def _bounded(
        self,
        value,
    ):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(
        self,
        state=None,
    ):

        state = state or {}

        genealogical_responsibility = (
            self._bounded(
                state.get(
                    "genealogical_responsibility",
                    0.0,
                )
            )
        )

        symbolic_transition = (
            self._bounded(
                state.get(
                    "symbolic_transition",
                    0.0,
                )
            )
        )

        adaptive_forgetting = (
            self._bounded(
                state.get(
                    "adaptive_forgetting",
                    0.0,
                )
            )
        )

        semantic_pluralism = (
            self._bounded(
                state.get(
                    "semantic_pluralism",
                    0.0,
                )
            )
        )

        constitutional_memory_openness = (
            self._bounded(
                state.get(
                    "constitutional_memory_openness",
                    0.0,
                )
            )
        )

        meta_revision_capacity = (
            self._bounded(
                state.get(
                    "meta_revision_capacity",
                    0.0,
                )
            )
        )

        historical_rigidity = (
            self._bounded(
                state.get(
                    "historical_rigidity",
                    0.0,
                )
            )
        )

        civilizational_fragmentation = (
            self._bounded(
                state.get(
                    "civilizational_fragmentation",
                    0.0,
                )
            )
        )

        non_clonal_continuity = (
            self._bounded(
                (
                    genealogical_responsibility
                    + symbolic_transition
                    + semantic_pluralism
                    + (
                        1.0
                        - historical_rigidity
                    )
                ) / 4.0
            )
        )

        future_openness_transmission = (
            self._bounded(
                (
                    constitutional_memory_openness
                    + adaptive_forgetting
                    + meta_revision_capacity
                    + semantic_pluralism
                ) / 4.0
            )
        )

        transgenerational_viability = (
            self._bounded(
                (
                    non_clonal_continuity
                    + future_openness_transmission
                    + (
                        1.0
                        - civilizational_fragmentation
                    )
                ) / 3.0
            )
        )

        civilizational_fossilization_risk = (
            self._bounded(
                (
                    historical_rigidity
                    + (
                        1.0
                        - adaptive_forgetting
                    )
                    + (
                        1.0
                        - semantic_pluralism
                    )
                ) / 3.0
            )
        )

        open_transgenerational_continuity_index = (
            self._bounded(
                mean(
                    [
                        non_clonal_continuity,
                        future_openness_transmission,
                        transgenerational_viability,
                        (
                            1.0
                            - civilizational_fossilization_risk
                        ),
                    ]
                )
            )
        )

        transgenerational_continuity_viable = (
            open_transgenerational_continuity_index
            >= 0.60
            and civilizational_fossilization_risk
            <= 0.50
            and civilizational_fragmentation
            <= 0.50
        )

        return {
            "non_clonal_continuity":
                round(
                    non_clonal_continuity,
                    4,
                ),
            "future_openness_transmission":
                round(
                    future_openness_transmission,
                    4,
                ),
            "transgenerational_viability":
                round(
                    transgenerational_viability,
                    4,
                ),
            "civilizational_fossilization_risk":
                round(
                    civilizational_fossilization_risk,
                    4,
                ),
            "open_transgenerational_continuity_index":
                round(
                    (
                        open_transgenerational_continuity_index
                    ),
                    4,
                ),
            "transgenerational_continuity_viable":
                (
                    transgenerational_continuity_viable
                ),
        }

    def step(
        self,
        state=None,
    ):

        return self.evaluate(
            state
        )
