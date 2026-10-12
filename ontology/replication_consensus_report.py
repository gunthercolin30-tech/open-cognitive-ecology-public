from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


class ReplicationConsensusReport:
    primitive = "replication_consensus_report"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "civilizational_scientific_certification"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"items": data if isinstance(data, list) else []}
        except Exception:
            return {}

    def _signal(self, relative: str) -> dict[str, Any]:
        return self._read_json(self.root / relative)

    def step(self, external_synthesis_state: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        synthesis = external_synthesis_state or self._signal("external_validation/civilizational_scientific_certification/latest_external_validation_synthesis_report.json")
        h18_stats = self._signal("external_validation/independent_validation_observatory/latest_replication_statistics_engine.json")
        evidence = self._signal("external_validation/replication_evidence/latest_replication_confidence_estimate.json")
        consensus = self._signal("external_validation/scientific_consensus_measurement/latest_scientific_consensus_analysis.json")
        feedback = self._signal("external_validation/github_replication_feedback/latest_github_replication_feedback.json")

        external_replication_count = int(synthesis.get("external_replication_count", h18_stats.get("external_replication_count", 0)) or 0)
        validation_stability_index = float(synthesis.get("validation_stability_index", h18_stats.get("validation_stability_index", 0.0)) or 0.0)
        scientific_consensus = float(synthesis.get("scientific_consensus", consensus.get("scientific_consensus_score", consensus.get("consensus_score", 0.0))) or 0.0)
        replication_confidence = float(evidence.get("replication_confidence", evidence.get("confidence", 0.0)) or 0.0)
        replication_feedback_count = int(synthesis.get("replication_feedback_count", feedback.get("replication_feedback_count", 0)) or 0)

        replication_presence_score = min(1.0, external_replication_count / 1.0)
        feedback_score = min(1.0, replication_feedback_count / 1.0)
        consensus_components = [
            replication_presence_score,
            validation_stability_index,
            scientific_consensus,
            replication_confidence,
            feedback_score,
            float(synthesis.get("external_validation_synthesis_score", 0.0) or 0.0),
        ]
        replication_consensus_score = mean([max(0.0, min(1.0, x)) for x in consensus_components])

        if replication_consensus_score >= 0.85:
            consensus_class = "strong_functional_replication_consensus"
        elif replication_consensus_score >= 0.65:
            consensus_class = "moderate_functional_replication_consensus"
        elif replication_consensus_score > 0.0:
            consensus_class = "emerging_functional_replication_consensus"
        else:
            consensus_class = "insufficient_replication_consensus"

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "H19",
            "replication_consensus_ready": True,
            "external_replication_count": external_replication_count,
            "replication_feedback_count": replication_feedback_count,
            "validation_stability_index": round(max(0.0, min(1.0, validation_stability_index)), 6),
            "scientific_consensus": round(max(0.0, min(1.0, scientific_consensus)), 6),
            "replication_confidence": round(max(0.0, min(1.0, replication_confidence)), 6),
            "replication_consensus_score": round(replication_consensus_score, 6),
            "replication_consensus_class": consensus_class,
            "independent_replication_documented": external_replication_count > 0,
            "consensus_measurable": replication_consensus_score > 0.0,
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "functional_indicators_only",
            "non_closure_compliant": True,
        }

        if persist:
            state_path = self.output_dir / "latest_replication_consensus_report.json"
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            history_path = self.output_dir / "replication_consensus_report.jsonl"
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)
        return result
