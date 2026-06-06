
from __future__ import annotations

from pathlib import Path
import json

PRIMITIVE = "longitudinal_trend_stability_analyzer"

DEPENDENCIES = [
    "extended_certification_continuity_tracker",
    "historical_metrics_harvester",
    "continuous_long_duration_runtime_executor",
    "long_duration_runtime_supervisor",
]

class LongitudinalTrendStabilityAnalyzer:

    def __init__(self, root=None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"

    def _collect_scores(self):
        scores = []

        for path in self.root.rglob("metrics_history.jsonl"):
            try:
                for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if not line.strip():
                        continue
                    rec = json.loads(line)
                    metrics = rec.get("metrics", {})
                    score = metrics.get("global_viability_score")
                    if score is not None:
                        scores.append(float(score))
            except Exception:
                pass

        return scores

    def step(self):
        scores = self._collect_scores()

        if len(scores) < 2:
            return {
                "primitive": PRIMITIVE,
                "trend_ready": False,
                "reason": "insufficient_history",
            }

        slope = scores[-1] - scores[0]
        stability_index = max(0.0, min(1.0, 1.0 - abs(slope)))

        if slope > 0.01:
            direction = "improving"
        elif slope < -0.01:
            direction = "degrading"
        else:
            direction = "stable"

        return {
            "primitive": PRIMITIVE,
            "history_length": len(scores),
            "trend_slope": round(slope, 6),
            "trajectory_direction": direction,
            "stability_index": round(stability_index, 6),
            "early_degradation_signal": direction == "degrading",
            "trend_ready": True,
        }
