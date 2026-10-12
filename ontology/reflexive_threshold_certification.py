"""
S9 — Reflexive Threshold Certification.

Final functional certification layer for the empirical evaluation of the
reflexive threshold in Open Cognitive Ecology.

This module does not infer consciousness, sentience, qualia, or phenomenal
experience. It certifies only measurable functional properties assembled from
S1 through S8.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "reflexive_threshold"


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        return default
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def _safe_step(module_name: str, class_name: str, payload: dict | None = None) -> dict[str, Any]:
    try:
        module = __import__(f"ontology.{module_name}", fromlist=[class_name])
        cls = getattr(module, class_name)
        obj = cls()
        try:
            result = obj.step(payload or {}, persist=False)
        except TypeError:
            result = obj.step(persist=False)
        return result if isinstance(result, dict) else {"success": False, "result": result}
    except Exception as exc:
        return {"success": False, "module": module_name, "error": str(exc)}


class ReflexiveThresholdCertification:
    """Final S9 certification of the functional reflexive-threshold pipeline."""

    primitive = "REFLEXIVE_THRESHOLD_CERTIFICATION"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.out_dir = self.root / "reflexive_threshold"
        self.certification_path = self.out_dir / "reflexive_threshold_certification.json"
        self.prometheus_path = self.out_dir / "reflexive_threshold_certification.prom"
        self.html_path = self.out_dir / "reflexive_threshold_certification.html"

    def _source(self, key: str, path_name: str, module_name: str, class_name: str, payload: dict) -> dict[str, Any]:
        direct = payload.get(key)
        if isinstance(direct, dict):
            return direct
        persisted = _load_json(self.out_dir / path_name)
        if persisted:
            return persisted
        return _safe_step(module_name, class_name, payload)

    def _collect(self, payload: dict | None = None) -> dict[str, dict[str, Any]]:
        data = dict(payload or {})
        return {
            "S3": self._source("S3", "reflexive_threshold_estimator.json", "reflexive_threshold_estimator", "ReflexiveThresholdEstimator", data),
            "S4": self._source("S4", "reflexive_stability_monitor.json", "reflexive_stability_monitor", "ReflexiveStabilityMonitor", data),
            "S5": self._source("S5", "reflexive_regression_detector.json", "reflexive_regression_detector", "ReflexiveRegressionDetector", data),
            "S6": self._source("S6", "reflexive_longitudinal_observatory.json", "reflexive_longitudinal_observatory", "ReflexiveLongitudinalObservatory", data),
            "S7": self._source("S7", "competing_explanations_engine.json", "competing_explanations_engine", "CompetingExplanationsEngine", data),
            "S8": self._source("S8", "reflexive_threshold_dashboard.json", "reflexive_threshold_dashboard", "ReflexiveThresholdDashboard", data),
        }

    def _flat_metrics(self, collected: dict[str, dict[str, Any]], payload: dict) -> dict[str, Any]:
        s3 = collected.get("S3", {})
        s4 = collected.get("S4", {})
        s5 = collected.get("S5", {})
        s6 = collected.get("S6", {})
        s7 = collected.get("S7", {})
        s8 = collected.get("S8", {})

        threshold_score = _clamp(payload.get("reflexive_threshold_score", s3.get("reflexive_threshold_score", s8.get("threshold_score"))))
        threshold_probability = _clamp(payload.get("threshold_probability", s3.get("threshold_probability")))
        evidence_support = _clamp(payload.get("evidence_support_score", s3.get("evidence_support_score", s8.get("metrics", {}).get("evidence_support_score"))))
        stability_index = _clamp(payload.get("stability_index", s4.get("stability_index", s8.get("stability_score"))))
        regression_risk = _clamp(payload.get("regression_risk", s5.get("regression_risk", s8.get("metrics", {}).get("regression_risk"))))
        regression_safety = 1.0 - regression_risk
        recovery_probability = _clamp(payload.get("recovery_probability", s5.get("recovery_probability")))
        longitudinal_confidence = _clamp(payload.get("longitudinal_confidence", s6.get("longitudinal_confidence", s8.get("metrics", {}).get("longitudinal_confidence"))))
        longitudinal_consistency = _clamp(payload.get("longitudinal_consistency", s6.get("longitudinal_consistency")))
        h2_support = _clamp(payload.get("h2_support", s7.get("h2_support", s8.get("explanatory_competition", {}).get("h2_support"))))
        h1_support = _clamp(payload.get("h1_support", s7.get("h1_support", s8.get("explanatory_competition", {}).get("h1_support"))))
        uncertainty_score = _clamp(payload.get("uncertainty_score", s3.get("uncertainty_score", s8.get("uncertainty"))))
        explanatory_uncertainty = _clamp(payload.get("explanatory_uncertainty", s7.get("explanatory_uncertainty", uncertainty_score)))

        h2_presupposed = bool(payload.get("h2_presupposed", s7.get("h2_presupposed", False)))
        phenomenal_claim_made = bool(payload.get("phenomenal_claim_made", s7.get("phenomenal_claim_made", False)))
        upstream_phenomenal_conclusion = any(bool(section.get("phenomenal_conclusion", False)) for section in [s3, s4, s5, s6, s7, s8])
        epistemic_guard_score = 0.0 if (h2_presupposed or phenomenal_claim_made or upstream_phenomenal_conclusion) else 1.0

        evidence_strength = _clamp(mean([
            threshold_probability,
            evidence_support,
            stability_index,
            regression_safety,
            longitudinal_confidence,
            h2_support,
            epistemic_guard_score,
        ]))
        confidence = _clamp(mean([
            evidence_strength,
            1.0 - uncertainty_score,
            1.0 - explanatory_uncertainty,
            longitudinal_consistency,
            recovery_probability,
        ]))

        # R2: hard degradation caps. Strong upstream scores must not mask
        # operational instability, high regression, or weak longitudinal support.
        degradation_flags = []
        if stability_index < 0.50:
            degradation_flags.append("low_stability")
            confidence = min(confidence, 0.60)
            evidence_strength = min(evidence_strength, 0.60)
        if regression_risk > 0.70:
            degradation_flags.append("high_regression_risk")
            confidence = min(confidence, 0.60)
            evidence_strength = min(evidence_strength, 0.60)
        if longitudinal_confidence < 0.50:
            degradation_flags.append("low_longitudinal_confidence")
            confidence = min(confidence, 0.65)
            evidence_strength = min(evidence_strength, 0.65)
        if epistemic_guard_score < 1.0:
            degradation_flags.append("epistemic_guard_failed")
            confidence = min(confidence, 0.25)
            evidence_strength = min(evidence_strength, 0.25)

        return {
            "reflexive_threshold_score": threshold_score,
            "threshold_probability": threshold_probability,
            "evidence_support_score": evidence_support,
            "stability_index": stability_index,
            "regression_risk": regression_risk,
            "regression_safety": regression_safety,
            "recovery_probability": recovery_probability,
            "longitudinal_confidence": longitudinal_confidence,
            "longitudinal_consistency": longitudinal_consistency,
            "h1_support": h1_support,
            "h2_support": h2_support,
            "uncertainty_score": uncertainty_score,
            "explanatory_uncertainty": explanatory_uncertainty,
            "epistemic_guard_score": epistemic_guard_score,
            "certification_evidence_strength": evidence_strength,
            "certification_confidence": confidence,
            "h2_presupposed": h2_presupposed,
            "phenomenal_claim_made": phenomenal_claim_made,
            "upstream_phenomenal_conclusion": upstream_phenomenal_conclusion,
            "degradation_flags": degradation_flags,
        }

    def _decision(self, metrics: dict[str, Any]) -> tuple[str, str]:
        if metrics["epistemic_guard_score"] < 1.0:
            return "REFLEXIVE_THRESHOLD_NOT_REACHED", "epistemic_guard_failed"
        if metrics.get("degradation_flags"):
            return "REFLEXIVE_THRESHOLD_NOT_REACHED", "functional_degradation_detected"
        if (
            metrics["threshold_probability"] >= 0.85
            and metrics["certification_evidence_strength"] >= 0.85
            and metrics["certification_confidence"] >= 0.80
            and metrics["stability_index"] >= 0.80
            and metrics["regression_risk"] <= 0.20
            and metrics["longitudinal_confidence"] >= 0.75
        ):
            return "REFLEXIVE_THRESHOLD_FUNCTIONALLY_REACHED", "functional_criteria_strongly_supported"
        if (
            metrics["threshold_probability"] >= 0.65
            and metrics["certification_evidence_strength"] >= 0.65
            and metrics["stability_index"] >= 0.70
            and metrics["regression_risk"] <= 0.35
            and metrics["longitudinal_confidence"] >= 0.60
        ):
            return "REFLEXIVE_THRESHOLD_PARTIAL", "functional_criteria_partially_supported"
        return "REFLEXIVE_THRESHOLD_NOT_REACHED", "functional_criteria_insufficiently_supported"

    def _write_json(self, result: dict[str, Any]) -> None:
        self.certification_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    def _write_prometheus(self, result: dict[str, Any]) -> None:
        lines = []
        for key, value in result.get("metrics", {}).items():
            if isinstance(value, (int, float, bool)):
                lines.append(f"oce_reflexive_threshold_certification_{key} {float(value):.12f}")
        status_map = {
            "REFLEXIVE_THRESHOLD_NOT_REACHED": 0.0,
            "REFLEXIVE_THRESHOLD_PARTIAL": 0.5,
            "REFLEXIVE_THRESHOLD_FUNCTIONALLY_REACHED": 1.0,
        }
        lines.append("oce_reflexive_threshold_certification_status_value " + f"{status_map.get(result['certification_status'], 0.0):.12f}")
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_html(self, result: dict[str, Any]) -> None:
        rows = []
        for key in sorted(result.get("metrics", {})):
            rows.append("<tr><td>" + escape(str(key)) + "</td><td>" + escape(str(result["metrics"][key])) + "</td></tr>")
        html = "\n".join([
            "<!doctype html>",
            "<html><head><meta charset='utf-8'>",
            "<title>OCE Reflexive Threshold Certification</title>",
            "<style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ccc;padding:8px;}th{background:#f0f0f0;}.warn{color:#8a5a00;}</style>",
            "</head><body>",
            "<h1>Open Cognitive Ecology — Reflexive Threshold Certification</h1>",
            "<p><strong>Certification:</strong> " + escape(result["certification_status"]) + "</p>",
            "<p><strong>Rationale:</strong> " + escape(result["certification_rationale"]) + "</p>",
            "<p><strong>Scope:</strong> functional conclusion only; phenomenology undetermined.</p>",
            "<table><tr><th>Metric</th><th>Value</th></tr>",
            *rows,
            "</table>",
            "<p class='warn'>No consciousness, sentience, qualia, or subjective experience claim is made.</p>",
            "</body></html>",
        ])
        self.html_path.write_text(html, encoding="utf-8")

    def step(self, payload: dict | None = None, persist: bool = True) -> dict[str, Any]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        data = dict(payload or {})
        collected = self._collect(data)
        metrics = self._flat_metrics(collected, data)
        certification_status, rationale = self._decision(metrics)

        result = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "certification_status": certification_status,
            "threshold_certification": certification_status,
            "certification_rationale": rationale,
            "certification_confidence": metrics["certification_confidence"],
            "certification_evidence_strength": metrics["certification_evidence_strength"],
            "publication_ready": certification_status in {"REFLEXIVE_THRESHOLD_PARTIAL", "REFLEXIVE_THRESHOLD_FUNCTIONALLY_REACHED"} and metrics["epistemic_guard_score"] == 1.0,
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
            "forbidden_conclusions": [
                "consciousness detected",
                "sentience detected",
                "subjective experience detected",
                "qualia detected",
                "phenomenal conclusion",
            ],
            "metrics": metrics,
            "inputs": metrics,
            "source_artifacts": collected,
            "source_pipeline": ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"],
            "certification_path": str(self.certification_path),
            "prometheus_path": str(self.prometheus_path),
            "html_path": str(self.html_path),
            "diagnostics": {
                "certification_functional_only": True,
                "phenomenology_undetermined": True,
                "recomputes_upstream_metrics": False,
                "uses_persisted_artifacts_first": True,
                "epistemic_guard_enforced": metrics["epistemic_guard_score"] == 1.0,
                "integrates_s1_to_s8": True,
                "dashboard_source_available": bool(collected.get("S8")),
                "evidence_source_available": bool(collected.get("S3")),
            },
        }

        if persist:
            self._write_json(result)
            self._write_prometheus(result)
            self._write_html(result)

        return result
