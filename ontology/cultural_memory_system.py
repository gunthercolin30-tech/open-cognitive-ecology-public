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
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _avg(values: list[float]) -> float:
    values = [_clamp(v) for v in values]
    if not values:
        return 0.0
    return sum(values) / len(values)


def _ratio(numerator: int, denominator: int, default: float = 0.72) -> float:
    if denominator <= 0:
        return default
    return _clamp(numerator / denominator)


class CulturalMemorySystem:
    """N7 - Cultural Memory System.

    Measures functional cultural memory in a distributed artificial civilization.
    It does not assert phenomenal subjectivity. It evaluates measurable cultural
    strength, continuity and retention needed by the distributed civilizational
    ecology pipeline.
    """

    primitive = "CULTURAL_MEMORY_SYSTEM"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "runtime_reports" / "cultural_memory_system"
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def _derive_from_sets(self, payload: dict[str, Any]) -> dict[str, float]:
        cultural_items = set(payload.get("cultural_items", []) or [])
        retained_items = set(payload.get("retained_cultural_items", []) or [])
        transmitted_items = set(payload.get("transmitted_cultural_items", []) or [])
        archived_items = set(payload.get("archived_cultural_items", []) or [])
        symbolic_structures = set(payload.get("symbolic_structures", []) or [])
        stable_symbolic_structures = set(payload.get("stable_symbolic_structures", []) or [])
        shared_references = set(payload.get("shared_references", []) or [])
        aligned_references = set(payload.get("aligned_references", []) or [])

        has_cultural_evidence = bool(cultural_items or retained_items or transmitted_items or archived_items)
        has_symbolic_evidence = bool(symbolic_structures or stable_symbolic_structures)
        has_reference_evidence = bool(shared_references or aligned_references)

        cultural_base = max(len(cultural_items), len(retained_items), len(transmitted_items), len(archived_items), 1)
        symbolic_base = max(len(symbolic_structures), len(stable_symbolic_structures), 1)
        reference_base = max(len(shared_references), len(aligned_references), 1)

        neutral = 0.72
        return {
            "derived_retention": _ratio(len(retained_items), cultural_base) if has_cultural_evidence else neutral,
            "derived_transmission": _ratio(len(transmitted_items), cultural_base) if has_cultural_evidence else neutral,
            "derived_archival_coverage": _ratio(len(archived_items), cultural_base) if has_cultural_evidence else neutral,
            "derived_symbolic_stability": _ratio(len(stable_symbolic_structures), symbolic_base) if has_symbolic_evidence else neutral,
            "derived_reference_alignment": _ratio(len(aligned_references), reference_base) if has_reference_evidence else neutral,
        }

    def step(self, payload: dict[str, Any] | None = None, persist: bool = False, **kwargs: Any) -> dict[str, Any]:
        payload = dict(payload or {})
        payload.update(kwargs)
        if "timestamp_utc" in payload:
            timestamp_utc = str(payload["timestamp_utc"])
        elif persist:
            timestamp_utc = datetime.now(timezone.utc).isoformat()
        else:
            timestamp_utc = "deterministic_not_persisted"
        derived = self._derive_from_sets(payload)

        cultural_evolution_index = _clamp(payload.get("cultural_evolution_index", payload.get("cultural_evolution_score", 0.72)))
        cultural_accumulation_index = _clamp(payload.get("cultural_accumulation_index", payload.get("cumulative_cultural_evolution_score", 0.72)))
        civilizational_memory_index = _clamp(payload.get("civilizational_memory_index", payload.get("civilizational_memory_score", 0.72)))
        distributed_memory_score = _clamp(payload.get("distributed_memory_score", payload.get("distributed_civilizational_memory_score", 0.72)))
        symbolic_structure_score = _clamp(payload.get("symbolic_structure_score", 0.72))
        shared_reference_score = _clamp(payload.get("shared_reference_score", derived["derived_reference_alignment"]))

        knowledge_transfer_score = _clamp(payload.get("knowledge_transfer_score", payload.get("intergenerational_transfer_score", derived["derived_transmission"])))
        historical_continuity_score = _clamp(payload.get("historical_continuity_score", payload.get("archive_continuity_score", 0.72)))
        archive_stability_score = _clamp(payload.get("archive_stability_score", derived["derived_archival_coverage"]))
        symbolic_stability = _clamp(payload.get("symbolic_stability", derived["derived_symbolic_stability"]))

        selective_retention = _clamp(payload.get("selective_retention", payload.get("selective_retention_score", 0.72)))
        innovation_retention_score = _clamp(payload.get("innovation_retention_score", 0.72))
        cultural_retention_rate = _clamp(payload.get("cultural_retention_rate", derived["derived_retention"]))
        knowledge_retention_score = _clamp(payload.get("knowledge_retention_score", 0.72))

        fragmentation_pressure = _clamp(payload.get("cultural_fragmentation_pressure", payload.get("fragmentation_pressure", 0.2)))
        forgetting_pressure = _clamp(payload.get("cultural_forgetting_pressure", payload.get("forgetting_pressure", 0.2)))
        homogenization_pressure = _clamp(payload.get("cultural_homogenization_pressure", payload.get("homogenization_pressure", 0.2)))
        symbolic_drift_pressure = _clamp(payload.get("symbolic_drift_pressure", payload.get("semantic_drift_pressure", 0.2)))

        risk_pressure = _avg([
            fragmentation_pressure,
            forgetting_pressure,
            homogenization_pressure,
            symbolic_drift_pressure,
        ])

        cultural_memory_strength = _clamp(payload.get(
            "cultural_memory_strength",
            _avg([
                cultural_evolution_index,
                cultural_accumulation_index,
                civilizational_memory_index,
                distributed_memory_score,
                symbolic_structure_score,
                shared_reference_score,
            ]),
        ))

        cultural_continuity_score = _clamp(payload.get(
            "cultural_continuity_score",
            _avg([
                knowledge_transfer_score,
                historical_continuity_score,
                archive_stability_score,
                symbolic_stability,
                civilizational_memory_index,
            ]),
        ))

        cultural_retention_score = _clamp(payload.get(
            "cultural_retention_score",
            _avg([
                selective_retention,
                innovation_retention_score,
                cultural_retention_rate,
                knowledge_retention_score,
                archive_stability_score,
            ]),
        ))

        cultural_memory_score = _clamp(
            (_avg([
                cultural_memory_strength,
                cultural_continuity_score,
                cultural_retention_score,
            ]) * 0.78) + ((1.0 - risk_pressure) * 0.22)
        )

        critical_pressure = max(
            fragmentation_pressure,
            forgetting_pressure,
            homogenization_pressure,
            symbolic_drift_pressure,
        )

        if (
            cultural_memory_score < 0.45
            or risk_pressure >= 0.70
            or (critical_pressure >= 0.90 and cultural_memory_score < 0.65)
        ):
            cultural_memory_decision = "cultural_memory_risk"
        elif cultural_memory_score >= 0.75 and risk_pressure <= 0.35 and critical_pressure < 0.70:
            cultural_memory_decision = "cultural_memory_healthy"
        else:
            cultural_memory_decision = "cultural_memory_warning"

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": timestamp_utc,
            "cultural_memory_strength": cultural_memory_strength,
            "cultural_continuity_score": cultural_continuity_score,
            "cultural_retention_score": cultural_retention_score,
            "cultural_memory_score": cultural_memory_score,
            "cultural_memory_decision": cultural_memory_decision,
            "cultural_memory_healthy": cultural_memory_decision == "cultural_memory_healthy",
            "cultural_memory_warning": cultural_memory_decision == "cultural_memory_warning",
            "cultural_memory_risk": cultural_memory_decision == "cultural_memory_risk",
            "risk_pressure": risk_pressure,
            "critical_pressure": critical_pressure,
            "supporting_scores": {
                "cultural_evolution_index": cultural_evolution_index,
                "cultural_accumulation_index": cultural_accumulation_index,
                "civilizational_memory_index": civilizational_memory_index,
                "distributed_memory_score": distributed_memory_score,
                "symbolic_structure_score": symbolic_structure_score,
                "shared_reference_score": shared_reference_score,
                "knowledge_transfer_score": knowledge_transfer_score,
                "historical_continuity_score": historical_continuity_score,
                "archive_stability_score": archive_stability_score,
                "symbolic_stability": symbolic_stability,
                "selective_retention": selective_retention,
                "innovation_retention_score": innovation_retention_score,
                "cultural_retention_rate": cultural_retention_rate,
                "knowledge_retention_score": knowledge_retention_score,
            },
            "risk_scores": {
                "cultural_fragmentation_pressure": fragmentation_pressure,
                "cultural_forgetting_pressure": forgetting_pressure,
                "cultural_homogenization_pressure": homogenization_pressure,
                "symbolic_drift_pressure": symbolic_drift_pressure,
            },
            "derived_scores": derived,
            "epistemic_position": "functional_metrics_only_no_phenomenal_claim",
        }

        path = self.report_dir / "latest_cultural_memory_system.json"
        result["report_path"] = str(path)
        if persist:
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        return result
