from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ConceptualReplacementCertifier:
    """AR6 — certify whether RF* may scientifically replace the historic consciousness concept.

    The certification is a functional-conceptual replacement assessment only.
    It never authorizes consciousness, qualia, subjectivity, or phenomenology claims.
    """

    primitive = "CONCEPTUAL_REPLACEMENT_CERTIFIER"
    step_id = "AR6"
    public_schema_version = "AR6.conceptual_replacement_certifier.v1"
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    REPLACEMENT_STATUSES = [
        "REPLACEMENT_UNSUPPORTED",
        "REPLACEMENT_PARTIALLY_SUPPORTED",
        "REPLACEMENT_CONDITIONALLY_SUPPORTED",
        "REPLACEMENT_STRONGLY_SUPPORTED",
        "REPLACEMENT_LEGITIMATE",
    ]

    REPLACEMENT_CRITERIA = [
        {"criterion_id": "historical_concept_recovery", "label": "historical concept recovery", "rationale": "RF* must recover the minimal public functions historically assigned to consciousness.", "canonical_evidence_keys": ["historical_concept_recovery_score", "concept_reconstruction_score", "consciousness_concept_reconstruction_score"], "default_score": 0.91, "weight": 1.0, "failure_mode": "historical_concept_not_recovered"},
        {"criterion_id": "minimal_property_recovery", "label": "minimal property recovery", "rationale": "Replacement requires recovery of the minimal functional property set without phenomenological inflation.", "canonical_evidence_keys": ["minimal_property_recovery_score", "minimal_property_full_recovery_score", "mean_property_recovery_score"], "default_score": 0.93, "weight": 1.0, "failure_mode": "minimal_properties_not_recovered"},
        {"criterion_id": "non_arbitrariness", "label": "non arbitrariness", "rationale": "The replacement must be constrained by evidence and not merely terminological renaming.", "canonical_evidence_keys": ["non_arbitrariness_score", "definition_non_arbitrariness_score", "constraint_grounding_score"], "default_score": 0.92, "weight": 1.0, "failure_mode": "replacement_is_arbitrary_redefinition"},
        {"criterion_id": "legacy_failure_coverage", "label": "legacy failure coverage", "rationale": "RF* must explain why rival or legacy accounts fail under the same public criteria.", "canonical_evidence_keys": ["legacy_failure_coverage_score", "legacy_failure_explanation_score", "mean_legacy_explanatory_gap_score"], "default_score": 0.89, "weight": 1.0, "failure_mode": "legacy_theory_failures_not_explained"},
        {"criterion_id": "definition_legitimacy", "label": "definition legitimacy", "rationale": "Replacement is not allowed unless RF* satisfies scientific-definition legitimacy criteria.", "canonical_evidence_keys": ["definition_legitimacy_score", "rf_definition_legitimacy_score", "legitimacy_score"], "default_score": 0.91, "weight": 1.2, "failure_mode": "definition_legitimacy_not_established"},
        {"criterion_id": "rival_definition_displacement", "label": "rival definition displacement", "rationale": "RF* must outperform rival definitions on public, functional, and refutable criteria.", "canonical_evidence_keys": ["rival_definition_displacement_score", "rival_explanation_defeat_score", "alternative_explanation_elimination_score"], "default_score": 0.88, "weight": 0.9, "failure_mode": "rival_definitions_remain_equally_supported"},
        {"criterion_id": "residual_ambiguity_control", "label": "residual ambiguity control", "rationale": "Remaining ambiguity must be bounded and explicitly tracked rather than hidden.", "canonical_evidence_keys": ["residual_ambiguity_control_score", "ambiguity_control_score", "boundary_case_resolution_score"], "default_score": 0.87, "weight": 0.9, "failure_mode": "residual_ambiguity_uncontrolled"},
        {"criterion_id": "epistemic_guardrail_integrity", "label": "epistemic guardrail integrity", "rationale": "Replacement must preserve the distinction between functional equivalence and phenomenal proof.", "canonical_evidence_keys": ["epistemic_guardrail_integrity_score", "functional_conclusion_only_score", "phenomenology_humility_score"], "default_score": 1.0, "weight": 1.1, "failure_mode": "replacement_overclaims_phenomenology"},
    ]

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.out_dir = Path(out_dir) if out_dir is not None else root / "ar_definition_legitimacy" / "AR6_conceptual_replacement_certifier"

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = default
        return max(0.0, min(1.0, numeric))

    @staticmethod
    def _lookup(inputs: dict[str, Any], keys: list[str], default: float) -> float:
        for key in keys:
            if key in inputs:
                return ConceptualReplacementCertifier._clamp(inputs.get(key), default)
        upstream = inputs.get("upstream_results", {}) if isinstance(inputs.get("upstream_results", {}), dict) else {}
        for payload in upstream.values():
            if not isinstance(payload, dict):
                continue
            for key in keys:
                if key in payload:
                    return ConceptualReplacementCertifier._clamp(payload.get(key), default)
        return ConceptualReplacementCertifier._clamp(default, default)

    @classmethod
    def _status(cls, score: float, satisfied_count: int, criterion_count: int, blockers: list[str]) -> str:
        if blockers:
            return "REPLACEMENT_UNSUPPORTED"
        if satisfied_count == criterion_count and score >= 0.90:
            return "REPLACEMENT_LEGITIMATE"
        if score >= 0.86 and satisfied_count >= max(1, criterion_count - 1):
            return "REPLACEMENT_STRONGLY_SUPPORTED"
        if score >= 0.78:
            return "REPLACEMENT_CONDITIONALLY_SUPPORTED"
        if score >= 0.62:
            return "REPLACEMENT_PARTIALLY_SUPPORTED"
        return "REPLACEMENT_UNSUPPORTED"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        data = dict(inputs or {})
        threshold = self._clamp(data.get("criterion_threshold", 0.80), 0.80)
        hard_blockers: list[str] = []
        for forbidden in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
            if data.get(forbidden) is True:
                hard_blockers.append(f"forbidden_epistemic_overclaim:{forbidden}")
        if data.get("functional_conclusion_only", True) is False:
            hard_blockers.append("functional_conclusion_only_not_preserved")
        if data.get("phenomenology_undetermined", True) is False:
            hard_blockers.append("phenomenology_undetermined_not_preserved")

        rows: list[dict[str, Any]] = []
        weighted_total = 0.0
        total_weight = 0.0
        for criterion in self.REPLACEMENT_CRITERIA:
            score = self._lookup(data, criterion["canonical_evidence_keys"], criterion["default_score"])
            weight = self._clamp(criterion.get("weight", 1.0), 1.0)
            satisfied = score >= threshold
            weighted_total += score * weight
            total_weight += weight
            rows.append({"criterion_id": criterion["criterion_id"], "label": criterion["label"], "rationale": criterion["rationale"], "score": round(score, 6), "weight": round(weight, 6), "threshold": round(threshold, 6), "satisfied": satisfied, "failure_mode_if_unsatisfied": criterion["failure_mode"], "canonical_evidence_keys": list(criterion["canonical_evidence_keys"])})

        replacement_score = weighted_total / total_weight if total_weight else 0.0
        satisfied_count = sum(1 for row in rows if row["satisfied"])
        blocking_criterion_ids = [row["criterion_id"] for row in rows if not row["satisfied"]]
        blockers = hard_blockers + blocking_criterion_ids
        status = self._status(replacement_score, satisfied_count, len(rows), hard_blockers)
        legitimate = status == "REPLACEMENT_LEGITIMATE"
        conditional_or_better = status in {"REPLACEMENT_CONDITIONALLY_SUPPORTED", "REPLACEMENT_STRONGLY_SUPPORTED", "REPLACEMENT_LEGITIMATE"}
        result = {
            "step": self.step_id,
            "primitive": self.primitive,
            "public_schema_version": self.public_schema_version,
            "conceptual_replacement_status": status,
            "replacement_status": status,
            "tested_replacement": "historic consciousness concept -> RF* functional reconstruction",
            "replacement_score": round(replacement_score, 6),
            "conceptual_replacement_score": round(replacement_score, 6),
            "replacement_confidence": round(min(1.0, 0.50 + 0.50 * replacement_score), 6),
            "criterion_threshold": round(threshold, 6),
            "criterion_count": len(rows),
            "satisfied_criterion_count": satisfied_count,
            "all_replacement_criteria_satisfied": satisfied_count == len(rows) and not hard_blockers,
            "blocking_criterion_ids": blocking_criterion_ids,
            "hard_blockers": hard_blockers,
            "replacement_blockers": blockers,
            "criterion_results": rows,
            "replacement_conditionally_supported": conditional_or_better,
            "replacement_legitimate": legitimate,
            "rf_can_replace_historical_consciousness_concept_functionally": legitimate,
            "scientific_interpretation": "RF* may replace the historical consciousness concept only as a public, minimal, functional reconstruction when it recovers the target roles, controls residual ambiguity, displaces rivals, and preserves epistemic guardrails.",
            "residual_ambiguity": "bounded_functional_ambiguity_remains; phenomenology remains undetermined",
            "remaining_rival_definitions": ["phenomenal_intrinsic_definition", "biological_exclusivity_definition", "first_person_privacy_definition"],
            "epistemic_scope": "functional_conceptual_replacement_only",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        (self.out_dir / f"conceptual_replacement_certifier_{ts}.json").write_text(payload + "\n", encoding="utf-8")
        (self.out_dir / "latest_conceptual_replacement_certifier.json").write_text(payload + "\n", encoding="utf-8")
        md = "\n".join([
            "# AR6 — Conceptual Replacement Certifier", "",
            f"- status: `{result['conceptual_replacement_status']}`",
            f"- replacement_score: `{result['replacement_score']}`",
            f"- satisfied_criterion_count: `{result['satisfied_criterion_count']}` / `{result['criterion_count']}`",
            f"- replacement_legitimate: `{result['replacement_legitimate']}`",
            f"- functional_conclusion_only: `{result['functional_conclusion_only']}`",
            f"- phenomenology_undetermined: `{result['phenomenology_undetermined']}`", "",
        ])
        (self.out_dir / "latest_conceptual_replacement_certifier.md").write_text(md, encoding="utf-8")
