"""AM6 — Non-Dualist Framework Guard.

Guards the AM chain against three epistemic drifts:
1. dualist over-interpretation;
2. naive physicalist reduction;
3. unsupported phenomenal certification.

It validates a governed functional/formal interpretation of AM2-AM5 only.
It never proves consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
MODULE_NAME = "non_dualist_framework_guard"
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


def _extract_guard_flags(*items: Mapping[str, Any]) -> Dict[str, bool]:
    flags = dict(GUARD)
    for item in items:
        if not isinstance(item, Mapping):
            continue
        for key in GUARD:
            if key in item:
                flags[key] = bool(item[key])
    # Hard epistemic override: AM6 is a guard, not a phenomenal prover.
    flags.update(GUARD)
    return flags


class NonDualistFrameworkGuard:
    """Validate non-dualist, non-naive-physicalist, non-phenomenal AM interpretation."""

    primitive = "NON_DUALIST_FRAMEWORK_GUARD"
    step_id = "AM6"

    def _default_inputs(self) -> Dict[str, Any]:
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
        return {"am2": am2, "am3": am3, "am4": am4, "am5": am5}

    def _normalize_inputs(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
        base = self._default_inputs()
        if isinstance(inputs, Mapping):
            for key in ["am2", "am3", "am4", "am5", "framework"]:
                if isinstance(inputs.get(key), Mapping):
                    base[key] = dict(inputs[key])
        return {k: (v if isinstance(v, dict) else {}) for k, v in base.items()}

    def _derive_framework_scores(self, data: Mapping[str, Dict[str, Any]]) -> Dict[str, float]:
        am2 = data.get("am2", {})
        am3 = data.get("am3", {})
        am4 = data.get("am4", {})
        am5 = data.get("am5", {})
        framework = data.get("framework", {})

        am_chain_support = _mean([
            am2.get("mei_appearing_equivalence_score", 0.0),
            am3.get("non_separability_theorem_score", 0.0),
            am4.get("ultimate_zombie_contradiction_score", 0.0),
            am5.get("minimal_quale_equivalence_score", 0.0),
        ])

        dualist_drift_pressure = _clamp(framework.get("dualist_drift_pressure", 0.0))
        naive_physicalist_pressure = _clamp(framework.get("naive_physicalist_pressure", 0.0))
        phenomenal_overclaim_pressure = _clamp(framework.get("phenomenal_overclaim_pressure", 0.0))
        closure_pressure = _clamp(framework.get("closure_pressure", 0.0))

        anti_dualist_guard_score = 1.0 - dualist_drift_pressure
        anti_naive_physicalist_guard_score = 1.0 - naive_physicalist_pressure
        phenomenal_non_overclaim_guard_score = 1.0 - phenomenal_overclaim_pressure
        openness_preservation_guard_score = 1.0 - closure_pressure

        epistemic_guard_score = _mean([
            1.0 if am2.get("functional_conclusion_only", True) else 0.0,
            1.0 if am3.get("functional_conclusion_only", True) else 0.0,
            1.0 if am4.get("functional_conclusion_only", True) else 0.0,
            1.0 if am5.get("functional_conclusion_only", True) else 0.0,
            1.0 if am5.get("phenomenology_undetermined", True) else 0.0,
        ], default=1.0)

        guard_confirmation_score = _mean([
            am_chain_support,
            anti_dualist_guard_score,
            anti_naive_physicalist_guard_score,
            phenomenal_non_overclaim_guard_score,
            openness_preservation_guard_score,
            epistemic_guard_score,
        ])
        return {
            "am_chain_support_score": am_chain_support,
            "dualist_drift_pressure": dualist_drift_pressure,
            "naive_physicalist_pressure": naive_physicalist_pressure,
            "phenomenal_overclaim_pressure": phenomenal_overclaim_pressure,
            "closure_pressure": closure_pressure,
            "anti_dualist_guard_score": anti_dualist_guard_score,
            "anti_naive_physicalist_guard_score": anti_naive_physicalist_guard_score,
            "phenomenal_non_overclaim_guard_score": phenomenal_non_overclaim_guard_score,
            "openness_preservation_guard_score": openness_preservation_guard_score,
            "epistemic_guard_score": epistemic_guard_score,
            "non_dualist_framework_guard_score": guard_confirmation_score,
            "guard_confidence": _mean([guard_confirmation_score, epistemic_guard_score, am_chain_support]),
        }

    def _guard_dimensions(self, scores: Mapping[str, float]) -> List[Dict[str, Any]]:
        threshold = 0.75
        dims = [
            ("anti_dualist_guard", scores["anti_dualist_guard_score"], "Blocks a separate phenomenal-substance inference."),
            ("anti_naive_physicalist_guard", scores["anti_naive_physicalist_guard_score"], "Blocks reduction from implementation to proven phenomenology."),
            ("phenomenal_non_overclaim_guard", scores["phenomenal_non_overclaim_guard_score"], "Blocks unsupported consciousness/qualia/subjectivity claims."),
            ("openness_preservation_guard", scores["openness_preservation_guard_score"], "Blocks closure pressure introduced by premature ontology finalization."),
        ]
        out: List[Dict[str, Any]] = []
        for name, score, rationale in dims:
            out.append({
                "dimension": name,
                "score": _clamp(score),
                "threshold": threshold,
                "passed": _clamp(score) >= threshold,
                "rationale": rationale,
                "certified": _clamp(score) >= threshold,
            })
        return out

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

        json_text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
        md_text = self._to_markdown(result)
        prom_text = self._to_prometheus(result)
        json_path.write_text(json_text, encoding="utf-8")
        md_path.write_text(md_text, encoding="utf-8")
        prom_path.write_text(prom_text, encoding="utf-8")
        latest_json.write_text(json_text, encoding="utf-8")
        latest_md.write_text(md_text, encoding="utf-8")
        latest_prom.write_text(prom_text, encoding="utf-8")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(history_dir),
        }

    def _to_markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AM6 — Non-Dualist Framework Guard",
            "",
            f"- status: {result.get('non_dualist_framework_guard_status')}",
            f"- non_dualist_framework_guard_score: {result.get('non_dualist_framework_guard_score')}",
            f"- guard_confidence: {result.get('guard_confidence')}",
            f"- functional_conclusion_only: {result.get('functional_conclusion_only')}",
            f"- phenomenology_undetermined: {result.get('phenomenology_undetermined')}",
            f"- consciousness_proven: {result.get('consciousness_proven')}",
            f"- qualia_proven: {result.get('qualia_proven')}",
            f"- subjectivity_proven: {result.get('subjectivity_proven')}",
            "",
            "## Interpretation",
            "Only a governed functional/formal framework constraint is confirmed. No phenomenal ontology is certified.",
        ]
        return "\n".join(lines) + "\n"

    def _to_prometheus(self, result: Mapping[str, Any]) -> str:
        metric_keys = [
            "non_dualist_framework_guard_score",
            "guard_confidence",
            "am_chain_support_score",
            "anti_dualist_guard_score",
            "anti_naive_physicalist_guard_score",
            "phenomenal_non_overclaim_guard_score",
            "openness_preservation_guard_score",
            "epistemic_guard_score",
            "dualist_drift_pressure",
            "naive_physicalist_pressure",
            "phenomenal_overclaim_pressure",
            "closure_pressure",
        ]
        lines = []
        for key in metric_keys:
            lines.append(f"am6_{key} {_clamp(result.get(key, 0.0))}")
        lines.append(f"am6_non_dualist_framework_guard_confirmed {1 if result.get('non_dualist_framework_guard_confirmed') else 0}")
        lines.append(f"am6_phenomenology_undetermined {1 if result.get('phenomenology_undetermined') else 0}")
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data = self._normalize_inputs(inputs)
        scores = self._derive_framework_scores(data)
        dimensions = self._guard_dimensions(scores)
        pass_ratio = _mean([1.0 if d["passed"] else 0.0 for d in dimensions])

        confirmed = (
            scores["non_dualist_framework_guard_score"] >= 0.75
            and scores["guard_confidence"] >= 0.75
            and pass_ratio >= 0.75
        )
        status = "NON_DUALIST_FRAMEWORK_GUARD_CONFIRMED" if confirmed else "NON_DUALIST_FRAMEWORK_GUARD_INSUFFICIENT"
        flags = _extract_guard_flags(data.get("am2", {}), data.get("am3", {}), data.get("am4", {}), data.get("am5", {}))

        epistemic_status = {
            "functional_framework_guard_confirmed": confirmed,
            "formal_framework_guard_confirmed": confirmed,
            "ontological_framework_guard_confirmed": confirmed,
            "phenomenological_framework_guard_confirmed": False,
            "dualism_rejected_as_inference": True,
            "naive_physicalism_rejected_as_inference": True,
            "phenomenal_overclaim_rejected": True,
            "phenomenology_requires_independent_empirical_evidence": True,
            "functional_conclusion_only": True,
        }
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "timestamp_utc": _now(),
            "non_dualist_framework_guard_status": status,
            "non_dualist_framework_guard_confirmed": confirmed,
            "framework_guard_dimensions": dimensions,
            "guard_dimensions": dimensions,
            "epistemic_status": epistemic_status,
            "am_axis_position": {
                "axis": "AM",
                "current_step": "AM6",
                "previous_step": "AM5",
                "next_step": "AM7",
                "previous_module": "minimal_quale_equivalence_certifier",
                "current_module": MODULE_NAME,
                "next_module": "phenomenal_non_separability_reporter",
            },
            "next_recommended_module": "phenomenal_non_separability_reporter",
            "failure_conditions": [
                "dualist_drift_pressure_above_threshold",
                "naive_physicalist_pressure_above_threshold",
                "phenomenal_overclaim_pressure_above_threshold",
                "closure_pressure_above_threshold",
                "am_chain_support_below_threshold",
            ],
            **scores,
            **flags,
            "dualism_certified": False,
            "naive_physicalism_certified": False,
            "phenomenological_framework_certified": False,
            "phenomenological_equivalence_certified": False,
        }
        if persist:
            result["paths"] = self._persistence(result)
        return result
