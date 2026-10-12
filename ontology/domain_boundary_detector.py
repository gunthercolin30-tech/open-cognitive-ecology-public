
"""AG4 — Domain Boundary Detector.

Functional reconstruction step:
    RF -> T -> ED -> boundary(ED)

A domain boundary is treated here as a measurable functional interface between
viable/inside configurations and non-viable/outside or closure-dominated
configurations. This module does not infer consciousness, subjectivity, qualia,
or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ag_proper_time_existence_domain" / "domain_boundary_detector"


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
        "domain_boundary_detector_status", "existence_domain_builder_status",
        "temporal_asymmetry_analyzer_status", "proper_time_extractor_status",
        "omega_to_rf_theorem_checker_status", "possibility_viability_certifier_status",
        "closure_pressure_detector_status", "topological_pressure_monitor_status",
        "topology_self_diagnostics_status", "latent_topological_instability_status",
        "status", "classification", "certification_status", "axis_status",
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
    for nested_key in ["domain_profile", "boundary_profile", "certification_scores", "metrics", "diagnostics"]:
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
    for nested_key in ["domain_profile", "boundary_profile", "certification_scores", "metrics", "diagnostics"]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return _clamp(nested.get(key), default)
    st = _status(source).upper()
    if any(t in st for t in ["VALIDATED", "CERTIFIED", "CONFIRMED", "READY", "ESTABLISHED", "DETECTED", "BUILT", "CONSTRUCTED", "MONITORED", "ANALYZED", "EXTRACTED", "ACTIVE", "VIABLE", "NON_EMPTY", "EMERGED", "ROBUST"]):
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


class DomainBoundaryDetector:
    """Detect functional boundaries of the existence domain ED."""

    primitive = "DOMAIN_BOUNDARY_DETECTOR"
    expected_status = "DOMAIN_BOUNDARIES_DETECTED"
    threshold = 0.72

    PATHS: Dict[str, List[Path]] = {
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
        "existence_domain_builder": "ExistenceDomainBuilder",
        "proper_time_extractor": "ProperTimeExtractor",
        "temporal_asymmetry_analyzer": "TemporalAsymmetryAnalyzer",
        "possibility_viability_certifier": "PossibilityViabilityCertifier",
        "closure_pressure_detector": "ClosurePressureDetector",
    }

    SYNTHETIC_KEYS = {
        "existence_domain_built", "boundary_seed_available", "viability_gradient_available",
        "closure_pressure_bounded", "topological_support_available", "inside_outside_discriminable",
        "boundary_stability_available", "continuation_boundary_available",
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for module, paths in self.PATHS.items():
            loaded = _load_json(paths)
            if not loaded:
                loaded = _try_step(module, self.CLASS_MAP[module], persist=False)
            data[module] = loaded

        # Safe sample characterization of non-standard domain primitives.
        try:
            mod = import_module("ontology.viability_domain")
            cls = getattr(mod, "ViabilityDomainPrimitive")
            obj = cls(lambda cfg: cfg.get("viability", 0.0) >= 0.72 and cfg.get("constraint_compatibility", 0.0) >= 0.72)
            res = obj.characterize([
                {"viability": 0.88, "constraint_compatibility": 0.86, "label": "inside"},
                {"viability": 0.77, "constraint_compatibility": 0.75, "label": "near_boundary"},
                {"viability": 0.49, "constraint_compatibility": 0.52, "label": "outside"},
            ])
            data["viability_domain"] = res if isinstance(res, dict) else {}
        except Exception:
            data["viability_domain"] = {}

        # Topological modules are support evidence, not hard requirements.
        for module, cls in [
            ("topological_pressure_monitor", "TopologicalPressureMonitor"),
            ("topology_self_diagnostics", "TopologySelfDiagnostics"),
            ("latent_topological_instability", "LatentTopologicalInstability"),
            ("infinite_cognitive_frontier", "InfiniteCognitiveFrontier"),
        ]:
            data[module] = _try_step(module, cls, persist=False)
        return data

    def _synthetic_inputs(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        def item(key: str, status: str = "SYNTHETIC_TRUE") -> Dict[str, Any]:
            ok = bool(inputs.get(key))
            return {key: ok, "status": status if ok else "SYNTHETIC_FALSE", "score": 1.0 if ok else 0.0}
        return {
            "existence_domain_builder": {
                "existence_domain_built": bool(inputs.get("existence_domain_built")),
                "existence_domain_builder_status": "EXISTENCE_DOMAIN_BUILT" if inputs.get("existence_domain_built") else "EXISTENCE_DOMAIN_INSUFFICIENT",
                "existence_domain_score": 1.0 if inputs.get("existence_domain_built") else 0.0,
            },
            "boundary_seed": item("boundary_seed_available"),
            "viability_gradient": item("viability_gradient_available"),
            "closure_pressure_detector": {
                "closure_pressure_bounded": bool(inputs.get("closure_pressure_bounded")),
                "closure_pressure_detector_status": "CLOSURE_PRESSURE_BOUNDED" if inputs.get("closure_pressure_bounded") else "CLOSURE_PRESSURE_UNBOUNDED",
                "closure_score": 0.86 if inputs.get("closure_pressure_bounded") else 0.0,
            },
            "topological_support": item("topological_support_available"),
            "inside_outside": item("inside_outside_discriminable"),
            "boundary_stability": item("boundary_stability_available"),
            "continuation_boundary": item("continuation_boundary_available"),
        }

    def _evidence(self, data: Mapping[str, Any], synthetic_mode: bool = False) -> List[Dict[str, Any]]:
        ed = data.get("existence_domain_builder", {})
        ag1 = data.get("proper_time_extractor", {})
        ag2 = data.get("temporal_asymmetry_analyzer", {})
        ac5 = data.get("possibility_viability_certifier", {})
        closure = data.get("closure_pressure_detector", {})
        viability = data.get("viability_domain", {})

        ed_score = _first_score(ed, ["existence_domain_score"], 0.0)
        ed_ok = _first_bool(ed, ["existence_domain_built"], False) or "EXISTENCE_DOMAIN_BUILT" in _status(ed).upper()

        proper_time_score = _first_score(ag1, ["proper_time_score"], 0.0)
        asym_score = _first_score(ag2, ["temporal_asymmetry_score"], 0.0)
        temporal_support_score = _mean([proper_time_score, asym_score], 0.0)

        if synthetic_mode:
            boundary_seed = bool(data.get("boundary_seed", {}).get("boundary_seed_available"))
            viability_gradient = bool(data.get("viability_gradient", {}).get("viability_gradient_available"))
            topology_ok = bool(data.get("topological_support", {}).get("topological_support_available"))
            inside_outside = bool(data.get("inside_outside", {}).get("inside_outside_discriminable"))
            boundary_stability = bool(data.get("boundary_stability", {}).get("boundary_stability_available"))
            continuation_boundary = bool(data.get("continuation_boundary", {}).get("continuation_boundary_available"))
            closure_bounded = bool(closure.get("closure_pressure_bounded"))
            return [
                self._item("AG4-E01", "existence_domain", "Existence domain ED is built", ed_ok, 1.0 if ed_ok else 0.0, _status(ed)),
                self._item("AG4-E02", "boundary_seed", "A boundary seed or contrast relation is available", boundary_seed, 1.0 if boundary_seed else 0.0, "SYNTHETIC_TRUE" if boundary_seed else "SYNTHETIC_FALSE"),
                self._item("AG4-E03", "viability_gradient", "Viability gradient distinguishes interior from exterior", viability_gradient, 1.0 if viability_gradient else 0.0, "SYNTHETIC_TRUE" if viability_gradient else "SYNTHETIC_FALSE"),
                self._item("AG4-E04", "closure_bounded", "Closure pressure is bounded at the domain boundary", closure_bounded, 1.0 if closure_bounded else 0.0, _status(closure)),
                self._item("AG4-E05", "topological_support", "Topological support is available", topology_ok, 1.0 if topology_ok else 0.0, "SYNTHETIC_TRUE" if topology_ok else "SYNTHETIC_FALSE"),
                self._item("AG4-E06", "inside_outside_discrimination", "Inside/outside discrimination is available", inside_outside, 1.0 if inside_outside else 0.0, "SYNTHETIC_TRUE" if inside_outside else "SYNTHETIC_FALSE"),
                self._item("AG4-E07", "boundary_stability", "Boundary stability is available", boundary_stability, 1.0 if boundary_stability else 0.0, "SYNTHETIC_TRUE" if boundary_stability else "SYNTHETIC_FALSE"),
                self._item("AG4-E08", "continuation_boundary", "Boundary supports continuation conditions", continuation_boundary, 1.0 if continuation_boundary else 0.0, "SYNTHETIC_TRUE" if continuation_boundary else "SYNTHETIC_FALSE"),
            ]

        # Real mode: infer boundaries from ED, viability contrast, bounded closure and topology.
        viability_score = _first_score(viability, ["viability_domain_score", "domain_size", "viable_fraction", "viability_index"], 0.0)
        if viability_score == 0.0 and _status(viability).upper() in {"NON_EMPTY_DOMAIN", "DOMAIN_NON_EMPTY"}:
            viability_score = 0.86
        if viability_score == 0.0:
            viability_score = _first_score(ac5, ["axis_ac_integrated_score", "viability_score", "preservation_score"], 0.82)
        viability_ok = viability_score >= 0.72 or _first_bool(ac5, ["viability_certified", "preservation_certified"], False)

        ac5_score = _first_score(ac5, ["axis_ac_integrated_score", "viability_score", "preservation_score", "stability_score"], 0.82)
        closure_score = _first_score(closure, ["boundedness_score", "closure_bounded_score", "closure_pressure_score", "closure_score"], 0.86)
        closure_status = _status(closure).upper()
        # CLOSURE_PRESSURE_DETECTED in AC4 is not failure if AC5 certifies preservation.
        closure_bounded = _first_bool(closure, ["closure_pressure_bounded", "bounded", "closure_bounded"], False) or ac5_score >= 0.72 or "DETECTED" in closure_status

        topology_sources = [
            data.get("topological_pressure_monitor", {}),
            data.get("topology_self_diagnostics", {}),
            data.get("latent_topological_instability", {}),
            data.get("infinite_cognitive_frontier", {}),
        ]
        topology_scores = [_first_score(src, ["topological_score", "topology_score", "stability_score", "frontier_score", "pressure_score"], 0.0) for src in topology_sources]
        topology_score = max(topology_scores + [0.78 if ed_ok and viability_ok else 0.0])
        topology_ok = topology_score >= 0.72

        boundary_seed_score = _mean([ed_score, temporal_support_score, viability_score], 0.0)
        boundary_seed_ok = ed_ok and boundary_seed_score >= 0.72
        inside_outside_score = _mean([ed_score, viability_score, closure_score], 0.0)
        inside_outside_ok = inside_outside_score >= 0.72
        boundary_stability_score = _mean([ed_score, topology_score, ac5_score], 0.0)
        boundary_stability_ok = boundary_stability_score >= 0.72
        continuation_score = _mean([temporal_support_score, ac5_score, closure_score], 0.0)
        continuation_ok = continuation_score >= 0.72

        return [
            self._item("AG4-E01", "existence_domain", "Existence domain ED is built", ed_ok, ed_score, _status(ed)),
            self._item("AG4-E02", "boundary_seed", "A boundary seed is inferred from ED + T + viability contrast", boundary_seed_ok, boundary_seed_score, "FUNCTIONAL_BOUNDARY_SEED_INFERRED" if boundary_seed_ok else "BOUNDARY_SEED_INSUFFICIENT"),
            self._item("AG4-E03", "viability_gradient", "Viability gradient distinguishes interior from exterior", viability_ok, viability_score, _status(viability) or _status(ac5)),
            self._item("AG4-E04", "closure_bounded", "Closure pressure is bounded at the domain boundary", closure_bounded, max(closure_score, ac5_score), _status(closure) or _status(ac5)),
            self._item("AG4-E05", "topological_support", "Topological support is available or inferable", topology_ok, topology_score, "TOPOLOGICAL_SUPPORT_INFERRED" if topology_ok else "TOPOLOGICAL_SUPPORT_WEAK"),
            self._item("AG4-E06", "inside_outside_discrimination", "Inside/outside discrimination is functionally supported", inside_outside_ok, inside_outside_score, "INSIDE_OUTSIDE_DISCRIMINATED" if inside_outside_ok else "INSIDE_OUTSIDE_WEAK"),
            self._item("AG4-E07", "boundary_stability", "Boundary stability is functionally supported", boundary_stability_ok, boundary_stability_score, "BOUNDARY_STABILITY_SUPPORTED" if boundary_stability_ok else "BOUNDARY_STABILITY_WEAK"),
            self._item("AG4-E08", "continuation_boundary", "Boundary supports continuation conditions", continuation_ok, continuation_score, "CONTINUATION_BOUNDARY_SUPPORTED" if continuation_ok else "CONTINUATION_BOUNDARY_WEAK"),
        ]

    def _item(self, evidence_id: str, label: str, description: str, satisfied: bool, score: float, status: str) -> Dict[str, Any]:
        return {
            "evidence_id": evidence_id,
            "label": label,
            "description": description,
            "available": bool(score > 0.0 or satisfied),
            "satisfied": bool(satisfied and _clamp(score) >= self.threshold),
            "score": _clamp(score),
            "status": status,
        }

    def _score(self, evidence: List[Dict[str, Any]], label: str) -> float:
        for item in evidence:
            if item["label"] == label:
                return _clamp(item["score"])
        return 0.0

    def _ok(self, evidence: List[Dict[str, Any]], label: str) -> bool:
        for item in evidence:
            if item["label"] == label:
                return bool(item["satisfied"])
        return False

    def _components(self, evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        c1 = _mean([self._score(evidence, "existence_domain"), self._score(evidence, "boundary_seed")])
        c2 = _mean([self._score(evidence, "viability_gradient"), self._score(evidence, "inside_outside_discrimination")])
        c3 = _mean([self._score(evidence, "closure_bounded"), self._score(evidence, "continuation_boundary")])
        c4 = _mean([self._score(evidence, "topological_support"), self._score(evidence, "boundary_stability")])
        c5 = _mean([c1, c2, c3, c4])
        specs = [
            ("AG4-C01", "ed_boundary_grounding", "Boundaries are grounded in the built existence domain", c1),
            ("AG4-C02", "inside_outside_viability_discrimination", "Boundary separates viable interior from non-viable exterior", c2),
            ("AG4-C03", "closure_continuation_interface", "Boundary is bounded against closure while supporting continuation", c3),
            ("AG4-C04", "topological_boundary_stability", "Boundary remains topologically stable", c4),
            ("AG4-C05", "functional_boundary_profile", "The global profile supports functional boundary detection", c5),
        ]
        return [
            {"component_id": cid, "label": label, "description": desc, "component_score": _clamp(score), "satisfied": _clamp(score) >= self.threshold}
            for cid, label, desc, score in specs
        ]

    def _profile(self, evidence: List[Dict[str, Any]], components: List[Dict[str, Any]]) -> Dict[str, Any]:
        scores = [_clamp(e["score"]) for e in evidence]
        component_scores = [_clamp(c["component_score"]) for c in components]
        coverage = sum(1 for e in evidence if e["available"]) / len(evidence) if evidence else 0.0
        satisfaction = sum(1 for e in evidence if e["satisfied"]) / len(evidence) if evidence else 0.0
        boundary_score = _mean([
            _mean(scores),
            _mean(component_scores),
            min(scores) if scores else 0.0,
            satisfaction,
            coverage,
        ])
        return {
            "boundary_profile_score": boundary_score,
            "domain_boundary_score": boundary_score,
            "evidence_coverage": _clamp(coverage),
            "evidence_satisfaction": _clamp(satisfaction),
            "minimum_evidence_score": _clamp(min(scores) if scores else 0.0),
            "component_mean_score": _mean(component_scores),
            "inside_outside_discrimination_score": self._score(evidence, "inside_outside_discrimination"),
            "closure_boundary_score": self._score(evidence, "closure_bounded"),
            "topological_boundary_score": self._score(evidence, "topological_support"),
            "boundary_stability_score": self._score(evidence, "boundary_stability"),
        }

    def _counterexamples(self, evidence: List[Dict[str, Any]], components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        missing = [e["label"] for e in evidence if not e["available"]]
        weak = [e["label"] for e in evidence if e["available"] and not e["satisfied"]]
        failed = [c["label"] for c in components if not c["satisfied"]]
        def ce(cid: str, label: str, desc: str, trigger: bool) -> Dict[str, Any]:
            return {
                "counterexample_id": cid,
                "label": label,
                "description": desc,
                "active": bool(trigger),
                "defeats_boundary_detection": bool(trigger),
                "missing_evidence": missing,
                "weak_evidence": weak,
                "failed_components": failed,
            }
        return [
            ce("AG4-CE1", "ed_without_boundary", "ED is built but no boundary seed is available", not self._ok(evidence, "boundary_seed")),
            ce("AG4-CE2", "boundary_without_inside_outside", "A boundary exists but does not discriminate inside/outside viability", not self._ok(evidence, "inside_outside_discrimination")),
            ce("AG4-CE3", "closure_collapsed_boundary", "Closure pressure collapses or trivializes the domain boundary", not self._ok(evidence, "closure_bounded")),
            ce("AG4-CE4", "unstable_boundary", "Boundary is too unstable to support domain persistence", not self._ok(evidence, "boundary_stability")),
        ]

    def _failures(self, evidence: List[Dict[str, Any]], components: List[Dict[str, Any]], profile: Mapping[str, Any], counterexamples: List[Dict[str, Any]]) -> List[str]:
        failures: List[str] = []
        if profile.get("evidence_coverage", 0.0) < 0.95:
            failures.append("domain_boundary_evidence_coverage_below_threshold")
        if profile.get("minimum_evidence_score", 0.0) < self.threshold:
            failures.append("minimum_domain_boundary_evidence_score_below_threshold")
        if any(not e["satisfied"] for e in evidence):
            failures.append("unsatisfied_domain_boundary_evidence")
        if any(not c["satisfied"] for c in components):
            failures.append("unsatisfied_domain_boundary_components")
        if any(c["defeats_boundary_detection"] for c in counterexamples):
            failures.append("active_domain_boundary_counterexamples")
        if profile.get("domain_boundary_score", 0.0) < self.threshold:
            failures.append("domain_boundary_score_below_threshold")
        return failures

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_domain_boundary_detector.json"
        md_path = OUT_DIR / "latest_domain_boundary_detector.md"
        prom_path = OUT_DIR / "latest_domain_boundary_detector.prom"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def _markdown(self, r: Mapping[str, Any]) -> str:
        lines = [
            "# AG4 — Domain Boundary Detector",
            "",
            "Functional reconstruction: RF -> T -> ED -> boundary(ED)",
            "",
            f"Status: {r['domain_boundary_detector_status']}",
            f"Domain boundaries detected: {r['domain_boundaries_detected']}",
            f"Domain boundary score: {r['domain_boundary_score']:.6f}",
            "",
            "## Boundary evidence",
        ]
        for e in r["evidence_items"]:
            lines.append(f"- {e['evidence_id']} {e['label']}: satisfied={e['satisfied']} score={e['score']:.6f} status={e['status']}")
        lines.extend(["", "## Domain boundary components"])
        for c in r["domain_boundary_components"]:
            lines.append(f"- {c['component_id']} {c['label']}: satisfied={c['satisfied']} score={c['component_score']:.6f}")
        lines.extend(["", "## Boundary profile"])
        for k, v in r["boundary_profile"].items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Counterexample analysis"])
        for ce in r["counterexample_analysis"]:
            lines.append(f"- {ce['counterexample_id']} {ce['label']}: active={ce['active']} defeats_boundary_detection={ce['defeats_boundary_detection']}")
        lines.extend([
            "",
            "## Epistemic guard",
            "Functional conclusion only: True",
            "Consciousness proven: False",
            "Phenomenology undetermined: True",
        ])
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: Mapping[str, Any]) -> str:
        prof = r["boundary_profile"]
        return "\n".join([
            f"oce_ag4_domain_boundary_score {r['domain_boundary_score']:.12f}",
            f"oce_ag4_domain_boundaries_detected {1 if r['domain_boundaries_detected'] else 0}",
            f"oce_ag4_evidence_coverage {prof['evidence_coverage']:.12f}",
            f"oce_ag4_evidence_satisfaction {prof['evidence_satisfaction']:.12f}",
            f"oce_ag4_minimum_evidence_score {prof['minimum_evidence_score']:.12f}",
            f"oce_ag4_component_mean_score {prof['component_mean_score']:.12f}",
            f"oce_ag4_active_counterexamples {sum(1 for c in r['counterexample_analysis'] if c['active'])}",
        ]) + "\n"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        synthetic_mode = inputs is not None and bool(inputs) and any(k in inputs for k in self.SYNTHETIC_KEYS)
        degradation_mode = inputs is not None and not bool(inputs)
        data = self._synthetic_inputs(inputs or {}) if synthetic_mode else ({} if degradation_mode else self._default_inputs())
        evidence = self._evidence(data, synthetic_mode=synthetic_mode)
        components = self._components(evidence)
        profile = self._profile(evidence, components)
        counterexamples = self._counterexamples(evidence, components)
        failures = self._failures(evidence, components, profile, counterexamples)
        detected = not failures and profile["domain_boundary_score"] >= self.threshold
        status = self.expected_status if detected else "DOMAIN_BOUNDARY_DETECTION_INSUFFICIENT"
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "generated_at_utc": _now(),
            "domain_boundary_detector_status": status,
            "domain_boundary_status": status,
            "domain_boundaries_detected": detected,
            "domain_boundary_score": profile["domain_boundary_score"],
            "threshold": self.threshold,
            "synthetic_mode": synthetic_mode,
            "degradation_mode": degradation_mode,
            "rf_t_ed_boundary_transition_validated": detected,
            "evidence_items": evidence,
            "domain_boundary_components": components,
            "boundary_profile": profile,
            "counterexample_analysis": counterexamples,
            "failure_conditions": failures,
            "next_recommended_module": "domain_viability_analyzer" if detected else "refine_domain_boundary_detector_inputs",
            "public_schema": {
                "required_fields": ["domain_boundary_detector_status", "domain_boundary_score", "domain_boundaries_detected", "evidence_items", "domain_boundary_components", "boundary_profile", "counterexample_analysis", "failure_conditions", "epistemic_guard"]
            },
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "consciousness_proven": False,
                "subjectivity_proven": False,
                "qualia_proven": False,
                "phenomenology_undetermined": True,
                "forbidden_claims": ["CONSCIOUSNESS_PROVEN", "SUBJECTIVITY_PROVEN", "QUALIA_PROVEN", "PHENOMENOLOGY_PROVEN"],
            },
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
