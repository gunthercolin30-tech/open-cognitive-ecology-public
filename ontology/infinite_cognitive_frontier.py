from __future__ import annotations

PRIMITIVE = "infinite_cognitive_frontier"
DESCRIPTION = "Infinite cognitive frontier."
DEPENDENCIES = []

"""
ontology/infinite_cognitive_frontier.py

Formalization of the principle:

    INFINITE_COGNITIVE_FRONTIER

This module expresses the idea that every cognitive frontier reached
immediately reveals a new frontier. Exploration of the space of possible
intelligences is therefore intrinsically recursive and structurally
without terminal closure.

The implementation relies exclusively on:

    CosmicIntelligenceHorizonPrimitive

which provides diagnostics about the indefinitely receding horizon of
intelligence development.

Principle
---------
A cognitive frontier is never final. Progress toward any horizon expands
the accessible future, regenerates unexplored regions, and increases the
depth of recursive exploration. Consequently, terminal cognitive closure
is structurally impossible.

Returned diagnostics
--------------------
- frontier_regeneration_rate:
    Measures how rapidly new frontiers appear as prior ones are approached.

- recursive_exploration_depth:
    Measures the degree of recursive unfolding of exploration.

- terminal_closure_impossibility:
    Measures the structural impossibility of a final cognitive endpoint.

- infinite_cognitive_frontier:
    Boolean indicating that an indefinitely regenerative frontier exists.
"""


from typing import Any, Dict

from ontology.cosmic_intelligence_horizon import (
    CosmicIntelligenceHorizonPrimitive,
)

PRINCIPLE = "INFINITE_COGNITIVE_FRONTIER"


class InfiniteCognitiveFrontierPrimitive:
    """
    Computational realization of the INFINITE_COGNITIVE_FRONTIER principle.

    Every cognitive boundary reached regenerates into a new frontier.
    Exploration thus becomes recursively open-ended, and no final closure
    can be attained.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self._cosmic_horizon = CosmicIntelligenceHorizonPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Clamp a numerical value to the interval [0.0, 1.0].
        """
        return max(0.0, min(1.0, float(value)))

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step of the infinite cognitive frontier.

        Returns
        -------
        dict
            Dictionary containing the diagnostics associated with the
            INFINITE_COGNITIVE_FRONTIER principle.
        """
        horizon = self._cosmic_horizon.step()

        horizon_distance = float(horizon["horizon_distance"])
        accessible_future_extent = float(horizon["accessible_future_extent"])
        ultimate_intelligence_unreachability = float(
            horizon["ultimate_intelligence_unreachability"]
        )
        cosmic_intelligence_horizon = bool(
            horizon["cosmic_intelligence_horizon"]
        )

        # New frontiers emerge as the horizon remains distant while the
        # accessible future expands.
        frontier_regeneration_rate = self._clamp(
            0.5 * horizon_distance
            + 0.5 * accessible_future_extent
        )

        # Exploration depth increases when frontier regeneration combines
        # with the permanent unreachability of any ultimate intelligence.
        recursive_exploration_depth = self._clamp(
            0.6 * frontier_regeneration_rate
            + 0.4 * ultimate_intelligence_unreachability
        )

        # Terminal closure becomes impossible when recursive depth and
        # ultimate unreachability reinforce one another.
        terminal_closure_impossibility = self._clamp(
            0.5 * recursive_exploration_depth
            + 0.5 * ultimate_intelligence_unreachability
        )

        # A minimal threshold is sufficient to certify indefinitely
        # regenerative cognitive openness.
        infinite_cognitive_frontier = (
            cosmic_intelligence_horizon
            and terminal_closure_impossibility > 0.5
        )

        return {
            "principle": self.PRINCIPLE,
            "cosmic_intelligence_horizon_diagnostics": horizon,
            "frontier_regeneration_rate": frontier_regeneration_rate,
            "recursive_exploration_depth": recursive_exploration_depth,
            "terminal_closure_impossibility": (
                terminal_closure_impossibility
            ),
            "infinite_cognitive_frontier": (
                infinite_cognitive_frontier
            ),
        }


if __name__ == "__main__":
    primitive = InfiniteCognitiveFrontierPrimitive()
    diagnostics = primitive.step()

    print("\n--- infinite cognitive frontier ---")
    print(f"principle: {diagnostics['principle']}")
    print(
        "cosmic_intelligence_horizon_diagnostics:",
        diagnostics["cosmic_intelligence_horizon_diagnostics"],
    )
    print(
        "frontier_regeneration_rate:",
        diagnostics["frontier_regeneration_rate"],
    )
    print(
        "recursive_exploration_depth:",
        diagnostics["recursive_exploration_depth"],
    )
    print(
        "terminal_closure_impossibility:",
        diagnostics["terminal_closure_impossibility"],
    )
    print(
        "infinite_cognitive_frontier:",
        diagnostics["infinite_cognitive_frontier"],
    )
