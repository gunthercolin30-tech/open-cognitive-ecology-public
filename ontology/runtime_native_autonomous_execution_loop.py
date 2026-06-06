"""
RUNTIME_NATIVE_AUTONOMOUS_EXECUTION_LOOP

Primitive de boucle d'exécution autonome persistante.
"""

import time
from typing import Any, Dict


class RuntimeNativeAutonomousExecutionLoop:
    primitive = "RUNTIME_NATIVE_AUTONOMOUS_EXECUTION_LOOP"

    def __init__(self, runtime=None, sleep_seconds: float = 0.0):
        self.runtime = runtime
        self.sleep_seconds = sleep_seconds
        self.cycle_count = 0
        self.last_result = None

    def step(self) -> Dict[str, Any]:
        self.cycle_count += 1

        if self.runtime is not None and hasattr(self.runtime, "step"):
            self.last_result = self.runtime.step()
        else:
            self.last_result = {"status": "idle", "message": "No runtime connected."}

        if self.sleep_seconds > 0:
            time.sleep(self.sleep_seconds)

        return {
            "primitive": self.primitive,
            "cycle_count": self.cycle_count,
            "last_result": self.last_result,
            "persistent": True,
            "autonomous": True,
        }

    def run_forever(self):
        while True:
            self.step()
