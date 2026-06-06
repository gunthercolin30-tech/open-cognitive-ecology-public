"""
Conversation Memory Archive

Primitive assurant l'archivage persistant des conversations entre
l'utilisateur et le représentant suprême.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

PRIMITIVE = "conversation_memory_archive"

DEPENDENCIES = ['supreme_representative_chat_interface', 'longitudinal_society_observatory', 'persistent_multi_scale_memory']


class ConversationMemoryArchive:
    def __init__(self, archive_dir: str = "conversation_archives") -> None:
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def save_exchange(self, question: str, response: str) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        path = self.archive_dir / f"exchange_{timestamp}.json"
        payload = {
            "timestamp": timestamp,
            "question": question,
            "response": response,
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def list_archives(self) -> list[str]:
        return sorted(p.name for p in self.archive_dir.glob("*.json"))

    def step(self) -> dict:
        archives = self.list_archives()
        return {
            "primitive": PRIMITIVE,
            "archive_count": len(archives),
            "latest_archive": archives[-1] if archives else None,
            "persistent_memory_enabled": True,
            "classification": "Conversation Memory Archive Operational",
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "archive_directory": str(self.archive_dir),
            },
        }
