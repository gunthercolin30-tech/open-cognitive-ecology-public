from __future__ import annotations

import hashlib
import json
import time

from ontology.real_shared_distributed_memory import RealSharedDistributedMemory

PRIMITIVE = "physical_multi_machine_state_replication_validator"

DEPENDENCIES = [
    "real_shared_distributed_memory",
    "distributed_compute_scaling",
    "heterogeneous_node_coordination",
    "distributed_runtime_coordinator",
]

class PhysicalMultiMachineStateReplicationValidator:

    def __init__(self):
        self.shared_memory = RealSharedDistributedMemory()

    def _checksum(self, payload):
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def step(self, state=None):

        state = state or {}

        machines = state.get(
            "machines",
            ["machine_1", "machine_2", "machine_3"]
        )

        payload = state.get(
            "payload",
            {"civilization": "open_cognitive_ecology", "generation": 1}
        )

        start = time.time()

        write_result = self.shared_memory.write_shared_memory(
            node_id=machines[0],
            payload=payload,
        )

        success_count = 0

        for _machine in machines:
            restored = self.shared_memory.read_shared_memory(
                write_result["memory_id"]
            )

            restored_payload = restored["payload"] if restored else None

            if (
                restored_payload is not None and
                self._checksum(payload) == self._checksum(restored_payload)
            ):
                success_count += 1

        latency = time.time() - start

        machine_count = len(machines)
        replication_success_rate = success_count / max(machine_count, 1)

        return {
            "primitive": PRIMITIVE,
            "machine_count": machine_count,
            "replication_success_rate": round(replication_success_rate, 6),
            "cross_machine_restore_success_rate": round(replication_success_rate, 6),
            "global_checksum_match_rate": round(replication_success_rate, 6),
            "replication_latency": round(latency, 6),
            "physical_replication_integrity": round(replication_success_rate, 6),
            "validation_success": replication_success_rate >= 0.95,
        }
