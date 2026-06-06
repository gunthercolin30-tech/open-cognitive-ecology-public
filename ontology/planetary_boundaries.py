from __future__ import annotations

PRIMITIVE = "planetary_boundaries"
DESCRIPTION = "Planetary boundaries."
DEPENDENCIES = []

"""
PLANETARY_BOUNDARIES primitive.

This module formalizes the global biophysical limits within which
civilizational trajectories remain viable. The primitive integrates ecological
pressure, integrity of critical boundaries, and overshoot risk.

The primitive computes:
- ecological_pressure
- boundary_integrity
- overshoot_risk
- planetary_boundaries_index
"""


PRIMITIVE_NAME = "PLANETARY_BOUNDARIES"
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


class PlanetaryBoundaries:
    """Formal model of planetary viability constraints."""

    def __init__(
        self,
        pressure_weight=1.0,
        integrity_weight=1.0,
        risk_weight=1.0,
    ):
        self.pressure_weight = max(0.0, float(pressure_weight))
        self.integrity_weight = max(0.0, float(integrity_weight))
        self.risk_weight = max(0.0, float(risk_weight))

    def evaluate(
        self,
        ecological_pressure=0.0,
        boundary_integrity=0.0,
        overshoot_risk=0.0,
    ):
        ecological_pressure = _clamp(ecological_pressure)
        boundary_integrity = _clamp(boundary_integrity)
        overshoot_risk = _clamp(overshoot_risk)

        safe_pressure = 1.0 - ecological_pressure
        safe_risk = 1.0 - overshoot_risk

        total_weight = (
            self.pressure_weight
            + self.integrity_weight
            + self.risk_weight
        )

        if total_weight <= 0.0:
            planetary_boundaries_index = 0.0
        else:
            planetary_boundaries_index = (
                self.pressure_weight * safe_pressure
                + self.integrity_weight * boundary_integrity
                + self.risk_weight * safe_risk
            ) / total_weight

        planetary_boundaries_index = _clamp(planetary_boundaries_index)

        is_empty = (
            ecological_pressure == 0.0
            and boundary_integrity == 0.0
            and overshoot_risk == 0.0
        )

        return {
            "ecological_pressure": ecological_pressure,
            "boundary_integrity": boundary_integrity,
            "overshoot_risk": overshoot_risk,
            "planetary_boundaries_index": planetary_boundaries_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "pressure_weight": self.pressure_weight,
                "integrity_weight": self.integrity_weight,
                "risk_weight": self.risk_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        ecological_pressure=0.0,
        boundary_integrity=0.0,
        overshoot_risk=0.0,
    ):
        return self.evaluate(
            ecological_pressure,
            boundary_integrity,
            overshoot_risk,
        )

    def validate(
        self,
        ecological_pressure=0.0,
        boundary_integrity=0.0,
        overshoot_risk=0.0,
    ):
        result = self.evaluate(
            ecological_pressure,
            boundary_integrity,
            overshoot_risk,
        )

        index_ = result["planetary_boundaries_index"]

        return {
            "is_valid": index_ > 0.0,
            "planetary_boundaries_index": index_,
            "diagnostics": result["diagnostics"],
        }
