"""AF4 — Frame Externality Test.

Functional test for whether the AF2 reference frame and AF3 intrinsic metric
remain internally generated rather than dependent on an externally imposed
coordinate system, metric, ontology, or evaluator.

The module reconstructs the transition:
    intrinsic metric over RF -> externality-independent RF candidate

Epistemic guard: this module evaluates functional, structural and metric
externality only. It does not assert consciousness, subjectivity, qualia,
experience, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "af_reference_frames" / "frame_externality_test"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return max(0.0, min(1.0, v))


def _mean(values: List[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    return _clamp(sum(vals) / len(vals), default) if vals else default


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    return {}


def _as_mapping(value: Any, preferred_key: str = "value") -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, (int, float)):
        return {preferred_key: value}
    return {}


def _first_score(source: Any, keys: List[str], default: float = 0.0) -> float:
    if isinstance(source, (int, float)):
        return _clamp(source, default)
    if not isinstance(source, Mapping):
        return default
    for key in keys:
        if key in source:
            return _clamp(source.get(key), default)
    return default


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


class FrameExternalityTest:
    """Test whether a self-generated RF avoids external-frame dependency."""

    primitive = "FRAME_EXTERNALITY_TEST"
    expected_status = "FRAME_EXTERNALITY_INDEPENDENCE_CONFIRMED"

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "reference_frame_constructor": _load_json(ROOT / "af_reference_frames" / "reference_frame_constructor" / "latest_reference_frame_constructor.json"),
            "intrinsic_metric_builder": _load_json(ROOT / "af_reference_frames" / "intrinsic_metric_builder" / "latest_intrinsic_metric_builder.json"),
            "intrinsic_distinction_detector": _load_json(ROOT / "af_reference_frames" / "intrinsic_distinction_detector" / "latest_intrinsic_distinction_detector.json"),
            "omega_failure_analyzer": _load_json(ROOT / "ae_omega_coherence" / "omega_failure_analyzer" / "latest_omega_failure_analyzer.json"),
            "omega_stability_monitor": _load_json(ROOT / "ae_omega_coherence" / "omega_stability_monitor" / "latest_omega_stability_monitor.json"),
            "identity_continuity_index": _load_json(ROOT / "ad_memory_identity_reflexivity" / "identity_continuity_index" / "latest_identity_continuity_index.json"),
            "constraint_failure_analyzer": _load_json(ROOT / "ab_constraint_emergence" / "constraint_failure_analyzer" / "latest_constraint_failure_analyzer.json"),
        }

    def _has_evidence(self, inputs: Mapping[str, Any]) -> bool:
        return any((isinstance(v, Mapping) and bool(v)) or isinstance(v, list) or isinstance(v, (int, float)) for v in inputs.values())

    def _extract_metrics(self, data: Mapping[str, Any]) -> Dict[str, float]:
        af2 = _as_mapping(data.get("reference_frame_constructor"), "reference_frame_score")
        af3 = _as_mapping(data.get("intrinsic_metric_builder"), "intrinsic_metric_score")
        af1 = _as_mapping(data.get("intrinsic_distinction_detector"), "intrinsic_distinction_score")
        ofa = _as_mapping(data.get("omega_failure_analyzer"), "omega_resilience_score")
        osm = _as_mapping(data.get("omega_stability_monitor"), "omega_stability_score")
        ici = _as_mapping(data.get("identity_continuity_index"), "identity_continuity_score")
        cfa = _as_mapping(data.get("constraint_failure_analyzer"), "constraint_failure_score")

        aliases = {
            "reference_frame_score": af2,
            "axis_grounding_score": af2,
            "coordinate_closure_score": af2,
            "externality_independence_score": af2,
            "intrinsic_metric_score": af3,
            "metric_invariance_score": af3,
            "metric_externality_penalty": af3,
            "external_metric_required": af3,
            "intrinsic_distinction_score": af1,
            "omega_resilience_score": ofa,
            "omega_stability_score": osm,
            "identity_continuity_score": ici,
            "constraint_failure_score": cfa,
            "external_reference_pressure": af3,
        }
        for key, target in aliases.items():
            if key in data:
                target[key] = data.get(key)

        af2_pre = af2.get("rf_prerequisites", {}) if isinstance(af2.get("rf_prerequisites"), Mapping) else {}
        af3_pre = af3.get("rf_prerequisites", {}) if isinstance(af3.get("rf_prerequisites"), Mapping) else {}
        af3_inv = af3.get("metric_invariance_checks", {}) if isinstance(af3.get("metric_invariance_checks"), Mapping) else {}
        af3_dfs = af3.get("distance_function_spec", {}) if isinstance(af3.get("distance_function_spec"), Mapping) else {}

        ext_required = bool(af3.get("external_metric_required", af3_pre.get("external_metric_required", af3_dfs.get("external_metric_required", False))))
        raw_penalty = _first_score(af3, ["metric_externality_penalty", "externality_penalty"], 0.0)
        if "external_reference_pressure" in af3:
            raw_penalty = max(raw_penalty, _first_score(af3, ["external_reference_pressure"], 0.0))
        if ext_required:
            raw_penalty = max(raw_penalty, 0.50)

        return {
            "reference_frame_score": _first_score(af2, ["reference_frame_score"], 0.80),
            "axis_grounding_score": _first_score(af2, ["axis_grounding_score"], 0.80),
            "coordinate_closure_score": _first_score(af2, ["coordinate_closure_score"], 0.80),
            "af2_externality_independence_score": _first_score(af2, ["externality_independence_score"], _first_score(af2_pre, ["externality_independence_score"], 0.80)),
            "intrinsic_metric_score": _first_score(af3, ["intrinsic_metric_score"], 0.80),
            "metric_invariance_score": _first_score(af3, ["metric_invariance_score"], _first_score(af3_inv, ["omega_stability_invariance_score", "symmetry_proxy_score"], 0.80)),
            "metric_externality_penalty": _clamp(raw_penalty),
            "intrinsic_distinction_score": _first_score(af1, ["intrinsic_distinction_score"], 0.80),
            "omega_resilience_score": _first_score(ofa, ["omega_resilience_score"], 0.80),
            "omega_stability_score": _first_score(osm, ["omega_stability_score", "omega_stability_readiness_score"], 0.80),
            "identity_continuity_score": _first_score(ici, ["identity_continuity_score", "continuity_score"], 0.80),
            "constraint_failure_score": _first_score(cfa, ["constraint_failure_score", "failure_pressure", "constraint_failure_index"], 0.0),
            "external_metric_required_flag": 1.0 if ext_required else 0.0,
            "af5_readiness_from_af3": _first_score(af3_pre, ["frame_externality_test_readiness"], 0.80),
        }

    def _externality_tests(self, data: Mapping[str, Any], metrics: Mapping[str, float]) -> List[Dict[str, Any]]:
        af2 = data.get("reference_frame_constructor") if isinstance(data.get("reference_frame_constructor"), Mapping) else {}
        af3 = data.get("intrinsic_metric_builder") if isinstance(data.get("intrinsic_metric_builder"), Mapping) else {}
        axes = _safe_list(af2.get("frame_axes")) or _safe_list(data.get("frame_axes"))
        components = _safe_list(af3.get("metric_components")) or _safe_list(data.get("metric_components"))
        external_axes = [a for a in axes if isinstance(a, Mapping) and bool(a.get("external_coordinate_required", False))]
        external_components = [c for c in components if isinstance(c, Mapping) and bool(c.get("external_metric_required", False))]

        axis_independence = _clamp(1.0 - (len(external_axes) / max(1, len(axes)))) if axes else metrics.get("af2_externality_independence_score", 0.80)
        metric_independence = _clamp(1.0 - (len(external_components) / max(1, len(components)))) if components else _clamp(1.0 - metrics.get("metric_externality_penalty", 0.0))
        origin_independence = _mean([metrics.get("intrinsic_distinction_score", 0.0), metrics.get("identity_continuity_score", 0.0), metrics.get("reference_frame_score", 0.0)])
        coordinate_independence = _mean([metrics.get("coordinate_closure_score", 0.0), axis_independence, metrics.get("omega_stability_score", 0.0)])
        metric_invariance_independence = _mean([metrics.get("intrinsic_metric_score", 0.0), metrics.get("metric_invariance_score", 0.0), metric_independence, metrics.get("omega_resilience_score", 0.0)])
        constraint_non_capture = _clamp(1.0 - metrics.get("constraint_failure_score", 0.0))

        tests = [
            ("FET-01", "axis_external_coordinate_absence", axis_independence, "No frame axis requires an externally supplied coordinate."),
            ("FET-02", "origin_internal_grounding", origin_independence, "Frame origin remains grounded in AF1/identity evidence."),
            ("FET-03", "coordinate_closure_without_external_scale", coordinate_independence, "Coordinates are closed over RF axes and Ω stability."),
            ("FET-04", "metric_external_dependency_absence", metric_independence, "AF3 metric components do not require external metric structure."),
            ("FET-05", "metric_invariance_under_internal_relabeling", metric_invariance_independence, "Metric remains invariant under internal RF relabeling proxies."),
            ("FET-06", "constraint_non_capture", constraint_non_capture, "Constraint failures do not externally capture RF construction."),
        ]
        out: List[Dict[str, Any]] = []
        for test_id, label, score, rationale in tests:
            s = _clamp(score)
            out.append({
                "test_id": test_id,
                "label": label,
                "test_score": s,
                "passed": s >= 0.62,
                "threshold": 0.62,
                "rationale": rationale,
                "external_dependency_detected": s < 0.62,
            })
        return out

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(self._default_inputs())
        if inputs is not None:
            data.update(dict(inputs))

        has_evidence = self._has_evidence(data)
        metric_keys = [
            "reference_frame_score", "axis_grounding_score", "coordinate_closure_score", "af2_externality_independence_score",
            "intrinsic_metric_score", "metric_invariance_score", "metric_externality_penalty", "intrinsic_distinction_score",
            "omega_resilience_score", "omega_stability_score", "identity_continuity_score", "constraint_failure_score",
            "external_metric_required_flag", "af5_readiness_from_af3",
        ]
        metrics = self._extract_metrics(data) if has_evidence else {k: 0.0 for k in metric_keys}
        tests = self._externality_tests(data, metrics) if has_evidence else []

        test_score = _mean([t["test_score"] for t in tests]) if tests else 0.0
        upstream_support_score = _mean([
            metrics["reference_frame_score"], metrics["intrinsic_metric_score"], metrics["intrinsic_distinction_score"],
            metrics["omega_resilience_score"], metrics["omega_stability_score"], metrics["identity_continuity_score"],
        ]) if has_evidence else 0.0
        externality_penalty = _clamp(0.65 * metrics["metric_externality_penalty"] + 0.25 * metrics["external_metric_required_flag"] + 0.10 * max(0.0, metrics["constraint_failure_score"])) if has_evidence else 1.0
        independence_score = _clamp(0.55 * test_score + 0.35 * upstream_support_score + 0.10 * metrics["af2_externality_independence_score"] - 0.25 * externality_penalty) if has_evidence else 0.0
        external_reference_pressure = _clamp(1.0 - independence_score)

        failure_conditions: List[str] = []
        if not has_evidence:
            failure_conditions.append("no_reference_frame_or_intrinsic_metric_evidence_available")
        if metrics["reference_frame_score"] < 0.62:
            failure_conditions.append("reference_frame_support_below_threshold")
        if metrics["intrinsic_metric_score"] < 0.62:
            failure_conditions.append("intrinsic_metric_support_below_threshold")
        if test_score < 0.62:
            failure_conditions.append("externality_test_score_below_threshold")
        if externality_penalty > 0.38:
            failure_conditions.append("externality_penalty_above_threshold")
        if any(t.get("external_dependency_detected") for t in tests):
            failure_conditions.append("external_dependency_detected_in_subtest")

        status = self.expected_status if (
            has_evidence and independence_score >= 0.72 and test_score >= 0.62 and externality_penalty <= 0.38 and not failure_conditions
        ) else "FRAME_EXTERNALITY_INDEPENDENCE_INSUFFICIENT"

        externality_profile = {
            "profile_id": "AF4-FRAME-EXTERNALITY-PROFILE",
            "external_reference_required": status != self.expected_status,
            "external_metric_required": bool(metrics["external_metric_required_flag"] >= 0.5),
            "external_reference_pressure": external_reference_pressure,
            "externality_penalty": externality_penalty,
            "intrinsic_closure_supported": status == self.expected_status,
        }
        independence_certificate = {
            "certificate_id": "AF4-RF-INDEPENDENCE-CERTIFICATE",
            "certified": status == self.expected_status,
            "certification_status": "AF4_FRAME_EXTERNALITY_CERTIFIED" if status == self.expected_status else "AF4_FRAME_EXTERNALITY_NOT_CERTIFIED",
            "basis": [t["label"] for t in tests if t.get("passed")],
            "failed_basis": [t["label"] for t in tests if not t.get("passed")],
            "next_required_module": "frame_stability_analyzer" if status == self.expected_status else "refine_frame_externality_inputs",
        }
        rf_prerequisites = {
            "frame_externality_independence_confirmed": status == self.expected_status,
            "reference_frame_externality_free": status == self.expected_status,
            "external_reference_required": status != self.expected_status,
            "frame_stability_analyzer_readiness": _clamp(0.60 * independence_score + 0.40 * metrics["af5_readiness_from_af3"]),
            "next_required_module": "frame_stability_analyzer",
        }
        public_schema = {
            "frame_externality_test_status": "str",
            "frame_externality_score": "float[0,1]",
            "externality_tests": "list[dict]",
            "externality_profile": "dict",
            "independence_certificate": "dict",
            "rf_prerequisites": "dict",
            "failure_conditions": "list[str]",
            "functional_conclusion_only": "bool",
            "phenomenology_undetermined": "bool",
            "consciousness_proven": "bool",
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "frame_externality_test_status": status,
            "af_axis_stage": "AF4",
            "theoretical_transition": "INTRINSIC_METRIC_TO_EXTERNALITY_INDEPENDENT_RF",
            "upstream_evidence_available": has_evidence,
            "metrics": metrics,
            "externality_tests": tests,
            "test_score": test_score,
            "upstream_support_score": upstream_support_score,
            "externality_penalty": externality_penalty,
            "external_reference_pressure": external_reference_pressure,
            "frame_externality_score": independence_score,
            "reference_frame_externality_score": independence_score,
            "externality_profile": externality_profile,
            "independence_certificate": independence_certificate,
            "rf_prerequisites": rf_prerequisites,
            "failure_conditions": failure_conditions,
            "public_schema": public_schema,
            "af4_certification": independence_certificate["certification_status"],
            "next_recommended_module": independence_certificate["next_required_module"],
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_guard": "Functional frame externality test only; no phenomenological claim is made.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_frame_externality_test.json"
        md_path = OUT_DIR / "latest_frame_externality_test.md"
        prom_path = OUT_DIR / "latest_frame_externality_test.prom"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AF4 — Frame Externality Test",
            "",
            f"Status: {result.get('frame_externality_test_status')}",
            f"Frame externality score: {result.get('frame_externality_score')}",
            f"Test score: {result.get('test_score')}",
            f"Externality penalty: {result.get('externality_penalty')}",
            f"External reference pressure: {result.get('external_reference_pressure')}",
            "",
            "## Externality tests",
        ]
        for t in result.get("externality_tests", []):
            if isinstance(t, Mapping):
                lines.append(f"- {t.get('test_id')}: {t.get('label')} — score={t.get('test_score')} — passed={t.get('passed')}")
        lines.extend(["", "## Externality profile"])
        for k, v in dict(result.get("externality_profile", {})).items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Independence certificate"])
        for k, v in dict(result.get("independence_certificate", {})).items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## RF prerequisites"])
        for k, v in dict(result.get("rf_prerequisites", {})).items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Failure conditions"])
        for c in result.get("failure_conditions", []):
            lines.append(f"- {c}")
        lines.extend(["", "## Epistemic guard", "Functional conclusion only; phenomenology undetermined; no consciousness claim."])
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# HELP oce_frame_externality_score AF4 frame externality independence score",
            "# TYPE oce_frame_externality_score gauge",
            f"oce_frame_externality_score {_clamp(result.get('frame_externality_score'))}",
            "# HELP oce_frame_externality_test_score AF4 externality subtest mean score",
            "# TYPE oce_frame_externality_test_score gauge",
            f"oce_frame_externality_test_score {_clamp(result.get('test_score'))}",
            "# HELP oce_frame_externality_penalty AF4 externality penalty",
            "# TYPE oce_frame_externality_penalty gauge",
            f"oce_frame_externality_penalty {_clamp(result.get('externality_penalty'))}",
            "# HELP oce_external_reference_pressure AF4 external reference pressure",
            "# TYPE oce_external_reference_pressure gauge",
            f"oce_external_reference_pressure {_clamp(result.get('external_reference_pressure'))}",
            "# HELP oce_frame_externality_test_count AF4 externality test count",
            "# TYPE oce_frame_externality_test_count gauge",
            f"oce_frame_externality_test_count {len(result.get('externality_tests', [])) if isinstance(result.get('externality_tests'), list) else 0}",
            "# HELP oce_frame_external_dependency_count AF4 external dependency count",
            "# TYPE oce_frame_external_dependency_count gauge",
            f"oce_frame_external_dependency_count {sum(1 for t in result.get('externality_tests', []) if isinstance(t, Mapping) and t.get('external_dependency_detected')) if isinstance(result.get('externality_tests'), list) else 0}",
            "# HELP oce_frame_externality_independence_confirmed AF4 independence certification flag",
            "# TYPE oce_frame_externality_independence_confirmed gauge",
            f"oce_frame_externality_independence_confirmed {1 if result.get('frame_externality_test_status') == self.expected_status else 0}",
        ]
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(json.dumps(FrameExternalityTest().step(persist=True), indent=2, ensure_ascii=False))
