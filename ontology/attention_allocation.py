from __future__ import annotations

PRIMITIVE = "attention_allocation"
DESCRIPTION = "Attention allocation."
DEPENDENCIES = []

"""
ATTENTION_ALLOCATION primitive.

This module formalizes the selective allocation of limited cognitive resources.
Attention emerges from the interaction between stimulus salience, available
resource focus, and strategic priority assignment.

The primitive computes:
- salience_distribution
- resource_focus
- selective_priority
- attention_index
"""


PRIMITIVE_NAME = "ATTENTION_ALLOCATION"
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


class AttentionAllocation:
    """Formal model of selective cognitive resource allocation."""

    def __init__(
        self,
        salience_weight=1.0,
        focus_weight=1.0,
        priority_weight=1.0,
    ):
        self.salience_weight = max(0.0, float(salience_weight))
        self.focus_weight = max(0.0, float(focus_weight))
        self.priority_weight = max(0.0, float(priority_weight))

    def evaluate(
        self,
        salience_distribution=0.0,
        resource_focus=0.0,
        selective_priority=0.0,
    ):
        salience_distribution = _clamp(salience_distribution)
        resource_focus = _clamp(resource_focus)
        selective_priority = _clamp(selective_priority)

        total_weight = (
            self.salience_weight
            + self.focus_weight
            + self.priority_weight
        )

        if total_weight <= 0.0:
            attention_index = 0.0
        else:
            attention_index = (
                self.salience_weight * salience_distribution
                + self.focus_weight * resource_focus
                + self.priority_weight * selective_priority
            ) / total_weight

        attention_index = _clamp(attention_index)

        is_empty = (
            salience_distribution == 0.0
            and resource_focus == 0.0
            and selective_priority == 0.0
        )

        return {
            "salience_distribution": salience_distribution,
            "resource_focus": resource_focus,
            "selective_priority": selective_priority,
            "attention_index": attention_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "salience_weight": self.salience_weight,
                "focus_weight": self.focus_weight,
                "priority_weight": self.priority_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        salience_distribution=0.0,
        resource_focus=0.0,
        selective_priority=0.0,
    ):
        return self.evaluate(
            salience_distribution,
            resource_focus,
            selective_priority,
        )

    def validate(
        self,
        salience_distribution=0.0,
        resource_focus=0.0,
        selective_priority=0.0,
    ):
        result = self.evaluate(
            salience_distribution,
            resource_focus,
            selective_priority,
        )

        attention_index = result["attention_index"]

        return {
            "is_valid": attention_index > 0.0,
            "attention_index": attention_index,
            "diagnostics": result["diagnostics"],
        }
