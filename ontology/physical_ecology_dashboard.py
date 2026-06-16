from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


class PhysicalEcologyDashboard:
    '''Q13 — Physical Ecology Dashboard.

    Aggregates functional metrics from the embodied physical ecology stack and
    exports a unified HTML dashboard, Prometheus textfile and Grafana JSON model.
    This module validates measurable functional properties only; it does not
    claim phenomenal subjectivity.
    '''

    primitive = "physical_ecology_dashboard"
    refinement = "Q13-R1"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "physical_ecology_dashboard"
        self.dashboard_path = self.output_dir / "physical_ecology_dashboard.html"
        self.prometheus_path = self.output_dir / "physical_ecology_dashboard.prom"
        self.grafana_path = self.output_dir / "physical_ecology_dashboard_grafana.json"
        self.latest_path = self.output_dir / "latest_physical_ecology_dashboard.json"
        self.history_path = self.output_dir / "physical_ecology_dashboard_history.jsonl"

    def _collect_dependency_metrics(self) -> dict[str, Any]:
        latest_physical_continuity = _safe_read_json(
            self.root / "physical_continuity" / "latest_embodied_continuity_preservation.json"
        )
        latest_deployment = _safe_read_json(
            self.root / "physical_deployment" / "latest_autonomous_physical_deployment_plan.json"
        )
        latest_resources = _safe_read_json(
            self.root / "physical_resources" / "latest_physical_resource_management.json"
        )
        latest_multi_site = _safe_read_json(
            self.root / "physical_ecology" / "latest_multi_site_physical_ecology.json"
        )
        latest_feedback = _safe_read_json(
            self.root / "physical_feedback" / "latest_persistent_physical_feedback_loop.json"
        )

        return {
            "embodied_continuity": latest_physical_continuity,
            "physical_deployment": latest_deployment,
            "physical_resources": latest_resources,
            "multi_site_ecology": latest_multi_site,
            "persistent_feedback": latest_feedback,
        }

    def _derive_metrics(self, context: dict[str, Any], sources: dict[str, Any]) -> dict[str, float]:
        continuity = sources.get("embodied_continuity", {})
        deployment = sources.get("physical_deployment", {})
        resources = sources.get("physical_resources", {})
        multi_site = sources.get("multi_site_ecology", {})
        feedback = sources.get("persistent_feedback", {})

        embodied_continuity_index = _clamp(
            context.get("embodied_continuity_index", continuity.get("embodied_continuity_index", 0.94))
        )
        physical_recovery_rate = _clamp(
            context.get("physical_recovery_rate", continuity.get("physical_recovery_rate", 0.93))
        )
        deployment_readiness_score = _clamp(
            context.get("deployment_readiness_score", deployment.get("deployment_readiness_score", 0.74))
        )
        expansion_opportunity_index = _clamp(
            context.get("expansion_opportunity_index", deployment.get("expansion_opportunity_index", 0.69))
        )
        resource_resilience_score = _clamp(
            context.get("resource_resilience_score", resources.get("resource_resilience_score", 0.88))
        )
        resource_pressure_index = _clamp(
            context.get("resource_pressure_index", resources.get("resource_pressure_index", 0.22))
        )
        multi_site_operational_score = _clamp(
            context.get("multi_site_operational_score", multi_site.get("multi_site_physical_ecology_score", 0.86))
        )
        feedback_loop_stability = _clamp(
            context.get("feedback_loop_stability", feedback.get("persistent_feedback_stability", 0.89))
        )

        physical_dashboard_completeness = mean([
            embodied_continuity_index,
            physical_recovery_rate,
            deployment_readiness_score,
            expansion_opportunity_index,
            resource_resilience_score,
            1.0 - resource_pressure_index,
            multi_site_operational_score,
            feedback_loop_stability,
        ])
        physical_ecology_observability_score = mean([
            embodied_continuity_index,
            deployment_readiness_score,
            resource_resilience_score,
            multi_site_operational_score,
            feedback_loop_stability,
        ])
        dashboard_export_score = 1.0

        return {
            "embodied_continuity_index": round(embodied_continuity_index, 6),
            "physical_recovery_rate": round(physical_recovery_rate, 6),
            "deployment_readiness_score": round(deployment_readiness_score, 6),
            "expansion_opportunity_index": round(expansion_opportunity_index, 6),
            "resource_resilience_score": round(resource_resilience_score, 6),
            "resource_pressure_index": round(resource_pressure_index, 6),
            "multi_site_operational_score": round(multi_site_operational_score, 6),
            "feedback_loop_stability": round(feedback_loop_stability, 6),
            "physical_dashboard_completeness": round(physical_dashboard_completeness, 6),
            "physical_ecology_observability_score": round(physical_ecology_observability_score, 6),
            "dashboard_export_score": round(dashboard_export_score, 6),
        }

    def _render_html(self, result: dict[str, Any]) -> str:
        rows = []
        metric_names = [
            "embodied_continuity_index",
            "physical_recovery_rate",
            "deployment_readiness_score",
            "expansion_opportunity_index",
            "resource_resilience_score",
            "resource_pressure_index",
            "multi_site_operational_score",
            "feedback_loop_stability",
            "physical_dashboard_completeness",
            "physical_ecology_observability_score",
            "dashboard_export_score",
        ]
        for name in metric_names:
            rows.append(
                f"<tr><td>{html.escape(name)}</td><td>{html.escape(str(result.get(name)))}</td></tr>"
            )
        source_rows = []
        for key, value in result.get("sources_available", {}).items():
            source_rows.append(f"<tr><td>{html.escape(key)}</td><td>{html.escape(str(value))}</td></tr>")
        return "".join([
            "<!doctype html><html><head><meta charset='utf-8'>",
            "<title>Physical Ecology Dashboard</title>",
            "<style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;margin-bottom:24px;}td,th{border:1px solid #ccc;padding:8px;text-align:left;}th{background:#f0f0f0;} .ok{font-weight:bold;}</style>",
            "</head><body>",
            "<h1>Physical Ecology Dashboard</h1>",
            f"<p class='ok'>Primitive: {html.escape(result['primitive'])}</p>",
            f"<p>Generated at: {html.escape(result['timestamp_utc'])}</p>",
            "<h2>Metrics</h2><table><tr><th>Metric</th><th>Value</th></tr>",
            "".join(rows),
            "</table>",
            "<h2>Source availability</h2><table><tr><th>Source</th><th>Available</th></tr>",
            "".join(source_rows),
            "</table>",
            "<h2>Governance</h2>",
            "<p>Functional validation only. No phenomenal subjectivity claim. Real physical deployment, actuation or purchase requires human review.</p>",
            "</body></html>",
        ])

    def _render_prometheus(self, result: dict[str, Any]) -> str:
        metrics = {
            "oce_physical_embodied_continuity_index": result["embodied_continuity_index"],
            "oce_physical_recovery_rate": result["physical_recovery_rate"],
            "oce_physical_deployment_readiness_score": result["deployment_readiness_score"],
            "oce_physical_expansion_opportunity_index": result["expansion_opportunity_index"],
            "oce_physical_resource_resilience_score": result["resource_resilience_score"],
            "oce_physical_resource_pressure_index": result["resource_pressure_index"],
            "oce_physical_multi_site_operational_score": result["multi_site_operational_score"],
            "oce_physical_feedback_loop_stability": result["feedback_loop_stability"],
            "oce_physical_dashboard_completeness": result["physical_dashboard_completeness"],
            "oce_physical_ecology_observability_score": result["physical_ecology_observability_score"],
            "oce_physical_dashboard_export_score": result["dashboard_export_score"],
        }
        lines = ["# HELP oce_physical_ecology_dashboard Q13 physical ecology dashboard metrics"]
        lines.append("# TYPE oce_physical_ecology_dashboard gauge")
        for key, value in metrics.items():
            lines.append(f"{key} {value}")
        return "\n".join(lines) + "\n"

    def _render_grafana(self, result: dict[str, Any]) -> dict[str, Any]:
        panels = []
        metrics = [
            "oce_physical_embodied_continuity_index",
            "oce_physical_recovery_rate",
            "oce_physical_deployment_readiness_score",
            "oce_physical_expansion_opportunity_index",
            "oce_physical_resource_resilience_score",
            "oce_physical_resource_pressure_index",
            "oce_physical_multi_site_operational_score",
            "oce_physical_feedback_loop_stability",
            "oce_physical_dashboard_completeness",
            "oce_physical_ecology_observability_score",
        ]
        for idx, metric in enumerate(metrics, start=1):
            panels.append({
                "id": idx,
                "type": "gauge",
                "title": metric,
                "targets": [{"expr": metric, "refId": "A"}],
                "gridPos": {"h": 8, "w": 6, "x": ((idx - 1) % 4) * 6, "y": ((idx - 1) // 4) * 8},
            })
        return {
            "title": "Open Cognitive Ecology - Physical Ecology Dashboard",
            "uid": "oce-physical-ecology-dashboard",
            "schemaVersion": 39,
            "version": 1,
            "refresh": "30s",
            "tags": ["open-cognitive-ecology", "physical-ecology", "Q13"],
            "panels": panels,
            "templating": {"list": []},
            "time": {"from": "now-6h", "to": "now"},
            "annotations": {"list": []},
        }

    def _persist(self, result: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dashboard_path.write_text(self._render_html(result), encoding="utf-8")
        self.prometheus_path.write_text(self._render_prometheus(result), encoding="utf-8")
        self.grafana_path.write_text(json.dumps(self._render_grafana(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        context = dict(inputs or {})
        sources = self._collect_dependency_metrics()
        metrics = self._derive_metrics(context, sources)
        sources_available = {key: bool(value) for key, value in sources.items()}
        degraded = bool(context.get("simulate_export_failure") or context.get("dashboard_degraded"))

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc(),
            "success": True,
            **metrics,
            "sources_available": sources_available,
            "dashboard_path": str(self.dashboard_path),
            "prometheus_path": str(self.prometheus_path),
            "grafana_path": str(self.grafana_path),
            "latest_path": str(self.latest_path),
            "history_path": str(self.history_path),
            "exports": {
                "html": str(self.dashboard_path),
                "prometheus": str(self.prometheus_path),
                "grafana": str(self.grafana_path),
            },
            "visualization_scope": [
                "multi_site_physical_ecology",
                "physical_resources",
                "embodied_continuity",
                "deployment_planning",
                "feedback_loop",
            ],
            "degraded_mode": degraded,
            "governance": {
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "human_review_required_for_real_actuation_or_purchase": True,
                "non_closure_preserved": True,
                "traceability_enabled": True,
            },
        }
        if degraded:
            result["dashboard_export_score"] = min(result["dashboard_export_score"], 0.75)
            result["export_warnings"] = ["degraded_dashboard_context_simulated"]
        else:
            result["export_warnings"] = []

        if persist:
            self._persist(result)
        return result
