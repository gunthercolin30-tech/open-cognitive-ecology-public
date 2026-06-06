PRIMITIVE = "semantic_field"
DESCRIPTION = "Semantic field."
DEPENDENCIES = []

import math

from ontology.non_representability import (
    NonRepresentabilityPrimitive,
)


class SemanticField:

    """
    Distributed semantic field.

    Represents a local topological structure where:
    - symbolic meanings interact,
    - compatibility gradients emerge,
    - attractor basins stabilize,
    - global closure remains impossible.
    """

    def __init__(self):

        self.field_nodes = {}

        self.compatibility_matrix = {}

        self.attractor_basins = {}

        self.semantic_gradients = {}

        self.global_closure = False

        self.semantic_field_residual_floor = 0.05
        self.semantic_field_instability_gain = 1.0

        self.non_representability = (
            NonRepresentabilityPrimitive(
                residual_floor=(
                    self.semantic_field_residual_floor
                ),
                instability_gain=(
                    self.semantic_field_instability_gain
                ),
            )
        )

        self.last_non_representability_state = {}

    # =========================================================
    # FIELD UPDATE
    # =========================================================

    def update(
        self,
        local_symbolic_system,
    ):

        local_lexicons = getattr(
            local_symbolic_system,
            "local_lexicons",
            {},
        )

        if not local_lexicons:

            self.field_nodes = {}

            self.compatibility_matrix = {}

            self.attractor_basins = {}

            self.semantic_gradients = {}

            self.global_closure = False

            self.last_non_representability_state = {
                "complexity_gap": 0.0,
                "residual": 0.0,
                "opacity": 0.0,
                "innovation_pressure": 0.0,
                "representational_stability": 1.0,
                "modulated_activation": 1.0,
            }

            return

        world_complexity = (
            1.0
            + len(
                getattr(
                    self,
                    "semantic_regions",
                    {},
                )
            )
            + len(
                getattr(
                    self,
                    "concept_attractors",
                    {},
                )
            )
        )

        model_complexity = (
            1.0
            + len(
                getattr(
                    self,
                    "semantic_fields",
                    {},
                )
            )
        )

        compression_ratio = 1.0

        self.last_non_representability_state = (
            self.non_representability.step(
                model_complexity=model_complexity,
                world_complexity=world_complexity,
                compression_ratio=compression_ratio,
            )
        )

        semantic_activation = (
            self.last_non_representability_state[
                "modulated_activation"
            ]
        )

        self._extract_field_nodes(
            local_symbolic_system
        )

        self._compute_compatibility_matrix()

        self._compute_semantic_gradients()

        self._identify_attractor_basins()

        for symbol in (
            self.semantic_gradients.keys()
        ):
            self.semantic_gradients[
                symbol
            ] *= semantic_activation

        for symbol, basin in (
            self.attractor_basins.items()
        ):
            basin["gradient"] *= (
                semantic_activation
            )

            basin["stability"] = min(
                1.0,
                basin["stability"]
                * semantic_activation,
            )

        agents = getattr(
            local_symbolic_system,
            "agents",
            [],
        )

        for agent in agents:

            agent.semantic_representation_residual = (
                self.last_non_representability_state[
                    "residual"
                ]
            )

            agent.semantic_innovation_pressure = (
                self.last_non_representability_state[
                    "innovation_pressure"
                ]
            )

            agent.semantic_representational_stability = (
                self.last_non_representability_state[
                    "representational_stability"
                ]
            )

            if hasattr(
                agent,
                "symbolic_activation",
            ):
                agent.symbolic_activation *= (
                    semantic_activation
                )

        self.global_closure = False

    # =========================================================
    # NODE EXTRACTION
    # =========================================================

    def _extract_field_nodes(
        self,
        local_symbolic_system,
    ):

        self.field_nodes = {}

        for agent_name, lexicon in (
            local_symbolic_system
            .local_lexicons
            .items()
        ):
            for symbol, value in lexicon.items():

                node = self.field_nodes.get(
                    symbol,
                    {
                        "weight": 0.0,
                        "count": 0,
                    },
                )

                node["weight"] += value.get(
                    "weight",
                    0.0,
                )

                node["count"] += 1

                self.field_nodes[symbol] = node

    # =========================================================
    # COMPATIBILITY MATRIX
    # =========================================================

    def _compute_compatibility_matrix(
        self,
    ):

        self.compatibility_matrix = {}

        symbols = list(
            self.field_nodes.keys()
        )

        for i, symbol_a in enumerate(symbols):
            for symbol_b in symbols[i + 1:]:

                weight_a = self.field_nodes[
                    symbol_a
                ]["weight"]

                weight_b = self.field_nodes[
                    symbol_b
                ]["weight"]

                compatibility = 1.0 / (
                    1.0
                    + abs(
                        weight_a - weight_b
                    )
                )

                self.compatibility_matrix[
                    (symbol_a, symbol_b)
                ] = compatibility

    # =========================================================
    # SEMANTIC GRADIENTS
    # =========================================================

    def _compute_semantic_gradients(
        self,
    ):

        self.semantic_gradients = {}

        for symbol, node in (
            self.field_nodes.items()
        ):
            self.semantic_gradients[
                symbol
            ] = math.log(
                1.0
                + abs(
                    node["weight"]
                )
                + node["count"]
            )

    # =========================================================
    # ATTRACTOR BASINS
    # =========================================================

    def _identify_attractor_basins(
        self,
    ):

        self.attractor_basins = {}

        for symbol, gradient in (
            self.semantic_gradients.items()
        ):
            if gradient < 1.0:
                continue

            self.attractor_basins[
                symbol
            ] = {
                "gradient": gradient,
                "stability": min(
                    1.0,
                    gradient / 5.0,
                ),
            }