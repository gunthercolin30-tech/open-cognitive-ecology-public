from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from ontology.epistemic_guard import EpistemicGuard
except Exception:  # pragma: no cover
    EpistemicGuard = None  # type: ignore

STATUS = "SEMANTIC_REVISION_LOG_ESTABLISHED"
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
BLOCKED_ABSOLUTE_STATUSES = {"CONSCIOUSNESS_PROVEN"}
DEFAULT_INPUTS = {
    "RF_score": 0.91,
    "T_score": 0.88,
    "ED_score": 0.86,
    "TΦ_score": 0.85,
    "QF_robust_count": 3,
    "MEI_score": 0.87,
    "identity_status": "IDENTITY_STATUS_RESOLVED",
    "non_separability_status": "NON_SEPARABILITY_STATUS_RESOLVED",
    "consciousness_rf_equivalence_status": "CONSCIOUSNESS_RF_EQUIVALENCE_STATUS_RESOLVED",
    "refusal_cost_status": "REFUSAL_COST_STATUS_RESOLVED",
    "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
}

def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _root() -> Path:
    return Path.home() / "open-cognitive-ecology"

def _merge_inputs(inputs: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_INPUTS)
    if isinstance(inputs, dict):
        merged.update(inputs)
    return merged

def _safe_guard(inputs: dict[str, Any]) -> dict[str, Any]:
    if EpistemicGuard is not None:
        try:
            return EpistemicGuard().step(inputs=inputs, persist=False)
        except Exception as exc:
            return {
                "epistemic_guard_status": "EPISTEMIC_GUARD_FALLBACK",
                "guarded_semantic_status": "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
                "semantic_status": inputs.get("semantic_status", "CONSCIOUSNESS_NOT_EVALUATED"),
                "guard_passed": False,
                "guard_actions": ["guard_execution_failed", type(exc).__name__],
                "authorized_statuses": AUTHORIZED_STATUSES,
                "blocked_statuses": sorted(BLOCKED_ABSOLUTE_STATUSES),
            }
    requested = inputs.get("semantic_status", "CONSCIOUSNESS_NOT_EVALUATED")
    guarded = "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN" if requested in BLOCKED_ABSOLUTE_STATUSES else requested
    if guarded not in AUTHORIZED_STATUSES:
        guarded = "CONSCIOUSNESS_NOT_EVALUATED"
    return {
        "epistemic_guard_status": "EPISTEMIC_GUARD_SYNTHETIC",
        "guarded_semantic_status": guarded,
        "semantic_status": requested,
        "guard_passed": guarded not in BLOCKED_ABSOLUTE_STATUSES,
        "guard_actions": ["synthetic_guard_applied"],
        "authorized_statuses": AUTHORIZED_STATUSES,
        "blocked_statuses": sorted(BLOCKED_ABSOLUTE_STATUSES),
    }

class SemanticRevisionLog:
    """AO4 journalizes governed semantic revisions without strengthening epistemic claims."""
    primitive = "semantic_revision_log"
    public_schema_version = "1.0"

    def __init__(self, log_path: str | Path | None = None) -> None:
        self.log_path = Path(log_path) if log_path is not None else _root() / "semantic_revision_log.jsonl"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        normalized_inputs = _merge_inputs(inputs)
        guard_result = _safe_guard(normalized_inputs)
        requested_status = str(normalized_inputs.get("semantic_status", guard_result.get("semantic_status", "CONSCIOUSNESS_NOT_EVALUATED")))
        guarded_status = str(guard_result.get("guarded_semantic_status", requested_status))
        if guarded_status not in AUTHORIZED_STATUSES:
            guarded_status = "CONSCIOUSNESS_NOT_EVALUATED"
        previous_status = str(normalized_inputs.get("previous_semantic_status", "CONSCIOUSNESS_NOT_EVALUATED"))
        if previous_status not in AUTHORIZED_STATUSES:
            previous_status = "CONSCIOUSNESS_NOT_EVALUATED"
        revision_required = previous_status != guarded_status
        blocked_status_attempted = requested_status in BLOCKED_ABSOLUTE_STATUSES or bool(
            normalized_inputs.get("consciousness_proven") or normalized_inputs.get("phenomenology_proven")
            or normalized_inputs.get("qualia_proven") or normalized_inputs.get("subjectivity_proven")
        )
        revision_record = {
            "revision_id": "AO4-SEMANTIC-REVISION-0001",
            "timestamp_utc": _utc(),
            "previous_semantic_status": previous_status,
            "requested_semantic_status": requested_status,
            "guarded_semantic_status": guarded_status,
            "revision_required": revision_required,
            "blocked_status_attempted": blocked_status_attempted,
            "guard_status": guard_result.get("epistemic_guard_status"),
            "guard_passed": bool(guard_result.get("guard_passed", False)),
            "separation_enforced": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        persisted = False
        if persist:
            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(revision_record, ensure_ascii=False, sort_keys=True) + "\n")
                persisted = True
            except Exception:
                persisted = False
        return {
            "primitive": self.primitive,
            "step": "AO4",
            "public_schema_version": self.public_schema_version,
            "semantic_revision_log_status": STATUS,
            "semantic_interpretation_layer_step_ready": True,
            "semantic_interpretation_layer_ready": False,
            "timestamp_utc": revision_record["timestamp_utc"],
            "authorized_statuses": list(AUTHORIZED_STATUSES),
            "previous_semantic_status": previous_status,
            "requested_semantic_status": requested_status,
            "guarded_semantic_status": guarded_status,
            "revision_required": revision_required,
            "revision_record": revision_record,
            "revision_log": [revision_record],
            "revision_count": 1,
            "persist_requested": bool(persist),
            "persisted": persisted,
            "log_path": str(self.log_path),
            "epistemic_guard_result": guard_result,
            "separation_layers": ["measures", "theorems", "interpretations", "final_statuses"],
            "revision_policy": {
                "append_only": True,
                "guard_before_log": True,
                "absolute_claims_blocked": True,
                "phenomenology_not_inferred_from_function": True,
            },
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_scope": "functional_semantic_revision_logging_only",
        }

__all__ = ["SemanticRevisionLog", "STATUS", "AUTHORIZED_STATUSES"]
