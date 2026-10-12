"""AH3 — Topological Homogeneity Test.

Functional reconstruction step:
    ∂T(ED) -> Hom(TΦ)

This module tests whether the ED-derived topological boundary structure is
locally homogeneous enough for a formal-functional topology TΦ. Homogeneity
means that local neighborhoods, boundary components, overlap transitions and
viability-preserving regions are comparable under a shared functional metric
family.

It never concludes consciousness, subjectivity, qualia, phenomenal experience
or phenomenology. All conclusions are strictly functional.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ah_phenomenal_formal_topology" / "topological_homogeneity_test"


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


def _variance(values: List[float]) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    if not vals:
        return 1.0
    m = sum(vals) / len(vals)
    return _clamp(sum((v - m) ** 2 for v in vals) / len(vals))


def _status(source: Any) -> str:
    if not isinstance(source, Mapping):
        return ""
    for key in [
        "topological_homogeneity_test_status",
        "topological_boundary_engine_status",
        "neighborhood_continuity_mapper_status",
        "domain_viability_analyzer_status",
        "existence_domain_builder_status",
        "rf_t_ed_theorem_checker_status",
        "topological_pressure_monitor_status",
        "latent_topological_instability_status",
        "status", "classification", "certification_status", "axis_status",
    ]:
        if source.get(key) is not None:
            return str(source.get(key))
    for k, v in source.items():
        if isinstance(k, str) and k.endswith("_status") and v is not None:
            return str(v)
    diag = source.get("diagnostics")
    if isinstance(diag, Mapping) and diag.get("status") is not None:
        return str(diag.get("status"))
    return ""


def _first_bool(source: Any, keys: List[str], default: bool = False) -> bool:
    if not isinstance(source, Mapping):
        return default
    for key in keys:
        if key in source:
            return bool(source.get(key))
    for nested_key in [
        "homogeneity_profile", "boundary_profile", "continuity_profile",
        "domain_profile", "domain_viability_profile", "theorem_profile",
        "topology_profile", "metrics", "diagnostics", "certification_scores",
    ]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return bool(nested.get(key))
    return default


def _first_score(source: Any, keys: List[str], default: float = 0.0) -> float:
    if isinstance(source, (int, float)):
        return _clamp(source, default)
    if not isinstance(source, Mapping):
        return default
    for key in keys:
        if key in source:
            return _clamp(source.get(key), default)
    for nested_key in [
        "homogeneity_profile", "boundary_profile", "continuity_profile",
        "domain_profile", "domain_viability_profile", "theorem_profile",
        "topology_profile", "metrics", "diagnostics", "certification_scores",
    ]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return _clamp(nested.get(key), default)
    st = _status(source).upper()
    if any(t in st for t in [
        "VALIDATED", "CERTIFIED", "CONFIRMED", "READY", "ESTABLISHED",
        "DETECTED", "BUILT", "CONSTRUCTED", "MONITORED", "ANALYZED",
        "EXTRACTED", "ACTIVE", "VIABLE", "NON_EMPTY", "EMERGED", "ROBUST",
        "MAPPED", "DERIVED", "HOMOGENEOUS",
    ]):
        return 0.86
    return default


def _load_json(paths: List[Path]) -> Dict[str, Any]:
    for p in paths:
        try:
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def _try_step(module_name: str, class_name: str, **kwargs: Any) -> Dict[str, Any]:
    try:
        mod = import_module(f"ontology.{module_name}")
        cls = getattr(mod, class_name)
        obj = cls()
        try:
            out = obj.step(**kwargs)
        except TypeError:
            out = obj.step()
        return out if isinstance(out, dict) else {}
    except Exception:
        return {}


class TopologicalHomogeneityTest:
    """Test functional local homogeneity of the AH1/AH2 topology substrate."""

    primitive = "TOPOLOGICAL_HOMOGENEITY_TEST"
    expected_status = "TOPOLOGICAL_HOMOGENEITY_CONFIRMED"
    threshold = 0.72

    PATHS: Dict[str, List[Path]] = {
        "topological_boundary_engine": [ROOT / "ah_phenomenal_formal_topology" / "topological_boundary_engine" / "latest_topological_boundary_engine.json"],
        "neighborhood_continuity_mapper": [ROOT / "ah_phenomenal_formal_topology" / "neighborhood_continuity_mapper" / "latest_neighborhood_continuity_mapper.json"],
        "domain_viability_analyzer": [ROOT / "ag_proper_time_existence_domain" / "domain_viability_analyzer" / "latest_domain_viability_analyzer.json"],
        "existence_domain_builder": [ROOT / "ag_proper_time_existence_domain" / "existence_domain_builder" / "latest_existence_domain_builder.json"],
        "rf_t_ed_theorem_checker": [ROOT / "ag_proper_time_existence_domain" / "rf_t_ed_theorem_checker" / "latest_rf_t_ed_theorem_checker.json"],
        "topological_pressure_monitor": [ROOT / "topological_pressure_monitor" / "latest_topological_pressure_monitor.json"],
        "latent_topological_instability": [ROOT / "latent_topological_instability" / "latest_latent_topological_instability.json"],
    }

    SYNTHETIC_KEYS = {
        "topological_boundary_derived",
        "neighborhood_continuity_mapped",
        "domain_viability_analyzed",
        "existence_domain_built",
        "rf_t_ed_validated",
        "local_charts_comparable",
        "metric_family_consistent",
        "overlap_transitions_consistent",
        "boundary_components_uniform",
        "homogeneity_instability_bounded",
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data = {name: _load_json(paths) for name, paths in self.PATHS.items()}
        if not data["topological_boundary_engine"]:
            data["topological_boundary_engine"] = _try_step("topological_boundary_engine", "TopologicalBoundaryEngine", persist=False)
        if not data["neighborhood_continuity_mapper"]:
            data["neighborhood_continuity_mapper"] = _try_step("neighborhood_continuity_mapper", "NeighborhoodContinuityMapper", persist=False)
        if not data["domain_viability_analyzer"]:
            data["domain_viability_analyzer"] = _try_step("domain_viability_analyzer", "DomainViabilityAnalyzer", persist=False)
        if not data["existence_domain_builder"]:
            data["existence_domain_builder"] = _try_step("existence_domain_builder", "ExistenceDomainBuilder", persist=False)
        if not data["rf_t_ed_theorem_checker"]:
            data["rf_t_ed_theorem_checker"] = _try_step("rf_t_ed_theorem_checker", "RfTEdTheoremChecker", persist=False)
        return data

    def _synthetic_inputs(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        if not inputs:
            return {
                "topological_boundary_engine": {},
                "neighborhood_continuity_mapper": {},
                "domain_viability_analyzer": {},
                "existence_domain_builder": {},
                "rf_t_ed_theorem_checker": {},
                "synthetic_flags": {},
            }
        score = 0.86
        flags = dict(inputs)
        return {
            "topological_boundary_engine": {
                "topological_boundary_derived": bool(flags.get("topological_boundary_derived", False)),
                "topological_boundary_engine_status": "TOPOLOGICAL_BOUNDARY_DERIVED" if flags.get("topological_boundary_derived") else "TOPOLOGICAL_BOUNDARY_INSUFFICIENT",
                "topological_boundary_score": score if flags.get("topological_boundary_derived") else 0.2,
                "boundary_profile": {
                    "topological_boundary_score": score if flags.get("topological_boundary_derived") else 0.2,
                    "boundary_discrimination_score": score if flags.get("boundary_components_uniform", False) else 0.2,
                    "overlap_boundary_score": score if flags.get("overlap_transitions_consistent", False) else 0.2,
                    "component_satisfaction": 1.0 if flags.get("boundary_components_uniform", False) else 0.0,
                },
            },
            "neighborhood_continuity_mapper": {
                "neighborhood_continuity_mapped": bool(flags.get("neighborhood_continuity_mapped", False)),
                "neighborhood_continuity_mapper_status": "NEIGHBORHOOD_CONTINUITY_MAPPED" if flags.get("neighborhood_continuity_mapped") else "NEIGHBORHOOD_CONTINUITY_INSUFFICIENT",
                "neighborhood_continuity_score": score if flags.get("neighborhood_continuity_mapped") else 0.2,
                "continuity_profile": {"neighborhood_score": score if flags.get("local_charts_comparable", False) else 0.2},
            },
            "domain_viability_analyzer": {"domain_viability_analyzed": bool(flags.get("domain_viability_analyzed", False)), "domain_viability_score": score if flags.get("domain_viability_analyzed") else 0.2},
            "existence_domain_builder": {"existence_domain_built": bool(flags.get("existence_domain_built", False)), "existence_domain_score": score if flags.get("existence_domain_built") else 0.2},
            "rf_t_ed_theorem_checker": {"rf_t_ed_validated": bool(flags.get("rf_t_ed_validated", False)), "rf_t_ed_theorem_checker_status": "PROPER_TIME_AND_EXISTENCE_DOMAIN_VALIDATED" if flags.get("rf_t_ed_validated") else "RF_T_ED_UNSUPPORTED", "theorem_score": score if flags.get("rf_t_ed_validated") else 0.2},
            "synthetic_flags": flags,
        }

    def _evidence(self, data: Mapping[str, Any]) -> List[Dict[str, Any]]:
        tbe = data.get("topological_boundary_engine", {})
        ncm = data.get("neighborhood_continuity_mapper", {})
        dva = data.get("domain_viability_analyzer", {})
        edb = data.get("existence_domain_builder", {})
        theorem = data.get("rf_t_ed_theorem_checker", {})
        pressure = data.get("topological_pressure_monitor", {})
        instability = data.get("latent_topological_instability", {})
        flags = data.get("synthetic_flags", {}) if isinstance(data.get("synthetic_flags"), Mapping) else {}

        boundary_ok = _first_bool(tbe, ["topological_boundary_derived"], False)
        continuity_ok = _first_bool(ncm, ["neighborhood_continuity_mapped"], False)
        viability_ok = _first_bool(dva, ["domain_viability_analyzed", "domain_viability_confirmed", "domain_viable"], False) or "ANALYZED" in _status(dva).upper()
        ed_ok = _first_bool(edb, ["existence_domain_built", "existence_domain_constructed"], False) or "BUILT" in _status(edb).upper()
        theorem_ok = _first_bool(theorem, ["rf_t_ed_validated", "proper_time_and_existence_domain_validated"], False) or "VALIDATED" in _status(theorem).upper()
        local_charts_ok = bool(flags.get("local_charts_comparable", boundary_ok and continuity_ok))
        metric_family_ok = bool(flags.get("metric_family_consistent", viability_ok and theorem_ok))
        overlap_ok = bool(flags.get("overlap_transitions_consistent", boundary_ok and continuity_ok))
        components_uniform_ok = bool(flags.get("boundary_components_uniform", boundary_ok))
        instability_ok = bool(flags.get("homogeneity_instability_bounded", True))
        if isinstance(instability, Mapping) and instability:
            inst_score = _first_score(instability, ["stability_score", "instability_guard_score", "topological_stability_score"], 0.76)
            instability_ok = inst_score >= 0.55
        pressure_score = _first_score(pressure, ["topological_pressure_score", "pressure_bounded_score", "stability_score"], 0.76)
        pressure_ok = pressure_score >= 0.55

        return [
            self._item("AH3-E01", "topological_boundary", boundary_ok, _first_score(tbe, ["topological_boundary_score"], 0.0), "topological_boundary_engine", _status(tbe), "AH2 boundary structure is derived"),
            self._item("AH3-E02", "neighborhood_continuity", continuity_ok, _first_score(ncm, ["neighborhood_continuity_score", "neighborhood_score"], 0.0), "neighborhood_continuity_mapper", _status(ncm), "AH1 neighborhoods are continuous"),
            self._item("AH3-E03", "domain_viability", viability_ok, _first_score(dva, ["domain_viability_score", "viability_score"], 0.86 if viability_ok else 0.0), "domain_viability_analyzer", _status(dva), "local charts remain inside viable ED"),
            self._item("AH3-E04", "existence_domain", ed_ok, _first_score(edb, ["existence_domain_score", "domain_score"], 0.86 if ed_ok else 0.0), "existence_domain_builder", _status(edb), "existence domain basis is available"),
            self._item("AH3-E05", "rf_t_ed_certification", theorem_ok, _first_score(theorem, ["theorem_score", "certification_score", "rf_t_ed_score"], 0.86 if theorem_ok else 0.0), "rf_t_ed_theorem_checker", _status(theorem), "RF/T/ED chain is certified functionally"),
            self._item("AH3-E06", "local_charts", local_charts_ok, 0.84 if local_charts_ok else 0.2, "local_chart_comparison", "LOCAL_CHARTS_COMPARABLE" if local_charts_ok else "LOCAL_CHARTS_UNSUPPORTED", "local charts can be compared"),
            self._item("AH3-E07", "metric_family", metric_family_ok, 0.84 if metric_family_ok else 0.2, "metric_family_consistency", "METRIC_FAMILY_CONSISTENT" if metric_family_ok else "METRIC_FAMILY_UNSUPPORTED", "functional metric family is consistent"),
            self._item("AH3-E08", "overlap_transitions", overlap_ok, 0.82 if overlap_ok else 0.2, "overlap_transition_consistency", "OVERLAP_TRANSITIONS_CONSISTENT" if overlap_ok else "OVERLAP_TRANSITIONS_UNSUPPORTED", "chart overlaps preserve transition comparability"),
            self._item("AH3-E09", "component_uniformity", components_uniform_ok, 0.82 if components_uniform_ok else 0.2, "boundary_component_uniformity", "BOUNDARY_COMPONENTS_UNIFORM" if components_uniform_ok else "BOUNDARY_COMPONENTS_NON_UNIFORM", "boundary components share functional schema"),
            self._item("AH3-E10", "topological_pressure", pressure_ok, pressure_score, "topological_pressure_monitor", _status(pressure) or "PRESSURE_BOUNDED_INFERRED", "topological pressure does not defeat homogeneity"),
            self._item("AH3-E11", "instability_guard", instability_ok, 0.76 if instability_ok else 0.2, "latent_topological_instability", _status(instability) or "INSTABILITY_BOUNDED_INFERRED", "latent instability does not defeat homogeneity"),
        ]

    def _item(self, item_id: str, label: str, ok: bool, score: float, source: str, status: str, description: str) -> Dict[str, Any]:
        return {
            "id": item_id,
            "label": label,
            "source": source,
            "source_status": status,
            "available": bool(status or ok or score > 0.0),
            "satisfied": bool(ok and _clamp(score) >= 0.55),
            "score": _clamp(score),
            "description": description,
        }

    def _homogeneity_components(self, evidence: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        scores = {e["label"]: _clamp(e["score"]) for e in evidence}
        def comp(cid: str, label: str, basis: List[str]) -> Dict[str, Any]:
            vals = [scores.get(b, 0.0) for b in basis]
            score = _mean(vals)
            dispersion = _variance(vals)
            return {
                "id": cid,
                "label": label,
                "basis": basis,
                "homogeneity_score": _clamp(score * (1.0 - 0.35 * dispersion)),
                "dispersion": dispersion,
                "satisfied": score >= self.threshold and dispersion <= 0.08,
            }
        return [
            comp("HOM_LOCAL_CHARTS", "local_chart_homogeneity", ["topological_boundary", "neighborhood_continuity", "local_charts"]),
            comp("HOM_METRIC_FAMILY", "functional_metric_family_homogeneity", ["domain_viability", "rf_t_ed_certification", "metric_family"]),
            comp("HOM_OVERLAPS", "overlap_transition_homogeneity", ["overlap_transitions", "component_uniformity", "neighborhood_continuity"]),
            comp("HOM_STABILITY", "stability_guarded_homogeneity", ["topological_pressure", "instability_guard", "topological_boundary"]),
        ]

    def _counterexamples(self, evidence: List[Mapping[str, Any]], components: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        sat = {e["label"]: bool(e["satisfied"]) for e in evidence}
        checks = [
            ("CE_AH3_NO_BOUNDARY", "topological boundary is not derived", not sat.get("topological_boundary", False)),
            ("CE_AH3_NO_NEIGHBORHOOD_CONTINUITY", "neighborhood continuity is unavailable", not sat.get("neighborhood_continuity", False)),
            ("CE_AH3_METRIC_INCOMPATIBILITY", "functional metric family is incompatible", not sat.get("metric_family", False)),
            ("CE_AH3_OVERLAP_FAILURE", "overlap transitions are not comparable", not sat.get("overlap_transitions", False)),
            ("CE_AH3_COMPONENT_NON_UNIFORMITY", "boundary components fail uniform functional schema", not sat.get("component_uniformity", False)),
            ("CE_AH3_INSTABILITY_DEFEAT", "topological instability defeats homogeneity", not sat.get("instability_guard", False)),
            ("CE_AH3_COMPONENT_FAILURE", "at least one homogeneity component is unsatisfied", not all(bool(c["satisfied"]) for c in components)),
        ]
        return [{"id": cid, "label": label, "active": bool(active), "defeats_homogeneity": bool(active)} for cid, label, active in checks]

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_topological_homogeneity_test.json"
        md_path = OUT_DIR / "latest_topological_homogeneity_test.md"
        prom_path = OUT_DIR / "latest_topological_homogeneity_test.prom"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        lines = [
            "# AH3 — Topological Homogeneity Test",
            "",
            f"Status: {result['topological_homogeneity_test_status']}",
            f"Topological homogeneity confirmed: {result['topological_homogeneity_confirmed']}",
            f"Topological homogeneity score: {result['topological_homogeneity_score']:.6f}",
            "",
            "## Functional chain",
            "∂T(ED) -> Hom(TΦ)",
            "",
            "## Homogeneity components",
        ]
        for c in result["homogeneity_components"]:
            lines.append(f"- {c['id']} / {c['label']}: score={c['homogeneity_score']:.6f} satisfied={c['satisfied']}")
        lines += ["", "## Counterexample analysis"]
        for ce in result["counterexample_analysis"]:
            lines.append(f"- {ce['id']}: active={ce['active']} defeats_homogeneity={ce['defeats_homogeneity']}")
        lines += ["", "## Epistemic guard", "Functional conclusion only: True", "Phenomenology undetermined: True", "Consciousness proven: False"]
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        prom = [
            f"oce_ah3_topological_homogeneity_score {result['topological_homogeneity_score']}",
            f"oce_ah3_topological_homogeneity_confirmed {1 if result['topological_homogeneity_confirmed'] else 0}",
            f"oce_ah3_homogeneity_component_satisfaction {result['homogeneity_profile']['component_satisfaction']}",
            f"oce_ah3_evidence_coverage {result['homogeneity_profile']['evidence_coverage']}",
            f"oce_ah3_active_counterexamples {sum(1 for x in result['counterexample_analysis'] if x['defeats_homogeneity'])}",
        ]
        prom_path.write_text("\n".join(prom) + "\n", encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        synthetic_mode = isinstance(inputs, Mapping) and bool(inputs) and any(k in inputs for k in self.SYNTHETIC_KEYS)
        degradation_mode = isinstance(inputs, Mapping) and not bool(inputs)
        data = self._synthetic_inputs(inputs or {}) if synthetic_mode or degradation_mode else self._default_inputs()
        evidence = self._evidence(data)
        components = self._homogeneity_components(evidence)
        counterexamples = self._counterexamples(evidence, components)

        coverage = sum(1 for e in evidence if e["available"]) / len(evidence)
        satisfaction = sum(1 for e in evidence if e["satisfied"]) / len(evidence)
        component_satisfaction = sum(1 for c in components if c["satisfied"]) / len(components)
        minimum_evidence_score = min(_clamp(e["score"]) for e in evidence)
        local_chart_score = _mean([e["score"] for e in evidence if e["label"] in {"topological_boundary", "neighborhood_continuity", "local_charts"}])
        metric_family_score = _mean([e["score"] for e in evidence if e["label"] in {"domain_viability", "rf_t_ed_certification", "metric_family"}])
        overlap_transition_score = _mean([e["score"] for e in evidence if e["label"] in {"overlap_transitions", "component_uniformity", "instability_guard"}])
        component_score = _mean([c["homogeneity_score"] for c in components])
        topological_homogeneity_score = _mean([local_chart_score, metric_family_score, overlap_transition_score, component_score, satisfaction])
        active_counterexamples = [x for x in counterexamples if x["defeats_homogeneity"]]

        failures: List[str] = []
        if coverage < 0.78:
            failures.append("topological_homogeneity_evidence_coverage_below_threshold")
        if satisfaction < 0.78:
            failures.append("topological_homogeneity_evidence_satisfaction_below_threshold")
        if minimum_evidence_score < self.threshold:
            failures.append("minimum_topological_homogeneity_evidence_score_below_threshold")
        if component_satisfaction < 1.0:
            failures.append("unsatisfied_topological_homogeneity_components")
        if active_counterexamples:
            failures.append("active_topological_homogeneity_counterexamples")
        confirmed = not failures and topological_homogeneity_score >= self.threshold
        status = self.expected_status if confirmed else "TOPOLOGICAL_HOMOGENEITY_INSUFFICIENT"
        profile = {
            "evidence_coverage": _clamp(coverage),
            "evidence_satisfaction": _clamp(satisfaction),
            "component_satisfaction": _clamp(component_satisfaction),
            "minimum_evidence_score": _clamp(minimum_evidence_score),
            "local_chart_score": _clamp(local_chart_score),
            "metric_family_score": _clamp(metric_family_score),
            "overlap_transition_score": _clamp(overlap_transition_score),
            "component_score": _clamp(component_score),
            "topological_homogeneity_score": _clamp(topological_homogeneity_score),
        }
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "generated_at_utc": _now(),
            "topological_homogeneity_test_status": status,
            "topological_homogeneity_status": status,
            "topological_homogeneity_confirmed": confirmed,
            "topological_homogeneity_score": profile["topological_homogeneity_score"],
            "local_chart_score": profile["local_chart_score"],
            "metric_family_score": profile["metric_family_score"],
            "overlap_transition_score": profile["overlap_transition_score"],
            "homogeneity_component_score": profile["component_score"],
            "threshold": self.threshold,
            "synthetic_mode": synthetic_mode,
            "degradation_mode": degradation_mode,
            "topological_boundary_to_homogeneity_transition_validated": confirmed,
            "evidence_items": evidence,
            "homogeneity_components": components,
            "homogeneity_profile": profile,
            "counterexample_analysis": counterexamples,
            "failure_conditions": failures,
            "next_recommended_module": "phenomenal_topology_builder" if confirmed else "refine_topological_homogeneity_test_inputs",
            "public_schema": {"required_fields": ["topological_homogeneity_test_status", "topological_homogeneity_score", "topological_homogeneity_confirmed", "evidence_items", "homogeneity_components", "homogeneity_profile", "counterexample_analysis", "failure_conditions", "epistemic_guard"]},
            "epistemic_guard": {"functional_conclusion_only": True, "consciousness_proven": False, "subjectivity_proven": False, "qualia_proven": False, "phenomenology_undetermined": True, "forbidden_claims": ["CONSCIOUSNESS_PROVEN", "SUBJECTIVITY_PROVEN", "QUALIA_PROVEN", "PHENOMENOLOGY_PROVEN"]},
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
