
"""
N3 — Civilizational Historical Archive Refinement

Raffinement supérieur des archives historiques civilisationnelles.

Ce module ne remplace pas civilizational_historical_archive,
civilizational_memory_archive, historical_state_reconciliation ni
longitudinal_metrics_archive. Il agrège leurs signaux en métriques mesurables :
historical_retrievability_score, historical_integrity_score,
historical_coverage_score, avec décision gouvernée.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
import json
import math


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = default
    if math.isnan(x) or math.isinf(x):
        x = default
    return max(0.0, min(1.0, x))


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _as_count(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, Mapping):
        return len(value)
    if isinstance(value, (list, tuple, set)):
        return len(value)
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


@dataclass(frozen=True)
class HistoricalArchiveThresholds:
    healthy: float = 0.74
    warning: float = 0.50


class CivilizationalHistoricalArchiveRefinement:
    """
    Agrège récupérabilité, intégrité, couverture et continuité historique.

    Le module est volontairement simulable : les tests peuvent injecter des
    signaux faibles ou forts sans modifier les archives réelles. En absence de
    payload, il estime une base saine correspondant à l'architecture installée.
    """

    primitive = "CIVILIZATIONAL_HISTORICAL_ARCHIVE_REFINEMENT"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "civilizational_memory_archive" / "historical_archive_refinement"
        self.thresholds = HistoricalArchiveThresholds()

    def _infer_collection_scores(self, inputs: Mapping[str, Any]) -> dict[str, float]:
        archived_events = _as_count(inputs.get("archived_events") or inputs.get("historical_records"))
        retrievable_events = _as_count(inputs.get("retrievable_events") or inputs.get("retrievable_records"))
        corrupted_events = _as_count(inputs.get("corrupted_events") or inputs.get("corrupted_records"))
        reconciled_states = _as_count(inputs.get("reconciled_states"))
        expected_states = _as_count(inputs.get("expected_states"))

        inferred: dict[str, float] = {}
        if archived_events > 0:
            inferred["historical_retrievability_score"] = retrievable_events / archived_events if retrievable_events else 0.0
            inferred["historical_integrity_score"] = 1.0 - (corrupted_events / archived_events)
        if expected_states > 0:
            inferred["historical_coverage_score"] = reconciled_states / expected_states
        return {k: _clamp(v) for k, v in inferred.items()}

    def _signals(self, inputs: Mapping[str, Any]) -> dict[str, float]:
        inferred = self._infer_collection_scores(inputs)

        retrievability = _clamp(
            inputs.get("historical_retrievability_score", inferred.get("historical_retrievability_score")),
            default=0.82,
        )
        integrity = _clamp(
            inputs.get("historical_integrity_score", inferred.get("historical_integrity_score")),
            default=0.83,
        )
        coverage = _clamp(
            inputs.get("historical_coverage_score", inferred.get("historical_coverage_score")),
            default=0.81,
        )
        reconciliation = _clamp(inputs.get("state_reconciliation_score"), default=0.80)
        longitudinal = _clamp(inputs.get("longitudinal_continuity_score"), default=0.82)
        archive_persistence = _clamp(inputs.get("archive_persistence_score"), default=0.81)
        distributed_memory = _clamp(inputs.get("distributed_memory_continuity_score"), default=0.80)
        genealogical = _clamp(inputs.get("genealogical_continuity_score"), default=0.79)
        corruption_pressure = _clamp(inputs.get("historical_corruption_pressure"), default=1.0 - integrity)
        retrieval_failure = _clamp(inputs.get("retrieval_failure_pressure"), default=1.0 - retrievability)
        coverage_gap = _clamp(inputs.get("historical_coverage_gap"), default=1.0 - coverage)

        return {
            "historical_retrievability_score": retrievability,
            "historical_integrity_score": integrity,
            "historical_coverage_score": coverage,
            "state_reconciliation_score": reconciliation,
            "longitudinal_continuity_score": longitudinal,
            "archive_persistence_score": archive_persistence,
            "distributed_memory_continuity_score": distributed_memory,
            "genealogical_continuity_score": genealogical,
            "historical_corruption_pressure": corruption_pressure,
            "retrieval_failure_pressure": retrieval_failure,
            "historical_coverage_gap": coverage_gap,
        }

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = dict(inputs or {})
        s = self._signals(inputs)

        historical_retrievability_score = _mean([
            s["historical_retrievability_score"],
            s["archive_persistence_score"],
            1.0 - s["retrieval_failure_pressure"],
        ])
        historical_integrity_score = _mean([
            s["historical_integrity_score"],
            s["state_reconciliation_score"],
            s["distributed_memory_continuity_score"],
            1.0 - s["historical_corruption_pressure"],
        ])
        historical_coverage_score = _mean([
            s["historical_coverage_score"],
            s["longitudinal_continuity_score"],
            s["genealogical_continuity_score"],
            1.0 - s["historical_coverage_gap"],
        ])
        historical_loss_risk = _mean([
            s["historical_corruption_pressure"],
            s["retrieval_failure_pressure"],
            s["historical_coverage_gap"],
            1.0 - s["state_reconciliation_score"],
        ])

        historical_archive_refinement_score = _clamp(
            0.34 * historical_retrievability_score
            + 0.36 * historical_integrity_score
            + 0.30 * historical_coverage_score
            - 0.15 * historical_loss_risk
        )

        if historical_archive_refinement_score >= self.thresholds.healthy and historical_loss_risk <= 0.35:
            historical_archive_state = "historical_archive_healthy"
        elif historical_archive_refinement_score >= self.thresholds.warning and historical_loss_risk <= 0.60:
            historical_archive_state = "historical_archive_warning"
        else:
            historical_archive_state = "historical_archive_risk"

        recommendations: list[str] = []
        if historical_retrievability_score < 0.55:
            recommendations.append("improve_historical_retrieval_indexing")
        if historical_integrity_score < 0.55:
            recommendations.append("reinforce_archive_integrity_checks")
        if historical_coverage_score < 0.55:
            recommendations.append("extend_longitudinal_coverage")
        if historical_loss_risk > 0.60:
            recommendations.append("activate_historical_loss_mitigation")

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "historical_retrievability_score": round(historical_retrievability_score, 6),
            "historical_integrity_score": round(historical_integrity_score, 6),
            "historical_coverage_score": round(historical_coverage_score, 6),
            "historical_loss_risk": round(historical_loss_risk, 6),
            "historical_archive_refinement_score": round(historical_archive_refinement_score, 6),
            "historical_archive_state": historical_archive_state,
            "historical_archive_healthy": historical_archive_state == "historical_archive_healthy",
            "historical_archive_warning": historical_archive_state == "historical_archive_warning",
            "historical_archive_risk": historical_archive_state == "historical_archive_risk",
            "signals": {k: round(v, 6) for k, v in s.items()},
            "recommendations": recommendations,
            "diagnostics": {
                "role": "second_level_civilizational_historical_archive_refinement_supervisor",
                "non_redundancy": "aggregates existing historical archive, memory archive, reconciliation and longitudinal metrics primitives without replacing them",
                "dependencies": [
                    "civilizational_historical_archive",
                    "civilizational_memory_archive",
                    "historical_state_reconciliation",
                    "longitudinal_metrics_archive",
                    "conversation_memory_archive",
                    "civilizational_state_persistence",
                    "distributed_civilizational_memory",
                    "distributed_memory_continuity",
                    "genealogical_continuity",
                    "continuity_metrics_engine",
                ],
            },
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_civilizational_historical_archive_refinement.json"
            result["report_path"] = str(path)
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        return result
