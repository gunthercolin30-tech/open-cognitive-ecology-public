PRIMITIVE = "critical_transitions"
DESCRIPTION = "Critical transitions."
DEPENDENCIES = []

"""
critical_transitions.py

Formalization of the principle CRITICAL_TRANSITIONS.

This module models the onset of critical transitions in evolving symbolic
ecologies. When diversification pressure, branching potential, and adaptive
plasticity jointly exceed stability thresholds, the system may undergo a
qualitative structural transition and access a novel configuration regime.

The module relies exclusively on EvolutionaryDiversificationPrimitive and
computes:

- transition_pressure
- regime_shift_intensity
- novel_configuration_access
- critical_transitions

Principle:
    CRITICAL_TRANSITIONS
"""

from ontology.evolutionary_diversification import (
    EvolutionaryDiversificationPrimitive,
)


class CriticalTransitionsPrimitive:
    """
    Critical structural transitions.

    A critical transition occurs when:
    - diversification pressure becomes sufficiently high,
    - branching dynamics intensify,
    - adaptive plasticity remains available,
    - the system accesses a new structural configuration.
    """

    PRINCIPLE = "CRITICAL_TRANSITIONS"

    def __init__(self):
        self.evolutionary_diversification = (
            EvolutionaryDiversificationPrimitive()
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
        Execute one critical transition step.

        Parameters
        ----------
        activation : float
            Global activation level (retained for API consistency).
        coherence : float
            Internal coherence of the current organization.
        representability : float
            Degree of structural representability.
        local_stability : float
            Stability of local trajectories.

        Returns
        -------
        dict
            Diagnostics describing critical transitions.
        """

        # EvolutionaryDiversificationPrimitive in the current project
        # accepts only positional arguments. We therefore pass values
        # positionally to guarantee compatibility regardless of the
        # parameter names used internally.
        diversification = self.evolutionary_diversification.step(
            coherence,
            representability,
            local_stability,
        )

        diversification_pressure = self._clamp(
            diversification.get(
                "diversification_pressure",
                diversification.get("branching_pressure", 0.0),
            )
        )

        branching_potential = self._clamp(
            diversification.get("branching_potential", 0.0)
        )

        adaptive_plasticity = self._clamp(
            diversification.get("adaptive_plasticity", 0.0)
        )

        evolutionary_diversification = bool(
            diversification.get(
                "evolutionary_diversification",
                diversification.get("diversification", False),
            )
        )

        # Global pressure toward structural reorganization.
        transition_pressure = self._clamp(
            (
                diversification_pressure
                + branching_potential
                + adaptive_plasticity
            )
            / 3.0
        )

        # Magnitude of the structural shift.
        regime_shift_intensity = self._clamp(
            transition_pressure * branching_potential
        )

        # Access to a novel configuration regime.
        novel_configuration_access = self._clamp(
            regime_shift_intensity * adaptive_plasticity
        )

        # A critical transition is considered effective only if:
        # - evolutionary diversification is active,
        # - transition pressure is substantial,
        # - access to a new configuration is non-negligible.
        critical_transitions = (
            evolutionary_diversification
            and transition_pressure >= 0.30
            and novel_configuration_access >= 0.05
        )

        return {
            "principle": self.PRINCIPLE,
            "evolutionary_diversification_diagnostics": (
                diversification
            ),
            "transition_pressure": transition_pressure,
            "regime_shift_intensity": regime_shift_intensity,
            "novel_configuration_access": (
                novel_configuration_access
            ),
            "critical_transitions": critical_transitions,
        }


if __name__ == "__main__":

    primitive = CriticalTransitionsPrimitive()

    diagnostics = primitive.step(
        activation=1.0,
        coherence=0.8,
        representability=0.65,
        local_stability=0.75,
    )

    print("\n--- critical transitions ---")

    for key, value in diagnostics.items():
        print(f"{key}: {value}")