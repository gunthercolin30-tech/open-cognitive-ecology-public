from __future__ import annotations

PRIMITIVE = "open_teleology"
DESCRIPTION = "Open teleology."
DEPENDENCIES = []

"""
ontology/open_teleology.py

Formalization of the principle OPEN_TELEOLOGY.

This module establishes that intelligence can exhibit local directional
orientations without being governed by any terminal goal. Purpose remains
real but structurally open-ended, with no final telos.

Underlying principle:
    INTELLIGENCE_WITHOUT_FINALITY

Derived principle:
    OPEN_TELEOLOGY
"""


from typing import Any, Dict

from ontology.intelligence_without_finality import (
    IntelligenceWithoutFinalityPrimitive,
)

PRINCIPLE = "OPEN_TELEOLOGY"


class OpenTeleologyPrimitive:
    """
    Primitive implementing the principle OPEN_TELEOLOGY.

    Interpretation
    --------------
    In the absence of any final state, intelligence may still display
    local directional tendencies. These orientations are transient and
    non-terminal, and their persistence constitutes an open teleology.

    Returned diagnostics
    --------------------
    local_directionality:
        Degree to which local orientations exist without global finality.

    non_terminal_orientation:
        Degree to which effective orientation targets non-terminal states.

    open_ended_purpose:
        Degree to which purpose remains structurally open.

    open_teleology:
        Boolean indicating that open teleology is constituted.
    """

    def __init__(
        self,
        intelligence_without_finality_primitive: (
            IntelligenceWithoutFinalityPrimitive | None
        ) = None,
        activation_threshold: float = 0.5,
    ) -> None:
        self.intelligence_without_finality_primitive = (
            intelligence_without_finality_primitive
            or IntelligenceWithoutFinalityPrimitive()
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
            Diagnostics supporting the principle OPEN_TELEOLOGY.
        """
        base = self.intelligence_without_finality_primitive.step()

        teleology_absence = self._clip(base.get("teleology_absence", 0.0))
        terminal_state_impossibility = self._clip(
            base.get("terminal_state_impossibility", 0.0)
        )
        indefinite_becoming_persistence = self._clip(
            base.get("indefinite_becoming_persistence", 0.0)
        )

        # Local directional tendencies become possible precisely because
        # no fixed global telos constrains the dynamics.
        local_directionality = (
            teleology_absence + indefinite_becoming_persistence
        ) / 2.0

        # Orientation remains effective while excluding terminal closure.
        non_terminal_orientation = (
            local_directionality + terminal_state_impossibility
        ) / 2.0

        # Purpose persists as an open-ended, non-final process.
        open_ended_purpose = (
            non_terminal_orientation + indefinite_becoming_persistence
        ) / 2.0

        # Constitution of open teleology.
        open_teleology = bool(
            base.get("intelligence_without_finality", False)
            and open_ended_purpose >= self.activation_threshold
        )

        return {
            "principle": self.principle,
            "intelligence_without_finality_diagnostics": base,
            "local_directionality": local_directionality,
            "non_terminal_orientation": non_terminal_orientation,
            "open_ended_purpose": open_ended_purpose,
            "open_teleology": open_teleology,
        }


if __name__ == "__main__":
    primitive = OpenTeleologyPrimitive()
    diagnostics = primitive.step()

    print("\n--- open teleology ---")
    print(f"principle: {diagnostics['principle']}")
    print(
        "intelligence_without_finality_diagnostics:",
        diagnostics["intelligence_without_finality_diagnostics"],
    )
    print(
        f"local_directionality: "
        f"{diagnostics['local_directionality']}"
    )
    print(
        f"non_terminal_orientation: "
        f"{diagnostics['non_terminal_orientation']}"
    )
    print(
        f"open_ended_purpose: "
        f"{diagnostics['open_ended_purpose']}"
    )
    print(
        f"open_teleology: "
        f"{diagnostics['open_teleology']}"
    )
