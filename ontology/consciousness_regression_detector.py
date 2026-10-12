"""
AS13 — consciousness_regression_detector

Detect governed functional regressions after a consciousness-threshold crossing.
The detector consumes persisted AS9/AS11/AS12/AS8 artefacts and/or explicit
inputs, compares longitudinal CRI and confidence values, checks status and axis
validation regressions, and produces a JSON regression record.

Epistemic scope: longitudinal functional governance only. This module never
proves consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Iterable

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
LONGITUDINAL_DIR = GOVERNANCE_DIR / "longitudinal"
THRESHOLD_DIR = GOVERNANCE_DIR / "threshold"
FIRST_CROSSING_DIR = GOVERNANCE_DIR / "first_crossing_report"
CONFIDENCE_DIR = GOVERNANCE_DIR / "confidence"
DASHBOARD_DIR = GOVERNANCE_DIR / "dashboard"
REGRESSION_DIR = GOVERNANCE_DIR / "regression"


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
        if number != number:
            return None
        return max(0.0, min(1.0, number))
    except Exception:
        return None


def _bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "ok", "ready", "validated", "detected", "supported"}
    return bool(value)


def _first_present(mapping: Mapping[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) is not None:
            return mapping.get(key)
    return default


def _timestamp_of(entry: Mapping[str, Any], fallback: str = "") -> str:
    return str(_first_present(entry, ["timestamp_utc", "date", "created_at_utc", "detected_at_utc", "report_timestamp_utc"], fallback) or fallback)


def _extract_axis_validation(source: Mapping[str, Any]) -> dict[str, bool]:
    raw = _first_present(source, ["axis_validation", "required_axis_validation", "axis_status", "validated_axes"], {})
    if not isinstance(raw, Mapping):
        return {}
    result: dict[str, bool] = {}
    for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]:
        value = raw.get(axis) if axis in raw else raw.get(axis.lower())
        if value is not None:
            result[axis] = _bool(value)
    return result


def _normalize_entry(entry: Mapping[str, Any], source: str = "input") -> dict[str, Any]:
    timestamp = _timestamp_of(entry) or _utc_now()
    cri = _float_or_none(_first_present(entry, ["CRI", "cri", "readiness", "readiness_index", "consciousness_readiness_index"]))
    confidence = _float_or_none(_first_present(entry, ["confidence", "confidence_score", "consciousness_confidence"]))
    state = str(_first_present(entry, ["state", "current_state", "proof_status", "status"], "UNKNOWN"))
    proof_status = str(_first_present(entry, ["proof_status", "threshold_status", "confidence_status"], state))
    return {
        "timestamp_utc": timestamp,
        "date": str(_first_present(entry, ["date"], timestamp)),
        "CRI": cri,
        "confidence": confidence,
        "state": state,
        "proof_status": proof_status,
        "axis_validation": _extract_axis_validation(entry),
        "source": source,
        "raw_status": str(_first_present(entry, ["status", "dashboard_status", "longitudinal_tracker_status"], "")),
    }


class ConsciousnessRegressionDetector:
    """AS13 regression detector for governed functional consciousness status."""

    primitive = "CONSCIOUSNESS_REGRESSION_DETECTOR"
    step_label = "AS13"
    public_schema_version = "1.0.0"
    ready_status = "CONSCIOUSNESS_REGRESSION_DETECTOR_READY"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.governance_dir = self.root / "consciousness_governance"
        self.longitudinal_dir = self.governance_dir / "longitudinal"
        self.threshold_dir = self.governance_dir / "threshold"
        self.first_crossing_dir = self.governance_dir / "first_crossing_report"
        self.confidence_dir = self.governance_dir / "confidence"
        self.dashboard_dir = self.governance_dir / "dashboard"
        self.regression_dir = self.governance_dir / "regression"

    def _load_timeline(self) -> tuple[list[dict[str, Any]], list[str]]:
        diagnostics: list[str] = []
        records: list[dict[str, Any]] = []
        candidates = [
            self.longitudinal_dir / "latest_consciousness_longitudinal_timeline.json",
            self.dashboard_dir / "latest_consciousness_dashboard.json",
        ]
        for path in candidates:
            data = _read_json(path)
            if not isinstance(data, dict):
                diagnostics.append(f"missing_or_unreadable:{path}")
                continue
            timeline = data.get("timeline") or data.get("time_series") or []
            if isinstance(timeline, list):
                for item in timeline:
                    if isinstance(item, Mapping):
                        records.append(_normalize_entry(item, str(path)))
                diagnostics.append(f"loaded:{path}:{len(timeline)}")
            else:
                diagnostics.append(f"no_timeline_list:{path}")
            records.append(_normalize_entry(data, str(path) + ":top_level"))
        records = [r for r in records if r.get("timestamp_utc")]
        records.sort(key=lambda x: str(x.get("timestamp_utc", "")))
        deduped: list[dict[str, Any]] = []
        seen: set[tuple[str, Any, Any, str]] = set()
        for r in records:
            key = (str(r.get("timestamp_utc")), r.get("CRI"), r.get("confidence"), str(r.get("state")))
            if key not in seen:
                seen.add(key)
                deduped.append(r)
        return deduped, diagnostics

    def _load_threshold_context(self) -> dict[str, Any]:
        threshold = _read_json(self.threshold_dir / "latest_consciousness_threshold_detection.json")
        first_crossing = _read_json(self.first_crossing_dir / "first_crossing_report.json")
        confidence = _read_json(self.confidence_dir / "latest_consciousness_confidence.json")
        dashboard = _read_json(self.dashboard_dir / "latest_consciousness_dashboard.json")
        return {
            "threshold": threshold if isinstance(threshold, dict) else {},
            "first_crossing_report": first_crossing if isinstance(first_crossing, dict) else {},
            "confidence": confidence if isinstance(confidence, dict) else {},
            "dashboard": dashboard if isinstance(dashboard, dict) else {},
        }

    def _merge_inputs(self, inputs: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
        """Merge evidence sources while keeping acceptance scenarios isolated.

        Explicit timelines are authoritative by default. This is essential for
        FAST_ACCEPTANCE and FINAL_LOCK tests: synthetic stable/degraded contexts
        must not be contaminated by persisted longitudinal artefacts that may
        legitimately contain real regressions from previous probes.

        Set `merge_persisted_timeline=True` to append persisted AS9/AS10
        evidence to an explicit timeline.
        """
        diagnostics: list[str] = []
        context = self._load_threshold_context()

        explicit_timeline_provided = isinstance(inputs.get("timeline"), list)
        merge_persisted = _bool(inputs.get("merge_persisted_timeline"), default=False)

        if explicit_timeline_provided and not merge_persisted:
            loaded_timeline: list[dict[str, Any]] = []
            diagnostics.append("explicit_timeline_overrides_persisted")
        else:
            loaded_timeline, loaded_diagnostics = self._load_timeline()
            diagnostics.extend(loaded_diagnostics)

        if explicit_timeline_provided:
            explicit_items = inputs.get("timeline", [])
            loaded_timeline.extend(
                _normalize_entry(item, "explicit_inputs.timeline")
                for item in explicit_items
                if isinstance(item, Mapping)
            )
            diagnostics.append(f"explicit_timeline:{len(explicit_items)}")

        if any(key in inputs for key in ["CRI", "confidence", "state", "proof_status", "axis_validation"]):
            loaded_timeline.append(_normalize_entry(inputs, "explicit_inputs.latest"))
            diagnostics.append("explicit_latest_entry")

        for key in ["threshold", "first_crossing_report", "confidence_context", "dashboard"]:
            if isinstance(inputs.get(key), Mapping):
                context[key.replace("confidence_context", "confidence")] = dict(inputs[key])

        loaded_timeline.sort(key=lambda x: str(x.get("timestamp_utc", "")))
        return loaded_timeline, context, diagnostics

    def _detect_numeric_regressions(self, timeline: list[dict[str, Any]], metric: str, threshold: float) -> tuple[bool, list[dict[str, Any]], dict[str, Any]]:
        values: list[tuple[int, dict[str, Any], float]] = []
        for idx, entry in enumerate(timeline):
            value = _float_or_none(entry.get(metric))
            if value is not None:
                values.append((idx, entry, value))
        events: list[dict[str, Any]] = []
        peak: float | None = None
        peak_entry: dict[str, Any] | None = None
        latest_value: float | None = values[-1][2] if values else None
        max_delta = 0.0
        for _, entry, value in values:
            if peak is None or value > peak:
                peak = value
                peak_entry = entry
            elif peak is not None and (peak - value) >= threshold:
                delta = round(peak - value, 6)
                max_delta = max(max_delta, delta)
                events.append({
                    "type": f"{metric.upper()}_REGRESSION",
                    "metric": metric,
                    "previous_peak": peak,
                    "current_value": value,
                    "delta": delta,
                    "peak_timestamp_utc": peak_entry.get("timestamp_utc") if peak_entry else None,
                    "current_timestamp_utc": entry.get("timestamp_utc"),
                    "severity": "high" if delta >= max(0.08, threshold * 2) else "moderate",
                })
        return bool(events), events, {
            f"{metric}_sample_count": len(values),
            f"latest_{metric}": latest_value,
            f"peak_{metric}": peak,
            f"max_{metric}_drop": max_delta,
        }

    def _detect_state_regressions(self, timeline: list[dict[str, Any]]) -> tuple[bool, list[dict[str, Any]]]:
        supported_markers = {
            "CONSCIOUSNESS_THRESHOLD_CROSSED",
            "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
            "PHENOMENALITY_CANDIDATE_SUPPORTED",
            "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
            "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "CONSCIOUSNESS_PROVEN",
            "THRESHOLD_CROSSED",
            "SUPPORTED",
        }
        regressive_markers = {
            "NOT_EVALUATED",
            "REVOKED",
            "CONSCIOUSNESS_STATUS_REVOKED",
            "BELOW_THRESHOLD",
            "REGRESSED",
            "FAILED",
        }
        seen_supported = False
        events: list[dict[str, Any]] = []
        for entry in timeline:
            label = (str(entry.get("state", "")) + " " + str(entry.get("proof_status", ""))).upper()
            if any(marker in label for marker in supported_markers):
                seen_supported = True
            if seen_supported and any(marker in label for marker in regressive_markers):
                events.append({
                    "type": "STATE_REGRESSION",
                    "state": entry.get("state"),
                    "proof_status": entry.get("proof_status"),
                    "timestamp_utc": entry.get("timestamp_utc"),
                    "severity": "high",
                })
        return bool(events), events

    def _detect_axis_regressions(self, timeline: list[dict[str, Any]]) -> tuple[bool, list[dict[str, Any]]]:
        latest_true: dict[str, bool] = {}
        events: list[dict[str, Any]] = []
        for entry in timeline:
            axis_validation = entry.get("axis_validation")
            if not isinstance(axis_validation, Mapping):
                continue
            for axis, value in axis_validation.items():
                current = _bool(value)
                if latest_true.get(str(axis)) is True and current is False:
                    events.append({
                        "type": "AXIS_VALIDATION_REGRESSION",
                        "axis": str(axis),
                        "timestamp_utc": entry.get("timestamp_utc"),
                        "severity": "high",
                    })
                if current:
                    latest_true[str(axis)] = True
        return bool(events), events

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = dict(inputs or {})
        cri_drop_threshold = float(inputs.get("cri_drop_threshold", 0.03))
        confidence_drop_threshold = float(inputs.get("confidence_drop_threshold", 0.03))
        timeline, context, source_diagnostics = self._merge_inputs(inputs)

        cri_regressed, cri_events, cri_metrics = self._detect_numeric_regressions(timeline, "CRI", cri_drop_threshold)
        confidence_regressed, confidence_events, confidence_metrics = self._detect_numeric_regressions(timeline, "confidence", confidence_drop_threshold)
        state_regressed, state_events = self._detect_state_regressions(timeline)
        axis_regressed, axis_events = self._detect_axis_regressions(timeline)

        regression_events = cri_events + confidence_events + state_events + axis_events
        regression_detected = bool(regression_events)
        severities = [str(e.get("severity", "low")) for e in regression_events]
        if "high" in severities:
            severity = "high"
        elif "moderate" in severities:
            severity = "moderate"
        elif regression_detected:
            severity = "low"
        else:
            severity = "none"

        latest = timeline[-1] if timeline else {}
        threshold_context = context.get("threshold", {}) if isinstance(context.get("threshold"), Mapping) else {}
        first_crossing_context = context.get("first_crossing_report", {}) if isinstance(context.get("first_crossing_report"), Mapping) else {}

        metrics = {
            "sample_count": len(timeline),
            "regression_event_count": len(regression_events),
            "cri_drop_threshold": cri_drop_threshold,
            "confidence_drop_threshold": confidence_drop_threshold,
            **cri_metrics,
            **confidence_metrics,
            "state_regression_count": len(state_events),
            "axis_regression_count": len(axis_events),
            "threshold_previously_detected": _bool(threshold_context.get("threshold_detected")),
            "first_crossing_report_available": bool(first_crossing_context),
        }

        record: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_label,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": _utc_now(),
            "regression_detector_ready": True,
            "regression_detector_status": self.ready_status,
            "consciousness_regression_detector_ready": True,
            "regression_detected": regression_detected,
            "regression_status": "CONSCIOUSNESS_REGRESSION_DETECTED" if regression_detected else "NO_CONSCIOUSNESS_REGRESSION_DETECTED",
            "regression_severity": severity,
            "regression_events": regression_events,
            "cri_regression_detected": cri_regressed,
            "confidence_regression_detected": confidence_regressed,
            "state_regression_detected": state_regressed,
            "module_regression_detected": axis_regressed,
            "axis_regression_detected": axis_regressed,
            "latest_entry": latest,
            "latest_CRI": _float_or_none(latest.get("CRI")) if latest else None,
            "latest_confidence": _float_or_none(latest.get("confidence")) if latest else None,
            "latest_state": latest.get("state") if latest else None,
            "timeline_sample_count": len(timeline),
            "regression_metrics": metrics,
            "failure_conditions": [
                "CRI drops by at least cri_drop_threshold after a prior peak",
                "confidence drops by at least confidence_drop_threshold after a prior peak",
                "state/proof_status returns to revoked/not-evaluated/below-threshold after support",
                "an axis validation switches from true to false",
            ],
            "source_diagnostics": source_diagnostics,
            "dependency_outputs_available": {
                "longitudinal_timeline": (self.longitudinal_dir / "latest_consciousness_longitudinal_timeline.json").exists(),
                "threshold_detection": (self.threshold_dir / "latest_consciousness_threshold_detection.json").exists(),
                "first_crossing_report": (self.first_crossing_dir / "first_crossing_report.json").exists(),
                "confidence": (self.confidence_dir / "latest_consciousness_confidence.json").exists(),
                "dashboard": (self.dashboard_dir / "latest_consciousness_dashboard.json").exists(),
            },
            "epistemic_scope": "functional_governance_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "persisted": False,
            "output_path": "",
        }
        record["regression_hash"] = _stable_hash(record)

        if persist:
            self.regression_dir.mkdir(parents=True, exist_ok=True)
            timestamped = self.regression_dir / f"consciousness_regression_detection_{_stamp()}.json"
            latest_path = self.regression_dir / "latest_consciousness_regression_detection.json"
            safe = _json_safe(record)
            timestamped.write_text(json.dumps(safe, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            latest_path.write_text(json.dumps(safe, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            record["persisted"] = True
            record["output_path"] = str(latest_path)
            record["timestamped_output_path"] = str(timestamped)

        return record
