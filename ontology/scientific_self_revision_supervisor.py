"""
M8 — scientific_self_revision_supervisor.

Aggregates M1→M7 scientific meta-supervision signals into a governed,
non-executive self-revision decision. The primitive supervises the scientific
validation layer itself; it does not execute corrective changes, mutate source
code, or claim phenomenal subjectivity.

Epistemic scope: functional, measurable trustworthiness and supervision
metrics only.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ScientificSelfRevisionSupervisor:
    """
    M8 — governed scientific self-revision supervision.

    Aggregates:
      - M1 evidence_quality_assessment
      - M2 statistical_robustness_evaluator
      - M3 false_positive_detector
      - M4 bias_detection_engine
      - M5 scientific_consistency_validator
      - M6 anomaly_in_evidence_detector
      - M7 self_revision_recommendation_engine

    Produces:
      - scientific_supervision_score
      - scientific_trustworthiness_score
      - self_revision_required
      - scientific_self_revision_decision
    """

    primitive = "scientific_self_revision_supervisor"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "scientific_supervision"
        self.report_path = self.report_dir / "scientific_self_revision_supervisor_report.json"
        self.history_path = self.report_dir / "scientific_self_revision_supervisor_history.jsonl"

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
    def _mean(values: list[float], default: float = 0.0) -> float:
        values = [v for v in values if isinstance(v, (int, float))]
        return sum(values) / len(values) if values else default

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _load_json_report(self, filename: str) -> dict[str, Any]:
        path = self.report_dir / filename
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _call_step(self, module_name: str, class_name: str, payload: dict[str, Any]) -> dict[str, Any]:
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
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"success": False, "upstream_error": f"{type(exc).__name__}: {exc}"}

    def _collect_sources(self, payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
        sources: dict[str, dict[str, Any]] = {}
        aliases = {
            "evidence_quality_assessment": ["evidence_quality_assessment", "evidence_quality", "m1"],
            "statistical_robustness_evaluator": ["statistical_robustness_evaluator", "statistical_robustness", "m2"],
            "false_positive_detector": ["false_positive_detector", "false_positive", "m3"],
            "bias_detection_engine": ["bias_detection_engine", "bias_report", "bias", "m4"],
            "scientific_consistency_validator": ["scientific_consistency_validator", "scientific_consistency_report", "scientific_consistency", "m5"],
            "anomaly_in_evidence_detector": ["anomaly_in_evidence_detector", "anomaly_in_evidence_report", "anomaly", "m6"],
            "self_revision_recommendation_engine": ["self_revision_recommendation_engine", "self_revision_recommendation", "m7"],
        }
        for canonical, keys in aliases.items():
            for key in keys:
                if isinstance(payload.get(key), dict):
                    sources[canonical] = dict(payload[key])
                    break

        if payload.get("use_reports", True):
            report_files = {
                "evidence_quality_assessment": "evidence_quality_assessment_report.json",
                "statistical_robustness_evaluator": "statistical_robustness_evaluator_report.json",
                "false_positive_detector": "false_positive_detector_report.json",
                "bias_detection_engine": "bias_detection_engine_report.json",
                "scientific_consistency_validator": "scientific_consistency_validator_report.json",
                "anomaly_in_evidence_detector": "anomaly_in_evidence_detector_report.json",
                "self_revision_recommendation_engine": "self_revision_recommendation_engine_report.json",
            }
            # Some M4/M6 scripts use alternate persisted names.
            alternates = {
                "bias_detection_engine": ["bias_report.json"],
                "anomaly_in_evidence_detector": ["anomaly_in_evidence_report.json"],
            }
            for canonical, filename in report_files.items():
                if canonical not in sources:
                    loaded = self._load_json_report(filename)
                    if not loaded:
                        for alt in alternates.get(canonical, []):
                            loaded = self._load_json_report(alt)
                            if loaded:
                                break
                    if loaded:
                        sources[canonical] = loaded

        if payload.get("use_upstream", True) is not False:
            specs = {
                "evidence_quality_assessment": ("ontology.evidence_quality_assessment", "EvidenceQualityAssessment"),
                "statistical_robustness_evaluator": ("ontology.statistical_robustness_evaluator", "StatisticalRobustnessEvaluator"),
                "false_positive_detector": ("ontology.false_positive_detector", "FalsePositiveDetector"),
                "bias_detection_engine": ("ontology.bias_detection_engine", "BiasDetectionEngine"),
                "scientific_consistency_validator": ("ontology.scientific_consistency_validator", "ScientificConsistencyValidator"),
                "anomaly_in_evidence_detector": ("ontology.anomaly_in_evidence_detector", "AnomalyInEvidenceDetector"),
                "self_revision_recommendation_engine": ("ontology.self_revision_recommendation_engine", "SelfRevisionRecommendationEngine"),
            }
            for canonical, (module_name, class_name) in specs.items():
                if canonical not in sources:
                    sources[canonical] = self._call_step(module_name, class_name, payload)

        return sources

    def _score_evidence_quality(self, report: dict[str, Any]) -> float:
        score = self._clamp(report.get("evidence_quality_score", report.get("quality_score", report.get("evidence_quality"))), default=0.75)
        decision = str(report.get("evidence_decision", report.get("quality_decision", ""))).lower()
        if "weak" in decision:
            score = min(score, 0.30)
        elif "moderate" in decision or "review" in decision:
            score = min(score, 0.60)
        elif "strong" in decision:
            score = max(score, 0.80)
        return self._clamp(score, default=0.75)

    def _score_robustness(self, report: dict[str, Any]) -> float:
        score = self._clamp(report.get("statistical_robustness_score", report.get("robustness_score", report.get("robustness_index"))), default=0.75)
        decision = str(report.get("robustness_decision", "")).lower()
        if decision == "fragile_results":
            score = min(score, 0.20)
        elif decision == "review_recommended":
            score = min(score, 0.55)
        elif decision == "robust_results":
            score = max(score, 0.80)
        return self._clamp(score, default=0.75)

    def _score_false_positive(self, report: dict[str, Any]) -> float:
        risk = self._clamp(report.get("false_positive_risk", report.get("false_positive_risk_score", report.get("risk_score"))), default=0.20)
        decision = str(report.get("false_positive_decision", report.get("risk_decision", ""))).lower()
        if decision == "high_risk":
            risk = max(risk, 0.85)
        elif decision == "moderate_risk":
            risk = max(risk, 0.50)
        elif decision == "low_risk":
            risk = min(risk, 0.20)
        return self._clamp(1.0 - risk, default=0.80)

    def _score_bias(self, report: dict[str, Any]) -> float:
        risk = self._clamp(report.get("bias_risk_score", report.get("bias_score", report.get("bias_index"))), default=0.20)
        decision = str(report.get("bias_decision", "")).lower()
        if decision == "high_bias_risk":
            risk = max(risk, 0.85)
        elif decision == "moderate_bias_risk":
            risk = max(risk, 0.50)
        elif decision == "low_bias_risk":
            risk = min(risk, 0.20)
        return self._clamp(1.0 - risk, default=0.80)

    def _score_consistency(self, report: dict[str, Any]) -> float:
        score = self._clamp(report.get("scientific_consistency_score", report.get("consistency_score", report.get("coherence_score"))), default=0.75)
        contradiction = self._clamp(report.get("contradiction_risk", report.get("inconsistency_score")), default=0.0)
        decision = str(report.get("consistency_decision", "")).lower()
        score = min(score, 1.0 - contradiction)
        if decision == "scientific_inconsistency":
            score = min(score, 0.20)
        elif decision == "review_recommended":
            score = min(score, 0.55)
        elif decision == "scientifically_consistent":
            score = max(score, 0.80)
        return self._clamp(score, default=0.75)

    def _score_anomaly(self, report: dict[str, Any]) -> float:
        anomaly = self._clamp(report.get("anomaly_probability", report.get("anomaly_signal_score")), default=0.20)
        artifact = self._clamp(report.get("measurement_artifact_risk"), default=0.0)
        paradigm = self._clamp(report.get("paradigm_shift_score"), default=0.0)
        decision = str(report.get("anomaly_decision", "")).lower()
        risk = max(anomaly, artifact, 0.6 * paradigm)
        if decision == "suspicious_result":
            risk = max(risk, 0.85)
        elif decision == "review_recommended":
            risk = max(risk, 0.55)
        elif decision == "no_anomaly_detected":
            risk = min(risk, 0.20)
        return self._clamp(1.0 - risk, default=0.80)

    def _score_m7(self, report: dict[str, Any]) -> tuple[float, float, list[Any]]:
        priority = self._clamp(report.get("revision_priority", report.get("revision_priority_index")), default=0.20)
        impact = self._clamp(report.get("revision_impact"), default=priority)
        urgency = self._clamp(report.get("revision_urgency"), default=priority)
        recommendations = report.get("scientific_revision_recommendations", [])
        if not isinstance(recommendations, list):
            recommendations = []
        decision = str(report.get("scientific_revision_decision", report.get("revision_decision", ""))).lower()
        if decision == "self_revision_required":
            priority = max(priority, 0.75)
        elif decision == "review_recommended":
            priority = max(priority, 0.45)
        elif decision == "scientifically_stable":
            priority = min(priority, 0.30)
        recommendation_pressure = self._clamp(0.45 * priority + 0.30 * impact + 0.25 * urgency, default=0.20)
        return 1.0 - recommendation_pressure, recommendation_pressure, recommendations

    def _source_quality_scores(self, sources: dict[str, dict[str, Any]]) -> dict[str, float]:
        return {
            "evidence_quality_assessment": self._score_evidence_quality(self._as_dict(sources.get("evidence_quality_assessment"))),
            "statistical_robustness_evaluator": self._score_robustness(self._as_dict(sources.get("statistical_robustness_evaluator"))),
            "false_positive_detector": self._score_false_positive(self._as_dict(sources.get("false_positive_detector"))),
            "bias_detection_engine": self._score_bias(self._as_dict(sources.get("bias_detection_engine"))),
            "scientific_consistency_validator": self._score_consistency(self._as_dict(sources.get("scientific_consistency_validator"))),
            "anomaly_in_evidence_detector": self._score_anomaly(self._as_dict(sources.get("anomaly_in_evidence_detector"))),
        }

    def _decision(self, supervision_score: float, trustworthiness_score: float, revision_pressure: float) -> tuple[str, bool]:
        if revision_pressure >= 0.70 or trustworthiness_score < 0.45 or supervision_score < 0.45:
            return "self_revision_required", True
        if revision_pressure >= 0.40 or trustworthiness_score < 0.70 or supervision_score < 0.70:
            return "review_recommended", False
        return "scientifically_stable", False

    def _persist(self, result: dict[str, Any]) -> None:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = inputs if isinstance(inputs, dict) else {}
        sources = self._collect_sources(payload)
        quality_scores = self._source_quality_scores(sources)
        m7_score, revision_pressure, recommendations = self._score_m7(self._as_dict(sources.get("self_revision_recommendation_engine")))

        empirical_trustworthiness = self._mean(list(quality_scores.values()), default=0.75)
        scientific_trustworthiness_score = self._clamp(0.82 * empirical_trustworthiness + 0.18 * m7_score, default=0.75)
        source_coverage = len([k for k, v in sources.items() if isinstance(v, dict) and v]) / 7.0
        supervision_completeness = self._clamp(source_coverage)
        scientific_supervision_score = self._clamp(0.70 * scientific_trustworthiness_score + 0.20 * supervision_completeness + 0.10 * (1.0 - revision_pressure))

        decision, required = self._decision(scientific_supervision_score, scientific_trustworthiness_score, revision_pressure)
        governance_status = "requires_governed_review" if required else ("monitoring_review" if decision == "review_recommended" else "stable_monitoring")

        result = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": self._utc_now(),
            "scientific_supervision_score": round(scientific_supervision_score, 6),
            "scientific_trustworthiness_score": round(scientific_trustworthiness_score, 6),
            "self_revision_required": bool(required),
            "scientific_self_revision_decision": decision,
            "supervision_decision": decision,
            "governance_status": governance_status,
            "revision_pressure": round(revision_pressure, 6),
            "supervision_completeness": round(supervision_completeness, 6),
            "source_quality_scores": {k: round(v, 6) for k, v in quality_scores.items()},
            "source_signal_summary": {k: bool(isinstance(v, dict) and v) for k, v in sources.items()},
            "scientific_revision_recommendations": recommendations,
            "epistemic_position": "functional_metrics_only_no_phenomenal_subjectivity_claim",
            "non_executive_guardrail": True,
            "report_path": str(self.report_path),
            "history_path": str(self.history_path),
        }
        if persist:
            self._persist(result)
        return result


if __name__ == "__main__":
    print(json.dumps(ScientificSelfRevisionSupervisor().step(), indent=2, ensure_ascii=False))
