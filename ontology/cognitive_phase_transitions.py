PRIMITIVE = "cognitive_phase_transitions"
DESCRIPTION = "Cognitive phase transitions."
DEPENDENCIES = []

"""
cognitive_phase_transitions.py

Formalization of the principle COGNITIVE_PHASE_TRANSITIONS.

This module models qualitative transitions occurring within autonomous
structural regimes. When a regime becomes sufficiently self-maintained,
coherent, and operationally viable, it can undergo a cognitive phase shift
that reorganizes its internal structure and grants access to new classes
of behaviors and capabilities.

The module relies exclusively on AutonomousRegimesPrimitive and computes:

- cognitive_reconfiguration
- capability_expansion
- phase_shift_stability
- cognitive_phase_transitions

Principle:
    COGNITIVE_PHASE_TRANSITIONS
"""

from ontology.autonomous_regimes import (
    AutonomousRegimesPrimitive,
)


class CognitivePhaseTransitionsPrimitive:
    """
    Cognitive phase transitions.

    A cognitive phase transition occurs when an autonomous regime:
    - undergoes a substantial structural reconfiguration,
    - gains access to expanded capabilities,
    - stabilizes the resulting phase shift,
    - sustains a new qualitative mode of organization.
    """

    PRINCIPLE = "COGNITIVE_PHASE_TRANSITIONS"

    def __init__(self):
        self.autonomous_regimes = AutonomousRegimesPrimitive()

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
        Execute one cognitive phase transition step.

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
            Diagnostics describing cognitive phase transitions.
        """

        regime_diagnostics = self.autonomous_regimes.step(
            activation=activation,
            coherence=coherence,
            representability=representability,
            local_stability=local_stability,
        )

        self_maintenance = self._clamp(
            regime_diagnostics.get("self_maintenance", 0.0)
        )

        internal_coherence_reinforcement = self._clamp(
            regime_diagnostics.get(
                "internal_coherence_reinforcement", 0.0
            )
        )

        operational_viability = self._clamp(
            regime_diagnostics.get("operational_viability", 0.0)
        )

        autonomous_regimes = bool(
            regime_diagnostics.get("autonomous_regimes", False)
        )

        # Extent of structural reorganization.
        cognitive_reconfiguration = self._clamp(
            (
                self_maintenance
                + internal_coherence_reinforcement
            ) / 2.0
        )

        # Access to new behavioral and functional capacities.
        capability_expansion = self._clamp(
            cognitive_reconfiguration * operational_viability
        )

        # Stability of the resulting cognitive phase.
        phase_shift_stability = self._clamp(
            (
                capability_expansion
                + operational_viability
            ) / 2.0
        )

        # A genuine cognitive phase transition requires:
        # - an established autonomous regime,
        # - substantial capability expansion,
        # - a stable resulting phase.
        cognitive_phase_transitions = (
            autonomous_regimes
            and capability_expansion >= 0.15
            and phase_shift_stability >= 0.20
        )

        return {
            "principle": self.PRINCIPLE,
            "autonomous_regimes_diagnostics": regime_diagnostics,
            "cognitive_reconfiguration": cognitive_reconfiguration,
            "capability_expansion": capability_expansion,
            "phase_shift_stability": phase_shift_stability,
            "cognitive_phase_transitions": (
                cognitive_phase_transitions
            ),
        }


if __name__ == "__main__":

    primitive = CognitivePhaseTransitionsPrimitive()

    diagnostics = primitive.step(
        activation=1.0,
        coherence=0.8,
        representability=0.65,
        local_stability=0.75,
    )

    print("\n--- cognitive phase transitions ---")

    for key, value in diagnostics.items():
        print(f"{key}: {value}")