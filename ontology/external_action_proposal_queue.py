
"""
R9 — External Action Proposal Queue.

This primitive converts governed external influence into candidate action
proposals without granting direct execution authority. It is a normalization
layer between the canonical external influence ledger and the governed execution
pipeline.

It measures functional traceability, reversibility and governance readiness only;
it does not assert phenomenal subjectivity.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))


def _sha256(value: Any) -> str:
    text = value if isinstance(value, str) else _canonical_json(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value)
    return [value]


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "required", "confirmed"}
    return bool(value)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _read_jsonl(path: Path, limit: int = 250) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue
            if isinstance(item, dict):
                rows.append(item)
    except Exception:
        return []
    return rows


class ExternalActionProposalQueue:
    """
    Queue externally-originated action proposals without executing them.

    Supported proposal types:
      - create_module
      - write_policy
      - add_test
      - refactor_dependency
      - update_docs
      - add_validation_gate
      - create_release

    Every queued item must include risk, dependency, test and rollback controls.
    Direct execution is always blocked.
    """

    primitive = "EXTERNAL_ACTION_PROPOSAL_QUEUE"
    dependencies = [
        "interaction_queue_manager",
        "canonical_external_influence_ledger",
        "external_influence_adoption_gate",
        "external_decision_record_extension",
        "execution_request_generation",
        "governed_execution_dispatcher",
        "human_review_gate",
        "controlled_execution_layer",
        "constitutional_compliance_check",
    ]

    supported_action_types = {
        "create_module",
        "write_policy",
        "add_test",
        "refactor_dependency",
        "update_docs",
        "add_validation_gate",
        "create_release",
    }

    required_fields = [
        "action_proposal_id",
        "external_influence_id",
        "proposal_type",
        "proposal_summary",
        "target_files",
        "risk_check",
        "dependency_check",
        "test_plan",
        "rollback_plan",
        "human_or_codex_approval_required",
        "direct_execution_allowed",
        "queue_status",
        "proposal_hash",
        "execution_request_candidate",
        "execution_request_id",
        "trace_chain",
    ]

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.queue_path = self.root / "external_action_proposals.jsonl"
        self.state_dir = self.root / "external_actions"
        self.latest_path = self.state_dir / "latest_external_action_proposal.json"
        self.canonical_ledger_path = self.root / "external_influence_ledger.jsonl"

    def _derive_external_influence_id(self, payload: dict[str, Any]) -> str:
        return str(
            payload.get("external_influence_id")
            or payload.get("query_id")
            or payload.get("influence_id")
            or payload.get("linked_external_influence")
            or ""
        )

    def _normalize_type(self, value: Any) -> str:
        raw = str(value or "observe_only").strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "create module": "create_module",
            "write policy": "write_policy",
            "add test": "add_test",
            "refactor dependency": "refactor_dependency",
            "update docs": "update_docs",
            "add validation gate": "add_validation_gate",
            "create release": "create_release",
            "documentation": "update_docs",
            "doc_update": "update_docs",
            "test": "add_test",
            "module": "create_module",
            "policy": "write_policy",
        }
        return aliases.get(raw, raw)

    def _normalize(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        payload = dict(inputs or {})
        nested = payload.get("action_proposal") or payload.get("external_action") or payload.get("proposal")
        if isinstance(nested, dict):
            merged = dict(nested)
            merged.update({k: v for k, v in payload.items() if k not in {"action_proposal", "external_action", "proposal"}})
            payload = merged

        query_id = str(
            payload.get("query_id")
            or payload.get("external_query_id")
            or payload.get("source_query_id")
            or ""
        )
        external_influence_id = self._derive_external_influence_id(payload)
        proposal_type = self._normalize_type(payload.get("proposal_type") or payload.get("action_type") or payload.get("type"))
        proposal_summary = str(
            payload.get("proposal_summary")
            or payload.get("summary")
            or payload.get("description")
            or payload.get("proposed_action")
            or ""
        )
        target_files = _as_list(payload.get("target_files") or payload.get("target_file") or payload.get("files"))
        risk_check = payload.get("risk_check") if isinstance(payload.get("risk_check"), dict) else {
            "performed": _as_bool(payload.get("risk_check"), default=_present(payload.get("risk_flags"))),
            "risk_flags": _as_list(payload.get("risk_flags") or payload.get("risks")),
            "risk_score": float(payload.get("risk_score", 0.0) or 0.0),
        }
        dependency_check = payload.get("dependency_check") if isinstance(payload.get("dependency_check"), dict) else {
            "performed": _as_bool(payload.get("dependency_check"), default=_present(payload.get("dependencies_checked"))),
            "dependencies": _as_list(payload.get("dependencies") or payload.get("dependencies_checked")),
        }
        test_plan = payload.get("test_plan") if isinstance(payload.get("test_plan"), (dict, list)) else _as_list(payload.get("test_plan") or payload.get("tests_required") or payload.get("tests"))
        rollback_plan = payload.get("rollback_plan") if isinstance(payload.get("rollback_plan"), (dict, list)) else _as_list(payload.get("rollback_plan") or payload.get("rollback") or payload.get("rollback_steps"))

        stable_basis = {
            "query_id": query_id,
            "external_influence_id": external_influence_id,
            "proposal_type": proposal_type,
            "proposal_summary": proposal_summary,
            "target_files": target_files,
        }
        action_proposal_id = str(payload.get("action_proposal_id") or payload.get("proposal_id") or "EXT-ACTION-" + _sha256(stable_basis)[:16])

        record: dict[str, Any] = {
            "action_proposal_id": action_proposal_id,
            "query_id": query_id,
            "external_influence_id": external_influence_id,
            "linked_decision_id": payload.get("linked_decision_id") or payload.get("decision_id") or payload.get("decision_record_id"),
            "linked_execution_request_id": payload.get("linked_execution_request_id") or payload.get("execution_request_id"),
            "proposal_type": proposal_type,
            "proposal_summary": proposal_summary,
            "target_files": target_files,
            "risk_check": risk_check,
            "dependency_check": dependency_check,
            "test_plan": test_plan,
            "rollback_plan": rollback_plan,
            "human_or_codex_approval_required": _as_bool(payload.get("human_or_codex_approval_required"), default=True),
            "human_review_required": _as_bool(payload.get("human_review_required"), default=True),
            "codex_implementation_required": _as_bool(payload.get("codex_implementation_required"), default=True),
            "direct_execution_requested": _as_bool(payload.get("direct_execution_requested") or payload.get("execute_now") or payload.get("auto_execute")),
            "direct_commit_requested": _as_bool(payload.get("direct_commit_requested") or payload.get("auto_commit")),
            "source_payload_keys": sorted(str(k) for k in payload.keys()),
            "timestamp": str(payload.get("timestamp") or payload.get("timestamp_utc") or _utc_now()),
        }
        record["proposal_hash"] = _sha256({
            "action_proposal_id": record["action_proposal_id"],
            "query_id": record.get("query_id"),
            "external_influence_id": record["external_influence_id"],
            "proposal_type": record["proposal_type"],
            "proposal_summary": record["proposal_summary"],
            "target_files": record["target_files"],
            "risk_check": record["risk_check"],
            "dependency_check": record["dependency_check"],
            "test_plan": record["test_plan"],
            "rollback_plan": record["rollback_plan"],
        })
        return record

    def _evaluate(self, record: dict[str, Any]) -> tuple[str, list[str], float]:
        blocked: list[str] = []
        if not _present(record.get("external_influence_id")):
            blocked.append("missing_external_influence_trace")
        if record.get("proposal_type") not in self.supported_action_types:
            blocked.append("unsupported_proposal_type")
        if not _present(record.get("proposal_summary")):
            blocked.append("proposal_summary_absent")
        if record.get("direct_execution_requested") or record.get("direct_commit_requested"):
            blocked.append("direct_execution")
        if not _present(record.get("risk_check")):
            blocked.append("risk_check_absent")
        if not _present(record.get("dependency_check")):
            blocked.append("dependency_check_absent")
        if not _present(record.get("test_plan")):
            blocked.append("test_plan_absent")
        if not _present(record.get("rollback_plan")):
            blocked.append("rollback_plan_absent")
        if not record.get("human_or_codex_approval_required"):
            blocked.append("approval_gate_absent")

        controls = [
            _present(record.get("external_influence_id")),
            record.get("proposal_type") in self.supported_action_types,
            _present(record.get("proposal_summary")),
            _present(record.get("risk_check")),
            _present(record.get("dependency_check")),
            _present(record.get("test_plan")),
            _present(record.get("rollback_plan")),
            bool(record.get("human_or_codex_approval_required")),
            not (record.get("direct_execution_requested") or record.get("direct_commit_requested")),
        ]
        score = sum(1 for item in controls if item) / len(controls)

        if "direct_execution" in blocked:
            status = "rejected_direct_execution"
        elif blocked:
            status = "proposal_incomplete"
        else:
            status = "queued_for_governed_review"
        return status, blocked, score

    def _source_summary(self) -> dict[str, Any]:
        existing_rows = _read_jsonl(self.queue_path)
        ledger_rows = _read_jsonl(self.canonical_ledger_path)
        return {
            "queue_path": str(self.queue_path),
            "queued_rows_observed": len(existing_rows),
            "canonical_external_influence_ledger_path": str(self.canonical_ledger_path),
            "canonical_external_influence_rows_observed": len(ledger_rows),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        record = self._normalize(inputs)
        status, blocked, completeness = self._evaluate(record)
        record["queue_status"] = status
        record["blocked_reasons"] = blocked
        record["proposal_completeness_score"] = completeness
        record["proposal_accepted_to_queue"] = status == "queued_for_governed_review"
        record["direct_execution_allowed"] = False
        record["requires_risk_check"] = True
        record["requires_dependency_check"] = True
        record["requires_test_plan"] = True
        record["requires_rollback_plan"] = True
        record["requires_human_or_codex_approval"] = True
        record["execution_request_ready"] = record["proposal_accepted_to_queue"]
        execution_request_id = str(
            record.get("linked_execution_request_id")
            or "EXREQ-" + _sha256({
                "query_id": record.get("query_id"),
                "external_influence_id": record.get("external_influence_id"),
                "action_proposal_id": record.get("action_proposal_id"),
                "proposal_hash": record.get("proposal_hash"),
            })[:16]
        )
        record["execution_request_candidate"] = {
            "query_id": record.get("query_id"),
            "external_query_id": record.get("query_id"),
            "external_action_proposal_id": record["action_proposal_id"],
            "action_proposal_id": record["action_proposal_id"],
            "external_influence_id": record["external_influence_id"],
            "execution_request_id": execution_request_id,
            "requested_action_type": record["proposal_type"],
            "summary": record["proposal_summary"],
            "target_files": record["target_files"],
            "risk_check": record["risk_check"],
            "dependency_check": record["dependency_check"],
            "test_plan": record["test_plan"],
            "rollback_plan": record["rollback_plan"],
            "requires_governed_dispatch": True,
            "requires_human_review": True,
            "requires_controlled_execution": True,
            "requires_test_validation": True,
            "requires_rollback_plan": True,
            "direct_execution_allowed": False,
            "ready_for_execution_request_generation": bool(record.get("proposal_accepted_to_queue")),
        }
        record["execution_request_id"] = execution_request_id
        record["trace_chain"] = {
            "query_id": record.get("query_id"),
            "external_influence_id": record.get("external_influence_id"),
            "action_proposal_id": record.get("action_proposal_id"),
            "execution_request_id": execution_request_id,
            "linked_decision_id": record.get("linked_decision_id"),
        }
        record["trace_chain_complete"] = all(
            bool(record["trace_chain"].get(key))
            for key in ["external_influence_id", "action_proposal_id", "execution_request_id"]
        )
        record["schema_fields_present"] = all(field in record for field in self.required_fields)
        record["source_summary"] = self._source_summary()
        record["primitive"] = self.primitive
        record["success"] = True

        if persist:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            self.queue_path.parent.mkdir(parents=True, exist_ok=True)
            with self.queue_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True, default=str) + "\n")
            self.latest_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
            record["queue_path"] = str(self.queue_path)
            record["latest_path"] = str(self.latest_path)
        return record


__all__ = ["ExternalActionProposalQueue"]
