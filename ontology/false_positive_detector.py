
"""
M3 — false_positive_detector

Functional detector of false-positive risk for scientific validation results.

This primitive does not declare that a result is false. It estimates a bounded,
traceable risk that a reported positive scientific result may be insufficiently
supported because of weak replication, fragile robustness, or confirmation bias.

Epistemic constraint: it evaluates functional scientific trustworthiness only;
it makes no claim of phenomenal subjectivity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable
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
        return value.strip().lower() in {"true", "yes", "1", "ok", "success", "replicated"}
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


def _extract_numeric_scores(items: Iterable[Any]) -> list[float]:
    scores: list[float] = []
    candidate_keys = (
        "score",
        "confidence_score",
        "evidence_quality_score",
        "statistical_robustness_score",
        "validation_score",
        "support_score",
        "effect_size_score",
    )
    for item in items:
        if isinstance(item, (int, float)):
            scores.append(_clamp(item))
            continue
        if isinstance(item, dict):
            for key in candidate_keys:
                if key in item:
                    scores.append(_clamp(item.get(key)))
                    break
    return scores


def _safe_report_write(path: Path, payload: dict[str, Any]) -> Path:
    """Write a JSON report with a fallback when a path component is a file or unwritable."""
    root = Path.home() / "open-cognitive-ecology"
    candidate = path if path.is_absolute() else root / path
    try:
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return candidate
    except Exception:
        fallback = root / "runtime_experiments_safe" / "false_positive_detection" / "false_positive_detector_report.json"
        fallback.parent.mkdir(parents=True, exist_ok=True)
        fallback.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return fallback


@dataclass
class FalsePositiveDetector:
    """Estimate false-positive risk from evidence, replication and robustness signals."""

    report_dir: str = "runtime_experiments/false_positive_detection"

    def step(self, inputs: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        if inputs is None:
            payload: dict[str, Any] = {}
        elif isinstance(inputs, dict):
            payload = dict(inputs)
        else:
            payload = {"results": inputs}
        payload.update(kwargs)

        evidence_items = _as_list(payload.get("evidence_items", payload.get("results", [])))
        replication_results = _as_list(payload.get("replication_results", []))
        anomaly_signals = _as_list(payload.get("anomaly_signals", []))

        evidence_quality_score = _clamp(payload.get("evidence_quality_score"), None) if payload.get("evidence_quality_score") is not None else None
        statistical_robustness_score = _clamp(payload.get("statistical_robustness_score"), None) if payload.get("statistical_robustness_score") is not None else None
        replication_support = _clamp(payload.get("replication_support"), None) if payload.get("replication_support") is not None else None
        confirmation_pressure = _clamp(payload.get("confirmation_pressure", payload.get("confirmation_bias_pressure", 0.0)))
        novelty_pressure = _clamp(payload.get("novelty_pressure", 0.0))

        scores = _extract_numeric_scores(evidence_items)
        if evidence_quality_score is None:
            evidence_quality_score = mean(scores) if scores else 0.0

        # Replication support can be explicit, or inferred from replication markers.
        if replication_support is None:
            markers: list[bool] = []
            for item in evidence_items + replication_results:
                if isinstance(item, dict):
                    for key in (
                        "replication_success",
                        "replicated",
                        "replication",
                        "success",
                        "external_replication_success",
                    ):
                        if key in item:
                            markers.append(_boolish(item.get(key)))
                            break
                elif isinstance(item, bool):
                    markers.append(item)
            replication_support = (sum(1 for x in markers if x) / len(markers)) if markers else 0.0

        if statistical_robustness_score is None:
            if scores:
                variance_stability = 1.0 - min(pstdev(scores), 1.0)
                statistical_robustness_score = _clamp((evidence_quality_score + variance_stability) / 2.0)
            else:
                statistical_robustness_score = 0.0

        # Replication failure risk rises when replication is absent, failed, or fragile.
        replication_failure_risk = _clamp(1.0 - replication_support)

        anomaly_penalty = 0.0
        if anomaly_signals:
            anomaly_values = []
            for item in anomaly_signals:
                if isinstance(item, dict):
                    anomaly_values.append(_clamp(item.get("anomaly_probability", item.get("score", item.get("risk", 0.0)))))
                elif isinstance(item, (int, float)):
                    anomaly_values.append(_clamp(item))
                elif _boolish(item):
                    anomaly_values.append(1.0)
            anomaly_penalty = mean(anomaly_values) if anomaly_values else 0.0

        # Confirmation bias risk rises when support is internally strong but externally weak,
        # or when explicit pressure markers are high.
        internal_support = _clamp(mean([evidence_quality_score, statistical_robustness_score]))
        external_gap = max(0.0, internal_support - replication_support)
        confirmation_bias_risk = _clamp(
            0.45 * confirmation_pressure
            + 0.30 * external_gap
            + 0.15 * novelty_pressure
            + 0.10 * anomaly_penalty
        )

        # False-positive risk synthesizes weak replication, weak robustness,
        # weak evidence, and confirmation pressure. It is a risk estimate, not a verdict.
        false_positive_risk = _clamp(
            0.35 * replication_failure_risk
            + 0.25 * (1.0 - statistical_robustness_score)
            + 0.20 * (1.0 - evidence_quality_score)
            + 0.20 * confirmation_bias_risk
        )

        if false_positive_risk >= 0.70 or replication_failure_risk >= 0.85:
            decision = "high_risk"
        elif false_positive_risk >= 0.40 or confirmation_bias_risk >= 0.45:
            decision = "moderate_risk"
        else:
            decision = "low_risk"

        risk_reasons: list[str] = []
        if replication_failure_risk >= 0.60:
            risk_reasons.append("weak_or_missing_replication")
        if statistical_robustness_score < 0.50:
            risk_reasons.append("fragile_statistical_support")
        if evidence_quality_score < 0.50:
            risk_reasons.append("weak_evidence_quality")
        if confirmation_bias_risk >= 0.40:
            risk_reasons.append("confirmation_bias_pressure")
        if anomaly_penalty >= 0.40:
            risk_reasons.append("anomaly_signals_present")

        result: dict[str, Any] = {
            "success": True,
            "primitive": "false_positive_detector",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "false_positive_risk": false_positive_risk,
            "replication_failure_risk": replication_failure_risk,
            "confirmation_bias_risk": confirmation_bias_risk,
            "false_positive_decision": decision,
            "risk_decision": decision,
            "high_risk": decision == "high_risk",
            "moderate_risk": decision == "moderate_risk",
            "low_risk": decision == "low_risk",
            "risk_reasons": risk_reasons,
            "evidence_quality_score": evidence_quality_score,
            "statistical_robustness_score": statistical_robustness_score,
            "replication_support": replication_support,
            "anomaly_penalty": anomaly_penalty,
            "diagnostics": {
                "evidence_item_count": len(evidence_items),
                "replication_result_count": len(replication_results),
                "anomaly_signal_count": len(anomaly_signals),
                "confirmation_pressure": confirmation_pressure,
                "novelty_pressure": novelty_pressure,
                "internal_support": internal_support,
                "external_replication_gap": external_gap,
            },
            "epistemic_position": {
                "architecture_computational": True,
                "functional_indicators_only": True,
                "phenomenal_subjectivity_claimed": False,
                "ontological_claim": "functional_false_positive_risk_estimation_only",
            },
        }

        result["false_positive_detector_report"] = {
            "false_positive_risk": false_positive_risk,
            "replication_failure_risk": replication_failure_risk,
            "confirmation_bias_risk": confirmation_bias_risk,
            "decision": decision,
            "risk_reasons": risk_reasons,
        }

        persist = payload.get("persist", True)
        report_path = Path(self.report_dir) / "false_positive_detector_report.json"
        if persist:
            report_path = _safe_report_write(report_path, result)
        result["report_path"] = str(report_path)

        return result
