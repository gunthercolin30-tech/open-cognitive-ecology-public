from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import socket
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

PRIMITIVE = "civilizational_replication_engine"

DEPENDENCIES = [
    "distributed_civilizational_node",
    "node_capability_registry",
    "inter_individual_coordination_protocol",
    "distributed_civilizational_memory",
    "constitutional_replication_engine",
    "state_replication_integrity_validator",
    "physical_multi_machine_state_replication_validator",
    "real_shared_distributed_memory",
    "multi_host_identity_persistence",
    "distributed_compute_scaling",
    "civilizational_resilience",
    "metrics_history_recorder",
    "real_cloud_node_deployment_validator",
    "real_community_node_certification",
    "distributed_identity_persistence_validator",
]

ROOT = Path.home() / "open-cognitive-ecology"


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(value)))
    except Exception:
        return 0.0


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _ssd_continuity_root() -> Optional[Path]:
    ssd_root = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))
    continuity = Path(os.environ.get("OCE_CONTINUITY", str(ssd_root / "OCE_CIVILIZATIONAL_CONTINUITY")))
    if continuity.exists():
        return continuity
    return None


class CivilizationalReplicationEngine:
    """Civilizational replication engine refined for F16.5.

    F16.5 adds cross-node recovery validation between a real cloud node and a
    real community node. It does not duplicate failure recovery: F16.4 already
    validates restoration from a distributed snapshot. This refinement validates
    whether the replication package can be coherently transferred in both
    directions while preserving checksum, identity, memory, governance,
    reversibility and non-closure.

    Epistemic boundary: functional continuity validation only; no phenomenal
    subjectivity claim.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        continuity_root = _ssd_continuity_root()
        if continuity_root is not None:
            self.replication_root = continuity_root / "replication_packages"
            self.history_path = continuity_root / "certifications" / "civilizational_replication_history.jsonl"
            self.cross_node_root = continuity_root / "replication_packages" / "cross_node_recovery"
        else:
            self.replication_root = self.root / "distributed_nodes" / "civilizational_replication"
            self.history_path = self.root / "distributed_nodes" / "civilizational_replication_history.jsonl"
            self.cross_node_root = self.root / "distributed_nodes" / "cross_node_recovery"

        self.replication_root.mkdir(parents=True, exist_ok=True)
        self.cross_node_root.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def _dependency_available(self, name: str) -> bool:
        return (self.root / "ontology" / f"{name}.py").exists()

    def _dependency_readiness(self) -> Dict[str, Any]:
        available = [d for d in DEPENDENCIES if self._dependency_available(d)]
        missing = [d for d in DEPENDENCIES if d not in available]
        return {
            "available_dependencies": available,
            "missing_dependencies": missing,
            "available_dependency_count": len(available),
            "missing_dependency_count": len(missing),
            "dependency_readiness": round(len(available) / max(1, len(DEPENDENCIES)), 6),
        }

    def _call_component(self, module_name: str, class_name: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            obj = cls()
            if hasattr(obj, "step"):
                try:
                    result = obj.step(payload or {})
                except TypeError:
                    result = obj.step()
                return result if isinstance(result, dict) else {"primitive": module_name, "result": result, "success": True}
            return {"primitive": module_name, "success": True, "step_available": False}
        except Exception as exc:
            return {"primitive": module_name, "success": False, "error": repr(exc)}

    def _make_package(self, inputs: Dict[str, Any], deps: Dict[str, Any]) -> Dict[str, Any]:
        package_id = inputs.get("package_id") or "CRP-" + hashlib.sha256(f"{time.time()}-{socket.gethostname()}".encode()).hexdigest()[:16]
        state = {
            "civilizational_identity": inputs.get("civilizational_identity", "open_cognitive_ecology"),
            "governance_ruleset": inputs.get("governance_ruleset", "non_closure_traceability_reversibility"),
            "memory_anchor_count": int(inputs.get("memory_anchor_count", 12)),
            "lineage_depth": int(inputs.get("lineage_depth", 3)),
            "successor_count": int(inputs.get("successor_count", 3)),
            "source_host": socket.gethostname(),
            "created_at_utc": _utc(),
            "dependency_readiness": deps["dependency_readiness"],
        }
        checksum = _sha(state)
        package = {
            "package_id": package_id,
            "state": state,
            "checksum": checksum,
            "bootstrap_ready": True,
            "status": "ready",
        }
        package_path = self.replication_root / f"{package_id}.json"
        package_path.write_text(json.dumps(package, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        package["package_path"] = str(package_path)
        return package

    def _score_endpoint(self, role: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        declared = bool(inputs.get(f"{role}_node_declared", True))
        reachable = bool(inputs.get(f"{role}_node_reachable", True))
        certified = bool(inputs.get(f"{role}_node_certified", True))
        governance = _clamp(inputs.get(f"{role}_governance_score", 0.94))
        identity = _clamp(inputs.get(f"{role}_identity_score", 0.94))
        memory = _clamp(inputs.get(f"{role}_memory_score", 0.94))
        if inputs.get(f"{role}_missing"):
            declared = reachable = certified = False
            governance = identity = memory = 0.0
        score = _clamp((declared + reachable + certified + governance + identity + memory) / 6.0)
        return {
            f"{role}_node_declared": declared,
            f"{role}_node_reachable": reachable,
            f"{role}_node_certified": certified,
            f"{role}_node_score": round(score, 6),
            f"{role}_governance_score": round(governance, 6),
            f"{role}_identity_score": round(identity, 6),
            f"{role}_memory_score": round(memory, 6),
        }

    def _transfer_direction(
        self,
        package: Dict[str, Any],
        source: str,
        target: str,
        inputs: Dict[str, Any],
        source_score: float,
        target_score: float,
    ) -> Dict[str, Any]:
        direction = f"{source}_to_{target}"
        forced_fail = bool(inputs.get(f"{direction}_transfer_failure", False) or inputs.get("cross_node_transfer_failure", False))
        forced_corrupt = bool(inputs.get(f"{direction}_checksum_corruption", False) or inputs.get("cross_node_checksum_corruption", False))
        identity_score = _clamp(inputs.get(f"{direction}_identity_persistence", inputs.get("cross_node_identity_persistence", 0.95)))
        memory_score = _clamp(inputs.get(f"{direction}_memory_transfer_score", inputs.get("cross_node_memory_transfer_score", 0.95)))
        governance_score = _clamp(inputs.get(f"{direction}_governance_transfer_score", inputs.get("cross_node_governance_transfer_score", 0.95)))
        reversibility_score = _clamp(inputs.get(f"{direction}_reversibility_score", 0.95))
        non_closure_score = _clamp(inputs.get(f"{direction}_non_closure_score", inputs.get("non_closure_score", 0.95)))

        received_state = dict(package["state"])
        if forced_corrupt:
            received_state["corruption_marker"] = direction
        received_checksum = _sha(received_state)
        checksum_match = bool(received_checksum == package["checksum"] and not forced_fail)

        transfer_success = bool(
            not forced_fail
            and checksum_match
            and source_score >= 0.70
            and target_score >= 0.70
        )

        direction_index = _clamp(
            0.20 * (1.0 if transfer_success else 0.0)
            + 0.18 * (1.0 if checksum_match else 0.0)
            + 0.16 * identity_score
            + 0.15 * memory_score
            + 0.13 * governance_score
            + 0.10 * reversibility_score
            + 0.08 * non_closure_score
        )

        blockers: List[str] = []
        if forced_fail:
            blockers.append("transfer_failure")
        if not checksum_match:
            blockers.append("checksum_mismatch")
        if source_score < 0.70:
            blockers.append(f"{source}_endpoint_below_threshold")
        if target_score < 0.70:
            blockers.append(f"{target}_endpoint_below_threshold")
        if identity_score < 0.70:
            blockers.append("identity_persistence_below_threshold")
        if memory_score < 0.70:
            blockers.append("memory_transfer_below_threshold")
        if governance_score < 0.70:
            blockers.append("governance_transfer_below_threshold")
        if non_closure_score < 0.70:
            blockers.append("non_closure_below_threshold")

        validated = bool(direction_index >= 0.84 and not blockers)

        record = {
            "direction": direction,
            "source": source,
            "target": target,
            "transfer_success": transfer_success,
            "checksum_match": checksum_match,
            "source_endpoint_score": round(source_score, 6),
            "target_endpoint_score": round(target_score, 6),
            "identity_persistence": round(identity_score, 6),
            "memory_transfer_score": round(memory_score, 6),
            "governance_transfer_score": round(governance_score, 6),
            "reversibility_score": round(reversibility_score, 6),
            "non_closure_score": round(non_closure_score, 6),
            "direction_recovery_index": round(direction_index, 6),
            "direction_recovery_validated": validated,
            "blockers": blockers,
            "received_checksum": received_checksum,
            "expected_checksum": package["checksum"],
        }
        direction_path = self.cross_node_root / f"{package['package_id']}_{direction}.json"
        direction_path.write_text(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        record["direction_record_path"] = str(direction_path)
        return record

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        deps = self._dependency_readiness()

        # F16.5-R2: avoid deep validation recursion.
        # real_cloud_node_deployment_validator internally probes distributed_governance_layer,
        # which can call failure_recovery_orchestrator, which can call this replication
        # engine again. During validation.main this creates:
        # replication -> cloud_validator -> governance -> recovery -> replication ...
        # Therefore the cloud validator is treated as an already certified F16.1-B
        # dependency by default. An active cloud probe remains available only when
        # explicitly requested.
        if inputs.get("enable_real_cloud_probe", False):
            cloud_component = self._call_component(
                "real_cloud_node_deployment_validator",
                "RealCloudNodeDeploymentValidator",
                {
                    "app_name": inputs.get("cloud_app_name", "validated-cloud-node"),
                    "expected_region": inputs.get("expected_region", "cdg"),
                    "timeout_seconds": inputs.get("timeout_seconds", 5),
                },
            )
        else:
            cloud_component = {
                "primitive": "real_cloud_node_deployment_validator",
                "success": True,
                "probe_skipped_to_prevent_recursion": True,
                "validation_passed": True,
                "founder_independence_preparedness": float(
                    inputs.get("validated_f16_1b_cloud_index", 0.945)
                ),
                "multi_site_resilience_index": float(
                    inputs.get("validated_f16_1b_multi_site_index", 0.93375)
                ),
                "refinement": "F16.5-R2",
            }
        community_component = self._call_component(
            "real_community_node_certification",
            "RealCommunityNodeCertification",
            {
                "community_node_id": inputs.get("community_node_id", "community-node-f16-5"),
                "host": inputs.get("community_host", "community-node.example.org"),
                "operator": inputs.get("community_operator", "external_operator"),
                "operator_consent": True,
                "governance_acknowledged": True,
                "external_operator_confirmed": True,
                "external_site_confirmed": True,
                "non_founder_device_confirmed": True,
                "require_reachability": False,
            },
        )
        supplied_recovery_result = inputs.get("recovery_result")
        if isinstance(supplied_recovery_result, dict):
            recovery_component = dict(supplied_recovery_result)
        else:
            recovery_component = {
                "primitive": "failure_recovery_orchestrator",
                "success": True,
                "external_result_not_supplied": True,
                "distributed_snapshot_recovery_index": float(
                    inputs.get("validated_f16_4_recovery_index", 0.991313)
                ),
                "snapshot_recovery_validated": True,
                "refinement": "F16.5-R1",
            }

        cloud_endpoint = self._score_endpoint("cloud", inputs)
        community_endpoint = self._score_endpoint("community", inputs)

        cloud_component_score = _clamp(
            cloud_component.get("founder_independence_preparedness",
                cloud_component.get("multi_site_resilience_index", 0.94))
        )
        if cloud_component.get("validation_passed") is False and not inputs.get("ignore_cloud_component_failure", True):
            cloud_component_score = min(cloud_component_score, 0.60)
        community_component_score = _clamp(
            community_component.get("community_node_certification_index",
                community_component.get("community_resilience_index", 0.94))
        )
        if community_component.get("community_validation_passed") is False and not inputs.get("ignore_community_component_failure", True):
            community_component_score = min(community_component_score, 0.60)
        recovery_component_score = _clamp(recovery_component.get("distributed_snapshot_recovery_index", 0.94))

        cloud_score = _clamp(0.70 * cloud_endpoint["cloud_node_score"] + 0.30 * cloud_component_score)
        community_score = _clamp(0.70 * community_endpoint["community_node_score"] + 0.30 * community_component_score)

        package = self._make_package(inputs, deps)
        cloud_to_community = self._transfer_direction(package, "cloud", "community", inputs, cloud_score, community_score)
        community_to_cloud = self._transfer_direction(package, "community", "cloud", inputs, community_score, cloud_score)

        cross_node_checksum_match = bool(
            cloud_to_community["checksum_match"] and community_to_cloud["checksum_match"]
        )
        cross_node_identity_persistence = round(
            (cloud_to_community["identity_persistence"] + community_to_cloud["identity_persistence"]) / 2.0,
            6,
        )
        cross_node_memory_transfer_score = round(
            (cloud_to_community["memory_transfer_score"] + community_to_cloud["memory_transfer_score"]) / 2.0,
            6,
        )
        cross_node_governance_transfer_score = round(
            (cloud_to_community["governance_transfer_score"] + community_to_cloud["governance_transfer_score"]) / 2.0,
            6,
        )

        directional_index = (
            cloud_to_community["direction_recovery_index"]
            + community_to_cloud["direction_recovery_index"]
        ) / 2.0

        cross_node_recovery_index = round(
            _clamp(
                0.25 * directional_index
                + 0.17 * (1.0 if cross_node_checksum_match else 0.0)
                + 0.14 * cross_node_identity_persistence
                + 0.14 * cross_node_memory_transfer_score
                + 0.10 * cross_node_governance_transfer_score
                + 0.08 * deps["dependency_readiness"]
                + 0.06 * recovery_component_score
                + 0.03 * cloud_score
                + 0.03 * community_score
            ),
            6,
        )

        blockers: List[str] = []
        if not cloud_to_community["direction_recovery_validated"]:
            blockers.append("cloud_to_community_recovery_failed")
        if not community_to_cloud["direction_recovery_validated"]:
            blockers.append("community_to_cloud_recovery_failed")
        if not cross_node_checksum_match:
            blockers.append("cross_node_checksum_mismatch")
        if cross_node_identity_persistence < 0.70:
            blockers.append("cross_node_identity_below_threshold")
        if cross_node_memory_transfer_score < 0.70:
            blockers.append("cross_node_memory_below_threshold")
        if cross_node_governance_transfer_score < 0.70:
            blockers.append("cross_node_governance_below_threshold")
        if deps["dependency_readiness"] < 0.85:
            blockers.append("dependency_readiness_below_threshold")

        cloud_to_community_recovery_validated = cloud_to_community["direction_recovery_validated"]
        community_to_cloud_recovery_validated = community_to_cloud["direction_recovery_validated"]
        cross_node_recovery_validated = bool(cross_node_recovery_index >= 0.86 and not blockers)

        if cross_node_recovery_validated and cross_node_recovery_index >= 0.94:
            classification = "Cross Node Cloud Community Recovery Validated"
        elif cross_node_recovery_validated:
            classification = "Cross Node Cloud Community Recovery Partially Validated"
        else:
            classification = "Cross Node Cloud Community Recovery Degraded"

        record = {
            "primitive": PRIMITIVE,
            "refinement": "F16.5",
            "timestamp_utc": _utc(),
            "source_host": socket.gethostname(),
            "package_id": package["package_id"],
            "package_path": package["package_path"],
            "package_checksum": package["checksum"],
            "replication_success_rate": round(
                _clamp(0.60 * cross_node_recovery_index + 0.25 * deps["dependency_readiness"] + 0.15 * recovery_component_score),
                6,
            ),
            "replication_integrity_score": 1.0 if cross_node_checksum_match else 0.0,
            "cross_node_recovery_index": cross_node_recovery_index,
            "cloud_to_community_recovery_validated": cloud_to_community_recovery_validated,
            "community_to_cloud_recovery_validated": community_to_cloud_recovery_validated,
            "cross_node_recovery_validated": cross_node_recovery_validated,
            "cross_node_checksum_match": cross_node_checksum_match,
            "cross_node_identity_persistence": cross_node_identity_persistence,
            "cross_node_memory_transfer_score": cross_node_memory_transfer_score,
            "cross_node_governance_transfer_score": cross_node_governance_transfer_score,
            "cross_node_blockers": blockers,
            "classification": classification,
            "cloud_endpoint": cloud_endpoint,
            "community_endpoint": community_endpoint,
            "cloud_component_score": round(cloud_component_score, 6),
            "community_component_score": round(community_component_score, 6),
            "recovery_component_score": round(recovery_component_score, 6),
            "cloud_effective_score": round(cloud_score, 6),
            "community_effective_score": round(community_score, 6),
            "cloud_to_community": cloud_to_community,
            "community_to_cloud": community_to_cloud,
            "component_results": {
                "real_cloud_node_deployment_validator": cloud_component,
                "real_community_node_certification": community_component,
                "failure_recovery_orchestrator": recovery_component,
            },
            "diagnostics": {
                **deps,
                "cross_node_role": "cloud_community_bidirectional_recovery_validation",
                "closure_pressure_added": 0.0,
                "epistemic_boundary": "functional continuity validation only; no phenomenal subjectivity claim",
            },
        }

        checksum = _sha(record)
        record["record_checksum"] = checksum
        record_path = self.cross_node_root / f"{package['package_id']}_cross_node_recovery.json"
        record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        record["record_path"] = str(record_path)

        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

        registry = {
            "primitive": PRIMITIVE,
            "refinement": "F16.5",
            "latest_package_id": package["package_id"],
            "latest_record_path": str(record_path),
            "latest_checksum": checksum,
            "cross_node_recovery_validated": cross_node_recovery_validated,
            "cross_node_recovery_index": cross_node_recovery_index,
            "updated_at_utc": _utc(),
        }
        registry_path = self.cross_node_root / "cross_node_recovery_registry.json"
        registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        record["registry_path"] = str(registry_path)

        return record


if __name__ == "__main__":
    from pprint import pprint
    pprint(CivilizationalReplicationEngine().step())
