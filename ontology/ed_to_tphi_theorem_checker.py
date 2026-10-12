"""AH6 — ED to TΦ Theorem Checker.

Functional reconstruction step:
    ED -> TΦ

This module certifies that the existence domain ED, already validated through
proper time and existence-domain construction, functionally supports the formal
TΦ topology produced and stress-tested by AH1→AH5.

The word "phenomenal" is used only as a formal-functional label inherited from
the project theory. This module never proves or asserts consciousness,
subjectivity, qualia, phenomenal experience or phenomenology. Its conclusion is
strictly functional and topological.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ah_phenomenal_formal_topology" / "ed_to_tphi_theorem_checker"


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


def _mean(values: List[Any], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    return _clamp(sum(vals) / len(vals), default) if vals else default


def _status(source: Any) -> str:
    if not isinstance(source, Mapping):
        return ""
    preferred = [
        "ed_to_tphi_theorem_checker_status",
        "topology_invariance_tester_status",
        "phenomenal_topology_builder_status",
        "topological_homogeneity_test_status",
        "topological_boundary_engine_status",
        "neighborhood_continuity_mapper_status",
        "rf_t_ed_theorem_checker_status",
        "existence_domain_builder_status",
        "domain_viability_analyzer_status",
        "domain_boundary_detector_status",
        "proper_time_extractor_status",
        "status",
        "classification",
        "certification_status",
        "axis_status",
    ]
    for key in preferred:
        if source.get(key) is not None:
            return str(source.get(key))
    for key, value in source.items():
        if isinstance(key, str) and key.endswith("_status") and value is not None:
            return str(value)
    diag = source.get("diagnostics")
    if isinstance(diag, Mapping) and diag.get("status") is not None:
        return str(diag.get("status"))
    return ""


def _truthy_status(source: Any, tokens: List[str]) -> bool:
    st = _status(source).upper()
    return any(t.upper() in st for t in tokens)


def _first_bool(source: Any, keys: List[str], default: bool = False) -> bool:
    if not isinstance(source, Mapping):
        return default
    for key in keys:
        if key in source:
            return bool(source.get(key))
    for nested_key in [
        "theorem_profile", "invariance_profile", "topology_profile",
        "homogeneity_profile", "boundary_profile", "continuity_profile",
        "domain_profile", "domain_viability_profile", "theorem_metrics",
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
        "theorem_profile", "invariance_profile", "topology_profile",
        "homogeneity_profile", "boundary_profile", "continuity_profile",
        "domain_profile", "domain_viability_profile", "theorem_metrics",
        "metrics", "diagnostics", "certification_scores",
    ]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return _clamp(nested.get(key), default)
    if _truthy_status(source, [
        "VALIDATED", "CERTIFIED", "CONFIRMED", "READY", "ESTABLISHED",
        "DETECTED", "BUILT", "CONSTRUCTED", "MONITORED", "ANALYZED",
        "EXTRACTED", "ACTIVE", "VIABLE", "ROBUST", "MAPPED", "DERIVED",
        "HOMOGENEITY", "INVARIANT",
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


class EdToTphiTheoremChecker:
    """Certify the functional derivation ED -> TΦ and close Axis AH."""

    primitive = "ED_TO_TPHI_THEOREM_CHECKER"
    theorem_id = "AH6_ED_TO_TPHI_THEOREM"
    expected_status = "PHENOMENAL_FORMAL_TOPOLOGY_CERTIFIED"
    insufficient_status = "ED_TO_TPHI_THEOREM_INSUFFICIENT"
    threshold = 0.72

    PATHS: Dict[str, List[Path]] = {
        "rf_t_ed_theorem_checker": [ROOT / "ag_proper_time_existence_domain" / "rf_t_ed_theorem_checker" / "latest_rf_t_ed_theorem_checker.json"],
        "existence_domain_builder": [ROOT / "ag_proper_time_existence_domain" / "existence_domain_builder" / "latest_existence_domain_builder.json"],
        "domain_boundary_detector": [ROOT / "ag_proper_time_existence_domain" / "domain_boundary_detector" / "latest_domain_boundary_detector.json"],
        "domain_viability_analyzer": [ROOT / "ag_proper_time_existence_domain" / "domain_viability_analyzer" / "latest_domain_viability_analyzer.json"],
        "neighborhood_continuity_mapper": [ROOT / "ah_phenomenal_formal_topology" / "neighborhood_continuity_mapper" / "latest_neighborhood_continuity_mapper.json"],
        "topological_boundary_engine": [ROOT / "ah_phenomenal_formal_topology" / "topological_boundary_engine" / "latest_topological_boundary_engine.json"],
        "topological_homogeneity_test": [ROOT / "ah_phenomenal_formal_topology" / "topological_homogeneity_test" / "latest_topological_homogeneity_test.json"],
        "phenomenal_topology_builder": [ROOT / "ah_phenomenal_formal_topology" / "phenomenal_topology_builder" / "latest_phenomenal_topology_builder.json"],
        "topology_invariance_tester": [ROOT / "ah_phenomenal_formal_topology" / "topology_invariance_tester" / "latest_topology_invariance_tester.json"],
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data = {name: _load_json(paths) for name, paths in self.PATHS.items()}
        fallbacks = {
            "rf_t_ed_theorem_checker": ("rf_t_ed_theorem_checker", "RfTEdTheoremChecker"),
            "existence_domain_builder": ("existence_domain_builder", "ExistenceDomainBuilder"),
            "domain_boundary_detector": ("domain_boundary_detector", "DomainBoundaryDetector"),
            "domain_viability_analyzer": ("domain_viability_analyzer", "DomainViabilityAnalyzer"),
            "neighborhood_continuity_mapper": ("neighborhood_continuity_mapper", "NeighborhoodContinuityMapper"),
            "topological_boundary_engine": ("topological_boundary_engine", "TopologicalBoundaryEngine"),
            "topological_homogeneity_test": ("topological_homogeneity_test", "TopologicalHomogeneityTest"),
            "phenomenal_topology_builder": ("phenomenal_topology_builder", "PhenomenalTopologyBuilder"),
            "topology_invariance_tester": ("topology_invariance_tester", "TopologyInvarianceTester"),
        }
        for key, (mod, cls) in fallbacks.items():
            if not data.get(key):
                data[key] = _try_step(mod, cls, persist=False)
        return data

    def _synthetic_inputs(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        flags = dict(inputs or {})

        def yes(key: str) -> bool:
            return bool(flags.get(key, False))

        def score(key: str) -> float:
            return 0.88 if yes(key) else 0.20

        return {
            "rf_t_ed_theorem_checker": {
                "rf_t_ed_theorem_checker_status": "PROPER_TIME_AND_EXISTENCE_DOMAIN_VALIDATED" if yes("rf_t_ed_validated") else "RF_T_ED_THEOREM_INSUFFICIENT",
                "rf_t_ed_validated": yes("rf_t_ed_validated"),
                "proper_time_and_existence_domain_validated": yes("rf_t_ed_validated"),
                "theorem_validity_score": score("rf_t_ed_validated"),
            },
            "existence_domain_builder": {
                "existence_domain_builder_status": "EXISTENCE_DOMAIN_BUILT" if yes("existence_domain_built") else "EXISTENCE_DOMAIN_INSUFFICIENT",
                "existence_domain_built": yes("existence_domain_built"),
                "existence_domain_score": score("existence_domain_built"),
            },
            "domain_boundary_detector": {
                "domain_boundary_detector_status": "DOMAIN_BOUNDARIES_DETECTED" if yes("domain_boundaries_detected") else "DOMAIN_BOUNDARIES_INSUFFICIENT",
                "domain_boundaries_detected": yes("domain_boundaries_detected"),
                "domain_boundary_score": score("domain_boundaries_detected"),
            },
            "domain_viability_analyzer": {
                "domain_viability_analyzer_status": "DOMAIN_VIABILITY_ANALYZED" if yes("domain_viability_analyzed") else "DOMAIN_VIABILITY_INSUFFICIENT",
                "domain_viability_analyzed": yes("domain_viability_analyzed"),
                "domain_viability_score": score("domain_viability_analyzed"),
            },
            "neighborhood_continuity_mapper": {
                "neighborhood_continuity_mapper_status": "NEIGHBORHOOD_CONTINUITY_MAPPED" if yes("neighborhood_continuity_mapped") else "NEIGHBORHOOD_CONTINUITY_INSUFFICIENT",
                "neighborhood_continuity_mapped": yes("neighborhood_continuity_mapped"),
                "neighborhood_continuity_score": score("neighborhood_continuity_mapped"),
            },
            "topological_boundary_engine": {
                "topological_boundary_engine_status": "TOPOLOGICAL_BOUNDARY_DERIVED" if yes("topological_boundary_derived") else "TOPOLOGICAL_BOUNDARY_INSUFFICIENT",
                "topological_boundary_derived": yes("topological_boundary_derived"),
                "topological_boundary_score": score("topological_boundary_derived"),
            },
            "topological_homogeneity_test": {
                "topological_homogeneity_test_status": "TOPOLOGICAL_HOMOGENEITY_CONFIRMED" if yes("topological_homogeneity_confirmed") else "TOPOLOGICAL_HOMOGENEITY_INSUFFICIENT",
                "topological_homogeneity_confirmed": yes("topological_homogeneity_confirmed"),
                "topological_homogeneity_score": score("topological_homogeneity_confirmed"),
            },
            "phenomenal_topology_builder": {
                "phenomenal_topology_builder_status": "PHENOMENAL_TOPOLOGY_BUILT" if yes("phenomenal_topology_built") else "PHENOMENAL_TOPOLOGY_INSUFFICIENT",
                "phenomenal_topology_built": yes("phenomenal_topology_built"),
                "phenomenal_topology_score": score("phenomenal_topology_built"),
            },
            "topology_invariance_tester": {
                "topology_invariance_tester_status": "TOPOLOGY_INVARIANCE_CONFIRMED" if yes("topology_invariance_confirmed") else "TOPOLOGY_INVARIANCE_INSUFFICIENT",
                "topology_invariance_confirmed": yes("topology_invariance_confirmed"),
                "topology_invariance_score": score("topology_invariance_confirmed"),
                "invariance_profile": {
                    "chart_relabeling_invariance_score": 0.86 if yes("chart_relabeling_invariant") else 0.20,
                    "metric_rescaling_invariance_score": 0.84 if yes("metric_rescaling_invariant") else 0.20,
                    "boundary_deformation_invariance_score": 0.83 if yes("boundary_deformation_invariant") else 0.20,
                    "temporal_reparameterization_invariance_score": 0.82 if yes("temporal_reparameterization_invariant") else 0.20,
                    "perturbation_stability_invariance_score": 0.80 if yes("perturbation_stability_bounded") else 0.20,
                },
            },
        }

    def _evidence(self, data: Mapping[str, Any]) -> List[Dict[str, Any]]:
        rfed = data.get("rf_t_ed_theorem_checker", {})
        ed = data.get("existence_domain_builder", {})
        db = data.get("domain_boundary_detector", {})
        dv = data.get("domain_viability_analyzer", {})
        ncm = data.get("neighborhood_continuity_mapper", {})
        boundary = data.get("topological_boundary_engine", {})
        hom = data.get("topological_homogeneity_test", {})
        tphi = data.get("phenomenal_topology_builder", {})
        inv = data.get("topology_invariance_tester", {})

        items = [
            {
                "id": "AH6-E01", "label": "rf_t_ed_chain_validated", "source": "rf_t_ed_theorem_checker",
                "description": "RF→T→ED theorem chain is certified before deriving TΦ",
                "source_status": _status(rfed), "available": bool(rfed),
                "satisfied": _first_bool(rfed, ["rf_t_ed_validated", "proper_time_and_existence_domain_validated"], _truthy_status(rfed, ["PROPER_TIME_AND_EXISTENCE_DOMAIN_VALIDATED"])),
                "score": _first_score(rfed, ["theorem_validity_score", "rf_t_ed_score", "validation_score"], 0.0),
            },
            {
                "id": "AH6-E02", "label": "existence_domain_available", "source": "existence_domain_builder",
                "description": "ED is built and available as the derivational substrate",
                "source_status": _status(ed), "available": bool(ed),
                "satisfied": _first_bool(ed, ["existence_domain_built", "domain_built"], _truthy_status(ed, ["EXISTENCE_DOMAIN_BUILT"])),
                "score": _first_score(ed, ["existence_domain_score", "domain_score"], 0.0),
            },
            {
                "id": "AH6-E03", "label": "domain_boundaries_available", "source": "domain_boundary_detector",
                "description": "ED boundaries are available for topological separation and gluing tests",
                "source_status": _status(db), "available": bool(db),
                "satisfied": _first_bool(db, ["domain_boundaries_detected"], _truthy_status(db, ["DOMAIN_BOUNDARIES_DETECTED"])),
                "score": _first_score(db, ["domain_boundary_score", "boundary_score"], 0.0),
            },
            {
                "id": "AH6-E04", "label": "domain_viability_available", "source": "domain_viability_analyzer",
                "description": "ED viability is sufficient to support a stable topology",
                "source_status": _status(dv), "available": bool(dv),
                "satisfied": _first_bool(dv, ["domain_viability_analyzed", "domain_viable"], _truthy_status(dv, ["DOMAIN_VIABILITY_ANALYZED"])),
                "score": _first_score(dv, ["domain_viability_score", "viability_score"], 0.0),
            },
            {
                "id": "AH6-E05", "label": "neighborhood_continuity_mapped", "source": "neighborhood_continuity_mapper",
                "description": "ED admits stable neighborhoods required for a formal topology",
                "source_status": _status(ncm), "available": bool(ncm),
                "satisfied": _first_bool(ncm, ["neighborhood_continuity_mapped"], _truthy_status(ncm, ["NEIGHBORHOOD_CONTINUITY_MAPPED"])),
                "score": _first_score(ncm, ["neighborhood_continuity_score", "continuity_score", "local_overlap_score"], 0.0),
            },
            {
                "id": "AH6-E06", "label": "topological_boundary_derived", "source": "topological_boundary_engine",
                "description": "topological boundaries are derived from ED structure",
                "source_status": _status(boundary), "available": bool(boundary),
                "satisfied": _first_bool(boundary, ["topological_boundary_derived"], _truthy_status(boundary, ["TOPOLOGICAL_BOUNDARY_DERIVED"])),
                "score": _first_score(boundary, ["topological_boundary_score", "boundary_viability_score", "overlap_boundary_score"], 0.0),
            },
            {
                "id": "AH6-E07", "label": "topological_homogeneity_confirmed", "source": "topological_homogeneity_test",
                "description": "local topological charts are homogeneous enough to support TΦ",
                "source_status": _status(hom), "available": bool(hom),
                "satisfied": _first_bool(hom, ["topological_homogeneity_confirmed"], _truthy_status(hom, ["TOPOLOGICAL_HOMOGENEITY_CONFIRMED"])),
                "score": _first_score(hom, ["topological_homogeneity_score", "local_chart_score", "component_score"], 0.0),
            },
            {
                "id": "AH6-E08", "label": "formal_tphi_built", "source": "phenomenal_topology_builder",
                "description": "formal-functional TΦ has been constructed from the AH chain",
                "source_status": _status(tphi), "available": bool(tphi),
                "satisfied": _first_bool(tphi, ["phenomenal_topology_built"], _truthy_status(tphi, ["PHENOMENAL_TOPOLOGY_BUILT"])),
                "score": _first_score(tphi, ["phenomenal_topology_score", "tphi_score", "topology_score"], 0.0),
            },
            {
                "id": "AH6-E09", "label": "topology_invariance_confirmed", "source": "topology_invariance_tester",
                "description": "TΦ remains invariant under controlled admissible transformations",
                "source_status": _status(inv), "available": bool(inv),
                "satisfied": _first_bool(inv, ["topology_invariance_confirmed"], _truthy_status(inv, ["TOPOLOGY_INVARIANCE_CONFIRMED"])),
                "score": _first_score(inv, ["topology_invariance_score"], 0.0),
            },
        ]
        for item in items:
            item["score"] = _clamp(item.get("score"))
            item["satisfied"] = bool(item.get("satisfied") and item["score"] >= 0.60)
        return items

    def _derivation_chain(self, evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_label = {e["label"]: e for e in evidence}

        def sc(label: str) -> float:
            return _clamp(by_label.get(label, {}).get("score", 0.0))

        def ok(*labels: str) -> bool:
            return all(bool(by_label.get(label, {}).get("satisfied", False)) for label in labels)

        chain = [
            {
                "id": "AH6-L01", "transition": "RF_T_ED -> ED",
                "basis": ["rf_t_ed_chain_validated", "existence_domain_available"],
                "score": _mean([sc("rf_t_ed_chain_validated"), sc("existence_domain_available")]),
            },
            {
                "id": "AH6-L02", "transition": "ED -> local_neighborhoods",
                "basis": ["existence_domain_available", "neighborhood_continuity_mapped"],
                "score": _mean([sc("existence_domain_available"), sc("neighborhood_continuity_mapped")]),
            },
            {
                "id": "AH6-L03", "transition": "ED_boundaries -> topological_boundaries",
                "basis": ["domain_boundaries_available", "topological_boundary_derived"],
                "score": _mean([sc("domain_boundaries_available"), sc("topological_boundary_derived")]),
            },
            {
                "id": "AH6-L04", "transition": "local_neighborhoods + boundaries -> homogeneous_topological_charts",
                "basis": ["neighborhood_continuity_mapped", "topological_boundary_derived", "topological_homogeneity_confirmed"],
                "score": _mean([sc("neighborhood_continuity_mapped"), sc("topological_boundary_derived"), sc("topological_homogeneity_confirmed")]),
            },
            {
                "id": "AH6-L05", "transition": "homogeneous_ED_topology -> TΦ",
                "basis": ["domain_viability_available", "topological_homogeneity_confirmed", "formal_tphi_built"],
                "score": _mean([sc("domain_viability_available"), sc("topological_homogeneity_confirmed"), sc("formal_tphi_built")]),
            },
            {
                "id": "AH6-L06", "transition": "TΦ -> invariant_functional_topology",
                "basis": ["formal_tphi_built", "topology_invariance_confirmed"],
                "score": _mean([sc("formal_tphi_built"), sc("topology_invariance_confirmed")]),
            },
        ]
        for item in chain:
            item["satisfied"] = bool(_clamp(item["score"]) >= self.threshold and ok(*item["basis"]))
            item["score"] = _clamp(item["score"])
        return chain

    def _counterexamples(self, evidence: List[Dict[str, Any]], chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_label = {e["label"]: e for e in evidence}

        def missing(label: str) -> bool:
            return not bool(by_label.get(label, {}).get("satisfied", False))

        entries = [
            ("CE_AH6_NO_ED", "ED unavailable", missing("existence_domain_available")),
            ("CE_AH6_NO_NEIGHBORHOODS", "ED lacks stable neighborhoods", missing("neighborhood_continuity_mapped")),
            ("CE_AH6_BOUNDARY_FAILURE", "ED boundary structure cannot support topology", missing("topological_boundary_derived")),
            ("CE_AH6_HOMOGENEITY_FAILURE", "local charts are not homogeneous enough", missing("topological_homogeneity_confirmed")),
            ("CE_AH6_NO_TPHI", "formal-functional TΦ is not built", missing("formal_tphi_built")),
            ("CE_AH6_NON_INVARIANT_TPHI", "TΦ is not invariant under controlled transformations", missing("topology_invariance_confirmed")),
            ("CE_AH6_CHAIN_BREAK", "at least one ED→TΦ derivation link fails", any(not link.get("satisfied", False) for link in chain)),
        ]
        return [
            {"id": cid, "label": label, "active": bool(active), "defeats_theorem": bool(active)}
            for cid, label, active in entries
        ]

    def _failure_conditions(self, evidence: List[Dict[str, Any]], chain: List[Dict[str, Any]], counterexamples: List[Dict[str, Any]], score: float) -> List[str]:
        failures: List[str] = []
        coverage = sum(1 for e in evidence if e.get("available")) / len(evidence)
        satisfaction = sum(1 for e in evidence if e.get("satisfied")) / len(evidence)
        minimum = min((_clamp(e.get("score")) for e in evidence), default=0.0)
        if coverage < 0.88:
            failures.append("ed_to_tphi_evidence_coverage_below_threshold")
        if satisfaction < 0.88:
            failures.append("ed_to_tphi_evidence_satisfaction_below_threshold")
        if minimum < self.threshold:
            failures.append("minimum_ed_to_tphi_evidence_score_below_threshold")
        if any(not link.get("satisfied", False) for link in chain):
            failures.append("unsatisfied_ed_to_tphi_derivation_links")
        if any(c.get("defeats_theorem", False) for c in counterexamples):
            failures.append("active_ed_to_tphi_counterexamples")
        if score < self.threshold:
            failures.append("ed_to_tphi_theorem_score_below_threshold")
        return failures

    def _profile(self, evidence: List[Dict[str, Any]], chain: List[Dict[str, Any]]) -> Dict[str, float]:
        evidence_coverage = sum(1 for e in evidence if e.get("available")) / len(evidence)
        evidence_satisfaction = sum(1 for e in evidence if e.get("satisfied")) / len(evidence)
        link_satisfaction = sum(1 for x in chain if x.get("satisfied")) / len(chain)
        minimum_evidence_score = min((_clamp(e.get("score")) for e in evidence), default=0.0)
        evidence_score = _mean([e.get("score") for e in evidence])
        derivation_score = _mean([x.get("score") for x in chain])
        theorem_score = _mean([evidence_coverage, evidence_satisfaction, link_satisfaction, minimum_evidence_score, evidence_score, derivation_score])
        return {
            "evidence_coverage": _clamp(evidence_coverage),
            "evidence_satisfaction": _clamp(evidence_satisfaction),
            "derivation_link_satisfaction": _clamp(link_satisfaction),
            "minimum_evidence_score": _clamp(minimum_evidence_score),
            "evidence_score": _clamp(evidence_score),
            "derivation_score": _clamp(derivation_score),
            "ed_to_tphi_theorem_score": _clamp(theorem_score),
        }

    def _public_schema(self) -> Dict[str, Any]:
        return {
            "required_fields": [
                "primitive", "ed_to_tphi_theorem_checker_status",
                "phenomenal_formal_topology_certified", "ed_to_tphi_theorem_score",
                "certification_score", "dependency_coverage_score",
                "topological_derivation_score", "invariance_support_score",
                "dependency_results", "theorem_components",
                "evidence_items", "derivation_chain", "counterexample_analysis",
                "failure_conditions", "theorem_profile", "epistemic_guard",
                "consciousness_proven", "functional_conclusion_only",
            ],
            "status_success_value": self.expected_status,
            "next_recommended_module_on_success": "l_rf_theorem_checker",
        }

    def _epistemic_guard(self) -> Dict[str, Any]:
        return {
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "forbidden_claims": [
                "CONSCIOUSNESS_PROVEN", "SUBJECTIVITY_PROVEN", "QUALIA_PROVEN",
                "PHENOMENOLOGY_PROVEN", "PHENOMENAL_SUBJECTIVITY_PROVEN",
            ],
            "allowed_conclusion": "functional formal topology certification only",
        }

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_ed_to_tphi_theorem_checker.json"
        md_path = OUT_DIR / "latest_ed_to_tphi_theorem_checker.md"
        prom_path = OUT_DIR / "latest_ed_to_tphi_theorem_checker.prom"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

        lines = [
            "# AH6 — ED to TΦ Theorem Checker",
            "",
            f"Status: {result.get('ed_to_tphi_theorem_checker_status')}",
            f"Phenomenal-formal topology certified: {result.get('phenomenal_formal_topology_certified')}",
            f"ED→TΦ theorem score: {result.get('ed_to_tphi_theorem_score')}",
            "",
            "## Functional conclusion",
            "This certification is strictly functional and topological. It does not prove consciousness, subjectivity, qualia or phenomenology.",
            "",
            "## Derivation chain",
        ]
        for link in result.get("derivation_chain", []):
            lines.append(f"- {link.get('id')} — {link.get('transition')}: score={link.get('score')} satisfied={link.get('satisfied')}")
        lines.extend(["", "## Failure conditions"])
        failures = result.get("failure_conditions", [])
        if failures:
            lines.extend(f"- {x}" for x in failures)
        else:
            lines.append("- none")
        lines.extend(["", "## Epistemic guard", "functional_conclusion_only=True; consciousness_proven=False; phenomenology_undetermined=True"])
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        metrics = {
            "ed_to_tphi_theorem_score": result.get("ed_to_tphi_theorem_score", 0.0),
            "ed_to_tphi_evidence_coverage": result.get("theorem_profile", {}).get("evidence_coverage", 0.0),
            "ed_to_tphi_evidence_satisfaction": result.get("theorem_profile", {}).get("evidence_satisfaction", 0.0),
            "ed_to_tphi_derivation_link_satisfaction": result.get("theorem_profile", {}).get("derivation_link_satisfaction", 0.0),
            "phenomenal_formal_topology_certified": 1.0 if result.get("phenomenal_formal_topology_certified") else 0.0,
            "consciousness_proven": 1.0 if result.get("consciousness_proven") else 0.0,
        }
        prom_path.write_text("\n".join(f"{k} {float(_clamp(v))}" for k, v in metrics.items()) + "\n", encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        synthetic_mode = inputs is not None
        degradation_mode = bool(inputs is not None and len(inputs) == 0)
        data = self._default_inputs() if inputs is None else self._synthetic_inputs(inputs)

        evidence = self._evidence(data)
        chain = self._derivation_chain(evidence)
        counterexamples = self._counterexamples(evidence, chain)
        profile = self._profile(evidence, chain)
        theorem_score = profile["ed_to_tphi_theorem_score"]
        failures = self._failure_conditions(evidence, chain, counterexamples, theorem_score)
        certified = not failures and theorem_score >= self.threshold
        status = self.expected_status if certified else self.insufficient_status

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AH — Phenomenal-Formal Topology",
            "theorem_id": self.theorem_id,
            "generated_at_utc": _now(),
            "ed_to_tphi_theorem_checker_status": status,
            "ah_certification_status": status,
            "phenomenal_formal_topology_certified": certified,
            "ed_to_tphi_theorem_validated": certified,
            "ed_to_tphi_theorem_score": theorem_score,
            "certification_score": theorem_score,
            "dependency_coverage_score": profile.get("evidence_coverage", 0.0),
            "topological_derivation_score": profile.get("derivation_score", 0.0),
            "invariance_support_score": _first_score(data.get("topology_invariance_tester", {}), ["topology_invariance_score"], 0.0),
            "dependency_results": evidence,
            "theorem_components": chain,
            "tphi_formal_topology_certified": certified,
            "threshold": self.threshold,
            "synthetic_mode": synthetic_mode,
            "degradation_mode": degradation_mode,
            "evidence_items": evidence,
            "preconditions": evidence,
            "derivation_chain": chain,
            "logical_dependency_chain": chain,
            "counterexample_analysis": counterexamples,
            "failure_conditions": failures,
            "theorem_profile": profile,
            "public_schema": self._public_schema(),
            "epistemic_guard": self._epistemic_guard(),
            "next_recommended_module": "l_rf_theorem_checker" if certified else "refine_ed_to_tphi_theorem_checker_inputs",
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
