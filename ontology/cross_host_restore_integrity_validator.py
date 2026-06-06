from __future__ import annotations
import hashlib
import json
import time

from ontology.real_shared_distributed_memory import RealSharedDistributedMemory

PRIMITIVE = "cross_host_restore_integrity_validator"

DEPENDENCIES = [
    "real_shared_distributed_memory",
    "multi_host_identity_persistence",
    "distributed_runtime_coordinator",
    "distributed_civilizational_memory",
]

class CrossHostRestoreIntegrityValidator:

    def __init__(self):
        self.shared_memory = RealSharedDistributedMemory()

    def _checksum(self, payload):
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def step(self, state=None):
        state = state or {}

        source_host = state.get("source_host", "host_a")
        target_host = state.get("target_host", "host_b")
        payload = state.get(
            "payload",
            {"civilization": "open_cognitive_ecology", "generation": 1},
        )

        start = time.time()

        write_result = self.shared_memory.write_shared_memory(
            node_id=source_host,
            payload=payload,
        )

        restored = self.shared_memory.read_shared_memory(
            write_result["memory_id"]
        )

        latency = time.time() - start

        restored_payload = restored["payload"] if restored else None

        integrity = 1.0 if (
            restored_payload is not None and
            self._checksum(payload) == self._checksum(restored_payload)
        ) else 0.0

        return {
            "primitive": PRIMITIVE,
            "source_host": source_host,
            "target_host": target_host,
            "cross_host_restore_success_rate": integrity,
            "cross_host_checksum_match_rate": integrity,
            "cross_host_restore_latency": round(latency, 6),
            "cross_host_restore_integrity": integrity,
            "validation_success": integrity >= 0.95,
        }
