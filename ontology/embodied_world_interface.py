
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


class EmbodiedWorldInterface:
    def __init__(self) -> None:
        self.root = Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "embodied_world_interface"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "embodied_world_state.json"

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "interaction_cycles": 0,
            "sensor_observations": 0,
            "actions_executed": 0,
            "environment_updates": 0,
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
        state["interaction_cycles"] += 1

        sensor_reliability = float(inputs.get("sensor_reliability", 0.96))
        actuator_precision = float(inputs.get("actuator_precision", 0.95))
        environmental_awareness = float(inputs.get("environmental_awareness", 0.94))
        safety_compliance = float(inputs.get("safety_compliance", 0.99))
        feedback_quality = float(inputs.get("feedback_quality", 0.95))

        sensor_observations = int(inputs.get("sensor_observations", 100))
        actions_executed = int(inputs.get("actions_executed", 10))
        environment_updates = int(inputs.get("environment_updates", 5))

        state["sensor_observations"] += max(0, sensor_observations)
        state["actions_executed"] += max(0, actions_executed)
        state["environment_updates"] += max(0, environment_updates)
        state["last_execution_utc"] = datetime.now(timezone.utc).isoformat()

        embodied_operational_index = max(
            0.0,
            min(
                1.0,
                (
                    sensor_reliability
                    + actuator_precision
                    + environmental_awareness
                    + safety_compliance
                    + feedback_quality
                ) / 5.0,
            ),
        )

        operational = embodied_operational_index >= 0.90

        self._save_state(state)

        return {
            "primitive": "EMBODIED_WORLD_INTERFACE",
            "interaction_cycles": state["interaction_cycles"],
            "sensor_observations": state["sensor_observations"],
            "actions_executed": state["actions_executed"],
            "environment_updates": state["environment_updates"],
            "sensor_reliability": sensor_reliability,
            "actuator_precision": actuator_precision,
            "environmental_awareness": environmental_awareness,
            "safety_compliance": safety_compliance,
            "feedback_quality": feedback_quality,
            "embodied_operational_index": embodied_operational_index,
            "operational": operational,
            "state_path": str(self.state_path),
        }
