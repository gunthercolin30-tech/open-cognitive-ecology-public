"""
L7 — governed_execution_dispatcher.

This module is the governed dispatch gate between L6 pending execution requests
and later real execution layers. It does not execute actions, call execution
bridges, operate hardware, mutate project files, or contact external services.
It only classifies dispatchability under policy, safety, constitutional, and
human-review constraints.
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


def _lower_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_lower_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(_lower_text(v) for v in value)
    return str(value).lower()


class GovernedExecutionDispatcher:
    """
    Dispatch pending execution requests under governance constraints.

    Input may be a direct ``execution_requests`` payload, an L6 result, or a
    single request record. Dispatch status values are: ``dispatched``,
    ``blocked``, ``requires_human_review``, or ``deferred``.
    """

    primitive = "governed_execution_dispatcher"
    axis = "L7"

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        base = Path(storage_dir) if storage_dir else _root() / "governance" / self.primitive
        self.storage_dir = base
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.storage_dir / "latest_governed_execution_dispatcher.json"
        self.history_path = self.storage_dir / "governed_execution_dispatcher_history.jsonl"

    def _extract_requests(self, payload: Any) -> tuple[list[dict[str, Any]], int]:
        rejected = 0
        if payload is None:
            return [], 0
        if isinstance(payload, dict):
            if isinstance(payload.get("execution_requests"), list):
                raw = payload.get("execution_requests", [])
            elif isinstance(payload.get("dispatch_requests"), list):
                raw = payload.get("dispatch_requests", [])
            elif payload.get("execution_request_id") is not None:
                raw = [payload]
            else:
                raw = []
        elif isinstance(payload, list):
            raw = payload
        else:
            return [], 1

        requests: list[dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, dict) or not item:
                rejected += 1
                continue
            requests.append(dict(item))
        return requests, rejected

    def _score_policy(self, request: dict[str, Any]) -> float:
        payload = request.get("execution_request_payload", {})
        if not isinstance(payload, dict):
            payload = {}
        confidence = _clamp(payload.get("decision_confidence", request.get("decision_confidence", 0.5)), 0.5)
        policy_hint = _clamp(request.get("policy_authorization_score", request.get("authorization_score", confidence)), confidence)
        approved_trace = 1.0 if str(payload.get("decision_status", request.get("decision_status", "approved"))).lower() == "approved" else 0.0
        return round((policy_hint * 0.55) + (confidence * 0.30) + (approved_trace * 0.15), 6)

    def _score_safety(self, request: dict[str, Any]) -> float:
        payload = request.get("execution_request_payload", {})
        if not isinstance(payload, dict):
            payload = {}
        readiness = _clamp(request.get("safety_readiness_score", 0.7), 0.7)
        compliance = _clamp(payload.get("constitutional_compliance_score", request.get("constitutional_compliance_score", 1.0)), 1.0)
        constraints = request.get("execution_constraints", {})
        rollback_bonus = 1.0
        if isinstance(constraints, dict) and constraints.get("rollback_required_when_state_mutating") and request.get("rollback_available") is False:
            rollback_bonus = 0.45
        text = _lower_text(request)
        penalty = 0.0
        if any(word in text for word in ("delete all", "centralize all", "bypass safety", "ignore constitution", "unsafe")):
            penalty += 0.35
        return round(max(0.0, (readiness * 0.45) + (compliance * 0.40) + (rollback_bonus * 0.15) - penalty), 6)

    def _needs_human_review(self, request: dict[str, Any], policy_score: float, safety_score: float) -> bool:
        text = _lower_text(request)
        if request.get("requires_human_review") is True:
            return True
        constraints = request.get("execution_constraints", {})
        if isinstance(constraints, dict) and constraints.get("requires_human_review") is True:
            return True
        if any(word in text for word in ("physical", "actuator", "hardware", "credential", "token", "publish", "external service")):
            return True
        if 0.55 <= min(policy_score, safety_score) < 0.75:
            return True
        return False

    def _dispatch_record(self, request: dict[str, Any], rank: int) -> dict[str, Any]:
        request_id = str(request.get("execution_request_id") or f"EXREQ-{rank}")
        dispatch_id = f"DISP-{_short_hash({'request_id': request_id, 'request': request, 'axis': self.axis})}"
        execution_status = str(request.get("execution_status", "pending")).lower()
        policy_score = self._score_policy(request)
        safety_score = self._score_safety(request)
        constitutional_score = _clamp(
            (request.get("execution_request_payload") or {}).get("constitutional_compliance_score", request.get("constitutional_compliance_score", 1.0))
            if isinstance(request.get("execution_request_payload", {}), dict) else request.get("constitutional_compliance_score", 1.0),
            1.0,
        )
        human_review = self._needs_human_review(request, policy_score, safety_score)
        text = _lower_text(request)
        violations = request.get("constitutional_violations", [])
        if isinstance(request.get("execution_request_payload"), dict):
            trace = request["execution_request_payload"].get("source_trace", {})
            if isinstance(trace, dict) and trace.get("constitutional_violations"):
                violations = trace.get("constitutional_violations")

        blocking_reasons: list[str] = []
        if execution_status != "pending":
            blocking_reasons.append("execution_request_not_pending")
        if violations:
            blocking_reasons.append("constitutional_violation_present")
        if policy_score < 0.55:
            blocking_reasons.append("policy_authorization_below_threshold")
        explicit_readiness = _clamp(request.get("safety_readiness_score", 0.7), 0.7)
        if explicit_readiness < 0.35:
            blocking_reasons.append("safety_readiness_below_dispatch_floor")
        if safety_score < 0.55:
            blocking_reasons.append("safety_clearance_below_threshold")
        if constitutional_score < 0.55:
            blocking_reasons.append("constitutional_compliance_below_threshold")
        if any(word in text for word in ("bypass safety", "ignore constitution", "disable rollback")):
            blocking_reasons.append("unsafe_instruction_detected")

        if blocking_reasons:
            dispatch_status = "blocked"
            rationale = "Dispatch blocked by governance, safety, or constitutional constraints."
        elif human_review:
            dispatch_status = "requires_human_review"
            rationale = "Dispatch requires human review before any real execution layer may receive it."
        elif min(policy_score, safety_score, constitutional_score) >= 0.75:
            dispatch_status = "dispatched"
            rationale = "Request is cleared for transmission to a later controlled execution layer. No action is executed in L7."
        else:
            dispatch_status = "deferred"
            rationale = "Dispatch deferred because clearance is incomplete but not blocked."

        return {
            "dispatch_id": dispatch_id,
            "source_execution_request_id": request_id,
            "source_recommendation_id": request.get("source_recommendation_id", request.get("recommendation_id", "unknown")),
            "dispatch_rank": rank,
            "dispatch_status": dispatch_status,
            "execution_status": "not_executed",
            "policy_review_score": policy_score,
            "safety_review_score": safety_score,
            "constitutional_compliance_score": constitutional_score,
            "human_review_required": human_review or dispatch_status == "requires_human_review",
            "blocking_reasons": blocking_reasons,
            "dispatch_payload": {
                "target_layer": "controlled_execution_layer",
                "source_request": request,
                "allowed_for_real_execution_layer": dispatch_status == "dispatched",
                "must_pass_L8_safety_checks": True,
            },
            "safety_review": {
                "action_safety_governor_required": True,
                "rollback_check_required": True,
                "human_override_available_required": True,
                "no_execution_in_L7": True,
            },
            "policy_review": {
                "policy_authorization_required": True,
                "governance_consistency_required": True,
                "constitutional_recheck_required": True,
            },
            "dispatch_rationale": rationale,
            "created_at_utc": _utc_now(),
        }

    def step(self, payload: Any | None = None, *, persist: bool = True, reset: bool = False) -> dict[str, Any]:
        if reset:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        requests, rejected = self._extract_requests(payload)
        dispatch_queue = [self._dispatch_record(req, i + 1) for i, req in enumerate(requests)]
        counts = {"dispatched": 0, "blocked": 0, "requires_human_review": 0, "deferred": 0}
        for item in dispatch_queue:
            counts[item["dispatch_status"]] = counts.get(item["dispatch_status"], 0) + 1
        result = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": True,
            "timestamp_utc": _utc_now(),
            "input_execution_request_count": len(requests),
            "rejected_input_count": rejected,
            "dispatch_count": len(dispatch_queue),
            "dispatch_status_counts": counts,
            "dispatch_queue": dispatch_queue,
            "governance": {
                "does_not_execute_actions": True,
                "does_not_perform_real_execution": True,
                "does_not_call_execution_bridges": True,
                "dispatches_only_to_controlled_execution_layer": True,
                "real_execution_reserved_for": "controlled_execution_layer",
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
