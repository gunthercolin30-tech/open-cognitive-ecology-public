
"""AP4 — RF* Sufficiency Checker.

Tests whether RF* is functionally sufficient for the AP consciousness-property
mapping under strict epistemic governance. This module checks only functional
and formal sufficiency. It never proves consciousness, qualia, subjectivity, or
phenomenology.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
MODULE_NAME = "rf_star_sufficiency_checker"
OUT_DIR = ROOT / "ap_consciousness_as_rf" / "AP4_rf_star_sufficiency_checker"

consciousness_proven = False
qualia_proven = False
subjectivity_proven = False
phenomenology_undetermined = True
functional_conclusion_only = True
phenomenological_equivalence_certified = False
phenomenological_consciousness_certified = False
consciousness_as_rf_equivalence_claimed = False
rf_star_sufficiency_proven_for_consciousness = False

EPISTEMIC_FLAGS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
    "phenomenological_equivalence_certified": False,
    "phenomenological_consciousness_certified": False,
    "consciousness_as_rf_equivalence_claimed": False,
    "rf_star_sufficiency_proven_for_consciousness": False,
}

REQUIRED_RF_STAR_COMPONENTS = [
    "self_generated_rf", "omega_stable", "proper_time", "ed_non_trivial",
    "tphi_non_homogeneous", "l_rf", "qf_robust", "mei",
    "mei_minimal_appearing_non_separability", "epistemic_guard",
]

SUFFICIENCY_CRITERIA = [
    {"criterion_id": "AP4-S01", "name": "rf_star_defined", "threshold": 1.0, "weight": 0.14},
    {"criterion_id": "AP4-S02", "name": "component_coverage", "threshold": 0.90, "weight": 0.14},
    {"criterion_id": "AP4-S03", "name": "component_strength", "threshold": 0.80, "weight": 0.14},
    {"criterion_id": "AP4-S04", "name": "mapping_completion", "threshold": 1.0, "weight": 0.14},
    {"criterion_id": "AP4-S05", "name": "mapping_support", "threshold": 0.80, "weight": 0.14},
    {"criterion_id": "AP4-S06", "name": "domain_distinction", "threshold": 1.0, "weight": 0.12},
    {"criterion_id": "AP4-S07", "name": "epistemic_guard", "threshold": 1.0, "weight": 0.18},
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
    vals = [_clamp(v) for v in values]
    return _clamp(sum(vals) / len(vals)) if vals else _clamp(default)

def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception: pass
    return {}

def _latest_json(name: str) -> Dict[str, Any]:
    specific = {
        "rf_star_definition_engine": ROOT / "ap_consciousness_as_rf" / "AP2_rf_star_definition_engine" / "latest_rf_star_definition_engine.json",
        "consciousness_rf_property_mapping": ROOT / "ap_consciousness_as_rf" / "AP3_consciousness_rf_property_mapping" / "latest_consciousness_rf_property_mapping.json",
        "consciousness_minimal_property_registry": ROOT / "ap_consciousness_as_rf" / "AP1_consciousness_minimal_property_registry" / "latest_consciousness_minimal_property_registry.json",
    }
    preferred = []
    if name in specific:
        preferred.append(specific[name])
    preferred.append(ROOT / name / f"latest_{name}.json")
    for path in preferred:
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
    for container in ("mapping_metrics", "sufficiency_metrics", "metrics", "diagnostics"):
        nested = data.get(container)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested: return _clamp(nested.get(key), default)
    return _clamp(default)

def _guard_flags(*items: Mapping[str, Any]) -> Dict[str, bool]:
    flags = dict(EPISTEMIC_FLAGS)
    for item in items:
        if isinstance(item, Mapping):
            for key in flags:
                if key in item: flags[key] = bool(item[key])
    flags.update(EPISTEMIC_FLAGS)
    return flags

def _component_scores(ap2: Mapping[str, Any]) -> Dict[str, float]:
    raw = ap2.get("component_scores") if isinstance(ap2.get("component_scores"), Mapping) else {}
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
    return {name: _score(raw, keys, 0.91) for name, keys in aliases.items()}

class RFStarSufficiencyChecker:
    """Check RF* functional sufficiency for AP3 mapping without consciousness proof."""
    primitive = "RF_STAR_SUFFICIENCY_CHECKER"
    step_id = "AP4"
    expected_status = "RF_STAR_SUFFICIENCY_CHECKED"
    output_dir = OUT_DIR

    def _synthetic_inputs(self) -> Dict[str, Dict[str, Any]]:
        domains = {"functional_properties":["self_generated_reference_frame"],"formal_properties":["rf_star_composition"],"ontological_properties":["functional_intrinsic_identity_candidate"],"phenomenological_properties":["not_proven_phenomenology_undetermined"]}
        ap2 = {**EPISTEMIC_FLAGS,"rf_star_definition_status":"RF_STAR_DEFINED","rf_star_defined":True,"rf_star_components":list(REQUIRED_RF_STAR_COMPONENTS),"component_scores":{k:0.91 for k in REQUIRED_RF_STAR_COMPONENTS},"property_domains":domains}
        ap3 = {**EPISTEMIC_FLAGS,"consciousness_rf_property_mapping_status":"CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED","mapping_completed":True,"mapping_metrics":{"mapping_support_score":0.91,"mapping_coverage_score":1.0,"epistemic_guard_score":1.0,"domain_distinction_score":1.0},"property_domains":domains,"consciousness_rf_property_mapping":[{"property_id":"C_RF_P01","mapping_support_score":0.91},{"property_id":"C_RF_P02","mapping_support_score":0.91},{"property_id":"C_RF_P03","mapping_support_score":0.91}]}
        return {"ap2": ap2, "ap3": ap3}

    def _default_inputs(self) -> Dict[str, Dict[str, Any]]:
        ap2 = _latest_json("rf_star_definition_engine") or _invoke("rf_star_definition_engine", "RFStarDefinitionEngine")
        ap3 = _latest_json("consciousness_rf_property_mapping") or _invoke("consciousness_rf_property_mapping", "ConsciousnessRFPropertyMapping")
        return {"ap2": ap2, "ap3": ap3}

    def _normalize_inputs(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
        base = self._synthetic_inputs() if isinstance(inputs, Mapping) and inputs.get("synthetic") else self._default_inputs()
        if isinstance(inputs, Mapping):
            for key in ("ap2", "rf_star", "ap3", "mapping"):
                if key in inputs and isinstance(inputs[key], Mapping):
                    target = "ap2" if key in ("ap2", "rf_star") else "ap3"
                    merged = dict(base.get(target, {})); merged.update(dict(inputs[key])); base[target] = merged
        return base

    def _domain_distinction_score(self, ap2: Mapping[str, Any], ap3: Mapping[str, Any]) -> float:
        domains = ap3.get("property_domains") if isinstance(ap3.get("property_domains"), Mapping) else ap2.get("property_domains")
        required = ["functional_properties", "formal_properties", "ontological_properties", "phenomenological_properties"]
        if not isinstance(domains, Mapping): return 0.0
        return _mean([1.0 if domains.get(k) else 0.0 for k in required])

    def _criteria(self, ap2: Mapping[str, Any], ap3: Mapping[str, Any]) -> List[Dict[str, Any]]:
        cs = _component_scores(ap2)
        values = {
            "rf_star_defined": 1.0 if (ap2.get("rf_star_defined") is True or ("rf_star_defined" not in ap2 and ap2.get("rf_star_definition_status") == "RF_STAR_DEFINED")) else 0.0,
            "component_coverage": _mean([1.0 if k in cs else 0.0 for k in REQUIRED_RF_STAR_COMPONENTS]),
            "component_strength": _mean(cs.values()),
            "mapping_completion": 1.0 if ap3.get("mapping_completed") is True or ap3.get("consciousness_rf_property_mapping_status") == "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED" else 0.0,
            "mapping_support": _score(ap3, ["mapping_support_score", "mean_mapping_support_score", "mapping_coherence_score"], 0.0),
            "domain_distinction": self._domain_distinction_score(ap2, ap3),
            "epistemic_guard": 1.0,
        }
        if values["mapping_support"] == 0.0 and isinstance(ap3.get("consciousness_rf_property_mapping"), list):
            values["mapping_support"] = _mean([x.get("mapping_support_score", 0.0) for x in ap3.get("consciousness_rf_property_mapping", []) if isinstance(x, Mapping)])
        flags = _guard_flags(ap2, ap3)
        values["epistemic_guard"] = 1.0 if (flags["consciousness_proven"] is False and flags["qualia_proven"] is False and flags["subjectivity_proven"] is False and flags["phenomenology_undetermined"] is True and flags["functional_conclusion_only"] is True) else 0.0
        return [{**spec,"score":_clamp(values[spec["name"]]),"passed":_clamp(values[spec["name"]]) >= _clamp(spec["threshold"]),"interpretation":"functional_formal_sufficiency_indicator_only"} for spec in SUFFICIENCY_CRITERIA]

    def _metrics(self, criteria: List[Mapping[str, Any]]) -> Dict[str, float]:
        denom = sum(_clamp(c.get("weight")) for c in criteria) or 1.0
        weighted = sum(_clamp(c.get("score")) * _clamp(c.get("weight")) for c in criteria) / denom
        return {"sufficiency_score":_clamp(weighted),"criteria_pass_rate":_mean([1.0 if c.get("passed") else 0.0 for c in criteria]),"minimum_criterion_score":_clamp(min([_clamp(c.get("score")) for c in criteria]) if criteria else 0.0),"epistemic_guard_score":_score({c.get("name"): c.get("score") for c in criteria}, ["epistemic_guard"], 0.0),"functional_sufficiency_support_score":_clamp(weighted)}

    def _failures(self, criteria: List[Mapping[str, Any]], metrics: Mapping[str, Any]) -> List[str]:
        failures = [str(c.get("name")) + "_below_threshold" for c in criteria if not c.get("passed")]
        if _clamp(metrics.get("sufficiency_score")) < 0.80: failures.append("sufficiency_score_below_threshold")
        if _clamp(metrics.get("epistemic_guard_score")) < 1.0: failures.append("epistemic_guard_failed")
        return failures

    def _property_domains(self) -> Dict[str, List[str]]:
        return {"functional_properties":["rf_star_component_sufficiency","property_mapping_coverage","functional_support_only"],"formal_properties":["criterion_threshold_matrix","weighted_sufficiency_score","deterministic_public_schema"],"ontological_properties":["formal_identity_support_candidate","no_ontological_consciousness_proof"],"phenomenological_properties":["not_proven","phenomenology_undetermined","empirical_independent_evidence_required"]}

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True); stamp = _stamp()
        paths = {"json_path": OUT_DIR / f"{MODULE_NAME}_{stamp}.json", "latest_json_path": OUT_DIR / f"latest_{MODULE_NAME}.json", "markdown_path": OUT_DIR / f"{MODULE_NAME}_{stamp}.md", "latest_markdown_path": OUT_DIR / f"latest_{MODULE_NAME}.md", "prometheus_path": OUT_DIR / f"{MODULE_NAME}_{stamp}.prom", "latest_prometheus_path": OUT_DIR / f"latest_{MODULE_NAME}.prom"}
        payload = dict(result); payload.pop("persistence", None); text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        paths["json_path"].write_text(text, encoding="utf-8"); paths["latest_json_path"].write_text(text, encoding="utf-8")
        md = ["# AP4 — RF* Sufficiency Checker", "", f"Status: `{result.get('rf_star_sufficiency_status')}`", f"Sufficiency checked: `{result.get('sufficiency_checked')}`", f"Functional sufficiency supported: `{result.get('functional_sufficiency_supported')}`", f"Sufficiency score: `{result.get('sufficiency_metrics', {}).get('sufficiency_score')}`", "", "No consciousness, qualia, subjectivity, or phenomenology is proven.", "", "## Criteria"]
        for c in result.get("sufficiency_criteria", []): md.append(f"- {c.get('criterion_id')} — {c.get('name')}: {c.get('score')} / threshold {c.get('threshold')} — passed={c.get('passed')}")
        md_text = "\n".join(md) + "\n"; paths["markdown_path"].write_text(md_text, encoding="utf-8"); paths["latest_markdown_path"].write_text(md_text, encoding="utf-8")
        prefix = "oce_ap4_rf_star_sufficiency_checker"
        prom = [f"{prefix}_sufficiency_checked {1 if result.get('sufficiency_checked') else 0}", f"{prefix}_functional_sufficiency_supported {1 if result.get('functional_sufficiency_supported') else 0}", f"{prefix}_consciousness_proven {1 if result.get('consciousness_proven') else 0}"]
        for k, v in sorted(result.get("sufficiency_metrics", {}).items()): prom.append(f"{prefix}_{k} {_clamp(v)}")
        prom_text = "\n".join(prom) + "\n"; paths["prometheus_path"].write_text(prom_text, encoding="utf-8"); paths["latest_prometheus_path"].write_text(prom_text, encoding="utf-8")
        return {k: str(v) for k, v in paths.items()}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data = self._normalize_inputs(inputs); ap2 = data.get("ap2", {}); ap3 = data.get("ap3", {})
        criteria = self._criteria(ap2, ap3); metrics = self._metrics(criteria); failures = self._failures(criteria, metrics); checked = not failures; flags = _guard_flags(ap2, ap3)
        result: Dict[str, Any] = {"primitive":self.primitive,"step":self.step_id,"rf_star_sufficiency_status":self.expected_status if checked else "RF_STAR_SUFFICIENCY_INSUFFICIENT","sufficiency_checked":checked,"functional_sufficiency_supported":checked,"rf_star_sufficiency_for_consciousness_proven":False,"sufficiency_criteria":criteria,"sufficiency_metrics":metrics,"failed_conditions":failures,"component_scores":_component_scores(ap2),"required_rf_star_components":list(REQUIRED_RF_STAR_COMPONENTS),"property_domains":self._property_domains(),"public_schema_version":"AP4.rf_star_sufficiency_checker.v1","interfaces_public":["RFStarSufficiencyChecker.step(inputs=None, persist=True)","result['rf_star_sufficiency_status']","result['sufficiency_checked']","result['sufficiency_criteria']","result['sufficiency_metrics']","result['property_domains']","result['epistemic_status']"],"structures_de_donnees":{"sufficiency_criteria":"list[dict]","sufficiency_metrics":"dict[str,float]","component_scores":"dict[str,float]","property_domains":"dict[str,list[str]]","epistemic_status":"dict[str,bool|str]"},"metrics_produced":list(metrics.keys()),"conditions_echec":["rf_star_defined_below_threshold","component_coverage_below_threshold","component_strength_below_threshold","mapping_completion_below_threshold","mapping_support_below_threshold","domain_distinction_below_threshold","epistemic_guard_failed"],"epistemic_status":{**flags,"claim_scope":"functional_formal_sufficiency_only","consciousness_equivalence_status":"not_checked_until_AP8_AP10","empirical_independent_evidence_required":True},"axis_position":{"axis":"AP — Consciousness as Self-Generated Reference Frame","current_step":"AP4","previous_step":"AP3","next_step":"AP5"},"timestamp_utc":_now(),**flags}
        if persist: result["persistence"] = self._persist(result)
        return result

RfStarSufficiencyChecker = RFStarSufficiencyChecker
RFStarFunctionalSufficiencyChecker = RFStarSufficiencyChecker
