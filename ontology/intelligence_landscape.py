from __future__ import annotations

PRIMITIVE = "intelligence_landscape"
DESCRIPTION = "Intelligence landscape."
DEPENDENCIES = []

"""
ontology/intelligence_landscape.py

Formalisation computationnelle du principe :

    INTELLIGENCE_LANDSCAPE

Ce module modélise la cartographie dynamique des classes d'intelligence
stabilisées au sein d'un espace topologique des intelligences possibles.

Le principe repose directement sur :

    IntelligenceClassStabilizationPrimitive

Diagnostics sous-jacents exploités :
    - class_coherence
    - structural_distinctiveness
    - long_term_stability
    - intelligence_class_stabilization

Diagnostics produits :
    - landscape_positioning
    - topological_separation
    - navigation_potential
    - intelligence_landscape
"""


from ontology.intelligence_class_stabilization import (
    IntelligenceClassStabilizationPrimitive,
)

PRINCIPLE = "INTELLIGENCE_LANDSCAPE"


class IntelligenceLandscapePrimitive:
    """
    Primitive formalisant la cartographie topologique des classes
    d'intelligence stabilisées.

    Cette primitive transforme la stabilisation locale d'une classe
    d'intelligence en représentation positionnelle au sein d'un paysage
    global des intelligences possibles.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self.class_stabilization = (
            IntelligenceClassStabilizationPrimitive()
        )

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Contraint une valeur dans l'intervalle [0, 1].
        """
        return max(0.0, min(1.0, value))

    def step(
        self,
        structural_integrity: float = 1.0,
        viability: float = 0.8,
        semantic_consistency: float = 0.65,
        symbolic_density: float = 0.75,
    ) -> dict:
        """
        Exécute un pas de calcul du principe INTELLIGENCE_LANDSCAPE.

        Paramètres
        ----------
        structural_integrity :
            Intégrité structurelle globale.
        viability :
            Viabilité locale.
        semantic_consistency :
            Cohérence sémantique.
        symbolic_density :
            Densité symbolique.

        Retour
        ------
        dict
            Diagnostics du paysage des intelligences.
        """

        # Appel positionnel pour garantir la compatibilité avec
        # IntelligenceClassStabilizationPrimitive.
        diagnostics = self.class_stabilization.step(
            structural_integrity,
            viability,
            semantic_consistency,
            symbolic_density,
        )

        class_coherence = diagnostics["class_coherence"]
        structural_distinctiveness = diagnostics[
            "structural_distinctiveness"
        ]
        long_term_stability = diagnostics["long_term_stability"]
        intelligence_class_stabilization = diagnostics[
            "intelligence_class_stabilization"
        ]

        # Positionnement global dans le paysage topologique.
        landscape_positioning = self._clamp(
            class_coherence
            * structural_distinctiveness
            * long_term_stability
        )

        # Séparation structurelle par rapport aux autres classes.
        topological_separation = self._clamp(
            structural_distinctiveness
            * (0.5 + 0.5 * class_coherence)
        )

        # Potentiel de navigation entre classes voisines.
        navigation_potential = self._clamp(
            landscape_positioning
            * topological_separation
        )

        # Le paysage est considéré comme établi si :
        # - la classe d'intelligence est stabilisée,
        # - les diagnostics dépassent les seuils minimaux.
        intelligence_landscape = (
            intelligence_class_stabilization
            and landscape_positioning > 0.10
            and topological_separation > 0.10
            and navigation_potential > 0.01
        )

        return {
            "principle": self.PRINCIPLE,
            "intelligence_class_stabilization_diagnostics": diagnostics,
            "landscape_positioning": landscape_positioning,
            "topological_separation": topological_separation,
            "navigation_potential": navigation_potential,
            "intelligence_landscape": intelligence_landscape,
        }


if __name__ == "__main__":
    primitive = IntelligenceLandscapePrimitive()

    results = primitive.step(
        structural_integrity=1.0,
        viability=0.8,
        semantic_consistency=0.65,
        symbolic_density=0.75,
    )

    print("\n--- intelligence landscape ---")
    print("principle:", results["principle"])
    print(
        "intelligence_class_stabilization_diagnostics:",
        results["intelligence_class_stabilization_diagnostics"],
    )
    print("landscape_positioning:", results["landscape_positioning"])
    print("topological_separation:", results["topological_separation"])
    print("navigation_potential:", results["navigation_potential"])
    print("intelligence_landscape:", results["intelligence_landscape"])
