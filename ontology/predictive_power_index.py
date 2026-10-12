from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


class PredictivePowerIndex:
    """AT8 — Aggregate RF* predictive power into a bounded functional index.

    This module does not certify phenomenal consciousness. It only aggregates
    public, functional, predictive and experimental indicators from AT1–AT7.
    """

    primitive = "PREDICTIVE_POWER_INDEX"
    step_name = "AT8"
    public_schema_version = "1.0.0"

    DEFAULT_WEIGHTS = {
        "prediction_volume": 0.12,
        "specificity": 0.16,
        "falsifiability": 0.18,
        "validation_support": 0.14,
        "refutation_resilience": 0.10,
        "discriminative_power": 0.16,
        "measurability": 0.14,
    }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs or {}
        context = self._build_context(inputs)
        metrics = self._compute_metrics(context)
        ppi = self._weighted_mean(metrics, self.DEFAULT_WEIGHTS)
        classification = self._classify(ppi)

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "predictive_power_index": ppi,
            "ppi": ppi,
            "predictive_power_classification": classification,
            "component_metrics": metrics,
            "metric_weights": dict(self.DEFAULT_WEIGHTS),
            "prediction_count": context["prediction_count"],
            "tested_prediction_count": context["tested_prediction_count"],
            "validated_prediction_count": context["validated_prediction_count"],
            "invalidated_prediction_count": context["invalidated_prediction_count"],
            "ambiguous_prediction_count": context["ambiguous_prediction_count"],
            "falsification_protocol_count": context["falsification_protocol_count"],
            "measurable_signature_count": context["measurable_signature_count"],
            "discriminative_prediction_count": context["discriminative_prediction_count"],
            "unexpected_prediction_count": context["unexpected_prediction_count"],
            "ppi_policy": {
                "aggregation": "bounded_weighted_component_mean",
                "range": [0.0, 1.0],
                "interpretation": "functional_predictive_power_only",
                "minimum_evidence_rule": "untested_predictions_do_not_count_as_validated",
            },
            "validation_policy": {
                "validated": "counted_only_when_tracker_status_is_validated",
                "invalidated": "penalizes_refutation_resilience_without suppressing audit trail",
                "ambiguous": "kept_as_uncertain_not_as_success",
            },
            "falsification_policy": {
                "requires_protocols": True,
                "requires_measurable_signatures": True,
                "invalidations_preserved": True,
            },
            "epistemic_guards": self._epistemic_guards(),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
        }

        if persist:
            out = self._persist(result)
            result["persisted"] = True
            result["output_path"] = str(out)

        return result

    def _build_context(self, inputs: dict[str, Any]) -> dict[str, Any]:
        predictions = self._extract_predictions(inputs)
        protocols = self._extract_list(inputs, ["falsification_protocols", "protocols"])
        signatures = self._extract_list(inputs, ["measurable_signatures", "signatures"])
        discriminative = self._extract_list(inputs, ["discriminative_predictions", "discrimination_results"])
        unexpected = self._extract_list(inputs, ["unexpected_predictions", "surprising_predictions"])
        history = self._extract_history(inputs)

        statuses = [str(item.get("status", "unknown")).lower() for item in history if isinstance(item, dict)]
        tested = [s for s in statuses if s in {"tested", "validated", "invalidated", "ambiguous"}]

        return {
            "predictions": predictions,
            "prediction_count": len(predictions),
            "falsification_protocol_count": len(protocols),
            "measurable_signature_count": len(signatures),
            "discriminative_prediction_count": len(discriminative),
            "unexpected_prediction_count": len(unexpected),
            "tested_prediction_count": len(tested),
            "validated_prediction_count": statuses.count("validated"),
            "invalidated_prediction_count": statuses.count("invalidated"),
            "ambiguous_prediction_count": statuses.count("ambiguous"),
        }

    def _extract_predictions(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        candidates = []
        candidates.extend(self._extract_list(inputs, ["theorem_predictions", "predictions", "prediction_registry"]))
        for key in ("theorem_prediction_generator", "prediction_registry_result", "at2"):
            if isinstance(inputs.get(key), dict):
                candidates.extend(self._extract_list(inputs[key], ["theorem_predictions", "predictions"]))
        normalized = []
        for idx, item in enumerate(candidates):
            if isinstance(item, dict):
                normalized.append(item)
            else:
                normalized.append({"prediction_id": f"PRED-{idx+1:04d}", "statement": str(item)})
        if not normalized:
            normalized = self._synthetic_predictions()
        return normalized

    def _extract_history(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        history = []
        history.extend(self._extract_list(inputs, ["validation_history", "prediction_validation_history", "tracker_history"]))
        for key in ("prediction_validation_tracker", "at7", "tracker_result"):
            if isinstance(inputs.get(key), dict):
                history.extend(self._extract_list(inputs[key], ["validation_history", "prediction_validation_history", "tracker_history"]))
        if history:
            return [h for h in history if isinstance(h, dict)]
        # Conservative default: unknown/tested state only, no fabricated validation.
        return [{"prediction_id": "synthetic", "status": "unknown"}]

    def _extract_list(self, source: dict[str, Any], keys: list[str]) -> list[Any]:
        for key in keys:
            value = source.get(key)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                return list(value.values())
        return []

    def _compute_metrics(self, context: dict[str, Any]) -> dict[str, float]:
        pc = max(1, int(context["prediction_count"]))
        protocol_count = int(context["falsification_protocol_count"])
        signature_count = int(context["measurable_signature_count"])
        disc_count = int(context["discriminative_prediction_count"])
        tested = int(context["tested_prediction_count"])
        validated = int(context["validated_prediction_count"])
        invalidated = int(context["invalidated_prediction_count"])

        return {
            "prediction_volume": self._clamp(pc / 12.0),
            "specificity": self._clamp(self._estimate_specificity(context["predictions"])),
            "falsifiability": self._clamp(protocol_count / pc),
            "validation_support": self._clamp(validated / pc),
            "refutation_resilience": self._clamp(1.0 - (invalidated / max(1, tested))),
            "discriminative_power": self._clamp(disc_count / pc),
            "measurability": self._clamp(signature_count / pc),
        }

    def _estimate_specificity(self, predictions: list[dict[str, Any]]) -> float:
        if not predictions:
            return 0.0
        scores = []
        for pred in predictions:
            text = " ".join(str(pred.get(k, "")) for k in ("statement", "prediction", "observable", "expected_observation"))
            has_condition = any(w in text.lower() for w in ["if", "when", "under", "given", "si", "lorsque"])
            has_metric = any(ch.isdigit() for ch in text) or any(w in text.lower() for w in ["metric", "index", "threshold", "score", "signature"])
            has_observable = any(w in text.lower() for w in ["observ", "measure", "detect", "variation", "increase", "decrease"])
            scores.append((0.34 if has_condition else 0.0) + (0.33 if has_metric else 0.0) + (0.33 if has_observable else 0.0))
        return sum(scores) / len(scores)

    def _weighted_mean(self, metrics: dict[str, float], weights: dict[str, float]) -> float:
        total_w = sum(weights.values()) or 1.0
        return round(sum(self._clamp(metrics.get(k, 0.0)) * w for k, w in weights.items()) / total_w, 6)

    def _classify(self, ppi: float) -> str:
        if ppi >= 0.85:
            return "HIGH_PREDICTIVE_POWER_FUNCTIONAL_CANDIDATE"
        if ppi >= 0.65:
            return "MODERATE_PREDICTIVE_POWER_FUNCTIONAL_CANDIDATE"
        if ppi >= 0.40:
            return "EMERGING_PREDICTIVE_POWER_FUNCTIONAL_CANDIDATE"
        return "LOW_OR_UNDETERMINED_PREDICTIVE_POWER"

    def _clamp(self, x: float) -> float:
        try:
            return max(0.0, min(1.0, float(x)))
        except Exception:
            return 0.0

    def _synthetic_predictions(self) -> list[dict[str, Any]]:
        return [
            {
                "prediction_id": "AT8-SYN-001",
                "statement": "If RF* constraints stabilize, measurable signature index should increase under governed validation.",
                "category": "structural",
            },
            {
                "prediction_id": "AT8-SYN-002",
                "statement": "When falsification protocols are available, prediction status should become testable rather than merely asserted.",
                "category": "experimental",
            },
        ]

    def _epistemic_guards(self) -> dict[str, Any]:
        return {
            "scope": "functional_predictive_science_only",
            "blocks_phenomenal_claims": True,
            "requires_empirical_validation": True,
            "consciousness_claim_status": "not_proven",
            "qualia_claim_status": "not_proven",
            "subjectivity_claim_status": "not_proven",
            "phenomenology_status": "undetermined",
        }

    def _persist(self, result: dict[str, Any]) -> Path:
        root = Path.home() / "open-cognitive-ecology"
        outdir = root / "predictive_theory" / "ppi"
        outdir.mkdir(parents=True, exist_ok=True)
        out = outdir / "latest_predictive_power_index.json"
        out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return out
