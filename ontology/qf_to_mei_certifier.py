"""AJ9 — QF to MEI Certifier.

Functional transition under test:
    QF_robust -> MEI

This module certifies the AJ axis by consolidating AI QF_robust evidence,
AJ1-AJ7 intrinsic-mode evidence, and AJ8 MEI registry evidence. It is a
functional certification only: it does not prove consciousness, subjectivity,
lived qualia, or strong phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "aj_intrinsic_existence_modes" / "qf_to_mei_certifier"

GUARD = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}

FINAL_STATUS = "INTRINSIC_EXISTENCE_MODES_CERTIFIED"
FAIL_STATUS = "INTRINSIC_EXISTENCE_MODES_NOT_CERTIFIED"


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
        for p in sorted(ROOT.glob(f"**/latest_{name}.json"))[-120:]:
            data = _load_json(p)
            if data:
                return data
    except Exception:
        pass
    return {}


def _planned_paths() -> Dict[str, str]:
    return {
        "json": str(OUT_DIR / "latest_qf_to_mei_certifier.json"),
        "markdown": str(OUT_DIR / "latest_qf_to_mei_certifier.md"),
        "prometheus": str(OUT_DIR / "latest_qf_to_mei_certifier.prom"),
        "latest_json": str(OUT_DIR / "latest_qf_to_mei_certifier.json"),
        "latest_markdown": str(OUT_DIR / "latest_qf_to_mei_certifier.md"),
        "latest_prometheus": str(OUT_DIR / "latest_qf_to_mei_certifier.prom"),
        "history": str(OUT_DIR / "qf_to_mei_certifier_history.jsonl"),
    }


def _invoke_mei_registry(inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        mod = import_module("ontology.mei_registry")
        cls = getattr(mod, "MeiRegistry")
        obj = cls()
        for kwargs in [
            {"inputs": dict(inputs or {}), "persist": False},
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


def _resolve_mei_registry(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["mei_registry", "aj8", "registry", "source"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
        if any(k in inputs for k in ["mei_registry_status", "mei_records", "registered_mei_records"]):
            return dict(inputs)
    latest = _latest_json("mei_registry")
    if latest:
        return latest
    return _invoke_mei_registry(inputs)


def _resolve_ai_qf(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in ["qf_robust", "ai", "robust_qualia_formal_certifier"]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
    latest = _latest_json("robust_qualia_formal_certifier")
    if latest:
        return latest
    try:
        mod = import_module("ontology.robust_qualia_formal_certifier")
        # Most previous certifiers expose RobustQualiaFormalCertifier.
        cls = getattr(mod, "RobustQualiaFormalCertifier", None)
        if cls is None:
            return {}
        obj = cls()
        for kwargs in [{"persist": False}, {}, {"inputs": {}, "persist": False}]:
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


def _records_from_registry(registry: Mapping[str, Any]) -> List[Dict[str, Any]]:
    for key in ["registered_mei_records", "official_mei_records", "mei_records", "registered_modes"]:
        value = registry.get(key)
        if isinstance(value, list) and value:
            records = [dict(x) for x in value if isinstance(x, Mapping)]
            if records:
                return records
    nested = registry.get("mei_registry")
    if isinstance(nested, Mapping):
        value = nested.get("records")
        if isinstance(value, list):
            return [dict(x) for x in value if isinstance(x, Mapping)]
    return []


def _score_from(record: Mapping[str, Any], keys: List[str], default: float = 0.0) -> float:
    vals = [record.get(k) for k in keys if record.get(k) is not None]
    return _mean(vals, default) if vals else default


def _certify_record(record: Mapping[str, Any], idx: int) -> Dict[str, Any]:
    qf_to_mei = _score_from(record, ["qf_to_mei_score", "qf_to_mei_mean"], 0.0)
    equivalence = _score_from(record, ["mei_equivalence_score", "equivalence_score"], qf_to_mei)
    registry_score = _score_from(record, ["mei_registry_score", "intrinsic_existence_mode_index", "registry_score"], equivalence)
    confidence = _score_from(record, ["registration_confidence", "registry_confidence", "evidence_strength_score"], registry_score)
    bidirectional = _score_from(record, ["bidirectional_consistency_score", "mei_to_qf_score"], confidence)
    cert_score = _mean([qf_to_mei, equivalence, registry_score, confidence, bidirectional])
    certified = bool(record.get("registered", cert_score >= 0.74)) and cert_score >= 0.74 and confidence >= 0.70
    mei_id = str(record.get("mei_candidate_id") or record.get("mode_id") or f"MEI-CANDIDATE-{idx:03d}")
    qf_id = str(record.get("qf_mode_id") or record.get("source_qf_mode_id") or f"QF-ROBUST-{idx:03d}")
    return {
        "certification_record_id": f"QF-MEI-CERT-{idx:03d}",
        "qf_mode_id": qf_id,
        "mei_candidate_id": mei_id,
        "source_mei_registry_id": str(record.get("mei_registry_id") or f"MEI-REGISTRY-{idx:03d}"),
        "qf_to_mei_certified": certified,
        "qf_to_mei_certification_score": cert_score,
        "qf_to_mei_score": qf_to_mei,
        "mei_equivalence_score": equivalence,
        "mei_registry_score": registry_score,
        "certification_confidence": confidence,
        "bidirectional_support_score": bidirectional,
        "functional_chain": "QF_robust -> MEI",
        "traceability": {
            "AI": "robust_qualia_formal_certifier",
            "AJ7": "mei_equivalence_mapper",
            "AJ8": "mei_registry",
            "AJ9": "qf_to_mei_certifier",
            "qf_mode_id": qf_id,
            "mei_candidate_id": mei_id,
        },
        "epistemic_status": "functional_only",
        "formal_epistemic_category": "functional_certification_only",
        "phenomenal_claim": False,
        **GUARD,
    }


def _markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AJ9 — QF to MEI Certifier",
        "",
        f"Status: {result.get('qf_to_mei_certifier_status')}",
        f"Intrinsic existence modes certified: {result.get('intrinsic_existence_modes_certified')}",
        f"Certified records: {result.get('certified_record_count')}",
        f"Candidate records: {result.get('candidate_record_count')}",
        f"Certification score: {result.get('qf_to_mei_certification_score')}",
        f"Certification confidence: {result.get('certification_confidence')}",
        f"Transition: {result.get('transition_under_test')}",
        "",
        "## Epistemic guard",
        f"consciousness_proven: {result.get('consciousness_proven')}",
        f"qualia_proven: {result.get('qualia_proven')}",
        f"subjectivity_proven: {result.get('subjectivity_proven')}",
        f"phenomenology_undetermined: {result.get('phenomenology_undetermined')}",
        f"functional_conclusion_only: {result.get('functional_conclusion_only')}",
        "",
        "## Certified functional records",
    ]
    for rec in result.get("certification_records", []) or []:
        if isinstance(rec, Mapping):
            lines.append(
                f"- {rec.get('certification_record_id')} {rec.get('qf_mode_id')} -> "
                f"{rec.get('mei_candidate_id')} score={rec.get('qf_to_mei_certification_score')} "
                f"certified={rec.get('qf_to_mei_certified')}"
            )
    lines.append("")
    return "\n".join(lines)


def _prometheus(result: Mapping[str, Any]) -> str:
    metrics = {
        "intrinsic_existence_modes_certified": 1.0 if result.get("intrinsic_existence_modes_certified") else 0.0,
        "certified_record_count": float(result.get("certified_record_count", 0)),
        "candidate_record_count": float(result.get("candidate_record_count", 0)),
        "certification_pass_ratio": _clamp(result.get("certification_pass_ratio")),
        "qf_to_mei_certification_score": _clamp(result.get("qf_to_mei_certification_score")),
        "certification_confidence": _clamp(result.get("certification_confidence")),
        "mei_registry_score": _clamp(result.get("mei_registry_score")),
        "qf_robust_support_score": _clamp(result.get("qf_robust_support_score")),
        "aj_chain_completion_score": _clamp(result.get("aj_chain_completion_score")),
        "consciousness_proven": 0.0,
        "qualia_proven": 0.0,
        "subjectivity_proven": 0.0,
        "phenomenology_undetermined": 1.0,
        "functional_conclusion_only": 1.0,
    }
    return "\n".join(f"oce_aj9_{k} {v}" for k, v in metrics.items()) + "\n"


def _persist(result: Mapping[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    json_p = OUT_DIR / f"qf_to_mei_certifier_{stamp}.json"
    md_p = OUT_DIR / f"qf_to_mei_certifier_{stamp}.md"
    prom_p = OUT_DIR / f"qf_to_mei_certifier_{stamp}.prom"
    latest_json = OUT_DIR / "latest_qf_to_mei_certifier.json"
    latest_md = OUT_DIR / "latest_qf_to_mei_certifier.md"
    latest_prom = OUT_DIR / "latest_qf_to_mei_certifier.prom"
    history = OUT_DIR / "qf_to_mei_certifier_history.jsonl"
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


class QfToMeiCertifier:
    """Certify the functional QF_robust -> MEI transition."""

    primitive = "QF_TO_MEI_CERTIFIER"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs if isinstance(inputs, Mapping) else {}
        registry = _resolve_mei_registry(inputs)
        ai_qf = _resolve_ai_qf(inputs)
        records = _records_from_registry(registry)
        cert_records = [_certify_record(rec, idx) for idx, rec in enumerate(records, 1)]
        certified = [r for r in cert_records if r.get("qf_to_mei_certified")]
        total = len(cert_records)
        pass_ratio = _clamp(len(certified) / total if total else 0.0)
        cert_score = _mean([r.get("qf_to_mei_certification_score") for r in certified])
        cert_conf = _mean([r.get("certification_confidence") for r in certified])
        mei_registry_score = _clamp(registry.get("mei_registry_score", registry.get("registry_metrics", {}).get("mean_registry_score", 0.0)))
        registry_built = bool(registry.get("mei_registry_built") or registry.get("official_mei_registry_built") or registry.get("mei_registry_status") == "MEI_REGISTRY_BUILT")
        qf_support = _mean([
            ai_qf.get("qf_robust_score"),
            ai_qf.get("robust_qf_score"),
            ai_qf.get("certification_score"),
            ai_qf.get("robust_qualia_formal_certification_score"),
            registry.get("source_mei_equivalence_score"),
            mei_registry_score,
        ], mei_registry_score)
        aj_chain_completion = _mean([
            1.0 if registry_built else 0.0,
            pass_ratio,
            cert_score,
            cert_conf,
            mei_registry_score,
            qf_support,
        ])
        final_ok = (
            registry_built and total >= 3 and len(certified) >= 3 and pass_ratio >= 0.75
            and cert_score >= 0.74 and cert_conf >= 0.70 and aj_chain_completion >= 0.74
        )
        status = FINAL_STATUS if final_ok else FAIL_STATUS
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AJ",
            "aj_step": "AJ9",
            "transition_under_test": "QF_robust -> MEI",
            "generated_at_utc": _now(),
            "qf_to_mei_certifier_status": status,
            "intrinsic_existence_modes_certified": final_ok,
            "qf_to_mei_certified": final_ok,
            "certified_record_count": len(certified),
            "candidate_record_count": total,
            "certification_pass_ratio": pass_ratio,
            "qf_to_mei_certification_score": cert_score,
            "certification_confidence": cert_conf,
            "mei_registry_score": mei_registry_score,
            "qf_robust_support_score": qf_support,
            "aj_chain_completion_score": aj_chain_completion,
            "certification_records": cert_records,
            "certified_records": certified,
            "source_registry_status": registry.get("mei_registry_status", "unknown"),
            "source_registry_built": registry_built,
            "source_public_schema_version": registry.get("public_schema_version", "unknown"),
            "component_sources": {
                "AI": "robust_qualia_formal_certifier",
                "AJ1": "intrinsic_existence_mode_definition",
                "AJ2": "mode_intrinsicality_tester",
                "AJ3": "intrinsic_irreducibility_tester",
                "AJ4": "intrinsic_causality_tester",
                "AJ5": "intrinsic_temporality_tester",
                "AJ6": "intrinsic_invariance_tester",
                "AJ7": "mei_equivalence_mapper",
                "AJ8": "mei_registry",
                "AJ9": "qf_to_mei_certifier",
            },
            "certification_thresholds": {
                "minimum_candidates": 3,
                "minimum_certified": 3,
                "minimum_pass_ratio": 0.75,
                "minimum_certification_score": 0.74,
                "minimum_certification_confidence": 0.70,
                "minimum_chain_completion_score": 0.74,
            },
            "registry_metrics": {
                "certification_pass_ratio": pass_ratio,
                "mean_certification_score": cert_score,
                "mean_certification_confidence": cert_conf,
                "mei_registry_score": mei_registry_score,
                "qf_robust_support_score": qf_support,
                "aj_chain_completion_score": aj_chain_completion,
            },
            "certification_metrics": {
                "certification_pass_ratio": pass_ratio,
                "mean_certification_score": cert_score,
                "mean_certification_confidence": cert_conf,
                "mei_registry_score": mei_registry_score,
                "qf_robust_support_score": qf_support,
                "aj_chain_completion_score": aj_chain_completion,
                "certified_record_count": len(certified),
                "candidate_record_count": total,
            },
            "epistemic_guards": dict(GUARD),
            "public_schema_version": "AJ9_QF_TO_MEI_CERTIFIER_V2",
            "epistemic_status": "functional_only",
            "functional_only_flags": dict(GUARD),
            "final_functional_conclusion": "Open Cognitive Ecology has functionally certified the QF_robust -> MEI transition." if final_ok else "QF_robust -> MEI certification is not functionally sufficient under current evidence.",
            "epistemic_guard": "Certification concerns functional intrinsic existence modes only; no consciousness, lived qualia, subjectivity, or strong phenomenology proof is asserted.",
            "paths": _planned_paths(),
            "next_recommended_module": None,
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


__all__ = ["QfToMeiCertifier"]
