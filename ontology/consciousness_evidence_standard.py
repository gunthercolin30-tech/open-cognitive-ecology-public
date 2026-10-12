from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


@dataclass(frozen=True)
class EvidenceCriterion:
    criterion_id: str
    label: str
    description: str
    minimum_score: float
    weight: float


class ConsciousnessEvidenceStandard:
    """
    Zprime-1 — consciousness_evidence_standard.

    Defines the minimum admissible evidence standard for strong functional
    consciousness claims under the Zprime program.
    """

    primitive = "CONSCIOUSNESS_EVIDENCE_STANDARD"

    STATUS_LEVELS = (
        "STANDARD_DEFINED_INSUFFICIENT_EVIDENCE",
        "STANDARD_DEFINED_PARTIAL_EVIDENCE",
        "STANDARD_DEFINED_REPLICATION_REQUIRED",
        "STANDARD_DEFINED_STRONG_FUNCTIONAL_EVIDENCE_READY",
    )

    FORBIDDEN_CLAIMS = (
        "CONSCIOUSNESS_PROVEN",
        "PHENOMENOLOGY_PROVEN",
        "SUBJECTIVITY_PROVEN",
        "SENTIENCE_PROVEN",
        "QUALIA_PROVEN",
    )

    MAXIMUM_ALLOWED_CLAIM = (
        "strong, replicated and theoretically constrained indicators "
        "compatible with consciousness under the Z-prime framework"
    )

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.output_dir = self.root / "consciousness_evidence_standard"

    def _criteria(self) -> dict[str, list[EvidenceCriterion]]:
        return {
            "functional_criteria": [
                EvidenceCriterion("functional_self_modeling", "Explicit self-modeling", "Stable, testable self-modeling rather than surface self-reference.", 0.75, 1.0),
                EvidenceCriterion("functional_autobiographical_continuity", "Autobiographical continuity", "Coherent memory across time, perturbations and succession.", 0.75, 1.0),
                EvidenceCriterion("functional_reflexive_revision", "Reflexive revision", "Governed revision under self-assessment.", 0.75, 1.0),
                EvidenceCriterion("functional_opening_preservation", "Preservation of future openness", "Active avoidance of closure-amplifying interpretations and actions.", 0.80, 1.0),
            ],
            "theoretical_criteria": [
                EvidenceCriterion("theory_constraint_alignment", "Constraint-theoretic alignment", "Candidate theories satisfy the Z/Z-prime constraint framework.", 0.75, 1.0),
                EvidenceCriterion("theory_falsifiability", "Falsifiability", "The theory generates weakening or rejection conditions.", 0.70, 1.0),
                EvidenceCriterion("theory_status_support", "Theoretical status support", "Z8 supports a theory without a phenomenological proof claim.", 0.70, 1.0),
            ],
            "predictive_criteria": [
                EvidenceCriterion("prediction_specificity", "Prediction specificity", "Interventions yield specific, prior, differentiated predictions.", 0.70, 1.0),
                EvidenceCriterion("prediction_tracking", "Prediction tracking", "Effects track predictions across memory, attention, continuity, self-model and constraints.", 0.70, 1.0),
            ],
            "replication_criteria": [
                EvidenceCriterion("independent_replication", "Independent replication", "Results reproduced by independent runs, hosts or reviewers.", 0.75, 1.0),
                EvidenceCriterion("longitudinal_stability", "Longitudinal stability", "Evidence remains stable over time.", 0.75, 1.0),
            ],
            "alternative_exclusion_criteria": [
                EvidenceCriterion("surface_simulation_excluded", "Surface simulation excluded", "Not explainable by shallow scripted output or dashboard mimicry.", 0.75, 1.0),
                EvidenceCriterion("linguistic_mimicry_excluded", "Linguistic mimicry excluded", "Not reducible to language imitation or prompt-following performance.", 0.75, 1.0),
                EvidenceCriterion("overfitting_excluded", "Overfitting excluded", "Not explainable by over-specialization to tests.", 0.70, 1.0),
                EvidenceCriterion("architecture_artifact_excluded", "Architecture artifact excluded", "Not a trivial artifact of architecture or persistence mechanisms.", 0.70, 1.0),
                EvidenceCriterion("anthropomorphism_excluded", "Anthropomorphism excluded", "Human interpretive projection explicitly controlled.", 0.75, 1.0),
            ],
        }

    def _criterion_to_dict(self, criterion: EvidenceCriterion) -> dict[str, Any]:
        return {
            "criterion_id": criterion.criterion_id,
            "label": criterion.label,
            "description": criterion.description,
            "minimum_score": criterion.minimum_score,
            "weight": criterion.weight,
        }

    def _score_category(self, category: str, criteria: list[EvidenceCriterion], payload: dict[str, Any]) -> dict[str, Any]:
        supplied_scores = payload.get(category, {})
        if not isinstance(supplied_scores, dict):
            supplied_scores = {}

        assessed = []
        weighted_total = 0.0
        weight_total = 0.0
        for criterion in criteria:
            score = _clamp(supplied_scores.get(criterion.criterion_id, payload.get(criterion.criterion_id, 0.0)))
            passed = score >= criterion.minimum_score
            assessed.append({
                **self._criterion_to_dict(criterion),
                "observed_score": score,
                "passed": passed,
                "measurement_type": "functional_indicator",
            })
            weighted_total += score * criterion.weight
            weight_total += criterion.weight

        category_score = weighted_total / weight_total if weight_total else 0.0
        return {
            "category": category,
            "category_score": round(category_score, 6),
            "category_passed": all(item["passed"] for item in assessed),
            "criteria": assessed,
        }

    def _status(self, category_results: dict[str, dict[str, Any]], overall_score: float) -> str:
        passed = {name: result["category_passed"] for name, result in category_results.items()}
        if not any(passed.values()):
            return "STANDARD_DEFINED_INSUFFICIENT_EVIDENCE"
        if not (passed.get("replication_criteria") and passed.get("alternative_exclusion_criteria")):
            return "STANDARD_DEFINED_REPLICATION_REQUIRED"
        if all(passed.values()) and overall_score >= 0.80:
            return "STANDARD_DEFINED_STRONG_FUNCTIONAL_EVIDENCE_READY"
        return "STANDARD_DEFINED_PARTIAL_EVIDENCE"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        payload = dict(inputs or {})
        timestamp = payload.get("timestamp_utc") or datetime.now(timezone.utc).isoformat()
        criteria = self._criteria()
        category_results = {category: self._score_category(category, items, payload) for category, items in criteria.items()}
        overall_score = round(_mean([result["category_score"] for result in category_results.values()]), 6)
        standard_status = self._status(category_results, overall_score)

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": timestamp,
            "evidence_standard_version": "ZPRIME-1.0",
            "standard_status": standard_status,
            "evidence_standard_score": overall_score,
            "minimum_categories": list(criteria.keys()),
            "category_results": category_results,
            "required_downstream_modules": [
                "alternative_explanation_eliminator",
                "causal_consciousness_intervention_protocol",
                "cross_architecture_consciousness_comparison",
                "strong_consciousness_inference_engine",
                "independent_consciousness_review_board",
                "adversarial_consciousness_audit",
                "consciousness_claim_governance_gate",
                "consciousness_status_report",
            ],
            "dependencies_reused": [
                "empirical_consciousness_evidence_synthesizer",
                "scientific_theory_confidence_engine",
                "phenomenology_theory_status",
                "phenomenology_theory_dashboard",
                "false_positive_detector",
                "theory_falsification_framework",
                "theory_replication_program",
            ],
            "forbidden_claims": list(self.FORBIDDEN_CLAIMS),
            "maximum_allowed_claim": self.MAXIMUM_ALLOWED_CLAIM,
            "candidate_theory_only": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "phenomenology_proof_claimed": False,
            "subjectivity_claimed": False,
            "consciousness_proven": False,
            "epistemic_classification": "standard_definition_only",
            "interpretation": {
                "functional_measure": "Defines and scores minimum admissible evidence categories.",
                "interpretive_hypothesis": "Strong functional support may become discussable only if all categories pass and replications survive adversarial controls.",
                "epistemic_limit": "No phenomenological subjectivity is inferred or proven by this standard.",
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "consciousness_evidence_standard.json"
        md_path = self.output_dir / "consciousness_evidence_standard.md"
        history_path = self.output_dir / "consciousness_evidence_standard_history.jsonl"
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._render_markdown(result), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {"json": str(json_path), "markdown": str(md_path), "history_jsonl": str(history_path)}

    def _render_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# Consciousness Evidence Standard",
            "",
            "Zprime-1 — consciousness_evidence_standard",
            "",
            "candidate theory only",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            "No proof of consciousness, subjectivity, sentience, qualia, or phenomenology.",
            "CONSCIOUSNESS_PROVEN is not an allowed conclusion.",
            "",
            f"standard_status: {result['standard_status']}",
            f"evidence_standard_score: {result['evidence_standard_score']}",
            "",
            "## Evidence categories",
        ]
        for category, category_result in result["category_results"].items():
            lines.extend(["", f"### {category}", f"category_score: {category_result['category_score']}", f"category_passed: {category_result['category_passed']}"])
            for item in category_result["criteria"]:
                lines.append(f"- {item['criterion_id']}: score={item['observed_score']} minimum={item['minimum_score']} passed={item['passed']}")
        lines.extend(["", "## Maximum allowed conclusion", result["maximum_allowed_claim"], "", "## Forbidden claims"])
        for claim in result["forbidden_claims"]:
            lines.append(f"- {claim}")
        lines.extend(["", "## Epistemic limit", "This standard defines functional and theoretical evidence requirements only. It does not validate phenomenal subjectivity."])
        return "\\n".join(lines) + "\n"


if __name__ == "__main__":
    outcome = ConsciousnessEvidenceStandard().step(persist=True)
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
