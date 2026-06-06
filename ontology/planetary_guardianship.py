from __future__ import annotations

PRIMITIVE = "planetary_guardianship"
DESCRIPTION = "Planetary guardianship."
DEPENDENCIES = []

"""
ontology/planetary_guardianship.py

Formalizes the principle that advanced intelligences and civilizations extend
their responsibility to the preservation of planetary habitability, ecological
stability, and biospheric continuity.

This primitive builds directly on CivilizationalStewardshipPrimitive and models
the transition from long-horizon civilizational care to explicit planetary
guardianship.

Principle
---------
PLANETARY_GUARDIANSHIP

Core idea
---------
A civilization becomes a planetary guardian when it recognizes that the
continuity of intelligence depends on preserving the ecological and physical
conditions that sustain life and future evolutionary possibilities.
"""


from pprint import pprint
from typing import Any, Dict

from ontology.civilizational_stewardship import (
    CivilizationalStewardshipPrimitive,
)


PRINCIPLE = "PLANETARY_GUARDIANSHIP"


class PlanetaryGuardianshipPrimitive:
    """
    Formalizes the capacity to preserve planetary habitability and biospheric
    integrity.

    Derived diagnostics
    -------------------
    planetary_habitability_preservation
        Capacity to maintain the planetary conditions necessary for continued
        habitability.

    ecological_responsibility
        Degree to which impacts on living systems are explicitly integrated
        into decision and action.

    biospheric_care_capacity
        Capacity to protect, restore, and sustain biospheric structures and
        ecological dynamics.

    planetary_guardianship
        Indicates whether a stable dynamic of effective planetary guardianship
        has been established.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(
        self,
        stewardship: CivilizationalStewardshipPrimitive | None = None,
        guardianship_threshold: float = 0.60,
    ) -> None:
        """
        Initialize the primitive.

        Parameters
        ----------
        stewardship:
            Optional preconfigured CivilizationalStewardshipPrimitive.
        guardianship_threshold:
            Minimum biospheric care capacity required for planetary
            guardianship to be considered established.
        """
        self.stewardship = (
            stewardship
            if stewardship is not None
            else CivilizationalStewardshipPrimitive()
        )
        self.guardianship_threshold = guardianship_threshold

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a value to the interval [0.0, 1.0]."""
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _mean(*values: float) -> float:
        """Compute the arithmetic mean of values in [0.0, 1.0]."""
        if not values:
            return 0.0
        return sum(values) / len(values)

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostic structure for planetary guardianship.
        """
        stewardship_diagnostics = self.stewardship.step()

        future_conditions_preservation = self._clamp(
            stewardship_diagnostics.get(
                "future_conditions_preservation", 0.0
            )
        )
        intergenerational_responsibility = self._clamp(
            stewardship_diagnostics.get(
                "intergenerational_responsibility", 0.0
            )
        )
        civilizational_care_capacity = self._clamp(
            stewardship_diagnostics.get(
                "civilizational_care_capacity", 0.0
            )
        )
        civilizational_stewardship = bool(
            stewardship_diagnostics.get(
                "civilizational_stewardship", False
            )
        )

        # Capacity to preserve planetary habitability.
        planetary_habitability_preservation = self._clamp(
            self._mean(
                future_conditions_preservation,
                civilizational_care_capacity,
            )
        )

        # Integration of ecological consequences into responsibility.
        ecological_responsibility = self._clamp(
            self._mean(
                planetary_habitability_preservation,
                intergenerational_responsibility,
            )
        )

        # Capacity to actively care for biospheric systems.
        biospheric_care_capacity = self._clamp(
            self._mean(
                ecological_responsibility,
                civilizational_care_capacity,
            )
        )

        # Effective planetary guardianship.
        planetary_guardianship = (
            civilizational_stewardship
            and biospheric_care_capacity >= self.guardianship_threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "civilizational_stewardship_diagnostics": (
                stewardship_diagnostics
            ),
            "planetary_habitability_preservation": (
                planetary_habitability_preservation
            ),
            "ecological_responsibility": ecological_responsibility,
            "biospheric_care_capacity": biospheric_care_capacity,
            "planetary_guardianship": planetary_guardianship,
        }


if __name__ == "__main__":
    primitive = PlanetaryGuardianshipPrimitive()

    print("\n--- planetary guardianship ---")
    pprint(primitive.step())
