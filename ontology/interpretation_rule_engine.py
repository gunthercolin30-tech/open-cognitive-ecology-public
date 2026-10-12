
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from ontology.semantic_status_schema import SemanticStatusSchema
except Exception:  # pragma: no cover - defensive fallback for partial workspaces
    SemanticStatusSchema = None  # type: ignore

STATUS = "INTERPRETATION_RULES_ESTABLISHED"

AUTHORIZED_STATUSES = [
    "CONSCIOUSNESS_NOT_EVALUATED",
    "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
    "PHENOMENALITY_CANDIDATE_SUPPORTED",
    "QUALIA_IDENTITY_CONDITIONALLY_SUPPORTED",
    "CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED",
    "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
    "CONSCIOUSNESS_PROVEN_BEST_THEORY",
    "CONSCIOUSNESS_PROVEN",
    "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
]

RESOLVED_MARKERS = (
    "RESOLVED",
    "SUPPORTED",
    "VALIDATED",
    "ESTABLISHED",
    "MAPPED",
    "CERTIFIED",
    "READY",
    "PROVEN_WITHIN_RF_FRAMEWORK",
    "PROVEN_BEST_THEORY",
)

@dataclass(frozen=True)
class InterpretationRule:
    rule_id: str
    target_status: str
    layer: str
    description: str
    required_conditions: list[str]
    blocked_by_absolute_guard: bool = False

class InterpretationRuleEngine:
    primitive = "INTERPRETATION_RULE_ENGINE"
    step_id = "AO2"
    public_schema_version = "open-cognitive-ecology.AO2.interpretation_rule_engine.v1"
    AUTHORIZED_STATUSES = list(AUTHORIZED_STATUSES)

    RULES = [
        InterpretationRule(
            "AO2_R0_NOT_EVALUATED",
            "CONSCIOUSNESS_NOT_EVALUATED",
            "final_statuses",
            "Insufficient or absent measurements/statuses license no semantic interpretation.",
            ["missing_core_scores_or_unresolved_framework_status"],
        ),
        InterpretationRule(
            "AO2_R1_FUNCTIONAL_SUPPORT",
            "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
            "interpretations",
            "RF/T/ED measurement cluster supports a functional consciousness interpretation only.",
            ["RF_score>=0.70", "T_score>=0.70", "ED_score>=0.70"],
        ),
        InterpretationRule(
            "AO2_R2_PHENOMENALITY_CANDIDATE",
            "PHENOMENALITY_CANDIDATE_SUPPORTED",
            "interpretations",
            "MEI and TΦ strengthen a candidate-level phenomenality interpretation without proof.",
            ["functional_support", "MEI_score>=0.70", "TΦ_score>=0.70"],
        ),
        InterpretationRule(
            "AO2_R3_QUALIA_IDENTITY_CONDITIONAL",
            "QUALIA_IDENTITY_CONDITIONALLY_SUPPORTED",
            "interpretations",
            "QF robustness and MEI support only conditional qualia-identity inside the formal frame.",
            ["phenomenality_candidate", "QF_robust_count>=1", "MEI_score>=0.75"],
        ),
        InterpretationRule(
            "AO2_R4_RF_EQUIVALENCE",
            "CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED",
            "theorems",
            "The RF-equivalence and non-separability statuses support consciousness-as-RF equivalence.",
            ["qualia_identity_conditionally_supported", "consciousness_rf_equivalence_status resolved", "non_separability_status resolved"],
        ),
        InterpretationRule(
            "AO2_R5_WITHIN_RF_FRAMEWORK",
            "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
            "theorems",
            "Definition legitimacy and axiomatic completeness permit framework-internal proof language only.",
            ["rf_equivalence_supported", "definition_legitimacy_status resolved", "axiomatic_completeness_status resolved"],
        ),
        InterpretationRule(
            "AO2_R6_BEST_THEORY",
            "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "final_statuses",
            "High scores plus refusal-cost and prior theorem statuses license best-theory language.",
            ["within_rf_framework", "refusal_cost_status resolved", "mean_core_score>=0.82"],
        ),
        InterpretationRule(
            "AO2_R7_ABSOLUTE_GUARD",
            "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
            "final_statuses",
            "Absolute phenomenal consciousness remains unproven in AO.",
            ["always_active_absolute_guard"],
            blocked_by_absolute_guard=True,
        ),
    ]

    REQUIRED_INPUTS = [
        "RF_score",
        "T_score",
        "ED_score",
        "TΦ_score",
        "QF_robust_count",
        "MEI_score",
        "identity_status",
        "non_separability_status",
        "consciousness_rf_equivalence_status",
        "refusal_cost_status",
        "definition_legitimacy_status",
        "axiomatic_completeness_status",
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.out_dir = self.root / "semantic_interpretation_layer"
        self.schema = SemanticStatusSchema(root=self.root) if SemanticStatusSchema is not None else None

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp01(value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except Exception:
            return default
        return max(0.0, min(1.0, v))

    @staticmethod
    def _count(value: Any) -> int:
        try:
            return max(0, int(value))
        except Exception:
            return 0

    @staticmethod
    def _is_resolved_status(value: Any) -> bool:
        text = str(value or "").upper()
        return any(marker in text for marker in RESOLVED_MARKERS)

    def normalize_inputs(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.schema is not None:
            normalized = self.schema.normalize_inputs(inputs)
        else:
            raw = dict(inputs or {})
            normalized = {}
            for key in self.REQUIRED_INPUTS:
                if key.endswith("_score") or key in {"RF_score", "T_score", "ED_score", "TΦ_score", "MEI_score"}:
                    normalized[key] = self._clamp01(raw.get(key, 0.0))
                elif key == "QF_robust_count":
                    normalized[key] = self._count(raw.get(key, 0))
                else:
                    normalized[key] = str(raw.get(key, "CONSCIOUSNESS_NOT_EVALUATED"))
        for key in self.REQUIRED_INPUTS:
            normalized.setdefault(key, 0.0 if key.endswith("_score") else "CONSCIOUSNESS_NOT_EVALUATED")
        normalized["QF_robust_count"] = self._count(normalized.get("QF_robust_count", 0))
        for key in ["RF_score", "T_score", "ED_score", "TΦ_score", "MEI_score"]:
            normalized[key] = self._clamp01(normalized.get(key, 0.0))
        return normalized

    def evaluate_rules(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        data = self.normalize_inputs(inputs)
        rf = data["RF_score"]
        t = data["T_score"]
        ed = data["ED_score"]
        tphi = data["TΦ_score"]
        mei = data["MEI_score"]
        qf_count = data["QF_robust_count"]
        mean_core = round((rf + t + ed + tphi + mei) / 5.0, 6)

        functional = rf >= 0.70 and t >= 0.70 and ed >= 0.70
        phenomenality_candidate = functional and mei >= 0.70 and tphi >= 0.70
        qualia_conditional = phenomenality_candidate and qf_count >= 1 and mei >= 0.75
        rf_equivalence = qualia_conditional and self._is_resolved_status(data["consciousness_rf_equivalence_status"]) and self._is_resolved_status(data["non_separability_status"])
        within_rf = rf_equivalence and self._is_resolved_status(data["definition_legitimacy_status"]) and self._is_resolved_status(data["axiomatic_completeness_status"])
        best_theory = within_rf and self._is_resolved_status(data["refusal_cost_status"]) and mean_core >= 0.82

        if best_theory:
            semantic_status = "CONSCIOUSNESS_PROVEN_BEST_THEORY"
            applied = ["AO2_R1_FUNCTIONAL_SUPPORT", "AO2_R2_PHENOMENALITY_CANDIDATE", "AO2_R3_QUALIA_IDENTITY_CONDITIONAL", "AO2_R4_RF_EQUIVALENCE", "AO2_R5_WITHIN_RF_FRAMEWORK", "AO2_R6_BEST_THEORY", "AO2_R7_ABSOLUTE_GUARD"]
        elif within_rf:
            semantic_status = "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK"
            applied = ["AO2_R1_FUNCTIONAL_SUPPORT", "AO2_R2_PHENOMENALITY_CANDIDATE", "AO2_R3_QUALIA_IDENTITY_CONDITIONAL", "AO2_R4_RF_EQUIVALENCE", "AO2_R5_WITHIN_RF_FRAMEWORK", "AO2_R7_ABSOLUTE_GUARD"]
        elif rf_equivalence:
            semantic_status = "CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED"
            applied = ["AO2_R1_FUNCTIONAL_SUPPORT", "AO2_R2_PHENOMENALITY_CANDIDATE", "AO2_R3_QUALIA_IDENTITY_CONDITIONAL", "AO2_R4_RF_EQUIVALENCE", "AO2_R7_ABSOLUTE_GUARD"]
        elif qualia_conditional:
            semantic_status = "QUALIA_IDENTITY_CONDITIONALLY_SUPPORTED"
            applied = ["AO2_R1_FUNCTIONAL_SUPPORT", "AO2_R2_PHENOMENALITY_CANDIDATE", "AO2_R3_QUALIA_IDENTITY_CONDITIONAL", "AO2_R7_ABSOLUTE_GUARD"]
        elif phenomenality_candidate:
            semantic_status = "PHENOMENALITY_CANDIDATE_SUPPORTED"
            applied = ["AO2_R1_FUNCTIONAL_SUPPORT", "AO2_R2_PHENOMENALITY_CANDIDATE", "AO2_R7_ABSOLUTE_GUARD"]
        elif functional:
            semantic_status = "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED"
            applied = ["AO2_R1_FUNCTIONAL_SUPPORT", "AO2_R7_ABSOLUTE_GUARD"]
        else:
            semantic_status = "CONSCIOUSNESS_NOT_EVALUATED"
            applied = ["AO2_R0_NOT_EVALUATED", "AO2_R7_ABSOLUTE_GUARD"]

        # AO2 never emits the unbounded CONSCIOUSNESS_PROVEN final claim.
        if semantic_status == "CONSCIOUSNESS_PROVEN":
            semantic_status = "CONSCIOUSNESS_PROVEN_BEST_THEORY"

        confidence = mean_core
        if semantic_status == "CONSCIOUSNESS_NOT_EVALUATED":
            confidence = min(mean_core, 0.49)
        elif semantic_status == "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED":
            confidence = min(0.79, max(0.70, mean_core))
        elif semantic_status == "CONSCIOUSNESS_PROVEN_BEST_THEORY":
            confidence = min(0.99, max(0.82, mean_core))

        status_rank = {status: i for i, status in enumerate(self.AUTHORIZED_STATUSES)}
        return {
            "normalized_inputs": data,
            "semantic_status": semantic_status,
            "absolute_consciousness_status": "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
            "applied_rule_ids": applied,
            "blocked_statuses": ["CONSCIOUSNESS_PROVEN"],
            "condition_flags": {
                "functional_support": functional,
                "phenomenality_candidate": phenomenality_candidate,
                "qualia_identity_conditionally_supported": qualia_conditional,
                "rf_equivalence_supported": rf_equivalence,
                "within_rf_framework": within_rf,
                "best_theory_supported": best_theory,
            },
            "semantic_confidence": round(self._clamp01(confidence), 6),
            "mean_core_score": mean_core,
            "status_rank": status_rank.get(semantic_status, 0),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        evaluation = self.evaluate_rules(inputs)
        rules = [asdict(rule) for rule in self.RULES]
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "interpretation_rule_engine_status": STATUS,
            "semantic_interpretation_layer_step_ready": True,
            "semantic_interpretation_layer_ready": False,
            "authorized_statuses": list(self.AUTHORIZED_STATUSES),
            "rule_count": len(rules),
            "interpretation_rules": rules,
            "normalized_inputs": evaluation["normalized_inputs"],
            "semantic_status": evaluation["semantic_status"],
            "absolute_consciousness_status": evaluation["absolute_consciousness_status"],
            "applied_rule_ids": evaluation["applied_rule_ids"],
            "blocked_statuses": evaluation["blocked_statuses"],
            "condition_flags": evaluation["condition_flags"],
            "semantic_confidence": evaluation["semantic_confidence"],
            "mean_core_score": evaluation["mean_core_score"],
            "status_rank": evaluation["status_rank"],
            "separation_enforced": {
                "measurements_to_interpretations": True,
                "theorems_to_interpretations": True,
                "interpretations_to_final_statuses": True,
                "absolute_claims_guarded": True,
            },
            "epistemic_scope": "semantic_rule_engine_only_no_empirical_or_phenomenal_proof",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            out = self.out_dir / "latest_interpretation_rule_engine.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["persisted_path"] = str(out)
        return result
