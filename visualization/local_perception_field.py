# visualization/local_perception_field.py

import math
import random


class LocalPerceptionField:

    def __init__(self):

        # =====================================================
        # LOCAL PERCEPTUAL CENTER
        # =====================================================

        self.center_x = 0.0
        self.center_y = 0.0

        # =====================================================
        # LOCAL OBSERVABILITY
        # =====================================================

        self.visibility_radius = 8.0

        self.visibility_jitter = 1.5

        # =====================================================
        # PERCEPTUAL DYNAMICS
        # =====================================================

        self.drift_velocity_x = 0.0
        self.drift_velocity_y = 0.0

        self.drift_inertia = 0.98

        # =====================================================
        # PERCEPTUAL GEOMETRY
        # =====================================================

        self.curvature_phase = random.uniform(
            0.0,
            math.pi * 2.0,
        )

        self.curvature_strength = random.uniform(
            0.04,
            0.18,
        )

        self.shear_strength = random.uniform(
            0.02,
            0.12,
        )

        self.compression_strength = random.uniform(
            0.03,
            0.15,
        )

        self.vortex_warp_strength = random.uniform(
            0.04,
            0.20,
        )

        # =====================================================
        # DISSIPATIVE MEMORY
        # =====================================================

        self.perception_memory = {}

        self.memory_decay = 0.985

        # =====================================================
        # INTER-PHENOMENOLOGICAL HISTORY
        # =====================================================

        self.contamination_trace = 0.0

        self.regime_fragmentation = 0.0

        self.ontological_drift = 0.0

        self.perceptual_saturation = 0.0

        self.interaction_fatigue = 0.0

        self.collapse_residue = 0.0

        self.compatibility_bias = random.uniform(
            -1.0,
            1.0,
        )

        self.local_reality_signature = (
            random.uniform(
                -1.0,
                1.0,
            )
        )

        self.geometric_identity = random.uniform(
            -1.0,
            1.0,
        )

        self.coherence_instability = 0.0

        self.historical_pressure = 0.0

        self.last_perceptual_sync = 0.0

        # =====================================================
        # PERCEPTUAL REGIMES
        # =====================================================

        self.forbidden_zones = []

        self.compatibility_corridors = []

        self.geometry_echoes = []

    # =========================================================
    # PERCEPTION
    # =========================================================

    def perceive(
        self,
        graph,
    ):

        self._update_perceptual_drift(
            graph
        )

        self._update_historical_dynamics()

        perceived_nodes = {}

        # =====================================================
        # NODE PERCEPTION
        # =====================================================

        for node in graph.nodes.values():

            dx = node.x - self.center_x
            dy = node.y - self.center_y

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            visibility_limit = (
                self.visibility_radius
                + random.uniform(
                    -self.visibility_jitter,
                    self.visibility_jitter,
                )
            )

            # =================================================
            # PHENOMENOLOGICAL EXCLUSION
            # =================================================

            if self._is_inside_forbidden_zone(
                node.x,
                node.y,
            ):

                exclusion_probability = min(
                    0.95,

                    0.35

                    + self.regime_fragmentation
                    * 0.25

                    + self.coherence_instability
                    * 0.20
                )

                if (
                    random.random()
                    < exclusion_probability
                ):
                    continue

            # =================================================
            # LOCAL OBSERVABILITY
            # =================================================

            if distance > visibility_limit:
                continue

            # =================================================
            # ECOLOGICAL OCCLUSION
            # =================================================

            occlusion_probability = min(
                0.45,

                (
                    node.turbulence_field * 0.18
                    + node.pressure * 0.03
                    + node.viability_turbulence * 0.25
                )
            )

            # =================================================
            # INTER-PHENOMENOLOGICAL TURBULENCE
            # =================================================

            occlusion_probability += (

                self.contamination_trace
                * 0.12

                + self.interaction_fatigue
                * 0.10

                + self.collapse_residue
                * 0.08
            )

            occlusion_probability = min(
                0.92,
                occlusion_probability,
            )

            if (
                random.random()
                < occlusion_probability
            ):
                continue

            # =================================================
            # BASE DISTORTION
            # =================================================

            distortion_strength = (

                node.turbulence_field * 0.9

                + node.temperature * 0.25

                + node.pressure * 0.04

                + node.viability_turbulence * 0.8
            )

            # =================================================
            # HISTORICAL DISTORTION
            # =================================================

            distortion_strength += (

                self.ontological_drift
                * 0.6

                + self.regime_fragmentation
                * 0.5

                + self.perceptual_saturation
                * 0.35

                + self.coherence_instability
                * 0.4
            )

            local_x = (
                node.x
                - self.center_x
            )

            local_y = (
                node.y
                - self.center_y
            )

            radial_distance = math.sqrt(
                local_x ** 2
                + local_y ** 2
            ) + 0.0001

            angle = math.atan2(
                local_y,
                local_x,
            )

            # =================================================
            # REGIONAL CURVATURE
            # =================================================

            curvature = math.sin(

                angle * 2.0

                + self.curvature_phase

                + radial_distance * 0.35

                + self.ontological_drift
                * 2.0
            )

            curvature_factor = (
                curvature
                * self.curvature_strength
                * radial_distance
            )

            # =================================================
            # GEOMETRIC MEMORY ECHOES
            # =================================================

            for echo in self.geometry_echoes:

                echo_phase = (
                    echo["phase"]
                )

                echo_strength = (
                    echo["strength"]
                )

                curvature_factor += (

                    math.sin(
                        angle
                        + echo_phase
                    )

                    * echo_strength

                    * radial_distance
                )

            curved_x = (
                local_x
                + curvature_factor
            )

            curved_y = (
                local_y
                - curvature_factor
            )

            # =================================================
            # CLIMATIC SHEAR
            # =================================================

            shear = (

                node.temperature

                + node.pressure * 0.03

                + node.turbulence_field
            )

            # =================================================
            # HISTORICAL SHEAR INSTABILITY
            # =================================================

            shear += (

                self.regime_fragmentation
                * 0.8

                + self.contamination_trace
                * 0.5
            )

            sheared_x = (
                curved_x
                + curved_y
                * shear
                * self.shear_strength
            )

            sheared_y = (
                curved_y
                + curved_x
                * shear
                * 0.5
                * self.shear_strength
            )

            # =================================================
            # REGIONAL COMPRESSION
            # =================================================

            compression = (

                1.0

                - (
                    node.constraint_pressure
                    * 0.03
                )

                - (
                    node.environmental_saturation
                    * 0.04
                )
            )

            compression -= (

                self.perceptual_saturation
                * 0.25

                + self.coherence_instability
                * 0.15
            )

            compression = max(
                0.25,
                compression,
            )

            compressed_x = (
                sheared_x
                * compression
            )

            compressed_y = (
                sheared_y
                * compression
            )

            # =================================================
            # VORTEX WARPING
            # =================================================

            vortex_rotation = (

                node.vorticity

                * self.vortex_warp_strength

                * radial_distance
            )

            # =================================================
            # INTER-OBSERVER TURBULENCE
            # =================================================

            vortex_rotation += (

                self.regime_fragmentation
                * radial_distance
                * 0.12

                + self.ontological_drift
                * 0.18
            )

            cos_theta = math.cos(
                vortex_rotation
            )

            sin_theta = math.sin(
                vortex_rotation
            )

            warped_x = (
                compressed_x * cos_theta
                - compressed_y * sin_theta
            )

            warped_y = (
                compressed_x * sin_theta
                + compressed_y * cos_theta
            )

            # =================================================
            # COMPATIBILITY CORRIDORS
            # =================================================

            corridor_factor = (
                self._compute_corridor_effect(
                    warped_x,
                    warped_y,
                )
            )

            warped_x *= corridor_factor
            warped_y *= corridor_factor

            # =================================================
            # FINAL PERCEPTUAL NOISE
            # =================================================

            perceived_x = (

                warped_x
                + self.center_x

                + random.uniform(
                    -distortion_strength,
                    distortion_strength,
                )
            )

            perceived_y = (

                warped_y
                + self.center_y

                + random.uniform(
                    -distortion_strength,
                    distortion_strength,
                )
            )

            # =================================================
            # LOCAL REALITY DIVERGENCE
            # =================================================

            perceived_x += (
                math.sin(
                    self.local_reality_signature
                    * radial_distance
                )
                * self.ontological_drift
            )

            perceived_y += (
                math.cos(
                    self.local_reality_signature
                    * radial_distance
                )
                * self.ontological_drift
            )

            # =================================================
            # DISSIPATIVE MEMORY
            # =================================================

            self.perception_memory[
                node.id
            ] = {
                "x": perceived_x,
                "y": perceived_y,
                "node": node,
                "memory": 1.0,
            }

            perceived_nodes[
                node.id
            ] = self.perception_memory[
                node.id
            ]

        # =====================================================
        # MEMORY DECAY
        # =====================================================

        forgotten = []

        for node_id, memory in (
            self.perception_memory.items()
        ):

            if node_id in perceived_nodes:
                continue

            memory["memory"] *= (
                self.memory_decay
            )

            drift_x = random.uniform(
                -0.05,
                0.05,
            )

            drift_y = random.uniform(
                -0.05,
                0.05,
            )

            # =================================================
            # HISTORICAL MEMORY DRIFT
            # =================================================

            drift_x += (
                self.ontological_drift
                * random.uniform(
                    -0.08,
                    0.08,
                )
            )

            drift_y += (
                self.regime_fragmentation
                * random.uniform(
                    -0.08,
                    0.08,
                )
            )

            memory["x"] += drift_x
            memory["y"] += drift_y

            if memory["memory"] < 0.08:

                forgotten.append(
                    node_id
                )

                continue

            perceived_nodes[
                node_id
            ] = memory

        for node_id in forgotten:

            del self.perception_memory[
                node_id
            ]

        # =====================================================
        # PARTIAL EDGE RECONSTRUCTION
        # =====================================================

        perceived_edges = []

        for edge in graph.edges:

            source_id = edge.source.id
            target_id = edge.target.id

            if (
                source_id
                not in perceived_nodes
            ):
                continue

            if (
                target_id
                not in perceived_nodes
            ):
                continue

            instability = (

                edge.source.turbulence_field

                + edge.target.turbulence_field

                + edge.source.viability_turbulence

                + edge.target.viability_turbulence

                + edge.source.constraint_pressure
                * 0.03

                + edge.target.constraint_pressure
                * 0.03
            )

            # =================================================
            # INTER-PHENOMENOLOGICAL INSTABILITY
            # =================================================

            instability += (

                self.contamination_trace
                * 0.8

                + self.coherence_instability
                * 0.6

                + self.collapse_residue
                * 0.5
            )

            edge_visibility = max(
                0.02,
                1.0 - instability * 0.25
            )

            if (
                random.random()
                > edge_visibility
            ):
                continue

            perceived_edges.append(
                (
                    source_id,
                    target_id,
                    edge,
                )
            )

        return {
            "nodes": perceived_nodes,
            "edges": perceived_edges,
            "center": (
                self.center_x,
                self.center_y,
            ),
        }

    # =========================================================
    # HISTORICAL DYNAMICS
    # =========================================================

    def _update_historical_dynamics(
        self,
    ):

        self.contamination_trace *= (
            0.996
        )

        self.regime_fragmentation *= (
            0.995
        )

        self.ontological_drift *= (
            0.998
        )

        self.perceptual_saturation *= (
            0.997
        )

        self.interaction_fatigue *= (
            0.996
        )

        self.collapse_residue *= (
            0.994
        )

        self.coherence_instability *= (
            0.995
        )

        self.historical_pressure *= (
            0.998
        )

        # =====================================================
        # SLOW HISTORICAL ACCUMULATION
        # =====================================================

        self.ontological_drift += (
            random.uniform(
                -0.002,
                0.004,
            )
        )

        self.regime_fragmentation += (
            random.uniform(
                0.0,
                0.003,
            )
        )

        self.coherence_instability += (
            random.uniform(
                0.0,
                0.002,
            )
        )

        # =====================================================
        # FORBIDDEN ZONE EMERGENCE
        # =====================================================

        emergence_probability = (

            0.002

            + self.regime_fragmentation
            * 0.01
        )

        if (
            random.random()
            < emergence_probability
        ):

            self.forbidden_zones.append(
                {
                    "x": random.uniform(
                        self.center_x - 8.0,
                        self.center_x + 8.0,
                    ),
                    "y": random.uniform(
                        self.center_y - 8.0,
                        self.center_y + 8.0,
                    ),
                    "radius": random.uniform(
                        1.0,
                        4.0,
                    ),
                    "strength": random.uniform(
                        0.2,
                        1.0,
                    ),
                }
            )

        # =====================================================
        # GEOMETRIC ECHOES
        # =====================================================

        echo_probability = (

            0.004

            + self.contamination_trace
            * 0.02
        )

        if (
            random.random()
            < echo_probability
        ):

            self.geometry_echoes.append(
                {
                    "phase": random.uniform(
                        -math.pi,
                        math.pi,
                    ),
                    "strength": random.uniform(
                        0.01,
                        0.08,
                    ),
                }
            )

        # =====================================================
        # MEMORY LIMITS
        # =====================================================

        if len(self.geometry_echoes) > 12:

            self.geometry_echoes.pop(0)

        if len(self.forbidden_zones) > 10:

            self.forbidden_zones.pop(0)

    # =========================================================
    # COMPATIBILITY CORRIDORS
    # =========================================================

    def _compute_corridor_effect(
        self,
        x,
        y,
    ):

        if not self.compatibility_corridors:
            return 1.0

        corridor_effect = 1.0

        for corridor in (
            self.compatibility_corridors
        ):

            dx = (
                x - corridor["x"]
            )

            dy = (
                y - corridor["y"]
            )

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if (
                distance
                > corridor["radius"]
            ):
                continue

            local_effect = (

                corridor["strength"]

                * (
                    1.0
                    - (
                        distance
                        / corridor["radius"]
                    )
                )
            )

            corridor_effect += (
                local_effect
            )

        return corridor_effect

    # =========================================================
    # FORBIDDEN ZONES
    # =========================================================

    def _is_inside_forbidden_zone(
        self,
        x,
        y,
    ):

        for zone in self.forbidden_zones:

            dx = x - zone["x"]
            dy = y - zone["y"]

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if (
                distance
                < zone["radius"]
            ):
                return True

        return False

    # =========================================================
    # PERCEPTUAL DRIFT
    # =========================================================

    def _update_perceptual_drift(
        self,
        graph,
    ):

        if not graph.nodes:
            return

        active_nodes = sorted(
            graph.nodes.values(),
            key=lambda n: (
                n.activation
                + n.temperature
                + n.motion_energy
            ),
            reverse=True,
        )

        target = active_nodes[0]

        dx = (
            target.x
            - self.center_x
        )

        dy = (
            target.y
            - self.center_y
        )

        # =====================================================
        # HISTORICAL DRIFT MODULATION
        # =====================================================

        drift_modifier = (

            1.0

            + self.ontological_drift
            * 0.4

            + self.interaction_fatigue
            * 0.2
        )

        self.drift_velocity_x += (
            dx * 0.002
            * drift_modifier
        )

        self.drift_velocity_y += (
            dy * 0.002
            * drift_modifier
        )

        self.drift_velocity_x += (
            random.uniform(-0.02, 0.02)
        )

        self.drift_velocity_y += (
            random.uniform(-0.02, 0.02)
        )

        # =====================================================
        # TURBULENT INTER-OBSERVER DRIFT
        # =====================================================

        self.drift_velocity_x += (
            self.regime_fragmentation
            * random.uniform(
                -0.04,
                0.04,
            )
        )

        self.drift_velocity_y += (
            self.regime_fragmentation
            * random.uniform(
                -0.04,
                0.04,
            )
        )

        self.drift_velocity_x *= (
            self.drift_inertia
        )

        self.drift_velocity_y *= (
            self.drift_inertia
        )

        self.center_x += (
            self.drift_velocity_x
        )

        self.center_y += (
            self.drift_velocity_y
        )

        # =====================================================
        # GEOMETRIC DRIFT
        # =====================================================

        self.curvature_phase += (
            random.uniform(
                -0.015,
                0.015,
            )
        )

        self.curvature_phase += (
            self.ontological_drift
            * 0.02
        )