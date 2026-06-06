PRIMITIVE = "multi_scale_coupling"
DESCRIPTION = "Multi scale coupling."
DEPENDENCIES = []

"""
MULTI_SCALE_COUPLING
====================

Scientific primitive formalizing the structural coupling between dynamics
operating at different organizational scales.

The primitive quantifies local-global coupling, cross-scale feedback,
scale coherence, and the resulting multi-scale potential.

Related primitives
------------------
- CONSTRAINT_FIELDS
- COEVOLUTIONARY_DYNAMICS
- GENEALOGICAL_CONTINUITY
- META_ADAPTATION
"""

from typing import Dict, Any


PRIMITIVE_NAME = "MULTI_SCALE_COUPLING"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class MultiScaleCoupling:
    """
    Formal model of cross-scale integration.

    Parameters
    ----------
    local_global_coupling : float
        Degree of coupling between local and global dynamics.
    cross_scale_feedback : float
        Strength of reciprocal interactions across scales.
    scale_coherence : float
        Structural coherence among scales.

    Scientific interpretation
    -------------------------
    multi_scale_potential is the mean of local-global coupling,
    cross-scale feedback, and scale coherence.
    """

    def __init__(
        self,
        local_global_coupling: float = 0.0,
        cross_scale_feedback: float = 0.0,
        scale_coherence: float = 0.0,
    ) -> None:
        self.local_global_coupling = _clamp(local_global_coupling)
        self.cross_scale_feedback = _clamp(cross_scale_feedback)
        self.scale_coherence = _clamp(scale_coherence)

    def evaluate(self) -> Dict[str, Any]:
        """Compute multi-scale coupling indicators."""
        multi_scale_potential = _clamp(
            (
                self.local_global_coupling
                + self.cross_scale_feedback
                + self.scale_coherence
            ) / 3.0
        )

        status = (
            "decoupled"
            if multi_scale_potential == 0.0
            else "coupled"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "local_global_coupling": self.local_global_coupling,
            "cross_scale_feedback": self.cross_scale_feedback,
            "scale_coherence": self.scale_coherence,
            "status": status,
        }

        return {
            "local_global_coupling": self.local_global_coupling,
            "cross_scale_feedback": self.cross_scale_feedback,
            "scale_coherence": self.scale_coherence,
            "multi_scale_potential": multi_scale_potential,
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
            "local_global_coupling",
            "cross_scale_feedback",
            "scale_coherence",
            "multi_scale_potential",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_coupled": evaluation["multi_scale_potential"] > 0.0,
            "multi_scale_potential": evaluation["multi_scale_potential"],
            "diagnostics": evaluation["diagnostics"],
        }
