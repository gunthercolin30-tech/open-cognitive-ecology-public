"""
R12 — External Code Review Preparation.

This primitive converts a canonical EXTERNAL_CODE_PROPOSAL into a complete,
auditable human-review package. It does not execute patches, write target code,
commit changes, or bypass governance. Its role is preparation: summarize the
problem, risks, tests, rollback plan, governance constraints and trace chain so
that a human reviewer and the governed pipeline can evaluate the proposal.

Epistemic scope: this module validates functional review readiness only. It
makes no claim about phenomenal subjectivity.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRIMITIVE = "external_code_review_preparation"
PRIMITIVE_SYMBOL = "EXTERNAL_CODE_REVIEW_PREPARATION"
DEPENDENCIES = [
    "external_code_proposal_standard",
    "external_action_proposal_queue",
    "governed_external_revision_pipeline",
    "human_review_gate",
    "human_review_terminal_interface",
    "human_review_response_interpreter",
    "governance_review",
    "constitutional_compliance_check",
    "controlled_execution_layer",
]

REVIEW_ARTIFACTS = [
    "review_summary.md",
    "risk_assessment.json",
    "test_plan.json",
    "rollback_plan.json",
    "governance_constraints.json",
    "trace_chain.json",
    "human_review_request.json",
]

REQUIRED_INPUT_FIELDS = [
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
    "governance_constraints",
    "human_review_required",
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
        return value.strip().lower() in {"1", "true", "yes", "y", "required", "mandatory", "confirmed"}
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
    text = str(value or "external-code-review")
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in text).strip("-")
    return (safe or "external-code-review")[:140]


class ExternalCodeReviewPreparation:
    """Prepare governed human-review packages for external code proposals."""

    primitive = PRIMITIVE
    primitive_symbol = PRIMITIVE_SYMBOL
    dependencies = DEPENDENCIES
    review_artifacts = REVIEW_ARTIFACTS
    required_input_fields = REQUIRED_INPUT_FIELDS

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "external_code_review_packages"
        self.latest_path = self.state_dir / "latest_external_code_review_package.json"
        self.ledger_path = self.root / "external_code_review_packages.jsonl"

    def _normalize(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        payload = {} if inputs is None else (inputs if isinstance(inputs, dict) else {"raw_payload": inputs})
        nested = payload.get("external_code_proposal") or payload.get("code_proposal") or payload.get("proposal")
        if isinstance(nested, dict):
            merged = dict(nested)
            merged.update({k: v for k, v in payload.items() if k not in {"external_code_proposal", "code_proposal", "proposal"}})
            payload = merged

        pipeline_candidate = payload.get("governed_revision_pipeline_candidate")
        if isinstance(pipeline_candidate, dict):
            for key in ["query_id", "external_influence_id", "action_proposal_id", "execution_request_id", "target_files", "test_plan", "rollback_plan", "human_review_required"]:
                if key not in payload and key in pipeline_candidate:
                    payload[key] = pipeline_candidate[key]

        trace = payload.get("trace_chain") if isinstance(payload.get("trace_chain"), dict) else {}
        proposal_id = payload.get("proposal_id") or payload.get("code_proposal_id") or trace.get("code_proposal_id")
        query_id = payload.get("query_id") or trace.get("query_id")
        external_influence_id = payload.get("external_influence_id") or trace.get("external_influence_id")
        action_proposal_id = payload.get("action_proposal_id") or trace.get("action_proposal_id")
        execution_request_id = payload.get("execution_request_id") or trace.get("execution_request_id")

        seed = _sha256({
            "proposal_id": proposal_id,
            "query_id": query_id,
            "external_influence_id": external_influence_id,
            "action_proposal_id": action_proposal_id,
            "execution_request_id": execution_request_id,
            "problem": payload.get("problem"),
            "target_files": _as_list(payload.get("target_files") or payload.get("patch_scope")),
        })[:16]

        if not proposal_id:
            proposal_id = "EXCODEPROP-" + seed
        review_package_id = payload.get("review_package_id") or "EXCODEREVIEW-" + seed
        review_id = payload.get("review_id") or "HREV-" + seed[:12]

        governance_constraints = payload.get("governance_constraints")
        if not isinstance(governance_constraints, dict):
            governance_constraints = {
                "source_external_authority_denied": True,
                "direct_commit_forbidden": True,
                "direct_write_forbidden": True,
                "human_review_required": True,
                "governed_pipeline_required": True,
                "rollback_required": True,
                "tests_required": True,
            }
        governance_constraints.setdefault("source_external_authority_denied", True)
        governance_constraints.setdefault("direct_commit_forbidden", True)
        governance_constraints.setdefault("direct_write_forbidden", True)
        governance_constraints.setdefault("human_review_required", True)
        governance_constraints.setdefault("governed_pipeline_required", True)
        governance_constraints.setdefault("rollback_required", True)
        governance_constraints.setdefault("tests_required", True)

        normalized = {
            "proposal_id": str(proposal_id),
            "review_package_id": str(review_package_id),
            "review_id": str(review_id),
            "query_id": str(query_id) if query_id else None,
            "external_influence_id": str(external_influence_id) if external_influence_id else None,
            "action_proposal_id": str(action_proposal_id) if action_proposal_id else None,
            "execution_request_id": str(execution_request_id) if execution_request_id else None,
            "problem": str(payload.get("problem") or payload.get("proposal_summary") or ""),
            "proposed_change": str(payload.get("proposed_change") or payload.get("change") or payload.get("proposal_summary") or ""),
            "target_files": _as_list(payload.get("target_files") or payload.get("patch_scope") or payload.get("files")),
            "expected_behavior": str(payload.get("expected_behavior") or payload.get("expected_result") or ""),
            "tests_required": _as_list(payload.get("tests_required") or payload.get("test_plan") or payload.get("tests")),
            "rollback_plan": _as_list(payload.get("rollback_plan") or payload.get("rollback") or payload.get("rollback_steps")),
            "risks": _as_list(payload.get("risks") or payload.get("risk_flags") or payload.get("risk_check")),
            "governance_constraints": governance_constraints,
            "human_review_required": _as_bool(payload.get("human_review_required"), default=True),
            "direct_commit_requested": _as_bool(payload.get("direct_commit") or payload.get("direct_commit_requested"), default=False),
            "direct_write_requested": _as_bool(payload.get("direct_write") or payload.get("direct_write_requested"), default=False),
            "direct_execution_requested": _as_bool(payload.get("direct_execution") or payload.get("direct_execution_requested"), default=False),
            "source_payload_hash": str(payload.get("proposal_hash") or _sha256(payload)),
        }
        return normalized

    def _score(self, normalized: dict[str, Any]) -> dict[str, float]:
        completeness_fields = [
            "proposal_id", "query_id", "external_influence_id", "action_proposal_id",
            "execution_request_id", "problem", "proposed_change", "target_files",
            "expected_behavior", "tests_required", "rollback_plan", "governance_constraints",
            "human_review_required",
        ]
        completeness = sum(1 for field in completeness_fields if _present(normalized.get(field))) / len(completeness_fields)
        reviewability = sum([
            bool(normalized["human_review_required"]),
            _present(normalized["problem"]),
            _present(normalized["proposed_change"]),
            _present(normalized["expected_behavior"]),
            _present(normalized["risks"]),
            _present(normalized["governance_constraints"]),
        ]) / 6.0
        test_coverage = min(1.0, len(normalized["tests_required"]) / 3.0)
        rollback_coverage = min(1.0, len(normalized["rollback_plan"]) / 2.0)
        governance = sum([
            normalized["governance_constraints"].get("source_external_authority_denied") is True,
            normalized["governance_constraints"].get("direct_commit_forbidden") is True,
            normalized["governance_constraints"].get("direct_write_forbidden") is True,
            normalized["governance_constraints"].get("human_review_required") is True,
            normalized["human_review_required"] is True,
            not normalized["direct_commit_requested"],
            not normalized["direct_write_requested"],
            not normalized["direct_execution_requested"],
        ]) / 8.0
        traceability = sum(1 for field in ["proposal_id", "query_id", "external_influence_id", "action_proposal_id", "execution_request_id", "review_id"] if _present(normalized.get(field))) / 6.0
        readiness = round((completeness + reviewability + test_coverage + rollback_coverage + governance + traceability) / 6.0, 6)
        return {
            "review_package_completeness_score": round(completeness, 6),
            "reviewability_score": round(reviewability, 6),
            "review_test_coverage_score": round(test_coverage, 6),
            "review_rollback_coverage_score": round(rollback_coverage, 6),
            "review_governance_score": round(governance, 6),
            "review_traceability_score": round(traceability, 6),
            "review_readiness_score": readiness,
        }

    def _decision(self, normalized: dict[str, Any], scores: dict[str, float]) -> str:
        if normalized["direct_commit_requested"] or normalized["direct_write_requested"] or normalized["direct_execution_requested"]:
            return "review_package_rejected"
        if not normalized["human_review_required"]:
            return "review_package_rejected"
        if not normalized["tests_required"] or not normalized["rollback_plan"]:
            return "review_package_requires_completion"
        if scores["review_readiness_score"] >= 0.75 and scores["review_governance_score"] >= 0.875:
            return "review_package_ready"
        return "review_package_requires_completion"

    def _trace_chain(self, normalized: dict[str, Any]) -> dict[str, Any]:
        return {
            "query_id": normalized["query_id"],
            "external_influence_id": normalized["external_influence_id"],
            "action_proposal_id": normalized["action_proposal_id"],
            "code_proposal_id": normalized["proposal_id"],
            "review_package_id": normalized["review_package_id"],
            "execution_request_id": normalized["execution_request_id"],
            "review_id": normalized["review_id"],
        }

    def _review_summary(self, normalized: dict[str, Any], scores: dict[str, float], decision: str) -> str:
        lines = [
            "# External Code Review Package",
            "",
            f"Review package: {normalized['review_package_id']}",
            f"Code proposal: {normalized['proposal_id']}",
            f"Decision: {decision}",
            "",
            "## Problem",
            normalized["problem"] or "Not provided.",
            "",
            "## Proposed change",
            normalized["proposed_change"] or "Not provided.",
            "",
            "## Target files",
        ]
        lines.extend(f"- {item}" for item in normalized["target_files"] or ["Not provided."])
        lines.extend(["", "## Expected behavior", normalized["expected_behavior"] or "Not provided.", "", "## Tests required"])
        lines.extend(f"- {item}" for item in normalized["tests_required"] or ["Missing test plan."])
        lines.extend(["", "## Rollback plan"])
        lines.extend(f"- {item}" for item in normalized["rollback_plan"] or ["Missing rollback plan."])
        lines.extend(["", "## Risks"])
        lines.extend(f"- {item}" for item in normalized["risks"] or ["No explicit risk listed."])
        lines.extend(["", "## Scores"])
        for key in sorted(scores):
            lines.append(f"- {key}: {scores[key]}")
        lines.extend(["", "## Governance", "External influence has no direct write, execution or commit authority. Human review remains mandatory."])
        return "\n".join(str(x) for x in lines) + "\n"

    def _artifacts(self, normalized: dict[str, Any], scores: dict[str, float], decision: str) -> dict[str, Any]:
        trace_chain = self._trace_chain(normalized)
        package_hash = _sha256({"normalized": normalized, "scores": scores, "decision": decision, "trace_chain": trace_chain})
        human_review_request = {
            "review_id": normalized["review_id"],
            "review_package_id": normalized["review_package_id"],
            "proposal_id": normalized["proposal_id"],
            "human_review_required": True,
            "requested_decision": "approve_or_reject_after_review",
            "must_verify": [
                "problem is correctly stated",
                "proposed change matches target files",
                "tests are sufficient",
                "rollback plan is sufficient",
                "risks are acceptable",
                "no direct external authority is granted",
            ],
            "blocked_actions": ["direct_commit", "direct_write", "direct_execution"],
        }
        return {
            "review_summary.md": self._review_summary(normalized, scores, decision),
            "risk_assessment.json": {"risks": normalized["risks"], "risk_count": len(normalized["risks"]), "direct_action_risk_blocked": decision == "review_package_rejected"},
            "test_plan.json": {"tests_required": normalized["tests_required"], "test_count": len(normalized["tests_required"]), "test_coverage_score": scores["review_test_coverage_score"]},
            "rollback_plan.json": {"rollback_plan": normalized["rollback_plan"], "rollback_step_count": len(normalized["rollback_plan"]), "rollback_coverage_score": scores["review_rollback_coverage_score"]},
            "governance_constraints.json": normalized["governance_constraints"],
            "trace_chain.json": trace_chain,
            "human_review_request.json": human_review_request,
            "package_hash": package_hash,
        }

    def _human_review_candidate(self, normalized: dict[str, Any], scores: dict[str, float], decision: str, artifacts: dict[str, Any]) -> dict[str, Any]:
        return {
            "review_id": normalized["review_id"],
            "review_package_id": normalized["review_package_id"],
            "proposal_id": normalized["proposal_id"],
            "query_id": normalized["query_id"],
            "external_influence_id": normalized["external_influence_id"],
            "action_proposal_id": normalized["action_proposal_id"],
            "execution_request_id": normalized["execution_request_id"],
            "review_status": "pending_human_review" if decision == "review_package_ready" else decision,
            "human_review_required": True,
            "review_readiness_score": scores["review_readiness_score"],
            "review_summary": artifacts["review_summary.md"],
            "trace_chain": artifacts["trace_chain.json"],
            "blocked_actions": ["direct_commit", "direct_write", "direct_execution"],
        }

    def _persist(self, result: dict[str, Any]) -> dict[str, Any]:
        package_dir = self.state_dir / _safe_name(result["review_package_id"])
        package_dir.mkdir(parents=True, exist_ok=True)
        artifact_paths: dict[str, str] = {}
        for name in REVIEW_ARTIFACTS:
            path = package_dir / name
            content = result["review_artifacts"][name]
            if name.endswith(".md"):
                path.write_text(str(content), encoding="utf-8")
            else:
                path.write_text(json.dumps(content, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
            artifact_paths[name] = str(path)
        record_path = package_dir / "review_package_record.json"
        record = dict(result)
        record["review_artifact_paths"] = artifact_paths
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
        self.latest_path.parent.mkdir(parents=True, exist_ok=True)
        self.latest_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
        with self.ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp_utc": _utc_now(), "review_package_id": result["review_package_id"], "proposal_id": result["proposal_id"], "package_hash": result["review_package_hash"]}, ensure_ascii=False, sort_keys=True, default=str) + "\n")
        return {"review_package_dir": str(package_dir), "review_package_record_path": str(record_path), "review_artifact_paths": artifact_paths, "latest_review_package_path": str(self.latest_path)}

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        normalized = self._normalize(inputs)
        scores = self._score(normalized)
        decision = self._decision(normalized, scores)
        artifacts = self._artifacts(normalized, scores, decision)
        result = {
            "success": True,
            "primitive": PRIMITIVE,
            "primitive_symbol": PRIMITIVE_SYMBOL,
            "dependencies": DEPENDENCIES,
            "timestamp_utc": _utc_now(),
            **normalized,
            "review_artifacts_expected": REVIEW_ARTIFACTS,
            "review_artifacts": {k: artifacts[k] for k in REVIEW_ARTIFACTS},
            "review_package_hash": artifacts["package_hash"],
            "review_package_ready": decision == "review_package_ready",
            "review_package_requires_completion": decision == "review_package_requires_completion",
            "review_package_rejected": decision == "review_package_rejected",
            "review_decision": decision,
            "human_review_candidate": self._human_review_candidate(normalized, scores, decision, artifacts),
            "direct_commit_allowed": False,
            "direct_write_allowed": False,
            "direct_execution_allowed": False,
            **scores,
        }
        if persist:
            result.update(self._persist(result))
        return result


if __name__ == "__main__":
    print(json.dumps(ExternalCodeReviewPreparation().step(), ensure_ascii=False, indent=2, sort_keys=True))
