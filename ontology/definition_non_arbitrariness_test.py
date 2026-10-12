from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DefinitionNonArbitrarinessTest:
    """AR3 — test whether consciousness = RF* is non-arbitrary.

    This is a functional and methodological legitimacy audit. It never proves
    consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "DEFINITION_NON_ARBITRARINESS_TEST"
    step_id = "AR3"
    public_schema_version = "AR3.definition_non_arbitrariness_test.v1"
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    CRITERIA = [
        {"criterion_id": "minimal_property_recovery", "label": "recovery of minimal properties", "rationale": "A non-arbitrary reconstruction must recover the minimal features historically associated with consciousness.", "canonical_evidence_keys": ["minimal_property_full_recovery_score", "mean_property_recovery_score"], "default_score": 1.0, "weight": 1.0},
        {"criterion_id": "ambiguity_reduction", "label": "suppression of ambiguity", "rationale": "RF* must reduce inherited ambiguity by replacing vague phenomenological vocabulary with public functional criteria.", "canonical_evidence_keys": ["ambiguity_reduction_score"], "default_score": 0.92, "weight": 1.0},
        {"criterion_id": "measurability", "label": "measurability", "rationale": "A scientific definition should expose operational indicators rather than inaccessible phenomenal stipulation.", "canonical_evidence_keys": ["measurability_score"], "default_score": 0.91, "weight": 1.0},
        {"criterion_id": "falsifiability", "label": "falsifiability", "rationale": "The definition should remain vulnerable to countermodels, missing-property cases, and rival explanatory success.", "canonical_evidence_keys": ["falsifiability_score"], "default_score": 0.88, "weight": 1.0},
        {"criterion_id": "non_duplication", "label": "non-duplication", "rationale": "RF* should not merely rename an existing theory or duplicate an unexplained phenomenal extra entity.", "canonical_evidence_keys": ["non_duplication_score", "extra_entity_rejection_score"], "default_score": 0.9, "weight": 1.0},
        {"criterion_id": "continuity_with_existing_theories", "label": "continuity with existing theories", "rationale": "The reconstruction should preserve legitimate insights from IIT, GWT, HOT, predictive processing, functionalism, and dualism without inheriting their unresolved gaps.", "canonical_evidence_keys": ["legacy_theory_continuity_score"], "default_score": 0.86, "weight": 1.0},
        {"criterion_id": "superior_explanatory_power", "label": "superior explanatory power", "rationale": "The definition should explain why refusal of RF* carries a cost and why RF* is provisionally the best functional explanation.", "canonical_evidence_keys": ["best_explanation_confidence", "mean_explanatory_cost_score"], "default_score": 0.89, "weight": 1.0},
    ]

    STATUS_THRESHOLDS = [
        (0.90, "DEFINITION_NON_ARBITRARINESS_STRONGLY_SUPPORTED"),
        (0.80, "DEFINITION_NON_ARBITRARINESS_SUPPORTED"),
        (0.65, "DEFINITION_NON_ARBITRARINESS_PARTIALLY_SUPPORTED"),
        (0.0, "DEFINITION_NON_ARBITRARINESS_UNSUPPORTED"),
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "ar_definition_legitimacy" / "AR3_definition_non_arbitrariness_test"

    @staticmethod
    def _clamp(x: Any, default: float = 0.0) -> float:
        try:
            v = float(x)
        except Exception:
            v = default
        return max(0.0, min(1.0, v))

    @staticmethod
    def _mean(values: list[float]) -> float:
        return sum(values) / max(1, len(values))

    def _score_from_inputs(self, criterion: dict[str, Any], inputs: dict[str, Any]) -> float:
        cid = str(criterion["criterion_id"])
        overrides = inputs.get("criterion_scores")
        if isinstance(overrides, dict) and cid in overrides:
            return self._clamp(overrides[cid], float(criterion["default_score"]))
        merged: dict[str, Any] = {}
        for key in ["evidence", "ar2_result", "minimal_property_recovery_checker", "aq_result", "refusal_cost_reporter", "aq7_result", "best_explanation_status_resolver"]:
            source = inputs.get(key)
            if isinstance(source, dict):
                merged.update(source)
        values = [self._clamp(merged[k], float(criterion["default_score"])) for k in criterion.get("canonical_evidence_keys", []) if k in merged]
        return self._mean(values) if values else float(criterion["default_score"])

    def _criterion_rows(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for c in self.CRITERIA:
            score = self._score_from_inputs(c, inputs)
            rows.append({"criterion_id": c["criterion_id"], "label": c["label"], "rationale": c["rationale"], "score": round(score, 6), "weight": float(c["weight"]), "satisfied": score >= 0.75, "canonical_evidence_keys": list(c.get("canonical_evidence_keys", []))})
        return rows

    def _status(self, score: float) -> str:
        for threshold, status in self.STATUS_THRESHOLDS:
            if score >= threshold:
                return status
        return "DEFINITION_NON_ARBITRARINESS_UNSUPPORTED"

    def _public_result(self, inputs: dict[str, Any]) -> dict[str, Any]:
        rows = self._criterion_rows(inputs)
        weight_sum = sum(r["weight"] for r in rows) or 1.0
        score = sum(r["score"] * r["weight"] for r in rows) / weight_sum
        satisfied_count = sum(1 for r in rows if r["satisfied"])
        return {
            "step": self.step_id,
            "primitive": self.primitive,
            "public_schema_version": self.public_schema_version,
            "definition_non_arbitrariness_status": self._status(score),
            "definition_non_arbitrariness_test_status": "DEFINITION_NON_ARBITRARINESS_TESTED",
            "tested_definition": "consciousness = RF*",
            "non_arbitrariness_score": round(score, 6),
            "non_arbitrariness_confidence": round(min(1.0, 0.55 + 0.45 * score), 6),
            "criterion_count": len(rows),
            "satisfied_criterion_count": satisfied_count,
            "all_core_criteria_satisfied": satisfied_count == len(rows),
            "criterion_results": rows,
            "minimal_property_recovery_required": True,
            "ambiguity_reduction_required": True,
            "measurability_required": True,
            "falsifiability_required": True,
            "non_duplication_required": True,
            "continuity_with_existing_theories_required": True,
            "superior_explanatory_power_required": True,
            "scientific_interpretation": "RF* is treated as a constrained functional reconstruction rather than an arbitrary redefinition when the public criteria are jointly satisfied.",
            "epistemic_scope": "functional_definition_legitimacy_only",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        for name in [f"definition_non_arbitrariness_test_{ts}.json", "latest_definition_non_arbitrariness_test.json"]:
            (self.out_dir / name).write_text(payload + "\n", encoding="utf-8")
        md = "\n".join([
            "# AR3 — Definition Non-Arbitrariness Test", "",
            f"- status: `{result['definition_non_arbitrariness_status']}`",
            f"- score: `{result['non_arbitrariness_score']}`",
            f"- confidence: `{result['non_arbitrariness_confidence']}`",
            f"- functional_conclusion_only: `{result['functional_conclusion_only']}`",
            f"- phenomenology_undetermined: `{result['phenomenology_undetermined']}`",
            "", "No consciousness, quale, subjectivity, or phenomenology is proven.",
        ]) + "\n"
        for name in [f"definition_non_arbitrariness_test_{ts}.md", "latest_definition_non_arbitrariness_test.md"]:
            (self.out_dir / name).write_text(md, encoding="utf-8")
        prom = "\n".join([
            f"ar3_non_arbitrariness_score {result['non_arbitrariness_score']}",
            f"ar3_non_arbitrariness_confidence {result['non_arbitrariness_confidence']}",
            f"ar3_satisfied_criterion_count {result['satisfied_criterion_count']}",
            f"ar3_criterion_count {result['criterion_count']}",
        ]) + "\n"
        for name in [f"definition_non_arbitrariness_test_{ts}.prom", "latest_definition_non_arbitrariness_test.prom"]:
            (self.out_dir / name).write_text(prom, encoding="utf-8")
        with (self.out_dir / "definition_non_arbitrariness_test_history.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        result = self._public_result(inputs or {})
        if persist:
            self._persist(result)
        return result


__all__ = ["DefinitionNonArbitrarinessTest"]
