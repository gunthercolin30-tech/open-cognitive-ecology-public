
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class ScientificTheoryConfidenceEngine:
    primitive = "SCIENTIFIC_THEORY_CONFIDENCE_ENGINE"

    def __init__(self, archive_dir=None):
        if archive_dir is None:
            archive_dir = (
                Path.home()
                / "open-cognitive-ecology"
                / "runtime_experiments"
                / "scientific_theory_confidence"
            )
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def step(self, consensus_result):
        if (
            not isinstance(consensus_result, dict)
            or not consensus_result.get("publication_ready")
        ):
            return {
                "primitive": self.primitive,
                "publication_ready": False,
                "reason": "invalid_consensus_result",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        consensus = float(consensus_result.get("consensus_strength_index", 0.0))
        consistency = float(
            consensus_result.get("cross_protocol_consistency", 0.0)
        )
        robustness = float(
            consensus_result.get("replication_robustness_index", 0.0)
        )

        theory_confidence = (
            0.4 * consensus
            + 0.3 * consistency
            + 0.3 * robustness
        )

        empirical_support = 0.5 * consensus + 0.5 * robustness
        credibility = 0.6 * theory_confidence + 0.4 * consistency
        falsification_resilience = min(1.0, 0.5 * robustness + 0.5 * consistency)

        if theory_confidence >= 0.98:
            status = "highly_supported"
        elif theory_confidence >= 0.90:
            status = "strongly_supported"
        elif theory_confidence >= 0.75:
            status = "provisionally_supported"
        else:
            status = "tentative"

        result = {
            "primitive": self.primitive,
            "theory_confidence_score": round(theory_confidence, 6),
            "empirical_support_strength": round(empirical_support, 6),
            "theoretical_credibility_index": round(credibility, 6),
            "falsification_resilience": round(falsification_resilience, 6),
            "scientific_theory_status": status,
            "publication_ready": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self._archive(result)
        return result

    def _archive(self, result):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = (
            self.archive_dir
            / f"scientific_theory_confidence_{timestamp}.json"
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    from pprint import pprint

    sample = {
        "consensus_strength_index": 0.99,
        "cross_protocol_consistency": 0.999775,
        "replication_robustness_index": 0.994887,
        "publication_ready": True,
    }

    pprint(ScientificTheoryConfidenceEngine().step(sample))
