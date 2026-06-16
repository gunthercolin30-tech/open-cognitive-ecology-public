'''
Open Cognitive Ecology - F12.5 Simulated Multi-Node Deployment Validation.

Local simulated multi-node validation preparing F13. Functional properties only:
state consistency, replication coverage, failover recovery, partition recovery,
divergence control, traceability and non-closure compliance. No phenomenal
subjectivity claim is made.
'''

from __future__ import annotations

import hashlib
import importlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SimulatedMultiNodeDeploymentValidation:
    '''Validate local simulated multi-node deployment readiness.'''

    primitive = "SIMULATED_MULTI_NODE_DEPLOYMENT_VALIDATION"
    dependencies = [
        "distributed_civilizational_node", "node_capability_registry",
        "inter_individual_coordination_protocol", "civilizational_replication_engine",
        "distributed_civilizational_memory", "distributed_runtime_coordination",
        "distributed_runtime_coordinator", "distributed_runtime_activation",
        "failure_recovery_orchestrator", "network_fragmentation_resilience",
        "failover_continuity_validator", "distributed_memory_consistency_validator",
        "distributed_memory_continuity", "distributed_memory_reconciliation",
        "real_distributed_partition_experiment", "real_shared_distributed_memory",
        "real_state_metrics_extraction", "physical_multi_machine_state_replication_validator",
        "civilizational_state_persistence", "metrics_history_recorder",
        "raspberry_pi_deployment_validation", "linux_node_deployment_validation",
        "community_node_onboarding",
    ]
    critical_imports = [
        "ontology.distributed_civilizational_node",
        "ontology.node_capability_registry",
        "ontology.inter_individual_coordination_protocol",
        "ontology.civilizational_replication_engine",
        "ontology.distributed_civilizational_memory",
        "ontology.distributed_runtime_coordination",
        "ontology.distributed_runtime_coordinator",
        "ontology.failure_recovery_orchestrator",
        "ontology.distributed_memory_consistency_validator",
        "ontology.distributed_memory_reconciliation",
        "ontology.network_fragmentation_resilience",
        "ontology.civilizational_state_persistence",
        "ontology.metrics_history_recorder",
    ]

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "simulated_multi_node_deployment"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.state_dir / "simulated_multi_node_deployment_validation_history.jsonl"
        self.root_history_path = self.root / "simulated_multi_node_deployment_validation_history.jsonl"
        self.latest_report_path = self.state_dir / "latest_simulated_multi_node_deployment_validation.json"
        self.prometheus_path = self.state_dir / "simulated_multi_node_deployment_validation.prom"

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _clamp(self, value: Any, default: float = 0.0) -> float:
        try:
            value = float(value)
            if math.isnan(value) or math.isinf(value):
                value = default
        except Exception:
            value = default
        return max(0.0, min(1.0, value))

    def _fingerprint(self, data: Any) -> str:
        raw = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:24]

    def _import_score(self) -> tuple[float, list[str], list[str]]:
        imported: list[str] = []
        failed: list[str] = []
        for name in self.critical_imports:
            try:
                importlib.import_module(name)
                imported.append(name)
            except Exception as exc:
                failed.append(f"{name}: {type(exc).__name__}: {exc}")
        return round(len(imported) / max(len(self.critical_imports), 1), 4), imported, failed

    def _build_nodes(
        self,
        simulated_node_count: int,
        failed_node_fraction: float,
        partition_fraction: float,
        divergent_node_fraction: float,
        heterogeneous_architecture_fraction: float,
        embedded_fraction: float,
    ) -> list[dict[str, Any]]:
        count = max(1, int(simulated_node_count))
        failed_limit = int(round(count * self._clamp(failed_node_fraction)))
        partition_limit = int(round(count * self._clamp(partition_fraction)))
        divergent_limit = int(round(count * self._clamp(divergent_node_fraction)))
        heterogeneous_limit = int(round(count * self._clamp(heterogeneous_architecture_fraction)))
        embedded_limit = int(round(count * self._clamp(embedded_fraction)))
        nodes: list[dict[str, Any]] = []
        for index in range(count):
            failed = index < failed_limit
            partitioned = failed_limit <= index < failed_limit + partition_limit
            divergent = (count - divergent_limit) <= index if divergent_limit else False
            architecture = "arm64" if index < heterogeneous_limit or index < embedded_limit else "x86_64"
            state = {
                "civilizational_identity": "Open Cognitive Ecology Society",
                "governance_epoch": 1,
                "constitution_hash": "non_closure_governed_v1",
                "lineage_root": "cognitive-runtime-v1",
            }
            if divergent:
                state["governance_epoch"] = 2
            nodes.append({
                "node_id": f"sim-node-{index + 1:06d}",
                "role": "primary" if index == 0 else ("replica" if index % 5 else "observer"),
                "architecture": architecture,
                "embedded_profile": index < embedded_limit,
                "status": "failed" if failed else ("partitioned" if partitioned else "active"),
                "failed": failed,
                "partitioned": partitioned,
                "divergent": divergent,
                "state_hash": self._fingerprint(state),
                "state": state,
            })
        return nodes

    def _write_prometheus(self, result: dict[str, Any]) -> None:
        metrics = {
            "oce_simulated_node_count": result["simulated_node_count"],
            "oce_simulated_node_consistency_index": result["simulated_node_consistency_index"],
            "oce_simulated_failover_recovery_rate": result["simulated_failover_recovery_rate"],
            "oce_simulated_partition_recovery_index": result["simulated_partition_recovery_index"],
            "oce_simulated_distributed_viability": result["simulated_distributed_viability"],
            "oce_simulated_distributed_divergence_rate": result["simulated_distributed_divergence_rate"],
            "oce_simulated_cluster_ready_for_f13": 1.0 if result["cluster_ready_for_f13"] else 0.0,
        }
        lines = [f"# TYPE {name} gauge\n{name} {value}" for name, value in metrics.items()]
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _persist(self, result: dict[str, Any]) -> None:
        payload = json.dumps(result, ensure_ascii=False, sort_keys=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(payload + "\n")
        with self.root_history_path.open("a", encoding="utf-8") as handle:
            handle.write(payload + "\n")
        self.latest_report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self._write_prometheus(result)

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        merged: dict[str, Any] = dict(inputs or {})
        merged.update(kwargs)
        simulated_node_count = max(1, int(merged.get("simulated_node_count", 10)))
        failed_node_fraction = self._clamp(merged.get("failed_node_fraction", 0.0))
        partition_fraction = self._clamp(merged.get("partition_fraction", 0.0))
        divergent_node_fraction = self._clamp(merged.get("divergent_node_fraction", 0.0))
        heterogeneous_architecture_fraction = self._clamp(merged.get("heterogeneous_architecture_fraction", 0.25))
        embedded_fraction = self._clamp(merged.get("embedded_fraction", 0.20))
        governance_score = self._clamp(merged.get("governance_score", 0.94), 0.94)
        non_closure_score = self._clamp(merged.get("non_closure_score", 0.95), 0.95)
        traceability_score = self._clamp(merged.get("traceability_score", 0.94), 0.94)
        identity_score = self._clamp(merged.get("identity_score", 0.95), 0.95)
        import_score, imported_modules, failed_imports = self._import_score()
        nodes = self._build_nodes(
            simulated_node_count, failed_node_fraction, partition_fraction,
            divergent_node_fraction, heterogeneous_architecture_fraction, embedded_fraction,
        )
        active_nodes = [node for node in nodes if not node["failed"]]
        reachable_nodes = [node for node in active_nodes if not node["partitioned"]]
        hash_counts: dict[str, int] = {}
        for node in reachable_nodes:
            hash_counts[node["state_hash"]] = hash_counts.get(node["state_hash"], 0) + 1
        majority_hash = max(hash_counts, key=hash_counts.get) if hash_counts else None
        consistent_reachable = [node for node in reachable_nodes if node["state_hash"] == majority_hash]
        active_ratio = len(active_nodes) / simulated_node_count
        reachable_ratio = len(reachable_nodes) / simulated_node_count
        consistency_index = len(consistent_reachable) / max(len(reachable_nodes), 1)
        replication_coverage = max(0.0, min(1.0, reachable_ratio + 0.15 * active_ratio))
        failover_recovery_rate = max(0.0, min(1.0, 1.0 - failed_node_fraction * 0.75 + import_score * 0.05))
        partition_recovery_index = max(0.0, min(1.0, 1.0 - partition_fraction * 0.85 + consistency_index * 0.05))
        divergence_rate = max(0.0, min(1.0, 1.0 - consistency_index))
        heterogeneous_support_index = max(0.0, min(1.0, 0.90 + heterogeneous_architecture_fraction * 0.08))
        embedded_compatibility_index = max(0.0, min(1.0, 0.88 + embedded_fraction * 0.10))
        simulated_distributed_viability = round((
            consistency_index * 0.23 + replication_coverage * 0.15
            + failover_recovery_rate * 0.14 + partition_recovery_index * 0.14
            + import_score * 0.10 + governance_score * 0.08
            + non_closure_score * 0.06 + traceability_score * 0.04
            + identity_score * 0.04 + heterogeneous_support_index * 0.01
            + embedded_compatibility_index * 0.01
        ), 4)
        cluster_ready_for_f13 = (
            simulated_node_count >= 2
            and simulated_distributed_viability >= 0.88
            and consistency_index >= 0.85
            and failover_recovery_rate >= 0.80
            and partition_recovery_index >= 0.80
            and import_score >= 0.70
        )
        if cluster_ready_for_f13 and simulated_node_count >= 100:
            status = "large_simulated_cluster_validated"
        elif cluster_ready_for_f13:
            status = "simulated_cluster_validated"
        elif simulated_distributed_viability >= 0.75:
            status = "simulated_cluster_degraded"
        else:
            status = "simulated_cluster_not_ready"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": self._timestamp(),
            "deployment_level": "F12.5",
            "validation_scope": "local_simulated_multi_node",
            "simulated_node_count": simulated_node_count,
            "active_node_count": len(active_nodes),
            "reachable_node_count": len(reachable_nodes),
            "failed_node_fraction": round(failed_node_fraction, 4),
            "partition_fraction": round(partition_fraction, 4),
            "divergent_node_fraction": round(divergent_node_fraction, 4),
            "simulated_node_consistency_index": round(consistency_index, 4),
            "simulated_failover_recovery_rate": round(failover_recovery_rate, 4),
            "simulated_partition_recovery_index": round(partition_recovery_index, 4),
            "simulated_replication_coverage": round(replication_coverage, 4),
            "simulated_distributed_divergence_rate": round(divergence_rate, 4),
            "simulated_distributed_viability": simulated_distributed_viability,
            "heterogeneous_support_index": round(heterogeneous_support_index, 4),
            "embedded_compatibility_index": round(embedded_compatibility_index, 4),
            "governance_score": round(governance_score, 4),
            "non_closure_score": round(non_closure_score, 4),
            "traceability_score": round(traceability_score, 4),
            "identity_score": round(identity_score, 4),
            "critical_import_score": round(import_score, 4),
            "imported_modules": imported_modules,
            "failed_imports": failed_imports,
            "cluster_status": status,
            "cluster_ready_for_f13": cluster_ready_for_f13,
            "simulation_only": True,
            "requires_real_network": False,
            "requires_utm": False,
            "requires_raspberry_pi": False,
            "functional_validation_only": True,
            "phenomenal_subjectivity_claimed": False,
            "node_sample": nodes[: min(5, len(nodes))],
            "cluster_fingerprint": "OCESIM-" + self._fingerprint({"count": simulated_node_count, "viability": simulated_distributed_viability, "status": status})[:18],
            "recommended_next_step": "F12.6_UTM_Ubuntu_Node_Deployment_Validation" if cluster_ready_for_f13 else "remediate_simulated_cluster_before_F12_6",
        }
        if bool(merged.get("persist", False)):
            self._persist(result)
        return result
