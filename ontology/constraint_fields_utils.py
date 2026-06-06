from __future__ import annotations

PRIMITIVE = "constraint_fields_utils"
DESCRIPTION = "Constraint fields utils."
DEPENDENCIES = []

"""
Utility functions for constraint field primitives.
"""



def clamp(
    value: float,
    min_value: float = 0.0,
    max_value: float = 1.0,
) -> float:
    """
    Clamp a numeric value between two bounds.

    Parameters
    ----------
    value:
        Input value.
    min_value:
        Lower bound.
    max_value:
        Upper bound.

    Returns
    -------
    float
        Clamped value.
    """
    if min_value > max_value:
        min_value, max_value = max_value, min_value

    return max(min_value, min(max_value, value))


class ConstraintFieldsUtils:
    """Auto-generated activation class for constraint_fields_utils."""

    PRIMITIVE = "constraint_fields_utils"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

