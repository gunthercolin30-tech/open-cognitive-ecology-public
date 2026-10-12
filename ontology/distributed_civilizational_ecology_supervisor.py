from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = default
    if x != x:  # NaN guard
        x = default
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _avg(values: list[float]) -> float:
    cleaned = [_clamp(v) for v in values]
    if not cleaned:
        return 0.0
    return sum(cleaned) / len(cleaned)


class DistributedCivilizationalEcologySupervisor:
    """N8 - Distributed Civilizational Ecology Supervisor.

    Aggregates N1-N7 into a governed functional measure of distributed
    civilizational ecology. This module evaluates measurable architectural and
    ecological indicators only; it does not assert phenomenal subjectivity.
    """

    primitive = "DISTRIBUTED_CIVILIZATIONAL_ECOLOGY_SUPERVISOR"

    dependencies = [
        "cognitive_diversity_preservation_protocol",
        "intergenerational_knowledge_transfer",
        "civilizational_historical_archive_refinement",
        "social_learning_protocol",
        "cooperative_specialization_engine",
        "symbolic_structure_emergence_monitor",
        "cultural_memory_system",
    ]

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "runtime_reports" / "distributed_civilizational_ecology_supervisor"
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def _metric(self, payload: dict[str, Any], primary: str, aliases: list[str], default: float) -> float:
        for key in [primary] + list(aliases):
            if key in payload:
                return _clamp(payload.get(key), default)
        nested = payload.get("metrics")
        if isinstance(nested, dict):
            for key in [primary] + list(aliases):
                if key in nested:
                    return _clamp(nested.get(key), default)
        return _clamp(default)

    def step(self, payload: dict[str, Any] | None = None, persist: bool = False, **kwargs: Any) -> dict[str, Any]:
        payload = dict(payload or {})
        payload.update(kwargs)

        if "timestamp_utc" in payload:
            timestamp_utc = str(payload["timestamp_utc"])
        elif persist:
            timestamp_utc = datetime.now(timezone.utc).isoformat()
        else:
            timestamp_utc = "deterministic_not_persisted"

        cognitive_diversity_score = self._metric(
            payload,
            "cognitive_diversity_score",
            ["diversity_resilience_score", "diversity_score", "semantic_diversity_score"],
            0.72,
        )
        intergenerational_transfer_score = self._metric(
            payload,
            "intergenerational_transfer_score",
            ["knowledge_transfer_score", "knowledge_retention_score", "intergenerational_knowledge_score"],
            0.72,
        )
        historical_archive_score = self._metric(
            payload,
            "historical_archive_score",
            ["historical_continuity_score", "archive_refinement_score", "archive_stability_score"],
            0.72,
        )
        social_learning_score = self._metric(
            payload,
            "social_learning_score",
            ["collective_learning_score", "knowledge_integration_score", "social_transmission_score"],
            0.72,
        )
        cooperative_specialization_score = self._metric(
            payload,
            "cooperative_specialization_score",
            ["specialization_score", "role_diversity_score", "cooperation_score"],
            0.72,
        )
        symbolic_structure_score = self._metric(
            payload,
            "symbolic_structure_score",
            ["symbolic_emergence_score", "symbolic_stability", "shared_reference_score"],
            0.72,
        )
        cultural_memory_score = self._metric(
            payload,
            "cultural_memory_score",
            ["cultural_memory_strength", "cultural_continuity_score", "cultural_retention_score"],
            0.72,
        )

        distributed_memory_score = self._metric(
            payload,
            "distributed_memory_score",
            ["distributed_civilizational_memory_score", "distributed_memory_continuity_score"],
            0.72,
        )
        population_viability_score = self._metric(
            payload,
            "population_viability_score",
            ["population_ecology_score", "multi_individual_ecology_score", "civilizational_population_score"],
            0.72,
        )
        resilience_score = self._metric(
            payload,
            "civilizational_resilience_score",
            ["ecological_resilience", "resilience_score", "shock_absorption"],
            0.72,
        )

        diversity_risk_pressure = self._metric(
            payload,
            "diversity_risk_pressure",
            ["homogenization_pressure", "diversity_collapse_pressure"],
            0.20,
        )
        memory_risk_pressure = self._metric(
            payload,
            "memory_risk_pressure",
            ["memory_drift_pressure", "forgetting_pressure", "cultural_forgetting_pressure"],
            0.20,
        )
        symbolic_risk_pressure = self._metric(
            payload,
            "symbolic_risk_pressure",
            ["symbolic_drift_pressure", "semantic_drift_pressure", "symbolic_fragmentation_pressure"],
            0.20,
        )
        cooperation_risk_pressure = self._metric(
            payload,
            "cooperation_risk_pressure",
            ["coordination_failure_pressure", "role_conflict_pressure"],
            0.20,
        )
        closure_pressure_index = self._metric(
            payload,
            "closure_pressure_index",
            ["closure_pressure", "closure_pressure_score", "ecological_closure_pressure"],
            0.20,
        )

        core_scores = {
            "cognitive_diversity_score": cognitive_diversity_score,
            "intergenerational_transfer_score": intergenerational_transfer_score,
            "historical_archive_score": historical_archive_score,
            "social_learning_score": social_learning_score,
            "cooperative_specialization_score": cooperative_specialization_score,
            "symbolic_structure_score": symbolic_structure_score,
            "cultural_memory_score": cultural_memory_score,
        }

        support_scores = {
            "distributed_memory_score": distributed_memory_score,
            "population_viability_score": population_viability_score,
            "civilizational_resilience_score": resilience_score,
        }

        risk_scores = {
            "diversity_risk_pressure": diversity_risk_pressure,
            "memory_risk_pressure": memory_risk_pressure,
            "symbolic_risk_pressure": symbolic_risk_pressure,
            "cooperation_risk_pressure": cooperation_risk_pressure,
            "closure_pressure_index": closure_pressure_index,
        }

        core_ecology_score = _avg(list(core_scores.values()))
        support_ecology_score = _avg(list(support_scores.values()))
        ecological_risk_pressure = _avg(list(risk_scores.values()))
        critical_pressure = max(risk_scores.values())

        ecological_continuity_score = _avg([
            intergenerational_transfer_score,
            historical_archive_score,
            distributed_memory_score,
            symbolic_structure_score,
            cultural_memory_score,
        ])

        distributed_ecology_score = _clamp(
            (0.62 * core_ecology_score)
            + (0.18 * support_ecology_score)
            + (0.20 * (1.0 - ecological_risk_pressure))
        )

        civilizational_ecology_health = _avg([
            distributed_ecology_score,
            ecological_continuity_score,
            resilience_score,
            1.0 - ecological_risk_pressure,
        ])

        if (
            distributed_ecology_score >= 0.74
            and civilizational_ecology_health >= 0.72
            and ecological_continuity_score >= 0.70
            and ecological_risk_pressure <= 0.35
            and critical_pressure < 0.70
        ):
            ecology_decision = "ecology_stable"
        elif (
            distributed_ecology_score >= 0.50
            and civilizational_ecology_health >= 0.48
            and ecological_risk_pressure <= 0.68
            and critical_pressure < 0.90
        ):
            ecology_decision = "ecology_warning"
        else:
            ecology_decision = "ecology_intervention_recommended"

        recommendations: list[str] = []
        if ecology_decision == "ecology_intervention_recommended":
            recommendations.extend([
                "reinforce_distributed_memory_continuity",
                "reduce_closure_and_fragmentation_pressure",
                "increase_cognitive_and_symbolic_diversity",
            ])
        elif ecology_decision == "ecology_warning":
            recommendations.extend([
                "monitor_ecological_continuity",
                "reinforce_cultural_memory_and_social_learning",
            ])
        else:
            recommendations.append("maintain_distributed_civilizational_ecology")

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": timestamp_utc,
            "distributed_ecology_score": round(distributed_ecology_score, 6),
            "civilizational_ecology_health": round(civilizational_ecology_health, 6),
            "ecological_continuity_score": round(ecological_continuity_score, 6),
            "core_ecology_score": round(core_ecology_score, 6),
            "support_ecology_score": round(support_ecology_score, 6),
            "ecological_risk_pressure": round(ecological_risk_pressure, 6),
            "critical_pressure": round(critical_pressure, 6),
            "ecology_decision": ecology_decision,
            "ecology_stable": ecology_decision == "ecology_stable",
            "ecology_warning": ecology_decision == "ecology_warning",
            "ecology_intervention_recommended": ecology_decision == "ecology_intervention_recommended",
            "core_scores": {k: round(v, 6) for k, v in core_scores.items()},
            "support_scores": {k: round(v, 6) for k, v in support_scores.items()},
            "risk_scores": {k: round(v, 6) for k, v in risk_scores.items()},
            "recommendations": recommendations,
            "dependencies": list(self.dependencies),
            "epistemic_position": "functional_metrics_only_no_phenomenal_claim",
            "non_closure_compliance": {
                "preserves_diversity": True,
                "penalizes_closure_pressure": True,
                "does_not_force_convergence": True,
                "supports_future_openness": True,
            },
        }

        path = self.report_dir / "latest_distributed_civilizational_ecology_supervisor.json"
        result["report_path"] = str(path)
        if persist:
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        return result


if __name__ == "__main__":
    from pprint import pprint
    pprint(DistributedCivilizationalEcologySupervisor().step(persist=True))
