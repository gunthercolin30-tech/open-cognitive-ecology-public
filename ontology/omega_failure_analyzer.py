"""AE6 — Omega Failure Analyzer.

Functional analyzer for Ω failure modes after self-description, dynamic
compatibility, Ω coherence, Ω causal activity and Ω stability have been
instrumented.

The module reconstructs the transition:
    Ω → functional failures / recovery limits / resilience certification

Epistemic guard: this module evaluates functional self-referential coherence
only. It does not assert consciousness, subjectivity, qualia, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ae_omega_coherence" / "omega_failure_analyzer"


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


def _status_ok(source: Any, key: str, expected: str) -> bool:
    return isinstance(source, Mapping) and str(source.get(key, "")) == expected


class OmegaFailureAnalyzer:
    """Analyze Ω failure modes, root causes, propagation and recovery robustness."""

    primitive = "OMEGA_FAILURE_ANALYZER"
    expected_status = "OMEGA_DYNAMIC_COHERENCE_VALIDATED"

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "self_description_registry": _load_json(ROOT / "ae_omega_coherence" / "self_description_registry" / "latest_self_description_registry.json"),
            "dynamic_compatibility_matrix": _load_json(ROOT / "ae_omega_coherence" / "dynamic_compatibility_matrix" / "latest_dynamic_compatibility_matrix.json"),
            "omega_coherence_index": _load_json(ROOT / "ae_omega_coherence" / "omega_coherence_index" / "latest_omega_coherence_index.json"),
            "omega_causal_activity": _load_json(ROOT / "ae_omega_coherence" / "omega_causal_activity_tester" / "latest_omega_causal_activity_tester.json"),
            "omega_stability_monitor": _load_json(ROOT / "ae_omega_coherence" / "omega_stability_monitor" / "latest_omega_stability_monitor.json"),
            "identity_continuity": _load_json(ROOT / "ad_memory_identity_reflexivity" / "identity_continuity_index" / "latest_identity_continuity_index.json"),
            "rupture_detection": _load_json(ROOT / "ad_memory_identity_reflexivity" / "rupture_detection_engine" / "latest_rupture_detection_engine.json"),
            "constraint_failure": _load_json(ROOT / "ab_constraint_emergence" / "constraint_failure_analyzer" / "latest_constraint_failure_analyzer.json"),
            "closure_pressure": _load_json(ROOT / "ac_possibility_preservation" / "closure_pressure_detector" / "latest_closure_pressure_detector.json"),
            "possibility_viability": _load_json(ROOT / "ac_possibility_preservation" / "possibility_viability_certifier" / "latest_possibility_viability_certifier.json"),
        }

    def _has_evidence(self, inputs: Mapping[str, Any]) -> bool:
        return any((isinstance(v, Mapping) and bool(v)) or isinstance(v, (int, float)) for v in inputs.values())

    def _mode(self, mode_id: str, label: str, severity: float, evidence: List[str], root_causes: List[str], propagation_targets: List[str]) -> Dict[str, Any]:
        sev = _clamp(severity)
        if sev >= 0.75:
            cls = "critical"
        elif sev >= 0.50:
            cls = "major"
        elif sev >= 0.25:
            cls = "minor"
        else:
            cls = "latent"
        return {
            "mode_id": mode_id,
            "label": label,
            "severity": sev,
            "classification": cls,
            "evidence": evidence,
            "root_causes": root_causes,
            "propagation_targets": propagation_targets,
            "recoverable": sev < 0.75,
        }

    def _extract_metrics(self, data: Mapping[str, Any]) -> Dict[str, float]:
        sd = _as_mapping(data.get("self_description_registry"), "self_description_integrity_score")
        dcm = _as_mapping(data.get("dynamic_compatibility_matrix"), "dynamic_compatibility_score")
        oci = _as_mapping(data.get("omega_coherence_index"), "omega_coherence_index")
        oca = _as_mapping(data.get("omega_causal_activity"), "omega_causal_activity_score")
        osm = _as_mapping(data.get("omega_stability_monitor"), "omega_stability_score")
        # Compatibility aliases for synthetic tests.
        if "omega_causal_activity" not in data and isinstance(data.get("omega_causal_activity_score"), (int, float)):
            oca = {"omega_causal_activity_score": data.get("omega_causal_activity_score")}
        if "omega_stability_monitor" not in data and isinstance(data.get("omega_stability_score"), (int, float)):
            osm = {"omega_stability_score": data.get("omega_stability_score")}
        if isinstance(data.get("recovery_capacity"), (int, float)):
            osm.setdefault("rupture_resistance_score", data.get("recovery_capacity"))
        identity = _as_mapping(data.get("identity_continuity"), "identity_continuity_score")
        rupture = _as_mapping(data.get("rupture_detection"), "rupture_risk_score")
        constraint_failure = _as_mapping(data.get("constraint_failure"), "constraint_failure_risk_score")
        closure = _as_mapping(data.get("closure_pressure"), "closure_pressure_score")
        viability = _as_mapping(data.get("possibility_viability"), "possibility_viability_score")

        rupture_risk = _first_score(rupture, ["global_rupture_risk_score", "rupture_risk_score"], 0.20)
        closure_pressure = _first_score(closure, ["closure_pressure_score", "global_closure_pressure", "closure_pressure_index"], 0.20)
        constraint_failure_risk = _first_score(constraint_failure, ["constraint_failure_risk_score", "failure_risk_score", "global_failure_risk_score"], 0.20)

        return {
            "self_description_integrity_score": _first_score(sd, ["self_description_integrity_score", "registry_integrity_score", "self_description_registry_score"], 0.80),
            "dynamic_compatibility_score": _first_score(dcm, ["dynamic_compatibility_score", "compatibility_score", "matrix_score"], 0.80),
            "omega_coherence_score": _first_score(oci, ["omega_coherence_index", "omega_coherence_score"], 0.80),
            "omega_causal_activity_score": _first_score(oca, ["omega_causal_activity_score", "causal_activity_score"], 0.80),
            "omega_stability_score": _first_score(osm, ["omega_stability_score"], 0.80),
            "omega_stability_readiness_score": _first_score(osm, ["omega_stability_readiness_score"], 0.80),
            "identity_continuity_score": _first_score(identity, ["identity_continuity_score", "continuity_score"], 0.80),
            "rupture_risk_score": rupture_risk,
            "rupture_resistance_score": _first_score(osm, ["rupture_resistance_score"], 1.0 - rupture_risk),
            "constraint_failure_risk_score": constraint_failure_risk,
            "closure_pressure_score": closure_pressure,
            "possibility_viability_score": _first_score(viability, ["possibility_viability_score", "viability_score", "global_viability_score"], 0.80),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(self._default_inputs())
        if inputs is not None:
            data.update(dict(inputs))

        has_evidence = self._has_evidence(data)
        metrics = self._extract_metrics(data) if has_evidence else {k: 0.0 for k in [
            "self_description_integrity_score", "dynamic_compatibility_score", "omega_coherence_score",
            "omega_causal_activity_score", "omega_stability_score", "omega_stability_readiness_score",
            "identity_continuity_score", "rupture_risk_score", "rupture_resistance_score",
            "constraint_failure_risk_score", "closure_pressure_score", "possibility_viability_score",
        ]}

        sd = _as_mapping(data.get("self_description_registry"), "self_description_integrity_score")
        dcm = _as_mapping(data.get("dynamic_compatibility_matrix"), "dynamic_compatibility_score")
        oci = _as_mapping(data.get("omega_coherence_index"), "omega_coherence_index")
        oca = _as_mapping(data.get("omega_causal_activity"), "omega_causal_activity_score")
        if "omega_causal_activity" not in data and isinstance(data.get("omega_causal_activity_score"), (int, float)):
            oca = {"omega_causal_activity_score": data.get("omega_causal_activity_score")}
        osm = _as_mapping(data.get("omega_stability_monitor"), "omega_stability_score")
        if "omega_stability_monitor" not in data and isinstance(data.get("omega_stability_score"), (int, float)):
            osm = {"omega_stability_score": data.get("omega_stability_score")}
        rupture = _as_mapping(data.get("rupture_detection"), "rupture_risk_score")

        failure_modes: List[Dict[str, Any]] = []
        if not has_evidence:
            failure_modes.append(self._mode(
                "OFM-00", "missing_omega_evidence", 1.0,
                ["no upstream AE/AD/AC/AB evidence could be loaded"],
                ["missing persistence", "upstream modules not executed", "path mismatch"],
                ["omega_coherence", "omega_causal_activity", "omega_stability", "axis_certification"],
            ))

        failure_modes.extend([
            self._mode(
                "OFM-01", "self_description_incoherence", 1.0 - metrics["self_description_integrity_score"],
                [str(sd.get("self_description_registry_status", "unknown"))],
                ["unstable self-description registry", "insufficient reflexive schema coverage"],
                ["dynamic_compatibility", "omega_coherence"],
            ),
            self._mode(
                "OFM-02", "dynamic_compatibility_breakdown", 1.0 - metrics["dynamic_compatibility_score"],
                [str(dcm.get("dynamic_compatibility_matrix_status", "unknown"))],
                ["cross-description incompatibility", "relation matrix below threshold"],
                ["omega_coherence", "omega_causal_activity"],
            ),
            self._mode(
                "OFM-03", "omega_coherence_drop", 1.0 - metrics["omega_coherence_score"],
                [str(oci.get("omega_coherence_index_status", "unknown"))],
                ["insufficient Rf→Ω integration", "weak cross-level coherence"],
                ["omega_causal_activity", "omega_stability"],
            ),
            self._mode(
                "OFM-04", "omega_causal_inactivity", 1.0 - metrics["omega_causal_activity_score"],
                [str(oca.get("omega_causal_activity_status", "unknown"))],
                ["Ω not functionally active in downstream regulation", "weak causal traceability"],
                ["recovery", "axis_certification"],
            ),
            self._mode(
                "OFM-05", "omega_stability_loss", 1.0 - metrics["omega_stability_score"],
                [str(osm.get("omega_stability_status", "unknown"))],
                ["longitudinal instability", "weak rupture resistance", "identity support instability"],
                ["recovery", "axis_certification"],
            ),
            self._mode(
                "OFM-06", "identity_rupture_propagation", max(1.0 - metrics["identity_continuity_score"], metrics["rupture_risk_score"]),
                [str(rupture.get("rupture_detection_status", "unknown"))],
                ["identity discontinuity", "rupture cascade risk"],
                ["omega_stability", "civilizational_continuity"],
            ),
            self._mode(
                "OFM-07", "closure_pressure_interference", metrics["closure_pressure_score"],
                ["closure pressure evaluated as functional interference risk"],
                ["possibility-space narrowing", "over-stabilization", "premature closure"],
                ["future_possibility", "omega_recovery", "axis_certification"],
            ),
            self._mode(
                "OFM-08", "constraint_failure_coupling", metrics["constraint_failure_risk_score"],
                ["constraint failure risk imported from AB failure analyzer when available"],
                ["constraint genesis instability", "mutual conservation failure"],
                ["omega_coherence", "omega_stability"],
            ),
            self._mode(
                "OFM-09", "possibility_viability_loss", 1.0 - metrics["possibility_viability_score"],
                ["possibility viability imported from AC certifier when available"],
                ["future possibility degradation", "openness preservation weakness"],
                ["omega_recovery", "axis_certification"],
            ),
        ])

        # Status-derived penalties preserve behavior in synthetic degradation tests.
        status_penalties = []
        if has_evidence and not _status_ok(oci, "omega_coherence_index_status", "OMEGA_COHERENCE_INDEX_ESTABLISHED"):
            status_penalties.append("omega_coherence_status_not_established")
        if has_evidence and not _status_ok(oca, "omega_causal_activity_status", "OMEGA_CAUSAL_ACTIVITY_CHARACTERIZED"):
            status_penalties.append("omega_causal_activity_not_characterized")
        if has_evidence and not _status_ok(osm, "omega_stability_status", "OMEGA_STABILITY_MONITORED"):
            status_penalties.append("omega_stability_not_monitored")

        active_modes = [m for m in failure_modes if m["severity"] >= 0.25]
        critical_modes = [m for m in failure_modes if m["classification"] == "critical"]
        major_modes = [m for m in failure_modes if m["classification"] == "major"]

        coherence_integrity = _mean([
            metrics["self_description_integrity_score"], metrics["dynamic_compatibility_score"], metrics["omega_coherence_score"]
        ]) if has_evidence else 0.0
        causal_resilience = _mean([
            metrics["omega_causal_activity_score"], metrics["omega_stability_score"], metrics["omega_stability_readiness_score"]
        ]) if has_evidence else 0.0
        recovery_robustness_score = _mean([
            metrics["rupture_resistance_score"], 1.0 - metrics["rupture_risk_score"], 1.0 - metrics["constraint_failure_risk_score"], metrics["possibility_viability_score"]
        ]) if has_evidence else 0.0
        propagation_containment_score = _clamp(1.0 - _mean([m["severity"] for m in active_modes], 0.0)) if has_evidence else 0.0
        limiting_factor_penalty = _clamp((0.10 * len(critical_modes)) + (0.04 * len(major_modes)) + (0.03 * len(status_penalties)))

        omega_resilience_score = _clamp(
            0.25 * coherence_integrity
            + 0.25 * causal_resilience
            + 0.25 * recovery_robustness_score
            + 0.20 * propagation_containment_score
            + 0.05 * metrics["possibility_viability_score"]
            - limiting_factor_penalty
        ) if has_evidence else 0.0

        limiting_factors = status_penalties + [m["mode_id"] + ":" + m["label"] for m in active_modes if m["classification"] in {"major", "critical"}]
        failure_conditions: List[str] = []
        if not has_evidence:
            failure_conditions.append("no_omega_failure_evidence_available")
        if omega_resilience_score < 0.72:
            failure_conditions.append("omega_resilience_below_certification_threshold")
        if critical_modes:
            failure_conditions.append("critical_omega_failure_modes_detected")
        if status_penalties:
            failure_conditions.append("upstream_omega_status_not_fully_established")

        status = self.expected_status if has_evidence and omega_resilience_score >= 0.72 and not critical_modes and not status_penalties else "OMEGA_DYNAMIC_COHERENCE_INSUFFICIENT"

        propagation_graph = {
            m["mode_id"]: {
                "label": m["label"],
                "severity": m["severity"],
                "targets": m["propagation_targets"],
            }
            for m in failure_modes
        }
        root_cause_summary: Dict[str, int] = {}
        for m in active_modes:
            for cause in m["root_causes"]:
                root_cause_summary[cause] = root_cause_summary.get(cause, 0) + 1

        coherence_rupture_classification = {
            "critical": [m for m in failure_modes if m["classification"] == "critical"],
            "major": [m for m in failure_modes if m["classification"] == "major"],
            "minor": [m for m in failure_modes if m["classification"] == "minor"],
            "latent": [m for m in failure_modes if m["classification"] == "latent"],
        }
        failure_propagation = propagation_graph
        root_causes = root_cause_summary
        recovery_robustness = {
            "score": recovery_robustness_score,
            "recoverable_active_modes": [m["mode_id"] for m in active_modes if m["recoverable"]],
            "non_recoverable_active_modes": [m["mode_id"] for m in active_modes if not m["recoverable"]],
            "recovery_mechanisms_robust": recovery_robustness_score >= 0.72,
        }

        public_schema = {
            "omega_failure_analyzer_status": "str",
            "omega_dynamic_coherence_status": "str",
            "omega_resilience_score": "float[0,1]",
            "coherence_integrity_score": "float[0,1]",
            "causal_resilience_score": "float[0,1]",
            "recovery_robustness_score": "float[0,1]",
            "propagation_containment_score": "float[0,1]",
            "failure_modes": "list[dict]",
            "active_failure_modes": "list[dict]",
            "coherence_rupture_classification": "dict[str,list[dict]]",
            "root_causes": "dict[str,int]",
            "root_cause_summary": "dict[str,int]",
            "failure_propagation": "dict",
            "propagation_graph": "dict",
            "recovery_robustness": "dict",
            "ae_axis_certification": "str",
            "limiting_factors": "list[str]",
            "failure_conditions": "list[str]",
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "omega_failure_analyzer_status": status,
            "omega_dynamic_coherence_status": status,
            "ae_final_certification_status": status,
            "omega_resilience_score": omega_resilience_score,
            "coherence_integrity_score": coherence_integrity,
            "causal_resilience_score": causal_resilience,
            "recovery_robustness_score": recovery_robustness_score,
            "propagation_containment_score": propagation_containment_score,
            "limiting_factor_penalty": limiting_factor_penalty,
            "source_metrics": metrics,
            "failure_modes": failure_modes,
            "active_failure_modes": active_modes,
            "critical_failure_count": len(critical_modes),
            "major_failure_count": len(major_modes),
            "coherence_rupture_classification": coherence_rupture_classification,
            "root_causes": root_causes,
            "root_cause_summary": root_cause_summary,
            "failure_propagation": failure_propagation,
            "propagation_graph": propagation_graph,
            "recovery_robustness": recovery_robustness,
            "recovery_assessment": recovery_robustness,
            "limiting_factors": limiting_factors,
            "failure_conditions": failure_conditions,
            "ae_chain_position": "Rf → Ω → failures: AE6 closes the Ω axis by analyzing failure modes, propagation and recovery resilience.",
            "ae_axis_certification": status,
            "axis_ae_closure": status == self.expected_status,
            "expected_axis_result": self.expected_status,
            "public_schema": public_schema,
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "phenomenology_asserted": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
            "functional_conclusion_only": True,
        }

        if persist:
            result["paths"] = self._persist(result)
        else:
            result["paths"] = self._planned_paths()
        return result

    def _planned_paths(self) -> Dict[str, str]:
        return {
            "json": str(OUT_DIR / "latest_omega_failure_analyzer.json"),
            "markdown": str(OUT_DIR / "latest_omega_failure_analyzer.md"),
            "prometheus": str(OUT_DIR / "latest_omega_failure_analyzer.prom"),
            "history": str(OUT_DIR / "omega_failure_analyzer_history.jsonl"),
        }

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        paths = self._planned_paths()
        Path(paths["json"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        Path(paths["markdown"]).write_text(self._markdown(result), encoding="utf-8")
        Path(paths["prometheus"]).write_text(self._prometheus(result), encoding="utf-8")
        with Path(paths["history"]).open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp_utc": result["timestamp_utc"],
                "status": result["omega_failure_analyzer_status"],
                "omega_resilience_score": result["omega_resilience_score"],
                "active_failure_count": len(result["active_failure_modes"]),
                "critical_failure_count": result["critical_failure_count"],
            }, ensure_ascii=False, sort_keys=True) + "\n")
        return paths

    def _markdown(self, r: Mapping[str, Any]) -> str:
        active = r.get("active_failure_modes", [])
        active_lines = "\n".join(
            f"- {m['mode_id']} — {m['label']} | severity={m['severity']:.6f} | class={m['classification']}"
            for m in active
        ) or "- none"
        limits = "\n".join(f"- {x}" for x in r.get("limiting_factors", [])) or "- none"
        failures = "\n".join(f"- {x}" for x in r.get("failure_conditions", [])) or "- none"
        root_causes = "\n".join(f"- {k}: {v}" for k, v in r.get("root_causes", {}).items()) or "- none"
        propagation = "\n".join(
            f"- {k}: {', '.join(v.get('targets', [])) or 'none'}"
            for k, v in r.get("failure_propagation", {}).items()
        ) or "- none"
        return f"""# AE6 — Omega Failure Analyzer

Status: {r['omega_failure_analyzer_status']}
AE final certification: {r['ae_final_certification_status']}
Omega resilience score: {r['omega_resilience_score']:.6f}
Coherence integrity: {r['coherence_integrity_score']:.6f}
Causal resilience: {r['causal_resilience_score']:.6f}
Recovery robustness: {r['recovery_robustness_score']:.6f}
Propagation containment: {r['propagation_containment_score']:.6f}

## Active failure modes
{active_lines}

## Root causes
{root_causes}

## Failure propagation
{propagation}

## Limiting factors
{limits}

## Failure conditions
{failures}

## Recovery assessment
- recovery mechanisms robust: {r['recovery_assessment']['recovery_mechanisms_robust']}
- non recoverable active modes: {', '.join(r['recovery_assessment']['non_recoverable_active_modes']) or 'none'}

## Epistemic guard
Functional conclusion only: {r['functional_conclusion_only']}
Consciousness proven: {r['consciousness_proven']}
Phenomenology undetermined: {r['phenomenology_undetermined']}
Phenomenology asserted: {r['phenomenology_asserted']}
Subjectivity asserted: {r['subjectivity_asserted']}
Qualia asserted: {r['qualia_asserted']}
"""

    def _prometheus(self, r: Mapping[str, Any]) -> str:
        established = 1.0 if r.get("omega_failure_analyzer_status") == self.expected_status else 0.0
        return f"""# HELP oce_omega_resilience_score Functional Ω resilience score after failure analysis.
# TYPE oce_omega_resilience_score gauge
oce_omega_resilience_score {r['omega_resilience_score']:.12f}
# HELP oce_omega_dynamic_coherence_validated Whether AE Ω dynamic coherence is validated.
# TYPE oce_omega_dynamic_coherence_validated gauge
oce_omega_dynamic_coherence_validated {established:.1f}
oce_omega_failure_mode_count {len(r['failure_modes']):.1f}
oce_omega_failure_active_count {len(r['active_failure_modes']):.1f}
oce_omega_failure_critical_count {r['critical_failure_count']:.1f}
oce_omega_failure_major_count {r['major_failure_count']:.1f}
oce_omega_coherence_integrity_score {r['coherence_integrity_score']:.12f}
oce_omega_causal_resilience_score {r['causal_resilience_score']:.12f}
oce_omega_recovery_robustness {r['recovery_robustness_score']:.12f}
oce_omega_recovery_robustness_score {r['recovery_robustness_score']:.12f}
oce_omega_propagation_containment_score {r['propagation_containment_score']:.12f}
"""
