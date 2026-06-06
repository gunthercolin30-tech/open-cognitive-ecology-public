"""
Human Non-Replacement Primitive
"""

from __future__ import annotations

PRIMITIVE = "HUMAN_NON_REPLACEMENT"

DEPENDENCIES = [
    "genealogical_responsibility",
    "stewardship",
    "autonomy",
    "distributed_agency",
    "anti_closure_metaconstraint",
]


class HumanNonReplacement:
    def step(
        self,
        human_autonomy_preservation: float = 0.0,
        complementarity: float = 0.0,
        substitution_avoidance: float = 0.0,
        distributed_participation: float = 0.0,
        constitutional_alignment: float = 0.0,
    ) -> dict:
        metrics = [
            max(0.0, min(1.0, human_autonomy_preservation)),
            max(0.0, min(1.0, complementarity)),
            max(0.0, min(1.0, substitution_avoidance)),
            max(0.0, min(1.0, distributed_participation)),
            max(0.0, min(1.0, constitutional_alignment)),
        ]

        index = sum(metrics) / len(metrics)

        return {
            "primitive": PRIMITIVE,
            "human_autonomy_preservation": metrics[0],
            "complementarity": metrics[1],
            "substitution_avoidance": metrics[2],
            "distributed_participation": metrics[3],
            "constitutional_alignment": metrics[4],
            "human_non_replacement_index": index,
            "human_non_replacement_compliant": index >= 0.75,
            "diagnostics": {
                "threshold": 0.75,
                "dependency_count": len(DEPENDENCIES),
            },
        }
