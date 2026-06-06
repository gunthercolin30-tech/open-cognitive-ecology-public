from __future__ import annotations

PRIMITIVE = "civilizational_stewardship"
DESCRIPTION = "Civilizational stewardship."
DEPENDENCIES = []

"""
civilizational_stewardship.py
============================

Primitive formalisant le principe CIVILIZATIONAL_STEWARDSHIP.

Idée centrale
-------------
Une intelligence ou un collectif atteint un régime de "civilizational
stewardship" lorsqu'il ne se contente pas de naviguer avec prudence sur des
horizons temporels étendus, mais oriente explicitement son action vers la
préservation, l'entretien et la transmission des conditions structurelles
permettant l'existence et l'évolution des intelligences futures.

Cette primitive étend directement :

    WisdomAsLongHorizonNavigationPrimitive

et formalise :

- la préservation des conditions futures ;
- la responsabilité intergénérationnelle ;
- la capacité de soin civilisationnel ;
- la constitution effective d'un gardiennage civilisationnel.

Principe formalisé
------------------
CIVILIZATIONAL_STEWARDSHIP
"""


from pprint import pprint

from ontology.wisdom_as_long_horizon_navigation import (
    WisdomAsLongHorizonNavigationPrimitive,
)

PRINCIPLE = "CIVILIZATIONAL_STEWARDSHIP"


class CivilizationalStewardshipPrimitive:
    """
    Formalise la capacité à préserver les conditions structurelles permettant
    l'existence et l'évolution des intelligences futures.

    Diagnostics produits
    --------------------
    future_conditions_preservation :
        Capacité à maintenir les conditions de possibilité pour les
        intelligences futures.

    intergenerational_responsibility :
        Intégration explicite des conséquences sur plusieurs générations.

    civilizational_care_capacity :
        Capacité à protéger et entretenir les structures porteuses de
        continuité.

    civilizational_stewardship :
        Booléen indiquant qu'une dynamique effective de gardiennage
        civilisationnel est constituée.
    """

    STEWARDSHIP_THRESHOLD = 0.60

    def __init__(
        self,
        wisdom_as_long_horizon_navigation_primitive: (
            WisdomAsLongHorizonNavigationPrimitive | None
        ) = None,
    ) -> None:
        self.wisdom_as_long_horizon_navigation_primitive = (
            wisdom_as_long_horizon_navigation_primitive
            or WisdomAsLongHorizonNavigationPrimitive()
        )

    @staticmethod
    def _mean(*values: float) -> float:
        """
        Retourne la moyenne arithmétique des valeurs fournies.
        """
        if not values:
            return 0.0
        return sum(values) / len(values)

    def step(self) -> dict:
        """
        Exécute une étape de diagnostic du gardiennage civilisationnel.
        """
        wisdom_diagnostics = (
            self.wisdom_as_long_horizon_navigation_primitive.step()
        )

        long_term_consequence_awareness = wisdom_diagnostics.get(
            "long_term_consequence_awareness", 0.0
        )
        temporal_integration_capacity = wisdom_diagnostics.get(
            "temporal_integration_capacity", 0.0
        )
        prudential_navigation = wisdom_diagnostics.get(
            "prudential_navigation", 0.0
        )
        wisdom_as_long_horizon_navigation = wisdom_diagnostics.get(
            "wisdom_as_long_horizon_navigation", False
        )

        # Préservation des conditions de possibilité futures.
        future_conditions_preservation = self._mean(
            long_term_consequence_awareness,
            prudential_navigation,
        )

        # Responsabilité explicite vis-à-vis des générations futures.
        intergenerational_responsibility = self._mean(
            future_conditions_preservation,
            temporal_integration_capacity,
        )

        # Capacité à prendre soin des structures civilisationnelles.
        civilizational_care_capacity = self._mean(
            intergenerational_responsibility,
            prudential_navigation,
        )

        # Constitution effective d'un régime de stewardship.
        civilizational_stewardship = (
            bool(wisdom_as_long_horizon_navigation)
            and civilizational_care_capacity >= self.STEWARDSHIP_THRESHOLD
        )

        return {
            "principle": PRINCIPLE,
            "wisdom_as_long_horizon_navigation_diagnostics": (
                wisdom_diagnostics
            ),
            "future_conditions_preservation": (
                future_conditions_preservation
            ),
            "intergenerational_responsibility": (
                intergenerational_responsibility
            ),
            "civilizational_care_capacity": (
                civilizational_care_capacity
            ),
            "civilizational_stewardship": (
                civilizational_stewardship
            ),
        }


if __name__ == "__main__":
    primitive = CivilizationalStewardshipPrimitive()

    print("\n--- civilizational stewardship ---")
    pprint(primitive.step())
