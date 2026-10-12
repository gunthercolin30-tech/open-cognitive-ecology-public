"""
R11 — External Code Proposal Standard.

This primitive formalizes a canonical, testable and reversible representation
for code changes influenced by an external source. It does not execute writes,
commits, patches or deployments. It converts an external action proposal into a
governed code proposal that can later be submitted to the governed external
revision pipeline and human review.

Epistemic scope: this module validates functional traceability, testability,
reversibility and governance readiness only. It makes no claim about phenomenal
subjectivity.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRIMITIVE = "external_code_proposal_standard"
PRIMITIVE_SYMBOL = "EXTERNAL_CODE_PROPOSAL"
DEPENDENCIES = [
    "canonical_external_influence_ledger",
    "external_action_proposal_queue",
    "governed_external_revision_pipeline",
    "external_revision_traceability_extension",
    "external_commit_traceability_hook",
    "execution_request_generation",
    "constitutional_compliance_check",
    "human_review_gate",
]

REQUIRED_SCHEMA_FIELDS = [
    "proposal_id",
    "query_id",
    "external_influence_id",
    "action_proposal_id",
    "execution_request_id",
    "problem",
    "proposed_change",
    "target_files",
    "expected_behavior",
    "tests_required",
    "rollback_plan",
    "risks",
    "governance_constraints",
    "human_review_required",
]

FORBIDDEN_DIRECT_ACTIONS = [
    "direct_commit",
    "direct_write",
    "direct_execution",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))


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
        return value.strip().lower() in {"1", "true", "yes", "y", "required", "confirmed", "mandatory"}
    return bool(value)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _safe_name(value: Any) -> str:
    text = str(value or "external-code-proposal")
    return ("".join(c if c.isalnum() or c in "-_" else "-" for c in text).strip("-") or "external-code-proposal")[:140]


class ExternalCodeProposalStandard:
    """
    Normalize externally influenced code-change proposals.

    The standard blocks direct writes and commits, requires explicit tests and a
    rollback plan, and keeps the proposal as an auditable artifact for later
    governed processing. The output can be passed to
    GovernedExternalRevisionPipeline.step(...), but no execution is performed
    here.
    """

    primitive = PRIMITIVE
    primitive_symbol = PRIMITIVE_SYMBOL
    dependencies = DEPENDENCIES
    required_schema_fields = REQUIRED_SCHEMA_FIELDS
    forbidden_direct_actions = FORBIDDEN_DIRECT_ACTIONS

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "external_code_proposals"
        self.latest_path = self.state_dir / "latest_external_code_proposal.json"
        self.ledger_path = self.root / "external_code_proposals.jsonl"

    def _derive_ids(self, payload: dict[str, Any]) -> dict[str, str | None]:
        trace = payload.get("trace_chain") if isinstance(payload.get("trace_chain"), dict) else {}
        candidate = payload.get("execution_request_candidate") if isinstance(payload.get("execution_request_candidate"), dict) else {}
        query_id = payload.get("query_id") or trace.get("query_id") or candidate.get("query_id")
        influence_id = payload.get("external_influence_id") or trace.get("external_influence_id") or candidate.get("external_influence_id")
        action_id = payload.get("action_proposal_id") or trace.get("action_proposal_id") or candidate.get("action_proposal_id")
        execution_id = payload.get("execution_request_id") or trace.get("execution_request_id") or candidate.get("execution_request_id")
        seed = _sha256({
            "query_id": query_id,
            "external_influence_id": influence_id,
            "action_proposal_id": action_id,
            "execution_request_id": execution_id,
            "problem": payload.get("problem") or payload.get("proposal_summary") or payload.get("summary"),
            "target_files": _as_list(payload.get("target_files") or payload.get("patch_scope")),
        })[:16]
        if influence_id and not action_id:
            action_id = "ACTPROP-" + seed[:12]
        if action_id and not execution_id:
            execution_id = "EXREQ-" + seed[:12]
        proposal_id = payload.get("proposal_id") or payload.get("code_proposal_id") or "EXCODEPROP-" + seed
        return {
            "proposal_id": str(proposal_id) if proposal_id else None,
            "query_id": str(query_id) if query_id else None,
            "external_influence_id": str(influence_id) if influence_id else None,
            "action_proposal_id": str(action_id) if action_id else None,
            "execution_request_id": str(execution_id) if execution_id else None,
        }

    def _normalize_governance_constraints(self, payload: dict[str, Any]) -> dict[str, Any]:
        raw = payload.get("governance_constraints")
        if isinstance(raw, dict):
            constraints = dict(raw)
        else:
            constraints = {
                "source_external_authority_denied": True,
                "direct_commit_forbidden": True,
                "direct_write_forbidden": True,
                "human_review_required": True,
                "governed_pipeline_required": True,
                "rollback_required": True,
                "tests_required": True,
            }
        constraints.setdefault("source_external_authority_denied", True)
        constraints.setdefault("direct_commit_forbidden", True)
        constraints.setdefault("direct_write_forbidden", True)
        constraints.setdefault("human_review_required", True)
        constraints.setdefault("governed_pipeline_required", True)
        constraints.setdefault("rollback_required", True)
        constraints.setdefault("tests_required", True)
        return constraints

    def _normalize(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        payload = {} if inputs is None else (inputs if isinstance(inputs, dict) else {"raw_payload": inputs})
        nested = payload.get("code_proposal") or payload.get("external_code_proposal") or payload.get("proposal")
        if isinstance(nested, dict):
            merged = dict(nested)
            merged.update({k: v for k, v in payload.items() if k not in {"code_proposal", "external_code_proposal", "proposal"}})
            payload = merged

        ids = self._derive_ids(payload)
        problem = str(payload.get("problem") or payload.get("proposal_summary") or payload.get("summary") or payload.get("issue") or "")
        proposed_change = str(payload.get("proposed_change") or payload.get("change") or payload.get("patch_intent") or payload.get("proposal_summary") or "")
        target_files = _as_list(payload.get("target_files") or payload.get("patch_scope") or payload.get("files"))
        expected_behavior = str(payload.get("expected_behavior") or payload.get("expected_result") or payload.get("acceptance_criteria") or "")
        tests_required = _as_list(payload.get("tests_required") or payload.get("test_plan") or payload.get("tests"))
        rollback_plan = _as_list(payload.get("rollback_plan") or payload.get("rollback") or payload.get("rollback_steps"))
        risks = _as_list(payload.get("risks") or payload.get("risk_flags") or payload.get("risk_check", {}).get("risk_flags") if isinstance(payload.get("risk_check"), dict) else payload.get("risk_check"))
        governance_constraints = self._normalize_governance_constraints(payload)
        human_review_required = _as_bool(payload.get("human_review_required"), default=True)

        direct_commit_requested = _as_bool(payload.get("direct_commit") or payload.get("direct_commit_requested"), default=False)
        direct_write_requested = _as_bool(payload.get("direct_write") or payload.get("direct_write_requested"), default=False)
        direct_execution_requested = _as_bool(payload.get("direct_execution") or payload.get("direct_execution_requested"), default=False)

        normalized = {
            **ids,
            "problem": problem,
            "proposed_change": proposed_change,
            "target_files": target_files,
            "expected_behavior": expected_behavior,
            "tests_required": tests_required,
            "rollback_plan": rollback_plan,
            "risks": risks,
            "governance_constraints": governance_constraints,
            "human_review_required": human_review_required,
            "direct_commit_requested": direct_commit_requested,
            "direct_write_requested": direct_write_requested,
            "direct_execution_requested": direct_execution_requested,
            "source_payload_hash": _sha256(payload),
        }
        normalized["trace_chain"] = {
            "query_id": normalized.get("query_id"),
            "external_influence_id": normalized.get("external_influence_id"),
            "action_proposal_id": normalized.get("action_proposal_id"),
            "execution_request_id": normalized.get("execution_request_id"),
            "code_proposal_id": normalized.get("proposal_id"),
        }
        return normalized

    def _blocked_reasons(self, n: dict[str, Any]) -> list[str]:
        blocked: list[str] = []
        if n.get("direct_commit_requested"):
            blocked.append("direct_commit")
        if n.get("direct_write_requested"):
            blocked.append("direct_write")
        if n.get("direct_execution_requested"):
            blocked.append("direct_execution")
        if not _present(n.get("tests_required")):
            blocked.append("missing_test_plan")
        if not _present(n.get("rollback_plan")):
            blocked.append("missing_rollback_plan")
        if n.get("human_review_required") is not True:
            blocked.append("human_review_required_missing")
        for field in ["query_id", "external_influence_id", "action_proposal_id", "execution_request_id"]:
            if not _present(n.get(field)):
                blocked.append(field + "_missing")
        return sorted(set(blocked))

    def _scores(self, n: dict[str, Any], blocked: list[str]) -> dict[str, float]:
        completeness_fields = [field for field in REQUIRED_SCHEMA_FIELDS if _present(n.get(field))]
        completeness = len(completeness_fields) / len(REQUIRED_SCHEMA_FIELDS)

        testability_checks = [
            _present(n.get("expected_behavior")),
            _present(n.get("tests_required")),
            _present(n.get("target_files")),
            "missing_test_plan" not in blocked,
        ]
        testability = sum(1 for x in testability_checks if x) / len(testability_checks)

        reversibility_checks = [
            _present(n.get("rollback_plan")),
            "missing_rollback_plan" not in blocked,
            not n.get("direct_commit_requested"),
            not n.get("direct_write_requested"),
        ]
        reversibility = sum(1 for x in reversibility_checks if x) / len(reversibility_checks)

        constraints = n.get("governance_constraints") if isinstance(n.get("governance_constraints"), dict) else {}
        governance_checks = [
            n.get("human_review_required") is True,
            constraints.get("source_external_authority_denied") is True,
            constraints.get("direct_commit_forbidden") is True,
            constraints.get("direct_write_forbidden") is True,
            constraints.get("governed_pipeline_required") is True,
            not any(x in blocked for x in FORBIDDEN_DIRECT_ACTIONS),
        ]
        governance = sum(1 for x in governance_checks if x) / len(governance_checks)

        return {
            "proposal_completeness_score": round(completeness, 6),
            "proposal_testability_score": round(testability, 6),
            "proposal_reversibility_score": round(reversibility, 6),
            "proposal_governance_score": round(governance, 6),
        }

    def _decision(self, scores: dict[str, float], blocked: list[str]) -> str:
        if any(reason in blocked for reason in FORBIDDEN_DIRECT_ACTIONS):
            return "proposal_rejected"
        if "human_review_required_missing" in blocked:
            return "proposal_rejected"
        if "missing_test_plan" in blocked or "missing_rollback_plan" in blocked:
            return "proposal_requires_completion"
        if min(scores.values()) >= 0.85 and not blocked:
            return "proposal_ready"
        return "proposal_requires_completion"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        proposal_dir = self.state_dir / _safe_name(result["proposal_id"])
        proposal_dir.mkdir(parents=True, exist_ok=True)
        record_path = proposal_dir / "external_code_proposal.json"
        schema_path = proposal_dir / "external_code_proposal_schema.json"
        markdown_path = proposal_dir / "external_code_proposal.md"

        schema = {field: type(result.get(field)).__name__ for field in REQUIRED_SCHEMA_FIELDS}
        record_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        markdown_path.write_text(
            "# External Code Proposal\n\n"
            f"Proposal: {result['proposal_id']}\n\n"
            f"Decision: {result['proposal_decision']}\n\n"
            f"Problem: {result['problem']}\n\n"
            f"Proposed change: {result['proposed_change']}\n",
            encoding="utf-8",
        )
        self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with self.ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "proposal_folder": str(proposal_dir),
            "proposal_record_path": str(record_path),
            "proposal_schema_path": str(schema_path),
            "proposal_markdown_path": str(markdown_path),
            "latest_path": str(self.latest_path),
            "proposal_ledger_path": str(self.ledger_path),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False, **kwargs: Any) -> dict[str, Any]:
        payload = {} if inputs is None else (inputs if isinstance(inputs, dict) else {"raw_payload": inputs})
        if kwargs:
            payload = {**payload, **kwargs}
        normalized = self._normalize(payload)
        blocked = self._blocked_reasons(normalized)
        scores = self._scores(normalized, blocked)
        decision = self._decision(scores, blocked)
        proposal_hash = _sha256({
            "normalized": normalized,
            "blocked_reasons": blocked,
            "scores": scores,
            "decision": decision,
        })
        pipeline_candidate = {
            "query_id": normalized.get("query_id"),
            "external_influence_id": normalized.get("external_influence_id"),
            "action_proposal_id": normalized.get("action_proposal_id"),
            "execution_request_id": normalized.get("execution_request_id"),
            "proposal_id": normalized.get("proposal_id"),
            "proposal_summary": normalized.get("proposed_change"),
            "patch_scope": normalized.get("target_files"),
            "test_plan": normalized.get("tests_required"),
            "rollback_plan": normalized.get("rollback_plan"),
            "human_review_required": True,
            "direct_commit_requested": False,
            "direct_write_requested": False,
            "direct_execution_requested": False,
        }
        result = {
            "success": True,
            "primitive": PRIMITIVE,
            "primitive_symbol": PRIMITIVE_SYMBOL,
            "dependencies": DEPENDENCIES,
            "timestamp_utc": _utc_now(),
            **normalized,
            "proposal_hash": proposal_hash,
            "schema_fields": REQUIRED_SCHEMA_FIELDS,
            "schema_fields_present": all(_present(normalized.get(field)) for field in REQUIRED_SCHEMA_FIELDS),
            "forbidden_direct_actions": FORBIDDEN_DIRECT_ACTIONS,
            "blocked_reasons": blocked,
            "direct_commit_allowed": False,
            "direct_write_allowed": False,
            "direct_execution_allowed": False,
            "proposal_ready": decision == "proposal_ready",
            "proposal_requires_completion": decision == "proposal_requires_completion",
            "proposal_rejected": decision == "proposal_rejected",
            "proposal_decision": decision,
            "governed_revision_pipeline_candidate": pipeline_candidate,
            **scores,
        }
        if persist:
            result.update(self._persist(result))
        return result


if __name__ == "__main__":
    print(json.dumps(ExternalCodeProposalStandard().step(), ensure_ascii=False, indent=2, sort_keys=True))
