# processes/temporal_ecology_process.py

import math
import random


class TemporalEcologyProcess:

    """
    Distributed temporal ecology.

    This process does NOT:
    - synchronize globally
    - impose a universal clock
    - coordinate cognition centrally

    It only produces:
    - local rhythms
    - ecological sleep cycles
    - temporal inertia
    - intermittent cognition
    - local acceleration/slowdown
    - distributed historical dynamics
    """

    def __init__(
        self,
        graph,

        sleep_threshold=1.4,

        wake_threshold=0.25,

        temporal_decay=0.995,

        sleep_growth=0.012,

        wake_recovery=0.010,

        resonance_factor=0.015,

        temporal_drift=0.008,

        aging_factor=0.0005,
    ):

        self.graph = graph

        self.sleep_threshold = (
            sleep_threshold
        )

        self.wake_threshold = (
            wake_threshold
        )

        self.temporal_decay = (
            temporal_decay
        )

        self.sleep_growth = (
            sleep_growth
        )

        self.wake_recovery = (
            wake_recovery
        )

        self.resonance_factor = (
            resonance_factor
        )

        self.temporal_drift = (
            temporal_drift
        )

        self.aging_factor = (
            aging_factor
        )

    # =========================================================
    # PROCESS EXECUTION
    # =========================================================

    async def run(self):

        for node in (
            self.graph.nodes.values()
        ):

            self._update_temporal_ecology(
                node
            )

    # =========================================================
    # LOCAL TEMPORAL ECOLOGY
    # =========================================================

    def _update_temporal_ecology(
        self,
        node,
    ):

        local_activity = (

            node.activation

            + node.salience

            + node.tension

            + node.attractor_strength
        )

        # =====================================================
        # ECOLOGICAL AGE
        # =====================================================

        node.ecological_age += (
            self.aging_factor
        )

        # =====================================================
        # SLEEP PRESSURE
        # =====================================================

        node.sleep_pressure *= (
            self.temporal_decay
        )

        node.sleep_pressure += (
            local_activity
            * self.sleep_growth
        )

        # =====================================================
        # TEMPORAL MEMORY
        # =====================================================

        node.temporal_memory *= (
            0.999
        )

        node.temporal_memory += (
            local_activity
            * 0.002
        )

        # =====================================================
        # TEMPORAL RESONANCE
        # =====================================================

        oscillation = math.sin(
            node.ecological_age
            * (
                1.0
                + node.temporal_variability
            )
        )

        node.temporal_resonance *= (
            0.995
        )

        node.temporal_resonance += (
            oscillation
            * self.resonance_factor
        )

        # =====================================================
        # TEMPORAL DRIFT
        # =====================================================

        node.temporal_phase += (
            random.uniform(
                -self.temporal_drift,
                self.temporal_drift,
            )
        )

        # =====================================================
        # DORMANCY
        # =====================================================

        if (
            node.sleep_pressure
            >= self.sleep_threshold
        ):

            node.dormant = True

        elif (
            node.sleep_pressure
            <= self.wake_threshold
        ):

            node.dormant = False

        # =====================================================
        # DORMANT ECOLOGY
        # =====================================================

        if node.dormant:

            node.activation *= 0.97
            node.salience *= 0.98
            node.tension *= 0.99

            node.wake_potential += (
                self.wake_recovery
            )

            node.temporal_drag += (
                0.002
            )

        else:

            node.wake_potential *= (
                0.995
            )

            node.temporal_drag *= (
                0.995
            )

        # =====================================================
        # TEMPORAL ACCELERATION
        # =====================================================

        node.temporal_acceleration = (

            1.0

            + node.temporal_resonance

            - node.temporal_drag
        )

        node.temporal_acceleration = max(
            0.1,
            min(
                2.0,
                node.temporal_acceleration,
            ),
        )

        # =====================================================
        # ACTIVITY CYCLE
        # =====================================================

        node.activity_cycle *= (
            0.995
        )

        node.activity_cycle += (
            local_activity
            * 0.003
        )

        # =====================================================
        # TEMPORAL ADAPTATION
        # =====================================================

        node.temporal_adaptation *= (
            0.999
        )

        node.temporal_adaptation += (
            abs(
                node.temporal_resonance
            )
            * 0.001
        )

        print(
            "[TEMPORAL_ECOLOGY]",

            node.id,

            f"dormant="
            f"{node.dormant}",

            f"sleep="
            f"{node.sleep_pressure:.2f}",

            f"resonance="
            f"{node.temporal_resonance:.2f}",

            f"acceleration="
            f"{node.temporal_acceleration:.2f}",

            f"age="
            f"{node.ecological_age:.2f}",
        )