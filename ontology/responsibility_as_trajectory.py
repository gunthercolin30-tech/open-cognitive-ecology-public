from __future__ import annotations

PRIMITIVE = "responsibility_as_trajectory"
DESCRIPTION = "Responsibility as trajectory."
DEPENDENCIES = []

"""
ontology/responsibility_as_trajectory.py

Formalizes the principle that responsibility does not consist in satisfying an
absolute moral norm, but in assuming the trajectories and consequences generated
by ethical navigation within a field of emergent values.

The primitive builds directly on EthicsAsNavigationPrimitive and evaluates
whether an agent is capable of:

1. Perceiving the impact of its action trajectories.
2. Tracking the consequences of its decisions over time.
3. Maintaining adaptive and context-sensitive accountability.

When these capacities are sufficiently developed, responsibility emerges as a
trajectory-level property rather than as compliance with externally imposed,
universal prescriptions.
"""


from pprint import pprint

from ontology.ethics_as_navigation import (
    EthicsAsNavigationPrimitive,
)


PRINCIPLE = "RESPONSIBILITY_AS_TRAJECTORY"


class ResponsibilityAsTrajectoryPrimitive:
    """
    Responsibility emerges when an intelligence is able to recognize the
    trajectory-level consequences of its actions and revise its behavior in a
    context-sensitive manner.

    Diagnostics
    -----------
    trajectory_impact_awareness:
        Capacity to perceive the impact of action trajectories.

    consequence_tracking_capacity:
        Capacity to follow the downstream effects of decisions.

    adaptive_accountability:
        Capacity to assume revisable and contextual responsibility.

    responsibility_as_trajectory:
        True when ethical navigation is active and adaptive accountability
        exceeds the emergence threshold.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self.ethics_as_navigation = EthicsAsNavigationPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a scalar to the interval [0.0, 1.0]."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostics characterizing the emergence of responsibility as a
            trajectory-based property.
        """
        ethics = self.ethics_as_navigation.step()

        value_field_density = float(ethics.get("value_field_density", 0.0))
        ethical_navigation_capacity = float(
            ethics.get("ethical_navigation_capacity", 0.0)
        )
        context_sensitive_evaluation = float(
            ethics.get("context_sensitive_evaluation", 0.0)
        )
        ethics_as_navigation = bool(
            ethics.get("ethics_as_navigation", False)
        )

        # Capacity to perceive how actions reshape the surrounding value field.
        trajectory_impact_awareness = self._clamp(
            (
                value_field_density
                + context_sensitive_evaluation
            ) / 2.0
        )

        # Capacity to project and monitor downstream consequences.
        consequence_tracking_capacity = self._clamp(
            (
                trajectory_impact_awareness
                + ethical_navigation_capacity
            ) / 2.0
        )

        # Capacity to remain accountable while adapting to changing contexts.
        adaptive_accountability = self._clamp(
            (
                consequence_tracking_capacity
                + context_sensitive_evaluation
            ) / 2.0
        )

        # Responsibility emerges when ethical navigation is active and
        # accountability is sufficiently robust.
        responsibility_as_trajectory = (
            ethics_as_navigation
            and adaptive_accountability >= 0.50
        )

        return {
            "principle": self.PRINCIPLE,
            "ethics_as_navigation_diagnostics": ethics,
            "trajectory_impact_awareness": trajectory_impact_awareness,
            "consequence_tracking_capacity": consequence_tracking_capacity,
            "adaptive_accountability": adaptive_accountability,
            "responsibility_as_trajectory": responsibility_as_trajectory,
        }


if __name__ == "__main__":
    primitive = ResponsibilityAsTrajectoryPrimitive()

    print("\n--- responsibility as trajectory ---")
    pprint(primitive.step())
