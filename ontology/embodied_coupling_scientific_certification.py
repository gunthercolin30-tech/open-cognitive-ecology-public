# -*- coding: utf-8 -*-

"""
G20 - Embodied Coupling Scientific Certification.

Consolidated scientific certification layer for the whole G embodied coupling
sequence. It integrates:
- G17 instantaneous embodied runtime coupling;
- G18 longitudinal environmental grounding stability;
- G19 dashboard/export reproducibility;
- anomaly, significance and non-closure compatible interpretation.

This primitive certifies functional and empirical indicators only. It does not
assert phenomenal subjectivity.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import math
from typing import Any, Optional

PRIMITIVE = "embodied_coupling_scientific_certification"
REFINEMENT = "G20-R1"

DEPENDENCIES = [
    "embodied_runtime_coupling_certifier",
    "environmental_grounding_longitudinal_observatory",
    "embodied_coupling_dashboard_exporter",
    "metrics_statistical_significance_engine",
    "metrics_anomaly_detection_engine",
    "scientific_meta_analysis_engine",
    "scientific_theory_confidence_engine",
    "scientific_self_revision_controller",
    "non_closure_certification_protocol",
    "openness_preservation_supervisor",
]

SCORE_KEYS = [
    "embodied_scientific_certification_score",
    "embodied_scientific_confidence_index",
    "embodied_scientific_significance_score",
    "embodied_scientific_anomaly_penalty",
    "embodied_grounding_evidence_score",
    "embodied_coupling_reproducibility_score",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if math.isnan(number) or math.isinf(number):
        number = default
    return max(0.0, min(1.0, number))


def _certification_level(score: float) -> str:
    score = _clamp(score)
    if score >= 0.95:
        return "Platinum Embodied Coupling Scientific Certification"
    if score >= 0.90:
        return "Gold Embodied Coupling Scientific Certification"
    if score >= 0.80:
        return "Silver Embodied Coupling Scientific Certification"
    if score >= 0.70:
        return "Bronze Embodied Coupling Scientific Certification"
    return "Embodied Coupling Scientific Certification Not Established"


def _publication_status(score: float, confidence: float, anomaly: float) -> str:
    if score >= 0.90 and confidence >= 0.85 and anomaly <= 0.10:
        return "publication_ready"
    if score >= 0.75 and confidence >= 0.65 and anomaly <= 0.25:
        return "prepublication_review"
    return "insufficient_evidence"


class EmbodiedCouplingScientificCertification:
    primitive = PRIMITIVE

    def __init__(self, root: Optional[str | Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.archive_dir = self.root / "runtime_experiments" / "embodied_coupling_scientific_certification"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.archive_dir / "embodied_coupling_scientific_certification_history.jsonl"
        self.state_path = self.archive_dir / "embodied_coupling_scientific_certification_state.json"
        self.report_path = self.archive_dir / "embodied_coupling_scientific_certification_report.json"

    def _collect_g17(self) -> dict[str, Any]:
        try:
            from ontology.embodied_runtime_coupling_certifier import EmbodiedRuntimeCouplingCertifier
            result = EmbodiedRuntimeCouplingCertifier(root=self.root).step()
            if isinstance(result, dict):
                return result
        except Exception as exc:
            return {"error_count": 1, "error": repr(exc)}
        return {}

    def _collect_g18(self) -> dict[str, Any]:
        try:
            from ontology.environmental_grounding_longitudinal_observatory import EnvironmentalGroundingLongitudinalObservatory
            result = EnvironmentalGroundingLongitudinalObservatory(root=self.root).step()
            if isinstance(result, dict):
                return result
        except Exception as exc:
            return {"error_count": 1, "error": repr(exc)}
        return {}

    def _collect_g19(self) -> dict[str, Any]:
        try:
            from ontology.embodied_coupling_dashboard_exporter import EmbodiedCouplingDashboardExporter
            result = EmbodiedCouplingDashboardExporter(root=self.root).step()
            if isinstance(result, dict):
                return result
        except Exception as exc:
            return {"error_count": 1, "error": repr(exc)}
        return {}

    def _append_history(self, result: dict[str, Any]) -> None:
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    def _write_state(self, result: dict[str, Any]) -> None:
        self.state_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        self.report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _history_count(self) -> int:
        if not self.history_path.exists():
            return 0
        try:
            return len(self.history_path.read_text(encoding="utf-8", errors="ignore").splitlines())
        except Exception:
            return 0

    def step(self, inputs: Optional[dict[str, Any]] = None, **overrides: Any) -> dict[str, Any]:
        data = dict(inputs or {})
        data.update(overrides)

        g17 = data.get("g17_result") if isinstance(data.get("g17_result"), dict) else self._collect_g17()
        g18 = data.get("g18_result") if isinstance(data.get("g18_result"), dict) else self._collect_g18()
        g19 = data.get("g19_result") if isinstance(data.get("g19_result"), dict) else self._collect_g19()

        grounding_evidence = _clamp(
            data.get(
                "embodied_grounding_evidence_score",
                0.50 * _clamp(g17.get("runtime_environment_coupling_index", 0.0))
                + 0.50 * _clamp(g17.get("environmental_grounding_index", 0.0)),
            )
        )

        longitudinal_stability = _clamp(
            data.get(
                "longitudinal_stability_score",
                g18.get("environmental_grounding_stability_index", 0.0),
            )
        )

        significance_score = _clamp(
            data.get(
                "embodied_scientific_significance_score",
                g18.get("coupling_significance_score", 0.0),
            )
        )

        anomaly_penalty = _clamp(
            data.get(
                "embodied_scientific_anomaly_penalty",
                g18.get("coupling_anomaly_score", 0.0),
            )
        )

        reproducibility_score = _clamp(
            data.get(
                "embodied_coupling_reproducibility_score",
                0.34 * float(bool(g19.get("html_export_success")))
                + 0.33 * float(bool(g19.get("prometheus_export_success")))
                + 0.33 * float(bool(g19.get("json_state_export_success"))),
            )
        )

        non_closure_score = _clamp(
            data.get(
                "non_closure_compliance_score",
                1.0 if g17.get("phenomenal_subjectivity_claimed", False) is False and
                g18.get("phenomenal_subjectivity_claimed", False) is False and
                g19.get("phenomenal_subjectivity_claimed", False) is False else 0.0,
            )
        )

        confidence = _clamp(
            data.get(
                "embodied_scientific_confidence_index",
                0.35 * grounding_evidence
                + 0.25 * longitudinal_stability
                + 0.20 * reproducibility_score
                + 0.20 * non_closure_score,
            )
        )

        certification_score = _clamp(
            data.get(
                "embodied_scientific_certification_score",
                0.30 * grounding_evidence
                + 0.25 * longitudinal_stability
                + 0.15 * significance_score
                + 0.15 * reproducibility_score
                + 0.15 * non_closure_score
                - 0.25 * anomaly_penalty,
            )
        )

        if anomaly_penalty > 0.35:
            recommendation = "revise_before_publication"
        elif certification_score >= 0.80:
            recommendation = "certification_supported"
        elif certification_score >= 0.65:
            recommendation = "continue_longitudinal_sampling"
        else:
            recommendation = "insufficient_embodied_grounding_evidence"

        history_count_before = self._history_count()

        result = {
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "timestamp_utc": _now(),
            "embodied_scientific_certification_score": round(certification_score, 6),
            "embodied_scientific_confidence_index": round(confidence, 6),
            "embodied_scientific_significance_score": round(significance_score, 6),
            "embodied_scientific_anomaly_penalty": round(anomaly_penalty, 6),
            "embodied_grounding_evidence_score": round(grounding_evidence, 6),
            "embodied_coupling_reproducibility_score": round(reproducibility_score, 6),
            "longitudinal_stability_score": round(longitudinal_stability, 6),
            "non_closure_compliance_score": round(non_closure_score, 6),
            "embodied_scientific_certification_level": _certification_level(certification_score),
            "publication_status": _publication_status(certification_score, confidence, anomaly_penalty),
            "recommendation": recommendation,
            "history_path": str(self.history_path),
            "state_path": str(self.state_path),
            "report_path": str(self.report_path),
            "history_count_before": history_count_before,
            "functional_measurement_only": True,
            "phenomenal_subjectivity_claimed": False,
            "dependencies": DEPENDENCIES,
            "g17_summary": {
                "runtime_environment_coupling_index": _clamp(g17.get("runtime_environment_coupling_index", 0.0)),
                "environmental_grounding_index": _clamp(g17.get("environmental_grounding_index", 0.0)),
                "certification": g17.get("certification", "unknown"),
            },
            "g18_summary": {
                "environmental_grounding_stability_index": _clamp(g18.get("environmental_grounding_stability_index", 0.0)),
                "coupling_significance_score": _clamp(g18.get("coupling_significance_score", 0.0)),
                "coupling_anomaly_score": _clamp(g18.get("coupling_anomaly_score", 0.0)),
                "certification": g18.get("coupling_longitudinal_certification", "unknown"),
            },
            "g19_summary": {
                "dashboard_score": _clamp(g19.get("dashboard_score", 0.0)),
                "dashboard_certification": g19.get("dashboard_certification", "unknown"),
                "html_export_success": bool(g19.get("html_export_success", False)),
                "prometheus_export_success": bool(g19.get("prometheus_export_success", False)),
                "json_state_export_success": bool(g19.get("json_state_export_success", False)),
            },
            "error_count": 0,
        }

        self._write_state(result)
        self._append_history(result)
        result["history_count_after"] = self._history_count()

        try:
            from ontology.metrics_history_recorder import record_metrics
            record_metrics(
                result,
                primitive=PRIMITIVE,
                validation_status=True,
                governance_status="governed",
                runtime_status="operational",
            )
            result["metrics_recorded"] = True
        except Exception as exc:
            result["metrics_recorded"] = False
            result["metrics_record_error"] = repr(exc)

        return result


ENGINE = EmbodiedCouplingScientificCertification()


def step(inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return ENGINE.step(inputs)
