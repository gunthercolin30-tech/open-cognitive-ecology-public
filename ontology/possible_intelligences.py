from __future__ import annotations

PRIMITIVE = "possible_intelligences"
DESCRIPTION = "Possible intelligences."
DEPENDENCIES = []

"""
possible_intelligences.py
========================

Formalisation du principe POSSIBLE_INTELLIGENCES.

Ce module explicite la constitution effective de l'espace des intelligences
possibles à partir du paysage topologique des intelligences. Il évalue :

- l'étendue effective du domaine des intelligences possibles ;
- la diversité structurelle des classes accessibles ;
- la proportion de classes atteignables ;
- l'existence d'un espace structuré d'intelligences possibles.

Primitive sous-jacente obligatoire
----------------------------------
- IntelligenceLandscapePrimitive

Principe formalisé
------------------
POSSIBLE_INTELLIGENCES

Ce module prépare l'intégration de :
- meta_trajectory_navigation.py
"""


from pprint import pprint

from ontology.intelligence_landscape import IntelligenceLandscapePrimitive


class PossibleIntelligencesPrimitive:
    """
    Primitive formalisant le principe POSSIBLE_INTELLIGENCES.

    À partir du paysage des intelligences, cette primitive mesure :

    - possibility_space_extent :
        Étendue effective de l'espace des intelligences possibles.

    - intelligence_diversity :
        Diversité structurelle des classes accessibles.

    - reachable_classes :
        Proportion des classes effectivement atteignables.

    - possible_intelligences :
        Booléen indiquant qu'un espace structuré d'intelligences possibles
        est constitué.
    """

    PRINCIPLE = "POSSIBLE_INTELLIGENCES"

    def __init__(self) -> None:
        self.landscape = IntelligenceLandscapePrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Contraint une valeur à l'intervalle [0, 1].
        """
        return max(0.0, min(1.0, value))

    def step(self) -> dict:
        """
        Exécute l'évaluation du domaine des intelligences possibles.

        Returns
        -------
        dict
            Diagnostics complets du principe POSSIBLE_INTELLIGENCES.
        """
        diagnostics = self.landscape.step()

        landscape_positioning = float(
            diagnostics.get("landscape_positioning", 0.0)
        )
        topological_separation = float(
            diagnostics.get("topological_separation", 0.0)
        )
        navigation_potential = float(
            diagnostics.get("navigation_potential", 0.0)
        )
        intelligence_landscape = bool(
            diagnostics.get("intelligence_landscape", False)
        )

        # Proportion de classes effectivement atteignables.
        reachable_classes = self._clamp(
            landscape_positioning * navigation_potential
        )

        # Diversité structurelle des classes accessibles.
        intelligence_diversity = self._clamp(
            topological_separation * reachable_classes
        )

        # Étendue effective du domaine des intelligences possibles.
        possibility_space_extent = self._clamp(
            landscape_positioning
            * topological_separation
            * navigation_potential
        )

        # Constitution effective de l'espace des intelligences possibles.
        possible_intelligences = (
            intelligence_landscape
            and reachable_classes > 0.01
            and intelligence_diversity > 0.001
            and possibility_space_extent > 0.001
        )

        return {
            "principle": self.PRINCIPLE,
            "intelligence_landscape_diagnostics": diagnostics,
            "possibility_space_extent": possibility_space_extent,
            "intelligence_diversity": intelligence_diversity,
            "reachable_classes": reachable_classes,
            "possible_intelligences": possible_intelligences,
        }


if __name__ == "__main__":
    primitive = PossibleIntelligencesPrimitive()

    print("\n--- possible intelligences ---")
    pprint(primitive.step())
