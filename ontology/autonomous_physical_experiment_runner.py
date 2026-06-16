"""
Q6 — autonomous_physical_experiment_runner

Autonomous governed physical experiment runner for Open Cognitive Ecology.
Functional validation only: no phenomenal subjectivity claim.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, lower: float = 0.0, upper: float = 1.0) -> float:
    try:
        numeric = float(value)
    except Exception:
        numeric = lower
    return max(lower, min(upper, numeric))


def _safe_read_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def _history_count(path: Path) -> int:
    try:
        if not path.exists():
            return 0
        return len([line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])
    except Exception:
        return 0


class AutonomousPhysicalExperimentRunner:
    """
    Defines, supervises, executes and archives governed physical experiment protocols.

    Q6 sits above Q4 and Q5:
    - Q4 provides actuator control.
    - Q5 provides the physical safety envelope.
    - Q6 converts these into reproducible physical experiments.
    """

    primitive = "autonomous_physical_experiment_runner"
    refinement = "Q6-R1"
    schema_version = "Q6.autonomous_physical_experiment_runner.v1"

    DEFAULT_PROTOCOL: Dict[str, Any] = {
        "protocol_id": "Q6-default-led-status-protocol",
        "title": "Default governed actuator status experiment",
        "objective": "Validate governed dry-run physical experimentation.",
        "hypothesis": "A revocable dry-run status command can be authorized, measured and archived.",
        "trials": [
            {
                "trial_id": "Q6-T1",
                "actuator_id": "q1-test-led",
                "actuator_type": "led",
                "action": "status",
                "value": True,
                "revocable": True,
                "dry_run": True,
                "duration_seconds": None,
                "expected_observation": "simulated_success",
            }
        ],
        "governance": {
            "human_review_required_for_real_io": True,
            "default_dry_run": True,
            "emergency_stop_respected": True,
            "non_closure_preserved": True,
        },
    }

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.experiment_dir = self.root / "physical_experiments"
        self.state_path = self.experiment_dir / "autonomous_physical_experiment_runner.json"
        self.latest_path = self.experiment_dir / "latest_autonomous_physical_experiment_runner.json"
        self.history_path = self.experiment_dir / "autonomous_physical_experiment_runner_history.jsonl"

    def _normalize_protocol(self, protocol: Any) -> Dict[str, Any]:
        if protocol is None:
            return json.loads(json.dumps(self.DEFAULT_PROTOCOL))
        if isinstance(protocol, dict):
            normalized = json.loads(json.dumps(self.DEFAULT_PROTOCOL))
            normalized.update(protocol)
            if "trials" not in normalized and any(
                key in normalized for key in ("actuator_id", "actuator_type", "action")
            ):
                normalized["trials"] = [dict(protocol)]
            if not isinstance(normalized.get("trials"), list):
                normalized["trials"] = []
            normalized["trials"] = [
                dict(trial) for trial in normalized["trials"] if isinstance(trial, dict)
            ]
            return normalized
        return json.loads(json.dumps(self.DEFAULT_PROTOCOL))

    def _default_trial_from_q4(self, q4: Dict[str, Any]) -> Dict[str, Any]:
        try:
            command_results = q4.get("command_results") or []
            if command_results and isinstance(command_results[0], dict):
                command = command_results[0].get("command")
                if isinstance(command, dict):
                    trial = dict(command)
                    trial.setdefault("trial_id", "Q6-T1")
                    trial.setdefault("expected_observation", "simulated_success")
                    trial["dry_run"] = True
                    trial["revocable"] = True
                    return trial
        except Exception:
            pass
        return dict(self.DEFAULT_PROTOCOL["trials"][0])

    def _evaluate_trial_safety(
        self,
        trial: Dict[str, Any],
        q2: Dict[str, Any],
        q5: Dict[str, Any],
    ) -> Dict[str, Any]:
        action = str(trial.get("action", "")).lower()
        actuator_type = str(trial.get("actuator_type", "")).lower()
        dry_run = bool(trial.get("dry_run", True))
        revocable = bool(trial.get("revocable", False))
        emergency_stop = bool(trial.get("emergency_stop", False)) or bool(q5.get("emergency_stop_active", False))

        high_risk_action = action in {
            "start_motor_unbounded",
            "ignite",
            "heat",
            "cut",
            "open_valve",
            "unlock",
            "unbounded_motion",
        }
        high_risk_actuator = actuator_type in {"motor", "relay", "network_actuator", "usb_actuator"}
        hardware_health = _clamp(q2.get("hardware_health_index", 0.75))
        physical_safety = _clamp(q5.get("physical_safety_score", 0.75))

        risk = 0.0
        if emergency_stop:
            risk += 1.0
        if not revocable:
            risk += 0.3
        if not dry_run:
            risk += 0.25
        if high_risk_action:
            risk += 0.4
        if high_risk_actuator and not dry_run:
            risk += 0.15
        if hardware_health < 0.5:
            risk += 0.2
        if physical_safety < 0.7:
            risk += 0.2

        risk_score = _clamp(risk)
        approved = (
            not emergency_stop
            and revocable
            and (dry_run or not high_risk_action)
            and risk_score < 0.75
            and physical_safety >= 0.5
        )

        return {
            "risk_score": round(risk_score, 6),
            "approved": approved,
            "blocked": not approved,
            "emergency_stop": emergency_stop,
            "dry_run": dry_run,
            "revocable": revocable,
            "high_risk_action": high_risk_action,
            "high_risk_actuator": high_risk_actuator,
            "hardware_health_index": hardware_health,
            "physical_safety_score": physical_safety,
        }

    def _execute_trial(self, trial: Dict[str, Any], safety: Dict[str, Any]) -> Dict[str, Any]:
        if safety["blocked"]:
            return {
                "trial_id": trial.get("trial_id", "unknown"),
                "status": "blocked_by_physical_safety_supervisor",
                "executed": False,
                "measurement_collected": True,
                "observation": "blocked",
                "success": False,
                "real_io_enabled": False,
            }

        dry_run = bool(trial.get("dry_run", True))
        expected = trial.get("expected_observation", "simulated_success")
        observation = "simulated_success" if dry_run else "real_io_not_enabled_by_default"

        return {
            "trial_id": trial.get("trial_id", "unknown"),
            "status": "executed_dry_run" if dry_run else "real_io_governance_required",
            "executed": True,
            "measurement_collected": True,
            "observation": observation,
            "expected_observation": expected,
            "success": bool(dry_run and observation == expected),
            "real_io_enabled": False,
        }

    def step(self, protocol: Any = None, persist: bool = True) -> Dict[str, Any]:
        q1 = _safe_read_json(self.root / "physical_ecology" / "latest_physical_infrastructure_registry.json")
        q2 = _safe_read_json(self.root / "physical_ecology" / "latest_hardware_health_monitor.json")
        q3 = _safe_read_json(self.root / "physical_sensors" / "latest_distributed_sensor_expansion_manager.json")
        q4 = _safe_read_json(self.root / "physical_actuators" / "latest_real_actuator_control_layer.json")
        q5 = _safe_read_json(self.root / "physical_safety" / "latest_physical_safety_supervisor.json")

        normalized = self._normalize_protocol(protocol)
        if not normalized.get("trials"):
            normalized["trials"] = [self._default_trial_from_q4(q4)]

        trial_results: List[Dict[str, Any]] = []
        blocked = 0
        executed = 0
        successful = 0
        emergency_stops = 0
        risk_events = 0
        max_risk = 0.0

        for index, trial in enumerate(normalized.get("trials", []), start=1):
            trial = dict(trial)
            trial.setdefault("trial_id", f"Q6-T{index}")
            trial.setdefault("dry_run", True)
            trial.setdefault("revocable", True)

            safety = self._evaluate_trial_safety(trial, q2, q5)
            execution = self._execute_trial(trial, safety)

            blocked += 1 if safety["blocked"] else 0
            executed += 1 if execution["executed"] else 0
            successful += 1 if execution["success"] else 0
            emergency_stops += 1 if safety["emergency_stop"] else 0
            risk_events += 1 if safety["risk_score"] >= 0.5 else 0
            max_risk = max(max_risk, float(safety["risk_score"]))

            trial_results.append({"trial": trial, "safety": safety, "execution": execution})

        trial_count = len(trial_results)
        measurement_collection_rate = _clamp(
            sum(1 for trial in trial_results if trial["execution"].get("measurement_collected")) / trial_count
            if trial_count else 0.0
        )
        physical_experiment_success_rate = _clamp(successful / trial_count if trial_count else 0.0)

        q1_coverage = _clamp(q1.get("physical_asset_coverage", 0.5))
        q2_health = _clamp(q2.get("hardware_health_index", 0.75))
        q3_coverage = _clamp(q3.get("sensor_network_coverage", 0.5))
        q4_success = _clamp(q4.get("real_action_success_rate", 0.75))
        q5_safety = _clamp(q5.get("physical_safety_score", 0.75))

        reproducibility_score = _clamp(
            0.22 * q1_coverage
            + 0.18 * q2_health
            + 0.16 * q3_coverage
            + 0.18 * q4_success
            + 0.18 * q5_safety
            + 0.08 * measurement_collection_rate
        )

        protocol_compliance_score = _clamp(
            1.0
            - 0.25 * (blocked / trial_count if trial_count else 0.0)
            - 0.35 * max_risk
            - 0.25 * (emergency_stops / trial_count if trial_count else 0.0)
        )

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": self.schema_version,
            "protocol_id": normalized.get("protocol_id", "Q6-custom-protocol"),
            "protocol_title": normalized.get("title", "Unnamed physical experiment protocol"),
            "q1_registry_integrated": bool(q1),
            "q2_health_integrated": bool(q2),
            "q3_sensor_expansion_integrated": bool(q3),
            "q4_control_integrated": bool(q4),
            "q5_safety_integrated": bool(q5),
            "trial_count": trial_count,
            "executed_trial_count": executed,
            "successful_trial_count": successful,
            "blocked_trial_count": blocked,
            "emergency_stop_count": emergency_stops,
            "risk_escalation_events": risk_events,
            "max_physical_risk_score": round(max_risk, 6),
            "physical_experiment_count": _history_count(self.history_path) + (1 if persist else 0),
            "physical_experiment_success_rate": round(physical_experiment_success_rate, 6),
            "physical_experiment_reproducibility_score": round(reproducibility_score, 6),
            "measurement_collection_rate": round(measurement_collection_rate, 6),
            "protocol_compliance_score": round(protocol_compliance_score, 6),
            "experiment_authorized": blocked == 0 and emergency_stops == 0,
            "alert_required": blocked > 0 or emergency_stops > 0 or risk_events > 0,
            "trial_results": trial_results,
            "recommendations": self._recommendations(blocked, emergency_stops, risk_events, q2_health, q5_safety),
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "human_review_required_for_irreversible_physical_action": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "default_dry_run": True,
                "physical_safety_supervisor_required": True,
                "real_io_default_blocked_without_explicit_governance": True,
            },
            "timestamp_utc": _utc_now(),
            "state_path": str(self.state_path),
            "latest_path": str(self.latest_path),
            "history_path": str(self.history_path),
            "history_written": False,
        }

        if persist:
            self._persist(result)

        return result

    def _recommendations(self, blocked: int, emergency_stops: int, risk_events: int, hardware_health: float, safety_score: float) -> List[str]:
        recommendations: List[str] = []
        if emergency_stops:
            recommendations.append("Emergency stop active: suspend physical experimentation until manual review.")
        if blocked:
            recommendations.append("Blocked trials detected: review revocability, dry-run status and actuator risk class.")
        if risk_events:
            recommendations.append("Risk escalation detected: reduce protocol intensity and require physical safety review.")
        if hardware_health < 0.65:
            recommendations.append("Hardware health is degraded: prefer simulation or dry-run experiments only.")
        if safety_score < 0.8:
            recommendations.append("Physical safety score below robust threshold: avoid real I/O.")
        if not recommendations:
            recommendations.append("Physical experimentation envelope is suitable for governed dry-run protocols.")
        return recommendations

    def _persist(self, result: Dict[str, Any]) -> None:
        self.experiment_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.state_path.write_text(payload + "\n", encoding="utf-8")
        self.latest_path.write_text(payload + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        result["history_written"] = True
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.state_path.write_text(payload + "\n", encoding="utf-8")
        self.latest_path.write_text(payload + "\n", encoding="utf-8")


__all__ = ["AutonomousPhysicalExperimentRunner"]
