"""
Open Cognitive Ecology — E8 Grafana Dashboard Exporter

Generate a Grafana-compatible dashboard JSON definition from the validated
Prometheus metrics exported by E7.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


PRIMITIVE = "grafana_dashboard_exporter"

DEPENDENCIES = [
    "prometheus_metrics_exporter",
    "metrics_html_report_generator",
    "metrics_anomaly_detection_engine",
    "metrics_statistical_significance_engine",
    "metrics_aggregation_engine",
    "civilizational_web_dashboard",
    "web_dashboard_exporter",
    "constitutional_dashboard_integration",
]


class GrafanaDashboardExporter:
    def __init__(self, root: Optional[Path] = None):
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.grafana_dir = self.root / "grafana"
        self.metrics_dir = self.root / "metrics"
        self.prometheus_path = self.metrics_dir / "prometheus" / "open_cognitive_ecology.prom"
        self.dashboard_path = self.grafana_dir / "open_cognitive_ecology_dashboard.json"
        self.state_path = self.metrics_dir / "grafana_dashboard_exporter_state.json"

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _read_prometheus_metric_names(self) -> List[str]:
        if not self.prometheus_path.exists():
            return []
        names = []
        for raw in self.prometheus_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            name = line.split()[0]
            if "{" in name:
                name = name.split("{", 1)[0]
            if name and name not in names:
                names.append(name)
        return names

    def _panel(self, panel_id: int, title: str, expr: str, x: int, y: int,
               w: int = 12, h: int = 7, panel_type: str = "timeseries",
               unit: str = "short", description: str = "") -> Dict[str, Any]:
        return {
            "id": panel_id,
            "type": panel_type,
            "title": title,
            "description": description,
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "fieldConfig": {
                "defaults": {
                    "unit": unit,
                    "custom": {
                        "drawStyle": "line",
                        "lineInterpolation": "linear",
                        "barAlignment": 0,
                        "lineWidth": 1,
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "spanNulls": True,
                        "showPoints": "auto",
                        "pointSize": 5
                    },
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "orange", "value": 0.7},
                            {"color": "red", "value": 0.9}
                        ]
                    }
                },
                "overrides": []
            },
            "options": {
                "legend": {"displayMode": "list", "placement": "bottom", "calcs": ["lastNotNull"]},
                "tooltip": {"mode": "single", "sort": "none"}
            },
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "${DS_PROMETHEUS}"},
                    "editorMode": "code",
                    "expr": expr,
                    "legendFormat": title,
                    "range": True,
                    "refId": "A"
                }
            ]
        }

    def _stat_panel(self, panel_id: int, title: str, expr: str, x: int, y: int,
                    w: int = 6, h: int = 5, unit: str = "short",
                    description: str = "") -> Dict[str, Any]:
        p = self._panel(panel_id, title, expr, x, y, w, h, "stat", unit, description)
        p["options"] = {
            "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
            "orientation": "auto",
            "textMode": "auto",
            "colorMode": "value",
            "graphMode": "area",
            "justifyMode": "auto"
        }
        return p

    def _dashboard(self, metric_names: List[str]) -> Dict[str, Any]:
        panels = [
            self._stat_panel(1, "Pipeline: Aggregation", "oce_metrics_pipeline_aggregation_success", 0, 0, unit="bool"),
            self._stat_panel(2, "Pipeline: Statistics", "oce_metrics_pipeline_statistical_analysis_success", 6, 0, unit="bool"),
            self._stat_panel(3, "Pipeline: Anomalies", "oce_metrics_pipeline_anomaly_detection_success", 12, 0, unit="bool"),
            self._stat_panel(4, "Pipeline: HTML Reports", "oce_metrics_pipeline_html_report_generated", 18, 0, unit="bool"),
            self._panel(5, "Runtime Stability", "oce_metrics_global_stability_index", 0, 5, unit="percentunit"),
            self._panel(6, "Conversational Initiative", "oce_conversational_initiative_index", 12, 5, unit="percentunit"),
            self._panel(7, "Noise Ratio", "oce_noise_ratio", 0, 12, unit="percentunit"),
            self._panel(8, "Conversation Continuity", "oce_conversation_continuity_score", 12, 12, unit="percentunit"),
            self._panel(9, "Error Count", "oce_error_count", 0, 19, unit="short"),
            self._panel(10, "Runtime Cycle Count", "oce_runtime_cycle_count", 12, 19, unit="short"),
            self._panel(11, "Beneficial Mutation Ratio", "oce_beneficial_mutation_ratio", 0, 26, unit="percentunit"),
            self._panel(12, "Civilizational Autonomy", "oce_civilizational_autonomy_score", 12, 26, unit="percentunit"),
            self._panel(13, "Anomaly Score", "oce_metrics_anomaly_score", 0, 33, unit="percentunit"),
            self._panel(14, "Critical + High Anomalies", "oce_metrics_critical_anomaly_count + oce_metrics_high_anomaly_count", 12, 33, unit="short"),
            self._panel(15, "Statistical Support Ratio", "oce_metrics_statistical_support_ratio", 0, 40, unit="percentunit"),
            self._panel(16, "Significant Metrics", "oce_metrics_significant_metric_count", 12, 40, unit="short"),
            self._panel(17, "Spontaneous Message Success", "oce_spontaneous_message_success_rate", 0, 47, unit="percentunit"),
            self._panel(18, "Spontaneous Message Count", "oce_spontaneous_message_count", 12, 47, unit="short"),
        ]

        required_metrics = [
            "oce_metrics_pipeline_aggregation_success",
            "oce_metrics_pipeline_statistical_analysis_success",
            "oce_metrics_pipeline_anomaly_detection_success",
            "oce_metrics_pipeline_html_report_generated",
            "oce_metrics_global_stability_index",
            "oce_conversational_initiative_index",
            "oce_noise_ratio",
            "oce_conversation_continuity_score",
            "oce_error_count",
            "oce_runtime_cycle_count",
            "oce_beneficial_mutation_ratio",
            "oce_civilizational_autonomy_score",
            "oce_metrics_anomaly_score",
            "oce_metrics_statistical_support_ratio",
            "oce_spontaneous_message_success_rate",
            "oce_spontaneous_message_count",
        ]
        missing = [m for m in required_metrics if m not in metric_names]

        return {
            "annotations": {"list": []},
            "editable": True,
            "graphTooltip": 0,
            "id": None,
            "links": [],
            "panels": panels,
            "refresh": "30s",
            "schemaVersion": 39,
            "style": "dark",
            "tags": ["open-cognitive-ecology", "metrics", "prometheus"],
            "templating": {
                "list": [
                    {
                        "name": "DS_PROMETHEUS",
                        "type": "datasource",
                        "query": "prometheus",
                        "current": {},
                        "hide": 0,
                        "label": "Prometheus datasource"
                    }
                ]
            },
            "time": {"from": "now-24h", "to": "now"},
            "timezone": "browser",
            "title": "Open Cognitive Ecology — Metrics Pipeline",
            "uid": "open-cognitive-ecology-metrics",
            "version": 1,
            "__inputs": [
                {
                    "name": "DS_PROMETHEUS",
                    "label": "Prometheus",
                    "description": "Prometheus datasource for Open Cognitive Ecology metrics.",
                    "type": "datasource",
                    "pluginId": "prometheus",
                    "pluginName": "Prometheus"
                }
            ],
            "__requires": [
                {"type": "grafana", "id": "grafana", "name": "Grafana", "version": "9.0.0"},
                {"type": "datasource", "id": "prometheus", "name": "Prometheus", "version": "1.0.0"},
                {"type": "panel", "id": "timeseries", "name": "Time series", "version": ""},
                {"type": "panel", "id": "stat", "name": "Stat", "version": ""}
            ],
            "oce_metadata": {
                "generated_by": PRIMITIVE,
                "generated_at": self._utc_now(),
                "source_prometheus_path": str(self.prometheus_path),
                "required_metric_count": len(required_metrics),
                "missing_required_metrics": missing,
                "panel_count": len(panels)
            }
        }

    def step(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.grafana_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        metric_names = self._read_prometheus_metric_names()
        dashboard = self._dashboard(metric_names)
        self.dashboard_path.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False), encoding="utf-8")
        missing = dashboard["oce_metadata"]["missing_required_metrics"]
        result = {
            "primitive": PRIMITIVE,
            "phase": "E8_GRAFANA_DASHBOARD_EXPORTER",
            "grafana_dashboard_exporter_operational": True,
            "grafana_dashboard_ready": self.dashboard_path.exists(),
            "dashboard_generated": self.dashboard_path.exists(),
            "dashboard_path": str(self.dashboard_path),
            "panel_count": len(dashboard.get("panels", [])),
            "prometheus_metric_count": len(metric_names),
            "missing_required_metrics": missing,
            "required_metrics_present": len(missing) == 0,
            "datasource_variable": "DS_PROMETHEUS",
            "diagnostics": {
                "consumes_e7_prometheus_export": True,
                "does_not_replace_html_dashboards": True,
                "does_not_launch_grafana": True,
                "importable_dashboard_json": True,
                "stdlib_only": True
            },
            "state_path": str(self.state_path),
            "next_step": "E9_runtime_metrics_hook",
            "error_count": 0 if self.dashboard_path.exists() else 1,
            "timestamp": self._utc_now()
        }
        self.state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result


ENGINE = GrafanaDashboardExporter()


def step(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return ENGINE.step(payload)


if __name__ == "__main__":
    print(json.dumps(GrafanaDashboardExporter().step(), indent=2, ensure_ascii=False))
