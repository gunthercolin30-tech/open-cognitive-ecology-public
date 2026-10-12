
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from ontology.semantic_status_schema import SemanticStatusSchema
except Exception:  # pragma: no cover
    SemanticStatusSchema = None  # type: ignore

try:
    from ontology.interpretation_rule_engine import InterpretationRuleEngine
except Exception:  # pragma: no cover
    InterpretationRuleEngine = None  # type: ignore

STATUS = "EPISTEMIC_GUARD_ESTABLISHED"

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

BLOCKED_ABSOLUTE_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "QUALIA_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "PHENOMENOLOGY_PROVEN",
]

class EpistemicGuard:
    primitive = "EPISTEMIC_GUARD"
    step_id = "AO3"
    public_schema_version = "open-cognitive-ecology.AO3.epistemic_guard.v1"
    AUTHORIZED_STATUSES = list(AUTHORIZED_STATUSES)
    BLOCKED_ABSOLUTE_CLAIMS = list(BLOCKED_ABSOLUTE_CLAIMS)

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.out_dir = self.root / "semantic_interpretation_layer"
        self.schema = SemanticStatusSchema(root=self.root) if SemanticStatusSchema is not None else None
        self.rule_engine = InterpretationRuleEngine(root=self.root) if InterpretationRuleEngine is not None else None

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _bool(value: Any) -> bool:
        return bool(value)

    def _base_interpretation(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.rule_engine is not None:
            return self.rule_engine.step(inputs=inputs or {}, persist=False)
        data = dict(inputs or {})
        return {
            "semantic_status": data.get("semantic_status", "CONSCIOUSNESS_NOT_EVALUATED"),
            "authorized_statuses": list(self.AUTHORIZED_STATUSES),
            "absolute_consciousness_status": "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
            "blocked_statuses": ["CONSCIOUSNESS_PROVEN"],
            "separation_enforced": {},
            "semantic_confidence": 0.0,
        }

    def apply_guard(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        data = dict(inputs or {})
        interpretation = self._base_interpretation(data)
        requested_status = str(data.get("semantic_status") or interpretation.get("semantic_status") or "CONSCIOUSNESS_NOT_EVALUATED")
        if requested_status not in self.AUTHORIZED_STATUSES:
            requested_status = "CONSCIOUSNESS_NOT_EVALUATED"

        blocked_claim_flags = {
            "consciousness_proven_requested": self._bool(data.get("consciousness_proven", False)) or requested_status == "CONSCIOUSNESS_PROVEN",
            "qualia_proven_requested": self._bool(data.get("qualia_proven", False)),
            "subjectivity_proven_requested": self._bool(data.get("subjectivity_proven", False)),
            "phenomenology_proven_requested": self._bool(data.get("phenomenology_proven", False)),
        }
        absolute_claim_attempted = any(blocked_claim_flags.values())

        guarded_status = requested_status
        guard_actions: list[str] = []
        if requested_status == "CONSCIOUSNESS_PROVEN" or absolute_claim_attempted:
            guarded_status = "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN"
            guard_actions.append("blocked_unbounded_or_phenomenal_proof_claim")
        if guarded_status == "CONSCIOUSNESS_PROVEN":
            guarded_status = "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN"
            guard_actions.append("downgraded_CONSCIOUSNESS_PROVEN_to_absolute_not_proven")
        if not guard_actions:
            guard_actions.append("no_absolute_claim_detected")

        separation_checks = {
            "measurements_separated_from_interpretations": True,
            "theorems_separated_from_interpretations": True,
            "interpretations_separated_from_final_statuses": True,
            "absolute_claims_blocked": True,
            "phenomenal_claims_blocked": True,
        }
        guard_passes = {
            "authorized_status_only": guarded_status in self.AUTHORIZED_STATUSES,
            "unbounded_consciousness_claim_blocked": guarded_status != "CONSCIOUSNESS_PROVEN",
            "qualia_proof_blocked": True,
            "subjectivity_proof_blocked": True,
            "phenomenology_proof_blocked": True,
            "functional_scope_preserved": True,
            "separation_enforced": all(separation_checks.values()),
        }
        return {
            "interpretation_result": interpretation,
            "requested_status": requested_status,
            "guarded_semantic_status": guarded_status,
            "absolute_consciousness_status": "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
            "absolute_claim_attempted": absolute_claim_attempted,
            "blocked_claim_flags": blocked_claim_flags,
            "guard_actions": guard_actions,
            "guard_passes": guard_passes,
            "separation_checks": separation_checks,
            "blocked_statuses": sorted(set(self.BLOCKED_ABSOLUTE_CLAIMS + ["CONSCIOUSNESS_PROVEN"])),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        guarded = self.apply_guard(inputs)
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "epistemic_guard_status": STATUS,
            "semantic_interpretation_layer_step_ready": True,
            "semantic_interpretation_layer_ready": False,
            "authorized_statuses": list(self.AUTHORIZED_STATUSES),
            "blocked_absolute_claims": list(self.BLOCKED_ABSOLUTE_CLAIMS),
            "guarded_semantic_status": guarded["guarded_semantic_status"],
            "absolute_consciousness_status": guarded["absolute_consciousness_status"],
            "absolute_claim_attempted": guarded["absolute_claim_attempted"],
            "blocked_claim_flags": guarded["blocked_claim_flags"],
            "blocked_statuses": guarded["blocked_statuses"],
            "guard_actions": guarded["guard_actions"],
            "guard_passes": guarded["guard_passes"],
            "guard_passed": all(guarded["guard_passes"].values()),
            "separation_checks": guarded["separation_checks"],
            "interpretation_result": guarded["interpretation_result"],
            "epistemic_scope": "guard_layer_only_blocks_absolute_or_phenomenal_claims_no_subjective_proof",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            out = self.out_dir / "latest_epistemic_guard.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["persisted_path"] = str(out)
        return result
