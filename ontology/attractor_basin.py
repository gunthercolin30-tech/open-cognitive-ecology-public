PRIMITIVE = "attractor_basin"
DESCRIPTION = "Attractor basin."
DEPENDENCIES = []

"""
ATTRACTOR_BASIN
================

Scientific primitive formalizing attraction basins as local domains of initial
configurations whose trajectories converge toward the same structural attractor.

The basin size measures the average convergence membership over a set of
configurations and quantifies the organizing reach and robustness of the
underlying structural regime.

The formulation is explicitly local and does not assume any global closure of
the state space, in accordance with the constraint-based ontology developed in:

- Structural Attractor
- Structural Transition Operator
- Cognitive Phase Transitions
- Trajectories Without Globality
- Formal Foundations of Constraint-Based Systems
"""

from typing import Any, Dict, Mapping


class AttractorBasin:
    """
    Formal representation of an attraction basin.

    Each configuration identifier is associated with a convergence probability in
    the interval [0, 1]. This value is interpreted directly as its basin
    membership. The basin size is the arithmetic mean of all memberships.

    A basin is considered significant when:

        basin_size >= basin_threshold

    This criterion quantifies whether the attractor captures a sufficiently
    large local domain of configurations to be regarded as structurally
    organizing and dynamically robust.
    """

    PRIMITIVE_NAME = "ATTRACTOR_BASIN"
    MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"

    def __init__(self, basin_threshold: float = 0.5):
        """
        Initialize the primitive.

        Parameters
        ----------
        basin_threshold:
            Minimum average membership required for a basin to be considered
            significant. The value is clamped to [0, 1].
        """
        self.basin_threshold = self._clamp(basin_threshold)

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a numeric value to the closed interval [0, 1]."""
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return float(value)

    def evaluate(
        self,
        convergence_probabilities: Mapping[str, float]
    ) -> Dict[str, Any]:
        """
        Evaluate the attraction basin associated with convergence probabilities.

        Parameters
        ----------
        convergence_probabilities:
            Mapping from configuration identifiers to convergence probabilities.

        Returns
        -------
        dict
            Contains:
            - basin_membership: bounded membership for each configuration
            - basin_size: arithmetic mean of memberships
            - significant_basin_exists: significance criterion result
            - diagnostics: metadata and status
        """
        basin_membership = {
            str(identifier): self._clamp(probability)
            for identifier, probability in convergence_probabilities.items()
        }

        configuration_count = len(basin_membership)

        if configuration_count == 0:
            basin_size = 0.0
        else:
            basin_size = sum(basin_membership.values()) / configuration_count

        significant_basin_exists = basin_size >= self.basin_threshold

        diagnostics = {
            "primitive": self.PRIMITIVE_NAME,
            "configuration_count": configuration_count,
            "basin_threshold": self.basin_threshold,
            "status": (
                "significant_basin"
                if significant_basin_exists
                else "insignificant_basin"
            ),
        }

        return {
            "basin_membership": basin_membership,
            "basin_size": basin_size,
            "significant_basin_exists": significant_basin_exists,
            "diagnostics": diagnostics,
        }

    def step(
        self,
        convergence_probabilities: Mapping[str, float]
    ) -> Dict[str, Any]:
        """
        Single-step evaluation of the attraction basin.

        Returns exactly the same structure as evaluate().
        """
        return self.evaluate(convergence_probabilities)

    def validate(
        self,
        convergence_probabilities: Mapping[str, float]
    ) -> Dict[str, Any]:
        """
        Validate basin existence and significance.

        Returns
        -------
        dict
            Contains:
            - valid: identical to significant_basin_exists
            - significant_basin_exists
            - basin_size
            - diagnostics
        """
        result = self.evaluate(convergence_probabilities)
        return {
            "valid": result["significant_basin_exists"],
            "significant_basin_exists": result["significant_basin_exists"],
            "basin_size": result["basin_size"],
            "diagnostics": result["diagnostics"],
        }
