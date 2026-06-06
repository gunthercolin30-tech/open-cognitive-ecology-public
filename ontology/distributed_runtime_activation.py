from datetime import datetime

PRIMITIVE = "distributed_runtime_activation"

class DistributedRuntimeActivation:

    def step(self, state=None):

        state = state or {}

        node_a = state.get("node_a_online", True)
        node_b = state.get("node_b_online", True)

        heartbeat_exchange = (
            node_a and node_b and
            state.get("heartbeat_exchange", True)
        )

        state_synchronization = (
            node_a and node_b and
            state.get("state_synchronization", True)
        )

        coordination_effective = (
            heartbeat_exchange and
            state_synchronization and
            state.get("coordination_effective", True)
        )

        dual_host_runtime_operational = (
            node_a and node_b and coordination_effective
        )

        return {
            "primitive": PRIMITIVE,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "node_a_online": node_a,
            "node_b_online": node_b,
            "heartbeat_exchange": heartbeat_exchange,
            "state_synchronization": state_synchronization,
            "coordination_effective": coordination_effective,
            "dual_host_runtime_operational": dual_host_runtime_operational,
        }
