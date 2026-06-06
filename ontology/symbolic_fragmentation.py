PRIMITIVE = "symbolic_fragmentation"
DESCRIPTION = "Symbolic fragmentation."
DEPENDENCIES = []

import random

from ontology.non_representability import (
    NonRepresentabilityPrimitive,
)


class SymbolicFragmentationMixin:

    def __init__(self):

        self.fragmentation_residual_floor = 0.05
        self.fragmentation_instability_gain = 1.0

        self.non_representability = (
            NonRepresentabilityPrimitive(
                residual_floor=(
                    self.fragmentation_residual_floor
                ),
                instability_gain=(
                    self.fragmentation_instability_gain
                ),
            )
        )

        self.last_non_representability_state = {}

    # =========================================================
    # SYMBOLIC FRAGMENTATION
    # =========================================================

    def _fragment_symbolic_regions(
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
                    "fragmentation_events",
                    [],
                )
            )
            + len(
                getattr(
                    self,
                    "symbolic_branches",
                    {},
                )
            )
        )

        model_complexity = (
            1.0
            + len(
                getattr(
                    self,
                    "fragmentation_memory",
                    [],
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

        fragmentation_activation = (
            self.last_non_representability_state[
                "modulated_activation"
            ]
        )

        if hasattr(
            self,
            "semantic_fragmentation_rate",
        ):
            self.semantic_fragmentation_rate *= (
                fragmentation_activation
            )

        for agent in agents:

            nearby_agents = (
                self._find_local_agents(
                    agent,
                    agents,
                    radius=7.0,
                )
            )

            fragmentation_pressure = 0.0

            for other in nearby_agents:

                if other is agent:
                    continue

                incompatibility = (
                    1.0
                    - self._semantic_compatibility(
                        agent,
                        other,
                    )
                )

                fragmentation_pressure += (
                    incompatibility
                )

            fragmentation_probability = (
                fragmentation_pressure
                * 0.003
                + self.semantic_fragmentation_rate
            )

            if (
                random.random()
                > fragmentation_probability
            ):
                agent.fragmentation_representation_residual = (
                    self.last_non_representability_state[
                        "residual"
                    ]
                )

                agent.fragmentation_innovation_pressure = (
                    self.last_non_representability_state[
                        "innovation_pressure"
                    ]
                )

                agent.fragmentation_representational_stability = (
                    self.last_non_representability_state[
                        "representational_stability"
                    ]
                )

                if hasattr(
                    agent,
                    "symbolic_activation",
                ):
                    agent.symbolic_activation *= (
                        fragmentation_activation
                    )

                continue

            agent.symbolic_drift += (
                random.uniform(
                    0.05,
                    0.2,
                )
            )

            agent.semiotic_instability += (
                random.uniform(
                    0.02,
                    0.1,
                )
            )

            agent.cultural_fragmentation += (
                random.uniform(
                    0.02,
                    0.1,
                )
            )

            agent.fragmentation_representation_residual = (
                self.last_non_representability_state[
                    "residual"
                ]
            )

            agent.fragmentation_innovation_pressure = (
                self.last_non_representability_state[
                    "innovation_pressure"
                ]
            )

            agent.fragmentation_representational_stability = (
                self.last_non_representability_state[
                    "representational_stability"
                ]
            )

            if hasattr(
                agent,
                "symbolic_activation",
            ):
                agent.symbolic_activation *= (
                    fragmentation_activation
                )