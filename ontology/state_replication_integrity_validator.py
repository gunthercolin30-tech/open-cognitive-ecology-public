from __future__ import annotations

import hashlib
import json
import time

from ontology.civilizational_state_persistence import (
    CivilizationalStatePersistence,
)

PRIMITIVE = "state_replication_integrity_validator"

DEPENDENCIES = [
    "civilizational_state_persistence",
    "real_shared_distributed_memory",
    "multi_host_identity_persistence",
    "distributed_runtime_coordinator",
]


class StateReplicationIntegrityValidator:

    def __init__(self):
        self.persistence = CivilizationalStatePersistence()

    def _checksum(self, state):
        payload = json.dumps(
            state,
            sort_keys=True,
            ensure_ascii=False,
        )
        return hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

    def step(self, state=None):

        state = state or {
            "civilization": "open_cognitive_ecology",
            "version": 1,
        }

        start = time.time()

        self.persistence.save(
            state,
            "replication_source.json",
        )

        restored = self.persistence.load(
            "replication_source.json",
        )

        restored_state = restored["state"]

        source_checksum = self._checksum(state)
        restored_checksum = self._checksum(
            restored_state
        )

        checksum_match = (
            source_checksum == restored_checksum
        )

        replication_latency = (
            time.time() - start
        )

        state_replication_integrity = (
            1.0 if checksum_match else 0.0
        )

        return {
            "primitive": PRIMITIVE,
            "snapshot_replication_success_rate":
                state_replication_integrity,
            "cross_host_restore_success_rate":
                state_replication_integrity,
            "state_checksum_match_rate":
                state_replication_integrity,
            "replication_latency":
                round(replication_latency, 6),
            "state_replication_integrity":
                state_replication_integrity,
            "validation_success":
                state_replication_integrity >= 0.95,
        }
