PRIMITIVE = "autonomous_regimes"
DESCRIPTION = "Autonomous regimes."
DEPENDENCIES = []

"""
autonomous_regimes.py

Formalization of the principle AUTONOMOUS_REGIMES.

This module models structural regimes that are able to maintain their own
organization, reinforce their internal coherence, and preserve operational
viability without direct external control.

The module relies exclusively on RegimeEmergencePrimitive and computes:

- self_maintenance
- internal_coherence_reinforcement
- operational_viability
- autonomous_regimes

Principle:
    AUTONOMOUS_REGIMES
"""

from ontology.regime_emergence import (
    RegimeEmergencePrimitive,
)


class AutonomousRegimesPrimitive:
    """
    Autonomous structural regimes.

    A regime becomes autonomous when an emergent regime:
    - maintains its own structure,
    - reinforces its internal coherence,
    - preserves operational viability,
    - sustains durable self-generated dynamics.
    """

    PRINCIPLE = "AUTONOMOUS_REGIMES"

    def __init__(self):
        self.regime_emergence = RegimeEmergencePrimitive()

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
        Execute one autonomous regime step.

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
            Diagnostics describing autonomous regimes.
        """

        regime_diagnostics = self.regime_emergence.step(
            activation=activation,
            coherence=coherence,
            representability=representability,
            local_stability=local_stability,
        )

        regime_stabilization = self._clamp(
            regime_diagnostics.get("regime_stabilization", 0.0)
        )

        constraint_reorganization = self._clamp(
            regime_diagnostics.get("constraint_reorganization", 0.0)
        )

        autonomous_dynamics = self._clamp(
            regime_diagnostics.get("autonomous_dynamics", 0.0)
        )

        regime_emergence = bool(
            regime_diagnostics.get("regime_emergence", False)
        )

        # Capacity to actively preserve the regime's own structure.
        self_maintenance = self._clamp(
            regime_stabilization * autonomous_dynamics
        )

        # Endogenous reinforcement of structural coherence.
        internal_coherence_reinforcement = self._clamp(
            self_maintenance * constraint_reorganization
        )

        # Ability to sustain operations over time.
        operational_viability = self._clamp(
            (
                self_maintenance
                + internal_coherence_reinforcement
                + autonomous_dynamics
            )
            / 3.0
        )

        # An autonomous regime is established only if:
        # - a regime has effectively emerged,
        # - self-maintenance is sufficiently strong,
        # - operational viability is robust.
        autonomous_regimes = (
            regime_emergence
            and self_maintenance >= 0.20
            and operational_viability >= 0.20
        )

        return {
            "principle": self.PRINCIPLE,
            "regime_emergence_diagnostics": regime_diagnostics,
            "self_maintenance": self_maintenance,
            "internal_coherence_reinforcement": (
                internal_coherence_reinforcement
            ),
            "operational_viability": operational_viability,
            "autonomous_regimes": autonomous_regimes,
        }


if __name__ == "__main__":

    primitive = AutonomousRegimesPrimitive()

    diagnostics = primitive.step(
        activation=1.0,
        coherence=0.8,
        representability=0.65,
        local_stability=0.75,
    )

    print("\n--- autonomous regimes ---")

    for key, value in diagnostics.items():
        print(f"{key}: {value}")