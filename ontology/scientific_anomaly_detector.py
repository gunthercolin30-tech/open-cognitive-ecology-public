
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class ScientificAnomalyDetector:
    primitive = "SCIENTIFIC_ANOMALY_DETECTOR"

    def __init__(self, archive_dir=None):
        if archive_dir is None:
            archive_dir = (
                Path.home()
                / "open-cognitive-ecology"
                / "runtime_experiments"
                / "scientific_anomalies"
            )
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def step(self, theory_result):
        if (
            not isinstance(theory_result, dict)
            or not theory_result.get("publication_ready")
        ):
            return {
                "primitive": self.primitive,
                "publication_ready": False,
                "reason": "invalid_theory_result",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        confidence = float(theory_result.get("theory_confidence_score", 0.0))
        credibility = float(
            theory_result.get("theoretical_credibility_index", 0.0)
        )
        resilience = float(
            theory_result.get("falsification_resilience", 0.0)
        )

        anomaly_score = max(
            0.0,
            1.0 - (0.4 * confidence + 0.3 * credibility + 0.3 * resilience),
        )

        empirical_tension_index = max(0.0, 1.0 - credibility)
        contradiction_index = max(0.0, 1.0 - resilience)
        revision_pressure_index = (
            0.5 * anomaly_score + 0.5 * empirical_tension_index
        )

        if anomaly_score < 0.02:
            anomaly_status = "none_detected"
        elif anomaly_score < 0.10:
            anomaly_status = "minor"
        elif anomaly_score < 0.25:
            anomaly_status = "moderate"
        else:
            anomaly_status = "major"

        result = {
            "primitive": self.primitive,
            "anomaly_score": round(anomaly_score, 6),
            "empirical_tension_index": round(empirical_tension_index, 6),
            "contradiction_index": round(contradiction_index, 6),
            "revision_pressure_index": round(revision_pressure_index, 6),
            "anomaly_status": anomaly_status,
            "publication_ready": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self._archive(result)
        return result

    def _archive(self, result):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = self.archive_dir / f"scientific_anomaly_{timestamp}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    from pprint import pprint

    sample = {
        "theory_confidence_score": 0.994399,
        "theoretical_credibility_index": 0.996549,
        "falsification_resilience": 0.997331,
        "publication_ready": True,
    }

    pprint(ScientificAnomalyDetector().step(sample))
