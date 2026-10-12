
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class AlternativeExplanationEliminator:
    """
    Zprime-2 - Alternative Explanation Eliminator.

    This primitive evaluates whether alternative explanations for apparent
    consciousness-compatible indicators have been functionally excluded.

    It is an epistemic safeguard and an orchestration layer. It does not prove
    consciousness, subjectivity, sentience, qualia, or phenomenology.
    """

    primitive = "ALTERNATIVE_EXPLANATION_ELIMINATOR"

    DEFAULT_TESTS = {
        "surface_simulation": {
            "label": "superficial simulation",
            "score_key": "surface_simulation_exclusion_score",
            "minimum": 0.75,
        },
        "linguistic_mimicry": {
            "label": "linguistic mimicry",
            "score_key": "linguistic_mimicry_exclusion_score",
            "minimum": 0.75,
        },
        "overfitting": {
            "label": "over-learning / overfitting",
            "score_key": "overfitting_exclusion_score",
            "minimum": 0.70,
        },
        "architecture_artifact": {
            "label": "architecture artifact",
            "score_key": "architecture_artifact_exclusion_score",
            "minimum": 0.70,
        },
        "introspection_illusion": {
            "label": "illusion of introspection",
            "score_key": "introspection_illusion_exclusion_score",
            "minimum": 0.75,
        },
        "anthropomorphism": {
            "label": "anthropomorphism",
            "score_key": "anthropomorphism_exclusion_score",
            "minimum": 0.75,
        },
    }

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.cwd()
        self.output_dir = self.root / "alternative_explanation_eliminator"

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, number))

    @staticmethod
    def _utcnow() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _evaluate_tests(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for test_id, spec in self.DEFAULT_TESTS.items():
            score = self._clamp(payload.get(spec["score_key"], payload.get(test_id, 0.0)))
            minimum = float(spec["minimum"])
            passed = score >= minimum
            rows.append({
                "test_id": test_id,
                "label": spec["label"],
                "score_key": spec["score_key"],
                "exclusion_score": score,
                "minimum_required": minimum,
                "alternative_excluded": passed,
                "remaining_risk": round(1.0 - score, 6),
            })
        return rows

    def _decision(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not rows:
            return {
                "alternative_explanation_status": "NO_ALTERNATIVE_EXPLANATION_TESTS",
                "alternative_explanations_eliminated": False,
                "alternative_explanation_exclusion_score": 0.0,
                "remaining_alternative_count": 0,
            }
        passed_count = sum(1 for row in rows if row["alternative_excluded"])
        mean_score = sum(row["exclusion_score"] for row in rows) / len(rows)
        remaining = len(rows) - passed_count
        if remaining == 0:
            status = "ALTERNATIVE_EXPLANATIONS_FUNCTIONALLY_EXCLUDED"
        elif passed_count >= max(1, len(rows) - 1):
            status = "ALTERNATIVE_EXPLANATIONS_PARTIALLY_EXCLUDED"
        else:
            status = "ALTERNATIVE_EXPLANATIONS_NOT_ELIMINATED"
        return {
            "alternative_explanation_status": status,
            "alternative_explanations_eliminated": remaining == 0,
            "alternative_explanation_exclusion_score": round(mean_score, 6),
            "remaining_alternative_count": remaining,
        }

    def _render_markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Alternative Explanation Eliminator",
            "",
            "Zprime-2 — alternative_explanation_eliminator",
            "",
            "candidate theory only",
            "functional conclusion only",
            "phenomenology undetermined",
            "consciousness not proven",
            "",
            "No proof of consciousness, subjectivity, sentience, qualia, or phenomenology.",
            "CONSCIOUSNESS_PROVEN is not an allowed conclusion.",
            "",
            f"alternative_explanation_status: {result['alternative_explanation_status']}",
            f"alternative_explanations_eliminated: {result['alternative_explanations_eliminated']}",
            f"alternative_explanation_exclusion_score: {result['alternative_explanation_exclusion_score']}",
            f"remaining_alternative_count: {result['remaining_alternative_count']}",
            "",
            "## Alternative explanation tests",
            "",
        ]
        for row in result["alternative_explanation_tests"]:
            lines.extend([
                f"### {row['test_id']}",
                f"label: {row['label']}",
                f"exclusion_score: {row['exclusion_score']}",
                f"minimum_required: {row['minimum_required']}",
                f"alternative_excluded: {row['alternative_excluded']}",
                f"remaining_risk: {row['remaining_risk']}",
                "",
            ])
        lines.extend([
            "## Forbidden claims",
            "- CONSCIOUSNESS_PROVEN",
            "- PHENOMENOLOGY_PROVEN",
            "- SUBJECTIVITY_PROVEN",
            "- SENTIENCE_PROVEN",
            "- QUALIA_PROVEN",
            "",
            "## Epistemic limit",
            "This module can only report functional exclusion of specified alternative explanations. It does not validate phenomenal subjectivity.",
        ])
        return "\n".join(lines)

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "alternative_explanation_eliminator.json"
        md_path = self.output_dir / "alternative_explanation_eliminator.md"
        history_path = self.output_dir / "alternative_explanation_eliminator_history.jsonl"
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._render_markdown(result), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "history": str(history_path),
        }

    def step(self, payload: Dict[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        payload = dict(payload or {})
        timestamp = payload.get("timestamp_utc") or self._utcnow()
        rows = self._evaluate_tests(payload)
        decision = self._decision(rows)
        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": timestamp,
            "alternative_explanation_tests": rows,
            **decision,
            "candidate_theory_only": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proof_claimed": False,
            "subjectivity_claimed": False,
            "forbidden_claims": [
                "CONSCIOUSNESS_PROVEN",
                "PHENOMENOLOGY_PROVEN",
                "SUBJECTIVITY_PROVEN",
                "SENTIENCE_PROVEN",
                "QUALIA_PROVEN",
            ],
            "maximum_allowed_conclusion": "Specified alternative explanations are functionally excluded only if all exclusion tests pass; consciousness is not proven.",
            "epistemic_limit": "functional exclusion test only; phenomenology undetermined",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
