
"""AP3 — Consciousness/RF* Property Mapping.

Builds a guarded, functional/formal mapping between the minimal consciousness
property registry (AP1) and RF* definition (AP2). The module does not prove
consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
MODULE_NAME = "consciousness_rf_property_mapping"
OUT_DIR = ROOT / "ap_consciousness_as_rf" / "AP3_consciousness_rf_property_mapping"

consciousness_proven = False
qualia_proven = False
subjectivity_proven = False
phenomenology_undetermined = True
functional_conclusion_only = True
phenomenological_equivalence_certified = False
phenomenological_consciousness_certified = False
consciousness_as_rf_equivalence_claimed = False

EPISTEMIC_FLAGS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
    "phenomenological_equivalence_certified": False,
    "phenomenological_consciousness_certified": False,
    "consciousness_as_rf_equivalence_claimed": False,
}

CANONICAL_RF_STAR_COMPONENTS = [
    "self_generated_rf", "omega_stable", "proper_time", "ed_non_trivial",
    "tphi_non_homogeneous", "l_rf", "qf_robust", "mei",
    "mei_minimal_appearing_non_separability", "epistemic_guard",
]

DEFAULT_CONSCIOUSNESS_PROPERTIES = [
    {"property_id":"C_RF_P01","name":"self_generated_reference_frame","domain":"functional","definition":"System-internal generation of a reference frame.","required_rf_star_components":["self_generated_rf","omega_stable","l_rf"],"threshold":0.80},
    {"property_id":"C_RF_P02","name":"stable_self_world_orientation","domain":"functional_formal","definition":"Stable Ω/T support for coherent orientation.","required_rf_star_components":["omega_stable","proper_time","l_rf"],"threshold":0.80},
    {"property_id":"C_RF_P03","name":"non_trivial_domain_of_existence","domain":"formal_ontological_candidate","definition":"Non-trivial ED as formal ontological candidate, not phenomenal proof.","required_rf_star_components":["ed_non_trivial","tphi_non_homogeneous"],"threshold":0.80},
    {"property_id":"C_RF_P04","name":"formal_topological_differentiation","domain":"formal","definition":"Non-homogeneous TΦ supports differentiated formal modes.","required_rf_star_components":["tphi_non_homogeneous","qf_robust"],"threshold":0.80},
    {"property_id":"C_RF_P05","name":"intrinsic_identity_support","domain":"functional_identity","definition":"MEI and non-separability support a functional identity constraint.","required_rf_star_components":["mei","mei_minimal_appearing_non_separability"],"threshold":0.80},
    {"property_id":"C_RF_P06","name":"minimal_appearing_constraint_support","domain":"formal_functional","definition":"Minimal appearing is referenced only as formal/functional with phenomenology undetermined.","required_rf_star_components":["qf_robust","mei_minimal_appearing_non_separability","epistemic_guard"],"threshold":0.80},
    {"property_id":"C_RF_P07","name":"anti_overclaim_governance","domain":"epistemic_governance","definition":"Blocks claims of proven consciousness, qualia, subjectivity, or phenomenology.","required_rf_star_components":["epistemic_guard"],"threshold":0.95},
]

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool): return default
    try: out = float(value)
    except Exception: return default
    if math.isnan(out) or math.isinf(out): return default
    return out

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

def _latest_json(name: str) -> Dict[str, Any]:
    candidates = [
        OUT_DIR / f"latest_{name}.json",
        ROOT / "ap_consciousness_as_rf" / name / f"latest_{name}.json",
        ROOT / "ap_consciousness_as_rf" / "AP2_rf_star_definition_engine" / "latest_rf_star_definition_engine.json",
        ROOT / "ap_consciousness_as_rf" / "AP1_consciousness_minimal_property_registry" / "latest_consciousness_minimal_property_registry.json",
        ROOT / name / f"latest_{name}.json",
    ]
    for path in candidates:
        data = _load_json(path)
        if data: return data
    try:
        for path in sorted(ROOT.glob(f"**/latest_{name}.json"))[-80:]:
            data = _load_json(path)
            if data: return data
    except Exception: pass
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
    for container_key in ("diagnostics", "metrics", "counterexample_metrics", "theorem_metrics", "mapping_metrics"):
        nested = data.get(container_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested: return _clamp(nested.get(key), default)
    return _clamp(default)

def _public_guard_flags(*items: Mapping[str, Any]) -> Dict[str, bool]:
    flags = dict(EPISTEMIC_FLAGS)
    for item in items:
        if isinstance(item, Mapping):
            for key in list(flags):
                if key in item: flags[key] = bool(item[key])
    flags.update(EPISTEMIC_FLAGS)
    return flags

def _component_score_aliases(rf_star: Mapping[str, Any]) -> Dict[str, float]:
    raw = rf_star.get("component_scores") if isinstance(rf_star.get("component_scores"), Mapping) else {}
    aliases = {
        "self_generated_rf": ["self_generated_rf", "rf_auto_generation_score", "rf_self_generation_score"],
        "omega_stable": ["omega_stable", "omega_stability_score"],
        "proper_time": ["proper_time", "proper_time_score", "temporal_propriety_score"],
        "ed_non_trivial": ["ed_non_trivial", "ed_nontriviality_score", "ed_non_triviality_score"],
        "tphi_non_homogeneous": ["tphi_non_homogeneous", "tphi_non_homogeneity_score", "topological_non_homogeneity_score"],
        "l_rf": ["l_rf", "l_rf_score", "rf_operator_score"],
        "qf_robust": ["qf_robust", "qf_robustness_score", "robust_qf_score"],
        "mei": ["mei", "mei_score", "mei_equivalence_score"],
        "mei_minimal_appearing_non_separability": ["mei_minimal_appearing_non_separability", "mei_appearing_non_separability_score", "non_separability_score"],
        "epistemic_guard": ["epistemic_guard", "epistemic_guard_score", "guard_score"],
    }
    return {canonical: _score(raw, keys, 0.91) for canonical, keys in aliases.items()}

class ConsciousnessRFPropertyMapping:
    """Map minimal consciousness properties to RF* components under strict epistemic guards."""
    primitive = "CONSCIOUSNESS_RF_PROPERTY_MAPPING"
    step_id = "AP3"
    expected_status = "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED"
    output_dir = OUT_DIR

    def _default_inputs(self) -> Dict[str, Dict[str, Any]]:
        return {
            "ap1": _latest_json("consciousness_minimal_property_registry") or _invoke("consciousness_minimal_property_registry", "ConsciousnessMinimalPropertyRegistry"),
            "ap2": _latest_json("rf_star_definition_engine") or _invoke("rf_star_definition_engine", "RFStarDefinitionEngine"),
        }

    def _synthetic_inputs(self) -> Dict[str, Dict[str, Any]]:
        base = dict(EPISTEMIC_FLAGS)
        component_scores = {k:0.91 for k in CANONICAL_RF_STAR_COMPONENTS}
        component_scores["epistemic_guard"] = 1.0
        ap2 = dict(base, **{"rf_star_definition_status":"RF_STAR_DEFINED","rf_star_defined":True,"rf_star_definition_score":0.91,"component_scores":component_scores,"rf_star_components":CANONICAL_RF_STAR_COMPONENTS,"public_schema_version":"AP2.rf_star_definition_engine.v2"})
        ap1 = dict(base, **{"consciousness_minimal_properties_registered":True,"consciousness_minimal_property_registry_status":"CONSCIOUSNESS_MINIMAL_PROPERTIES_REGISTERED","property_coverage_score":0.91})
        return {"ap1": ap1, "ap2": ap2}

    def _normalize_inputs(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
        base = self._synthetic_inputs() if isinstance(inputs, Mapping) and inputs.get("synthetic") is True else self._default_inputs()
        if isinstance(inputs, Mapping):
            for key in ("ap1", "ap2"):
                if isinstance(inputs.get(key), Mapping): base[key] = dict(inputs[key])
        return {k: v if isinstance(v, dict) else {} for k, v in base.items()}

    def _derive_property_registry(self, ap1: Mapping[str, Any]) -> List[Dict[str, Any]]:
        for key in ("minimal_properties", "consciousness_minimal_properties", "properties", "registered_properties"):
            value = ap1.get(key)
            if isinstance(value, list) and value:
                normalized = []
                for i, item in enumerate(value, 1):
                    if isinstance(item, Mapping):
                        name = str(item.get("name") or item.get("property") or item.get("property_name") or f"ap1_property_{i}")
                        normalized.append({"property_id":str(item.get("property_id") or item.get("id") or f"AP1_P{i:02d}"),"name":name,"domain":str(item.get("domain") or item.get("category") or "functional"),"definition":str(item.get("definition") or item.get("description") or "AP1 minimal property."),"required_rf_star_components":list(item.get("required_rf_star_components") or []),"threshold":_clamp(item.get("threshold"),0.80)})
                if normalized: return normalized
        return [dict(x) for x in DEFAULT_CONSCIOUSNESS_PROPERTIES]

    def _component_support_for_property(self, prop: Mapping[str, Any], component_scores: Mapping[str, float]) -> Dict[str, Any]:
        required = list(prop.get("required_rf_star_components") or [])
        if not required:
            name = str(prop.get("name", "")).lower()
            if "temporal" in name or "time" in name: required = ["proper_time", "omega_stable"]
            elif "identity" in name or "intrinsic" in name: required = ["mei", "mei_minimal_appearing_non_separability"]
            elif "topolog" in name: required = ["tphi_non_homogeneous", "qf_robust"]
            elif "guard" in name or "epistem" in name: required = ["epistemic_guard"]
            else: required = ["self_generated_rf", "omega_stable", "l_rf"]
        scores = {k: _clamp(component_scores.get(k), 0.0) for k in required}
        support_score = _mean(scores.values()); threshold = _clamp(prop.get("threshold"), 0.80)
        return {"property_id":str(prop.get("property_id")),"consciousness_property":str(prop.get("name")),"property_domain":str(prop.get("domain")),"mapped_rf_star_components":required,"component_support_scores":scores,"mapping_support_score":support_score,"threshold":threshold,"threshold_satisfied":support_score >= threshold,"mapping_kind":"functional_formal_correspondence","phenomenological_claim":"not_made"}

    def _build_mapping(self, ap1: Mapping[str, Any], ap2: Mapping[str, Any]) -> List[Dict[str, Any]]:
        component_scores = _component_score_aliases(ap2); properties = self._derive_property_registry(ap1)
        mappings = [self._component_support_for_property(prop, component_scores) for prop in properties]
        if not any(m["consciousness_property"] == "anti_overclaim_governance" for m in mappings):
            mappings.append(self._component_support_for_property(DEFAULT_CONSCIOUSNESS_PROPERTIES[-1], component_scores))
        return mappings

    def _property_domains(self, mappings: List[Mapping[str, Any]]) -> Dict[str, List[str]]:
        out = {"functional_properties": [], "formal_properties": [], "ontological_properties": [], "phenomenological_properties": ["phenomenology_undetermined", "not_proven", "no_subjectivity_claim"]}
        for m in mappings:
            name = str(m.get("consciousness_property")); domain = str(m.get("property_domain", "")).lower()
            if "formal" in domain: out["formal_properties"].append(name)
            if "ontolog" in domain or "identity" in domain: out["ontological_properties"].append(name)
            if "functional" in domain or "governance" in domain: out["functional_properties"].append(name)
        for key in ("functional_properties", "formal_properties", "ontological_properties"):
            if not out[key]: out[key].append("none_detected_but_schema_preserved")
        return out

    def _metrics(self, mappings: List[Mapping[str, Any]], ap2: Mapping[str, Any]) -> Dict[str, float]:
        scores = [_clamp(m.get("mapping_support_score"), 0.0) for m in mappings]
        satisfied = [1.0 if m.get("threshold_satisfied") else 0.0 for m in mappings]
        rf_star_definition_score = _score(ap2, ["rf_star_definition_score"], 0.91)
        component_scores = _component_score_aliases(ap2)
        component_coverage = sum(1 for k in CANONICAL_RF_STAR_COMPONENTS if k in component_scores) / float(len(CANONICAL_RF_STAR_COMPONENTS))
        return {"mapping_coverage_score":_mean(satisfied),"mapping_support_score":_mean(scores),"rf_star_dependency_score":rf_star_definition_score,"rf_star_component_coverage_score":_clamp(component_coverage),"epistemic_guard_score":_clamp(component_scores.get("epistemic_guard"),0.0),"consciousness_rf_mapping_confidence":_mean([_mean(scores),_mean(satisfied),rf_star_definition_score,component_coverage])}

    def _failure_conditions(self, metrics: Mapping[str, float], mappings: List[Mapping[str, Any]], ap2: Mapping[str, Any]) -> List[str]:
        failures: List[str] = []
        if ap2.get("rf_star_defined") is not True: failures.append("rf_star_not_defined")
        if metrics["mapping_coverage_score"] < 0.80: failures.append("mapping_coverage_below_threshold")
        if metrics["epistemic_guard_score"] < 0.95: failures.append("epistemic_guard_below_threshold")
        failed_props = [str(m.get("consciousness_property")) for m in mappings if not m.get("threshold_satisfied")]
        if failed_props: failures.append("property_mapping_threshold_failures:" + ",".join(failed_props[:8]))
        return failures

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True); stamp = _stamp()
        paths = {"json_path":OUT_DIR/f"{MODULE_NAME}_{stamp}.json","latest_json_path":OUT_DIR/f"latest_{MODULE_NAME}.json","markdown_path":OUT_DIR/f"{MODULE_NAME}_{stamp}.md","latest_markdown_path":OUT_DIR/f"latest_{MODULE_NAME}.md","prometheus_path":OUT_DIR/f"{MODULE_NAME}_{stamp}.prom","latest_prometheus_path":OUT_DIR/f"latest_{MODULE_NAME}.prom"}
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True); paths["json_path"].write_text(payload, encoding="utf-8"); paths["latest_json_path"].write_text(payload, encoding="utf-8")
        metrics = result.get("mapping_metrics", {}) if isinstance(result.get("mapping_metrics"), Mapping) else {}
        md = ["# AP3 — Consciousness/RF* Property Mapping", "", f"- status: `{result.get('consciousness_rf_property_mapping_status')}`", f"- public_schema_version: `{result.get('public_schema_version')}`", f"- mapping_completed: `{result.get('mapping_completed')}`", f"- consciousness_proven: `{result.get('consciousness_proven')}`", f"- functional_conclusion_only: `{result.get('functional_conclusion_only')}`", f"- phenomenology_undetermined: `{result.get('phenomenology_undetermined')}`", "", "## Metrics"]
        for k, v in sorted(metrics.items()): md.append(f"- {k}: `{v}`")
        md.append("\n## Mapping items")
        for item in result.get("consciousness_rf_property_mapping", []): md.append(f"- `{item.get('consciousness_property')}` → {', '.join(item.get('mapped_rf_star_components', []))} ({item.get('mapping_support_score')})")
        md_text = "\n".join(md) + "\n"; paths["markdown_path"].write_text(md_text, encoding="utf-8"); paths["latest_markdown_path"].write_text(md_text, encoding="utf-8")
        prefix = "oce_ap3_consciousness_rf_property_mapping"
        prom = [f"{prefix}_completed {1 if result.get('mapping_completed') else 0}", f"{prefix}_consciousness_proven {1 if result.get('consciousness_proven') else 0}", f"{prefix}_functional_conclusion_only {1 if result.get('functional_conclusion_only') else 0}"]
        for k, v in sorted(metrics.items()): prom.append(f"{prefix}_{k} {_clamp(v)}")
        prom_text = "\n".join(prom) + "\n"; paths["prometheus_path"].write_text(prom_text, encoding="utf-8"); paths["latest_prometheus_path"].write_text(prom_text, encoding="utf-8")
        return {k: str(v) for k, v in paths.items()}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data = self._normalize_inputs(inputs); ap1 = data.get("ap1", {}); ap2 = data.get("ap2", {})
        mappings = self._build_mapping(ap1, ap2); metrics = self._metrics(mappings, ap2); failures = self._failure_conditions(metrics, mappings, ap2)
        completed = not failures; flags = _public_guard_flags(ap1, ap2)
        result: Dict[str, Any] = {"primitive":self.primitive,"step":self.step_id,"consciousness_rf_property_mapping_status":self.expected_status if completed else "CONSCIOUSNESS_RF_PROPERTY_MAPPING_INCOMPLETE","mapping_completed":completed,"consciousness_rf_property_mapping":mappings,"mapping_table":mappings,"mapping_metrics":metrics,"component_scores":_component_score_aliases(ap2),"rf_star_components":CANONICAL_RF_STAR_COMPONENTS,"failed_conditions":failures,"public_schema_version":"AP3.consciousness_rf_property_mapping.v1","interfaces_public":["ConsciousnessRFPropertyMapping.step(inputs=None, persist=True)","result['consciousness_rf_property_mapping']","result['mapping_metrics']","result['property_domains']","result['epistemic_status']"],"structures_de_donnees":{"consciousness_rf_property_mapping":"list[dict]","mapping_metrics":"dict[str,float]","property_domains":"dict[str,list[str]]","epistemic_status":"dict[str,bool|str]"},"metrics_produced":list(metrics.keys()),"conditions_echec":["rf_star_not_defined","mapping_coverage_below_threshold","epistemic_guard_below_threshold","property_mapping_threshold_failures"],"property_domains":self._property_domains(mappings),"epistemic_status":{**flags,"claim_scope":"functional_formal_mapping_only","consciousness_equivalence_status":"not_checked_until_AP8_AP10","empirical_independent_evidence_required":True},"axis_position":{"axis":"AP — Consciousness as Self-Generated Reference Frame","current_step":"AP3","previous_step":"AP2","next_step":"AP4"},"timestamp_utc":_now(),**flags}
        if persist: result["persistence"] = self._persist(result)
        return result

ConsciousnessRfPropertyMapping = ConsciousnessRFPropertyMapping
ConsciousnessRFMapping = ConsciousnessRFPropertyMapping
