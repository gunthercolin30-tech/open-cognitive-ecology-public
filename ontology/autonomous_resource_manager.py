
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


class AutonomousResourceManager:
    def __init__(self) -> None:
        self.root = Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "resource_management"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "resource_manager_state.json"

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "management_cycles": 0,
            "allocation_events": 0,
            "optimization_events": 0,
            "shortage_alerts": 0,
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
        state["management_cycles"] += 1

        cpu_availability = float(inputs.get("cpu_availability", 0.95))
        memory_availability = float(inputs.get("memory_availability", 0.96))
        storage_availability = float(inputs.get("storage_availability", 0.97))
        energy_stability = float(inputs.get("energy_stability", 0.94))
        budget_stability = float(inputs.get("budget_stability", 0.93))

        allocation_events = int(inputs.get("allocation_events", 5))
        optimization_events = int(inputs.get("optimization_events", 3))

        state["allocation_events"] += max(0, allocation_events)
        state["optimization_events"] += max(0, optimization_events)

        if min(
            cpu_availability,
            memory_availability,
            storage_availability,
            energy_stability,
            budget_stability,
        ) < 0.70:
            state["shortage_alerts"] += 1

        state["last_execution_utc"] = datetime.now(timezone.utc).isoformat()

        resource_viability_index = max(
            0.0,
            min(
                1.0,
                (
                    cpu_availability
                    + memory_availability
                    + storage_availability
                    + energy_stability
                    + budget_stability
                ) / 5.0,
            ),
        )

        operational = resource_viability_index >= 0.90

        self._save_state(state)

        return {
            "primitive": "AUTONOMOUS_RESOURCE_MANAGER",
            "management_cycles": state["management_cycles"],
            "allocation_events": state["allocation_events"],
            "optimization_events": state["optimization_events"],
            "shortage_alerts": state["shortage_alerts"],
            "cpu_availability": cpu_availability,
            "memory_availability": memory_availability,
            "storage_availability": storage_availability,
            "energy_stability": energy_stability,
            "budget_stability": budget_stability,
            "resource_viability_index": resource_viability_index,
            "operational": operational,
            "state_path": str(self.state_path),
        }
