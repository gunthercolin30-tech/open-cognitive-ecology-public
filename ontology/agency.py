PRIMITIVE = "agency"
DESCRIPTION = "Agency."
DEPENDENCIES = []

"""
ontology/agency.py

Scientific primitive: AGENCY

This primitive formalizes the integrated capacity of a system to initiate,
maintain, and modulate its own trajectories according to internal goals,
state-dependent regulation, and environmental constraints.

The primitive synthesizes four components:
- autonomous_initiation
- self_modulation
- intentional_persistence
- agency_index

All values are bounded to [0, 1].
"""

from typing import Dict, Any


PRIMITIVE_NAME = "AGENCY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numeric value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Agency:
    """
    Formal representation of operational agency.

    Parameters
    ----------
    initiation_weight : float
        Weight assigned to autonomous initiation.
    modulation_weight : float
        Weight assigned to self modulation.
    persistence_weight : float
        Weight assigned to intentional persistence.

    The weights are normalized during evaluation to preserve a convex
    combination.
    """

    def __init__(
        self,
        initiation_weight: float = 1.0,
        modulation_weight: float = 1.0,
        persistence_weight: float = 1.0,
    ) -> None:
        self.initiation_weight = max(0.0, float(initiation_weight))
        self.modulation_weight = max(0.0, float(modulation_weight))
        self.persistence_weight = max(0.0, float(persistence_weight))

    def evaluate(
        self,
        goal_directedness: float = 0.0,
        steerability: float = 0.0,
        controllability: float = 0.0,
        observability: float = 0.0,
        reflexive_threshold: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Evaluate the agency capacity of the system.

        Parameters are expected in [0, 1], but are clamped if necessary.
        """
        gd = _clamp(goal_directedness)
        st = _clamp(steerability)
        ct = _clamp(controllability)
        ob = _clamp(observability)
        rt = _clamp(reflexive_threshold)

        autonomous_initiation = _clamp(0.5 * gd + 0.5 * rt)
        self_modulation = _clamp((st + ct + ob) / 3.0)
        intentional_persistence = _clamp(0.5 * gd + 0.5 * self_modulation)

        total_weight = (
            self.initiation_weight
            + self.modulation_weight
            + self.persistence_weight
        )

        if total_weight <= 0.0:
            agency_index = 0.0
        else:
            agency_index = _clamp(
                (
                    self.initiation_weight * autonomous_initiation
                    + self.modulation_weight * self_modulation
                    + self.persistence_weight * intentional_persistence
                )
                / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "goal_directedness": gd,
            "steerability": st,
            "controllability": ct,
            "observability": ob,
            "reflexive_threshold": rt,
            "autonomous_initiation": autonomous_initiation,
            "self_modulation": self_modulation,
            "intentional_persistence": intentional_persistence,
            "status": "computed",
        }

        return {
            "autonomous_initiation": autonomous_initiation,
            "self_modulation": self_modulation,
            "intentional_persistence": intentional_persistence,
            "agency_index": agency_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        """
        Single-step update. For this foundational primitive, step delegates
        directly to evaluate.
        """
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        """
        Validate whether the system exhibits non-zero agency.
        """
        result = self.evaluate(**kwargs)
        valid = result["agency_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "agency_index": result["agency_index"],
            "diagnostics": diagnostics,
        }
