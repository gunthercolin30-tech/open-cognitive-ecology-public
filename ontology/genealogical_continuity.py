PRIMITIVE = "genealogical_continuity"
DESCRIPTION = "Genealogical continuity."
DEPENDENCIES = []

"""
GENEALOGICAL_CONTINUITY
=======================

Scientific primitive formalizing the persistence of a lineage through
successive transformations despite imperfect replication and cumulative
divergence.

The primitive quantifies the structural continuity of a genealogical chain
under the constraints of inheritance fidelity and variation.

Related primitives
------------------
- MINIMAL_DNA
- REAL_SUCCESSION
- NON_CLONABILITY
- STRUCTURAL_CONTINUITY
"""

from typing import Dict, Any


PRIMITIVE_NAME = "GENEALOGICAL_CONTINUITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class GenealogicalContinuity:
    """
    Formal model of lineage continuity.

    Parameters
    ----------
    inheritance_fidelity : float
        Degree to which transmissible structure is preserved.
    cumulative_divergence : float
        Accumulated transformation across generations.
    succession_stability : float
        Stability of the succession process.

    Scientific interpretation
    -------------------------
    lineage_integrity depends positively on inheritance fidelity and
    succession stability, and negatively on cumulative divergence.

    continuity_strength is identified with lineage_integrity.
    """

    def __init__(
        self,
        inheritance_fidelity: float = 0.0,
        cumulative_divergence: float = 0.0,
        succession_stability: float = 0.0,
    ) -> None:
        self.inheritance_fidelity = _clamp(inheritance_fidelity)
        self.cumulative_divergence = _clamp(cumulative_divergence)
        self.succession_stability = _clamp(succession_stability)

    def evaluate(self) -> Dict[str, Any]:
        """Compute genealogical continuity indicators."""
        lineage_integrity = (
            self.inheritance_fidelity
            + (1.0 - self.cumulative_divergence)
            + self.succession_stability
        ) / 3.0
        lineage_integrity = _clamp(lineage_integrity)

        continuity_strength = lineage_integrity

        status = (
            "discontinuous"
            if continuity_strength == 0.0
            else "continuous"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "inheritance_fidelity": self.inheritance_fidelity,
            "cumulative_divergence": self.cumulative_divergence,
            "succession_stability": self.succession_stability,
            "status": status,
        }

        return {
            "lineage_integrity": lineage_integrity,
            "inheritance_fidelity": self.inheritance_fidelity,
            "cumulative_divergence": self.cumulative_divergence,
            "continuity_strength": continuity_strength,
            "diagnostics": diagnostics,
        }

    def step(self) -> Dict[str, Any]:
        """Return one evaluation step."""
        return self.evaluate()

    def validate(self) -> Dict[str, Any]:
        """Validate internal coherence and continuity state."""
        evaluation = self.evaluate()

        valid = True
        for key in (
            "lineage_integrity",
            "inheritance_fidelity",
            "cumulative_divergence",
            "continuity_strength",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_continuous": evaluation["continuity_strength"] > 0.0,
            "continuity_strength": evaluation["continuity_strength"],
            "diagnostics": evaluation["diagnostics"],
        }
