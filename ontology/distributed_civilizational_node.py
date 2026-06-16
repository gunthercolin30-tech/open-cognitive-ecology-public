
# -*- coding: utf-8 -*-
"""
F1 — Distributed Civilizational Node.

This primitive defines the local node unit required for multi-machine
civilizational deployment. It does not perform network operations directly;
instead, it produces a persistent, auditable, and measurable local node state
that can be consumed by coordination, replication, memory, migration, and
failure-recovery layers.

The validation target is functional: identity stability, local memory anchoring,
heartbeat emission, availability measurement, and readiness for synchronization.
"""


from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import hashlib
import json
import os
import platform
import socket
import uuid

PRIMITIVE = "distributed_civilizational_node"

DEPENDENCIES = [
    "civilizational_state_persistence",
    "civilizational_memory_archive",
    "civilizational_identity_synthesis",
    "distributed_runtime_coordination",
    "distributed_runtime_coordinator",
    "distributed_knowledge_access",
    "civilizational_resilience",
    "resilience_distribution_analyzer",
    "heterogeneous_node_coordination",
    "autonomous_inter_node_civilizational_coordination",
    "metrics_history_recorder",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if number != number or number in (float("inf"), float("-inf")):
        return default
    return max(0.0, min(1.0, number))


def _safe_text(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


@dataclass
class NodeState:
    node_id: str
    node_name: str
    host_fingerprint: str
    platform_name: str
    role: str
    status: str
    timestamp_utc: str
    local_memory_ready: bool
    local_state_ready: bool
    identity_ready: bool
    sync_ready: bool
    heartbeat_count: int
    active_node_count: int
    node_availability_ratio: float
    node_identity_hash: str
    last_sync_timestamp: Optional[str]


class DistributedCivilizationalNode:
    """Persistent local node descriptor for distributed civilization deployment."""

    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None, node_id: str | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.node_dir = self.root / "distributed_nodes"
        self.node_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.node_dir / "node_registry.json"
        self.history_path = self.node_dir / "node_heartbeat_history.jsonl"
        self.node_id = node_id or os.environ.get("OCE_NODE_ID") or self._load_or_create_node_id()
        self.state_path = self.node_dir / f"{self.node_id}.json"

    def _load_or_create_node_id(self) -> str:
        identity_path = self.node_dir / "local_node_identity.json"
        if identity_path.exists():
            try:
                data = json.loads(identity_path.read_text(encoding="utf-8"))
                candidate = _safe_text(data.get("node_id"), "")
                if candidate:
                    return candidate
            except Exception:
                pass
        seed = f"{socket.gethostname()}:{platform.platform()}:{uuid.uuid4()}"
        node_id = "oce-node-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
        identity_path.write_text(
            json.dumps({"node_id": node_id, "created_at_utc": _now()}, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return node_id

    def _host_fingerprint(self) -> str:
        seed = "|".join([
            socket.gethostname(),
            platform.system(),
            platform.release(),
            platform.machine(),
            str(self.root),
        ])
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]

    def _identity_hash(self, node_name: str, role: str) -> str:
        seed = "|".join([
            self.node_id,
            node_name,
            role,
            self._host_fingerprint(),
            "Open Cognitive Ecology Society",
        ])
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()

    def _read_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return default
        return default

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            return True
        except Exception:
            return False

    def _append_history(self, payload: Dict[str, Any]) -> bool:
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
            return True
        except Exception:
            return False

    def _update_registry(self, state: Dict[str, Any]) -> Dict[str, Any]:
        registry = self._read_json(self.registry_path, {"primitive": PRIMITIVE, "nodes": {}})
        if not isinstance(registry, dict):
            registry = {"primitive": PRIMITIVE, "nodes": {}}
        nodes = registry.setdefault("nodes", {})
        if not isinstance(nodes, dict):
            nodes = {}
            registry["nodes"] = nodes
        nodes[self.node_id] = {
            "node_id": self.node_id,
            "node_name": state.get("node_name"),
            "role": state.get("role"),
            "status": state.get("status"),
            "last_seen_utc": state.get("timestamp_utc"),
            "node_availability_ratio": state.get("node_availability_ratio"),
            "node_identity_hash": state.get("node_identity_hash"),
        }
        active_nodes = [n for n in nodes.values() if n.get("status") in {"active", "degraded"}]
        registry["active_node_count"] = len(active_nodes)
        registry["updated_at_utc"] = _now()
        self._write_json(self.registry_path, registry)
        return registry

    def _previous_heartbeat_count(self) -> int:
        previous = self._read_json(self.state_path, {})
        if isinstance(previous, dict):
            try:
                return int(previous.get("heartbeat_count", 0))
            except Exception:
                return 0
        return 0

    def step(self, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        state = state or {}

        node_name = _safe_text(state.get("node_name"), socket.gethostname() or self.node_id)
        role = _safe_text(state.get("role"), "primary")

        local_memory_ready = bool(state.get("local_memory_ready", True))
        local_state_ready = bool(state.get("local_state_ready", True))
        identity_ready = bool(state.get("identity_ready", True))
        sync_signal = _bounded(state.get("sync_signal", 1.0), 1.0)
        coordination_signal = _bounded(state.get("coordination_signal", 1.0), 1.0)
        memory_signal = _bounded(state.get("memory_signal", 1.0 if local_memory_ready else 0.0), 1.0)
        state_signal = _bounded(state.get("state_signal", 1.0 if local_state_ready else 0.0), 1.0)

        sync_ready = sync_signal >= 0.5 and coordination_signal >= 0.5
        availability_components = [sync_signal, coordination_signal, memory_signal, state_signal]
        if not identity_ready:
            availability_components.append(0.0)
        node_availability_ratio = _bounded(sum(availability_components) / len(availability_components))

        if not identity_ready or not local_state_ready:
            status = "degraded"
        elif node_availability_ratio >= 0.80 and sync_ready:
            status = "active"
        elif node_availability_ratio >= 0.50:
            status = "degraded"
        else:
            status = "inactive"

        heartbeat_count = self._previous_heartbeat_count() + 1
        timestamp = _now()
        last_sync_timestamp = timestamp if sync_ready else None

        node_state = NodeState(
            node_id=self.node_id,
            node_name=node_name,
            host_fingerprint=self._host_fingerprint(),
            platform_name=platform.platform(),
            role=role,
            status=status,
            timestamp_utc=timestamp,
            local_memory_ready=local_memory_ready,
            local_state_ready=local_state_ready,
            identity_ready=identity_ready,
            sync_ready=sync_ready,
            heartbeat_count=heartbeat_count,
            active_node_count=1 if status in {"active", "degraded"} else 0,
            node_availability_ratio=round(node_availability_ratio, 4),
            node_identity_hash=self._identity_hash(node_name, role),
            last_sync_timestamp=last_sync_timestamp,
        )

        payload = asdict(node_state)
        state_persisted = self._write_json(self.state_path, payload)
        registry = self._update_registry(payload)
        history_written = self._append_history(payload)

        active_node_count = int(registry.get("active_node_count", payload["active_node_count"]))
        payload["active_node_count"] = active_node_count
        payload["state_persisted"] = state_persisted
        payload["history_written"] = history_written
        payload["registry_path"] = str(self.registry_path)
        payload["state_path"] = str(self.state_path)
        payload["history_path"] = str(self.history_path)
        payload["node_operational"] = status in {"active", "degraded"}
        payload["diagnostics"] = {
            "primitive": PRIMITIVE,
            "dependencies": DEPENDENCIES,
            "non_redundant_role": "local_persistent_node_unit",
            "supports_future_phases": ["F2", "F3", "F4", "F5", "F6", "F7", "F12"],
            "closure_pressure_added": 0.0,
        }
        return payload
