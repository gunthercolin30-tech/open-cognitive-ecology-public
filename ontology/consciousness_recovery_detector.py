"""
AS14 — consciousness_recovery_detector

Detect governed recovery after a previously detected functional regression.
The detector consumes persisted AS9/AS11/AS13 artefacts and/or explicit inputs,
identifies recovery conditions, and emits a recoverability record suitable for
AS15 stability analysis.

Epistemic scope: longitudinal functional governance only. This module never
proves consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
LONGITUDINAL_DIR = GOVERNANCE_DIR / "longitudinal"
THRESHOLD_DIR = GOVERNANCE_DIR / "threshold"
REGRESSION_DIR = GOVERNANCE_DIR / "regression"
RECOVERY_DIR = GOVERNANCE_DIR / "recovery"
CONFIDENCE_DIR = GOVERNANCE_DIR / "confidence"
DASHBOARD_DIR = GOVERNANCE_DIR / "dashboard"


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
        return value.strip().lower() in {"true", "1", "yes", "ok", "ready", "validated", "detected", "supported", "complete"}
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
    }


def _axis_all_valid(axis_validation: Mapping[str, Any]) -> bool:
    required = ["AP", "AQ", "AR", "AN", "AO", "AL"]
    return all(_bool(axis_validation.get(axis)) for axis in required)


def _label_has_any(entry: Mapping[str, Any], markers: set[str]) -> bool:
    label = (str(entry.get("state", "")) + " " + str(entry.get("proof_status", ""))).upper()
    return any(marker in label for marker in markers)


class ConsciousnessRecoveryDetector:
    """AS14 recovery detector for governed functional consciousness status."""

    primitive = "CONSCIOUSNESS_RECOVERY_DETECTOR"
    step_label = "AS14"
    public_schema_version = "1.0.0"
    ready_status = "CONSCIOUSNESS_RECOVERY_DETECTOR_READY"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.governance_dir = self.root / "consciousness_governance"
        self.longitudinal_dir = self.governance_dir / "longitudinal"
        self.threshold_dir = self.governance_dir / "threshold"
        self.regression_dir = self.governance_dir / "regression"
        self.recovery_dir = self.governance_dir / "recovery"
        self.confidence_dir = self.governance_dir / "confidence"
        self.dashboard_dir = self.governance_dir / "dashboard"

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

    def _load_context(self) -> dict[str, Any]:
        regression = _read_json(self.regression_dir / "latest_consciousness_regression_detection.json")
        threshold = _read_json(self.threshold_dir / "latest_consciousness_threshold_detection.json")
        confidence = _read_json(self.confidence_dir / "latest_consciousness_confidence.json")
        dashboard = _read_json(self.dashboard_dir / "latest_consciousness_dashboard.json")
        return {
            "regression": regression if isinstance(regression, dict) else {},
            "threshold": threshold if isinstance(threshold, dict) else {},
            "confidence": confidence if isinstance(confidence, dict) else {},
            "dashboard": dashboard if isinstance(dashboard, dict) else {},
        }

    def _merge_inputs(self, inputs: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
        diagnostics: list[str] = []
        context = self._load_context()
        explicit_timeline_provided = isinstance(inputs.get("timeline"), list)
        merge_persisted = _bool(inputs.get("merge_persisted_timeline"), default=False)

        if explicit_timeline_provided and not merge_persisted:
            timeline: list[dict[str, Any]] = []
            diagnostics.append("explicit_timeline_overrides_persisted")
        else:
            timeline, loaded_diagnostics = self._load_timeline()
            diagnostics.extend(loaded_diagnostics)

        # AS14 repair: explicit synthetic timelines used by fast/final locks must
        # not inherit persisted regression context unless explicitly requested.
        # This prevents false-positive recovery in the `no_prior` scenario while
        # preserving normal persisted-context behaviour for production calls.
        if explicit_timeline_provided and not merge_persisted and "regression_detected" not in inputs and not isinstance(inputs.get("regression"), Mapping):
            context["regression"] = {}
            diagnostics.append("explicit_timeline_regression_context_cleared")

        if explicit_timeline_provided:
            explicit_items = inputs.get("timeline", [])
            timeline.extend(
                _normalize_entry(item, "explicit_inputs.timeline")
                for item in explicit_items
                if isinstance(item, Mapping)
            )
            diagnostics.append(f"explicit_timeline:{len(explicit_items)}")

        if any(key in inputs for key in ["CRI", "confidence", "state", "proof_status", "axis_validation"]):
            timeline.append(_normalize_entry(inputs, "explicit_inputs.latest"))
            diagnostics.append("explicit_latest_entry")

        for key in ["regression", "threshold", "confidence_context", "dashboard"]:
            if isinstance(inputs.get(key), Mapping):
                context[key.replace("confidence_context", "confidence")] = dict(inputs[key])

        if "regression_detected" in inputs:
            context["regression"] = dict(context.get("regression", {}))
            context["regression"]["regression_detected"] = _bool(inputs.get("regression_detected"))

        timeline.sort(key=lambda x: str(x.get("timestamp_utc", "")))
        return timeline, context, diagnostics

    def _previous_regression(self, timeline: list[dict[str, Any]], context: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
        regression_context = context.get("regression", {}) if isinstance(context.get("regression"), Mapping) else {}
        if _bool(regression_context.get("regression_detected")):
            return True, {
                "source": "latest_regression_record",
                "event_count": regression_context.get("regression_metrics", {}).get("regression_event_count") if isinstance(regression_context.get("regression_metrics"), Mapping) else len(regression_context.get("regression_events", []) or []),
                "latest_state": regression_context.get("latest_state"),
                "latest_CRI": regression_context.get("latest_CRI"),
                "latest_confidence": regression_context.get("latest_confidence"),
            }

        regressive_markers = {"REGRESSED", "REVOKED", "BELOW_THRESHOLD", "FAILED", "NOT_EVALUATED"}
        for entry in timeline:
            if _label_has_any(entry, regressive_markers):
                return True, {
                    "source": "timeline_marker",
                    "timestamp_utc": entry.get("timestamp_utc"),
                    "state": entry.get("state"),
                    "proof_status": entry.get("proof_status"),
                }
        return False, {"source": "none"}

    def _latest_recovered(self, latest: Mapping[str, Any], context: Mapping[str, Any], inputs: Mapping[str, Any]) -> tuple[bool, dict[str, Any], list[str]]:
        missing: list[str] = []
        cri_threshold = float(inputs.get("cri_recovery_threshold", 0.95))
        confidence_threshold = float(inputs.get("confidence_recovery_threshold", 0.90))
        cri = _float_or_none(latest.get("CRI"))
        confidence = _float_or_none(latest.get("confidence"))
        axis_validation = latest.get("axis_validation") if isinstance(latest.get("axis_validation"), Mapping) else _extract_axis_validation(inputs)

        supported_markers = {
            "CONSCIOUSNESS_THRESHOLD_CROSSED",
            "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
            "PHENOMENALITY_CANDIDATE_SUPPORTED",
            "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
            "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "CONSCIOUSNESS_PROVEN",
            "SUPPORTED",
            "THRESHOLD_CROSSED",
        }
        regressive_markers = {"REGRESSED", "REVOKED", "BELOW_THRESHOLD", "FAILED", "NOT_EVALUATED"}

        if cri is None or cri < cri_threshold:
            missing.append("CRI")
        if confidence is None or confidence < confidence_threshold:
            missing.append("confidence")
        if not _axis_all_valid(axis_validation):
            missing.append("axis_validation")
        if _bool(inputs.get("revocation_required"), default=False):
            missing.append("revocation_not_required")
        if _label_has_any(latest, regressive_markers):
            missing.append("latest_state_not_regressive")
        if not _label_has_any(latest, supported_markers):
            threshold_context = context.get("threshold", {}) if isinstance(context.get("threshold"), Mapping) else {}
            if not _bool(threshold_context.get("threshold_detected")):
                missing.append("supported_or_threshold_state")

        metrics = {
            "cri_recovery_threshold": cri_threshold,
            "confidence_recovery_threshold": confidence_threshold,
            "latest_CRI": cri,
            "latest_confidence": confidence,
            "axis_validation_all_true": _axis_all_valid(axis_validation),
            "latest_state": latest.get("state"),
            "latest_proof_status": latest.get("proof_status"),
        }
        return not missing, metrics, missing

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timeline, context, source_diagnostics = self._merge_inputs(inputs)
        latest = timeline[-1] if timeline else _normalize_entry(inputs, "empty_or_explicit")
        previous_regression, previous_regression_details = self._previous_regression(timeline, context)
        latest_recovered, recovery_metrics, missing_conditions = self._latest_recovered(latest, context, inputs)

        recovery_detected = bool(previous_regression and latest_recovered)
        recovery_event_type = "CONSCIOUSNESS_STATUS_RECOVERED" if recovery_detected else "NO_CONSCIOUSNESS_STATUS_RECOVERY"
        recovery_event = {
            "type": recovery_event_type,
            "timestamp_utc": latest.get("timestamp_utc") or _utc_now(),
            "previous_regression": previous_regression,
            "latest_recovered": latest_recovered,
            "latest_CRI": recovery_metrics.get("latest_CRI"),
            "latest_confidence": recovery_metrics.get("latest_confidence"),
            "latest_state": recovery_metrics.get("latest_state"),
            "severity": "positive" if recovery_detected else "none",
        }

        record: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_label,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": _utc_now(),
            "recovery_detector_ready": True,
            "consciousness_recovery_detector_ready": True,
            "recovery_detector_status": self.ready_status,
            "recovery_detected": recovery_detected,
            "recovery_status": "CONSCIOUSNESS_STATUS_RECOVERED" if recovery_detected else "NO_CONSCIOUSNESS_STATUS_RECOVERY_DETECTED",
            "recovery_event_type": recovery_event_type,
            "recovery_event": recovery_event,
            "recovery_events": [recovery_event] if recovery_detected else [],
            "previous_regression_detected": previous_regression,
            "previous_regression_details": previous_regression_details,
            "latest_recovered": latest_recovered,
            "latest_entry": latest,
            "latest_CRI": recovery_metrics.get("latest_CRI"),
            "latest_confidence": recovery_metrics.get("latest_confidence"),
            "latest_state": recovery_metrics.get("latest_state"),
            "timeline_sample_count": len(timeline),
            "recovery_metrics": {
                **recovery_metrics,
                "sample_count": len(timeline),
                "missing_condition_count": len(missing_conditions),
            },
            "missing_conditions": missing_conditions,
            "failure_conditions": [
                "No prior regression was detected in AS13 or timeline markers",
                "Latest CRI remains below cri_recovery_threshold",
                "Latest confidence remains below confidence_recovery_threshold",
                "Required axis validations are not all true",
                "Latest state still carries a regressive marker",
                "Revocation remains required",
            ],
            "source_diagnostics": source_diagnostics,
            "dependency_outputs_available": {
                "regression_detection": (self.regression_dir / "latest_consciousness_regression_detection.json").exists(),
                "longitudinal_timeline": (self.longitudinal_dir / "latest_consciousness_longitudinal_timeline.json").exists(),
                "threshold_detection": (self.threshold_dir / "latest_consciousness_threshold_detection.json").exists(),
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
        record["recovery_hash"] = _stable_hash(record)

        if persist:
            self.recovery_dir.mkdir(parents=True, exist_ok=True)
            timestamped = self.recovery_dir / f"consciousness_recovery_detection_{_stamp()}.json"
            latest_path = self.recovery_dir / "latest_consciousness_recovery_detection.json"
            safe = _json_safe(record)
            timestamped.write_text(json.dumps(safe, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            latest_path.write_text(json.dumps(safe, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            record["persisted"] = True
            record["output_path"] = str(latest_path)
            record["timestamped_output_path"] = str(timestamped)

        return record
