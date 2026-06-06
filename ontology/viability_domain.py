from __future__ import annotations

PRIMITIVE = "viability_domain"
DESCRIPTION = "Viability domain."
DEPENDENCIES = []

"""
viability_domain.py

Formalization of the Viability Domain concept.

A viability domain is the set of configurations that satisfy a given
constraint function. It defines the region of state space in which
a structure can persist without violating essential constraints.

Core properties:
- deterministic evaluation of admissibility
- batch assessment of candidate configurations
- explicit diagnostics and metrics
- compatibility with Minimal DNA and Structural Continuity
- support for arbitrary user-defined viability predicates
"""


from copy import deepcopy
from typing import Any, Callable, Dict, Iterable, List, Optional


class ViabilityDomainPrimitive:
    """
    Evaluate whether configurations belong to a viability domain.

    Parameters
    ----------
    viability_function:
        Callable receiving a configuration dictionary and returning True
        if the configuration is viable.
    reference_constraints:
        Optional dictionary describing structural constraints used only
        for diagnostics.
    """

    def __init__(
        self,
        viability_function: Callable[[Dict[str, Any]], bool],
        reference_constraints: Optional[Dict[str, Any]] = None,
    ):
        if not callable(viability_function):
            raise ValueError("viability_function must be callable.")

        self._viability_function = viability_function
        self._reference_constraints = deepcopy(reference_constraints or {})

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def is_viable(self, configuration: Dict[str, Any]) -> bool:
        """
        Return True if the configuration belongs to the viability domain.
        """
        try:
            return bool(self._viability_function(deepcopy(configuration)))
        except Exception:
            return False

    def evaluate(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single configuration and return standardized diagnostics.
        """
        viable = self.is_viable(configuration)

        return {
            "valid": viable,
            "in_viability_domain": viable,
            "configuration_size": len(configuration),
            "diagnostics": {
                "primitive": "VIABILITY_DOMAIN",
                "reference_constraint_count": len(self._reference_constraints),
                "status": "viable" if viable else "non_viable",
            },
        }

    # ------------------------------------------------------------------
    # Batch evaluation
    # ------------------------------------------------------------------

    def evaluate_many(
        self,
        configurations: Iterable[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluate multiple configurations.
        """
        results: List[Dict[str, Any]] = []
        viable_count = 0
        total_count = 0

        for configuration in configurations:
            result = self.evaluate(configuration)
            results.append(result)
            total_count += 1
            if result["valid"]:
                viable_count += 1

        viability_ratio = (
            viable_count / total_count if total_count > 0 else 0.0
        )

        return {
            "valid": viable_count > 0,
            "evaluated_configurations": total_count,
            "viable_configurations": viable_count,
            "viability_ratio": viability_ratio,
            "results": results,
            "diagnostics": {
                "primitive": "VIABILITY_DOMAIN",
                "status": "non_empty_domain" if viable_count > 0 else "empty_domain",
            },
        }

    # ------------------------------------------------------------------
    # Domain characterization
    # ------------------------------------------------------------------

    def characterize(
        self,
        sample_configurations: Iterable[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Characterize the sampled viability domain.
        """
        summary = self.evaluate_many(sample_configurations)

        return {
            "valid": summary["valid"],
            "domain_non_empty": summary["viable_configurations"] > 0,
            "evaluated_configurations": summary["evaluated_configurations"],
            "viable_configurations": summary["viable_configurations"],
            "viability_ratio": summary["viability_ratio"],
            "reference_constraint_count": len(self._reference_constraints),
            "diagnostics": summary["diagnostics"],
        }

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def structural_signature(self) -> Dict[str, Any]:
        """
        Return a compact structural signature.
        """
        return {
            "reference_constraint_count": len(self._reference_constraints),
            "callable_defined": True,
        }

    def __repr__(self) -> str:
        sig = self.structural_signature()
        return (
            f"ViabilityDomainPrimitive("
            f"reference_constraints={sig['reference_constraint_count']}, "
            f"callable_defined={sig['callable_defined']})"
        )
