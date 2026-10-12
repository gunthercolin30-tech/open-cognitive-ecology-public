"""Y6 — independent_correlation_replication.

Replicates the empirical phenomenology correlation programme across
independent labs, external teams, and independent architectures.

This module is intentionally an orchestrator. It reuses existing Y1-Y5
correlation outputs and H-axis replication infrastructure instead of creating
new statistical or replication engines.

Epistemic scope:
- correlations only
- independent replication status only
- functional conclusion only
- phenomenology undetermined
- no proof of consciousness, subjectivity, sentience, qualia, or phenomenology
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

PRIMITIVE = "INDEPENDENT_CORRELATION_REPLICATION"


class IndependentCorrelationReplication:
    """Y6 orchestrator for independent replication of Y1-Y5 correlations.

    The class reads persisted outputs when available and accepts explicit test
    payloads for fast deterministic tests. It does not scan the repository.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "independent_correlation_replication"
        self.latest_file = self.base_dir / "independent_correlation_replication.json"
        self.history_file = self.base_dir / "independent_correlation_replication_history.jsonl"
        self.report_file = self.base_dir / "independent_correlation_replication.md"
        self.prometheus_file = self.base_dir / "independent_correlation_replication.prom"

    def _now(self, payload: Dict[str, Any] | None = None) -> str:
        if payload and payload.get("timestamp_utc"):
            return str(payload["timestamp_utc"])
        return datetime.now(timezone.utc).isoformat()

    def _score(self, value: Any, default: float = 0.0) -> float:
        try:
            x = float(value)
        except Exception:
            return default
        return max(0.0, min(1.0, x))

    def _load_json(self, relative: str) -> Dict[str, Any]:
        path = self.root / relative
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        explicit = payload.get("context")
        if isinstance(explicit, dict):
            return explicit
        return {
            "registry": self._load_json("phenomenology_correlation_registry/phenomenology_correlation_registry.json"),
            "candidate_metrics": self._load_json("phenomenology_candidate_metrics/phenomenology_candidate_metrics.json"),
            "architecture_comparison": self._load_json("multi_architecture_comparator/multi_architecture_comparator.json"),
            "correlation_engine": self._load_json("phenomenology_correlation_engine/phenomenology_correlation_engine.json"),
            "prediction_engine": self._load_json("phenomenology_prediction_engine/phenomenology_prediction_engine.json"),
            "replication_confidence": self._load_json("external_validation/replication_evidence/latest_replication_confidence_estimate.json"),
            "independent_observatory": self._load_json("external_validation/independent_validation_observatory/latest_independent_validation_observatory.json"),
        }

    def _replication_inputs(self, payload: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        records = payload.get("replications")
        if isinstance(records, list):
            return [r for r in records if isinstance(r, dict)]

        predictions = ctx.get("prediction_engine", {}).get("predictions", [])
        if not isinstance(predictions, list):
            predictions = []
        correlation_evidence = self._score(ctx.get("correlation_engine", {}).get("correlation_evidence_strength"), 0.5)
        prediction_readiness = self._score(ctx.get("prediction_engine", {}).get("prediction_program_readiness"), 0.5)
        baseline_support = round(mean([correlation_evidence, prediction_readiness]), 4)

        generated = []
        for idx, prediction in enumerate(predictions[:4], start=1):
            prediction_id = str(prediction.get("prediction_id", f"Y5-PRED-{idx:03d}"))
            generated.append({
                "replication_id": f"Y6-AUTO-{idx:03d}",
                "source_prediction_id": prediction_id,
                "lab_id": "pending_independent_lab",
                "team_id": "pending_external_team",
                "architecture_id": "pending_independent_architecture",
                "observed_correlation": baseline_support,
                "expected_correlation": self._score(prediction.get("prediction_confidence"), baseline_support),
                "replicated": baseline_support >= 0.65,
                "independent": False,
                "status": "pending_independent_replication",
            })
        return generated

    def _summarize_replications(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        count = len(records)
        independent_count = sum(1 for r in records if bool(r.get("independent")))
        replicated = [r for r in records if bool(r.get("replicated"))]
        rejected = [r for r in records if r.get("replicated") is False and r.get("status") in {"rejected", "not_replicated", "failed_replication"}]
        pending = [r for r in records if str(r.get("status", "")).startswith("pending")]

        deltas: List[float] = []
        support_scores: List[float] = []
        for r in records:
            observed = self._score(r.get("observed_correlation"), 0.0)
            expected = self._score(r.get("expected_correlation"), observed)
            deltas.append(max(0.0, 1.0 - abs(observed - expected)))
            support_scores.append(observed)

        agreement = mean(deltas) if deltas else 0.0
        support = mean(support_scores) if support_scores else 0.0
        independence = min(1.0, independent_count / max(1, count)) if count else 0.0
        replication_rate = len(replicated) / count if count else 0.0
        confidence = round(mean([agreement, support, independence, replication_rate]) if count else 0.0, 4)

        if count == 0:
            status = "no_replication_data"
        elif independent_count == 0:
            status = "pending_independent_replication"
        elif confidence >= 0.75 and replication_rate >= 0.6:
            status = "independently_replicated"
        elif len(rejected) > len(replicated):
            status = "replication_rejected"
        else:
            status = "partially_replicated"

        return {
            "replication_status": status,
            "replication_count": count,
            "independent_replication_count": independent_count,
            "replicated_correlation_count": len(replicated),
            "rejected_correlation_count": len(rejected),
            "pending_replication_count": len(pending),
            "replication_confidence": confidence,
            "replication_agreement_score": round(agreement, 4),
            "replication_support_score": round(support, 4),
            "replication_independence_score": round(independence, 4),
            "replication_rate": round(replication_rate, 4),
            "replicated_correlations": [r.get("source_prediction_id") for r in replicated],
            "rejected_correlations": [r.get("source_prediction_id") for r in rejected],
        }

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.latest_file.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, sort_keys=True) + "\n")
        self.report_file.write_text(self._report(result), encoding="utf-8")
        self.prometheus_file.write_text(self._prometheus(result), encoding="utf-8")
        return {
            "json": str(self.latest_file),
            "history": str(self.history_file),
            "report": str(self.report_file),
            "prometheus": str(self.prometheus_file),
        }

    def _report(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Y6 — Independent Correlation Replication",
            "",
            f"- primitive: {PRIMITIVE}",
            f"- replication_status: {result.get('replication_status')}",
            f"- replication_count: {result.get('replication_count')}",
            f"- independent_replication_count: {result.get('independent_replication_count')}",
            f"- replication_confidence: {result.get('replication_confidence')}",
            "- correlations_only: true",
            "- functional_conclusion_only: true",
            "- consciousness_proof_claimed: false",
            "- phenomenology_proof_claimed: false",
            "- phenomenology_undetermined: true",
            "",
            "## Replicated correlations",
        ]
        for item in result.get("replicated_correlations", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("## Rejected correlations")
        for item in result.get("rejected_correlations", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("Conclusion: functional conclusion only; phenomenology undetermined.")
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Dict[str, Any]) -> str:
        success = 1 if result.get("success") else 0
        return "\n".join([
            "# HELP oce_independent_correlation_replication_success Y6 functional success flag",
            "# TYPE oce_independent_correlation_replication_success gauge",
            f"oce_independent_correlation_replication_success {success}",
            "# HELP oce_independent_correlation_replication_count Independent correlation replication count",
            "# TYPE oce_independent_correlation_replication_count gauge",
            f"oce_independent_correlation_replication_count {result.get('replication_count', 0)}",
            "# HELP oce_independent_correlation_replication_confidence Independent correlation replication confidence",
            "# TYPE oce_independent_correlation_replication_confidence gauge",
            f"oce_independent_correlation_replication_confidence {result.get('replication_confidence', 0)}",
        ]) + "\n"

    def step(self, payload: Dict[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        payload = payload or {}
        ctx = self._context(payload)
        records = self._replication_inputs(payload, ctx)
        summary = self._summarize_replications(records)

        result: Dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "timestamp_utc": self._now(payload),
            **summary,
            "replications": records,
            "source_context_present": {k: bool(v) for k, v in ctx.items()},
            "correlations_only": True,
            "independent_replication_only": True,
            "functional_conclusion_only": True,
            "consciousness_proof_claimed": False,
            "subjectivity_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "phenomenology_undetermined": True,
            "epistemic_scope": "functional_statistical_correlation_replication_only",
            "diagnostics": {
                "uses_y1_y5_outputs": True,
                "uses_existing_replication_infrastructure": True,
                "no_global_repository_scan": True,
                "claim_scope": "functional conclusion only; phenomenology undetermined",
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
