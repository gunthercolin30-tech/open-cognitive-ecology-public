PRIMITIVE = "dialect_stabilization"
DESCRIPTION = "Dialect stabilization."
DEPENDENCIES = []

from ontology.non_representability import (
    NonRepresentabilityPrimitive,
)


class DialectStabilizationMixin:

    def __init__(self):

        self.dialect_residual_floor = 0.05
        self.dialect_instability_gain = 1.0

        self.non_representability = (
            NonRepresentabilityPrimitive(
                residual_floor=(
                    self.dialect_residual_floor
                ),
                instability_gain=(
                    self.dialect_instability_gain
                ),
            )
        )

        self.last_non_representability_state = {}

    # =========================================================
    # DIALECT STABILIZATION
    # =========================================================

    def _stabilize_local_dialects(
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
                    "dialect_clusters",
                    {},
                )
            )
            + len(
                getattr(
                    self,
                    "dialect_history",
                    [],
                )
            )
        )

        model_complexity = (
            1.0
            + len(
                getattr(
                    self,
                    "dialect_statistics",
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

        dialect_activation = (
            self.last_non_representability_state[
                "modulated_activation"
            ]
        )

        if hasattr(
            self,
            "dialect_stability_gain",
        ):
            self.dialect_stability_gain *= (
                dialect_activation
            )

        if hasattr(
            self,
            "cluster_threshold",
        ):
            self.cluster_threshold *= (
                dialect_activation
            )

        for agent in agents:

            nearby_agents = (
                self._find_local_agents(
                    agent,
                    agents,
                    radius=5.0,
                )
            )

            compatible_neighbors = 0

            for other in nearby_agents:

                if other is agent:
                    continue

                compatibility = (
                    self._semantic_compatibility(
                        agent,
                        other,
                    )
                )

                if compatibility > 0.5:
                    compatible_neighbors += 1

            if compatible_neighbors > 0:

                stabilization = (
                    compatible_neighbors
                    * 0.003
                )

                stabilization *= (
                    dialect_activation
                )

                dialect_key = int(
                    (
                        agent.x
                        + agent.y
                    )
                    * 0.5
                )

                self.dialect_clusters[
                    dialect_key
                ] = (
                    self.dialect_clusters.get(
                        dialect_key,
                        0,
                    )
                    + stabilization
                )

                agent.cultural_stability += (
                    stabilization
                )

                agent.local_coherence += (
                    stabilization
                )

            agent.dialect_representation_residual = (
                self.last_non_representability_state[
                    "residual"
                ]
            )

            agent.dialect_innovation_pressure = (
                self.last_non_representability_state[
                    "innovation_pressure"
                ]
            )

            agent.dialect_representational_stability = (
                self.last_non_representability_state[
                    "representational_stability"
                ]
            )

            if hasattr(
                agent,
                "symbolic_activation",
            ):
                agent.symbolic_activation *= (
                    dialect_activation
                )

    # =========================================================
    # SEMANTIC COMPATIBILITY
    # =========================================================

    def _semantic_compatibility(
        self,
        agent_a,
        agent_b,
    ):

        drift_distance = abs(
            agent_a.symbolic_drift
            - agent_b.symbolic_drift
        )

        civilizational_distance = abs(
            agent_a.civilizational_signature
            - agent_b.civilizational_signature
        )

        compatibility = (
            1.0
            - drift_distance
            * 0.4
            - civilizational_distance
            * 0.3
        )

        return max(
            0.0,
            min(
                1.0,
                compatibility,
            )
        )