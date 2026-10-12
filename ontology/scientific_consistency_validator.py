
"""
M5 — scientific_consistency_validator

Functional validator of scientific consistency for the Open Cognitive Ecology
meta-supervision pipeline.

This primitive estimates historical consistency, cross-validation consistency,
and replication consistency. It detects functional scientific inconsistency
without making ontological or phenomenal claims. It is designed to aggregate
M1 evidence quality, M2 statistical robustness, M3 false-positive risk, and
M4 bias risk into a conservative consistency signal.

Epistemic constraint: this module evaluates measurable functional indicators
only; it makes no claim of phenomenal subjectivity.
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
            "true", "yes", "1", "ok", "success", "successful", "consistent",
            "replicated", "validated", "passed", "stable", "confirmed"
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
        "score", "consistency_score", "historical_consistency_score",
        "cross_validation_score", "replication_consistency_score",
        "evidence_quality_score", "statistical_robustness_score",
        "validation_score", "confidence_score", "consensus_score",
        "replication_support", "effect_size_score", "trustworthiness_score"
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


def _extract_risk_scores(items: Iterable[Any]) -> list[float]:
    keys = (
        "risk", "inconsistency_risk", "false_positive_risk", "bias_score",
        "bias_risk", "anomaly_probability", "contradiction_score",
        "replication_failure_risk"
    )
    risks: list[float] = []
    for item in items:
        if isinstance(item, dict):
            for key in keys:
                if key in item:
                    risks.append(_clamp(item.get(key)))
                    break
        elif isinstance(item, (int, float)):
            risks.append(_clamp(item))
    return risks


def _success_rate(items: Iterable[Any], keys: tuple[str, ...]) -> float | None:
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


def _contradiction_rate(items: Iterable[Any]) -> float:
    if not items:
        return 0.0
    markers = 0
    total = 0
    for item in items:
        total += 1
        if isinstance(item, dict):
            if any(_boolish(item.get(k)) for k in (
                "contradiction", "inconsistent", "scientific_inconsistency",
                "conflict", "failed", "failure"
            ) if k in item):
                markers += 1
            elif _clamp(item.get("contradiction_score", item.get("inconsistency_risk", 0.0))) >= 0.5:
                markers += 1
        elif isinstance(item, str):
            lowered = item.lower()
            if any(k in lowered for k in ("contradiction", "inconsistency", "conflict", "failure")):
                markers += 1
    return _clamp(markers / max(total, 1))


def _stability_from_scores(scores: list[float], default: float = 0.5) -> float:
    if not scores:
        return default
    if len(scores) == 1:
        return _clamp(scores[0])
    # Standard deviation of bounded scores rarely exceeds 0.5 in coherent sets;
    # multiplying by 2 makes inconsistency visible while preserving bounds.
    return _clamp(1.0 - min(pstdev(scores) * 2.0, 1.0))


class ScientificConsistencyValidator:
    """
    Validate scientific consistency across history, cross-validation evidence,
    and replication evidence.
    """

    primitive = "scientific_consistency_validator"

    def __init__(self, report_dir: str | Path = "runtime_experiments/scientific_consistency") -> None:
        self.report_dir = Path(report_dir)

    def plan_persistence(self) -> dict[str, Any]:
        report_path = Path(self.report_dir) / "scientific_consistency_validator_report.json"
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

        history = _as_list(payload.get("historical_records", payload.get("history", [])))
        cross_validation = _as_list(payload.get("cross_validation_records", payload.get("validation_records", [])))
        replication = _as_list(payload.get("replication_records", payload.get("replication_results", [])))
        evidence_items = _as_list(payload.get("evidence_items", []))
        anomaly_signals = _as_list(payload.get("anomaly_signals", []))
        contradiction_signals = _as_list(payload.get("contradiction_signals", payload.get("inconsistency_signals", [])))

        # M1-M4 direct inputs, if supplied.
        evidence_quality_score = _clamp(payload.get("evidence_quality_score", 0.5), 0.5)
        statistical_robustness_score = _clamp(payload.get("statistical_robustness_score", 0.5), 0.5)
        false_positive_risk = _clamp(payload.get("false_positive_risk", 0.0))
        bias_score = _clamp(payload.get("bias_score", payload.get("bias_risk", 0.0)))
        replication_support = _clamp(payload.get("replication_support", 0.5), 0.5)

        explicit_historical = payload.get("historical_consistency_score")
        explicit_cross = payload.get("cross_validation_score")
        explicit_replication = payload.get("replication_consistency_score")

        historical_scores = _extract_scores(history)
        if not historical_scores and evidence_items:
            historical_scores = _extract_scores(evidence_items)
        historical_stability = _stability_from_scores(historical_scores, default=0.65 if not history else 0.5)
        historical_success = _success_rate(history, ("success", "stable", "consistent", "validated"))
        historical_success_score = historical_success if historical_success is not None else 0.65
        historical_contradiction = _contradiction_rate(history + contradiction_signals)
        historical_consistency_score = _clamp(
            explicit_historical
            if explicit_historical is not None
            else 0.45 * historical_stability
                 + 0.35 * historical_success_score
                 + 0.20 * (1.0 - historical_contradiction)
        )

        cross_scores = _extract_scores(cross_validation)
        if not cross_scores:
            cross_scores = [evidence_quality_score, statistical_robustness_score]
        cross_stability = _stability_from_scores(cross_scores, default=0.55)
        cross_success = _success_rate(cross_validation, ("success", "validated", "consistent", "passed"))
        cross_success_score = cross_success if cross_success is not None else mean(cross_scores) if cross_scores else 0.55
        cross_contradiction = _contradiction_rate(cross_validation + contradiction_signals)
        cross_validation_score = _clamp(
            explicit_cross
            if explicit_cross is not None
            else 0.40 * cross_stability
                 + 0.40 * cross_success_score
                 + 0.20 * (1.0 - cross_contradiction)
        )

        replication_scores = _extract_scores(replication)
        if not replication_scores:
            replication_scores = [replication_support]
        replication_success = _success_rate(replication, ("replication_success", "replicated", "success", "consistent"))
        replication_success_score = replication_success if replication_success is not None else replication_support
        replication_failure_risks = _extract_risk_scores(replication)
        replication_failure_risk = mean(replication_failure_risks) if replication_failure_risks else _clamp(payload.get("replication_failure_risk", 1.0 - replication_support))
        replication_consistency_score = _clamp(
            explicit_replication
            if explicit_replication is not None
            else 0.45 * _stability_from_scores(replication_scores, default=replication_support)
                 + 0.35 * replication_success_score
                 + 0.20 * (1.0 - replication_failure_risk)
        )

        anomaly_risks = _extract_risk_scores(anomaly_signals)
        anomaly_penalty = mean(anomaly_risks) if anomaly_risks else 0.0
        contradiction_penalty = max(
            _contradiction_rate(contradiction_signals),
            _clamp(payload.get("contradiction_risk", 0.0)),
        )

        scientific_consistency_score = _clamp(
            0.30 * historical_consistency_score
            + 0.30 * cross_validation_score
            + 0.30 * replication_consistency_score
            + 0.05 * evidence_quality_score
            + 0.05 * statistical_robustness_score
            - 0.10 * max(false_positive_risk, bias_score, anomaly_penalty, contradiction_penalty)
        )

        inconsistency_risk = _clamp(1.0 - scientific_consistency_score)
        scientific_inconsistency = (
            scientific_consistency_score < 0.45
            or min(historical_consistency_score, cross_validation_score, replication_consistency_score) < 0.35
            or max(false_positive_risk, bias_score, anomaly_penalty, contradiction_penalty) >= 0.75
        )

        if scientific_inconsistency:
            decision = "scientific_inconsistency"
        elif scientific_consistency_score >= 0.75:
            decision = "scientifically_consistent"
        else:
            decision = "review_recommended"

        inconsistency_reasons: list[str] = []
        if historical_consistency_score < 0.45:
            inconsistency_reasons.append("low_historical_consistency")
        if cross_validation_score < 0.45:
            inconsistency_reasons.append("low_cross_validation_consistency")
        if replication_consistency_score < 0.45:
            inconsistency_reasons.append("low_replication_consistency")
        if false_positive_risk >= 0.60:
            inconsistency_reasons.append("false_positive_risk")
        if bias_score >= 0.60:
            inconsistency_reasons.append("bias_risk")
        if anomaly_penalty >= 0.60:
            inconsistency_reasons.append("anomaly_signals")
        if contradiction_penalty >= 0.50:
            inconsistency_reasons.append("contradiction_signals")

        result: dict[str, Any] = {
            "success": True,
            "primitive": "scientific_consistency_validator",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "historical_consistency_score": historical_consistency_score,
            "cross_validation_score": cross_validation_score,
            "replication_consistency_score": replication_consistency_score,
            "scientific_consistency_score": scientific_consistency_score,
            "inconsistency_risk": inconsistency_risk,
            "scientific_inconsistency": scientific_inconsistency,
            "consistency_decision": decision,
            "scientifically_consistent": decision == "scientifically_consistent",
            "review_recommended": decision == "review_recommended",
            "inconsistency_reasons": inconsistency_reasons,
            "anomaly_penalty": anomaly_penalty,
            "contradiction_penalty": contradiction_penalty,
            "diagnostics": {
                "historical_record_count": len(history),
                "cross_validation_record_count": len(cross_validation),
                "replication_record_count": len(replication),
                "evidence_item_count": len(evidence_items),
                "historical_stability": historical_stability,
                "historical_success_score": historical_success_score,
                "cross_stability": cross_stability,
                "cross_success_score": cross_success_score,
                "replication_success_score": replication_success_score,
                "replication_failure_risk": replication_failure_risk,
                "evidence_quality_score": evidence_quality_score,
                "statistical_robustness_score": statistical_robustness_score,
                "false_positive_risk": false_positive_risk,
                "bias_score": bias_score,
            },
            "epistemic_position": {
                "architecture_computational": True,
                "functional_indicators_only": True,
                "phenomenal_subjectivity_claimed": False,
                "ontological_claim": "functional_scientific_consistency_validation_only",
            },
        }

        result["scientific_consistency_report"] = {
            "historical_consistency_score": historical_consistency_score,
            "cross_validation_score": cross_validation_score,
            "replication_consistency_score": replication_consistency_score,
            "scientific_consistency_score": scientific_consistency_score,
            "scientific_inconsistency": scientific_inconsistency,
            "decision": decision,
            "inconsistency_reasons": inconsistency_reasons,
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
