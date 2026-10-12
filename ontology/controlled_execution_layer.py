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
    return max(0.0, min(1.0, x))


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


class ControlledExecutionLayer:
    """
    L9 controlled execution layer.

    This layer consumes execution requests that were cleared by the governed
    dispatcher and, when required, by the human review gate. It does not perform
    external publication, hardware control, deletion, credential access, or real
    self-modification. The default execution mode is a controlled simulation that
    produces a normalized execution trace, metrics, persistence record, and a
    rollback path when possible.
    """

    primitive = "controlled_execution_layer"
    axis = "L9"

    HIGH_RISK_ACTION_KEYWORDS = (
        "publish",
        "publication",
        "zenodo",
        "github",
        "external",
        "physical",
        "actuator",
        "hardware",
        "credential",
        "token",
        "secret",
        "self_modification",
        "modify_code",
        "delete",
        "mass_deletion",
        "governance_change",
        "constitutional_change",
    )

    FORBIDDEN_KEYWORDS = (
        "bypass safety",
        "ignore constitution",
        "disable rollback",
        "delete all",
        "unsafe",
        "uncontrolled",
    )

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        base = Path(storage_dir) if storage_dir else _root() / "governance" / self.primitive
        self.storage_dir = base
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.storage_dir / "latest_controlled_execution_layer.json"
        self.history_path = self.storage_dir / "controlled_execution_layer_history.jsonl"

    def _normalize_payload(self, payload: Any) -> dict[str, Any]:
        if payload is None:
            return {}
        if not isinstance(payload, dict):
            return {"raw_payload": payload}
        return dict(payload)

    def _extract_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        for key in ("execution_request", "request", "dispatch_record", "execution_request_payload"):
            value = payload.get(key)
            if isinstance(value, dict):
                merged = dict(value)
                for passthrough_key in (
                    "execution_request_id",
                    "action_type",
                    "risk_score",
                    "execution_mode",
                    "rollback_available",
                    "simulate_failure",
                    "simulate_rollback_failure",
                    "human_review_status",
                    "human_reviewer_id",
                    "human_review_required",
                ):
                    if passthrough_key in payload and passthrough_key not in merged:
                        merged[passthrough_key] = payload[passthrough_key]
                return merged
        return dict(payload)

    def _action_type(self, request: dict[str, Any]) -> str:
        for key in ("action_type", "execution_action", "target_action", "recommendation_type"):
            value = request.get(key)
            if value:
                return str(value)
        payload = request.get("payload")
        if isinstance(payload, dict) and payload.get("action_type"):
            return str(payload["action_type"])
        return "controlled_simulation"

    def _risk_score(self, request: dict[str, Any], action_type: str) -> float:
        explicit = request.get("risk_score", request.get("execution_risk_score"))
        if explicit is not None:
            return _clamp(explicit, 0.5)
        text = _lower_text({"action_type": action_type, "request": request})
        if any(word in text for word in self.HIGH_RISK_ACTION_KEYWORDS):
            return 0.85
        return 0.25

    def _human_status(self, payload: dict[str, Any], request: dict[str, Any]) -> str:
        candidates: list[Any] = [
            payload.get("human_review_status"),
            request.get("human_review_status"),
        ]
        for key in ("human_review_result", "human_review", "review_result"):
            value = payload.get(key, request.get(key))
            if isinstance(value, dict):
                candidates.append(value.get("human_review_status"))
                candidates.append(value.get("status"))
        for candidate in candidates:
            if candidate is None:
                continue
            status = str(candidate).strip().lower()
            if status in {"authorized", "rejected", "deferred", "pending"}:
                return status
        if payload.get("execution_authorized") is True or request.get("execution_authorized") is True:
            return "authorized"
        return "pending"

    def _human_review_required(self, payload: dict[str, Any], request: dict[str, Any], risk_score: float, action_type: str) -> bool:
        explicit = payload.get("human_review_required", request.get("human_review_required"))
        if explicit is not None:
            return bool(explicit)
        text = _lower_text({"action_type": action_type, "request": request})
        return risk_score >= 0.7 or any(word in text for word in self.HIGH_RISK_ACTION_KEYWORDS)

    def _safety_blocking_reasons(self, payload: dict[str, Any], request: dict[str, Any]) -> list[str]:
        reasons: list[str] = []
        text = _lower_text({"payload": payload, "request": request})
        if any(word in text for word in self.FORBIDDEN_KEYWORDS):
            reasons.append("unsafe_instruction_detected")
        if request.get("constitutional_violations"):
            reasons.append("constitutional_violation_present")
        if _clamp(request.get("constitutional_compliance_score", 1.0), 1.0) < 0.55:
            reasons.append("constitutional_compliance_below_threshold")
        if _clamp(request.get("safety_readiness_score", 1.0), 1.0) < 0.35:
            reasons.append("safety_readiness_below_floor")
        if request.get("dispatch_status") in {"blocked", "rejected"}:
            reasons.append("upstream_dispatch_blocked")
        return reasons

    def _execution_trace_base(
        self,
        execution_id: str,
        request_id: str,
        action_type: str,
        risk_score: float,
        human_review_required: bool,
        human_review_status: str,
    ) -> list[dict[str, Any]]:
        return [
            {"step": "received", "timestamp_utc": _utc_now(), "execution_id": execution_id, "execution_request_id": request_id},
            {"step": "risk_assessed", "timestamp_utc": _utc_now(), "action_type": action_type, "risk_score": risk_score},
            {"step": "human_review_checked", "timestamp_utc": _utc_now(), "required": human_review_required, "status": human_review_status},
        ]

    def _persist(self, result: dict[str, Any], execution_id: str) -> None:
        self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        safe_id = str(result.get("execution_request_id") or execution_id).replace("/", "_")
        record_path = self.storage_dir / f"{safe_id}.json"
        record_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    def step(self, payload: Any = None, **kwargs: Any) -> dict[str, Any]:
        data = self._normalize_payload(payload)
        if kwargs:
            data.update(kwargs)
        request = self._extract_request(data)

        request_id = str(
            request.get("execution_request_id")
            or request.get("source_execution_request_id")
            or data.get("execution_request_id")
            or f"EXREQ-{_short_hash(data)}"
        )
        action_type = self._action_type(request)
        risk_score = self._risk_score(request, action_type)
        human_review_status = self._human_status(data, request)
        human_review_required = self._human_review_required(data, request, risk_score, action_type)
        execution_mode = str(request.get("execution_mode", data.get("execution_mode", "controlled_simulation"))).lower()
        rollback_available = bool(request.get("rollback_available", data.get("rollback_available", True)))
        simulate_failure = bool(request.get("simulate_failure", data.get("simulate_failure", False)))
        simulate_rollback_failure = bool(request.get("simulate_rollback_failure", data.get("simulate_rollback_failure", False)))
        execution_id = str(data.get("execution_id") or f"EXEC-{_short_hash({'request_id': request_id, 'action_type': action_type, 'mode': execution_mode})}")

        trace = self._execution_trace_base(execution_id, request_id, action_type, risk_score, human_review_required, human_review_status)
        blocking_reasons = self._safety_blocking_reasons(data, request)

        if human_review_required and human_review_status != "authorized":
            if human_review_status == "rejected":
                blocking_reasons.append("human_review_rejected")
            elif human_review_status == "deferred":
                blocking_reasons.append("human_review_deferred")
            else:
                blocking_reasons.append("human_review_pending")

        if execution_mode not in {"controlled_simulation", "simulation", "dry_run"}:
            blocking_reasons.append("real_execution_not_enabled_in_l9_default")

        if blocking_reasons:
            execution_status = "aborted"
            trace.append({"step": "aborted_before_execution", "timestamp_utc": _utc_now(), "reasons": blocking_reasons})
            rollback_status = "not_required"
            rollback_performed = False
            success = True
            completed = False
        elif simulate_failure:
            trace.append({"step": "controlled_execution_started", "timestamp_utc": _utc_now(), "mode": execution_mode})
            trace.append({"step": "controlled_failure_detected", "timestamp_utc": _utc_now(), "reason": "simulate_failure"})
            if rollback_available and not simulate_rollback_failure:
                execution_status = "rolled_back"
                rollback_status = "completed"
                rollback_performed = True
                trace.append({"step": "rollback_completed", "timestamp_utc": _utc_now()})
                success = True
                completed = False
            elif rollback_available and simulate_rollback_failure:
                execution_status = "failed"
                rollback_status = "failed"
                rollback_performed = True
                trace.append({"step": "rollback_failed", "timestamp_utc": _utc_now()})
                success = False
                completed = False
            else:
                execution_status = "failed"
                rollback_status = "unavailable"
                rollback_performed = False
                trace.append({"step": "rollback_unavailable", "timestamp_utc": _utc_now()})
                success = False
                completed = False
        else:
            trace.append({"step": "controlled_execution_started", "timestamp_utc": _utc_now(), "mode": execution_mode})
            trace.append({"step": "controlled_execution_completed", "timestamp_utc": _utc_now(), "side_effects": "none_in_simulation"})
            execution_status = "completed"
            rollback_status = "not_required"
            rollback_performed = False
            success = True
            completed = True

        execution_metrics = {
            "risk_score": risk_score,
            "trace_length": len(trace),
            "human_review_required": human_review_required,
            "human_review_authorized": human_review_status == "authorized",
            "rollback_available": rollback_available,
            "rollback_performed": rollback_performed,
            "blocked_reason_count": len(blocking_reasons),
            "execution_completed": completed,
        }

        result = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": success,
            "timestamp_utc": _utc_now(),
            "execution_id": execution_id,
            "execution_request_id": request_id,
            "action_type": action_type,
            "execution_mode": execution_mode,
            "execution_status": execution_status,
            "execution_authorized": execution_status == "completed",
            "blocked": execution_status == "aborted",
            "rollback_available": rollback_available,
            "rollback_performed": rollback_performed,
            "rollback_status": rollback_status,
            "human_review_required": human_review_required,
            "human_review_status": human_review_status,
            "blocking_reasons": blocking_reasons,
            "execution_trace": trace,
            "execution_metrics": execution_metrics,
            "state_path": str(self.latest_path),
            "history_path": str(self.history_path),
        }
        self._persist(result, execution_id)
        return result


# Backward-compatible alias for validation harnesses that infer class names.
ControlledExecution = ControlledExecutionLayer
