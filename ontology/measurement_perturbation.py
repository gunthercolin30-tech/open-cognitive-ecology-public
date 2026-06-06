from __future__ import annotations

PRIMITIVE = "measurement_perturbation"
DESCRIPTION = "Measurement perturbation."
DEPENDENCIES = []

"""
MEASUREMENT_PERTURBATION
=======================

Foundational primitive formalizing the principle that any observation
necessarily perturbs the observed system. It quantifies perturbation,
information cost, irreversibility, and predictive degradation induced by
measurement.

All principal quantities are normalized in [0, 1].
"""


PRIMITIVE_NAME = "MEASUREMENT_PERTURBATION"
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


class MeasurementPerturbation:
    """
    Evaluate perturbation induced by measurement.
    """

    def __init__(self):
        pass

    def evaluate(
        self,
        measurement_intensity=0.0,
        observation_precision=0.0,
        system_sensitivity=0.0,
        interaction_strength=0.0,
    ):
        m = _clamp(measurement_intensity)
        o = _clamp(observation_precision)
        s = _clamp(system_sensitivity)
        i = _clamp(interaction_strength)

        perturbation_level = (m + o + s + i) / 4.0
        information_cost = (m + o) / 2.0
        irreversibility = (perturbation_level + i) / 2.0
        predictive_degradation = (perturbation_level + s) / 2.0

        status = (
            "high"
            if perturbation_level >= 0.75
            else ("moderate" if perturbation_level > 0.0 else "minimal")
        )

        return {
            "perturbation_level": perturbation_level,
            "information_cost": information_cost,
            "irreversibility": irreversibility,
            "predictive_degradation": predictive_degradation,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "measurement_intensity": m,
                "observation_precision": o,
                "system_sensitivity": s,
                "interaction_strength": i,
                "status": status,
            },
        }

    def step(self, **kwargs):
        return self.evaluate(**kwargs)

    def validate(self, **kwargs):
        result = self.evaluate(**kwargs)
        return {
            "valid": result["perturbation_level"] >= 0.0,
            "observation_is_intrusive": True,
            "diagnostics": result["diagnostics"],
        }
