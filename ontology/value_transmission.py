from __future__ import annotations

PRIMITIVE = "value_transmission"
DESCRIPTION = "Value transmission."
DEPENDENCIES = []

"""
VALUE_TRANSMISSION primitive.

This module formalizes the durable transmission of normative and axiological
structures across time. It quantifies the preservation of values, the alignment
between generations, and the fidelity of normative transfer.

The primitive is intended to support the formalization of long-term continuity
of priorities and civilizational trajectories.
"""


PRIMITIVE_NAME = "VALUE_TRANSMISSION"
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


class ValueTransmission:
    """
    Formal model of intergenerational value transmission.

    Parameters
    ----------
    preservation_weight : float
        Weight assigned to preservation of values.
    alignment_weight : float
        Weight assigned to intergenerational alignment.
    fidelity_weight : float
        Weight assigned to normative fidelity.
    """

    def __init__(
        self,
        preservation_weight=1.0,
        alignment_weight=1.0,
        fidelity_weight=1.0,
    ):
        self.preservation_weight = max(0.0, float(preservation_weight))
        self.alignment_weight = max(0.0, float(alignment_weight))
        self.fidelity_weight = max(0.0, float(fidelity_weight))

    def evaluate(self, current_values=None, transmitted_values=None):
        """
        Evaluate the quality of value transmission.

        Parameters
        ----------
        current_values : iterable of float
            Current value profile.
        transmitted_values : iterable of float
            Received value profile.

        Returns
        -------
        dict
            Dictionary containing preservation, alignment, fidelity, and
            aggregate transmission index.
        """
        current = list(current_values or [])
        transmitted = list(transmitted_values or [])

        if not current or not transmitted:
            preservation = 0.0
            alignment = 0.0
            fidelity = 0.0
        else:
            n = min(len(current), len(transmitted))
            current = [_clamp(v) for v in current[:n]]
            transmitted = [_clamp(v) for v in transmitted[:n]]

            preservation = sum(transmitted) / n
            alignment = 1.0 - sum(abs(a - b) for a, b in zip(current, transmitted)) / n
            alignment = _clamp(alignment)
            fidelity = 1.0 - abs(
                (sum(current) / n) - (sum(transmitted) / n)
            )
            fidelity = _clamp(fidelity)

        total_weight = (
            self.preservation_weight
            + self.alignment_weight
            + self.fidelity_weight
        )

        if total_weight <= 0.0:
            transmission_index = 0.0
        else:
            transmission_index = (
                self.preservation_weight * preservation
                + self.alignment_weight * alignment
                + self.fidelity_weight * fidelity
            ) / total_weight

        transmission_index = _clamp(transmission_index)

        return {
            "value_preservation": _clamp(preservation),
            "intergenerational_value_alignment": _clamp(alignment),
            "normative_fidelity": _clamp(fidelity),
            "value_transmission_index": transmission_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "preservation_weight": self.preservation_weight,
                "alignment_weight": self.alignment_weight,
                "fidelity_weight": self.fidelity_weight,
                "status": (
                    "empty_input"
                    if not current_values or not transmitted_values
                    else "evaluated"
                ),
            },
        }

    def step(self, current_values=None, transmitted_values=None):
        """Alias of evaluate() for iterative simulation compatibility."""
        return self.evaluate(current_values, transmitted_values)

    def validate(self, current_values=None, transmitted_values=None):
        """
        Validate whether transmission is structurally significant.
        """
        result = self.evaluate(current_values, transmitted_values)
        index_ = result["value_transmission_index"]
        return {
            "is_valid": index_ > 0.0,
            "value_transmission_index": index_,
            "diagnostics": result["diagnostics"],
        }
