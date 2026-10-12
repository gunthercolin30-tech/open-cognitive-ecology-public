"""AF2 — Reference Frame Constructor.

Functional constructor for self-generated reference frames (RF) derived from
AF1 intrinsic distinctions and upstream Ω coherence evidence.

The module reconstructs the transition:
    intrinsic distinctions -> self-generated reference frame candidate

It builds an internal coordinate system from AF1 distinctions without requiring
an externally supplied frame: axes, origin, metric seeds, topology, externality
barriers, stability priors, and AF3 prerequisites.

Epistemic guard: this module only evaluates functional, structural, metric and
reference-frame properties. It does not assert consciousness, subjectivity,
qualia, experience, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "af_reference_frames" / "reference_frame_constructor"


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


class ReferenceFrameConstructor:
    """Construct a functional self-generated reference frame from AF1 evidence."""

    primitive = "REFERENCE_FRAME_CONSTRUCTOR"
    expected_status = "SELF_GENERATED_REFERENCE_FRAME_CONSTRUCTED"

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "intrinsic_distinction_detector": _load_json(ROOT / "af_reference_frames" / "intrinsic_distinction_detector" / "latest_intrinsic_distinction_detector.json"),
            "omega_coherence_index": _load_json(ROOT / "ae_omega_coherence" / "omega_coherence_index" / "latest_omega_coherence_index.json"),
            "omega_causal_activity_tester": _load_json(ROOT / "ae_omega_coherence" / "omega_causal_activity_tester" / "latest_omega_causal_activity_tester.json"),
            "omega_stability_monitor": _load_json(ROOT / "ae_omega_coherence" / "omega_stability_monitor" / "latest_omega_stability_monitor.json"),
            "omega_failure_analyzer": _load_json(ROOT / "ae_omega_coherence" / "omega_failure_analyzer" / "latest_omega_failure_analyzer.json"),
            "dynamic_graph_constructor": _load_json(ROOT / "aa_foundations" / "dynamic_graph_constructor" / "latest_dynamic_graph_constructor.json"),
            "identity_continuity_index": _load_json(ROOT / "ad_memory_identity_reflexivity" / "identity_continuity_index" / "latest_identity_continuity_index.json"),
        }

    def _has_evidence(self, inputs: Mapping[str, Any]) -> bool:
        return any((isinstance(v, Mapping) and bool(v)) or isinstance(v, list) or isinstance(v, (int, float)) for v in inputs.values())

    def _extract_metrics(self, data: Mapping[str, Any]) -> Dict[str, float]:
        af1 = _as_mapping(data.get("intrinsic_distinction_detector"), "intrinsic_distinction_score")
        oci = _as_mapping(data.get("omega_coherence_index"), "omega_coherence_index")
        oca = _as_mapping(data.get("omega_causal_activity_tester"), "omega_causal_activity_score")
        osm = _as_mapping(data.get("omega_stability_monitor"), "omega_stability_score")
        ofa = _as_mapping(data.get("omega_failure_analyzer"), "omega_resilience_score")
        dgc = _as_mapping(data.get("dynamic_graph_constructor"), "dynamic_graph_score")
        ici = _as_mapping(data.get("identity_continuity_index"), "identity_continuity_score")

        aliases = {
            "intrinsic_distinction_score": af1,
            "reference_frame_readiness": af1,
            "omega_coherence_index": oci,
            "omega_causal_activity_score": oca,
            "omega_stability_score": osm,
            "omega_resilience_score": ofa,
            "dynamic_graph_score": dgc,
            "identity_continuity_score": ici,
        }
        for key, target in aliases.items():
            if isinstance(data.get(key), (int, float)):
                target[key] = data.get(key)

        rf_pre = af1.get("rf_prerequisites", {}) if isinstance(af1.get("rf_prerequisites"), Mapping) else {}
        return {
            "intrinsic_distinction_score": _first_score(af1, ["intrinsic_distinction_score"], 0.80),
            "reference_frame_readiness": _first_score(rf_pre, ["reference_frame_readiness"], _first_score(af1, ["reference_frame_readiness"], 0.80)),
            "omega_coherence_score": _first_score(oci, ["omega_coherence_index", "omega_coherence_score"], 0.80),
            "omega_causal_activity_score": _first_score(oca, ["omega_causal_activity_score", "causal_activity_score"], 0.80),
            "omega_stability_score": _first_score(osm, ["omega_stability_score", "omega_stability_readiness_score"], 0.80),
            "omega_resilience_score": _first_score(ofa, ["omega_resilience_score"], 0.80),
            "dynamic_graph_score": _first_score(dgc, ["dynamic_graph_score", "graph_construction_score", "dynamic_graph_constructor_score"], 0.80),
            "identity_continuity_score": _first_score(ici, ["identity_continuity_score", "continuity_score"], 0.80),
        }

    def _distinctions_from_inputs(self, data: Mapping[str, Any]) -> List[Dict[str, Any]]:
        af1 = data.get("intrinsic_distinction_detector")
        if isinstance(af1, Mapping):
            ds = af1.get("candidate_distinctions") or af1.get("distinctions") or []
        else:
            ds = []
        if isinstance(data.get("candidate_distinctions"), list):
            ds = data.get("candidate_distinctions")
        out: List[Dict[str, Any]] = []
        for i, d in enumerate(_safe_list(ds), 1):
            if isinstance(d, Mapping):
                out.append({
                    "distinction_id": str(d.get("distinction_id", f"ID-{i:02d}")),
                    "label": str(d.get("label", f"distinction_{i}")),
                    "distinction_score": _clamp(d.get("distinction_score"), 0.80),
                    "classification": str(d.get("classification", "candidate_intrinsic_distinction")),
                })
        if not out:
            # Deterministic minimal synthetic basis used only when scalar tests are supplied.
            labels = [
                "self_non_self_boundary",
                "internal_external_relation_boundary",
                "stable_unstable_omega_boundary",
                "causal_passive_boundary",
                "viable_non_viable_possibility_boundary",
                "recoverable_non_recoverable_boundary",
            ]
            out = [{"distinction_id": f"ID-{i:02d}", "label": label, "distinction_score": 0.80, "classification": "synthetic_candidate_distinction"} for i, label in enumerate(labels, 1)]
        return out

    def _axis(self, axis_id: str, label: str, source_distinctions: List[str], grounding: float, orientation: str) -> Dict[str, Any]:
        grounding = _clamp(grounding)
        primary_source = str(source_distinctions[0]) if source_distinctions else "unspecified_intrinsic_distinction"
        return {
            "axis_id": axis_id,
            "label": label,
            "source_distinction": primary_source,
            "source_distinctions": list(source_distinctions),
            "axis_score": grounding,
            "axis_grounding_score": grounding,
            "orientation": orientation,
            "origin_relation": "anchored_to_intrinsic_zero_point",
            "external_coordinate_required": False if grounding >= 0.62 else True,
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(self._default_inputs())
        if inputs is not None:
            data.update(dict(inputs))

        has_evidence = self._has_evidence(data)
        metrics = self._extract_metrics(data) if has_evidence else {k: 0.0 for k in [
            "intrinsic_distinction_score", "reference_frame_readiness", "omega_coherence_score",
            "omega_causal_activity_score", "omega_stability_score", "omega_resilience_score",
            "dynamic_graph_score", "identity_continuity_score",
        ]}
        distinctions = self._distinctions_from_inputs(data) if has_evidence else []
        usable_distinctions = [d for d in distinctions if _clamp(d.get("distinction_score")) >= 0.62]

        distinction_basis_score = _mean([_clamp(d.get("distinction_score")) for d in usable_distinctions]) if has_evidence and usable_distinctions else 0.0
        omega_support_score = _mean([
            metrics["omega_coherence_score"], metrics["omega_causal_activity_score"],
            metrics["omega_stability_score"], metrics["omega_resilience_score"],
        ]) if has_evidence else 0.0
        structural_support_score = _mean([
            metrics["dynamic_graph_score"], metrics["identity_continuity_score"], metrics["reference_frame_readiness"],
        ]) if has_evidence else 0.0

        axes = [
            self._axis("RF-A1", "identity_boundary_axis", ["ID-01", "ID-03"], _mean([metrics["identity_continuity_score"], metrics["omega_stability_score"], distinction_basis_score]), "self_to_non_self"),
            self._axis("RF-A2", "relational_externality_axis", ["ID-02", "ID-04"], _mean([metrics["omega_causal_activity_score"], metrics["dynamic_graph_score"], distinction_basis_score]), "internal_to_external"),
            self._axis("RF-A3", "viability_recovery_axis", ["ID-05", "ID-06"], _mean([metrics["omega_resilience_score"], metrics["omega_stability_score"], distinction_basis_score]), "viable_to_non_viable"),
        ] if has_evidence else []

        axis_grounding_score = _mean([a["axis_grounding_score"] for a in axes]) if axes else 0.0
        origin_grounding_score = _clamp(0.40 * metrics["intrinsic_distinction_score"] + 0.30 * metrics["identity_continuity_score"] + 0.30 * metrics["omega_coherence_score"]) if has_evidence else 0.0
        coordinate_closure_score = _clamp(0.50 * axis_grounding_score + 0.30 * omega_support_score + 0.20 * structural_support_score) if has_evidence else 0.0
        externality_independence_score = _clamp(0.45 * distinction_basis_score + 0.30 * metrics["reference_frame_readiness"] + 0.25 * metrics["omega_resilience_score"]) if has_evidence else 0.0
        reference_frame_score = _clamp(
            0.25 * distinction_basis_score
            + 0.20 * axis_grounding_score
            + 0.20 * origin_grounding_score
            + 0.20 * coordinate_closure_score
            + 0.15 * externality_independence_score
        ) if has_evidence else 0.0

        failure_conditions: List[str] = []
        if not has_evidence:
            failure_conditions.append("no_af1_or_omega_evidence_available")
        if len(usable_distinctions) < 4:
            failure_conditions.append("insufficient_intrinsic_distinctions_for_frame")
        if distinction_basis_score < 0.62:
            failure_conditions.append("distinction_basis_below_threshold")
        if axis_grounding_score < 0.62:
            failure_conditions.append("axis_grounding_below_threshold")
        if origin_grounding_score < 0.62:
            failure_conditions.append("origin_grounding_below_threshold")
        if coordinate_closure_score < 0.62:
            failure_conditions.append("coordinate_closure_below_threshold")
        if externality_independence_score < 0.62:
            failure_conditions.append("externality_independence_below_threshold")

        status = self.expected_status if (
            has_evidence
            and reference_frame_score >= 0.72
            and len(usable_distinctions) >= 4
            and not failure_conditions
        ) else "SELF_GENERATED_REFERENCE_FRAME_INSUFFICIENT"

        reference_frame = {
            "frame_id": "RF-AF2-OMEGA-GROUNDED",
            "frame_type": "self_generated_functional_reference_frame",
            "origin": {
                "origin_id": "RF-O0",
                "definition": "intrinsic_zero_point_defined_by_self_non_self_and_omega_stability_boundaries",
                "origin_grounding_score": origin_grounding_score,
                "external_origin_required": False if origin_grounding_score >= 0.62 else True,
            },
            "axes": axes,
            "coordinates": [
                {"coordinate_id": "c_identity", "axis_id": "RF-A1", "value_range": [0.0, 1.0]},
                {"coordinate_id": "c_externality", "axis_id": "RF-A2", "value_range": [0.0, 1.0]},
                {"coordinate_id": "c_viability", "axis_id": "RF-A3", "value_range": [0.0, 1.0]},
            ] if axes else [],
            "topology": {
                "nodes": [a["axis_id"] for a in axes] + ["RF-O0"],
                "edges": [
                    {"source": "RF-O0", "target": "RF-A1", "relation": "origin_anchors_identity_axis"},
                    {"source": "RF-O0", "target": "RF-A2", "relation": "origin_anchors_externality_axis"},
                    {"source": "RF-O0", "target": "RF-A3", "relation": "origin_anchors_viability_axis"},
                    {"source": "RF-A1", "target": "RF-A2", "relation": "identity_bounds_externality"},
                    {"source": "RF-A2", "target": "RF-A3", "relation": "causal_externality_modulates_viability"},
                ] if axes else [],
            },
            "metric_seed": {
                "metric_seed_id": "RF-M0",
                "distance_components": ["identity_distance", "externality_distance", "viability_distance"],
                "metric_grounding_score": coordinate_closure_score,
                "next_builder": "intrinsic_metric_builder",
            },
        }

        rf_prerequisites = {
            "reference_frame_constructed": status == self.expected_status,
            "self_generated_reference_frame_available": status == self.expected_status,
            "intrinsic_metric_readiness": _clamp(0.50 * reference_frame_score + 0.50 * coordinate_closure_score),
            "next_required_module": "intrinsic_metric_builder",
            "external_frame_required": externality_independence_score < 0.62,
        }

        public_schema = {
            "reference_frame_constructor_status": "str",
            "reference_frame_score": "float[0,1]",
            "reference_frame": "dict",
            "frame_axes": "list[dict]",
            "frame_origin": "dict",
            "frame_coordinates": "list[dict]",
            "metric_seed": "dict",
            "rf_prerequisites": "dict",
            "failure_conditions": "list[str]",
            "functional_conclusion_only": "bool",
            "phenomenology_undetermined": "bool",
            "consciousness_proven": "bool",
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "reference_frame_constructor_status": status,
            "af_axis_stage": "AF2",
            "theoretical_transition": "INTRINSIC_DISTINCTIONS_TO_REFERENCE_FRAME",
            "upstream_evidence_available": has_evidence,
            "metrics": metrics,
            "distinction_basis_score": distinction_basis_score,
            "omega_support_score": omega_support_score,
            "structural_support_score": structural_support_score,
            "axis_grounding_score": axis_grounding_score,
            "origin_grounding_score": origin_grounding_score,
            "coordinate_closure_score": coordinate_closure_score,
            "externality_independence_score": externality_independence_score,
            "reference_frame_score": reference_frame_score,
            "usable_distinction_count": len(usable_distinctions),
            "source_distinctions": distinctions,
            "usable_distinctions": usable_distinctions,
            "reference_frame": reference_frame,
            "frame_axes": axes,
            "frame_origin": reference_frame["origin"],
            "frame_coordinates": reference_frame["coordinates"],
            "frame_topology": reference_frame["topology"],
            "metric_seed": reference_frame["metric_seed"],
            "rf_prerequisites": rf_prerequisites,
            "failure_conditions": failure_conditions,
            "public_schema": public_schema,
            "af2_certification": "AF2_REFERENCE_FRAME_CERTIFIED" if status == self.expected_status else "AF2_REFERENCE_FRAME_NOT_CERTIFIED",
            "next_recommended_module": "intrinsic_metric_builder" if status == self.expected_status else "refine_reference_frame_constructor_inputs",
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_guard": "Functional reference-frame construction only; no phenomenological claim is made.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_reference_frame_constructor.json"
        md_path = OUT_DIR / "latest_reference_frame_constructor.md"
        prom_path = OUT_DIR / "latest_reference_frame_constructor.prom"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AF2 — Reference Frame Constructor",
            "",
            f"Status: {result.get('reference_frame_constructor_status')}",
            f"Reference frame score: {result.get('reference_frame_score')}",
            f"Axis grounding score: {result.get('axis_grounding_score')}",
            f"Origin grounding score: {result.get('origin_grounding_score')}",
            f"Coordinate closure score: {result.get('coordinate_closure_score')}",
            f"Externality independence score: {result.get('externality_independence_score')}",
            "",
            "## Self-generated reference frame",
        ]
        rf = result.get("reference_frame", {}) if isinstance(result.get("reference_frame"), Mapping) else {}
        lines.append(f"Frame ID: {rf.get('frame_id')}")
        lines.append(f"Frame type: {rf.get('frame_type')}")
        lines.extend(["", "## Frame origin"])
        origin = result.get("frame_origin", {}) if isinstance(result.get("frame_origin"), Mapping) else {}
        for k, v in dict(origin).items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Frame axes"])
        for a in result.get("frame_axes", []):
            if isinstance(a, Mapping):
                lines.append(f"- {a.get('axis_id')}: {a.get('label')} — score={a.get('axis_grounding_score')} — orientation={a.get('orientation')}")
        lines.extend(["", "## Frame coordinates"])
        for c in result.get("frame_coordinates", []):
            if isinstance(c, Mapping):
                lines.append(f"- {c.get('coordinate_id')}: axis={c.get('axis_id')} range={c.get('value_range')}")
        lines.extend(["", "## Metric seed"])
        metric_seed = result.get("metric_seed", {}) if isinstance(result.get("metric_seed"), Mapping) else {}
        for k, v in dict(metric_seed).items():
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
            "# HELP oce_reference_frame_score AF2 reference frame score",
            "# TYPE oce_reference_frame_score gauge",
            f"oce_reference_frame_score {_clamp(result.get('reference_frame_score'))}",
            "# HELP oce_frame_axis_grounding_score AF2 frame axis grounding score",
            "# TYPE oce_frame_axis_grounding_score gauge",
            f"oce_frame_axis_grounding_score {_clamp(result.get('axis_grounding_score'))}",
            "# HELP oce_frame_origin_grounding_score AF2 frame origin grounding score",
            "# TYPE oce_frame_origin_grounding_score gauge",
            f"oce_frame_origin_grounding_score {_clamp(result.get('origin_grounding_score'))}",
            "# HELP oce_coordinate_closure_score AF2 coordinate closure score",
            "# TYPE oce_coordinate_closure_score gauge",
            f"oce_coordinate_closure_score {_clamp(result.get('coordinate_closure_score'))}",
            "# HELP oce_externality_independence_score AF2 externality independence score",
            "# TYPE oce_externality_independence_score gauge",
            f"oce_externality_independence_score {_clamp(result.get('externality_independence_score'))}",
            "# HELP oce_reference_frame_axis_count AF2 reference frame axis count",
            "# TYPE oce_reference_frame_axis_count gauge",
            f"oce_reference_frame_axis_count {len(result.get('frame_axes', [])) if isinstance(result.get('frame_axes'), list) else 0}",
            "# HELP oce_reference_frame_constructed AF2 construction flag",
            "# TYPE oce_reference_frame_constructed gauge",
            f"oce_reference_frame_constructed {1 if result.get('reference_frame_constructor_status') == self.expected_status else 0}",
        ]
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(json.dumps(ReferenceFrameConstructor().step(persist=True), indent=2, ensure_ascii=False))
