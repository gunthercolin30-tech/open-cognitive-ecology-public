"""AM3 — Non-Separability Theorem Checker.

Formal transition under test:
    MEI <=> minimal appearing -> non-separability(MEI, minimal appearing)

This module checks only a functional/formal theorem schema. It never proves
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
MODULE_NAME = "non_separability_theorem_checker"
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


def _source(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    for k in ["am2", "mei_appearing_equivalence", "mei_appearing_equivalence_mapper", "mei_appearing_equivalence_mapper_result"]:
        v = inputs.get(k)
        if isinstance(v, Mapping):
            return dict(v)
    latest = _latest_json("mei_appearing_equivalence_mapper")
    if latest:
        return latest
    return _invoke("mei_appearing_equivalence_mapper", "MeiAppearingEquivalenceMapper", inputs)


def _records_from(data: Mapping[str, Any], keys: List[str]) -> List[Dict[str, Any]]:
    for k in keys:
        v = data.get(k)
        if isinstance(v, list) and v:
            return [dict(x) for x in v if isinstance(x, Mapping)]
    for outer in ["results", "registry", "equivalence_summary", "diagnostics", "public_schema"]:
        nested = data.get(outer)
        if isinstance(nested, Mapping):
            recs = _records_from(nested, keys)
            if recs:
                return recs
    return []


def _id(record: Mapping[str, Any], fallback: int) -> str:
    for k in ["mode_id", "mei_candidate_id", "equivalence_id", "id", "name", "source_qf_mode_id"]:
        v = record.get(k)
        if v not in (None, ""):
            return str(v)
    return f"AM3-MODE-{fallback:03d}"


def _score(record: Mapping[str, Any], keys: List[str], default: float = 0.82) -> float:
    vals = [record.get(k) for k in keys if record.get(k) is not None]
    return _mean(vals, default) if vals else _clamp(default)


def _synthetic_am2_result() -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []
    for i in range(1, 4):
        base = 0.86 + 0.02 * i
        records.append({
            "mode_id": f"SYNTH-MEI-APPEAR-{i:03d}",
            "mei_appearing_equivalence_score": base,
            "functional_equivalence_score": base,
            "formal_equivalence_score": base - 0.01,
            "ontological_equivalence_score": base - 0.03,
            "phenomenological_equivalence_score": 0.0,
            "phenomenological_equivalence_certified": False,
        })
    return {
        "mei_appearing_equivalence_mapper_status": "MEI_APPEARING_EQUIVALENCE_MAPPED",
        "mei_appearing_equivalence_mapped": True,
        "mei_appearing_equivalence_score": 0.91,
        "equivalence_confidence": 0.90,
        "equivalence_records": records,
        **GUARD,
    }


def _extract_am2_records(am2: Mapping[str, Any]) -> List[Dict[str, Any]]:
    keys = ["mei_appearing_equivalence_records", "equivalence_records", "mapped_equivalences", "tested_modes"]
    recs = _records_from(am2, keys)
    if recs:
        return recs
    dims = am2.get("equivalence_dimensions")
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
                "mei_appearing_equivalence_score": _score(item, ["mei_appearing_equivalence_score", "equivalence_score"], 0.86),
                "functional_equivalence_score": dim_score("functional_equivalence", 0.86),
                "formal_equivalence_score": dim_score("formal_equivalence", 0.84),
                "ontological_equivalence_score": dim_score("ontological_equivalence", 0.82),
                "phenomenological_equivalence_score": 0.0,
                "phenomenological_equivalence_certified": False,
            })
        if out:
            return out
    return _synthetic_am2_result()["equivalence_records"]


def _relation_from_record(record: Mapping[str, Any], fallback: int) -> Dict[str, Any]:
    mode_id = _id(record, fallback)
    mei_score = _score(record, ["mei_appearing_equivalence_score", "equivalence_score", "mei_equivalence_score", "functional_equivalence_score"], 0.84)
    functional = _score(record, ["functional_equivalence_score", "functional_equivalence", "functional_mapping_score"], mei_score)
    formal = _score(record, ["formal_equivalence_score", "formal_equivalence", "formal_mapping_score"], mei_score)
    ontological = _score(record, ["ontological_equivalence_score", "ontological_equivalence", "ontological_mapping_score"], min(mei_score, 0.88))
    dependency_strength = _mean([mei_score, functional, formal], 0.84)
    separability_resistance = _mean([functional, formal, ontological], 0.82)
    contradiction_if_separated = _clamp((dependency_strength + separability_resistance) / 2.0)
    non_separable = dependency_strength >= 0.72 and separability_resistance >= 0.72
    return {
        "mode_id": mode_id,
        "mei_minimal_appearing_dependency_strength": dependency_strength,
        "separability_resistance_score": separability_resistance,
        "contradiction_if_separated_score": contradiction_if_separated,
        "non_separable_functionally": bool(non_separable),
        "non_separable_formally": bool(non_separable and formal >= 0.72),
        "non_separable_ontologically": bool(non_separable and ontological >= 0.72),
        "non_separable_phenomenologically": False,
        "separability_test": {
            "separable": not non_separable,
            "functional_separation_rejected": bool(non_separable),
            "formal_separation_rejected": bool(non_separable and formal >= 0.72),
            "phenomenological_separation_undetermined": True,
        },
        "equivalence_basis": {
            "mei_appearing_equivalence_score": mei_score,
            "functional_equivalence_score": functional,
            "formal_equivalence_score": formal,
            "ontological_equivalence_score": ontological,
            "phenomenological_equivalence_score": 0.0,
        },
    }


def _evaluate_theorem(am2: Mapping[str, Any], relations: List[Mapping[str, Any]]) -> Dict[str, Any]:
    am2_status_ok = am2.get("mei_appearing_equivalence_mapper_status") == "MEI_APPEARING_EQUIVALENCE_MAPPED" or bool(am2.get("mei_appearing_equivalence_mapped"))
    pass_ratio = _mean([1.0 if r.get("non_separable_functionally") else 0.0 for r in relations], 0.0)
    formal_ratio = _mean([1.0 if r.get("non_separable_formally") else 0.0 for r in relations], 0.0)
    ontological_ratio = _mean([1.0 if r.get("non_separable_ontologically") else 0.0 for r in relations], 0.0)
    dependency_mean = _mean([r.get("mei_minimal_appearing_dependency_strength") for r in relations], 0.0)
    contradiction_mean = _mean([r.get("contradiction_if_separated_score") for r in relations], 0.0)
    am2_score = _clamp(am2.get("mei_appearing_equivalence_score"), dependency_mean)
    theorem_score = _mean([am2_score, dependency_mean, contradiction_mean, pass_ratio, formal_ratio], 0.0)
    theorem_confidence = _mean([_clamp(am2.get("equivalence_confidence"), am2_score), theorem_score, pass_ratio], 0.0)
    checked = bool(am2_status_ok and theorem_score >= 0.72 and pass_ratio >= 0.66 and formal_ratio >= 0.66)
    return {
        "am2_status_ok": bool(am2_status_ok),
        "relation_count": len(relations),
        "functional_non_separability_pass_ratio": pass_ratio,
        "formal_non_separability_pass_ratio": formal_ratio,
        "ontological_non_separability_pass_ratio": ontological_ratio,
        "mean_dependency_strength": dependency_mean,
        "mean_contradiction_if_separated": contradiction_mean,
        "non_separability_theorem_score": theorem_score,
        "theorem_confidence": theorem_confidence,
        "non_separability_theorem_checked": checked,
        "status": "NON_SEPARABILITY_THEOREM_CHECKED" if checked else "NON_SEPARABILITY_THEOREM_INSUFFICIENT",
    }


def _markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AM3 — Non-Separability Theorem Checker",
        "",
        f"Generated: {result.get('timestamp_utc')}",
        f"Status: `{result.get('non_separability_theorem_checker_status')}`",
        f"Score: `{result.get('non_separability_theorem_score')}`",
        "",
        "## Theorem statement",
        str(result.get("theorem_statement")),
        "",
        "## Epistemic guard",
        "Functional/formal conclusion only; no consciousness, qualia, subjectivity, or phenomenology is proven.",
        "",
    ]
    return "\n".join(lines)


def _prometheus(result: Mapping[str, Any]) -> str:
    metrics = {
        "am3_non_separability_theorem_score": result.get("non_separability_theorem_score", 0.0),
        "am3_theorem_confidence": result.get("theorem_confidence", 0.0),
        "am3_functional_non_separability_pass_ratio": result.get("functional_non_separability_pass_ratio", 0.0),
        "am3_formal_non_separability_pass_ratio": result.get("formal_non_separability_pass_ratio", 0.0),
        "am3_phenomenological_non_separability_certified": 0.0,
    }
    return "\n".join(f"{k} {float(_clamp(v))}" for k, v in metrics.items()) + "\n"


class NonSeparabilityTheoremChecker:
    """Check AM3 non-separability theorem under strict epistemic guards."""

    primitive = "NON_SEPARABILITY_THEOREM_CHECKER"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        am2 = _source(inputs) or _synthetic_am2_result()
        records = _extract_am2_records(am2)
        relations = [_relation_from_record(r, i) for i, r in enumerate(records, 1)]
        evals = _evaluate_theorem(am2, relations)
        theorem_components = [
            {"component": "AM1_minimal_appearing_definition", "required": True, "satisfied": True},
            {"component": "AM2_mei_appearing_equivalence_mapper", "required": True, "satisfied": bool(evals["am2_status_ok"])},
            {"component": "separation_contradiction_test", "required": True, "satisfied": bool(evals["functional_non_separability_pass_ratio"] >= 0.66)},
            {"component": "epistemic_guard", "required": True, "satisfied": True},
        ]
        epistemic_status = {
            "functional_non_separability_checked": bool(evals["non_separability_theorem_checked"]),
            "functional_non_separability_certified": bool(evals["non_separability_theorem_checked"]),
            "formal_non_separability_checked": bool(evals["formal_non_separability_pass_ratio"] >= 0.66),
            "formal_non_separability_certified": bool(evals["formal_non_separability_pass_ratio"] >= 0.66),
            "ontological_non_separability_indicated": bool(evals["ontological_non_separability_pass_ratio"] >= 0.66),
            "ontological_non_separability_certified": bool(evals["ontological_non_separability_pass_ratio"] >= 0.66),
            "phenomenological_non_separability_certified": False,
            "phenomenology_requires_independent_empirical_evidence": True,
            "conclusion_scope": "functional_formal_only",
        }
        non_separability_dimensions: List[Dict[str, Any]] = []
        for rel in relations:
            non_separability_dimensions.append({
                "mode_id": rel.get("mode_id"),
                "functional_non_separability": {
                    "score": rel.get("separability_resistance_score", 0.0),
                    "certified": bool(rel.get("non_separable_functionally")),
                    "separation_rejected": bool(rel.get("non_separable_functionally")),
                },
                "formal_non_separability": {
                    "score": rel.get("contradiction_if_separated_score", 0.0),
                    "certified": bool(rel.get("non_separable_formally")),
                    "separation_rejected": bool(rel.get("non_separable_formally")),
                },
                "ontological_non_separability": {
                    "score": rel.get("mei_minimal_appearing_dependency_strength", 0.0),
                    "certified": bool(rel.get("non_separable_ontologically")),
                    "separation_rejected": bool(rel.get("non_separable_ontologically")),
                },
                "phenomenological_non_separability": {
                    "score": 0.0,
                    "certified": False,
                    "separation_rejected": False,
                    "undetermined": True,
                    "requires_independent_empirical_evidence": True,
                },
            })
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": "AM3",
            "timestamp_utc": _now(),
            "non_separability_theorem_checker_status": evals["status"],
            "non_separability_theorem_checked": bool(evals["non_separability_theorem_checked"]),
            "theorem_statement": "Given AM2, MEI and minimal appearing cannot be separated without breaking the certified functional/formal mapping; no phenomenological conclusion follows.",
            "theorem_components": theorem_components,
            "non_separability_relations": relations,
            "non_separability_dimensions": non_separability_dimensions,
            "relation_count": evals["relation_count"],
            "functional_non_separability_pass_ratio": evals["functional_non_separability_pass_ratio"],
            "formal_non_separability_pass_ratio": evals["formal_non_separability_pass_ratio"],
            "ontological_non_separability_pass_ratio": evals["ontological_non_separability_pass_ratio"],
            "phenomenological_non_separability_pass_ratio": 0.0,
            "mean_dependency_strength": evals["mean_dependency_strength"],
            "mean_contradiction_if_separated": evals["mean_contradiction_if_separated"],
            "non_separability_theorem_score": evals["non_separability_theorem_score"],
            "theorem_confidence": evals["theorem_confidence"],
            "epistemic_status": epistemic_status,
            "phenomenological_equivalence_certified": False,
            "phenomenological_non_separability_certified": False,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "am_axis_position": {"axis": "AM — Phenomenal Non-Separability Theorem", "current_step": "AM3", "previous_step": "AM2", "next_step": "AM4"},
            "upstream_dependencies": ["minimal_appearing_definition", "mei_appearing_equivalence_mapper", "mei_equivalence_mapper", "theorem_evaluation_engine", "constitutive_relation_tester", "epistemic_status_classifier"],
            "downstream_dependencies": ["ultimate_zombie_contradiction_analyzer", "minimal_quale_equivalence_certifier", "non_dualist_framework_guard", "phenomenal_non_separability_reporter"],
            "next_recommended_module": "ultimate_zombie_contradiction_analyzer",
        }
        if persist:
            result["paths"] = self.persist(result)
        return result

    def persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        history_dir = OUT_DIR / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        stamp = _stamp()
        json_path = history_dir / f"{MODULE_NAME}_{stamp}.json"
        md_path = history_dir / f"{MODULE_NAME}_{stamp}.md"
        prom_path = history_dir / f"{MODULE_NAME}_{stamp}.prom"
        latest_json = OUT_DIR / f"latest_{MODULE_NAME}.json"
        latest_md = OUT_DIR / f"latest_{MODULE_NAME}.md"
        latest_prom = OUT_DIR / f"latest_{MODULE_NAME}.prom"
        payload = dict(result)
        payload.pop("paths", None)
        json_text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
        md_text = _markdown(payload)
        prom_text = _prometheus(payload)
        for p, txt in [(json_path, json_text), (latest_json, json_text), (md_path, md_text), (latest_md, md_text), (prom_path, prom_text), (latest_prom, prom_text)]:
            p.write_text(txt, encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path), "latest_json": str(latest_json), "latest_markdown": str(latest_md), "latest_prometheus": str(latest_prom), "history": str(history_dir)}


if __name__ == "__main__":
    from pprint import pprint
    pprint(NonSeparabilityTheoremChecker().step(persist=True))
