from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "phenomenology_model_selection"


@dataclass(frozen=True)
class ModelScores:
    model_id: str
    name: str
    explanatory_power: float
    robustness: float
    parsimony: float
    replication_support: float
    constraint_compatibility: float
    falsification_resistance: float
    model_selection_score: float
    model_selection_status: str


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        x = default
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PhenomenologyModelSelection:
    """Z4 — Select candidate phenomenology models using functional evidence only."""

    primitive = "PHENOMENOLOGY_MODEL_SELECTION"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.out_dir = self.root / "phenomenology_model_selection"

    def _default_models(self) -> List[Dict[str, Any]]:
        # Candidate models are theory entries only. Scores are functional proxies.
        return [
            {"model_id": "RPT", "name": "Recurrent Processing Theory", "parsimony": 0.86},
            {"model_id": "PP", "name": "Predictive Processing / Active Inference", "parsimony": 0.78},
            {"model_id": "GNW", "name": "Global Neuronal Workspace / Global Workspace Theory", "parsimony": 0.72},
            {"model_id": "HOT", "name": "Higher-Order Thought / Higher-Order Representation", "parsimony": 0.74},
            {"model_id": "IIT", "name": "Integrated Information Theory", "parsimony": 0.58},
            {"model_id": "CBP", "name": "Constraint-Based Phenomenology Candidate", "parsimony": 0.82},
        ]

    def _load_json_if_exists(self, rel: str) -> Dict[str, Any]:
        path = self.root / rel
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _context(self) -> Dict[str, Any]:
        return {
            "constraint": self._load_json_if_exists("theory_constraint_engine/theory_constraint_engine.json"),
            "falsification": self._load_json_if_exists("theory_falsification_framework/theory_falsification_framework.json"),
            "correlation_report": self._load_json_if_exists("phenomenology_correlation_report/phenomenology_correlation_report.json"),
            "replication": self._load_json_if_exists("independent_correlation_replication/independent_correlation_replication.json"),
        }

    def _score_model(self, model: Dict[str, Any], payload: Dict[str, Any], context: Dict[str, Any]) -> ModelScores:
        model_id = str(model.get("model_id") or model.get("theory_id") or model.get("id") or "UNKNOWN").upper()
        name = str(model.get("name") or model_id)

        constraints = context.get("constraint") or {}
        falsification = context.get("falsification") or {}
        correlation_report = context.get("correlation_report") or {}
        replication = context.get("replication") or {}

        explicit_scores = payload.get("model_scores", {}) if isinstance(payload.get("model_scores"), dict) else {}
        model_explicit = explicit_scores.get(model_id, {}) if isinstance(explicit_scores.get(model_id, {}), dict) else {}

        ranked_theories = constraints.get("ranked_theories") or constraints.get("theory_scores") or []
        constraint_score = None
        if isinstance(ranked_theories, list):
            for item in ranked_theories:
                if not isinstance(item, dict):
                    continue
                tid = str(item.get("theory_id") or item.get("model_id") or "").upper()
                if tid == model_id:
                    constraint_score = item.get("overall_theory_constraint_score", item.get("score", item.get("model_selection_score")))
                    break

        falsification_tests = falsification.get("falsification_tests") or falsification.get("theory_falsification_tests") or []
        falsification_pressure = None
        if isinstance(falsification_tests, list):
            for item in falsification_tests:
                if not isinstance(item, dict):
                    continue
                tid = str(item.get("theory_id") or item.get("model_id") or "").upper()
                if tid == model_id:
                    falsification_pressure = item.get("falsification_pressure", item.get("pressure"))
                    break

        # Functional proxy values. These are not phenomenological proof criteria.
        y_score = _clamp(payload.get("y_support_score", correlation_report.get("report_readiness_score", 0.72)), 0.72)
        replication_support = _clamp(model_explicit.get("replication_support", payload.get("replication_support", replication.get("replication_confidence", 0.66))), 0.66)
        constraint_compatibility = _clamp(model_explicit.get("constraint_compatibility", constraint_score if constraint_score is not None else payload.get("constraint_compatibility", 0.70)), 0.70)
        falsification_pressure = _clamp(model_explicit.get("falsification_pressure", falsification_pressure if falsification_pressure is not None else payload.get("falsification_pressure", 0.30)), 0.30)
        falsification_resistance = _clamp(model_explicit.get("falsification_resistance", 1.0 - falsification_pressure), 0.70)
        parsimony = _clamp(model_explicit.get("parsimony", model.get("parsimony", payload.get("parsimony", 0.70))), 0.70)
        robustness = _clamp(model_explicit.get("robustness", payload.get("robustness", (constraint_compatibility + replication_support + falsification_resistance) / 3.0)), 0.70)
        explanatory_power = _clamp(model_explicit.get("explanatory_power", payload.get("explanatory_power", (y_score + constraint_compatibility) / 2.0)), 0.70)

        score = round((
            explanatory_power * 0.24
            + robustness * 0.20
            + parsimony * 0.14
            + replication_support * 0.16
            + constraint_compatibility * 0.16
            + falsification_resistance * 0.10
        ), 4)

        if score >= 0.80:
            status = "preferred_functional_model_candidate"
        elif score >= 0.68:
            status = "plausible_functional_model_candidate"
        elif score >= 0.50:
            status = "weak_functional_model_candidate"
        else:
            status = "not_supported_as_functional_model"

        return ModelScores(
            model_id=model_id,
            name=name,
            explanatory_power=round(explanatory_power, 4),
            robustness=round(robustness, 4),
            parsimony=round(parsimony, 4),
            replication_support=round(replication_support, 4),
            constraint_compatibility=round(constraint_compatibility, 4),
            falsification_resistance=round(falsification_resistance, 4),
            model_selection_score=score,
            model_selection_status=status,
        )

    def _as_dict(self, score: ModelScores) -> Dict[str, Any]:
        return {
            "model_id": score.model_id,
            "name": score.name,
            "explanatory_power": score.explanatory_power,
            "robustness": score.robustness,
            "parsimony": score.parsimony,
            "replication_support": score.replication_support,
            "constraint_compatibility": score.constraint_compatibility,
            "falsification_resistance": score.falsification_resistance,
            "model_selection_score": score.model_selection_score,
            "model_selection_status": score.model_selection_status,
        }

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Phenomenology Model Selection",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            f"Model count: {result['model_count']}",
            f"Selected model: {result.get('selected_model_id')}",
            f"Selection status: {result.get('model_selection_status')}",
            f"Mean model selection score: {result.get('mean_model_selection_score')}",
            "",
            "## Ranked models",
        ]
        for item in result.get("ranked_models", []):
            lines.append(
                f"- {item['model_id']} — {item['name']} — score={item['model_selection_score']} — "
                f"explanatory_power={item['explanatory_power']} — robustness={item['robustness']} — "
                f"parsimony={item['parsimony']} — status={item['model_selection_status']}"
            )
        lines.extend([
            "",
            "No consciousness, subjectivity, or phenomenology proof is claimed.",
        ])
        return "\n".join(lines) + "\n"

    def _html(self, result: Dict[str, Any]) -> str:
        rows = []
        for item in result.get("ranked_models", []):
            rows.append(
                "<tr>"
                f"<td>{item['model_id']}</td><td>{item['name']}</td>"
                f"<td>{item['model_selection_score']}</td><td>{item['explanatory_power']}</td>"
                f"<td>{item['robustness']}</td><td>{item['parsimony']}</td>"
                f"<td>{item['replication_support']}</td><td>{item['constraint_compatibility']}</td>"
                f"<td>{item['falsification_resistance']}</td><td>{item['model_selection_status']}</td>"
                "</tr>"
            )
        body = "".join(rows)
        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Phenomenology Model Selection</title>"
            "<style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}"
            "td,th{border:1px solid #ccc;padding:6px;}th{background:#eee;}</style></head><body>"
            "<h1>Phenomenology Model Selection</h1>"
            "<p><strong>functional conclusion only</strong></p>"
            "<p><strong>phenomenology undetermined</strong></p>"
            f"<p>Selected model: {result.get('selected_model_id')}</p>"
            f"<p>Model selection status: {result.get('model_selection_status')}</p>"
            "<table><tr><th>Model</th><th>Name</th><th>Score</th><th>Explanatory power</th>"
            "<th>Robustness</th><th>Parsimony</th><th>Replication support</th>"
            "<th>Constraint compatibility</th><th>Falsification resistance</th><th>Status</th></tr>"
            f"{body}</table>"
            "<p>No consciousness, subjectivity, or phenomenology proof is claimed.</p>"
            "</body></html>"
        )

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.out_dir / "phenomenology_model_selection.json"
        history_path = self.out_dir / "phenomenology_model_selection_history.jsonl"
        md_path = self.out_dir / "phenomenology_model_selection.md"
        html_path = self.out_dir / "phenomenology_model_selection.html"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, sort_keys=True) + "\n")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        html_path.write_text(self._html(result), encoding="utf-8")
        return {
            "json": str(json_path),
            "history": str(history_path),
            "markdown": str(md_path),
            "html": str(html_path),
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        payload = dict(inputs or {})
        timestamp = payload.get("timestamp_utc") or _now()
        models = payload.get("models")
        if models is None:
            models = payload.get("theories")
        if models is None:
            models = self._default_models()
        if not isinstance(models, list):
            models = []

        context = self._context()
        ranked = [self._as_dict(self._score_model(m, payload, context)) for m in models if isinstance(m, dict)]
        ranked.sort(key=lambda x: (-x["model_selection_score"], x["model_id"]))

        selected = ranked[0] if ranked else None
        mean_score = round(sum(x["model_selection_score"] for x in ranked) / len(ranked), 4) if ranked else 0.0
        preferred = sum(1 for x in ranked if x["model_selection_status"] == "preferred_functional_model_candidate")

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "model_count": len(ranked),
            "evaluated_model_count": len(ranked),
            "selected_model_id": selected["model_id"] if selected else None,
            "selected_model_name": selected["name"] if selected else None,
            "model_selection_status": selected["model_selection_status"] if selected else "no_model_available",
            "mean_model_selection_score": mean_score,
            "preferred_model_candidate_count": preferred,
            "ranked_models": ranked,
            "selection_criteria": [
                "explanatory_power",
                "robustness",
                "parsimony",
                "replication_support",
                "constraint_compatibility",
                "falsification_resistance",
            ],
            "epistemic_scope": "functional_model_selection_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proof_claimed": False,
            "subjectivity_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "diagnostics": {
                "uses_z1_theory_registry": True,
                "uses_z2_constraint_scores": True,
                "uses_z3_falsification_pressure": True,
                "uses_y_axis_outputs": True,
                "no_phenomenology_claim": True,
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
