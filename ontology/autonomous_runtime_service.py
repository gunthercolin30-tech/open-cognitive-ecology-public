
"""
AUTONOMOUS_RUNTIME_SERVICE
"""

from pathlib import Path
from datetime import datetime
import json
import time

PRIMITIVE = "AUTONOMOUS_RUNTIME_SERVICE"


class AutonomousRuntimeService:
    primitive = PRIMITIVE

    def __init__(self, root=None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.service_dir = self.root / "runtime_service"
        self.service_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.service_dir / "service_state.json"

    def _timestamp(self):
        return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    def _save_state(self, state):
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def step(
        self,
        max_cycles=10,
        sleep_seconds=0.0,
        viability_threshold=0.90,
        autonomy_threshold=0.90,
    ):
        from ontology.long_horizon_stability_protocol import LongHorizonStabilityProtocol

        result = LongHorizonStabilityProtocol(root=self.root).step(
            max_cycles=max_cycles,
            sleep_seconds=sleep_seconds,
            viability_threshold=viability_threshold,
            autonomy_threshold=autonomy_threshold,
        )

        state = {
            "primitive": self.primitive,
            "timestamp": self._timestamp(),
            "last_result": result,
            "status": "completed",
        }
        self._save_state(state)

        return {
            "primitive": self.primitive,
            "service_state_path": str(self.state_path),
            "last_result": result,
            "status": "completed",
        }

    def run_forever(
        self,
        interval_seconds=3600.0,
        max_cycles=10,
        sleep_seconds=0.0,
        viability_threshold=0.90,
        autonomy_threshold=0.90,
    ):
        iterations = 0
        try:
            while True:
                iterations += 1
                result = self.step(
                    max_cycles=max_cycles,
                    sleep_seconds=sleep_seconds,
                    viability_threshold=viability_threshold,
                    autonomy_threshold=autonomy_threshold,
                )

                state = {
                    "primitive": self.primitive,
                    "timestamp": self._timestamp(),
                    "iterations": iterations,
                    "last_result": result,
                    "status": "running",
                }
                self._save_state(state)

                if interval_seconds > 0:
                    time.sleep(interval_seconds)
        except KeyboardInterrupt:
            state = {
                "primitive": self.primitive,
                "timestamp": self._timestamp(),
                "iterations": iterations,
                "status": "stopped_by_user",
            }
            self._save_state(state)
            return state
