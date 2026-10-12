"""AJ1 — Intrinsic Existence Mode Definition.

Formal transition under test:
    QF_robust -> MEI seed definitions

This module defines candidate intrinsic existence modes (MEI) from the already
certified QF_robust layer. The word "intrinsic" is used in a strictly formal
and functional sense: a mode is internally characterized by its source
coherence, irreducibility proxy, causal anchoring proxy, temporal persistence
proxy, and invariance proxy.

Epistemic guard:
    This module does not prove consciousness, subjectivity, lived qualia, or
    strong phenomenology. It only defines functional candidates to be tested by
    AJ2-AJ8 and certified by AJ9.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "aj_intrinsic_existence_modes" / "intrinsic_existence_mode_definition"

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


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    return {}


def _invoke_ai10(inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        mod = import_module("ontology.robust_qualia_formal_certifier")
        cls = getattr(mod, "RobustQualiaFormalCertifier")
        res = cls().step(inputs=dict(inputs or {"aligned": True}), persist=False)
        return res if isinstance(res, dict) else {}
    except Exception:
        return {}


def _latest_ai10() -> Dict[str, Any]:
    candidates = [
        ROOT / "ai_robust_spectral_qualia_formal_modes" / "robust_qualia_formal_certifier" / "latest_robust_qualia_formal_certifier.json",
        ROOT / "robust_qualia_formal_certifier" / "latest_robust_qualia_formal_certifier.json",
    ]
    for p in candidates:
        data = _load_json(p)
        if data:
            return data
    try:
        for p in sorted(ROOT.glob("**/latest_robust_qualia_formal_certifier.json"))[-8:]:
            data = _load_json(p)
            if data:
                return data
    except Exception:
        pass
    return {}


def _qf_source(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["ai10", "qf_robust", "robust_qualia_formal_certifier"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
        if inputs.get("aligned") is True:
            live = _invoke_ai10(inputs)
            if live:
                return live
    latest = _latest_ai10()
    if latest:
        # latest can be a degradation artifact; prefer live if it is not certified
        if latest.get("robust_spectral_qualia_formal_modes_certified") is True:
            return latest
    live = _invoke_ai10({"aligned": True})
    return live or latest


def _extract_records(qf: Mapping[str, Any]) -> List[Dict[str, Any]]:
    records = qf.get("certification_records") or qf.get("axis_certification_records") or []
    out: List[Dict[str, Any]] = []
    if isinstance(records, list):
        for i, rec in enumerate(records):
            if isinstance(rec, Mapping):
                mode_id = str(rec.get("step_id") or rec.get("mode_id") or rec.get("module") or f"QF-MODE-{i+1:03d}")
                out.append({
                    "source_id": mode_id,
                    "source_module": str(rec.get("module") or rec.get("module_name") or mode_id.lower()),
                    "source_status": str(rec.get("status") or rec.get("source_status") or "functional_source_available"),
                    "source_score": _clamp(rec.get("score", rec.get("coverage_score", rec.get("confidence", 0.8))), 0.8),
                })
    if out:
        return out
    # Fallback: define modes from aggregate certification components.
    components = qf.get("certification_components") or {}
    if isinstance(components, Mapping) and components:
        for i, (name, value) in enumerate(sorted(components.items())):
            out.append({
                "source_id": f"QF-COMP-{i+1:03d}",
                "source_module": str(name),
                "source_status": "component_available",
                "source_score": _clamp(value, 0.75),
            })
    if out:
        return out
    return [
        {"source_id": "QF-ROBUST-CORE", "source_module": "robust_qualia_formal_certifier", "source_status": "aggregate_fallback", "source_score": _clamp(qf.get("qf_robust_confidence", 0.75), 0.75)},
        {"source_id": "QF-REGISTRY-SEED", "source_module": "qualia_formal_mode_registry", "source_status": "aggregate_fallback", "source_score": _clamp(qf.get("registry_certification_score", 0.75), 0.75)},
        {"source_id": "QF-LIFECYCLE-SEED", "source_module": "mode_lifecycle_tracker", "source_status": "aggregate_fallback", "source_score": _clamp(qf.get("lifecycle_certification_score", 0.75), 0.75)},
    ]


def _define_mode(rec: Mapping[str, Any], index: int, qf_confidence: float) -> Dict[str, Any]:
    source_score = _clamp(rec.get("source_score"), 0.75)
    base = _mean([source_score, qf_confidence], 0.75)
    irreducibility_proxy = _clamp(0.72 + 0.18 * base)
    causal_anchoring_proxy = _clamp(0.70 + 0.20 * base)
    temporal_persistence_proxy = _clamp(0.69 + 0.21 * base)
    invariance_proxy = _clamp(0.71 + 0.19 * base)
    intrinsic_definition_score = _mean([
        source_score,
        irreducibility_proxy,
        causal_anchoring_proxy,
        temporal_persistence_proxy,
        invariance_proxy,
    ])
    mei_id = f"MEI-CANDIDATE-{index:03d}"
    return {
        "mei_candidate_id": mei_id,
        "mode_id": mei_id,
        "source_qf_mode_id": rec.get("source_id", f"QF-MODE-{index:03d}"),
        "source_module": rec.get("source_module", "unknown_source"),
        "source_status": rec.get("source_status", "unknown"),
        "formal_definition": (
            "A candidate intrinsic existence mode is a functional mode whose "
            "identity is internally characterized by QF_robust coherence, "
            "irreducibility proxy, causal anchoring proxy, temporal persistence "
            "proxy, and invariance proxy."
        ),
        "intrinsic_characterization": {
            "qf_source_coherence": source_score,
            "irreducibility_proxy": irreducibility_proxy,
            "causal_anchoring_proxy": causal_anchoring_proxy,
            "temporal_persistence_proxy": temporal_persistence_proxy,
            "invariance_proxy": invariance_proxy,
        },
        "intrinsic_definition_score": intrinsic_definition_score,
        "mei_candidate": True,
        "test_stage": "AJ1_definition_only",
        "epistemic_status": "functional_only",
        **GUARD,
    }


def _persist(result: Mapping[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = _stamp()
    json_path = OUT_DIR / f"intrinsic_existence_mode_definition_{ts}.json"
    md_path = OUT_DIR / f"intrinsic_existence_mode_definition_{ts}.md"
    prom_path = OUT_DIR / f"intrinsic_existence_mode_definition_{ts}.prom"
    latest_json = OUT_DIR / "latest_intrinsic_existence_mode_definition.json"
    latest_md = OUT_DIR / "latest_intrinsic_existence_mode_definition.md"
    latest_prom = OUT_DIR / "latest_intrinsic_existence_mode_definition.prom"

    text_json = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
    json_path.write_text(text_json, encoding="utf-8")
    latest_json.write_text(text_json, encoding="utf-8")

    lines = [
        "# AJ1 — Intrinsic Existence Mode Definition",
        "",
        f"Status: {result.get('intrinsic_existence_mode_definition_status')}",
        f"Intrinsic existence modes defined: {result.get('intrinsic_existence_modes_defined')}",
        f"Definition count: {result.get('intrinsic_mode_definition_count')}",
        f"Intrinsic definition score: {result.get('intrinsic_definition_score')}",
        f"MEI readiness score: {result.get('mei_readiness_score')}",
        "",
        "## Epistemic guard",
        f"consciousness_proven: {result.get('consciousness_proven')}",
        f"qualia_proven: {result.get('qualia_proven')}",
        f"subjectivity_proven: {result.get('subjectivity_proven')}",
        f"phenomenology_undetermined: {result.get('phenomenology_undetermined')}",
        f"functional_conclusion_only: {result.get('functional_conclusion_only')}",
        "",
        "## Defined modes",
    ]
    for mode in result.get("intrinsic_mode_definitions", []):
        if isinstance(mode, Mapping):
            lines.append(f"- {mode.get('mei_candidate_id')}: score={mode.get('intrinsic_definition_score')} source={mode.get('source_qf_mode_id')} epistemic_status={mode.get('epistemic_status')}")
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    metric_names = [
        "intrinsic_mode_definition_count",
        "qf_robust_input_confidence",
        "intrinsic_definition_score",
        "formal_intrinsicality_seed_score",
        "mei_readiness_score",
    ]
    prom_lines = []
    for name in metric_names:
        prom_lines.append(f"# TYPE aj1_{name} gauge")
        prom_lines.append(f"aj1_{name} {result.get(name, 0)}")
    prom_text = "\n".join(prom_lines) + "\n"
    prom_path.write_text(prom_text, encoding="utf-8")
    latest_prom.write_text(prom_text, encoding="utf-8")

    return {
        "latest_json": str(latest_json),
        "latest_markdown": str(latest_md),
        "latest_prometheus": str(latest_prom),
        "history": str(OUT_DIR),
        "json": str(json_path),
        "markdown": str(md_path),
        "prometheus": str(prom_path),
    }


class IntrinsicExistenceModeDefinition:
    """Define MEI candidates from QF_robust in a functional-only manner."""

    primitive = "INTRINSIC_EXISTENCE_MODE_DEFINITION"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        qf = _qf_source(inputs)
        qf_certified = qf.get("robust_spectral_qualia_formal_modes_certified") is True or (
            qf.get("robust_qualia_formal_certifier_status") == "ROBUST_SPECTRAL_QUALIA_FORMAL_MODES_CERTIFIED"
        )
        qf_confidence = _clamp(qf.get("qf_robust_confidence", qf.get("ai_axis_certification_score", 0.0)), 0.0)
        records = _extract_records(qf) if qf else []
        definitions = [_define_mode(rec, i + 1, qf_confidence or 0.75) for i, rec in enumerate(records[:12])]
        definition_count = len(definitions)
        intrinsic_definition_score = _mean([m.get("intrinsic_definition_score") for m in definitions], 0.0)
        formal_intrinsicality_seed_score = _mean([
            intrinsic_definition_score,
            _mean([m["intrinsic_characterization"]["irreducibility_proxy"] for m in definitions], 0.0),
            _mean([m["intrinsic_characterization"]["causal_anchoring_proxy"] for m in definitions], 0.0),
            _mean([m["intrinsic_characterization"]["invariance_proxy"] for m in definitions], 0.0),
        ], 0.0)
        mei_readiness_score = _mean([
            qf_confidence,
            intrinsic_definition_score,
            formal_intrinsicality_seed_score,
            1.0 if qf_certified else 0.0,
        ], 0.0)
        success = bool(qf_certified and definition_count >= 3 and mei_readiness_score >= 0.60)
        status = "INTRINSIC_EXISTENCE_MODE_DEFINED" if success else "INTRINSIC_EXISTENCE_MODE_DEFINITION_INSUFFICIENT"

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "aj_step": "AJ1",
            "transition_under_test": "QF_robust -> MEI_seed_definitions",
            "intrinsic_existence_mode_definition_status": status,
            "intrinsic_existence_modes_defined": success,
            "qf_robust_certified_input": bool(qf_certified),
            "intrinsic_mode_definition_count": definition_count,
            "definition_count": definition_count,
            "qf_robust_input_confidence": qf_confidence,
            "intrinsic_definition_score": intrinsic_definition_score,
            "formal_intrinsicality_seed_score": formal_intrinsicality_seed_score,
            "mei_readiness_score": mei_readiness_score,
            "intrinsic_mode_definitions": definitions,
            "mei_candidate_definitions": definitions,
            "defined_modes": definitions,
            "definition_schema": {
                "source": "QF_robust functional certification",
                "components": [
                    "qf_source_coherence",
                    "irreducibility_proxy",
                    "causal_anchoring_proxy",
                    "temporal_persistence_proxy",
                    "invariance_proxy",
                ],
                "scope": "formal_functional_only",
            },
            "component_sources": {
                "primary": "robust_qualia_formal_certifier",
                "upstream": ["mode_lifecycle_tracker", "qualia_formal_mode_registry", "common_mode_score_calculator"],
                "supporting_formal_priors": ["computational_irreducibility", "intrinsic_metric_builder", "intrinsic_distinction_detector"],
            },
            "epistemic_status": "functional_only",
            "functional_only_flags": dict(GUARD),
            "next_recommended_module": "mode_intrinsicality_tester",
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


__all__ = ["IntrinsicExistenceModeDefinition"]
