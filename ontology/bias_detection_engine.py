
"""
M4 — bias_detection_engine

Functional detector of scientific bias risks for the Open Cognitive Ecology
validation pipeline.

This primitive estimates bounded risks for selection bias, measurement bias,
survivorship bias, and publication bias. It does not invalidate results by
itself; it produces traceable indicators that can feed later scientific
consistency validation and self-revision supervision.

Epistemic constraint: it evaluates functional scientific trustworthiness only;
it makes no claim of phenomenal subjectivity.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable

from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
import json


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = default
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
            "true", "yes", "1", "ok", "success", "successful", "published",
            "positive", "replicated", "accepted", "passed"
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
    scores: list[float] = []
    keys = (
        "score", "evidence_quality_score", "validation_score", "confidence_score",
        "statistical_robustness_score", "support_score", "result_score",
        "effect_size_score", "consensus_score"
    )
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


def _rate(items: Iterable[Any], keys: tuple[str, ...]) -> float | None:
    values: list[bool] = []
    for item in items:
        if isinstance(item, dict):
            for key in keys:
                if key in item:
                    values.append(_boolish(item.get(key)))
                    break
        elif isinstance(item, bool):
            values.append(item)
    if not values:
        return None
    return sum(1 for v in values if v) / len(values)


def _count_marker(items: Iterable[Any], keys: tuple[str, ...]) -> int:
    count = 0
    for item in items:
        if isinstance(item, dict):
            if any(_boolish(item.get(key)) for key in keys if key in item):
                count += 1
        elif isinstance(item, str):
            lowered = item.lower()
            if any(key.lower() in lowered for key in keys):
                count += 1
    return count


class BiasDetectionEngine:
    """
    Estimate scientific bias risk from evidence, replication, publication,
    measurement, and sampling signals.
    """

    primitive = "bias_detection_engine"

    def __init__(self, report_dir: str | Path = "runtime_experiments/scientific_bias_detection") -> None:
        self.report_dir = Path(report_dir)

    def plan_persistence(self) -> dict[str, Any]:
        report_path = Path(self.report_dir) / "bias_detection_engine_report.json"
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
        sources = _as_list(payload.get("sources", payload.get("source_records", [])))
        measurement_records = _as_list(payload.get("measurement_records", payload.get("metrics", [])))
        replication_results = _as_list(payload.get("replication_results", []))
        publication_records = _as_list(payload.get("publication_records", payload.get("publications", [])))
        negative_results = _as_list(payload.get("negative_results", payload.get("failed_results", [])))
        null_results = _as_list(payload.get("null_results", []))
        anomaly_signals = _as_list(payload.get("anomaly_signals", []))

        scores = _extract_scores(evidence_items)
        source_count = len(sources)
        evidence_count = len(evidence_items)
        publication_count = len(publication_records)
        negative_count = len(negative_results) + len(null_results)
        replication_count = len(replication_results)

        explicit_selection_bias = payload.get("selection_bias")
        explicit_measurement_bias = payload.get("measurement_bias")
        explicit_survivorship_bias = payload.get("survivorship_bias")
        explicit_publication_bias = payload.get("publication_bias")

        # Selection bias rises when evidence is sourced narrowly, sample size is small,
        # or explicit source diversity is weak.
        source_diversity = payload.get("source_diversity")
        if source_diversity is None:
            if source_count <= 0:
                source_diversity_score = 0.0
            else:
                unique_sources = set()
                for s in sources:
                    if isinstance(s, dict):
                        unique_sources.add(str(s.get("source", s.get("name", s.get("id", s)))))
                    else:
                        unique_sources.add(str(s))
                source_diversity_score = _clamp(len(unique_sources) / max(source_count, 1))
        else:
            source_diversity_score = _clamp(source_diversity)

        sample_adequacy = _clamp(payload.get("sample_adequacy", min(evidence_count / 10.0, 1.0)))
        selection_bias = _clamp(
            explicit_selection_bias
            if explicit_selection_bias is not None
            else 0.55 * (1.0 - source_diversity_score) + 0.45 * (1.0 - sample_adequacy)
        )

        # Measurement bias rises when measurement reliability is low, variance is high,
        # or there are explicit measurement warnings.
        measurement_reliability = payload.get("measurement_reliability")
        if measurement_reliability is None:
            reliability_values: list[float] = []
            for item in measurement_records:
                if isinstance(item, dict):
                    for key in ("reliability", "measurement_reliability", "instrument_reliability", "quality"):
                        if key in item:
                            reliability_values.append(_clamp(item.get(key)))
                            break
            measurement_reliability_score = mean(reliability_values) if reliability_values else 0.75
        else:
            measurement_reliability_score = _clamp(measurement_reliability)

        score_variability = min(pstdev(scores), 1.0) if len(scores) >= 2 else 0.0
        measurement_warning_rate = _clamp(
            _count_marker(measurement_records, ("warning", "instrument_error", "measurement_error", "low_quality"))
            / max(len(measurement_records), 1)
        ) if measurement_records else 0.0
        measurement_bias = _clamp(
            explicit_measurement_bias
            if explicit_measurement_bias is not None
            else 0.45 * (1.0 - measurement_reliability_score)
                 + 0.35 * score_variability
                 + 0.20 * measurement_warning_rate
        )

        # Survivorship bias rises when failures/nulls are absent despite high positivity,
        # or when failed/negative runs are under-represented.
        positive_rate = _rate(evidence_items + replication_results, ("success", "positive", "replication_success", "replicated", "published"))
        if positive_rate is None:
            positive_rate = mean(scores) if scores else 0.5
        failure_visibility = _clamp(negative_count / max(negative_count + evidence_count + replication_count, 1))
        survivorship_bias = _clamp(
            explicit_survivorship_bias
            if explicit_survivorship_bias is not None
            else 0.60 * max(0.0, positive_rate - failure_visibility)
                 + 0.40 * (1.0 - min(negative_count / 3.0, 1.0))
        )

        # Publication bias rises when positive/published records dominate, negative/null
        # records are scarce, or explicit publication pressure is high.
        publication_pressure = _clamp(payload.get("publication_pressure", 0.0))
        published_rate = _rate(publication_records + evidence_items, ("published", "publication_success", "accepted"))
        if published_rate is None:
            published_rate = 1.0 if publication_count > 0 and negative_count == 0 else 0.5
        negative_visibility = _clamp(negative_count / max(publication_count + negative_count, 1))
        publication_bias = _clamp(
            explicit_publication_bias
            if explicit_publication_bias is not None
            else 0.45 * max(0.0, published_rate - negative_visibility)
                 + 0.35 * (1.0 - negative_visibility)
                 + 0.20 * publication_pressure
        )

        anomaly_penalty = 0.0
        if anomaly_signals:
            anomaly_values: list[float] = []
            for item in anomaly_signals:
                if isinstance(item, dict):
                    anomaly_values.append(_clamp(item.get("anomaly_probability", item.get("score", item.get("risk", 0.0)))))
                elif isinstance(item, (int, float)):
                    anomaly_values.append(_clamp(item))
                elif _boolish(item):
                    anomaly_values.append(1.0)
            anomaly_penalty = mean(anomaly_values) if anomaly_values else 0.0

        confirmation_bias_risk = _clamp(payload.get("confirmation_bias_risk", payload.get("confirmation_pressure", 0.0)))
        false_positive_risk = _clamp(payload.get("false_positive_risk", 0.0))

        bias_score = _clamp(
            0.25 * selection_bias
            + 0.25 * measurement_bias
            + 0.20 * survivorship_bias
            + 0.20 * publication_bias
            + 0.05 * confirmation_bias_risk
            + 0.05 * max(anomaly_penalty, false_positive_risk)
        )

        if bias_score >= 0.70 or max(selection_bias, measurement_bias, survivorship_bias, publication_bias) >= 0.85:
            decision = "high_bias_risk"
        elif bias_score >= 0.40:
            decision = "moderate_bias_risk"
        else:
            decision = "low_bias_risk"

        bias_reasons: list[str] = []
        if selection_bias >= 0.50:
            bias_reasons.append("selection_bias_risk")
        if measurement_bias >= 0.50:
            bias_reasons.append("measurement_bias_risk")
        if survivorship_bias >= 0.50:
            bias_reasons.append("survivorship_bias_risk")
        if publication_bias >= 0.50:
            bias_reasons.append("publication_bias_risk")
        if confirmation_bias_risk >= 0.50:
            bias_reasons.append("confirmation_bias_pressure")
        if anomaly_penalty >= 0.50:
            bias_reasons.append("anomaly_signals_present")

        result: dict[str, Any] = {
            "success": True,
            "primitive": "bias_detection_engine",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "selection_bias": selection_bias,
            "measurement_bias": measurement_bias,
            "survivorship_bias": survivorship_bias,
            "publication_bias": publication_bias,
            "bias_score": bias_score,
            "bias_decision": decision,
            "bias_detected": decision != "low_bias_risk",
            "high_bias_risk": decision == "high_bias_risk",
            "moderate_bias_risk": decision == "moderate_bias_risk",
            "low_bias_risk": decision == "low_bias_risk",
            "bias_reasons": bias_reasons,
            "source_diversity_score": source_diversity_score,
            "sample_adequacy": sample_adequacy,
            "measurement_reliability": measurement_reliability_score,
            "failure_visibility": failure_visibility,
            "negative_visibility": negative_visibility,
            "anomaly_penalty": anomaly_penalty,
            "diagnostics": {
                "evidence_item_count": evidence_count,
                "source_count": source_count,
                "measurement_record_count": len(measurement_records),
                "replication_result_count": replication_count,
                "publication_record_count": publication_count,
                "negative_result_count": negative_count,
                "positive_rate": positive_rate,
                "published_rate": published_rate,
                "score_variability": score_variability,
                "publication_pressure": publication_pressure,
                "confirmation_bias_risk": confirmation_bias_risk,
                "false_positive_risk": false_positive_risk,
            },
            "epistemic_position": {
                "architecture_computational": True,
                "functional_indicators_only": True,
                "phenomenal_subjectivity_claimed": False,
                "ontological_claim": "functional_scientific_bias_risk_estimation_only",
            },
        }

        result["bias_report"] = {
            "selection_bias": selection_bias,
            "measurement_bias": measurement_bias,
            "survivorship_bias": survivorship_bias,
            "publication_bias": publication_bias,
            "bias_score": bias_score,
            "decision": decision,
            "bias_reasons": bias_reasons,
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
