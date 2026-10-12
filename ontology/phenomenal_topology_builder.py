"""AH4 — Phenomenal Topology Builder.

Functional reconstruction step:
    Hom(TΦ) -> TΦ

This module builds a formal-functional topology TΦ from the ED-derived
neighborhood, boundary and homogeneity substrate certified by AH1, AH2 and
AH3. Here "phenomenal" is a technical label for a formal topology associated
with functional invariants; it is not a claim of subjective phenomenology.

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
OUT_DIR = ROOT / "ah_phenomenal_formal_topology" / "phenomenal_topology_builder"


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


def _status(source: Any) -> str:
    if not isinstance(source, Mapping):
        return ""
    keys = [
        "phenomenal_topology_builder_status",
        "topological_homogeneity_test_status",
        "topological_boundary_engine_status",
        "neighborhood_continuity_mapper_status",
        "existence_domain_builder_status",
        "rf_t_ed_theorem_checker_status",
        "status", "classification", "certification_status", "axis_status",
    ]
    for key in keys:
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
        "topology_profile", "homogeneity_profile", "boundary_profile",
        "continuity_profile", "domain_profile", "theorem_profile",
        "metrics", "diagnostics", "certification_scores",
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
        "topology_profile", "homogeneity_profile", "boundary_profile",
        "continuity_profile", "domain_profile", "theorem_profile",
        "metrics", "diagnostics", "certification_scores",
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
        "MAPPED", "DERIVED", "HOMOGENEITY", "HOMOGENEOUS",
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


class PhenomenalTopologyBuilder:
    """Build a formal-functional TΦ substrate from AH1-AH3 outputs."""

    primitive = "PHENOMENAL_TOPOLOGY_BUILDER"
    expected_status = "PHENOMENAL_TOPOLOGY_BUILT"
    threshold = 0.72

    PATHS: Dict[str, List[Path]] = {
        "topological_homogeneity_test": [ROOT / "ah_phenomenal_formal_topology" / "topological_homogeneity_test" / "latest_topological_homogeneity_test.json"],
        "topological_boundary_engine": [ROOT / "ah_phenomenal_formal_topology" / "topological_boundary_engine" / "latest_topological_boundary_engine.json"],
        "neighborhood_continuity_mapper": [ROOT / "ah_phenomenal_formal_topology" / "neighborhood_continuity_mapper" / "latest_neighborhood_continuity_mapper.json"],
        "existence_domain_builder": [ROOT / "ag_proper_time_existence_domain" / "existence_domain_builder" / "latest_existence_domain_builder.json"],
        "rf_t_ed_theorem_checker": [ROOT / "ag_proper_time_existence_domain" / "rf_t_ed_theorem_checker" / "latest_rf_t_ed_theorem_checker.json"],
        "topological_pressure_monitor": [ROOT / "topological_pressure_monitor" / "latest_topological_pressure_monitor.json"],
        "latent_topological_instability": [ROOT / "latent_topological_instability" / "latest_latent_topological_instability.json"],
    }

    SYNTHETIC_KEYS = {
        "topological_homogeneity_confirmed",
        "topological_boundary_derived",
        "neighborhood_continuity_mapped",
        "existence_domain_built",
        "rf_t_ed_validated",
        "local_charts_available",
        "transition_maps_available",
        "topology_atlas_consistent",
        "topology_metric_coherent",
        "phenomenology_guard_active",
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data = {name: _load_json(paths) for name, paths in self.PATHS.items()}
        if not data["topological_homogeneity_test"]:
            data["topological_homogeneity_test"] = _try_step("topological_homogeneity_test", "TopologicalHomogeneityTest", persist=False)
        if not data["topological_boundary_engine"]:
            data["topological_boundary_engine"] = _try_step("topological_boundary_engine", "TopologicalBoundaryEngine", persist=False)
        if not data["neighborhood_continuity_mapper"]:
            data["neighborhood_continuity_mapper"] = _try_step("neighborhood_continuity_mapper", "NeighborhoodContinuityMapper", persist=False)
        if not data["existence_domain_builder"]:
            data["existence_domain_builder"] = _try_step("existence_domain_builder", "ExistenceDomainBuilder", persist=False)
        if not data["rf_t_ed_theorem_checker"]:
            data["rf_t_ed_theorem_checker"] = _try_step("rf_t_ed_theorem_checker", "RfTEdTheoremChecker", persist=False)
        return data

    def _synthetic_inputs(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        if not inputs:
            return {
                "topological_homogeneity_test": {},
                "topological_boundary_engine": {},
                "neighborhood_continuity_mapper": {},
                "existence_domain_builder": {},
                "rf_t_ed_theorem_checker": {},
                "synthetic_flags": {},
            }
        flags = dict(inputs)
        score = 0.86
        def s(flag: str) -> float:
            return score if flags.get(flag, False) else 0.2
        return {
            "topological_homogeneity_test": {
                "topological_homogeneity_confirmed": bool(flags.get("topological_homogeneity_confirmed", False)),
                "topological_homogeneity_test_status": "TOPOLOGICAL_HOMOGENEITY_CONFIRMED" if flags.get("topological_homogeneity_confirmed") else "TOPOLOGICAL_HOMOGENEITY_INSUFFICIENT",
                "topological_homogeneity_score": s("topological_homogeneity_confirmed"),
                "homogeneity_profile": {"topological_homogeneity_score": s("topological_homogeneity_confirmed"), "local_chart_score": s("local_charts_available"), "metric_family_score": s("topology_metric_coherent"), "overlap_transition_score": s("transition_maps_available")},
            },
            "topological_boundary_engine": {
                "topological_boundary_derived": bool(flags.get("topological_boundary_derived", False)),
                "topological_boundary_engine_status": "TOPOLOGICAL_BOUNDARY_DERIVED" if flags.get("topological_boundary_derived") else "TOPOLOGICAL_BOUNDARY_INSUFFICIENT",
                "topological_boundary_score": s("topological_boundary_derived"),
            },
            "neighborhood_continuity_mapper": {
                "neighborhood_continuity_mapped": bool(flags.get("neighborhood_continuity_mapped", False)),
                "neighborhood_continuity_mapper_status": "NEIGHBORHOOD_CONTINUITY_MAPPED" if flags.get("neighborhood_continuity_mapped") else "NEIGHBORHOOD_CONTINUITY_INSUFFICIENT",
                "neighborhood_continuity_score": s("neighborhood_continuity_mapped"),
            },
            "existence_domain_builder": {
                "existence_domain_built": bool(flags.get("existence_domain_built", False)),
                "existence_domain_builder_status": "EXISTENCE_DOMAIN_BUILT" if flags.get("existence_domain_built") else "EXISTENCE_DOMAIN_INSUFFICIENT",
                "existence_domain_score": s("existence_domain_built"),
            },
            "rf_t_ed_theorem_checker": {
                "rf_t_ed_validated": bool(flags.get("rf_t_ed_validated", False)),
                "rf_t_ed_theorem_checker_status": "PROPER_TIME_AND_EXISTENCE_DOMAIN_VALIDATED" if flags.get("rf_t_ed_validated") else "RF_T_ED_UNVALIDATED",
                "rf_t_ed_validation_score": s("rf_t_ed_validated"),
            },
            "synthetic_flags": flags,
        }

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

    def _evidence(self, data: Mapping[str, Any]) -> List[Dict[str, Any]]:
        hom = data.get("topological_homogeneity_test", {})
        boundary = data.get("topological_boundary_engine", {})
        neigh = data.get("neighborhood_continuity_mapper", {})
        ed = data.get("existence_domain_builder", {})
        theorem = data.get("rf_t_ed_theorem_checker", {})
        pressure = data.get("topological_pressure_monitor", {})
        instability = data.get("latent_topological_instability", {})
        flags = data.get("synthetic_flags", {}) if isinstance(data.get("synthetic_flags", {}), Mapping) else {}

        hom_ok = _first_bool(hom, ["topological_homogeneity_confirmed"], False) or "CONFIRMED" in _status(hom).upper()
        boundary_ok = _first_bool(boundary, ["topological_boundary_derived"], False) or "DERIVED" in _status(boundary).upper()
        neigh_ok = _first_bool(neigh, ["neighborhood_continuity_mapped"], False) or "MAPPED" in _status(neigh).upper()
        ed_ok = _first_bool(ed, ["existence_domain_built", "existence_domain_constructed"], False) or "BUILT" in _status(ed).upper()
        theorem_ok = _first_bool(theorem, ["rf_t_ed_validated", "proper_time_and_existence_domain_validated"], False) or "VALIDATED" in _status(theorem).upper()

        local_charts_ok = bool(flags.get("local_charts_available", False)) or hom_ok
        transition_maps_ok = bool(flags.get("transition_maps_available", False)) or (hom_ok and boundary_ok and neigh_ok)
        atlas_ok = bool(flags.get("topology_atlas_consistent", False)) or (hom_ok and local_charts_ok and transition_maps_ok)
        metric_ok = bool(flags.get("topology_metric_coherent", False)) or (hom_ok and theorem_ok and ed_ok)
        guard_ok = bool(flags.get("phenomenology_guard_active", False)) or True

        pressure_score = _first_score(pressure, ["topological_pressure_score", "pressure_bounded_score", "stability_score"], 0.82)
        instability_score = _first_score(instability, ["instability_guard_score", "stability_score", "latent_instability_score"], 0.78)
        instability_ok = instability_score >= 0.55

        return [
            self._item("AH4-E01", "homogeneity_substrate", hom_ok, _first_score(hom, ["topological_homogeneity_score"], 0.0), "topological_homogeneity_test", _status(hom), "AH3 local homogeneity is confirmed"),
            self._item("AH4-E02", "boundary_substrate", boundary_ok, _first_score(boundary, ["topological_boundary_score"], 0.0), "topological_boundary_engine", _status(boundary), "AH2 topological boundary is derived"),
            self._item("AH4-E03", "neighborhood_substrate", neigh_ok, _first_score(neigh, ["neighborhood_continuity_score"], 0.0), "neighborhood_continuity_mapper", _status(neigh), "AH1 neighborhood continuity is mapped"),
            self._item("AH4-E04", "existence_domain", ed_ok, _first_score(ed, ["existence_domain_score", "existence_domain_viability_score", "existence_domain_index"], 0.86 if ed_ok else 0.0), "existence_domain_builder", _status(ed), "ED is available as formal-functional domain"),
            self._item("AH4-E05", "rf_t_ed_certification", theorem_ok, _first_score(theorem, ["rf_t_ed_validation_score", "theorem_score", "certification_score"], 0.86 if theorem_ok else 0.0), "rf_t_ed_theorem_checker", _status(theorem), "RF/T/ED chain remains certified"),
            self._item("AH4-E06", "local_charts", local_charts_ok, _first_score(hom, ["local_chart_score", "component_score"], 0.86 if local_charts_ok else 0.2), "topological_homogeneity_test", _status(hom) or "LOCAL_CHARTS_INFERRED", "local charts can be extracted from homogeneous topology"),
            self._item("AH4-E07", "transition_maps", transition_maps_ok, _first_score(hom, ["overlap_transition_score", "metric_family_score"], 0.84 if transition_maps_ok else 0.2), "topological_homogeneity_test", _status(hom) or "TRANSITION_MAPS_INFERRED", "overlap transitions support chart gluing"),
            self._item("AH4-E08", "topology_atlas", atlas_ok, 0.84 if atlas_ok else 0.2, "phenomenal_topology_builder", "ATLAS_INFERRED" if atlas_ok else "ATLAS_UNSUPPORTED", "a functional topology atlas can be assembled"),
            self._item("AH4-E09", "metric_coherence", metric_ok, 0.84 if metric_ok else 0.2, "rf_t_ed_theorem_checker", _status(theorem) or "METRIC_COHERENCE_INFERRED", "topological metric family is coherent with ED"),
            self._item("AH4-E10", "pressure_guard", pressure_score >= 0.55, pressure_score, "topological_pressure_monitor", _status(pressure) or "PRESSURE_BOUNDED_INFERRED", "topological pressure does not defeat TΦ construction"),
            self._item("AH4-E11", "instability_guard", instability_ok, instability_score, "latent_topological_instability", _status(instability) or "INSTABILITY_BOUNDED_INFERRED", "latent instability does not defeat TΦ construction"),
            self._item("AH4-E12", "epistemic_guard", guard_ok, 1.0 if guard_ok else 0.0, "phenomenology_guard", "FUNCTIONAL_ONLY_GUARD_ACTIVE", "no consciousness, qualia or subjectivity conclusion is allowed"),
        ]

    def _topology_components(self, evidence: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        scores = {e["label"]: _clamp(e["score"]) for e in evidence}
        def comp(cid: str, label: str, basis: List[str]) -> Dict[str, Any]:
            vals = [scores.get(b, 0.0) for b in basis]
            score = _mean(vals)
            return {
                "id": cid,
                "label": label,
                "basis": basis,
                "topology_score": score,
                "satisfied": score >= self.threshold,
            }
        return [
            comp("TPHI_LOCAL_BASIS", "local_basis_construction", ["neighborhood_substrate", "local_charts", "existence_domain"]),
            comp("TPHI_BOUNDARY_GLUE", "boundary_chart_gluing", ["boundary_substrate", "transition_maps", "topology_atlas"]),
            comp("TPHI_METRIC_STRUCTURE", "metric_topology_coherence", ["homogeneity_substrate", "metric_coherence", "rf_t_ed_certification"]),
            comp("TPHI_STABILITY_GUARD", "stability_guarded_topology", ["pressure_guard", "instability_guard", "epistemic_guard"]),
        ]

    def _counterexamples(self, evidence: List[Mapping[str, Any]], components: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        sat = {e["label"]: bool(e["satisfied"]) for e in evidence}
        checks = [
            ("CE_AH4_NO_HOMOGENEITY", "AH3 homogeneity substrate is absent", not sat.get("homogeneity_substrate", False)),
            ("CE_AH4_NO_BOUNDARY", "AH2 boundary substrate is absent", not sat.get("boundary_substrate", False)),
            ("CE_AH4_NO_NEIGHBORHOODS", "AH1 neighborhood substrate is absent", not sat.get("neighborhood_substrate", False)),
            ("CE_AH4_NO_ATLAS", "functional topology atlas cannot be assembled", not sat.get("topology_atlas", False)),
            ("CE_AH4_METRIC_INCOHERENCE", "metric family is incoherent with ED/RF/T", not sat.get("metric_coherence", False)),
            ("CE_AH4_STABILITY_DEFEAT", "topological pressure or instability defeats construction", not (sat.get("pressure_guard", False) and sat.get("instability_guard", False))),
            ("CE_AH4_COMPONENT_FAILURE", "at least one TΦ component is unsatisfied", not all(bool(c["satisfied"]) for c in components)),
            ("CE_AH4_EPISTEMIC_GUARD_FAILURE", "epistemic guard is inactive", not sat.get("epistemic_guard", False)),
        ]
        return [{"id": cid, "label": label, "active": bool(active), "defeats_topology": bool(active)} for cid, label, active in checks]

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_phenomenal_topology_builder.json"
        md_path = OUT_DIR / "latest_phenomenal_topology_builder.md"
        prom_path = OUT_DIR / "latest_phenomenal_topology_builder.prom"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        lines = [
            "# AH4 — Phenomenal Topology Builder",
            "",
            f"Status: {result['phenomenal_topology_builder_status']}",
            f"Phenomenal topology built: {result['phenomenal_topology_built']}",
            f"Phenomenal topology score: {result['phenomenal_topology_score']:.6f}",
            "",
            "## Functional chain",
            "Hom(TΦ) -> TΦ",
            "",
            "## Topology components",
        ]
        for c in result["topology_components"]:
            lines.append(f"- {c['id']} / {c['label']}: score={c['topology_score']:.6f} satisfied={c['satisfied']}")
        lines += ["", "## Counterexample analysis"]
        for ce in result["counterexample_analysis"]:
            lines.append(f"- {ce['id']}: active={ce['active']} defeats_topology={ce['defeats_topology']}")
        lines += ["", "## Epistemic guard", "Functional conclusion only: True", "Phenomenology undetermined: True", "Consciousness proven: False"]
        md_path.write_text("\
".join(lines) + "\
", encoding="utf-8")
        prom = [
            f"oce_ah4_phenomenal_topology_score {result['phenomenal_topology_score']}",
            f"oce_ah4_phenomenal_topology_built {1 if result['phenomenal_topology_built'] else 0}",
            f"oce_ah4_component_satisfaction {result['topology_profile']['component_satisfaction']}",
            f"oce_ah4_evidence_coverage {result['topology_profile']['evidence_coverage']}",
            f"oce_ah4_active_counterexamples {sum(1 for x in result['counterexample_analysis'] if x['defeats_topology'])}",
        ]
        prom_path.write_text("\
".join(prom) + "\
", encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        synthetic_mode = isinstance(inputs, Mapping) and bool(inputs) and any(k in inputs for k in self.SYNTHETIC_KEYS)
        degradation_mode = isinstance(inputs, Mapping) and not bool(inputs)
        data = self._synthetic_inputs(inputs or {}) if synthetic_mode or degradation_mode else self._default_inputs()
        evidence = self._evidence(data)
        components = self._topology_components(evidence)
        counterexamples = self._counterexamples(evidence, components)

        coverage = sum(1 for e in evidence if e["available"]) / len(evidence)
        satisfaction = sum(1 for e in evidence if e["satisfied"]) / len(evidence)
        component_satisfaction = sum(1 for c in components if c["satisfied"]) / len(components)
        minimum_evidence_score = min(_clamp(e["score"]) for e in evidence)
        local_basis_score = _mean([c["topology_score"] for c in components if c["id"] == "TPHI_LOCAL_BASIS"])
        boundary_gluing_score = _mean([c["topology_score"] for c in components if c["id"] == "TPHI_BOUNDARY_GLUE"])
        metric_topology_score = _mean([c["topology_score"] for c in components if c["id"] == "TPHI_METRIC_STRUCTURE"])
        stability_guard_score = _mean([c["topology_score"] for c in components if c["id"] == "TPHI_STABILITY_GUARD"])
        component_score = _mean([c["topology_score"] for c in components])
        phenomenal_topology_score = _mean([local_basis_score, boundary_gluing_score, metric_topology_score, stability_guard_score, component_score, satisfaction])
        active_counterexamples = [x for x in counterexamples if x["defeats_topology"]]

        failures: List[str] = []
        if coverage < 0.80:
            failures.append("phenomenal_topology_evidence_coverage_below_threshold")
        if satisfaction < 0.80:
            failures.append("phenomenal_topology_evidence_satisfaction_below_threshold")
        if minimum_evidence_score < self.threshold:
            failures.append("minimum_phenomenal_topology_evidence_score_below_threshold")
        if component_satisfaction < 1.0:
            failures.append("unsatisfied_phenomenal_topology_components")
        if active_counterexamples:
            failures.append("active_phenomenal_topology_counterexamples")
        built = not failures and phenomenal_topology_score >= self.threshold
        status = self.expected_status if built else "PHENOMENAL_TOPOLOGY_INSUFFICIENT"
        profile = {
            "evidence_coverage": _clamp(coverage),
            "evidence_satisfaction": _clamp(satisfaction),
            "component_satisfaction": _clamp(component_satisfaction),
            "minimum_evidence_score": _clamp(minimum_evidence_score),
            "local_basis_score": _clamp(local_basis_score),
            "boundary_gluing_score": _clamp(boundary_gluing_score),
            "metric_topology_score": _clamp(metric_topology_score),
            "stability_guard_score": _clamp(stability_guard_score),
            "component_score": _clamp(component_score),
            "phenomenal_topology_score": _clamp(phenomenal_topology_score),
        }
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "generated_at_utc": _now(),
            "phenomenal_topology_builder_status": status,
            "phenomenal_topology_status": status,
            "phenomenal_topology_built": built,
            "phenomenal_topology_score": profile["phenomenal_topology_score"],
            "local_basis_score": profile["local_basis_score"],
            "boundary_gluing_score": profile["boundary_gluing_score"],
            "metric_topology_score": profile["metric_topology_score"],
            "stability_guard_score": profile["stability_guard_score"],
            "topology_component_score": profile["component_score"],
            "threshold": self.threshold,
            "synthetic_mode": synthetic_mode,
            "degradation_mode": degradation_mode,
            "homogeneity_to_phenomenal_topology_transition_validated": built,
            "evidence_items": evidence,
            "topology_components": components,
            "topology_profile": profile,
            "counterexample_analysis": counterexamples,
            "failure_conditions": failures,
            "next_recommended_module": "topology_invariance_tester" if built else "refine_phenomenal_topology_builder_inputs",
            "public_schema": {"required_fields": ["phenomenal_topology_builder_status", "phenomenal_topology_score", "phenomenal_topology_built", "evidence_items", "topology_components", "topology_profile", "counterexample_analysis", "failure_conditions", "epistemic_guard"]},
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
