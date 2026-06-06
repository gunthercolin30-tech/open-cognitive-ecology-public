# cognitive_graph/propagation.py

import random


class PropagationEngine:

    def __init__(
        self,
        graph,
        decay=0.85,
        salience_factor=0.5,
        tension_factor=0.2,
        bifurcation_factor=0.35,
        corridor_factor=0.15,
        ecological_factor=0.25,
        migration_factor=0.30,
        retention_factor=0.20,
        long_range_factor=0.18,

        # =====================================================
        # ECOLOGICAL DISSIPATION
        # =====================================================

        propagation_cost_factor=0.08,
        local_dissipation_factor=0.04,
        saturation_factor=0.30,
        corridor_fatigue_factor=0.20,
        migratory_cost_factor=0.12,
        recursive_damping_factor=0.05,
    ):

        self.graph = graph

        self.decay = decay

        self.salience_factor = (
            salience_factor
        )

        self.tension_factor = (
            tension_factor
        )

        # =====================================================
        # BIFURCATION FIELD
        # =====================================================

        self.bifurcation_factor = (
            bifurcation_factor
        )

        self.corridor_factor = (
            corridor_factor
        )

        # =====================================================
        # ECOLOGICAL CIRCULATION
        # =====================================================

        self.ecological_factor = (
            ecological_factor
        )

        self.migration_factor = (
            migration_factor
        )

        self.retention_factor = (
            retention_factor
        )

        self.long_range_factor = (
            long_range_factor
        )

        # =====================================================
        # DISSIPATIVE ECOLOGY
        # =====================================================

        self.propagation_cost_factor = (
            propagation_cost_factor
        )

        self.local_dissipation_factor = (
            local_dissipation_factor
        )

        self.saturation_factor = (
            saturation_factor
        )

        self.corridor_fatigue_factor = (
            corridor_fatigue_factor
        )

        self.migratory_cost_factor = (
            migratory_cost_factor
        )

        self.recursive_damping_factor = (
            recursive_damping_factor
        )

    # =========================================================
    # PUBLIC PROPAGATION
    # =========================================================

    def propagate_from(
        self,
        node_id,
        intensity=1.0,
        depth=2,
    ):

        visited = set()

        self._propagate(

            node_id=node_id,

            intensity=intensity,

            depth=depth,

            visited=visited,
        )

    # =========================================================
    # INTERNAL PROPAGATION
    # =========================================================

    def _propagate(
        self,
        node_id,
        intensity,
        depth,
        visited,
    ):

        if depth <= 0:
            return

        node = self.graph.get_node(
            node_id
        )

        if node is None:
            return

        # =====================================================
        # LOCAL DISSIPATION
        # =====================================================

        node.activation *= (
            1.0
            - self.local_dissipation_factor
        )

        node.salience *= (
            1.0
            - self.local_dissipation_factor
        )

        node.tension *= (
            1.0
            - (
                self.local_dissipation_factor
                * 0.5
            )
        )

        local_signature = (
            node_id,
            depth,
        )

        if local_signature in visited:
            return

        visited.add(local_signature)

        source_ecology = (
            self.graph.get_ecological_state(
                node_id
            )
        )

        source_pressure = (
            source_ecology.get(
                "pressure",
                0.0,
            )
        )

        source_migration = (
            source_ecology.get(
                "migration_potential",
                0.0,
            )
        )

        source_retention = (
            source_ecology.get(
                "retention",
                0.0,
            )
        )

        # =====================================================
        # LOCAL SATURATION
        # =====================================================

        local_energy = (

            node.activation
            + node.salience
            + node.tension
        )

        saturation = min(
            1.0,
            local_energy * 0.02,
        )

        neighbors = list(
            self.graph.neighbors(
                node_id
            )
        )

        random.shuffle(neighbors)

        for edge in neighbors:

            target = edge.target

            target_ecology = (
                self.graph.get_ecological_state(
                    target.id
                )
            )

            # =================================================
            # BASE PROPAGATION
            # =================================================

            propagated_activation = (

                intensity

                * edge.weight

                * self.decay
            )

            # =================================================
            # PROPAGATION COST
            # =================================================

            propagation_cost = (

                propagated_activation
                * self.propagation_cost_factor
            )

            propagated_activation -= (
                propagation_cost
            )

            # =================================================
            # BIFURCATION RETROACTION
            # =================================================

            bifurcation_boost = (
                self._compute_bifurcation_boost(
                    source_id=node_id,
                    target_id=target.id,
                )
            )

            propagated_activation *= (
                1.0 + bifurcation_boost
            )

            # =================================================
            # CORRIDOR EFFECT
            # =================================================

            corridor_boost = (
                self._compute_corridor_effect(
                    source_id=node_id,
                    target_id=target.id,
                )
            )

            propagated_activation *= (
                1.0 + corridor_boost
            )

            # =================================================
            # CORRIDOR FATIGUE
            # =================================================

            corridor_fatigue = (
                self._compute_corridor_fatigue(
                    source_id=node_id,
                    target_id=target.id,
                )
            )

            propagated_activation *= (
                corridor_fatigue
            )

            # =================================================
            # ECOLOGICAL GRADIENT
            # =================================================

            ecological_gradient = (
                self._compute_ecological_gradient(
                    source_pressure,
                    target_ecology,
                )
            )

            propagated_activation *= (
                1.0 + ecological_gradient
            )

            # =================================================
            # MIGRATORY DRIFT
            # =================================================

            migratory_drift = (
                self._compute_migratory_drift(
                    source_migration,
                    target_ecology,
                )
            )

            propagated_activation *= (
                1.0 + migratory_drift
            )

            # =================================================
            # MIGRATORY COST
            # =================================================

            migratory_cost = (
                abs(migratory_drift)
                * self.migratory_cost_factor
            )

            propagated_activation *= (
                max(
                    0.1,
                    1.0 - migratory_cost,
                )
            )

            # =================================================
            # RETENTION RESISTANCE
            # =================================================

            retention_resistance = (
                self._compute_retention_resistance(
                    source_retention
                )
            )

            propagated_activation *= (
                retention_resistance
            )

            # =================================================
            # LONG RANGE CIRCULATION
            # =================================================

            long_range_boost = (
                self._compute_long_range_effect(
                    source_id=node_id,
                    target_id=target.id,
                )
            )

            propagated_activation *= (
                1.0 + long_range_boost
            )

            # =================================================
            # SATURATION DAMPING
            # =================================================

            saturation_damping = (

                1.0

                - (
                    saturation
                    * self.saturation_factor
                )
            )

            propagated_activation *= (
                max(
                    0.05,
                    saturation_damping,
                )
            )

            # =================================================
            # STOCHASTIC ECOLOGICAL VARIATION
            # =================================================

            ecological_noise = (
                random.uniform(
                    0.95,
                    1.05,
                )
            )

            propagated_activation *= (
                ecological_noise
            )

            # =================================================
            # SECONDARY FIELDS
            # =================================================

            propagated_salience = (

                propagated_activation

                * self.salience_factor
            )

            propagated_tension = (

                propagated_activation

                * self.tension_factor
            )

            # =================================================
            # ECOLOGICAL AMPLIFICATION
            # =================================================

            permeability = (
                target_ecology.get(
                    "permeability",
                    1.0,
                )
            )

            propagated_salience *= (
                permeability
            )

            propagated_tension *= (
                1.0
                + migratory_drift
            )

            # =================================================
            # FIELD UPDATE
            # =================================================

            target.activation += (
                propagated_activation
            )

            target.salience += (
                propagated_salience
            )

            target.tension += (
                propagated_tension
            )

            # =================================================
            # TRACE
            # =================================================

            print(
                "[DISSIPATIVE_PROPAGATION]",

                f"{node_id} -> {target.id}",

                f"activation="
                f"{target.activation:.2f}",

                f"saturation="
                f"{saturation:.2f}",

                f"fatigue="
                f"{corridor_fatigue:.2f}",

                f"cost="
                f"{propagation_cost:.2f}",

                f"migration_cost="
                f"{migratory_cost:.2f}",
            )

            # =================================================
            # RECURSIVE ECOLOGICAL PROPAGATION
            # =================================================

            recursive_damping = (

                1.0

                - (
                    depth
                    * self.recursive_damping_factor
                )
            )

            recursive_intensity = (
                propagated_activation
                * recursive_damping
            )

            if recursive_intensity <= 0.01:
                continue

            self._propagate(

                node_id=target.id,

                intensity=recursive_intensity,

                depth=depth - 1,

                visited=visited,
            )

    # =========================================================
    # BIFURCATION RETROACTION
    # =========================================================

    def _compute_bifurcation_boost(
        self,
        source_id,
        target_id,
    ):

        boost = 0.0

        for bifurcation in (
            self.graph
            .get_active_bifurcations()
        ):

            if (
                bifurcation["source"]
                == source_id
                and
                bifurcation["target"]
                == target_id
            ):

                boost += (

                    bifurcation["energy"]

                    * self.bifurcation_factor
                )

        return boost

    # =========================================================
    # CORRIDOR EFFECT
    # =========================================================

    def _compute_corridor_effect(
        self,
        source_id,
        target_id,
    ):

        corridor_strength = 0.0

        matching_branches = 0

        for bifurcation in (
            self.graph
            .get_active_bifurcations()
        ):

            if (
                bifurcation["source"]
                == source_id
                and
                bifurcation["target"]
                == target_id
            ):

                corridor_strength += (
                    bifurcation["stability"]
                )

                matching_branches += 1

        if matching_branches == 0:
            return 0.0

        corridor_strength /= (
            matching_branches
        )

        return (
            corridor_strength
            * self.corridor_factor
        )

    # =========================================================
    # CORRIDOR FATIGUE
    # =========================================================

    def _compute_corridor_fatigue(
        self,
        source_id,
        target_id,
    ):

        corridor_flow = (
            self.graph.get_corridor_flow(
                source_id,
                target_id,
            )
        )

        fatigue = (

            1.0

            - (
                corridor_flow
                * self.corridor_fatigue_factor
            )
        )

        return max(
            0.15,
            fatigue,
        )

    # =========================================================
    # ECOLOGICAL GRADIENTS
    # =========================================================

    def _compute_ecological_gradient(
        self,
        source_pressure,
        target_ecology,
    ):

        target_pressure = (
            target_ecology.get(
                "pressure",
                0.0,
            )
        )

        target_retention = (
            target_ecology.get(
                "retention",
                0.0,
            )
        )

        gradient = (

            source_pressure * 0.6

            - target_pressure * 0.3

            + target_retention * 0.2
        )

        return (
            gradient
            * self.ecological_factor
        )

    # =========================================================
    # MIGRATORY DRIFT
    # =========================================================

    def _compute_migratory_drift(
        self,
        source_migration,
        target_ecology,
    ):

        target_migration = (
            target_ecology.get(
                "migration_potential",
                0.0,
            )
        )

        target_permeability = (
            target_ecology.get(
                "permeability",
                1.0,
            )
        )

        drift = (

            source_migration * 0.5

            + target_permeability * 0.4

            - target_migration * 0.2
        )

        return (
            drift
            * self.migration_factor
        )

    # =========================================================
    # RETENTION RESISTANCE
    # =========================================================

    def _compute_retention_resistance(
        self,
        source_retention,
    ):

        resistance = (

            1.0

            - (
                source_retention
                * self.retention_factor
            )
        )

        return max(
            0.1,
            resistance,
        )

    # =========================================================
    # LONG RANGE CIRCULATION
    # =========================================================

    def _compute_long_range_effect(
        self,
        source_id,
        target_id,
    ):

        corridor_flow = (
            self.graph.get_corridor_flow(
                source_id,
                target_id,
            )
        )

        return (
            corridor_flow
            * self.long_range_factor
        )