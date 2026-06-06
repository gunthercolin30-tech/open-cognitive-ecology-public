PRIMITIVE = "symbolic_generation"
DESCRIPTION = "Symbolic generation."
DEPENDENCIES = []

import random

from ontology.non_representability import (
    NonRepresentabilityPrimitive,
)


class SymbolicGenerationMixin:

    def __init__(self):

        self.symbol_generation_residual_floor = 0.05
        self.symbol_generation_instability_gain = 1.0

        self.non_representability = (
            NonRepresentabilityPrimitive(
                residual_floor=(
                    self.symbol_generation_residual_floor
                ),
                instability_gain=(
                    self.symbol_generation_instability_gain
                ),
            )
        )

        self.last_non_representability_state = {}

    # =========================================================
    # SYMBOL GENERATION
    # =========================================================

    def _generate_local_symbols(
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
                    "symbolic_history",
                    [],
                )
            )
            + len(
                getattr(
                    self,
                    "local_lexicons",
                    {},
                )
            )
        )

        model_complexity = (
            1.0
            + len(
                getattr(
                    self,
                    "symbol_statistics",
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

        generation_activation = (
            self.last_non_representability_state[
                "modulated_activation"
            ]
        )

        if hasattr(
            self,
            "symbol_creation_probability",
        ):
            self.symbol_creation_probability *= (
                generation_activation
            )

        if hasattr(
            self,
            "symbolic_mutation_rate",
        ):
            self.symbolic_mutation_rate *= (
                generation_activation
            )

        for agent in agents:

            probability = (
                0.002
                + agent.symbolic_drift
                * 0.01
                + agent.mythological_pressure
                * 0.005
            )

            probability *= (
                generation_activation
            )

            if (
                random.random()
                <= probability
            ):

                symbol = self._generate_symbol()

                symbolic_weight = random.uniform(
                    -1.0,
                    1.0,
                )

                lexicon = self.local_lexicons.get(
                    agent.state["name"],
                    {},
                )

                lexicon[symbol] = {
                    "weight": symbolic_weight,
                    "drift": random.uniform(
                        0.0,
                        1.0,
                    ),
                    "cycle": (
                        agent.state["cycle"]
                    ),
                }

                self.local_lexicons[
                    agent.state["name"]
                ] = lexicon

                agent.symbolic_patterns[
                    symbol
                ] = symbolic_weight

            agent.symbol_generation_representation_residual = (
                self.last_non_representability_state[
                    "residual"
                ]
            )

            agent.symbol_generation_innovation_pressure = (
                self.last_non_representability_state[
                    "innovation_pressure"
                ]
            )

            agent.symbol_generation_representational_stability = (
                self.last_non_representability_state[
                    "representational_stability"
                ]
            )

            if hasattr(
                agent,
                "symbolic_activation",
            ):
                agent.symbolic_activation *= (
                    generation_activation
                )

    def _generate_symbol(
        self,
    ):

        alphabet = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )

        size = random.randint(
            2,
            6,
        )

        return "".join(
            random.choice(alphabet)
            for _ in range(size)
        )