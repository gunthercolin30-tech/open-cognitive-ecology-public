PRIMITIVE = "semantic_propagation"
DESCRIPTION = "Semantic propagation."
DEPENDENCIES = []

import random

from ontology.non_representability import (
    NonRepresentabilityPrimitive,
)


class SemanticPropagationMixin:

    def __init__(self):

        self.semantic_propagation_residual_floor = 0.05
        self.semantic_propagation_instability_gain = 1.0

        self.non_representability = (
            NonRepresentabilityPrimitive(
                residual_floor=(
                    self.semantic_propagation_residual_floor
                ),
                instability_gain=(
                    self.semantic_propagation_instability_gain
                ),
            )
        )

        self.last_non_representability_state = {}

    # =========================================================
    # SEMANTIC PROPAGATION
    # =========================================================

    def _propagate_semantic_fields(
        self,
        agents,
    ):

        if not agents:
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
                    "semantic_fluxes",
                    [],
                )
            )
            + len(
                getattr(
                    self,
                    "field_nodes",
                    {},
                )
            )
        )

        model_complexity = (
            1.0
            + len(
                getattr(
                    self,
                    "compatibility_matrix",
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

        propagation_activation = (
            self.last_non_representability_state[
                "modulated_activation"
            ]
        )

        if hasattr(
            self,
            "semantic_exchange_rate",
        ):
            self.semantic_exchange_rate *= (
                propagation_activation
            )

        for agent in agents:

            nearby_agents = (
                self._find_local_agents(
                    agent,
                    agents,
                    radius=6.0,
                )
            )

            source_lexicon = (
                self.local_lexicons.get(
                    agent.state["name"],
                    {},
                )
            )

            if source_lexicon:

                for other in nearby_agents:

                    if other is agent:
                        continue

                    propagation_probability = (
                        0.01
                        + agent.local_coherence
                        * 0.01
                        + agent.transmission_drive
                        * 0.02
                    )

                    if hasattr(
                        self,
                        "propagation_probability",
                    ):
                        self.propagation_probability *= (
                            propagation_activation
                        )

                    propagation_probability *= (
                        propagation_activation
                    )

                    if (
                        random.random()
                        <= propagation_probability
                    ):

                        symbol = random.choice(
                            list(
                                source_lexicon.keys()
                            )
                        )

                        propagated = (
                            self._mutate_symbolic_meaning(
                                source_lexicon[symbol]
                            )
                        )

                        target_lexicon = (
                            self.local_lexicons.get(
                                other.state["name"],
                                {},
                            )
                        )

                        target_lexicon[symbol] = (
                            propagated
                        )

                        self.local_lexicons[
                            other.state["name"]
                        ] = target_lexicon

                        other.symbolic_drift += (
                            random.uniform(
                                0.01,
                                0.05,
                            )
                        )

            agent.semantic_propagation_residual = (
                self.last_non_representability_state[
                    "residual"
                ]
            )

            agent.semantic_propagation_innovation_pressure = (
                self.last_non_representability_state[
                    "innovation_pressure"
                ]
            )

            agent.semantic_propagation_representational_stability = (
                self.last_non_representability_state[
                    "representational_stability"
                ]
            )

            if hasattr(
                agent,
                "symbolic_activation",
            ):
                agent.symbolic_activation *= (
                    propagation_activation
                )

    # =========================================================
    # SEMANTIC MUTATION
    # =========================================================

    def _mutate_symbolic_meaning(
        self,
        symbolic_entry,
    ):

        mutated = dict(symbolic_entry)

        mutated["weight"] += (
            random.uniform(
                -0.3,
                0.3,
            )
        )

        mutated["drift"] += (
            random.uniform(
                -0.2,
                0.2,
            )
        )

        mutated["mutation"] = True

        return mutated