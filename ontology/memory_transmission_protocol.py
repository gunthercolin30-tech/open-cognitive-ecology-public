from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
STATE_PATH = STATE_DIR / "memory_transmission.json"
HISTORY_PATH = STATE_DIR / "memory_transmission_history.jsonl"
REGISTRY_PATH = STATE_DIR / "representative_registry.json"
READINESS_PATH = STATE_DIR / "succession_readiness.json"
CONSTITUTIONAL_CONTINUITY_PATH = STATE_DIR / "constitutional_continuity.json"
CANDIDATES_PATH = STATE_DIR / "succession_candidates.json"


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if number < 0.0:
        return 0.0
    if number > 1.0:
        return 1.0
    return number


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value, key=lambda x: _canonical_json(x))
    if isinstance(value, dict):
        return list(value.keys())
    return [value]


def _item_identity(item: Any) -> str:
    if isinstance(item, dict):
        for key in ("id", "memory_id", "knowledge_id", "record_id", "name", "key", "title"):
            if key in item:
                return str(item[key])
    return _canonical_json(item)


def _coverage(source_items: list[Any], transferred_items: list[Any]) -> float:
    if not source_items and not transferred_items:
        return 1.0
    if not source_items:
        return 1.0 if transferred_items else 0.0
    source_ids = {_item_identity(x) for x in source_items}
    transferred_ids = {_item_identity(x) for x in transferred_items}
    if not source_ids:
        return 1.0
    return _clamp(len(source_ids & transferred_ids) / len(source_ids))


def _integrity(source_items: list[Any], transferred_items: list[Any]) -> float:
    if not source_items and not transferred_items:
        return 1.0
    source_map = {_item_identity(x): _canonical_json(x) for x in source_items}
    transferred_map = {_item_identity(x): _canonical_json(x) for x in transferred_items}
    if not source_map:
        return 1.0 if transferred_map else 0.0
    common = set(source_map) & set(transferred_map)
    if not common:
        return 0.0
    exact = sum(1 for key in common if source_map[key] == transferred_map[key])
    return _clamp(exact / len(source_map))


def _decision(score: float, loss: float) -> str:
    if score >= 0.92 and loss <= 0.08:
        return "transmission_high_fidelity"
    if score >= 0.75 and loss <= 0.25:
        return "transmission_successful"
    if score >= 0.45 and loss <= 0.55:
        return "transmission_partial"
    return "transmission_failed"


class MemoryTransmissionProtocol:
    '''U7 memory transmission protocol for representative succession.

    This primitive does not claim phenomenal memory transfer. It measures
    functional preservation across an explicit source/target memory set and
    persists a trace suitable for successor readiness and execution layers.
    '''

    primitive = "memory_transmission_protocol"

    def __init__(self, state_dir: Path | None = None) -> None:
        self.state_dir = Path(state_dir) if state_dir else STATE_DIR
        self.state_path = self.state_dir / "memory_transmission.json"
        self.history_path = self.state_dir / "memory_transmission_history.jsonl"

    def _context(self) -> dict[str, Any]:
        registry = _read_json(REGISTRY_PATH, {})
        readiness = _read_json(READINESS_PATH, {})
        constitutional = _read_json(CONSTITUTIONAL_CONTINUITY_PATH, {})
        candidates = _read_json(CANDIDATES_PATH, {})
        current = registry.get("current_representative", {}) if isinstance(registry, dict) else {}
        top_candidate = None
        if isinstance(candidates, dict):
            top_candidate = candidates.get("top_candidate")
        if not top_candidate and isinstance(readiness, dict):
            top_candidate = {"candidate_id": readiness.get("top_candidate_id")}
        return {
            "current_representative_id": current.get("representative_id"),
            "current_representative_name": current.get("representative_name"),
            "source_representative_id": current.get("representative_id"),
            "target_candidate_id": (top_candidate or {}).get("candidate_id") if isinstance(top_candidate, dict) else None,
            "succession_readiness_score": readiness.get("succession_readiness_score") if isinstance(readiness, dict) else None,
            "constitutional_continuity_score": constitutional.get("constitutional_continuity_score") if isinstance(constitutional, dict) else None,
        }

    def step(self, inputs: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if isinstance(inputs, Mapping):
            data.update(dict(inputs))
        data.update(kwargs)

        source_memory = _listify(
            data.get("source_memory")
            or data.get("memory_before")
            or data.get("previous_memory")
            or data.get("source_memory_items")
        )
        transmitted_memory = _listify(
            data.get("transmitted_memory")
            or data.get("memory_after")
            or data.get("target_memory")
            or data.get("transferred_memory_items")
        )
        retained_knowledge = _listify(
            data.get("retained_knowledge")
            or data.get("knowledge_after")
            or data.get("retained_knowledge_items")
        )
        source_knowledge = _listify(
            data.get("source_knowledge")
            or data.get("knowledge_before")
            or data.get("source_knowledge_items")
        )

        explicit_transfer = data.get("memory_transfer_ratio")
        explicit_integrity = data.get("memory_integrity_score")
        explicit_retention = data.get("knowledge_retention_score")

        memory_transfer_ratio = _clamp(explicit_transfer) if explicit_transfer is not None else _coverage(source_memory, transmitted_memory)
        memory_integrity_score = _clamp(explicit_integrity) if explicit_integrity is not None else _integrity(source_memory, transmitted_memory)

        if explicit_retention is not None:
            knowledge_retention_score = _clamp(explicit_retention)
        elif source_knowledge or retained_knowledge:
            knowledge_retention_score = _coverage(source_knowledge, retained_knowledge)
        else:
            knowledge_retention_score = memory_transfer_ratio

        memory_loss_ratio = _clamp(1.0 - memory_transfer_ratio)
        transmission_quality_score = _clamp(
            0.40 * memory_transfer_ratio
            + 0.35 * memory_integrity_score
            + 0.25 * knowledge_retention_score
        )
        transmission_decision = _decision(transmission_quality_score, memory_loss_ratio)

        warnings: list[str] = []
        if memory_transfer_ratio < 0.60:
            warnings.append("memory_transfer_insufficient")
        if memory_integrity_score < 0.70:
            warnings.append("memory_integrity_degraded")
        if knowledge_retention_score < 0.70:
            warnings.append("knowledge_retention_degraded")

        context = self._context()
        timestamp = datetime.now(timezone.utc).isoformat()
        record = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            **context,
            "source_memory_count": len(source_memory),
            "transmitted_memory_count": len(transmitted_memory),
            "source_knowledge_count": len(source_knowledge),
            "retained_knowledge_count": len(retained_knowledge),
            "memory_transfer_ratio": round(memory_transfer_ratio, 6),
            "memory_integrity_score": round(memory_integrity_score, 6),
            "knowledge_retention_score": round(knowledge_retention_score, 6),
            "memory_loss_ratio": round(memory_loss_ratio, 6),
            "transmission_quality_score": round(transmission_quality_score, 6),
            "transmission_decision": transmission_decision,
            "transmission_successful": transmission_decision in {"transmission_successful", "transmission_high_fidelity"},
            "high_fidelity_transmission": transmission_decision == "transmission_high_fidelity",
            "warnings": warnings,
            "diagnostics": {
                "score_formula": "0.40*memory_transfer_ratio + 0.35*memory_integrity_score + 0.25*knowledge_retention_score",
                "methodological_note": "functional memory transmission metrics only; no phenomenal subjectivity asserted",
            },
        }

        self._persist(record)
        return record

    def _persist(self, record: Mapping[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write(chr(10))
