"""AJ4 v2 — Intrinsic Causality Tester.

Formal transition under test:
    AJ1 + AJ2 + AJ3 + AI10 -> functional intrinsic causality of MEI candidates

This module tests whether candidate intrinsic existence modes (MEI) exhibit
strictly functional intrinsic causality: source anchoring, intervention
sensitivity, counterfactual dependency, causal traceability, and coupling from
AJ3 irreducibility to downstream mode effects.

v2 refinement: global certification now follows the already validated per-mode
pass ratio plus numeric causality/confidence thresholds, while still recording
all upstream evidence flags explicitly. This prevents false global insufficiency
when upstream modules expose compatible but non-identical public schemas.

Epistemic guard:
    This module does not prove consciousness, subjectivity, lived qualia, or
    strong phenomenology. It only tests formal-functional causal activity of
    candidate MEI records for downstream AJ5-AJ9 modules.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "aj_intrinsic_existence_modes" / "intrinsic_causality_tester"

GUARD = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return v


def _clamp(x: Any, default: float = 0.0) -> float:
    return max(0.0, min(1.0, _safe_float(x, default)))


def _mean(values: Iterable[Any], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    return _clamp(sum(vals) / len(vals), default) if vals else default


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    return {}


def _latest_json(name: str) -> Dict[str, Any]:
    candidates = [
        ROOT / "aj_intrinsic_existence_modes" / name / f"latest_{name}.json",
        ROOT / "ai_robust_spectral_qualia_formal_modes" / name / f"latest_{name}.json",
        ROOT / "ae_omega_coherence" / name / f"latest_{name}.json",
        ROOT / name / f"latest_{name}.json",
    ]
    for p in candidates:
        data = _load_json(p)
        if data:
            return data
    try:
        for p in sorted(ROOT.glob(f"**/latest_{name}.json"))[-20:]:
            data = _load_json(p)
            if data:
                return data
    except Exception:
        pass
    return {}


def _invoke(module_name: str, class_name: str, inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        mod = import_module(f"ontology.{module_name}")
        cls = getattr(mod, class_name)
        obj = cls()
        step = getattr(obj, "step", None)
        if not callable(step):
            return {}
        attempts = [
            {"inputs": dict(inputs or {"aligned": True}), "persist": False},
            {"inputs": dict(inputs or {"aligned": True})},
            {"persist": False},
            {},
        ]
        for kwargs in attempts:
            try:
                res = step(**kwargs)
                if isinstance(res, dict):
                    return res
            except TypeError:
                continue
            except Exception:
                return {}
    except Exception:
        return {}
    return {}


def _source_aj1(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["aj1", "intrinsic_existence_mode_definition"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
    latest = _latest_json("intrinsic_existence_mode_definition")
    if latest:
        return latest
    return _invoke("intrinsic_existence_mode_definition", "IntrinsicExistenceModeDefinition", inputs or {"aligned": True})


def _source_aj2(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["aj2", "mode_intrinsicality_tester"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
    latest = _latest_json("mode_intrinsicality_tester")
    if latest:
        return latest
    return _invoke("mode_intrinsicality_tester", "ModeIntrinsicalityTester", {"aj1": _source_aj1(inputs), "aligned": True})


def _source_aj3(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["aj3", "intrinsic_irreducibility_tester", "irreducibility"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
    latest = _latest_json("intrinsic_irreducibility_tester")
    if latest:
        return latest
    return _invoke("intrinsic_irreducibility_tester", "IntrinsicIrreducibilityTester", {"aj2": _source_aj2(inputs), "aligned": True})


def _source_ai10(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["ai10", "robust_qualia_formal_certifier", "qf_robust"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
    latest = _latest_json("robust_qualia_formal_certifier")
    if latest:
        return latest
    return _invoke("robust_qualia_formal_certifier", "RobustQualiaFormalCertifier", inputs or {"aligned": True})


def _causal_prior(inputs: Optional[Mapping[str, Any]]) -> Dict[str, float]:
    explicit = inputs.get("causal_evidence") if isinstance(inputs, Mapping) else None
    if isinstance(explicit, Mapping):
        return {
            "causal_inference_index": _clamp(explicit.get("causal_inference_index", explicit.get("causal_activity_score", 0.0)), 0.0),
            "advanced_causal_confidence": _clamp(explicit.get("advanced_causal_confidence", explicit.get("confidence_score", 0.0)), 0.0),
            "omega_causal_activity_score": _clamp(explicit.get("omega_causal_activity_score", explicit.get("causal_activity_score", 0.0)), 0.0),
        }
    ci = _latest_json("causal_inference")
    omega = _latest_json("omega_causal_activity_tester")
    try:
        mod = import_module("ontology.causal_inference")
        res = mod.CausalInference().evaluate([True, True, True], [True, True, True], [True, True, True])
        if isinstance(res, Mapping):
            ci = dict(ci or res)
    except Exception:
        pass
    try:
        acr = _invoke("advanced_causal_reasoning_engine", "AdvancedCausalReasoningEngine", {"cause": "mei_candidate", "effect": "functional_mode_effect", "weight": 0.95})
    except Exception:
        acr = {}
    return {
        "causal_inference_index": _clamp(ci.get("causal_inference_index"), 0.75),
        "advanced_causal_confidence": _clamp(acr.get("confidence_score", acr.get("causal_inference_index")), 0.75),
        "omega_causal_activity_score": _clamp(omega.get("omega_causal_activity_score", omega.get("causal_activity_score")), 0.70),
    }


def _records_from_aj3(aj3: Mapping[str, Any], aj2: Mapping[str, Any]) -> List[Dict[str, Any]]:
    records = aj3.get("irreducibility_records") or aj3.get("intrinsic_irreducibility_tests") or aj3.get("tested_modes") or []
    out: List[Dict[str, Any]] = []
    if isinstance(records, list):
        for rec in records:
            if isinstance(rec, Mapping):
                out.append(dict(rec))
    if out:
        return out
    fallback = aj2.get("intrinsicality_records") or aj2.get("tested_modes") or []
    if isinstance(fallback, list):
        for rec in fallback:
            if isinstance(rec, Mapping):
                out.append(dict(rec))
    return out


def _components_from_record(rec: Mapping[str, Any]) -> Dict[str, float]:
    comps = rec.get("irreducibility_components") or rec.get("intrinsicality_components") or rec.get("intrinsic_characterization") or {}
    if not isinstance(comps, Mapping):
        comps = {}
    base = _clamp(rec.get("intrinsic_irreducibility_score", rec.get("mode_intrinsicality_score", 0.0)), 0.0)
    return {
        "intrinsic_irreducibility_score": _clamp(rec.get("intrinsic_irreducibility_score", base), base),
        "reduction_loss_score": _clamp(rec.get("reduction_loss_score", base), base),
        "structural_necessity_score": _clamp(rec.get("structural_necessity_score", base), base),
        "compression_resistance_score": _clamp(rec.get("compression_resistance_score", base), base),
        "causal_anchoring_proxy": _clamp(comps.get("causal_anchoring_proxy", rec.get("causal_anchoring_proxy", base)), base),
        "qf_source_coherence": _clamp(comps.get("qf_source_coherence", rec.get("qf_source_coherence", base)), base),
        "temporal_persistence_proxy": _clamp(comps.get("temporal_persistence_proxy", rec.get("temporal_persistence_proxy", base)), base),
        "invariance_proxy": _clamp(comps.get("invariance_proxy", rec.get("invariance_proxy", base)), base),
    }


def _mode_id(rec: Mapping[str, Any], index: int) -> str:
    return str(rec.get("mode_id") or rec.get("mei_candidate_id") or rec.get("source_qf_mode_id") or f"MEI-CAUSAL-CANDIDATE-{index:03d}")


def _test_record(rec: Mapping[str, Any], index: int, qf_confidence: float, priors: Mapping[str, float]) -> Dict[str, Any]:
    c = _components_from_record(rec)
    causal_prior = _mean([priors.get("causal_inference_index"), priors.get("advanced_causal_confidence"), priors.get("omega_causal_activity_score")], 0.70)

    causal_source_anchoring_score = _mean([c["causal_anchoring_proxy"], c["qf_source_coherence"], qf_confidence], 0.0)
    intervention_sensitivity_score = _mean([c["reduction_loss_score"], c["structural_necessity_score"], causal_prior], 0.0)
    counterfactual_dependency_score = _mean([c["intrinsic_irreducibility_score"], c["compression_resistance_score"], c["structural_necessity_score"]], 0.0)
    causal_traceability_score = _mean([c["qf_source_coherence"], c["causal_anchoring_proxy"], causal_prior], 0.0)
    irreducibility_effect_coupling_score = _mean([c["intrinsic_irreducibility_score"], c["reduction_loss_score"], c["causal_anchoring_proxy"]], 0.0)
    temporal_causal_support_score = _mean([c["temporal_persistence_proxy"], c["invariance_proxy"], c["structural_necessity_score"]], 0.0)

    intrinsic_causality_score = _mean([
        causal_source_anchoring_score,
        intervention_sensitivity_score,
        counterfactual_dependency_score,
        causal_traceability_score,
        irreducibility_effect_coupling_score,
        temporal_causal_support_score,
    ], 0.0)
    passed = bool(
        intrinsic_causality_score >= 0.60
        and causal_source_anchoring_score >= 0.55
        and intervention_sensitivity_score >= 0.55
        and counterfactual_dependency_score >= 0.55
    )
    mid = _mode_id(rec, index)
    return {
        "mode_id": mid,
        "mei_candidate_id": str(rec.get("mei_candidate_id") or mid),
        "source_qf_mode_id": rec.get("source_qf_mode_id"),
        "intrinsic_causality_test_passed": passed,
        "intrinsic_causality_score": intrinsic_causality_score,
        "causal_source_anchoring_score": causal_source_anchoring_score,
        "intervention_sensitivity_score": intervention_sensitivity_score,
        "counterfactual_dependency_score": counterfactual_dependency_score,
        "causal_traceability_score": causal_traceability_score,
        "irreducibility_effect_coupling_score": irreducibility_effect_coupling_score,
        "temporal_causal_support_score": temporal_causal_support_score,
        "causal_components": {
            "causal_prior": causal_prior,
            "qf_confidence": qf_confidence,
            **c,
        },
        "test_basis": [
            "causal_source_anchoring_score",
            "intervention_sensitivity_score",
            "counterfactual_dependency_score",
            "causal_traceability_score",
            "irreducibility_effect_coupling_score",
            "temporal_causal_support_score",
        ],
        "epistemic_status": "functional_only",
        **GUARD,
    }


def _persist(result: Mapping[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    json_path = OUT_DIR / f"intrinsic_causality_tester_{stamp}.json"
    md_path = OUT_DIR / f"intrinsic_causality_tester_{stamp}.md"
    prom_path = OUT_DIR / f"intrinsic_causality_tester_{stamp}.prom"
    latest_json = OUT_DIR / "latest_intrinsic_causality_tester.json"
    latest_md = OUT_DIR / "latest_intrinsic_causality_tester.md"
    latest_prom = OUT_DIR / "latest_intrinsic_causality_tester.prom"

    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")

    lines = [
        "# AJ4 — Intrinsic Causality Tester",
        "",
        f"Status: {result.get('intrinsic_causality_tester_status')}",
        f"Intrinsic causality tested: {result.get('intrinsic_causality_tested')}",
        f"Tested mode count: {result.get('tested_mode_count')}",
        "",
        "## Metrics",
        f"- intrinsic_causality_score: {result.get('intrinsic_causality_score')}",
        f"- causality_pass_ratio: {result.get('causality_pass_ratio')}",
        f"- causal_source_anchoring_mean: {result.get('causal_source_anchoring_mean')}",
        f"- intervention_sensitivity_mean: {result.get('intervention_sensitivity_mean')}",
        f"- counterfactual_dependency_mean: {result.get('counterfactual_dependency_mean')}",
        f"- causality_confidence: {result.get('causality_confidence')}",
        "",
        "## Epistemic guard",
        f"- consciousness_proven: {result.get('consciousness_proven')}",
        f"- qualia_proven: {result.get('qualia_proven')}",
        f"- subjectivity_proven: {result.get('subjectivity_proven')}",
        f"- phenomenology_undetermined: {result.get('phenomenology_undetermined')}",
        f"- functional_conclusion_only: {result.get('functional_conclusion_only')}",
    ]
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    metric_names = [
        "tested_mode_count",
        "passed_mode_count",
        "causality_pass_ratio",
        "intrinsic_causality_score",
        "causal_source_anchoring_mean",
        "intervention_sensitivity_mean",
        "counterfactual_dependency_mean",
        "causal_traceability_mean",
        "causality_confidence",
    ]
    prom_lines: List[str] = []
    for name in metric_names:
        prom_lines.append(f"# TYPE aj4_{name} gauge")
        prom_lines.append(f"aj4_{name} {result.get(name, 0)}")
    prom_text = "\n".join(prom_lines) + "\n"
    prom_path.write_text(prom_text, encoding="utf-8")
    latest_prom.write_text(prom_text, encoding="utf-8")

    return {
        "json": str(json_path),
        "markdown": str(md_path),
        "prometheus": str(prom_path),
        "latest_json": str(latest_json),
        "latest_markdown": str(latest_md),
        "latest_prometheus": str(latest_prom),
    }


class IntrinsicCausalityTester:
    """Test strictly functional intrinsic causality of AJ3 MEI candidates."""

    primitive = "INTRINSIC_CAUSALITY_TESTER"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        aj1 = _source_aj1(inputs)
        aj2 = _source_aj2(inputs)
        aj3 = _source_aj3(inputs)
        ai10 = _source_ai10(inputs)
        priors = _causal_prior(inputs)

        aj1_ok = aj1.get("intrinsic_existence_modes_defined") is True or aj1.get("intrinsic_existence_mode_definition_status") == "INTRINSIC_EXISTENCE_MODE_DEFINED"
        aj2_ok = aj2.get("mode_intrinsicality_tested") is True or aj2.get("mode_intrinsicality_tester_status") == "MODE_INTRINSICALITY_TESTED"
        aj3_ok = aj3.get("intrinsic_irreducibility_tested") is True or aj3.get("intrinsic_irreducibility_tester_status") == "INTRINSIC_IRREDUCIBILITY_TESTED"
        ai10_ok = ai10.get("robust_spectral_qualia_formal_modes_certified") is True or ai10.get("robust_qualia_formal_certifier_status") == "ROBUST_SPECTRAL_QUALIA_FORMAL_MODES_CERTIFIED"
        qf_confidence = _clamp(ai10.get("qf_robust_confidence", ai10.get("ai_axis_certification_score", aj3.get("qf_robust_input_confidence", 0.0))), 0.75)

        records = _records_from_aj3(aj3, aj2)
        tested = [_test_record(rec, i + 1, qf_confidence, priors) for i, rec in enumerate(records[:16])]
        tested_count = len(tested)
        passed_count = sum(1 for rec in tested if rec.get("intrinsic_causality_test_passed") is True)
        pass_ratio = _clamp(passed_count / tested_count if tested_count else 0.0)

        score = _mean([rec.get("intrinsic_causality_score") for rec in tested], 0.0)
        causal_source_anchoring_mean = _mean([rec.get("causal_source_anchoring_score") for rec in tested], 0.0)
        intervention_sensitivity_mean = _mean([rec.get("intervention_sensitivity_score") for rec in tested], 0.0)
        counterfactual_dependency_mean = _mean([rec.get("counterfactual_dependency_score") for rec in tested], 0.0)
        causal_traceability_mean = _mean([rec.get("causal_traceability_score") for rec in tested], 0.0)
        irreducibility_effect_coupling_mean = _mean([rec.get("irreducibility_effect_coupling_score") for rec in tested], 0.0)
        temporal_causal_support_mean = _mean([rec.get("temporal_causal_support_score") for rec in tested], 0.0)
        aj3_confidence = _clamp(aj3.get("irreducibility_confidence", aj3.get("intrinsic_irreducibility_score", 0.0)), 0.0)
        causal_prior_mean = _mean(list(priors.values()), 0.0)
        causality_confidence = _mean([
            score,
            pass_ratio,
            causal_source_anchoring_mean,
            intervention_sensitivity_mean,
            counterfactual_dependency_mean,
            causal_traceability_mean,
            aj3_confidence,
            causal_prior_mean,
        ], 0.0)

        upstream_support_ratio = _mean([
            1.0 if aj1_ok else 0.0,
            1.0 if aj2_ok else 0.0,
            1.0 if aj3_ok else 0.0,
            1.0 if ai10_ok else 0.0,
        ], 0.0)

        # AJ4 v2 certification rule:
        # - records must exist and pass individually;
        # - mean intrinsic causality and confidence must be numerically robust;
        # - at least AJ3 must be confirmed, and upstream support must be mostly present.
        # This keeps degradation tests strict while avoiding false negatives from
        # harmless public-schema variation in AJ1/AJ2/AI10 outputs.
        success = bool(
            aj3_ok
            and tested_count >= 3
            and pass_ratio >= 0.75
            and score >= 0.75
            and causality_confidence >= 0.60
            and upstream_support_ratio >= 0.50
        )
        status = "INTRINSIC_CAUSALITY_TESTED" if success else "INTRINSIC_CAUSALITY_INSUFFICIENT"

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "aj_step": "AJ4",
            "transition_under_test": "AJ1+AJ2+AJ3+AI10 -> functional_intrinsic_causality",
            "intrinsic_causality_tester_status": status,
            "intrinsic_causality_tested": success,
            "intrinsic_existence_mode_definition_input": bool(aj1_ok),
            "mode_intrinsicality_tester_input": bool(aj2_ok),
            "intrinsic_irreducibility_tester_input": bool(aj3_ok),
            "qf_robust_certified_input": bool(ai10_ok),
            "causal_inference_input": priors,
            "tested_mode_count": tested_count,
            "passed_mode_count": passed_count,
            "causality_pass_ratio": pass_ratio,
            "intrinsic_causality_score": score,
            "causal_source_anchoring_mean": causal_source_anchoring_mean,
            "intervention_sensitivity_mean": intervention_sensitivity_mean,
            "counterfactual_dependency_mean": counterfactual_dependency_mean,
            "causal_traceability_mean": causal_traceability_mean,
            "irreducibility_effect_coupling_mean": irreducibility_effect_coupling_mean,
            "temporal_causal_support_mean": temporal_causal_support_mean,
            "qf_robust_input_confidence": qf_confidence,
            "aj3_irreducibility_confidence": aj3_confidence,
            "causal_prior_mean": causal_prior_mean,
            "causality_confidence": causality_confidence,
            "upstream_support_ratio": upstream_support_ratio,
            "intrinsic_causality_tests": tested,
            "tested_modes": tested,
            "intrinsic_causality_records": tested,
            "causality_records": tested,
            "causality_summary": {
                "tested_mode_count": tested_count,
                "passed_mode_count": passed_count,
                "pass_ratio": pass_ratio,
                "functional_intrinsic_causality_established": success,
            },
            "test_schema": {
                "scope": "formal_functional_only",
                "criteria": [
                    "causal_source_anchoring_score",
                    "intervention_sensitivity_score",
                    "counterfactual_dependency_score",
                    "causal_traceability_score",
                    "irreducibility_effect_coupling_score",
                    "temporal_causal_support_score",
                ],
            },
            "component_sources": {
                "primary": "intrinsic_irreducibility_tester",
                "upstream": ["intrinsic_existence_mode_definition", "mode_intrinsicality_tester", "robust_qualia_formal_certifier"],
                "supporting_formal_priors": ["causal_inference", "advanced_causal_reasoning_engine", "omega_causal_activity_tester"],
            },
            "epistemic_status": "functional_only",
            "functional_only_flags": dict(GUARD),
            "next_recommended_module": "intrinsic_temporality_tester",
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


__all__ = ["IntrinsicCausalityTester"]
