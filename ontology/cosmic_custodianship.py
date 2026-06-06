from __future__ import annotations

PRIMITIVE = "cosmic_custodianship"
DESCRIPTION = "Cosmic custodianship."
DEPENDENCIES = []

"""
ontology/cosmic_custodianship.py

Formalization of the principle COSMIC_CUSTODIANSHIP.

This primitive extends planetary guardianship toward the cosmological scale.
It models the capacity of an intelligence or civilization to preserve the
astrophysical and astroecological conditions that support the emergence,
continuity, and diversification of intelligent processes throughout the universe.

The principle asserts that sufficiently mature intelligence does not restrict
its responsibility to local biospheres, but recognizes habitable environments
as cosmologically valuable and worthy of preservation. Care becomes a universal
function directed toward the maintenance of conditions under which life and
intelligence can continue to unfold.

Dependencies:
    - ontology.planetary_guardianship.PlanetaryGuardianshipPrimitive
"""


from pprint import pprint
from typing import Any, Dict, Optional

from ontology.planetary_guardianship import (
    PlanetaryGuardianshipPrimitive,
)


class CosmicCustodianshipPrimitive:
    """
    Formalizes the principle COSMIC_CUSTODIANSHIP.

    Diagnostic interpretation
    -------------------------
    cosmic_habitability_preservation:
        Capacity to preserve cosmological conditions favorable to the emergence
        and continuity of intelligence.

    astroecological_responsibility:
        Explicit integration of consequences for living and potentially living
        systems at cosmic scale.

    cosmic_care_capacity:
        Capacity to extend care, protection, and maintenance to all habitable
        environments.

    cosmic_custodianship:
        Boolean indicating that effective cosmological responsibility has been
        constituted.
    """

    PRINCIPLE = "COSMIC_CUSTODIANSHIP"

    def __init__(
        self,
        planetary_guardianship_primitive: Optional[
            PlanetaryGuardianshipPrimitive
        ] = None,
        custodianship_threshold: float = 0.5,
    ) -> None:
        self.planetary_guardianship_primitive = (
            planetary_guardianship_primitive
            if planetary_guardianship_primitive is not None
            else PlanetaryGuardianshipPrimitive()
        )
        self.custodianship_threshold = float(custodianship_threshold)

    @staticmethod
    def _clip(value: Any) -> float:
        """
        Convert a value to a float and constrain it to the interval [0, 1].
        """
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = 0.0
        return max(0.0, min(1.0, numeric))

    @staticmethod
    def _mean(*values: Any) -> float:
        """
        Compute the arithmetic mean of the provided values after clipping them
        to the interval [0, 1].
        """
        if not values:
            return 0.0
        normalized = [CosmicCustodianshipPrimitive._clip(v) for v in values]
        return sum(normalized) / len(normalized)

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step of cosmic custodianship.
        """
        planetary_diagnostics = self.planetary_guardianship_primitive.step()

        planetary_habitability_preservation = self._clip(
            planetary_diagnostics.get(
                "planetary_habitability_preservation", 0.0
            )
        )
        ecological_responsibility = self._clip(
            planetary_diagnostics.get("ecological_responsibility", 0.0)
        )
        biospheric_care_capacity = self._clip(
            planetary_diagnostics.get("biospheric_care_capacity", 0.0)
        )
        planetary_guardianship = bool(
            planetary_diagnostics.get("planetary_guardianship", False)
        )

        # Capacity to preserve cosmic habitability conditions.
        cosmic_habitability_preservation = self._mean(
            planetary_habitability_preservation,
            biospheric_care_capacity,
        )

        # Explicit responsibility toward living and potentially living systems
        # at astrophysical and cosmological scales.
        astroecological_responsibility = self._mean(
            cosmic_habitability_preservation,
            ecological_responsibility,
        )

        # Generalized capacity to care for habitable environments.
        cosmic_care_capacity = self._mean(
            astroecological_responsibility,
            biospheric_care_capacity,
        )

        # Effective cosmological stewardship.
        cosmic_custodianship = (
            planetary_guardianship
            and cosmic_care_capacity >= self.custodianship_threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "planetary_guardianship_diagnostics": planetary_diagnostics,
            "cosmic_habitability_preservation": (
                cosmic_habitability_preservation
            ),
            "astroecological_responsibility": (
                astroecological_responsibility
            ),
            "cosmic_care_capacity": cosmic_care_capacity,
            "cosmic_custodianship": cosmic_custodianship,
        }


if __name__ == "__main__":
    primitive = CosmicCustodianshipPrimitive()

    print("\n--- cosmic custodianship ---")
    pprint(primitive.step())
