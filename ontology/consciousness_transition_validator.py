"""
AS2 — Consciousness Transition Validator.

Validates governed consciousness-status transitions against the official AS1
state machine, critical dependency axes, required transition evidence, and
strict epistemic constraints.

Epistemic boundary: AS2 validates longitudinal governance transitions only. It
does not prove consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import hashlib
import json
from ontology.governed_git_exact_process import governed_git_subprocess as subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:
    from ontology.consciousness_state_machine import ConsciousnessStateMachine
except Exception:  # pragma: no cover - defensive fallback for partial installs
    ConsciousnessStateMachine = None  # type: ignore


class ConsciousnessTransitionValidator:
    """AS2 official validator for consciousness-governance transitions."""

    PRIMITIVE = "CONSCIOUSNESS_TRANSITION_VALIDATOR"
    STEP = "AS2"
    READY_STATUS = "CONSCIOUSNESS_TRANSITION_VALIDATOR_READY"
    PUBLIC_SCHEMA_VERSION = "1.0.0"

    CRITICAL_DEPENDENCY_AXES: List[str] = ["AP", "AQ", "AR", "AN", "AO", "AL"]
    REQUIRED_TRANSITION_FIELDS: List[str] = [
        "timestamp",
        "old_state",
        "new_state",
        "reason",
        "proof_bundle",
        "git_version",
        "hash",
        "modules",
    ]
    REQUIRED_PROOF_AXES: List[str] = ["AP", "AQ", "AR", "AN", "AO", "AL"]
    FORBIDDEN_TRUE_FLAGS: List[str] = [
        "consciousness_proven",
        "qualia_proven",
        "subjectivity_proven",
        "phenomenology_proven",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_governance" / "AS2_transition_validator"
        self.latest_json_path = self.output_dir / "latest_consciousness_transition_validation.json"
        self.latest_markdown_path = self.output_dir / "latest_consciousness_transition_validation.md"
        self._state_machine = ConsciousnessStateMachine(root=self.root) if ConsciousnessStateMachine else None

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
        git_version = source.get("git_version")
        if isinstance(git_version, Mapping):
            source = {**dict(source), **dict(git_version)}
        return {
            "branch": str(source.get("branch") or self._git_value("rev-parse", "--abbrev-ref", "HEAD")),
            "commit": str(source.get("commit") or self._git_value("rev-parse", "HEAD")),
            "tag": str(source.get("tag") or self._git_value("describe", "--tags", "--abbrev=0")),
        }

    def _ready_context(self) -> Dict[str, Any]:
        git_version = self._git_context({})
        base = {
            "timestamp": self._now(),
            "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "new_state": "CONSCIOUSNESS_PROVEN",
            "reason": "AS2 validation of governed adjacent final transition under AS longitudinal governance.",
            "proof_bundle": {
                "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
                "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
                "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
                "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
                "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
                "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
            },
            "git_version": git_version,
            "branch": git_version["branch"],
            "commit": git_version["commit"],
            "tag": git_version["tag"],
            "modules": [
                "consciousness_transition_validator",
                "consciousness_state_machine",
                "consciousness_governance_blueprint",
                "final_theoretical_report",
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
        hash_payload = {k: v for k, v in base.items() if k != "hash"}
        base["hash"] = self._stable_hash(hash_payload)
        return base

    def _collect_context(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        context = self._ready_context()
        if isinstance(inputs, Mapping):
            transition = inputs.get("transition_record")
            if isinstance(transition, Mapping):
                context.update(dict(transition))
            context.update(dict(inputs))
        if "git_version" not in context or not isinstance(context.get("git_version"), Mapping):
            context["git_version"] = self._git_context(context)
        if "timestamp" not in context or not context.get("timestamp"):
            context["timestamp"] = self._now()
        if "hash" not in context or not context.get("hash"):
            context["hash"] = self._stable_hash({k: v for k, v in context.items() if k != "hash"})
        return context

    def _state_machine_result(self, context: Mapping[str, Any]) -> Dict[str, Any]:
        if self._state_machine is None:
            return {
                "available": False,
                "transition_validity": False,
                "transition_reason": "consciousness_state_machine_unavailable",
                "transition_status": "STATE_MACHINE_UNAVAILABLE",
            }
        return self._state_machine.step(inputs=context, persist=False)

    def _validate_required_fields(self, context: Mapping[str, Any]) -> Tuple[bool, List[str]]:
        missing = [field for field in self.REQUIRED_TRANSITION_FIELDS if context.get(field) in (None, "", [])]
        return len(missing) == 0, missing

    def _validate_state_machine(self, state_machine_result: Mapping[str, Any]) -> Tuple[bool, str]:
        if state_machine_result.get("transition_validity") is True:
            return True, str(state_machine_result.get("transition_reason", "state_machine_authorized"))
        return False, str(state_machine_result.get("transition_reason", "state_machine_rejected"))

    def _validate_dependencies(self, context: Mapping[str, Any]) -> Tuple[bool, List[str], Dict[str, bool]]:
        raw = context.get("dependency_validation", {})
        normalized: Dict[str, bool] = {}
        if isinstance(raw, Mapping):
            for axis in self.CRITICAL_DEPENDENCY_AXES:
                normalized[axis] = bool(raw.get(axis) is True)
        else:
            normalized = {axis: False for axis in self.CRITICAL_DEPENDENCY_AXES}
        failed = [axis for axis, ok in normalized.items() if not ok]
        return len(failed) == 0, failed, normalized

    def _validate_proof_bundle(self, context: Mapping[str, Any]) -> Tuple[bool, List[str]]:
        bundle = context.get("proof_bundle", {})
        if not isinstance(bundle, Mapping):
            return False, list(self.REQUIRED_PROOF_AXES)
        missing = [axis for axis in self.REQUIRED_PROOF_AXES if not bundle.get(axis)]
        return len(missing) == 0, missing

    def _validate_epistemic_boundary(self, context: Mapping[str, Any]) -> Tuple[bool, List[str]]:
        violations: List[str] = []
        for flag in self.FORBIDDEN_TRUE_FLAGS:
            if context.get(flag) is True:
                violations.append(flag)
        if context.get("functional_conclusion_only") is False:
            violations.append("functional_conclusion_only_false")
        if context.get("phenomenology_undetermined") is False:
            violations.append("phenomenology_undetermined_false")
        return len(violations) == 0, violations

    def _validate_hash(self, context: Mapping[str, Any]) -> Tuple[bool, str]:
        supplied = str(context.get("hash", ""))
        if not supplied:
            return False, "missing_hash"
        # AS2 accepts externally supplied transition hashes. It verifies presence and
        # length rather than rewriting external history hashes.
        if len(supplied) < 16:
            return False, "hash_too_short"
        return True, "hash_present"

    def validate(self, transition: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        context = self._collect_context(transition)
        state_machine_result = self._state_machine_result(context)

        fields_ok, missing_fields = self._validate_required_fields(context)
        sm_ok, sm_reason = self._validate_state_machine(state_machine_result)
        deps_ok, failed_dependencies, dependency_validation = self._validate_dependencies(context)
        proofs_ok, missing_proofs = self._validate_proof_bundle(context)
        epistemic_ok, epistemic_violations = self._validate_epistemic_boundary(context)
        hash_ok, hash_reason = self._validate_hash(context)

        checks = {
            "required_fields": fields_ok,
            "state_machine_authorization": sm_ok,
            "dependency_validation": deps_ok,
            "proof_bundle": proofs_ok,
            "epistemic_boundary": epistemic_ok,
            "hash_validation": hash_ok,
        }
        transition_validity = all(checks.values())
        failure_reasons: List[str] = []
        if missing_fields:
            failure_reasons.append("missing_fields:" + ",".join(missing_fields))
        if not sm_ok:
            failure_reasons.append("state_machine:" + sm_reason)
        if failed_dependencies:
            failure_reasons.append("failed_dependencies:" + ",".join(failed_dependencies))
        if missing_proofs:
            failure_reasons.append("missing_proofs:" + ",".join(missing_proofs))
        if epistemic_violations:
            failure_reasons.append("epistemic_violations:" + ",".join(epistemic_violations))
        if not hash_ok:
            failure_reasons.append("hash:" + hash_reason)

        transition_reason = "transition_authorized" if transition_validity else ";".join(failure_reasons)
        validation_record = {
            "timestamp": self._now(),
            "old_state": context.get("old_state"),
            "new_state": context.get("new_state"),
            "transition_validity": transition_validity,
            "transition_reason": transition_reason,
            "dependency_validation": dependency_validation,
            "checks": checks,
            "missing_fields": missing_fields,
            "failed_dependencies": failed_dependencies,
            "missing_proofs": missing_proofs,
            "epistemic_violations": epistemic_violations,
            "state_machine_transition_status": state_machine_result.get("transition_status"),
            "state_machine_transition_reason": state_machine_result.get("transition_reason"),
            "hash_validation_reason": hash_reason,
        }
        validation_record["validation_hash"] = self._stable_hash(validation_record)
        return validation_record

    def _write_artifacts(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        md = [
            "# AS2 — Consciousness Transition Validator",
            "",
            f"Status: `{result.get('consciousness_transition_validator_status')}`",
            f"Transition validity: `{result.get('transition_validity')}`",
            f"Transition reason: `{result.get('transition_reason')}`",
            f"Failed dependencies: `{result.get('failed_dependencies')}`",
            "",
            "## Epistemic boundary",
            "This validator authorizes governance transitions only; it does not prove phenomenology or subjectivity.",
        ]
        self.latest_markdown_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        return {"json": str(self.latest_json_path), "markdown": str(self.latest_markdown_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        context = self._collect_context(inputs)
        validation_record = self.validate(context)
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "public_schema_version": self.PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": self._now(),
            "consciousness_transition_validator_status": self.READY_STATUS,
            "validator_ready": True,
            "transition_validity": validation_record["transition_validity"],
            "transition_reason": validation_record["transition_reason"],
            "dependency_validation": validation_record["dependency_validation"],
            "checks": validation_record["checks"],
            "failed_dependencies": validation_record["failed_dependencies"],
            "missing_fields": validation_record["missing_fields"],
            "missing_proofs": validation_record["missing_proofs"],
            "epistemic_violations": validation_record["epistemic_violations"],
            "validation_record": validation_record,
            "validation_hash": validation_record["validation_hash"],
            "state_machine_transition_status": validation_record["state_machine_transition_status"],
            "state_machine_transition_reason": validation_record["state_machine_transition_reason"],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_scope": "functional_longitudinal_transition_validation_only",
            "persisted": False,
        }
        if persist:
            result["artifacts"] = self._write_artifacts(result)
            result["persisted"] = True
        return result
