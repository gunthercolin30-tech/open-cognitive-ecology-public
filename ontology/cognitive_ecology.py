from __future__ import annotations

PRIMITIVE = "cognitive_ecology"
DESCRIPTION = "Cognitive ecology."
DEPENDENCIES = []

"""
ontology/cognitive_ecology.py
=============================

Formalisation du principe :

    COGNITIVE_ECOLOGY

Ce module constitue le niveau synthétique de l'architecture Open Cognitive
Ecology. Il formalise l'émergence d'une écologie cognitive globale dans
laquelle plusieurs classes d'intelligences possibles coexistent, interagissent,
se transforment et naviguent au sein d'un espace de trajectoires.

Primitive sous-jacente
----------------------
Ce module repose exclusivement sur :

    MetaTrajectoryNavigationPrimitive

Diagnostics exploités
---------------------
La primitive sous-jacente fournit notamment :

    - trajectory_space
    - navigation_capacity
    - transformation_accessibility
    - meta_trajectory_navigation

Diagnostics produits
--------------------
La méthode ``step()`` retourne :

    - ecology_extent
    - interaction_density
    - adaptive_connectivity
    - cognitive_ecology

Interprétation
--------------
ecology_extent
    Mesure l'étendue effective de l'écosystème des intelligences.

interaction_density
    Mesure la densité potentielle d'interactions entre classes.

adaptive_connectivity
    Mesure la connectivité permettant transformations et adaptations.

cognitive_ecology
    Booléen indiquant qu'une écologie cognitive globale est constituée.

Principe théorique
------------------
Une écologie cognitive émerge lorsque :

1. un espace de trajectoires est suffisamment développé ;
2. la navigation entre trajectoires est possible ;
3. les transformations entre régimes sont accessibles ;
4. l'ensemble forme un réseau adaptatif connecté.

Cette structure constitue un espace global où plusieurs formes
d'intelligence peuvent coexister et évoluer.
"""


from typing import Dict, Any

from ontology.meta_trajectory_navigation import (
    MetaTrajectoryNavigationPrimitive,
)

PRINCIPLE = "COGNITIVE_ECOLOGY"


class CognitiveEcologyPrimitive:
    """
    Primitive formalisant le principe COGNITIVE_ECOLOGY.

    Cette primitive agrège les propriétés de navigation et de transformation
    fournies par MetaTrajectoryNavigationPrimitive afin de déterminer si une
    écologie cognitive globale peut émerger.
    """

    def __init__(self) -> None:
        self.meta_trajectory_navigation = MetaTrajectoryNavigationPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Contraint une valeur dans l'intervalle [0, 1].
        """
        return max(0.0, min(1.0, value))

    def step(self) -> Dict[str, Any]:
        """
        Exécute une étape de calcul du principe COGNITIVE_ECOLOGY.

        Returns
        -------
        dict
            Dictionnaire des diagnostics du principe.
        """
        diagnostics = self.meta_trajectory_navigation.step()

        trajectory_space = float(diagnostics["trajectory_space"])
        navigation_capacity = float(diagnostics["navigation_capacity"])
        transformation_accessibility = float(
            diagnostics["transformation_accessibility"]
        )
        meta_trajectory_navigation = bool(
            diagnostics["meta_trajectory_navigation"]
        )

        # Étendue globale de l'écologie cognitive.
        ecology_extent = self._clamp(
            trajectory_space * transformation_accessibility
        )

        # Densité potentielle d'interactions entre classes d'intelligence.
        interaction_density = self._clamp(
            trajectory_space * navigation_capacity
        )

        # Connectivité adaptative globale.
        adaptive_connectivity = self._clamp(
            (
                navigation_capacity
                + transformation_accessibility
                + interaction_density
            )
            / 3.0
        )

        # Une écologie cognitive globale existe lorsque :
        # - la navigation méta-trajectorielle est active,
        # - l'étendue de l'écologie est significative,
        # - les interactions sont suffisantes,
        # - la connectivité adaptative dépasse un seuil minimal.
        cognitive_ecology = (
            meta_trajectory_navigation
            and ecology_extent > 0.01
            and interaction_density > 0.01
            and adaptive_connectivity > 0.05
        )

        return {
            "principle": PRINCIPLE,
            "meta_trajectory_navigation_diagnostics": diagnostics,
            "ecology_extent": ecology_extent,
            "interaction_density": interaction_density,
            "adaptive_connectivity": adaptive_connectivity,
            "cognitive_ecology": cognitive_ecology,
        }


if __name__ == "__main__":
    primitive = CognitiveEcologyPrimitive()
    diagnostics = primitive.step()

    print("\n--- cognitive ecology ---")
    for key, value in diagnostics.items():
        print(f"{key}: {value}")
