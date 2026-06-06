from __future__ import annotations

PRIMITIVE = "buffering_capacity"
DESCRIPTION = "Buffering capacity."
DEPENDENCIES = []

"""
ontology/buffering_capacity.py

Scientific implementation of the BUFFERING_CAPACITY primitive.

BUFFERING_CAPACITY quantifies the capacity of a system to temporarily absorb
perturbations and delay functional degradation.

Dimensions:
- absorption_capacity
- delay_tolerance
- stabilization_margin
- buffering_capacity_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "BUFFERING_CAPACITY"
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


class BufferingCapacity:
    """
    Temporary perturbation absorption and stabilization capacity.
    """

    def __init__(
        self,
        absorption_capacity=0.0,
        delay_tolerance=0.0,
        stabilization_margin=0.0,
    ):
        self.absorption_capacity = _clamp(absorption_capacity)
        self.delay_tolerance = _clamp(delay_tolerance)
        self.stabilization_margin = _clamp(stabilization_margin)

    def evaluate(self, state=None):
        """
        Evaluate buffering capacity metrics.

        Parameters
        ----------
        state : dict or None
            Optional override values:
            - absorption_capacity
            - delay_tolerance
            - stabilization_margin
        """
        state = state or {}

        ac = _clamp(state.get("absorption_capacity", self.absorption_capacity))
        dt = _clamp(state.get("delay_tolerance", self.delay_tolerance))
        sm = _clamp(state.get("stabilization_margin", self.stabilization_margin))

        buffering_capacity_index = (ac + dt + sm) / 3.0
        status = "active" if buffering_capacity_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "absorption_capacity": ac,
            "delay_tolerance": dt,
            "stabilization_margin": sm,
            "status": status,
        }

        return {
            "absorption_capacity": ac,
            "delay_tolerance": dt,
            "stabilization_margin": sm,
            "buffering_capacity_index": buffering_capacity_index,
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
        index = result["buffering_capacity_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "buffering_capacity_index": index,
            "diagnostics": result["diagnostics"],
        }
