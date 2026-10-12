
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "theory_constraint_engine"

CORE_THEORY_IDS = {"IIT", "GNW", "HOT", "PP"}

DEFAULT_CONSTRAINT_PROFILE = {
    "structural_non_closure": 0.90,
    "falsifiability": 0.88,
    "functional_operationalization": 0.86,
    "longitudinal_compatibility": 0.84,
    "correlation_compatibility": 0.84,
    "anti_phenomenology_claim_guard": 1.00,
}

THEORY_PRIORS = {
    "IIT": {
        "name": "Integrated Information Theory",
        "structural_non_closure": 0.58,
        "falsifiability": 0.62,
        "functional_operationalization": 0.64,
        "longitudinal_compatibility": 0.58,
        "correlation_compatibility": 0.68,
    },
    "GNW": {
        "name": "Global Neuronal Workspace / Global Workspace Theory",
        "structural_non_closure": 0.76,
        "falsifiability": 0.78,
        "functional_operationalization": 0.82,
        "longitudinal_compatibility": 0.72,
        "correlation_compatibility": 0.76,
    },
    "HOT": {
        "name": "Higher-Order Thought / Higher-Order Theories",
        "structural_non_closure": 0.68,
        "falsifiability": 0.70,
        "functional_operationalization": 0.74,
        "longitudinal_compatibility": 0.70,
        "correlation_compatibility": 0.72,
    },
    "PP": {
        "name": "Predictive Processing",
        "structural_non_closure": 0.80,
        "falsifiability": 0.76,
        "functional_operationalization": 0.82,
        "longitudinal_compatibility": 0.78,
        "correlation_compatibility": 0.80,
    },
    "CBP": {
        "name": "Constraint-Based Phenomenology / Constraint-Based Functional Theory",
        "structural_non_closure": 0.90,
        "falsifiability": 0.80,
        "functional_operationalization": 0.86,
        "longitudinal_compatibility": 0.86,
        "correlation_compatibility": 0.84,
    },
}


def _clamp(value: Any) -> float:
    try:
        x = float(value)
    except Exception:
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def _load_json(path: Path) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _default_theories() -> list[dict[str, Any]]:
    theories = []
    for tid, profile in THEORY_PRIORS.items():
        theories.append({
            "theory_id": tid,
            "name": profile["name"],
            "source": "default_registry_prior",
        })
    return theories


class TheoryConstraintEngine:
    primitive = "THEORY_CONSTRAINT_ENGINE"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.output_dir = self.root / "theory_constraint_engine"

    def _autoload_context(self) -> dict[str, Any]:
        registry = _load_json(self.root / "phenomenology_theory_registry" / "phenomenology_theory_registry.json")
        y_report = _load_json(self.root / "phenomenology_correlation_report" / "phenomenology_correlation_report.json")
        y_dashboard = _load_json(self.root / "phenomenology_correlation_dashboard" / "phenomenology_correlation_dashboard.json")
        x_cert = _load_json(self.root / "longitudinal_reflexive_certification" / "longitudinal_reflexive_certification.json")
        return {
            "registry": registry,
            "y_report": y_report,
            "y_dashboard": y_dashboard,
            "x_certification": x_cert,
        }

    def _extract_theories(self, payload: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
        if "theories" in payload:
            return list(payload.get("theories") or [])
        registry = context.get("registry") or {}
        theories = registry.get("theories") if isinstance(registry, dict) else None
        if isinstance(theories, list) and theories:
            return theories
        return _default_theories()

    def _x_support(self, payload: dict[str, Any], context: dict[str, Any]) -> float:
        if "x_support_score" in payload:
            return _clamp(payload.get("x_support_score"))
        x = payload.get("x_results") or context.get("x_certification") or {}
        if isinstance(x, dict):
            candidates = [
                x.get("longitudinal_certification_score"),
                x.get("certification_score"),
                x.get("longitudinal_stability_score"),
                x.get("reflexive_threshold_score"),
                x.get("overall_score"),
            ]
            vals = [_clamp(v) for v in candidates if isinstance(v, (int, float))]
            if vals:
                return _mean(vals)
        return 0.75

    def _y_support(self, payload: dict[str, Any], context: dict[str, Any]) -> float:
        if "y_support_score" in payload:
            return _clamp(payload.get("y_support_score"))
        y = payload.get("y_results") or context.get("y_report") or context.get("y_dashboard") or {}
        if isinstance(y, dict):
            candidates = [
                y.get("report_readiness_score"),
                y.get("dashboard_readiness_score"),
                y.get("replication_confidence"),
                y.get("correlation_support_score"),
                y.get("overall_correlation_score"),
            ]
            if isinstance(y.get("replication_summary"), dict):
                candidates.append(y["replication_summary"].get("replication_confidence"))
            vals = [_clamp(v) for v in candidates if isinstance(v, (int, float))]
            if vals:
                return _mean(vals)
        return 0.75

    def _score_theory(self, theory: dict[str, Any], x_score: float, y_score: float) -> dict[str, Any]:
        tid = str(theory.get("theory_id") or theory.get("id") or theory.get("name") or "UNKNOWN").upper()
        prior = dict(THEORY_PRIORS.get(tid, {}))
        explicit = theory.get("constraint_profile") if isinstance(theory.get("constraint_profile"), dict) else {}
        profile = dict(DEFAULT_CONSTRAINT_PROFILE)
        for key in [
            "structural_non_closure",
            "falsifiability",
            "functional_operationalization",
            "longitudinal_compatibility",
            "correlation_compatibility",
        ]:
            if key in prior:
                profile[key] = prior[key]
            if key in explicit:
                profile[key] = explicit[key]
            if key in theory:
                profile[key] = theory[key]

        constraint_compatibility_score = _mean([
            _clamp(profile["structural_non_closure"]),
            _clamp(profile["falsifiability"]),
            _clamp(profile["functional_operationalization"]),
            _clamp(profile["anti_phenomenology_claim_guard"]),
        ])
        x_support_score = _mean([_clamp(profile["longitudinal_compatibility"]), x_score])
        y_support_score = _mean([_clamp(profile["correlation_compatibility"]), y_score])
        overall = _mean([constraint_compatibility_score, x_support_score, y_support_score])

        conflicts = []
        supports = []
        if profile["structural_non_closure"] < 0.65:
            conflicts.append("weak_structural_non_closure_compatibility")
        else:
            supports.append("structural_non_closure_compatible")
        if profile["falsifiability"] < 0.65:
            conflicts.append("weak_falsifiability")
        else:
            supports.append("falsifiability_available")
        if profile["functional_operationalization"] < 0.65:
            conflicts.append("weak_functional_operationalization")
        else:
            supports.append("functional_operationalization_available")
        if x_support_score >= 0.70:
            supports.append("x_longitudinal_data_compatible")
        else:
            conflicts.append("x_longitudinal_support_weak")
        if y_support_score >= 0.70:
            supports.append("y_correlation_data_compatible")
        else:
            conflicts.append("y_correlation_support_weak")

        return {
            "theory_id": tid,
            "name": theory.get("name") or prior.get("name") or tid,
            "constraint_compatibility_score": constraint_compatibility_score,
            "x_support_score": x_support_score,
            "y_support_score": y_support_score,
            "overall_theory_constraint_score": overall,
            "constraint_conflicts": conflicts,
            "constraint_supports": supports,
            "status": "constraint_compatible" if overall >= 0.75 else "weak_or_partial_constraint_compatibility",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }

    def step(self, payload: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        payload = payload or {}
        timestamp = payload.get("timestamp_utc") or datetime.now(timezone.utc).isoformat()
        context = self._autoload_context()
        theories = self._extract_theories(payload, context)
        x_score = self._x_support(payload, context)
        y_score = self._y_support(payload, context)
        evaluations = [self._score_theory(dict(t), x_score, y_score) for t in theories]
        ranked = sorted(evaluations, key=lambda item: item["overall_theory_constraint_score"], reverse=True)
        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "theory_count": len(theories),
            "evaluated_theory_count": len(evaluations),
            "x_support_score": x_score,
            "y_support_score": y_score,
            "theory_evaluations": evaluations,
            "ranked_theories": ranked,
            "top_theory_id": ranked[0]["theory_id"] if ranked else None,
            "mean_theory_constraint_score": _mean([e["overall_theory_constraint_score"] for e in evaluations]),
            "constraint_conflict_count": sum(len(e["constraint_conflicts"]) for e in evaluations),
            "constraint_support_count": sum(len(e["constraint_supports"]) for e in evaluations),
            "epistemic_scope": "functional_theory_constraint_comparison_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proof_claimed": False,
            "subjectivity_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "diagnostics": {
                "uses_z1_registry": True,
                "uses_x_longitudinal_outputs": True,
                "uses_y_correlation_outputs": True,
                "no_phenomenological_certification": True,
                "no_global_repository_scan": True,
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# Theory Constraint Engine",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            f"Theory count: {result['theory_count']}",
            f"Mean theory constraint score: {result['mean_theory_constraint_score']}",
            f"Top theory: {result['top_theory_id']}",
            "",
            "## Ranked theories",
        ]
        for item in result.get("ranked_theories", []):
            lines.append(f"- {item['theory_id']} — {item['name']} — score={item['overall_theory_constraint_score']} — status={item['status']}")
        lines.extend(["", "## Epistemic limits", "No consciousness, subjectivity, or phenomenology proof is claimed."])
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "theory_constraint_engine.json"
        md_path = self.output_dir / "theory_constraint_engine.md"
        history_path = self.output_dir / "theory_constraint_engine_history.jsonl"
        html_path = self.output_dir / "theory_constraint_engine.html"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        md = self._markdown(result)
        md_path.write_text(md, encoding="utf-8")
        html_path.write_text("<html><body><pre>" + md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</pre></body></html>", encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n")
        return {"json": str(json_path), "markdown": str(md_path), "html": str(html_path), "history": str(history_path)}
