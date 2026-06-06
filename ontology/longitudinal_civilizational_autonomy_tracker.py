"""
Longitudinal Civilizational Autonomy Tracker.
Persistent JSONL-backed version.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json

PRIMITIVE = "LONGITUDINAL_CIVILIZATIONAL_AUTONOMY_TRACKER"

DEPENDENCIES = [
    "civilizational_autonomy_index",
    "civilizational_memory",
]

ROOT = Path.home() / "open-cognitive-ecology"
HISTORY_FILE = ROOT / "autonomy_history.jsonl"


class LongitudinalCivilizationalAutonomyTracker:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE
        self.history = []
        self._load_history()

    def _load_history(self) -> None:
        if not HISTORY_FILE.exists():
            return
        try:
            with HISTORY_FILE.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        self.history.append(json.loads(line))
        except Exception:
            self.history = []

    def _persist_entry(self, entry: dict) -> None:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with HISTORY_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(self, civilizational_autonomy_score: float = 0.0) -> dict:
        score = self._clamp(civilizational_autonomy_score)

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "score": score,
        }

        self.history.append(entry)
        self._persist_entry(entry)

        scores = [item["score"] for item in self.history]

        current = scores[-1]
        average = sum(scores) / len(scores)
        best = max(scores)
        worst = min(scores)

        delta = scores[-1] - scores[-2] if len(scores) >= 2 else 0.0

        if delta > 0.01:
            trend = "improving"
        elif delta < -0.01:
            trend = "declining"
        else:
            trend = "stable"

        milestones = {
            "gold_reached": best >= 0.90,
            "high_autonomy_reached": best >= 0.75,
            "advanced_reached": best >= 0.60,
        }

        return {
            "primitive": self.primitive,
            "current_score": current,
            "average_score": average,
            "best_score": best,
            "worst_score": worst,
            "delta": delta,
            "trend": trend,
            "history_length": len(self.history),
            "milestones": milestones,
            "latest_entry": entry,
        }

