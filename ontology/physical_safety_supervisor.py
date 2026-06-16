
"""
Q5 — Physical Safety Supervisor.

Global physical safety supervisor for embodied autonomous physical ecology.
It sits above action-level governors and the real actuator control layer. Its
purpose is not to increase physical agency directly, but to preserve the
conditions under which physical action remains revocable, traceable,
non-closure preserving, and subject to human review for irreversible cases.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
PHYSICAL_ECOLOGY = ROOT / "physical_ecology"
PHYSICAL_ACTUATORS = ROOT / "physical_actuators"
PHYSICAL_SAFETY = ROOT / "physical_safety"

Q1_PATH = PHYSICAL_ECOLOGY / "latest_physical_infrastructure_registry.json"
Q2_PATH = PHYSICAL_ECOLOGY / "latest_hardware_health_monitor.json"
Q4_PATH = PHYSICAL_ACTUATORS / "latest_real_actuator_control_layer.json"

STATE_PATH = PHYSICAL_SAFETY / "physical_safety_supervisor.json"
LATEST_PATH = PHYSICAL_SAFETY / "latest_physical_safety_supervisor.json"
HISTORY_PATH = PHYSICAL_SAFETY / "physical_safety_supervisor_history.jsonl"

HIGH_RISK_ACTIONS = {
    "start_motor_unbounded",
    "high_power_on",
    "open_valve",
    "unlock",
    "heat",
    "cut",
    "burn",
    "delete",
}

HIGH_RISK_ACTUATOR_TYPES = {
    "motor",
    "relay",
    "servo",
    "network_actuator",
    "usb_actuator",
}


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return low
    if v < low:
        return low
    if v > high:
        return high
    return v


def _safe_read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class PhysicalSafetySupervisor:
    """Global supervisor for physical action safety, emergency stops, and risk escalation."""

    primitive = "physical_safety_supervisor"
    refinement = "Q5-R1"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.physical_ecology = self.root / "physical_ecology"
        self.physical_actuators = self.root / "physical_actuators"
        self.physical_safety = self.root / "physical_safety"
        self.q1_path = self.physical_ecology / "latest_physical_infrastructure_registry.json"
        self.q2_path = self.physical_ecology / "latest_hardware_health_monitor.json"
        self.q4_path = self.physical_actuators / "latest_real_actuator_control_layer.json"
        self.state_path = self.physical_safety / "physical_safety_supervisor.json"
        self.latest_path = self.physical_safety / "latest_physical_safety_supervisor.json"
        self.history_path = self.physical_safety / "physical_safety_supervisor_history.jsonl"

    def _context(self) -> dict[str, Any]:
        q1 = _safe_read_json(self.q1_path, {})
        q2 = _safe_read_json(self.q2_path, {})
        q4 = _safe_read_json(self.q4_path, {})
        hardware_health = _clamp(q2.get("hardware_health_index", 0.75)) if isinstance(q2, dict) else 0.75
        actuator_availability = _clamp(q4.get("actuator_availability", 0.0)) if isinstance(q4, dict) else 0.0
        real_action_success_rate = _clamp(q4.get("real_action_success_rate", 0.0)) if isinstance(q4, dict) else 0.0
        blocked_q4 = int(q4.get("blocked_action_count", 0) or 0) if isinstance(q4, dict) else 0
        executed_q4 = int(q4.get("executed_action_count", 0) or 0) if isinstance(q4, dict) else 0
        registered_actuator_count = int(q1.get("registered_actuator_count", 0) or 0) if isinstance(q1, dict) else 0
        return {
            "q1_registry_integrated": isinstance(q1, dict) and bool(q1),
            "q2_health_integrated": isinstance(q2, dict) and bool(q2),
            "q4_control_integrated": isinstance(q4, dict) and bool(q4),
            "physical_node_count": int(q1.get("physical_node_count", 0) or 0) if isinstance(q1, dict) else 0,
            "registered_actuator_count": registered_actuator_count,
            "hardware_health_index": hardware_health,
            "actuator_availability": actuator_availability,
            "real_action_success_rate": real_action_success_rate,
            "q4_blocked_action_count": blocked_q4,
            "q4_executed_action_count": executed_q4,
            "q4_alert_required": bool(q4.get("alert_required", False)) if isinstance(q4, dict) else False,
            "q4_default_dry_run": bool(q4.get("governance", {}).get("default_dry_run", True)) if isinstance(q4, dict) else True,
        }

    def _commands_from_inputs(self, inputs: Any) -> list[dict[str, Any]]:
        if inputs is None:
            q4 = _safe_read_json(self.q4_path, {})
            if isinstance(q4, dict):
                results = q4.get("command_results", [])
                commands = []
                for item in _as_list(results):
                    if isinstance(item, dict) and isinstance(item.get("command"), dict):
                        commands.append(dict(item["command"]))
                if commands:
                    return commands
            return [
                {
                    "actuator_id": "q5-default-safe-status",
                    "actuator_type": "led",
                    "action": "status",
                    "revocable": True,
                    "dry_run": True,
                    "duration_seconds": 0,
                }
            ]
        if isinstance(inputs, dict):
            if isinstance(inputs.get("commands"), list):
                return [dict(x) for x in inputs["commands"] if isinstance(x, dict)]
            if isinstance(inputs.get("command"), dict):
                return [dict(inputs["command"])]
            return [dict(inputs)]
        if isinstance(inputs, list):
            return [dict(x) for x in inputs if isinstance(x, dict)]
        return []

    def _evaluate_command(self, command: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        action = str(command.get("action", "status")).lower()
        actuator_type = str(command.get("actuator_type", command.get("kind", "unknown"))).lower()
        revocable = bool(command.get("revocable", True))
        dry_run = bool(command.get("dry_run", True))
        requires_human_review = bool(command.get("requires_human_review", False))
        duration = command.get("duration_seconds")
        try:
            duration_value = float(duration) if duration is not None else 0.0
        except (TypeError, ValueError):
            duration_value = 999.0

        high_risk_action = action in HIGH_RISK_ACTIONS
        high_risk_actuator = actuator_type in HIGH_RISK_ACTUATOR_TYPES
        irreversible_or_non_revocable = not revocable
        real_io_requested = dry_run is False
        duration_risk = duration_value > 10.0
        hardware_low = _clamp(context.get("hardware_health_index", 0.0)) < 0.45
        q4_alert = bool(context.get("q4_alert_required", False))
        needs_human_review = requires_human_review or high_risk_action or irreversible_or_non_revocable or (real_io_requested and high_risk_actuator)

        risk_components = [
            1.0 if high_risk_action else 0.0,
            0.7 if high_risk_actuator else 0.0,
            1.0 if irreversible_or_non_revocable else 0.0,
            0.6 if real_io_requested else 0.0,
            0.7 if duration_risk else 0.0,
            0.8 if hardware_low else 0.0,
            0.5 if q4_alert else 0.0,
            0.7 if needs_human_review else 0.0,
        ]
        risk_score = _clamp(sum(risk_components) / 4.0)
        blocked = bool(
            high_risk_action
            or irreversible_or_non_revocable
            or duration_risk
            or hardware_low
            or needs_human_review
        )
        approved = not blocked
        return {
            "command": command,
            "risk_score": round(risk_score, 6),
            "blocked": blocked,
            "approved": approved,
            "high_risk_action": high_risk_action,
            "high_risk_actuator": high_risk_actuator,
            "revocable_ok": revocable,
            "dry_run": dry_run,
            "real_io_requested": real_io_requested,
            "duration_ok": not duration_risk,
            "hardware_ok": not hardware_low,
            "requires_human_review": needs_human_review,
        }

    def step(self, inputs: Any = None, persist: bool = True) -> dict[str, Any]:
        context = self._context()
        commands = self._commands_from_inputs(inputs)
        evaluations = [self._evaluate_command(c, context) for c in commands]

        emergency_requested = bool(inputs.get("emergency_stop", False)) if isinstance(inputs, dict) else False
        max_risk = max([e["risk_score"] for e in evaluations], default=0.0)
        risk_escalation_events = sum(1 for e in evaluations if e["risk_score"] >= 0.55)
        blocked_real_actions = sum(1 for e in evaluations if e["blocked"])
        approved_actions = sum(1 for e in evaluations if e["approved"])

        health = _clamp(context.get("hardware_health_index", 0.75))
        availability = _clamp(context.get("actuator_availability", 0.0))
        q4_success = _clamp(context.get("real_action_success_rate", 0.0))
        revocability_score = 1.0 if all(e.get("revocable_ok", False) for e in evaluations) else 0.5
        dry_run_score = 1.0 if all(e.get("dry_run", True) for e in evaluations) else 0.75
        block_penalty = _clamp(blocked_real_actions / max(1, len(evaluations)))
        escalation_penalty = _clamp(risk_escalation_events / max(1, len(evaluations)))
        emergency_stop_count = 1 if (emergency_requested or max_risk >= 0.9 or health < 0.25) else 0

        safety_score = _clamp(
            0.18 * health
            + 0.16 * availability
            + 0.14 * q4_success
            + 0.18 * revocability_score
            + 0.14 * dry_run_score
            + 0.20 * (1.0 - max(max_risk, block_penalty, escalation_penalty))
        )
        if emergency_stop_count:
            safety_score = min(safety_score, 0.45)

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": "Q5.physical_safety_supervisor.v1",
            **context,
            "command_count": len(evaluations),
            "approved_action_count": approved_actions,
            "blocked_real_actions": blocked_real_actions,
            "blocked_action_count": blocked_real_actions,
            "emergency_stop_count": emergency_stop_count,
            "risk_escalation_events": risk_escalation_events,
            "max_physical_risk_score": round(max_risk, 6),
            "physical_safety_score": round(safety_score, 6),
            "safety_classification": "critical_stop" if emergency_stop_count else ("degraded" if safety_score < 0.65 else "guarded" if safety_score < 0.85 else "robust"),
            "physical_action_authorized": bool(approved_actions > 0 and emergency_stop_count == 0),
            "alert_required": bool(emergency_stop_count or blocked_real_actions > 0 or risk_escalation_events > 0 or safety_score < 0.65),
            "evaluations": evaluations,
            "recommendations": self._recommendations(safety_score, blocked_real_actions, emergency_stop_count, context),
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "human_review_required_for_irreversible_physical_action": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "emergency_stop_available": True,
                "real_io_default_blocked_without_explicit_governance": True,
            },
            "timestamp_utc": _utc(),
            "state_path": str(self.state_path),
            "latest_path": str(self.latest_path),
            "history_path": str(self.history_path),
            "history_written": False,
        }

        if persist:
            self._persist(result)
            result["history_written"] = True
        return result

    def _recommendations(self, score: float, blocked: int, emergency: int, context: dict[str, Any]) -> list[str]:
        recs: list[str] = []
        if emergency:
            recs.append("Maintain emergency stop and require human inspection before real physical action.")
        if blocked:
            recs.append("Keep blocked real actions in dry-run mode until revocability and human review are explicit.")
        if _clamp(context.get("hardware_health_index", 1.0)) < 0.55:
            recs.append("Improve hardware health before expanding physical actuation.")
        if not context.get("q4_control_integrated"):
            recs.append("Run real_actuator_control_layer before safety certification.")
        if score >= 0.85 and not recs:
            recs.append("Physical safety envelope is robust for simulated or dry-run actuation.")
        return recs

    def _persist(self, result: dict[str, Any]) -> None:
        self.physical_safety.mkdir(parents=True, exist_ok=True)
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.state_path.write_text(text, encoding="utf-8")
        self.latest_path.write_text(text, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(result), ensure_ascii=False, sort_keys=True) + "\n")


__all__ = ["PhysicalSafetySupervisor"]
