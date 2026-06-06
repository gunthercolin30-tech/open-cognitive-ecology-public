"""
Constitutional Integrity Index Primitive
"""

from __future__ import annotations

PRIMITIVE = "CONSTITUTIONAL_INTEGRITY_INDEX"

DEPENDENCIES = [
    "meta_species_constraint",
    "constraint_constitution_layer",
]


class ConstitutionalIntegrityIndex:
    def step(
        self,
        constitutional_integrity_index: float = 0.0,
    ) -> dict:
        value = max(0.0, min(1.0, constitutional_integrity_index))

        return {
            "primitive": PRIMITIVE,
            "constitutional_integrity_index": value,
            "constitutional_integrity_class": (
                "HIGH" if value >= 0.90
                else "MODERATE" if value >= 0.75
                else "LOW"
            ),
            "constitutionally_viable": value >= 0.75,
            "diagnostics": {
                "high_threshold": 0.90,
                "viability_threshold": 0.75,
                "dependency_count": len(DEPENDENCIES),
            },
        }
