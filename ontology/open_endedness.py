PRIMITIVE = "open_endedness"
DESCRIPTION = "Open endedness."
DEPENDENCIES = []

"""
OPEN_ENDEDNESS
==============

Scientific primitive formalizing the capacity of a system to continue
generating novel configurations without converging to a final closure.

The primitive quantifies novelty generation, innovation capacity,
resistance to closure, and the resulting open-ended potential.

Related primitives
------------------
- NON_CLOSURE
- NON_REPRESENTABILITY
- EVOLUTIONARY_DRIFT
- ADAPTIVE_LANDSCAPE
"""

from typing import Dict, Any


PRIMITIVE_NAME = "OPEN_ENDEDNESS"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class OpenEndedness:
    """
    Formal model of indefinite novelty production.

    Parameters
    ----------
    novelty_generation : float
        Rate of structurally relevant novelty production.
    innovation_capacity : float
        Capacity to stabilize and exploit new configurations.
    closure_resistance : float
        Degree to which the system avoids terminal closure.

    Scientific interpretation
    -------------------------
    open_ended_potential is the mean of novelty generation,
    innovation capacity, and closure resistance.
    """

    def __init__(
        self,
        novelty_generation: float = 0.0,
        innovation_capacity: float = 0.0,
        closure_resistance: float = 0.0,
    ) -> None:
        self.novelty_generation = _clamp(novelty_generation)
        self.innovation_capacity = _clamp(innovation_capacity)
        self.closure_resistance = _clamp(closure_resistance)

    def evaluate(self) -> Dict[str, Any]:
        """Compute open-endedness indicators."""
        open_ended_potential = _clamp(
            (
                self.novelty_generation
                + self.innovation_capacity
                + self.closure_resistance
            ) / 3.0
        )

        status = (
            "closed"
            if open_ended_potential == 0.0
            else "open_ended"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "novelty_generation": self.novelty_generation,
            "innovation_capacity": self.innovation_capacity,
            "closure_resistance": self.closure_resistance,
            "status": status,
        }

        return {
            "novelty_generation": self.novelty_generation,
            "innovation_capacity": self.innovation_capacity,
            "closure_resistance": self.closure_resistance,
            "open_ended_potential": open_ended_potential,
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
            "novelty_generation",
            "innovation_capacity",
            "closure_resistance",
            "open_ended_potential",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_open_ended": (
                evaluation["open_ended_potential"] > 0.0
            ),
            "open_ended_potential": evaluation["open_ended_potential"],
            "diagnostics": evaluation["diagnostics"],
        }
