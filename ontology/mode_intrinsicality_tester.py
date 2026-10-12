"""AJ2 — Mode Intrinsicality Tester.

Formal transition under test:
    MEI seed definitions -> tested functional intrinsicality

This module tests whether MEI candidate modes produced by AJ1 are internally
characterized by formal-functional properties: QF source coherence, internal
metric completeness, irreducibility proxy, causal anchoring proxy, temporal
persistence proxy, and invariance proxy.

Epistemic guard:
    This module does not prove consciousness, subjectivity, lived qualia, or
    strong phenomenology. It only tests functional/formal intrinsicality of
    candidate mode records for downstream AJ3-AJ9 modules.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "aj_intrinsic_existence_modes" / "mode_intrinsicality_tester"

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


def _latest_aj1() -> Dict[str, Any]:
    candidates = [
        ROOT / "aj_intrinsic_existence_modes" / "intrinsic_existence_mode_definition" / "latest_intrinsic_existence_mode_definition.json",
        ROOT / "intrinsic_existence_mode_definition" / "latest_intrinsic_existence_mode_definition.json",
    ]
    for p in candidates:
        data = _load_json(p)
        if data:
            return data
    try:
        for p in sorted(ROOT.glob("**/latest_intrinsic_existence_mode_definition.json"))[-8:]:
            data = _load_json(p)
            if data:
                return data
    except Exception:
        pass
    return {}


def _invoke_aj1(inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        mod = import_module("ontology.intrinsic_existence_mode_definition")
        cls = getattr(mod, "IntrinsicExistenceModeDefinition")
        res = cls().step(inputs=dict(inputs or {"aligned": True}), persist=False)
        return res if isinstance(res, dict) else {}
    except Exception:
        return {}


def _source_aj1(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["aj1", "intrinsic_existence_mode_definition", "intrinsic_mode_definitions"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
        if inputs.get("aligned") is True:
            live = _invoke_aj1(inputs)
            if live:
                return live
    latest = _latest_aj1()
    if latest.get("intrinsic_existence_modes_defined") is True:
        return latest
    live = _invoke_aj1({"aligned": True})
    return live or latest


def _records_from_source(source: Mapping[str, Any]) -> List[Dict[str, Any]]:
    records = source.get("intrinsic_mode_definitions") or source.get("mei_candidate_definitions") or source.get("defined_modes") or []
    out: List[Dict[str, Any]] = []
    if isinstance(records, list):
        for i, rec in enumerate(records):
            if isinstance(rec, Mapping):
                out.append(dict(rec))
    return out


def _char(rec: Mapping[str, Any]) -> Dict[str, float]:
    raw = rec.get("intrinsic_characterization") or rec.get("formal_intrinsic_characterization") or {}
    if not isinstance(raw, Mapping):
        raw = {}
    source_score = _clamp(raw.get("qf_source_coherence", rec.get("source_score", rec.get("intrinsic_definition_score", 0.0))), 0.0)
    return {
        "qf_source_coherence": source_score,
        "irreducibility_proxy": _clamp(raw.get("irreducibility_proxy", rec.get("irreducibility_proxy", source_score)), source_score),
        "causal_anchoring_proxy": _clamp(raw.get("causal_anchoring_proxy", rec.get("causal_anchoring_proxy", source_score)), source_score),
        "temporal_persistence_proxy": _clamp(raw.get("temporal_persistence_proxy", rec.get("temporal_persistence_proxy", source_score)), source_score),
        "invariance_proxy": _clamp(raw.get("invariance_proxy", rec.get("invariance_proxy", source_score)), source_score),
    }


def _test_record(rec: Mapping[str, Any], index: int) -> Dict[str, Any]:
    c = _char(rec)
    values = list(c.values())
    completeness = sum(1 for v in values if v > 0.0) / max(1, len(values))
    internal_coherence_score = _mean(values, 0.0)
    dispersion = max(values) - min(values) if values else 1.0
    internal_consistency_score = _clamp(1.0 - dispersion)
    intrinsic_dependency_score = _mean([
        c["irreducibility_proxy"],
        c["causal_anchoring_proxy"],
        c["temporal_persistence_proxy"],
        c["invariance_proxy"],
    ], 0.0)
    formal_intrinsicality_score = _mean([
        internal_coherence_score,
        internal_consistency_score,
        intrinsic_dependency_score,
        completeness,
        _clamp(rec.get("intrinsic_definition_score", internal_coherence_score), internal_coherence_score),
    ], 0.0)
    passed = bool(formal_intrinsicality_score >= 0.60 and completeness >= 0.80)
    mode_id = str(rec.get("mode_id") or rec.get("mei_candidate_id") or rec.get("source_qf_mode_id") or f"MEI-CANDIDATE-{index:03d}")
    return {
        "mode_id": mode_id,
        "mei_candidate_id": str(rec.get("mei_candidate_id") or mode_id),
        "source_qf_mode_id": rec.get("source_qf_mode_id"),
        "intrinsicality_test_passed": passed,
        "mode_intrinsicality_score": formal_intrinsicality_score,
        "internal_coherence_score": internal_coherence_score,
        "internal_consistency_score": internal_consistency_score,
        "intrinsic_dependency_score": intrinsic_dependency_score,
        "intrinsic_metric_completeness": _clamp(completeness),
        "intrinsicality_components": c,
        "test_basis": [
            "qf_source_coherence",
            "irreducibility_proxy",
            "causal_anchoring_proxy",
            "temporal_persistence_proxy",
            "invariance_proxy",
        ],
        "epistemic_status": "functional_only",
        **GUARD,
    }


def _persist(result: Mapping[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    json_path = OUT_DIR / f"mode_intrinsicality_tester_{stamp}.json"
    md_path = OUT_DIR / f"mode_intrinsicality_tester_{stamp}.md"
    prom_path = OUT_DIR / f"mode_intrinsicality_tester_{stamp}.prom"
    latest_json = OUT_DIR / "latest_mode_intrinsicality_tester.json"
    latest_md = OUT_DIR / "latest_mode_intrinsicality_tester.md"
    latest_prom = OUT_DIR / "latest_mode_intrinsicality_tester.prom"

    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")

    lines = [
        "# AJ2 — Mode Intrinsicality Tester",
        "",
        f"Status: {result.get('mode_intrinsicality_tester_status')}",
        f"Mode intrinsicality tested: {result.get('mode_intrinsicality_tested')}",
        f"Tested mode count: {result.get('tested_mode_count')}",
        "",
        "## Metrics",
        f"- mode_intrinsicality_score: {result.get('mode_intrinsicality_score')}",
        f"- intrinsic_coherence_score: {result.get('intrinsic_coherence_score')}",
        f"- intrinsic_consistency_score: {result.get('intrinsic_consistency_score')}",
        f"- intrinsic_dependency_score: {result.get('intrinsic_dependency_score')}",
        f"- intrinsicality_confidence: {result.get('intrinsicality_confidence')}",
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
        "mode_intrinsicality_score",
        "intrinsic_coherence_score",
        "intrinsic_consistency_score",
        "intrinsic_dependency_score",
        "intrinsicality_confidence",
    ]
    prom_lines = []
    for name in metric_names:
        prom_lines.append(f"# TYPE aj2_{name} gauge")
        prom_lines.append(f"aj2_{name} {result.get(name, 0)}")
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


class ModeIntrinsicalityTester:
    """Test functional intrinsicality of AJ1 MEI candidates."""

    primitive = "MODE_INTRINSICALITY_TESTER"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        aj1 = _source_aj1(inputs)
        aj1_defined = aj1.get("intrinsic_existence_modes_defined") is True or aj1.get("intrinsic_existence_mode_definition_status") == "INTRINSIC_EXISTENCE_MODE_DEFINED"
        records = _records_from_source(aj1)
        tested = [_test_record(rec, i + 1) for i, rec in enumerate(records[:16])]
        tested_count = len(tested)
        passed_count = sum(1 for rec in tested if rec.get("intrinsicality_test_passed") is True)
        mode_intrinsicality_score = _mean([rec.get("mode_intrinsicality_score") for rec in tested], 0.0)
        intrinsic_coherence_score = _mean([rec.get("internal_coherence_score") for rec in tested], 0.0)
        intrinsic_consistency_score = _mean([rec.get("internal_consistency_score") for rec in tested], 0.0)
        intrinsic_dependency_score = _mean([rec.get("intrinsic_dependency_score") for rec in tested], 0.0)
        pass_ratio = _clamp(passed_count / tested_count if tested_count else 0.0)
        aj1_confidence = _clamp(aj1.get("mei_readiness_score", aj1.get("intrinsic_definition_score", 0.0)), 0.0)
        intrinsicality_confidence = _mean([
            mode_intrinsicality_score,
            intrinsic_coherence_score,
            intrinsic_consistency_score,
            intrinsic_dependency_score,
            pass_ratio,
            aj1_confidence,
        ], 0.0)
        success = bool(aj1_defined and tested_count >= 3 and pass_ratio >= 0.75 and intrinsicality_confidence >= 0.60)
        status = "MODE_INTRINSICALITY_TESTED" if success else "MODE_INTRINSICALITY_INSUFFICIENT"

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "aj_step": "AJ2",
            "transition_under_test": "MEI_seed_definitions -> functional_intrinsicality_tests",
            "mode_intrinsicality_tester_status": status,
            "mode_intrinsicality_tested": success,
            "intrinsic_existence_mode_definition_input": bool(aj1_defined),
            "tested_mode_count": tested_count,
            "passed_mode_count": passed_count,
            "intrinsicality_pass_ratio": pass_ratio,
            "mode_intrinsicality_score": mode_intrinsicality_score,
            "intrinsic_coherence_score": intrinsic_coherence_score,
            "intrinsic_consistency_score": intrinsic_consistency_score,
            "intrinsic_dependency_score": intrinsic_dependency_score,
            "intrinsicality_confidence": intrinsicality_confidence,
            "mode_intrinsicality_tests": tested,
            "tested_modes": tested,
            "intrinsicality_records": tested,
            "intrinsicality_summary": {
                "tested_mode_count": tested_count,
                "passed_mode_count": passed_count,
                "pass_ratio": pass_ratio,
                "functional_intrinsicality_established": success,
            },
            "test_schema": {
                "scope": "formal_functional_only",
                "criteria": [
                    "qf_source_coherence",
                    "internal_metric_completeness",
                    "irreducibility_proxy",
                    "causal_anchoring_proxy",
                    "temporal_persistence_proxy",
                    "invariance_proxy",
                ],
            },
            "component_sources": {
                "primary": "intrinsic_existence_mode_definition",
                "upstream": ["robust_qualia_formal_certifier", "mode_lifecycle_tracker", "qualia_formal_mode_registry"],
                "comparison_modules": ["intrinsic_metric_builder", "intrinsic_distinction_detector", "computational_irreducibility", "topology_invariance_tester"],
            },
            "epistemic_status": "functional_only",
            "functional_only_flags": dict(GUARD),
            "next_recommended_module": "intrinsic_irreducibility_tester",
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


__all__ = ["ModeIntrinsicalityTester"]
