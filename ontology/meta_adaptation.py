PRIMITIVE = "meta_adaptation"
DESCRIPTION = "Meta adaptation."
DEPENDENCIES = []

"""
META_ADAPTATION
===============

Scientific primitive formalizing the capacity of a system to revise its
own adaptive mechanisms and search strategies.

The primitive quantifies self-modification, strategy revision,
adaptive reflexivity, and the resulting meta-adaptive potential.

Related primitives
------------------
- REFLEXIVE_THRESHOLD
- EXPLORATION_EXPLOITATION_BALANCE
- OPEN_ENDEDNESS
- NON_REPRESENTABILITY
"""

from typing import Dict, Any


PRIMITIVE_NAME = "META_ADAPTATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class MetaAdaptation:
    """
    Formal model of reflexive adaptation.

    Parameters
    ----------
    self_modification_capacity : float
        Capacity to alter internal structures and rules.
    strategy_revision_rate : float
        Rate at which adaptive strategies are revised.
    adaptive_reflexivity : float
        Degree of reflexive awareness of adaptive mechanisms.

    Scientific interpretation
    -------------------------
    meta_adaptive_potential is the mean of the three structural factors.
    """

    def __init__(
        self,
        self_modification_capacity: float = 0.0,
        strategy_revision_rate: float = 0.0,
        adaptive_reflexivity: float = 0.0,
    ) -> None:
        self.self_modification_capacity = _clamp(
            self_modification_capacity
        )
        self.strategy_revision_rate = _clamp(
            strategy_revision_rate
        )
        self.adaptive_reflexivity = _clamp(
            adaptive_reflexivity
        )

    def evaluate(self) -> Dict[str, Any]:
        """Compute meta-adaptation indicators."""
        meta_adaptive_potential = _clamp(
            (
                self.self_modification_capacity
                + self.strategy_revision_rate
                + self.adaptive_reflexivity
            ) / 3.0
        )

        status = (
            "static"
            if meta_adaptive_potential == 0.0
            else "meta_adaptive"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "self_modification_capacity": (
                self.self_modification_capacity
            ),
            "strategy_revision_rate": self.strategy_revision_rate,
            "adaptive_reflexivity": self.adaptive_reflexivity,
            "status": status,
        }

        return {
            "self_modification_capacity": (
                self.self_modification_capacity
            ),
            "strategy_revision_rate": self.strategy_revision_rate,
            "adaptive_reflexivity": self.adaptive_reflexivity,
            "meta_adaptive_potential": meta_adaptive_potential,
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
            "self_modification_capacity",
            "strategy_revision_rate",
            "adaptive_reflexivity",
            "meta_adaptive_potential",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_meta_adaptive": (
                evaluation["meta_adaptive_potential"] > 0.0
            ),
            "meta_adaptive_potential": (
                evaluation["meta_adaptive_potential"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
