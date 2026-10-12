from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json


ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
STATE_PATH = STATE_DIR / "representative_lineage_registry.json"
HISTORY_PATH = STATE_DIR / "representative_lineage_history.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except Exception:
        v = default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _stable_id(prefix: str, payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _extract_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    event = payload.get("succession_event") or payload.get("succession_execution", {}).get("succession_event")
    if isinstance(event, dict):
        return event
    return {}


def _extract_previous(payload: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
    previous = payload.get("previous_representative") or event.get("previous_representative")
    if isinstance(previous, dict):
        return previous
    rid = payload.get("previous_representative_id") or event.get("previous_representative_id")
    if rid:
        return {"representative_id": str(rid)}
    return {}


def _extract_new(payload: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
    new = payload.get("new_representative") or event.get("new_representative")
    if isinstance(new, dict):
        return new
    rid = payload.get("new_representative_id") or event.get("new_representative_id")
    if rid:
        return {"representative_id": str(rid)}
    return {}


def _rep_id(rep: Dict[str, Any], fallback: str) -> str:
    for key in ("representative_id", "candidate_id", "id", "name", "representative_name"):
        if rep.get(key):
            return str(rep[key])
    return fallback


@dataclass
class RepresentativeLineageRegistry:
    """Canonical lineage registry for representative succession events.

    This module does not claim phenomenal subjectivity. It records functional
    succession continuity between replaceable representatives of Open Cognitive
    Ecology Society and produces measurable lineage indicators.
    """

    primitive: str = "representative_lineage_registry"
    state_path: str = str(STATE_PATH)
    history_path: str = str(HISTORY_PATH)

    def step(self, payload: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if isinstance(payload, dict):
            data.update(payload)
        data.update(kwargs)

        dry_run = bool(data.get("dry_run", False))
        timestamp = str(data.get("timestamp_utc") or _utc_now())
        event = _extract_event(data)
        previous = _extract_previous(data, event)
        new = _extract_new(data, event)

        existing = _load_json(STATE_PATH, {})
        representatives = _as_list(existing.get("representatives"))
        succession_history = _as_list(existing.get("succession_history"))

        previous_id = _rep_id(previous, str(data.get("previous_representative_id") or "unknown_previous"))
        new_id = _rep_id(new, str(data.get("new_representative_id") or "unknown_successor"))

        succession_executed = bool(
            data.get("succession_executed")
            or data.get("succession_execution", {}).get("succession_executed")
            or event
            or (new_id != "unknown_successor")
        )

        event_payload = {
            "timestamp_utc": timestamp,
            "previous_representative_id": previous_id,
            "new_representative_id": new_id,
            "source_event_id": event.get("event_id") or data.get("succession_event_id"),
            "succession_executed": succession_executed,
        }
        lineage_event_id = str(data.get("lineage_event_id") or _stable_id("RLR", event_payload))

        lineage_event = {
            "event_id": lineage_event_id,
            "event_type": "representative_lineage_registration",
            "timestamp_utc": timestamp,
            "previous_representative": previous,
            "new_representative": new,
            "previous_representative_id": previous_id,
            "new_representative_id": new_id,
            "source_succession_event": event,
            "succession_executed": succession_executed,
        }

        if succession_executed:
            seen_ids = {str(r.get("representative_id")) for r in representatives if isinstance(r, dict)}
            if previous and previous_id not in seen_ids:
                prev_record = dict(previous)
                prev_record.setdefault("representative_id", previous_id)
                prev_record.setdefault("lineage_status", "previous")
                representatives.append(prev_record)
                seen_ids.add(previous_id)
            if new_id not in seen_ids:
                new_record = dict(new)
                new_record.setdefault("representative_id", new_id)
                new_record.setdefault("lineage_status", "active_successor")
                representatives.append(new_record)
                seen_ids.add(new_id)
            succession_history.append(lineage_event)

        generation_values = []
        for rep in representatives:
            if isinstance(rep, dict):
                for key in ("representative_generation", "candidate_generation", "generation"):
                    if key in rep:
                        try:
                            generation_values.append(int(rep[key]))
                            break
                        except Exception:
                            pass
        generation_count = max(generation_values) + 1 if generation_values else len(representatives)
        lineage_depth = len(succession_history)
        unique_representative_count = len({str(r.get("representative_id")) for r in representatives if isinstance(r, dict) and r.get("representative_id")})

        continuity_composite_score = _clamp(data.get("continuity_composite_score", data.get("continuity_metrics", {}).get("continuity_composite_score", 1.0)))
        identity_preservation_score = _clamp(data.get("civilizational_identity_preservation_score", data.get("identity_preservation", {}).get("civilizational_identity_preservation_score", 1.0)))
        verification_score = _clamp(data.get("continuity_validation_score", data.get("post_succession_verification", {}).get("continuity_validation_score", 1.0)))

        lineage_integrity_score = _clamp((continuity_composite_score + identity_preservation_score + verification_score) / 3.0)
        lineage_continuity_valid = bool(succession_executed and lineage_integrity_score >= 0.70 and unique_representative_count >= 1)
        lineage_decision = (
            "lineage_registered" if lineage_continuity_valid else
            "lineage_registered_with_warning" if succession_executed else
            "lineage_not_registered"
        )

        representative_lineage_graph = {
            "nodes": [
                {"id": str(r.get("representative_id")), "label": str(r.get("representative_name", r.get("representative_id", "unknown")))}
                for r in representatives if isinstance(r, dict) and r.get("representative_id")
            ],
            "edges": [
                {
                    "from": e.get("previous_representative_id"),
                    "to": e.get("new_representative_id"),
                    "event_id": e.get("event_id"),
                    "timestamp_utc": e.get("timestamp_utc"),
                }
                for e in succession_history if isinstance(e, dict)
            ],
        }

        result = {
            "primitive": self.primitive,
            "success": True,
            "lineage_event": lineage_event,
            "lineage_registered": succession_executed,
            "lineage_decision": lineage_decision,
            "lineage_continuity_valid": lineage_continuity_valid,
            "lineage_integrity_score": lineage_integrity_score,
            "lineage_depth": lineage_depth,
            "generation_count": generation_count,
            "unique_representative_count": unique_representative_count,
            "succession_history": succession_history,
            "representatives": representatives,
            "representative_lineage_graph": representative_lineage_graph,
            "state_path": str(STATE_PATH),
            "history_path": str(HISTORY_PATH),
            "epistemic_status": {
                "phenomenal_subjectivity_claimed": False,
                "validated_property": "functional representative lineage continuity",
            },
        }

        if not dry_run:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            STATE_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            with HISTORY_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(lineage_event, ensure_ascii=False, sort_keys=True) + "\n")

        return result


def step(payload: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
    return RepresentativeLineageRegistry().step(payload, **kwargs)
