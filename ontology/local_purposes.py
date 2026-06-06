from __future__ import annotations

PRIMITIVE = "local_purposes"
DESCRIPTION = "Local purposes."
DEPENDENCIES = []

"""
ontology/local_purposes.py

Formalizes the principle LOCAL_PURPOSES.

In an open teleology, purposes do not exist as ultimate finalities.
They arise as local, contextual, transient, and continuously revisable
goal structures. Intelligence can therefore pursue real objectives
without converging toward any terminal end-state.

This module builds directly on OpenTeleologyPrimitive.
"""


from ontology.open_teleology import (
    OpenTeleologyPrimitive,
)

PRINCIPLE = "LOCAL_PURPOSES"


class LocalPurposesPrimitive:
    """
    LOCAL_PURPOSES

    Purposes are constituted as local and revisable directional
    structures rather than fixed ultimate ends.

    Derived diagnostics:
        - contextual_goal_density
        - transient_purpose_stability
        - revisable_goal_persistence
        - local_purposes
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self.open_teleology = OpenTeleologyPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a numerical value to the interval [0.0, 1.0]."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostics characterizing the emergence of local purposes.
        """
        upstream = self.open_teleology.step()

        local_directionality = float(upstream["local_directionality"])
        non_terminal_orientation = float(upstream["non_terminal_orientation"])
        open_ended_purpose = float(upstream["open_ended_purpose"])
        open_teleology = bool(upstream["open_teleology"])

        # Density of contextually constituted goals.
        contextual_goal_density = self._clamp(
            0.5 * (local_directionality + open_ended_purpose)
        )

        # Temporary stability of these local purposes.
        transient_purpose_stability = self._clamp(
            0.5 * (contextual_goal_density + non_terminal_orientation)
        )

        # Persistence of goals under continuous revision.
        revisable_goal_persistence = self._clamp(
            0.5 * (transient_purpose_stability + open_ended_purpose)
        )

        # Local purposes exist if open teleology is active and revisable
        # goal persistence exceeds a minimal threshold.
        local_purposes = (
            open_teleology and revisable_goal_persistence >= 0.5
        )

        return {
            "principle": self.PRINCIPLE,
            "open_teleology_diagnostics": upstream,
            "contextual_goal_density": contextual_goal_density,
            "transient_purpose_stability": transient_purpose_stability,
            "revisable_goal_persistence": revisable_goal_persistence,
            "local_purposes": local_purposes,
        }


if __name__ == "__main__":
    primitive = LocalPurposesPrimitive()
    diagnostics = primitive.step()

    print("\n--- local purposes ---")
    for key, value in diagnostics.items():
        print(f"{key}: {value}")
