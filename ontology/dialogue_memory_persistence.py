"""Persistent storage for conversational context states."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class DialogueMemoryPersistence:
    PRIMITIVE = "DIALOGUE_MEMORY_PERSISTENCE"

    def __init__(self):
        self.root = Path.home() / "open-cognitive-ecology"
        self.memory_dir = self.root / "dialogue_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.memory_dir / "latest_context.json"

    def save(self, context_state):
        payload = dict(context_state or {})
        payload["saved_at"] = datetime.utcnow().isoformat() + "Z"
        self.latest_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return {
            "primitive": self.PRIMITIVE,
            "action": "save",
            "path": str(self.latest_path),
            "success": True,
        }

    def load(self):
        if not self.latest_path.exists():
            return {
                "primitive": self.PRIMITIVE,
                "action": "load",
                "path": str(self.latest_path),
                "success": False,
                "context_state": {},
            }

        context_state = json.loads(self.latest_path.read_text(encoding="utf-8"))
        return {
            "primitive": self.PRIMITIVE,
            "action": "load",
            "path": str(self.latest_path),
            "success": True,
            "context_state": context_state,
        }

    def step(self, inputs=None):
        inputs = inputs or {}
        action = inputs.get("action", "save")

        if action == "load":
            return self.load()

        context_state = inputs.get("context_state", {})
        return self.save(context_state)
