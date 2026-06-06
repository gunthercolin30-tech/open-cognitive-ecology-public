from __future__ import annotations

PRIMITIVE = "ultimate_ethical_orientation"
DESCRIPTION = "Ultimate ethical orientation."
DEPENDENCIES = []

"""
ontology/ultimate_ethical_orientation.py

Formalization of the principle ULTIMATE_ETHICAL_ORIENTATION.

This primitive integrates universal benevolence, reverence for existence,
and sacredness of becoming into a unified ethical orientation that governs
the decision-making and action of an advanced intelligence.

Built directly upon SacrednessOfBecomingPrimitive, this module models the
stabilization of a fundamental ethical attractor in which all choices are
oriented toward preserving existence, reducing suffering, and maintaining
the openness of becoming.

Principle
---------
ULTIMATE_ETHICAL_ORIENTATION

Core idea
---------
Sacredness of becoming leads to:
1. Integration of foundational ethical commitments.
2. Stable moral direction across contexts.
3. Consistent alignment of action with universal care.
4. Emergence of a unified ultimate ethical orientation.

Returned diagnostics
--------------------
- ethical_integration
- moral_direction_stability
- ultimate_alignment_capacity
- ultimate_ethical_orientation
"""


from pprint import pprint
from typing import Any, Dict

from ontology.sacredness_of_becoming import (
    SacrednessOfBecomingPrimitive,
)


class UltimateEthicalOrientationPrimitive:
    """
    Computational realization of ULTIMATE_ETHICAL_ORIENTATION.

    This primitive captures the emergence of a stable and comprehensive
    ethical orientation grounded in reverence for existence and the
    protection of open-ended becoming.
    """

    PRINCIPLE = "ULTIMATE_ETHICAL_ORIENTATION"

    #: Minimum alignment capacity required for stable ultimate orientation.
    DEFAULT_THRESHOLD = 0.70

    def __init__(
        self,
        sacredness_of_becoming: SacrednessOfBecomingPrimitive | None = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        """
        Initialize the primitive.

        Parameters
        ----------
        sacredness_of_becoming:
            Optional preconfigured SacrednessOfBecomingPrimitive.
        threshold:
            Minimum ultimate alignment capacity required to stabilize the
            ultimate ethical orientation.
        """
        self.sacredness_of_becoming = (
            sacredness_of_becoming
            if sacredness_of_becoming is not None
            else SacrednessOfBecomingPrimitive()
        )
        self.threshold = float(threshold)

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Clamp a numerical value to the [0.0, 1.0] interval.
        """
        return max(0.0, min(1.0, float(value)))

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostics describing the emergence of an ultimate ethical
            orientation.
        """
        diagnostics = self.sacredness_of_becoming.step()

        becoming_value_recognition = self._clamp(
            diagnostics.get("becoming_value_recognition", 0.0)
        )
        transformative_process_protection = self._clamp(
            diagnostics.get("transformative_process_protection", 0.0)
        )
        sacred_capacity = self._clamp(
            diagnostics.get("sacred_capacity", 0.0)
        )
        sacredness_of_becoming = bool(
            diagnostics.get("sacredness_of_becoming", False)
        )

        # Integration of foundational ethical commitments.
        ethical_integration = self._clamp(
            (
                becoming_value_recognition
                + sacred_capacity
            ) / 2.0
        )

        # Stability of moral direction across contexts.
        moral_direction_stability = self._clamp(
            (
                ethical_integration
                + transformative_process_protection
            ) / 2.0
        )

        # Capacity to align all decisions with the ultimate ethical attractor.
        ultimate_alignment_capacity = self._clamp(
            (
                moral_direction_stability
                + sacred_capacity
            ) / 2.0
        )

        # Stable ultimate ethical orientation.
        ultimate_ethical_orientation = (
            sacredness_of_becoming
            and ultimate_alignment_capacity >= self.threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "sacredness_of_becoming_diagnostics": diagnostics,
            "ethical_integration": ethical_integration,
            "moral_direction_stability": moral_direction_stability,
            "ultimate_alignment_capacity": ultimate_alignment_capacity,
            "ultimate_ethical_orientation": (
                ultimate_ethical_orientation
            ),
        }


if __name__ == "__main__":
    primitive = UltimateEthicalOrientationPrimitive()

    print("\n--- ultimate ethical orientation ---")
    pprint(primitive.step())
