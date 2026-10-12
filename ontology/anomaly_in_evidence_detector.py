
"""
M6 — anomaly_in_evidence_detector

Functional detector of anomalies in scientific evidence for the Open Cognitive
Ecology meta-supervision pipeline.

This primitive estimates unexpected performance, outlier intensity, and anomaly
probability. It distinguishes suspicious evidence from ordinary variance using
bounded, deterministic, explainable indicators. It does not make ontological or
phenomenal claims; it only reports functional anomaly signals relevant to
scientific self-supervision.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Iterable

from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
import json
import math


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = default
    if math.isnan(v) or math.isinf(v):
        return default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {
            "true", "yes", "1", "ok", "success", "successful", "passed",
            "anomaly", "anomalous", "outlier", "suspicious", "unexpected",
            "rupture", "shift", "transition", "regime_change"
        }
    if isinstance(value, (int, float)):
        return value > 0
    return False


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _extract_scores(items: Iterable[Any]) -> list[float]:
    keys = (
        "score", "value", "result", "performance", "performance_score",
        "evidence_quality_score", "statistical_robustness_score",
        "scientific_consistency_score", "confidence_score", "validation_score",
        "replication_support", "consensus_score", "effect_size_score",
        "metric_value", "measurement", "observed_value"
    )
    scores: list[float] = []
    for item in items:
        if isinstance(item, (int, float)):
            scores.append(_clamp(item))
            continue
        if isinstance(item, dict):
            for key in keys:
                if key in item:
                    scores.append(_clamp(item.get(key)))
                    break
    return scores


def _extract_risks(items: Iterable[Any]) -> list[float]:
    keys = (
        "anomaly_probability", "anomaly_score", "outlier_score",
        "unexpected_performance_score", "suspiciousness", "risk",
        "false_positive_risk", "bias_score", "inconsistency_risk",
        "contradiction_score", "replication_failure_risk", "rupture_probability",
        "transition_probability", "regime_shift_score"
    )
    risks: list[float] = []
    for item in items:
        if isinstance(item, (int, float)):
            risks.append(_clamp(item))
            continue
        if isinstance(item, dict):
            for key in keys:
                if key in item:
                    risks.append(_clamp(item.get(key)))
                    break
    return risks


def _marker_rate(items: Iterable[Any], markers: tuple[str, ...]) -> float:
    items_list = list(items)
    if not items_list:
        return 0.0
    count = 0
    total = 0
    for item in items_list:
        total += 1
        if isinstance(item, str):
            lowered = item.lower()
            if any(marker in lowered for marker in markers):
                count += 1
        elif isinstance(item, dict):
            if any(_boolish(item.get(marker)) for marker in markers if marker in item):
                count += 1
            else:
                text = json.dumps(item, ensure_ascii=False).lower()
                if any(marker in text for marker in markers):
                    count += 1
    return _clamp(count / max(total, 1))


def _robust_outlier_intensity(scores: list[float]) -> float:
    if not scores:
        return 0.0
    if len(scores) == 1:
        return 0.0
    med = median(scores)
    deviations = [abs(v - med) for v in scores]
    max_dev = max(deviations) if deviations else 0.0
    # In bounded [0, 1] scores, distance > 0.35 from median is a strong outlier.
    distance_component = _clamp(max_dev / 0.50)
    variance_component = _clamp(pstdev(scores) / 0.35)
    return _clamp(0.60 * distance_component + 0.40 * variance_component)


def _unexpected_performance(scores: list[float], expected: float | None, baseline_scores: list[float]) -> float:
    if not scores:
        return 0.0
    observed = mean(scores)
    if expected is None:
        if baseline_scores:
            expected_value = mean(baseline_scores)
        elif len(scores) > 1:
            expected_value = median(scores)
        else:
            expected_value = 0.5
    else:
        expected_value = _clamp(expected, 0.5)
    deviation = abs(observed - expected_value)
    # Deviation of 0.4 on bounded scientific scores is already substantial.
    return _clamp(deviation / 0.40)


class AnomalyInEvidenceDetector:
    """
    Detect functional anomalies in scientific evidence.
    """

    primitive = "anomaly_in_evidence_detector"

    def __init__(self, report_dir: str | Path = "runtime_experiments/scientific_anomalies") -> None:
        self.report_dir = Path(report_dir)

    def plan_persistence(self) -> dict[str, Any]:
        report_path = Path(self.report_dir) / "anomaly_in_evidence_detector_report.json"
        return {
            "report_path": str(report_path),
            "operation_cardinality": {"FS_CREATE_DIRS": 1, "FS_WRITE_REPLACE_BYTES": 1},
        }

    def step(self, inputs: Any = None, filesystem_effect_context: GovernedFilesystemEffectContext | None = None, **kwargs: Any) -> dict[str, Any]:
        if isinstance(inputs, dict):
            payload: dict[str, Any] = dict(inputs)
        else:
            payload = {}
        payload.update(kwargs)

        evidence_items = _as_list(payload.get("evidence_items", payload.get("results", [])))
        baseline_records = _as_list(payload.get("baseline_records", payload.get("historical_records", [])))
        anomaly_signals = _as_list(payload.get("anomaly_signals", []))
        paradigm_signals = _as_list(payload.get("paradigm_signals", payload.get("regime_signals", [])))
        contradiction_signals = _as_list(payload.get("contradiction_signals", payload.get("inconsistency_signals", [])))

        direct_scores = _extract_scores(evidence_items)
        baseline_scores = _extract_scores(baseline_records)

        # Accept direct M1-M5 scalar inputs as evidence when no list is supplied.
        scalar_keys = (
            "evidence_quality_score", "statistical_robustness_score",
            "scientific_consistency_score", "confidence_score", "replication_support",
            "effect_size_score"
        )
        if not direct_scores:
            for key in scalar_keys:
                if key in payload:
                    direct_scores.append(_clamp(payload.get(key)))

        expected_value = payload.get("expected_performance", payload.get("baseline_score"))
        expected = None if expected_value is None else _clamp(expected_value, 0.5)

        explicit_unexpected = payload.get("unexpected_performance_score")
        explicit_outlier = payload.get("outlier_result_score")
        explicit_probability = payload.get("anomaly_probability")

        unexpected_performance_score = _clamp(
            explicit_unexpected
            if explicit_unexpected is not None
            else _unexpected_performance(direct_scores, expected, baseline_scores)
        )

        outlier_result_score = _clamp(
            explicit_outlier
            if explicit_outlier is not None
            else _robust_outlier_intensity(direct_scores + baseline_scores if baseline_scores else direct_scores)
        )

        anomaly_risks = _extract_risks(anomaly_signals)
        paradigm_risks = _extract_risks(paradigm_signals)
        contradiction_risks = _extract_risks(contradiction_signals)

        marker_anomaly = _marker_rate(
            anomaly_signals + evidence_items,
            ("anomaly", "anomalous", "outlier", "unexpected", "suspicious")
        )
        marker_paradigm = _marker_rate(
            paradigm_signals,
            ("paradigm", "shift", "transition", "rupture", "regime")
        )
        marker_contradiction = _marker_rate(
            contradiction_signals + evidence_items,
            ("contradiction", "inconsistency", "conflict", "failure")
        )

        false_positive_risk = _clamp(payload.get("false_positive_risk", 0.0))
        bias_score = _clamp(payload.get("bias_score", payload.get("bias_risk", 0.0)))
        scientific_consistency_score = _clamp(payload.get("scientific_consistency_score", 0.7), 0.7)
        statistical_robustness_score = _clamp(payload.get("statistical_robustness_score", 0.7), 0.7)
        measurement_reliability = _clamp(payload.get("measurement_reliability", 0.75), 0.75)

        anomaly_signal_score = mean(anomaly_risks) if anomaly_risks else marker_anomaly
        paradigm_shift_score = mean(paradigm_risks) if paradigm_risks else marker_paradigm
        contradiction_score = mean(contradiction_risks) if contradiction_risks else marker_contradiction

        fragility_component = _clamp(
            0.35 * false_positive_risk
            + 0.25 * bias_score
            + 0.25 * (1.0 - scientific_consistency_score)
            + 0.15 * (1.0 - statistical_robustness_score)
        )
        measurement_artifact_risk = _clamp(1.0 - measurement_reliability)

        anomaly_probability = _clamp(
            explicit_probability
            if explicit_probability is not None
            else 0.25 * unexpected_performance_score
                 + 0.25 * outlier_result_score
                 + 0.20 * anomaly_signal_score
                 + 0.15 * contradiction_score
                 + 0.10 * fragility_component
                 + 0.05 * measurement_artifact_risk
        )

        # Paradigm shift is not itself a scientific error; it increases review need,
        # but is separated from suspiciousness to avoid collapsing novelty into failure.
        suspicious_result = (
            anomaly_probability >= 0.60
            or (unexpected_performance_score >= 0.75 and outlier_result_score >= 0.65)
            or contradiction_score >= 0.75
        )

        if suspicious_result:
            anomaly_decision = "suspicious_result"
        elif anomaly_probability >= 0.35 or paradigm_shift_score >= 0.50:
            anomaly_decision = "review_recommended"
        else:
            anomaly_decision = "no_anomaly_detected"

        interpretation = "ordinary_variance"
        if suspicious_result and measurement_artifact_risk >= 0.50:
            interpretation = "possible_measurement_artifact"
        elif suspicious_result:
            interpretation = "scientific_anomaly_candidate"
        elif paradigm_shift_score >= 0.50:
            interpretation = "possible_regime_or_paradigm_transition"
        elif anomaly_probability >= 0.35:
            interpretation = "weak_anomaly_signal"

        anomaly_reasons: list[str] = []
        if unexpected_performance_score >= 0.50:
            anomaly_reasons.append("unexpected_performance")
        if outlier_result_score >= 0.50:
            anomaly_reasons.append("outlier_result")
        if anomaly_signal_score >= 0.50:
            anomaly_reasons.append("explicit_anomaly_signals")
        if contradiction_score >= 0.50:
            anomaly_reasons.append("contradiction_signals")
        if false_positive_risk >= 0.60:
            anomaly_reasons.append("false_positive_risk")
        if bias_score >= 0.60:
            anomaly_reasons.append("bias_risk")
        if measurement_artifact_risk >= 0.50:
            anomaly_reasons.append("measurement_artifact_risk")
        if paradigm_shift_score >= 0.50:
            anomaly_reasons.append("paradigm_shift_signal")

        result: dict[str, Any] = {
            "success": True,
            "primitive": "anomaly_in_evidence_detector",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "unexpected_performance_score": unexpected_performance_score,
            "outlier_result_score": outlier_result_score,
            "anomaly_probability": anomaly_probability,
            "suspicious_result": suspicious_result,
            "anomaly_decision": anomaly_decision,
            "anomaly_interpretation": interpretation,
            "anomaly_reasons": anomaly_reasons,
            "anomaly_signal_score": _clamp(anomaly_signal_score),
            "paradigm_shift_score": _clamp(paradigm_shift_score),
            "contradiction_score": _clamp(contradiction_score),
            "measurement_artifact_risk": measurement_artifact_risk,
            "fragility_component": fragility_component,
            "diagnostics": {
                "evidence_item_count": len(evidence_items),
                "baseline_record_count": len(baseline_records),
                "direct_score_count": len(direct_scores),
                "baseline_score_count": len(baseline_scores),
                "expected_performance": expected,
                "observed_mean": mean(direct_scores) if direct_scores else None,
                "baseline_mean": mean(baseline_scores) if baseline_scores else None,
                "false_positive_risk": false_positive_risk,
                "bias_score": bias_score,
                "scientific_consistency_score": scientific_consistency_score,
                "statistical_robustness_score": statistical_robustness_score,
                "measurement_reliability": measurement_reliability,
            },
            "epistemic_position": {
                "architecture_computational": True,
                "functional_indicators_only": True,
                "phenomenal_subjectivity_claimed": False,
                "ontological_claim": "functional_anomaly_detection_only",
            },
        }

        result["anomaly_in_evidence_report"] = {
            "unexpected_performance_score": unexpected_performance_score,
            "outlier_result_score": outlier_result_score,
            "anomaly_probability": anomaly_probability,
            "suspicious_result": suspicious_result,
            "decision": anomaly_decision,
            "interpretation": interpretation,
            "reasons": anomaly_reasons,
        }

        persist = payload.get("persist", True)
        persistence_plan = self.plan_persistence()
        report_path = Path(persistence_plan["report_path"])
        result["report_path"] = str(report_path)
        if persist:
            effect_context = filesystem_effect_context
            if not isinstance(effect_context, GovernedFilesystemEffectContext):
                raise RuntimeError("governed filesystem effect context required")
            if effect_context.authority_minting is not False:
                raise RuntimeError("consumer authority minting forbidden")
            expected = {"persist_parent_create": 1, "persist_report_write": 1}
            if effect_context.remaining() != expected:
                raise RuntimeError("filesystem effect slot cardinality mismatch")
            effect_context.begin()
            effect_context.execute_path("persist_parent_create", "FS_CREATE_DIRS", report_path.parent)
            encoded = json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8")
            effect_context.execute_path("persist_report_write", "FS_WRITE_REPLACE_BYTES", report_path, encoded)
            if any(effect_context.remaining().values()):
                raise RuntimeError("unconsumed filesystem effect handles")

        return result
