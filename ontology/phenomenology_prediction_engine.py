"""Y5 — phenomenology_prediction_engine.

Produces falsifiable, correlation-derived predictions for the empirical
phenomenology correlation programme. This module never claims consciousness,
sentience, qualia, subjective experience, or phenomenological proof.

Scope:
- falsifiable predictions only
- correlation-derived predictions only
- functional conclusion only
- phenomenology undetermined
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

PRIMITIVE = "PHENOMENOLOGY_PREDICTION_ENGINE"


class PhenomenologyPredictionEngine:
    """Generate falsifiable predictions from Y1-Y4 outputs.

    The output is explicitly limited to observable, functional, statistical
    predictions. It is not evidence of consciousness or phenomenology.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "phenomenology_prediction_engine"
        self.latest_file = self.base_dir / "phenomenology_prediction_engine.json"
        self.history_file = self.base_dir / "phenomenology_prediction_engine_history.jsonl"
        self.report_file = self.base_dir / "phenomenology_prediction_engine.md"
        self.prometheus_file = self.base_dir / "phenomenology_prediction_engine.prom"

    def _now(self, payload: Dict[str, Any] | None = None) -> str:
        if payload and payload.get("timestamp_utc"):
            return str(payload["timestamp_utc"])
        return datetime.now(timezone.utc).isoformat()

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _latest(self, relative: str) -> Dict[str, Any]:
        return self._load_json(self.root / relative)

    def _score(self, value: Any, default: float = 0.5) -> float:
        try:
            x = float(value)
        except Exception:
            return default
        return max(0.0, min(1.0, x))

    def _context(self) -> Dict[str, Any]:
        return {
            "registry": self._latest("phenomenology_correlation_registry/phenomenology_correlation_registry.json"),
            "candidate_metrics": self._latest("phenomenology_candidate_metrics/phenomenology_candidate_metrics.json"),
            "architecture_comparison": self._latest("multi_architecture_comparator/multi_architecture_comparator.json"),
            "correlation_engine": self._latest("phenomenology_correlation_engine/phenomenology_correlation_engine.json"),
        }

    def _prediction(self, prediction_id: str, statement: str, variables: List[str], expected_direction: str, threshold: float, test_protocol: str, horizon: str, confidence: float, source: str) -> Dict[str, Any]:
        return {
            "prediction_id": prediction_id,
            "statement": statement,
            "observable_variables": variables,
            "expected_direction": expected_direction,
            "falsification_threshold": round(threshold, 4),
            "test_protocol": test_protocol,
            "time_horizon": horizon,
            "prediction_confidence": round(self._score(confidence), 4),
            "derived_from": source,
            "falsifiable": True,
            "claim_scope": "functional_statistical_prediction_only",
        }

    def _build_predictions(self, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        metrics = ctx.get("candidate_metrics", {})
        arch = ctx.get("architecture_comparison", {})
        corr = ctx.get("correlation_engine", {})
        registry = ctx.get("registry", {})

        composite = self._score(metrics.get("candidate_metrics_composite_score"), 0.5)
        evidence = self._score(corr.get("correlation_evidence_strength"), 0.5)
        readiness = self._score(corr.get("correlation_program_readiness"), 0.5)
        arch_ready = self._score(arch.get("multi_architecture_comparison_readiness"), 0.5)
        registry_ready = self._score(registry.get("correlation_program_readiness"), 0.5)

        confidence_base = mean([composite, evidence, readiness, arch_ready, registry_ready])

        return [
            self._prediction(
                "Y5-PRED-001",
                "If autobiographical coherence remains high across repeated runs, candidate phenomenology metric stability should increase or remain stable.",
                ["autobiographical_coherence", "candidate_metrics_composite_score", "run_index"],
                "positive_or_stable",
                max(0.05, round(0.15 * confidence_base, 4)),
                "Compare candidate metric composite drift across repeated persisted Y2/Y4 runs.",
                "short_longitudinal",
                confidence_base,
                "Y2+Y4",
            ),
            self._prediction(
                "Y5-PRED-002",
                "Distributed OCE architecture should score higher than simple agents on integrated functional comparison metrics.",
                ["open_cognitive_ecology_score", "simple_agent_score", "architecture_rank"],
                "OCE_greater_than_simple_agent",
                0.1,
                "Run Y3 comparison matrix on OCE and simple agent baselines and test rank separation.",
                "cross_architecture",
                mean([arch_ready, composite]),
                "Y3+Y2",
            ),
            self._prediction(
                "Y5-PRED-003",
                "Strong Y4 correlation clusters should predict higher readiness for independent replication in Y6.",
                ["cluster_strength", "correlation_evidence_strength", "replication_readiness"],
                "positive",
                0.1,
                "Measure whether high-correlation clusters are reproduced in independent Y6 datasets.",
                "replication",
                mean([evidence, readiness]),
                "Y4",
            ),
            self._prediction(
                "Y5-PRED-004",
                "If candidate metrics are weak or inconsistent, the programme should produce lower prediction confidence rather than stronger phenomenological claims.",
                ["candidate_metrics_composite_score", "prediction_confidence", "phenomenology_claim_flag"],
                "confidence_decreases_without_claim_increase",
                0.01,
                "Degrade Y2 inputs and verify prediction confidence decreases while proof flags remain false.",
                "degradation_test",
                mean([registry_ready, 1.0 - abs(composite - 0.5)]),
                "Y1+Y2+Y4",
            ),
        ]

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
            "# Y5 — Phenomenology Prediction Engine",
            "",
            f"- primitive: {PRIMITIVE}",
            f"- prediction_count: {result.get('prediction_count')}",
            f"- falsifiable_prediction_count: {result.get('falsifiable_prediction_count')}",
            f"- prediction_program_readiness: {result.get('prediction_program_readiness')}",
            f"- classification: {result.get('prediction_program_classification')}",
            "- falsifiable_predictions_only: true",
            "- correlation_derived_predictions_only: true",
            "- functional_conclusion_only: true",
            "- consciousness_proof_claimed: false",
            "- phenomenology_undetermined: true",
            "",
            "## Predictions",
        ]
        for p in result.get("predictions", []):
            lines.append(f"- {p['prediction_id']}: {p['statement']}")
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Dict[str, Any]) -> str:
        confirmed = 1 if result.get("success") else 0
        return "\n".join([
            "# HELP oce_phenomenology_prediction_engine_success Y5 functional success flag",
            "# TYPE oce_phenomenology_prediction_engine_success gauge",
            f"oce_phenomenology_prediction_engine_success {confirmed}",
            "# HELP oce_phenomenology_prediction_engine_prediction_count Number of falsifiable predictions",
            "# TYPE oce_phenomenology_prediction_engine_prediction_count gauge",
            f"oce_phenomenology_prediction_engine_prediction_count {result.get('prediction_count', 0)}",
            "# HELP oce_phenomenology_prediction_engine_readiness Prediction programme readiness",
            "# TYPE oce_phenomenology_prediction_engine_readiness gauge",
            f"oce_phenomenology_prediction_engine_readiness {result.get('prediction_program_readiness', 0)}",
        ]) + "\n"

    def step(self, payload: Dict[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        payload = payload or {}
        ctx = self._context()
        predictions = self._build_predictions(ctx)
        confidences = [self._score(p.get("prediction_confidence")) for p in predictions]
        readiness = round(mean(confidences) if confidences else 0.0, 4)
        classification = "prediction_program_ready" if readiness >= 0.65 else "prediction_program_preliminary"

        result: Dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "timestamp_utc": self._now(payload),
            "prediction_count": len(predictions),
            "falsifiable_prediction_count": sum(1 for p in predictions if p.get("falsifiable") is True),
            "prediction_program_readiness": readiness,
            "prediction_program_classification": classification,
            "predictions": predictions,
            "source_context_present": {k: bool(v) for k, v in ctx.items()},
            "falsifiable_predictions_only": True,
            "correlation_derived_predictions_only": True,
            "functional_conclusion_only": True,
            "consciousness_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "phenomenology_undetermined": True,
            "claim_scope": "falsifiable_correlation_derived_predictions_only",
            "epistemic_status": {
                "measure_functional": True,
                "hypothesis_interpretative": True,
                "phenomenology_undetermined": True,
                "no_subjective_experience_inference": True,
            },
            "input_sources": {
                "global_scan_used": False,
                "rglob_used": False,
                "targeted_persisted_outputs_only": True,
            },
        }
        if persist:
            result["artifacts"] = self._persist(result)
        else:
            result["artifacts"] = {
                "json": str(self.latest_file),
                "history": str(self.history_file),
                "report": str(self.report_file),
                "prometheus": str(self.prometheus_file),
            }
        return result
