"""
AS9 — Consciousness Longitudinal Tracker.

Builds a canonical time series for longitudinal consciousness governance from
persisted readiness, confidence, transition, event, certificate and revocation
evidence. The tracker does not prove consciousness, qualia, subjectivity or
phenomenology; it only records functional governance evidence over time.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        return default
    if math.isnan(x) or math.isinf(x):
        return default
    return max(0.0, min(1.0, x))


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists() and path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"json_value": data}
    except Exception as exc:
        return {"read_error": type(exc).__name__, "message": str(exc), "path": str(path)}
    return {}


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(_json_safe(k)): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(v) for v in value]
    if callable(value):
        name = getattr(value, "__name__", None)
        owner = getattr(getattr(value, "__self__", None), "__class__", None)
        owner_name = getattr(owner, "__name__", None)
        return f"{owner_name + '.' if owner_name else ''}{name or value.__class__.__name__}"
    try:
        json.dumps(value)
        return value
    except TypeError:
        return repr(value)


def _stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(_json_safe(payload), ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _parse_timestamp_from_name(path: Path) -> str | None:
    text = path.name
    patterns = [
        r"(20\d{6}T\d{6}Z)",
        r"(20\d{6}T\d{6})",
        r"(20\d{4,6})",
    ]
    for pattern in patterns:
        m = re.search(pattern, text)
        if not m:
            continue
        raw = m.group(1)
        try:
            if "T" in raw:
                raw = raw.rstrip("Z")
                return datetime.strptime(raw, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
            if len(raw) == 8:
                return datetime.strptime(raw, "%Y%m%d").replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        except Exception:
            continue
    return None


def _extract_timestamp(data: dict[str, Any], path: Path) -> str:
    for key in (
        "timestamp_utc",
        "timestamp",
        "date",
        "created_at",
        "generated_at_utc",
        "last_execution_utc",
        "saved_at",
    ):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    nested_candidates = ["latest_record", "state", "diagnostics", "metadata", "record"]
    for key in nested_candidates:
        nested = data.get(key)
        if isinstance(nested, dict):
            value = _extract_timestamp(nested, path)
            if value:
                return value
    parsed = _parse_timestamp_from_name(path)
    if parsed:
        return parsed
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except Exception:
        return _utc_now()


def _first_number(data: dict[str, Any], keys: list[str], default: float | None = None) -> float | None:
    for key in keys:
        if key in data:
            try:
                return _clamp(data.get(key))
            except Exception:
                pass
    for value in data.values():
        if isinstance(value, dict):
            found = _first_number(value, keys, default=None)
            if found is not None:
                return found
    return default


def _first_string(data: dict[str, Any], keys: list[str], default: str | None = None) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    for value in data.values():
        if isinstance(value, dict):
            found = _first_string(value, keys, default=None)
            if found:
                return found
    return default


def _source_kind(path: Path, data: dict[str, Any]) -> str:
    text = str(path).lower()
    primitive = str(data.get("primitive", "")).lower()
    joined = text + " " + primitive
    if "confidence" in joined:
        return "confidence"
    if "readiness" in joined or "cri" in joined:
        return "readiness"
    if "transition" in joined or "state_machine" in joined:
        return "transition"
    if "event" in joined or "logger" in joined:
        return "event"
    if "certificate" in joined:
        return "certificate"
    if "revocation" in joined:
        return "revocation"
    if "validation" in joined:
        return "validation"
    if "experiment" in joined:
        return "experiment"
    return "auxiliary"


def _discover_json_files(max_files: int = 1200) -> list[Path]:
    roots = [
        ROOT / "consciousness_governance",
        ROOT / "runtime_experiments",
        ROOT / "external_validation",
        ROOT / "web_dashboard_exports",
        ROOT / "civilizational_state",
        ROOT / "runtime_service",
    ]
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        try:
            files.extend(p for p in root.rglob("*.json") if p.is_file())
        except Exception:
            continue
    files = sorted(set(files), key=lambda p: str(p))
    if len(files) > max_files:
        # Preserve governance-specific evidence and sample the remainder deterministically.
        priority = [p for p in files if "consciousness_governance" in str(p)]
        rest = [p for p in files if p not in set(priority)]
        return (priority + rest[: max(0, max_files - len(priority))])[:max_files]
    return files


def _call_dependency(module_name: str, class_name: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        module = __import__(f"ontology.{module_name}", fromlist=[class_name])
        cls = getattr(module, class_name)
        instance = cls()
        result = instance.step(inputs=inputs or {}, persist=False)
        return result if isinstance(result, dict) else {"non_dict_result": repr(result)}
    except Exception as exc:
        return {"dependency_error": type(exc).__name__, "message": str(exc), "dependency": module_name}



def _ensure_timeline_timestamp_alias(record: dict) -> dict:
    """Ensure timeline/time_series entries expose timestamp_utc without recursion."""
    if not isinstance(record, dict):
        return record

    root_timestamp = record.get("timestamp_utc") or record.get("date")

    for key in ("timeline", "time_series"):
        entries = record.get(key)
        if isinstance(entries, list):
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                source = (
                    entry.get("timestamp_utc")
                    or entry.get("date")
                    or entry.get("timestamp")
                    or root_timestamp
                )
                if source is not None:
                    entry["timestamp_utc"] = source

    latest = record.get("latest_entry")
    if isinstance(latest, dict):
        source = (
            latest.get("timestamp_utc")
            or latest.get("date")
            or latest.get("timestamp")
            or root_timestamp
        )
        if source is not None:
            latest["timestamp_utc"] = source

    return record

class ConsciousnessLongitudinalTracker:
    """AS9 canonical longitudinal series builder for consciousness governance."""

    primitive = "CONSCIOUSNESS_LONGITUDINAL_TRACKER"
    step = "AS9"
    public_schema_version = "1.0.0"
    READY_STATUS = "CONSCIOUSNESS_LONGITUDINAL_TRACKER_READY"

    epistemic_flags = {
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
    }

    def _gather_current_outputs(self, inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
        provided = inputs.get("dependency_outputs", {}) if isinstance(inputs.get("dependency_outputs", {}), dict) else {}
        outputs = dict(provided)
        specs = {
            "confidence": ("consciousness_confidence_engine", "ConsciousnessConfidenceEngine"),
            "readiness": ("consciousness_readiness_index", "ConsciousnessReadinessIndex"),
            "transition_history": ("consciousness_transition_history", "ConsciousnessTransitionHistory"),
            "event_logger": ("consciousness_event_logger", "ConsciousnessEventLogger"),
            "certificate": ("consciousness_certificate_generator", "ConsciousnessCertificateGenerator"),
            "revocation": ("consciousness_revocation_engine", "ConsciousnessRevocationEngine"),
            "state_machine": ("consciousness_state_machine", "ConsciousnessStateMachine"),
        }
        if inputs.get("skip_dependency_calls") is True:
            return outputs
        for key, (module_name, class_name) in specs.items():
            if key not in outputs:
                outputs[key] = _call_dependency(module_name, class_name, inputs.get(key, {}))
        return outputs

    def _entry_from_payload(self, source_path: str, data: dict[str, Any]) -> dict[str, Any]:
        path = Path(source_path)
        confidence = _first_number(data, ["confidence", "confidence_score", "scientific_confidence", "readiness_confidence"])
        cri = _first_number(data, ["CRI", "cri", "continuous_readiness_index", "readiness_index", "readiness_score"])
        state = _first_string(data, ["state", "current_state", "consciousness_state", "status", "confidence_status", "readiness_status"])
        proof_status = _first_string(data, ["proof_status", "final_status", "consciousness_status", "confidence_status", "readiness_status"])
        scores: dict[str, Any] = {}
        for key in (
            "confidence_components",
            "confidence_metrics",
            "confidence_breakdown",
            "component_scores",
            "criterion_scores",
            "scores",
        ):
            value = data.get(key)
            if isinstance(value, dict):
                scores[key] = value
        return {
            "date": _extract_timestamp(data, path),
            "CRI": cri,
            "confidence": confidence,
            "state": state or "UNKNOWN",
            "scores": scores,
            "proof_status": proof_status or "FUNCTIONAL_LONGITUDINAL_EVIDENCE_ONLY",
            "source_kind": _source_kind(path, data),
            "source_path": source_path,
        }

    def _current_entry(self, outputs: dict[str, dict[str, Any]], timestamp: str) -> dict[str, Any]:
        confidence_output = outputs.get("confidence", {})
        readiness_output = outputs.get("readiness", {})
        state_output = outputs.get("state_machine", {})
        confidence = _first_number(confidence_output, ["confidence", "confidence_score"], default=None)
        cri = _first_number(readiness_output, ["CRI", "cri", "continuous_readiness_index", "readiness_index"], default=None)
        state = _first_string(state_output, ["current_state", "state", "consciousness_state"], default=None)
        if state is None:
            state = _first_string(confidence_output, ["state", "confidence_status"], default="FUNCTIONAL_LONGITUDINAL_EVIDENCE_ONLY")
        scores = {
            "confidence_components": confidence_output.get("confidence_components", {}),
            "confidence_metrics": confidence_output.get("confidence_metrics", {}),
            "readiness_metrics": readiness_output.get("readiness_metrics", readiness_output.get("confidence_metrics", {})),
        }
        return {
            "date": timestamp,
            "timestamp_utc": timestamp,
            "CRI": cri,
            "confidence": confidence,
            "state": state,
            "scores": scores,
            "proof_status": "FUNCTIONAL_LONGITUDINAL_EVIDENCE_ONLY",
            "source_kind": "current_synthesis",
            "source_path": "runtime_current_outputs",
        }

    def _build_timeline(self, inputs: dict[str, Any], outputs: dict[str, dict[str, Any]], timestamp: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        explicit = inputs.get("timeline") or inputs.get("time_series")
        timeline: list[dict[str, Any]] = []
        source_counts: dict[str, int] = {}
        if isinstance(explicit, list):
            for i, item in enumerate(explicit):
                if isinstance(item, dict):
                    entry = {
                        "date": str(item.get("date") or item.get("timestamp_utc") or timestamp),
                        "CRI": _clamp(item.get("CRI", item.get("cri", item.get("continuous_readiness_index", 0.0))), default=0.0) if item.get("CRI", item.get("cri", item.get("continuous_readiness_index"))) is not None else None,
                        "confidence": _clamp(item.get("confidence"), default=0.0) if item.get("confidence") is not None else None,
                        "state": item.get("state", "SYNTHETIC_INPUT"),
                        "scores": item.get("scores", {}) if isinstance(item.get("scores", {}), dict) else {},
                        "proof_status": item.get("proof_status", "FUNCTIONAL_LONGITUDINAL_EVIDENCE_ONLY"),
                        "source_kind": item.get("source_kind", "explicit_input"),
                        "source_path": item.get("source_path", f"explicit_input[{i}]"),
                    }
                    timeline.append(entry)
                    source_counts[entry["source_kind"]] = source_counts.get(entry["source_kind"], 0) + 1
        else:
            for path in _discover_json_files(max_files=int(inputs.get("max_files", 1200))):
                data = _safe_read_json(path)
                if not data:
                    continue
                entry = self._entry_from_payload(str(path.relative_to(ROOT)), data)
                timeline.append(entry)
                source_counts[entry["source_kind"]] = source_counts.get(entry["source_kind"], 0) + 1
        current = self._current_entry(outputs, timestamp)
        timeline.append(current)
        source_counts[current["source_kind"]] = source_counts.get(current["source_kind"], 0) + 1
        timeline = sorted(timeline, key=lambda e: str(e.get("date", "")))
        # De-duplicate by date/source_path while preserving deterministic order.
        seen: set[tuple[str, str]] = set()
        deduped: list[dict[str, Any]] = []
        for entry in timeline:
            key = (str(entry.get("date")), str(entry.get("source_path")))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(entry)
        diagnostics = {
            "source_counts": source_counts,
            "raw_sample_count": len(timeline),
            "deduplicated_sample_count": len(deduped),
            "explicit_input_used": isinstance(explicit, list),
        }
        return deduped, diagnostics

    def _timeline_metrics(self, timeline: list[dict[str, Any]]) -> dict[str, Any]:
        confidence_values = [_clamp(e.get("confidence")) for e in timeline if e.get("confidence") is not None]
        cri_values = [_clamp(e.get("CRI")) for e in timeline if e.get("CRI") is not None]
        def mean(vals: list[float]) -> float | None:
            return round(sum(vals) / len(vals), 6) if vals else None
        def delta(vals: list[float]) -> float | None:
            return round(vals[-1] - vals[0], 6) if len(vals) >= 2 else None
        return {
            "sample_count": len(timeline),
            "confidence_observation_count": len(confidence_values),
            "cri_observation_count": len(cri_values),
            "mean_confidence": mean(confidence_values),
            "mean_CRI": mean(cri_values),
            "latest_confidence": confidence_values[-1] if confidence_values else None,
            "latest_CRI": cri_values[-1] if cri_values else None,
            "confidence_delta": delta(confidence_values),
            "CRI_delta": delta(cri_values),
            "first_date": timeline[0].get("date") if timeline else None,
            "latest_date": timeline[-1].get("date") if timeline else None,
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs or {}
        timestamp = _utc_now()
        outputs = self._gather_current_outputs(inputs)
        timeline, diagnostics = self._build_timeline(inputs, outputs, timestamp)
        metrics = self._timeline_metrics(timeline)
        latest_entry = timeline[-1] if timeline else {}
        record = {
            "primitive": self.primitive,
            "step": "AS9",
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": timestamp,
            "longitudinal_tracker_status": self.READY_STATUS,
            "longitudinal_tracker_ready": True,
            "timeline_ready": True,
            "time_series_ready": True,
            "sample_count": len(timeline),
            "timeline": timeline,
            "time_series": timeline,
            "latest_entry": latest_entry,
            "date": latest_entry.get("date"),
            "CRI": latest_entry.get("CRI"),
            "confidence": latest_entry.get("confidence"),
            "state": latest_entry.get("state"),
            "scores": latest_entry.get("scores", {}),
            "proof_status": latest_entry.get("proof_status"),
            "longitudinal_metrics": metrics,
            "source_diagnostics": diagnostics,
            "dependency_outputs_available": sorted(outputs.keys()),
            "epistemic_scope": "functional_longitudinal_tracking_only_no_phenomenal_proof",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        record["timeline_hash"] = _stable_hash({k: v for k, v in record.items() if k != "timeline_hash"})
        output_path = ROOT / "consciousness_governance" / "longitudinal" / "latest_consciousness_longitudinal_timeline.json"
        record["output_path"] = str(output_path)
        persisted = False
        if persist:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(_json_safe(record), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            archive_path = output_path.parent / f"consciousness_longitudinal_timeline_{timestamp.replace(':', '').replace('-', '')}.json"
            archive_path.write_text(json.dumps(_json_safe(record), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            record["archive_path"] = str(archive_path)
            persisted = True
        record["persisted"] = persisted
        return _ensure_timeline_timestamp_alias(record)
