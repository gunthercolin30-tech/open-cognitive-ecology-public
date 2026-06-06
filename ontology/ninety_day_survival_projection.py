
from __future__ import annotations

from pathlib import Path
import json

PRIMITIVE = "ninety_day_survival_projection"

DEPENDENCIES = [
    "extended_certification_continuity_tracker",
    "longitudinal_trend_stability_analyzer",
    "thirty_day_distributed_monitoring",
    "long_duration_runtime_supervisor",
]

class NinetyDaySurvivalProjection:

    def __init__(self, root=None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"

    def _collect_viability_scores(self):
        scores = []

        for path in self.root.rglob("metrics_history.jsonl"):
            try:
                for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if not line.strip():
                        continue
                    rec = json.loads(line)
                    metrics = rec.get("metrics", {})
                    value = metrics.get("global_viability_score")
                    if value is not None:
                        scores.append(float(value))
            except Exception:
                pass

        return scores

    def step(self):
        scores = self._collect_viability_scores()

        if len(scores) < 2:
            return {
                "primitive": PRIMITIVE,
                "projection_ready": False,
                "reason": "insufficient_history",
            }

        n = len(scores)

        x_mean = (n - 1) / 2.0
        y_mean = sum(scores) / n

        num = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(scores))
        den = sum((i - x_mean) ** 2 for i in range(n))

        slope = num / den if den else 0.0

        projected_90 = scores[-1] + slope * 90.0
        projected_90 = max(0.0, min(1.0, projected_90))

        survival_probability = projected_90
        resilience_projection = (scores[-1] + projected_90) / 2.0

        return {
            "primitive": PRIMITIVE,
            "history_length": n,
            "current_viability": round(scores[-1], 6),
            "trend_slope": round(slope, 8),
            "projected_stability_index": round(projected_90, 6),
            "projected_certification_continuity": round(projected_90, 6),
            "ninety_day_survival_probability": round(survival_probability, 6),
            "resilience_projection": round(resilience_projection, 6),
            "projection_ready": True,
        }
