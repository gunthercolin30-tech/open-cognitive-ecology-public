from __future__ import annotations

PRIMITIVE = "structural_continuity"
DESCRIPTION = "Structural continuity."
DEPENDENCIES = []

"""
structural_continuity.py

Formalization of the Structural Continuity concept.

Structural continuity measures whether two successive configurations preserve
the invariant core required for lineage persistence. The concept captures the
idea that transformation is admissible only if enough structural content is
conserved across succession.

Core properties:
- invariant preservation
- continuity ratio computation
- configurable acceptance threshold
- deterministic diagnostics
- compatibility with Minimal DNA
"""


from copy import deepcopy
from typing import Any, Dict, Optional


class StructuralContinuityPrimitive:
    """
    Evaluate whether two structures preserve sufficient continuity.

    Parameters
    ----------
    ancestor:
        Reference structure.
    descendant:
        Successor structure to evaluate.
    threshold:
        Minimum continuity ratio required for validation.
        Must be in the interval [0, 1].
    invariant_keys:
        Optional subset of keys to consider as structural invariants.
        If None, all keys from the ancestor are used.
    """

    def __init__(
        self,
        ancestor: Dict[str, Any],
        descendant: Dict[str, Any],
        threshold: float = 1.0,
        invariant_keys: Optional[list[str]] = None,
    ):
        if not ancestor:
            raise ValueError("Structural continuity requires a non-empty ancestor.")

        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0 and 1.")

        self._ancestor = deepcopy(ancestor)
        self._descendant = deepcopy(descendant)
        self._threshold = float(threshold)

        if invariant_keys is None:
            self._invariant_keys = list(self._ancestor.keys())
        else:
            self._invariant_keys = [key for key in invariant_keys if key in self._ancestor]

        if not self._invariant_keys:
            raise ValueError("At least one invariant key must be defined.")

    # ------------------------------------------------------------------
    # Core metrics
    # ------------------------------------------------------------------

    def preserved_count(self) -> int:
        """
        Number of invariant keys whose values are unchanged.
        """
        count = 0
        for key in self._invariant_keys:
            if self._descendant.get(key) == self._ancestor.get(key):
                count += 1
        return count

    def total_invariants(self) -> int:
        """
        Total number of invariant keys considered.
        """
        return len(self._invariant_keys)

    def continuity_ratio(self) -> float:
        """
        Ratio of preserved invariants.
        """
        return self.preserved_count() / self.total_invariants()

    def is_continuous(self) -> bool:
        """
        True if continuity ratio meets the configured threshold.
        """
        return self.continuity_ratio() >= self._threshold

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> Dict[str, Any]:
        """
        Validate structural continuity and return standardized diagnostics.
        """
        ratio = self.continuity_ratio()
        valid = ratio >= self._threshold

        return {
            "valid": valid,
            "continuity_preserved": valid,
            "preserved_invariants": self.preserved_count(),
            "total_invariants": self.total_invariants(),
            "continuity_ratio": ratio,
            "threshold": self._threshold,
            "diagnostics": {
                "primitive": "STRUCTURAL_CONTINUITY",
                "invariant_keys": deepcopy(self._invariant_keys),
                "status": "continuous" if valid else "discontinuous",
            },
        }

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def structural_signature(self) -> Dict[str, Any]:
        """
        Compact summary of the primitive configuration.
        """
        return {
            "ancestor_size": len(self._ancestor),
            "descendant_size": len(self._descendant),
            "invariant_count": self.total_invariants(),
            "continuity_ratio": self.continuity_ratio(),
            "threshold": self._threshold,
            "continuous": self.is_continuous(),
        }

    def __repr__(self) -> str:
        sig = self.structural_signature()
        return (
            f"StructuralContinuityPrimitive("
            f"invariants={sig['invariant_count']}, "
            f"ratio={sig['continuity_ratio']:.3f}, "
            f"threshold={sig['threshold']:.3f}, "
            f"continuous={sig['continuous']})"
        )
