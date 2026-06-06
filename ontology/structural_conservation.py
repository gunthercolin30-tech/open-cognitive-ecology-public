from __future__ import annotations

PRIMITIVE = "structural_conservation"
DESCRIPTION = "Structural conservation."
DEPENDENCIES = []

"""
ontology/structural_conservation.py

Computational implementation of the ontological primitive STRUCTURAL_CONSERVATION.

This module formalizes the principle that a system may undergo transformation
while preserving a core subset of structural invariants. The primitive measures
the fraction of reference invariants that remain present after transformation.

The primitive can be used in cognitive, symbolic, ecological, and distributed
constraint-based systems.

Theoretical references
----------------------
- Colin Gunther, Formal Foundations of Constraint-Based Systems.
- Colin Gunther, Existence as a Constraint-Induced Domain.
- Colin Gunther, Physique des intelligences possibles.
"""


from typing import Any, Dict, Iterable, Set


PRIMITIVE_NAME = "STRUCTURAL_CONSERVATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class StructuralConservationPrimitive:
    """
    Ontological primitive measuring preservation of structural invariants.

    Parameters
    ----------
    conservation_threshold:
        Minimum fraction of preserved invariants required to validate
        structural conservation.
    """

    primitive_name = PRIMITIVE_NAME
    maturity_level = MATURITY_LEVEL

    def __init__(
        self,
        conservation_threshold: float = 0.75,
    ) -> None:
        self.conservation_threshold = max(
            0.0,
            min(1.0, float(conservation_threshold)),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_set(
        self,
        invariants: Iterable[str] | None,
    ) -> Set[str]:
        """
        Convert an iterable of invariants into a normalized set of strings.
        """
        if invariants is None:
            return set()

        return {
            str(item).strip()
            for item in invariants
            if str(item).strip()
        }

    # ------------------------------------------------------------------
    # Core computations
    # ------------------------------------------------------------------

    def conservation_score(
        self,
        reference_invariants: Iterable[str],
        current_invariants: Iterable[str],
    ) -> float:
        """
        Compute the fraction of reference invariants that are preserved.

        Returns
        -------
        float
            Preservation score in [0, 1].
        """
        reference = self._to_set(reference_invariants)
        current = self._to_set(current_invariants)

        if not reference:
            return 0.0

        preserved = reference & current

        return len(preserved) / len(reference)

    def preserved_invariants(
        self,
        reference_invariants: Iterable[str],
        current_invariants: Iterable[str],
    ) -> Set[str]:
        """
        Return the set of preserved invariants.
        """
        reference = self._to_set(reference_invariants)
        current = self._to_set(current_invariants)
        return reference & current

    def missing_invariants(
        self,
        reference_invariants: Iterable[str],
        current_invariants: Iterable[str],
    ) -> Set[str]:
        """
        Return the set of lost invariants.
        """
        reference = self._to_set(reference_invariants)
        current = self._to_set(current_invariants)
        return reference - current

    # ------------------------------------------------------------------
    # Simulation API
    # ------------------------------------------------------------------

    def step(
        self,
        reference_invariants: Iterable[str] | None = None,
        current_invariants: Iterable[str] | None = None,
    ) -> Dict[str, Any]:
        """
        Evaluate structural conservation for a given transformation.

        Default invariants correspond to the Minimal DNA of the corpus.
        """
        if reference_invariants is None:
            reference_invariants = {
                "non_closure",
                "real_succession",
                "structural_continuity",
                "viability",
            }

        if current_invariants is None:
            current_invariants = {
                "non_closure",
                "real_succession",
                "structural_continuity",
                "viability",
            }

        reference = self._to_set(reference_invariants)
        current = self._to_set(current_invariants)

        preserved = self.preserved_invariants(
            reference,
            current,
        )

        missing = self.missing_invariants(
            reference,
            current,
        )

        score = self.conservation_score(
            reference,
            current,
        )

        conserved = (
            score >= self.conservation_threshold
        )

        return {
            "reference_count": len(reference),
            "current_count": len(current),
            "preserved_count": len(preserved),
            "missing_count": len(missing),
            "conservation_score": score,
            "conserved": conserved,
            "preserved_invariants": sorted(preserved),
            "missing_invariants": sorted(missing),
        }

    # ------------------------------------------------------------------
    # Scientific validation API
    # ------------------------------------------------------------------

    def validate(
        self,
        reference_invariants: Iterable[str] | None = None,
        current_invariants: Iterable[str] | None = None,
    ) -> Dict[str, Any]:
        """
        Scientific validation entry point.
        """
        result = self.step(
            reference_invariants=reference_invariants,
            current_invariants=current_invariants,
        )

        valid = bool(result["conserved"])

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "maturity_level": MATURITY_LEVEL,
            "reference_constraint_count": result[
                "reference_count"
            ],
            "current_constraint_count": result[
                "current_count"
            ],
            "preserved_count": result[
                "preserved_count"
            ],
            "missing_count": result[
                "missing_count"
            ],
            "conservation_score": result[
                "conservation_score"
            ],
            "conservation_threshold": (
                self.conservation_threshold
            ),
            "preserved_invariants": result[
                "preserved_invariants"
            ],
            "missing_invariants": result[
                "missing_invariants"
            ],
            "status": (
                "structural conservation preserved"
                if valid
                else "structural conservation failure"
            ),
        }

        return {
            "valid": valid,
            "in_viability_domain": valid,
            "configuration_size": result[
                "reference_count"
            ],
            "diagnostics": diagnostics,
        }


if __name__ == "__main__":
    primitive = StructuralConservationPrimitive()

    result = primitive.validate()

    print("STRUCTURAL_CONSERVATION validation")
    print("-" * 60)
    print(f"Valid: {result['valid']}")
    print(f"Maturity: {MATURITY_LEVEL}")
    print()

    for key, value in result["diagnostics"].items():
        print(f"{key:28s}: {value}")
