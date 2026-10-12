from __future__ import annotations

import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


class LongitudinalClosurePressureDashboard:
    """K10 - Longitudinal Closure Pressure Dashboard.

    Strictly observational dashboard consolidating closure-pressure axis K5-K9.
    It visualizes closure pressure, closure cascades, preserved openness,
    anti-closure recommendations and closure forecasting without executing actions,
    modifying identity, memory, or strategy.
    """

    primitive = "longitudinal_closure_pressure_dashboard"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "closure_pressure"
        self.state_dir = self.base_dir / self.primitive
        self.latest_path = self.state_dir / f"latest_{self.primitive}.json"
        self.history_path = self.state_dir / f"{self.primitive}_history.jsonl"
        self.dashboard_path = self.state_dir / f"{self.primitive}.html"
        self.prometheus_path = self.state_dir / f"{self.primitive}.prom"
        self.grafana_path = self.state_dir / f"{self.primitive}_grafana.json"
        self.upstream_paths = {
            "closure_pressure_monitor": self.base_dir / "closure_pressure_monitor" / "latest_closure_pressure_monitor.json",
            "closure_cascade_detector": self.base_dir / "closure_cascade_detector" / "latest_closure_cascade_detector.json",
            "openness_preservation_index": self.base_dir / "openness_preservation_index" / "latest_openness_preservation_index.json",
            "anti_closure_recommendation_engine": self.base_dir / "anti_closure_recommendation_engine" / "latest_anti_closure_recommendation_engine.json",
            "closure_pressure_forecasting_engine": self.base_dir / "closure_pressure_forecasting_engine" / "latest_closure_pressure_forecasting_engine.json",
        }
        self.history_paths = {
            "closure_pressure_monitor": self.base_dir / "closure_pressure_monitor" / "closure_pressure_monitor_history.jsonl",
            "closure_cascade_detector": self.base_dir / "closure_cascade_detector" / "closure_cascade_detector_history.jsonl",
            "openness_preservation_index": self.base_dir / "openness_preservation_index" / "openness_preservation_index_history.jsonl",
            "anti_closure_recommendation_engine": self.base_dir / "anti_closure_recommendation_engine" / "anti_closure_recommendation_engine_history.jsonl",
            "closure_pressure_forecasting_engine": self.base_dir / "closure_pressure_forecasting_engine" / "closure_pressure_forecasting_engine_history.jsonl",
        }

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if math.isnan(number) or math.isinf(number):
            number = default
        return max(0.0, min(1.0, number))

    def _load_json(self, path: Path) -> dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _read_jsonl(self, path: Path, limit: int = 120) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        try:
            if not path.exists():
                return rows
            for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
                if not line.strip():
                    continue
                item = json.loads(line)
                if isinstance(item, dict):
                    rows.append(item)
        except Exception:
            return rows
        return rows

    def _source(self, inputs: dict[str, Any], key: str) -> dict[str, Any]:
        sources = inputs.get("sources", {})
        if isinstance(sources, dict) and isinstance(sources.get(key), dict):
            return sources[key]
        if isinstance(inputs.get(key), dict):
            return inputs[key]
        return self._load_json(self.upstream_paths[key])

    def _history(self, inputs: dict[str, Any], key: str, limit: int) -> list[dict[str, Any]]:
        history = inputs.get("history", {})
        if isinstance(history, dict) and isinstance(history.get(key), list):
            return [row for row in history[key][-limit:] if isinstance(row, dict)]
        specific = inputs.get(f"{key}_history")
        if isinstance(specific, list):
            return [row for row in specific[-limit:] if isinstance(row, dict)]
        return self._read_jsonl(self.history_paths[key], limit=limit)

    @classmethod
    def _first_metric(cls, source: Mapping[str, Any], keys: Iterable[str], default: float = 0.0) -> float:
        for key in keys:
            if key in source:
                return cls._clamp(source.get(key), default=default)
        return cls._clamp(default)

    @classmethod
    def _extract_series(cls, rows: Iterable[Mapping[str, Any]], keys: list[str]) -> list[float]:
        series: list[float] = []
        for row in rows:
            for key in keys:
                if key in row:
                    series.append(cls._clamp(row.get(key)))
                    break
        return series

    def _series_from_sources(self, histories: dict[str, list[dict[str, Any]]]) -> dict[str, list[float]]:
        return {
            "rigidity_index": self._extract_series(histories["closure_pressure_monitor"], ["rigidity_index"]),
            "homogenization_index": self._extract_series(histories["closure_pressure_monitor"], ["homogenization_index"]),
            "exploratory_reduction_index": self._extract_series(histories["closure_pressure_monitor"], ["exploratory_reduction_index"]),
            "closure_pressure_index": self._extract_series(histories["closure_pressure_monitor"], ["closure_pressure_index"]),
            "closure_cascade_risk": self._extract_series(histories["closure_cascade_detector"], ["closure_cascade_risk"]),
            "openness_preservation_index": self._extract_series(histories["openness_preservation_index"], ["openness_preservation_index"]),
            "openness_loss_index": self._extract_series(histories["openness_preservation_index"], ["openness_loss_index"]),
            "recommendation_priority_score": self._extract_series(histories["anti_closure_recommendation_engine"], ["recommendation_priority_score"]),
            "expected_openness_gain": self._extract_series(histories["anti_closure_recommendation_engine"], ["expected_openness_gain"]),
            "predicted_closure_pressure": self._extract_series(histories["closure_pressure_forecasting_engine"], ["predicted_closure_pressure"]),
            "predicted_openness_loss": self._extract_series(histories["closure_pressure_forecasting_engine"], ["predicted_openness_loss"]),
            "forecast_confidence": self._extract_series(histories["closure_pressure_forecasting_engine"], ["forecast_confidence"]),
        }

    def _latest_metrics(self, sources: dict[str, dict[str, Any]], inputs: dict[str, Any]) -> dict[str, Any]:
        pressure = sources["closure_pressure_monitor"]
        cascade = sources["closure_cascade_detector"]
        openness = sources["openness_preservation_index"]
        recommendation = sources["anti_closure_recommendation_engine"]
        forecast = sources["closure_pressure_forecasting_engine"]
        return {
            "rigidity_index": self._first_metric(inputs, ["rigidity_index"], self._first_metric(pressure, ["rigidity_index"], 0.0)),
            "homogenization_index": self._first_metric(inputs, ["homogenization_index"], self._first_metric(pressure, ["homogenization_index"], 0.0)),
            "exploratory_reduction_index": self._first_metric(inputs, ["exploratory_reduction_index"], self._first_metric(pressure, ["exploratory_reduction_index"], 0.0)),
            "closure_pressure_index": self._first_metric(inputs, ["closure_pressure_index"], self._first_metric(pressure, ["closure_pressure_index"], 0.0)),
            "closure_cascade_risk": self._first_metric(inputs, ["closure_cascade_risk"], self._first_metric(cascade, ["closure_cascade_risk"], 0.0)),
            "openness_preservation_index": self._first_metric(inputs, ["openness_preservation_index"], self._first_metric(openness, ["openness_preservation_index"], 0.0)),
            "openness_loss_index": self._first_metric(inputs, ["openness_loss_index"], self._first_metric(openness, ["openness_loss_index"], 0.0)),
            "recommendation_priority_score": self._first_metric(inputs, ["recommendation_priority_score"], self._first_metric(recommendation, ["recommendation_priority_score"], 0.0)),
            "recommendation_confidence": self._first_metric(inputs, ["recommendation_confidence"], self._first_metric(recommendation, ["recommendation_confidence"], 0.0)),
            "expected_openness_gain": self._first_metric(inputs, ["expected_openness_gain"], self._first_metric(recommendation, ["expected_openness_gain"], 0.0)),
            "predicted_closure_pressure": self._first_metric(inputs, ["predicted_closure_pressure"], self._first_metric(forecast, ["predicted_closure_pressure"], 0.0)),
            "predicted_openness_loss": self._first_metric(inputs, ["predicted_openness_loss"], self._first_metric(forecast, ["predicted_openness_loss"], 0.0)),
            "forecast_confidence": self._first_metric(inputs, ["forecast_confidence"], self._first_metric(forecast, ["forecast_confidence"], 0.0)),
            "closure_horizon_estimate": inputs.get("closure_horizon_estimate", forecast.get("closure_horizon_estimate", "unknown")),
            "closure_trajectory_classification": inputs.get("closure_trajectory_classification", forecast.get("closure_trajectory_classification", "unknown")),
            "recommendation_priority": inputs.get("recommendation_priority", recommendation.get("recommendation_priority", "unknown")),
            "targeted_closure_factor": inputs.get("targeted_closure_factor", recommendation.get("targeted_closure_factor", "unknown")),
        }

    def _classify_dashboard_status(self, metrics: dict[str, Any]) -> str:
        pressure = self._clamp(metrics.get("closure_pressure_index"))
        cascade = self._clamp(metrics.get("closure_cascade_risk"))
        openness = self._clamp(metrics.get("openness_preservation_index"))
        predicted = self._clamp(metrics.get("predicted_closure_pressure"))
        risk = max(pressure, cascade, predicted, 1.0 - openness)
        if risk >= 0.82:
            return "critical_closure_dashboard"
        if risk >= 0.65:
            return "elevated_closure_watch_dashboard"
        if risk >= 0.45:
            return "moderate_closure_dashboard"
        return "open_trajectory_dashboard"

    @staticmethod
    def _series_summary(series: dict[str, list[float]]) -> dict[str, dict[str, Any]]:
        summary: dict[str, dict[str, Any]] = {}
        for key, values in series.items():
            if not values:
                summary[key] = {"count": 0, "latest": None, "mean": None, "min": None, "max": None}
                continue
            summary[key] = {
                "count": len(values),
                "latest": values[-1],
                "mean": round(sum(values) / len(values), 6),
                "min": min(values),
                "max": max(values),
            }
        return summary

    @staticmethod
    def _escape(value: Any) -> str:
        return html.escape(str(value))

    def _metric_bar(self, label: str, value: Any) -> str:
        if not isinstance(value, (int, float)):
            return "<tr><td>{}</td><td colspan='2'>{}</td></tr>".format(self._escape(label), self._escape(value))
        pct = self._clamp(value) * 100.0
        return "<tr><td>{}</td><td>{:.6f}</td><td><div class='bar'><span style='width:{:.2f}%'></span></div></td></tr>".format(
            self._escape(label), float(value), pct
        )

    def _render_html(self, result: dict[str, Any]) -> str:
        metrics = result.get("latest_metrics", {})
        series = result.get("longitudinal_series", {})
        recommendations = result.get("anti_closure_recommendations", [])
        metric_rows = "\n".join(self._metric_bar(k, v) for k, v in metrics.items()) or "<tr><td colspan='3'>No metrics available</td></tr>"
        series_rows = []
        for key, values in sorted(series.items()):
            tail = values[-10:] if isinstance(values, list) else []
            series_rows.append("<tr><td>{}</td><td>{}</td><td><code>{}</code></td></tr>".format(self._escape(key), len(tail), self._escape(json.dumps(tail, ensure_ascii=False))))
        series_rows_html = "\n".join(series_rows) or "<tr><td colspan='3'>No series available</td></tr>"
        rec_items = []
        if isinstance(recommendations, list):
            for item in recommendations[:12]:
                if isinstance(item, dict):
                    title = item.get("recommendation") or item.get("title") or item.get("description") or item.get("action") or item.get("id") or "recommendation"
                    priority = item.get("priority") or item.get("priority_score") or item.get("score") or ""
                    rec_items.append("<li><strong>{}</strong> {}</li>".format(self._escape(title), self._escape(priority)))
                else:
                    rec_items.append("<li>{}</li>".format(self._escape(item)))
        recommendations_html = "\n".join(rec_items) or "<li>No anti-closure recommendation available.</li>"
        generated = self._escape(result.get("timestamp_utc"))
        status = self._escape(result.get("dashboard_status"))
        return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Longitudinal Closure Pressure Dashboard</title>
<style>
body{{font-family:Arial,sans-serif;margin:40px;background:#fafafa;color:#222;}}
section{{background:white;border:1px solid #ddd;border-radius:8px;padding:18px;margin:18px 0;}}
table{{border-collapse:collapse;width:100%;margin-top:12px;}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left;vertical-align:top;}}
th{{background:#f0f0f0;}}
.bar{{width:100%;height:12px;background:#e6e6e6;border-radius:8px;overflow:hidden;}}
.bar span{{display:block;height:12px;background:#777;}}
code{{white-space:pre-wrap;}}
.badge{{display:inline-block;padding:6px 10px;border-radius:12px;background:#eee;font-weight:bold;}}
</style></head><body>
<h1>Longitudinal Closure Pressure Dashboard</h1>
<p>Generated at {generated}. Status: <span class='badge'>{status}</span></p>
<section><h2>Latest closure metrics</h2><table><tr><th>Metric</th><th>Value</th><th>Scale</th></tr>{metric_rows}</table></section>
<section><h2>Longitudinal series tails</h2><table><tr><th>Series</th><th>Displayed samples</th><th>Tail</th></tr>{series_rows_html}</table></section>
<section><h2>Anti-closure recommendations</h2><ul>{recommendations_html}</ul></section>
<section><h2>Governance</h2><p>Observational only. No action execution. No identity, memory or strategy modification.</p></section>
</body></html>"""

    def _render_prometheus(self, result: dict[str, Any]) -> str:
        lines = ["# HELP oce_closure_dashboard_metric Closure pressure dashboard metrics", "# TYPE oce_closure_dashboard_metric gauge"]
        for key, value in sorted(result.get("latest_metrics", {}).items()):
            if isinstance(value, (int, float)):
                lines.append(f'oce_closure_dashboard_metric{{metric="{key}"}} {float(value):.8f}')
        lines.append(f'oce_closure_dashboard_history_samples {int(result.get("history_samples_used", 0))}')
        status = str(result.get("dashboard_status", "unknown"))
        lines.append(f'oce_closure_dashboard_status{{status="{status}"}} 1')
        return "\n".join(lines) + "\n"

    def _render_grafana(self, result: dict[str, Any]) -> dict[str, Any]:
        metrics = [k for k, v in result.get("latest_metrics", {}).items() if isinstance(v, (int, float))]
        panels = []
        for idx, key in enumerate(metrics, start=1):
            panels.append({"id": idx, "type": "timeseries", "title": key, "targets": [{"expr": f'oce_closure_dashboard_metric{{metric="{key}"}}'}], "gridPos": {"h": 8, "w": 12, "x": 0 if idx % 2 else 12, "y": ((idx - 1) // 2) * 8}})
        return {"title": "Open Cognitive Ecology - Longitudinal Closure Pressure", "uid": "oce-closure-pressure-k10", "schemaVersion": 39, "version": 1, "tags": ["open-cognitive-ecology", "closure-pressure", "K10"], "panels": panels}

    def step(self, inputs: dict[str, Any] | None = None, history_limit: int = 120, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        history_limit = max(1, min(1000, int(history_limit or 120)))
        sources = {key: self._source(inputs, key) for key in self.upstream_paths}
        histories = {key: self._history(inputs, key, history_limit) for key in self.history_paths}
        latest_metrics = self._latest_metrics(sources, inputs)
        longitudinal_series = self._series_from_sources(histories)
        history_samples_used = sum(len(rows) for rows in histories.values())
        recommendation_source = sources.get("anti_closure_recommendation_engine", {})
        recommendations = inputs.get("anti_closure_recommendations", recommendation_source.get("anti_closure_recommendations", []))
        if not isinstance(recommendations, list):
            recommendations = []
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": self._now(),
            "success": True,
            "dashboard_ready": True,
            "observational_only": True,
            "latest_metrics": latest_metrics,
            "longitudinal_series": longitudinal_series,
            "series_summary": self._series_summary(longitudinal_series),
            "anti_closure_recommendations": recommendations,
            "dashboard_status": self._classify_dashboard_status(latest_metrics),
            "history_samples_used": history_samples_used,
            "visualized_dimensions": sorted(longitudinal_series.keys()),
            "source_availability": {key: bool(value) for key, value in sources.items()},
            "paths": {"latest_json": str(self.latest_path), "history_jsonl": str(self.history_path), "dashboard_html": str(self.dashboard_path), "prometheus": str(self.prometheus_path), "grafana": str(self.grafana_path)},
            "governance": {"observational_only": True, "does_not_execute_actions": True, "does_not_modify_identity": True, "does_not_modify_memory": True, "does_not_modify_strategy": True, "recommendations_remain_non_executive": True},
            "diagnostics": {"integrates_closure_pressure_monitor": bool(sources.get("closure_pressure_monitor")) or "closure_pressure_index" in inputs, "integrates_closure_cascade_detector": bool(sources.get("closure_cascade_detector")) or "closure_cascade_risk" in inputs, "integrates_openness_preservation_index": bool(sources.get("openness_preservation_index")) or "openness_preservation_index" in inputs, "integrates_anti_closure_recommendation_engine": bool(sources.get("anti_closure_recommendation_engine")) or "recommendation_priority_score" in inputs, "integrates_closure_pressure_forecasting_engine": bool(sources.get("closure_pressure_forecasting_engine")) or "predicted_closure_pressure" in inputs, "html_export_ready": True, "prometheus_export_ready": True, "grafana_export_ready": True},
        }
        if persist:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            self.dashboard_path.write_text(self._render_html(result), encoding="utf-8")
            self.prometheus_path.write_text(self._render_prometheus(result), encoding="utf-8")
            self.grafana_path.write_text(json.dumps(self._render_grafana(result), indent=2, ensure_ascii=False), encoding="utf-8")
        return result


if __name__ == "__main__":
    print(json.dumps(LongitudinalClosurePressureDashboard().step(), indent=2, ensure_ascii=False))
