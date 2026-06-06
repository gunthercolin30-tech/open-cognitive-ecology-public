PRIMITIVE = "grammar_dynamics"
DESCRIPTION = "Grammar dynamics."
DEPENDENCIES = []

import random

from ontology.non_representability import (
    NonRepresentabilityPrimitive,
)


class GrammarDynamicsMixin:

    def __init__(self):

        self.grammar_residual_floor = 0.05
        self.grammar_instability_gain = 1.0

        self.non_representability = (
            NonRepresentabilityPrimitive(
                residual_floor=(
                    self.grammar_residual_floor
                ),
                instability_gain=(
                    self.grammar_instability_gain
                ),
            )
        )

        self.last_non_representability_state = {}

    # =========================================================
    # GRAMMATICAL MUTATION
    # =========================================================

    def _mutate_grammars(
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
                    "grammar_rules",
                    {},
                )
            )
            + len(
                getattr(
                    self,
                    "grammar_innovations",
                    [],
                )
            )
        )

        model_complexity = (
            1.0
            + len(
                getattr(
                    self,
                    "grammar_statistics",
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

        grammar_activation = (
            self.last_non_representability_state[
                "modulated_activation"
            ]
        )

        if hasattr(
            self,
            "grammar_learning_rate",
        ):
            self.grammar_learning_rate *= (
                grammar_activation
            )

        if hasattr(
            self,
            "rule_creation_probability",
        ):
            self.rule_creation_probability *= (
                grammar_activation
            )

        if hasattr(
            self,
            "grammar_instability",
        ):
            self.grammar_instability *= (
                grammar_activation
            )

        for agent in agents:

            mutation_probability = (
                self.grammar_instability
                + agent.semiotic_instability
                * 0.01
            )

            if (
                random.random()
                <= mutation_probability
            ):

                grammar_key = int(
                    random.uniform(
                        -1000,
                        1000,
                    )
                )

                grammar_state = {
                    "coherence": random.uniform(
                        0.0,
                        1.0,
                    ),
                    "instability": random.uniform(
                        0.0,
                        1.0,
                    ),
                    "cycle": (
                        agent.state["cycle"]
                    ),
                }

                self.grammatical_attractors[
                    grammar_key
                ] = grammar_state

            agent.grammar_representation_residual = (
                self.last_non_representability_state[
                    "residual"
                ]
            )

            agent.grammar_innovation_pressure = (
                self.last_non_representability_state[
                    "innovation_pressure"
                ]
            )

            agent.grammar_representational_stability = (
                self.last_non_representability_state[
                    "representational_stability"
                ]
            )

            if hasattr(
                agent,
                "symbolic_activation",
            ):
                agent.symbolic_activation *= (
                    grammar_activation
                )