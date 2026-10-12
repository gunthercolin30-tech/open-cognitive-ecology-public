"""
M7 — self_revision_recommendation_engine.

Transforms scientific supervision signals M1→M6 into ranked, traceable and
non-executive self-revision recommendations. This primitive does not perform
revision by itself; it prepares governed scientific self-revision for M8 and
later governance layers.

Epistemic scope: functional metrics only. No phenomenal subjectivity claim is
made or inferred by this module.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SelfRevisionRecommendationEngine:
    """
    M7 — generation of governed scientific self-revision recommendations.

    Inputs may be either:
      - explicit reports from M1→M6;
      - raw experimental evidence, in which case M1→M6 are invoked when
        available;
      - partial diagnostic dictionaries.

    Main outputs:
      - revision_priority
      - revision_impact
      - revision_urgency
      - scientific_revision_recommendations
    """

    primitive = "self_revision_recommendation_engine"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "scientific_supervision"
        self.report_path = self.report_dir / "self_revision_recommendation_engine_report.json"
        self.history_path = self.report_dir / "self_revision_recommendation_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            if value is None or isinstance(value, bool):
                return default
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _mean(values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _invoke_m1_to_m6(self, payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Invoke upstream scientific monitors defensively when reports are absent."""
        reports: dict[str, dict[str, Any]] = {}

        explicit_map = {
            "evidence_quality": ("evidence_quality_assessment", "evidence_quality_assessment_report", "m1"),
            "statistical_robustness": ("statistical_robustness_evaluator", "statistical_robustness_evaluator_report", "m2"),
            "false_positive": ("false_positive_detector", "false_positive_detector_report", "m3"),
            "bias": ("bias_detection_engine", "bias_report", "m4"),
            "scientific_consistency": ("scientific_consistency_validator", "scientific_consistency_report", "m5"),
            "anomaly": ("anomaly_in_evidence_detector", "anomaly_in_evidence_report", "m6"),
        }

        for canonical, keys in explicit_map.items():
            for key in keys:
                if isinstance(payload.get(key), dict):
                    reports[canonical] = dict(payload[key])
                    break

        # Also accept already flattened module outputs.
        for canonical, keys in explicit_map.items():
            if canonical not in reports and any(k in payload for k in keys):
                reports[canonical] = dict(payload)

        if payload.get("use_upstream", True) is False:
            return reports

        upstream_specs = [
            ("evidence_quality", "ontology.evidence_quality_assessment", "EvidenceQualityAssessment"),
            ("statistical_robustness", "ontology.statistical_robustness_evaluator", "StatisticalRobustnessEvaluator"),
            ("false_positive", "ontology.false_positive_detector", "FalsePositiveDetector"),
            ("bias", "ontology.bias_detection_engine", "BiasDetectionEngine"),
            ("scientific_consistency", "ontology.scientific_consistency_validator", "ScientificConsistencyValidator"),
            ("anomaly", "ontology.anomaly_in_evidence_detector", "AnomalyInEvidenceDetector"),
        ]

        for canonical, module_name, class_name in upstream_specs:
            if canonical in reports:
                continue
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                try:
                    result = instance.step(payload, persist=False)
                except TypeError:
                    try:
                        result = instance.step(payload)
                    except TypeError:
                        result = instance.step()
                if isinstance(result, dict):
                    reports[canonical] = result
            except Exception as exc:  # defensive: M7 must not break validation if an upstream monitor changes
                reports[canonical] = {
                    "success": False,
                    "upstream_error": f"{type(exc).__name__}: {exc}",
                }

        return reports

    def _signal_evidence_quality(self, report: dict[str, Any]) -> dict[str, Any]:
        quality = self._clamp(
            report.get("evidence_quality_score", report.get("quality_score", report.get("evidence_quality"))),
            default=0.0,
        )
        decision = str(report.get("evidence_decision", report.get("quality_decision", ""))).lower()
        risk = 1.0 - quality
        if "weak" in decision:
            risk = max(risk, 0.85)
        elif "moderate" in decision or "review" in decision:
            risk = max(risk, 0.45)
        elif "strong" in decision:
            risk = min(risk, 0.25)
        return {
            "source": "evidence_quality_assessment",
            "risk": self._clamp(risk),
            "impact": self._clamp(0.85 * risk + 0.15 * (1.0 - quality)),
            "urgency": self._clamp(0.75 * risk + 0.25 * (1.0 - quality)),
            "title": "Improve evidence quality",
            "action": "increase sample support, traceability and independent replication before strengthening scientific claims",
            "reason": f"evidence_quality_score={quality:.3f}; decision={decision or 'unspecified'}",
        }

    def _signal_statistical_robustness(self, report: dict[str, Any]) -> dict[str, Any]:
        score = self._clamp(
            report.get("statistical_robustness_score", report.get("robustness_score", report.get("robustness_index"))),
            default=0.0,
        )
        decision = str(report.get("robustness_decision", "")).lower()
        risk = 1.0 - score
        if decision == "fragile_results":
            risk = max(risk, 0.90)
        elif decision == "review_recommended":
            risk = max(risk, 0.60)
        elif decision == "robust_results":
            risk = min(risk, 0.25)
        return {
            "source": "statistical_robustness_evaluator",
            "risk": self._clamp(risk),
            "impact": self._clamp(0.80 * risk + 0.20 * (1.0 - score)),
            "urgency": self._clamp(0.70 * risk + 0.30 * (1.0 - score)),
            "title": "Strengthen statistical robustness",
            "action": "run additional robustness checks, perturbation tests and sensitivity analysis before accepting the result as stable",
            "reason": f"robustness_score={score:.3f}; decision={decision or 'unspecified'}",
        }

    def _signal_false_positive(self, report: dict[str, Any]) -> dict[str, Any]:
        risk = self._clamp(
            report.get("false_positive_risk", report.get("false_positive_risk_score", report.get("risk_score"))),
            default=0.0,
        )
        decision = str(report.get("false_positive_decision", report.get("risk_decision", ""))).lower()
        if decision == "high_risk":
            risk = max(risk, 0.90)
        elif decision == "moderate_risk":
            risk = max(risk, 0.55)
        elif decision == "low_risk":
            risk = min(risk, 0.25)
        return {
            "source": "false_positive_detector",
            "risk": self._clamp(risk),
            "impact": self._clamp(0.90 * risk + 0.10),
            "urgency": self._clamp(0.85 * risk + 0.05),
            "title": "Reduce false-positive risk",
            "action": "downgrade unsupported positive claims and require replication or stricter controls",
            "reason": f"false_positive_risk={risk:.3f}; decision={decision or 'unspecified'}",
        }

    def _signal_bias(self, report: dict[str, Any]) -> dict[str, Any]:
        risk = self._clamp(
            report.get("bias_risk_score", report.get("bias_score", report.get("bias_index"))),
            default=0.0,
        )
        decision = str(report.get("bias_decision", "")).lower()
        if decision == "high_bias_risk":
            risk = max(risk, 0.90)
        elif decision == "moderate_bias_risk":
            risk = max(risk, 0.55)
        elif decision == "low_bias_risk":
            risk = min(risk, 0.25)
        return {
            "source": "bias_detection_engine",
            "risk": self._clamp(risk),
            "impact": self._clamp(0.75 * risk + 0.10),
            "urgency": self._clamp(0.70 * risk + 0.05),
            "title": "Mitigate scientific bias",
            "action": "diversify evidence sources, rebalance sampling and add bias controls to the validation protocol",
            "reason": f"bias_risk_score={risk:.3f}; decision={decision or 'unspecified'}",
        }

    def _signal_consistency(self, report: dict[str, Any]) -> dict[str, Any]:
        consistency = self._clamp(
            report.get("scientific_consistency_score", report.get("consistency_score", report.get("coherence_score"))),
            default=0.0,
        )
        contradiction = self._clamp(report.get("contradiction_risk", report.get("inconsistency_score")), default=0.0)
        decision = str(report.get("consistency_decision", "")).lower()
        risk = max(1.0 - consistency, contradiction)
        if decision == "scientific_inconsistency":
            risk = max(risk, 0.90)
        elif decision == "review_recommended":
            risk = max(risk, 0.60)
        elif decision == "scientifically_consistent":
            risk = min(risk, 0.30)
        return {
            "source": "scientific_consistency_validator",
            "risk": self._clamp(risk),
            "impact": self._clamp(0.85 * risk + 0.15 * contradiction),
            "urgency": self._clamp(0.75 * risk + 0.25 * contradiction),
            "title": "Resolve scientific inconsistency",
            "action": "isolate contradictory assumptions and require consistency repair before downstream certification",
            "reason": f"consistency_score={consistency:.3f}; contradiction_risk={contradiction:.3f}; decision={decision or 'unspecified'}",
        }

    def _signal_anomaly(self, report: dict[str, Any]) -> dict[str, Any]:
        probability = self._clamp(report.get("anomaly_probability", report.get("anomaly_signal_score")), default=0.0)
        paradigm_shift = self._clamp(report.get("paradigm_shift_score"), default=0.0)
        artifact = self._clamp(report.get("measurement_artifact_risk"), default=0.0)
        decision = str(report.get("anomaly_decision", "")).lower()
        risk = max(probability, artifact, 0.7 * paradigm_shift)
        if decision == "suspicious_result":
            risk = max(risk, 0.90)
        elif decision == "review_recommended":
            risk = max(risk, 0.60)
        elif decision == "no_anomaly_detected":
            risk = min(risk, 0.30)
        return {
            "source": "anomaly_in_evidence_detector",
            "risk": self._clamp(risk),
            "impact": self._clamp(max(probability, paradigm_shift, artifact)),
            "urgency": self._clamp(0.50 * probability + 0.30 * artifact + 0.20 * paradigm_shift),
            "title": "Investigate anomalous evidence",
            "action": "separate potential discovery signals from measurement artifacts before revising theory or validation criteria",
            "reason": f"anomaly_probability={probability:.3f}; paradigm_shift_score={paradigm_shift:.3f}; measurement_artifact_risk={artifact:.3f}; decision={decision or 'unspecified'}",
        }

    def _build_signals(self, reports: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        builders = [
            ("evidence_quality", self._signal_evidence_quality),
            ("statistical_robustness", self._signal_statistical_robustness),
            ("false_positive", self._signal_false_positive),
            ("bias", self._signal_bias),
            ("scientific_consistency", self._signal_consistency),
            ("anomaly", self._signal_anomaly),
        ]
        signals: list[dict[str, Any]] = []
        for key, builder in builders:
            report = self._as_dict(reports.get(key))
            signal = builder(report)
            signal["available"] = bool(report)
            signal["upstream_success"] = report.get("success", True) if report else False
            signals.append(signal)
        return signals

    def _recommendation_decision(self, priority: float) -> str:
        if priority >= 0.72:
            return "self_revision_required"
        if priority >= 0.42:
            return "review_recommended"
        return "monitoring_only"

    def _build_recommendations(self, signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        for signal in signals:
            risk = self._clamp(signal.get("risk"))
            impact = self._clamp(signal.get("impact"))
            urgency = self._clamp(signal.get("urgency"))
            priority = self._clamp(0.45 * risk + 0.35 * impact + 0.20 * urgency)
            if priority < 0.05:
                continue
            recommendations.append({
                "recommendation_id": f"M7-{signal['source'].upper()}",
                "source": signal["source"],
                "title": signal["title"],
                "recommended_action": signal["action"],
                "revision_priority": round(priority, 6),
                "revision_impact": round(impact, 6),
                "revision_urgency": round(urgency, 6),
                "risk_score": round(risk, 6),
                "decision": self._recommendation_decision(priority),
                "requires_governance_review": priority >= 0.42,
                "requires_human_review": priority >= 0.72,
                "non_execution_notice": "recommendation_only_no_automatic_revision",
                "reason": signal.get("reason", "unspecified"),
            })
        recommendations.sort(
            key=lambda item: (
                item["revision_priority"],
                item["revision_impact"],
                item["revision_urgency"],
                item["source"],
            ),
            reverse=True,
        )
        for idx, item in enumerate(recommendations, start=1):
            item["rank"] = idx
        return recommendations

    def step(self, inputs: Any = None, *, persist: bool = True, reset: bool = False, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if isinstance(inputs, dict):
            payload.update(inputs)
        elif inputs is not None:
            payload["records"] = inputs
        payload.update(kwargs)

        if reset and self.history_path.exists():
            self.history_path.unlink()

        reports = self._invoke_m1_to_m6(payload)
        signals = self._build_signals(reports)
        recommendations = self._build_recommendations(signals)

        priority_values = [self._clamp(item.get("revision_priority")) for item in recommendations]
        impact_values = [self._clamp(item.get("revision_impact")) for item in recommendations]
        urgency_values = [self._clamp(item.get("revision_urgency")) for item in recommendations]

        revision_priority = max(priority_values) if priority_values else 0.0
        revision_impact = self._mean(impact_values) if impact_values else 0.0
        revision_urgency = max(urgency_values) if urgency_values else 0.0

        if revision_priority >= 0.72:
            global_decision = "self_revision_required"
        elif revision_priority >= 0.42:
            global_decision = "review_recommended"
        else:
            global_decision = "scientifically_stable"

        result = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": self._utc_now(),
            "revision_priority": round(revision_priority, 6),
            "revision_impact": round(revision_impact, 6),
            "revision_urgency": round(revision_urgency, 6),
            "self_revision_required": global_decision == "self_revision_required",
            "review_recommended": global_decision == "review_recommended",
            "scientific_revision_decision": global_decision,
            "scientific_revision_recommendations": recommendations,
            "recommendation_count": len(recommendations),
            "top_recommendation": recommendations[0] if recommendations else None,
            "source_signal_summary": {
                signal["source"]: {
                    "risk": round(self._clamp(signal.get("risk")), 6),
                    "impact": round(self._clamp(signal.get("impact")), 6),
                    "urgency": round(self._clamp(signal.get("urgency")), 6),
                    "available": bool(signal.get("available")),
                }
                for signal in signals
            },
            "epistemic_position": "functional_scientific_supervision_only_no_phenomenal_claim",
            "report_path": str(self.report_path),
        }
        result["self_revision_recommendation_engine_report"] = {
            "primitive": self.primitive,
            "revision_priority": result["revision_priority"],
            "revision_impact": result["revision_impact"],
            "revision_urgency": result["revision_urgency"],
            "decision": global_decision,
            "recommendation_count": len(recommendations),
        }

        if persist:
            self.report_dir.mkdir(parents=True, exist_ok=True)
            self.report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")

        return result


if __name__ == "__main__":
    from pprint import pprint

    pprint(SelfRevisionRecommendationEngine().step(persist=True))
