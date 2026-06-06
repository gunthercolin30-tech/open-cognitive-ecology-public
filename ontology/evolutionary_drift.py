PRIMITIVE = "evolutionary_drift"
DESCRIPTION = "Evolutionary drift."
DEPENDENCIES = []

"""
EVOLUTIONARY_DRIFT
==================

Scientific primitive formalizing the progressive divergence of lineages
through imperfect replication and cumulative variation.

The primitive quantifies how local fluctuations and replication errors
generate increasing evolutionary distance over time.

Related primitives
------------------
- NON_CLONABILITY
- GENEALOGICAL_CONTINUITY
- QUANTUM_INDETERMINACY
- STRUCTURAL_ATTRACTOR
"""

from typing import Dict, Any


PRIMITIVE_NAME = "EVOLUTIONARY_DRIFT"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class EvolutionaryDrift:
    """
    Formal model of evolutionary drift.

    Parameters
    ----------
    replication_error : float
        Irreducible error introduced during copying.
    stochastic_fluctuation : float
        Random local perturbations.
    generational_depth : float
        Effective depth of accumulated transmission.

    Scientific interpretation
    -------------------------
    drift_rate is the mean of replication error and stochastic fluctuation.
    cumulative_variation scales with drift_rate and generational depth.
    lineage_dispersion equals cumulative_variation.
    evolutionary_distance equals cumulative_variation.
    """

    def __init__(
        self,
        replication_error: float = 0.0,
        stochastic_fluctuation: float = 0.0,
        generational_depth: float = 0.0,
    ) -> None:
        self.replication_error = _clamp(replication_error)
        self.stochastic_fluctuation = _clamp(stochastic_fluctuation)
        self.generational_depth = _clamp(generational_depth)

    def evaluate(self) -> Dict[str, Any]:
        """Compute evolutionary drift indicators."""
        drift_rate = _clamp(
            (self.replication_error + self.stochastic_fluctuation) / 2.0
        )
        cumulative_variation = _clamp(
            drift_rate * self.generational_depth
        )
        lineage_dispersion = cumulative_variation
        evolutionary_distance = cumulative_variation

        status = "stable" if evolutionary_distance == 0.0 else "drifting"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "replication_error": self.replication_error,
            "stochastic_fluctuation": self.stochastic_fluctuation,
            "generational_depth": self.generational_depth,
            "status": status,
        }

        return {
            "drift_rate": drift_rate,
            "cumulative_variation": cumulative_variation,
            "lineage_dispersion": lineage_dispersion,
            "evolutionary_distance": evolutionary_distance,
            "diagnostics": diagnostics,
        }

    def step(self) -> Dict[str, Any]:
        """Return one evaluation step."""
        return self.evaluate()

    def validate(self) -> Dict[str, Any]:
        """Validate internal coherence."""
        evaluation = self.evaluate()

        valid = True
        for key in (
            "drift_rate",
            "cumulative_variation",
            "lineage_dispersion",
            "evolutionary_distance",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_drifting": evaluation["evolutionary_distance"] > 0.0,
            "evolutionary_distance": evaluation["evolutionary_distance"],
            "diagnostics": evaluation["diagnostics"],
        }
