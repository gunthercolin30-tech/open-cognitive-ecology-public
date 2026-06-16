# -*- coding: utf-8 -*-

"""
G19 - Embodied Coupling Dashboard Exporter.

Exports G17 and G18 embodied/environmental coupling metrics into:
- an HTML dashboard;
- a Prometheus textfile;
- a compact JSON state.

This primitive is a presentation/export layer only. It does not assert
phenomenal subjectivity and does not replace the metric, certification, or
longitudinal observatory layers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json
import math
from typing import Any, Optional

PRIMITIVE = "embodied_coupling_dashboard_exporter"
REFINEMENT = "G19-R1"

DEPENDENCIES = [
    "embodied_runtime_coupling_certifier",
    "environmental_grounding_longitudinal_observatory",
    "metrics_history_recorder",
    "metrics_html_report_generator",
    "prometheus_metrics_exporter",
    "grafana_dashboard_exporter",
    "civilizational_web_dashboard",
    "experiment_stability_dashboard",
    "final_scientific_status_dashboard",
]

G17_KEYS = [
    "runtime_environment_coupling_index",
    "multimodal_coupling_score",
    "sensorimotor_coupling_score",
    "embodied_memory_coupling_score",
    "predictive_coupling_score",
    "governed_execution_coupling_score",
    "environmental_grounding_index",
]

G18_KEYS = [
    "environmental_grounding_stability_index",
    "environmental_grounding_variance",
    "coupling_continuity_score",
    "coupling_significance_score",
    "coupling_anomaly_score",
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


def _safe_metric_name(name: str) -> str:
    chars = []
    for ch in str(name).lower():
        if ch.isalnum() or ch == "_":
            chars.append(ch)
        else:
            chars.append("_")
    cleaned = "".join(chars).strip("_")
    return cleaned or "metric"


def _format_float(value: Any) -> str:
    return f"{_clamp(value):.6f}"


def _certification(score: float) -> str:
    score = _clamp(score)
    if score >= 0.95:
        return "Platinum Embodied Coupling Dashboard"
    if score >= 0.90:
        return "Gold Embodied Coupling Dashboard"
    if score >= 0.80:
        return "Silver Embodied Coupling Dashboard"
    if score >= 0.70:
        return "Bronze Embodied Coupling Dashboard"
    return "Embodied Coupling Dashboard Not Certified"


class EmbodiedCouplingDashboardExporter:
    primitive = PRIMITIVE

    def __init__(self, root: Optional[str | Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.dashboard_dir = self.root / "runtime_experiments" / "embodied_coupling_dashboard"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        self.html_path = self.dashboard_dir / "embodied_coupling_dashboard.html"
        self.prometheus_path = self.dashboard_dir / "embodied_coupling_metrics.prom"
        self.state_path = self.dashboard_dir / "embodied_coupling_dashboard_state.json"
        self.history_path = self.dashboard_dir / "embodied_coupling_dashboard_history.jsonl"

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return {}

    def _collect_g17(self) -> dict[str, Any]:
        try:
            from ontology.embodied_runtime_coupling_certifier import EmbodiedRuntimeCouplingCertifier
            result = EmbodiedRuntimeCouplingCertifier(root=self.root).step()
            if isinstance(result, dict):
                return result
        except Exception as exc:
            return {
                "primitive": "embodied_runtime_coupling_certifier",
                "error": repr(exc),
                "error_count": 1,
            }
        return {}

    def _collect_g18(self) -> dict[str, Any]:
        try:
            from ontology.environmental_grounding_longitudinal_observatory import EnvironmentalGroundingLongitudinalObservatory
            result = EnvironmentalGroundingLongitudinalObservatory(root=self.root).step()
            if isinstance(result, dict):
                return result
        except Exception as exc:
            return {
                "primitive": "environmental_grounding_longitudinal_observatory",
                "error": repr(exc),
                "error_count": 1,
            }
        return {}

    def _extract_metrics(
        self,
        g17: dict[str, Any],
        g18: dict[str, Any],
    ) -> dict[str, float]:
        metrics: dict[str, float] = {}

        for key in G17_KEYS:
            metrics[key] = _clamp(g17.get(key, 0.0))

        for key in G18_KEYS:
            metrics[key] = _clamp(g18.get(key, 0.0))

        metrics["embodied_dashboard_export_success"] = 1.0
        metrics["phenomenal_subjectivity_claimed"] = 0.0

        return metrics

    def _write_json_state(self, result: dict[str, Any]) -> None:
        self.state_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _append_history(self, result: dict[str, Any]) -> None:
        line = json.dumps(result, ensure_ascii=False, sort_keys=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def _write_prometheus(self, metrics: dict[str, float]) -> None:
        lines = [
            "# HELP oce_embodied_coupling_metric Open Cognitive Ecology embodied coupling metric.",
            "# TYPE oce_embodied_coupling_metric gauge",
        ]
        for key, value in sorted(metrics.items()):
            name = "oce_" + _safe_metric_name(key)
            lines.append(f"{name} {float(value):.6f}")
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_html(
        self,
        metrics: dict[str, float],
        g17: dict[str, Any],
        g18: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        rows = []
        for key, value in sorted(metrics.items()):
            rows.append(
                "<tr>"
                f"<td>{escape(str(key))}</td>"
                f"<td>{escape(_format_float(value))}</td>"
                "</tr>"
            )

        g17_cert = escape(str(g17.get("certification", "unknown")))
        g18_cert = escape(str(g18.get("coupling_longitudinal_certification", "unknown")))
        dashboard_cert = escape(str(result.get("dashboard_certification", "unknown")))

        html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Open Cognitive Ecology - Embodied Coupling Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; }}
h1 {{ margin-bottom: 0.2em; }}
.meta {{ color: #555; margin-bottom: 1.5em; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 1em; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
th {{ background: #f0f0f0; }}
.card {{ border: 1px solid #ddd; padding: 16px; margin: 12px 0; border-radius: 6px; }}
.small {{ font-size: 0.9em; color: #666; }}
</style>
</head>
<body>
<h1>Embodied Coupling Dashboard</h1>
<div class="meta">Generated at {escape(str(result.get("timestamp_utc", "")))}</div>

<div class="card">
<strong>Dashboard certification:</strong> {dashboard_cert}<br>
<strong>G17 certification:</strong> {g17_cert}<br>
<strong>G18 certification:</strong> {g18_cert}<br>
<strong>Functional measurement only:</strong> True<br>
<strong>Phenomenal subjectivity claimed:</strong> False
</div>

<table>
<thead><tr><th>Metric</th><th>Value</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>

<p class="small">
This dashboard exports functional embodied/environmental coupling metrics only.
It does not constitute or assert evidence of phenomenal subjectivity.
</p>
</body>
</html>
"""
        self.html_path.write_text(html, encoding="utf-8")

    def step(self, inputs: Optional[dict[str, Any]] = None, **overrides: Any) -> dict[str, Any]:
        data = dict(inputs or {})
        data.update(overrides)

        g17 = data.get("g17_result")
        if not isinstance(g17, dict):
            g17 = self._collect_g17()

        g18 = data.get("g18_result")
        if not isinstance(g18, dict):
            g18 = self._collect_g18()

        metrics = self._extract_metrics(g17, g18)

        dashboard_score = _clamp(
            0.40 * metrics.get("runtime_environment_coupling_index", 0.0)
            + 0.40 * metrics.get("environmental_grounding_stability_index", 0.0)
            + 0.20 * metrics.get("coupling_continuity_score", 0.0)
        )

        result = {
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "timestamp_utc": _now(),
            "html_path": str(self.html_path),
            "prometheus_path": str(self.prometheus_path),
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "metrics_exported": len(metrics),
            "metrics": metrics,
            "dashboard_score": round(dashboard_score, 6),
            "dashboard_certification": _certification(dashboard_score),
            "html_export_success": True,
            "prometheus_export_success": True,
            "json_state_export_success": True,
            "functional_measurement_only": True,
            "phenomenal_subjectivity_claimed": False,
            "dependencies": DEPENDENCIES,
            "error_count": 0,
        }

        self._write_prometheus(metrics)
        self._write_html(metrics, g17, g18, result)
        self._write_json_state(result)
        self._append_history(result)

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


ENGINE = EmbodiedCouplingDashboardExporter()


def step(inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return ENGINE.step(inputs)
