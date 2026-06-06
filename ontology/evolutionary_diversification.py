PRIMITIVE = "evolutionary_diversification"
DESCRIPTION = "Evolutionary diversification."
DEPENDENCIES = []

"""
evolutionary_diversification.py

Formalization of the principle EVOLUTIONARY_DIVERSIFICATION.

This module models the emergence of evolutionary diversification from
bifurcation dynamics. When branching structures become viable and adaptive
plasticity remains active, the system can explore a broader space of
structural possibilities.

The module relies exclusively on BifurcationDynamicsPrimitive and computes:

- diversification_pressure
- branching_potential
- adaptive_plasticity
- evolutionary_diversification

Principle:
    EVOLUTIONARY_DIVERSIFICATION
"""

from ontology.bifurcation_dynamics import (
    BifurcationDynamicsPrimitive,
)


class EvolutionaryDiversificationPrimitive:
    """
    Evolutionary diversification dynamics.

    Diversification occurs when:
    - branching pressure is sufficiently high,
    - multiple structural trajectories are accessible,
    - adaptive plasticity supports exploration.
    """

    PRINCIPLE = "EVOLUTIONARY_DIVERSIFICATION"

    def __init__(self):
        self.bifurcation = BifurcationDynamicsPrimitive()

    @staticmethod
    def _clamp(value):
        """Clamp a numerical value to the interval [0, 1]."""
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        coherence=0.8,
        representability=0.65,
        local_stability=0.75,
    ):
        """
        Execute one evolutionary diversification step.

        Parameters
        ----------
        coherence : float
            Internal coherence of the current organization.
        representability : float
            Degree of structural representability.
        local_stability : float
            Stability of local trajectories.

        Returns
        -------
        dict
            Diagnostics describing evolutionary diversification.
        """

        # Use positional arguments exclusively to ensure compatibility
        # with BifurcationDynamicsPrimitive regardless of its internal
        # parameter naming conventions.
        diagnostics = self.bifurcation.step(
            1.0,  # activation (default)
            coherence,
            representability,
            local_stability,
        )

        branching_pressure = self._clamp(
            diagnostics.get("branching_pressure", 0.0)
        )

        branching_potential = self._clamp(
            diagnostics.get("branching_potential", 0.0)
        )

        adaptive_plasticity = self._clamp(
            diagnostics.get("adaptive_plasticity", 0.0)
        )

        bifurcation_dynamics = bool(
            diagnostics.get("bifurcation_dynamics", False)
        )

        # Pressure toward diversification.
        diversification_pressure = self._clamp(
            (
                branching_pressure
                + branching_potential
                + adaptive_plasticity
            )
            / 3.0
        )

        # Diversification is active when:
        # - bifurcation dynamics are established,
        # - diversification pressure is substantial,
        # - adaptive plasticity remains sufficient.
        evolutionary_diversification = (
            bifurcation_dynamics
            and diversification_pressure >= 0.10
            and adaptive_plasticity >= 0.10
        )

        return {
            "principle": self.PRINCIPLE,
            "bifurcation_dynamics_diagnostics": diagnostics,
            "diversification_pressure": (
                diversification_pressure
            ),
            "branching_potential": branching_potential,
            "adaptive_plasticity": adaptive_plasticity,
            "evolutionary_diversification": (
                evolutionary_diversification
            ),
        }


if __name__ == "__main__":

    primitive = EvolutionaryDiversificationPrimitive()

    diagnostics = primitive.step(
        coherence=0.8,
        representability=0.65,
        local_stability=0.75,
    )

    print("\n--- evolutionary diversification ---")

    for key, value in diagnostics.items():
        print(f"{key}: {value}")