from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

PRIMITIVE = "distributed_civilizational_memory"

DEPENDENCIES = [
    "distributed_civilizational_node",
    "node_capability_registry",
    "persistent_multi_scale_memory",
    "persistent_external_memory_fabric",
    "internet_external_memory_fabric",
    "distributed_knowledge_access",
    "civilizational_state_persistence",
    "metrics_history_recorder",
]


class DistributedCivilizationalMemory:
    """Persistent distributed civilizational memory runtime.

    This module preserves the legacy evaluate(state) interface while adding
    the F4 runtime layer: replica construction, synchronization diagnostics,
    recovery estimation, persistence, and JSONL history.
    """

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "distributed_nodes"
        self.memory_dir = self.base_dir / "civilizational_memory_replicas"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.base_dir / "distributed_civilizational_memory.json"
        self.history_path = self.base_dir / "distributed_memory_history.jsonl"

    def _bounded(self, value):
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    def _now(self):
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _read_json(self, path: Path, default):
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return default

    def _write_json(self, path: Path, payload) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            return True
        except Exception:
            return False

    def _append_jsonl(self, path: Path, payload) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
            return True
        except Exception:
            return False

    def _dependency_available_count(self) -> tuple[int, list[str]]:
        missing = []
        count = 0
        for dep in DEPENDENCIES:
            path = self.root / "ontology" / f"{dep}.py"
            if path.exists():
                count += 1
            else:
                missing.append(dep)
        return count, missing

    def _node_identity(self) -> dict:
        node_registry = self.base_dir / "node_registry.json"
        data = self._read_json(node_registry, {})
        node_id = data.get("node_id") or data.get("latest", {}).get("node_id")
        node_name = data.get("node_name") or data.get("latest", {}).get("node_name")
        if not node_id:
            node_id = "oce-node-local-fallback"
        return {"node_id": node_id, "node_name": node_name or "local"}

    def _stable_hash(self, payload) -> str:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def evaluate(self, state):
        state = state or {}
        memory_nodes = state.get("memory_nodes", [])
        if not memory_nodes:
            return {
                "distributed_retention": 0.0,
                "distributed_transmission": 0.0,
                "fragmentation_pressure": 1.0,
                "redundancy_factor": 0.0,
                "archive_integrity": 0.0,
                "distributed_memory_index": 0.0,
                "memory_viability": False,
            }

        distributed_retention = mean([self._bounded(n.get("retention", 0.0)) for n in memory_nodes])
        distributed_transmission = mean([self._bounded(n.get("transmission", 0.0)) for n in memory_nodes])
        fragmentation_pressure = self._bounded(state.get("fragmentation_pressure", 0.0))
        redundancy_factor = self._bounded(state.get("redundancy_factor", 0.0))
        archive_integrity = self._bounded(state.get("archive_integrity", 0.0))
        closure_pressure = self._bounded(state.get("closure_pressure", 0.0))
        distributed_memory_index = self._bounded((
            distributed_retention
            + distributed_transmission
            + redundancy_factor
            + archive_integrity
            + (1.0 - fragmentation_pressure)
            + (1.0 - closure_pressure)
        ) / 6.0)
        return {
            "distributed_retention": round(distributed_retention, 4),
            "distributed_transmission": round(distributed_transmission, 4),
            "fragmentation_pressure": round(fragmentation_pressure, 4),
            "redundancy_factor": round(redundancy_factor, 4),
            "archive_integrity": round(archive_integrity, 4),
            "closure_pressure": round(closure_pressure, 4),
            "distributed_memory_index": round(distributed_memory_index, 4),
            "memory_viability": distributed_memory_index >= 0.5,
        }

    def _build_default_memory_nodes(self, replica_count: int, failed: set[int], corrupt: set[int]):
        nodes = []
        for i in range(replica_count):
            failed_i = i in failed
            corrupt_i = i in corrupt
            retention = 0.0 if failed_i else (0.35 if corrupt_i else 0.88)
            transmission = 0.0 if failed_i else (0.40 if corrupt_i else 0.86)
            nodes.append({
                "replica_id": f"memory-replica-{i+1}",
                "retention": retention,
                "transmission": transmission,
                "available": not failed_i,
                "corrupt": corrupt_i,
            })
        return nodes

    def _persist_replicas(self, replicas):
        written = 0
        hashes = []
        for replica in replicas:
            rid = replica.get("replica_id", "replica")
            path = self.memory_dir / f"{rid}.json"
            payload = dict(replica)
            payload["written_at_utc"] = self._now()
            payload_hash = self._stable_hash(payload)
            payload["replica_hash"] = payload_hash
            if self._write_json(path, payload):
                written += 1
                hashes.append(payload_hash)
        return written, hashes

    def step(self, state=None):
        state = state or {}
        timestamp = self._now()
        node = self._node_identity()

        replica_count = int(state.get("replica_count", 0) or 0)
        memory_nodes = state.get("memory_nodes")
        failed = set(int(i) for i in state.get("failed_replica_indices", []))
        corrupt = set(int(i) for i in state.get("corrupt_replica_indices", []))

        if memory_nodes:
            replica_count = max(replica_count, len(memory_nodes))
            replicas = []
            for i, item in enumerate(memory_nodes):
                replica = dict(item)
                replica.setdefault("replica_id", f"memory-replica-{i+1}")
                replica.setdefault("available", i not in failed)
                replica.setdefault("corrupt", i in corrupt)
                replicas.append(replica)
        else:
            replica_count = max(replica_count, 3)
            replicas = self._build_default_memory_nodes(replica_count, failed, corrupt)
            memory_nodes = replicas

        total_replicas = max(1, len(replicas))
        available_replicas = sum(1 for r in replicas if r.get("available", True))
        healthy_replicas = sum(1 for r in replicas if r.get("available", True) and not r.get("corrupt", False))
        corrupt_replicas = sum(1 for r in replicas if r.get("corrupt", False))
        failed_replicas = total_replicas - available_replicas

        memory_replication_factor = round(float(total_replicas), 4)
        replica_health_ratio = self._bounded(healthy_replicas / total_replicas)
        availability_ratio = self._bounded(available_replicas / total_replicas)
        corruption_resistance = self._bounded(1.0 - (corrupt_replicas / total_replicas))
        failure_resistance = self._bounded(1.0 - (failed_replicas / total_replicas))

        eval_state = dict(state)
        eval_state["memory_nodes"] = memory_nodes
        eval_state.setdefault("redundancy_factor", self._bounded(min(total_replicas, 5) / 5.0))
        eval_state.setdefault("archive_integrity", replica_health_ratio)
        eval_state.setdefault("fragmentation_pressure", self._bounded(1.0 - replica_health_ratio))
        evaluation = self.evaluate(eval_state)

        written_count, hashes = self._persist_replicas(replicas)
        unique_hash_ratio = self._bounded(len(set(hashes)) / max(1, len(hashes))) if hashes else 0.0
        distributed_memory_sync_ratio = self._bounded((availability_ratio + replica_health_ratio + (1.0 - abs(1.0 - unique_hash_ratio))) / 3.0)
        memory_recovery_success_rate = self._bounded((replica_health_ratio + failure_resistance + corruption_resistance) / 3.0)
        memory_survival_probability = self._bounded((
            evaluation["distributed_memory_index"]
            + replica_health_ratio
            + availability_ratio
            + memory_recovery_success_rate
            + min(1.0, total_replicas / 3.0)
        ) / 5.0)

        dependency_count, missing_dependencies = self._dependency_available_count()
        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": timestamp,
            "node_id": node["node_id"],
            "node_name": node["node_name"],
            **evaluation,
            "replica_count": total_replicas,
            "available_replica_count": available_replicas,
            "healthy_replica_count": healthy_replicas,
            "failed_replica_count": failed_replicas,
            "corrupt_replica_count": corrupt_replicas,
            "memory_replication_factor": memory_replication_factor,
            "replica_health_ratio": round(replica_health_ratio, 4),
            "distributed_memory_sync_ratio": round(distributed_memory_sync_ratio, 4),
            "memory_recovery_success_rate": round(memory_recovery_success_rate, 4),
            "memory_survival_probability": round(memory_survival_probability, 4),
            "memory_replication_ready": total_replicas >= 2,
            "memory_recovery_ready": healthy_replicas >= 1,
            "distributed_memory_ready": memory_survival_probability >= 0.60,
            "replica_write_count": written_count,
            "registry_path": str(self.registry_path),
            "history_path": str(self.history_path),
            "replica_dir": str(self.memory_dir),
            "available_dependency_count": dependency_count,
            "missing_dependencies": missing_dependencies,
            "missing_dependency_count": len(missing_dependencies),
            "diagnostics": {
                "primitive": PRIMITIVE,
                "non_redundant_role": "persistent_replicated_civilizational_memory_runtime",
                "scoring_model": "bounded_distributed_memory_survival_model_v2",
                "closure_pressure_added": 0.0,
                "dependencies": DEPENDENCIES,
                "supports_future_phases": ["F5", "F6", "F7", "F8", "F12"],
            },
        }
        result["registry_written"] = self._write_json(self.registry_path, result)
        result["history_written"] = self._append_jsonl(self.history_path, result)
        return result
