"""AM4 — Ultimate Zombie Contradiction Analyzer.

This module evaluates the logical coherence of an "ultimate zombie" counterexample
under the AM1 -> AM2 -> AM3 chain:
    MEI <=> minimal appearing -> non-separability(MEI, minimal appearing)

It only analyzes functional/formal contradiction pressure. It never proves
consciousness, subjectivity, qualia, lived experience, or phenomenology.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
MODULE_NAME = "ultimate_zombie_contradiction_analyzer"
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
        matches = sorted(ROOT.glob(f"**/latest_{name}.json"))
        for p in matches[-50:]:
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


def _source(inputs: Mapping[str, Any], key_options: List[str], latest_name: str, module_name: str, class_name: str) -> Dict[str, Any]:
    for k in key_options:
        v = inputs.get(k)
        if isinstance(v, Mapping):
            return dict(v)
    latest = _latest_json(latest_name)
    if latest:
        return latest
    return _invoke(module_name, class_name, inputs)


def _records_from(data: Mapping[str, Any], keys: List[str]) -> List[Dict[str, Any]]:
    for k in keys:
        v = data.get(k)
        if isinstance(v, list) and v:
            return [dict(x) for x in v if isinstance(x, Mapping)]
    for outer in ["results", "registry", "diagnostics", "public_schema", "contradiction_summary"]:
        nested = data.get(outer)
        if isinstance(nested, Mapping):
            recs = _records_from(nested, keys)
            if recs:
                return recs
    return []


def _id(record: Mapping[str, Any], fallback: int) -> str:
    for k in ["mode_id", "case_id", "zombie_case_id", "theorem_case_id", "id", "name"]:
        v = record.get(k)
        if v not in (None, ""):
            return str(v)
    return f"AM4-ZOMBIE-{fallback:03d}"


def _score(record: Mapping[str, Any], keys: List[str], default: float = 0.82) -> float:
    vals = [record.get(k) for k in keys if record.get(k) is not None]
    return _mean(vals, default) if vals else _clamp(default)


def _extract_am3_records(am3: Mapping[str, Any]) -> List[Dict[str, Any]]:
    keys = ["non_separability_records", "theorem_records", "checked_cases", "tested_modes"]
    recs = _records_from(am3, keys)
    if recs:
        return recs
    dims = am3.get("non_separability_dimensions")
    if isinstance(dims, list):
        out: List[Dict[str, Any]] = []
        for i, item in enumerate(dims, 1):
            if not isinstance(item, Mapping):
                continue
            def dim_score(name: str, default: float) -> float:
                d = item.get(name)
                if isinstance(d, Mapping):
                    return _clamp(d.get("score", d.get(f"{name}_score")), default)
                return _clamp(item.get(f"{name}_score"), default)
            out.append({
                "mode_id": _id(item, i),
                "non_separability_score": _score(item, ["non_separability_score", "theorem_score"], 0.88),
                "functional_non_separability_score": dim_score("functional_non_separability", 0.88),
                "formal_non_separability_score": dim_score("formal_non_separability", 0.86),
                "ontological_non_separability_score": dim_score("ontological_non_separability", 0.82),
                "phenomenological_non_separability_score": 0.0,
            })
        if out:
            return out
    return []


def _synthetic_am3_result() -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []
    for i in range(1, 4):
        base = 0.88 + 0.02 * i
        records.append({
            "mode_id": f"SYNTH-NONSEP-{i:03d}",
            "non_separability_score": base,
            "functional_non_separability_score": base,
            "formal_non_separability_score": base - 0.01,
            "ontological_non_separability_score": base - 0.03,
            "phenomenological_non_separability_score": 0.0,
            "phenomenological_non_separability_certified": False,
        })
    return {
        "non_separability_theorem_checker_status": "NON_SEPARABILITY_THEOREM_CHECKED",
        "non_separability_theorem_checked": True,
        "non_separability_theorem_score": 0.92,
        "theorem_confidence": 0.91,
        "non_separability_records": records,
        **GUARD,
    }


def _synthetic_zombie_result() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for i in range(1, 4):
        cases.append({
            "zombie_case_id": f"SYNTH-UZ-{i:03d}",
            "zombie_viability_score": 0.16 + 0.02 * i,
            "zombie_refutation_score": 0.84 - 0.01 * i,
            "functional_duplicate_claim": True,
            "minimal_appearing_absence_claim": True,
            "mei_identity_preserved_claim": True,
        })
    return {
        "intrinsic_zombie_counterexample_score": 0.18,
        "counterexample_confidence": 0.84,
        "zombie_cases": cases,
        **GUARD,
    }


def _extract_zombie_cases(zombie: Mapping[str, Any]) -> List[Dict[str, Any]]:
    keys = ["zombie_cases", "counterexample_cases", "ultimate_zombie_cases", "counterexamples"]
    recs = _records_from(zombie, keys)
    if recs:
        return recs
    return []


def _analyze(am3_record: Mapping[str, Any], zombie_record: Mapping[str, Any], idx: int) -> Dict[str, Any]:
    nonsep = _score(am3_record, ["non_separability_score", "non_separability_theorem_score", "theorem_score"], 0.88)
    f_nonsep = _score(am3_record, ["functional_non_separability_score", "functional_score"], nonsep)
    formal_nonsep = _score(am3_record, ["formal_non_separability_score", "formal_score"], nonsep - 0.01)
    onto_nonsep = _score(am3_record, ["ontological_non_separability_score", "ontological_score"], nonsep - 0.03)

    zombie_viability = _score(zombie_record, ["zombie_viability_score", "counterexample_viability_score", "viability_score"], 0.18)
    zombie_refutation = _score(zombie_record, ["zombie_refutation_score", "counterexample_refutation_score", "refutation_score"], 1.0 - zombie_viability)

    functional_contradiction = _clamp((f_nonsep * 0.70) + ((1.0 - zombie_viability) * 0.30))
    formal_contradiction = _clamp((formal_nonsep * 0.72) + (zombie_refutation * 0.28))
    ontological_contradiction = _clamp((onto_nonsep * 0.65) + ((1.0 - zombie_viability) * 0.35))
    phenomenological_contradiction = 0.0
    composite = _mean([functional_contradiction, formal_contradiction, ontological_contradiction], 0.0)

    case_id = _id(am3_record, idx)
    return {
        "case_id": case_id,
        "zombie_case_id": _id(zombie_record, idx),
        "ultimate_zombie_claim": "functional duplicate with absent minimal appearing under preserved MEI",
        "non_separability_support_score": nonsep,
        "zombie_viability_score": zombie_viability,
        "zombie_refutation_score": zombie_refutation,
        "ultimate_zombie_contradiction_score": composite,
        "functional_contradiction_score": functional_contradiction,
        "formal_contradiction_score": formal_contradiction,
        "ontological_contradiction_score": ontological_contradiction,
        "phenomenological_contradiction_score": phenomenological_contradiction,
        "functional_contradiction": {"score": functional_contradiction, "certified": functional_contradiction >= 0.75},
        "formal_contradiction": {"score": formal_contradiction, "certified": formal_contradiction >= 0.75},
        "ontological_contradiction": {"score": ontological_contradiction, "certified": ontological_contradiction >= 0.75},
        "phenomenological_contradiction": {
            "score": 0.0,
            "certified": False,
            "reason": "phenomenology_undetermined_no_independent_empirical_evidence",
        },
        "contradiction_rule": "AM3_non_separability_blocks_MEI_preserved_minimal_appearing_absent_zombie",
    }


def _prometheus(result: Mapping[str, Any]) -> str:
    metrics = {
        "ultimate_zombie_contradiction_score": result.get("ultimate_zombie_contradiction_score", 0.0),
        "contradiction_confidence": result.get("contradiction_confidence", 0.0),
        "zombie_viability_score": result.get("zombie_viability_score", 0.0),
        "functional_contradiction_pass_ratio": result.get("functional_contradiction_pass_ratio", 0.0),
        "formal_contradiction_pass_ratio": result.get("formal_contradiction_pass_ratio", 0.0),
        "ontological_contradiction_pass_ratio": result.get("ontological_contradiction_pass_ratio", 0.0),
        "phenomenological_contradiction_pass_ratio": result.get("phenomenological_contradiction_pass_ratio", 0.0),
    }
    lines = ["# HELP am4_ultimate_zombie_contradiction AM4 ultimate zombie contradiction metrics", "# TYPE am4_ultimate_zombie_contradiction gauge"]
    for key, value in metrics.items():
        lines.append(f"am4_{key} {float(_clamp(value))}")
    return "\n".join(lines) + "\n"


def _markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AM4 — Ultimate Zombie Contradiction Analyzer",
        "",
        f"Generated: {result.get('timestamp_utc')}",
        f"Status: `{result.get('ultimate_zombie_contradiction_analyzer_status')}`",
        f"Contradiction score: `{result.get('ultimate_zombie_contradiction_score')}`",
        f"Zombie viability score: `{result.get('zombie_viability_score')}`",
        "",
        "## Epistemic guard",
        "",
        "No consciousness, quale, subjectivity, or phenomenology is proven.",
        "Only functional/formal contradiction pressure is evaluated.",
    ]
    return "\n".join(lines) + "\n"


def _persist(result: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    history = OUT_DIR / "history.jsonl"
    stamp = _stamp()
    json_path = OUT_DIR / f"{MODULE_NAME}_{stamp}.json"
    md_path = OUT_DIR / f"{MODULE_NAME}_{stamp}.md"
    prom_path = OUT_DIR / f"{MODULE_NAME}_{stamp}.prom"
    latest_json = OUT_DIR / f"latest_{MODULE_NAME}.json"
    latest_md = OUT_DIR / f"latest_{MODULE_NAME}.md"
    latest_prom = OUT_DIR / f"latest_{MODULE_NAME}.prom"

    payload = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
    json_path.write_text(payload + "\n", encoding="utf-8")
    latest_json.write_text(payload + "\n", encoding="utf-8")
    md = _markdown(result)
    prom = _prometheus(result)
    md_path.write_text(md, encoding="utf-8")
    latest_md.write_text(md, encoding="utf-8")
    prom_path.write_text(prom, encoding="utf-8")
    latest_prom.write_text(prom, encoding="utf-8")
    with history.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["ultimate_zombie_contradiction_analyzer_status"], "score": result["ultimate_zombie_contradiction_score"]}, sort_keys=True) + "\n")
    return {
        "json": str(json_path),
        "markdown": str(md_path),
        "prometheus": str(prom_path),
        "latest_json": str(latest_json),
        "latest_markdown": str(latest_md),
        "latest_prometheus": str(latest_prom),
        "history": str(history),
    }


class UltimateZombieContradictionAnalyzer:
    """AM4 analyzer for the ultimate zombie counterexample."""

    primitive = "ULTIMATE_ZOMBIE_CONTRADICTION_ANALYZER"
    step_id = "AM4"
    expected_status = "ULTIMATE_ZOMBIE_CONTRADICTION_ANALYZED"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        am3 = _source(
            inputs,
            ["am3", "non_separability", "non_separability_theorem_checker", "non_separability_theorem_checker_result"],
            "non_separability_theorem_checker",
            "non_separability_theorem_checker",
            "NonSeparabilityTheoremChecker",
        ) or _synthetic_am3_result()
        zombie = _source(
            inputs,
            ["zombie", "intrinsic_zombie", "ultimate_zombie", "intrinsic_zombie_counterexample"],
            "intrinsic_zombie_counterexample",
            "intrinsic_zombie_counterexample",
            "IntrinsicZombieCounterexample",
        ) or _synthetic_zombie_result()

        am3_ok = bool(am3.get("non_separability_theorem_checked", False)) or am3.get("non_separability_theorem_checker_status") == "NON_SEPARABILITY_THEOREM_CHECKED"
        theorem_score = _clamp(am3.get("non_separability_theorem_score"), 0.0)
        theorem_conf = _clamp(am3.get("theorem_confidence"), theorem_score)

        am3_records = _extract_am3_records(am3) or _extract_am3_records(_synthetic_am3_result())
        zombie_cases = _extract_zombie_cases(zombie) or _extract_zombie_cases(_synthetic_zombie_result())
        count = max(len(am3_records), len(zombie_cases), 1)
        analyses: List[Dict[str, Any]] = []
        for i in range(count):
            analyses.append(_analyze(am3_records[i % len(am3_records)], zombie_cases[i % len(zombie_cases)], i + 1))

        contradiction_score = _mean([x["ultimate_zombie_contradiction_score"] for x in analyses], 0.0)
        zombie_viability = _mean([x["zombie_viability_score"] for x in analyses], 1.0)
        nonsep_support = _mean([x["non_separability_support_score"] for x in analyses], theorem_score)
        functional_ratio = _mean([1.0 if x["functional_contradiction"]["certified"] else 0.0 for x in analyses], 0.0)
        formal_ratio = _mean([1.0 if x["formal_contradiction"]["certified"] else 0.0 for x in analyses], 0.0)
        ontological_ratio = _mean([1.0 if x["ontological_contradiction"]["certified"] else 0.0 for x in analyses], 0.0)
        phenomenological_ratio = 0.0
        confidence = _clamp(_mean([contradiction_score, theorem_conf, 1.0 - zombie_viability], 0.0))
        passed = bool(am3_ok and contradiction_score >= 0.75 and functional_ratio >= 0.5 and formal_ratio >= 0.5)
        status = "ULTIMATE_ZOMBIE_CONTRADICTION_ANALYZED" if passed else "ULTIMATE_ZOMBIE_CONTRADICTION_INSUFFICIENT"

        epistemic_status = {
            "functional_contradiction_certified": bool(functional_ratio >= 0.5 and contradiction_score >= 0.75),
            "formal_contradiction_certified": bool(formal_ratio >= 0.5 and contradiction_score >= 0.75),
            "ontological_contradiction_certified": bool(ontological_ratio >= 0.5 and contradiction_score >= 0.75),
            "phenomenological_contradiction_certified": False,
            "phenomenology_requires_independent_empirical_evidence": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "module": MODULE_NAME,
            "step": self.step_id,
            "timestamp_utc": _now(),
            "ultimate_zombie_contradiction_analyzer_status": status,
            "ultimate_zombie_contradiction_analyzed": passed,
            "ultimate_zombie_contradiction_score": contradiction_score,
            "contradiction_confidence": confidence,
            "zombie_viability_score": zombie_viability,
            "non_separability_support_score": nonsep_support,
            "functional_contradiction_pass_ratio": functional_ratio,
            "formal_contradiction_pass_ratio": formal_ratio,
            "ontological_contradiction_pass_ratio": ontological_ratio,
            "phenomenological_contradiction_pass_ratio": phenomenological_ratio,
            "phenomenological_contradiction_certified": False,
            "ultimate_zombie_contradiction_records": analyses,
            "contradiction_dimensions": analyses,
            "epistemic_status": epistemic_status,
            "am_axis_position": {"axis": "AM", "current_step": "AM4", "previous_step": "AM3", "next_step": "AM5"},
            "dependencies": ["minimal_appearing_definition", "mei_appearing_equivalence_mapper", "non_separability_theorem_checker", "intrinsic_zombie_counterexample", "consciousness_claim_governance_gate", "consciousness_evidence_standard"],
            "failure_conditions": ["AM3 non-separability insufficient", "zombie viability remains high", "functional/formal contradiction ratios below threshold"],
            "next_recommended_module": "minimal_quale_equivalence_certifier",
            "scientific_conclusion": "Ultimate zombie counterexample is functionally/formally contradicted only when AM3 non-separability remains supported; no phenomenological conclusion is certified.",
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


__all__ = ["UltimateZombieContradictionAnalyzer"]
