from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


class ReplicationConfidenceEstimator:
    """Estimates confidence in external replication evidence without overclaiming."""

    primitive = "replication_confidence_estimator"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "replication_evidence"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def step(
        self,
        evidence_synthesis: dict[str, Any] | None = None,
        normalized_results: dict[str, Any] | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        if evidence_synthesis is None:
            evidence_synthesis = {}
        if normalized_results is None:
            normalized_results = {}

        evidence_score = float(evidence_synthesis.get("replication_evidence_score", 0.25))
        traceability_score = float(evidence_synthesis.get("traceability_score", 1.0))
        governance_score = float(evidence_synthesis.get("governance_score", 0.95))
        comparable_result_score = float(normalized_results.get("comparable_result_score", 0.25))
        validated_replications = int(normalized_results.get("validated_replications", evidence_synthesis.get("validated_replications", 0)))
        external_replication_count = int(normalized_results.get("external_replication_count", 0))

        replication_confidence_score = mean(
            [
                evidence_score,
                traceability_score,
                governance_score,
                comparable_result_score,
                min(1.0, validated_replications / 3.0),
                min(1.0, external_replication_count / 5.0),
            ]
        )

        if validated_replications > 0 and replication_confidence_score >= 0.75:
            confidence_class = "externally_supported"
        elif external_replication_count > 0 and replication_confidence_score >= 0.5:
            confidence_class = "partially_supported"
        else:
            confidence_class = "campaign_deployed_pending_independent_replication"

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "external_replication_count": external_replication_count,
            "validated_replications": validated_replications,
            "replication_confidence_score": round(replication_confidence_score, 6),
            "confidence_class": confidence_class,
            "scientific_claim_authorized": validated_replications > 0,
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "functional_indicators_only",
            "diagnostics": {
                "evidence_score": evidence_score,
                "traceability_score": traceability_score,
                "governance_score": governance_score,
                "comparable_result_score": comparable_result_score,
                "requires_independent_replications_for_stronger_claim": validated_replications == 0,
            },
        }

        if persist:
            path = self.output_dir / "latest_replication_confidence_estimate.json"
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["state_path"] = str(path)

        return result

