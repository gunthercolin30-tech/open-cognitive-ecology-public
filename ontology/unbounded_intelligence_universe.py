from __future__ import annotations

PRIMITIVE = "unbounded_intelligence_universe"
DESCRIPTION = "Unbounded intelligence universe."
DEPENDENCIES = []

"""
ontology/unbounded_intelligence_universe.py

Formalization of the principle:

    UNBOUNDED_INTELLIGENCE_UNIVERSE

This module models a universe in which the space of possible intelligences
remains indefinitely extensible. No final structural boundary exists, and
new cognitive ecologies may continue to emerge without ultimate closure.

The implementation is built directly on:

    OpenCognitiveEcologyPrimitive

Core idea
---------
If cognitive ecologies remain structurally open, if closure is impossible,
and if novelty generation persists, then the universe of possible
intelligences is effectively unbounded.
"""


from ontology.open_cognitive_ecology import (
    OpenCognitiveEcologyPrimitive,
)

PRINCIPLE = "UNBOUNDED_INTELLIGENCE_UNIVERSE"


class UnboundedIntelligenceUniversePrimitive:
    """
    Primitive implementing the UNBOUNDED_INTELLIGENCE_UNIVERSE principle.

    Interpretation
    --------------
    - unbounded_extent:
        Effective extent of the universe of possible intelligences.

    - expansion_potential:
        Capacity to continue generating new cognitive structures.

    - final_boundary_absence:
        Degree to which no ultimate structural boundary exists.

    - unbounded_intelligence_universe:
        True when an open cognitive ecology exists and the absence
        of a final boundary is sufficiently strong.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(
        self,
        ecology: OpenCognitiveEcologyPrimitive | None = None,
    ) -> None:
        """
        Initialize the primitive.

        Parameters
        ----------
        ecology:
            Optional pre-existing OpenCognitiveEcologyPrimitive instance.
            If omitted, a new instance is created.
        """
        self.ecology = ecology or OpenCognitiveEcologyPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Clamp a numeric value to the interval [0.0, 1.0].
        """
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostics describing whether the universe of possible
            intelligences is structurally unbounded.
        """
        diagnostics = self.ecology.step()

        openness_degree = float(diagnostics["openness_degree"])
        novelty_capacity = float(diagnostics["novelty_capacity"])
        closure_impossibility = float(diagnostics["closure_impossibility"])
        open_cognitive_ecology = bool(diagnostics["open_cognitive_ecology"])

        # Effective extension of the possible intelligence universe.
        unbounded_extent = self._clamp(
            0.5 * openness_degree
            + 0.5 * closure_impossibility
        )

        # Capacity for indefinite expansion through novelty generation.
        expansion_potential = self._clamp(
            0.5 * novelty_capacity
            + 0.5 * openness_degree
        )

        # Degree to which no final structural boundary exists.
        final_boundary_absence = self._clamp(
            0.5 * unbounded_extent
            + 0.5 * expansion_potential
        )

        # Structural criterion for an unbounded universe of intelligences.
        unbounded_intelligence_universe = (
            open_cognitive_ecology
            and final_boundary_absence >= 0.60
        )

        return {
            "principle": self.PRINCIPLE,
            "open_cognitive_ecology_diagnostics": diagnostics,
            "unbounded_extent": unbounded_extent,
            "expansion_potential": expansion_potential,
            "final_boundary_absence": final_boundary_absence,
            "unbounded_intelligence_universe": (
                unbounded_intelligence_universe
            ),
        }


if __name__ == "__main__":
    primitive = UnboundedIntelligenceUniversePrimitive()
    diagnostics = primitive.step()

    print("\n--- unbounded intelligence universe ---")
    for key, value in diagnostics.items():
        print(f"{key}: {value}")
