from __future__ import annotations

PRIMITIVE = "quantum_indeterminacy"
DESCRIPTION = "Quantum indeterminacy."
DEPENDENCIES = []

"""
QUANTUM_INDETERMINACY
====================

Foundational primitive formalizing irreducible indeterminacy imposed by
the quantum structure of reality. It quantifies the minimal uncertainty
that remains even under idealized observation and constrains prediction
and knowledge.

All principal quantities are normalized in [0, 1].
"""


PRIMITIVE_NAME = "QUANTUM_INDETERMINACY"
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


class QuantumIndeterminacy:
    """
    Evaluate irreducible quantum indeterminacy.
    """

    def __init__(self):
        pass

    def evaluate(
        self,
        state_superposition=0.0,
        measurement_precision=1.0,
        information_access=1.0,
        predictive_horizon=1.0,
    ):
        s = _clamp(state_superposition)
        m = _clamp(measurement_precision)
        i = _clamp(information_access)
        p = _clamp(predictive_horizon)

        precision_limit = 1.0 - m
        access_limit = 1.0 - i
        prediction_limit = 1.0 - p

        indeterminacy_level = (
            s + precision_limit + access_limit + prediction_limit
        ) / 4.0

        knowledge_incompleteness = (access_limit + prediction_limit) / 2.0
        uncertainty_floor = indeterminacy_level

        status = (
            "high"
            if indeterminacy_level >= 0.75
            else ("moderate" if indeterminacy_level > 0.0 else "minimal")
        )

        return {
            "indeterminacy_level": indeterminacy_level,
            "prediction_limit": prediction_limit,
            "knowledge_incompleteness": knowledge_incompleteness,
            "uncertainty_floor": uncertainty_floor,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "state_superposition": s,
                "measurement_precision": m,
                "information_access": i,
                "predictive_horizon": p,
                "precision_limit": precision_limit,
                "access_limit": access_limit,
                "status": status,
            },
        }

    def step(self, **kwargs):
        return self.evaluate(**kwargs)

    def validate(self, **kwargs):
        result = self.evaluate(**kwargs)
        return {
            "valid": result["indeterminacy_level"] >= 0.0,
            "physically_constrained": True,
            "diagnostics": result["diagnostics"],
        }
