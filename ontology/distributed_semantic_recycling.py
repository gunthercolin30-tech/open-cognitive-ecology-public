
"""
Distributed Semantic Recycling.
"""

from __future__ import annotations

import random

PRIMITIVE = "distributed_semantic_recycling"

DEPENDENCIES = [
    "adaptive_civilizational_forgetting",
    "distributed_symbolic_ecology",
    "semantic_field",
    "symbolic_generation",
    "semantic_propagation",
    "symbolic_fragmentation",
    "innovation_retention",
    "structural_attractor",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class DistributedSemanticRecycling:

    def __init__(
        self,
        recycling_gain: float = 0.20,
        diversity_floor: float = 0.35,
    ):
        self.recycling_gain = recycling_gain
        self.diversity_floor = diversity_floor

        self.recycled_history = []

    def _recombine_symbol(
        self,
        symbol_a: str,
        symbol_b: str,
    ):

        left = symbol_a[: max(1, len(symbol_a) // 2)]
        right = symbol_b[max(0, len(symbol_b) // 2):]

        return (left + right)[:12]

    def step(
        self,
        forgotten_symbols=None,
        openness_score: float = 1.0,
    ):

        forgotten_symbols = forgotten_symbols or []

        openness_score = _bounded(
            openness_score
        )

        recycling_pressure = _bounded(
            (
                len(forgotten_symbols) * 0.05
                + (1.0 - openness_score)
            )
        )

        recycling_active = (
            recycling_pressure >= 0.10
        )

        recycled_symbols = []

        if len(forgotten_symbols) >= 2:

            random.shuffle(
                forgotten_symbols
            )

            for i in range(
                0,
                len(forgotten_symbols) - 1,
                2,
            ):

                symbol_a = forgotten_symbols[i]
                symbol_b = forgotten_symbols[i + 1]

                recycled = self._recombine_symbol(
                    symbol_a,
                    symbol_b,
                )

                recycled_symbols.append(
                    recycled
                )

        symbolic_recombination_index = _bounded(
            len(recycled_symbols)
            * self.recycling_gain
        )

        distributed_recycling_diversity = max(
            self.diversity_floor,
            1.0
            - (
                symbolic_recombination_index
                * 0.3
            )
        )

        attractor_regeneration_score = _bounded(
            symbolic_recombination_index
            * openness_score
        )

        semantic_recycling_stability = _bounded(
            (
                distributed_recycling_diversity
                + openness_score
            ) / 2.0
        )

        future_openness_preservation = _bounded(
            (
                semantic_recycling_stability
                + openness_score
            ) / 2.0
        )

        self.recycled_history.extend(
            recycled_symbols
        )

        if len(self.recycled_history) > 500:
            self.recycled_history = (
                self.recycled_history[-500:]
            )

        return {
            "primitive": PRIMITIVE,
            "recycling_active":
                recycling_active,
            "recycling_pressure":
                round(
                    recycling_pressure,
                    4,
                ),
            "recycled_symbol_count":
                len(recycled_symbols),
            "recycled_symbols":
                recycled_symbols,
            "symbolic_recombination_index":
                round(
                    symbolic_recombination_index,
                    4,
                ),
            "distributed_recycling_diversity":
                round(
                    distributed_recycling_diversity,
                    4,
                ),
            "attractor_regeneration_score":
                round(
                    attractor_regeneration_score,
                    4,
                ),
            "semantic_recycling_stability":
                round(
                    semantic_recycling_stability,
                    4,
                ),
            "future_openness_preserved":
                future_openness_preservation
                >= 0.70,
            "future_openness_preservation":
                round(
                    future_openness_preservation,
                    4,
                ),
        }
