from __future__ import annotations

PRIMITIVE = "structural_transition_operator"
DESCRIPTION = "Structural transition operator."
DEPENDENCIES = []


from typing import Any, Callable, Dict, Iterable, List, Optional


class StructuralTransitionOperatorPrimitive:
    """
    STRUCTURAL_TRANSITION_OPERATOR

    Transforme une configuration instable en une nouvelle configuration viable
    en sélectionnant la meilleure transformation candidate selon :
    - la viabilité du résultat,
    - la conservation de l'ADN minimal.
    """

    PRIMITIVE_NAME = "STRUCTURAL_TRANSITION_OPERATOR"
    MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"

    def __init__(
        self,
        viability_threshold: float = 0.5,
        alpha: float = 0.5,
        beta: float = 0.5,
    ) -> None:
        self.viability_threshold = float(viability_threshold)
        self.alpha = float(alpha)
        self.beta = float(beta)

    @staticmethod
    def _extract_features(configuration: Any) -> set:
        if configuration is None:
            return set()
        if isinstance(configuration, dict):
            return set(configuration.keys())
        if isinstance(configuration, (list, tuple, set)):
            return set(configuration)
        return {configuration}

    def _dna_preservation_score(
        self,
        original_configuration: Any,
        transformed_configuration: Any,
        minimal_dna: Optional[Iterable[Any]],
    ) -> float:
        if minimal_dna is None:
            return 1.0

        dna = set(minimal_dna)
        if not dna:
            return 1.0

        transformed_features = self._extract_features(transformed_configuration)
        conserved = len(dna & transformed_features)
        return conserved / len(dna)

    def _viability_score(
        self,
        transformed_configuration: Any,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> float:
        if transformed_configuration is None:
            return 0.0

        if isinstance(transformed_configuration, dict):
            if "viability_score" in transformed_configuration:
                try:
                    return max(
                        0.0,
                        min(1.0, float(transformed_configuration["viability_score"])),
                    )
                except (TypeError, ValueError):
                    return 0.0

            if transformed_configuration.get("valid") is False:
                return 0.0

        return 1.0

    def _apply_transformation(
        self,
        configuration: Any,
        transformation: Callable[[Any], Any],
    ) -> Any:
        return transformation(configuration)

    def step(
        self,
        configuration: Any,
        instability_measure: float,
        critical_threshold: float,
        candidate_transformations: Optional[List[Callable[[Any], Any]]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        minimal_dna: Optional[Iterable[Any]] = None,
    ) -> Dict[str, Any]:
        candidate_transformations = candidate_transformations or []

        if instability_measure < critical_threshold:
            return {
                "transition_triggered": False,
                "selected_transformation": None,
                "transformed_configuration": configuration,
                "viability_score": self._viability_score(configuration, constraints),
                "dna_preservation_score": 1.0,
                "transition_success": False,
                "diagnostics": {
                    "primitive": self.PRIMITIVE_NAME,
                    "reason": "instability_below_threshold",
                    "instability_measure": instability_measure,
                    "critical_threshold": critical_threshold,
                    "status": "stable",
                },
            }

        if not candidate_transformations:
            return {
                "transition_triggered": True,
                "selected_transformation": None,
                "transformed_configuration": configuration,
                "viability_score": 0.0,
                "dna_preservation_score": 1.0,
                "transition_success": False,
                "diagnostics": {
                    "primitive": self.PRIMITIVE_NAME,
                    "reason": "no_candidate_transformations",
                    "status": "failed",
                },
            }

        best = None

        for transformation in candidate_transformations:
            transformed = self._apply_transformation(configuration, transformation)
            viability = self._viability_score(transformed, constraints)
            dna_score = self._dna_preservation_score(
                configuration,
                transformed,
                minimal_dna,
            )
            aggregate = self.alpha * viability + self.beta * dna_score

            candidate = {
                "transformation": transformation,
                "transformed_configuration": transformed,
                "viability_score": viability,
                "dna_preservation_score": dna_score,
                "aggregate_score": aggregate,
            }

            if best is None or candidate["aggregate_score"] > best["aggregate_score"]:
                best = candidate

        transition_success = (
            best is not None
            and best["viability_score"] >= self.viability_threshold
        )

        return {
            "transition_triggered": True,
            "selected_transformation": best["transformation"] if best else None,
            "transformed_configuration": (
                best["transformed_configuration"] if best else configuration
            ),
            "viability_score": best["viability_score"] if best else 0.0,
            "dna_preservation_score": (
                best["dna_preservation_score"] if best else 1.0
            ),
            "transition_success": transition_success,
            "diagnostics": {
                "primitive": self.PRIMITIVE_NAME,
                "instability_measure": instability_measure,
                "critical_threshold": critical_threshold,
                "candidate_count": len(candidate_transformations),
                "aggregate_score": best["aggregate_score"] if best else 0.0,
                "status": (
                    "transition_success"
                    if transition_success
                    else "transition_failed"
                ),
            },
        }

    def validate(self, configuration: Any, **kwargs: Any) -> Dict[str, Any]:
        result = self.step(configuration=configuration, **kwargs)
        return {
            "valid": bool(result["transition_success"]),
            "transition_success": bool(result["transition_success"]),
            "diagnostics": result["diagnostics"],
        }
