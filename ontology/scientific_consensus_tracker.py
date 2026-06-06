
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class ScientificConsensusTracker:
    primitive = "SCIENTIFIC_CONSENSUS_TRACKER"

    def __init__(self, archive_dir=None):
        if archive_dir is None:
            archive_dir = (
                Path.home()
                / "open-cognitive-ecology"
                / "runtime_experiments"
                / "scientific_consensus"
            )
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def step(self, meta_analyses):
        valid = [
            m for m in meta_analyses
            if isinstance(m, dict) and m.get("publication_ready")
        ]

        if not valid:
            return {
                "primitive": self.primitive,
                "meta_analysis_count": 0,
                "publication_ready": False,
                "reason": "no_valid_meta_analyses",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        effects = [
            float(m.get("combined_effect_size", 0.0))
            for m in valid
        ]
        significances = [
            m.get("overall_significance", "ns")
            for m in valid
        ]
        i2_values = [
            float(m.get("heterogeneity", {}).get("I2", 1.0))
            for m in valid
        ]

        mean_effect = sum(effects) / len(effects)
        mean_i2 = sum(i2_values) / len(i2_values)

        significant_count = sum(1 for s in significances if s != "ns")
        significance_ratio = significant_count / len(valid)

        # Consensus strength: combines significance prevalence and low heterogeneity
        consensus_strength = (
            0.6 * significance_ratio
            + 0.4 * max(0.0, 1.0 - mean_i2)
        )

        # Cross-protocol consistency: low dispersion of effect sizes
        if len(effects) > 1:
            variance = sum(
                (x - mean_effect) ** 2 for x in effects
            ) / len(effects)
            consistency = max(0.0, 1.0 - variance)
        else:
            consistency = 1.0

        replication_robustness = (
            0.5 * consensus_strength
            + 0.5 * consistency
        )

        if consensus_strength >= 0.95:
            confidence = "very_high"
        elif consensus_strength >= 0.85:
            confidence = "high"
        elif consensus_strength >= 0.70:
            confidence = "moderate"
        else:
            confidence = "preliminary"

        result = {
            "primitive": self.primitive,
            "meta_analysis_count": len(valid),
            "mean_effect_size": round(mean_effect, 6),
            "mean_heterogeneity_I2": round(mean_i2, 6),
            "significant_ratio": round(significance_ratio, 6),
            "consensus_strength_index": round(consensus_strength, 6),
            "cross_protocol_consistency": round(consistency, 6),
            "replication_robustness_index": round(
                replication_robustness, 6
            ),
            "scientific_confidence_level": confidence,
            "publication_ready": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self._archive(result)
        return result

    def _archive(self, result):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = (
            self.archive_dir
            / f"scientific_consensus_{timestamp}.json"
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    from pprint import pprint

    sample = [
        {
            "combined_effect_size": 0.46,
            "overall_significance": "p<0.001",
            "heterogeneity": {"I2": 0.0},
            "publication_ready": True,
        },
        {
            "combined_effect_size": 0.43,
            "overall_significance": "p<0.01",
            "heterogeneity": {"I2": 0.05},
            "publication_ready": True,
        },
    ]

    pprint(ScientificConsensusTracker().step(sample))
