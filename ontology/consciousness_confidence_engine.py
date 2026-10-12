"""
AS8 — Consciousness Confidence Engine.

Computes a longitudinal, auditable confidence score for the functional
consciousness governance stack. The score is explicitly epistemically guarded:
it is a functional/scientific confidence metric only and never a proof of
phenomenal subjectivity, qualia, or consciousness.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

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


def _bool_score(value: Any) -> float:
    return 1.0 if value is True else 0.0


def _mean(values: list[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    return round(sum(vals) / len(vals), 6) if vals else default


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists() and path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {}


def _stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _call_dependency(module_name: str, class_name: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        module = __import__(f"ontology.{module_name}", fromlist=[class_name])
        cls = getattr(module, class_name)
        instance = cls()
        result = instance.step(inputs=inputs or {}, persist=False)
        return result if isinstance(result, dict) else {"non_dict_result": repr(result)}
    except Exception as exc:
        return {"dependency_error": type(exc).__name__, "message": str(exc), "dependency": module_name}





def _json_safe(value):
    """Return a JSON-serializable representation without altering public semantics."""
    from pathlib import Path as _Path
    import dataclasses as _dataclasses

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, _Path):
        return str(value)
    if isinstance(value, dict):
        return {str(_json_safe(k)): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(v) for v in value]
    if _dataclasses.is_dataclass(value):
        return _json_safe(_dataclasses.asdict(value))
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


class ConsciousnessConfidenceEngine:
    """AS8 confidence synthesis over readiness, evidence, coherence and history."""

    primitive = "CONSCIOUSNESS_CONFIDENCE_ENGINE"
    step = "AS8"
    public_schema_version = "1.0.0"
    READY_STATUS = "CONSCIOUSNESS_CONFIDENCE_ENGINE_READY"

    weights = {
        "stability": 0.18,
        "replications": 0.16,
        "countermodels": 0.14,
        "completeness": 0.20,
        "coherence": 0.17,
        "historical": 0.15,
    }

    epistemic_flags = {
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
    }

    def _load_real_reports(self) -> dict[str, Any]:
        return {
            "scientific_validation_report": _safe_read_json(ROOT / "scientific_validation_report.json"),
            "latest_state": _safe_read_json(ROOT / "civilizational_state" / "latest_state.json"),
            "runtime_service_state": _safe_read_json(ROOT / "runtime_service" / "service_state.json"),
        }

    def _count_historical_files(self) -> dict[str, int]:
        roots = [
            ROOT / "runtime_experiments",
            ROOT / "external_validation",
            ROOT / "publication_archive",
            ROOT / "civilizational_memory_archive",
            ROOT / "conversation_memory_archive",
            ROOT / "web_dashboard_exports",
        ]
        counts: dict[str, int] = {}
        for r in roots:
            key = r.name
            try:
                counts[key] = sum(1 for p in r.rglob("*") if p.is_file()) if r.exists() else 0
            except Exception:
                counts[key] = 0
        return counts

    def _gather_dependencies(self, inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
        provided = inputs.get("dependency_outputs", {}) if isinstance(inputs.get("dependency_outputs", {}), dict) else {}
        deps = dict(provided)
        dependency_specs = {
            "readiness": ("consciousness_readiness_index", "ConsciousnessReadinessIndex"),
            "transition_history": ("consciousness_transition_history", "ConsciousnessTransitionHistory"),
            "event_logger": ("consciousness_event_logger", "ConsciousnessEventLogger"),
            "revocation": ("consciousness_revocation_engine", "ConsciousnessRevocationEngine"),
            "certificate": ("consciousness_certificate_generator", "ConsciousnessCertificateGenerator"),
            "state_machine": ("consciousness_state_machine", "ConsciousnessStateMachine"),
            "axiomatic_completeness": ("axiomatic_completeness_certifier", "AxiomaticCompletenessCertifier"),
            "semantic_revision": ("semantic_revision_log", "SemanticRevisionLog"),
            "final_dashboard": ("final_dashboard", "FinalDashboard"),
            "final_theoretical_report": ("final_theoretical_report", "FinalTheoreticalReport"),
        }
        if inputs.get("skip_dependency_calls") is True:
            return deps
        for key, (module_name, class_name) in dependency_specs.items():
            if key not in deps:
                deps[key] = _call_dependency(module_name, class_name, inputs.get(key, {}))
        return deps

    def _component_stability(self, deps: dict[str, dict[str, Any]], inputs: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        transition = deps.get("transition_history", {})
        event = deps.get("event_logger", {})
        revocation = deps.get("revocation", {})
        readiness = deps.get("readiness", {})
        scores = [
            _bool_score(transition.get("history_ready")),
            _bool_score(transition.get("append_only")),
            1.0 - _bool_score(revocation.get("revocation_required")),
            1.0 - _bool_score(revocation.get("revoked")),
            _bool_score(event.get("event_logger_ready")),
            _clamp(readiness.get("cri", readiness.get("continuous_readiness_index", inputs.get("cri", 0.0)))),
        ]
        return _mean(scores), {
            "transition_history_ready": transition.get("history_ready"),
            "append_only": transition.get("append_only"),
            "revocation_required": revocation.get("revocation_required"),
            "revoked": revocation.get("revoked"),
            "event_logger_ready": event.get("event_logger_ready"),
        }

    def _component_replications(self, reports: dict[str, Any], inputs: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        validation = reports.get("scientific_validation_report", {}) if isinstance(reports, dict) else {}
        diagnostics = validation.get("diagnostics", {}) if isinstance(validation.get("diagnostics", {}), dict) else {}
        tests = validation.get("tests", []) if isinstance(validation.get("tests", []), list) else []
        if "replication_score" in inputs:
            base = _clamp(inputs.get("replication_score"))
        elif validation:
            error_score = 1.0 if diagnostics.get("error_count", 0) == 0 and diagnostics.get("failed_calls", 0) == 0 else 0.0
            test_score = _mean([_bool_score(t.get("passed")) for t in tests], default=1.0 if validation.get("overall_success") is True else 0.0)
            base = _mean([_bool_score(validation.get("overall_success")), error_score, test_score])
        else:
            base = _clamp(inputs.get("replication_score", 0.75))
        return base, {"validation_diagnostics": diagnostics, "validation_tests": len(tests), "overall_success": validation.get("overall_success")}

    def _component_countermodels(self, deps: dict[str, dict[str, Any]], inputs: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        ax = deps.get("axiomatic_completeness", {})
        if "countermodel_score" in inputs:
            score = _clamp(inputs.get("countermodel_score"))
        else:
            countermodel_necessity = None
            criterion_scores = ax.get("criterion_scores", {}) if isinstance(ax.get("criterion_scores", {}), dict) else {}
            if "countermodel_necessity" in criterion_scores:
                countermodel_necessity = criterion_scores.get("countermodel_necessity")
            unresolved = ax.get("redundant_proof_paths", [])
            redundancy_penalty = 0.0 if not unresolved else 0.15
            score = _clamp((countermodel_necessity if countermodel_necessity is not None else 0.85) - redundancy_penalty)
        return score, {"axiomatic_status": ax.get("axiomatic_completeness_status"), "criterion_scores": ax.get("criterion_scores", {})}

    def _component_completeness(self, deps: dict[str, dict[str, Any]], inputs: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        readiness = deps.get("readiness", {})
        ax = deps.get("axiomatic_completeness", {})
        sem = deps.get("semantic_revision", {})
        final_report = deps.get("final_theoretical_report", {})
        final_dashboard = deps.get("final_dashboard", {})
        scores = [
            _clamp(readiness.get("cri", readiness.get("continuous_readiness_index", inputs.get("cri", 0.0)))),
            _clamp(readiness.get("critical_completeness", 0.0)),
            _clamp(readiness.get("theoretical_completeness", 0.0)),
            _clamp(readiness.get("governance_completeness", 0.0)),
            _clamp(ax.get("completeness_score", 1.0 if ax.get("axiomatic_completeness_status") == "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED" else 0.75)),
            _bool_score(sem.get("semantic_interpretation_layer_step_ready", sem.get("semantic_interpretation_layer_ready"))),
            _bool_score(final_dashboard.get("dashboard_ready")),
            _bool_score(final_report.get("report_ready")),
        ]
        return _mean(scores), {
            "readiness_status": readiness.get("readiness_index_status"),
            "critical_axis_status": readiness.get("critical_axis_status", {}),
            "axiomatic_status": ax.get("axiomatic_completeness_status"),
            "final_axis_status": final_report.get("final_axis_status"),
        }

    def _component_coherence(self, deps: dict[str, dict[str, Any]]) -> tuple[float, dict[str, Any]]:
        checked = []
        violations = []
        for name, result in deps.items():
            if not isinstance(result, dict):
                continue
            for flag, expected in self.epistemic_flags.items():
                if flag in result:
                    ok = result.get(flag) is expected
                    checked.append(1.0 if ok else 0.0)
                    if not ok:
                        violations.append({"dependency": name, "flag": flag, "value": result.get(flag), "expected": expected})
        return _mean(checked, default=1.0), {"epistemic_checks": len(checked), "violations": violations}

    def _component_historical(self, file_counts: dict[str, int], deps: dict[str, dict[str, Any]], inputs: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        total_files = sum(file_counts.values())
        file_score = _clamp(math.log1p(total_files) / math.log1p(1000)) if total_files > 0 else _clamp(inputs.get("historical_score", 0.6))
        event_count = deps.get("event_logger", {}).get("event_count_after", 0) or 0
        history_count = deps.get("transition_history", {}).get("history_count_after", 0) or 0
        trace_score = _clamp((float(event_count) + float(history_count) + 1.0) / 5.0)
        return _mean([file_score, trace_score]), {"file_counts": file_counts, "total_files": total_files, "event_count_after": event_count, "history_count_after": history_count}

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs or {}
        timestamp = _utc_now()
        deps = self._gather_dependencies(inputs)
        reports = self._load_real_reports()
        file_counts = self._count_historical_files()

        stability, stability_details = self._component_stability(deps, inputs)
        replications, replications_details = self._component_replications(reports, inputs)
        countermodels, countermodels_details = self._component_countermodels(deps, inputs)
        completeness, completeness_details = self._component_completeness(deps, inputs)
        coherence, coherence_details = self._component_coherence(deps)
        historical, historical_details = self._component_historical(file_counts, deps, inputs)

        confidence_components = {
            "stability": stability,
            "replications": replications,
            "countermodels": countermodels,
            "completeness": completeness,
            "coherence": coherence,
            "historical": historical,
        }
        confidence_breakdown = {
            key: round(confidence_components[key] * self.weights[key], 6)
            for key in self.weights
        }
        confidence = round(sum(confidence_breakdown.values()), 6)
        confidence_ready = confidence >= _clamp(inputs.get("confidence_threshold", 0.75))

        confidence_metrics = {
            "confidence": confidence,
            "confidence_threshold": _clamp(inputs.get("confidence_threshold", 0.75)),
            "weighted_component_sum": confidence,
            "minimum_component": min(confidence_components.values()) if confidence_components else 0.0,
            "maximum_component": max(confidence_components.values()) if confidence_components else 0.0,
            "component_count": len(confidence_components),
            "historical_file_total": historical_details.get("total_files", 0),
            "epistemic_violation_count": len(coherence_details.get("violations", [])),
        }

        failure_conditions = []
        for name, value in confidence_components.items():
            if value < 0.5:
                failure_conditions.append(f"low_{name}")
        if coherence_details.get("violations"):
            failure_conditions.append("epistemic_guard_violation")

        record = {
            "primitive": self.primitive,
            "step": "AS8",
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": timestamp,
            "confidence_status": self.READY_STATUS,
            "confidence_engine_ready": True,
            "confidence_ready": confidence_ready,
            "confidence": confidence,
            "confidence_breakdown": confidence_breakdown,
            "confidence_components": confidence_components,
            "confidence_metrics": confidence_metrics,
            "component_details": {
                "stability": stability_details,
                "replications": replications_details,
                "countermodels": countermodels_details,
                "completeness": completeness_details,
                "coherence": coherence_details,
                "historical": historical_details,
            },
            "dependency_outputs_available": sorted(deps.keys()),
            "failure_conditions": failure_conditions,
            "epistemic_scope": "functional_longitudinal_confidence_only_no_phenomenal_proof",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        record["confidence_hash"] = _stable_hash({k: v for k, v in record.items() if k != "confidence_hash"})

        output_path = ROOT / "consciousness_governance" / "confidence" / "latest_consciousness_confidence.json"
        record["output_path"] = str(output_path)
        persisted = False
        if persist:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(_json_safe(record), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            persisted = True
        record["persisted"] = persisted
        return record
