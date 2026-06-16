"""
Multimodal observation archive for Open Cognitive Ecology.

This primitive stores metadata-level multimodal observations produced by
multimodal_perception_engine. It deliberately avoids raw binary persistence by
default in order to preserve storage governance, reversibility, traceability and
non-closure.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import hashlib
import json

PRIMITIVE = "multimodal_observation_archive"
REFINEMENT = "G2-R1-FIX1"


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, _safe_float(value, low)))


def _hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class MultimodalObservationArchive:
    """
    Persist metadata-only multimodal observations.

    The archive is intentionally conservative: it records summaries, modality
    activation, fusion diagnostics and governance fields, but not raw audio,
    image or sensor binaries unless another governed module explicitly handles
    those artifacts later.
    """

    def __init__(self, root: Optional[Path] = None, max_history_bytes: int = 50 * 1024 * 1024) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.archive_dir = self.root / "multimodal_observations"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.archive_dir / "multimodal_observation_history.jsonl"
        self.latest_path = self.archive_dir / "latest_multimodal_observation.json"
        self.state_path = self.archive_dir / "multimodal_observation_archive_state.json"
        self.max_history_bytes = max(1024 * 1024, int(max_history_bytes))

    def _load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "observation_count": 0,
            "rotation_count": 0,
            "latest_observation_id": None,
            "latest_timestamp_utc": None,
        }

    def _save_state(self, state: Dict[str, Any]) -> None:
        state["primitive"] = PRIMITIVE
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _rotate_if_needed(self) -> None:
        try:
            if not self.history_path.exists() or self.history_path.stat().st_size <= self.max_history_bytes:
                return
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            rotated = self.archive_dir / f"multimodal_observation_history_{stamp}.jsonl"
            self.history_path.rename(rotated)
            state = self._load_state()
            state["rotation_count"] = _safe_int(state.get("rotation_count")) + 1
            self._save_state(state)
        except Exception:
            pass

    def _append(self, record: Dict[str, Any]) -> None:
        self._rotate_if_needed()
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\\n")
        self.latest_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _normalise_record(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        record = dict(observation)
        record.setdefault("primitive", PRIMITIVE)
        record.setdefault("refinement", REFINEMENT)
        record.setdefault("timestamp_utc", _utc())
        record.setdefault("observation_id", "MMO-" + _hash(record))
        record.setdefault("archival_scope", "metadata_and_summary_only")
        record.setdefault("raw_binary_stored", False)
        record.setdefault("reversible", True)
        record.setdefault("non_closure_compliant", True)
        record.setdefault("storage_governed", True)
        return record

    def step(self, observation: Optional[Dict[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        observation = dict(observation or {})
        state = self._load_state()
        record = self._normalise_record(observation)

        if persist:
            self._append(record)
            state["observation_count"] = _safe_int(state.get("observation_count")) + 1
            state["latest_observation_id"] = record.get("observation_id")
            state["latest_timestamp_utc"] = record.get("timestamp_utc")
            self._save_state(state)
        else:
            state["observation_count"] = _safe_int(state.get("observation_count"))

        modality_summary = record.get("modality_summary", {})
        if not isinstance(modality_summary, dict):
            modality_summary = {}
        active_modalities = [
            key for key, value in modality_summary.items()
            if isinstance(value, dict) and bool(value.get("active"))
        ]
        modality_count = len(modality_summary)
        active_count = len(active_modalities)
        archive_completeness = 1.0 if persist else 0.5
        if modality_count:
            archive_completeness = (archive_completeness + active_count / modality_count) / 2.0

        return {
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "success": True,
            "timestamp_utc": _utc(),
            "observation_id": record.get("observation_id"),
            "observation_archived": bool(persist),
            "multimodal_observation_count": state.get("observation_count", 0),
            "active_modalities": active_modalities,
            "active_modality_count": active_count,
            "archive_completeness_score": _clamp(archive_completeness),
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
            "state_path": str(self.state_path),
            "raw_binary_stored": False,
            "reversible": True,
            "non_closure_compliant": True,
            "diagnostics": {
                "schema_version": "G2.multimodal_observation_archive.v1",
                "archival_scope": "metadata_and_summary_only",
                "storage_directory": str(self.archive_dir),
                "history_path": str(self.history_path),
                "latest_path": str(self.latest_path),
                "state_path": str(self.state_path),
            },
        }
