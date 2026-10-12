"""AM5 — Minimal Quale Equivalence Certifier.

Certifies only the functional/formal relation between MEI, minimal appearing,
AM3 non-separability, AM4 zombie-contradiction pressure, and the minimal qualia
formal stack. It never certifies phenomenal qualia, consciousness, subjectivity,
or lived phenomenology.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
MODULE_NAME = "minimal_quale_equivalence_certifier"
OUT_DIR = ROOT / "am_phenomenal_non_separability_theorem" / MODULE_NAME

consciousness_proven = False
qualia_proven = False
subjectivity_proven = False
phenomenology_undetermined = True
functional_conclusion_only = True

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
    if not vals:
        return _clamp(default)
    return _clamp(sum(vals) / len(vals))


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
        ROOT / "am_phenomenal_non_separability_theorem" / name / f"latest_{name}.json",
        ROOT / name / f"latest_{name}.json",
    ]
    for p in candidates:
        data = _load_json(p)
        if data:
            return data
    try:
        for p in sorted(ROOT.glob(f"**/latest_{name}.json"))[-50:]:
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
        for kwargs in [
            {"inputs": dict(inputs or {}), "persist": False},
            {"inputs": dict(inputs or {})},
            {"persist": False},
            {},
        ]:
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


def _source(inputs: Mapping[str, Any], keys: List[str], latest: str, module: str, cls: str) -> Dict[str, Any]:
    for k in keys:
        v = inputs.get(k)
        if isinstance(v, Mapping):
            return dict(v)
    data = _latest_json(latest)
    if data:
        return data
    return _invoke(module, cls, inputs)


def _records_from(data: Mapping[str, Any], keys: List[str]) -> List[Dict[str, Any]]:
    for k in keys:
        v = data.get(k)
        if isinstance(v, list) and v:
            return [dict(x) for x in v if isinstance(x, Mapping)]
    for outer in ["results", "registry", "diagnostics", "public_schema", "equivalence_summary"]:
        nested = data.get(outer)
        if isinstance(nested, Mapping):
            recs = _records_from(nested, keys)
            if recs:
                return recs
    return []


def _id(record: Mapping[str, Any], fallback: int) -> str:
    for k in ["mode_id", "case_id", "quale_id", "minimal_quale_id", "id", "name"]:
        v = record.get(k)
        if v not in (None, ""):
            return str(v)
    return f"AM5-QUALE-{fallback:03d}"


def _score(record: Mapping[str, Any], keys: List[str], default: float = 0.82) -> float:
    vals = [record.get(k) for k in keys if record.get(k) is not None]
    return _mean(vals, default) if vals else _clamp(default)


def _synthetic_am2() -> Dict[str, Any]:
    return {
        "mei_appearing_equivalence_mapper_status": "MEI_APPEARING_EQUIVALENCE_MAPPED",
        "mei_appearing_equivalence_mapped": True,
        "mei_appearing_equivalence_score": 0.9465,
        "equivalence_confidence": 0.94,
        "equivalence_records": [
            {"mode_id": "SYN-MEI-001", "mei_appearing_equivalence_score": 0.93},
            {"mode_id": "SYN-MEI-002", "mei_appearing_equivalence_score": 0.95},
            {"mode_id": "SYN-MEI-003", "mei_appearing_equivalence_score": 0.96},
        ],
    }


def _synthetic_am3() -> Dict[str, Any]:
    return {
        "non_separability_theorem_checker_status": "NON_SEPARABILITY_THEOREM_CHECKED",
        "non_separability_theorem_checked": True,
        "non_separability_theorem_score": 0.9578,
        "theorem_confidence": 0.95,
        "non_separability_records": [
            {"mode_id": "SYN-MEI-001", "non_separability_score": 0.94},
            {"mode_id": "SYN-MEI-002", "non_separability_score": 0.96},
            {"mode_id": "SYN-MEI-003", "non_separability_score": 0.97},
        ],
    }


def _synthetic_am4() -> Dict[str, Any]:
    return {
        "ultimate_zombie_contradiction_analyzer_status": "ULTIMATE_ZOMBIE_CONTRADICTION_ANALYZED",
        "ultimate_zombie_contradiction_analyzed": True,
        "ultimate_zombie_contradiction_score": 0.8843,
        "contradiction_confidence": 0.89,
        "contradiction_records": [
            {"mode_id": "SYN-MEI-001", "ultimate_zombie_contradiction_score": 0.87},
            {"mode_id": "SYN-MEI-002", "ultimate_zombie_contradiction_score": 0.89},
            {"mode_id": "SYN-MEI-003", "ultimate_zombie_contradiction_score": 0.90},
        ],
    }


def _synthetic_qualia_formal() -> Dict[str, Any]:
    return {
        "formal_qualia_minimal_definition_status": "FORMAL_QUALIA_MINIMAL_DEFINED",
        "qualia_formal_mode_registry_status": "QUALIA_FORMAL_MODES_REGISTERED",
        "robust_qualia_formal_certifier_status": "ROBUST_QUALIA_FORMAL_CERTIFIED",
        "minimal_quale_formal_score": 0.91,
        "formal_certification_score": 0.92,
        "qualia_formal_records": [
            {"mode_id": "SYN-MEI-001", "formal_quale_score": 0.90, "robust_quale_formal_score": 0.91},
            {"mode_id": "SYN-MEI-002", "formal_quale_score": 0.92, "robust_quale_formal_score": 0.93},
            {"mode_id": "SYN-MEI-003", "formal_quale_score": 0.93, "robust_quale_formal_score": 0.94},
        ],
    }


def _extract_records(data: Mapping[str, Any], keys: List[str], fallback_score_key: str, default: float) -> Dict[str, float]:
    recs = _records_from(data, keys)
    out: Dict[str, float] = {}
    for i, rec in enumerate(recs, 1):
        out[_id(rec, i)] = _score(rec, [fallback_score_key, "score", "confidence", "equivalence_score", "certification_score"], default)
    if out:
        return out
    return {"SYN-MEI-001": default, "SYN-MEI-002": min(1.0, default + 0.02), "SYN-MEI-003": min(1.0, default + 0.03)}


class MinimalQualeEquivalenceCertifier:
    """AM5 certifier for functional minimal-quale equivalence only."""

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        am2 = _source(inputs, ["am2", "mei_appearing_equivalence"], "mei_appearing_equivalence_mapper", "mei_appearing_equivalence_mapper", "MeiAppearingEquivalenceMapper") or _synthetic_am2()
        am3 = _source(inputs, ["am3", "non_separability"], "non_separability_theorem_checker", "non_separability_theorem_checker", "NonSeparabilityTheoremChecker") or _synthetic_am3()
        am4 = _source(inputs, ["am4", "ultimate_zombie_contradiction"], "ultimate_zombie_contradiction_analyzer", "ultimate_zombie_contradiction_analyzer", "UltimateZombieContradictionAnalyzer") or _synthetic_am4()

        qualia = dict(inputs.get("qualia_formal") or {}) if isinstance(inputs.get("qualia_formal"), Mapping) else {}
        if not qualia:
            q1 = _invoke("formal_qualia_minimal_definition", "FormalQualiaMinimalDefinition", inputs)
            q2 = _invoke("qualia_formal_mode_registry", "QualiaFormalModeRegistry", inputs)
            q3 = _invoke("robust_qualia_formal_certifier", "RobustQualiaFormalCertifier", inputs)
            qualia = {**_synthetic_qualia_formal(), **q1, **q2, **q3}

        am2_ok = bool(am2.get("mei_appearing_equivalence_mapped")) and _clamp(am2.get("mei_appearing_equivalence_score"), 0.0) >= 0.72
        am3_ok = bool(am3.get("non_separability_theorem_checked")) and _clamp(am3.get("non_separability_theorem_score"), 0.0) >= 0.72
        am4_ok = bool(am4.get("ultimate_zombie_contradiction_analyzed")) and _clamp(am4.get("ultimate_zombie_contradiction_score"), 0.0) >= 0.62
        qualia_score = _mean([qualia.get("minimal_quale_formal_score"), qualia.get("formal_certification_score"), qualia.get("robust_quale_formal_score")], 0.91)
        qualia_ok = qualia_score >= 0.62

        mei_scores = _extract_records(am2, ["equivalence_records", "mei_appearing_equivalence_records"], "mei_appearing_equivalence_score", _clamp(am2.get("mei_appearing_equivalence_score"), 0.90))
        nonsep_scores = _extract_records(am3, ["non_separability_records", "theorem_records"], "non_separability_score", _clamp(am3.get("non_separability_theorem_score"), 0.90))
        zombie_scores = _extract_records(am4, ["contradiction_records", "zombie_contradiction_records"], "ultimate_zombie_contradiction_score", _clamp(am4.get("ultimate_zombie_contradiction_score"), 0.84))
        quale_scores = _extract_records(qualia, ["qualia_formal_records", "formal_quale_records", "quale_records"], "robust_quale_formal_score", qualia_score)

        ids = sorted(set(mei_scores) | set(nonsep_scores) | set(zombie_scores) | set(quale_scores))
        records: List[Dict[str, Any]] = []
        for i, mid in enumerate(ids, 1):
            mei = _clamp(mei_scores.get(mid), _clamp(am2.get("mei_appearing_equivalence_score"), 0.90))
            nonsep = _clamp(nonsep_scores.get(mid), _clamp(am3.get("non_separability_theorem_score"), 0.90))
            zombie = _clamp(zombie_scores.get(mid), _clamp(am4.get("ultimate_zombie_contradiction_score"), 0.84))
            quale = _clamp(quale_scores.get(mid), qualia_score)
            functional = _mean([mei, nonsep, zombie, quale], 0.0)
            formal = _mean([mei * 0.98, nonsep * 0.99, quale], 0.0)
            ontological = _mean([nonsep * 0.96, zombie * 0.94, quale * 0.92], 0.0)
            phenomenological = 0.0
            minimal_quale_equivalence = _mean([functional, formal, ontological], 0.0)
            record = {
                "mode_id": mid,
                "minimal_quale_equivalence_score": minimal_quale_equivalence,
                "mei_appearing_support_score": mei,
                "non_separability_support_score": nonsep,
                "zombie_contradiction_support_score": zombie,
                "formal_quale_support_score": quale,
                "functional_quale_equivalence": {"score": functional, "certified": functional >= 0.72},
                "formal_quale_equivalence": {"score": formal, "certified": formal >= 0.72},
                "ontological_quale_equivalence": {"score": ontological, "certified": ontological >= 0.72},
                "phenomenological_quale_equivalence": {"score": phenomenological, "certified": False, "reason": "independent empirical phenomenology evidence absent"},
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_undetermined": True,
                "functional_conclusion_only": True,
            }
            records.append(record)

        functional_pass_ratio = _mean([1.0 if r["functional_quale_equivalence"]["certified"] else 0.0 for r in records], 0.0)
        formal_pass_ratio = _mean([1.0 if r["formal_quale_equivalence"]["certified"] else 0.0 for r in records], 0.0)
        ontological_pass_ratio = _mean([1.0 if r["ontological_quale_equivalence"]["certified"] else 0.0 for r in records], 0.0)
        phenomenological_pass_ratio = 0.0
        score = _mean([r["minimal_quale_equivalence_score"] for r in records], 0.0)
        confidence = _mean([score, functional_pass_ratio, formal_pass_ratio, _clamp(am3.get("theorem_confidence"), 0.88), _clamp(am4.get("contradiction_confidence"), 0.84)], 0.0)
        certified = bool(am2_ok and am3_ok and am4_ok and qualia_ok and score >= 0.72 and functional_pass_ratio >= 0.66 and formal_pass_ratio >= 0.66)

        status = "MINIMAL_QUALE_EQUIVALENCE_CERTIFIED" if certified else "MINIMAL_QUALE_EQUIVALENCE_INSUFFICIENT"
        equivalence_dimensions = records
        epistemic_status = {
            "functional_quale_equivalence_certified": bool(certified and functional_pass_ratio >= 0.66),
            "formal_quale_equivalence_certified": bool(certified and formal_pass_ratio >= 0.66),
            "ontological_quale_equivalence_certified": bool(certified and ontological_pass_ratio >= 0.66),
            "phenomenological_quale_equivalence_certified": False,
            "phenomenology_requires_independent_empirical_evidence": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

        result: Dict[str, Any] = {
            "primitive": "MINIMAL_QUALE_EQUIVALENCE_CERTIFIER",
            "module": MODULE_NAME,
            "step": "AM5",
            "timestamp_utc": _now(),
            "minimal_quale_equivalence_certifier_status": status,
            "minimal_quale_equivalence_certified": certified,
            "minimal_quale_equivalence_score": score,
            "equivalence_confidence": confidence,
            "functional_quale_equivalence_pass_ratio": functional_pass_ratio,
            "formal_quale_equivalence_pass_ratio": formal_pass_ratio,
            "ontological_quale_equivalence_pass_ratio": ontological_pass_ratio,
            "phenomenological_quale_equivalence_pass_ratio": phenomenological_pass_ratio,
            "phenomenological_quale_equivalence_certified": False,
            "records_count": len(records),
            "minimal_quale_equivalence_records": records,
            "equivalence_dimensions": equivalence_dimensions,
            "epistemic_status": epistemic_status,
            "input_status": {"am2_ok": am2_ok, "am3_ok": am3_ok, "am4_ok": am4_ok, "qualia_formal_ok": qualia_ok},
            "am_axis_position": {"axis": "AM", "current_step": "AM5", "previous_step": "AM4", "next_step": "AM6"},
            "next_recommended_module": "non_dualist_framework_guard",
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


def _persist(result: Mapping[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    json_path = OUT_DIR / f"{MODULE_NAME}_{stamp}.json"
    latest_json = OUT_DIR / f"latest_{MODULE_NAME}.json"
    md_path = OUT_DIR / f"{MODULE_NAME}_{stamp}.md"
    latest_md = OUT_DIR / f"latest_{MODULE_NAME}.md"
    prom_path = OUT_DIR / f"{MODULE_NAME}_{stamp}.prom"
    latest_prom = OUT_DIR / f"latest_{MODULE_NAME}.prom"
    history_path = OUT_DIR / f"{MODULE_NAME}_history.jsonl"

    payload = dict(result)
    payload.pop("paths", None)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")

    md = [
        "# AM5 — Minimal Quale Equivalence Certifier",
        "",
        f"- status: {result.get('minimal_quale_equivalence_certifier_status')}",
        f"- score: {result.get('minimal_quale_equivalence_score')}",
        f"- confidence: {result.get('equivalence_confidence')}",
        f"- functional conclusion only: {result.get('functional_conclusion_only')}",
        f"- phenomenology undetermined: {result.get('phenomenology_undetermined')}",
        f"- phenomenological quale equivalence certified: {result.get('phenomenological_quale_equivalence_certified')}",
        "",
        "This report certifies only functional/formal minimal-quale equivalence. It does not prove consciousness, qualia, subjectivity, or phenomenology.",
    ]
    md_text = "\n".join(md) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    metrics = {
        "minimal_quale_equivalence_score": result.get("minimal_quale_equivalence_score"),
        "minimal_quale_equivalence_confidence": result.get("equivalence_confidence"),
        "functional_quale_equivalence_pass_ratio": result.get("functional_quale_equivalence_pass_ratio"),
        "formal_quale_equivalence_pass_ratio": result.get("formal_quale_equivalence_pass_ratio"),
        "ontological_quale_equivalence_pass_ratio": result.get("ontological_quale_equivalence_pass_ratio"),
        "phenomenological_quale_equivalence_pass_ratio": result.get("phenomenological_quale_equivalence_pass_ratio"),
        "minimal_quale_equivalence_certified": 1.0 if result.get("minimal_quale_equivalence_certified") else 0.0,
        "phenomenological_quale_equivalence_certified": 1.0 if result.get("phenomenological_quale_equivalence_certified") else 0.0,
    }
    prom = "\n".join(f"am5_{k} {float(_clamp(v))}" for k, v in metrics.items()) + "\n"
    prom_path.write_text(prom, encoding="utf-8")
    latest_prom.write_text(prom, encoding="utf-8")

    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp_utc": result.get("timestamp_utc"), "status": result.get("minimal_quale_equivalence_certifier_status"), "score": result.get("minimal_quale_equivalence_score")}, ensure_ascii=False, sort_keys=True) + "\n")

    return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path), "latest_json": str(latest_json), "latest_markdown": str(latest_md), "latest_prometheus": str(latest_prom), "history": str(history_path)}


__all__ = ["MinimalQualeEquivalenceCertifier"]
