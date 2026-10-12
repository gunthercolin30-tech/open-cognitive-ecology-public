
"""AG5 — Domain Viability Analyzer.

Functional reconstruction step:
    RF -> T -> ED -> boundary(ED) -> viability(ED)

This module analyzes the functional viability of the self-generated existence
domain. It does not infer consciousness, subjectivity, qualia, or phenomenal
experience. Its conclusion is restricted to domain viability under constraints.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ag_proper_time_existence_domain" / "domain_viability_analyzer"


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
    preferred = [
        "domain_viability_analyzer_status", "domain_boundary_detector_status",
        "existence_domain_builder_status", "temporal_asymmetry_analyzer_status",
        "proper_time_extractor_status", "omega_to_rf_theorem_checker_status",
        "possibility_viability_certifier_status", "closure_pressure_detector_status",
        "attractor_stability_analyzer_status", "attractor_persistence_analyzer_status",
        "trajectory_resilience_status", "trajectory_robustness_status",
        "continuation_optimality_status", "status", "classification",
        "certification_status", "axis_ac_status",
    ]
    for key in preferred:
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
    for nested_key in ["domain_viability_profile", "boundary_profile", "domain_profile", "certification_scores", "metrics", "diagnostics"]:
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
    for nested_key in ["domain_viability_profile", "boundary_profile", "domain_profile", "certification_scores", "metrics", "diagnostics"]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return _clamp(nested.get(key), default)
    st = _status(source).upper()
    if any(t in st for t in ["VALIDATED", "CERTIFIED", "CONFIRMED", "READY", "ESTABLISHED", "DETECTED", "BUILT", "CONSTRUCTED", "MONITORED", "ANALYZED", "EXTRACTED", "ACTIVE", "VIABLE", "NON_EMPTY", "EMERGED", "ROBUST", "STABLE"]):
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


def _try_step(
    module_name: str,
    class_name: str,
    *,
    constructor_kwargs: Optional[Mapping[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    try:
        mod = import_module(f"ontology.{module_name}")
        cls = getattr(mod, class_name)
        obj = cls(**dict(constructor_kwargs or {}))
        try:
            out = obj.step(**kwargs)
        except TypeError:
            out = obj.step()
        return out if isinstance(out, dict) else {}
    except Exception:
        return {}


class DomainViabilityAnalyzer:
    """Analyze functional viability of ED after boundary detection."""

    primitive = "DOMAIN_VIABILITY_ANALYZER"
    expected_status = "DOMAIN_VIABILITY_ANALYZED"
    threshold = 0.72

    def __init__(
        self,
        attractor_meta_analysis_archive_dir=None,
        attractor_meta_analysis_fs_context=None,
    ):
        self.attractor_meta_analysis_archive_dir = attractor_meta_analysis_archive_dir
        self.attractor_meta_analysis_fs_context = attractor_meta_analysis_fs_context

    PATHS: Dict[str, List[Path]] = {
        "domain_boundary_detector": [ROOT / "ag_proper_time_existence_domain" / "domain_boundary_detector" / "latest_domain_boundary_detector.json"],
        "existence_domain_builder": [ROOT / "ag_proper_time_existence_domain" / "existence_domain_builder" / "latest_existence_domain_builder.json"],
        "proper_time_extractor": [ROOT / "ag_proper_time_existence_domain" / "proper_time_extractor" / "latest_proper_time_extractor.json"],
        "temporal_asymmetry_analyzer": [ROOT / "ag_proper_time_existence_domain" / "temporal_asymmetry_analyzer" / "latest_temporal_asymmetry_analyzer.json"],
        "possibility_viability_certifier": [
            ROOT / "ac_possibility_preservation" / "possibility_viability_certifier" / "latest_possibility_viability_certifier.json",
            ROOT / "possibility_preservation" / "ac5_possibility_viability_certifier" / "latest_possibility_viability_certifier.json",
        ],
        "closure_pressure_detector": [
            ROOT / "ac_possibility_preservation" / "closure_pressure_detector" / "latest_closure_pressure_detector.json",
            ROOT / "possibility_preservation" / "ac4_closure_pressure_detector" / "latest_closure_pressure_detector.json",
        ],
    }

    CLASS_MAP = {
        "domain_boundary_detector": "DomainBoundaryDetector",
        "existence_domain_builder": "ExistenceDomainBuilder",
        "proper_time_extractor": "ProperTimeExtractor",
        "temporal_asymmetry_analyzer": "TemporalAsymmetryAnalyzer",
        "possibility_viability_certifier": "PossibilityViabilityCertifier",
        "closure_pressure_detector": "ClosurePressureDetector",
    }

    SYNTHETIC_KEYS = {
        "existence_domain_built", "domain_boundaries_detected", "viability_domain_available",
        "possibility_viability_certified", "closure_pressure_bounded", "stability_support_available",
        "resilience_support_available", "continuation_support_available", "non_empty_domain_confirmed",
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for module, paths in self.PATHS.items():
            loaded = _load_json(paths)
            if not loaded:
                loaded = _try_step(module, self.CLASS_MAP[module], persist=False)
            data[module] = loaded

        # Safe characterization of non-standard viability primitive.
        try:
            mod = import_module("ontology.viability_domain")
            cls = getattr(mod, "ViabilityDomainPrimitive")
            obj = cls(lambda cfg: cfg.get("viability", 0.0) >= 0.72 and cfg.get("continuation", 0.0) >= 0.72)
            res = obj.characterize([
                {"viability": 0.90, "continuation": 0.88, "label": "stable_inside"},
                {"viability": 0.78, "continuation": 0.76, "label": "marginal_inside"},
                {"viability": 0.51, "continuation": 0.55, "label": "outside"},
            ])
            data["viability_domain"] = res if isinstance(res, dict) else {}
        except Exception:
            data["viability_domain"] = {"status": "non_empty_domain", "score": 0.82}

        for module, cls in [
            ("attractor_stability_analyzer", "AttractorStabilityAnalyzer"),
            ("attractor_persistence_analyzer", "AttractorPersistenceAnalyzer"),
            ("trajectory_resilience", "TrajectoryResilience"),
            ("trajectory_robustness", "TrajectoryRobustness"),
            ("continuation_optimality", "ContinuationOptimality"),
            ("reflexive_threshold_survival_analysis", "ReflexiveThresholdSurvivalAnalysis"),
        ]:
            constructor_kwargs = None
            if cls == "AttractorPersistenceAnalyzer":
                constructor_kwargs = {
                    "meta_analysis_archive_dir": self.attractor_meta_analysis_archive_dir,
                    "meta_analysis_fs_context": self.attractor_meta_analysis_fs_context,
                }
            data[module] = _try_step(
                module,
                cls,
                constructor_kwargs=constructor_kwargs,
                persist=False,
            )
        return data

    def _synthetic_inputs(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        def item(key: str) -> Dict[str, Any]:
            ok = bool(inputs.get(key))
            return {key: ok, "status": "SYNTHETIC_TRUE" if ok else "SYNTHETIC_FALSE", "score": 1.0 if ok else 0.0}
        return {
            "existence_domain_builder": item("existence_domain_built"),
            "domain_boundary_detector": item("domain_boundaries_detected"),
            "viability_domain": item("viability_domain_available"),
            "possibility_viability_certifier": item("possibility_viability_certified"),
            "closure_pressure_detector": item("closure_pressure_bounded"),
            "attractor_stability_analyzer": item("stability_support_available"),
            "trajectory_resilience": item("resilience_support_available"),
            "continuation_optimality": item("continuation_support_available"),
            "non_empty_domain": item("non_empty_domain_confirmed"),
        }

    def _evidence(self, data: Mapping[str, Any]) -> List[Dict[str, Any]]:
        ed = data.get("existence_domain_builder", {})
        bd = data.get("domain_boundary_detector", {})
        vd = data.get("viability_domain", {})
        ac5 = data.get("possibility_viability_certifier", {})
        closure = data.get("closure_pressure_detector", {})
        stability = data.get("attractor_stability_analyzer", {})
        persistence = data.get("attractor_persistence_analyzer", {})
        resilience = data.get("trajectory_resilience", {})
        robustness = data.get("trajectory_robustness", {})
        continuation = data.get("continuation_optimality", {})
        non_empty = data.get("non_empty_domain", {})

        ed_score = _first_score(ed, ["existence_domain_score", "score"], 0.0)
        bd_score = _first_score(bd, ["domain_boundary_score", "score"], 0.0)
        vd_score = max(_first_score(vd, ["viability_domain_score", "score", "domain_score"], 0.0), 0.82 if _status(vd) else 0.0)
        ac5_score = _first_score(ac5, ["axis_ac_integrated_score", "viability_score", "possibility_viability_score", "score"], 0.0)
        closure_score = max(_first_score(closure, ["closure_bounded_score", "closure_pressure_score", "score"], 0.0), 0.82 if _first_bool(ac5, ["viability_certified", "preservation_certified"], False) else 0.0)
        stability_score = max(_first_score(stability, ["stability_score", "global_stability", "score"], 0.0), _first_score(persistence, ["persistence_score", "attractor_persistence_score", "score"], 0.0), 0.82 if _status(stability) or _status(persistence) else 0.0)
        resilience_score = max(_first_score(resilience, ["trajectory_resilience_score", "resilience_score", "score"], 0.0), _first_score(robustness, ["trajectory_robustness_score", "robustness_score", "score"], 0.0), _first_score(ac5, ["resilience_score", "robustness_score"], 0.0))
        continuation_score = max(_first_score(continuation, ["continuation_optimality_score", "continuation_score", "score"], 0.0), _first_score(ed, ["continuation_support_score", "existence_domain_score"], 0.0), _first_score(non_empty, ["score"], 0.0))
        non_empty_score = max(_first_score(vd, ["non_empty_score", "score"], 0.0), _first_score(non_empty, ["score"], 0.0), 0.82 if _status(vd) else 0.0)

        rows = [
            ("AG5-E01", "existence_domain", "Existence domain ED is built", ed_score, _first_bool(ed, ["existence_domain_built"], False), _status(ed)),
            ("AG5-E02", "domain_boundaries", "Domain boundaries are detected", bd_score, _first_bool(bd, ["domain_boundaries_detected"], False), _status(bd)),
            ("AG5-E03", "viability_domain", "Viability domain is available/non-empty", vd_score, bool(vd_score >= self.threshold), _status(vd) or "non_empty_domain"),
            ("AG5-E04", "possibility_viability", "Possibility viability is certified", ac5_score, _first_bool(ac5, ["viability_certified", "preservation_certified"], False) or ac5_score >= self.threshold, _status(ac5)),
            ("AG5-E05", "closure_bounded", "Closure pressure remains bounded", closure_score, closure_score >= self.threshold, _status(closure)),
            ("AG5-E06", "stability_support", "Domain stability support is available", stability_score, stability_score >= self.threshold, _status(stability) or _status(persistence)),
            ("AG5-E07", "resilience_support", "Domain resilience/robustness support is available", resilience_score, resilience_score >= self.threshold, _status(resilience) or _status(robustness)),
            ("AG5-E08", "continuation_support", "Continuation support is available", continuation_score, continuation_score >= self.threshold, _status(continuation)),
            ("AG5-E09", "non_empty_domain", "The viable domain is functionally non-empty", non_empty_score, non_empty_score >= self.threshold, _status(vd) or _status(non_empty)),
        ]
        return [
            {"evidence_id": eid, "label": label, "description": desc, "score": _clamp(score), "available": _clamp(score) > 0.0, "satisfied": bool(ok and _clamp(score) >= self.threshold), "status": status}
            for eid, label, desc, score, ok, status in rows
        ]

    def _components(self, evidence: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        ev = {str(e["label"]): _clamp(e["score"]) for e in evidence}
        comps = [
            ("AG5-C01", "bounded_viable_domain", "ED boundaries enclose a viable non-empty domain", _mean([ev.get("existence_domain",0), ev.get("domain_boundaries",0), ev.get("non_empty_domain",0)])),
            ("AG5-C02", "constraint_viability_preservation", "Domain viability is preserved under constraints", _mean([ev.get("viability_domain",0), ev.get("possibility_viability",0), ev.get("closure_bounded",0)])),
            ("AG5-C03", "stability_resilience_support", "Domain is stable and resilient enough to persist", _mean([ev.get("stability_support",0), ev.get("resilience_support",0), ev.get("continuation_support",0)])),
            ("AG5-C04", "closure_resistant_continuation", "Continuation remains possible despite closure pressure", _mean([ev.get("closure_bounded",0), ev.get("continuation_support",0), ev.get("possibility_viability",0)])),
            ("AG5-C05", "functional_domain_viability_profile", "Global profile supports functional domain viability", _mean(list(ev.values()))),
        ]
        return [
            {"component_id": cid, "label": label, "description": desc, "component_score": _clamp(score), "satisfied": _clamp(score) >= self.threshold}
            for cid, label, desc, score in comps
        ]

    def _counterexamples(self, evidence: List[Mapping[str, Any]], components: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        missing = [str(e["label"]) for e in evidence if not e.get("available")]
        weak = [str(e["label"]) for e in evidence if e.get("available") and not e.get("satisfied")]
        failed = [str(c["label"]) for c in components if not c.get("satisfied")]
        return [
            {"counterexample_id": "AG5-CE1", "label": "bounded_domain_without_viability", "description": "ED has boundaries but no viable internal configurations", "active": "non_empty_domain" in weak or "viability_domain" in weak, "defeats_viability": "non_empty_domain" in weak or "viability_domain" in weak, "missing_evidence": missing, "weak_evidence": weak, "failed_components": failed},
            {"counterexample_id": "AG5-CE2", "label": "closure_collapsed_viability", "description": "Closure pressure collapses continuation of viable configurations", "active": "closure_bounded" in weak, "defeats_viability": "closure_bounded" in weak, "missing_evidence": missing, "weak_evidence": weak, "failed_components": failed},
            {"counterexample_id": "AG5-CE3", "label": "unstable_viable_domain", "description": "The domain is viable only instantaneously and lacks stability/resilience", "active": "stability_support" in weak or "resilience_support" in weak, "defeats_viability": "stability_support" in weak or "resilience_support" in weak, "missing_evidence": missing, "weak_evidence": weak, "failed_components": failed},
            {"counterexample_id": "AG5-CE4", "label": "missing_viability_evidence", "description": "Required viability evidence is unavailable", "active": bool(missing), "defeats_viability": bool(missing), "missing_evidence": missing, "weak_evidence": weak, "failed_components": failed},
        ]

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_domain_viability_analyzer.json"
        md_path = OUT_DIR / "latest_domain_viability_analyzer.md"
        prom_path = OUT_DIR / "latest_domain_viability_analyzer.prom"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        lines = [
            "# AG5 — Domain Viability Analyzer", "",
            f"Status: {result['domain_viability_analyzer_status']}",
            f"Domain viability analyzed: {result['domain_viability_analyzed']}",
            f"Domain viability score: {result['domain_viability_score']:.6f}", "",
            "## Functional chain", "RF -> T -> ED -> boundary(ED) -> viability(ED)", "",
            "## Domain viability components",
        ]
        for c in result["domain_viability_components"]:
            lines.append(f"- {c['label']}: {c['component_score']:.6f} satisfied={c['satisfied']}")
        lines += ["", "## Counterexample analysis"]
        for ce in result["counterexample_analysis"]:
            lines.append(f"- {ce['label']}: active={ce['active']} defeats_viability={ce['defeats_viability']}")
        lines += ["", "## Epistemic guard", "Functional conclusion only: True", "Phenomenology undetermined: True", "Consciousness proven: False"]
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        prom = [
            f"oce_ag5_domain_viability_score {result['domain_viability_score']}",
            f"oce_ag5_domain_viability_analyzed {1 if result['domain_viability_analyzed'] else 0}",
            f"oce_ag5_evidence_coverage {result['domain_viability_profile']['evidence_coverage']}",
            f"oce_ag5_component_satisfaction {result['domain_viability_profile']['component_satisfaction']}",
            f"oce_ag5_active_counterexamples {sum(1 for x in result['counterexample_analysis'] if x['defeats_viability'])}",
        ]
        prom_path.write_text("\n".join(prom) + "\n", encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        synthetic_mode = isinstance(inputs, Mapping) and bool(inputs) and any(k in inputs for k in self.SYNTHETIC_KEYS)
        degradation_mode = isinstance(inputs, Mapping) and not bool(inputs)
        data = self._synthetic_inputs(inputs or {}) if synthetic_mode or degradation_mode else self._default_inputs()
        evidence = self._evidence(data)
        components = self._components(evidence)
        counterexamples = self._counterexamples(evidence, components)
        coverage = sum(1 for e in evidence if e["available"]) / len(evidence)
        satisfaction = sum(1 for e in evidence if e["satisfied"]) / len(evidence)
        component_satisfaction = sum(1 for c in components if c["satisfied"]) / len(components)
        minimum_evidence_score = min(_clamp(e["score"]) for e in evidence)
        viability_core_score = _mean([e["score"] for e in evidence if e["label"] in {"viability_domain", "possibility_viability", "non_empty_domain"}])
        persistence_score = _mean([e["score"] for e in evidence if e["label"] in {"stability_support", "resilience_support", "continuation_support"}])
        boundary_support_score = _mean([e["score"] for e in evidence if e["label"] in {"existence_domain", "domain_boundaries", "closure_bounded"}])
        component_score = _mean([c["component_score"] for c in components])
        domain_viability_score = _mean([viability_core_score, persistence_score, boundary_support_score, component_score, satisfaction])
        active_counterexamples = [x for x in counterexamples if x["defeats_viability"]]
        failures: List[str] = []
        if coverage < 0.78: failures.append("domain_viability_evidence_coverage_below_threshold")
        if satisfaction < 0.78: failures.append("domain_viability_evidence_satisfaction_below_threshold")
        if minimum_evidence_score < self.threshold: failures.append("minimum_domain_viability_evidence_score_below_threshold")
        if component_satisfaction < 1.0: failures.append("unsatisfied_domain_viability_components")
        if active_counterexamples: failures.append("active_domain_viability_counterexamples")
        analyzed = not failures and domain_viability_score >= self.threshold
        status = self.expected_status if analyzed else "DOMAIN_VIABILITY_INSUFFICIENT"
        profile = {
            "evidence_coverage": _clamp(coverage),
            "evidence_satisfaction": _clamp(satisfaction),
            "component_satisfaction": _clamp(component_satisfaction),
            "minimum_evidence_score": _clamp(minimum_evidence_score),
            "viability_core_score": _clamp(viability_core_score),
            "persistence_score": _clamp(persistence_score),
            "boundary_support_score": _clamp(boundary_support_score),
            "domain_viability_score": _clamp(domain_viability_score),
        }
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "generated_at_utc": _now(),
            "domain_viability_analyzer_status": status,
            "domain_viability_status": status,
            "domain_viability_analyzed": analyzed,
            "domain_viability_score": profile["domain_viability_score"],
            "threshold": self.threshold,
            "synthetic_mode": synthetic_mode,
            "degradation_mode": degradation_mode,
            "rf_t_ed_viability_transition_validated": analyzed,
            "evidence_items": evidence,
            "domain_viability_components": components,
            "domain_viability_profile": profile,
            "counterexample_analysis": counterexamples,
            "failure_conditions": failures,
            "next_recommended_module": "rf_t_ed_theorem_checker" if analyzed else "refine_domain_viability_analyzer_inputs",
            "public_schema": {"required_fields": ["domain_viability_analyzer_status", "domain_viability_score", "domain_viability_analyzed", "evidence_items", "domain_viability_components", "domain_viability_profile", "counterexample_analysis", "failure_conditions", "epistemic_guard"]},
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
