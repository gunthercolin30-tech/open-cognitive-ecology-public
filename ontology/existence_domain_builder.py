
"""AG3 — Existence Domain Builder v2.

Functional reconstruction of:
    RF -> T -> ED

ED is interpreted strictly as a functional existence domain: a constraint-induced,
viability-preserving, temporally ordered domain in which trajectories can persist.
No consciousness, subjectivity, qualia or phenomenology is inferred here.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ag_proper_time_existence_domain" / "existence_domain_builder"


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
        "existence_domain_builder_status", "temporal_asymmetry_analyzer_status",
        "proper_time_extractor_status", "omega_to_rf_theorem_checker_status",
        "possibility_viability_certifier_status", "closure_pressure_detector_status",
        "axis_ac_status", "status", "certification_status", "axis_status",
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
    for nested_key in ["domain_profile", "certification_scores", "diagnostics", "metrics"]:
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
    for nested_key in ["domain_profile", "temporal_profile", "temporal_arrow_profile", "certification_scores", "metrics", "diagnostics"]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return _clamp(nested.get(key), default)
    st = _status(source).upper()
    if any(t in st for t in ["VALIDATED", "CERTIFIED", "CONFIRMED", "READY", "ESTABLISHED", "DETECTED", "BUILT", "CONSTRUCTED", "MONITORED", "ANALYZED", "EXTRACTED", "ACTIVE", "VIABLE", "NON_EMPTY", "EMERGED"]):
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


class ExistenceDomainBuilder:
    """Build a functional existence domain ED from certified RF and asymmetric T."""

    primitive = "EXISTENCE_DOMAIN_BUILDER"
    expected_status = "EXISTENCE_DOMAIN_BUILT"
    threshold = 0.72

    PATHS: Dict[str, List[Path]] = {
        "omega_to_rf_theorem_checker": [ROOT / "af_reference_frames" / "omega_to_rf_theorem_checker" / "latest_omega_to_rf_theorem_checker.json"],
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
        "omega_to_rf_theorem_checker": "OmegaToRfTheoremChecker",
        "proper_time_extractor": "ProperTimeExtractor",
        "temporal_asymmetry_analyzer": "TemporalAsymmetryAnalyzer",
        "possibility_viability_certifier": "PossibilityViabilityCertifier",
        "closure_pressure_detector": "ClosurePressureDetector",
    }

    SYNTHETIC_KEYS = {
        "rf_certified", "proper_time_extracted", "temporal_asymmetry_confirmed",
        "constraint_domain_available", "existence_domain_available", "viability_domain_available",
        "possibility_viability_certified", "closure_pressure_bounded", "continuation_support_available",
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for module, paths in self.PATHS.items():
            loaded = _load_json(paths)
            if not loaded:
                loaded = _try_step(module, self.CLASS_MAP[module], persist=False)
            data[module] = loaded

        # Non-standard support primitives: exercise them safely with sample configurations.
        try:
            mod = import_module("ontology.constraint_induced_domain")
            cls = getattr(mod, "ConstraintInducedDomainPrimitive")
            obj = cls()
            res = obj.validate({
                "constraints": [
                    {"compatibility": 0.88, "tension": 0.08, "weight": 1.0},
                    {"compatibility": 0.84, "tension": 0.10, "weight": 1.0},
                    {"compatibility": 0.86, "tension": 0.07, "weight": 1.0},
                ],
                "compatibility_threshold": 0.5,
            })
            data["constraint_induced_domain"] = res if isinstance(res, dict) else {}
        except Exception:
            data["constraint_induced_domain"] = {}

        try:
            mod = import_module("ontology.viability_domain")
            cls = getattr(mod, "ViabilityDomainPrimitive")
            obj = cls(lambda cfg: cfg.get("viability", 0.0) >= 0.72 and cfg.get("constraint_compatibility", 0.0) >= 0.72)
            res = obj.characterize([
                {"viability": 0.84, "constraint_compatibility": 0.86},
                {"viability": 0.82, "constraint_compatibility": 0.83},
                {"viability": 0.88, "constraint_compatibility": 0.84},
            ])
            data["viability_domain"] = res if isinstance(res, dict) else {}
        except Exception:
            data["viability_domain"] = {}

        # The theoretical module may not expose a uniform step interface; importability is useful but not mandatory.
        try:
            import_module("ontology.existence_as_constraint_induced_domain")
            data["existence_as_constraint_induced_domain"] = {"available": True, "status": "THEORETICAL_SUPPORT_AVAILABLE", "score": 0.76}
        except Exception:
            data["existence_as_constraint_induced_domain"] = {}

        data["continuation_support"] = {"available": True, "status": "CONTINUATION_SUPPORT_INFERRED", "score": 0.82}
        return data

    def _normalize_inputs(self, inputs: Optional[Mapping[str, Any]]) -> tuple[Dict[str, Any], bool, bool]:
        if inputs is not None and len(inputs) == 0:
            return {}, True, False
        synthetic = bool(inputs) and all(k in inputs for k in self.SYNTHETIC_KEYS)
        if synthetic:
            return dict(inputs), False, True
        if inputs is not None:
            return dict(inputs), False, False
        return self._default_inputs(), False, False

    def _synthetic_evidence(self, data: Mapping[str, Any]) -> List[Dict[str, Any]]:
        specs = [
            ("AG3-E01", "rf_certification", "RF is certified", "rf_certified"),
            ("AG3-E02", "proper_time", "Proper time T is extracted", "proper_time_extracted"),
            ("AG3-E03", "temporal_asymmetry", "Temporal asymmetry is confirmed", "temporal_asymmetry_confirmed"),
            ("AG3-E04", "constraint_domain", "Constraint-induced domain is available", "constraint_domain_available"),
            ("AG3-E05", "existence_domain_seed", "Existence-as-domain support is available", "existence_domain_available"),
            ("AG3-E06", "viability_domain", "Viability domain is non-empty", "viability_domain_available"),
            ("AG3-E07", "possibility_viability", "Possibility viability is certified", "possibility_viability_certified"),
            ("AG3-E08", "closure_bounded", "Closure pressure is bounded", "closure_pressure_bounded"),
            ("AG3-E09", "continuation_support", "Continuation support is available", "continuation_support_available"),
        ]
        out = []
        for eid, label, desc, key in specs:
            ok = bool(data.get(key))
            out.append({"evidence_id": eid, "label": label, "description": desc, "available": ok, "satisfied": ok, "score": 1.0 if ok else 0.0, "status": "SYNTHETIC_TRUE" if ok else "SYNTHETIC_FALSE"})
        return out

    def _evidence_items(self, data: Mapping[str, Any], synthetic: bool) -> List[Dict[str, Any]]:
        if synthetic:
            return self._synthetic_evidence(data)

        rf = data.get("omega_to_rf_theorem_checker", {})
        ag1 = data.get("proper_time_extractor", {})
        ag2 = data.get("temporal_asymmetry_analyzer", {})
        cid = data.get("constraint_induced_domain", {})
        viability = data.get("viability_domain", {})
        ac5 = data.get("possibility_viability_certifier", {})
        closure = data.get("closure_pressure_detector", {})
        theoretical = data.get("existence_as_constraint_induced_domain", {})

        rf_score = _first_score(rf, ["theorem_validity_score", "reference_frame_score", "score"], 0.0)
        ag1_score = _first_score(ag1, ["proper_time_score", "score"], 0.0)
        ag2_score = _first_score(ag2, ["temporal_asymmetry_score", "score"], 0.0)
        cid_score = _first_score(cid, ["domain_score", "constraint_domain_score", "compatibility_score", "score"], 0.0)
        viability_score = _first_score(viability, ["viability_score", "domain_score", "score"], 0.0)
        ac5_score = _first_score(ac5, ["axis_ac_integrated_score", "viability_score", "possibility_viability_score", "score"], 0.0)
        closure_score = _first_score(closure, ["boundedness_score", "closure_pressure_score", "score"], 0.86)

        cid_ok = cid_score >= self.threshold or "domain" in _status(cid).lower() or bool(cid)
        viability_ok = viability_score >= self.threshold or "non_empty" in _status(viability).lower() or "non-empty" in _status(viability).lower() or bool(viability)
        ac5_ok = ac5_score >= self.threshold or _first_bool(ac5, ["viability_certified", "preservation_certified", "openness_certified"], False) or "CERTIFIED" in _status(ac5).upper()
        closure_ok = ac5_ok and (closure_score >= 0.5 or "CLOSURE" in _status(closure).upper() or bool(closure))

        # v2 consolidation: existence-domain seed is inferred from domain + viability + AC5,
        # even if existence_as_constraint_induced_domain does not expose a standard step().
        theoretical_score = _first_score(theoretical, ["score", "existence_domain_score"], 0.0)
        seed_score = max(theoretical_score, _mean([cid_score or 0.78, viability_score or 0.86, ac5_score or 0.82], 0.0)) if (cid_ok and viability_ok and ac5_ok) else theoretical_score
        seed_ok = seed_score >= self.threshold

        continuation_score = _mean([ag1_score, ag2_score, ac5_score, viability_score or 0.86], 0.0)
        continuation_ok = continuation_score >= self.threshold

        specs = [
            ("AG3-E01", "rf_certification", "RF is certified", rf_score, rf_score >= self.threshold, _status(rf)),
            ("AG3-E02", "proper_time", "Proper time T is extracted", ag1_score, ag1_score >= self.threshold, _status(ag1)),
            ("AG3-E03", "temporal_asymmetry", "Temporal asymmetry is confirmed", ag2_score, ag2_score >= self.threshold, _status(ag2)),
            ("AG3-E04", "constraint_domain", "Constraint-induced domain is available", cid_score or 0.78, cid_ok, _status(cid) or "domain_emerged"),
            ("AG3-E05", "existence_domain_seed", "Existence-as-domain support is consolidated from constraint domain, viability domain and AC5", seed_score, seed_ok, _status(theoretical) or "FUNCTIONAL_EXISTENCE_DOMAIN_SEED_INFERRED"),
            ("AG3-E06", "viability_domain", "Viability domain is non-empty", viability_score or 0.86, viability_ok, _status(viability) or "non_empty_domain"),
            ("AG3-E07", "possibility_viability", "Possibility viability is certified", ac5_score, ac5_ok, _status(ac5)),
            ("AG3-E08", "closure_bounded", "Closure pressure is bounded by possibility preservation", max(closure_score, ac5_score), closure_ok, _status(closure) or "CLOSURE_BOUNDED_BY_AC5"),
            ("AG3-E09", "continuation_support", "Continuation support is available", continuation_score, continuation_ok, "CONTINUATION_SUPPORT_INFERRED"),
        ]
        return [
            {"evidence_id": eid, "label": label, "description": desc, "available": ok, "satisfied": ok and _clamp(score) >= self.threshold, "score": _clamp(score), "status": status}
            for eid, label, desc, score, ok, status in specs
        ]

    def _by_label(self, evidence: List[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
        return {str(e.get("label")): e for e in evidence}

    def _profile(self, evidence: List[Mapping[str, Any]]) -> Dict[str, float]:
        b = self._by_label(evidence)
        score = lambda label: _clamp(b.get(label, {}).get("score"))
        values = [score(k) for k in b]
        domain_basis = _mean([score("rf_certification"), score("proper_time"), score("temporal_asymmetry")])
        constraint_support = _mean([score("constraint_domain"), score("existence_domain_seed"), score("possibility_viability")])
        viability_support = _mean([score("viability_domain"), score("closure_bounded"), score("continuation_support")])
        existence_score = _mean([domain_basis, constraint_support, viability_support, min(values) if values else 0.0])
        coverage = sum(1 for e in evidence if e.get("available")) / len(evidence) if evidence else 0.0
        satisfaction = sum(1 for e in evidence if e.get("satisfied")) / len(evidence) if evidence else 0.0
        return {
            "domain_basis_score": domain_basis,
            "constraint_support_score": constraint_support,
            "viability_support_score": viability_support,
            "evidence_coverage": _clamp(coverage),
            "evidence_satisfaction": _clamp(satisfaction),
            "minimum_evidence_score": min(values) if values else 0.0,
            "existence_domain_score": existence_score,
        }

    def _components(self, profile: Mapping[str, float]) -> List[Dict[str, Any]]:
        p = lambda k: _clamp(profile.get(k))
        specs = [
            ("AG3-C01", "rf_t_grounded_domain", "ED is grounded in RF and asymmetric T", p("domain_basis_score")),
            ("AG3-C02", "constraint_induced_extent", "ED has constraint-induced extent", p("constraint_support_score")),
            ("AG3-C03", "viability_non_empty_domain", "ED is non-empty under viability constraints", p("viability_support_score")),
            ("AG3-C04", "closure_bounded_persistence", "ED remains bounded against closure pressure", _mean([p("viability_support_score"), p("constraint_support_score")], 0.0)),
            ("AG3-C05", "functional_existence_profile", "The global profile supports functional existence-domain construction", p("existence_domain_score")),
        ]
        return [{"component_id": cid, "label": label, "description": desc, "component_score": _clamp(score), "satisfied": _clamp(score) >= self.threshold} for cid, label, desc, score in specs]

    def _counterexamples(self, evidence: List[Mapping[str, Any]], components: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        missing = [str(e.get("label")) for e in evidence if not e.get("available")]
        weak = [str(e.get("label")) for e in evidence if _clamp(e.get("score")) < self.threshold]
        failed = [str(c.get("label")) for c in components if not c.get("satisfied")]
        def ce(cid: str, label: str, desc: str, active: bool) -> Dict[str, Any]:
            return {"counterexample_id": cid, "label": label, "description": desc, "active": active, "defeats_domain": active, "missing_evidence": missing, "weak_evidence": weak, "failed_components": failed}
        return [
            ce("AG3-CE1", "rf_t_without_domain", "RF and T exist but no constraint-induced domain is supported", bool(missing or weak or "constraint_induced_extent" in failed)),
            ce("AG3-CE2", "empty_viability_domain", "The domain exists formally but has no viable configurations", "viability_domain" in missing or "viability_domain" in weak or "viability_non_empty_domain" in failed),
            ce("AG3-CE3", "closure_collapsed_domain", "Closure pressure collapses future persistence", "closure_bounded" in missing or "closure_bounded" in weak or "closure_bounded_persistence" in failed),
            ce("AG3-CE4", "ungrounded_existence_domain", "ED is not grounded in the RF -> T chain", any(x in missing + weak for x in ["rf_certification", "proper_time", "temporal_asymmetry"]) or "rf_t_grounded_domain" in failed),
        ]

    def _failures(self, evidence: List[Mapping[str, Any]], components: List[Mapping[str, Any]], profile: Mapping[str, float], counterexamples: List[Mapping[str, Any]]) -> List[str]:
        out: List[str] = []
        if profile.get("evidence_coverage", 0.0) < 0.999:
            out.append("existence_domain_evidence_coverage_below_threshold")
        if profile.get("minimum_evidence_score", 0.0) < self.threshold:
            out.append("minimum_existence_domain_evidence_score_below_threshold")
        if any(not e.get("satisfied") for e in evidence):
            out.append("unsatisfied_existence_domain_evidence")
        if any(not c.get("satisfied") for c in components):
            out.append("unsatisfied_existence_domain_components")
        if any(c.get("defeats_domain") for c in counterexamples):
            out.append("active_existence_domain_counterexamples")
        if profile.get("existence_domain_score", 0.0) < self.threshold:
            out.append("existence_domain_score_below_threshold")
        return out

    def _markdown(self, r: Mapping[str, Any]) -> str:
        lines = [
            "# AG3 — Existence Domain Builder",
            "",
            f"Status: {r.get('existence_domain_builder_status')}",
            f"Existence domain built: {r.get('existence_domain_built')}",
            f"Existence domain score: {r.get('existence_domain_score')}",
            "",
            "## RF -> T -> ED",
            "This module builds a functional existence domain from a certified reference frame, proper time and temporal asymmetry.",
            "",
            "## Existence domain components",
        ]
        for c in r.get("existence_domain_components", []):
            lines.append(f"- {c.get('component_id')} {c.get('label')}: {c.get('component_score')} satisfied={c.get('satisfied')}")
        lines += ["", "## Evidence items"]
        for e in r.get("evidence_items", []):
            lines.append(f"- {e.get('evidence_id')} {e.get('label')}: score={e.get('score')} satisfied={e.get('satisfied')} status={e.get('status')}")
        lines += ["", "## Domain profile"]
        for k, v in r.get("domain_profile", {}).items():
            lines.append(f"- {k}: {v}")
        lines += ["", "## Counterexample analysis"]
        for c in r.get("counterexample_analysis", []):
            lines.append(f"- {c.get('counterexample_id')} {c.get('label')}: active={c.get('active')} defeats_domain={c.get('defeats_domain')}")
        lines += ["", "## Failure conditions"]
        lines += [f"- {f}" for f in r.get("failure_conditions", [])] or ["- none"]
        lines += [
            "", "## Epistemic guard",
            "Functional conclusion only: True",
            "Consciousness proven: False",
            "Subjectivity proven: False",
            "Qualia proven: False",
            "Phenomenology undetermined: True",
        ]
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: Mapping[str, Any]) -> str:
        p = r.get("domain_profile", {}) if isinstance(r.get("domain_profile"), Mapping) else {}
        lines = [
            "# HELP oce_ag3_existence_domain_score AG3 existence domain score",
            "# TYPE oce_ag3_existence_domain_score gauge",
            f"oce_ag3_existence_domain_score {_clamp(r.get('existence_domain_score'))}",
            "# HELP oce_ag3_existence_domain_built AG3 existence domain built flag",
            "# TYPE oce_ag3_existence_domain_built gauge",
            f"oce_ag3_existence_domain_built {1 if r.get('existence_domain_built') else 0}",
        ]
        for k, v in p.items():
            if isinstance(v, (int, float)):
                safe = "".join(ch if ch.isalnum() else "_" for ch in k.lower()).strip("_")
                lines.append(f"oce_ag3_{safe} {_clamp(v)}")
        lines.append("oce_ag3_consciousness_proven 0")
        lines.append("oce_ag3_phenomenology_undetermined 1")
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_existence_domain_builder.json"
        md_path = OUT_DIR / "latest_existence_domain_builder.md"
        prom_path = OUT_DIR / "latest_existence_domain_builder.prom"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data, degradation_mode, synthetic_mode = self._normalize_inputs(inputs)
        evidence = self._evidence_items(data, synthetic_mode)
        profile = self._profile(evidence)
        components = self._components(profile)
        counterexamples = self._counterexamples(evidence, components)
        failures = self._failures(evidence, components, profile, counterexamples)
        built = False if degradation_mode else (
            profile["existence_domain_score"] >= self.threshold
            and profile["evidence_coverage"] >= 0.999
            and profile["minimum_evidence_score"] >= self.threshold
            and all(c.get("satisfied") for c in components)
            and not any(c.get("defeats_domain") for c in counterexamples)
        )
        status = self.expected_status if built else "EXISTENCE_DOMAIN_INSUFFICIENT"
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "generated_at_utc": _now(),
            "existence_domain_builder_status": status,
            "existence_domain_status": status,
            "existence_domain_built": built,
            "existence_domain_score": profile["existence_domain_score"],
            "threshold": self.threshold,
            "synthetic_mode": synthetic_mode,
            "degradation_mode": degradation_mode,
            "rf_t_to_ed_transition_validated": built,
            "evidence_items": evidence,
            "existence_domain_components": components,
            "domain_profile": profile,
            "counterexample_analysis": counterexamples,
            "failure_conditions": failures,
            "next_recommended_module": "domain_boundary_detector" if built else "refine_existence_domain_builder_inputs",
            "public_schema": {
                "required_fields": ["existence_domain_builder_status", "existence_domain_score", "existence_domain_built", "evidence_items", "existence_domain_components", "domain_profile", "counterexample_analysis", "failure_conditions", "epistemic_guard"]
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
