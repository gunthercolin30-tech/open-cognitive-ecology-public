"""
L6 — execution_request_generation.

This module converts approved governance decisions into traceable execution
requests. It is intentionally non-executive: it does not execute actions, does
not dispatch requests, does not call bridges, and does not mutate target
modules. Dispatch is reserved for the next governed layer.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _root() -> Path:
    return Path.home() / "open-cognitive-ecology"


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = default
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _stable_json(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    except TypeError:
        return json.dumps(str(value), sort_keys=True, ensure_ascii=False)


def _short_hash(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()[:16]


class ExecutionRequestGeneration:
    """
    Generate governed execution requests from L5 decisions.

    Input may be a direct ``decision_queue`` payload, an L5 result, or a single
    decision record. Only records with ``decision_status == approved`` are
    converted into requests. Rejected and deferred decisions remain traceable
    but do not generate execution requests.
    """

    primitive = "execution_request_generation"
    axis = "L6"

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        base = Path(storage_dir) if storage_dir else _root() / "governance" / self.primitive
        self.storage_dir = base
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.storage_dir / "latest_execution_request_generation.json"
        self.history_path = self.storage_dir / "execution_request_generation_history.jsonl"

    def _extract_decisions(self, payload: Any) -> tuple[list[dict[str, Any]], int]:
        rejected = 0
        if payload is None:
            return [], 0

        if isinstance(payload, dict):
            if isinstance(payload.get("decision_queue"), list):
                raw = payload.get("decision_queue", [])
            elif isinstance(payload.get("decisions"), list):
                raw = payload.get("decisions", [])
            elif payload.get("decision_status") is not None:
                raw = [payload]
            else:
                raw = []
        elif isinstance(payload, list):
            raw = payload
        else:
            return [], 1

        decisions: list[dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, dict) or not item:
                rejected += 1
                continue
            decisions.append(dict(item))
        return decisions, rejected

    def _infer_execution_type(self, decision: dict[str, Any]) -> str:
        text = " ".join(str(decision.get(k, "")) for k in (
            "recommendation_type", "recommended_action", "decision_rationale", "action_type"
        )).lower()
        if any(x in text for x in ("physical", "actuator", "sensor", "hardware")):
            return "physical_or_embodied_action_request"
        if any(x in text for x in ("github", "zenodo", "publication", "external", "collaboration")):
            return "external_collaboration_request"
        if any(x in text for x in ("memory", "archive", "state")):
            return "memory_or_state_management_request"
        if any(x in text for x in ("policy", "governance", "constitution")):
            return "governance_policy_request"
        return "generic_governed_execution_request"

    def _required_safety_checks(self, decision: dict[str, Any], execution_type: str) -> list[str]:
        checks = [
            "policy_authorization_check",
            "action_safety_governor_check",
            "constitutional_compliance_recheck",
            "non_closure_pressure_check",
            "audit_trace_integrity_check",
        ]
        if execution_type == "physical_or_embodied_action_request":
            checks.extend(["physical_safety_supervisor_check", "human_review_check"])
        if execution_type == "memory_or_state_management_request":
            checks.extend(["backup_available_check", "rollback_available_check"])
        if decision.get("requires_human_review") is True:
            checks.append("explicit_human_review_required")
        return list(dict.fromkeys(checks))

    def _make_request(self, decision: dict[str, Any], rank: int) -> dict[str, Any]:
        execution_type = self._infer_execution_type(decision)
        decision_id = str(decision.get("decision_id") or decision.get("recommendation_id") or f"decision_{rank}")
        request_seed = {"decision_id": decision_id, "decision": decision, "axis": self.axis}
        request_id = f"EXREQ-{_short_hash(request_seed)}"
        confidence = _clamp(decision.get("decision_confidence", decision.get("recommendation_confidence", 0.5)), 0.5)
        compliance = _clamp(decision.get("constitutional_compliance_score", 1.0), 1.0)
        safety_readiness = round((confidence + compliance) / 2.0, 6)
        return {
            "execution_request_id": request_id,
            "source_decision_id": decision_id,
            "source_recommendation_id": decision.get("recommendation_id", decision_id),
            "execution_request_rank": rank,
            "execution_request_type": execution_type,
            "execution_status": "pending",
            "dispatch_status": "not_dispatched",
            "execution_request_payload": {
                "recommended_action": decision.get("recommended_action", decision.get("decision_rationale", "governed_action_unspecified")),
                "decision_status": decision.get("decision_status"),
                "decision_confidence": confidence,
                "constitutional_compliance_score": compliance,
                "source_trace": decision,
            },
            "execution_constraints": {
                "must_not_execute_in_L6": True,
                "requires_governed_dispatcher": True,
                "requires_policy_authorization": True,
                "requires_safety_clearance": True,
                "requires_constitutional_recheck": True,
                "rollback_required_when_state_mutating": True,
            },
            "required_safety_checks": self._required_safety_checks(decision, execution_type),
            "safety_readiness_score": safety_readiness,
            "request_rationale": (
                "Approved decision converted into a pending execution request. "
                "No execution or dispatch has occurred in L6."
            ),
            "created_at_utc": _utc_now(),
        }

    def step(self, payload: Any | None = None, *, persist: bool = True, reset: bool = False) -> dict[str, Any]:
        if reset:
            self.storage_dir.mkdir(parents=True, exist_ok=True)

        decisions, rejected = self._extract_decisions(payload)
        execution_requests: list[dict[str, Any]] = []
        blocked_decisions: list[dict[str, Any]] = []

        for decision in decisions:
            status = str(decision.get("decision_status", "")).lower()
            if status == "approved":
                execution_requests.append(self._make_request(decision, len(execution_requests) + 1))
            else:
                blocked_decisions.append({
                    "recommendation_id": decision.get("recommendation_id", decision.get("decision_id", "unknown")),
                    "decision_status": decision.get("decision_status", "unknown"),
                    "request_generated": False,
                    "reason": "only approved decisions generate execution requests",
                })

        result = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": True,
            "timestamp_utc": _utc_now(),
            "input_decision_count": len(decisions),
            "rejected_input_count": rejected,
            "execution_request_count": len(execution_requests),
            "blocked_decision_count": len(blocked_decisions),
            "execution_requests": execution_requests,
            "blocked_decisions": blocked_decisions,
            "governance": {
                "does_not_execute_actions": True,
                "does_not_dispatch_requests": True,
                "does_not_call_execution_bridges": True,
                "generates_pending_requests_only": True,
                "next_required_layer": "governed_execution_dispatcher",
            },
            "state_paths": {
                "latest": str(self.latest_path),
                "history": str(self.history_path),
            },
        }

        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")
