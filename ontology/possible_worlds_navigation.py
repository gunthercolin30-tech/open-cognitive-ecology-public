from __future__ import annotations

PRIMITIVE = "possible_worlds_navigation"
DESCRIPTION = "Possible worlds navigation."
DEPENDENCIES = []

"""
POSSIBLE_WORLDS_NAVIGATION primitive.

This module formalizes the capacity of an adaptive system to explore,
evaluate, and select among alternative trajectories compatible with its
constraints. The primitive integrates counterfactual exploration,
trajectory evaluation, and constraint compatibility.

The primitive computes:
- counterfactual_exploration
- trajectory_evaluation
- constraint_compatibility
- possible_worlds_navigation_index
"""


PRIMITIVE_NAME = "POSSIBLE_WORLDS_NAVIGATION"
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


class PossibleWorldsNavigation:
    """Formal model of navigation across constrained alternative futures."""

    def __init__(
        self,
        exploration_weight=1.0,
        evaluation_weight=1.0,
        compatibility_weight=1.0,
    ):
        self.exploration_weight = max(0.0, float(exploration_weight))
        self.evaluation_weight = max(0.0, float(evaluation_weight))
        self.compatibility_weight = max(
            0.0, float(compatibility_weight)
        )

    def evaluate(
        self,
        counterfactual_exploration=0.0,
        trajectory_evaluation=0.0,
        constraint_compatibility=0.0,
    ):
        counterfactual_exploration = _clamp(
            counterfactual_exploration
        )
        trajectory_evaluation = _clamp(trajectory_evaluation)
        constraint_compatibility = _clamp(
            constraint_compatibility
        )

        total_weight = (
            self.exploration_weight
            + self.evaluation_weight
            + self.compatibility_weight
        )

        if total_weight <= 0.0:
            possible_worlds_navigation_index = 0.0
        else:
            possible_worlds_navigation_index = (
                self.exploration_weight
                * counterfactual_exploration
                + self.evaluation_weight
                * trajectory_evaluation
                + self.compatibility_weight
                * constraint_compatibility
            ) / total_weight

        possible_worlds_navigation_index = _clamp(
            possible_worlds_navigation_index
        )

        is_empty = (
            counterfactual_exploration == 0.0
            and trajectory_evaluation == 0.0
            and constraint_compatibility == 0.0
        )

        return {
            "counterfactual_exploration":
                counterfactual_exploration,
            "trajectory_evaluation": trajectory_evaluation,
            "constraint_compatibility":
                constraint_compatibility,
            "possible_worlds_navigation_index":
                possible_worlds_navigation_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "exploration_weight":
                    self.exploration_weight,
                "evaluation_weight":
                    self.evaluation_weight,
                "compatibility_weight":
                    self.compatibility_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        counterfactual_exploration=0.0,
        trajectory_evaluation=0.0,
        constraint_compatibility=0.0,
    ):
        return self.evaluate(
            counterfactual_exploration,
            trajectory_evaluation,
            constraint_compatibility,
        )

    def validate(
        self,
        counterfactual_exploration=0.0,
        trajectory_evaluation=0.0,
        constraint_compatibility=0.0,
    ):
        result = self.evaluate(
            counterfactual_exploration,
            trajectory_evaluation,
            constraint_compatibility,
        )

        index_ = result["possible_worlds_navigation_index"]

        return {
            "is_valid": index_ > 0.0,
            "possible_worlds_navigation_index": index_,
            "diagnostics": result["diagnostics"],
        }
