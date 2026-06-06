from __future__ import annotations

import time

PRIMITIVE = "failover_continuity_validator"

DEPENDENCIES = [
    "distributed_runtime_coordination",
    "distributed_runtime_coordinator",
    "civilizational_resilience",
    "network_fragmentation_resilience",
    "longitudinal_recovery_observer",
]


class FailoverContinuityValidator:

    def _ratio(self, a, b):
        return a / b if b else 0.0

    def step(self, state=None):

        state = state or {}

        machines = state.get(
            "machines",
            [f"machine_{i}" for i in range(5)]
        )

        failed_machines = state.get(
            "failed_machines",
            [machines[0]] if machines else []
        )

        start = time.time()

        total_count = len(machines)
        failed_count = len(failed_machines)

        surviving = [
            m for m in machines
            if m not in failed_machines
        ]

        survival_rate = self._ratio(
            len(surviving),
            total_count,
        )

        continuity = (
            1.0 if len(surviving) > 0 else 0.0
        )

        continuity_score = round(
            (survival_rate + continuity) / 2.0,
            6,
        )

        return {
            "primitive": PRIMITIVE,
            "machine_count": total_count,
            "failed_machine_count": failed_count,
            "remaining_node_count": len(surviving),
            "continuity_after_primary_failure": continuity,
            "state_survival_rate": round(
                survival_rate, 6
            ),
            "failover_recovery_time": round(
                time.time() - start, 6
            ),
            "civilizational_continuity_score":
                continuity_score,
            "validation_success":
                continuity_score >= 0.75,
        }