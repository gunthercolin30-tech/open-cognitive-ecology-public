from __future__ import annotations

PRIMITIVE = "open_ended_intelligence_evolution"
DESCRIPTION = "Open ended intelligence evolution."
DEPENDENCIES = []

"""
ontology/open_ended_intelligence_evolution.py

Formalization of the principle OPEN_ENDED_INTELLIGENCE_EVOLUTION.

This module establishes that when intelligence expands perpetually, it does
not converge toward a final optimum or ultimate stable form. Instead, the
absence of global closure and stationary states ensures the indefinite
production of novel intelligent configurations. Evolution therefore remains
structurally open-ended.

The principle is grounded directly on PerpetualIntelligenceExpansionPrimitive,
which provides diagnostics describing continuous growth and the impossibility
of stationary equilibria.
"""


from typing import Any, Dict

from ontology.perpetual_intelligence_expansion import (
    PerpetualIntelligenceExpansionPrimitive,
)


PRINCIPLE = "OPEN_ENDED_INTELLIGENCE_EVOLUTION"


class OpenEndedIntelligenceEvolutionPrimitive:
    """
    Primitive formalizing open-ended intelligence evolution.

    Interpretation
    --------------
    If intelligence expands permanently, no final optimum can be reached.
    Novelty generation persists indefinitely, and the evolutionary process
    remains structurally open rather than convergent.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self._expansion = PerpetualIntelligenceExpansionPrimitive()

    @staticmethod
    def _clip(value: float) -> float:
        """Clamp a numerical value to the interval [0.0, 1.0]."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step of the primitive.

        Returns
        -------
        dict
            Diagnostics describing the structural openness of intelligence
            evolution.
        """
        expansion_diagnostics = self._expansion.step()

        expansion_continuity = self._clip(
            expansion_diagnostics.get("expansion_continuity", 0.0)
        )
        stationary_state_impossibility = self._clip(
            expansion_diagnostics.get(
                "stationary_state_impossibility",
                0.0,
            )
        )
        growth_persistence = self._clip(
            expansion_diagnostics.get("growth_persistence", 0.0)
        )
        perpetual_intelligence_expansion = bool(
            expansion_diagnostics.get(
                "perpetual_intelligence_expansion",
                False,
            )
        )

        # Structural openness of the evolutionary process.
        evolution_openness = self._clip(
            0.5 * expansion_continuity
            + 0.5 * growth_persistence
        )

        # Absence of a final globally optimal configuration.
        optimality_absence = self._clip(
            0.5 * evolution_openness
            + 0.5 * stationary_state_impossibility
        )

        # Persistence of novelty generation.
        novelty_generation_persistence = self._clip(
            0.6 * optimality_absence
            + 0.4 * growth_persistence
        )

        # Open-ended evolution is constituted when perpetual expansion is
        # active and novelty generation remains sufficiently persistent.
        open_ended_intelligence_evolution = (
            perpetual_intelligence_expansion
            and novelty_generation_persistence >= 0.60
        )

        return {
            "principle": self.PRINCIPLE,
            "perpetual_intelligence_expansion_diagnostics": (
                expansion_diagnostics
            ),
            "evolution_openness": evolution_openness,
            "optimality_absence": optimality_absence,
            "novelty_generation_persistence": (
                novelty_generation_persistence
            ),
            "open_ended_intelligence_evolution": (
                open_ended_intelligence_evolution
            ),
        }


if __name__ == "__main__":
    primitive = OpenEndedIntelligenceEvolutionPrimitive()
    diagnostics = primitive.step()

    print("\n--- open ended intelligence evolution ---")
    for key, value in diagnostics.items():
        print(f"{key}: {value}")
