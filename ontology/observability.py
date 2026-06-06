from __future__ import annotations

PRIMITIVE = "observability"
DESCRIPTION = "Observability."
DEPENDENCIES = []

"""
ontology/observability.py

Scientific implementation of the OBSERVABILITY primitive.

OBSERVABILITY quantifies the capacity of a system to infer internal states
from accessible signals and measurements.

Dimensions:
- state_visibility
- signal_informativeness
- inference_reliability
- observability_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "OBSERVABILITY"
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


class Observability:
    """
    Internal state inferability from accessible signals.
    """

    def __init__(
        self,
        state_visibility=0.0,
        signal_informativeness=0.0,
        inference_reliability=0.0,
    ):
        self.state_visibility = _clamp(state_visibility)
        self.signal_informativeness = _clamp(signal_informativeness)
        self.inference_reliability = _clamp(inference_reliability)

    def evaluate(self, state=None):
        """
        Evaluate observability metrics.
        """
        state = state or {}

        sv = _clamp(state.get("state_visibility", self.state_visibility))
        si = _clamp(
            state.get("signal_informativeness", self.signal_informativeness)
        )
        ir = _clamp(
            state.get("inference_reliability", self.inference_reliability)
        )

        observability_index = (sv + si + ir) / 3.0
        status = "active" if observability_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "state_visibility": sv,
            "signal_informativeness": si,
            "inference_reliability": ir,
            "status": status,
        }

        return {
            "state_visibility": sv,
            "signal_informativeness": si,
            "inference_reliability": ir,
            "observability_index": observability_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        return self.evaluate(state)

    def validate(self, state=None):
        result = self.evaluate(state)
        index = result["observability_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "observability_index": index,
            "diagnostics": result["diagnostics"],
        }
