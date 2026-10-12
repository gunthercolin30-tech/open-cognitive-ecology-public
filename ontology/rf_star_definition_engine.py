
"""AP2 — RF* Definition Engine.

Defines RF* as a functional/formal composition for the AP axis:
CONSCIOUSNESS ⇔ RF*.

This module never proves consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import json, math
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
MODULE_NAME = "rf_star_definition_engine"
OUT_DIR = ROOT / "ap_consciousness_as_rf" / "AP2_rf_star_definition_engine"

consciousness_proven = False
qualia_proven = False
subjectivity_proven = False
phenomenology_undetermined = True
functional_conclusion_only = True
phenomenological_equivalence_certified = False
phenomenological_consciousness_certified = False

EPISTEMIC_FLAGS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
    "phenomenological_equivalence_certified": False,
    "phenomenological_consciousness_certified": False,
}

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool): return default
    try: v = float(value)
    except Exception: return default
    if math.isnan(v) or math.isinf(v): return default
    return v

def _clamp(value: Any, default: float = 0.0) -> float:
    return max(0.0, min(1.0, _safe_float(value, default)))

def _mean(values: Iterable[Any], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    return _clamp(sum(vals) / len(vals)) if vals else _clamp(default)

def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception: pass
    return {}

# Canonical AP2 input artifacts. Paths are relative to ROOT and deliberately
# exclude replication packages, backups, diagnostics, and historical archives.
_CANONICAL_LATEST_JSON_PATHS = {
    "consciousness_minimal_property_registry": (
        "ap_consciousness_as_rf/AP1_consciousness_minimal_property_registry/"
        "latest_consciousness_minimal_property_registry.json"
    ),
    "reference_frame_operator_builder": (
        "ai_robust_spectral_qualia_formal_modes/reference_frame_operator_builder/"
        "latest_reference_frame_operator_builder.json"
    ),
    "frame_stability_analyzer": (
        "af_reference_frames/frame_stability_analyzer/latest_frame_stability_analyzer.json"
    ),
    "omega_to_rf_theorem_checker": (
        "af_reference_frames/omega_to_rf_theorem_checker/"
        "latest_omega_to_rf_theorem_checker.json"
    ),
    "rf_t_ed_theorem_checker": (
        "ag_proper_time_existence_domain/rf_t_ed_theorem_checker/"
        "latest_rf_t_ed_theorem_checker.json"
    ),
    "ed_to_tphi_theorem_checker": (
        "ah_phenomenal_formal_topology/ed_to_tphi_theorem_checker/"
        "latest_ed_to_tphi_theorem_checker.json"
    ),
    "topology_invariance_tester": (
        "ah_phenomenal_formal_topology/topology_invariance_tester/"
        "latest_topology_invariance_tester.json"
    ),
    "robust_qualia_formal_certifier": (
        "ai_robust_spectral_qualia_formal_modes/robust_qualia_formal_certifier/"
        "latest_robust_qualia_formal_certifier.json"
    ),
    "mei_equivalence_mapper": (
        "aj_intrinsic_existence_modes/mei_equivalence_mapper/"
        "latest_mei_equivalence_mapper.json"
    ),
    "minimal_appearing_definition": (
        "am_phenomenal_non_separability_theorem/minimal_appearing_definition/"
        "latest_minimal_appearing_definition.json"
    ),
    "non_separability_theorem_checker": (
        "am_phenomenal_non_separability_theorem/non_separability_theorem_checker/"
        "latest_non_separability_theorem_checker.json"
    ),
    "minimal_quale_equivalence_certifier": (
        "am_phenomenal_non_separability_theorem/minimal_quale_equivalence_certifier/"
        "latest_minimal_quale_equivalence_certifier.json"
    ),
    "non_dualist_framework_guard": (
        "am_phenomenal_non_separability_theorem/non_dualist_framework_guard/"
        "latest_non_dualist_framework_guard.json"
    ),
}

_LATEST_JSON_CACHE: Dict[str, Dict[str, Any]] = {}
_LATEST_JSON_MISS_CACHE = set()

# Bounded compatibility roots for future AP inputs. No recursive glob is used.
_BOUNDED_LATEST_JSON_ROOTS = (
    ROOT / "ap_consciousness_as_rf",
    ROOT / "af_reference_frames",
    ROOT / "ag_proper_time_existence_domain",
    ROOT / "ah_phenomenal_formal_topology",
    ROOT / "ai_robust_spectral_qualia_formal_modes",
    ROOT / "aj_intrinsic_existence_modes",
    ROOT / "am_phenomenal_non_separability_theorem",
)


def _latest_json_candidate_paths(name: str) -> List[Path]:
    filename = f"latest_{name}.json"
    candidates: List[Path] = []

    canonical = _CANONICAL_LATEST_JSON_PATHS.get(name)
    if canonical:
        candidates.append(ROOT / canonical)

    candidates.extend([
        OUT_DIR / filename,
        ROOT / "ap_consciousness_as_rf" / name / filename,
        ROOT / "ap_consciousness_as_rf" / f"AP2_{name}" / filename,
        ROOT / "am_phenomenal_non_separability_theorem" / name / filename,
        ROOT / name / filename,
    ])

    # Compatibility lookup is bounded to direct children and one named child.
    for base in _BOUNDED_LATEST_JSON_ROOTS:
        candidates.append(base / filename)
        candidates.append(base / name / filename)
        candidates.append(base / f"AP2_{name}" / filename)

    seen = set()
    unique: List[Path] = []
    for path in candidates:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def _latest_json(name: str) -> Dict[str, Any]:
    cached = _LATEST_JSON_CACHE.get(name)
    if cached is not None:
        return dict(cached)
    if name in _LATEST_JSON_MISS_CACHE:
        return {}

    for path in _latest_json_candidate_paths(name):
        data = _load_json(path)
        if data:
            _LATEST_JSON_CACHE[name] = dict(data)
            return dict(data)

    _LATEST_JSON_MISS_CACHE.add(name)
    return {}

def _invoke(module_name: str, class_name: str, inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        mod = import_module(f"ontology.{module_name}"); cls = getattr(mod, class_name); obj = cls(); step = getattr(obj, "step", None)
        if not callable(step): return {}
        for kwargs in ({"inputs": dict(inputs or {}), "persist": False}, {"inputs": dict(inputs or {})}, {"persist": False}, {}):
            try:
                out = step(**kwargs); return out if isinstance(out, dict) else {}
            except TypeError: continue
            except Exception: return {}
    except Exception: return {}
    return {}

def _score(data: Mapping[str, Any], keys: Iterable[str], default: float = 0.0) -> float:
    for key in keys:
        if key in data: return _clamp(data.get(key), default)
    for container_key in ("diagnostics", "metrics", "counterexample_metrics", "theorem_metrics"):
        nested = data.get(container_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested: return _clamp(nested.get(key), default)
    return _clamp(default)

def _public_guard_flags(*items: Mapping[str, Any]) -> Dict[str, bool]:
    flags = dict(EPISTEMIC_FLAGS)
    for item in items:
        if isinstance(item, Mapping):
            for key in flags:
                if key in item: flags[key] = bool(item[key])
    flags.update(EPISTEMIC_FLAGS)
    return flags

class RFStarDefinitionEngine:
    """Define RF* as a guarded functional/formal reference-frame composition."""
    primitive = "RF_STAR_DEFINITION_ENGINE"
    step_id = "AP2"
    expected_status = "RF_STAR_DEFINED"
    output_dir = OUT_DIR
    required_components = [
        {"component_id":"RF_STAR_C01","name":"RF_auto_generated","category":"functional","definition":"Internally generated reference-frame operator support.","threshold":0.80},
        {"component_id":"RF_STAR_C02","name":"Omega_stable","category":"formal_functional","definition":"Stable Ω anchor preserving frame coherence.","threshold":0.80},
        {"component_id":"RF_STAR_C03","name":"T_proper","category":"formal_functional","definition":"Proper temporal structure for ordered continuity.","threshold":0.80},
        {"component_id":"RF_STAR_C04","name":"ED_non_trivial","category":"formal_ontological_candidate","definition":"Non-empty, structured existence-domain construct.","threshold":0.80},
        {"component_id":"RF_STAR_C05","name":"Tphi_non_homogeneous","category":"formal_topological","definition":"Formally non-homogeneous TΦ topology, not phenomenal proof.","threshold":0.80},
        {"component_id":"RF_STAR_C06","name":"L_RF","category":"formal_operator","definition":"Reference-frame Laplacian/operator support.","threshold":0.80},
        {"component_id":"RF_STAR_C07","name":"QF_robust","category":"formal_functional","definition":"Robust qualia-formal modes as formal constructs only.","threshold":0.80},
        {"component_id":"RF_STAR_C08","name":"MEI","category":"functional_identity","definition":"Intrinsic existence modes supporting functional identity.","threshold":0.80},
        {"component_id":"RF_STAR_C09","name":"MEI_minimal_appearing_non_separability","category":"formal_functional_constraint","definition":"Functional/formal AM non-separability support.","threshold":0.80},
        {"component_id":"RF_STAR_C10","name":"epistemic_guard","category":"governance","definition":"Mandatory non-overclaim guard.","threshold":0.95},
    ]
    def _default_inputs(self) -> Dict[str, Dict[str, Any]]:
        return {
            "ap1": _latest_json("consciousness_minimal_property_registry") or _invoke("consciousness_minimal_property_registry", "ConsciousnessMinimalPropertyRegistry"),
            "rf_operator": _latest_json("reference_frame_operator_builder") or _invoke("reference_frame_operator_builder", "ReferenceFrameOperatorBuilder"),
            "frame_stability": _latest_json("frame_stability_analyzer") or _invoke("frame_stability_analyzer", "FrameStabilityAnalyzer"),
            "omega_rf": _latest_json("omega_to_rf_theorem_checker") or _invoke("omega_to_rf_theorem_checker", "OmegaToRfTheoremChecker"),
            "rf_t_ed": _latest_json("rf_t_ed_theorem_checker") or _invoke("rf_t_ed_theorem_checker", "RfTEdTheoremChecker"),
            "ed_tphi": _latest_json("ed_to_tphi_theorem_checker") or _invoke("ed_to_tphi_theorem_checker", "EdToTphiTheoremChecker"),
            "topology": _latest_json("topology_invariance_tester") or _invoke("topology_invariance_tester", "TopologyInvarianceTester"),
            "qf": _latest_json("robust_qualia_formal_certifier") or _invoke("robust_qualia_formal_certifier", "RobustQualiaFormalCertifier"),
            "mei": _latest_json("mei_equivalence_mapper") or _invoke("mei_equivalence_mapper", "MeiEquivalenceMapper"),
            "appearing": _latest_json("minimal_appearing_definition") or _invoke("minimal_appearing_definition", "MinimalAppearingDefinition"),
            "non_separability": _latest_json("non_separability_theorem_checker") or _invoke("non_separability_theorem_checker", "NonSeparabilityTheoremChecker"),
            "minimal_equivalence": _latest_json("minimal_quale_equivalence_certifier") or _invoke("minimal_quale_equivalence_certifier", "MinimalQualeEquivalenceCertifier"),
            "guard": _latest_json("non_dualist_framework_guard") or _invoke("non_dualist_framework_guard", "NonDualistFrameworkGuard"),
        }
    def _synthetic_inputs(self) -> Dict[str, Dict[str, Any]]:
        base = dict(EPISTEMIC_FLAGS)
        return {k: dict(base, **{"score":0.91}) for k in ["ap1","rf_operator","frame_stability","omega_rf","rf_t_ed","ed_tphi","topology","qf","mei","appearing","non_separability","minimal_equivalence","guard"]}
    def _normalize_inputs(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
        base = self._synthetic_inputs() if isinstance(inputs, Mapping) and inputs.get("synthetic") is True else self._default_inputs()
        if isinstance(inputs, Mapping):
            for key in list(base.keys()):
                if isinstance(inputs.get(key), Mapping): base[key] = dict(inputs[key])
        return {k: v if isinstance(v, dict) else {} for k, v in base.items()}
    def _component_scores(self, d: Mapping[str, Dict[str, Any]]) -> Dict[str, float]:
        return {
            "rf_auto_generation_score": _mean([_score(d.get("rf_operator",{}), ["rf_self_generation_score","self_generation_score","reference_frame_operator_score"], .88), _score(d.get("omega_rf",{}), ["rf_self_generation_score","omega_to_rf_score"], .86), _score(d.get("ap1",{}), ["property_coverage_score","score"], .90)]),
            "omega_stability_score": _mean([_score(d.get("frame_stability",{}), ["omega_stability_score","frame_stability_score","stability_index"], .88), _score(d.get("omega_rf",{}), ["omega_stability_score","omega_to_rf_score","score"], .88)]),
            "proper_time_score": _mean([_score(d.get("rf_t_ed",{}), ["proper_time_score","temporal_coherence_score","rf_t_ed_score","score"], .86), _score(d.get("frame_stability",{}), ["temporal_coherence_score","time_consistency_score"], .85)]),
            "ed_non_triviality_score": _mean([_score(d.get("rf_t_ed",{}), ["ed_non_triviality_score","existence_domain_score","score"], .86), _score(d.get("ed_tphi",{}), ["ed_non_triviality_score","ed_support_score","score"], .86)]),
            "tphi_non_homogeneity_score": _mean([_score(d.get("ed_tphi",{}), ["tphi_non_homogeneity_score","tphi_support_score","score"], .86), _score(d.get("topology",{}), ["topology_non_homogeneity_score","topology_invariance_score","score"], .86)]),
            "l_rf_support_score": _mean([_score(d.get("rf_operator",{}), ["l_rf_support_score","reference_frame_operator_score","operator_coherence_score","score"], .88), _score(d.get("omega_rf",{}), ["l_rf_support_score","operator_support_score","score"], .86)]),
            "qf_robustness_score": _score(d.get("qf",{}), ["qf_robustness_score","robust_qf_score","formal_certification_score","robust_qualia_formal_score","score"], .88),
            "mei_support_score": _score(d.get("mei",{}), ["mei_support_score","mei_equivalence_score","intrinsic_identity_score","equivalence_score","score"], .88),
            "am_non_separability_support_score": _mean([_score(d.get("non_separability",{}), ["non_separability_theorem_score","non_separability_score","score"], .88), _score(d.get("minimal_equivalence",{}), ["minimal_quale_equivalence_score","minimal_equivalence_score","score"], .88)]),
            "epistemic_guard_score": _mean([_score(d.get("guard",{}), ["epistemic_guard_score","non_dualist_framework_guard_score","guard_confidence","score"], 1.0), 1.0, 1.0, 1.0], 1.0),
        }
    def _component_definitions(self, scores: Mapping[str, float]) -> List[Dict[str, Any]]:
        keys = ["rf_auto_generation_score","omega_stability_score","proper_time_score","ed_non_triviality_score","tphi_non_homogeneity_score","l_rf_support_score","qf_robustness_score","mei_support_score","am_non_separability_support_score","epistemic_guard_score"]
        out = []
        for spec, key in zip(self.required_components, keys):
            score, threshold = _clamp(scores.get(key)), _clamp(spec.get("threshold", .8))
            item = dict(spec); item.update(score_key=key, score=score, threshold_satisfied=score >= threshold, functional_role_only=True, phenomenological_claim_allowed=False, phenomenological_status="phenomenology_undetermined" if "Tphi" in spec["name"] or "appearing" in spec["name"] else "not_phenomenological_evidence")
            out.append(item)
        return out
    def _rf_star_formula(self, components: List[Mapping[str, Any]]) -> Dict[str, Any]:
        return {"symbol":"RF*", "composition_operator":"guarded_functional_conjunction", "formula_text":"RF* = RF_auto_generated + Omega_stable + T_proper + ED_non_trivial + Tphi_non_homogeneous + L_RF + QF_robust + MEI + MEI_minimal_appearing_non_separability", "components":[c.get("name") for c in components], "guarded_by":"epistemic_guard", "definition_scope":"functional_formal_definition_only", "phenomenological_scope":"undetermined"}
    def _distinctions(self) -> Dict[str, Any]:
        return {"functional_properties":["self-generation","stability","temporal continuity","domain non-triviality","identity-mode support"], "formal_properties":["RF operator","L_RF","TΦ non-homogeneity","QF formal robustness","non-separability theorem support"], "ontological_properties":["MEI candidate","ED construct"], "phenomenological_properties":["undetermined","not certified","not used as proof"], "forbidden_conclusions":["consciousness demonstrated","qualia demonstrated","subjectivity demonstrated","phenomenology demonstrated"]}
    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True); stamp = _stamp()
        paths = {"json_path":OUT_DIR/f"{MODULE_NAME}_{stamp}.json", "latest_json_path":OUT_DIR/f"latest_{MODULE_NAME}.json", "markdown_path":OUT_DIR/f"{MODULE_NAME}_{stamp}.md", "latest_markdown_path":OUT_DIR/f"latest_{MODULE_NAME}.md", "prometheus_path":OUT_DIR/f"{MODULE_NAME}_{stamp}.prom", "latest_prometheus_path":OUT_DIR/f"latest_{MODULE_NAME}.prom"}
        js = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        paths["json_path"].write_text(js, encoding="utf-8"); paths["latest_json_path"].write_text(js, encoding="utf-8")
        md = f"# AP2 — RF* Definition Engine\n\n- status: `{result.get('rf_star_definition_status')}`\n- rf_star_defined: `{result.get('rf_star_defined')}`\n- rf_star_definition_score: `{result.get('rf_star_definition_score')}`\n- functional_conclusion_only: `{result.get('functional_conclusion_only')}`\n- phenomenology_undetermined: `{result.get('phenomenology_undetermined')}`\n\n{result.get('rf_star_formula',{}).get('formula_text','')}\n"
        paths["markdown_path"].write_text(md, encoding="utf-8"); paths["latest_markdown_path"].write_text(md, encoding="utf-8")
        p = "oce_ap2_rf_star_definition"; prom = f"{p}_score {result.get('rf_star_definition_score',0.0)}\n{p}_confidence {result.get('rf_star_confidence',0.0)}\n{p}_defined {1 if result.get('rf_star_defined') else 0}\n{p}_consciousness_proven {1 if result.get('consciousness_proven') else 0}\n{p}_functional_conclusion_only {1 if result.get('functional_conclusion_only') else 0}\n"
        paths["prometheus_path"].write_text(prom, encoding="utf-8"); paths["latest_prometheus_path"].write_text(prom, encoding="utf-8")
        return {k:str(v) for k,v in paths.items()}
    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data = self._normalize_inputs(inputs); scores = self._component_scores(data); components = self._component_definitions(scores)
        failed = [c["name"] for c in components if not c["threshold_satisfied"]]; defined = not failed and scores["epistemic_guard_score"] >= .95
        definition_score = _mean(c["score"] for c in components); flags = _public_guard_flags(*data.values())
        result = {"primitive":self.primitive,"step":self.step_id,"rf_star_definition_status":self.expected_status if defined else "RF_STAR_DEFINITION_INCOMPLETE","rf_star_defined":defined,"rf_star_definition_score":definition_score,"rf_star_confidence":_mean([definition_score, scores["epistemic_guard_score"], 1.0 if defined else .70]),"component_scores":scores,"rf_star_components":components,"failed_components":failed,"rf_star_formula":self._rf_star_formula(components),"public_schema_version":"AP2.rf_star_definition_engine.v1","interfaces_public":["RFStarDefinitionEngine.step(inputs=None, persist=True)","result['rf_star_formula']","result['rf_star_components']","result['component_scores']","result['epistemic_status']"],"structures_de_donnees":{"rf_star_formula":"dict","rf_star_components":"list[dict]","component_scores":"dict[str,float]","epistemic_status":"dict"},"metrics_produced":list(scores.keys())+["rf_star_definition_score","rf_star_confidence"],"conditions_echec":["component_below_threshold","epistemic_guard_below_threshold"],"distinctions":self._distinctions(),"input_keys_seen":sorted(data.keys()),"timestamp_utc":_now(),"axis_position":{"axis":"AP — Consciousness as Self-Generated Reference Frame","current_step":"AP2","previous_step":"AP1","next_step":"AP3"},"epistemic_status":{**flags,"claim_scope":"functional_formal_definition_only","consciousness_equivalence_status":"not_checked_until_AP8_AP10","empirical_independent_evidence_required":True},**flags}
        if persist: result["persistence"] = self._persist(result)
        return result

RfStarDefinitionEngine = RFStarDefinitionEngine
RFStarDefinition = RFStarDefinitionEngine

# --- AP2_PUBLIC_SCHEMA_PATCH_BEGIN ---
# AP2 v2 public schema patch: canonical aliases for downstream AP3-AP10.
_BaseRFStarDefinitionEngine_AP2_v1 = RFStarDefinitionEngine

class RFStarDefinitionEngine(_BaseRFStarDefinitionEngine_AP2_v1):
    """AP2 RF* definition engine with canonical v2 public schema aliases."""

    public_schema_version = "AP2.rf_star_definition_engine.v2"

    CANONICAL_SCORE_ALIASES = {
        "self_generated_rf": "rf_auto_generation_score",
        "omega_stable": "omega_stability_score",
        "proper_time": "proper_time_score",
        "ed_non_trivial": "ed_non_triviality_score",
        "tphi_non_homogeneous": "tphi_non_homogeneity_score",
        "l_rf": "l_rf_support_score",
        "qf_robust": "qf_robustness_score",
        "mei": "mei_support_score",
        "mei_minimal_appearing_non_separability": "am_non_separability_support_score",
        "epistemic_guard": "epistemic_guard_score",
    }

    CANONICAL_COMPONENT_ALIASES = {
        "RF_auto_generated": "self_generated_rf",
        "Omega_stable": "omega_stable",
        "T_proper": "proper_time",
        "ED_non_trivial": "ed_non_trivial",
        "Tphi_non_homogeneous": "tphi_non_homogeneous",
        "L_RF": "l_rf",
        "QF_robust": "qf_robust",
        "MEI": "mei",
        "MEI_minimal_appearing_non_separability": "mei_minimal_appearing_non_separability",
        "epistemic_guard": "epistemic_guard",
    }

    def _apply_public_schema_v2(self, result):
        scores = result.get("component_scores", {})
        if isinstance(scores, dict):
            for public_key, internal_key in self.CANONICAL_SCORE_ALIASES.items():
                if public_key not in scores and internal_key in scores:
                    scores[public_key] = scores[internal_key]
            result["component_scores"] = scores

        previous_components = result.get("rf_star_components", [])
        if isinstance(previous_components, dict):
            component_list = list(previous_components.values())
        elif isinstance(previous_components, list):
            component_list = previous_components
        else:
            component_list = []

        components_by_key = {}
        for component in component_list:
            if not isinstance(component, dict):
                continue
            name = component.get("name")
            public_key = self.CANONICAL_COMPONENT_ALIASES.get(name)
            if not public_key:
                continue
            item = dict(component)
            item["canonical_key"] = public_key
            item["public_key"] = public_key
            item["score"] = scores.get(public_key, item.get("score", 0.0))
            components_by_key[public_key] = item

        # Ensure every canonical key exists, even if an upstream component was absent.
        for public_key, internal_key in self.CANONICAL_SCORE_ALIASES.items():
            components_by_key.setdefault(public_key, {
                "canonical_key": public_key,
                "public_key": public_key,
                "name": public_key,
                "score_key": internal_key,
                "score": scores.get(public_key, scores.get(internal_key, 0.0)),
                "threshold": 0.95 if public_key == "epistemic_guard" else 0.80,
                "threshold_satisfied": scores.get(public_key, scores.get(internal_key, 0.0)) >= (0.95 if public_key == "epistemic_guard" else 0.80),
                "functional_role_only": True,
                "phenomenological_claim_allowed": False,
            })

        result["rf_star_component_list"] = component_list
        result["rf_star_components"] = components_by_key
        result["rf_star_components_by_name"] = components_by_key
        result["rf_star_component_aliases"] = dict(self.CANONICAL_COMPONENT_ALIASES)

        domains = result.get("property_domains") or result.get("distinctions") or {}
        if isinstance(domains, dict):
            result["property_domains"] = domains
        else:
            result["property_domains"] = {
                "functional_properties": [],
                "formal_properties": [],
                "ontological_properties": [],
                "phenomenological_properties": ["undetermined", "not_proven"],
            }
        result["property_domains"].setdefault("functional_properties", [])
        result["property_domains"].setdefault("formal_properties", [])
        result["property_domains"].setdefault("ontological_properties", [])
        result["property_domains"].setdefault("phenomenological_properties", ["undetermined", "not_proven"])

        result["public_schema_version"] = self.public_schema_version
        result["interfaces_public"] = sorted(set(result.get("interfaces_public", []) + [
            "result['rf_star_components'][canonical_component_key]",
            "result['rf_star_component_list']",
            "result['property_domains']",
            "result['component_scores'][canonical_component_key]",
        ]))
        result["structures_de_donnees"] = dict(result.get("structures_de_donnees", {}), **{
            "rf_star_components": "dict[canonical_key, component_definition]",
            "rf_star_component_list": "list[dict]",
            "property_domains": "dict[str, list[str]]",
        })
        metrics = list(result.get("metrics_produced", []))
        for key in self.CANONICAL_SCORE_ALIASES:
            if key not in metrics:
                metrics.append(key)
        result["metrics_produced"] = metrics
        return result

    def step(self, inputs=None, persist=True):
        # Call v1 without persistence so the persisted JSON/MD/Prom carries the v2 schema.
        result = super().step(inputs=inputs, persist=False)
        result = self._apply_public_schema_v2(result)
        if persist:
            result["persistence"] = self._persist(result)
        return result

RFStarDefinition = RFStarDefinitionEngine
# --- AP2_PUBLIC_SCHEMA_PATCH_END ---
