"""AF3 — Intrinsic Metric Builder v2.

Functional builder for an intrinsic metric over the self-generated reference
frame constructed in AF2.

The module reconstructs the transition:
    RF -> intrinsic metric seed

It derives distances, weights, normalization rules, invariance checks,
externality penalties and AF4 prerequisites from AF2 frame axes plus AF1/Ω
support. The metric is strictly functional: it evaluates structural and
computational properties only and does not assert consciousness, subjectivity,
qualia, experience, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "af_reference_frames" / "intrinsic_metric_builder"


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


class IntrinsicMetricBuilder:
    """Build an intrinsic metric from the AF2 self-generated frame."""

    primitive = "INTRINSIC_METRIC_BUILDER"
    expected_status = "INTRINSIC_METRIC_BUILT"

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "reference_frame_constructor": _load_json(ROOT / "af_reference_frames" / "reference_frame_constructor" / "latest_reference_frame_constructor.json"),
            "intrinsic_distinction_detector": _load_json(ROOT / "af_reference_frames" / "intrinsic_distinction_detector" / "latest_intrinsic_distinction_detector.json"),
            "omega_coherence_index": _load_json(ROOT / "ae_omega_coherence" / "omega_coherence_index" / "latest_omega_coherence_index.json"),
            "omega_causal_activity_tester": _load_json(ROOT / "ae_omega_coherence" / "omega_causal_activity_tester" / "latest_omega_causal_activity_tester.json"),
            "omega_stability_monitor": _load_json(ROOT / "ae_omega_coherence" / "omega_stability_monitor" / "latest_omega_stability_monitor.json"),
            "omega_failure_analyzer": _load_json(ROOT / "ae_omega_coherence" / "omega_failure_analyzer" / "latest_omega_failure_analyzer.json"),
            "identity_continuity_index": _load_json(ROOT / "ad_memory_identity_reflexivity" / "identity_continuity_index" / "latest_identity_continuity_index.json"),
            "continuity_metrics_engine": _load_json(ROOT / "continuity_metrics_engine" / "latest_continuity_metrics_engine.json"),
        }

    def _has_evidence(self, inputs: Mapping[str, Any]) -> bool:
        return any((isinstance(v, Mapping) and bool(v)) or isinstance(v, list) or isinstance(v, (int, float)) for v in inputs.values())

    def _extract_metrics(self, data: Mapping[str, Any]) -> Dict[str, float]:
        af2 = _as_mapping(data.get("reference_frame_constructor"), "reference_frame_score")
        af1 = _as_mapping(data.get("intrinsic_distinction_detector"), "intrinsic_distinction_score")
        oci = _as_mapping(data.get("omega_coherence_index"), "omega_coherence_index")
        oca = _as_mapping(data.get("omega_causal_activity_tester"), "omega_causal_activity_score")
        osm = _as_mapping(data.get("omega_stability_monitor"), "omega_stability_score")
        ofa = _as_mapping(data.get("omega_failure_analyzer"), "omega_resilience_score")
        ici = _as_mapping(data.get("identity_continuity_index"), "identity_continuity_score")
        cme = _as_mapping(data.get("continuity_metrics_engine"), "continuity_score")

        aliases = {
            "reference_frame_score": af2,
            "axis_grounding_score": af2,
            "origin_grounding_score": af2,
            "coordinate_closure_score": af2,
            "externality_independence_score": af2,
            "intrinsic_metric_readiness": af2,
            "intrinsic_distinction_score": af1,
            "reference_frame_readiness": af1,
            "omega_coherence_index": oci,
            "omega_causal_activity_score": oca,
            "omega_stability_score": osm,
            "omega_resilience_score": ofa,
            "identity_continuity_score": ici,
            "continuity_score": cme,
        }
        for key, target in aliases.items():
            if isinstance(data.get(key), (int, float)):
                target[key] = data.get(key)

        rf_pre = af2.get("rf_prerequisites", {}) if isinstance(af2.get("rf_prerequisites"), Mapping) else {}
        return {
            "reference_frame_score": _first_score(af2, ["reference_frame_score"], 0.80),
            "axis_grounding_score": _first_score(af2, ["axis_grounding_score"], 0.80),
            "origin_grounding_score": _first_score(af2, ["origin_grounding_score"], 0.80),
            "coordinate_closure_score": _first_score(af2, ["coordinate_closure_score"], 0.80),
            "externality_independence_score": _first_score(af2, ["externality_independence_score"], 0.80),
            "intrinsic_metric_readiness": _first_score(rf_pre, ["intrinsic_metric_readiness"], _first_score(af2, ["intrinsic_metric_readiness"], 0.80)),
            "intrinsic_distinction_score": _first_score(af1, ["intrinsic_distinction_score"], 0.80),
            "omega_coherence_score": _first_score(oci, ["omega_coherence_index", "omega_coherence_score"], 0.80),
            "omega_causal_activity_score": _first_score(oca, ["omega_causal_activity_score", "causal_activity_score"], 0.80),
            "omega_stability_score": _first_score(osm, ["omega_stability_score", "omega_stability_readiness_score"], 0.80),
            "omega_resilience_score": _first_score(ofa, ["omega_resilience_score"], 0.80),
            "identity_continuity_score": _first_score(ici, ["identity_continuity_score", "continuity_score"], 0.80),
            "continuity_score": _first_score(cme, ["continuity_score", "continuity_metrics_score", "continuity_index"], 0.80),
        }

    def _axes_from_inputs(self, data: Mapping[str, Any]) -> List[Dict[str, Any]]:
        af2 = data.get("reference_frame_constructor")
        axes: Any = []
        if isinstance(af2, Mapping):
            axes = af2.get("frame_axes") or (af2.get("reference_frame", {}) if isinstance(af2.get("reference_frame"), Mapping) else {}).get("axes") or []
        if isinstance(data.get("frame_axes"), list):
            axes = data.get("frame_axes")
        out: List[Dict[str, Any]] = []
        for i, axis in enumerate(_safe_list(axes), 1):
            if isinstance(axis, Mapping):
                out.append({
                    "axis_id": str(axis.get("axis_id", f"RF-A{i}")),
                    "label": str(axis.get("label", f"axis_{i}")),
                    "source_distinction": str(axis.get("source_distinction", axis.get("source_distinctions", ["unspecified"])[0] if isinstance(axis.get("source_distinctions"), list) and axis.get("source_distinctions") else "unspecified")),
                    "axis_score": _clamp(axis.get("axis_score", axis.get("axis_grounding_score")), 0.80),
                    "orientation": str(axis.get("orientation", "intrinsic_orientation")),
                    "external_coordinate_required": bool(axis.get("external_coordinate_required", False)),
                })
        if not out:
            labels = [
                ("RF-A1", "identity_continuity_axis", "self_non_self_boundary"),
                ("RF-A2", "externality_discrimination_axis", "internal_external_relation_boundary"),
                ("RF-A3", "viability_gradient_axis", "viable_non_viable_possibility_boundary"),
            ]
            out = [{"axis_id": a, "label": b, "source_distinction": c, "axis_score": 0.80, "orientation": "synthetic_intrinsic_orientation", "external_coordinate_required": False} for a, b, c in labels]
        return out

    def _component(self, component_id: str, label: str, axis_id: str, weight: float, grounding: float, formula: str) -> Dict[str, Any]:
        weight = _clamp(weight)
        grounding = _clamp(grounding)
        return {
            "component_id": component_id,
            "label": label,
            "axis_id": axis_id,
            "weight": weight,
            "component_weight": weight,
            "grounding_score": grounding,
            "component_score": _clamp(0.88 * grounding + 0.12 * (1.0 if weight > 0.0 else 0.0)),
            "distance_formula": formula,
            "normalization": "bounded_unit_interval",
            "external_metric_required": False if grounding >= 0.62 else True,
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(self._default_inputs())
        if inputs is not None:
            data.update(dict(inputs))

        has_evidence = self._has_evidence(data)
        metrics = self._extract_metrics(data) if has_evidence else {k: 0.0 for k in [
            "reference_frame_score", "axis_grounding_score", "origin_grounding_score", "coordinate_closure_score",
            "externality_independence_score", "intrinsic_metric_readiness", "intrinsic_distinction_score",
            "omega_coherence_score", "omega_causal_activity_score", "omega_stability_score", "omega_resilience_score",
            "identity_continuity_score", "continuity_score",
        ]}
        axes = self._axes_from_inputs(data) if has_evidence else []
        usable_axes = [a for a in axes if _clamp(a.get("axis_score")) >= 0.62]

        axis_basis_score = _mean([_clamp(a.get("axis_score")) for a in usable_axes]) if has_evidence and usable_axes else 0.0
        frame_support_score = _mean([
            metrics["reference_frame_score"], metrics["axis_grounding_score"], metrics["origin_grounding_score"], metrics["coordinate_closure_score"], metrics["intrinsic_metric_readiness"],
        ]) if has_evidence else 0.0
        omega_support_score = _mean([
            metrics["omega_coherence_score"], metrics["omega_causal_activity_score"], metrics["omega_stability_score"], metrics["omega_resilience_score"],
        ]) if has_evidence else 0.0
        continuity_support_score = _mean([metrics["identity_continuity_score"], metrics["continuity_score"], metrics["intrinsic_distinction_score"]]) if has_evidence else 0.0
        externality_penalty = _clamp(1.0 - metrics["externality_independence_score"]) if has_evidence else 1.0

        base_weight = _clamp(1.0 / len(usable_axes), 0.0) if usable_axes else 0.0
        metric_components: List[Dict[str, Any]] = []
        for i, axis in enumerate(usable_axes, 1):
            metric_components.append(self._component(
                f"IM-C{i:02d}",
                f"{axis.get('label')}_distance_component",
                str(axis.get("axis_id")),
                base_weight,
                _mean([_clamp(axis.get("axis_score")), frame_support_score, omega_support_score]),
                f"abs({axis.get('axis_id')}_x - {axis.get('axis_id')}_y)",
            ))

        component_grounding_score = _mean([_clamp(c.get("component_score")) for c in metric_components]) if metric_components else 0.0
        metric_symmetry_score = _mean([component_grounding_score, metrics["coordinate_closure_score"], metrics["omega_stability_score"]]) if has_evidence else 0.0
        metric_separation_score = _mean([axis_basis_score, metrics["intrinsic_distinction_score"], metrics["reference_frame_score"]]) if has_evidence else 0.0
        metric_triangle_proxy_score = _mean([metrics["coordinate_closure_score"], metrics["omega_resilience_score"], continuity_support_score]) if has_evidence else 0.0
        metric_invariance_score = _mean([metrics["omega_stability_score"], metrics["omega_resilience_score"], continuity_support_score, 1.0 - externality_penalty]) if has_evidence else 0.0

        intrinsic_metric_score = _clamp(
            0.20 * frame_support_score +
            0.18 * axis_basis_score +
            0.15 * component_grounding_score +
            0.13 * metric_symmetry_score +
            0.12 * metric_separation_score +
            0.12 * metric_triangle_proxy_score +
            0.10 * metric_invariance_score -
            0.08 * externality_penalty
        ) if has_evidence else 0.0

        failure_conditions: List[str] = []
        if not has_evidence:
            failure_conditions.append("no_reference_frame_or_omega_evidence_available")
        if len(usable_axes) < 3:
            failure_conditions.append("insufficient_frame_axes_for_metric")
        if frame_support_score < 0.62:
            failure_conditions.append("reference_frame_support_below_threshold")
        if component_grounding_score < 0.62:
            failure_conditions.append("metric_component_grounding_below_threshold")
        if metric_symmetry_score < 0.62:
            failure_conditions.append("metric_symmetry_proxy_below_threshold")
        if metric_separation_score < 0.62:
            failure_conditions.append("metric_separation_proxy_below_threshold")
        if metric_invariance_score < 0.62:
            failure_conditions.append("metric_invariance_below_threshold")
        if externality_penalty > 0.38:
            failure_conditions.append("external_metric_dependency_above_threshold")

        status = self.expected_status if (
            has_evidence and intrinsic_metric_score >= 0.72 and len(usable_axes) >= 3 and not failure_conditions
        ) else "INTRINSIC_METRIC_INSUFFICIENT"

        intrinsic_metric = {
            "metric_id": "IM-AF3-RF-GROUNDED",
            "metric_type": "self_generated_intrinsic_pseudometric_candidate",
            "domain": "AF2 self-generated reference frame coordinates",
            "components": metric_components,
            "distance_function_spec": {
                "function_id": "d_RF_intrinsic",
                "definition": "weighted_l1_distance_over_intrinsic_rf_axes",
                "formula": "sum_i w_i * abs(x_i - y_i)",
                "normalization": "bounded_unit_interval",
                "external_metric_required": externality_penalty > 0.38,
            },
            "metric_tensor_seed": {
                "tensor_id": "IM-T0",
                "diagonal_weights": {c["axis_id"]: c["weight"] for c in metric_components},
                "off_diagonal_policy": "zero_until_af5_stability_evidence",
                "positive_semidefinite_proxy": component_grounding_score >= 0.62,
            },
            "invariance_checks": {
                "symmetry_proxy_score": metric_symmetry_score,
                "separation_proxy_score": metric_separation_score,
                "triangle_proxy_score": metric_triangle_proxy_score,
                "omega_stability_invariance_score": metric_invariance_score,
            },
        }

        rf_prerequisites = {
            "intrinsic_metric_available": status == self.expected_status,
            "metric_components_available": len(metric_components) >= 3,
            "frame_externality_test_readiness": _clamp(0.50 * intrinsic_metric_score + 0.50 * metric_invariance_score),
            "next_required_module": "frame_externality_test",
            "external_metric_required": externality_penalty > 0.38,
        }

        public_schema = {
            "intrinsic_metric_builder_status": "str",
            "intrinsic_metric_score": "float[0,1]",
            "intrinsic_metric": "dict",
            "metric_components": "list[dict]",
            "distance_function_spec": "dict",
            "metric_tensor_seed": "dict",
            "metric_invariance_checks": "dict",
            "rf_prerequisites": "dict",
            "failure_conditions": "list[str]",
            "functional_conclusion_only": "bool",
            "phenomenology_undetermined": "bool",
            "consciousness_proven": "bool",
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "intrinsic_metric_builder_status": status,
            "af_axis_stage": "AF3",
            "theoretical_transition": "REFERENCE_FRAME_TO_INTRINSIC_METRIC",
            "upstream_evidence_available": has_evidence,
            "metrics": metrics,
            "axis_basis_score": axis_basis_score,
            "frame_support_score": frame_support_score,
            "omega_support_score": omega_support_score,
            "continuity_support_score": continuity_support_score,
            "component_grounding_score": component_grounding_score,
            "metric_symmetry_score": metric_symmetry_score,
            "metric_separation_score": metric_separation_score,
            "metric_triangle_proxy_score": metric_triangle_proxy_score,
            "metric_invariance_score": metric_invariance_score,
            "externality_penalty": externality_penalty,
            "intrinsic_metric_score": intrinsic_metric_score,
            "source_frame_axes": axes,
            "usable_frame_axes": usable_axes,
            "intrinsic_metric": intrinsic_metric,
            "metric_components": metric_components,
            "distance_function_spec": intrinsic_metric["distance_function_spec"],
            "metric_tensor_seed": intrinsic_metric["metric_tensor_seed"],
            "metric_invariance_checks": intrinsic_metric["invariance_checks"],
            "rf_prerequisites": rf_prerequisites,
            "failure_conditions": failure_conditions,
            "public_schema": public_schema,
            "af3_certification": "AF3_INTRINSIC_METRIC_CERTIFIED" if status == self.expected_status else "AF3_INTRINSIC_METRIC_NOT_CERTIFIED",
            "next_recommended_module": "frame_externality_test" if status == self.expected_status else "refine_intrinsic_metric_inputs",
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_guard": "Functional intrinsic metric construction only; no phenomenological claim is made.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_intrinsic_metric_builder.json"
        md_path = OUT_DIR / "latest_intrinsic_metric_builder.md"
        prom_path = OUT_DIR / "latest_intrinsic_metric_builder.prom"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AF3 — Intrinsic Metric Builder",
            "",
            f"Status: {result.get('intrinsic_metric_builder_status')}",
            f"Intrinsic metric score: {result.get('intrinsic_metric_score')}",
            f"Frame support score: {result.get('frame_support_score')}",
            f"Component grounding score: {result.get('component_grounding_score')}",
            f"Metric invariance score: {result.get('metric_invariance_score')}",
            f"Externality penalty: {result.get('externality_penalty')}",
            "",
            "## Intrinsic metric",
        ]
        metric = result.get("intrinsic_metric", {}) if isinstance(result.get("intrinsic_metric"), Mapping) else {}
        lines.append(f"Metric ID: {metric.get('metric_id')}")
        lines.append(f"Metric type: {metric.get('metric_type')}")
        lines.append(f"Domain: {metric.get('domain')}")
        lines.extend(["", "## Metric components"])
        for c in result.get("metric_components", []):
            if isinstance(c, Mapping):
                lines.append(f"- {c.get('component_id')}: {c.get('label')} — axis={c.get('axis_id')} — weight={c.get('weight')} — score={c.get('component_score')}")
        lines.extend(["", "## Distance function spec"])
        dfs = result.get("distance_function_spec", {}) if isinstance(result.get("distance_function_spec"), Mapping) else {}
        for k, v in dict(dfs).items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Metric tensor seed"])
        mts = result.get("metric_tensor_seed", {}) if isinstance(result.get("metric_tensor_seed"), Mapping) else {}
        for k, v in dict(mts).items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Metric invariance checks"])
        for k, v in dict(result.get("metric_invariance_checks", {})).items():
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
            "# HELP oce_intrinsic_metric_score AF3 intrinsic metric score",
            "# TYPE oce_intrinsic_metric_score gauge",
            f"oce_intrinsic_metric_score {_clamp(result.get('intrinsic_metric_score'))}",
            "# HELP oce_metric_component_grounding_score AF3 metric component grounding score",
            "# TYPE oce_metric_component_grounding_score gauge",
            f"oce_metric_component_grounding_score {_clamp(result.get('component_grounding_score'))}",
            "# HELP oce_metric_invariance_score AF3 metric invariance score",
            "# TYPE oce_metric_invariance_score gauge",
            f"oce_metric_invariance_score {_clamp(result.get('metric_invariance_score'))}",
            "# HELP oce_metric_externality_penalty AF3 metric externality penalty",
            "# TYPE oce_metric_externality_penalty gauge",
            f"oce_metric_externality_penalty {_clamp(result.get('externality_penalty'))}",
            "# HELP oce_intrinsic_metric_component_count AF3 intrinsic metric component count",
            "# TYPE oce_intrinsic_metric_component_count gauge",
            f"oce_intrinsic_metric_component_count {len(result.get('metric_components', [])) if isinstance(result.get('metric_components'), list) else 0}",
            "# HELP oce_intrinsic_metric_built AF3 build flag",
            "# TYPE oce_intrinsic_metric_built gauge",
            f"oce_intrinsic_metric_built {1 if result.get('intrinsic_metric_builder_status') == self.expected_status else 0}",
        ]
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(json.dumps(IntrinsicMetricBuilder().step(persist=True), indent=2, ensure_ascii=False))
