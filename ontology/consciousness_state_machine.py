"""
AS1 — Consciousness State Machine.

Official longitudinal state machine for governed consciousness-status claims.
It records authorized states, allowed adjacent transitions, forbidden transition
classes, and validation metadata required for every state change.

Epistemic boundary: AS1 does not prove consciousness, qualia, subjectivity, or
phenomenology. It governs status transitions for bounded functional claims.
"""
from __future__ import annotations

import hashlib
import json
from ontology.governed_git_exact_process import governed_git_subprocess as subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple


class ConsciousnessStateMachine:
    """AS1 official longitudinal consciousness-status state machine."""

    PRIMITIVE = "CONSCIOUSNESS_STATE_MACHINE"
    STEP = "AS1"
    READY_STATUS = "CONSCIOUSNESS_STATE_MACHINE_READY"
    PUBLIC_SCHEMA_VERSION = "1.0.0"

    STATES: List[str] = [
        "NOT_EVALUATED",
        "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
        "PHENOMENALITY_CANDIDATE_SUPPORTED",
        "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
        "CONSCIOUSNESS_PROVEN_BEST_THEORY",
        "CONSCIOUSNESS_PROVEN",
    ]

    REQUIRED_TRANSITION_FIELDS: List[str] = [
        "timestamp",
        "reason",
        "proof_bundle",
        "git_version",
        "hash",
        "modules",
    ]

    CRITICAL_DEPENDENCY_AXES: List[str] = ["AP", "AQ", "AR", "AN", "AO", "AL"]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_governance" / "AS1_state_machine"
        self.latest_json_path = self.output_dir / "latest_consciousness_state_machine.json"
        self.latest_markdown_path = self.output_dir / "latest_consciousness_state_machine.md"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _stable_hash(payload: Mapping[str, Any]) -> str:
        data = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def _git_value(self, *args: str, default: str = "unknown") -> str:
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=str(self.root),
                check=False,
                capture_output=True,
                text=True,
                timeout=2,
            )
            value = completed.stdout.strip()
            return value or default
        except Exception:
            return default

    def _git_context(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, str]:
        source = inputs if isinstance(inputs, Mapping) else {}
        return {
            "branch": str(source.get("branch") or self._git_value("rev-parse", "--abbrev-ref", "HEAD")),
            "commit": str(source.get("commit") or self._git_value("rev-parse", "HEAD")),
            "tag": str(source.get("tag") or self._git_value("describe", "--tags", "--abbrev=0")),
        }

    def _ready_context(self) -> Dict[str, Any]:
        return {
            "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "new_state": "CONSCIOUSNESS_PROVEN",
            "reason": "AL final functional certification complete under AS longitudinal governance bootstrap.",
            "proof_bundle": {
                "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
                "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
                "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
                "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
                "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
                "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
            },
            "modules": [
                "consciousness_governance_blueprint",
                "final_theoretical_report",
                "consciousness_status_resolver",
                "interpretation_reporter",
                "axiomatic_completeness_certifier",
            ],
            "confidence": 0.95,
            "dependency_validation": {axis: True for axis in self.CRITICAL_DEPENDENCY_AXES},
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
        }

    def _collect_context(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        context = self._ready_context()
        if isinstance(inputs, Mapping):
            for key in ["final_theoretical_report", "consciousness_governance_blueprint"]:
                nested = inputs.get(key)
                if isinstance(nested, Mapping):
                    context.update(dict(nested))
            context.update(dict(inputs))
        return context

    def _state_index(self, state: str) -> int:
        try:
            return self.STATES.index(state)
        except ValueError:
            return -1

    def allowed_transitions(self) -> List[Dict[str, Any]]:
        transitions: List[Dict[str, Any]] = []
        for index, state in enumerate(self.STATES[:-1]):
            transitions.append({
                "old_state": state,
                "new_state": self.STATES[index + 1],
                "transition_type": "forward_adjacent",
                "requires_justification": True,
                "requires_proof_bundle": True,
                "authorized": True,
            })
        for index, state in enumerate(self.STATES[1:], start=1):
            transitions.append({
                "old_state": state,
                "new_state": self.STATES[index - 1],
                "transition_type": "governed_revocation_or_regression",
                "requires_justification": True,
                "requires_proof_bundle": True,
                "requires_revocation_cause": True,
                "authorized": True,
            })
        return transitions

    def forbidden_transition_rules(self) -> List[str]:
        return [
            "state_jumps_without_intermediate_state_are_forbidden",
            "backward_transition_without_revocation_or_regression_evidence_is_forbidden",
            "transition_without_timestamp_reason_proof_bundle_git_version_hash_or_modules_is_forbidden",
            "transition_contradicting_AP_AQ_AR_AN_AO_AL_is_forbidden",
            "history_deletion_or_rewriting_is_forbidden",
            "phenomenal_or_subjective_truth_claim_escalation_without_explicit_semantic_authorization_is_forbidden",
        ]

    def validate_transition(self, old_state: str, new_state: str, context: Mapping[str, Any]) -> Tuple[bool, str, str]:
        old_i = self._state_index(old_state)
        new_i = self._state_index(new_state)
        if old_i < 0:
            return False, "old_state_unknown", "UNKNOWN_STATE"
        if new_i < 0:
            return False, "new_state_unknown", "UNKNOWN_STATE"
        delta = new_i - old_i
        if delta == 0:
            return True, "state_reconfirmed", "RECONFIRMATION"
        if abs(delta) > 1:
            return False, "state_jump_forbidden", "FORBIDDEN_JUMP"
        if delta == 1:
            missing = [field for field in self.REQUIRED_TRANSITION_FIELDS if field not in context or context.get(field) in (None, "", [])]
            if missing:
                return False, "missing_required_transition_fields:" + ",".join(missing), "MISSING_FIELDS"
            dependency_validation = context.get("dependency_validation", {})
            if isinstance(dependency_validation, Mapping):
                failed = [axis for axis in self.CRITICAL_DEPENDENCY_AXES if dependency_validation.get(axis) is False]
                if failed:
                    return False, "critical_dependency_failed:" + ",".join(failed), "DEPENDENCY_FAILURE"
            return True, "authorized_forward_adjacent_transition", "AUTHORIZED_FORWARD"
        revocation_keys = ["revocation_cause", "regression_evidence", "affected_module", "impact"]
        has_revocation_evidence = any(context.get(key) for key in revocation_keys)
        if not has_revocation_evidence:
            return False, "backward_transition_requires_revocation_or_regression_evidence", "MISSING_REVOCATION_EVIDENCE"
        return True, "authorized_governed_backward_transition", "AUTHORIZED_BACKWARD"

    def _transition_record(self, context: Mapping[str, Any]) -> Dict[str, Any]:
        old_state = str(context.get("old_state", "CONSCIOUSNESS_PROVEN_BEST_THEORY"))
        new_state = str(context.get("new_state", "CONSCIOUSNESS_PROVEN"))
        git_context = self._git_context(context)
        base_record: Dict[str, Any] = {
            "timestamp": str(context.get("timestamp") or self._now()),
            "old_state": old_state,
            "new_state": new_state,
            "reason": str(context.get("reason") or "AS1 governed transition evaluation."),
            "proof_bundle": context.get("proof_bundle", {}),
            "git_version": git_context,
            "branch": git_context["branch"],
            "commit": git_context["commit"],
            "tag": git_context["tag"],
            "modules": list(context.get("modules", [])) if isinstance(context.get("modules"), list) else [],
            "confidence": float(context.get("confidence", 0.0) or 0.0),
            "dependency_validation": context.get("dependency_validation", {}),
        }
        base_record["hash"] = self._stable_hash(base_record)
        valid, reason, status = self.validate_transition(old_state, new_state, base_record)
        base_record["transition_validity"] = valid
        base_record["transition_reason"] = reason
        base_record["transition_status"] = status
        return base_record

    def _machine_definition(self, transition_record: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "state_machine_id": "AS1_CONSCIOUSNESS_STATE_MACHINE",
            "states": list(self.STATES),
            "initial_state": self.STATES[0],
            "terminal_theoretical_state": self.STATES[-1],
            "allowed_transitions": self.allowed_transitions(),
            "forbidden_transition_rules": self.forbidden_transition_rules(),
            "required_transition_fields": list(self.REQUIRED_TRANSITION_FIELDS),
            "critical_dependency_axes": list(self.CRITICAL_DEPENDENCY_AXES),
            "current_transition": dict(transition_record),
            "append_only_history_required": True,
            "revocation_governed": True,
            "public_claim_escalation_requires_semantic_guard": True,
        }

    def _write_artifacts(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        md = [
            "# AS1 — Consciousness State Machine",
            "",
            f"Status: `{result.get('consciousness_state_machine_status')}`",
            f"Current state: `{result.get('current_state')}`",
            f"Target state: `{result.get('target_state')}`",
            f"Transition valid: `{result.get('transition_validity')}`",
            f"Transition reason: `{result.get('transition_reason')}`",
            "",
            "## Epistemic boundary",
            "This state machine governs functional certification statuses only; it does not prove phenomenology or subjectivity.",
        ]
        self.latest_markdown_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        return {"json": str(self.latest_json_path), "markdown": str(self.latest_markdown_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        context = self._collect_context(inputs)
        transition_record = self._transition_record(context)
        machine_definition = self._machine_definition(transition_record)
        missing_transition_fields = [
            field for field in self.REQUIRED_TRANSITION_FIELDS
            if transition_record.get(field) in (None, "", [])
        ]

        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "public_schema_version": self.PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": self._now(),
            "consciousness_state_machine_status": self.READY_STATUS,
            "state_machine_ready": True,
            "state_count": len(self.STATES),
            "states": list(self.STATES),
            "current_state": transition_record["old_state"],
            "target_state": transition_record["new_state"],
            "transition_record": transition_record,
            "transition_validity": transition_record["transition_validity"],
            "transition_reason": transition_record["transition_reason"],
            "transition_status": transition_record["transition_status"],
            "dependency_validation": transition_record.get("dependency_validation", {}),
            "allowed_transition_count": len(machine_definition["allowed_transitions"]),
            "forbidden_transition_rules": machine_definition["forbidden_transition_rules"],
            "missing_transition_fields": missing_transition_fields,
            "state_machine": machine_definition,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_scope": "functional_longitudinal_governance_only",
            "persisted": False,
        }
        result["machine_hash"] = self._stable_hash(machine_definition)
        if persist:
            result["artifacts"] = self._write_artifacts(result)
            result["persisted"] = True
        return result
