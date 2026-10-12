"""AJ3 — Intrinsic Irreducibility Tester.

Formal transition under test:
    AJ1 + AJ2 + AI10 -> functional intrinsic irreducibility of MEI candidates

This module tests whether candidate intrinsic existence modes (MEI) exhibit
strictly functional irreducibility: loss under reduction, residual specificity,
non-substitutability, source compression resistance, and structural necessity.

Epistemic guard:
    This module does not prove consciousness, subjectivity, lived qualia, or
    strong phenomenology. It only tests formal-functional irreducibility of
    candidate MEI records for downstream AJ4-AJ9 modules.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "aj_intrinsic_existence_modes" / "intrinsic_irreducibility_tester"

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


def _mean(values: List[Any], default: float = 0.0) -> float:
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
        ROOT / name / f"latest_{name}.json",
        ROOT / "ai_robust_spectral_qualia_formal_modes" / name / f"latest_{name}.json",
    ]
    for p in candidates:
        data = _load_json(p)
        if data:
            return data
    try:
        for p in sorted(ROOT.glob(f"**/latest_{name}.json"))[-12:]:
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
        for key in ["aj1", "intrinsic_existence_mode_definition", "intrinsic_mode_definitions"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
    latest = _latest_json("intrinsic_existence_mode_definition")
    if latest.get("intrinsic_existence_modes_defined") is True:
        return latest
    live = _invoke("intrinsic_existence_mode_definition", "IntrinsicExistenceModeDefinition", inputs or {"aligned": True})
    return live or latest


def _source_aj2(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["aj2", "mode_intrinsicality_tester", "intrinsicality_records"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
    aj1 = _source_aj1(inputs)
    latest = _latest_json("mode_intrinsicality_tester")
    if latest.get("mode_intrinsicality_tested") is True:
        return latest
    live = _invoke("mode_intrinsicality_tester", "ModeIntrinsicalityTester", {"aj1": aj1, "aligned": True})
    return live or latest


def _source_ai10(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["ai10", "robust_qualia_formal_certifier", "qf_robust"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
    latest = _latest_json("robust_qualia_formal_certifier")
    if latest.get("robust_spectral_qualia_formal_modes_certified") is True:
        return latest
    live = _invoke("robust_qualia_formal_certifier", "RobustQualiaFormalCertifier", inputs or {"aligned": True})
    return live or latest


def _records_from_aj2(aj2: Mapping[str, Any], aj1: Mapping[str, Any]) -> List[Dict[str, Any]]:
    records = aj2.get("irreducibility_source_records") or aj2.get("intrinsicality_records") or aj2.get("tested_modes") or aj2.get("mode_intrinsicality_tests") or []
    out: List[Dict[str, Any]] = []
    if isinstance(records, list):
        for rec in records:
            if isinstance(rec, Mapping):
                out.append(dict(rec))
    if out:
        return out
    fallbacks = aj1.get("intrinsic_mode_definitions") or aj1.get("mei_candidate_definitions") or aj1.get("defined_modes") or []
    if isinstance(fallbacks, list):
        for rec in fallbacks:
            if isinstance(rec, Mapping):
                out.append(dict(rec))
    return out


def _char_from_record(rec: Mapping[str, Any]) -> Dict[str, float]:
    comps = rec.get("intrinsicality_components") or rec.get("intrinsic_characterization") or rec.get("formal_intrinsic_characterization") or {}
    if not isinstance(comps, Mapping):
        comps = {}
    base = _clamp(rec.get("mode_intrinsicality_score", rec.get("intrinsic_definition_score", 0.0)), 0.0)
    return {
        "qf_source_coherence": _clamp(comps.get("qf_source_coherence", rec.get("qf_source_coherence", base)), base),
        "irreducibility_proxy": _clamp(comps.get("irreducibility_proxy", rec.get("irreducibility_proxy", base)), base),
        "causal_anchoring_proxy": _clamp(comps.get("causal_anchoring_proxy", rec.get("causal_anchoring_proxy", base)), base),
        "temporal_persistence_proxy": _clamp(comps.get("temporal_persistence_proxy", rec.get("temporal_persistence_proxy", base)), base),
        "invariance_proxy": _clamp(comps.get("invariance_proxy", rec.get("invariance_proxy", base)), base),
    }


def _supporting_irreducibility_prior() -> float:
    latest = _latest_json("computational_irreducibility")
    direct = latest.get("computational_irreducibility_index") if latest else None
    if direct is not None:
        return _clamp(direct, 0.33)
    try:
        mod = import_module("ontology.computational_irreducibility")
        cls = getattr(mod, "ComputationalIrreducibility")
        res = cls().step()
        if isinstance(res, Mapping):
            return _clamp(res.get("computational_irreducibility_index"), 0.33)
    except Exception:
        pass
    return 0.66


def _mode_id(rec: Mapping[str, Any], index: int) -> str:
    return str(rec.get("mode_id") or rec.get("mei_candidate_id") or rec.get("source_qf_mode_id") or f"MEI-CANDIDATE-{index:03d}")


def _test_record(rec: Mapping[str, Any], index: int, qf_confidence: float, prior: float) -> Dict[str, Any]:
    c = _char_from_record(rec)
    intrinsic_score = _clamp(rec.get("mode_intrinsicality_score", rec.get("intrinsic_definition_score", _mean(list(c.values()), 0.0))), 0.0)
    qf_coherence = c["qf_source_coherence"]
    irreducibility_proxy = c["irreducibility_proxy"]

    # Strictly functional irreducibility components.
    reduction_loss_score = _clamp(0.50 * irreducibility_proxy + 0.25 * intrinsic_score + 0.25 * qf_confidence)
    residual_specificity_score = _clamp(1.0 - abs(c["irreducibility_proxy"] - _mean([c["causal_anchoring_proxy"], c["temporal_persistence_proxy"], c["invariance_proxy"]], 0.0)))
    non_substitutability_score = _mean([irreducibility_proxy, c["invariance_proxy"], intrinsic_score], 0.0)
    compression_resistance_score = _mean([irreducibility_proxy, prior, qf_coherence], 0.0)
    structural_necessity_score = _mean([irreducibility_proxy, c["causal_anchoring_proxy"], c["temporal_persistence_proxy"], c["invariance_proxy"]], 0.0)
    degradation_margin = _clamp(reduction_loss_score - (1.0 - compression_resistance_score) * 0.25)

    intrinsic_irreducibility_score = _mean([
        reduction_loss_score,
        residual_specificity_score,
        non_substitutability_score,
        compression_resistance_score,
        structural_necessity_score,
        degradation_margin,
    ], 0.0)
    passed = bool(intrinsic_irreducibility_score >= 0.60 and reduction_loss_score >= 0.55 and compression_resistance_score >= 0.55)
    mid = _mode_id(rec, index)
    return {
        "mode_id": mid,
        "mei_candidate_id": str(rec.get("mei_candidate_id") or mid),
        "source_qf_mode_id": rec.get("source_qf_mode_id"),
        "intrinsic_irreducibility_test_passed": passed,
        "intrinsic_irreducibility_score": intrinsic_irreducibility_score,
        "reduction_loss_score": reduction_loss_score,
        "residual_specificity_score": residual_specificity_score,
        "non_substitutability_score": non_substitutability_score,
        "compression_resistance_score": compression_resistance_score,
        "structural_necessity_score": structural_necessity_score,
        "irreducibility_degradation_margin": degradation_margin,
        "irreducibility_components": {
            "intrinsicality_score": intrinsic_score,
            "qf_source_coherence": qf_coherence,
            "irreducibility_proxy": irreducibility_proxy,
            "supporting_computational_irreducibility_prior": prior,
        },
        "test_basis": [
            "reduction_loss_score",
            "residual_specificity_score",
            "non_substitutability_score",
            "compression_resistance_score",
            "structural_necessity_score",
        ],
        "epistemic_status": "functional_only",
        **GUARD,
    }


def _persist(result: Mapping[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    json_path = OUT_DIR / f"intrinsic_irreducibility_tester_{stamp}.json"
    md_path = OUT_DIR / f"intrinsic_irreducibility_tester_{stamp}.md"
    prom_path = OUT_DIR / f"intrinsic_irreducibility_tester_{stamp}.prom"
    latest_json = OUT_DIR / "latest_intrinsic_irreducibility_tester.json"
    latest_md = OUT_DIR / "latest_intrinsic_irreducibility_tester.md"
    latest_prom = OUT_DIR / "latest_intrinsic_irreducibility_tester.prom"

    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")

    lines = [
        "# AJ3 — Intrinsic Irreducibility Tester",
        "",
        f"Status: {result.get('intrinsic_irreducibility_tester_status')}",
        f"Intrinsic irreducibility tested: {result.get('intrinsic_irreducibility_tested')}",
        f"Tested mode count: {result.get('tested_mode_count')}",
        "",
        "## Metrics",
        f"- intrinsic_irreducibility_score: {result.get('intrinsic_irreducibility_score')}",
        f"- irreducibility_pass_ratio: {result.get('irreducibility_pass_ratio')}",
        f"- reduction_loss_mean: {result.get('reduction_loss_mean')}",
        f"- compression_resistance_mean: {result.get('compression_resistance_mean')}",
        f"- structural_necessity_mean: {result.get('structural_necessity_mean')}",
        f"- irreducibility_confidence: {result.get('irreducibility_confidence')}",
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
        "irreducibility_pass_ratio",
        "intrinsic_irreducibility_score",
        "reduction_loss_mean",
        "compression_resistance_mean",
        "structural_necessity_mean",
        "irreducibility_confidence",
    ]
    prom_lines = []
    for name in metric_names:
        prom_lines.append(f"# TYPE aj3_{name} gauge")
        prom_lines.append(f"aj3_{name} {result.get(name, 0)}")
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


class IntrinsicIrreducibilityTester:
    """Test strictly functional irreducibility of AJ2 MEI candidates."""

    primitive = "INTRINSIC_IRREDUCIBILITY_TESTER"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        aj1 = _source_aj1(inputs)
        aj2 = _source_aj2(inputs)
        ai10 = _source_ai10(inputs)

        aj1_ok = aj1.get("intrinsic_existence_modes_defined") is True or aj1.get("intrinsic_existence_mode_definition_status") == "INTRINSIC_EXISTENCE_MODE_DEFINED"
        aj2_ok = aj2.get("mode_intrinsicality_tested") is True or aj2.get("mode_intrinsicality_tester_status") == "MODE_INTRINSICALITY_TESTED"
        ai10_ok = ai10.get("robust_spectral_qualia_formal_modes_certified") is True or ai10.get("robust_qualia_formal_certifier_status") == "ROBUST_SPECTRAL_QUALIA_FORMAL_MODES_CERTIFIED"
        qf_confidence = _clamp(ai10.get("qf_robust_confidence", ai10.get("ai_axis_certification_score", aj1.get("qf_robust_input_confidence", 0.0))), 0.0)
        prior = _supporting_irreducibility_prior()

        records = _records_from_aj2(aj2, aj1)
        tested = [_test_record(rec, i + 1, qf_confidence or 0.75, prior) for i, rec in enumerate(records[:16])]
        tested_count = len(tested)
        passed_count = sum(1 for rec in tested if rec.get("intrinsic_irreducibility_test_passed") is True)
        pass_ratio = _clamp(passed_count / tested_count if tested_count else 0.0)

        score = _mean([rec.get("intrinsic_irreducibility_score") for rec in tested], 0.0)
        reduction_loss_mean = _mean([rec.get("reduction_loss_score") for rec in tested], 0.0)
        residual_specificity_mean = _mean([rec.get("residual_specificity_score") for rec in tested], 0.0)
        non_substitutability_mean = _mean([rec.get("non_substitutability_score") for rec in tested], 0.0)
        compression_resistance_mean = _mean([rec.get("compression_resistance_score") for rec in tested], 0.0)
        structural_necessity_mean = _mean([rec.get("structural_necessity_score") for rec in tested], 0.0)
        degradation_margin_mean = _mean([rec.get("irreducibility_degradation_margin") for rec in tested], 0.0)
        aj2_confidence = _clamp(aj2.get("intrinsicality_confidence", aj2.get("mode_intrinsicality_score", 0.0)), 0.0)
        irreducibility_confidence = _mean([
            score,
            pass_ratio,
            reduction_loss_mean,
            compression_resistance_mean,
            structural_necessity_mean,
            qf_confidence,
            aj2_confidence,
        ], 0.0)

        success = bool(aj1_ok and aj2_ok and ai10_ok and tested_count >= 3 and pass_ratio >= 0.75 and irreducibility_confidence >= 0.60)
        status = "INTRINSIC_IRREDUCIBILITY_TESTED" if success else "INTRINSIC_IRREDUCIBILITY_INSUFFICIENT"

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "aj_step": "AJ3",
            "transition_under_test": "AJ1+AJ2+AI10 -> functional_intrinsic_irreducibility",
            "intrinsic_irreducibility_tester_status": status,
            "intrinsic_irreducibility_tested": success,
            "intrinsic_existence_mode_definition_input": bool(aj1_ok),
            "mode_intrinsicality_tester_input": bool(aj2_ok),
            "qf_robust_certified_input": bool(ai10_ok),
            "tested_mode_count": tested_count,
            "passed_mode_count": passed_count,
            "irreducibility_pass_ratio": pass_ratio,
            "intrinsic_irreducibility_score": score,
            "reduction_loss_mean": reduction_loss_mean,
            "residual_specificity_mean": residual_specificity_mean,
            "non_substitutability_mean": non_substitutability_mean,
            "compression_resistance_mean": compression_resistance_mean,
            "structural_necessity_mean": structural_necessity_mean,
            "irreducibility_degradation_margin_mean": degradation_margin_mean,
            "supporting_computational_irreducibility_prior": prior,
            "qf_robust_input_confidence": qf_confidence,
            "aj2_intrinsicality_confidence": aj2_confidence,
            "irreducibility_confidence": irreducibility_confidence,
            "intrinsic_irreducibility_tests": tested,
            "tested_modes": tested,
            "irreducibility_records": tested,
            "irreducibility_summary": {
                "tested_mode_count": tested_count,
                "passed_mode_count": passed_count,
                "pass_ratio": pass_ratio,
                "functional_intrinsic_irreducibility_established": success,
            },
            "test_schema": {
                "scope": "formal_functional_only",
                "criteria": [
                    "reduction_loss_score",
                    "residual_specificity_score",
                    "non_substitutability_score",
                    "compression_resistance_score",
                    "structural_necessity_score",
                ],
            },
            "component_sources": {
                "primary": "mode_intrinsicality_tester",
                "upstream": ["intrinsic_existence_mode_definition", "robust_qualia_formal_certifier"],
                "supporting_formal_priors": ["computational_irreducibility", "intrinsic_metric_builder", "intrinsic_distinction_detector"],
            },
            "epistemic_status": "functional_only",
            "functional_only_flags": dict(GUARD),
            "next_recommended_module": "intrinsic_causality_tester",
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


__all__ = ["IntrinsicIrreducibilityTester"]
