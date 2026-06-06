"""Adaptive Relationship Modeling."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class AdaptiveRelationshipModeling:
    PRIMITIVE = "ADAPTIVE_RELATIONSHIP_MODELING"

    def __init__(self, user_name: str = "User") -> None:
        self.user_name = user_name
        self.storage_dir = Path.home() / ".open_cognitive_ecology"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.profile_file = self.storage_dir / f"{user_name.lower()}_relationship_profile.json"

    def _load(self) -> Dict[str, Any]:
        import json
        if self.profile_file.exists():
            try:
                return json.loads(self.profile_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "user_name": self.user_name,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "interaction_count": 0,
            "observed_topics": {},
            "last_message": "",
        }

    def _save(self, data: Dict[str, Any]) -> None:
        import json
        self.profile_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def step(self, message: str = "") -> Dict[str, Any]:
        data = self._load()

        if message.strip():
            data["interaction_count"] += 1
            data["last_message"] = message
            for token in message.lower().split():
                token = token.strip(".,;:!?()[]{}")
                if len(token) >= 4:
                    topics = data.setdefault("observed_topics", {})
                    topics[token] = topics.get(token, 0) + 1
            self._save(data)

        topics = data.get("observed_topics", {})
        top_topics = sorted(
            topics.items(),
            key=lambda kv: (-kv[1], kv[0])
        )[:10]

        return {
            "primitive": self.PRIMITIVE,
            "user_name": self.user_name,
            "profile_file": str(self.profile_file),
            "interaction_count": data.get("interaction_count", 0),
            "top_topics": top_topics,
            "last_message": data.get("last_message", ""),
            "relationship_model_active": True,
        }


def step(message: str = "", user_name: str = "User") -> Dict[str, Any]:
    return AdaptiveRelationshipModeling(user_name=user_name).step(message)
