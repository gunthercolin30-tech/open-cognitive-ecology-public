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
    def __init__(
        self,
        archive_dir: str = "conversation_archives",
        filesystem_effect_context_provider=None,
    ) -> None:
        self.archive_dir = Path(archive_dir)
        self.filesystem_effect_context_provider = filesystem_effect_context_provider
        self._ensure_governed_directory(self.archive_dir, "p162g6_macro02_conversation_archive_create")

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

    def save_exchange(self, question: str, response: str) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        path = self.archive_dir / f"exchange_{timestamp}.json"
        payload = {
            "timestamp": timestamp,
            "question": question,
            "response": response,
        }
        encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        provider = self.filesystem_effect_context_provider
        if not callable(provider):
            raise RuntimeError("filesystem_effect_context_provider_required")
        context = provider("FS_WRITE_REPLACE_BYTES", path)
        if context is None:
            raise RuntimeError("preissued_filesystem_effect_context_required")
        context.begin()
        remaining = context.remaining()
        slot = "p162g6_macro04_conversation_archive_write_replace"
        if remaining.get(slot, 0) != 1 or sum(remaining.values()) != 1:
            raise RuntimeError("exactly_one_conversation_archive_write_replace_authority_required")
        context.execute_path(
            slot,
            "FS_WRITE_REPLACE_BYTES",
            path,
            payload=encoded,
        )
        if any(context.remaining().values()):
            raise RuntimeError("conversation_archive_write_replace_authority_not_fully_consumed")
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
