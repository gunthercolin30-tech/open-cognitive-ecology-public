from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ReplicationResultNormalizer:
    """Normalizes heterogeneous replication outcomes into comparable metrics."""

    primitive = "replication_result_normalizer"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "replication_evidence"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _normalize_status(self, status: str) -> str:
        value = str(status or "unknown").strip().lower()
        if value in {"validated", "success", "successful", "replicated", "ok", "pass", "passed"}:
            return "validated"
        if value in {"partial", "partially_validated", "mixed", "inconclusive"}:
            return "partial"
        if value in {"failed", "failure", "not_replicated", "ko", "fail"}:
            return "failed"
        return "pending"

    def step(self, replication_results: list[dict[str, Any]] | None = None, persist: bool = True) -> dict[str, Any]:
        if replication_results is None:
            replication_results = [
                {
                    "replication_id": "H13-CAMPAIGN-BOOTSTRAP",
                    "status": "pending",
                    "independence_score": 1.0,
                    "methodological_completeness": 0.75,
                    "artifact_integrity": 1.0,
                    "reported_error_count": 0,
                }
            ]

        normalized = []
        for idx, item in enumerate(replication_results, start=1):
            status = self._normalize_status(str(item.get("status", "pending")))
            validated = status == "validated"
            partial = status == "partial"
            failed = status == "failed"
            confidence_weight = 1.0 if validated else 0.5 if partial else 0.0 if failed else 0.25
            normalized.append(
                {
                    "replication_id": item.get("replication_id", f"H14-RESULT-{idx:03d}"),
                    "normalized_status": status,
                    "validated": validated,
                    "partial": partial,
                    "failed": failed,
                    "independence_score": float(item.get("independence_score", 0.0)),
                    "methodological_completeness": float(item.get("methodological_completeness", 0.0)),
                    "artifact_integrity": float(item.get("artifact_integrity", 0.0)),
                    "reported_error_count": int(item.get("reported_error_count", 0)),
                    "confidence_weight": confidence_weight,
                }
            )

        total = len(normalized)
        validated_replications = sum(1 for r in normalized if r["validated"])
        partial_replications = sum(1 for r in normalized if r["partial"])
        failed_replications = sum(1 for r in normalized if r["failed"])
        pending_replications = total - validated_replications - partial_replications - failed_replications
        external_replication_count = validated_replications + partial_replications

        comparable_result_score = (
            sum(r["confidence_weight"] for r in normalized) / total if total else 0.0
        )

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "result_count": total,
            "external_replication_count": external_replication_count,
            "validated_replications": validated_replications,
            "partial_replications": partial_replications,
            "failed_replications": failed_replications,
            "pending_replications": pending_replications,
            "comparable_result_score": round(comparable_result_score, 6),
            "normalized_results": normalized,
            "epistemic_scope": "functional_replication_result_normalization",
        }

        if persist:
            path = self.output_dir / "latest_replication_result_normalization.json"
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["state_path"] = str(path)

        return result

