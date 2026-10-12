
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
SUPERVISION_DIR = ROOT / "scientific_supervision"
DASHBOARD_DIR = SUPERVISION_DIR / "scientific_meta_dashboard"


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


def _mean(values: list[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    if not vals:
        return default
    return sum(vals) / len(vals)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


class ScientificMetaDashboard:
    """
    M10 — Scientific Meta Dashboard.

    This primitive visualizes the scientific meta-supervision chain M1→M9.
    It does not execute revisions and does not decide corrective actions.
    It consolidates the persisted or live state of evidence quality, bias,
    false-positive risk, statistical robustness, consistency, anomalies,
    self-revision pressure, trustworthiness, and execution performance.
    """

    primitive = "scientific_meta_dashboard"

    report_candidates = {
        "evidence_quality_assessment": [
            SUPERVISION_DIR / "evidence_quality_assessment_report.json",
            SUPERVISION_DIR / "latest_evidence_quality_assessment.json",
        ],
        "statistical_robustness_evaluator": [
            SUPERVISION_DIR / "statistical_robustness_evaluator_report.json",
            SUPERVISION_DIR / "latest_statistical_robustness_evaluator.json",
        ],
        "false_positive_detector": [
            SUPERVISION_DIR / "false_positive_detector_report.json",
            SUPERVISION_DIR / "latest_false_positive_detector.json",
        ],
        "bias_detection_engine": [
            SUPERVISION_DIR / "bias_detection_engine_report.json",
            SUPERVISION_DIR / "bias_report.json",
            SUPERVISION_DIR / "latest_bias_detection_engine.json",
        ],
        "scientific_consistency_validator": [
            SUPERVISION_DIR / "scientific_consistency_validator_report.json",
            SUPERVISION_DIR / "scientific_consistency_report.json",
            SUPERVISION_DIR / "latest_scientific_consistency_validator.json",
        ],
        "anomaly_in_evidence_detector": [
            SUPERVISION_DIR / "anomaly_in_evidence_detector_report.json",
            SUPERVISION_DIR / "anomaly_in_evidence_report.json",
            SUPERVISION_DIR / "latest_anomaly_in_evidence_detector.json",
        ],
        "self_revision_recommendation_engine": [
            SUPERVISION_DIR / "self_revision_recommendation_engine_report.json",
            SUPERVISION_DIR / "latest_self_revision_recommendation_engine.json",
        ],
        "scientific_self_revision_supervisor": [
            SUPERVISION_DIR / "scientific_self_revision_supervisor_report.json",
            SUPERVISION_DIR / "latest_scientific_self_revision_supervisor.json",
        ],
        "scientific_revision_execution_monitor": [
            SUPERVISION_DIR / "scientific_revision_execution_monitor_report.json",
            SUPERVISION_DIR / "latest_scientific_revision_execution_monitor.json",
        ],
    }

    def _load_reports(self) -> dict[str, dict[str, Any]]:
        reports: dict[str, dict[str, Any]] = {}
        for name, paths in self.report_candidates.items():
            for p in paths:
                data = _load_json(p)
                if data:
                    reports[name] = data
                    break
        return reports

    def _run_upstream(self) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        imports = [
            ("evidence_quality_assessment", "EvidenceQualityAssessment"),
            ("statistical_robustness_evaluator", "StatisticalRobustnessEvaluator"),
            ("false_positive_detector", "FalsePositiveDetector"),
            ("bias_detection_engine", "BiasDetectionEngine"),
            ("scientific_consistency_validator", "ScientificConsistencyValidator"),
            ("anomaly_in_evidence_detector", "AnomalyInEvidenceDetector"),
            ("self_revision_recommendation_engine", "SelfRevisionRecommendationEngine"),
            ("scientific_self_revision_supervisor", "ScientificSelfRevisionSupervisor"),
            ("scientific_revision_execution_monitor", "ScientificRevisionExecutionMonitor"),
        ]
        for module_name, class_name in imports:
            try:
                module = __import__(f"ontology.{module_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                obj = cls()
                try:
                    out = obj.step(persist=False)
                except TypeError:
                    out = obj.step()
                if isinstance(out, dict):
                    results[module_name] = out
            except Exception as exc:
                results[module_name] = {
                    "success": False,
                    "error": repr(exc),
                    "module": module_name,
                }
        return results

    def _extract_metrics(self, signals: dict[str, dict[str, Any]]) -> dict[str, float]:
        eqa = signals.get("evidence_quality_assessment", {})
        sre = signals.get("statistical_robustness_evaluator", {})
        fpd = signals.get("false_positive_detector", {})
        bde = signals.get("bias_detection_engine", {})
        scv = signals.get("scientific_consistency_validator", {})
        aed = signals.get("anomaly_in_evidence_detector", {})
        m7 = signals.get("self_revision_recommendation_engine", {})
        m8 = signals.get("scientific_self_revision_supervisor", {})
        m9 = signals.get("scientific_revision_execution_monitor", {})

        evidence_quality = _clamp(
            eqa.get("evidence_quality_score", eqa.get("evidence_quality", eqa.get("quality_score", 0.0)))
        )
        statistical_robustness = _clamp(
            sre.get("robustness_score", sre.get("statistical_robustness_score", 0.0))
        )
        false_positive_risk = _clamp(
            fpd.get("false_positive_risk_score", fpd.get("false_positive_probability", 0.0))
        )
        bias_risk = _clamp(
            bde.get("bias_risk_score", bde.get("bias_score", bde.get("bias_probability", 0.0)))
        )
        scientific_consistency = _clamp(
            scv.get("scientific_consistency_score", scv.get("consistency_score", 0.0))
        )
        anomaly_probability = _clamp(
            aed.get("anomaly_probability", aed.get("anomaly_signal_score", 0.0))
        )
        trustworthiness = _clamp(
            m8.get("scientific_trustworthiness_score", _mean([
                evidence_quality,
                statistical_robustness,
                1.0 - false_positive_risk,
                1.0 - bias_risk,
                scientific_consistency,
                1.0 - anomaly_probability,
            ]))
        )
        supervision_score = _clamp(
            m8.get("scientific_supervision_score", trustworthiness)
        )
        revision_priority = _clamp(m7.get("revision_priority", 0.0))
        revision_urgency = _clamp(m7.get("revision_urgency", 0.0))
        revision_execution_rate = _clamp(m9.get("revision_execution_rate", 0.0))
        revision_effectiveness = _clamp(m9.get("revision_effectiveness", 0.0))
        revision_success_rate = _clamp(m9.get("revision_success_rate", 0.0))

        scientific_meta_dashboard_score = _mean([
            evidence_quality,
            statistical_robustness,
            1.0 - false_positive_risk,
            1.0 - bias_risk,
            scientific_consistency,
            1.0 - anomaly_probability,
            trustworthiness,
            supervision_score,
            revision_execution_rate,
            revision_effectiveness,
            revision_success_rate,
        ])

        return {
            "evidence_quality": evidence_quality,
            "statistical_robustness": statistical_robustness,
            "false_positive_risk": false_positive_risk,
            "bias_risk": bias_risk,
            "scientific_consistency": scientific_consistency,
            "anomaly_probability": anomaly_probability,
            "scientific_trustworthiness_score": trustworthiness,
            "scientific_supervision_score": supervision_score,
            "revision_priority": revision_priority,
            "revision_urgency": revision_urgency,
            "revision_execution_rate": revision_execution_rate,
            "revision_effectiveness": revision_effectiveness,
            "revision_success_rate": revision_success_rate,
            "scientific_meta_dashboard_score": scientific_meta_dashboard_score,
        }

    def _decision(self, metrics: dict[str, float]) -> str:
        trust = metrics["scientific_trustworthiness_score"]
        anomaly = metrics["anomaly_probability"]
        bias = metrics["bias_risk"]
        false_positive = metrics["false_positive_risk"]
        revision_pressure = _mean([
            metrics["revision_priority"],
            metrics["revision_urgency"],
            anomaly,
            bias,
            false_positive,
        ])
        if trust < 0.45 or revision_pressure >= 0.70:
            return "scientific_meta_dashboard_alert"
        if trust < 0.70 or revision_pressure >= 0.40:
            return "scientific_meta_dashboard_watch"
        return "scientific_meta_dashboard_nominal"

    def _render_html(self, payload: dict[str, Any]) -> str:
        metrics = payload["metrics"]
        rows = []
        for k in sorted(metrics):
            rows.append(
                f"<tr><td>{escape(k)}</td><td>{metrics[k]:.6f}</td></tr>"
            )
        sources = "".join(
            f"<li>{escape(k)}: {escape(str(v.get('success', 'unknown')))}</li>"
            for k, v in sorted(payload["source_signal_summary"].items())
        )
        return "".join([
            "<!doctype html><html><head><meta charset='utf-8'>",
            "<title>Scientific Meta Dashboard</title>",
            "<style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}",
            "td,th{border:1px solid #ccc;padding:8px;text-align:left;}th{background:#f0f0f0;}",
            ".decision{font-weight:bold;font-size:1.2em;}</style></head><body>",
            "<h1>Open Cognitive Ecology — Scientific Meta Dashboard</h1>",
            f"<p>Generated at: {escape(payload['timestamp_utc'])}</p>",
            f"<p class='decision'>Decision: {escape(payload['scientific_meta_dashboard_decision'])}</p>",
            "<h2>Metrics</h2><table><tr><th>Metric</th><th>Value</th></tr>",
            "".join(rows),
            "</table><h2>Source modules</h2><ul>",
            sources,
            "</ul></body></html>",
        ])

    def _render_prometheus(self, payload: dict[str, Any]) -> str:
        lines = [
            "# HELP oce_scientific_meta_dashboard_metric Scientific meta-dashboard metric.",
            "# TYPE oce_scientific_meta_dashboard_metric gauge",
        ]
        for key, value in sorted(payload["metrics"].items()):
            safe = key.replace("-", "_").replace(" ", "_")
            lines.append(f'oce_scientific_meta_dashboard_metric{{metric="{safe}"}} {float(value):.6f}')
        return "\n".join(lines) + "\n"

    def _render_grafana(self, payload: dict[str, Any]) -> dict[str, Any]:
        panels = []
        for idx, key in enumerate(sorted(payload["metrics"].keys()), start=1):
            panels.append({
                "id": idx,
                "title": key,
                "type": "stat",
                "targets": [{
                    "expr": f'oce_scientific_meta_dashboard_metric{{metric="{key}"}}',
                    "legendFormat": key,
                }],
                "gridPos": {"h": 4, "w": 6, "x": ((idx - 1) % 4) * 6, "y": ((idx - 1) // 4) * 4},
            })
        return {
            "title": "Open Cognitive Ecology — Scientific Meta Dashboard",
            "schemaVersion": 39,
            "version": 1,
            "refresh": "30s",
            "panels": panels,
            "tags": ["open-cognitive-ecology", "scientific-supervision", "M10"],
        }

    def _write_exports(self, payload: dict[str, Any]) -> dict[str, str]:
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        json_path = DASHBOARD_DIR / "scientific_meta_dashboard.json"
        html_path = DASHBOARD_DIR / "scientific_meta_dashboard.html"
        prom_path = DASHBOARD_DIR / "scientific_meta_dashboard.prom"
        grafana_path = DASHBOARD_DIR / "scientific_meta_dashboard_grafana.json"
        latest_path = SUPERVISION_DIR / "latest_scientific_meta_dashboard.json"

        json_text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(json_text, encoding="utf-8")
        latest_path.write_text(json_text, encoding="utf-8")
        html_path.write_text(self._render_html(payload), encoding="utf-8")
        prom_path.write_text(self._render_prometheus(payload), encoding="utf-8")
        grafana_path.write_text(
            json.dumps(self._render_grafana(payload), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        history_path = SUPERVISION_DIR / "scientific_meta_dashboard_history.jsonl"
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json_text.replace("\n", " ") + "\n")

        return {
            "json_export_path": str(json_path),
            "html_export_path": str(html_path),
            "prometheus_export_path": str(prom_path),
            "grafana_export_path": str(grafana_path),
            "latest_report_path": str(latest_path),
            "history_path": str(history_path),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        use_upstream = bool(inputs.get("use_upstream", True))
        use_reports = bool(inputs.get("use_reports", True))

        signals: dict[str, dict[str, Any]] = {}
        if use_reports:
            signals.update(self._load_reports())
        if use_upstream:
            signals.update(self._run_upstream())

        for key in self.report_candidates:
            if isinstance(inputs.get(key), dict):
                signals[key] = inputs[key]

        metrics = self._extract_metrics(signals)
        decision = self._decision(metrics)
        timestamp = datetime.now(timezone.utc).isoformat()
        source_signal_summary = {
            key: {
                "success": value.get("success"),
                "primitive": value.get("primitive"),
                "decision": value.get("scientific_self_revision_decision")
                or value.get("scientific_revision_execution_decision")
                or value.get("scientific_revision_decision")
                or value.get("robustness_decision")
                or value.get("anomaly_decision")
                or value.get("bias_decision")
                or value.get("consistency_decision")
                or value.get("evidence_decision"),
            }
            for key, value in sorted(signals.items())
        }

        payload: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": timestamp,
            "metrics": metrics,
            "evidence_quality": metrics["evidence_quality"],
            "statistical_robustness": metrics["statistical_robustness"],
            "false_positive_risk": metrics["false_positive_risk"],
            "bias_risk": metrics["bias_risk"],
            "scientific_consistency": metrics["scientific_consistency"],
            "anomaly_probability": metrics["anomaly_probability"],
            "scientific_trustworthiness_score": metrics["scientific_trustworthiness_score"],
            "scientific_supervision_score": metrics["scientific_supervision_score"],
            "revision_execution_rate": metrics["revision_execution_rate"],
            "revision_effectiveness": metrics["revision_effectiveness"],
            "revision_success_rate": metrics["revision_success_rate"],
            "scientific_meta_dashboard_score": metrics["scientific_meta_dashboard_score"],
            "scientific_meta_dashboard_decision": decision,
            "source_signal_summary": source_signal_summary,
            "exports": {},
        }

        if persist:
            paths = self._write_exports(payload)
            payload["exports"] = paths
            payload.update(paths)
        return payload
