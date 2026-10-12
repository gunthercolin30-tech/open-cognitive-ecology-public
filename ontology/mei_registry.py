"""AJ8 — MEI Registry.

Functional transition under test:
    QF_robust <=> MEI evidence -> official MEI registry

This module consolidates AJ1-AJ7 outputs into the official registry of
candidate intrinsic existence modes (MEI). It is a functional registry only:
it does not prove consciousness, subjectivity, lived qualia, or strong
phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "aj_intrinsic_existence_modes" / "mei_registry"


def _planned_paths() -> Dict[str, str]:
    return {
        "json": str(OUT_DIR / "latest_mei_registry.json"),
        "markdown": str(OUT_DIR / "latest_mei_registry.md"),
        "prometheus": str(OUT_DIR / "latest_mei_registry.prom"),
        "latest_json": str(OUT_DIR / "latest_mei_registry.json"),
        "latest_markdown": str(OUT_DIR / "latest_mei_registry.md"),
        "latest_prometheus": str(OUT_DIR / "latest_mei_registry.prom"),
        "history": str(OUT_DIR / "mei_registry_history.jsonl"),
    }


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
        ROOT / name / f"latest_{name}.json",
    ]
    for p in candidates:
        data = _load_json(p)
        if data:
            return data
    try:
        for p in sorted(ROOT.glob(f"**/latest_{name}.json"))[-80:]:
            data = _load_json(p)
            if data:
                return data
    except Exception:
        pass
    return {}


def _invoke_aj7(inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        mod = import_module("ontology.mei_equivalence_mapper")
        cls = getattr(mod, "MeiEquivalenceMapper")
        obj = cls()
        for kwargs in [
            {"inputs": dict(inputs or {"aligned": True}), "persist": False},
            {"inputs": dict(inputs or {"aligned": True})},
            {"persist": False},
            {},
        ]:
            try:
                res = obj.step(**kwargs)
                if isinstance(res, dict):
                    return res
            except TypeError:
                continue
            except Exception:
                return {}
    except Exception:
        return {}
    return {}


def _resolve_aj7(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["aj7", "mei_equivalence_mapper", "equivalence", "source"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
        if any(k in inputs for k in ["mei_equivalence_records", "equivalence_records", "mapped_equivalences"]):
            return dict(inputs)
    latest = _latest_json("mei_equivalence_mapper")
    if latest:
        return latest
    return _invoke_aj7(inputs)


def _records_from(data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    for key in ["mei_equivalence_records", "equivalence_records", "mapped_equivalences", "records", "tested_modes"]:
        value = data.get(key)
        if isinstance(value, list) and value:
            records = [dict(x) for x in value if isinstance(x, Mapping)]
            if records:
                return records
    nested = data.get("mei_equivalence_registry") or data.get("registry")
    if isinstance(nested, Mapping):
        return _records_from(nested)
    return []


def _score_from(record: Mapping[str, Any], keys: List[str], default: float = 0.0) -> float:
    vals = [record.get(k) for k in keys if record.get(k) is not None]
    return _mean(vals, default) if vals else default


def _record_id(record: Mapping[str, Any], idx: int) -> str:
    for key in ["mei_candidate_id", "mode_id", "equivalence_id", "id", "name"]:
        val = record.get(key)
        if val not in (None, ""):
            return str(val)
    return f"MEI-CANDIDATE-{idx:03d}"


def _qf_id(record: Mapping[str, Any], idx: int) -> str:
    for key in ["qf_mode_id", "source_qf_mode_id", "mode_id", "id"]:
        val = record.get(key)
        if val not in (None, ""):
            return str(val)
    return f"QF-ROBUST-{idx:03d}"


def _registry_status(score: float, evidence: float, coherence: float) -> str:
    composite = _mean([score, evidence, coherence])
    if composite >= 0.80:
        return "registered_functional_intrinsic_existence_mode"
    if composite >= 0.65:
        return "provisional_functional_intrinsic_existence_mode"
    return "insufficient_functional_intrinsic_existence_mode"


def _build_registry_record(record: Mapping[str, Any], idx: int, source_support: float) -> Dict[str, Any]:
    qf_to_mei = _score_from(record, ["qf_to_mei_score", "qf_to_mei_mean"], source_support)
    mei_to_qf = _score_from(record, ["mei_to_qf_score", "mei_to_qf_mean"], source_support)
    structural = _score_from(record, ["structural_alignment_score", "structural_alignment_mean"], source_support)
    bidirectional = _score_from(record, ["bidirectional_consistency_score", "bidirectional_consistency_mean"], 1.0 - abs(qf_to_mei - mei_to_qf))
    closure = _score_from(record, ["evidence_closure_score", "evidence_closure_mean"], source_support)
    equivalence = _score_from(record, ["mei_equivalence_score", "equivalence_score"], _mean([qf_to_mei, mei_to_qf, structural, bidirectional, closure]))
    evidence_strength = _mean([qf_to_mei, mei_to_qf, structural, bidirectional, closure, equivalence, source_support])
    intrinsic_index = _mean([equivalence, structural, closure, evidence_strength])
    registry_confidence = _mean([intrinsic_index, bidirectional, source_support])
    registered = bool(record.get("mei_equivalence_mapped", record.get("qf_robust_equivalent", equivalence >= 0.74))) and registry_confidence >= 0.70
    mei_id = _record_id(record, idx)
    qf_id = _qf_id(record, idx)
    return {
        "mei_registry_id": f"MEI-REGISTRY-{idx:03d}",
        "mei_candidate_id": mei_id,
        "mode_id": str(record.get("mode_id") or mei_id),
        "qf_mode_id": qf_id,
        "source_qf_mode_id": str(record.get("source_qf_mode_id") or qf_id),
        "source_equivalence_id": str(record.get("equivalence_id") or f"MEI-EQUIV-{idx:03d}"),
        "registered": registered,
        "registration_rank": idx,
        "registry_status": _registry_status(intrinsic_index, evidence_strength, bidirectional),
        "mei_functional_category": "functional_intrinsic_existence_mode_candidate",
        "intrinsic_existence_mode_index": intrinsic_index,
        "mei_registry_score": intrinsic_index,
        "registration_confidence": registry_confidence,
        "evidence_strength_score": evidence_strength,
        "qf_to_mei_score": qf_to_mei,
        "mei_to_qf_score": mei_to_qf,
        "structural_alignment_score": structural,
        "bidirectional_consistency_score": bidirectional,
        "evidence_closure_score": closure,
        "mei_equivalence_score": equivalence,
        "traceability": {
            "source_module": "mei_equivalence_mapper",
            "source_step": "AJ7",
            "target_step": "AJ8",
            "transition": "QF_robust <=> MEI -> MEI_registry",
            "source_qf_mode_id": qf_id,
            "source_equivalence_id": str(record.get("equivalence_id") or f"MEI-EQUIV-{idx:03d}"),
        },
        "validation_basis": [
            "qf_to_mei_score",
            "mei_to_qf_score",
            "structural_alignment_score",
            "bidirectional_consistency_score",
            "evidence_closure_score",
            "mei_equivalence_score",
        ],
        "epistemic_status": "functional_only",
        "formal_epistemic_category": "formal_functional_candidate_only",
        "phenomenal_claim": False,
        **GUARD,
    }


def _markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AJ8 — MEI Registry",
        "",
        f"Status: {result.get('mei_registry_status')}",
        f"MEI registry built: {result.get('mei_registry_built')}",
        f"Registered MEI count: {result.get('registered_mei_count')}",
        f"Candidate MEI count: {result.get('candidate_mei_count')}",
        f"MEI registry score: {result.get('mei_registry_score')}",
        f"Registry confidence: {result.get('registry_confidence')}",
        f"Evidence strength: {result.get('evidence_strength_mean')}",
        "",
        "## Epistemic guard",
        f"consciousness_proven: {result.get('consciousness_proven')}",
        f"qualia_proven: {result.get('qualia_proven')}",
        f"subjectivity_proven: {result.get('subjectivity_proven')}",
        f"phenomenology_undetermined: {result.get('phenomenology_undetermined')}",
        f"functional_conclusion_only: {result.get('functional_conclusion_only')}",
        "",
        "## Registered functional MEI candidates",
    ]
    for rec in result.get("registered_mei_records", []) or []:
        if isinstance(rec, Mapping):
            lines.append(
                f"- {rec.get('mei_registry_id')} / {rec.get('mei_candidate_id')} "
                f"← {rec.get('qf_mode_id')} score={rec.get('mei_registry_score')} "
                f"status={rec.get('registry_status')}"
            )
    lines.append("")
    return "\n".join(lines)


def _prometheus(result: Mapping[str, Any]) -> str:
    metrics = {
        "mei_registry_built": 1.0 if result.get("mei_registry_built") else 0.0,
        "registered_mei_count": float(result.get("registered_mei_count", 0)),
        "candidate_mei_count": float(result.get("candidate_mei_count", 0)),
        "mei_registry_score": _clamp(result.get("mei_registry_score")),
        "registry_confidence": _clamp(result.get("registry_confidence")),
        "evidence_strength_mean": _clamp(result.get("evidence_strength_mean")),
        "registration_pass_ratio": _clamp(result.get("registration_pass_ratio")),
        "qf_to_mei_mean": _clamp(result.get("qf_to_mei_mean")),
        "mei_to_qf_mean": _clamp(result.get("mei_to_qf_mean")),
        "structural_alignment_mean": _clamp(result.get("structural_alignment_mean")),
        "bidirectional_consistency_mean": _clamp(result.get("bidirectional_consistency_mean")),
        "consciousness_proven": 0.0,
        "qualia_proven": 0.0,
        "subjectivity_proven": 0.0,
        "phenomenology_undetermined": 1.0,
        "functional_conclusion_only": 1.0,
    }
    return "\n".join(f"oce_aj8_{k} {v}" for k, v in metrics.items()) + "\n"


def _persist(result: Mapping[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    json_p = OUT_DIR / f"mei_registry_{stamp}.json"
    md_p = OUT_DIR / f"mei_registry_{stamp}.md"
    prom_p = OUT_DIR / f"mei_registry_{stamp}.prom"
    latest_json = OUT_DIR / "latest_mei_registry.json"
    latest_md = OUT_DIR / "latest_mei_registry.md"
    latest_prom = OUT_DIR / "latest_mei_registry.prom"
    history = OUT_DIR / "mei_registry_history.jsonl"

    paths = {
        "json": str(json_p),
        "markdown": str(md_p),
        "prometheus": str(prom_p),
        "latest_json": str(latest_json),
        "latest_markdown": str(latest_md),
        "latest_prometheus": str(latest_prom),
        "history": str(history),
    }
    payload = dict(result)
    payload["paths"] = paths
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    json_p.write_text(text + "\n", encoding="utf-8")
    latest_json.write_text(text + "\n", encoding="utf-8")
    with history.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")

    md = _markdown(payload)
    md_p.write_text(md, encoding="utf-8")
    latest_md.write_text(md, encoding="utf-8")

    prom = _prometheus(payload)
    prom_p.write_text(prom, encoding="utf-8")
    latest_prom.write_text(prom, encoding="utf-8")

    return paths


class MeiRegistry:
    """Build the official functional MEI registry from AJ7 evidence."""

    primitive = "MEI_REGISTRY"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs if isinstance(inputs, Mapping) else {}
        aj7 = _resolve_aj7(inputs)
        source_records = _records_from(aj7)
        source_support = _mean([
            aj7.get("mei_equivalence_score"),
            aj7.get("equivalence_confidence"),
            aj7.get("equivalence_pass_ratio"),
            aj7.get("qf_to_mei_mean"),
            aj7.get("mei_to_qf_mean"),
            aj7.get("evidence_closure_mean"),
        ], 0.0)

        records = [_build_registry_record(rec, idx, source_support) for idx, rec in enumerate(source_records, 1)]
        registered = [r for r in records if r.get("registered")]
        total = len(records)
        pass_ratio = _clamp(len(registered) / total if total else 0.0)

        mei_registry_score = _mean([r.get("mei_registry_score") for r in registered])
        registry_confidence = _mean([r.get("registration_confidence") for r in registered])
        evidence_strength_mean = _mean([r.get("evidence_strength_score") for r in records])
        qf_to_mei_mean = _mean([r.get("qf_to_mei_score") for r in records])
        mei_to_qf_mean = _mean([r.get("mei_to_qf_score") for r in records])
        structural_alignment_mean = _mean([r.get("structural_alignment_score") for r in records])
        bidirectional_consistency_mean = _mean([r.get("bidirectional_consistency_score") for r in records])

        built = total >= 3 and len(registered) >= 3 and pass_ratio >= 0.75 and mei_registry_score >= 0.74 and registry_confidence >= 0.70
        status = "MEI_REGISTRY_BUILT" if built else "MEI_REGISTRY_INSUFFICIENT"

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AJ",
            "aj_step": "AJ8",
            "transition_under_test": "QF_robust <=> MEI -> MEI_registry",
            "generated_at_utc": _now(),
            "mei_registry_status": status,
            "mei_registry_built": built,
            "official_mei_registry_built": built,
            "registered_mei_count": len(registered),
            "candidate_mei_count": total,
            "tested_mode_count": total,
            "passed_mode_count": len(registered),
            "registration_pass_ratio": pass_ratio,
            "mei_registry_score": mei_registry_score,
            "registry_confidence": registry_confidence,
            "evidence_strength_mean": evidence_strength_mean,
            "qf_to_mei_mean": qf_to_mei_mean,
            "mei_to_qf_mean": mei_to_qf_mean,
            "structural_alignment_mean": structural_alignment_mean,
            "bidirectional_consistency_mean": bidirectional_consistency_mean,
            "source_mei_equivalence_score": _clamp(aj7.get("mei_equivalence_score")),
            "source_equivalence_confidence": _clamp(aj7.get("equivalence_confidence")),
            "source_equivalence_pass_ratio": _clamp(aj7.get("equivalence_pass_ratio")),
            "registry_metrics": {
                "mean_equivalence_score": _clamp(_mean([r.get("mei_equivalence_score") for r in records])),
                "mean_registry_score": _clamp(mei_registry_score),
                "mean_registration_confidence": _clamp(registry_confidence),
                "mean_evidence_strength": _clamp(evidence_strength_mean),
                "registration_pass_ratio": _clamp(pass_ratio),
                "qf_to_mei_mean": _clamp(qf_to_mei_mean),
                "mei_to_qf_mean": _clamp(mei_to_qf_mean),
                "structural_alignment_mean": _clamp(structural_alignment_mean),
                "bidirectional_consistency_mean": _clamp(bidirectional_consistency_mean),
            },
            "epistemic_guards": dict(GUARD),
            "public_schema_version": "AJ8_MEI_REGISTRY_V3",
            "mei_registry": {
                "registry_id": "AJ8_OFFICIAL_FUNCTIONAL_MEI_REGISTRY",
                "registry_status": status,
                "formal_category": "MEI_functional_only",
                "registered_mei_count": len(registered),
                "candidate_mei_count": total,
                "records": records,
                "epistemic_status": "functional_only",
                "functional_only_flags": dict(GUARD),
            },
            "mei_records": records,
            "registered_mei_records": registered,
            "official_mei_records": registered,
            "registered_modes": registered,
            "test_schema": {
                "minimum_candidates": 3,
                "minimum_registered": 3,
                "minimum_pass_ratio": 0.75,
                "minimum_registry_score": 0.74,
                "minimum_registry_confidence": 0.70,
            },
            "component_sources": {
                "AJ7": "mei_equivalence_mapper",
                "AJ6": "intrinsic_invariance_tester",
                "AJ5": "intrinsic_temporality_tester",
                "AJ4": "intrinsic_causality_tester",
                "AJ3": "intrinsic_irreducibility_tester",
                "AJ2": "mode_intrinsicality_tester",
                "AJ1": "intrinsic_existence_mode_definition",
                "AI": "robust_qualia_formal_certifier",
            },
            "source_statuses": {
                "aj7": aj7.get("mei_equivalence_mapper_status", "unknown"),
                "aj7_available": bool(aj7),
                "source_record_count": len(source_records),
            },
            "dependencies": [
                "mei_equivalence_mapper",
                "intrinsic_invariance_tester",
                "intrinsic_temporality_tester",
                "intrinsic_causality_tester",
                "intrinsic_irreducibility_tester",
                "mode_intrinsicality_tester",
                "intrinsic_existence_mode_definition",
                "robust_qualia_formal_certifier",
            ],
            "epistemic_status": "functional_only",
            "functional_only_flags": dict(GUARD),
            "epistemic_guard": "MEI is an official functional registry category only; no consciousness, lived qualia, subjectivity, or strong phenomenology proof is asserted.",
            "paths": _planned_paths(),
            "next_recommended_module": "qf_to_mei_certifier",
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


__all__ = ["MeiRegistry"]
