from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "phenomenology_theory_synthesis"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        v = default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


class PhenomenologyTheorySynthesis:
    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.out_dir = self.root / "phenomenology_theory_synthesis"

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return {}

    def _autoload(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        candidates = {
            "registry": self.root / "phenomenology_theory_registry" / "phenomenology_theory_registry.json",
            "constraints": self.root / "theory_constraint_engine" / "theory_constraint_engine.json",
            "falsification": self.root / "theory_falsification_framework" / "theory_falsification_framework.json",
            "model_selection": self.root / "phenomenology_model_selection" / "phenomenology_model_selection.json",
            "correlation_report": self.root / "phenomenology_correlation_report" / "phenomenology_correlation_report.json",
        }
        for key, path in candidates.items():
            value = self._load_json(path)
            if value:
                data[key] = value
        return data

    def _models_from_inputs(self, payload: Dict[str, Any], loaded: Dict[str, Any]) -> List[Dict[str, Any]]:
        explicit = payload.get("models") or payload.get("theories")
        if isinstance(explicit, list):
            return [m for m in explicit if isinstance(m, dict)]

        ms = loaded.get("model_selection", {})
        ranked = ms.get("ranked_models") or ms.get("models") or []
        if isinstance(ranked, list) and ranked:
            return [m for m in ranked if isinstance(m, dict)]

        reg = loaded.get("registry", {})
        theories = reg.get("theories") or reg.get("registered_theories") or []
        if isinstance(theories, list) and theories:
            return [t for t in theories if isinstance(t, dict)]

        return [
            {"model_id": "IIT", "name": "Integrated Information Theory"},
            {"model_id": "GNW", "name": "Global Workspace Theory"},
            {"model_id": "HOT", "name": "Higher-Order Thought"},
            {"model_id": "PP", "name": "Predictive Processing / Active Inference"},
            {"model_id": "CBP", "name": "Constraint-Based Phenomenology Candidate"},
        ]

    def _score_model(self, model: Dict[str, Any], loaded: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        mid = str(model.get("model_id") or model.get("theory_id") or model.get("id") or "UNKNOWN")
        name = str(model.get("name") or mid)
        selection_score = _clamp(model.get("model_selection_score", model.get("score", payload.get("default_selection_score", 0.55))))
        explanatory_power = _clamp(model.get("explanatory_power", selection_score))
        robustness = _clamp(model.get("robustness", model.get("robustness_score", selection_score)))
        parsimony = _clamp(model.get("parsimony", model.get("parsimony_score", 0.70)))
        constraint_compatibility = _clamp(model.get("constraint_compatibility_score", model.get("constraint_score", selection_score)))
        falsification_resistance = _clamp(model.get("falsification_resistance", 1.0 - _clamp(model.get("falsification_pressure", 0.25))))
        replication_support = _clamp(model.get("replication_support", model.get("replication_score", selection_score)))
        candidate_score = round((
            explanatory_power * 0.24 +
            robustness * 0.18 +
            parsimony * 0.14 +
            constraint_compatibility * 0.18 +
            falsification_resistance * 0.14 +
            replication_support * 0.12
        ), 4)
        return {
            "model_id": mid,
            "name": name,
            "candidate_synthesis_score": candidate_score,
            "explanatory_power": round(explanatory_power, 4),
            "robustness": round(robustness, 4),
            "parsimony": round(parsimony, 4),
            "constraint_compatibility": round(constraint_compatibility, 4),
            "falsification_resistance": round(falsification_resistance, 4),
            "replication_support": round(replication_support, 4),
            "status": "candidate_component_only",
        }

    def _candidate_statement(self, top: Optional[Dict[str, Any]]) -> str:
        if not top:
            return "No candidate phenomenology theory model is available from current functional evidence."
        return (
            "Candidate model only: the currently highest-scoring synthesis is "
            f"{top['model_id']} ({top['name']}), based on functional explanatory, robustness, "
            "parsimony, constraint, falsification, and replication indicators. This is not a proof "
            "of consciousness, subjectivity, or phenomenology."
        )

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        payload = dict(inputs or {})
        loaded = self._autoload()
        models = self._models_from_inputs(payload, loaded)
        evaluated = [self._score_model(m, loaded, payload) for m in models]
        ranked = sorted(evaluated, key=lambda x: x["candidate_synthesis_score"], reverse=True)
        top = ranked[0] if ranked else None
        mean_score = round(sum(m["candidate_synthesis_score"] for m in ranked) / len(ranked), 4) if ranked else 0.0
        status = "no_candidate_model" if not top else (
            "candidate_model_available" if top["candidate_synthesis_score"] >= 0.65 else "weak_candidate_model"
        )

        result: Dict[str, Any] = {
            "primitive": "PHENOMENOLOGY_THEORY_SYNTHESIS",
            "success": True,
            "timestamp_utc": str(payload.get("timestamp_utc") or _utc_now()),
            "model_count": len(models),
            "evaluated_model_count": len(evaluated),
            "candidate_model_id": top["model_id"] if top else None,
            "candidate_model_name": top["name"] if top else None,
            "candidate_synthesis_score": top["candidate_synthesis_score"] if top else 0.0,
            "mean_candidate_synthesis_score": mean_score,
            "candidate_theory_status": status,
            "candidate_theory_only": True,
            "not_validated_phenomenology": True,
            "ranked_candidate_models": ranked,
            "candidate_statement": self._candidate_statement(top),
            "source_context_present": {k: bool(v) for k, v in loaded.items()},
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proof_claimed": False,
            "subjectivity_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "epistemic_scope": "candidate_theory_synthesis_from_functional_indicators_only",
            "diagnostics": {
                "uses_z1_z4": True,
                "uses_y8": True,
                "no_phenomenology_claim": True,
                "no_global_repository_scan": True,
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Phenomenology Theory Synthesis",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "candidate theory only",
            "not validated phenomenology",
            "",
            f"Candidate theory status: {result['candidate_theory_status']}",
            f"Candidate model: {result['candidate_model_id']} — {result['candidate_model_name']}",
            f"Candidate synthesis score: {result['candidate_synthesis_score']}",
            f"Mean candidate synthesis score: {result['mean_candidate_synthesis_score']}",
            "",
            "## Candidate statement",
            result["candidate_statement"],
            "",
            "## Ranked candidate models",
        ]
        for model in result["ranked_candidate_models"]:
            lines.append(f"- {model['model_id']} — {model['name']} — score={model['candidate_synthesis_score']} — status={model['status']}")
        lines.extend([
            "",
            "No consciousness, subjectivity, or phenomenology proof is claimed.",
        ])
        return "\n".join(lines) + "\n"

    def _html(self, result: Dict[str, Any]) -> str:
        rows = "".join(
            f"<tr><td>{m['model_id']}</td><td>{m['name']}</td><td>{m['candidate_synthesis_score']}</td><td>{m['status']}</td></tr>"
            for m in result["ranked_candidate_models"]
        )
        return (
            "<!doctype html><html><head><meta charset='utf-8'><title>Phenomenology Theory Synthesis</title></head>"
            "<body><h1>Phenomenology Theory Synthesis</h1>"
            "<p>functional conclusion only</p><p>phenomenology undetermined</p>"
            "<p>candidate theory only</p><p>not validated phenomenology</p>"
            f"<p>Candidate: {result['candidate_model_id']} — {result['candidate_model_name']}</p>"
            f"<p>Score: {result['candidate_synthesis_score']}</p>"
            f"<p>{result['candidate_statement']}</p>"
            "<table><tr><th>Model</th><th>Name</th><th>Score</th><th>Status</th></tr>"
            f"{rows}</table><p>No consciousness, subjectivity, or phenomenology proof is claimed.</p></body></html>"
        )

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.out_dir / "phenomenology_theory_synthesis.json"
        history_path = self.out_dir / "phenomenology_theory_synthesis_history.jsonl"
        md_path = self.out_dir / "phenomenology_theory_synthesis.md"
        html_path = self.out_dir / "phenomenology_theory_synthesis.html"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, sort_keys=True) + "\n")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        html_path.write_text(self._html(result), encoding="utf-8")
        return {"json": str(json_path), "history": str(history_path), "markdown": str(md_path), "html": str(html_path)}
