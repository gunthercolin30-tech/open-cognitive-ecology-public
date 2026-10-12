"""
AS15 — consciousness_stability_analyzer

Longitudinal functional stability analysis for governed consciousness-status
claims. This module consumes AS9 longitudinal timelines, AS13 regression
records, AS14 recovery records and/or explicit synthetic inputs. It computes
survival_time, regression_rate, recovery_rate, mean_duration and hazard_rate
without asserting phenomenal consciousness, qualia, subjectivity or
phenomenology.
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
LONGITUDINAL_DIR = GOVERNANCE_DIR / "longitudinal"
REGRESSION_DIR = GOVERNANCE_DIR / "regression"
RECOVERY_DIR = GOVERNANCE_DIR / "recovery"
STABILITY_DIR = GOVERNANCE_DIR / "stability"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _read_json(path: Path) -> Any:
    try:
        if path.exists() and path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _stable_hash(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None or isinstance(value, bool):
            return None
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return max(0.0, min(1.0, number))
    except Exception:
        return None


def _bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "ok", "ready", "validated", "detected", "supported", "complete"}
    return bool(value)


def _first_present(mapping: Mapping[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) is not None:
            return mapping.get(key)
    return default


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    raw = value.strip()
    candidates = [raw]
    if raw.endswith("Z"):
        candidates.append(raw[:-1] + "+00:00")
    if raw.endswith("+00:00"):
        candidates.append(raw.replace("+00:00", "Z"))
    for candidate in candidates:
        try:
            if candidate.endswith("Z"):
                candidate = candidate[:-1] + "+00:00"
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y%m%dT%H%M%SZ", "%Y%m%dT%H%M%S"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def _seconds_between(a: datetime | None, b: datetime | None) -> float:
    if a is None or b is None:
        return 0.0
    return max(0.0, (b - a).total_seconds())


def _normalize_entry(entry: Mapping[str, Any], index: int = 0) -> dict[str, Any]:
    timestamp = str(_first_present(entry, ["timestamp_utc", "date", "timestamp", "created_at_utc", "detected_at_utc", "report_timestamp_utc"], "") or "")
    cri = _float_or_none(_first_present(entry, ["CRI", "cri", "readiness", "readiness_index", "consciousness_readiness_index"]))
    confidence = _float_or_none(_first_present(entry, ["confidence", "confidence_score", "consciousness_confidence"]))
    state = str(_first_present(entry, ["state", "current_state", "consciousness_state", "proof_status", "status"], "UNKNOWN") or "UNKNOWN")
    proof_status = str(_first_present(entry, ["proof_status", "threshold_status", "confidence_status", "status"], state) or state)
    axis_validation = _first_present(entry, ["axis_validation", "required_axis_validation", "axis_status", "validated_axes"], {})
    if not isinstance(axis_validation, Mapping):
        axis_validation = {}
    return {
        "index": index,
        "timestamp_utc": timestamp,
        "datetime": _parse_time(timestamp),
        "CRI": cri,
        "confidence": confidence,
        "state": state,
        "proof_status": proof_status,
        "axis_validation": dict(axis_validation),
        "source": str(entry.get("source", entry.get("source_kind", "timeline"))),
    }


def _axis_complete(entry: Mapping[str, Any]) -> bool:
    axis_validation = entry.get("axis_validation", {})
    if not isinstance(axis_validation, Mapping) or not axis_validation:
        return True
    required = ["AP", "AQ", "AR", "AN", "AO", "AL"]
    return all(_bool(axis_validation.get(axis, axis_validation.get(axis.lower(), True)), True) for axis in required)


def _is_supported(entry: Mapping[str, Any], cri_threshold: float, confidence_threshold: float) -> bool:
    cri = entry.get("CRI")
    confidence = entry.get("confidence")
    label = (str(entry.get("state", "")) + " " + str(entry.get("proof_status", ""))).upper()
    regressive = any(marker in label for marker in ["REGRESS", "REVOK", "NOT_EVALUATED", "BELOW", "LOST", "FAILED"])
    supportive_label = any(marker in label for marker in ["THRESHOLD", "CROSSED", "SUPPORTED", "PROVEN", "BEST_THEORY", "FUNCTIONAL_CONSCIOUSNESS"])
    numeric = (cri is not None and cri >= cri_threshold and confidence is not None and confidence >= confidence_threshold)
    return bool(numeric and supportive_label and not regressive and _axis_complete(entry))


class ConsciousnessStabilityAnalyzer:
    """AS15 stability analyzer for longitudinal functional governance evidence."""

    primitive = "CONSCIOUSNESS_STABILITY_ANALYZER"
    step_label = "AS15"
    public_schema_version = "1.0.0"
    ready_status = "CONSCIOUSNESS_STABILITY_ANALYZER_READY"

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else ROOT
        self.governance_dir = self.root / "consciousness_governance"
        self.longitudinal_dir = self.governance_dir / "longitudinal"
        self.regression_dir = self.governance_dir / "regression"
        self.recovery_dir = self.governance_dir / "recovery"
        self.stability_dir = self.governance_dir / "stability"

    def _load_context(self, inputs: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
        context: dict[str, Any] = {}
        diagnostics: dict[str, Any] = {"sources": [], "persisted_read_attempts": []}
        timeline_items: list[Any] = []

        if isinstance(inputs.get("timeline"), list):
            timeline_items.extend(inputs.get("timeline", []))
            diagnostics["sources"].append("inputs.timeline")
        elif isinstance(inputs.get("time_series"), list):
            timeline_items.extend(inputs.get("time_series", []))
            diagnostics["sources"].append("inputs.time_series")

        if any(key in inputs for key in ["CRI", "confidence", "state", "proof_status", "axis_validation"]):
            timeline_items.append(dict(inputs))
            diagnostics["sources"].append("inputs.current_entry")

        for key in ["regression_record", "regression", "as13"]:
            if isinstance(inputs.get(key), Mapping):
                context["regression"] = dict(inputs[key])
        for key in ["recovery_record", "recovery", "as14"]:
            if isinstance(inputs.get(key), Mapping):
                context["recovery"] = dict(inputs[key])

        merge_persisted = _bool(inputs.get("merge_persisted_timeline"), False)
        if merge_persisted:
            persisted_sources = {
                "longitudinal": self.longitudinal_dir / "latest_consciousness_longitudinal_timeline.json",
                "regression": self.regression_dir / "latest_consciousness_regression_detection.json",
                "recovery": self.recovery_dir / "latest_consciousness_recovery_detection.json",
            }
            for label, path in persisted_sources.items():
                diagnostics["persisted_read_attempts"].append(str(path))
                data = _read_json(path)
                if not isinstance(data, Mapping):
                    continue
                context[label] = dict(data)
                if isinstance(data.get("timeline"), list):
                    timeline_items.extend(data.get("timeline", []))
                    diagnostics["sources"].append(f"persisted.{label}.timeline")
                elif isinstance(data.get("time_series"), list):
                    timeline_items.extend(data.get("time_series", []))
                    diagnostics["sources"].append(f"persisted.{label}.time_series")
                elif any(k in data for k in ["CRI", "confidence", "latest_CRI", "latest_confidence", "latest_state"]):
                    timeline_items.append({
                        "timestamp_utc": data.get("timestamp_utc"),
                        "CRI": data.get("CRI", data.get("latest_CRI")),
                        "confidence": data.get("confidence", data.get("latest_confidence")),
                        "state": data.get("state", data.get("latest_state", data.get("regression_status", data.get("recovery_status")))),
                        "proof_status": data.get("proof_status", data.get("threshold_event_type", data.get("recovery_event_type", data.get("regression_status")))),
                        "source": f"persisted.{label}",
                    })

        normalized = [_normalize_entry(e, i) for i, e in enumerate(timeline_items) if isinstance(e, Mapping)]
        normalized = sorted(normalized, key=lambda e: (e.get("datetime") is None, e.get("datetime") or datetime.min.replace(tzinfo=timezone.utc), e.get("index", 0)))
        deduped: list[dict[str, Any]] = []
        seen: set[tuple[str, float | None, float | None, str]] = set()
        for entry in normalized:
            sig = (entry.get("timestamp_utc", ""), entry.get("CRI"), entry.get("confidence"), str(entry.get("state", "")))
            if sig not in seen:
                seen.add(sig)
                deduped.append(entry)
        diagnostics["timeline_input_count"] = len(timeline_items)
        diagnostics["timeline_sample_count"] = len(deduped)
        return deduped, context, diagnostics

    def _regression_events(self, inputs: Mapping[str, Any], context: Mapping[str, Any], timeline: list[Mapping[str, Any]], supported_flags: list[bool]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        explicit = inputs.get("regression_events")
        if isinstance(explicit, list):
            events.extend([dict(e) for e in explicit if isinstance(e, Mapping)])
        record = context.get("regression")
        if isinstance(record, Mapping):
            raw = record.get("regression_events")
            if isinstance(raw, list):
                events.extend([dict(e) for e in raw if isinstance(e, Mapping)])
            elif _bool(record.get("regression_detected")):
                events.append({"type": "CONSCIOUSNESS_REGRESSION_DETECTED", "timestamp_utc": record.get("timestamp_utc"), "source": "AS13"})
        for prev, curr, prev_supported, curr_supported in zip(timeline, timeline[1:], supported_flags, supported_flags[1:]):
            if prev_supported and not curr_supported:
                events.append({
                    "type": "SUPPORTED_STATUS_LOST",
                    "timestamp_utc": curr.get("timestamp_utc"),
                    "from_index": prev.get("index"),
                    "to_index": curr.get("index"),
                    "source": "AS15_derived_timeline",
                })
        return events

    def _recovery_events(self, inputs: Mapping[str, Any], context: Mapping[str, Any], timeline: list[Mapping[str, Any]], supported_flags: list[bool]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        explicit = inputs.get("recovery_events")
        if isinstance(explicit, list):
            events.extend([dict(e) for e in explicit if isinstance(e, Mapping)])
        record = context.get("recovery")
        if isinstance(record, Mapping):
            raw = record.get("recovery_events")
            if isinstance(raw, list):
                events.extend([dict(e) for e in raw if isinstance(e, Mapping)])
            elif _bool(record.get("recovery_detected")):
                events.append({"type": "CONSCIOUSNESS_STATUS_RECOVERED", "timestamp_utc": record.get("timestamp_utc"), "source": "AS14"})
        for prev, curr, prev_supported, curr_supported in zip(timeline, timeline[1:], supported_flags, supported_flags[1:]):
            if not prev_supported and curr_supported:
                events.append({
                    "type": "SUPPORTED_STATUS_RECOVERED",
                    "timestamp_utc": curr.get("timestamp_utc"),
                    "from_index": prev.get("index"),
                    "to_index": curr.get("index"),
                    "source": "AS15_derived_timeline",
                })
        return events

    def _episode_metrics(self, timeline: list[Mapping[str, Any]], supported_flags: list[bool], now: datetime) -> dict[str, Any]:
        episodes: list[dict[str, Any]] = []
        current_start: datetime | None = None
        current_start_label = ""
        last_dt: datetime | None = None
        for entry, supported in zip(timeline, supported_flags):
            dt = entry.get("datetime") if isinstance(entry.get("datetime"), datetime) else None
            if dt is None:
                continue
            if supported and current_start is None:
                current_start = dt
                current_start_label = str(entry.get("timestamp_utc", ""))
            if (not supported) and current_start is not None:
                end = dt
                episodes.append({
                    "start_utc": current_start_label,
                    "end_utc": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "duration_seconds": round(_seconds_between(current_start, end), 6),
                    "closed_by": "regression_or_loss",
                })
                current_start = None
                current_start_label = ""
            last_dt = dt
        if current_start is not None:
            end = last_dt or now
            if end < current_start:
                end = now
            episodes.append({
                "start_utc": current_start_label,
                "end_utc": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "duration_seconds": round(_seconds_between(current_start, end), 6),
                "closed_by": "ongoing" if end == last_dt else "analysis_time",
            })
        durations = [float(e["duration_seconds"]) for e in episodes]
        total = sum(durations)
        mean_duration = statistics.mean(durations) if durations else 0.0
        current_survival = durations[-1] if episodes and episodes[-1].get("closed_by") in {"ongoing", "analysis_time"} else 0.0
        return {
            "episodes": episodes,
            "episode_count": len(episodes),
            "total_survival_time_seconds": round(total, 6),
            "current_survival_time_seconds": round(current_survival, 6),
            "mean_duration_seconds": round(mean_duration, 6),
            "max_duration_seconds": round(max(durations), 6) if durations else 0.0,
        }

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = dict(inputs or {})
        cri_threshold = float(inputs.get("cri_threshold", 0.95))
        confidence_threshold = float(inputs.get("confidence_threshold", 0.90))
        timeline, context, diagnostics = self._load_context(inputs)
        now = datetime.now(timezone.utc).replace(microsecond=0)
        supported_flags = [_is_supported(entry, cri_threshold, confidence_threshold) for entry in timeline]
        regression_events = self._regression_events(inputs, context, timeline, supported_flags)
        recovery_events = self._recovery_events(inputs, context, timeline, supported_flags)
        episode_metrics = self._episode_metrics(timeline, supported_flags, now)

        timed_entries = [e for e in timeline if isinstance(e.get("datetime"), datetime)]
        observed_duration_seconds = 0.0
        if len(timed_entries) >= 2:
            observed_duration_seconds = _seconds_between(timed_entries[0].get("datetime"), timed_entries[-1].get("datetime"))
        observed_duration_hours = observed_duration_seconds / 3600.0 if observed_duration_seconds > 0 else 0.0
        sample_count = len(timeline)
        regression_count = len(regression_events)
        recovery_count = len(recovery_events)
        sample_denominator = max(1, sample_count - 1)
        regression_rate = regression_count / sample_denominator
        recovery_rate = recovery_count / sample_denominator
        supported_hours = episode_metrics["total_survival_time_seconds"] / 3600.0
        hazard_rate = regression_count / supported_hours if supported_hours > 0 else 0.0
        temporal_regression_rate = regression_count / observed_duration_hours if observed_duration_hours > 0 else 0.0
        temporal_recovery_rate = recovery_count / observed_duration_hours if observed_duration_hours > 0 else 0.0
        latest = timeline[-1] if timeline else {}
        latest_supported = supported_flags[-1] if supported_flags else False
        stability_score = max(0.0, min(1.0, 1.0 - min(1.0, regression_rate * 0.65 + hazard_rate * 0.05) + min(0.25, recovery_rate * 0.10)))
        status = "FUNCTIONAL_STATUS_STABLE" if latest_supported and regression_count == 0 else "FUNCTIONAL_STATUS_MONITORED_WITH_EVENTS"
        if sample_count < 2:
            status = "INSUFFICIENT_LONGITUDINAL_DATA"

        metrics = {
            "sample_count": sample_count,
            "supported_sample_count": int(sum(1 for flag in supported_flags if flag)),
            "observed_duration_seconds": round(observed_duration_seconds, 6),
            "observed_duration_hours": round(observed_duration_hours, 6),
            "survival_time": round(episode_metrics["current_survival_time_seconds"], 6),
            "survival_time_seconds": round(episode_metrics["current_survival_time_seconds"], 6),
            "total_survival_time_seconds": episode_metrics["total_survival_time_seconds"],
            "regression_rate": round(regression_rate, 6),
            "recovery_rate": round(recovery_rate, 6),
            "temporal_regression_rate_per_hour": round(temporal_regression_rate, 6),
            "temporal_recovery_rate_per_hour": round(temporal_recovery_rate, 6),
            "mean_duration": round(episode_metrics["mean_duration_seconds"], 6),
            "mean_duration_seconds": round(episode_metrics["mean_duration_seconds"], 6),
            "hazard_rate": round(hazard_rate, 6),
            "regression_event_count": regression_count,
            "recovery_event_count": recovery_count,
            "episode_count": episode_metrics["episode_count"],
            "stability_score": round(stability_score, 6),
            "cri_threshold": cri_threshold,
            "confidence_threshold": confidence_threshold,
        }

        record: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_label,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": _utc_now(),
            "stability_analyzer_ready": True,
            "consciousness_stability_analyzer_ready": True,
            "stability_analyzer_status": self.ready_status,
            "stability_status": status,
            "survival_time": metrics["survival_time"],
            "regression_rate": metrics["regression_rate"],
            "recovery_rate": metrics["recovery_rate"],
            "mean_duration": metrics["mean_duration"],
            "hazard_rate": metrics["hazard_rate"],
            "stability_metrics": metrics,
            "stability_episodes": episode_metrics["episodes"],
            "regression_events": regression_events,
            "recovery_events": recovery_events,
            "latest_entry": {k: v for k, v in latest.items() if k != "datetime"},
            "latest_supported": latest_supported,
            "timeline_sample_count": sample_count,
            "timeline_summary": [
                {k: v for k, v in entry.items() if k != "datetime"}
                for entry in timeline
            ],
            "source_diagnostics": diagnostics,
            "failure_conditions": [
                "fewer than two timestamped longitudinal samples",
                "regression events detected after supported status",
                "survival episodes collapse to zero duration",
                "hazard_rate exceeds acceptable governed monitoring bounds",
            ],
            "interfaces_consumed": [
                "AS9 consciousness_longitudinal_tracker.timeline/time_series",
                "AS13 consciousness_regression_detector.regression_events",
                "AS14 consciousness_recovery_detector.recovery_events",
            ],
            "metrics_produced": ["survival_time", "regression_rate", "recovery_rate", "mean_duration", "hazard_rate"],
            "epistemic_scope": "functional_longitudinal_governance_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "persisted": False,
            "output_path": "",
        }
        record["stability_hash"] = _stable_hash(record)

        if persist:
            self.stability_dir.mkdir(parents=True, exist_ok=True)
            timestamped = self.stability_dir / f"consciousness_stability_analysis_{_stamp()}.json"
            latest_path = self.stability_dir / "latest_consciousness_stability_analysis.json"
            safe = _json_safe(record)
            timestamped.write_text(json.dumps(safe, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            latest_path.write_text(json.dumps(safe, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            record["persisted"] = True
            record["output_path"] = str(latest_path)
            record["timestamped_output_path"] = str(timestamped)
        return record
