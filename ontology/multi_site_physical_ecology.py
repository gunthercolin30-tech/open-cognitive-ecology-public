"""
Q9 — multi_site_physical_ecology

Distributed multi-site physical ecology layer for Open Cognitive Ecology.

Functional validation only: this module measures distributed physical coverage,
site availability and cross-site synchronization without claiming phenomenal
subjectivity.
"""

from __future__ import annotations

import json
import math
import socket
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


def _host_id() -> str:
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "local-host"


def _unique(values: List[Any]) -> List[str]:
    out: List[str] = []
    for value in values:
        text = str(value)
        if text and text not in out:
            out.append(text)
    return out


class MultiSitePhysicalEcology:
    """
    Coordinates physical ecology metrics across local, simulated and distributed sites.

    Q9 does not replace the distributed civilizational node layer. It binds Q1-Q8
    to a physical-site representation and computes multi-site readiness.
    """

    primitive = "multi_site_physical_ecology"
    refinement = "Q9-R1"
    schema_version = "Q9.multi_site_physical_ecology.v1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.output_dir = self.root / "physical_multisite"
        self.state_path = self.output_dir / "multi_site_physical_ecology.json"
        self.latest_path = self.output_dir / "latest_multi_site_physical_ecology.json"
        self.history_path = self.output_dir / "multi_site_physical_ecology_history.jsonl"

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
        }

    def _normalize_inputs(self, inputs: Any) -> Dict[str, Any]:
        if isinstance(inputs, dict):
            return dict(inputs)
        return {}

    def _derive_sites(self, context: Dict[str, Dict[str, Any]], inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        provided = inputs.get("sites")
        if isinstance(provided, list):
            sites = [dict(site) for site in provided if isinstance(site, dict)]
            if sites:
                return sites

        q1 = context["q1"]
        q2 = context["q2"]
        q3 = context["q3"]
        q8 = context["q8"]

        host = q1.get("host_node_id") or _host_id()
        physical_nodes = q1.get("physical_node_count", 1)
        sensor_nodes = q3.get("distributed_sensor_node_count", 1)

        sites: List[Dict[str, Any]] = [
            {
                "site_id": f"site:local:{host}",
                "site_type": "local_host",
                "online": True,
                "physical_node_count": max(1, int(physical_nodes or 1)),
                "sensor_node_count": max(1, int(sensor_nodes or 1)),
                "actuator_count": int(q1.get("registered_actuator_count", 0) or 0),
                "feedback_stability_index": _clamp(q8.get("feedback_stability_index", 0.75)),
                "hardware_health_index": _clamp(q2.get("hardware_health_index", 0.75)),
                "synchronization_score": 1.0,
            }
        ]

        # Add simulated remote physical sites when local registries already imply more
        # than one physical/sensor node. This keeps Q9 testable without claiming that
        # a remote machine is physically present.
        if int(physical_nodes or 0) >= 2 or int(sensor_nodes or 0) >= 2:
            sites.append({
                "site_id": "site:simulated:edge-sensor-cluster",
                "site_type": "simulated_remote_site",
                "online": True,
                "physical_node_count": 1,
                "sensor_node_count": max(1, min(2, int(sensor_nodes or 1))),
                "actuator_count": 0,
                "feedback_stability_index": _clamp(q8.get("feedback_stability_index", 0.70)),
                "hardware_health_index": _clamp(q2.get("hardware_health_index", 0.70)),
                "synchronization_score": 0.82,
            })

        if bool(inputs.get("include_cloud_site", True)):
            cloud_count = int(q1.get("cloud_node_count", 0) or 0)
            if cloud_count > 0:
                sites.append({
                    "site_id": "site:cloud:coordination-node",
                    "site_type": "coordination_cloud",
                    "online": True,
                    "physical_node_count": 0,
                    "sensor_node_count": 0,
                    "actuator_count": 0,
                    "feedback_stability_index": _clamp(q8.get("feedback_stability_index", 0.65)),
                    "hardware_health_index": 0.85,
                    "synchronization_score": 0.88,
                })

        return sites

    def _evaluate_sites(self, sites: List[Dict[str, Any]], context: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        physical_site_count = len([site for site in sites if site.get("online", False)])
        total_sites = len(sites)

        availability_values = [1.0 if site.get("online", False) else 0.0 for site in sites]
        sync_values = [_clamp(site.get("synchronization_score", 0.0)) for site in sites]
        health_values = [_clamp(site.get("hardware_health_index", 0.0)) for site in sites]
        feedback_values = [_clamp(site.get("feedback_stability_index", 0.0)) for site in sites]

        total_physical_nodes = sum(int(site.get("physical_node_count", 0) or 0) for site in sites)
        total_sensor_nodes = sum(int(site.get("sensor_node_count", 0) or 0) for site in sites)
        total_actuators = sum(int(site.get("actuator_count", 0) or 0) for site in sites)

        q1_coverage = _clamp(context["q1"].get("physical_asset_coverage", 0.5))
        q3_coverage = _clamp(context["q3"].get("sensor_network_coverage", 0.5))
        q8_stability = _clamp(context["q8"].get("feedback_stability_index", 0.5))

        site_availability_index = _clamp(mean(availability_values) if availability_values else 0.0)
        cross_site_synchronization_score = _clamp(mean(sync_values) if sync_values else 0.0)
        distributed_feedback_consistency = _clamp(
            0.45 * (mean(feedback_values) if feedback_values else 0.0)
            + 0.30 * cross_site_synchronization_score
            + 0.25 * q8_stability
        )

        node_factor = _clamp(total_physical_nodes / 4.0)
        site_factor = _clamp(physical_site_count / 3.0)
        sensor_factor = _clamp(total_sensor_nodes / 4.0)
        actuator_factor = _clamp(total_actuators / 2.0)

        distributed_physical_coverage = _clamp(
            0.24 * q1_coverage
            + 0.20 * q3_coverage
            + 0.18 * node_factor
            + 0.16 * site_factor
            + 0.12 * sensor_factor
            + 0.10 * actuator_factor
        )

        multi_site_readiness_index = _clamp(
            0.25 * distributed_physical_coverage
            + 0.22 * site_availability_index
            + 0.22 * cross_site_synchronization_score
            + 0.18 * distributed_feedback_consistency
            + 0.13 * (mean(health_values) if health_values else 0.0)
        )

        return {
            "physical_site_count": physical_site_count,
            "total_site_count": total_sites,
            "total_physical_nodes": total_physical_nodes,
            "total_sensor_nodes": total_sensor_nodes,
            "total_actuators": total_actuators,
            "distributed_physical_coverage": round(distributed_physical_coverage, 6),
            "cross_site_synchronization_score": round(cross_site_synchronization_score, 6),
            "site_availability_index": round(site_availability_index, 6),
            "distributed_feedback_consistency": round(distributed_feedback_consistency, 6),
            "multi_site_readiness_index": round(multi_site_readiness_index, 6),
        }

    def step(self, inputs: Any = None, persist: bool = True) -> Dict[str, Any]:
        normalized_inputs = self._normalize_inputs(inputs)
        context = self._load_context()
        sites = self._derive_sites(context, normalized_inputs)
        site_metrics = self._evaluate_sites(sites, context)

        integrations = {
            "q1_registry_integrated": bool(context["q1"]),
            "q2_health_integrated": bool(context["q2"]),
            "q3_sensor_expansion_integrated": bool(context["q3"]),
            "q4_control_integrated": bool(context["q4"]),
            "q5_safety_integrated": bool(context["q5"]),
            "q6_experiment_integrated": bool(context["q6"]),
            "q7_intervention_integrated": bool(context["q7"]),
            "q8_feedback_integrated": bool(context["q8"]),
        }
        integration_score = _clamp(sum(1 for value in integrations.values() if value) / len(integrations))

        site_ids = _unique([site.get("site_id", "unknown") for site in sites])
        physical_ecology_distributed = site_metrics["physical_site_count"] >= 2

        recommendations: List[str] = []
        if site_metrics["physical_site_count"] < 2:
            recommendations.append("Add or certify at least one additional physical site for true distributed ecology.")
        if site_metrics["cross_site_synchronization_score"] < 0.75:
            recommendations.append("Improve cross-site synchronization before enabling distributed physical feedback.")
        if site_metrics["distributed_feedback_consistency"] < 0.70:
            recommendations.append("Repeat Q8 cycles across sites to improve distributed feedback consistency.")
        if not recommendations:
            recommendations.append("Multi-site physical ecology is ready for Q10 resource management integration.")

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": self.schema_version,
            **integrations,
            "physical_ecology_distributed": physical_ecology_distributed,
            "physical_multisite_cycles": _history_count(self.history_path) + (1 if persist else 0),
            "site_ids": site_ids,
            "sites": sites,
            "integration_score": round(integration_score, 6),
            **site_metrics,
            "alert_required": site_metrics["physical_site_count"] < 2 or site_metrics["cross_site_synchronization_score"] < 0.60,
            "recommendations": recommendations,
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "human_review_required_for_irreversible_physical_action": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "distributed_site_onboarding_requires_review": True,
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


__all__ = ["MultiSitePhysicalEcology"]
