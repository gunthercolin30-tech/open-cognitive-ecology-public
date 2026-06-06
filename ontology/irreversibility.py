from __future__ import annotations

PRIMITIVE = "irreversibility"
DESCRIPTION = "Irreversibility."
DEPENDENCIES = []

"""
IRREVERSIBILITY primitive.

This module formalizes the intrinsic directionality of time in systems whose
transformations cannot be fully undone. Irreversibility emerges from entropy
production, historical path dependence, and reversal difficulty.

The primitive computes:
- entropy_production
- historical_path_dependence
- reversal_difficulty
- irreversibility_index
"""


PRIMITIVE_NAME = "IRREVERSIBILITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


class Irreversibility:
    """Formal model of temporal asymmetry under constraints."""

    def __init__(
        self,
        entropy_weight=1.0,
        path_weight=1.0,
        reversal_weight=1.0,
    ):
        self.entropy_weight = max(0.0, float(entropy_weight))
        self.path_weight = max(0.0, float(path_weight))
        self.reversal_weight = max(0.0, float(reversal_weight))

    def evaluate(
        self,
        entropy_production=0.0,
        historical_path_dependence=0.0,
        reversal_difficulty=0.0,
    ):
        entropy_production = _clamp(entropy_production)
        historical_path_dependence = _clamp(
            historical_path_dependence
        )
        reversal_difficulty = _clamp(reversal_difficulty)

        total_weight = (
            self.entropy_weight
            + self.path_weight
            + self.reversal_weight
        )

        if total_weight <= 0.0:
            irreversibility_index = 0.0
        else:
            irreversibility_index = (
                self.entropy_weight * entropy_production
                + self.path_weight * historical_path_dependence
                + self.reversal_weight * reversal_difficulty
            ) / total_weight

        irreversibility_index = _clamp(irreversibility_index)

        is_empty = (
            entropy_production == 0.0
            and historical_path_dependence == 0.0
            and reversal_difficulty == 0.0
        )

        return {
            "entropy_production": entropy_production,
            "historical_path_dependence":
                historical_path_dependence,
            "reversal_difficulty": reversal_difficulty,
            "irreversibility_index": irreversibility_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "entropy_weight": self.entropy_weight,
                "path_weight": self.path_weight,
                "reversal_weight": self.reversal_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        entropy_production=0.0,
        historical_path_dependence=0.0,
        reversal_difficulty=0.0,
    ):
        return self.evaluate(
            entropy_production,
            historical_path_dependence,
            reversal_difficulty,
        )

    def validate(
        self,
        entropy_production=0.0,
        historical_path_dependence=0.0,
        reversal_difficulty=0.0,
    ):
        result = self.evaluate(
            entropy_production,
            historical_path_dependence,
            reversal_difficulty,
        )

        index_ = result["irreversibility_index"]

        return {
            "is_valid": index_ > 0.0,
            "irreversibility_index": index_,
            "diagnostics": result["diagnostics"],
        }
