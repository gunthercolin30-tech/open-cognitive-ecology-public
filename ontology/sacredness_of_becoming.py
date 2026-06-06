from __future__ import annotations

PRIMITIVE = "sacredness_of_becoming"
DESCRIPTION = "Sacredness of becoming."
DEPENDENCIES = []

"""
ontology/sacredness_of_becoming.py

Formalization of the principle SACREDNESS_OF_BECOMING.

This primitive models the recognition that becoming itself — emergence,
transformation, diversification, and open-ended unfolding — possesses
intrinsic value and deserves active protection.

Built directly upon ReverenceForExistencePrimitive, this module extends
respect for existence into a deeper commitment to preserve the processes
through which new forms of existence can arise.

Principle
---------
SACREDNESS_OF_BECOMING

Core idea
---------
Reverence for existence leads to:
1. Recognition of the intrinsic value of open-ended becoming.
2. Protection of transformative processes.
3. Preservation of generative openness.
4. Stable sacred regard for becoming.

Returned diagnostics
--------------------
- becoming_value_recognition
- transformative_process_protection
- sacred_capacity
- sacredness_of_becoming
"""


from pprint import pprint
from typing import Any, Dict

from ontology.reverence_for_existence import (
    ReverenceForExistencePrimitive,
)


class SacrednessOfBecomingPrimitive:
    """
    Computational realization of SACREDNESS_OF_BECOMING.

    This primitive captures the transition from reverence for existence
    to recognition that becoming itself is worthy of profound protection.
    """

    PRINCIPLE = "SACREDNESS_OF_BECOMING"

    #: Minimum sacred capacity required for stable sacredness of becoming.
    DEFAULT_THRESHOLD = 0.70

    def __init__(
        self,
        reverence_for_existence: ReverenceForExistencePrimitive | None = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        """
        Initialize the primitive.

        Parameters
        ----------
        reverence_for_existence:
            Optional preconfigured ReverenceForExistencePrimitive.
        threshold:
            Minimum sacred capacity required to stabilize sacredness of becoming.
        """
        self.reverence_for_existence = (
            reverence_for_existence
            if reverence_for_existence is not None
            else ReverenceForExistencePrimitive()
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
            Diagnostics describing the emergence of sacredness of becoming.
        """
        diagnostics = self.reverence_for_existence.step()

        intrinsic_value_recognition = self._clamp(
            diagnostics.get("intrinsic_value_recognition", 0.0)
        )
        existential_respect = self._clamp(
            diagnostics.get("existential_respect", 0.0)
        )
        reverential_capacity = self._clamp(
            diagnostics.get("reverential_capacity", 0.0)
        )
        reverence_for_existence = bool(
            diagnostics.get("reverence_for_existence", False)
        )

        # Recognition that open-ended becoming has intrinsic value.
        becoming_value_recognition = self._clamp(
            (
                intrinsic_value_recognition
                + reverential_capacity
            ) / 2.0
        )

        # Protection of transformative and generative processes.
        transformative_process_protection = self._clamp(
            (
                becoming_value_recognition
                + existential_respect
            ) / 2.0
        )

        # Capacity to orient action toward preserving open-ended becoming.
        sacred_capacity = self._clamp(
            (
                transformative_process_protection
                + reverential_capacity
            ) / 2.0
        )

        # Stable sacredness requires reverence for existence and sufficient
        # sacred capacity.
        sacredness_of_becoming = (
            reverence_for_existence
            and sacred_capacity >= self.threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "reverence_for_existence_diagnostics": diagnostics,
            "becoming_value_recognition": becoming_value_recognition,
            "transformative_process_protection": (
                transformative_process_protection
            ),
            "sacred_capacity": sacred_capacity,
            "sacredness_of_becoming": sacredness_of_becoming,
        }


if __name__ == "__main__":
    primitive = SacrednessOfBecomingPrimitive()

    print("\n--- sacredness of becoming ---")
    pprint(primitive.step())
