from __future__ import annotations

PRIMITIVE = "control_hierarchy"
DESCRIPTION = "Control hierarchy."
DEPENDENCIES = []

"""
ontology/control_hierarchy.py

Scientific implementation of the CONTROL_HIERARCHY primitive.

CONTROL_HIERARCHY quantifies the capacity of a system to organize
nested regulatory levels in which higher-order controllers coordinate
and modulate lower-order controllers.

Dimensions:
- hierarchical_depth
- cross_level_coordination
- meta_control_capacity
- control_hierarchy_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "CONTROL_HIERARCHY"
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


class ControlHierarchy:
    """
    Multi-level regulatory organization and meta-control capacity.
    """

    def __init__(
        self,
        hierarchical_depth=0.0,
        cross_level_coordination=0.0,
        meta_control_capacity=0.0,
    ):
        self.hierarchical_depth = _clamp(hierarchical_depth)
        self.cross_level_coordination = _clamp(cross_level_coordination)
        self.meta_control_capacity = _clamp(meta_control_capacity)

    def evaluate(self, state=None):
        """
        Evaluate control hierarchy metrics.
        """
        state = state or {}

        hd = _clamp(state.get("hierarchical_depth", self.hierarchical_depth))
        clc = _clamp(
            state.get(
                "cross_level_coordination",
                self.cross_level_coordination,
            )
        )
        mcc = _clamp(
            state.get("meta_control_capacity", self.meta_control_capacity)
        )

        control_hierarchy_index = (hd + clc + mcc) / 3.0
        status = "active" if control_hierarchy_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "hierarchical_depth": hd,
            "cross_level_coordination": clc,
            "meta_control_capacity": mcc,
            "status": status,
        }

        return {
            "hierarchical_depth": hd,
            "cross_level_coordination": clc,
            "meta_control_capacity": mcc,
            "control_hierarchy_index": control_hierarchy_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        return self.evaluate(state)

    def validate(self, state=None):
        result = self.evaluate(state)
        index = result["control_hierarchy_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "control_hierarchy_index": index,
            "diagnostics": result["diagnostics"],
        }
