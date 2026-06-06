from __future__ import annotations

from datetime import datetime
from statistics import mean

PRIMITIVE = "distributed_memory_consistency_validator"

DEPENDENCIES = [
    "distributed_memory_continuity",
    "distributed_runtime_coordination",
    "distributed_runtime_coordinator",
    "dual_host_deployment_validator",
]


class DistributedMemoryConsistencyValidator:

    def step(self, state=None):

        state = state or {}

        write_count = int(state.get("write_count", 100))
        read_count = int(state.get("read_count", 100))
        successful_replications = int(
            state.get("successful_replications", 98)
        )

        heartbeat_count = int(
            state.get("heartbeat_count", 100)
        )

        heartbeat_losses = int(
            state.get("heartbeat_losses", 1)
        )

        replication_latency = float(
            state.get("replication_latency", 0.10)
        )

        synchronization_success_rate = min(
            1.0,
            successful_replications / max(write_count, 1),
        )

        heartbeat_loss_rate = (
            heartbeat_losses / max(heartbeat_count, 1)
        )

        host_availability_index = max(
            0.0,
            1.0 - heartbeat_loss_rate,
        )

        distributed_memory_consistency = mean(
            [
                synchronization_success_rate,
                host_availability_index,
            ]
        )

        return {
            "primitive": PRIMITIVE,
            "timestamp_utc":
                datetime.utcnow().isoformat() + "Z",
            "write_count": write_count,
            "read_count": read_count,
            "successful_replications":
                successful_replications,
            "replication_latency":
                replication_latency,
            "heartbeat_count":
                heartbeat_count,
            "heartbeat_loss_rate":
                round(heartbeat_loss_rate, 6),
            "host_availability_index":
                round(host_availability_index, 6),
            "synchronization_success_rate":
                round(synchronization_success_rate, 6),
            "distributed_memory_consistency":
                round(distributed_memory_consistency, 6),
            "validation_success":
                distributed_memory_consistency >= 0.95,
        }
