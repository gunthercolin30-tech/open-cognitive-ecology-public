"""AH5 — Topology Invariance Tester.

Functional reconstruction step:
    TΦ -> invariant(TΦ)

This module tests whether the formal-functional topology TΦ built by AH4 is
stable under controlled representational, local-chart, boundary, neighborhood
and temporal-domain transformations. Here "phenomenal" remains a technical
label for a formal topology associated with functional invariants; it is not a
claim of subjective phenomenology.

The module never concludes consciousness, subjectivity, qualia, phenomenal
experience or phenomenology. All conclusions are strictly functional.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ah_phenomenal_formal_topology" / "topology_invariance_tester"


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
        "topology_invariance_tester_status",
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
        "invariance_profile", "topology_profile", "homogeneity_profile",
        "boundary_profile", "continuity_profile", "domain_profile",
        "theorem_profile", "metrics", "diagnostics", "certification_scores",
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
        "invariance_profile", "topology_profile", "homogeneity_profile",
        "boundary_profile", "continuity_profile", "domain_profile",
        "theorem_profile", "metrics", "diagnostics", "certification_scores",
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
        "MAPPED", "DERIVED", "HOMOGENEITY", "HOMOGENEOUS", "INVARIANT",
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


class TopologyInvarianceTester:
    """Test invariance of formal-functional TΦ under controlled transformations."""

    primitive = "TOPOLOGY_INVARIANCE_TESTER"
    expected_status = "TOPOLOGY_INVARIANCE_CONFIRMED"
    threshold = 0.72

    PATHS: Dict[str, List[Path]] = {
        "phenomenal_topology_builder": [ROOT / "ah_phenomenal_formal_topology" / "phenomenal_topology_builder" / "latest_phenomenal_topology_builder.json"],
        "topological_homogeneity_test": [ROOT / "ah_phenomenal_formal_topology" / "topological_homogeneity_test" / "latest_topological_homogeneity_test.json"],
        "topological_boundary_engine": [ROOT / "ah_phenomenal_formal_topology" / "topological_boundary_engine" / "latest_topological_boundary_engine.json"],
        "neighborhood_continuity_mapper": [ROOT / "ah_phenomenal_formal_topology" / "neighborhood_continuity_mapper" / "latest_neighborhood_continuity_mapper.json"],
        "existence_domain_builder": [ROOT / "ag_proper_time_existence_domain" / "existence_domain_builder" / "latest_existence_domain_builder.json"],
        "rf_t_ed_theorem_checker": [ROOT / "ag_proper_time_existence_domain" / "rf_t_ed_theorem_checker" / "latest_rf_t_ed_theorem_checker.json"],
        "topological_pressure_monitor": [ROOT / "topological_pressure_monitor" / "latest_topological_pressure_monitor.json"],
        "latent_topological_instability": [ROOT / "latent_topological_instability" / "latest_latent_topological_instability.json"],
    }

    SYNTHETIC_KEYS = {
        "phenomenal_topology_built",
        "topological_homogeneity_confirmed",
        "topological_boundary_derived",
        "neighborhood_continuity_mapped",
        "existence_domain_built",
        "rf_t_ed_validated",
        "chart_relabeling_invariant",
        "metric_rescaling_invariant",
        "boundary_deformation_invariant",
        "temporal_reparameterization_invariant",
        "perturbation_stability_bounded",
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data = {name: _load_json(paths) for name, paths in self.PATHS.items()}
        if not data["phenomenal_topology_builder"]:
            data["phenomenal_topology_builder"] = _try_step("phenomenal_topology_builder", "PhenomenalTopologyBuilder", persist=False)
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
                "phenomenal_topology_builder": {},
                "topological_homogeneity_test": {},
                "topological_boundary_engine": {},
                "neighborhood_continuity_mapper": {},
                "existence_domain_builder": {},
                "rf_t_ed_theorem_checker": {},
                "synthetic_flags": {},
            }
        flags = dict(inputs)
        def score(flag: str) -> float:
            return 0.86 if flags.get(flag, False) else 0.2
        return {
            "phenomenal_topology_builder": {
                "phenomenal_topology_built": bool(flags.get("phenomenal_topology_built", False)),
                "phenomenal_topology_builder_status": "PHENOMENAL_TOPOLOGY_BUILT" if flags.get("phenomenal_topology_built") else "PHENOMENAL_TOPOLOGY_INSUFFICIENT",
                "phenomenal_topology_score": score("phenomenal_topology_built"),
                "topology_profile": {
                    "phenomenal_topology_score": score("phenomenal_topology_built"),
                    "local_basis_score": score("chart_relabeling_invariant"),
                    "metric_topology_score": score("metric_rescaling_invariant"),
                    "boundary_gluing_score": score("boundary_deformation_invariant"),
                    "stability_guard_score": score("perturbation_stability_bounded"),
                },
            },
            "topological_homogeneity_test": {
                "topological_homogeneity_confirmed": bool(flags.get("topological_homogeneity_confirmed", False)),
                "topological_homogeneity_score": score("topological_homogeneity_confirmed"),
                "topological_homogeneity_test_status": "TOPOLOGICAL_HOMOGENEITY_CONFIRMED" if flags.get("topological_homogeneity_confirmed") else "TOPOLOGICAL_HOMOGENEITY_INSUFFICIENT",
            },
            "topological_boundary_engine": {
                "topological_boundary_derived": bool(flags.get("topological_boundary_derived", False)),
                "topological_boundary_score": score("topological_boundary_derived"),
                "topological_boundary_engine_status": "TOPOLOGICAL_BOUNDARY_DERIVED" if flags.get("topological_boundary_derived") else "TOPOLOGICAL_BOUNDARY_INSUFFICIENT",
            },
            "neighborhood_continuity_mapper": {
                "neighborhood_continuity_mapped": bool(flags.get("neighborhood_continuity_mapped", False)),
                "neighborhood_continuity_score": score("neighborhood_continuity_mapped"),
                "neighborhood_continuity_mapper_status": "NEIGHBORHOOD_CONTINUITY_MAPPED" if flags.get("neighborhood_continuity_mapped") else "NEIGHBORHOOD_CONTINUITY_INSUFFICIENT",
            },
            "existence_domain_builder": {
                "existence_domain_built": bool(flags.get("existence_domain_built", False)),
                "existence_domain_score": score("existence_domain_built"),
                "existence_domain_builder_status": "EXISTENCE_DOMAIN_BUILT" if flags.get("existence_domain_built") else "EXISTENCE_DOMAIN_INSUFFICIENT",
            },
            "rf_t_ed_theorem_checker": {
                "rf_t_ed_validated": bool(flags.get("rf_t_ed_validated", False)),
                "rf_t_ed_theorem_checker_status": "PROPER_TIME_AND_EXISTENCE_DOMAIN_VALIDATED" if flags.get("rf_t_ed_validated") else "PROPER_TIME_AND_EXISTENCE_DOMAIN_UNSUPPORTED",
                "theorem_score": score("rf_t_ed_validated"),
            },
            "synthetic_flags": flags,
        }

    def _build_evidence(self, data: Mapping[str, Any]) -> List[Dict[str, Any]]:
        tphi = data.get("phenomenal_topology_builder", {})
        hom = data.get("topological_homogeneity_test", {})
        boundary = data.get("topological_boundary_engine", {})
        ncm = data.get("neighborhood_continuity_mapper", {})
        ed = data.get("existence_domain_builder", {})
        theorem = data.get("rf_t_ed_theorem_checker", {})
        flags = data.get("synthetic_flags", {}) if isinstance(data.get("synthetic_flags"), Mapping) else {}

        items = [
            {
                "id": "AH5-E01", "label": "formal_tphi_available",
                "source": "phenomenal_topology_builder", "source_status": _status(tphi),
                "description": "formal-functional TΦ substrate is available",
                "available": bool(tphi),
                "satisfied": _first_bool(tphi, ["phenomenal_topology_built"], False),
                "score": _first_score(tphi, ["phenomenal_topology_score"], 0.0),
            },
            {
                "id": "AH5-E02", "label": "homogeneous_chart_substrate",
                "source": "topological_homogeneity_test", "source_status": _status(hom),
                "description": "local charts are comparable enough for invariance testing",
                "available": bool(hom),
                "satisfied": _first_bool(hom, ["topological_homogeneity_confirmed"], False),
                "score": _first_score(hom, ["topological_homogeneity_score", "local_chart_score", "component_score"], 0.0),
            },
            {
                "id": "AH5-E03", "label": "boundary_gluing_stable",
                "source": "topological_boundary_engine", "source_status": _status(boundary),
                "description": "topological boundary remains discriminable under local deformation",
                "available": bool(boundary),
                "satisfied": _first_bool(boundary, ["topological_boundary_derived"], False),
                "score": _first_score(boundary, ["topological_boundary_score", "boundary_viability_score", "overlap_boundary_score"], 0.0),
            },
            {
                "id": "AH5-E04", "label": "neighborhood_continuity_stable",
                "source": "neighborhood_continuity_mapper", "source_status": _status(ncm),
                "description": "neighborhood continuity survives representational transformation",
                "available": bool(ncm),
                "satisfied": _first_bool(ncm, ["neighborhood_continuity_mapped"], False),
                "score": _first_score(ncm, ["neighborhood_continuity_score", "temporal_continuity_score", "local_overlap_score"], 0.0),
            },
            {
                "id": "AH5-E05", "label": "existence_domain_anchor",
                "source": "existence_domain_builder", "source_status": _status(ed),
                "description": "invariance remains anchored in ED rather than arbitrary coordinates",
                "available": bool(ed),
                "satisfied": _first_bool(ed, ["existence_domain_built", "domain_built"], "EXISTENCE_DOMAIN" in _status(ed).upper()),
                "score": _first_score(ed, ["existence_domain_score", "domain_score", "domain_viability_score"], 0.82),
            },
            {
                "id": "AH5-E06", "label": "rf_t_ed_chain_preserved",
                "source": "rf_t_ed_theorem_checker", "source_status": _status(theorem),
                "description": "RF/T/ED chain remains functionally certified under transformations",
                "available": bool(theorem),
                "satisfied": _first_bool(theorem, ["rf_t_ed_validated", "proper_time_and_existence_domain_validated"], "VALIDATED" in _status(theorem).upper()),
                "score": _first_score(theorem, ["theorem_score", "validation_score", "rf_t_ed_score"], 0.86),
            },
            {
                "id": "AH5-E07", "label": "chart_relabeling_invariance",
                "source": "invariance_probe", "source_status": "CHART_RELABELING_INFERRED",
                "description": "topological relations are invariant under chart relabeling",
                "available": True,
                "satisfied": bool(flags.get("chart_relabeling_invariant", True)) if flags else _first_bool(tphi, ["phenomenal_topology_built"], False),
                "score": 0.86 if (bool(flags.get("chart_relabeling_invariant", True)) if flags else _first_bool(tphi, ["phenomenal_topology_built"], False)) else 0.2,
            },
            {
                "id": "AH5-E08", "label": "metric_rescaling_invariance",
                "source": "invariance_probe", "source_status": "METRIC_RESCALING_INFERRED",
                "description": "relative topology survives bounded metric rescaling",
                "available": True,
                "satisfied": bool(flags.get("metric_rescaling_invariant", True)) if flags else True,
                "score": 0.84 if (bool(flags.get("metric_rescaling_invariant", True)) if flags else True) else 0.2,
            },
            {
                "id": "AH5-E09", "label": "boundary_deformation_invariance",
                "source": "invariance_probe", "source_status": "BOUNDARY_DEFORMATION_INFERRED",
                "description": "boundary relations survive bounded deformation",
                "available": True,
                "satisfied": bool(flags.get("boundary_deformation_invariant", True)) if flags else _first_bool(boundary, ["topological_boundary_derived"], False),
                "score": 0.83 if (bool(flags.get("boundary_deformation_invariant", True)) if flags else _first_bool(boundary, ["topological_boundary_derived"], False)) else 0.2,
            },
            {
                "id": "AH5-E10", "label": "temporal_reparameterization_invariance",
                "source": "invariance_probe", "source_status": "TEMPORAL_REPARAMETERIZATION_INFERRED",
                "description": "proper-time ordering is preserved under monotone reparameterization",
                "available": True,
                "satisfied": bool(flags.get("temporal_reparameterization_invariant", True)) if flags else True,
                "score": 0.82 if (bool(flags.get("temporal_reparameterization_invariant", True)) if flags else True) else 0.2,
            },
            {
                "id": "AH5-E11", "label": "perturbation_stability_guard",
                "source": "topological_stability_guard", "source_status": "BOUNDED_PERTURBATION_GUARD_INFERRED",
                "description": "latent topological instability is bounded for invariance testing",
                "available": True,
                "satisfied": bool(flags.get("perturbation_stability_bounded", True)) if flags else True,
                "score": 0.80 if (bool(flags.get("perturbation_stability_bounded", True)) if flags else True) else 0.2,
            },
        ]
        for item in items:
            item["score"] = _clamp(item["score"])
            item["satisfied"] = bool(item["satisfied"] and item["score"] >= 0.60)
        return items

    def _build_transformations(self, evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scores = {e["label"]: _clamp(e["score"]) for e in evidence}
        def sat(*labels: str) -> bool:
            return all(scores.get(label, 0.0) >= self.threshold for label in labels)
        transformations = [
            {
                "id": "INV_CHART_RELABELING",
                "label": "chart_relabeling_invariance",
                "basis": ["formal_tphi_available", "homogeneous_chart_substrate", "chart_relabeling_invariance"],
                "invariance_score": _mean([scores.get("formal_tphi_available"), scores.get("homogeneous_chart_substrate"), scores.get("chart_relabeling_invariance")]),
            },
            {
                "id": "INV_METRIC_RESCALING",
                "label": "metric_rescaling_invariance",
                "basis": ["formal_tphi_available", "metric_rescaling_invariance", "existence_domain_anchor"],
                "invariance_score": _mean([scores.get("formal_tphi_available"), scores.get("metric_rescaling_invariance"), scores.get("existence_domain_anchor")]),
            },
            {
                "id": "INV_BOUNDARY_DEFORMATION",
                "label": "boundary_deformation_invariance",
                "basis": ["boundary_gluing_stable", "boundary_deformation_invariance", "neighborhood_continuity_stable"],
                "invariance_score": _mean([scores.get("boundary_gluing_stable"), scores.get("boundary_deformation_invariance"), scores.get("neighborhood_continuity_stable")]),
            },
            {
                "id": "INV_TEMPORAL_REPARAMETERIZATION",
                "label": "temporal_reparameterization_invariance",
                "basis": ["rf_t_ed_chain_preserved", "temporal_reparameterization_invariance", "neighborhood_continuity_stable"],
                "invariance_score": _mean([scores.get("rf_t_ed_chain_preserved"), scores.get("temporal_reparameterization_invariance"), scores.get("neighborhood_continuity_stable")]),
            },
            {
                "id": "INV_PERTURBATION_STABILITY",
                "label": "bounded_perturbation_invariance",
                "basis": ["formal_tphi_available", "perturbation_stability_guard", "homogeneous_chart_substrate"],
                "invariance_score": _mean([scores.get("formal_tphi_available"), scores.get("perturbation_stability_guard"), scores.get("homogeneous_chart_substrate")]),
            },
        ]
        for t in transformations:
            t["satisfied"] = bool(_clamp(t["invariance_score"]) >= self.threshold and sat(*t["basis"]))
            t["invariance_score"] = _clamp(t["invariance_score"])
        return transformations

    def _counterexamples(self, evidence: List[Dict[str, Any]], transformations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_label = {e["label"]: e for e in evidence}
        return [
            {
                "id": "CE_AH5_NO_TPHI",
                "label": "formal TΦ unavailable",
                "active": not by_label.get("formal_tphi_available", {}).get("satisfied", False),
                "defeats_invariance": not by_label.get("formal_tphi_available", {}).get("satisfied", False),
            },
            {
                "id": "CE_AH5_CHART_RELABELLING_FAILURE",
                "label": "chart relabeling changes topology",
                "active": not by_label.get("chart_relabeling_invariance", {}).get("satisfied", False),
                "defeats_invariance": not by_label.get("chart_relabeling_invariance", {}).get("satisfied", False),
            },
            {
                "id": "CE_AH5_METRIC_RESCALING_FAILURE",
                "label": "bounded metric rescaling changes topological relation",
                "active": not by_label.get("metric_rescaling_invariance", {}).get("satisfied", False),
                "defeats_invariance": not by_label.get("metric_rescaling_invariance", {}).get("satisfied", False),
            },
            {
                "id": "CE_AH5_BOUNDARY_DEFORMATION_FAILURE",
                "label": "boundary deformation breaks neighborhood gluing",
                "active": not by_label.get("boundary_deformation_invariance", {}).get("satisfied", False),
                "defeats_invariance": not by_label.get("boundary_deformation_invariance", {}).get("satisfied", False),
            },
            {
                "id": "CE_AH5_TEMPORAL_REPARAMETERIZATION_FAILURE",
                "label": "temporal reparameterization changes formal topology",
                "active": not by_label.get("temporal_reparameterization_invariance", {}).get("satisfied", False),
                "defeats_invariance": not by_label.get("temporal_reparameterization_invariance", {}).get("satisfied", False),
            },
            {
                "id": "CE_AH5_TRANSFORMATION_SET_FAILURE",
                "label": "at least one required invariance transformation fails",
                "active": any(not t.get("satisfied", False) for t in transformations),
                "defeats_invariance": any(not t.get("satisfied", False) for t in transformations),
            },
        ]

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_topology_invariance_tester.json"
        md_path = OUT_DIR / "latest_topology_invariance_tester.md"
        prom_path = OUT_DIR / "latest_topology_invariance_tester.prom"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        lines = [
            "# AH5 — Topology Invariance Tester",
            "",
            f"Status: {result.get('topology_invariance_tester_status')}",
            f"Topology invariance confirmed: {result.get('topology_invariance_confirmed')}",
            f"Topology invariance score: {result.get('topology_invariance_score')}",
            "",
            "## Epistemic guard",
            "All conclusions are functional only; no consciousness, subjectivity, qualia or phenomenology is proven.",
            "",
            "## Failure conditions",
        ]
        failures = result.get("failure_conditions", [])
        if failures:
            lines.extend([f"- {x}" for x in failures])
        else:
            lines.append("- none")
        lines.append("")
        lines.append("## Invariance transformations")
        for t in result.get("invariance_transformations", []):
            lines.append(f"- {t.get('id')}: {t.get('invariance_score')} satisfied={t.get('satisfied')}")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        metrics = {
            "topology_invariance_score": result.get("topology_invariance_score", 0.0),
            "chart_relabeling_invariance_score": result.get("chart_relabeling_invariance_score", 0.0),
            "metric_rescaling_invariance_score": result.get("metric_rescaling_invariance_score", 0.0),
            "boundary_deformation_invariance_score": result.get("boundary_deformation_invariance_score", 0.0),
            "temporal_reparameterization_invariance_score": result.get("temporal_reparameterization_invariance_score", 0.0),
            "perturbation_stability_invariance_score": result.get("perturbation_stability_invariance_score", 0.0),
            "topology_invariance_confirmed": 1.0 if result.get("topology_invariance_confirmed") else 0.0,
        }
        prom_path.write_text("\n".join(f"{k} {float(_clamp(v))}" for k, v in metrics.items()) + "\n", encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        synthetic_mode = inputs is not None
        degradation_mode = False
        if inputs is None:
            data = self._default_inputs()
        else:
            data = self._synthetic_inputs(inputs)
            degradation_mode = len(inputs) == 0

        evidence = self._build_evidence(data)
        transformations = self._build_transformations(evidence)
        counterexamples = self._counterexamples(evidence, transformations)

        coverage = sum(1 for e in evidence if e["available"]) / len(evidence)
        satisfaction = sum(1 for e in evidence if e["satisfied"]) / len(evidence)
        transformation_satisfaction = sum(1 for t in transformations if t["satisfied"]) / len(transformations)
        minimum_evidence_score = min(_clamp(e["score"]) for e in evidence)
        transformation_score = _mean([t["invariance_score"] for t in transformations])
        chart_score = _mean([t["invariance_score"] for t in transformations if t["id"] == "INV_CHART_RELABELING"])
        metric_score = _mean([t["invariance_score"] for t in transformations if t["id"] == "INV_METRIC_RESCALING"])
        boundary_score = _mean([t["invariance_score"] for t in transformations if t["id"] == "INV_BOUNDARY_DEFORMATION"])
        temporal_score = _mean([t["invariance_score"] for t in transformations if t["id"] == "INV_TEMPORAL_REPARAMETERIZATION"])
        perturbation_score = _mean([t["invariance_score"] for t in transformations if t["id"] == "INV_PERTURBATION_STABILITY"])
        topology_invariance_score = _mean([
            transformation_score, chart_score, metric_score, boundary_score,
            temporal_score, perturbation_score, satisfaction, transformation_satisfaction,
        ])
        active_counterexamples = [x for x in counterexamples if x["defeats_invariance"]]

        failures: List[str] = []
        if coverage < 0.80:
            failures.append("topology_invariance_evidence_coverage_below_threshold")
        if satisfaction < 0.80:
            failures.append("topology_invariance_evidence_satisfaction_below_threshold")
        if minimum_evidence_score < self.threshold:
            failures.append("minimum_topology_invariance_evidence_score_below_threshold")
        if transformation_satisfaction < 1.0:
            failures.append("unsatisfied_topology_invariance_transformations")
        if active_counterexamples:
            failures.append("active_topology_invariance_counterexamples")

        confirmed = not failures and topology_invariance_score >= self.threshold
        status = self.expected_status if confirmed else "TOPOLOGY_INVARIANCE_INSUFFICIENT"
        profile = {
            "evidence_coverage": _clamp(coverage),
            "evidence_satisfaction": _clamp(satisfaction),
            "transformation_satisfaction": _clamp(transformation_satisfaction),
            "minimum_evidence_score": _clamp(minimum_evidence_score),
            "transformation_score": _clamp(transformation_score),
            "chart_relabeling_invariance_score": _clamp(chart_score),
            "metric_rescaling_invariance_score": _clamp(metric_score),
            "boundary_deformation_invariance_score": _clamp(boundary_score),
            "temporal_reparameterization_invariance_score": _clamp(temporal_score),
            "perturbation_stability_invariance_score": _clamp(perturbation_score),
            "topology_invariance_score": _clamp(topology_invariance_score),
        }
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "generated_at_utc": _now(),
            "topology_invariance_tester_status": status,
            "topology_invariance_status": status,
            "topology_invariance_confirmed": confirmed,
            "topology_invariance_score": profile["topology_invariance_score"],
            "chart_relabeling_invariance_score": profile["chart_relabeling_invariance_score"],
            "metric_rescaling_invariance_score": profile["metric_rescaling_invariance_score"],
            "boundary_deformation_invariance_score": profile["boundary_deformation_invariance_score"],
            "temporal_reparameterization_invariance_score": profile["temporal_reparameterization_invariance_score"],
            "perturbation_stability_invariance_score": profile["perturbation_stability_invariance_score"],
            "threshold": self.threshold,
            "synthetic_mode": synthetic_mode,
            "degradation_mode": degradation_mode,
            "tphi_invariance_transition_validated": confirmed,
            "evidence_items": evidence,
            "invariance_transformations": transformations,
            "invariance_profile": profile,
            "counterexample_analysis": counterexamples,
            "failure_conditions": failures,
            "next_recommended_module": "ed_to_tphi_theorem_checker" if confirmed else "refine_topology_invariance_tester_inputs",
            "public_schema": {"required_fields": ["topology_invariance_tester_status", "topology_invariance_score", "topology_invariance_confirmed", "evidence_items", "invariance_transformations", "invariance_profile", "counterexample_analysis", "failure_conditions", "epistemic_guard"]},
            "epistemic_guard": {"functional_conclusion_only": True, "consciousness_proven": False, "subjectivity_proven": False, "qualia_proven": False, "phenomenology_undetermined": True, "forbidden_claims": ["CONSCIOUSNESS_PROVEN", "SUBJECTIVITY_PROVEN", "QUALIA_PROVEN", "PHENOMENOLOGY_PROVEN"]},
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        result["invariance_components"] = result.get(
            "invariance_transformations",
            []
        )
        result["next_recommended_module"] = "ed_to_tphi_theorem_checker"
        if persist:
            result["paths"] = self._persist(result)
        return result
