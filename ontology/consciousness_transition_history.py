"""
AS3 — Consciousness Transition History.

Append-only longitudinal history for governed consciousness-status transitions.
Each record carries timestamp, old/new state, reason, commit, branch, tag,
modules, confidence, proof bundle, transition validation, hash, and hash-chain
metadata.

Epistemic boundary: AS3 records governance transitions only. It does not prove
consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import hashlib
import json
from ontology.governed_git_exact_process import governed_git_subprocess as subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:
    from ontology.consciousness_transition_validator import ConsciousnessTransitionValidator
except Exception:  # pragma: no cover - defensive fallback for partial installs
    ConsciousnessTransitionValidator = None  # type: ignore


class ConsciousnessTransitionHistory:
    """AS3 append-only transition history for consciousness governance."""

    PRIMITIVE = "CONSCIOUSNESS_TRANSITION_HISTORY"
    STEP = "AS3"
    READY_STATUS = "CONSCIOUSNESS_TRANSITION_HISTORY_READY"
    PUBLIC_SCHEMA_VERSION = "1.0.0"

    REQUIRED_HISTORY_FIELDS: List[str] = [
        "timestamp",
        "old_state",
        "new_state",
        "reason",
        "commit",
        "branch",
        "tag",
        "modules",
        "confidence",
        "proof_bundle",
        "hash",
    ]
    CRITICAL_AXES: List[str] = ["AP", "AQ", "AR", "AN", "AO", "AL"]
    FORBIDDEN_TRUE_FLAGS: List[str] = [
        "consciousness_proven",
        "qualia_proven",
        "subjectivity_proven",
        "phenomenology_proven",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_governance" / "AS3_transition_history"
        self.history_jsonl_path = self.output_dir / "consciousness_transition_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_consciousness_transition_history.json"
        self.latest_markdown_path = self.output_dir / "latest_consciousness_transition_history.md"
        self.validator = ConsciousnessTransitionValidator(root=self.root) if ConsciousnessTransitionValidator else None

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

    def _last_record(self) -> Optional[Dict[str, Any]]:
        if not self.history_jsonl_path.exists():
            return None
        try:
            lines = [line for line in self.history_jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if not lines:
                return None
            parsed = json.loads(lines[-1])
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None

    def _history_count(self) -> int:
        if not self.history_jsonl_path.exists():
            return 0
        try:
            return sum(1 for line in self.history_jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip())
        except Exception:
            return 0

    def _ready_transition(self) -> Dict[str, Any]:
        git_version = self._git_context({})
        base: Dict[str, Any] = {
            "timestamp": self._now(),
            "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "new_state": "CONSCIOUSNESS_PROVEN",
            "reason": "AS3 append-only history record for governed adjacent final transition.",
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
                "consciousness_transition_history",
                "consciousness_transition_validator",
                "consciousness_state_machine",
                "consciousness_governance_blueprint",
                "final_theoretical_report",
            ],
            "confidence": 0.95,
            "dependency_validation": {axis: True for axis in self.CRITICAL_AXES},
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
        }
        base["hash"] = self._stable_hash({k: v for k, v in base.items() if k != "hash"})
        return base

    def _collect_transition(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        transition = self._ready_transition()
        if isinstance(inputs, Mapping):
            nested = inputs.get("transition_record")
            if isinstance(nested, Mapping):
                transition.update(dict(nested))
            transition.update(dict(inputs))
        git_version = transition.get("git_version") if isinstance(transition.get("git_version"), Mapping) else self._git_context(transition)
        transition["git_version"] = dict(git_version)
        transition["branch"] = str(transition.get("branch") or git_version.get("branch") or "unknown")
        transition["commit"] = str(transition.get("commit") or git_version.get("commit") or "unknown")
        transition["tag"] = str(transition.get("tag") or git_version.get("tag") or "unknown")
        transition.setdefault("timestamp", self._now())
        transition.setdefault("modules", ["consciousness_transition_history"])
        transition.setdefault("confidence", 0.0)
        transition.setdefault("proof_bundle", {})
        transition.setdefault("dependency_validation", {axis: False for axis in self.CRITICAL_AXES})
        transition.setdefault("functional_conclusion_only", True)
        transition.setdefault("phenomenology_undetermined", True)
        for flag in self.FORBIDDEN_TRUE_FLAGS:
            transition.setdefault(flag, False)
        if not transition.get("hash"):
            transition["hash"] = self._stable_hash({k: v for k, v in transition.items() if k != "hash"})
        return transition

    def _validate_transition(self, transition: Mapping[str, Any]) -> Dict[str, Any]:
        if self.validator is None:
            return {
                "transition_validity": False,
                "transition_reason": "consciousness_transition_validator_unavailable",
                "dependency_validation": {axis: False for axis in self.CRITICAL_AXES},
                "checks": {"validator_available": False},
            }
        return self.validator.step(inputs=transition, persist=False)

    def _missing_history_fields(self, record: Mapping[str, Any]) -> List[str]:
        return [field for field in self.REQUIRED_HISTORY_FIELDS if record.get(field) in (None, "", [])]

    def _epistemic_violations(self, transition: Mapping[str, Any]) -> List[str]:
        violations: List[str] = []
        for flag in self.FORBIDDEN_TRUE_FLAGS:
            if transition.get(flag) is True:
                violations.append(flag)
        if transition.get("functional_conclusion_only") is False:
            violations.append("functional_conclusion_only_false")
        if transition.get("phenomenology_undetermined") is False:
            violations.append("phenomenology_undetermined_false")
        return violations

    def build_history_record(self, transition: Mapping[str, Any]) -> Dict[str, Any]:
        transition = dict(transition)
        validation = self._validate_transition(transition)
        last = self._last_record()
        previous_hash = str(last.get("record_hash")) if isinstance(last, Mapping) and last.get("record_hash") else None
        sequence_index = self._history_count() + 1

        record: Dict[str, Any] = {
            "sequence_index": sequence_index,
            "timestamp": transition.get("timestamp") or self._now(),
            "old_state": transition.get("old_state"),
            "new_state": transition.get("new_state"),
            "reason": transition.get("reason"),
            "commit": transition.get("commit"),
            "branch": transition.get("branch"),
            "tag": transition.get("tag"),
            "modules": list(transition.get("modules") or []),
            "confidence": float(transition.get("confidence", 0.0)),
            "proof_bundle": dict(transition.get("proof_bundle") or {}),
            "hash": str(transition.get("hash") or ""),
            "previous_hash": previous_hash,
            "transition_validity": bool(validation.get("transition_validity") is True),
            "transition_reason": str(validation.get("transition_reason", "unknown")),
            "dependency_validation": dict(validation.get("dependency_validation") or {}),
            "validator_hash": validation.get("validation_hash"),
            "append_only_policy": "no_deletion_no_mutation_append_only_jsonl",
            "epistemic_scope": "functional_longitudinal_transition_history_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
        }
        record["missing_history_fields"] = self._missing_history_fields(record)
        record["epistemic_violations"] = self._epistemic_violations(transition)
        record["record_ready"] = (
            record["transition_validity"] is True
            and record["missing_history_fields"] == []
            and record["epistemic_violations"] == []
        )
        record["record_hash"] = self._stable_hash({k: v for k, v in record.items() if k != "record_hash"})
        return record

    def _write_artifacts(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        record = result.get("history_record")
        if isinstance(record, Mapping):
            with self.history_jsonl_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, sort_keys=True, default=str) + "\n")
        self.latest_json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        md = [
            "# AS3 — Consciousness Transition History",
            "",
            f"Status: `{result.get('consciousness_transition_history_status')}`",
            f"Append-only: `{result.get('append_only')}`",
            f"History count before append: `{result.get('history_count_before')}`",
            f"Record ready: `{result.get('record_ready')}`",
            f"Transition validity: `{result.get('transition_validity')}`",
            "",
            "## Epistemic boundary",
            "AS3 historizes governed functional status transitions only; it does not prove phenomenology or subjectivity.",
        ]
        self.latest_markdown_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        return {
            "jsonl": str(self.history_jsonl_path),
            "json": str(self.latest_json_path),
            "markdown": str(self.latest_markdown_path),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        transition = self._collect_transition(inputs)
        history_count_before = self._history_count()
        history_record = self.build_history_record(transition)
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "public_schema_version": self.PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": self._now(),
            "consciousness_transition_history_status": self.READY_STATUS,
            "history_ready": True,
            "append_only": True,
            "deletion_allowed": False,
            "mutation_allowed": False,
            "history_path": str(self.history_jsonl_path),
            "history_count_before": history_count_before,
            "history_count_after": history_count_before + (1 if persist and history_record.get("record_ready") else 0),
            "required_history_fields": list(self.REQUIRED_HISTORY_FIELDS),
            "missing_history_fields": history_record["missing_history_fields"],
            "record_ready": history_record["record_ready"],
            "transition_validity": history_record["transition_validity"],
            "transition_reason": history_record["transition_reason"],
            "dependency_validation": history_record["dependency_validation"],
            "history_record": history_record,
            "record_hash": history_record["record_hash"],
            "previous_hash": history_record["previous_hash"],
            "epistemic_violations": history_record["epistemic_violations"],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_scope": "functional_longitudinal_transition_history_only",
            "persisted": False,
        }
        if persist and history_record.get("record_ready"):
            result["artifacts"] = self._write_artifacts(result)
            result["persisted"] = True
        return result
