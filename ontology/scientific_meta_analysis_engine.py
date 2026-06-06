
from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path


class ScientificMetaAnalysisEngine:
    primitive = "SCIENTIFIC_META_ANALYSIS_ENGINE"

    def __init__(self, archive_dir=None):
        if archive_dir is None:
            archive_dir = (
                Path.home()
                / "open-cognitive-ecology"
                / "runtime_experiments"
                / "scientific_meta_analysis"
            )
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def _normalize(self, studies):
        normalized = []
        for study in studies:
            if "effect_size" not in study:
                continue
            variance = float(study.get("variance", 1.0))
            if variance <= 0:
                variance = 1e-12
            normalized.append(
                {
                    "effect_size": float(study["effect_size"]),
                    "variance": variance,
                    "weight": 1.0 / variance,
                }
            )
        return normalized

    def step(self, studies):
        studies = self._normalize(studies)

        if not studies:
            return {
                "primitive": self.primitive,
                "study_count": 0,
                "publication_ready": False,
                "reason": "no_valid_studies",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        total_weight = sum(s["weight"] for s in studies)
        combined = sum(
            s["effect_size"] * s["weight"] for s in studies
        ) / total_weight

        variance_combined = 1.0 / total_weight
        standard_error = math.sqrt(variance_combined)

        ci_lower = combined - 1.96 * standard_error
        ci_upper = combined + 1.96 * standard_error

        z_value = combined / standard_error if standard_error > 0 else 0.0

        q = sum(
            s["weight"] * (s["effect_size"] - combined) ** 2
            for s in studies
        )

        df = max(len(studies) - 1, 1)

        if q > 0:
            i2 = max(0.0, (q - df) / q)
        else:
            i2 = 0.0

        sum_w_sq = sum(s["weight"] ** 2 for s in studies)

        if total_weight > 0:
            c = total_weight - (sum_w_sq / total_weight)
        else:
            c = 0.0

        if c > 0:
            tau2 = max(0.0, (q - df) / c)
        else:
            tau2 = 0.0

        if abs(z_value) >= 3.29:
            significance = "p<0.001"
        elif abs(z_value) >= 2.58:
            significance = "p<0.01"
        elif abs(z_value) >= 1.96:
            significance = "p<0.05"
        else:
            significance = "ns"

        result = {
            "primitive": self.primitive,
            "study_count": len(studies),
            "combined_effect_size": round(combined, 6),
            "standard_error": round(standard_error, 6),
            "variance": round(variance_combined, 6),
            "confidence_interval": {
                "lower": round(ci_lower, 6),
                "upper": round(ci_upper, 6),
            },
            "heterogeneity": {
                "Q": round(q, 6),
                "degrees_of_freedom": len(studies) - 1,
                "I2": round(i2, 6),
                "tau2": round(tau2, 6),
            },
            "overall_significance": significance,
            "publication_ready": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self._archive(result)
        return result

    def _archive(self, result):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = (
            self.archive_dir
            / f"scientific_meta_analysis_{timestamp}.json"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    from pprint import pprint

    studies = [
        {"effect_size": 0.45, "variance": 0.04},
        {"effect_size": 0.52, "variance": 0.03},
        {"effect_size": 0.39, "variance": 0.05},
    ]

    pprint(ScientificMetaAnalysisEngine().step(studies))
