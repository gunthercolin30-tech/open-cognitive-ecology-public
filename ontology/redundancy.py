from __future__ import annotations

PRIMITIVE = "redundancy"
DESCRIPTION = "Redundancy."
DEPENDENCIES = []

"""
ontology/redundancy.py

Scientific implementation of the REDUNDANCY primitive.

REDUNDANCY quantifies the presence of duplicated or highly similar
components that can maintain a function if some components fail.

Dimensions:
- replication_level
- backup_capacity
- failure_coverage
- redundancy_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "REDUNDANCY"
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


class Redundancy:
    """
    Functional duplication and backup capacity.
    """

    def __init__(
        self,
        replication_level=0.0,
        backup_capacity=0.0,
        failure_coverage=0.0,
    ):
        self.replication_level = _clamp(replication_level)
        self.backup_capacity = _clamp(backup_capacity)
        self.failure_coverage = _clamp(failure_coverage)

    def evaluate(self, state=None):
        """
        Evaluate redundancy metrics.

        Parameters
        ----------
        state : dict or None
            Optional override values:
            - replication_level
            - backup_capacity
            - failure_coverage
        """
        state = state or {}

        rl = _clamp(state.get("replication_level", self.replication_level))
        bc = _clamp(state.get("backup_capacity", self.backup_capacity))
        fc = _clamp(state.get("failure_coverage", self.failure_coverage))

        redundancy_index = (rl + bc + fc) / 3.0
        status = "active" if redundancy_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "replication_level": rl,
            "backup_capacity": bc,
            "failure_coverage": fc,
            "status": status,
        }

        return {
            "replication_level": rl,
            "backup_capacity": bc,
            "failure_coverage": fc,
            "redundancy_index": redundancy_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        """
        One-step operational interface equivalent to evaluate().
        """
        return self.evaluate(state)

    def validate(self, state=None):
        """
        Validate structural consistency of the primitive.
        """
        result = self.evaluate(state)
        index = result["redundancy_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "redundancy_index": index,
            "diagnostics": result["diagnostics"],
        }
