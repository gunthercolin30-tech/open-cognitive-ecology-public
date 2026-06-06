from __future__ import annotations

PRIMITIVE = "structural_attractor"
DESCRIPTION = "Structural attractor."
DEPENDENCIES = []

"""Structural attractor primitive.

This module formalizes structural attractors toward which successive
constraint-driven transitions converge. A structural attractor is not a
predefined final state, but a locally emergent region of the configuration
space that recurrently captures viable trajectories while exhibiting
high coherence and low instability.

For each configuration i:

    attractor_strength(i) =
        visitation_frequencies(i)
        * coherence_levels(i)
        * (1 - instability_levels(i))

The dominant configuration is the one maximizing attractor strength.
A structural attractor exists when the maximal attractor strength exceeds
(or equals) a persistence threshold.
"""


from typing import Any, Dict, Mapping, Optional, Set


class StructuralAttractor:
    """Detects structural attractors in a constrained configuration space."""

    PRIMITIVE_NAME = "STRUCTURAL_ATTRACTOR"
    MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"

    def __init__(self, persistence_threshold: float = 0.5) -> None:
        self.persistence_threshold = self._clamp(persistence_threshold)

    @staticmethod
    def _clamp(value: float) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = 0.0

        if numeric < 0.0:
            return 0.0
        if numeric > 1.0:
            return 1.0
        return numeric

    @staticmethod
    def _all_keys(*mappings: Mapping[str, float]) -> Set[str]:
        keys: Set[str] = set()
        for mapping in mappings:
            keys.update(mapping.keys())
        return keys

    def evaluate(
        self,
        visitation_frequencies: Mapping[str, float],
        coherence_levels: Mapping[str, float],
        instability_levels: Mapping[str, float],
    ) -> Dict[str, Any]:
        keys = self._all_keys(
            visitation_frequencies,
            coherence_levels,
            instability_levels,
        )

        if not keys:
            diagnostics = {
                "primitive": self.PRIMITIVE_NAME,
                "configuration_count": 0,
                "persistence_threshold": self.persistence_threshold,
                "dominant_configuration": None,
                "status": "no_attractor",
            }
            return {
                "attractor_strengths": {},
                "dominant_configuration": None,
                "persistence_score": 0.0,
                "structural_attractor_exists": False,
                "diagnostics": diagnostics,
            }

        attractor_strengths: Dict[str, float] = {}

        for key in keys:
            visitation = self._clamp(visitation_frequencies.get(key, 0.0))
            coherence = self._clamp(coherence_levels.get(key, 0.0))
            instability = self._clamp(instability_levels.get(key, 0.0))

            strength = visitation * coherence * (1.0 - instability)
            attractor_strengths[key] = self._clamp(strength)

        dominant_configuration: Optional[str] = max(
            attractor_strengths,
            key=attractor_strengths.get,
        )

        persistence_score = attractor_strengths[dominant_configuration]
        structural_attractor_exists = (
            persistence_score >= self.persistence_threshold
        )

        diagnostics = {
            "primitive": self.PRIMITIVE_NAME,
            "configuration_count": len(keys),
            "persistence_threshold": self.persistence_threshold,
            "dominant_configuration": dominant_configuration,
            "status": (
                "attractor_detected"
                if structural_attractor_exists
                else "no_attractor"
            ),
        }

        return {
            "attractor_strengths": attractor_strengths,
            "dominant_configuration": dominant_configuration,
            "persistence_score": persistence_score,
            "structural_attractor_exists": structural_attractor_exists,
            "diagnostics": diagnostics,
        }

    def step(
        self,
        visitation_frequencies: Mapping[str, float],
        coherence_levels: Mapping[str, float],
        instability_levels: Mapping[str, float],
    ) -> Dict[str, Any]:
        return self.evaluate(
            visitation_frequencies,
            coherence_levels,
            instability_levels,
        )

    def validate(
        self,
        visitation_frequencies: Mapping[str, float],
        coherence_levels: Mapping[str, float],
        instability_levels: Mapping[str, float],
    ) -> Dict[str, Any]:
        result = self.evaluate(
            visitation_frequencies,
            coherence_levels,
            instability_levels,
        )

        return {
            "valid": result["structural_attractor_exists"],
            "structural_attractor_exists": result[
                "structural_attractor_exists"
            ],
            "dominant_configuration": result[
                "dominant_configuration"
            ],
            "persistence_score": result["persistence_score"],
            "diagnostics": result["diagnostics"],
        }
