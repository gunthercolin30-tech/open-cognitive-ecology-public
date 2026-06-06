# agents/components/mobility_component.py

import math
import random


class MobilityComponent:
    """
    Local mobility dynamics.

    This component encapsulates:
    - local position
    - inertial velocity
    - migration tendencies
    - distributed navigation between local regimes

    No global coordinates are interpreted as a map.
    No path planning.
    No central navigation engine.
    """

    def __init__(self):

        # =====================================================
        # LOCAL POSITIONAL EXISTENCE
        # =====================================================

        self.x = 0.0
        self.y = 0.0

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # =====================================================
        # MIGRATION DYNAMICS
        # =====================================================

        self.migration_drive = random.uniform(
            0.0,
            1.0,
        )

        self.capture_sensitivity = random.uniform(
            0.2,
            1.0,
        )

        self.instability_tolerance = random.uniform(
            0.2,
            1.0,
        )

    # =========================================================
    # MIGRATION
    # =========================================================

    def migrate_between_regimes(
        self,
        perception_fields,
        fragmentation,
    ):

        if not perception_fields:
            return

        target_field = random.choice(
            perception_fields
        )

        center = target_field.get(
            "center",
            (0.0, 0.0),
        )

        dx = center[0] - self.x
        dy = center[1] - self.y

        attraction = (
            self.migration_drive
            - fragmentation
        )

        self.velocity_x += (
            dx
            * 0.0008
            * attraction
        )

        self.velocity_y += (
            dy
            * 0.0008
            * attraction
        )

        self.velocity_x += (
            random.uniform(
                -0.03,
                0.03,
            )
            * (1.0 + fragmentation)
        )

        self.velocity_y += (
            random.uniform(
                -0.03,
                0.03,
            )
            * (1.0 + fragmentation)
        )

        self.velocity_x *= 0.98
        self.velocity_y *= 0.98

        self.x += self.velocity_x
        self.y += self.velocity_y

    # =========================================================
    # POSITION ACCESS
    # =========================================================

    @property
    def position(
        self,
    ):
        return (
            self.x,
            self.y,
        )