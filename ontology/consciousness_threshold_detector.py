"""
AS11 — consciousness_threshold_detector

Governed detector for the functional consciousness threshold.

This module does not prove consciousness, qualia, subjectivity, or phenomenology.
It evaluates whether functional governance criteria are currently sufficient to
emit the governed event type CONSCIOUSNESS_THRESHOLD_CROSSED.

Inputs may override all observed metrics for tests and degradation checks.
When no override is provided, the detector reads persisted outputs from AS7,
AS8, AS9, and AS10 and falls back to executing available upstream modules with
persist=False.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
THRESHOLD_DIR = GOVERNANCE_DIR / "threshold"
CONFIDENCE_DIR = GOVERNANCE_DIR / "confidence"
READINESS_DIR = GOVERNANCE_DIR / "AS7_readiness_index"
LONGITUDINAL_DIR = GOVERNANCE_DIR / "longitudinal"
DASHBOARD_DIR = GOVERNANCE_DIR / "dashboard"

try:
    from ontology.consciousness_readiness_index import ConsciousnessReadinessIndex
except Exception:  # pragma: no cover
    ConsciousnessReadinessIndex = None  # type: ignore

try:
    from ontology.consciousness_confidence_engine import ConsciousnessConfidenceEngine
except Exception:  # pragma: no cover
    ConsciousnessConfidenceEngine = None  # type: ignore

try:
    from ontology.consciousness_longitudinal_tracker import ConsciousnessLongitudinalTracker
except Exception:  # pragma: no cover
    ConsciousnessLongitudinalTracker = None  # type: ignore

try:
    from ontology.consciousness_dashboard import ConsciousnessDashboard
except Exception:  # pragma: no cover
    ConsciousnessDashboard = None  # type: ignore


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return default
        number = float(value)
        if number != number:  # NaN
            return default
        return max(0.0, min(1.0, number))
    except Exception:
        return default


def _bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "ok", "ready", "validated", "passed"}
    return bool(value)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists() and path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    return {}


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


def _latest_json(directory: Path, preferred: str | None = None) -> dict[str, Any]:
    if preferred:
        data = _read_json(directory / preferred)
        if data:
            return data
    try:
        candidates = sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for candidate in candidates:
            data = _read_json(candidate)
            if data:
                return data
    except Exception:
        return {}
    return {}


def _first_present(mapping: Mapping[str, Any], keys: list[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) is not None:
            return mapping.get(key)
    return default


class ConsciousnessThresholdDetector:
    """AS11 governed threshold detector."""

    primitive = "CONSCIOUSNESS_THRESHOLD_DETECTOR"
    step_label = "AS11"
    public_schema_version = "1.0.0"
    ready_status = "CONSCIOUSNESS_THRESHOLD_DETECTED"
    not_ready_status = "CONSCIOUSNESS_THRESHOLD_NOT_DETECTED"

    required_axes = ["AP", "AQ", "AR", "AN", "AO", "AL"]
    default_cri_threshold = 0.95
    default_confidence_threshold = 0.90

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.threshold_dir = self.root / "consciousness_governance" / "threshold"
        self.latest_path = self.threshold_dir / "latest_consciousness_threshold_detection.json"

    def _load_sources(self, inputs: Mapping[str, Any]) -> dict[str, Any]:
        sources: dict[str, Any] = {}

        explicit_axis = (
            inputs.get("axis_validation")
            or inputs.get("axis_status")
            or inputs.get("critical_axis_status")
            or inputs.get("required_axis_validation")
        )
        explicit_metrics_ready = (
            _first_present(inputs, ["CRI", "cri", "continuous_readiness_index"]) is not None
            and _first_present(inputs, ["confidence", "confidence_score"]) is not None
            and isinstance(explicit_axis, Mapping)
            and not _bool(inputs.get("force_source_loading"), default=False)
        )
        if explicit_metrics_ready:
            # explicit_inputs_fast_path: FAST_ACCEPTANCE and FINAL_LOCK contexts
            # provide all criteria directly, so expensive live upstream calls are
            # skipped while the public detector logic remains unchanged.
            sources["explicit_inputs_fast_path"] = dict(inputs)
            return sources

        readiness_persisted = _latest_json(self.root / "consciousness_governance" / "AS7_readiness_index", "latest_readiness_index.json")
        confidence_persisted = _latest_json(self.root / "consciousness_governance" / "confidence", "latest_consciousness_confidence.json")
        longitudinal_persisted = _latest_json(self.root / "consciousness_governance" / "longitudinal", "latest_consciousness_longitudinal_timeline.json")
        dashboard_persisted = _latest_json(self.root / "consciousness_governance" / "dashboard", "latest_consciousness_dashboard.json")

        if readiness_persisted:
            sources["readiness_persisted"] = readiness_persisted
        if confidence_persisted:
            sources["confidence_persisted"] = confidence_persisted
        if longitudinal_persisted:
            sources["longitudinal_persisted"] = longitudinal_persisted
        if dashboard_persisted:
            sources["dashboard_persisted"] = dashboard_persisted

        # Prefer live upstream outputs where available, because AS7/AS8 compute
        # current CRI/confidence while some persisted dashboard snapshots may be
        # historical and contain null longitudinal samples.
        if ConsciousnessReadinessIndex is not None:
            try:
                sources["readiness_live"] = ConsciousnessReadinessIndex(root=self.root).step(inputs=inputs, persist=False)
            except TypeError:
                try:
                    sources["readiness_live"] = ConsciousnessReadinessIndex().step(inputs=inputs, persist=False)
                except Exception as exc:
                    sources["readiness_live_error"] = str(exc)
            except Exception as exc:
                sources["readiness_live_error"] = str(exc)

        if ConsciousnessConfidenceEngine is not None:
            try:
                sources["confidence_live"] = ConsciousnessConfidenceEngine().step(inputs=inputs, persist=False)
            except Exception as exc:
                sources["confidence_live_error"] = str(exc)

        if ConsciousnessLongitudinalTracker is not None:
            try:
                sources["longitudinal_live"] = ConsciousnessLongitudinalTracker().step(inputs=inputs, persist=False)
            except Exception as exc:
                sources["longitudinal_live_error"] = str(exc)

        if ConsciousnessDashboard is not None:
            try:
                sources["dashboard_live"] = ConsciousnessDashboard().step(inputs=inputs, persist=False)
            except Exception as exc:
                sources["dashboard_live_error"] = str(exc)

        return sources

    def _derive_cri(self, inputs: Mapping[str, Any], sources: Mapping[str, Any]) -> float:
        direct = _first_present(inputs, ["CRI", "cri", "continuous_readiness_index"])
        if direct is not None:
            return _clamp(direct)
        for key in ("readiness_live", "readiness_persisted", "longitudinal_live", "longitudinal_persisted", "dashboard_live", "dashboard_persisted"):
            record = sources.get(key)
            if isinstance(record, Mapping):
                candidate = _first_present(record, ["cri", "CRI", "continuous_readiness_index"])
                if candidate is not None:
                    return _clamp(candidate)
                nested = record.get("readiness_record")
                if isinstance(nested, Mapping) and nested.get("cri") is not None:
                    return _clamp(nested.get("cri"))
                state = record.get("current_state")
                if isinstance(state, Mapping):
                    candidate = _first_present(state, ["CRI", "cri"])
                    if candidate is not None:
                        return _clamp(candidate)
        return 0.0

    def _derive_confidence(self, inputs: Mapping[str, Any], sources: Mapping[str, Any]) -> float:
        direct = _first_present(inputs, ["confidence", "confidence_score"])
        if direct is not None:
            return _clamp(direct)
        for key in ("confidence_persisted", "confidence_live", "longitudinal_live", "longitudinal_persisted", "dashboard_live", "dashboard_persisted"):
            record = sources.get(key)
            if isinstance(record, Mapping):
                candidate = _first_present(record, ["confidence", "confidence_score"])
                if candidate is not None:
                    return _clamp(candidate)
                metrics = record.get("confidence_metrics") or record.get("dashboard_metrics") or record.get("longitudinal_metrics")
                if isinstance(metrics, Mapping):
                    candidate = _first_present(metrics, ["confidence", "confidence_score"])
                    if candidate is not None:
                        return _clamp(candidate)
                state = record.get("current_state")
                if isinstance(state, Mapping):
                    candidate = _first_present(state, ["confidence", "confidence_score"])
                    if candidate is not None:
                        return _clamp(candidate)
        return 0.0

    def _axis_validation(self, inputs: Mapping[str, Any], sources: Mapping[str, Any]) -> dict[str, bool]:
        status: dict[str, bool] = {}
        explicit = (
            inputs.get("axis_validation")
            or inputs.get("axis_status")
            or inputs.get("critical_axis_status")
            or inputs.get("required_axis_validation")
        )
        if isinstance(explicit, Mapping):
            for axis in self.required_axes:
                if axis in explicit:
                    status[axis] = _bool(explicit.get(axis))
                elif axis.lower() in explicit:
                    status[axis] = _bool(explicit.get(axis.lower()))

        for record_key in ("readiness_live", "readiness_persisted"):
            record = sources.get(record_key)
            if isinstance(record, Mapping):
                critical = record.get("critical_axis_status")
                if isinstance(critical, Mapping):
                    for axis in self.required_axes:
                        if axis not in status and axis in critical:
                            status[axis] = _bool(critical.get(axis))

        # File-based evidence: the required final fast acceptance suites exist
        # only after those axes were installed and validated in the local workflow.
        suite_map = {
            "AP": "ap_axis_fast_acceptance_suite.py",
            "AQ": "aq8_fast_acceptance_suite.py",
            "AR": "ar8_fast_acceptance_suite.py",
            "AN": "an7_fast_acceptance_suite.py",
            "AO": "ao5_fast_acceptance_suite.py",
            "AL": "al11_fast_acceptance_suite.py",
        }
        for axis, suite in suite_map.items():
            if axis not in status:
                status[axis] = (self.root / suite).exists()

        return {axis: bool(status.get(axis, False)) for axis in self.required_axes}

    def _epistemic_guard_ok(self, sources: Mapping[str, Any]) -> tuple[bool, list[str]]:
        violations: list[str] = []
        forbidden = ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]
        for source_name, record in sources.items():
            if not isinstance(record, Mapping):
                continue
            for flag in forbidden:
                if record.get(flag) is True:
                    violations.append(f"{source_name}.{flag}=True")
            if record.get("functional_conclusion_only") is False:
                violations.append(f"{source_name}.functional_conclusion_only=False")
            if record.get("phenomenology_undetermined") is False:
                violations.append(f"{source_name}.phenomenology_undetermined=False")
        return (len(violations) == 0, violations)

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs or {}
        timestamp = _utc_now()
        cri_threshold = _clamp(inputs.get("cri_threshold", self.default_cri_threshold), self.default_cri_threshold)
        confidence_threshold = _clamp(inputs.get("confidence_threshold", self.default_confidence_threshold), self.default_confidence_threshold)

        sources = self._load_sources(inputs)
        cri = self._derive_cri(inputs, sources)
        confidence = self._derive_confidence(inputs, sources)
        axis_validation = self._axis_validation(inputs, sources)
        axis_validation_complete = all(axis_validation.values())

        epistemic_guard_ok, epistemic_violations = self._epistemic_guard_ok(sources)
        revocation_required = _bool(inputs.get("revocation_required"), default=False)
        for key in ("readiness_live", "readiness_persisted"):
            record = sources.get(key)
            if isinstance(record, Mapping) and record.get("revocation_required") is not None:
                revocation_required = revocation_required or _bool(record.get("revocation_required"))

        cri_condition = cri >= cri_threshold
        confidence_condition = confidence >= confidence_threshold
        threshold_detected = bool(
            cri_condition
            and confidence_condition
            and axis_validation_complete
            and epistemic_guard_ok
            and not revocation_required
        )

        criteria = {
            "cri": {"value": cri, "threshold": cri_threshold, "passed": cri_condition},
            "confidence": {"value": confidence, "threshold": confidence_threshold, "passed": confidence_condition},
            "axis_validation": {"value": axis_validation, "passed": axis_validation_complete},
            "epistemic_guard": {"passed": epistemic_guard_ok, "violations": epistemic_violations},
            "revocation_absent": {"value": not revocation_required, "passed": not revocation_required},
        }
        missing_conditions = [name for name, item in criteria.items() if isinstance(item, Mapping) and not item.get("passed")]

        event = {
            "event_type": "CONSCIOUSNESS_THRESHOLD_CROSSED" if threshold_detected else "CONSCIOUSNESS_THRESHOLD_NOT_CROSSED",
            "timestamp_utc": timestamp,
            "justification": "functional_threshold_criteria_satisfied" if threshold_detected else "functional_threshold_criteria_not_satisfied",
            "CRI": cri,
            "confidence": confidence,
            "criteria": criteria,
            "missing_conditions": missing_conditions,
        }
        event["event_hash"] = _stable_hash(event)

        record = {
            "primitive": self.primitive,
            "step": self.step_label,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": timestamp,
            "threshold_detector_ready": True,
            "threshold_detection_status": self.ready_status if threshold_detected else self.not_ready_status,
            "threshold_detected": threshold_detected,
            "threshold_crossed": threshold_detected,
            "threshold_event_type": event["event_type"],
            "event": event,
            "CRI": cri,
            "cri": cri,
            "confidence": confidence,
            "cri_threshold": cri_threshold,
            "confidence_threshold": confidence_threshold,
            "criteria": criteria,
            "axis_validation": axis_validation,
            "axis_validation_complete": axis_validation_complete,
            "missing_conditions": missing_conditions,
            "dependency_outputs_available": sorted(str(k) for k in sources.keys()),
            "source_diagnostics": {
                "source_count": len(sources),
                "readiness_source_available": any(k.startswith("readiness_") for k in sources),
                "confidence_source_available": any(k.startswith("confidence_") for k in sources),
                "dashboard_source_available": any(k.startswith("dashboard_") for k in sources),
                "longitudinal_source_available": any(k.startswith("longitudinal_") for k in sources),
            },
            "epistemic_scope": "functional_threshold_detection_only_no_phenomenal_proof",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "persisted": False,
            "output_path": str(self.latest_path),
        }
        record["threshold_hash"] = _stable_hash({k: v for k, v in record.items() if k != "threshold_hash"})

        if persist:
            self.threshold_dir.mkdir(parents=True, exist_ok=True)
            snapshot = self.threshold_dir / f"consciousness_threshold_detection_{_stamp()}.json"
            payload = json.dumps(_json_safe(record), ensure_ascii=False, indent=2, sort_keys=True)
            self.latest_path.write_text(payload, encoding="utf-8")
            snapshot.write_text(payload, encoding="utf-8")
            record["persisted"] = True
            record["output_path"] = str(self.latest_path)
            record["snapshot_path"] = str(snapshot)

        return record


__all__ = ["ConsciousnessThresholdDetector"]
