"""
CIVILIZATIONAL_STRATEGIC_PLANNER

Coordinates long-term civilizational priorities, resources,
scientific programs, and strategic trajectories.
"""

from typing import Dict, Any


class CivilizationalStrategicPlanner:
    """Computes civilizational strategic planning metrics."""

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        scientific_priority_alignment = self._clip(
            inputs.get("scientific_priority_alignment", 0.5)
        )
        resource_allocation_quality = self._clip(
            inputs.get("resource_allocation_quality", 0.5)
        )
        technological_trajectory_quality = self._clip(
            inputs.get("technological_trajectory_quality", 0.5)
        )
        constitutional_alignment = self._clip(
            inputs.get("constitutional_alignment", 0.5)
        )
        long_term_goal_coherence = self._clip(
            inputs.get("long_term_goal_coherence", 0.5)
        )
        civilizational_resilience = self._clip(
            inputs.get("civilizational_resilience", 0.5)
        )

        civilizational_strategic_index = self._clip(
            0.20 * scientific_priority_alignment
            + 0.15 * resource_allocation_quality
            + 0.15 * technological_trajectory_quality
            + 0.20 * constitutional_alignment
            + 0.15 * long_term_goal_coherence
            + 0.15 * civilizational_resilience
        )

        if civilizational_strategic_index >= 0.95:
            planner_class = "canonical_civilizational_strategy"
        elif civilizational_strategic_index >= 0.85:
            planner_class = "high_fidelity_civilizational_strategy"
        elif civilizational_strategic_index >= 0.70:
            planner_class = "functional_civilizational_strategy"
        else:
            planner_class = "partial_civilizational_strategy"

        return {
            "civilizational_strategic_index": round(
                civilizational_strategic_index, 4
            ),
            "species_strategy_score": round(
                civilizational_strategic_index, 4
            ),
            "planner_class": planner_class,
        }
