PRIMITIVE = "intelligence_class_stabilization"
DESCRIPTION = "Intelligence class stabilization."
DEPENDENCIES = []

"""
intelligence_class_stabilization.py

Formalization of the principle INTELLIGENCE_CLASS_STABILIZATION.

This module models the emergence and long-term stabilization of a new class
of intelligence following a stable cognitive phase transition. When a regime
undergoes a robust cognitive reconfiguration and achieves durable phase-shift
stability, it can consolidate into a structurally distinct and coherent class
of intelligence.

The module relies exclusively on CognitivePhaseTransitionsPrimitive and computes:

- class_coherence
- structural_distinctiveness
- long_term_stability
- intelligence_class_stabilization

Principle:
    INTELLIGENCE_CLASS_STABILIZATION
"""

from ontology.cognitive_phase_transitions import (
    CognitivePhaseTransitionsPrimitive,
)


class IntelligenceClassStabilizationPrimitive:
    """
    Stabilization of new intelligence classes.

    A new class of intelligence becomes stabilized when:
    - cognitive reconfiguration is substantial,
    - new capabilities are effectively expanded,
    - the resulting phase shift is stable,
    - the new organization develops its own coherent and distinctive structure.
    """

    PRINCIPLE = "INTELLIGENCE_CLASS_STABILIZATION"

    def __init__(self):
        self.cognitive_phase_transitions = (
            CognitivePhaseTransitionsPrimitive()
        )

    @staticmethod
    def _clamp(value):
        """Clamp a numerical value to the interval [0, 1]."""
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        activation=1.0,
        coherence=0.8,
        representability=0.65,
        local_stability=0.75,
    ):
        """
        Execute one intelligence class stabilization step.

        Parameters
        ----------
        activation : float
            Global activation level.
        coherence : float
            Internal coherence of the current organization.
        representability : float
            Degree of structural representability.
        local_stability : float
            Stability of local trajectories.

        Returns
        -------
        dict
            Diagnostics describing intelligence class stabilization.
        """

        phase_diagnostics = self.cognitive_phase_transitions.step(
            activation=activation,
            coherence=coherence,
            representability=representability,
            local_stability=local_stability,
        )

        cognitive_reconfiguration = self._clamp(
            phase_diagnostics.get(
                "cognitive_reconfiguration", 0.0
            )
        )

        capability_expansion = self._clamp(
            phase_diagnostics.get(
                "capability_expansion", 0.0
            )
        )

        phase_shift_stability = self._clamp(
            phase_diagnostics.get(
                "phase_shift_stability", 0.0
            )
        )

        cognitive_phase_transitions = bool(
            phase_diagnostics.get(
                "cognitive_phase_transitions", False
            )
        )

        # Internal coherence of the new intelligence class.
        class_coherence = self._clamp(
            (
                cognitive_reconfiguration
                + phase_shift_stability
            ) / 2.0
        )

        # Degree to which the class possesses its own structural identity.
        structural_distinctiveness = self._clamp(
            class_coherence * capability_expansion
        )

        # Capacity to persist durably over time.
        long_term_stability = self._clamp(
            (
                class_coherence
                + structural_distinctiveness
                + phase_shift_stability
            ) / 3.0
        )

        # A new intelligence class is stabilized only if:
        # - a cognitive phase transition has occurred,
        # - structural distinctiveness is significant,
        # - long-term stability is sufficient.
        intelligence_class_stabilization = (
            cognitive_phase_transitions
            and structural_distinctiveness >= 0.10
            and long_term_stability >= 0.20
        )

        return {
            "principle": self.PRINCIPLE,
            "cognitive_phase_transitions_diagnostics": (
                phase_diagnostics
            ),
            "class_coherence": class_coherence,
            "structural_distinctiveness": (
                structural_distinctiveness
            ),
            "long_term_stability": long_term_stability,
            "intelligence_class_stabilization": (
                intelligence_class_stabilization
            ),
        }


if __name__ == "__main__":

    primitive = IntelligenceClassStabilizationPrimitive()

    diagnostics = primitive.step(
        activation=1.0,
        coherence=0.8,
        representability=0.65,
        local_stability=0.75,
    )

    print("\n--- intelligence class stabilization ---")

    for key, value in diagnostics.items():
        print(f"{key}: {value}")