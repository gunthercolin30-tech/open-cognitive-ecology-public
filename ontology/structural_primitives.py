PRIMITIVE = "structural_primitives"
DESCRIPTION = "Structural primitives."
DEPENDENCIES = []

import random

from ontology.non_representability import (
    NonRepresentabilityPrimitive,
)


class StructuralPrimitivesMixin:

    def __init__(self):

        self.structural_residual_floor = 0.05
        self.structural_instability_gain = 1.0

        self.non_representability = (
            NonRepresentabilityPrimitive(
                residual_floor=(
                    self.structural_residual_floor
                ),
                instability_gain=(
                    self.structural_instability_gain
                ),
            )
        )

        self.last_non_representability_state = {}

    def _initialize_structural_primitives(
        self,
    ):

        self.structural_primitives = {
            "NON_CLOSURE": {
                "weight": 2.5,
                "drift": 0.05,
                "primitive": True,
                "stability": 0.95,
            },
            "CONSTRAINT_FIELDS": {
                "weight": 2.4,
                "drift": 0.05,
                "primitive": True,
                "stability": 0.95,
            },
            "NON_REPRESENTABILITY": {
                "weight": 2.3,
                "drift": 0.08,
                "primitive": True,
                "stability": 0.93,
            },
            "CONSTRAINT_INDUCED_DOMAIN": {
                "weight": 2.2,
                "drift": 0.07,
                "primitive": True,
                "stability": 0.93,
            },
            "TRAJECTORIES_WITHOUT_GLOBALITY": {
                "weight": 2.1,
                "drift": 0.08,
                "primitive": True,
                "stability": 0.92,
            },
            "UNSTABLE_CONFIGURATION": {
                "weight": 2.0,
                "drift": 0.10,
                "primitive": True,
                "stability": 0.90,
            },
            "FORMAL_CONSTRAINT_SYSTEMS": {
                "weight": 2.0,
                "drift": 0.07,
                "primitive": True,
                "stability": 0.92,
            },
            "IMPOSSIBILITY_OF_GLOBAL_CLOSURE": {
                "weight": 2.5,
                "drift": 0.05,
                "primitive": True,
                "stability": 0.95,
            },
        }

    def _seed_structural_primitives(
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
                    "structural_primitives",
                    {},
                )
            )
            + len(
                getattr(
                    self,
                    "primitive_history",
                    [],
                )
            )
        )

        model_complexity = (
            1.0
            + len(
                getattr(
                    self,
                    "primitive_statistics",
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

        structural_activation = (
            self.last_non_representability_state[
                "modulated_activation"
            ]
        )

        if hasattr(
            self,
            "primitive_detection_rate",
        ):
            self.primitive_detection_rate *= (
                structural_activation
            )

        if hasattr(
            self,
            "primitive_stability_gain",
        ):
            self.primitive_stability_gain *= (
                structural_activation
            )

        if hasattr(
            self,
            "structural_seed_probability",
        ):
            self.structural_seed_probability *= (
                structural_activation
            )

        for agent in agents:

            probability = (
                self.structural_seed_probability
                + agent.local_coherence
                * self.constraint_field_gain
            )

            if random.random() <= probability:

                primitive_name = random.choice(
                    list(
                        self.structural_primitives.keys()
                    )
                )

                primitive_value = dict(
                    self.structural_primitives[
                        primitive_name
                    ]
                )

                primitive_value["cycle"] = (
                    agent.state["cycle"]
                )

                lexicon = self.local_lexicons.get(
                    agent.state["name"],
                    {},
                )

                existing = lexicon.get(
                    primitive_name
                )

                if (
                    existing is None
                    or existing.get(
                        "weight",
                        0.0,
                    )
                    < primitive_value["weight"]
                ):
                    lexicon[
                        primitive_name
                    ] = primitive_value

                self.local_lexicons[
                    agent.state["name"]
                ] = lexicon

                agent.symbolic_patterns[
                    primitive_name
                ] = primitive_value[
                    "weight"
                ]

                agent.local_coherence += (
                    random.uniform(
                        0.001,
                        0.005,
                    )
                )

                agent.cultural_stability += (
                    random.uniform(
                        0.001,
                        0.004,
                    )
                )

            agent.structural_representation_residual = (
                self.last_non_representability_state[
                    "residual"
                ]
            )

            agent.structural_innovation_pressure = (
                self.last_non_representability_state[
                    "innovation_pressure"
                ]
            )

            agent.structural_representational_stability = (
                self.last_non_representability_state[
                    "representational_stability"
                ]
            )

            if hasattr(
                agent,
                "symbolic_activation",
            ):
                agent.symbolic_activation *= (
                    structural_activation
                )

    def _is_structural_primitive(
        self,
        symbol,
    ):

        return (
            symbol
            in self.structural_primitives
        )