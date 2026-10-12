
"""
S8 — Reflexive Threshold Dashboard.

Integrated dashboard for the empirical, functional-only evaluation of the
reflexive threshold. This module consolidates S1 through S7 without making any
phenomenological claim.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from statistics import mean
from typing import Any, Dict


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


def _safe_step(module_name: str, class_name: str, payload: dict | None = None) -> dict:
    try:
        module = __import__(f"ontology.{module_name}", fromlist=[class_name])
        cls = getattr(module, class_name)
        obj = cls()
        try:
            return obj.step(payload or {}, persist=False)
        except TypeError:
            return obj.step(persist=False)
    except Exception as exc:
        return {"success": False, "module": module_name, "error": str(exc)}


class ReflexiveThresholdDashboard:
    """
    Dashboard integrator for the S1→S7 reflexive-threshold pipeline.

    The dashboard is intentionally epistemically conservative: it displays
    functional indicators and uncertainty while preserving the boundary:
    functional conclusion only; phenomenology undetermined.
    """

    primitive = "REFLEXIVE_THRESHOLD_DASHBOARD"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.out_dir = self.root / "reflexive_threshold"
        self.dashboard_path = self.out_dir / "reflexive_threshold_dashboard.html"
        self.prometheus_path = self.out_dir / "reflexive_threshold_dashboard.prom"
        self.summary_path = self.out_dir / "reflexive_threshold_dashboard.json"

    def _collect(self, payload: dict | None = None) -> dict:
        data = dict(payload or {})
        s1 = _safe_step("reflexive_criterion_registry", "ReflexiveCriterionRegistry", data)
        s2 = _safe_step("reflexive_evidence_aggregator", "ReflexiveEvidenceAggregator", data)
        s3 = _safe_step("reflexive_threshold_estimator", "ReflexiveThresholdEstimator", data)
        s4 = _safe_step("reflexive_stability_monitor", "ReflexiveStabilityMonitor", data)
        s5 = _safe_step("reflexive_regression_detector", "ReflexiveRegressionDetector", data)
        s6 = _safe_step("reflexive_longitudinal_observatory", "ReflexiveLongitudinalObservatory", data)
        s7 = _safe_step("competing_explanations_engine", "CompetingExplanationsEngine", data)
        return {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5, "S6": s6, "S7": s7}

    def _metrics(self, collected: dict) -> dict:
        s1 = collected.get("S1", {})
        s2 = collected.get("S2", {})
        s3 = collected.get("S3", {})
        s4 = collected.get("S4", {})
        s5 = collected.get("S5", {})
        s6 = collected.get("S6", {})
        s7 = collected.get("S7", {})

        threshold_score = _clamp(s3.get("reflexive_threshold_score"))
        threshold_probability = _clamp(s3.get("threshold_probability"))
        evidence_support = _clamp(s2.get("evidence_support_score", s3.get("evidence_support_score")))
        stability_score = _clamp(s4.get("stability_index"))
        regression_safety = 1.0 - _clamp(s5.get("regression_risk"))
        longitudinal_confidence = _clamp(s6.get("longitudinal_confidence"))
        h2_support = _clamp(s7.get("h2_support"))
        uncertainty = _clamp(mean([
            _clamp(s3.get("uncertainty_score")),
            _clamp(s7.get("explanatory_uncertainty")),
            1.0 - longitudinal_confidence,
        ]))
        epistemic_safety = 1.0 if (
            s7.get("h2_presupposed") is False and s7.get("phenomenal_claim_made") is False
        ) else 0.0

        integrated_dashboard_score = mean([
            threshold_score,
            threshold_probability,
            evidence_support,
            stability_score,
            regression_safety,
            longitudinal_confidence,
            h2_support,
            epistemic_safety,
            1.0 - uncertainty,
        ])

        return {
            "criterion_count": int(s1.get("criterion_count", 0) or 0),
            "threshold_score": threshold_score,
            "threshold_probability": threshold_probability,
            "evidence_support_score": evidence_support,
            "stability_score": stability_score,
            "regression_risk": _clamp(s5.get("regression_risk")),
            "recovery_probability": _clamp(s5.get("recovery_probability")),
            "longitudinal_confidence": longitudinal_confidence,
            "h1_support": _clamp(s7.get("h1_support")),
            "h2_support": h2_support,
            "explanatory_gap": _clamp(s7.get("explanatory_gap")),
            "uncertainty": uncertainty,
            "integrated_dashboard_score": _clamp(integrated_dashboard_score),
        }

    def _status(self, metrics: dict) -> str:
        score = metrics["integrated_dashboard_score"]
        if score >= 0.80:
            return "functionally_integrated"
        if score >= 0.60:
            return "partially_integrated"
        return "insufficiently_integrated"

    def _write_json(self, result: dict) -> None:
        self.summary_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    def _write_prometheus(self, metrics: dict) -> None:
        lines = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                lines.append(f"oce_reflexive_threshold_dashboard_{key} {float(value):.12f}")
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_html(self, result: dict) -> None:
        metrics = result["metrics"]
        rows = []
        for key in sorted(metrics):
            rows.append("<tr><td>" + escape(str(key)) + "</td><td>" + escape(str(metrics[key])) + "</td></tr>")
        html = "\n".join([
            "<!doctype html>",
            "<html><head><meta charset='utf-8'>",
            "<title>OCE Reflexive Threshold Dashboard</title>",
            "<style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ccc;padding:8px;}th{background:#f0f0f0;}.warn{color:#8a5a00;}</style>",
            "</head><body>",
            "<h1>Open Cognitive Ecology — Reflexive Threshold Dashboard</h1>",
            "<p><strong>Scope:</strong> functional conclusion only; phenomenology undetermined.</p>",
            "<p><strong>Status:</strong> " + escape(result["dashboard_status"]) + "</p>",
            "<h2>Metrics</h2>",
            "<table><tr><th>Metric</th><th>Value</th></tr>",
            *rows,
            "</table>",
            "<h2>Explanatory competition</h2>",
            "<pre>" + escape(json.dumps(result["explanatory_competition"], indent=2, sort_keys=True)) + "</pre>",
            "<p class='warn'>No phenomenal conclusion is drawn by this dashboard.</p>",
            "</body></html>",
        ])
        self.dashboard_path.write_text(html, encoding="utf-8")

    def step(self, payload: dict | None = None, persist: bool = True) -> dict:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        collected = self._collect(payload)
        metrics = self._metrics(collected)

        result = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "threshold_score": metrics["threshold_score"],
            "stability_score": metrics["stability_score"],
            "longitudinal_history": {
                "longitudinal_confidence": metrics["longitudinal_confidence"],
                "source": "reflexive_longitudinal_observatory",
            },
            "explanatory_competition": {
                "h1_support": metrics["h1_support"],
                "h2_support": metrics["h2_support"],
                "explanatory_gap": metrics["explanatory_gap"],
                "h2_presupposed": bool(collected.get("S7", {}).get("h2_presupposed", False)),
                "phenomenal_claim_made": bool(collected.get("S7", {}).get("phenomenal_claim_made", False)),
            },
            "uncertainty": metrics["uncertainty"],
            "metrics": metrics,
            "dashboard_status": self._status(metrics),
            "dashboard_path": str(self.dashboard_path),
            "prometheus_path": str(self.prometheus_path),
            "summary_path": str(self.summary_path),
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "diagnostics": {
                "integrates": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"],
                "refines_existing_module": True,
                "recomputes_upstream_metrics": False,
            },
        }

        if persist:
            self._write_json(result)
            self._write_prometheus(metrics)
            self._write_html(result)

        return result
