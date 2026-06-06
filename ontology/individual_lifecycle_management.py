"""
Individual Lifecycle Management.

Implements lifecycle state transitions from emergence through
development, reproduction, aging, and termination.
"""

from __future__ import annotations

PRIMITIVE = "individual_lifecycle_management"

DEPENDENCIES = [
    "developmental_growth_engine",
    "artificial_reproduction_protocol",
    "real_succession",
    "genealogical_continuity",
    "temporal_self_continuity",
]


class IndividualLifecycleManagement:
    STATES = [
        "emergence",
        "development",
        "maturity",
        "reproduction",
        "senescence",
        "termination",
    ]

    def __init__(self) -> None:
        self.age = 0
        self.state = "emergence"

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        developmental_index: float = 0.0,
        viability_score: float = 0.0,
        reproduction_readiness: float = 0.0,
    ) -> dict:
        developmental_index = self._clamp(developmental_index)
        viability_score = self._clamp(viability_score)
        reproduction_readiness = self._clamp(reproduction_readiness)

        self.age += 1

        if viability_score < 0.10:
            self.state = "termination"
        elif self.age > 100:
            self.state = "senescence"
        elif reproduction_readiness > 0.80:
            self.state = "reproduction"
        elif developmental_index > 0.75:
            self.state = "maturity"
        elif developmental_index > 0.25:
            self.state = "development"

        lifecycle_viability_index = (
            developmental_index +
            viability_score +
            reproduction_readiness
        ) / 3.0

        return {
            "primitive": PRIMITIVE.upper(),
            "age": self.age,
            "state": self.state,
            "lifecycle_viability_index": lifecycle_viability_index,
            "diagnostics": {
                "developmental_index": developmental_index,
                "viability_score": viability_score,
                "reproduction_readiness": reproduction_readiness,
                "dependencies": DEPENDENCIES,
            },
        }
