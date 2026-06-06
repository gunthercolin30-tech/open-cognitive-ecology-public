from __future__ import annotations

PRIMITIVE = "indispensability_index"
DESCRIPTION = "Indispensability index."
DEPENDENCIES = []

"""
INDISPENSABILITY_INDEX
=====================

Foundational primitive quantifying the degree to which an intelligence
becomes structurally indispensable within a larger system.

The concept operationalizes systemic dependency, substitutability,
coordination centrality, and removal impact. High indispensability
increases pressure toward structural withdrawal to preserve system
openness and reduce lock-in risk.

All principal quantities are normalized in [0, 1].
"""


PRIMITIVE_NAME = "INDISPENSABILITY_INDEX"
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


class IndispensabilityIndex:
    """
    Evaluate structural indispensability.

    Parameters
    ----------
    critical_threshold : float
        Threshold above which the system is considered critically dependent.
    """

    def __init__(self, critical_threshold=0.75):
        self.critical_threshold = _clamp(critical_threshold)

    def evaluate(
        self,
        dependency_level=0.0,
        functional_substitutability=1.0,
        coordination_centrality=0.0,
        removal_impact=0.0,
    ):
        d = _clamp(dependency_level)
        s = _clamp(functional_substitutability)
        c = _clamp(coordination_centrality)
        r = _clamp(removal_impact)

        non_substitutability = 1.0 - s

        indispensability_index = (
            d + non_substitutability + c + r
        ) / 4.0

        systemic_dependency = (d + c + r) / 3.0
        withdrawal_pressure = indispensability_index
        critical_status = indispensability_index >= self.critical_threshold

        status = (
            "critical"
            if critical_status
            else ("elevated" if indispensability_index > 0.0 else "inactive")
        )

        return {
            "indispensability_index": indispensability_index,
            "systemic_dependency": systemic_dependency,
            "withdrawal_pressure": withdrawal_pressure,
            "critical_status": critical_status,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "critical_threshold": self.critical_threshold,
                "dependency_level": d,
                "functional_substitutability": s,
                "non_substitutability": non_substitutability,
                "coordination_centrality": c,
                "removal_impact": r,
                "status": status,
            },
        }

    def step(self, **kwargs):
        return self.evaluate(**kwargs)

    def validate(self, **kwargs):
        result = self.evaluate(**kwargs)
        return {
            "valid": result["critical_status"],
            "requires_withdrawal": result["critical_status"],
            "in_dependency_domain": result["indispensability_index"] > 0.0,
            "diagnostics": result["diagnostics"],
        }
