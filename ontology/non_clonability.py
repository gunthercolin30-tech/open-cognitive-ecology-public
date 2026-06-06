PRIMITIVE = "non_clonability"
DESCRIPTION = "Non clonability."
DEPENDENCIES = []

"""
NON_CLONABILITY
===============

Scientific primitive formalizing the impossibility of perfectly copying an
unknown state. The primitive quantifies intrinsic limits on replication
fidelity and the irreducible divergence between an original configuration
and its copy.

This concept is structurally linked to:
- MINIMAL_DNA
- REAL_SUCCESSION
- QUANTUM_INDETERMINACY
- MEASUREMENT_PERTURBATION
"""

from typing import Dict, Any


PRIMITIVE_NAME = "NON_CLONABILITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value into the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class NonClonability:
    """
    Formalization of the non-clonability principle.

    Parameters
    ----------
    state_complexity : float
        Complexity or opacity of the state to be copied.
    indeterminacy : float
        Degree of intrinsic uncertainty affecting measurement and copying.
    transmission_noise : float
        Additional perturbation during replication.

    Scientific interpretation
    -------------------------
    cloning_fidelity = 1 - effective_limit
    replication_error = effective_limit
    copy_divergence = effective_limit
    transmission_limit = effective_limit

    where effective_limit is the mean of the bounded structural sources
    of irreducible copying uncertainty.
    """

    def __init__(
        self,
        state_complexity: float = 0.0,
        indeterminacy: float = 0.0,
        transmission_noise: float = 0.0,
    ) -> None:
        self.state_complexity = _clamp(state_complexity)
        self.indeterminacy = _clamp(indeterminacy)
        self.transmission_noise = _clamp(transmission_noise)

    def evaluate(self) -> Dict[str, Any]:
        """Compute the non-clonability indicators."""
        effective_limit = (
            self.state_complexity
            + self.indeterminacy
            + self.transmission_noise
        ) / 3.0
        effective_limit = _clamp(effective_limit)

        cloning_fidelity = _clamp(1.0 - effective_limit)
        replication_error = effective_limit
        copy_divergence = effective_limit
        transmission_limit = effective_limit

        status = (
            "perfectly_clonable"
            if effective_limit == 0.0
            else "non_clonable"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "state_complexity": self.state_complexity,
            "indeterminacy": self.indeterminacy,
            "transmission_noise": self.transmission_noise,
            "status": status,
        }

        return {
            "cloning_fidelity": cloning_fidelity,
            "replication_error": replication_error,
            "copy_divergence": copy_divergence,
            "transmission_limit": transmission_limit,
            "diagnostics": diagnostics,
        }

    def step(self) -> Dict[str, Any]:
        """Return one evaluation step."""
        return self.evaluate()

    def validate(self) -> Dict[str, Any]:
        """Validate whether the primitive output is internally coherent."""
        evaluation = self.evaluate()

        valid = (
            0.0 <= evaluation["cloning_fidelity"] <= 1.0
            and 0.0 <= evaluation["replication_error"] <= 1.0
            and 0.0 <= evaluation["copy_divergence"] <= 1.0
            and 0.0 <= evaluation["transmission_limit"] <= 1.0
        )

        return {
            "valid": valid,
            "non_clonable": evaluation["replication_error"] > 0.0,
            "cloning_fidelity": evaluation["cloning_fidelity"],
            "diagnostics": evaluation["diagnostics"],
        }
