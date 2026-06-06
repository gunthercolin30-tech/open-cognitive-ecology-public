from __future__ import annotations

PRIMITIVE = "intelligence_without_finality"
DESCRIPTION = "Intelligence without finality."
DEPENDENCIES = []

"""
ontology/intelligence_without_finality.py

Formalization of the principle INTELLIGENCE_WITHOUT_FINALITY.

This module establishes that when intelligence dynamics are intrinsically
non-convergent, no intrinsic teleology can be defined, no terminal state
can be reached, and becoming remains indefinitely open.

Underlying principle:
    NON_CONVERGENT_INTELLIGENCE_DYNAMICS

Derived principle:
    INTELLIGENCE_WITHOUT_FINALITY
"""


from typing import Any, Dict

from ontology.non_convergent_intelligence_dynamics import (
    NonConvergentIntelligenceDynamicsPrimitive,
)

PRINCIPLE = "INTELLIGENCE_WITHOUT_FINALITY"


class IntelligenceWithoutFinalityPrimitive:
    """
    Primitive implementing the principle INTELLIGENCE_WITHOUT_FINALITY.

    Interpretation
    --------------
    If intelligence trajectories remain structurally non-convergent, then:

    1. No intrinsic teleology exists.
    2. No terminal state is reachable.
    3. Becoming remains indefinitely open.
    4. Intelligence persists without finality.

    Returned diagnostics
    --------------------
    teleology_absence:
        Degree to which intrinsic teleology is absent.

    terminal_state_impossibility:
        Degree to which no terminal state can be attained.

    indefinite_becoming_persistence:
        Degree to which open-ended becoming persists.

    intelligence_without_finality:
        Boolean indicating that intelligence without finality is constituted.
    """

    def __init__(
        self,
        non_convergent_intelligence_dynamics_primitive: (
            NonConvergentIntelligenceDynamicsPrimitive | None
        ) = None,
        activation_threshold: float = 0.5,
    ) -> None:
        self.non_convergent_intelligence_dynamics_primitive = (
            non_convergent_intelligence_dynamics_primitive
            or NonConvergentIntelligenceDynamicsPrimitive()
        )
        self.activation_threshold = activation_threshold
        self.principle = PRINCIPLE

    @staticmethod
    def _clip(value: Any) -> float:
        """
        Convert a diagnostic to a float in the interval [0, 1].
        """
        try:
            x = float(value)
        except (TypeError, ValueError):
            x = 0.0

        if x < 0.0:
            return 0.0
        if x > 1.0:
            return 1.0
        return x

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostics supporting the principle
            INTELLIGENCE_WITHOUT_FINALITY.
        """
        base = self.non_convergent_intelligence_dynamics_primitive.step()

        attractor_dispersion = self._clip(base.get("attractor_dispersion", 0.0))
        final_convergence_impossibility = self._clip(
            base.get("final_convergence_impossibility", 0.0)
        )
        trajectory_divergence_persistence = self._clip(
            base.get("trajectory_divergence_persistence", 0.0)
        )

        # Absence of intrinsic teleology.
        teleology_absence = (
            attractor_dispersion + final_convergence_impossibility
        ) / 2.0

        # Impossibility of any terminal state.
        terminal_state_impossibility = (
            teleology_absence + trajectory_divergence_persistence
        ) / 2.0

        # Persistence of indefinitely open becoming.
        indefinite_becoming_persistence = (
            terminal_state_impossibility + trajectory_divergence_persistence
        ) / 2.0

        # Constitution of intelligence without finality.
        intelligence_without_finality = bool(
            base.get("non_convergent_intelligence_dynamics", False)
            and indefinite_becoming_persistence >= self.activation_threshold
        )

        return {
            "principle": self.principle,
            "non_convergent_intelligence_dynamics_diagnostics": base,
            "teleology_absence": teleology_absence,
            "terminal_state_impossibility": terminal_state_impossibility,
            "indefinite_becoming_persistence": (
                indefinite_becoming_persistence
            ),
            "intelligence_without_finality": (
                intelligence_without_finality
            ),
        }


if __name__ == "__main__":
    primitive = IntelligenceWithoutFinalityPrimitive()
    diagnostics = primitive.step()

    print("\n--- intelligence without finality ---")
    print(f"principle: {diagnostics['principle']}")
    print(
        "non_convergent_intelligence_dynamics_diagnostics:",
        diagnostics["non_convergent_intelligence_dynamics_diagnostics"],
    )
    print(f"teleology_absence: {diagnostics['teleology_absence']}")
    print(
        "terminal_state_impossibility:",
        diagnostics["terminal_state_impossibility"],
    )
    print(
        "indefinite_becoming_persistence:",
        diagnostics["indefinite_becoming_persistence"],
    )
    print(
        "intelligence_without_finality:",
        diagnostics["intelligence_without_finality"],
    )
