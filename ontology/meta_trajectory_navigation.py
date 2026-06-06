from __future__ import annotations

PRIMITIVE = "meta_trajectory_navigation"
DESCRIPTION = "Meta trajectory navigation."
DEPENDENCIES = []

"""
ontology/meta_trajectory_navigation.py

Formalisation du principe :

    META_TRAJECTORY_NAVIGATION

Ce module modélise la capacité de navigation entre classes
d'intelligences au sein de l'espace structuré des intelligences
possibles.

Primitive sous-jacente :
    PossibleIntelligencesPrimitive

Diagnostics exploités :
    - possibility_space_extent
    - intelligence_diversity
    - reachable_classes
    - possible_intelligences

Diagnostics produits :
    - trajectory_space
    - navigation_capacity
    - transformation_accessibility
    - meta_trajectory_navigation

Interprétation :
    - trajectory_space :
        Étendue effective des trajectoires entre classes
        d'intelligences.
    - navigation_capacity :
        Capacité à explorer activement cet espace.
    - transformation_accessibility :
        Accessibilité moyenne des transformations entre classes.
    - meta_trajectory_navigation :
        Indique si une navigation structurée entre classes
        d'intelligences est effectivement possible.
"""


from typing import Dict

from ontology.possible_intelligences import (
    PossibleIntelligencesPrimitive,
)

PRINCIPLE = "META_TRAJECTORY_NAVIGATION"


class MetaTrajectoryNavigationPrimitive:
    """
    Primitive de navigation entre classes d'intelligences.

    Cette primitive repose sur la structure de l'espace des
    intelligences possibles et estime la capacité d'un système
    à parcourir les transformations admissibles entre classes.
    """

    def __init__(
        self,
        possible_intelligences_primitive: PossibleIntelligencesPrimitive | None = None,
    ) -> None:
        self.possible_intelligences_primitive = (
            possible_intelligences_primitive
            if possible_intelligences_primitive is not None
            else PossibleIntelligencesPrimitive()
        )

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Contraint une valeur dans l'intervalle [0, 1].
        """
        return max(0.0, min(1.0, value))

    def step(self) -> Dict[str, object]:
        """
        Exécute une étape d'évaluation de la navigation
        entre classes d'intelligences.

        Returns
        -------
        dict
            {
                "principle": PRINCIPLE,
                "possible_intelligences_diagnostics": ...,
                "trajectory_space": float,
                "navigation_capacity": float,
                "transformation_accessibility": float,
                "meta_trajectory_navigation": bool,
            }
        """
        diagnostics = self.possible_intelligences_primitive.step()

        possibility_space_extent = float(
            diagnostics.get("possibility_space_extent", 0.0)
        )
        intelligence_diversity = float(
            diagnostics.get("intelligence_diversity", 0.0)
        )
        reachable_classes = float(
            diagnostics.get("reachable_classes", 0.0)
        )
        possible_intelligences = bool(
            diagnostics.get("possible_intelligences", False)
        )

        # Étendue effective de l'espace des trajectoires.
        trajectory_space = self._clamp(
            possibility_space_extent
            * intelligence_diversity
            * reachable_classes
        )

        # Capacité de navigation active.
        navigation_capacity = self._clamp(
            trajectory_space * reachable_classes
        )

        # Accessibilité moyenne des transformations entre classes.
        transformation_accessibility = self._clamp(
            intelligence_diversity * reachable_classes
        )

        # Navigation structurée possible si l'espace existe
        # et si les transformations sont suffisamment accessibles.
        meta_trajectory_navigation = (
            possible_intelligences
            and trajectory_space > 0.05
            and navigation_capacity > 0.01
            and transformation_accessibility > 0.05
        )

        return {
            "principle": PRINCIPLE,
            "possible_intelligences_diagnostics": diagnostics,
            "trajectory_space": trajectory_space,
            "navigation_capacity": navigation_capacity,
            "transformation_accessibility": transformation_accessibility,
            "meta_trajectory_navigation": meta_trajectory_navigation,
        }


if __name__ == "__main__":
    primitive = MetaTrajectoryNavigationPrimitive()
    diagnostics = primitive.step()

    print("\n--- meta trajectory navigation ---")
    for key, value in diagnostics.items():
        print(f"{key}: {value}")
