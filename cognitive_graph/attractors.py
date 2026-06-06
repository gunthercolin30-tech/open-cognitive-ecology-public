# cognitive_graph/attractors.py

import math
import random
import time


class DistributedAttractorEngine:
    """
    Distributed ecological attractors.

    This system does NOT:
    - create central hubs
    - enforce global convergence
    - control cognition

    It only produces:
    - local metastable retention
    - ecological sink formation
    - distributed attractor competition
    - reversible stabilization fields
    - dissipative ecological persistence
    """

    def __init__(
        self,
        attractor_threshold=0.45,
        attractor_decay=0.992,
        attractor_growth=0.025,
        migration_sensitivity=0.35,
        ecological_coupling=0.25,
        competitive_inhibition=0.15,
        minimum_attractor_strength=0.01,

        # =====================================================
        # DISSIPATIVE ECOLOGY
        # =====================================================

        maintenance_cost_factor=0.015,
        attractor_fatigue_gain=0.012,
        attractor_fatigue_decay=0.996,

        saturation_gain=0.010,
        saturation_decay=0.997,

        collapse_probability_factor=0.020,

        propagation_decay_factor=0.35,

        ecological_instability_factor=0.20,

        regeneration_rate=0.002,
    ):

        self.attractor_threshold = (
            attractor_threshold
        )

        self.attractor_decay = (
            attractor_decay
        )

        self.attractor_growth = (
            attractor_growth
        )

        self.migration_sensitivity = (
            migration_sensitivity
        )

        self.ecological_coupling = (
            ecological_coupling
        )

        self.competitive_inhibition = (
            competitive_inhibition
        )

        self.minimum_attractor_strength = (
            minimum_attractor_strength
        )

        # =====================================================
        # DISSIPATIVE PARAMETERS
        # =====================================================

        self.maintenance_cost_factor = (
            maintenance_cost_factor
        )

        self.attractor_fatigue_gain = (
            attractor_fatigue_gain
        )

        self.attractor_fatigue_decay = (
            attractor_fatigue_decay
        )

        self.saturation_gain = (
            saturation_gain
        )

        self.saturation_decay = (
            saturation_decay
        )

        self.collapse_probability_factor = (
            collapse_probability_factor
        )

        self.propagation_decay_factor = (
            propagation_decay_factor
        )

        self.ecological_instability_factor = (
            ecological_instability_factor
        )

        self.regeneration_rate = (
            regeneration_rate
        )

    # =========================================================
    # GLOBAL ATTRACTOR TICK
    # =========================================================

    def tick(
        self,
        graph,
    ):

        self._maintain_ecology(
            graph
        )

        self._decay_attractors(
            graph
        )

        self._emerge_attractors(
            graph
        )

        self._propagate_attractor_fields(
            graph
        )

        self._apply_competitive_inhibition(
            graph
        )

        self._apply_local_collapses(
            graph
        )

    # =========================================================
    # ECOLOGICAL MAINTENANCE
    # =========================================================

    def _maintain_ecology(
        self,
        graph,
    ):

        for node in graph.nodes.values():

            if not hasattr(
                node,
                "attractor_fatigue",
            ):

                node.attractor_fatigue = 0.0

            if not hasattr(
                node,
                "attractor_saturation",
            ):

                node.attractor_saturation = 0.0

            if not hasattr(
                node,
                "ecological_regeneration",
            ):

                node.ecological_regeneration = 1.0

            strength = getattr(
                node,
                "attractor_strength",
                0.0,
            )

            # =================================================
            # FATIGUE
            # =================================================

            node.attractor_fatigue *= (
                self.attractor_fatigue_decay
            )

            node.attractor_fatigue += (
                strength
                * self.attractor_fatigue_gain
            )

            # =================================================
            # SATURATION
            # =================================================

            node.attractor_saturation *= (
                self.saturation_decay
            )

            node.attractor_saturation += (
                strength
                * self.saturation_gain
            )

            # =================================================
            # ECOLOGICAL REGENERATION
            # =================================================

            ecological_pressure = (

                node.attractor_fatigue * 0.5

                + node.attractor_saturation * 0.5
            )

            node.ecological_regeneration += (
                self.regeneration_rate
            )

            node.ecological_regeneration -= (
                ecological_pressure
                * 0.01
            )

            node.ecological_regeneration = max(
                0.05,
                min(
                    1.0,
                    node.ecological_regeneration,
                ),
            )

            # =================================================
            # MAINTENANCE COST
            # =================================================

            maintenance_cost = (

                strength
                * self.maintenance_cost_factor
            )

            node.activation -= (
                maintenance_cost
            )

            node.salience -= (
                maintenance_cost
                * 0.5
            )

            node.tension += (
                maintenance_cost
                * 0.25
            )

            # =================================================
            # FLOOR STABILITY
            # =================================================

            node.activation = max(
                0.0,
                node.activation,
            )

            node.salience = max(
                0.0,
                node.salience,
            )

    # =========================================================
    # ATTRACTOR DECAY
    # =========================================================

    def _decay_attractors(
        self,
        graph,
    ):

        for node in graph.nodes.values():

            current = getattr(
                node,
                "attractor_strength",
                0.0,
            )

            fatigue = getattr(
                node,
                "attractor_fatigue",
                0.0,
            )

            saturation = getattr(
                node,
                "attractor_saturation",
                0.0,
            )

            ecological_regeneration = getattr(
                node,
                "ecological_regeneration",
                1.0,
            )

            decay_modifier = (

                1.0

                - (
                    fatigue
                    * 0.05
                )

                - (
                    saturation
                    * 0.05
                )
            )

            decay_modifier *= (
                ecological_regeneration
            )

            current *= (
                self.attractor_decay
            )

            current *= max(
                0.05,
                decay_modifier,
            )

            if (
                current
                < self.minimum_attractor_strength
            ):
                current = 0.0

            node.attractor_strength = (
                current
            )

    # =========================================================
    # ATTRACTOR EMERGENCE
    # =========================================================

    def _emerge_attractors(
        self,
        graph,
    ):

        for node_id, node in (
            graph.nodes.items()
        ):

            habitat = (
                graph.cognitive_habitats.get(
                    node_id,
                    {}
                )
            )

            ecology = (
                graph.get_ecological_state(
                    node_id
                )
            )

            activation = getattr(
                node,
                "activation",
                0.0,
            )

            salience = getattr(
                node,
                "salience",
                0.0,
            )

            tension = getattr(
                node,
                "tension",
                0.0,
            )

            migration = ecology.get(
                "migration_potential",
                0.0,
            )

            retention = ecology.get(
                "retention",
                0.0,
            )

            corridor_flow = habitat.get(
                "corridor_flow",
                0.0,
            )

            fatigue = getattr(
                node,
                "attractor_fatigue",
                0.0,
            )

            saturation = getattr(
                node,
                "attractor_saturation",
                0.0,
            )

            ecological_regeneration = getattr(
                node,
                "ecological_regeneration",
                1.0,
            )

            ecological_stability = (

                activation * 0.30

                + salience * 0.25

                + retention * 0.25

                + corridor_flow * 0.15

                - tension * 0.10

                - migration * 0.10
            )

            # =================================================
            # ECOLOGICAL INSTABILITY
            # =================================================

            ecological_instability = (

                fatigue * 0.5

                + saturation * 0.5
            )

            ecological_stability -= (
                ecological_instability
                * self.ecological_instability_factor
            )

            ecological_stability *= (
                ecological_regeneration
            )

            if (
                ecological_stability
                < self.attractor_threshold
            ):
                continue

            local_growth = (

                ecological_stability

                * self.attractor_growth
            )

            local_growth *= random.uniform(
                0.9,
                1.1,
            )

            node.attractor_strength += (
                local_growth
            )

    # =========================================================
    # FIELD PROPAGATION
    # =========================================================

    def _propagate_attractor_fields(
        self,
        graph,
    ):

        field_updates = []

        for node_id, node in (
            graph.nodes.items()
        ):

            strength = getattr(
                node,
                "attractor_strength",
                0.0,
            )

            if strength <= 0.0:
                continue

            fatigue = getattr(
                node,
                "attractor_fatigue",
                0.0,
            )

            saturation = getattr(
                node,
                "attractor_saturation",
                0.0,
            )

            propagation_modifier = (

                1.0

                - (
                    fatigue
                    * self.propagation_decay_factor
                )

                - (
                    saturation
                    * self.propagation_decay_factor
                )
            )

            propagation_modifier = max(
                0.05,
                propagation_modifier,
            )

            neighbors = graph.neighbors(
                node_id
            )

            for edge in neighbors:

                target = edge.target

                ecological_bias = (
                    self._compute_ecological_affinity(
                        graph,
                        node_id,
                        target.id,
                    )
                )

                propagated_field = (

                    strength

                    * edge.weight

                    * 0.08

                    * ecological_bias

                    * propagation_modifier
                )

                if (
                    propagated_field
                    <= 0.0
                ):
                    continue

                field_updates.append(
                    (
                        target,
                        propagated_field,
                    )
                )

        for target, propagated_field in (
            field_updates
        ):

            target.attractor_strength += (
                propagated_field
            )

    # =========================================================
    # ECOLOGICAL AFFINITY
    # =========================================================

    def _compute_ecological_affinity(
        self,
        graph,
        source_id,
        target_id,
    ):

        source_habitat = (
            graph.cognitive_habitats.get(
                source_id,
                {}
            )
        )

        target_habitat = (
            graph.cognitive_habitats.get(
                target_id,
                {}
            )
        )

        source_type = (
            source_habitat.get(
                "type",
                "transitional",
            )
        )

        target_type = (
            target_habitat.get(
                "type",
                "transitional",
            )
        )

        affinity = 1.0

        if (
            source_type
            == target_type
        ):

            affinity += 0.35

        if (
            source_type
            == "exploratory"
            and
            target_type
            == "migratory"
        ):

            affinity += 0.25

        if (
            source_type
            == "attractive"
            and
            target_type
            == "attractive"
        ):

            affinity += 0.20

        if (
            target_type
            == "unstable"
        ):

            affinity *= 0.75

        return affinity

    # =========================================================
    # COMPETITIVE ECOLOGY
    # =========================================================

    def _apply_competitive_inhibition(
        self,
        graph,
    ):

        for node_id, node in (
            graph.nodes.items()
        ):

            local_strength = getattr(
                node,
                "attractor_strength",
                0.0,
            )

            if local_strength <= 0.0:
                continue

            neighboring_strength = 0.0

            neighboring_count = 0

            for edge in graph.neighbors(
                node_id
            ):

                target = edge.target

                neighboring_strength += getattr(
                    target,
                    "attractor_strength",
                    0.0,
                )

                neighboring_count += 1

            if neighboring_count <= 0:
                continue

            neighboring_strength /= (
                neighboring_count
            )

            inhibition = (

                neighboring_strength

                * self.competitive_inhibition
            )

            fatigue = getattr(
                node,
                "attractor_fatigue",
                0.0,
            )

            inhibition *= (
                1.0
                + fatigue
            )

            node.attractor_strength -= (
                inhibition
            )

            if (
                node.attractor_strength
                < 0.0
            ):

                node.attractor_strength = 0.0

    # =========================================================
    # LOCAL ECOLOGICAL COLLAPSES
    # =========================================================

    def _apply_local_collapses(
        self,
        graph,
    ):

        for node in graph.nodes.values():

            strength = getattr(
                node,
                "attractor_strength",
                0.0,
            )

            if strength <= 0.0:
                continue

            fatigue = getattr(
                node,
                "attractor_fatigue",
                0.0,
            )

            saturation = getattr(
                node,
                "attractor_saturation",
                0.0,
            )

            collapse_pressure = (

                fatigue * 0.5

                + saturation * 0.5
            )

            collapse_probability = (

                collapse_pressure

                * self.collapse_probability_factor
            )

            if (
                random.random()
                < collapse_probability
            ):

                collapse_factor = random.uniform(
                    0.3,
                    0.7,
                )

                node.attractor_strength *= (
                    collapse_factor
                )

                node.tension += (
                    (1.0 - collapse_factor)
                    * 0.25
                )

                print(
                    "[ATTRACTOR_COLLAPSE]",

                    node.id,

                    f"collapse_factor="
                    f"{collapse_factor:.2f}",

                    f"fatigue="
                    f"{fatigue:.2f}",

                    f"saturation="
                    f"{saturation:.2f}",
                )