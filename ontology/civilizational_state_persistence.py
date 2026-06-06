"""
Civilizational State Persistence.
Save and restore civilization-scale state snapshots using the Python standard library.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

PRIMITIVE = "CIVILIZATIONAL_STATE_PERSISTENCE"

DEPENDENCIES = [
    "civilizational_memory",
    "autonomous_civilizational_governor",
]


class CivilizationalStatePersistence:
    def __init__(self, storage_dir: str = "civilizational_state") -> None:
        self.primitive = PRIMITIVE
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, state: dict, filename: str = "latest_state.json") -> dict:
        path = self.storage_dir / filename

        payload = {
            "primitive": self.primitive,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "state": state,
        }

        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return {
            "primitive": self.primitive,
            "action": "save",
            "path": str(path),
            "success": True,
        }

    def load(self, filename: str = "latest_state.json") -> dict:
        path = self.storage_dir / filename
        payload = json.loads(path.read_text(encoding="utf-8"))

        return {
            "primitive": self.primitive,
            "action": "load",
            "path": str(path),
            "success": True,
            "timestamp": payload.get("timestamp"),
            "state": payload.get("state", {}),
        }

    def step(self, state: dict | None = None) -> dict:
        if state is None:
            state = {}
        save_result = self.save(state)
        load_result = self.load()

        return {
            "primitive": self.primitive,
            "save_result": save_result,
            "load_result": load_result,
            "state_restored": load_result["state"] == state,
        }
