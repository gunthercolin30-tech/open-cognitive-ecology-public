"""
AT4 — measurable_signature_builder.

Transforms RF* predictions into measurable signatures, metrics, indicators and
experimental observables while preserving strict epistemic guards.

The module does not assert phenomenal consciousness, qualia, subjectivity or
phenomenology. It only exposes functional, predictive and measurement-facing
structures that can be used by later falsification, validation and dashboard
modules.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        return default
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _slug(value: Any) -> str:
    text = str(value or "unknown").strip().lower()
    out = []
    for ch in text:
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "_":
            out.append("_")
    slug = "".join(out).strip("_")
    return slug or "unknown"


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, dict):
        return [value]
    return [value]


class MeasurableSignatureBuilder:
    """Build measurable signatures from AT2/AT3 predictive outputs."""

    primitive = "MEASURABLE_SIGNATURE_BUILDER"
    step_name = "AT4"
    public_schema_version = "1.0.0"
    status = "MEASURABLE_SIGNATURES_READY"

    epistemic_guards = {
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
        "allowed_scope": [
            "functional_prediction_measurement",
            "experimental_observable_construction",
            "quantitative_signature_generation",
            "falsifiable_metric_preparation",
        ],
        "blocked_scope": [
            "phenomenal_consciousness_proof",
            "qualia_proof",
            "subjectivity_proof",
            "ontological_closure_claim",
        ],
    }

    category_metric_templates = {
        "structural": ["constraint_density", "frame_coherence", "dependency_integrity"],
        "dynamic": ["transition_stability", "recovery_latency", "trajectory_persistence"],
        "topological": ["invariance_score", "connectivity_preservation", "boundary_stability"],
        "spectral": ["mode_separation", "spectral_coherence", "resonance_stability"],
        "developmental": ["stage_progression", "canalization_strength", "plasticity_window"],
        "collective": ["coordination_coherence", "distributed_alignment", "consensus_stability"],
        "comparative": ["discrimination_margin", "alternative_overlap", "specificity_score"],
        "governance": ["guard_integrity", "revision_traceability", "non_closure_preservation"],
        "general": ["observable_strength", "measurement_reliability", "replication_readiness"],
    }

    def _load_at3(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        direct = inputs.get("discriminative_prediction_engine") or inputs.get("at3")
        if isinstance(direct, dict):
            return dict(direct)
        try:
            from ontology.discriminative_prediction_engine import DiscriminativePredictionEngine
            return DiscriminativePredictionEngine().step(inputs=inputs, persist=False)
        except Exception as exc:
            return {"available": False, "error": str(exc), "discriminative_predictions": []}

    def _load_at2(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        direct = inputs.get("theorem_prediction_generator") or inputs.get("at2")
        if isinstance(direct, dict):
            return dict(direct)
        try:
            from ontology.theorem_prediction_generator import TheoremPredictionGenerator
            return TheoremPredictionGenerator().step(inputs=inputs, persist=False)
        except Exception as exc:
            return {"available": False, "error": str(exc), "theorem_predictions": []}

    def _extract_prediction_records(self, at3: Mapping[str, Any], at2: Mapping[str, Any], inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []

        candidates = []
        candidates.extend(_as_list(inputs.get("predictions")))
        candidates.extend(_as_list(inputs.get("theorem_predictions")))
        candidates.extend(_as_list(inputs.get("discriminative_predictions")))
        candidates.extend(_as_list(at3.get("discriminative_predictions")))
        candidates.extend(_as_list(at3.get("rf_star_discriminative_predictions")))
        candidates.extend(_as_list(at2.get("theorem_predictions")))

        for idx, item in enumerate(candidates, start=1):
            if isinstance(item, dict):
                rec = dict(item)
            else:
                rec = {"prediction": str(item)}
            pred_id = rec.get("prediction_id") or rec.get("id") or rec.get("theorem") or f"prediction_{idx:03d}"
            category = rec.get("category") or rec.get("prediction_category") or rec.get("discriminative_category") or "general"
            statement = (
                rec.get("prediction")
                or rec.get("statement")
                or rec.get("observable_prediction")
                or rec.get("description")
                or rec.get("expected_observation")
                or f"Observable consequence for {pred_id}"
            )
            confidence = _safe_float(rec.get("confidence", rec.get("prediction_confidence", 0.72)), 0.72)
            discriminative_power = _safe_float(rec.get("discriminative_power", rec.get("specificity", confidence)), confidence)
            records.append({
                "prediction_id": str(pred_id),
                "category": str(category),
                "statement": str(statement),
                "confidence": confidence,
                "discriminative_power": discriminative_power,
                "source_record": rec,
            })

        if not records:
            # Degradation-safe seed. This keeps public schema stable without claiming empirical validation.
            records.append({
                "prediction_id": "synthetic_rf_star_prediction",
                "category": "general",
                "statement": "RF* should yield operationally measurable functional signatures under explicit epistemic guards.",
                "confidence": 0.5,
                "discriminative_power": 0.5,
                "source_record": {"synthetic": True, "reason": "no_prediction_input_available"},
            })
        return records

    def _templates_for(self, category: str) -> List[str]:
        key = _slug(category)
        if key in self.category_metric_templates:
            return self.category_metric_templates[key]
        for known, templates in self.category_metric_templates.items():
            if known in key:
                return templates
        return self.category_metric_templates["general"]

    def _build_signature(self, record: Mapping[str, Any], ordinal: int) -> Dict[str, Any]:
        category = str(record.get("category") or "general")
        pred_id = str(record.get("prediction_id") or f"prediction_{ordinal:03d}")
        templates = self._templates_for(category)
        confidence = _safe_float(record.get("confidence"), 0.5)
        discriminative_power = _safe_float(record.get("discriminative_power"), confidence)
        reliability = round((confidence + discriminative_power + 0.75) / 3.0, 6)
        falsifiability = round(min(1.0, 0.55 + 0.25 * len(templates) / 3.0 + 0.20 * discriminative_power), 6)
        specificity = round((discriminative_power * 0.65) + (confidence * 0.35), 6)
        measurement_readiness = round((reliability + falsifiability + specificity) / 3.0, 6)

        metrics = []
        observables = []
        indicators = []
        for metric in templates:
            metric_id = f"{_slug(pred_id)}__{_slug(metric)}"
            metrics.append({
                "metric_id": metric_id,
                "name": metric,
                "type": "bounded_numeric_indicator",
                "range": [0.0, 1.0],
                "aggregation": "mean_or_last_observation",
                "expected_direction": "higher_supports_prediction",
                "minimum_viable_value": 0.5,
            })
            observables.append({
                "observable_id": f"obs__{metric_id}",
                "name": f"observable_{metric}",
                "measurement_channel": self._measurement_channel_for(metric),
                "sampling_policy": "repeatable_snapshot_or_longitudinal_series",
                "instrumentation_status": "defined_not_empirically_confirmed",
            })
            indicators.append({
                "indicator_id": f"ind__{metric_id}",
                "indicator": metric,
                "validation_threshold": 0.65,
                "refutation_threshold": 0.35,
                "ambiguous_interval": [0.35, 0.65],
            })

        return {
            "signature_id": f"SIG-AT4-{ordinal:04d}-{_slug(pred_id)}",
            "prediction_id": pred_id,
            "category": category,
            "source_statement": record.get("statement"),
            "metrics": metrics,
            "observables": observables,
            "indicators": indicators,
            "signature_scores": {
                "measurement_reliability": reliability,
                "falsifiability": falsifiability,
                "specificity": specificity,
                "measurement_readiness": measurement_readiness,
            },
            "validation_rule": "validate_when_metrics_exceed_threshold_under_replicated_protocol",
            "falsification_rule": "refute_when_core_metrics_remain_below_threshold_under_adequate_power",
            "epistemic_scope": "functional_measurement_only",
        }

    def _measurement_channel_for(self, metric: str) -> str:
        m = _slug(metric)
        if "spectral" in m or "mode" in m or "resonance" in m:
            return "spectral_or_graph_mode_analysis"
        if "transition" in m or "latency" in m or "trajectory" in m:
            return "longitudinal_runtime_timeseries"
        if "coordination" in m or "distributed" in m or "consensus" in m:
            return "distributed_population_or_governance_metrics"
        if "guard" in m or "trace" in m or "closure" in m:
            return "governance_audit_log"
        return "structured_experiment_or_validation_report"

    def _summarize_metrics(self, signatures: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
        sigs = list(signatures)
        metric_count = sum(len(_as_list(s.get("metrics"))) for s in sigs)
        observable_count = sum(len(_as_list(s.get("observables"))) for s in sigs)
        indicator_count = sum(len(_as_list(s.get("indicators"))) for s in sigs)
        readiness_values = [
            _safe_float((s.get("signature_scores") or {}).get("measurement_readiness"), 0.0)
            for s in sigs
        ]
        return {
            "signature_count": len(sigs),
            "metric_count": metric_count,
            "observable_count": observable_count,
            "indicator_count": indicator_count,
            "mean_measurement_readiness": round(sum(readiness_values) / len(readiness_values), 6) if readiness_values else 0.0,
            "min_measurement_readiness": round(min(readiness_values), 6) if readiness_values else 0.0,
            "max_measurement_readiness": round(max(readiness_values), 6) if readiness_values else 0.0,
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        at3 = self._load_at3(inputs)
        at2 = self._load_at2(inputs)
        prediction_records = self._extract_prediction_records(at3, at2, inputs)
        signatures = [self._build_signature(record, idx) for idx, record in enumerate(prediction_records, start=1)]
        categories = sorted({str(s.get("category", "general")) for s in signatures})
        metrics_summary = self._summarize_metrics(signatures)

        output_path = ROOT / "predictive_theory" / "measurable_signatures" / "latest_measurable_signatures.json"
        persisted = False
        if persist:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({
                "primitive": self.primitive,
                "step": self.step_name,
                "measurable_signatures": signatures,
                "metrics_summary": metrics_summary,
                "timestamp_utc": _utc_now(),
            }, indent=2, sort_keys=True), encoding="utf-8")
            persisted = True

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "status": self.status,
            "prediction_count": len(prediction_records),
            "signature_count": metrics_summary["signature_count"],
            "metric_count": metrics_summary["metric_count"],
            "observable_count": metrics_summary["observable_count"],
            "indicator_count": metrics_summary["indicator_count"],
            "measurable_signatures": signatures,
            "generated_signature_categories": categories,
            "measurement_policy": {
                "bounded_metrics": True,
                "repeatable_observables_required": True,
                "longitudinal_series_supported": True,
                "empirical_confirmation_claimed": False,
            },
            "validation_policy": {
                "validation_requires_protocol": True,
                "validation_threshold_default": 0.65,
                "replication_required_for_strong_support": True,
                "statistical_power_required": "deferred_to_AT5_AT7",
            },
            "falsification_policy": {
                "falsification_threshold_default": 0.35,
                "adequate_power_required": True,
                "negative_result_status": "functional_refutation_candidate_only",
                "phenomenology_not_refuted_or_proven": True,
            },
            "metrics_summary": metrics_summary,
            "epistemic_guards": dict(self.epistemic_guards),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "persist_requested": bool(persist),
            "persisted": persisted,
            "output_path": str(output_path) if persist else None,
            "timestamp_utc": _utc_now(),
        }
        return result


__all__ = ["MeasurableSignatureBuilder"]
