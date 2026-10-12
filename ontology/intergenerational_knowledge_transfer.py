
"""
N2 — Intergenerational Knowledge Transfer

Superviseur fonctionnel de transfert intergenerationnel de connaissances.

Ce module ne remplace pas memory_transmission_protocol ni
intergenerational_transmission_process. Il agrège leurs signaux en métriques
mesurables : knowledge_transfer_rate, knowledge_retention_score,
knowledge_loss_risk, avec décision gouvernée.
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


@dataclass(frozen=True)
class TransferThresholds:
    healthy: float = 0.74
    warning: float = 0.50


class IntergenerationalKnowledgeTransfer:
    """
    Agrège les signaux de transmission mémorielle, continuité intergénérationnelle,
    rétention symbolique et accès distribué à la connaissance.
    """

    primitive = "INTERGENERATIONAL_KNOWLEDGE_TRANSFER"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "civilizational_memory_archive" / "intergenerational_knowledge_transfer"
        self.thresholds = TransferThresholds()

    def _infer_from_collections(self, inputs: Mapping[str, Any]) -> dict[str, float]:
        source_knowledge = inputs.get("source_knowledge") or inputs.get("source_memory") or []
        transferred_knowledge = inputs.get("transferred_knowledge") or inputs.get("transmitted_memory") or []
        retained_knowledge = inputs.get("retained_knowledge") or inputs.get("retained_memory") or []

        def as_set(v: Any) -> set[str]:
            if isinstance(v, Mapping):
                return {str(k) for k in v.keys()}
            if isinstance(v, (list, tuple, set)):
                return {str(x) for x in v}
            return set()

        source = as_set(source_knowledge)
        transferred = as_set(transferred_knowledge)
        retained = as_set(retained_knowledge)

        if not source:
            return {}

        transfer_rate = len(source & transferred) / len(source)
        retention_score = len(source & retained) / len(source)
        symbolic_integrity = _clamp(inputs.get("symbolic_integrity_score"), default=retention_score)
        continuity_score = _clamp(inputs.get("intergenerational_continuity_score"), default=(transfer_rate + retention_score) / 2.0)

        return {
            "knowledge_transfer_rate": transfer_rate,
            "knowledge_retention_score": retention_score,
            "symbolic_reconstruction_score": symbolic_integrity,
            "continuity_alignment_score": continuity_score,
        }

    def _signals(self, inputs: Mapping[str, Any]) -> dict[str, float]:
        inferred = self._infer_from_collections(inputs)

        transfer = _clamp(
            inputs.get("knowledge_transfer_rate", inferred.get("knowledge_transfer_rate")),
            default=0.82,
        )
        retention = _clamp(
            inputs.get("knowledge_retention_score", inferred.get("knowledge_retention_score")),
            default=0.80,
        )
        symbolic = _clamp(
            inputs.get("symbolic_reconstruction_score", inferred.get("symbolic_reconstruction_score")),
            default=0.78,
        )
        continuity = _clamp(
            inputs.get("continuity_alignment_score", inferred.get("continuity_alignment_score")),
            default=0.81,
        )
        distributed_access = _clamp(inputs.get("distributed_knowledge_access_score"), default=0.79)
        memory_consistency = _clamp(inputs.get("distributed_memory_consistency_score"), default=0.80)
        lineage_integrity = _clamp(inputs.get("lineage_integrity_score"), default=0.82)
        loss_pressure = _clamp(inputs.get("knowledge_loss_pressure"), default=1.0 - _mean([transfer, retention, memory_consistency]))
        fragmentation = _clamp(inputs.get("symbolic_fragmentation_index"), default=1.0 - symbolic)

        return {
            "knowledge_transfer_rate": transfer,
            "knowledge_retention_score": retention,
            "symbolic_reconstruction_score": symbolic,
            "continuity_alignment_score": continuity,
            "distributed_knowledge_access_score": distributed_access,
            "distributed_memory_consistency_score": memory_consistency,
            "lineage_integrity_score": lineage_integrity,
            "knowledge_loss_pressure": loss_pressure,
            "symbolic_fragmentation_index": fragmentation,
        }

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = dict(inputs or {})
        s = self._signals(inputs)

        transfer_components = [
            s["knowledge_transfer_rate"],
            s["distributed_knowledge_access_score"],
            s["continuity_alignment_score"],
        ]
        retention_components = [
            s["knowledge_retention_score"],
            s["distributed_memory_consistency_score"],
            s["symbolic_reconstruction_score"],
            s["lineage_integrity_score"],
        ]
        risk_components = [
            s["knowledge_loss_pressure"],
            s["symbolic_fragmentation_index"],
            1.0 - s["distributed_memory_consistency_score"],
            1.0 - s["knowledge_retention_score"],
        ]

        knowledge_transfer_rate = _mean(transfer_components)
        knowledge_retention_score = _mean(retention_components)
        knowledge_loss_risk = _mean(risk_components)

        intergenerational_transfer_score = _clamp(
            0.38 * knowledge_transfer_rate
            + 0.42 * knowledge_retention_score
            + 0.20 * (1.0 - knowledge_loss_risk)
        )

        if intergenerational_transfer_score >= self.thresholds.healthy and knowledge_loss_risk <= 0.35:
            transfer_state = "knowledge_transfer_healthy"
        elif intergenerational_transfer_score >= self.thresholds.warning and knowledge_loss_risk <= 0.60:
            transfer_state = "knowledge_transfer_warning"
        else:
            transfer_state = "knowledge_transfer_risk"

        recommendations: list[str] = []
        if s["knowledge_transfer_rate"] < 0.55:
            recommendations.append("increase_transfer_bandwidth")
        if s["knowledge_retention_score"] < 0.55:
            recommendations.append("reinforce_retention_protocols")
        if s["symbolic_reconstruction_score"] < 0.55:
            recommendations.append("strengthen_symbolic_reconstruction")
        if knowledge_loss_risk > 0.60:
            recommendations.append("activate_knowledge_loss_mitigation")

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "knowledge_transfer_rate": round(knowledge_transfer_rate, 6),
            "knowledge_retention_score": round(knowledge_retention_score, 6),
            "knowledge_loss_risk": round(knowledge_loss_risk, 6),
            "intergenerational_transfer_score": round(intergenerational_transfer_score, 6),
            "transfer_state": transfer_state,
            "transfer_healthy": transfer_state == "knowledge_transfer_healthy",
            "transfer_warning": transfer_state == "knowledge_transfer_warning",
            "transfer_risk": transfer_state == "knowledge_transfer_risk",
            "signals": {k: round(v, 6) for k, v in s.items()},
            "recommendations": recommendations,
            "diagnostics": {
                "role": "second_level_intergenerational_knowledge_transfer_supervisor",
                "non_redundancy": "aggregates existing memory transmission and continuity primitives without replacing them",
                "dependencies": [
                    "memory_transmission_protocol",
                    "intergenerational_transmission_process",
                    "intergenerational_continuity_metrics",
                    "intergenerational_symbolic_reconstruction",
                    "distributed_civilizational_memory",
                    "distributed_memory_continuity",
                    "distributed_knowledge_access",
                    "genealogical_continuity",
                    "continuity_metrics_engine",
                ],
            },
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_intergenerational_knowledge_transfer.json"
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["report_path"] = str(path)
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        return result
