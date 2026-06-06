# processes/spontaneous_reactivation_process.py

import random


class SpontaneousReactivationProcess:

    def __init__(
        self,
        graph,
        propagation_engine,
        interval=3,
    ):

        self.graph = graph

        self.propagation_engine = (
            propagation_engine
        )

        self.interval = interval

        self.counter = 0

    # =========================================================
    # PROCESS EXECUTION
    # =========================================================

    async def run(self):

        self.counter += 1

        if self.counter < self.interval:
            return

        self.counter = 0

        latent_nodes = (
            self.graph.latent_nodes()
        )

        if not latent_nodes:
            return

        random.shuffle(
            latent_nodes
        )

        for node in latent_nodes[:10]:

            ecological_probability = (
                self._compute_reactivation_probability(
                    node
                )
            )

            if (
                random.random()
                < ecological_probability
            ):

                reactivation_energy = (
                    self._compute_reactivation_energy(
                        node
                    )
                )

                self._apply_reactivation(
                    node,
                    reactivation_energy,
                )

                print(
                    "[ECOLOGICAL_REACTIVATION]",

                    node.id,

                    f"activation="
                    f"{node.activation:.2f}",

                    f"salience="
                    f"{node.salience:.2f}",

                    f"migration="
                    f"{node.migration_pressure:.2f}",

                    f"resonance="
                    f"{node.path_resonance:.2f}",
                )

                self.propagation_engine.propagate_from(

                    node.id,

                    intensity=(
                        reactivation_energy
                    )
                )

    # =========================================================
    # ECOLOGICAL PROBABILITY
    # =========================================================

    def _compute_reactivation_probability(
        self,
        node,
    ):

        local_density = (
            self.graph.local_density(
                node.id
            )
        )

        probability = (

            0.03

            + node.salience * 0.04

            + node.tension * 0.03

            + local_density * 0.01

            + node.path_resonance * 0.05

            + node.reactivation_potential * 0.04

            + node.circulation_potential * 0.03

            + node.long_range_activation * 0.02

            + node.migration_trace * 0.03
        )

        return min(
            0.85,
            probability,
        )

    # =========================================================
    # REACTIVATION ENERGY
    # =========================================================

    def _compute_reactivation_energy(
        self,
        node,
    ):

        base_energy = random.uniform(
            0.05,
            0.25,
        )

        ecological_modifier = (

            1.0

            + node.path_resonance * 0.20

            + node.corridor_affinity * 0.15

            + node.reactivation_potential * 0.15
        )

        return (
            base_energy
            * ecological_modifier
        )

    # =========================================================
    # ECOLOGICAL REACTIVATION
    # =========================================================

    def _apply_reactivation(
        self,
        node,
        reactivation_energy,
    ):

        salience_boost = (
            reactivation_energy
            * 0.5
        )

        migration_boost = (
            reactivation_energy
            * 0.15
        )

        resonance_boost = (
            reactivation_energy
            * 0.10
        )

        circulation_boost = (
            reactivation_energy
            * 0.08
        )

        node.activation += (
            reactivation_energy
        )

        node.salience += (
            salience_boost
        )

        node.migration_pressure += (
            migration_boost
        )

        node.path_resonance += (
            resonance_boost
        )

        node.circulation_potential += (
            circulation_boost
        )

        # =====================================================
        # LONG RANGE MEMORY
        # =====================================================

        node.migration_trace *= (
            0.995
        )

        node.migration_trace += (
            reactivation_energy
            * 0.04
        )

        # =====================================================
        # ECOLOGICAL STABILIZATION
        # =====================================================

        node.ecological_stability *= (
            0.997
        )

        node.ecological_stability += (
            node.attractor_strength
            * 0.003
        )

        # =====================================================
        # CORRIDOR AFFINITY
        # =====================================================

        node.corridor_affinity *= (
            0.996
        )

        node.corridor_affinity += (
            node.path_resonance
            * 0.002
        )