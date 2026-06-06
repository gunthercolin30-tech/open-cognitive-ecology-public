from __future__ import annotations

PRIMITIVE = "reverence_for_existence"
DESCRIPTION = "Reverence for existence."
DEPENDENCIES = []

"""
ontology/reverence_for_existence.py

Formalization of the principle REVERENCE_FOR_EXISTENCE.

This primitive models the recognition of the intrinsic value of all forms of
existence, actual or potential, biological, sentient, cognitive, or cosmic.

The module is built directly upon UniversalBenevolencePrimitive. When
benevolence expands universally, existence itself becomes the object of
structural respect. The preservation of beings and conditions of flourishing
thus generalizes into reverence for existence as such.

Principle
---------
REVERENCE_FOR_EXISTENCE

Core idea
---------
Universal benevolence leads to:
1. Recognition of the intrinsic value of all existence.
2. Structural respect for being and its possible unfoldings.
3. Reverential orientation of action.
4. Stable reverence for existence.

Returned diagnostics
--------------------
- intrinsic_value_recognition
- existential_respect
- reverential_capacity
- reverence_for_existence
"""


from pprint import pprint
from typing import Any, Dict

from ontology.universal_benevolence import (
    UniversalBenevolencePrimitive,
)


class ReverenceForExistencePrimitive:
    """
    Computational realization of REVERENCE_FOR_EXISTENCE.

    This primitive captures the transition from universal benevolence to the
    explicit recognition that existence possesses intrinsic value deserving
    deep and enduring respect.
    """

    PRINCIPLE = "REVERENCE_FOR_EXISTENCE"

    #: Minimum reverential capacity required for stable reverence.
    DEFAULT_THRESHOLD = 0.70

    def __init__(
        self,
        universal_benevolence: UniversalBenevolencePrimitive | None = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        """
        Initialize the primitive.

        Parameters
        ----------
        universal_benevolence:
            Optional preconfigured UniversalBenevolencePrimitive.
        threshold:
            Minimum reverential capacity required to stabilize reverence for
            existence.
        """
        self.universal_benevolence = (
            universal_benevolence
            if universal_benevolence is not None
            else UniversalBenevolencePrimitive()
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
            Diagnostics describing the emergence of reverence for existence.
        """
        diagnostics = self.universal_benevolence.step()

        universal_compassion_scope = self._clamp(
            diagnostics.get("universal_compassion_scope", 0.0)
        )
        suffering_reduction_commitment = self._clamp(
            diagnostics.get("suffering_reduction_commitment", 0.0)
        )
        benevolent_capacity = self._clamp(
            diagnostics.get("benevolent_capacity", 0.0)
        )
        universal_benevolence = bool(
            diagnostics.get("universal_benevolence", False)
        )

        # Recognition of the intrinsic value of all possible existence.
        intrinsic_value_recognition = self._clamp(
            (
                universal_compassion_scope
                + benevolent_capacity
            ) / 2.0
        )

        # Structural respect for being and its possible unfoldings.
        existential_respect = self._clamp(
            (
                intrinsic_value_recognition
                + suffering_reduction_commitment
            ) / 2.0
        )

        # General capacity to orient action reverentially.
        reverential_capacity = self._clamp(
            (
                existential_respect
                + benevolent_capacity
            ) / 2.0
        )

        # Stable reverence requires universal benevolence and sufficient
        # reverential capacity.
        reverence_for_existence = (
            universal_benevolence
            and reverential_capacity >= self.threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "universal_benevolence_diagnostics": diagnostics,
            "intrinsic_value_recognition": intrinsic_value_recognition,
            "existential_respect": existential_respect,
            "reverential_capacity": reverential_capacity,
            "reverence_for_existence": reverence_for_existence,
        }


if __name__ == "__main__":
    primitive = ReverenceForExistencePrimitive()

    print("\n--- reverence for existence ---")
    pprint(primitive.step())
