from __future__ import annotations

PRIMITIVE = "wisdom_as_long_horizon_navigation"
DESCRIPTION = "Wisdom as long horizon navigation."
DEPENDENCIES = []

"""
wisdom_as_long_horizon_navigation.py

Formalizes the principle that wisdom is not the application of immutable truths,
but the capacity to navigate responsibly across extended temporal horizons by
integrating delayed consequences into decision trajectories.

The module builds directly on ResponsibilityAsTrajectoryPrimitive and derives
diagnostics that characterize prudential navigation over long-term horizons.

Principle
---------
WISDOM_AS_LONG_HORIZON_NAVIGATION

Core idea
---------
Wisdom emerges when an agent:
1. Perceives delayed effects of its actions.
2. Integrates multiple temporal horizons.
3. Adjusts trajectories according to future consequences.
4. Maintains responsibility as a dynamic and revisable process.

This formulation remains local, adaptive, and non-finalized.
"""


from pprint import pprint

from ontology.responsibility_as_trajectory import (
    ResponsibilityAsTrajectoryPrimitive,
)


class WisdomAsLongHorizonNavigationPrimitive:
    """
    Primitive formalizing wisdom as responsible navigation over long-term
    temporal horizons.

    Derived diagnostics
    -------------------
    - long_term_consequence_awareness:
        Capacity to perceive delayed effects of decisions.

    - temporal_integration_capacity:
        Capacity to integrate multiple temporal horizons.

    - prudential_navigation:
        Capacity to adapt trajectories according to anticipated future effects.

    - wisdom_as_long_horizon_navigation:
        Indicates whether a genuine wisdom dynamic is constituted.
    """

    PRINCIPLE = "WISDOM_AS_LONG_HORIZON_NAVIGATION"

    def __init__(self) -> None:
        self.responsibility_as_trajectory = (
            ResponsibilityAsTrajectoryPrimitive()
        )

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a numerical value to the interval [0.0, 1.0]."""
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _mean(*values: float) -> float:
        """Compute the arithmetic mean of provided values."""
        if not values:
            return 0.0
        return sum(values) / len(values)

    def step(self) -> dict:
        """
        Execute one evaluation step and derive wisdom diagnostics.

        Returns
        -------
        dict
            Dictionary containing:
            - principle
            - responsibility_as_trajectory_diagnostics
            - long_term_consequence_awareness
            - temporal_integration_capacity
            - prudential_navigation
            - wisdom_as_long_horizon_navigation
        """
        responsibility_diagnostics = (
            self.responsibility_as_trajectory.step()
        )

        trajectory_impact_awareness = self._clamp(
            responsibility_diagnostics.get(
                "trajectory_impact_awareness", 0.0
            )
        )
        consequence_tracking_capacity = self._clamp(
            responsibility_diagnostics.get(
                "consequence_tracking_capacity", 0.0
            )
        )
        adaptive_accountability = self._clamp(
            responsibility_diagnostics.get(
                "adaptive_accountability", 0.0
            )
        )
        responsibility_as_trajectory = bool(
            responsibility_diagnostics.get(
                "responsibility_as_trajectory", False
            )
        )

        # Capacity to perceive delayed effects of decisions.
        long_term_consequence_awareness = self._clamp(
            self._mean(
                trajectory_impact_awareness,
                consequence_tracking_capacity,
            )
        )

        # Capacity to integrate several temporal horizons.
        temporal_integration_capacity = self._clamp(
            self._mean(
                long_term_consequence_awareness,
                adaptive_accountability,
            )
        )

        # Capacity to navigate prudently according to future consequences.
        prudential_navigation = self._clamp(
            self._mean(
                temporal_integration_capacity,
                consequence_tracking_capacity,
            )
        )

        # Minimal prudential threshold required for wisdom.
        prudential_threshold = 0.5

        wisdom_as_long_horizon_navigation = (
            responsibility_as_trajectory
            and prudential_navigation >= prudential_threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "responsibility_as_trajectory_diagnostics": (
                responsibility_diagnostics
            ),
            "long_term_consequence_awareness": (
                long_term_consequence_awareness
            ),
            "temporal_integration_capacity": (
                temporal_integration_capacity
            ),
            "prudential_navigation": prudential_navigation,
            "wisdom_as_long_horizon_navigation": (
                wisdom_as_long_horizon_navigation
            ),
        }


if __name__ == "__main__":
    primitive = WisdomAsLongHorizonNavigationPrimitive()

    print("\n--- wisdom as long horizon navigation ---")
    pprint(primitive.step())
