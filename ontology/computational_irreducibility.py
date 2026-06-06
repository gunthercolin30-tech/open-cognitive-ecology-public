from __future__ import annotations

PRIMITIVE = "computational_irreducibility"
DESCRIPTION = "Computational irreducibility."
DEPENDENCIES = []

"""
COMPUTATIONAL_IRREDUCIBILITY primitive.

This module formalizes the principle that some system dynamics cannot be
predicted more efficiently than by performing the full computation itself.
The primitive integrates predictive compressibility, simulation necessity,
and forecast limits.

The primitive computes:
- predictive_compressibility
- simulation_necessity
- forecast_limit
- computational_irreducibility_index
"""


PRIMITIVE_NAME = "COMPUTATIONAL_IRREDUCIBILITY"
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


class ComputationalIrreducibility:
    """Formal model of intrinsic limits to predictive compression."""

    def __init__(
        self,
        compressibility_weight=1.0,
        simulation_weight=1.0,
        forecast_weight=1.0,
    ):
        self.compressibility_weight = max(
            0.0, float(compressibility_weight)
        )
        self.simulation_weight = max(0.0, float(simulation_weight))
        self.forecast_weight = max(0.0, float(forecast_weight))

    def evaluate(
        self,
        predictive_compressibility=0.0,
        simulation_necessity=0.0,
        forecast_limit=0.0,
    ):
        predictive_compressibility = _clamp(
            predictive_compressibility
        )
        simulation_necessity = _clamp(simulation_necessity)
        forecast_limit = _clamp(forecast_limit)

        irreducible_compression = 1.0 - predictive_compressibility

        total_weight = (
            self.compressibility_weight
            + self.simulation_weight
            + self.forecast_weight
        )

        if total_weight <= 0.0:
            computational_irreducibility_index = 0.0
        else:
            computational_irreducibility_index = (
                self.compressibility_weight
                * irreducible_compression
                + self.simulation_weight
                * simulation_necessity
                + self.forecast_weight
                * forecast_limit
            ) / total_weight

        computational_irreducibility_index = _clamp(
            computational_irreducibility_index
        )

        is_empty = (
            predictive_compressibility == 0.0
            and simulation_necessity == 0.0
            and forecast_limit == 0.0
        )

        return {
            "predictive_compressibility":
                predictive_compressibility,
            "simulation_necessity": simulation_necessity,
            "forecast_limit": forecast_limit,
            "computational_irreducibility_index":
                computational_irreducibility_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "compressibility_weight":
                    self.compressibility_weight,
                "simulation_weight": self.simulation_weight,
                "forecast_weight": self.forecast_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        predictive_compressibility=0.0,
        simulation_necessity=0.0,
        forecast_limit=0.0,
    ):
        return self.evaluate(
            predictive_compressibility,
            simulation_necessity,
            forecast_limit,
        )

    def validate(
        self,
        predictive_compressibility=0.0,
        simulation_necessity=0.0,
        forecast_limit=0.0,
    ):
        result = self.evaluate(
            predictive_compressibility,
            simulation_necessity,
            forecast_limit,
        )

        index_ = result["computational_irreducibility_index"]

        return {
            "is_valid": index_ > 0.0,
            "computational_irreducibility_index": index_,
            "diagnostics": result["diagnostics"],
        }
