from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


class ReplicationEvidenceSynthesizer:
    """Consolidates independent replication evidence into a traceable synthesis.

    This primitive belongs to H14. It does not claim phenomenological
    subjectivity; it only aggregates functional, reproducible and externally
    auditable indicators.
    """

    primitive = "replication_evidence_synthesizer"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "replication_evidence"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_json_if_exists(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def step(self, evidence_records: list[dict[str, Any]] | None = None, persist: bool = True) -> dict[str, Any]:
        if evidence_records is None:
            evidence_records = [
                {
                    "source": "H13_public_campaign_bootstrap",
                    "independent": True,
                    "reproducible": False,
                    "validated": False,
                    "traceability_score": 1.0,
                    "governance_score": 0.95,
                    "confidence": 0.25,
                }
            ]

        normalized: list[dict[str, Any]] = []
        for idx, record in enumerate(evidence_records, start=1):
            normalized.append(
                {
                    "evidence_id": record.get("evidence_id", f"H14-EVIDENCE-{idx:03d}"),
                    "source": str(record.get("source", "unknown")),
                    "independent": bool(record.get("independent", False)),
                    "reproducible": bool(record.get("reproducible", False)),
                    "validated": bool(record.get("validated", False)),
                    "traceability_score": float(record.get("traceability_score", 0.0)),
                    "governance_score": float(record.get("governance_score", 0.0)),
                    "confidence": float(record.get("confidence", 0.0)),
                }
            )

        evidence_count = len(normalized)
        validated_replications = sum(1 for r in normalized if r["validated"])
        independent_evidence_count = sum(1 for r in normalized if r["independent"])
        reproducible_evidence_count = sum(1 for r in normalized if r["reproducible"])

        traceability_score = mean([r["traceability_score"] for r in normalized]) if normalized else 0.0
        governance_score = mean([r["governance_score"] for r in normalized]) if normalized else 0.0
        mean_confidence = mean([r["confidence"] for r in normalized]) if normalized else 0.0

        replication_evidence_score = mean(
            [
                independent_evidence_count / evidence_count if evidence_count else 0.0,
                reproducible_evidence_count / evidence_count if evidence_count else 0.0,
                validated_replications / evidence_count if evidence_count else 0.0,
                traceability_score,
                governance_score,
                mean_confidence,
            ]
        )

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "evidence_count": evidence_count,
            "independent_evidence_count": independent_evidence_count,
            "reproducible_evidence_count": reproducible_evidence_count,
            "validated_replications": validated_replications,
            "traceability_score": round(traceability_score, 6),
            "governance_score": round(governance_score, 6),
            "mean_confidence": round(mean_confidence, 6),
            "replication_evidence_score": round(replication_evidence_score, 6),
            "evidence_records": normalized,
            "epistemic_scope": "functional_validation_only_no_phenomenological_claim",
        }

        if persist:
            path = self.output_dir / "latest_replication_evidence_synthesis.json"
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["state_path"] = str(path)

        return result

