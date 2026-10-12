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


def _normalize_effects(value: Any) -> list[str]:
    effects: list[str] = []
    for item in _as_list(value):
        if isinstance(item, dict):
            label = item.get("name") or item.get("effect") or item.get("id") or item.get("description")
            if label:
                effects.append(str(label).strip().lower())
        elif item is not None:
            text = str(item).strip().lower()
            if text:
                effects.append(text)
    return sorted(set(effects))


def _mean(values: list[float], default: float = 0.0) -> float:
    if not values:
        return default
    return sum(values) / len(values)


class OutcomeMonitoring:
    """
    L10 outcome monitoring.

    This primitive consumes a controlled execution record and compares the
    expected outcomes with the observed outcomes. It detects unexpected effects,
    estimates goal progress, normalizes monitoring status, and persists a
    longitudinal JSONL history for L11 effectiveness assessment.
    """

    primitive = "outcome_monitoring"
    axis = "L10"

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        base = Path(storage_dir) if storage_dir else _root() / "governance" / self.primitive
        self.storage_dir = base
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.storage_dir / "latest_outcome_monitoring.json"
        self.history_path = self.storage_dir / "outcome_monitoring_history.jsonl"

    def _normalize_payload(self, payload: Any) -> dict[str, Any]:
        if payload is None:
            return {}
        if not isinstance(payload, dict):
            return {"raw_payload": payload}
        return dict(payload)

    def _extract_execution_record(self, payload: dict[str, Any]) -> dict[str, Any]:
        for key in ("execution_record", "controlled_execution", "execution_result", "execution"):
            value = payload.get(key)
            if isinstance(value, dict):
                merged = dict(value)
                for passthrough in (
                    "execution_id",
                    "execution_request_id",
                    "action_type",
                    "execution_status",
                    "execution_authorized",
                    "rollback_status",
                    "rollback_performed",
                    "expected_outcomes",
                    "observed_outcomes",
                    "observed_effects",
                    "unexpected_effects",
                    "goal_progress",
                    "simulate_observation_gap",
                ):
                    if passthrough in payload and passthrough not in merged:
                        merged[passthrough] = payload[passthrough]
                return merged
        return dict(payload)

    def _expected_outcomes(self, payload: dict[str, Any], execution: dict[str, Any]) -> list[str]:
        candidates = [
            payload.get("expected_outcomes"),
            execution.get("expected_outcomes"),
            execution.get("expected_effects"),
        ]
        request = execution.get("execution_request") or payload.get("execution_request")
        if isinstance(request, dict):
            candidates.extend([request.get("expected_outcomes"), request.get("expected_effects")])
        effects: list[str] = []
        for candidate in candidates:
            effects.extend(_normalize_effects(candidate))
        return sorted(set(effects))

    def _observed_outcomes(self, payload: dict[str, Any], execution: dict[str, Any], expected: list[str]) -> list[str]:
        explicit: list[str] = []
        for candidate in (
            payload.get("observed_outcomes"),
            payload.get("observed_effects"),
            execution.get("observed_outcomes"),
            execution.get("observed_effects"),
            execution.get("actual_outcomes"),
        ):
            explicit.extend(_normalize_effects(candidate))
        explicit = sorted(set(explicit))
        if explicit:
            return explicit

        status = str(execution.get("execution_status", payload.get("execution_status", "unknown"))).lower()
        if payload.get("simulate_observation_gap") or execution.get("simulate_observation_gap"):
            return []
        if status == "completed":
            return list(expected) if expected else ["controlled_execution_completed"]
        if status == "rolled_back":
            return ["rollback_performed"]
        if status in {"aborted", "failed"}:
            return []
        return []

    def _unexpected_effects(
        self,
        payload: dict[str, Any],
        execution: dict[str, Any],
        expected: list[str],
        observed: list[str],
    ) -> list[str]:
        explicit: list[str] = []
        for candidate in (payload.get("unexpected_effects"), execution.get("unexpected_effects")):
            explicit.extend(_normalize_effects(candidate))
        if explicit:
            return sorted(set(explicit))
        expected_set = set(expected)
        return sorted(effect for effect in set(observed) if expected_set and effect not in expected_set)

    def _goal_progress(
        self,
        payload: dict[str, Any],
        execution: dict[str, Any],
        expected: list[str],
        observed: list[str],
        unexpected: list[str],
    ) -> float:
        explicit = payload.get("goal_progress", execution.get("goal_progress"))
        if explicit is not None:
            return _clamp(explicit)

        status = str(execution.get("execution_status", payload.get("execution_status", "unknown"))).lower()
        if status in {"aborted", "failed"}:
            return 0.0
        if status == "rolled_back":
            return 0.25 if observed else 0.0
        if expected:
            matched = len(set(expected).intersection(set(observed))) / max(1, len(set(expected)))
            penalty = min(0.5, 0.2 * len(unexpected))
            return _clamp(matched - penalty)
        if status == "completed":
            return _clamp(1.0 - min(0.5, 0.2 * len(unexpected)))
        return 0.0

    def _monitoring_status(self, execution_status: str, goal_progress: float, unexpected: list[str]) -> str:
        if execution_status in {"aborted", "failed"}:
            return "no_effect_or_failed_execution"
        if execution_status == "rolled_back":
            return "rolled_back_monitored"
        if unexpected and goal_progress < 0.7:
            return "divergent"
        if unexpected:
            return "completed_with_unexpected_effects"
        if goal_progress >= 0.95:
            return "matched"
        if goal_progress > 0.0:
            return "partial"
        return "insufficient_observation"

    def _confidence(self, expected: list[str], observed: list[str], execution_status: str) -> float:
        base = 0.7
        if execution_status == "completed":
            base += 0.15
        if expected and observed:
            base += 0.1
        if not observed:
            base -= 0.25
        return _clamp(base)

    def _persist(self, record: dict[str, Any]) -> None:
        self.latest_path.write_text(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        request_id = record.get("execution_request_id") or record.get("outcome_monitoring_id")
        if request_id:
            safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(request_id))
            (self.storage_dir / f"{safe}.json").write_text(
                json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )

    def step(self, inputs: Any = None, **kwargs: Any) -> dict[str, Any]:
        payload = self._normalize_payload(inputs)
        payload.update(kwargs)
        execution = self._extract_execution_record(payload)

        execution_id = str(execution.get("execution_id") or payload.get("execution_id") or f"EXEC-{_short_hash(execution)}")
        request_id = str(execution.get("execution_request_id") or payload.get("execution_request_id") or f"EXREQ-{_short_hash(execution)}")
        action_type = str(execution.get("action_type") or payload.get("action_type") or "unknown_action")
        execution_status = str(execution.get("execution_status") or payload.get("execution_status") or "unknown").lower()
        rollback_status = str(execution.get("rollback_status") or payload.get("rollback_status") or "not_applicable").lower()

        expected = self._expected_outcomes(payload, execution)
        observed = self._observed_outcomes(payload, execution, expected)
        unexpected = self._unexpected_effects(payload, execution, expected, observed)
        goal_progress = self._goal_progress(payload, execution, expected, observed, unexpected)
        monitoring_status = self._monitoring_status(execution_status, goal_progress, unexpected)
        confidence = self._confidence(expected, observed, execution_status)

        observation_gap = bool(expected and not observed and execution_status == "completed")
        divergence_score = _clamp((1.0 - goal_progress) + min(0.5, 0.15 * len(unexpected)))
        matched_outcomes = sorted(set(expected).intersection(set(observed)))
        missing_expected_outcomes = sorted(set(expected).difference(set(observed)))

        record: dict[str, Any] = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": True,
            "timestamp_utc": _utc_now(),
            "outcome_monitoring_id": f"OM-{_short_hash({'request_id': request_id, 'execution_id': execution_id})}",
            "execution_id": execution_id,
            "execution_request_id": request_id,
            "action_type": action_type,
            "execution_status": execution_status,
            "rollback_status": rollback_status,
            "expected_outcomes": expected,
            "observed_outcomes": observed,
            "observed_effects": observed,
            "unexpected_effects": unexpected,
            "matched_outcomes": matched_outcomes,
            "missing_expected_outcomes": missing_expected_outcomes,
            "goal_progress": goal_progress,
            "outcome_alignment_score": goal_progress,
            "divergence_score": divergence_score,
            "monitoring_status": monitoring_status,
            "observation_gap": observation_gap,
            "monitoring_confidence": confidence,
            "requires_effectiveness_assessment": True,
            "l11_ready": True,
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
        }
        self._persist(record)
        return record


# Compatibility alias used by some discovery and integration tools.
OutcomeMonitoringPrimitive = OutcomeMonitoring
