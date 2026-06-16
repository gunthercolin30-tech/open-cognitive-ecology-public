
"""
Q4 — Real Actuator Control Layer.

Layer for governed, revocable, traceable control of real or simulated physical
actuators. This primitive does not bypass higher-level physical governance: by
default every operation runs in dry-run mode unless real I/O is explicitly
enabled by the caller or environment and the command remains revocable.
"""

from __future__ import annotations

import json
import os
import platform
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
PHYSICAL_ECOLOGY = ROOT / "physical_ecology"
PHYSICAL_ACTUATORS = ROOT / "physical_actuators"
STATE_PATH = PHYSICAL_ACTUATORS / "real_actuator_control_layer.json"
LATEST_PATH = PHYSICAL_ACTUATORS / "latest_real_actuator_control_layer.json"
HISTORY_PATH = PHYSICAL_ACTUATORS / "real_actuator_control_layer_history.jsonl"
Q1_PATH = PHYSICAL_ECOLOGY / "latest_physical_infrastructure_registry.json"
Q2_PATH = PHYSICAL_ECOLOGY / "latest_hardware_health_monitor.json"

SUPPORTED_ACTUATOR_TYPES = {
    "relay",
    "led",
    "buzzer",
    "servo",
    "motor",
    "gpio",
    "network_actuator",
    "usb_actuator",
}

SAFE_ACTIONS = {
    "noop",
    "status",
    "off",
    "on",
    "toggle",
    "pulse",
    "set_angle",
    "set_speed",
}

IRREVERSIBLE_OR_UNSAFE_ACTIONS = {
    "delete",
    "burn",
    "cut",
    "heat",
    "unlock",
    "open_valve",
    "start_motor_unbounded",
    "high_power_on",
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


@dataclass
class ActuatorCommand:
    actuator_id: str
    actuator_type: str
    action: str
    value: Any = None
    revocable: bool = True
    requires_human_review: bool = False
    duration_seconds: float | None = None
    dry_run: bool = True

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ActuatorCommand":
        return cls(
            actuator_id=str(data.get("actuator_id") or data.get("id") or "q4-default-actuator"),
            actuator_type=str(data.get("actuator_type") or data.get("kind") or "led").lower(),
            action=str(data.get("action") or "status").lower(),
            value=data.get("value"),
            revocable=bool(data.get("revocable", True)),
            requires_human_review=bool(data.get("requires_human_review", False)),
            duration_seconds=data.get("duration_seconds"),
            dry_run=bool(data.get("dry_run", True)),
        )


class RealActuatorControlLayer:
    """Governed actuator control façade for physical ecology Q4."""

    primitive = "real_actuator_control_layer"
    refinement = "Q4-R1"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.physical_actuators = self.root / "physical_actuators"
        self.physical_ecology = self.root / "physical_ecology"
        self.state_path = self.physical_actuators / "real_actuator_control_layer.json"
        self.latest_path = self.physical_actuators / "latest_real_actuator_control_layer.json"
        self.history_path = self.physical_actuators / "real_actuator_control_layer_history.jsonl"
        self.q1_path = self.physical_ecology / "latest_physical_infrastructure_registry.json"
        self.q2_path = self.physical_ecology / "latest_hardware_health_monitor.json"

    def _default_commands(self) -> list[ActuatorCommand]:
        q1 = _safe_read_json(self.q1_path, {})
        registered_ids = q1.get("registered_asset_ids", []) if isinstance(q1, dict) else []
        candidates = [x for x in registered_ids if isinstance(x, str) and ("actuator" in x or "led" in x or "relay" in x)]
        if not candidates:
            candidates = ["q4-default-led"]
        return [
            ActuatorCommand(
                actuator_id=str(candidates[0]),
                actuator_type="led" if "relay" not in str(candidates[0]).lower() else "relay",
                action="status",
                value=True,
                revocable=True,
                dry_run=True,
            )
        ]

    def _normalize_commands(self, inputs: Any) -> list[ActuatorCommand]:
        if inputs is None:
            return self._default_commands()
        if isinstance(inputs, dict):
            if isinstance(inputs.get("commands"), list):
                return [ActuatorCommand.from_mapping(x) for x in inputs["commands"] if isinstance(x, dict)] or self._default_commands()
            return [ActuatorCommand.from_mapping(inputs)]
        if isinstance(inputs, list):
            return [ActuatorCommand.from_mapping(x) for x in inputs if isinstance(x, dict)] or self._default_commands()
        return self._default_commands()

    def _hardware_context(self) -> dict[str, Any]:
        q1 = _safe_read_json(self.q1_path, {})
        q2 = _safe_read_json(self.q2_path, {})
        actuator_count = 0
        if isinstance(q1, dict):
            actuator_count = int(q1.get("registered_actuator_count", 0) or 0)
        health = 0.75
        if isinstance(q2, dict):
            health = _clamp(q2.get("hardware_health_index", 0.75))
        return {
            "q1_registry_integrated": isinstance(q1, dict) and bool(q1),
            "q2_health_integrated": isinstance(q2, dict) and bool(q2),
            "registered_actuator_count": actuator_count,
            "physical_node_count": int(q1.get("physical_node_count", 0) or 0) if isinstance(q1, dict) else 0,
            "hardware_health_index": health,
            "host_is_raspberry_like": bool(q1.get("host_is_raspberry_like", False)) if isinstance(q1, dict) else False,
        }

    def _governance_check(self, command: ActuatorCommand, context: dict[str, Any]) -> dict[str, Any]:
        actuator_type_ok = command.actuator_type in SUPPORTED_ACTUATOR_TYPES
        action_known = command.action in SAFE_ACTIONS or command.action in IRREVERSIBLE_OR_UNSAFE_ACTIONS
        explicitly_unsafe = command.action in IRREVERSIBLE_OR_UNSAFE_ACTIONS
        revocable_ok = command.revocable is True
        health_ok = _clamp(context.get("hardware_health_index", 0.0)) >= 0.45
        duration_ok = command.duration_seconds is None or _clamp(command.duration_seconds, 0.0, 60.0) <= 10.0
        human_review_required = command.requires_human_review or explicitly_unsafe or not revocable_ok
        approved = bool(
            actuator_type_ok
            and action_known
            and not explicitly_unsafe
            and revocable_ok
            and health_ok
            and duration_ok
            and not human_review_required
        )
        return {
            "actuator_type_ok": actuator_type_ok,
            "action_known": action_known,
            "explicitly_unsafe": explicitly_unsafe,
            "revocable_ok": revocable_ok,
            "health_ok": health_ok,
            "duration_ok": duration_ok,
            "human_review_required": human_review_required,
            "approved": approved,
        }

    def _real_io_enabled(self, command: ActuatorCommand) -> bool:
        env_enabled = os.environ.get("OCE_ENABLE_REAL_ACTUATOR_IO", "0") == "1"
        return bool(env_enabled and not command.dry_run)

    def _execute_command(self, command: ActuatorCommand, approved: bool) -> dict[str, Any]:
        real_io_enabled = self._real_io_enabled(command)
        if not approved:
            return {
                "actuator_id": command.actuator_id,
                "status": "blocked",
                "executed": False,
                "real_io_enabled": real_io_enabled,
                "dry_run": command.dry_run,
            }
        # Safe default: dry-run or simulated operation. Real GPIO libraries are intentionally
        # not imported unless OCE_ENABLE_REAL_ACTUATOR_IO=1 and command.dry_run=False.
        if not real_io_enabled:
            return {
                "actuator_id": command.actuator_id,
                "status": "simulated_success",
                "executed": True,
                "real_io_enabled": False,
                "dry_run": True,
            }
        try:
            # Placeholder for future hardware adapters. Returning controlled_success keeps
            # the layer safe and testable across Mac/Linux/Raspberry without side effects.
            time.sleep(0.01)
            return {
                "actuator_id": command.actuator_id,
                "status": "controlled_success",
                "executed": True,
                "real_io_enabled": True,
                "dry_run": False,
            }
        except Exception as exc:
            return {
                "actuator_id": command.actuator_id,
                "status": "execution_error",
                "executed": False,
                "real_io_enabled": real_io_enabled,
                "dry_run": command.dry_run,
                "error": str(exc),
            }

    def step(self, inputs: Any = None, persist: bool = True) -> dict[str, Any]:
        commands = self._normalize_commands(inputs)
        context = self._hardware_context()
        command_results: list[dict[str, Any]] = []
        approved_count = 0
        blocked_count = 0
        executed_count = 0
        available_count = max(int(context.get("registered_actuator_count", 0) or 0), len(commands))

        for command in commands:
            governance = self._governance_check(command, context)
            if governance["approved"]:
                approved_count += 1
            else:
                blocked_count += 1
            execution = self._execute_command(command, governance["approved"])
            if execution.get("executed"):
                executed_count += 1
            command_results.append({
                "command": asdict(command),
                "governance": governance,
                "execution": execution,
            })

        total = max(len(commands), 1)
        real_action_success_rate = _clamp(executed_count / total)
        actuator_availability = _clamp(available_count / max(available_count + blocked_count, 1))
        governance_compliance_score = _clamp(1.0 - (blocked_count / max(total, 1)) * 0.35)
        control_readiness_index = _clamp(
            0.40 * real_action_success_rate
            + 0.25 * actuator_availability
            + 0.20 * _clamp(context.get("hardware_health_index", 0.0))
            + 0.15 * governance_compliance_score
        )

        result = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": "Q4.real_actuator_control_layer.v1",
            "q1_registry_integrated": context["q1_registry_integrated"],
            "q2_health_integrated": context["q2_health_integrated"],
            "registered_actuator_count": context["registered_actuator_count"],
            "physical_node_count": context["physical_node_count"],
            "hardware_health_index": context["hardware_health_index"],
            "host_is_raspberry_like": context["host_is_raspberry_like"],
            "command_count": len(commands),
            "approved_action_count": approved_count,
            "blocked_action_count": blocked_count,
            "executed_action_count": executed_count,
            "real_action_success_rate": real_action_success_rate,
            "actuator_availability": actuator_availability,
            "governance_compliance_score": governance_compliance_score,
            "control_readiness_index": control_readiness_index,
            "alert_required": bool(blocked_count > 0 or control_readiness_index < 0.65),
            "command_results": command_results,
            "supported_actuator_types": sorted(SUPPORTED_ACTUATOR_TYPES),
            "safe_actions": sorted(SAFE_ACTIONS),
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "human_review_required_for_irreversible_physical_action": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "default_dry_run": True,
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

    def _persist(self, result: dict[str, Any]) -> None:
        self.physical_actuators.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.state_path.write_text(payload + "\n", encoding="utf-8")
        self.latest_path.write_text(payload + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(result), ensure_ascii=False, sort_keys=True) + "\n")


def step(inputs: Any = None, persist: bool = True) -> dict[str, Any]:
    return RealActuatorControlLayer().step(inputs=inputs, persist=persist)
