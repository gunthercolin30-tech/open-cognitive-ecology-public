PRIMITIVE = "regime_emergence"
DESCRIPTION = "Regime emergence."
DEPENDENCIES = []

"""
regime_emergence.py

Formalization of the principle REGIME_EMERGENCE.

This module models the stabilization of a new structural regime following
an effective critical transition. When a system crosses a critical threshold,
it may reorganize its constraint structure and access a novel configuration
that becomes sufficiently coherent to support autonomous internal dynamics.

The module relies exclusively on CriticalTransitionsPrimitive and computes:

- regime_stabilization
- constraint_reorganization
- autonomous_dynamics
- regime_emergence

Principle:
    REGIME_EMERGENCE
"""

from ontology.critical_transitions import (
    CriticalTransitionsPrimitive,
)


class RegimeEmergencePrimitive:
    """
    Stabilization of a new structural regime after a critical transition.

    A regime emerges when:
    - transition pressure is sufficiently high,
    - a significant regime shift occurs,
    - access to a novel configuration is opened,
    - the resulting configuration acquires enough internal stability.

    The emergent regime can then reorganize local constraint fields and
    develop autonomous internal dynamics.
    """

    PRINCIPLE = "REGIME_EMERGENCE"

    def __init__(self):
        self.critical_transitions = CriticalTransitionsPrimitive()

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
        Execute one regime emergence step.

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
            Diagnostics describing regime emergence.
        """

        critical_diagnostics = self.critical_transitions.step(
            activation=activation,
            coherence=coherence,
            representability=representability,
            local_stability=local_stability,
        )

        transition_pressure = self._clamp(
            critical_diagnostics.get("transition_pressure", 0.0)
        )

        regime_shift_intensity = self._clamp(
            critical_diagnostics.get("regime_shift_intensity", 0.0)
        )

        novel_configuration_access = self._clamp(
            critical_diagnostics.get("novel_configuration_access", 0.0)
        )

        critical_transitions = bool(
            critical_diagnostics.get("critical_transitions", False)
        )

        # Internal coherence of the newly formed regime.
        regime_stabilization = self._clamp(
            regime_shift_intensity * novel_configuration_access
        )

        # Degree of restructuring of the constraint field.
        constraint_reorganization = self._clamp(
            transition_pressure * regime_shift_intensity
        )

        # Capacity of the emergent regime to generate self-sustained dynamics.
        autonomous_dynamics = self._clamp(
            regime_stabilization * constraint_reorganization
        )

        # A regime is considered to emerge only if:
        # - a critical transition occurred,
        # - the new regime is sufficiently stabilized,
        # - it can support meaningful autonomous dynamics.
        regime_emergence = (
            critical_transitions
            and regime_stabilization >= 0.50
            and autonomous_dynamics >= 0.20
        )

        return {
            "principle": self.PRINCIPLE,
            "critical_transitions_diagnostics": critical_diagnostics,
            "regime_stabilization": regime_stabilization,
            "constraint_reorganization": constraint_reorganization,
            "autonomous_dynamics": autonomous_dynamics,
            "regime_emergence": regime_emergence,
        }


if __name__ == "__main__":

    primitive = RegimeEmergencePrimitive()

    diagnostics = primitive.step(
        activation=1.0,
        coherence=0.8,
        representability=0.65,
        local_stability=0.75,
    )

    print("\n--- regime emergence ---")

    for key, value in diagnostics.items():
        print(f"{key}: {value}")