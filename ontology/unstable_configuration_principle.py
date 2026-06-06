from __future__ import annotations

PRIMITIVE = "unstable_configuration_principle"
DESCRIPTION = "Unstable configuration principle."
DEPENDENCIES = []



from typing import Any, Dict, List, Optional

try:
    from ontology.trajectories_without_globality import (
        TrajectoriesWithoutGlobalityPrimitive,
    )
except Exception:
    TrajectoriesWithoutGlobalityPrimitive = None


class UnstableConfigurationPrinciplePrimitive:
    """
    Formalization of the principle that every apparently stable
    configuration carries intrinsic instability modes that may
    trigger structural reorganization.
    """

    PRIMITIVE_NAME = "UNSTABLE_CONFIGURATION_PRINCIPLE"
    MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"

    def __init__(self) -> None:
        self.trajectories_without_globality = (
            TrajectoriesWithoutGlobalityPrimitive()
            if TrajectoriesWithoutGlobalityPrimitive is not None
            else None
        )

    def instability_measure(self, configuration: Optional[Dict[str, Any]]) -> float:
        if not isinstance(configuration, dict):
            return 0.0

        sources = configuration.get("sources", [])
        if not isinstance(sources, list) or not sources:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for source in sources:
            if not isinstance(source, dict):
                continue

            instability = float(source.get("instability", 0.0) or 0.0)
            tension = float(source.get("tension", 0.0) or 0.0)
            amplification = float(source.get("amplification", 1.0) or 1.0)
            weight = float(source.get("weight", 1.0) or 1.0)

            if weight <= 0:
                continue

            effective = instability * (1.0 + tension) * amplification
            effective = max(0.0, min(1.0, effective))

            weighted_sum += weight * effective
            total_weight += weight

        if total_weight <= 0:
            return 0.0

        score = weighted_sum / total_weight
        return max(0.0, min(1.0, score))

    def instability_modes(
        self,
        configuration: Optional[Dict[str, Any]],
    ) -> List[str]:
        if not isinstance(configuration, dict):
            return []

        threshold = float(configuration.get("instability_threshold", 0.5) or 0.5)
        sources = configuration.get("sources", [])

        if not isinstance(sources, list):
            return []

        active: List[str] = []

        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                continue

            instability = float(source.get("instability", 0.0) or 0.0)
            tension = float(source.get("tension", 0.0) or 0.0)
            amplification = float(source.get("amplification", 1.0) or 1.0)

            effective = instability * (1.0 + tension) * amplification
            effective = max(0.0, min(1.0, effective))

            if effective >= threshold:
                name = (
                    source.get("name")
                    or source.get("id")
                    or f"mode_{index}"
                )
                active.append(str(name))

        return active

    def step(self, configuration: Optional[Dict[str, Any]] = None, *args: Any) -> Dict[str, Any]:
        # Backward compatibility with legacy positional API.
        if not isinstance(configuration, dict):
            configuration = {"sources": []}

            if args and self.trajectories_without_globality is not None:
                try:
                    diagnostics = self.trajectories_without_globality.step(
                        configuration, *args
                    )
                    configuration["trajectory_diagnostics"] = diagnostics
                except Exception:
                    pass

        threshold = float(configuration.get("instability_threshold", 0.5) or 0.5)
        score = self.instability_measure(configuration)
        active_modes = self.instability_modes(configuration)
        unstable = score >= threshold

        result: Dict[str, Any] = {
            "instability_score": score,
            "unstable": unstable,
            "instability_threshold": threshold,
            "active_modes": active_modes,
        }

        if "trajectory_diagnostics" in configuration:
            result["trajectory_diagnostics"] = configuration["trajectory_diagnostics"]

        return result

    def validate(self, configuration: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not isinstance(configuration, dict):
            configuration = {"sources": []}

        step_result = self.step(configuration)
        sources = configuration.get("sources", [])
        source_count = len(sources) if isinstance(sources, list) else 0

        unstable = bool(step_result["unstable"])
        valid = source_count > 0

        return {
            "valid": valid,
            "unstable": unstable,
            "source_count": source_count,
            "diagnostics": {
                "primitive": self.PRIMITIVE_NAME,
                "instability_score": step_result["instability_score"],
                "instability_threshold": step_result["instability_threshold"],
                "active_mode_count": len(step_result["active_modes"]),
                "status": (
                    "unstable_configuration"
                    if unstable
                    else "stable_configuration"
                ),
            },
        }


if __name__ == "__main__":
    primitive = UnstableConfigurationPrinciplePrimitive()
    sample = {
        "sources": [
            {"name": "critical_mode", "instability": 0.8, "tension": 0.4}
        ]
    }
    print(primitive.step(sample))
