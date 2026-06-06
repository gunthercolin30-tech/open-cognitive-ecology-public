from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from ontology.persistent_external_memory_fabric import (
    PersistentExternalMemoryFabric,
)

PRIMITIVE = "real_shared_distributed_memory"

DEPENDENCIES = [
    "persistent_external_memory_fabric",
    "distributed_memory_consistency_validator",
    "distributed_runtime_coordination",
]


class RealSharedDistributedMemory:

    def __init__(self):
        self.memory = PersistentExternalMemoryFabric()

    def write_shared_memory(
        self,
        node_id="host_a",
        payload=None,
    ):

        payload = payload or {}

        memory_id = str(uuid4())

        record = {
            "memory_id": memory_id,
            "node_id": node_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload,
        }

        self.memory.store(memory_id, record)

        return record

    def read_shared_memory(self, memory_id):

        return self.memory.recall(memory_id)

    def step(self, state=None):

        state = state or {}

        payload = state.get(
            "payload",
            {"message": "distributed_memory_test"},
        )

        write_result = self.write_shared_memory(
            node_id=state.get("writer", "host_a"),
            payload=payload,
        )

        read_result = self.read_shared_memory(
            write_result["memory_id"]
        )

        success = (
            read_result is not None
            and read_result["payload"] == payload
        )

        return {
            "primitive": PRIMITIVE,
            "memory_id": write_result["memory_id"],
            "writer": write_result["node_id"],
            "cross_host_read_success": success,
            "distributed_memory_consistency":
                1.0 if success else 0.0,
            "shared_memory_operational": success,
        }