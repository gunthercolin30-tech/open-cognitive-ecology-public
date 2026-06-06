# visualization/distributed_perception_ecology.py

import math
import random

from visualization.local_perception_field import (
    LocalPerceptionField
)


class DistributedPerceptionEcology:

    def __init__(
        self,
        perception_count=4,
    ):

        self.perception_fields = []

        self.min_fields = 2
        self.max_fields = 6

        self.ecology_phase = 0.0

        # =====================================================
        # INTER-PHENOMENOLOGICAL ECOLOGY
        # =====================================================

        self.interaction_radius = 8.0

        self.contamination_strength = 0.015

        self.sync_probability = 0.025

        self.conflict_probability = 0.035

        self.collapse_propagation_probability = (
            0.020
        )

        self.coalition_probability = 0.018

        # =====================================================
        # INITIAL PERCEPTION ECOLOGY
        # =====================================================

        for i in range(
            perception_count
        ):

            self.perception_fields.append(
                self._create_field()
            )

    # =========================================================
    # FIELD CREATION
    # =========================================================

    def _create_field(self):

        field = (
            LocalPerceptionField()
        )

        # =====================================================
        # ECOLOGICAL DIFFERENTIATION
        # =====================================================

        field.center_x = random.uniform(
            -10.0,
            10.0,
        )

        field.center_y = random.uniform(
            -10.0,
            10.0,
        )

        field.visibility_radius = (
            random.uniform(
                4.0,
                12.0,
            )
        )

        field.visibility_jitter = (
            random.uniform(
                0.5,
                3.0,
            )
        )

        field.memory_decay = (
            random.uniform(
                0.94,
                0.995,
            )
        )

        field.drift_inertia = (
            random.uniform(
                0.90,
                0.995,
            )
        )

        field.curvature_strength = (
            random.uniform(
                0.03,
                0.25,
            )
        )

        field.shear_strength = (
            random.uniform(
                0.01,
                0.18,
            )
        )

        field.compression_strength = (
            random.uniform(
                0.02,
                0.20,
            )
        )

        field.vortex_warp_strength = (
            random.uniform(
                0.02,
                0.30,
            )
        )

        # =====================================================
        # ECOLOGICAL STATE
        # =====================================================

        field.perceptual_stability = (
            random.uniform(
                0.4,
                1.0,
            )
        )

        field.perceptual_saturation = 0.0

        field.perceptual_fatigue = 0.0

        field.collapse_probability = (
            random.uniform(
                0.0005,
                0.005,
            )
        )

        field.bifurcation_probability = (
            random.uniform(
                0.001,
                0.008,
            )
        )

        field.perceptual_age = 0.0

        # =====================================================
        # INTER-PHENOMENOLOGICAL STATE
        # =====================================================

        field.perceptual_signature = (
            random.uniform(
                -1.0,
                1.0,
            )
        )

        field.local_coherence = random.uniform(
            0.2,
            1.0,
        )

        field.contamination_load = 0.0

        field.regime_instability = 0.0

        field.coalition_affinity = random.uniform(
            0.0,
            1.0,
        )

        field.last_sync_phase = random.uniform(
            0.0,
            math.pi * 2.0,
        )

        field.phenomenological_density = (
            random.uniform(
                0.3,
                1.2,
            )
        )

        return field

    # =========================================================
    # DISTRIBUTED PERCEPTION
    # =========================================================

    def perceive(
        self,
        graph,
    ):

        self.ecology_phase += 0.01

        self._evolve_perception_ecology()

        self._interact_perception_fields()

        distributed_fields = []

        surviving_fields = []

        for field in (
            self.perception_fields
        ):

            # =================================================
            # PERCEPTUAL COLLAPSE
            # =================================================

            collapse_risk = (

                field.collapse_probability

                * (
                    1.0
                    + field.perceptual_fatigue
                )

                * (
                    1.0
                    + field.regime_instability
                )

                * (
                    1.0
                    + field.contamination_load
                )
            )

            if (
                random.random()
                < collapse_risk
            ):

                self._propagate_local_collapse(
                    field
                )

                continue

            perceived = (
                field.perceive(graph)
            )

            distributed_fields.append(
                perceived
            )

            surviving_fields.append(
                field
            )

        self.perception_fields = (
            surviving_fields
        )

        # =====================================================
        # ECOLOGICAL REGENERATION
        # =====================================================

        if (
            len(self.perception_fields)
            < self.min_fields
        ):

            self.perception_fields.append(
                self._create_field()
            )

        # =====================================================
        # PERCEPTUAL EMERGENCE
        # =====================================================

        emergence_probability = (
            0.01
            + (
                len(graph.nodes)
                * 0.0005
            )
        )

        if (
            random.random()
            < emergence_probability
        ):

            if (
                len(self.perception_fields)
                < self.max_fields
            ):

                self.perception_fields.append(
                    self._create_field()
                )

        return distributed_fields

    # =========================================================
    # INTER-PHENOMENOLOGICAL ECOLOGY
    # =========================================================

    def _interact_perception_fields(
        self,
    ):

        field_count = len(
            self.perception_fields
        )

        if field_count < 2:
            return

        for i in range(field_count):

            field_a = (
                self.perception_fields[i]
            )

            for j in range(i + 1, field_count):

                field_b = (
                    self.perception_fields[j]
                )

                dx = (
                    field_b.center_x
                    - field_a.center_x
                )

                dy = (
                    field_b.center_y
                    - field_a.center_y
                )

                distance = math.sqrt(
                    dx * dx
                    + dy * dy
                )

                if (
                    distance
                    > self.interaction_radius
                ):
                    continue

                proximity = (
                    1.0
                    - (
                        distance
                        / self.interaction_radius
                    )
                )

                # =============================================
                # PERCEPTUAL CONTAMINATION
                # =============================================

                self._apply_contamination(
                    field_a,
                    field_b,
                    proximity,
                )

                # =============================================
                # TEMPORARY SYNCHRONIZATION
                # =============================================

                if (
                    random.random()
                    < (
                        self.sync_probability
                        * proximity
                    )
                ):

                    self._temporary_sync(
                        field_a,
                        field_b,
                    )

                # =============================================
                # PERCEPTUAL CONFLICT
                # =============================================

                if (
                    random.random()
                    < (
                        self.conflict_probability
                        * proximity
                    )
                ):

                    self._trigger_conflict(
                        field_a,
                        field_b,
                    )

                # =============================================
                # LOCAL COALITIONS
                # =============================================

                if (
                    random.random()
                    < (
                        self.coalition_probability
                        * proximity
                    )
                ):

                    self._form_local_coalition(
                        field_a,
                        field_b,
                    )

    # =========================================================
    # CONTAMINATION
    # =========================================================

    def _apply_contamination(
        self,
        field_a,
        field_b,
        proximity,
    ):

        delta_curvature = (
            field_b.curvature_strength
            - field_a.curvature_strength
        )

        delta_shear = (
            field_b.shear_strength
            - field_a.shear_strength
        )

        delta_vortex = (
            field_b.vortex_warp_strength
            - field_a.vortex_warp_strength
        )

        contamination_factor = (

            self.contamination_strength
            * proximity
        )

        field_a.curvature_strength += (
            delta_curvature
            * contamination_factor
        )

        field_a.shear_strength += (
            delta_shear
            * contamination_factor
        )

        field_a.vortex_warp_strength += (
            delta_vortex
            * contamination_factor
        )

        field_b.curvature_strength -= (
            delta_curvature
            * contamination_factor
        )

        field_b.shear_strength -= (
            delta_shear
            * contamination_factor
        )

        field_b.vortex_warp_strength -= (
            delta_vortex
            * contamination_factor
        )

        contamination_noise = (
            random.uniform(
                0.0,
                0.03,
            )
            * proximity
        )

        field_a.contamination_load += (
            contamination_noise
        )

        field_b.contamination_load += (
            contamination_noise
        )

    # =========================================================
    # TEMPORARY SYNCHRONIZATION
    # =========================================================

    def _temporary_sync(
        self,
        field_a,
        field_b,
    ):

        sync_strength = random.uniform(
            0.01,
            0.04,
        )

        shared_phase = (
            (
                field_a.curvature_phase
                + field_b.curvature_phase
            )
            * 0.5
        )

        field_a.curvature_phase += (
            (
                shared_phase
                - field_a.curvature_phase
            )
            * sync_strength
        )

        field_b.curvature_phase += (
            (
                shared_phase
                - field_b.curvature_phase
            )
            * sync_strength
        )

        field_a.last_sync_phase = (
            self.ecology_phase
        )

        field_b.last_sync_phase = (
            self.ecology_phase
        )

        # =====================================================
        # SYNCHRONIZATION REMAINS UNSTABLE
        # =====================================================

        field_a.regime_instability += (
            random.uniform(
                0.005,
                0.03,
            )
        )

        field_b.regime_instability += (
            random.uniform(
                0.005,
                0.03,
            )
        )

    # =========================================================
    # PERCEPTUAL CONFLICT
    # =========================================================

    def _trigger_conflict(
        self,
        field_a,
        field_b,
    ):

        instability = random.uniform(
            0.02,
            0.08,
        )

        field_a.regime_instability += (
            instability
        )

        field_b.regime_instability += (
            instability
        )

        field_a.vortex_warp_strength += (
            random.uniform(
                -0.04,
                0.04,
            )
        )

        field_b.vortex_warp_strength += (
            random.uniform(
                -0.04,
                0.04,
            )
        )

        field_a.curvature_phase += (
            random.uniform(
                -0.3,
                0.3,
            )
        )

        field_b.curvature_phase += (
            random.uniform(
                -0.3,
                0.3,
            )
        )

    # =========================================================
    # LOCAL COALITIONS
    # =========================================================

    def _form_local_coalition(
        self,
        field_a,
        field_b,
    ):

        coalition_effect = random.uniform(
            0.01,
            0.03,
        )

        field_a.local_coherence += (
            coalition_effect
        )

        field_b.local_coherence += (
            coalition_effect
        )

        # =====================================================
        # COALITIONS ARE TEMPORARY
        # =====================================================

        field_a.perceptual_fatigue += (
            random.uniform(
                0.002,
                0.010,
            )
        )

        field_b.perceptual_fatigue += (
            random.uniform(
                0.002,
                0.010,
            )
        )

    # =========================================================
    # COLLAPSE PROPAGATION
    # =========================================================

    def _propagate_local_collapse(
        self,
        collapsed_field,
    ):

        for field in (
            self.perception_fields
        ):

            if field is collapsed_field:
                continue

            dx = (
                field.center_x
                - collapsed_field.center_x
            )

            dy = (
                field.center_y
                - collapsed_field.center_y
            )

            distance = math.sqrt(
                dx * dx
                + dy * dy
            )

            if distance > (
                self.interaction_radius
                * 1.5
            ):
                continue

            if (
                random.random()
                > self.collapse_propagation_probability
            ):
                continue

            field.regime_instability += (
                random.uniform(
                    0.05,
                    0.18,
                )
            )

            field.perceptual_fatigue += (
                random.uniform(
                    0.02,
                    0.08,
                )
            )

            field.contamination_load += (
                random.uniform(
                    0.03,
                    0.12,
                )
            )

            field.perception_memory.clear()

    # =========================================================
    # ECOLOGICAL EVOLUTION
    # =========================================================

    def _evolve_perception_ecology(
        self,
    ):

        for field in (
            self.perception_fields
        ):

            field.perceptual_age += 1.0

            # =================================================
            # FATIGUE ACCUMULATION
            # =================================================

            field.perceptual_fatigue += (
                random.uniform(
                    0.0,
                    0.003,
                )
            )

            field.perceptual_fatigue *= (
                0.995
            )

            # =================================================
            # SATURATION DYNAMICS
            # =================================================

            field.perceptual_saturation += (
                random.uniform(
                    -0.02,
                    0.03,
                )
            )

            field.perceptual_saturation = max(
                0.0,
                min(
                    1.0,
                    field.perceptual_saturation,
                )
            )

            # =================================================
            # INTER-PHENOMENOLOGICAL DRIFT
            # =================================================

            field.contamination_load *= (
                0.992
            )

            field.regime_instability *= (
                0.994
            )

            field.local_coherence *= (
                0.998
            )

            # =================================================
            # CONTINUOUS GEOMETRIC DRIFT
            # =================================================

            field.curvature_strength += (
                random.uniform(
                    -0.002,
                    0.002,
                )
            )

            field.shear_strength += (
                random.uniform(
                    -0.001,
                    0.001,
                )
            )

            field.compression_strength += (
                random.uniform(
                    -0.002,
                    0.002,
                )
            )

            field.vortex_warp_strength += (
                random.uniform(
                    -0.003,
                    0.003,
                )
            )

            field.visibility_radius += (
                random.uniform(
                    -0.08,
                    0.08,
                )
            )

            field.memory_decay += (
                random.uniform(
                    -0.0008,
                    0.0008,
                )
            )

            # =================================================
            # BOUNDS
            # =================================================

            field.curvature_strength = max(
                0.01,
                min(
                    0.45,
                    field.curvature_strength,
                )
            )

            field.shear_strength = max(
                0.005,
                min(
                    0.35,
                    field.shear_strength,
                )
            )

            field.compression_strength = max(
                0.01,
                min(
                    0.45,
                    field.compression_strength,
                )
            )

            field.vortex_warp_strength = max(
                0.01,
                min(
                    0.60,
                    field.vortex_warp_strength,
                )
            )

            field.visibility_radius = max(
                2.0,
                min(
                    18.0,
                    field.visibility_radius,
                )
            )

            field.memory_decay = max(
                0.85,
                min(
                    0.999,
                    field.memory_decay,
                )
            )

            # =================================================
            # PERCEPTUAL BIFURCATIONS
            # =================================================

            bifurcation_risk = (

                field.bifurcation_probability

                * (
                    1.0
                    + field.perceptual_saturation
                )

                * (
                    1.0
                    + field.perceptual_fatigue
                )

                * (
                    1.0
                    + field.regime_instability
                )
            )

            if (
                random.random()
                < bifurcation_risk
            ):

                self._trigger_bifurcation(
                    field
                )

    # =========================================================
    # PERCEPTUAL BIFURCATION
    # =========================================================

    def _trigger_bifurcation(
        self,
        field,
    ):

        mode = random.choice(
            [
                "hyper_compression",
                "vortex_instability",
                "memory_collapse",
                "blindness",
                "geometric_explosion",
                "hyper_localization",
                "regime_fragmentation",
                "contamination_spike",
            ]
        )

        # =====================================================
        # HYPER COMPRESSION
        # =====================================================

        if mode == "hyper_compression":

            field.compression_strength *= (
                random.uniform(
                    1.8,
                    3.5,
                )
            )

        # =====================================================
        # VORTEX INSTABILITY
        # =====================================================

        elif mode == "vortex_instability":

            field.vortex_warp_strength *= (
                random.uniform(
                    1.5,
                    3.0,
                )
            )

            field.curvature_strength *= (
                random.uniform(
                    1.2,
                    2.5,
                )
            )

        # =====================================================
        # MEMORY COLLAPSE
        # =====================================================

        elif mode == "memory_collapse":

            field.memory_decay *= (
                random.uniform(
                    0.85,
                    0.95,
                )
            )

            field.perception_memory.clear()

        # =====================================================
        # PERCEPTUAL BLINDNESS
        # =====================================================

        elif mode == "blindness":

            field.visibility_radius *= (
                random.uniform(
                    0.3,
                    0.7,
                )
            )

        # =====================================================
        # GEOMETRIC EXPLOSION
        # =====================================================

        elif mode == "geometric_explosion":

            field.curvature_strength *= (
                random.uniform(
                    2.0,
                    4.0,
                )
            )

            field.shear_strength *= (
                random.uniform(
                    1.5,
                    3.5,
                )
            )

        # =====================================================
        # HYPER LOCALIZATION
        # =====================================================

        elif mode == "hyper_localization":

            field.visibility_radius *= (
                random.uniform(
                    0.2,
                    0.5,
                )
            )

            field.memory_decay *= (
                random.uniform(
                    0.90,
                    0.97,
                )
            )

        # =====================================================
        # REGIME FRAGMENTATION
        # =====================================================

        elif mode == "regime_fragmentation":

            field.regime_instability += (
                random.uniform(
                    0.2,
                    0.5,
                )
            )

            field.local_coherence *= (
                random.uniform(
                    0.4,
                    0.8,
                )
            )

        # =====================================================
        # CONTAMINATION SPIKE
        # =====================================================

        elif mode == "contamination_spike":

            field.contamination_load += (
                random.uniform(
                    0.2,
                    0.6,
                )
            )

            field.perceptual_fatigue += (
                random.uniform(
                    0.05,
                    0.15,
                )
            )