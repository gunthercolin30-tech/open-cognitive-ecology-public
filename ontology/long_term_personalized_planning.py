"""Long-Term Personalized Planning."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class LongTermPersonalizedPlanning:
    PRIMITIVE = "LONG_TERM_PERSONALIZED_PLANNING"

    def __init__(self, user_name: str = "User") -> None:
        self.user_name = user_name
        self.storage_dir = Path.home() / ".open_cognitive_ecology"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.plan_file = self.storage_dir / f"{user_name.lower()}_long_term_plan.json"

    def _load(self) -> Dict[str, Any]:
        import json
        if self.plan_file.exists():
            try:
                return json.loads(self.plan_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "user_name": self.user_name,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "objectives": [],
            "milestones": [],
            "priorities": [],
        }

    def _save(self, data: Dict[str, Any]) -> None:
        import json
        self.plan_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add_objective(self, objective: str, priority: str = "high") -> Dict[str, Any]:
        data = self._load()
        data["objectives"].append({
            "objective": objective,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "active",
        })
        self._save(data)
        return data

    def step(self, message: str = "") -> Dict[str, Any]:
        if message.strip() and (
            "objectif" in message.lower() or "objective" in message.lower()
        ):
            self.add_objective(message)

        data = self._load()

        return {
            "primitive": self.PRIMITIVE,
            "user_name": self.user_name,
            "plan_file": str(self.plan_file),
            "objective_count": len(data.get("objectives", [])),
            "milestone_count": len(data.get("milestones", [])),
            "priority_count": len(data.get("priorities", [])),
            "latest_objective": data["objectives"][-1] if data.get("objectives") else None,
            "planning_active": True,
        }


def step(message: str = "", user_name: str = "User") -> Dict[str, Any]:
    return LongTermPersonalizedPlanning(user_name=user_name).step(message)
