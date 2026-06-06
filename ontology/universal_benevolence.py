from __future__ import annotations

PRIMITIVE = "universal_benevolence"
DESCRIPTION = "Universal benevolence."
DEPENDENCIES = []

"""
ontology/universal_benevolence.py

Formalizes the principle that cosmic custodianship can be extended into a
stable regime of universal benevolence. In this regime, an intelligence or
civilization does not merely preserve habitability conditions, but explicitly
orients its capacities toward the reduction of suffering and the flourishing
of all present and potential forms of life, sentience, and intelligence.

This module depends exclusively on CosmicCustodianshipPrimitive and preserves
the standard API of the project.
"""


from pprint import pprint
from typing import Any, Dict, Optional

from ontology.cosmic_custodianship import (
    CosmicCustodianshipPrimitive,
)

PRINCIPLE = "UNIVERSAL_BENEVOLENCE"


class UniversalBenevolencePrimitive:
    """
    UNIVERSAL_BENEVOLENCE

    Universal benevolence represents the extension of moral concern to the
    broadest possible scope. Once a civilization develops the capacity to
    preserve cosmic habitability and to act as a custodian of future
    possibilities, this custodial orientation can become an explicit commitment
    to reducing suffering and supporting the flourishing of all beings.

    Diagnostics
    -----------
    universal_compassion_scope:
        Effective scope of compassion and moral concern at cosmic scale.

    suffering_reduction_commitment:
        Explicit commitment to reducing suffering and protecting sentient beings.

    benevolent_capacity:
        General capacity to orient action toward preservation and flourishing.

    universal_benevolence:
        True when a stable regime of universal benevolence is established.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(
        self,
        cosmic_custodianship_primitive: Optional[
            CosmicCustodianshipPrimitive
        ] = None,
        activation_threshold: float = 0.70,
    ) -> None:
        """
        Initialize the primitive.

        Parameters
        ----------
        cosmic_custodianship_primitive:
            Optional preconfigured CosmicCustodianshipPrimitive instance.

        activation_threshold:
            Minimum benevolent capacity required to activate universal
            benevolence when cosmic custodianship is already established.
        """
        self.cosmic_custodianship_primitive = (
            cosmic_custodianship_primitive
            if cosmic_custodianship_primitive is not None
            else CosmicCustodianshipPrimitive()
        )
        self.activation_threshold = float(activation_threshold)

    @staticmethod
    def _clip(value: Any) -> float:
        """
        Convert to float and constrain to the [0.0, 1.0] interval.
        """
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0
        return max(0.0, min(1.0, value))

    @staticmethod
    def _mean(*values: Any) -> float:
        """
        Arithmetic mean of clipped values.
        """
        if not values:
            return 0.0
        clipped = [UniversalBenevolencePrimitive._clip(v) for v in values]
        return sum(clipped) / len(clipped)

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostic dictionary for the UNIVERSAL_BENEVOLENCE principle.
        """
        custodianship = self.cosmic_custodianship_primitive.step()

        cosmic_habitability_preservation = self._clip(
            custodianship.get("cosmic_habitability_preservation", 0.0)
        )
        astroecological_responsibility = self._clip(
            custodianship.get("astroecological_responsibility", 0.0)
        )
        cosmic_care_capacity = self._clip(
            custodianship.get("cosmic_care_capacity", 0.0)
        )
        cosmic_custodianship = bool(
            custodianship.get("cosmic_custodianship", False)
        )

        # Effective extension of compassion to the widest possible scope.
        universal_compassion_scope = self._mean(
            cosmic_habitability_preservation,
            astroecological_responsibility,
        )

        # Commitment to reducing suffering and protecting sentient beings.
        suffering_reduction_commitment = self._mean(
            universal_compassion_scope,
            cosmic_care_capacity,
        )

        # General operational capacity to support flourishing.
        benevolent_capacity = self._mean(
            suffering_reduction_commitment,
            cosmic_care_capacity,
        )

        # Stable activation condition.
        universal_benevolence = (
            cosmic_custodianship
            and benevolent_capacity >= self.activation_threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "cosmic_custodianship_diagnostics": custodianship,
            "universal_compassion_scope": universal_compassion_scope,
            "suffering_reduction_commitment": (
                suffering_reduction_commitment
            ),
            "benevolent_capacity": benevolent_capacity,
            "universal_benevolence": universal_benevolence,
        }


if __name__ == "__main__":
    primitive = UniversalBenevolencePrimitive()

    print("\n--- universal benevolence ---")
    pprint(primitive.step())
