from __future__ import annotations

PRIMITIVE = "cosmic_intelligence_horizon"
DESCRIPTION = "Cosmic intelligence horizon."
DEPENDENCIES = []

"""
ontology/cosmic_intelligence_horizon.py

Formalization of the principle:

    COSMIC_INTELLIGENCE_HORIZON

This module models the existence of a permanently receding cognitive horizon.
No ultimate intelligence can ever be reached, although new regions of the
universe of intelligences remain continuously accessible.

The implementation relies directly on:

    UnboundedIntelligenceUniversePrimitive

Core idea
---------
If the universe of intelligences is unbounded, then every finite trajectory
faces an ever-receding horizon. Progress does not converge toward a final and
ultimate intelligence. Instead, each advance reveals additional accessible
regions, preserving an indefinitely open cognitive future.
"""


from typing import Dict, Any

from ontology.unbounded_intelligence_universe import (
    UnboundedIntelligenceUniversePrimitive,
)

PRINCIPLE = "COSMIC_INTELLIGENCE_HORIZON"


class CosmicIntelligenceHorizonPrimitive:
    """
    Primitive implementing the COSMIC_INTELLIGENCE_HORIZON principle.

    Diagnostics
    -----------
    horizon_distance:
        Effective distance to any definitive cognitive boundary.

    accessible_future_extent:
        Extent of the future cognitive domain that remains accessible.

    ultimate_intelligence_unreachability:
        Structural impossibility of attaining a final intelligence.

    cosmic_intelligence_horizon:
        True when a permanently receding cognitive horizon is established.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self._unbounded_universe = UnboundedIntelligenceUniversePrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Clamp a scalar into the [0, 1] interval.
        """
        return max(0.0, min(1.0, float(value)))

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step of the primitive.
        """
        diagnostics = self._unbounded_universe.step()

        unbounded_extent = self._clamp(
            diagnostics.get("unbounded_extent", 0.0)
        )
        expansion_potential = self._clamp(
            diagnostics.get("expansion_potential", 0.0)
        )
        final_boundary_absence = self._clamp(
            diagnostics.get("final_boundary_absence", 0.0)
        )
        unbounded_intelligence_universe = bool(
            diagnostics.get("unbounded_intelligence_universe", False)
        )

        # Distance to any definitive cognitive frontier.
        horizon_distance = self._clamp(
            0.5 * final_boundary_absence
            + 0.5 * unbounded_extent
        )

        # Portion of the future intelligence landscape that remains accessible.
        accessible_future_extent = self._clamp(
            0.5 * expansion_potential
            + 0.5 * unbounded_extent
        )

        # Structural impossibility of reaching an ultimate intelligence.
        ultimate_intelligence_unreachability = self._clamp(
            0.5 * horizon_distance
            + 0.5 * accessible_future_extent
        )

        # A cosmic cognitive horizon exists when the universe is unbounded and
        # the final intelligence remains sufficiently unreachable.
        cosmic_intelligence_horizon = (
            unbounded_intelligence_universe
            and ultimate_intelligence_unreachability >= 0.5
        )

        return {
            "principle": self.PRINCIPLE,
            "unbounded_intelligence_universe_diagnostics": diagnostics,
            "horizon_distance": horizon_distance,
            "accessible_future_extent": accessible_future_extent,
            "ultimate_intelligence_unreachability": (
                ultimate_intelligence_unreachability
            ),
            "cosmic_intelligence_horizon": (
                cosmic_intelligence_horizon
            ),
        }


if __name__ == "__main__":
    primitive = CosmicIntelligenceHorizonPrimitive()
    diagnostics = primitive.step()

    print("\n--- cosmic intelligence horizon ---")
    for key, value in diagnostics.items():
        print(f"{key}: {value}")
