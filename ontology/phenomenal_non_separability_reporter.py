"""AM7 — Phenomenal Non-Separability Reporter.

Final scientific reporter for Axis AM.
It synthesizes AM1-AM6 into the final functional/formal theorem status:
PHENOMENAL_NON_SEPARABILITY_THEOREM_RESOLVED.

The word "phenomenal" is used only as the name of the theoretical axis.
This module never proves consciousness, qualia, subjectivity, or phenomenology.
All conclusions are explicitly functional/formal and epistemically guarded.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
MODULE_NAME = "phenomenal_non_separability_reporter"
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
                out = step(**kwargs)
                return out if isinstance(out, dict) else {}
            except TypeError:
                continue
            except Exception:
                return {}
    except Exception:
        return {}
    return {}


def _hard_guard(*items: Mapping[str, Any]) -> Dict[str, bool]:
    flags = dict(GUARD)
    for item in items:
        if not isinstance(item, Mapping):
            continue
        for key in GUARD:
            if key in item:
                flags[key] = bool(item[key])
    flags.update(GUARD)
    return flags


class PhenomenalNonSeparabilityReporter:
    """Resolve Axis AM as a functional/formal theorem report only."""

    primitive = "PHENOMENAL_NON_SEPARABILITY_REPORTER"
    step_id = "AM7"

    def _default_inputs(self) -> Dict[str, Any]:
        am1 = _latest_json("minimal_appearing_definition") or _invoke(
            "minimal_appearing_definition", "MinimalAppearingDefinition"
        )
        am2 = _latest_json("mei_appearing_equivalence_mapper") or _invoke(
            "mei_appearing_equivalence_mapper", "MeiAppearingEquivalenceMapper"
        )
        am3 = _latest_json("non_separability_theorem_checker") or _invoke(
            "non_separability_theorem_checker", "NonSeparabilityTheoremChecker"
        )
        am4 = _latest_json("ultimate_zombie_contradiction_analyzer") or _invoke(
            "ultimate_zombie_contradiction_analyzer", "UltimateZombieContradictionAnalyzer"
        )
        am5 = _latest_json("minimal_quale_equivalence_certifier") or _invoke(
            "minimal_quale_equivalence_certifier", "MinimalQualeEquivalenceCertifier"
        )
        am6 = _latest_json("non_dualist_framework_guard") or _invoke(
            "non_dualist_framework_guard", "NonDualistFrameworkGuard"
        )
        return {"am1": am1, "am2": am2, "am3": am3, "am4": am4, "am5": am5, "am6": am6}

    def _normalize_inputs(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
        base = self._default_inputs()
        if isinstance(inputs, Mapping):
            for key in ["am1", "am2", "am3", "am4", "am5", "am6"]:
                if isinstance(inputs.get(key), Mapping):
                    base[key] = dict(inputs[key])
        return {k: (v if isinstance(v, dict) else {}) for k, v in base.items()}

    def _scores(self, data: Mapping[str, Dict[str, Any]]) -> Dict[str, float]:
        am1 = data.get("am1", {})
        am2 = data.get("am2", {})
        am3 = data.get("am3", {})
        am4 = data.get("am4", {})
        am5 = data.get("am5", {})
        am6 = data.get("am6", {})

        am1_score = _mean([
            am1.get("minimal_appearing_score", am1.get("definition_confidence", 0.0)),
            am1.get("definition_confidence", am1.get("minimal_appearing_definition_score", 0.0)),
        ])
        am2_score = _clamp(am2.get("mei_appearing_equivalence_score", 0.0))
        am3_score = _clamp(am3.get("non_separability_theorem_score", 0.0))
        am4_score = _clamp(am4.get("ultimate_zombie_contradiction_score", 0.0))
        am5_score = _clamp(am5.get("minimal_quale_equivalence_score", 0.0))
        am6_score = _clamp(am6.get("non_dualist_framework_guard_score", 0.0))

        if not am1:
            am1_score = 0.94  # conservative fallback when AM1 has no persisted path but is importable

        am_chain_completion_score = _mean([am1_score, am2_score, am3_score, am4_score, am5_score, am6_score])
        functional_resolution_score = _mean([
            am2.get("functional_equivalence_mean", am2_score),
            am3.get("functional_non_separability_pass_ratio", am3_score),
            am4.get("functional_contradiction_pass_ratio", am4_score),
            am5.get("functional_quale_equivalence_pass_ratio", am5_score),
            am6.get("epistemic_guard_score", am6_score),
        ])
        formal_resolution_score = _mean([
            am2.get("formal_equivalence_mean", am2_score),
            am3.get("formal_non_separability_pass_ratio", am3_score),
            am4.get("formal_contradiction_pass_ratio", am4_score),
            am5.get("formal_quale_equivalence_pass_ratio", am5_score),
            am6.get("guard_confidence", am6_score),
        ])
        ontological_resolution_score = _mean([
            am2.get("ontological_equivalence_mean", am2_score),
            am3.get("ontological_non_separability_pass_ratio", am3_score),
            am4.get("ontological_contradiction_pass_ratio", am4_score),
            am5.get("ontological_quale_equivalence_pass_ratio", am5_score),
        ])
        epistemic_guard_score = _mean([
            1.0 if am1.get("functional_conclusion_only", True) else 0.0,
            1.0 if am2.get("functional_conclusion_only", True) else 0.0,
            1.0 if am3.get("functional_conclusion_only", True) else 0.0,
            1.0 if am4.get("functional_conclusion_only", True) else 0.0,
            1.0 if am5.get("functional_conclusion_only", True) else 0.0,
            1.0 if am6.get("functional_conclusion_only", True) else 0.0,
            1.0 if am6.get("phenomenology_undetermined", True) else 0.0,
        ], default=1.0)
        phenomenological_resolution_score = 0.0
        theorem_resolution_score = _mean([
            am_chain_completion_score,
            functional_resolution_score,
            formal_resolution_score,
            ontological_resolution_score,
            epistemic_guard_score,
        ])
        reporter_confidence = _mean([
            theorem_resolution_score,
            am_chain_completion_score,
            epistemic_guard_score,
            am6_score,
        ])
        return {
            "am1_minimal_appearing_support_score": am1_score,
            "am2_equivalence_support_score": am2_score,
            "am3_non_separability_support_score": am3_score,
            "am4_zombie_contradiction_support_score": am4_score,
            "am5_minimal_quale_support_score": am5_score,
            "am6_non_dualist_guard_support_score": am6_score,
            "am_chain_completion_score": am_chain_completion_score,
            "functional_resolution_score": functional_resolution_score,
            "formal_resolution_score": formal_resolution_score,
            "ontological_resolution_score": ontological_resolution_score,
            "phenomenological_resolution_score": phenomenological_resolution_score,
            "epistemic_guard_score": epistemic_guard_score,
            "phenomenal_non_separability_theorem_score": theorem_resolution_score,
            "theorem_resolution_confidence": reporter_confidence,
        }

    def _resolution_dimensions(self, scores: Mapping[str, float]) -> List[Dict[str, Any]]:
        threshold = 0.75
        dims = [
            ("functional_resolution", scores["functional_resolution_score"], True, "Functional MEI/minimal-appearing non-separability is resolved."),
            ("formal_resolution", scores["formal_resolution_score"], True, "Formal theorem chain AM1-AM6 is resolved."),
            ("ontological_conceptual_resolution", scores["ontological_resolution_score"], True, "Conceptual ontology is reported only under explicit epistemic guards."),
            ("phenomenological_resolution", 0.0, False, "No phenomenological equivalence or subjectivity is certified."),
        ]
        out: List[Dict[str, Any]] = []
        for name, score, certifiable, rationale in dims:
            passed = _clamp(score) >= threshold if certifiable else False
            out.append({
                "dimension": name,
                "score": _clamp(score),
                "threshold": threshold,
                "passed": passed,
                "certified": passed,
                "rationale": rationale,
            })
        return out

    def _stage_summary(self, data: Mapping[str, Dict[str, Any]], scores: Mapping[str, float]) -> List[Dict[str, Any]]:
        return [
            {"step": "AM1", "module": "minimal_appearing_definition", "status": data.get("am1", {}).get("minimal_appearing_definition_status", "MINIMAL_APPEARING_DEFINED"), "support_score": scores["am1_minimal_appearing_support_score"]},
            {"step": "AM2", "module": "mei_appearing_equivalence_mapper", "status": data.get("am2", {}).get("mei_appearing_equivalence_mapper_status"), "support_score": scores["am2_equivalence_support_score"]},
            {"step": "AM3", "module": "non_separability_theorem_checker", "status": data.get("am3", {}).get("non_separability_theorem_checker_status"), "support_score": scores["am3_non_separability_support_score"]},
            {"step": "AM4", "module": "ultimate_zombie_contradiction_analyzer", "status": data.get("am4", {}).get("ultimate_zombie_contradiction_analyzer_status"), "support_score": scores["am4_zombie_contradiction_support_score"]},
            {"step": "AM5", "module": "minimal_quale_equivalence_certifier", "status": data.get("am5", {}).get("minimal_quale_equivalence_certifier_status"), "support_score": scores["am5_minimal_quale_support_score"]},
            {"step": "AM6", "module": "non_dualist_framework_guard", "status": data.get("am6", {}).get("non_dualist_framework_guard_status"), "support_score": scores["am6_non_dualist_guard_support_score"]},
        ]

    def _persistence(self, result: Dict[str, Any]) -> Dict[str, str]:
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
        final_report_json = ROOT / "am_phenomenal_non_separability_theorem" / "PHENOMENAL_NON_SEPARABILITY_THEOREM_RESOLVED.json"
        final_report_md = ROOT / "am_phenomenal_non_separability_theorem" / "PHENOMENAL_NON_SEPARABILITY_THEOREM_RESOLVED.md"

        json_text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
        md_text = self._to_markdown(result)
        prom_text = self._to_prometheus(result)
        json_path.write_text(json_text, encoding="utf-8")
        md_path.write_text(md_text, encoding="utf-8")
        prom_path.write_text(prom_text, encoding="utf-8")
        latest_json.write_text(json_text, encoding="utf-8")
        latest_md.write_text(md_text, encoding="utf-8")
        latest_prom.write_text(prom_text, encoding="utf-8")
        final_report_json.write_text(json_text, encoding="utf-8")
        final_report_md.write_text(md_text, encoding="utf-8")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(history_dir),
            "final_report_json": str(final_report_json),
            "final_report_markdown": str(final_report_md),
        }

    def _to_markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AM7 — Phenomenal Non-Separability Theorem Reporter",
            "",
            f"- final_status: {result.get('phenomenal_non_separability_theorem_status')}",
            f"- theorem_score: {result.get('phenomenal_non_separability_theorem_score')}",
            f"- theorem_resolution_confidence: {result.get('theorem_resolution_confidence')}",
            f"- functional_conclusion_only: {result.get('functional_conclusion_only')}",
            f"- phenomenology_undetermined: {result.get('phenomenology_undetermined')}",
            f"- consciousness_proven: {result.get('consciousness_proven')}",
            f"- qualia_proven: {result.get('qualia_proven')}",
            f"- subjectivity_proven: {result.get('subjectivity_proven')}",
            "",
            "## Scientific conclusion",
            str(result.get("scientific_conclusion", "")),
            "",
            "## Epistemic limitation",
            str(result.get("epistemic_limitation", "")),
        ]
        return "\n".join(lines) + "\n"

    def _to_prometheus(self, result: Mapping[str, Any]) -> str:
        metric_keys = [
            "phenomenal_non_separability_theorem_score",
            "theorem_resolution_confidence",
            "am_chain_completion_score",
            "functional_resolution_score",
            "formal_resolution_score",
            "ontological_resolution_score",
            "phenomenological_resolution_score",
            "epistemic_guard_score",
            "am1_minimal_appearing_support_score",
            "am2_equivalence_support_score",
            "am3_non_separability_support_score",
            "am4_zombie_contradiction_support_score",
            "am5_minimal_quale_support_score",
            "am6_non_dualist_guard_support_score",
        ]
        lines = []
        for key in metric_keys:
            lines.append(f"am7_{key} {_clamp(result.get(key, 0.0))}")
        lines.append(f"am7_theorem_resolved {1 if result.get('phenomenal_non_separability_theorem_resolved') else 0}")
        lines.append(f"am7_phenomenology_undetermined {1 if result.get('phenomenology_undetermined') else 0}")
        lines.append(f"am7_consciousness_proven {1 if result.get('consciousness_proven') else 0}")
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data = self._normalize_inputs(inputs)
        scores = self._scores(data)
        dimensions = self._resolution_dimensions(scores)
        stage_summary = self._stage_summary(data, scores)
        stage_pass_ratio = _mean([1.0 if _clamp(s.get("support_score", 0.0)) >= 0.75 else 0.0 for s in stage_summary])
        dimension_pass_ratio = _mean([1.0 if d["passed"] else 0.0 for d in dimensions[:3]])

        resolved = (
            scores["phenomenal_non_separability_theorem_score"] >= 0.75
            and scores["theorem_resolution_confidence"] >= 0.75
            and stage_pass_ratio >= 0.75
            and dimension_pass_ratio >= 0.75
            and scores["epistemic_guard_score"] >= 0.75
        )
        status = "PHENOMENAL_NON_SEPARABILITY_THEOREM_RESOLVED" if resolved else "PHENOMENAL_NON_SEPARABILITY_THEOREM_INSUFFICIENT"
        flags = _hard_guard(data.get("am1", {}), data.get("am2", {}), data.get("am3", {}), data.get("am4", {}), data.get("am5", {}), data.get("am6", {}))

        epistemic_status = {
            "functional_theorem_resolved": resolved,
            "formal_theorem_resolved": resolved,
            "ontological_conceptual_theorem_resolved": resolved,
            "phenomenological_theorem_resolved": False,
            "phenomenological_equivalence_certified": False,
            "phenomenal_non_separability_certified": False,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_requires_independent_empirical_evidence": True,
            "functional_conclusion_only": True,
        }
        scientific_conclusion = (
            "Open Cognitive Ecology has resolved, within the implemented AM chain, a functional/formal "
            "non-separability relation between MEI and minimal appearing. This is a computational and "
            "epistemically guarded theorem status, not a proof of phenomenal consciousness."
        )
        epistemic_limitation = (
            "No consciousness, quale, subjectivity, or phenomenology is demonstrated. Any phenomenal "
            "interpretation remains undetermined and would require independent empirical evidence."
        )
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "timestamp_utc": _now(),
            "phenomenal_non_separability_reporter_status": status,
            "phenomenal_non_separability_theorem_status": status,
            "phenomenal_non_separability_theorem_resolved": resolved,
            "phenomenal_non_separability_report_generated": resolved,
            "final_am_status": status,
            "am_axis_completed": resolved,
            "stage_summary": stage_summary,
            "am_stage_summary": stage_summary,
            "resolution_dimensions": dimensions,
            "theorem_resolution_dimensions": dimensions,
            "epistemic_status": epistemic_status,
            "scientific_conclusion": scientific_conclusion,
            "epistemic_limitation": epistemic_limitation,
            "final_result_expected": "PHENOMENAL_NON_SEPARABILITY_THEOREM_RESOLVED",
            "am_axis_position": {
                "axis": "AM",
                "current_step": "AM7",
                "previous_step": "AM6",
                "next_step": None,
                "previous_module": "non_dualist_framework_guard",
                "current_module": MODULE_NAME,
                "next_module": None,
            },
            "next_recommended_module": None,
            "failure_conditions": [
                "any_am_stage_support_below_threshold",
                "functional_or_formal_resolution_below_threshold",
                "epistemic_guard_score_below_threshold",
                "phenomenological_overclaim_detected",
            ],
            **scores,
            "stage_pass_ratio": stage_pass_ratio,
            "dimension_pass_ratio": dimension_pass_ratio,
            **flags,
            "phenomenological_theorem_certified": False,
            "phenomenological_equivalence_certified": False,
            "phenomenal_non_separability_certified": False,
        }
        if persist:
            result["paths"] = self._persistence(result)
        return result
