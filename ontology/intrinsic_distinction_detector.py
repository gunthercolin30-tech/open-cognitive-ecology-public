"""AF1 — Intrinsic Distinction Detector.

Functional detector for intrinsic distinctions produced after Ω dynamic
coherence has been validated.

The module reconstructs the first transition of axis AF:
    Ω -> intrinsic distinctions -> RF prerequisites

It detects whether the system can construct non-arbitrary, internally grounded
distinctions from its own Ω-coherence evidence: self/non-self, internal/external,
stable/unstable, causal/passive, viable/non-viable, and recoverable/non-recoverable.

Epistemic guard: this module only evaluates functional, structural and metric
properties. It does not assert consciousness, subjectivity, qualia, experience,
or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "af_reference_frames" / "intrinsic_distinction_detector"


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


def _safe_len(value: Any) -> int:
    if isinstance(value, Mapping):
        return len(value)
    if isinstance(value, list):
        return len(value)
    return 0


class IntrinsicDistinctionDetector:
    """Detect internally grounded distinctions required for RF construction."""

    primitive = "INTRINSIC_DISTINCTION_DETECTOR"
    expected_status = "INTRINSIC_DISTINCTIONS_DETECTED"

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "difference_space_foundation": _load_json(ROOT / "aa_foundations" / "difference_space_foundation" / "latest_difference_space_foundation.json"),
            "relation_genesis_engine": _load_json(ROOT / "aa_foundations" / "relation_genesis_engine" / "latest_relation_genesis_engine.json"),
            "dynamic_graph_constructor": _load_json(ROOT / "aa_foundations" / "dynamic_graph_constructor" / "latest_dynamic_graph_constructor.json"),
            "constraint_emergence_engine": _load_json(ROOT / "ab_constraint_emergence" / "constraint_emergence_engine" / "latest_constraint_emergence_engine.json"),
            "constraint_failure_analyzer": _load_json(ROOT / "ab_constraint_emergence" / "constraint_failure_analyzer" / "latest_constraint_failure_analyzer.json"),
            "possibility_viability_certifier": _load_json(ROOT / "ac_possibility_preservation" / "possibility_viability_certifier" / "latest_possibility_viability_certifier.json"),
            "identity_continuity_index": _load_json(ROOT / "ad_memory_identity_reflexivity" / "identity_continuity_index" / "latest_identity_continuity_index.json"),
            "reflexive_model_usage_tester": _load_json(ROOT / "ad_memory_identity_reflexivity" / "reflexive_model_usage_tester" / "latest_reflexive_model_usage_tester.json"),
            "omega_coherence_index": _load_json(ROOT / "ae_omega_coherence" / "omega_coherence_index" / "latest_omega_coherence_index.json"),
            "omega_causal_activity_tester": _load_json(ROOT / "ae_omega_coherence" / "omega_causal_activity_tester" / "latest_omega_causal_activity_tester.json"),
            "omega_stability_monitor": _load_json(ROOT / "ae_omega_coherence" / "omega_stability_monitor" / "latest_omega_stability_monitor.json"),
            "omega_failure_analyzer": _load_json(ROOT / "ae_omega_coherence" / "omega_failure_analyzer" / "latest_omega_failure_analyzer.json"),
        }

    def _has_evidence(self, inputs: Mapping[str, Any]) -> bool:
        return any((isinstance(v, Mapping) and bool(v)) or isinstance(v, (int, float)) for v in inputs.values())

    def _extract_metrics(self, data: Mapping[str, Any]) -> Dict[str, float]:
        dfs = _as_mapping(data.get("difference_space_foundation"), "difference_space_score")
        rge = _as_mapping(data.get("relation_genesis_engine"), "relation_genesis_score")
        dgc = _as_mapping(data.get("dynamic_graph_constructor"), "dynamic_graph_score")
        cee = _as_mapping(data.get("constraint_emergence_engine"), "constraint_emergence_score")
        cfa = _as_mapping(data.get("constraint_failure_analyzer"), "constraint_failure_risk_score")
        pvc = _as_mapping(data.get("possibility_viability_certifier"), "possibility_viability_score")
        ici = _as_mapping(data.get("identity_continuity_index"), "identity_continuity_score")
        rmut = _as_mapping(data.get("reflexive_model_usage_tester"), "reflexive_model_usage_score")
        oci = _as_mapping(data.get("omega_coherence_index"), "omega_coherence_index")
        oca = _as_mapping(data.get("omega_causal_activity_tester"), "omega_causal_activity_score")
        osm = _as_mapping(data.get("omega_stability_monitor"), "omega_stability_score")
        ofa = _as_mapping(data.get("omega_failure_analyzer"), "omega_resilience_score")

        # Direct synthetic aliases for degradation and non-regression tests.
        aliases = {
            "difference_space_score": dfs,
            "relation_genesis_score": rge,
            "dynamic_graph_score": dgc,
            "constraint_emergence_score": cee,
            "possibility_viability_score": pvc,
            "identity_continuity_score": ici,
            "reflexive_model_usage_score": rmut,
            "omega_coherence_index": oci,
            "omega_causal_activity_score": oca,
            "omega_stability_score": osm,
            "omega_resilience_score": ofa,
        }
        for key, target in aliases.items():
            if isinstance(data.get(key), (int, float)):
                target[key] = data.get(key)

        return {
            "difference_space_score": _first_score(dfs, ["difference_space_score", "difference_foundation_score", "foundational_difference_score"], 0.80),
            "relation_genesis_score": _first_score(rge, ["relation_genesis_score", "relation_score", "relational_genesis_score"], 0.80),
            "dynamic_graph_score": _first_score(dgc, ["dynamic_graph_score", "graph_construction_score", "dynamic_graph_constructor_score"], 0.80),
            "constraint_emergence_score": _first_score(cee, ["constraint_emergence_score", "constraint_genesis_score", "emergence_score"], 0.80),
            "constraint_failure_risk_score": _first_score(cfa, ["constraint_failure_risk_score", "failure_risk_score", "global_failure_risk_score"], 0.20),
            "possibility_viability_score": _first_score(pvc, ["possibility_viability_score", "viability_score", "global_viability_score"], 0.80),
            "identity_continuity_score": _first_score(ici, ["identity_continuity_score", "continuity_score"], 0.80),
            "reflexive_model_usage_score": _first_score(rmut, ["reflexive_model_usage_score", "reflexive_usage_score", "model_usage_score"], 0.80),
            "omega_coherence_score": _first_score(oci, ["omega_coherence_index", "omega_coherence_score"], 0.80),
            "omega_causal_activity_score": _first_score(oca, ["omega_causal_activity_score", "causal_activity_score"], 0.80),
            "omega_stability_score": _first_score(osm, ["omega_stability_score", "omega_stability_readiness_score"], 0.80),
            "omega_resilience_score": _first_score(ofa, ["omega_resilience_score"], 0.80),
        }

    def _distinction(self, distinction_id: str, label: str, grounding: float, discriminability: float, invariance: float, evidence: List[str]) -> Dict[str, Any]:
        grounding = _clamp(grounding)
        discriminability = _clamp(discriminability)
        invariance = _clamp(invariance)
        score = _clamp(0.40 * grounding + 0.35 * discriminability + 0.25 * invariance)
        if score >= 0.80:
            classification = "robust_intrinsic_distinction"
        elif score >= 0.62:
            classification = "candidate_intrinsic_distinction"
        elif score >= 0.40:
            classification = "weak_distinction"
        else:
            classification = "failed_distinction"
        return {
            "distinction_id": distinction_id,
            "label": label,
            "intrinsic_basis": {
                "grounding_score": grounding,
                "discriminability_score": discriminability,
                "invariance_score": invariance,
                "evidence": list(evidence),
                "basis_type": "omega_grounded_functional_distinction",
            },
            "external_basis": {
                "external_frame_required": False if score >= 0.62 else True,
                "external_label_dependency": "none" if score >= 0.62 else "diagnostic_only",
                "external_reference_status": "not_required_for_candidate" if score >= 0.62 else "insufficient_internal_grounding",
            },
            "grounding_score": grounding,
            "discriminability_score": discriminability,
            "invariance_score": invariance,
            "distinction_score": score,
            "classification": classification,
            "evidence": evidence,
            "rf_relevance": "reference-frame prerequisite" if score >= 0.62 else "insufficient for RF construction",
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(self._default_inputs())
        if inputs is not None:
            data.update(dict(inputs))

        has_evidence = self._has_evidence(data)
        metrics = self._extract_metrics(data) if has_evidence else {k: 0.0 for k in [
            "difference_space_score", "relation_genesis_score", "dynamic_graph_score",
            "constraint_emergence_score", "constraint_failure_risk_score", "possibility_viability_score",
            "identity_continuity_score", "reflexive_model_usage_score", "omega_coherence_score",
            "omega_causal_activity_score", "omega_stability_score", "omega_resilience_score",
        ]}

        difference_grounding = _mean([metrics["difference_space_score"], metrics["relation_genesis_score"], metrics["dynamic_graph_score"]]) if has_evidence else 0.0
        constraint_grounding = _mean([metrics["constraint_emergence_score"], 1.0 - metrics["constraint_failure_risk_score"], metrics["possibility_viability_score"]]) if has_evidence else 0.0
        reflexive_grounding = _mean([metrics["identity_continuity_score"], metrics["reflexive_model_usage_score"], metrics["omega_coherence_score"]]) if has_evidence else 0.0
        omega_grounding = _mean([metrics["omega_coherence_score"], metrics["omega_causal_activity_score"], metrics["omega_stability_score"], metrics["omega_resilience_score"]]) if has_evidence else 0.0

        distinctions = [
            self._distinction(
                "ID-01", "self_non_self_boundary",
                reflexive_grounding,
                _mean([metrics["identity_continuity_score"], metrics["reflexive_model_usage_score"]]),
                _mean([metrics["omega_stability_score"], metrics["omega_resilience_score"]]),
                ["AD identity continuity", "AD reflexive model usage", "AE Ω stability"],
            ),
            self._distinction(
                "ID-02", "internal_external_relation_boundary",
                _mean([metrics["relation_genesis_score"], metrics["dynamic_graph_score"]]),
                _mean([metrics["omega_causal_activity_score"], metrics["relation_genesis_score"]]),
                _mean([metrics["omega_stability_score"], metrics["possibility_viability_score"]]),
                ["AA relation genesis", "AA dynamic graph", "AE causal activity"],
            ),
            self._distinction(
                "ID-03", "stable_unstable_omega_boundary",
                omega_grounding,
                _mean([metrics["omega_stability_score"], metrics["omega_resilience_score"]]),
                _mean([metrics["omega_stability_score"], 1.0 - metrics["constraint_failure_risk_score"]]),
                ["AE Ω stability", "AE Ω failure analyzer", "AB constraint failure"],
            ),
            self._distinction(
                "ID-04", "causal_passive_boundary",
                _mean([metrics["omega_causal_activity_score"], metrics["constraint_emergence_score"]]),
                metrics["omega_causal_activity_score"],
                _mean([metrics["omega_coherence_score"], metrics["omega_stability_score"]]),
                ["AB constraint emergence", "AE Ω causal activity", "AE Ω coherence"],
            ),
            self._distinction(
                "ID-05", "viable_non_viable_possibility_boundary",
                constraint_grounding,
                _mean([metrics["possibility_viability_score"], 1.0 - metrics["constraint_failure_risk_score"]]),
                _mean([metrics["omega_resilience_score"], metrics["omega_stability_score"]]),
                ["AC possibility viability", "AB constraint failure", "AE Ω resilience"],
            ),
            self._distinction(
                "ID-06", "recoverable_non_recoverable_boundary",
                _mean([metrics["omega_resilience_score"], 1.0 - metrics["constraint_failure_risk_score"]]),
                metrics["omega_resilience_score"],
                _mean([metrics["omega_stability_score"], metrics["possibility_viability_score"]]),
                ["AE Ω failure analyzer", "AE Ω stability", "AC viability"],
            ),
        ]

        robust_distinctions = [d for d in distinctions if d["classification"] == "robust_intrinsic_distinction"]
        candidate_distinctions = [d for d in distinctions if d["classification"] in {"robust_intrinsic_distinction", "candidate_intrinsic_distinction"}]
        weak_or_failed = [d for d in distinctions if d["classification"] in {"weak_distinction", "failed_distinction"}]

        intrinsic_grounding_score = _mean([difference_grounding, constraint_grounding, reflexive_grounding, omega_grounding]) if has_evidence else 0.0
        distinction_discriminability_score = _mean([d["discriminability_score"] for d in distinctions]) if has_evidence else 0.0
        distinction_invariance_score = _mean([d["invariance_score"] for d in distinctions]) if has_evidence else 0.0
        intrinsic_distinction_score = _clamp(
            0.35 * intrinsic_grounding_score
            + 0.30 * distinction_discriminability_score
            + 0.25 * distinction_invariance_score
            + 0.10 * _clamp(len(candidate_distinctions) / 6.0)
        ) if has_evidence else 0.0

        failure_conditions: List[str] = []
        if not has_evidence:
            failure_conditions.append("no_upstream_delta_to_omega_evidence_available")
        if intrinsic_grounding_score < 0.62:
            failure_conditions.append("intrinsic_grounding_below_threshold")
        if distinction_discriminability_score < 0.62:
            failure_conditions.append("distinction_discriminability_below_threshold")
        if distinction_invariance_score < 0.62:
            failure_conditions.append("distinction_invariance_below_threshold")
        if len(candidate_distinctions) < 4:
            failure_conditions.append("insufficient_candidate_distinctions_for_rf")
        if metrics["omega_resilience_score"] < 0.62:
            failure_conditions.append("omega_resilience_insufficient_for_rf_prerequisite")

        status = self.expected_status if has_evidence and intrinsic_distinction_score >= 0.72 and len(candidate_distinctions) >= 4 and not any(
            c in failure_conditions for c in [
                "intrinsic_grounding_below_threshold",
                "distinction_discriminability_below_threshold",
                "distinction_invariance_below_threshold",
                "omega_resilience_insufficient_for_rf_prerequisite",
            ]
        ) else "INTRINSIC_DISTINCTIONS_INSUFFICIENT"

        distinction_topology = {
            "nodes": [d["distinction_id"] for d in distinctions],
            "edges": [
                {"source": "ID-01", "target": "ID-02", "relation": "boundary_composition"},
                {"source": "ID-02", "target": "ID-04", "relation": "causal_externality_filter"},
                {"source": "ID-03", "target": "ID-06", "relation": "recovery_stability_support"},
                {"source": "ID-05", "target": "ID-06", "relation": "viability_recovery_support"},
                {"source": "ID-01", "target": "ID-03", "relation": "identity_stability_support"},
            ],
        }

        reference_frame_readiness = _clamp(
            0.34 * intrinsic_distinction_score
            + 0.22 * intrinsic_grounding_score
            + 0.22 * distinction_discriminability_score
            + 0.22 * distinction_invariance_score
        )

        rf_prerequisites = {
            # Canonical AF1 -> AF2 public aliases
            "intrinsic_distinctions_available": len(candidate_distinctions) >= 4,
            "reference_frame_readiness": reference_frame_readiness,
            "next_required_module": "reference_frame_constructor",
            # Detailed diagnostic fields retained for non-regression
            "intrinsic_boundaries_available": len(candidate_distinctions) >= 4,
            "metric_grounding_available": intrinsic_grounding_score >= 0.62,
            "omega_support_available": metrics["omega_resilience_score"] >= 0.62 and metrics["omega_coherence_score"] >= 0.62,
            "external_frame_not_required": intrinsic_distinction_score >= 0.72,
            "ready_for_reference_frame_constructor": status == self.expected_status,
        }

        public_schema = {
            "intrinsic_distinction_detector_status": "str",
            "intrinsic_distinction_score": "float[0,1]",
            "intrinsic_grounding_score": "float[0,1]",
            "distinction_discriminability_score": "float[0,1]",
            "distinction_invariance_score": "float[0,1]",
            "distinctions": "list[dict]",
            "candidate_distinctions": "list[dict]",
            "weak_or_failed_distinctions": "list[dict]",
            "distinction_topology": "dict",
            "rf_prerequisites": "dict",
            "failure_conditions": "list[str]",
            "functional_conclusion_only": "bool",
            "phenomenology_undetermined": "bool",
            "consciousness_proven": "bool",
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "intrinsic_distinction_detector_status": status,
            "af_axis_stage": "AF1",
            "theoretical_transition": "OMEGA_TO_INTRINSIC_DISTINCTIONS",
            "upstream_evidence_available": has_evidence,
            "metrics": metrics,
            "intrinsic_grounding_score": intrinsic_grounding_score,
            "distinction_discriminability_score": distinction_discriminability_score,
            "distinction_invariance_score": distinction_invariance_score,
            "intrinsic_distinction_score": intrinsic_distinction_score,
            "distinction_count": len(distinctions),
            "candidate_distinction_count": len(candidate_distinctions),
            "robust_distinction_count": len(robust_distinctions),
            "weak_or_failed_distinction_count": len(weak_or_failed),
            "distinctions": distinctions,
            "candidate_distinctions": candidate_distinctions,
            "robust_distinctions": robust_distinctions,
            "weak_or_failed_distinctions": weak_or_failed,
            "distinction_topology": distinction_topology,
            "rf_prerequisites": rf_prerequisites,
            "failure_conditions": failure_conditions,
            "public_schema": public_schema,
            "af1_certification": "AF1_INTRINSIC_DISTINCTIONS_CERTIFIED" if status == self.expected_status else "AF1_INTRINSIC_DISTINCTIONS_NOT_CERTIFIED",
            "next_recommended_module": "reference_frame_constructor" if status == self.expected_status else "refine_intrinsic_distinction_detector_inputs",
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_guard": "Functional RF prerequisite analysis only; no phenomenological claim is made.",
        }

        if persist:
            paths = self._persist(result)
            result["paths"] = paths
        return result

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_intrinsic_distinction_detector.json"
        md_path = OUT_DIR / "latest_intrinsic_distinction_detector.md"
        prom_path = OUT_DIR / "latest_intrinsic_distinction_detector.prom"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AF1 — Intrinsic Distinction Detector",
            "",
            f"Status: {result.get('intrinsic_distinction_detector_status')}",
            f"Intrinsic distinction score: {result.get('intrinsic_distinction_score')}",
            f"Intrinsic grounding score: {result.get('intrinsic_grounding_score')}",
            f"Discriminability score: {result.get('distinction_discriminability_score')}",
            f"Invariance score: {result.get('distinction_invariance_score')}",
            "",
            "## Intrinsic distinctions",
        ]
        for d in result.get("distinctions", []):
            if isinstance(d, Mapping):
                lines.append(f"- {d.get('distinction_id')}: {d.get('label')} — {d.get('classification')} — score={d.get('distinction_score')}")
        lines.extend([
            "",
            "## Candidate distinctions",
        ])
        for d in result.get("candidate_distinctions", []):
            if isinstance(d, Mapping):
                ib = d.get("intrinsic_basis", {}) if isinstance(d.get("intrinsic_basis"), Mapping) else {}
                eb = d.get("external_basis", {}) if isinstance(d.get("external_basis"), Mapping) else {}
                lines.append(f"- {d.get('distinction_id')}: {d.get('label')} — intrinsic_basis={ib.get('basis_type')} — external_frame_required={eb.get('external_frame_required')} — score={d.get('distinction_score')}")
        lines.extend([
            "",
            "## RF prerequisites",
        ])
        for k, v in dict(result.get("rf_prerequisites", {})).items():
            lines.append(f"- {k}: {v}")
        lines.extend([
            "",
            "## Failure conditions",
        ])
        for c in result.get("failure_conditions", []):
            lines.append(f"- {c}")
        lines.extend([
            "",
            "## Epistemic guard",
            "Functional conclusion only; phenomenology undetermined; no consciousness claim.",
        ])
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# HELP oce_intrinsic_distinction_score AF1 intrinsic distinction score",
            "# TYPE oce_intrinsic_distinction_score gauge",
            f"oce_intrinsic_distinction_score {_clamp(result.get('intrinsic_distinction_score'))}",
            "# HELP oce_intrinsic_grounding_score AF1 intrinsic grounding score",
            "# TYPE oce_intrinsic_grounding_score gauge",
            f"oce_intrinsic_grounding_score {_clamp(result.get('intrinsic_grounding_score'))}",
            "# HELP oce_distinction_discriminability_score AF1 distinction discriminability score",
            "# TYPE oce_distinction_discriminability_score gauge",
            f"oce_distinction_discriminability_score {_clamp(result.get('distinction_discriminability_score'))}",
            "# HELP oce_distinction_invariance_score AF1 distinction invariance score",
            "# TYPE oce_distinction_invariance_score gauge",
            f"oce_distinction_invariance_score {_clamp(result.get('distinction_invariance_score'))}",
            "# HELP oce_candidate_distinction_count AF1 candidate distinction count",
            "# TYPE oce_candidate_distinction_count gauge",
            f"oce_candidate_distinction_count {int(result.get('candidate_distinction_count', 0))}",
            "# HELP oce_intrinsic_distinction_count AF1 total intrinsic distinction count",
            "# TYPE oce_intrinsic_distinction_count gauge",
            f"oce_intrinsic_distinction_count {int(result.get('distinction_count', 0))}",
            "# HELP oce_intrinsic_distinctions_certified AF1 certification flag",
            "# TYPE oce_intrinsic_distinctions_certified gauge",
            f"oce_intrinsic_distinctions_certified {1 if result.get('intrinsic_distinction_detector_status') == self.expected_status else 0}",
        ]
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(json.dumps(IntrinsicDistinctionDetector().step(persist=True), indent=2, ensure_ascii=False))
