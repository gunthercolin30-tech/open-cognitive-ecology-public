
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class ScientificParadigmShiftMonitor:
    primitive = "SCIENTIFIC_PARADIGM_SHIFT_MONITOR"

    def __init__(self, archive_dir=None):
        if archive_dir is None:
            archive_dir = (
                Path.home()
                / "open-cognitive-ecology"
                / "runtime_experiments"
                / "scientific_paradigm_shifts"
            )
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def step(self, anomaly_result):
        if (
            not isinstance(anomaly_result, dict)
            or not anomaly_result.get("publication_ready")
        ):
            return {
                "primitive": self.primitive,
                "publication_ready": False,
                "reason": "invalid_anomaly_result",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        anomaly_score = float(anomaly_result.get("anomaly_score", 0.0))
        revision_pressure = float(
            anomaly_result.get("revision_pressure_index", 0.0)
        )
        contradiction = float(
            anomaly_result.get("contradiction_index", 0.0)
        )

        paradigm_shift_probability = min(
            1.0,
            0.5 * anomaly_score
            + 0.3 * revision_pressure
            + 0.2 * contradiction,
        )

        conceptual_instability_index = min(
            1.0,
            0.6 * revision_pressure + 0.4 * contradiction,
        )

        if paradigm_shift_probability < 0.05:
            paradigm_status = "stable_paradigm"
        elif paradigm_shift_probability < 0.20:
            paradigm_status = "watch"
        elif paradigm_shift_probability < 0.50:
            paradigm_status = "transition_risk"
        else:
            paradigm_status = "paradigm_shift_likely"

        result = {
            "primitive": self.primitive,
            "paradigm_shift_probability": round(
                paradigm_shift_probability, 6
            ),
            "conceptual_instability_index": round(
                conceptual_instability_index, 6
            ),
            "paradigm_status": paradigm_status,
            "publication_ready": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self._archive(result)
        return result

    def _archive(self, result):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = (
            self.archive_dir
            / f"scientific_paradigm_shift_{timestamp}.json"
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    from pprint import pprint

    sample = {
        "anomaly_score": 0.004076,
        "revision_pressure_index": 0.003764,
        "contradiction_index": 0.002669,
        "publication_ready": True,
    }

    pprint(ScientificParadigmShiftMonitor().step(sample))
