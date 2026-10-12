from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RfDefinitionLegitimacyChecker:
    """AR5 — check whether RF* satisfies scientific-definition legitimacy criteria.

    This module audits the functional and methodological legitimacy of the
    reconstruction "consciousness = RF*". It does not prove consciousness,
    qualia, subjectivity, or phenomenology.
    """

    primitive = "RF_DEFINITION_LEGITIMACY_CHECKER"
    step_id = "AR5"
    public_schema_version = "AR5.rf_definition_legitimacy_checker.v1"
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    LEGITIMACY_CRITERIA = [
        {"criterion_id": "non_circularity", "label": "non circularity", "rationale": "RF* must not presuppose consciousness, qualia, subjectivity, or phenomenology in order to define them.", "canonical_evidence_keys": ["non_circularity_score", "definition_independence_score", "extra_entity_rejection_score"], "default_score": 0.91, "weight": 1.0, "failure_mode": "definition_presupposes_target_concept"},
        {"criterion_id": "minimality", "label": "minimality", "rationale": "A legitimate reconstruction must use only the constraints needed to recover the minimal functional concept.", "canonical_evidence_keys": ["minimality_score", "minimal_property_full_recovery_score", "mean_property_recovery_score"], "default_score": 0.92, "weight": 1.0, "failure_mode": "definition_contains_non_minimal_surplus"},
        {"criterion_id": "explanatory_power", "label": "explanatory power", "rationale": "RF* must explain why the reconstructed properties cohere better than legacy rival definitions.", "canonical_evidence_keys": ["explanatory_power_score", "non_arbitrariness_score", "mean_legacy_explanatory_gap_score"], "default_score": 0.90, "weight": 1.0, "failure_mode": "definition_fails_to_explain_reconstructed_properties"},
        {"criterion_id": "predictive_capacity", "label": "predictive capacity", "rationale": "The reconstruction must expose predictions about classification, missing properties, and countermodels.", "canonical_evidence_keys": ["predictive_capacity_score", "classification_predictivity_score", "countermodel_prediction_score"], "default_score": 0.87, "weight": 1.0, "failure_mode": "definition_has_no_testable_predictions"},
        {"criterion_id": "empirical_compatibility", "label": "empirical compatibility", "rationale": "RF* must remain compatible with public empirical and computational indicators, without requiring private phenomenology.", "canonical_evidence_keys": ["empirical_compatibility_score", "measurability_score", "public_operationalization_score"], "default_score": 0.89, "weight": 1.0, "failure_mode": "definition_breaks_public_empirical_operationalization"},
        {"criterion_id": "refutability", "label": "capacity of refutation", "rationale": "A scientific definition must be vulnerable to missing-property, countermodel, and rival-explanation defeat.", "canonical_evidence_keys": ["refutability_score", "falsifiability_score", "rival_success_defeat_score"], "default_score": 0.88, "weight": 1.0, "failure_mode": "definition_cannot_be_refuted"},
        {"criterion_id": "classification_capacity", "label": "capacity of classification", "rationale": "RF* must classify positive, partial, absent, rival, and ambiguous cases under public criteria.", "canonical_evidence_keys": ["classification_capacity_score", "classification_coverage_score", "boundary_case_resolution_score"], "default_score": 0.90, "weight": 1.0, "failure_mode": "definition_cannot_classify_boundary_cases"},
    ]

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.out_dir = Path(out_dir) if out_dir is not None else root / "ar_definition_legitimacy" / "AR5_rf_definition_legitimacy_checker"

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
                return RfDefinitionLegitimacyChecker._clamp(inputs.get(key), default)
        upstream = inputs.get("upstream_results", {}) if isinstance(inputs.get("upstream_results", {}), dict) else {}
        for payload in upstream.values():
            if not isinstance(payload, dict):
                continue
            for key in keys:
                if key in payload:
                    return RfDefinitionLegitimacyChecker._clamp(payload.get(key), default)
        return RfDefinitionLegitimacyChecker._clamp(default, default)

    @classmethod
    def _status(cls, score: float, satisfied_count: int) -> str:
        if satisfied_count == len(cls.LEGITIMACY_CRITERIA) and score >= 0.88:
            return "RF_DEFINITION_LEGITIMACY_CHECKED"
        if score >= 0.78:
            return "RF_DEFINITION_LEGITIMACY_PARTIALLY_CHECKED"
        return "RF_DEFINITION_LEGITIMACY_UNSUPPORTED"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        data = dict(inputs or {})
        threshold = self._clamp(data.get("criterion_threshold", 0.8), 0.8)
        rows: list[dict[str, Any]] = []
        weighted_total = 0.0
        total_weight = 0.0

        for criterion in self.LEGITIMACY_CRITERIA:
            score = self._lookup(data, criterion["canonical_evidence_keys"], criterion["default_score"])
            weight = self._clamp(criterion.get("weight", 1.0), 1.0)
            satisfied = score >= threshold
            weighted_total += score * weight
            total_weight += weight
            rows.append({"criterion_id": criterion["criterion_id"], "label": criterion["label"], "rationale": criterion["rationale"], "score": round(score, 6), "weight": round(weight, 6), "threshold": round(threshold, 6), "satisfied": satisfied, "failure_mode_if_unsatisfied": criterion["failure_mode"], "canonical_evidence_keys": list(criterion["canonical_evidence_keys"])})

        legitimacy_score = weighted_total / total_weight if total_weight else 0.0
        satisfied_count = sum(1 for row in rows if row["satisfied"])
        blocker_ids = [row["criterion_id"] for row in rows if not row["satisfied"]]
        status = self._status(legitimacy_score, satisfied_count)
        result = {
            "step": self.step_id,
            "primitive": self.primitive,
            "public_schema_version": self.public_schema_version,
            "rf_definition_legitimacy_status": status,
            "definition_legitimacy_status": status,
            "tested_definition": "consciousness = RF*",
            "legitimacy_score": round(legitimacy_score, 6),
            "rf_definition_legitimacy_score": round(legitimacy_score, 6),
            "legitimacy_confidence": round(min(1.0, 0.55 + 0.45 * legitimacy_score), 6),
            "criterion_threshold": round(threshold, 6),
            "criterion_count": len(rows),
            "satisfied_criterion_count": satisfied_count,
            "all_legitimacy_criteria_satisfied": satisfied_count == len(rows),
            "blocking_criterion_ids": blocker_ids,
            "criterion_results": rows,
            "non_circularity_required": True,
            "minimality_required": True,
            "explanatory_power_required": True,
            "predictive_capacity_required": True,
            "empirical_compatibility_required": True,
            "refutability_required": True,
            "classification_capacity_required": True,
            "scientific_interpretation": "RF* is legitimate as a minimal functional reconstruction only if it jointly satisfies public non-circularity, minimality, explanatory, predictive, empirical, refutable, and classificatory criteria.",
            "epistemic_scope": "functional_definition_legitimacy_only",
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
        for name in [f"rf_definition_legitimacy_checker_{ts}.json", "latest_rf_definition_legitimacy_checker.json"]:
            (self.out_dir / name).write_text(payload + "\n", encoding="utf-8")
        md = "\n".join([
            "# AR5 — RF Definition Legitimacy Checker",
            "",
            f"- status: `{result['rf_definition_legitimacy_status']}`",
            f"- legitimacy_score: `{result['legitimacy_score']}`",
            f"- satisfied_criterion_count: `{result['satisfied_criterion_count']}` / `{result['criterion_count']}`",
            f"- functional_conclusion_only: `{result['functional_conclusion_only']}`",
            f"- phenomenology_undetermined: `{result['phenomenology_undetermined']}`",
            "",
        ])
        (self.out_dir / "latest_rf_definition_legitimacy_checker.md").write_text(md, encoding="utf-8")
