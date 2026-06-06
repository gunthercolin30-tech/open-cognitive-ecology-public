"""
Recursive Civilizational Self Improvement.
Coordinates simulation, constitutional evolution, and adoption of validated improvements.
"""

from __future__ import annotations

PRIMITIVE = "RECURSIVE_CIVILIZATIONAL_SELF_IMPROVEMENT"

DEPENDENCIES = [
    "civilization_scale_simulation_runner",
    "adaptive_constitutional_evolution",
    "civilizational_autonomy_index",
    "longitudinal_civilizational_autonomy_tracker",
]


class RecursiveCivilizationalSelfImprovement:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE
        self.iteration = 0
        self.best_global_viability = 0.0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        current_global_viability: float = 0.92457,
        proposed_global_viability: float = 0.93000,
        constitutional_change_accepted: bool = True,
    ) -> dict:
        self.iteration += 1

        current = self._clamp(current_global_viability)
        proposed = self._clamp(proposed_global_viability)

        improvement = proposed - current
        accepted = constitutional_change_accepted and improvement > 0.0

        resulting_viability = proposed if accepted else current
        self.best_global_viability = max(
            self.best_global_viability,
            resulting_viability,
        )

        if accepted:
            status = "improvement_adopted"
        else:
            status = "improvement_rejected"

        return {
            "primitive": self.primitive,
            "iteration": self.iteration,
            "accepted": accepted,
            "status": status,
            "improvement": improvement,
            "current_global_viability": current,
            "proposed_global_viability": proposed,
            "resulting_global_viability": resulting_viability,
            "best_global_viability": self.best_global_viability,
        }
