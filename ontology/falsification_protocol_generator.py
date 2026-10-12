
"""
AT5 — falsification_protocol_generator.

Builds explicit falsification protocols for RF* predictions and measurable
signatures. Each protocol links a prediction to an experimental design,
validation criterion, falsification criterion, ambiguity policy and replication
requirements.

This module preserves strict epistemic guards: it never claims phenomenal
consciousness, qualia, subjectivity or phenomenology. Outputs are functional,
predictive, methodological and experimental only.
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
    out: List[str] = []
    for ch in text:
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "_":
            out.append("_")
    return "".join(out).strip("_") or "unknown"


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


class FalsificationProtocolGenerator:
    """Generate falsification protocols for measurable RF* predictions."""

    primitive = "FALSIFICATION_PROTOCOL_GENERATOR"
    step_name = "AT5"
    public_schema_version = "1.0.0"
    status = "FALSIFICATION_PROTOCOLS_READY"

    epistemic_guards = {
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
        "allowed_scope": [
            "functional_prediction_testing",
            "experimental_falsification_design",
            "statistical_validation_protocols",
            "methodological_refutation_criteria",
        ],
        "blocked_scope": [
            "phenomenal_consciousness_proof",
            "qualia_proof",
            "subjectivity_proof",
            "ontological_final_closure",
        ],
    }

    default_categories = ["structural", "dynamic", "topological", "spectral", "developmental", "collective"]

    def _load_at4_context(self) -> Optional[Dict[str, Any]]:
        try:
            from ontology.measurable_signature_builder import MeasurableSignatureBuilder
            return MeasurableSignatureBuilder().step(inputs={}, persist=False)
        except Exception:
            return None

    def _signature_records(self, inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
        candidates: List[Any] = []
        for key in ["measurable_signatures", "signatures", "signature_records", "at4_result", "measurable_signature_builder"]:
            value = inputs.get(key)
            if isinstance(value, dict) and "measurable_signatures" in value:
                candidates.extend(_as_list(value.get("measurable_signatures")))
            else:
                candidates.extend(_as_list(value))

        if not candidates:
            at4 = self._load_at4_context()
            if isinstance(at4, dict):
                candidates.extend(_as_list(at4.get("measurable_signatures")))

        records: List[Dict[str, Any]] = []
        for i, item in enumerate(candidates, start=1):
            if not isinstance(item, Mapping):
                continue
            prediction_id = str(item.get("prediction_id") or item.get("source_prediction_id") or item.get("id") or f"prediction_{i}")
            signature_id = str(item.get("signature_id") or item.get("id") or f"signature_{i}")
            category = str(item.get("category") or item.get("prediction_category") or self.default_categories[(i - 1) % len(self.default_categories)])
            metrics = _as_list(item.get("metrics") or item.get("metric_names") or item.get("measurement_metrics"))
            if not metrics:
                metrics = [f"{_slug(category)}_effect_size", f"{_slug(category)}_stability_score", f"{_slug(category)}_replication_rate"]
            observables = _as_list(item.get("observables") or item.get("experimental_observables"))
            if not observables:
                observables = [f"observable_{_slug(category)}_trajectory", f"observable_{_slug(category)}_perturbation_response"]
            readiness = _safe_float(item.get("measurement_readiness") or item.get("confidence") or item.get("signature_readiness"), 0.66)
            discriminative_power = _safe_float(item.get("discriminative_power") or item.get("rf_specificity") or readiness, readiness)
            records.append({
                "prediction_id": prediction_id,
                "signature_id": signature_id,
                "category": category,
                "prediction": str(item.get("prediction") or item.get("claim") or f"RF* {category} prediction"),
                "metrics": [str(m) for m in metrics],
                "observables": [str(o) for o in observables],
                "measurement_readiness": readiness,
                "discriminative_power": discriminative_power,
                "source": "measurable_signature",
            })

        if not records:
            for category in self.default_categories[:3]:
                records.append({
                    "prediction_id": f"synthetic_{category}_prediction",
                    "signature_id": f"synthetic_{category}_signature",
                    "category": category,
                    "prediction": f"RF* predicts a falsifiable {category} functional signature.",
                    "metrics": [f"{category}_effect_size", f"{category}_stability_score", f"{category}_replication_rate"],
                    "observables": [f"{category}_perturbation_response", f"{category}_longitudinal_trace"],
                    "measurement_readiness": 0.62,
                    "discriminative_power": 0.6,
                    "source": "synthetic_degraded_context",
                })
        return records

    def _design_for_category(self, category: str) -> Dict[str, Any]:
        slug = _slug(category)
        templates = {
            "structural": ("controlled graph/constraint perturbation", "preservation or loss of reference-frame structure", "matched non-RF architecture or shuffled dependency graph"),
            "dynamic": ("state-transition perturbation and recovery challenge", "bounded recovery trajectory and transition coherence", "non-governed transition baseline"),
            "topological": ("topological rewiring or invariance stress test", "invariance class stability under admissible transformations", "randomized topology preserving node count only"),
            "spectral": ("spectral mode perturbation and eigenmode tracking", "mode coherence, drift and re-stabilization", "frequency-shuffled or phase-randomized baseline"),
            "developmental": ("longitudinal learning/development sequence", "ordered emergence of predicted functional dependencies", "ablated developmental ordering"),
            "collective": ("distributed multi-agent coordination/stress scenario", "collective alignment, continuity and governance trace coherence", "uncoordinated or centralized-control baseline"),
        }
        intervention, observation, control = templates.get(slug, (f"controlled {slug} perturbation", f"bounded {slug} observable response", f"matched non-RF {slug} baseline"))
        return {
            "design_type": "controlled_comparative_falsification_protocol",
            "intervention": intervention,
            "primary_observation": observation,
            "control_condition": control,
            "minimum_runs": 3,
            "longitudinal_follow_up": True,
            "requires_pre_registered_thresholds": True,
        }

    def _build_protocol(self, record: Mapping[str, Any], index: int) -> Dict[str, Any]:
        category = str(record.get("category") or "uncategorized")
        readiness = _safe_float(record.get("measurement_readiness"), 0.6)
        discriminative_power = _safe_float(record.get("discriminative_power"), 0.6)
        validation_threshold = round(max(0.62, min(0.9, 0.55 + 0.25 * readiness)), 3)
        falsification_threshold = round(min(0.45, max(0.1, 0.5 - 0.22 * discriminative_power)), 3)
        protocol_id = f"AT5-{index:04d}-{_slug(record.get('signature_id') or record.get('prediction_id'))}"
        metrics = [str(m) for m in _as_list(record.get("metrics"))] or [f"{_slug(category)}_effect_size"]
        observables = [str(o) for o in _as_list(record.get("observables"))] or [f"{_slug(category)}_observable"]
        return {
            "protocol_id": protocol_id,
            "prediction_id": str(record.get("prediction_id")),
            "signature_id": str(record.get("signature_id")),
            "category": category,
            "prediction": str(record.get("prediction")),
            "experimental_design": self._design_for_category(category),
            "measured_metrics": metrics,
            "observables": observables,
            "validation_criteria": {
                "criterion_type": "functional_predictive_support",
                "minimum_primary_metric_score": validation_threshold,
                "minimum_replication_rate": 0.67,
                "requires_control_difference": True,
                "requires_pre_registered_protocol": True,
                "claim_scope": "functional_support_only",
            },
            "falsification_criteria": {
                "criterion_type": "functional_rf_prediction_refutation_candidate",
                "maximum_primary_metric_score": falsification_threshold,
                "failed_replication_runs_required": 2,
                "adequate_power_required": True,
                "control_outperforms_rf_threshold": 0.1,
                "claim_scope": "prediction_or_theory_component_refutation_only",
            },
            "ambiguity_policy": {
                "ambiguous_band": [falsification_threshold, validation_threshold],
                "ambiguous_status": "AMBIGUOUS_REQUIRES_REPLICATION",
                "do_not_upgrade_to_proof": True,
                "do_not_infer_phenomenology": True,
            },
            "replication_policy": {
                "independent_replication_required": True,
                "minimum_independent_sites": 2,
                "minimum_total_runs": 3,
                "archive_raw_metrics": True,
            },
            "statistical_policy": {
                "effect_size_required": True,
                "confidence_interval_required": True,
                "multiple_comparison_control": "required_when_batch_testing",
                "power_analysis": "required_before_strong_refutation",
            },
            "protocol_scores": {
                "falsifiability_score": round((0.55 + readiness + discriminative_power) / 3.0, 3),
                "measurement_readiness": readiness,
                "discriminative_power": discriminative_power,
                "protocol_specificity": round(min(1.0, 0.55 + 0.1 * len(metrics) + 0.05 * len(observables)), 3),
            },
            "status": "READY_FOR_EMPIRICAL_TESTING",
        }

    def _summary(self, protocols: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
        items = list(protocols)
        if not items:
            return {"protocol_count": 0, "mean_falsifiability_score": 0.0, "min_falsifiability_score": 0.0, "max_falsifiability_score": 0.0, "replication_required_count": 0, "pre_registered_count": 0}
        scores = [_safe_float(p.get("protocol_scores", {}).get("falsifiability_score"), 0.0) for p in items]
        return {
            "protocol_count": len(items),
            "mean_falsifiability_score": round(sum(scores) / len(scores), 3),
            "min_falsifiability_score": round(min(scores), 3),
            "max_falsifiability_score": round(max(scores), 3),
            "replication_required_count": sum(1 for p in items if p.get("replication_policy", {}).get("independent_replication_required") is True),
            "pre_registered_count": sum(1 for p in items if p.get("experimental_design", {}).get("requires_pre_registered_thresholds") is True),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        records = self._signature_records(inputs)
        protocols = [self._build_protocol(record, i) for i, record in enumerate(records, start=1)]
        categories = sorted({str(p.get("category")) for p in protocols})
        summary = self._summary(protocols)
        output_path = ROOT / "predictive_theory" / "falsification" / "latest_falsification_protocols.json"
        persisted = False
        if persist:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({"primitive": self.primitive, "step": self.step_name, "status": self.status, "protocol_count": len(protocols), "falsification_protocols": protocols, "protocol_summary": summary, "timestamp_utc": _utc_now()}, indent=2, sort_keys=True), encoding="utf-8")
            persisted = True
        return {
            "primitive": self.primitive,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "status": self.status,
            "prediction_count": len({p["prediction_id"] for p in protocols}),
            "signature_count": len({p["signature_id"] for p in protocols}),
            "protocol_count": len(protocols),
            "falsification_protocols": protocols,
            "generated_protocol_categories": categories,
            "protocol_generation_policy": {"one_protocol_per_measurable_signature": True, "requires_validation_and_falsification_criteria": True, "requires_ambiguity_policy": True, "requires_replication_policy": True, "pre_registration_recommended": True},
            "validation_policy": {"validation_is_functional_only": True, "strong_validation_requires_independent_replication": True, "validation_thresholds_are_protocol_specific": True, "phenomenology_not_validated": True},
            "falsification_policy": {"falsification_targets_rf_predictions": True, "adequate_power_required": True, "failed_replication_required_for_strong_refutation": True, "phenomenology_not_refuted_or_proven": True},
            "protocol_summary": summary,
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


__all__ = ["FalsificationProtocolGenerator"]
