
from __future__ import annotations

from pathlib import Path
import json

PRIMITIVE = "extended_certification_continuity_tracker"

DEPENDENCIES = [
    "historical_metrics_harvester",
    "longitudinal_society_observatory",
    "continuous_long_duration_runtime_executor",
    "long_duration_runtime_supervisor",
]

class ExtendedCertificationContinuityTracker:

    def __init__(self, root=None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"

    def _collect_real_certifications(self):
        certifications = []

        for path in self.root.rglob("metrics_history.jsonl"):
            try:
                for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    metrics = record.get("metrics", {})
                    cert = metrics.get("certification")
                    if cert:
                        certifications.append(str(cert))
            except Exception:
                pass

        return certifications

    def step(self):
        certifications = self._collect_real_certifications()

        if not certifications:
            return {
                "primitive": PRIMITIVE,
                "real_history_length": 0,
                "continuity_verified": False,
                "real_monitoring_active": False,
                "reason": "no_real_certifications_found",
            }

        continuity = (
            sum(1 for c in certifications if "failed" not in c.lower())
            / len(certifications)
        )

        return {
            "primitive": PRIMITIVE,
            "real_history_length": len(certifications),
            "real_certification_continuity_index": round(continuity, 4),
            "real_survival_monitoring_index": round(continuity, 4),
            "continuity_verified": continuity >= 0.90,
            "real_monitoring_active": True,
        }
