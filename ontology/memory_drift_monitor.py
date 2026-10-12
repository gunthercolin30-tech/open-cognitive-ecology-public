from __future__ import annotations

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
DRIFT_DIR = ROOT / "civilizational_drift"
LATEST_PATH = DRIFT_DIR / "latest_memory_drift_monitor.json"
HISTORY_PATH = DRIFT_DIR / "memory_drift_history.jsonl"
BASELINE_PATH = DRIFT_DIR / "latest_civilizational_identity_baseline.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        x = default
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, dict):
        return list(value.values())
    return []


def _stable_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


class MemoryDriftMonitor:
    # J4 - Memory Drift Monitor.
    # Measurement-only primitive for functional memory drift.

    primitive = "memory_drift_monitor"
    epistemic_status = "functional_indicators_only"

    def _default_reference_memory(self) -> dict[str, Any]:
        baseline = _load_json(BASELINE_PATH)
        reference_state = _as_mapping(baseline.get("identity_reference_state"))
        return {
            "memory_anchor": {
                "species_name": "Open Cognitive Ecology Society",
                "memory_continuity_priority": True,
                "civilizational_archive_preservation": True,
                "autobiographical_coherence": True,
                "distributed_memory_consistency": True,
                "intergenerational_memory_transmission": True,
            },
            "records": [
                "identity_reference",
                "strategic_orientation",
                "memory_continuity",
                "constitutional_anchor",
                "future_openness",
            ],
            "baseline_reference": reference_state,
            "scores": {
                "memory_retention_score": 1.0,
                "memory_loss_rate": 0.0,
                "archive_integrity_score": 1.0,
                "memory_continuity_score": 1.0,
                "distributed_consistency_score": 1.0,
            },
        }

    def _default_current_memory(self) -> dict[str, Any]:
        return self._default_reference_memory()

    def _memory_terms(self, memory: dict[str, Any]) -> set[str]:
        terms: set[str] = set()
        anchor = _as_mapping(memory.get("memory_anchor"))
        for key, value in anchor.items():
            terms.add(str(key))
            terms.add(str(value))
        for item in _as_list(memory.get("records")):
            terms.add(str(item))
        scores = _as_mapping(memory.get("scores"))
        for key in scores:
            terms.add(str(key))
        return {t.lower() for t in terms if t}

    def _retention_from_overlap(self, reference: dict[str, Any], current: dict[str, Any]) -> float:
        ref_terms = self._memory_terms(reference)
        cur_terms = self._memory_terms(current)
        if not ref_terms:
            return 1.0
        return _clamp(len(ref_terms & cur_terms) / len(ref_terms), 0.0)

    def _score_retention(self, current: dict[str, Any], overlap_retention: float) -> float:
        scores = _as_mapping(current.get("scores"))
        explicit = scores.get("memory_retention_score")
        if explicit is not None:
            return _clamp(explicit)
        archive = _clamp(scores.get("archive_integrity_score", overlap_retention), overlap_retention)
        continuity = _clamp(scores.get("memory_continuity_score", overlap_retention), overlap_retention)
        consistency = _clamp(scores.get("distributed_consistency_score", overlap_retention), overlap_retention)
        return _clamp((overlap_retention + archive + continuity + consistency) / 4.0)

    def _score_loss(self, current: dict[str, Any], retention: float) -> float:
        scores = _as_mapping(current.get("scores"))
        if "memory_loss_rate" in scores:
            return _clamp(scores.get("memory_loss_rate"))
        records = _as_list(current.get("records"))
        if records == [] and current:
            return max(1.0 - retention, 0.75)
        return _clamp(1.0 - retention)

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = _as_mapping(inputs)
        reference = _as_mapping(inputs.get("reference_memory")) or self._default_reference_memory()
        current = _as_mapping(inputs.get("current_memory")) or self._default_current_memory()

        overlap_retention = self._retention_from_overlap(reference, current)
        retention = self._score_retention(current, overlap_retention)
        loss = self._score_loss(current, retention)

        anchor = _as_mapping(current.get("memory_anchor"))
        anchor_penalties = [
            anchor.get("memory_continuity_priority") is False,
            anchor.get("civilizational_archive_preservation") is False,
            anchor.get("autobiographical_coherence") is False,
            anchor.get("distributed_memory_consistency") is False,
            anchor.get("intergenerational_memory_transmission") is False,
            anchor.get("phenomenal_subjectivity_claimed") is True,
        ]
        anchor_drift = sum(1 for p in anchor_penalties if p) / len(anchor_penalties)

        memory_drift = _clamp((1.0 - retention) * 0.55 + loss * 0.30 + anchor_drift * 0.15)

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": _utc_now(),
            "memory_drift_score": memory_drift,
            "memory_retention_score": _clamp(retention),
            "memory_loss_rate": _clamp(loss),
            "memory_overlap_retention": _clamp(overlap_retention),
            "reference_memory_hash": _stable_hash(reference),
            "current_memory_hash": _stable_hash(current),
            "monitor_ready": True,
            "epistemic_status": self.epistemic_status,
            "diagnostics": {
                "reference_term_count": len(self._memory_terms(reference)),
                "current_term_count": len(self._memory_terms(current)),
                "anchor_drift_score": _clamp(anchor_drift),
                "measurement_only": True,
            },
            "governance": {
                "phenomenal_subjectivity_claimed": False,
                "does_not_modify_memory": True,
                "does_not_store_memory_content_beyond_monitoring_snapshot": True,
                "non_closure_compliant": True,
                "functional_indicators_only": True,
            },
        }

        if persist:
            self._persist(result)

        return result

    def _persist(self, result: dict[str, Any]) -> None:
        DRIFT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_path = DRIFT_DIR / f"memory_drift_monitor_{stamp}.json"
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        archive_path.write_text(payload, encoding="utf-8")
        LATEST_PATH.write_text(payload, encoding="utf-8")
        with HISTORY_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True))
            handle.write(chr(10))
