
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


class LongDurationRuntimeSupervisor:
    def __init__(self) -> None:
        self.root = Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "runtime_supervision"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "long_duration_runtime_state.json"

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "supervision_cycles": 0,
            "restart_events": 0,
            "last_uptime_score": 1.0,
        }

    def _save_state(self, state: dict) -> None:
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def step(self, inputs=None) -> dict:
        if inputs is None:
            inputs = {}

        state = self._load_state()
        state["supervision_cycles"] += 1

        uptime_score = float(inputs.get("uptime_score", 0.99))
        persistence_integrity = float(inputs.get("persistence_integrity", 1.0))
        restart_frequency = float(inputs.get("restart_frequency", 0.0))
        drift_score = float(inputs.get("drift_score", 0.02))
        resource_stability = float(inputs.get("resource_stability", 0.98))

        if restart_frequency > 0.1:
            state["restart_events"] += 1

        long_duration_viability = max(
            0.0,
            min(
                1.0,
                (
                    uptime_score
                    + persistence_integrity
                    + (1.0 - restart_frequency)
                    + (1.0 - drift_score)
                    + resource_stability
                ) / 5.0,
            ),
        )

        autonomous_continuation_authorized = long_duration_viability >= 0.90

        state["last_uptime_score"] = uptime_score
        state["last_long_duration_viability"] = long_duration_viability
        state["last_execution_utc"] = datetime.now(timezone.utc).isoformat()

        self._save_state(state)

        return {
            "primitive": "LONG_DURATION_RUNTIME_SUPERVISOR",
            "supervision_cycles": state["supervision_cycles"],
            "restart_events": state["restart_events"],
            "uptime_score": uptime_score,
            "persistence_integrity": persistence_integrity,
            "restart_frequency": restart_frequency,
            "drift_score": drift_score,
            "resource_stability": resource_stability,
            "long_duration_viability": long_duration_viability,
            "autonomous_continuation_authorized": autonomous_continuation_authorized,
            "state_path": str(self.state_path),
        }
