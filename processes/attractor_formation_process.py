# processes/attractor_formation_process.py

from cognitive_graph.attractors import (
    DistributedAttractorEngine
)


class AttractorFormationProcess:

    def __init__(
        self,
        graph,
        activation_threshold=0.6,
        salience_threshold=0.5,
        reinforcement_rate=0.02,
        decay_rate=0.005,
    ):

        self.graph = graph

        # =====================================================
        # LEGACY PARAMETERS
        # =====================================================

        self.activation_threshold = (
            activation_threshold
        )

        self.salience_threshold = (
            salience_threshold
        )

        self.reinforcement_rate = (
            reinforcement_rate
        )

        self.decay_rate = (
            decay_rate
        )

        # =====================================================
        # DISTRIBUTED ECOLOGICAL ATTRACTORS
        # =====================================================

        self.engine = (
            DistributedAttractorEngine(

                attractor_threshold=(
                    activation_threshold * 0.75
                ),

                attractor_growth=(
                    reinforcement_rate
                ),

                minimum_attractor_strength=(
                    decay_rate
                ),
            )
        )

    # =========================================================
    # PROCESS EXECUTION
    # =========================================================

    async def run(self):

        # =====================================================
        # ECOLOGICAL ATTRACTOR DYNAMICS
        # =====================================================

        self.engine.tick(
            self.graph
        )

        # =====================================================
        # OBSERVATION TRACES
        # =====================================================

        self._emit_ecological_traces()

    # =========================================================
    # FIELD OBSERVATION
    # =========================================================

    def _emit_ecological_traces(
        self,
    ):

        active_regions = []

        for node_id, node in (
            self.graph.nodes.items()
        ):

            strength = getattr(
                node,
                "attractor_strength",
                0.0,
            )

            if strength <= 0.05:
                continue

            habitat = (
                self.graph
                .cognitive_habitats
                .get(
                    node_id,
                    {}
                )
            )

            ecology = (
                self.graph
                .get_ecological_state(
                    node_id
                )
            )

            active_regions.append(
                (
                    node_id,
                    strength,
                    habitat.get(
                        "type",
                        "unknown",
                    ),
                    ecology.get(
                        "migration_potential",
                        0.0,
                    ),
                    ecology.get(
                        "retention",
                        0.0,
                    ),
                )
            )

        active_regions.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        for (
            node_id,
            strength,
            habitat_type,
            migration,
            retention,
        ) in active_regions[:10]:

            print(
                "[ATTRACTOR_FIELD]",

                f"node={node_id}",

                f"strength="
                f"{strength:.2f}",

                f"habitat="
                f"{habitat_type}",

                f"migration="
                f"{migration:.2f}",

                f"retention="
                f"{retention:.2f}",
            )