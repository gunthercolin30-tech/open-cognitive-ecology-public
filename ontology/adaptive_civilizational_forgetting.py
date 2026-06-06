
"""
Adaptive Civilizational Forgetting.
"""

from __future__ import annotations

PRIMITIVE = "adaptive_civilizational_forgetting"

DEPENDENCIES = [
    "civilizational_memory_archive",
    "persistent_multi_scale_memory",
    "distributed_symbolic_ecology",
    "openness_preservation_supervisor",
    "adaptive_ecological_regulation_engine",
    "ecological_decay",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class AdaptiveCivilizationalForgetting:

    def __init__(
        self,
        forgetting_gain: float = 0.15,
        preservation_floor: float = 0.35,
    ):
        self.forgetting_gain = forgetting_gain
        self.preservation_floor = preservation_floor

    def step(
        self,
        archive_size: int = 0,
        symbolic_density: float = 0.0,
        openness_score: float = 1.0,
    ):

        archive_pressure = min(
            1.0,
            archive_size / 100000.0,
        )

        symbolic_density = _bounded(
            symbolic_density
        )

        openness_score = _bounded(
            openness_score
        )

        forgetting_pressure = _bounded(
            (
                archive_pressure
                + symbolic_density
                + (1.0 - openness_score)
            ) / 3.0
        )

        adaptive_retention_score = _bounded(
            1.0
            - (
                forgetting_pressure
                * self.forgetting_gain
            )
        )

        adaptive_retention_score = max(
            self.preservation_floor,
            adaptive_retention_score,
        )

        symbolic_desaturation_index = _bounded(
            forgetting_pressure
            * adaptive_retention_score
        )

        archive_recycling_ratio = _bounded(
            symbolic_desaturation_index
            * 0.5
        )

        future_openness_preservation = _bounded(
            (
                openness_score
                + adaptive_retention_score
            ) / 2.0
        )

        semantic_load_factor = _bounded(
            symbolic_density
            * archive_pressure
        )

        return {
            "primitive": PRIMITIVE,
            "desaturation_active":
                forgetting_pressure >= 0.25,
            "forgetting_pressure":
                round(
                    forgetting_pressure,
                    4,
                ),
            "adaptive_retention_score":
                round(
                    adaptive_retention_score,
                    4,
                ),
            "symbolic_desaturation_index":
                round(
                    symbolic_desaturation_index,
                    4,
                ),
            "archive_recycling_ratio":
                round(
                    archive_recycling_ratio,
                    4,
                ),
            "future_openness_preserved":
                future_openness_preservation
                >= 0.75,
            "future_openness_preservation":
                round(
                    future_openness_preservation,
                    4,
                ),
            "semantic_load_factor":
                round(
                    semantic_load_factor,
                    4,
                ),
        }
