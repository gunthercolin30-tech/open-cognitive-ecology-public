from datetime import datetime

from ontology.multi_host_identity_persistence import (
    MultiHostIdentityPersistence,
)
from ontology.distributed_runtime_coordination import (
    DistributedRuntimeCoordination,
)
from ontology.distributed_memory_continuity import (
    DistributedMemoryContinuity,
)
from ontology.distributed_knowledge_access import (
    DistributedKnowledgeAccess,
)

PRIMITIVE = "autonomous_host_preparation"


class AutonomousHostPreparation:

    def __init__(self):

        self.identity = MultiHostIdentityPersistence()
        self.runtime = DistributedRuntimeCoordination()
        self.memory = DistributedMemoryContinuity()
        self.knowledge = DistributedKnowledgeAccess()


    def _validate_host(self, candidate_host):

        allowed_hosts = {
            "oracle_cloud_free_tier",
            "https://www.oracle.com/cloud/free/",
            "https://github.com/features/actions",
            "https://www.scaleway.com/",
            "https://www.hetzner.com/",
        }

        return candidate_host in allowed_hosts


    def step(self, state=None):

        state = state or {}

        candidate_host = state.get(
            "candidate_host",
            "oracle_cloud_free_tier",
        )

        identity_result = self.identity.step()
        runtime_result = self.runtime.step(
            remote_nodes=[candidate_host]
        )
        memory_result = self.memory.step()
        knowledge_result = self.knowledge.step()

        deployment_bundle = {
            "candidate_host": candidate_host,
            "heartbeat_enabled": True,
            "identity_sync_enabled": True,
            "memory_sync_enabled": True,
            "knowledge_sync_enabled": True,
            "generated_utc": (
                datetime.utcnow().isoformat() + "Z"
            ),
        }

        host_validation_success = self._validate_host(candidate_host)

        host_preparation_ready = (
            host_validation_success and
            identity_result.get(
                "multi_host_identity_persistence_index",
                0.0,
            ) >= 0.80
            and runtime_result.get(
                "distributed_governance_ready",
                False,
            )
            and memory_result.get(
                "continuity_established",
                False,
            )
        )

        return {
            "primitive": PRIMITIVE,
            "candidate_host": candidate_host,
            "deployment_bundle": deployment_bundle,
            "node_count": runtime_result.get(
                "node_count",
                0,
            ),
            "identity_persistence_index":
                identity_result.get(
                    "multi_host_identity_persistence_index",
                    0.0,
                ),
            "distributed_memory_continuity_index":
                memory_result.get(
                    "distributed_memory_continuity_index",
                    0.0,
                ),
            "knowledge_sharing_enabled":
                knowledge_result.get(
                    "collective_sharing_enabled",
                    False,
                ),
            "host_validation_success":
                host_validation_success,
            "host_preparation_ready":
                host_preparation_ready,
        }
