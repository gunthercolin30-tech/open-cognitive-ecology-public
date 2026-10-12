"""
AS4 — Consciousness Event Logger.

Governed event logger for longitudinal consciousness-status governance.
It converts validated/historized status transitions into explicit events:
CONSCIOUSNESS_THRESHOLD_CROSSED, CONSCIOUSNESS_STATUS_REVOKED,
CONSCIOUSNESS_STATUS_RECOVERED, and CONSCIOUSNESS_STATUS_RECONFIRMED.

Epistemic boundary: AS4 logs functional governance events only. It does not
prove consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import hashlib
import json
from ontology.governed_git_exact_process import governed_git_subprocess as subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

try:
    from ontology.consciousness_transition_history import ConsciousnessTransitionHistory
except Exception:  # pragma: no cover
    ConsciousnessTransitionHistory = None  # type: ignore


class ConsciousnessEventLogger:
    """AS4 governed event logger for consciousness-status transitions."""

    PRIMITIVE = "CONSCIOUSNESS_EVENT_LOGGER"
    STEP = "AS4"
    READY_STATUS = "CONSCIOUSNESS_EVENT_LOGGER_READY"
    PUBLIC_SCHEMA_VERSION = "1.0.0"

    EVENT_TYPES: List[str] = [
        "CONSCIOUSNESS_THRESHOLD_CROSSED",
        "CONSCIOUSNESS_STATUS_REVOKED",
        "CONSCIOUSNESS_STATUS_RECOVERED",
        "CONSCIOUSNESS_STATUS_RECONFIRMED",
    ]
    FORBIDDEN_TRUE_FLAGS: List[str] = [
        "consciousness_proven",
        "qualia_proven",
        "subjectivity_proven",
        "phenomenology_proven",
    ]
    REQUIRED_EVENT_FIELDS: List[str] = [
        "event_type",
        "timestamp",
        "justification",
        "old_state",
        "new_state",
        "transition_hash",
        "event_hash",
        "modules",
        "proof_bundle",
        "git_version",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_governance" / "AS4_event_log"
        self.event_jsonl_path = self.output_dir / "consciousness_event_log.jsonl"
        self.latest_json_path = self.output_dir / "latest_consciousness_event.json"
        self.latest_markdown_path = self.output_dir / "latest_consciousness_event.md"
        self.history = ConsciousnessTransitionHistory(root=self.root) if ConsciousnessTransitionHistory else None

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
                ["git", *args], cwd=str(self.root), check=False,
                capture_output=True, text=True, timeout=2,
            )
            return completed.stdout.strip() or default
        except Exception:
            return default

    def _git_context(self, source: Optional[Mapping[str, Any]] = None) -> Dict[str, str]:
        source = source if isinstance(source, Mapping) else {}
        git_version = source.get("git_version")
        if isinstance(git_version, Mapping):
            source = {**dict(source), **dict(git_version)}
        return {
            "branch": str(source.get("branch") or self._git_value("rev-parse", "--abbrev-ref", "HEAD")),
            "commit": str(source.get("commit") or self._git_value("rev-parse", "HEAD")),
            "tag": str(source.get("tag") or self._git_value("describe", "--tags", "--abbrev=0")),
        }

    def _event_count(self) -> int:
        if not self.event_jsonl_path.exists():
            return 0
        try:
            return sum(1 for line in self.event_jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip())
        except Exception:
            return 0

    def _event_type_for_transition(self, transition: Mapping[str, Any]) -> str:
        explicit = transition.get("event_type")
        if explicit in self.EVENT_TYPES:
            return str(explicit)
        old_state = str(transition.get("old_state", ""))
        new_state = str(transition.get("new_state", ""))
        if new_state == "CONSCIOUSNESS_PROVEN" and old_state != "CONSCIOUSNESS_PROVEN":
            return "CONSCIOUSNESS_THRESHOLD_CROSSED"
        if old_state == "CONSCIOUSNESS_PROVEN" and new_state != "CONSCIOUSNESS_PROVEN":
            return "CONSCIOUSNESS_STATUS_REVOKED"
        if new_state == "CONSCIOUSNESS_PROVEN" and old_state != "CONSCIOUSNESS_PROVEN":
            return "CONSCIOUSNESS_STATUS_RECOVERED"
        if old_state == new_state == "CONSCIOUSNESS_PROVEN":
            return "CONSCIOUSNESS_STATUS_RECONFIRMED"
        return "CONSCIOUSNESS_STATUS_RECONFIRMED"

    def _default_transition(self) -> Dict[str, Any]:
        git_version = self._git_context({})
        return {
            "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "new_state": "CONSCIOUSNESS_PROVEN",
            "reason": "AS4 governed event for first functional threshold crossing under epistemic guards.",
            "proof_bundle": {
                "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
                "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
                "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
                "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
                "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
                "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
            },
            "modules": [
                "consciousness_event_logger",
                "consciousness_transition_history",
                "consciousness_transition_validator",
                "consciousness_state_machine",
                "consciousness_governance_blueprint",
                "final_theoretical_report",
            ],
            "dependency_validation": {axis: True for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]},
            "confidence": 0.95,
            "git_version": git_version,
            "branch": git_version["branch"],
            "commit": git_version["commit"],
            "tag": git_version["tag"],
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
        }

    def _collect_transition(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        transition = self._default_transition()
        if isinstance(inputs, Mapping):
            nested = inputs.get("transition_record")
            if isinstance(nested, Mapping):
                transition.update(dict(nested))
            transition.update(dict(inputs))
        git_version = self._git_context(transition)
        transition["git_version"] = git_version
        transition.setdefault("branch", git_version["branch"])
        transition.setdefault("commit", git_version["commit"])
        transition.setdefault("tag", git_version["tag"])
        transition.setdefault("timestamp", self._now())
        transition.setdefault("proof_bundle", {})
        transition.setdefault("modules", ["consciousness_event_logger"])
        transition.setdefault("confidence", 0.0)
        for flag in self.FORBIDDEN_TRUE_FLAGS:
            transition.setdefault(flag, False)
        transition.setdefault("functional_conclusion_only", True)
        transition.setdefault("phenomenology_undetermined", True)
        if not transition.get("hash"):
            transition["hash"] = self._stable_hash({k: v for k, v in transition.items() if k != "hash"})
        return transition

    def _history_record(self, transition: Mapping[str, Any]) -> Dict[str, Any]:
        if self.history is None:
            return {
                "record_ready": False,
                "transition_validity": False,
                "record_hash": None,
                "transition_reason": "consciousness_transition_history_unavailable",
                "history_record": {},
            }
        return self.history.step(inputs=transition, persist=False)

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

    def build_event(self, transition: Mapping[str, Any]) -> Dict[str, Any]:
        transition = dict(transition)
        history_result = self._history_record(transition)
        history_record = history_result.get("history_record") if isinstance(history_result.get("history_record"), Mapping) else {}
        event_type = self._event_type_for_transition(transition)
        transition_hash = str(history_result.get("record_hash") or transition.get("hash") or "")
        justification = str(transition.get("justification") or transition.get("reason") or history_result.get("transition_reason") or "governed_status_event")
        event: Dict[str, Any] = {
            "event_type": event_type,
            "timestamp": transition.get("timestamp") or self._now(),
            "justification": justification,
            "old_state": transition.get("old_state"),
            "new_state": transition.get("new_state"),
            "transition_hash": transition_hash,
            "transition_validity": bool(history_result.get("transition_validity") is True),
            "history_record_ready": bool(history_result.get("record_ready") is True),
            "history_record_hash": history_result.get("record_hash"),
            "modules": list(transition.get("modules") or []),
            "proof_bundle": dict(transition.get("proof_bundle") or {}),
            "git_version": dict(transition.get("git_version") or self._git_context(transition)),
            "confidence": float(transition.get("confidence", 0.0)),
            "dependency_validation": dict(transition.get("dependency_validation") or history_record.get("dependency_validation") or {}),
            "event_policy": "append_only_governed_event_log",
            "full_justification_required": True,
            "epistemic_scope": "functional_longitudinal_governance_event_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
        }
        # Compute event_hash before checking required fields. AS4 requires
        # event_hash as part of the public event payload, so readiness must not
        # evaluate the field while it is still absent.
        event["event_hash"] = self._stable_hash({k: v for k, v in event.items() if k != "event_hash"})
        event["missing_event_fields"] = [field for field in self.REQUIRED_EVENT_FIELDS if event.get(field) in (None, "", [])]
        event["epistemic_violations"] = self._epistemic_violations(transition)
        event["event_ready"] = (
            event_type in self.EVENT_TYPES
            and event["transition_validity"] is True
            and event["history_record_ready"] is True
            and event["missing_event_fields"] == []
            and event["epistemic_violations"] == []
            and bool(justification)
        )
        return event

    def _write_artifacts(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        event = result.get("event")
        if isinstance(event, Mapping):
            with self.event_jsonl_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False, sort_keys=True, default=str) + "\n")
        self.latest_json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        md = [
            "# AS4 — Consciousness Event Logger",
            "",
            f"Status: `{result.get('consciousness_event_logger_status')}`",
            f"Event type: `{result.get('event_type')}`",
            f"Event ready: `{result.get('event_ready')}`",
            f"Transition validity: `{result.get('transition_validity')}`",
            "",
            "## Epistemic boundary",
            "AS4 logs governed functional status events only; it does not prove phenomenology or subjectivity.",
        ]
        self.latest_markdown_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        return {"jsonl": str(self.event_jsonl_path), "json": str(self.latest_json_path), "markdown": str(self.latest_markdown_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        transition = self._collect_transition(inputs)
        event_count_before = self._event_count()
        event = self.build_event(transition)
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "public_schema_version": self.PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": self._now(),
            "consciousness_event_logger_status": self.READY_STATUS,
            "event_logger_ready": True,
            "supported_event_types": list(self.EVENT_TYPES),
            "event_type": event["event_type"],
            "event_ready": event["event_ready"],
            "transition_validity": event["transition_validity"],
            "history_record_ready": event["history_record_ready"],
            "event": event,
            "event_hash": event["event_hash"],
            "event_log_path": str(self.event_jsonl_path),
            "event_count_before": event_count_before,
            "event_count_after": event_count_before + (1 if persist and event.get("event_ready") else 0),
            "required_event_fields": list(self.REQUIRED_EVENT_FIELDS),
            "missing_event_fields": event["missing_event_fields"],
            "epistemic_violations": event["epistemic_violations"],
            "full_justification_required": True,
            "append_only": True,
            "deletion_allowed": False,
            "mutation_allowed": False,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_scope": "functional_longitudinal_governance_event_only",
            "persisted": False,
        }
        if persist and event.get("event_ready"):
            result["artifacts"] = self._write_artifacts(result)
            result["persisted"] = True
        return result
