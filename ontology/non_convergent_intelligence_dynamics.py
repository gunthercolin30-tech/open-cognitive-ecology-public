from __future__ import annotations

PRIMITIVE = "non_convergent_intelligence_dynamics"
DESCRIPTION = "Non convergent intelligence dynamics."
DEPENDENCIES = []

"""
ontology/non_convergent_intelligence_dynamics.py

Formalization of the principle NON_CONVERGENT_INTELLIGENCE_DYNAMICS.

This module establishes that when intelligence evolves in an open-ended
manner, it cannot converge toward a single final attractor. Multiple
configurations remain structurally accessible, novelty continues to be
generated, and trajectories remain persistently divergent. The dynamics of
intelligence are therefore intrinsically non-convergent.

The principle is grounded directly on OpenEndedIntelligenceEvolutionPrimitive,
which provides diagnostics describing structural openness, the absence of a
final optimum, and persistent novelty generation.
"""


from typing import Any, Dict

from ontology.open_ended_intelligence_evolution import (
    OpenEndedIntelligenceEvolutionPrimitive,
)


PRINCIPLE = "NON_CONVERGENT_INTELLIGENCE_DYNAMICS"


class NonConvergentIntelligenceDynamicsPrimitive:
    """
    Primitive formalizing non-convergent intelligence dynamics.

    Interpretation
    --------------
    In an open-ended evolutionary regime, no unique terminal attractor can be
    selected. Divergence among trajectories persists, and intelligence remains
    dynamically distributed across an ever-renewed space of possibilities.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self._evolution = OpenEndedIntelligenceEvolutionPrimitive()

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
            Diagnostics describing the structural non-convergence of
            intelligence dynamics.
        """
        evolution_diagnostics = self._evolution.step()

        evolution_openness = self._clip(
            evolution_diagnostics.get("evolution_openness", 0.0)
        )
        optimality_absence = self._clip(
            evolution_diagnostics.get("optimality_absence", 0.0)
        )
        novelty_generation_persistence = self._clip(
            evolution_diagnostics.get(
                "novelty_generation_persistence",
                0.0,
            )
        )
        open_ended_intelligence_evolution = bool(
            evolution_diagnostics.get(
                "open_ended_intelligence_evolution",
                False,
            )
        )

        # Structural dispersion of reachable attractors.
        attractor_dispersion = self._clip(
            0.5 * evolution_openness
            + 0.5 * novelty_generation_persistence
        )

        # Impossibility of convergence to a unique final attractor.
        final_convergence_impossibility = self._clip(
            0.5 * attractor_dispersion
            + 0.5 * optimality_absence
        )

        # Persistence of divergence among evolutionary trajectories.
        trajectory_divergence_persistence = self._clip(
            0.6 * final_convergence_impossibility
            + 0.4 * novelty_generation_persistence
        )

        # Non-convergent dynamics are constituted when open-ended evolution
        # is active and divergence remains sufficiently persistent.
        non_convergent_intelligence_dynamics = (
            open_ended_intelligence_evolution
            and trajectory_divergence_persistence >= 0.60
        )

        return {
            "principle": self.PRINCIPLE,
            "open_ended_intelligence_evolution_diagnostics": (
                evolution_diagnostics
            ),
            "attractor_dispersion": attractor_dispersion,
            "final_convergence_impossibility": (
                final_convergence_impossibility
            ),
            "trajectory_divergence_persistence": (
                trajectory_divergence_persistence
            ),
            "non_convergent_intelligence_dynamics": (
                non_convergent_intelligence_dynamics
            ),
        }


if __name__ == "__main__":
    primitive = NonConvergentIntelligenceDynamicsPrimitive()
    diagnostics = primitive.step()

    print("\n--- non convergent intelligence dynamics ---")
    for key, value in diagnostics.items():
        print(f"{key}: {value}")
