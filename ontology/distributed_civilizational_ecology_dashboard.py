from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


class DistributedCivilizationalEcologyDashboard:
    """
    N10 — Distributed Civilizational Ecology Dashboard.

    Visualise and exports the distributed civilizational ecology state.
    The module is deterministic when persist=False and writes HTML, JSON,
    Prometheus and Grafana artifacts when persist=True.
    """

    primitive = "DISTRIBUTED_CIVILIZATIONAL_ECOLOGY_DASHBOARD"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "runtime_reports" / "distributed_civilizational_ecology_dashboard"
        self.html_path = self.report_dir / "distributed_civilizational_ecology_dashboard.html"
        self.json_path = self.report_dir / "latest_distributed_civilizational_ecology_dashboard.json"
        self.prometheus_path = self.report_dir / "distributed_civilizational_ecology_dashboard.prom"
        self.grafana_path = self.report_dir / "distributed_civilizational_ecology_grafana.json"

    def _extract_metrics(self, inputs: dict[str, Any] | None) -> dict[str, float]:
        data = inputs or {}

        diversity = _clamp(data.get("cognitive_diversity_score", data.get("diversity_score", data.get("distributed_semantic_pluralism", 0.7))), 0.7)
        culture = _clamp(data.get("cultural_memory_score", data.get("cultural_memory_strength", 0.7)), 0.7)
        memory = _clamp(data.get("memory_continuity_score", data.get("civilizational_memory_index", data.get("intergenerational_transfer_score", 0.7))), 0.7)
        cooperation = _clamp(data.get("cooperative_specialization_score", data.get("social_learning_score", data.get("cooperation_score", 0.7))), 0.7)
        symbolic = _clamp(data.get("symbolic_structure_score", data.get("symbolic_emergence_score", 0.7)), 0.7)
        historicity = _clamp(data.get("historical_archive_score", data.get("historical_continuity_score", data.get("ecological_stability", 0.7))), 0.7)

        distributed_ecology_score = _clamp(data.get("distributed_ecology_score", _mean([diversity, culture, memory, cooperation, symbolic, historicity])), 0.7)
        ecological_stability = _clamp(data.get("ecological_stability", _mean([distributed_ecology_score, historicity, memory])), 0.7)
        ecological_growth_rate = _clamp(data.get("ecological_growth_rate", _mean([diversity, culture, symbolic])), 0.7)
        ecological_resilience = _clamp(data.get("ecological_resilience", _mean([distributed_ecology_score, ecological_stability, memory, cooperation])), 0.7)
        ecological_continuity_score = _clamp(data.get("ecological_continuity_score", _mean([memory, historicity, culture])), 0.7)
        closure_pressure_index = _clamp(data.get("closure_pressure_index", 0.0), 0.0)

        return {
            "diversity_visualization_score": diversity,
            "cultural_visualization_score": culture,
            "memory_visualization_score": memory,
            "cooperation_visualization_score": cooperation,
            "symbolic_visualization_score": symbolic,
            "historicity_visualization_score": historicity,
            "distributed_ecology_score": distributed_ecology_score,
            "ecological_stability": ecological_stability,
            "ecological_growth_rate": ecological_growth_rate,
            "ecological_resilience": ecological_resilience,
            "ecological_continuity_score": ecological_continuity_score,
            "closure_pressure_index": closure_pressure_index,
        }

    def _dashboard_score(self, metrics: dict[str, float]) -> float:
        positive = _mean([
            metrics["diversity_visualization_score"],
            metrics["cultural_visualization_score"],
            metrics["memory_visualization_score"],
            metrics["cooperation_visualization_score"],
            metrics["symbolic_visualization_score"],
            metrics["historicity_visualization_score"],
            metrics["distributed_ecology_score"],
            metrics["ecological_stability"],
            metrics["ecological_resilience"],
            metrics["ecological_continuity_score"],
        ])
        pressure_penalty = 0.25 * metrics["closure_pressure_index"]
        return round(_clamp(positive - pressure_penalty), 6)

    def _decision(self, dashboard_score: float, closure_pressure: float) -> dict[str, Any]:
        intervention = dashboard_score < 0.45 or closure_pressure >= 0.80
        warning = (not intervention) and (dashboard_score < 0.70 or closure_pressure >= 0.50)
        ready = not intervention and dashboard_score >= 0.70 and closure_pressure < 0.50
        if intervention:
            health = "dashboard_intervention_recommended"
        elif warning:
            health = "dashboard_warning"
        else:
            health = "dashboard_ready"
        return {
            "dashboard_health": health,
            "dashboard_ready": ready,
            "dashboard_warning": warning,
            "dashboard_intervention_recommended": intervention,
        }

    def _html(self, result: dict[str, Any]) -> str:
        rows = []
        for key in [
            "distributed_ecology_score",
            "ecological_stability",
            "ecological_growth_rate",
            "ecological_resilience",
            "ecological_continuity_score",
            "diversity_visualization_score",
            "cultural_visualization_score",
            "memory_visualization_score",
            "cooperation_visualization_score",
            "symbolic_visualization_score",
            "historicity_visualization_score",
            "dashboard_score",
            "dashboard_health",
        ]:
            rows.append(f"<tr><td>{key}</td><td>{result.get(key)}</td></tr>")
        rows_html = "\n".join(rows)
        generated = result.get("timestamp_utc", "deterministic_non_persisted")
        return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Distributed Civilizational Ecology Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
th {{ background: #f0f0f0; }}
.ok {{ color: #065f46; }}
.warn {{ color: #92400e; }}
.risk {{ color: #991b1b; }}
</style>
</head>
<body>
<h1>Distributed Civilizational Ecology Dashboard</h1>
<p>Generated: {generated}</p>
<table>
<tr><th>Metric</th><th>Value</th></tr>
{rows_html}
</table>
</body>
</html>
"""

    def _prometheus(self, result: dict[str, Any]) -> str:
        mapping = {
            "oce_distributed_ecology_score": "distributed_ecology_score",
            "oce_ecological_stability": "ecological_stability",
            "oce_ecological_growth_rate": "ecological_growth_rate",
            "oce_ecological_resilience": "ecological_resilience",
            "oce_ecological_continuity_score": "ecological_continuity_score",
            "oce_cultural_visualization_score": "cultural_visualization_score",
            "oce_memory_visualization_score": "memory_visualization_score",
            "oce_cooperation_visualization_score": "cooperation_visualization_score",
            "oce_symbolic_visualization_score": "symbolic_visualization_score",
            "oce_dashboard_score": "dashboard_score",
            "oce_closure_pressure_index": "closure_pressure_index",
        }
        lines = []
        for prom_name, key in mapping.items():
            value = _clamp(result.get(key, 0.0))
            lines.append(f"# TYPE {prom_name} gauge")
            lines.append(f"{prom_name} {value}")
        return "\n".join(lines) + "\n"

    def _grafana(self, result: dict[str, Any]) -> dict[str, Any]:
        metric_names = [
            "oce_distributed_ecology_score",
            "oce_ecological_stability",
            "oce_ecological_growth_rate",
            "oce_ecological_resilience",
            "oce_ecological_continuity_score",
            "oce_dashboard_score",
        ]
        panels = []
        for i, metric in enumerate(metric_names, start=1):
            panels.append({
                "id": i,
                "title": metric,
                "type": "stat",
                "targets": [{"expr": metric, "legendFormat": metric}],
                "gridPos": {"h": 4, "w": 8, "x": ((i - 1) % 3) * 8, "y": ((i - 1) // 3) * 4},
            })
        return {
            "title": "Distributed Civilizational Ecology Dashboard",
            "schemaVersion": 39,
            "version": 1,
            "refresh": "30s",
            "panels": panels,
            "tags": ["open-cognitive-ecology", "axis-n", "distributed-civilizational-ecology"],
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        metrics = self._extract_metrics(inputs)
        dashboard_score = self._dashboard_score(metrics)
        decision = self._decision(dashboard_score, metrics["closure_pressure_index"])

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            **metrics,
            "dashboard_score": dashboard_score,
            **decision,
            "exports": ["html", "json", "prometheus", "grafana"],
            "visualized_domains": [
                "memory",
                "culture",
                "diversity",
                "historicity",
                "cooperation",
                "symbolic_structures",
            ],
        }

        if persist:
            result["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
            self.report_dir.mkdir(parents=True, exist_ok=True)
            self.html_path.write_text(self._html(result), encoding="utf-8")
            self.json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            self.prometheus_path.write_text(self._prometheus(result), encoding="utf-8")
            self.grafana_path.write_text(json.dumps(self._grafana(result), indent=2, sort_keys=True), encoding="utf-8")
            result["html_path"] = str(self.html_path)
            result["json_path"] = str(self.json_path)
            result["prometheus_path"] = str(self.prometheus_path)
            result["grafana_path"] = str(self.grafana_path)
            result["report_path"] = str(self.json_path)

        return result
