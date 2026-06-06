"""
Continuous Civilizational Scheduler.
Executes the persistent civilizational runtime repeatedly.
"""

from __future__ import annotations

from ontology.persistent_civilizational_runtime import PersistentCivilizationalRuntime

PRIMITIVE = "CONTINUOUS_CIVILIZATIONAL_SCHEDULER"

DEPENDENCIES = [
    "persistent_civilizational_runtime",
]


class ContinuousCivilizationalScheduler:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE
        self.runtime = PersistentCivilizationalRuntime()
        self.total_cycles = 0

    def step(self, cycles: int = 1) -> dict:
        cycles = max(1, int(cycles))
        results = []

        for _ in range(cycles):
            results.append(self.runtime.step())
            self.total_cycles += 1

        latest = results[-1]

        return {
            "primitive": self.primitive,
            "cycles_requested": cycles,
            "total_cycles_executed": self.total_cycles,
            "latest_runtime_result": latest,
            "continuous_operation": True,
        }
