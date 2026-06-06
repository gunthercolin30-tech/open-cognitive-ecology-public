from __future__ import annotations

PRIMITIVE = "open_cognitive_ecology"
DESCRIPTION = "Open cognitive ecology."
DEPENDENCIES = []

"""
ontology/open_cognitive_ecology.py
=================================

Formalisation du principe :

    OPEN_COGNITIVE_ECOLOGY

Une écologie cognitive ouverte est une structure dans laquelle aucune
clôture globale définitive ne peut être atteinte. Le système demeure
structurellement capable d'accueillir l'apparition de nouvelles classes
d'intelligences, de nouvelles trajectoires, de nouvelles organisations
et de nouvelles écologies.

La primitive s'appuie directement sur :

    CognitiveEcologyPrimitive

Diagnostics principaux retournés par ``step()`` :

    - openness_degree
    - novelty_capacity
    - closure_impossibility
    - open_cognitive_ecology
"""


from ontology.cognitive_ecology import CognitiveEcologyPrimitive

PRINCIPLE = "OPEN_COGNITIVE_ECOLOGY"


class OpenCognitiveEcologyPrimitive:
    """
    Primitive formalisant le principe OPEN_COGNITIVE_ECOLOGY.

    Interprétation conceptuelle
    --------------------------
    Une écologie cognitive est dite ouverte lorsque :

    1. Son extension structurelle est suffisamment développée.
    2. Les connexions adaptatives permettent des reconfigurations.
    3. Les interactions rendent possible l'émergence de nouveautés.
    4. Toute clôture globale devient structurellement impossible.

    La présence simultanée de ces propriétés indique qu'un univers
    d'intelligences possibles reste indéfiniment extensible.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self.cognitive_ecology = CognitiveEcologyPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Restreint une valeur dans l'intervalle [0, 1].
        """
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Exécute une étape de la primitive OPEN_COGNITIVE_ECOLOGY.

        Returns
        -------
        dict
            {
                "principle": "OPEN_COGNITIVE_ECOLOGY",
                "cognitive_ecology_diagnostics": ...,
                "openness_degree": ...,
                "novelty_capacity": ...,
                "closure_impossibility": ...,
                "open_cognitive_ecology": ...,
            }
        """
        diagnostics = self.cognitive_ecology.step()

        ecology_extent = self._clamp(
            diagnostics.get("ecology_extent", 0.0)
        )
        interaction_density = self._clamp(
            diagnostics.get("interaction_density", 0.0)
        )
        adaptive_connectivity = self._clamp(
            diagnostics.get("adaptive_connectivity", 0.0)
        )
        cognitive_ecology = bool(
            diagnostics.get("cognitive_ecology", False)
        )

        # Degré global d'ouverture structurelle.
        openness_degree = self._clamp(
            0.5 * ecology_extent
            + 0.5 * adaptive_connectivity
        )

        # Capacité d'apparition de nouvelles formes d'intelligence.
        novelty_capacity = self._clamp(
            0.5 * interaction_density
            + 0.5 * adaptive_connectivity
        )

        # Impossibilité structurelle de la clôture globale.
        closure_impossibility = self._clamp(
            0.5 * openness_degree
            + 0.5 * novelty_capacity
        )

        # Seuil minimal indiquant une ouverture effective.
        open_cognitive_ecology = (
            cognitive_ecology
            and closure_impossibility >= 0.50
        )

        return {
            "principle": self.PRINCIPLE,
            "cognitive_ecology_diagnostics": diagnostics,
            "openness_degree": openness_degree,
            "novelty_capacity": novelty_capacity,
            "closure_impossibility": closure_impossibility,
            "open_cognitive_ecology": open_cognitive_ecology,
        }


if __name__ == "__main__":
    primitive = OpenCognitiveEcologyPrimitive()
    diagnostics = primitive.step()

    print("\n--- open cognitive ecology ---")
    print("principle:", diagnostics["principle"])
    print(
        "cognitive_ecology_diagnostics:",
        diagnostics["cognitive_ecology_diagnostics"],
    )
    print("openness_degree:", diagnostics["openness_degree"])
    print("novelty_capacity:", diagnostics["novelty_capacity"])
    print(
        "closure_impossibility:",
        diagnostics["closure_impossibility"],
    )
    print(
        "open_cognitive_ecology:",
        diagnostics["open_cognitive_ecology"],
    )
