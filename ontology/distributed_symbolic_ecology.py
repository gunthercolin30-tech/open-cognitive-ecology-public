PRIMITIVE = "distributed_symbolic_ecology"
DESCRIPTION = "Distributed symbolic ecology."
DEPENDENCIES = []

import random

from ontology.non_representability import (
    NonRepresentabilityPrimitive,
)


class DistributedSymbolicEcology:

    """
    Distributed interactions between local symbolic systems.

    This module introduces:
    - exchanges between symbolic regions,
    - distributed constraint fields,
    - local viability reinforcement,
    - prevention of semantic global closure.
    """

    def __init__(self):

        self.region_links = {}

        self.constraint_topology = {}

        self.semantic_fluxes = []

        self.global_openness = 1.0

        self.exchange_probability = 0.05

        self.constraint_reinforcement = 0.02

        self.max_flux_history = 500

        self.distributed_representation_residual_floor = 0.05

        self.distributed_representation_instability_gain = 1.0

        self.distributed_residual_floor = 0.05

        self.distributed_instability_gain = 1.0

        self.non_representability = (
            NonRepresentabilityPrimitive(
                residual_floor=(
                    self.distributed_residual_floor
                ),
                instability_gain=(
                    self.distributed_instability_gain
                ),
            )
        )

        self.last_non_representability_state = {}

    # =========================================================
    # MAIN EVOLUTION
    # =========================================================

    def evolve(
        self,
        local_symbolic_system,
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
                    "region_links",
                    {},
                )
            )
            + len(
                getattr(
                    self,
                    "constraint_topology",
                    {},
                )
            )
            + len(
                getattr(
                    self,
                    "semantic_fluxes",
                    [],
                )
            )
        )

        model_complexity = (
            1.0
            + len(
                getattr(
                    self,
                    "exchange_history",
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

        distributed_activation = (
            self.last_non_representability_state[
                "modulated_activation"
            ]
        )

        self._update_region_links(
            local_symbolic_system,
            agents,
        )

        self._propagate_constraint_fields(
            local_symbolic_system,
            agents,
        )

        self._generate_semantic_fluxes(
            local_symbolic_system,
            agents,
        )

        self._maintain_global_openness()

        self.global_openness *= (
            distributed_activation
        )

        for agent in agents:

            agent.distributed_representation_residual = (
                self.last_non_representability_state[
                    "residual"
                ]
            )

            agent.distributed_innovation_pressure = (
                self.last_non_representability_state[
                    "innovation_pressure"
                ]
            )

            agent.distributed_representational_stability = (
                self.last_non_representability_state[
                    "representational_stability"
                ]
            )

            if hasattr(
                agent,
                "symbolic_activation",
            ):
                agent.symbolic_activation *= (
                    distributed_activation
                )

    # =========================================================
    # REGION LINKS
    # =========================================================

    def _update_region_links(
        self,
        local_symbolic_system,
        agents,
    ):

        self.region_links.clear()

        for agent in agents:

            region_key = int(
                (agent.x + agent.y) * 0.5
            )

            self.region_links.setdefault(
                region_key,
                [],
            ).append(
                agent.state["name"]
            )

    # =========================================================
    # CONSTRAINT FIELDS
    # =========================================================

    def _propagate_constraint_fields(
        self,
        local_symbolic_system,
        agents,
    ):

        for region_key, members in (
            self.region_links.items()
        ):

            primitive_count = 0

            for name in members:

                lexicon = (
                    local_symbolic_system
                    .local_lexicons
                    .get(name, {})
                )

                for symbol in lexicon:

                    if (
                        local_symbolic_system
                        ._is_structural_primitive(
                            symbol
                        )
                    ):
                        primitive_count += 1

            self.constraint_topology[
                region_key
            ] = (
                primitive_count
                * self.constraint_reinforcement
            )

    # =========================================================
    # SEMANTIC FLUXES
    # =========================================================

    def _generate_semantic_fluxes(
        self,
        local_symbolic_system,
        agents,
    ):

        for agent in agents:

            if (
                random.random()
                > self.exchange_probability
            ):
                continue

            region_key = int(
                (agent.x + agent.y) * 0.5
            )

            constraint_level = (
                self.constraint_topology.get(
                    region_key,
                    0.0,
                )
            )

            flux = {
                "cycle": (
                    agent.state["cycle"]
                ),
                "agent": (
                    agent.state["name"]
                ),
                "region": region_key,
                "constraint": (
                    constraint_level
                ),
                "openness": (
                    self.global_openness
                ),
            }

            self.semantic_fluxes.append(
                flux
            )

        if (
            len(self.semantic_fluxes)
            > self.max_flux_history
        ):
            self.semantic_fluxes = (
                self.semantic_fluxes[
                    -self.max_flux_history:
                ]
            )

    # =========================================================
    # GLOBAL OPENNESS
    # =========================================================

    def _maintain_global_openness(
        self,
    ):

        self.global_openness = max(
            0.05,
            1.0
            - len(self.constraint_topology)
            * 0.001,
        )