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
    def __init__(
        self,
        storage_dir: str = "civilizational_state",
        filesystem_effect_context_provider=None,
    ) -> None:
        self.primitive = PRIMITIVE
        self.storage_dir = Path(storage_dir)
        self.filesystem_effect_context_provider = filesystem_effect_context_provider
        self._ensure_governed_directory(self.storage_dir, "p162g6_macro02_state_directory_create")

    def _ensure_governed_directory(self, directory: Path, slot: str) -> None:
        if directory.exists():
            return
        provider = self.filesystem_effect_context_provider
        if not callable(provider):
            raise RuntimeError("filesystem_effect_context_provider_required")
        context = provider("FS_CREATE_DIR", directory)
        if context is None:
            raise RuntimeError("preissued_filesystem_effect_context_required")
        context.begin()
        context.execute_path(slot, "FS_CREATE_DIR", directory)

    def save(
        self,
        state: dict,
        filename: str = "latest_state.json",
        filesystem_context=None,
    ) -> dict:
        path = self.storage_dir / filename

        payload = {
            "primitive": self.primitive,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "state": state,
        }
        encoded = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")

        if filesystem_context is None:
            raise PermissionError("governed filesystem context required")
        remaining = filesystem_context.remaining()
        if remaining.get("state_write_replace", 0) != 1:
            raise RuntimeError("exactly one state_write_replace authority required")
        filesystem_context.execute_path(
            "state_write_replace",
            "FS_WRITE_REPLACE_BYTES",
            path,
            payload=encoded,
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

    def step(self, state: dict | None = None, filesystem_context=None) -> dict:
        if state is None:
            state = {}
        save_result = self.save(state, filesystem_context=filesystem_context)
        load_result = self.load()

        return {
            "primitive": self.primitive,
            "save_result": save_result,
            "load_result": load_result,
            "state_restored": load_result["state"] == state,
        }
