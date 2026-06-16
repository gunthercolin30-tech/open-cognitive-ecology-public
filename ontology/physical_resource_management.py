"""
Q10 — physical_resource_management

Physical resource management layer for Open Cognitive Ecology.

Functional validation only. This module estimates and governs physical resource
pressure across energy, storage, bandwidth, CPU/RAM and multi-site resources.
"""

from __future__ import annotations

import json
import math
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, lower: float = 0.0, upper: float = 1.0) -> float:
    try:
        numeric = float(value)
    except Exception:
        numeric = lower
    if math.isnan(numeric) or math.isinf(numeric):
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


def _disk_usage_ratio(path: Path) -> float:
    try:
        usage = shutil.disk_usage(path)
        if usage.total <= 0:
            return 0.0
        return _clamp(usage.used / usage.total)
    except Exception:
        return 0.0


def _memory_used_ratio_macos() -> float:
    try:
        # Conservative fallback: Q2 already measures memory; avoid platform-heavy parsing here.
        return 0.5
    except Exception:
        return 0.5


class PhysicalResourceManagement:
    """
    Manages physical resource pressure over the embodied physical ecology.

    Q10 is distinct from Q2:
    - Q2 observes hardware health.
    - Q10 estimates utilization pressure and recommends allocation policy.
    """

    primitive = "physical_resource_management"
    refinement = "Q10-R1"
    schema_version = "Q10.physical_resource_management.v1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.output_dir = self.root / "physical_resources"
        self.state_path = self.output_dir / "physical_resource_management.json"
        self.latest_path = self.output_dir / "latest_physical_resource_management.json"
        self.history_path = self.output_dir / "physical_resource_management_history.jsonl"

    def _load_context(self) -> Dict[str, Dict[str, Any]]:
        return {
            "q1": _safe_read_json(self.root / "physical_ecology" / "latest_physical_infrastructure_registry.json"),
            "q2": _safe_read_json(self.root / "physical_ecology" / "latest_hardware_health_monitor.json"),
            "q3": _safe_read_json(self.root / "physical_sensors" / "latest_distributed_sensor_expansion_manager.json"),
            "q4": _safe_read_json(self.root / "physical_actuators" / "latest_real_actuator_control_layer.json"),
            "q5": _safe_read_json(self.root / "physical_safety" / "latest_physical_safety_supervisor.json"),
            "q6": _safe_read_json(self.root / "physical_experiments" / "latest_autonomous_physical_experiment_runner.json"),
            "q7": _safe_read_json(self.root / "physical_interventions" / "latest_environmental_intervention_tracker.json"),
            "q8": _safe_read_json(self.root / "physical_feedback" / "latest_persistent_physical_feedback_loop.json"),
            "q9": _safe_read_json(self.root / "physical_multisite" / "latest_multi_site_physical_ecology.json"),
        }

    def _normalize_inputs(self, inputs: Any) -> Dict[str, Any]:
        if isinstance(inputs, dict):
            return dict(inputs)
        return {}

    def _compute_resource_metrics(self, context: Dict[str, Dict[str, Any]], inputs: Dict[str, Any]) -> Dict[str, Any]:
        q1 = context["q1"]
        q2 = context["q2"]
        q8 = context["q8"]
        q9 = context["q9"]

        cpu_pressure = _clamp(inputs.get("cpu_utilization_index", q2.get("cpu", {}).get("cpu_load_ratio", 0.45)))
        memory_pressure = _clamp(inputs.get("memory_utilization_index", q2.get("memory", {}).get("memory_used_ratio", _memory_used_ratio_macos())))
        storage_pressure = _clamp(inputs.get("storage_utilization_index", _disk_usage_ratio(self.root)))
        bandwidth_pressure = _clamp(inputs.get("bandwidth_utilization_index", 0.30 + 0.12 * _clamp(q9.get("physical_site_count", 1) / 4.0)))
        energy_pressure = _clamp(inputs.get("energy_utilization_index", 0.35 + 0.15 * _clamp(q1.get("physical_node_count", 1) / 5.0)))

        hardware_health = _clamp(q2.get("hardware_health_index", 0.75))
        feedback_stability = _clamp(q8.get("feedback_stability_index", 0.75))
        multi_site_readiness = _clamp(q9.get("multi_site_readiness_index", 0.5))
        site_availability = _clamp(q9.get("site_availability_index", 0.5))
        distributed_coverage = _clamp(q9.get("distributed_physical_coverage", 0.5))

        physical_resource_utilization = _clamp(
            mean([cpu_pressure, memory_pressure, storage_pressure, bandwidth_pressure, energy_pressure])
        )

        resource_pressure_index = _clamp(
            0.26 * cpu_pressure
            + 0.22 * memory_pressure
            + 0.20 * storage_pressure
            + 0.16 * bandwidth_pressure
            + 0.16 * energy_pressure
        )

        energy_efficiency_index = _clamp(
            1.0
            - (0.58 * energy_pressure)
            + (0.18 * feedback_stability)
            + (0.14 * hardware_health)
            + (0.10 * site_availability)
        )

        storage_resilience = _clamp(1.0 - storage_pressure)
        bandwidth_resilience = _clamp(1.0 - bandwidth_pressure)
        compute_resilience = _clamp(1.0 - mean([cpu_pressure, memory_pressure]))

        resource_resilience_score = _clamp(
            0.22 * storage_resilience
            + 0.18 * bandwidth_resilience
            + 0.18 * compute_resilience
            + 0.16 * hardware_health
            + 0.14 * multi_site_readiness
            + 0.12 * distributed_coverage
        )

        resource_governance_score = _clamp(
            0.35 * resource_resilience_score
            + 0.25 * energy_efficiency_index
            + 0.20 * (1.0 - resource_pressure_index)
            + 0.20 * feedback_stability
        )

        return {
            "cpu_utilization_index": round(cpu_pressure, 6),
            "memory_utilization_index": round(memory_pressure, 6),
            "storage_utilization_index": round(storage_pressure, 6),
            "bandwidth_utilization_index": round(bandwidth_pressure, 6),
            "energy_utilization_index": round(energy_pressure, 6),
            "physical_resource_utilization": round(physical_resource_utilization, 6),
            "resource_pressure_index": round(resource_pressure_index, 6),
            "energy_efficiency_index": round(energy_efficiency_index, 6),
            "resource_resilience_score": round(resource_resilience_score, 6),
            "resource_governance_score": round(resource_governance_score, 6),
            "storage_resilience_score": round(storage_resilience, 6),
            "bandwidth_resilience_score": round(bandwidth_resilience, 6),
            "compute_resilience_score": round(compute_resilience, 6),
        }

    def _policy(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        pressure = _clamp(metrics.get("resource_pressure_index", 0.0))
        storage = _clamp(metrics.get("storage_utilization_index", 0.0))
        bandwidth = _clamp(metrics.get("bandwidth_utilization_index", 0.0))
        energy = _clamp(metrics.get("energy_utilization_index", 0.0))
        compute = _clamp(mean([
            metrics.get("cpu_utilization_index", 0.0),
            metrics.get("memory_utilization_index", 0.0),
        ]))

        constraints: List[str] = []
        if storage >= 0.80:
            constraints.append("storage_quota_required")
        if bandwidth >= 0.75:
            constraints.append("bandwidth_throttling_required")
        if energy >= 0.75:
            constraints.append("energy_saving_mode_required")
        if compute >= 0.80:
            constraints.append("compute_load_shedding_required")
        if pressure >= 0.75:
            constraints.append("physical_resource_pressure_high")

        if pressure >= 0.85:
            mode = "critical_conservation"
        elif pressure >= 0.65:
            mode = "constrained_optimization"
        elif pressure >= 0.40:
            mode = "balanced_allocation"
        else:
            mode = "expansion_allowed"

        return {
            "resource_management_mode": mode,
            "resource_constraints": constraints,
            "resource_expansion_allowed": mode in {"balanced_allocation", "expansion_allowed"} and not constraints,
            "local_storage_quota_preserved": True,
            "recommendations": self._recommendations(metrics, mode, constraints),
        }

    def _recommendations(self, metrics: Dict[str, Any], mode: str, constraints: List[str]) -> List[str]:
        recommendations: List[str] = []
        if "storage_quota_required" in constraints:
            recommendations.append("Preserve local disk by enforcing storage quotas and externalizing large archives.")
        if "bandwidth_throttling_required" in constraints:
            recommendations.append("Throttle non-critical synchronization until bandwidth pressure decreases.")
        if "energy_saving_mode_required" in constraints:
            recommendations.append("Prefer low-frequency sensing and dry-run physical cycles to preserve energy.")
        if "compute_load_shedding_required" in constraints:
            recommendations.append("Reduce background simulations and postpone non-critical validation runs.")
        if mode == "expansion_allowed":
            recommendations.append("Resource envelope supports continued physical ecology expansion.")
        if not recommendations:
            recommendations.append("Maintain balanced physical resource allocation and continue monitoring.")
        return recommendations

    def step(self, inputs: Any = None, persist: bool = True) -> Dict[str, Any]:
        normalized_inputs = self._normalize_inputs(inputs)
        context = self._load_context()
        metrics = self._compute_resource_metrics(context, normalized_inputs)
        policy = self._policy(metrics)

        integrations = {
            "q1_registry_integrated": bool(context["q1"]),
            "q2_health_integrated": bool(context["q2"]),
            "q3_sensor_expansion_integrated": bool(context["q3"]),
            "q4_control_integrated": bool(context["q4"]),
            "q5_safety_integrated": bool(context["q5"]),
            "q6_experiment_integrated": bool(context["q6"]),
            "q7_intervention_integrated": bool(context["q7"]),
            "q8_feedback_integrated": bool(context["q8"]),
            "q9_multisite_integrated": bool(context["q9"]),
        }
        integration_score = _clamp(sum(1 for value in integrations.values() if value) / len(integrations))

        alert_required = (
            metrics["resource_pressure_index"] >= 0.75
            or metrics["storage_utilization_index"] >= 0.85
            or metrics["energy_utilization_index"] >= 0.85
        )

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": self.schema_version,
            **integrations,
            "physical_resource_cycles": _history_count(self.history_path) + (1 if persist else 0),
            "integration_score": round(integration_score, 6),
            **metrics,
            **policy,
            "alert_required": alert_required,
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "local_storage_quota_required_until_external_storage_reliable": True,
                "resource_expansion_must_preserve_future_openness": True,
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

    def _persist(self, result: Dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.state_path.write_text(payload + "\n", encoding="utf-8")
        self.latest_path.write_text(payload + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        result["history_written"] = True
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.state_path.write_text(payload + "\n", encoding="utf-8")
        self.latest_path.write_text(payload + "\n", encoding="utf-8")


__all__ = ["PhysicalResourceManagement"]
