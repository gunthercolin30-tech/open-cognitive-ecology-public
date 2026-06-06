# processes/tension_redistribution_process.py

import random


class TensionRedistributionProcess:

    """
    Distributed ecological tension redistribution.

    This process does NOT:
    - regulate globally
    - optimize globally
    - stabilize centrally

    It only produces:
    - local tension relaxation
    - migratory release
    - exploratory opening
    - corridor destabilization
    - peripheral reactivation
    - ecological micro-collapses
    """

    def __init__(
        self,
        graph,

        tension_threshold=1.0,

        redistribution_factor=0.18,

        migration_conversion=0.12,

        exploration_conversion=0.10,

        collapse_probability=0.025,

        relaxation_decay=0.96,

        peripheral_reactivation=0.08,

        corridor_destabilization=0.04,
    ):

        self.graph = graph

        self.tension_threshold = (
            tension_threshold
        )

        self.redistribution_factor = (
            redistribution_factor
        )

        self.migration_conversion = (
            migration_conversion
        )

        self.exploration_conversion = (
            exploration_conversion
        )

        self.collapse_probability = (
            collapse_probability
        )

        self.relaxation_decay = (
            relaxation_decay
        )

        self.peripheral_reactivation = (
            peripheral_reactivation
        )

        self.corridor_destabilization = (
            corridor_destabilization
        )

    # =========================================================
    # PROCESS EXECUTION
    # =========================================================

    async def run(self):

        for node_id, node in (
            self.graph.nodes.items()
        ):

            tension = getattr(
                node,
                "tension",
                0.0,
            )

            if (
                tension
                < self.tension_threshold
            ):
                continue

            self._redistribute_tension(
                node_id,
                node,
            )

    # =========================================================
    # LOCAL REDISTRIBUTION
    # =========================================================

    def _redistribute_tension(
        self,
        node_id,
        node,
    ):

        neighbors = list(
            self.graph.neighbors(
                node_id
            )
        )

        if not neighbors:
            return

        local_release = (

            node.tension
            * self.redistribution_factor
        )

        node.tension *= (
            self.relaxation_decay
        )

        redistributed_energy = (
            local_release
            / len(neighbors)
        )

        for edge in neighbors:

            target = edge.target

            # =================================================
            # MIGRATORY RELEASE
            # =================================================

            migration_energy = (

                redistributed_energy
                * self.migration_conversion
            )

            target.migration_pressure += (
                migration_energy
            )

            # =================================================
            # EXPLORATORY ACTIVATION
            # =================================================

            exploratory_energy = (

                redistributed_energy
                * self.exploration_conversion
            )

            target.activation += (
                exploratory_energy
            )

            target.salience += (
                exploratory_energy
                * 0.5
            )

            # =================================================
            # PERIPHERAL REACTIVATION
            # =================================================

            if (
                getattr(
                    target,
                    "activation",
                    0.0,
                )
                < 0.15
            ):

                target.reactivation_potential += (
                    redistributed_energy
                    * self.peripheral_reactivation
                )

            # =================================================
            # CORRIDOR DESTABILIZATION
            # =================================================

            target.path_resonance *= (
                1.0
                - self.corridor_destabilization
            )

            # =================================================
            # ECOLOGICAL MICRO-COLLAPSE
            # =================================================

            if (
                random.random()
                < self.collapse_probability
            ):

                collapse_factor = random.uniform(
                    0.6,
                    0.9,
                )

                target.activation *= (
                    collapse_factor
                )

                target.salience *= (
                    collapse_factor
                )

                target.attractor_strength *= (
                    collapse_factor
                )

                target.tension += (
                    (
                        1.0
                        - collapse_factor
                    )
                    * 0.3
                )

                print(
                    "[TENSION_COLLAPSE]",

                    target.id,

                    f"collapse="
                    f"{collapse_factor:.2f}",
                )

            print(
                "[TENSION_REDISTRIBUTION]",

                f"{node_id} -> {target.id}",

                f"release="
                f"{redistributed_energy:.2f}",

                f"migration="
                f"{target.migration_pressure:.2f}",

                f"reactivation="
                f"{target.reactivation_potential:.2f}",
            )