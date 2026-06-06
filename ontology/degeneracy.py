from __future__ import annotations

PRIMITIVE = "degeneracy"
DESCRIPTION = "Degeneracy."
DEPENDENCIES = []

"""
ontology/degeneracy.py

Scientific implementation of the DEGENERACY primitive.

DEGENERACY quantifies the capacity of structurally distinct configurations
to realize equivalent or overlapping functions. It captures non-identical
redundancy and functional substitutability.

Dimensions:
- structural_diversity
- functional_overlap
- substitutability
- degeneracy_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "DEGENERACY"
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


class Degeneracy:
    """
    Structural diversity with functional equivalence.
    """

    def __init__(
        self,
        structural_diversity=0.0,
        functional_overlap=0.0,
        substitutability=0.0,
    ):
        self.structural_diversity = _clamp(structural_diversity)
        self.functional_overlap = _clamp(functional_overlap)
        self.substitutability = _clamp(substitutability)

    def evaluate(self, state=None):
        """
        Evaluate degeneracy metrics.

        Parameters
        ----------
        state : dict or None
            Optional override values:
            - structural_diversity
            - functional_overlap
            - substitutability
        """
        state = state or {}

        sd = _clamp(state.get("structural_diversity", self.structural_diversity))
        fo = _clamp(state.get("functional_overlap", self.functional_overlap))
        su = _clamp(state.get("substitutability", self.substitutability))

        degeneracy_index = (sd + fo + su) / 3.0
        status = "active" if degeneracy_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "structural_diversity": sd,
            "functional_overlap": fo,
            "substitutability": su,
            "status": status,
        }

        return {
            "structural_diversity": sd,
            "functional_overlap": fo,
            "substitutability": su,
            "degeneracy_index": degeneracy_index,
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
        index = result["degeneracy_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "degeneracy_index": index,
            "diagnostics": result["diagnostics"],
        }
