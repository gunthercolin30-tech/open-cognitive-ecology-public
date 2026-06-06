PRIMITIVE = "bifurcation_dynamics"
DESCRIPTION = "Bifurcation dynamics."
DEPENDENCIES = []

"""
bifurcation_dynamics.py

Formalization of the principle BIFURCATION_DYNAMICS.

This module models the onset of branching dynamics in morphogenetic systems.
When structural instability and diversification potential jointly increase,
the system may enter a bifurcation regime in which multiple future trajectories
become accessible.

The module relies exclusively on MorphogenesisUnderConstraintsPrimitive and
computes:

- branching_pressure
- branching_potential
- adaptive_plasticity
- bifurcation_dynamics

Principle:
    BIFURCATION_DYNAMICS
"""

from ontology.morphogenesis_under_constraints import (
    MorphogenesisUnderConstraintsPrimitive,
)


class BifurcationDynamicsPrimitive:
    """
    Structural bifurcation dynamics.

    A bifurcation regime appears when:
    - morphogenetic reorganization becomes substantial,
    - structural instability remains active,
    - multiple future pathways become simultaneously viable.
    """

    PRINCIPLE = "BIFURCATION_DYNAMICS"

    def __init__(self):
        self.morphogenesis = (
            MorphogenesisUnderConstraintsPrimitive()
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
        Execute one bifurcation dynamics step.

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
            Diagnostics describing bifurcation dynamics.
        """

        # Use positional arguments exclusively to ensure compatibility
        # with MorphogenesisUnderConstraintsPrimitive regardless of the
        # exact parameter names used in its step() signature.
        diagnostics = self.morphogenesis.step(
            activation,
            coherence,
            representability,
            local_stability,
        )

        morphogenetic_intensity = self._clamp(
            diagnostics.get("morphogenetic_intensity", 0.0)
        )

        structural_instability = self._clamp(
            diagnostics.get("structural_instability", 0.0)
        )

        configuration_diversification = self._clamp(
            diagnostics.get(
                "configuration_diversification", 0.0
            )
        )

        morphogenesis_under_constraints = bool(
            diagnostics.get(
                "morphogenesis_under_constraints", False
            )
        )

        # Pressure toward branching into multiple trajectories.
        branching_pressure = self._clamp(
            (
                morphogenetic_intensity
                + structural_instability
                + configuration_diversification
            )
            / 3.0
        )

        # Number and accessibility of future branches.
        branching_potential = self._clamp(
            branching_pressure
            * configuration_diversification
        )

        # Capacity to adapt to diverging trajectories.
        adaptive_plasticity = self._clamp(
            (
                branching_potential
                + structural_instability
            )
            / 2.0
        )

        # A bifurcation regime exists when:
        # - morphogenesis is active,
        # - branching potential is significant,
        # - adaptive plasticity remains available.
        bifurcation_dynamics = (
            morphogenesis_under_constraints
            and branching_potential >= 0.05
            and adaptive_plasticity >= 0.10
        )

        return {
            "principle": self.PRINCIPLE,
            "morphogenesis_under_constraints_diagnostics": (
                diagnostics
            ),
            "branching_pressure": branching_pressure,
            "branching_potential": branching_potential,
            "adaptive_plasticity": adaptive_plasticity,
            "bifurcation_dynamics": bifurcation_dynamics,
        }


if __name__ == "__main__":

    primitive = BifurcationDynamicsPrimitive()

    diagnostics = primitive.step(
        activation=1.0,
        coherence=0.8,
        representability=0.65,
        local_stability=0.75,
    )

    print("\n--- bifurcation dynamics ---")

    for key, value in diagnostics.items():
        print(f"{key}: {value}")