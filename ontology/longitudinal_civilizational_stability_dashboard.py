from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class LongitudinalCivilizationalStabilityDashboard:
    """
    J10 — Longitudinal Civilizational Stability Dashboard.

    Strictly observational dashboard consolidating J2-J9.
    """

    primitive = "longitudinal_civilizational_stability_dashboard"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.drift_dir = self.root / "civilizational_drift"
        self.latest_json = self.drift_dir / "latest_longitudinal_civilizational_stability_dashboard.json"
        self.history_jsonl = self.drift_dir / "longitudinal_civilizational_stability_dashboard_history.jsonl"
        self.dashboard_html = self.drift_dir / "longitudinal_civilizational_stability_dashboard.html"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            x = float(value)
        except (TypeError, ValueError):
            return default
        return max(0.0, min(1.0, x))

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return {}

    def _read_jsonl(self, path: Path, limit: int = 120) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if isinstance(data, dict):
                        rows.append(data)
                except Exception:
                    continue
        except Exception:
            return []
        return rows[-limit:]

    def _latest_sources(self) -> Dict[str, Dict[str, Any]]:
        files = {
            "identity": "latest_identity_drift_monitor.json",
            "strategy": "latest_strategic_drift_monitor.json",
            "memory": "latest_memory_drift_monitor.json",
            "correlation": "latest_drift_correlation_analyzer.json",
            "cascade": "latest_drift_cascade_detector.json",
            "stability": "latest_civilizational_stability_index.json",
            "forecast": "latest_drift_forecasting_engine.json",
            "recommendation": "latest_preventive_stability_recommendation_engine.json",
        }
        return {name: self._read_json(self.drift_dir / filename) for name, filename in files.items()}

    def _history_sources(self, limit: int = 120) -> Dict[str, List[Dict[str, Any]]]:
        files = {
            "identity": "identity_drift_monitor_history.jsonl",
            "strategy": "strategic_drift_monitor_history.jsonl",
            "memory": "memory_drift_monitor_history.jsonl",
            "correlation": "drift_correlation_analyzer_history.jsonl",
            "cascade": "drift_cascade_detector_history.jsonl",
            "stability": "civilizational_stability_index_history.jsonl",
            "forecast": "drift_forecasting_engine_history.jsonl",
            "recommendation": "preventive_stability_recommendation_engine_history.jsonl",
        }
        return {name: self._read_jsonl(self.drift_dir / filename, limit=limit) for name, filename in files.items()}

    def _extract_metrics(self, latest: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        return {
            "identity_drift_score": self._clamp(latest.get("identity", {}).get("identity_drift_score")),
            "strategic_drift_score": self._clamp(latest.get("strategy", {}).get("strategic_drift_score")),
            "memory_drift_score": self._clamp(latest.get("memory", {}).get("memory_drift_score")),
            "systemic_drift_coupling_index": self._clamp(latest.get("correlation", {}).get("systemic_drift_coupling_index")),
            "coordinated_drift_risk_index": self._clamp(latest.get("correlation", {}).get("coordinated_drift_risk_index")),
            "cascade_strength": self._clamp(latest.get("cascade", {}).get("cascade_strength")),
            "cascade_risk_index": self._clamp(latest.get("cascade", {}).get("cascade_risk_index")),
            "early_warning_score": self._clamp(latest.get("cascade", {}).get("early_warning_score")),
            "civilizational_stability_index": self._clamp(latest.get("stability", {}).get("civilizational_stability_index"), 1.0),
            "stability_risk_index": self._clamp(latest.get("stability", {}).get("stability_risk_index")),
            "forecast_risk_index": self._clamp(latest.get("forecast", {}).get("forecast_risk_index")),
            "forecast_confidence": self._clamp(latest.get("forecast", {}).get("forecast_confidence")),
            "recommendation_priority_score": self._clamp(latest.get("recommendation", {}).get("recommendation_priority_score")),
        }

    def _history_lengths(self, history: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        return {name: len(items) for name, items in history.items()}

    def _series(self, history: Dict[str, List[Dict[str, Any]]], key_map: Dict[str, str]) -> Dict[str, List[float]]:
        out: Dict[str, List[float]] = {}
        for name, key in key_map.items():
            out[name] = [self._clamp(item.get(key)) for item in history.get(name, []) if key in item]
        return out

    def _latest_timestamp(self, latest: Dict[str, Dict[str, Any]]) -> str:
        timestamps = []
        for data in latest.values():
            t = data.get("timestamp_utc") or data.get("timestamp")
            if isinstance(t, str):
                timestamps.append(t)
        return max(timestamps) if timestamps else self._now()

    def _classify_dashboard_status(self, metrics: Dict[str, float]) -> str:
        stability = metrics.get("civilizational_stability_index", 0.0)
        risk = max(
            metrics.get("stability_risk_index", 0.0),
            metrics.get("forecast_risk_index", 0.0),
            metrics.get("recommendation_priority_score", 0.0),
        )
        if stability >= 0.80 and risk < 0.35:
            return "robust"
        if stability >= 0.65 and risk < 0.55:
            return "stable"
        if stability >= 0.45 and risk < 0.75:
            return "watch"
        if stability >= 0.25:
            return "fragile"
        return "critical"

    def _html_table(self, title: str, rows: Dict[str, Any]) -> str:
        body = []
        for k, v in rows.items():
            body.append(
                "<tr><td>{}</td><td>{}</td></tr>".format(
                    html.escape(str(k)),
                    html.escape(str(v)),
                )
            )
        return "<h2>{}</h2><table><tr><th>Metric</th><th>Value</th></tr>{}</table>".format(
            html.escape(title), "".join(body)
        )

    def _bar(self, label: str, value: float) -> str:
        value = self._clamp(value)
        percent = round(value * 100, 2)
        return (
            "<div class='barrow'><span>{label}</span>"
            "<div class='bar'><div class='fill' style='width:{percent}%'></div></div>"
            "<b>{percent}%</b></div>"
        ).format(label=html.escape(label), percent=percent)

    def _render_html(self, result):
        import html as _html
        import json as _json

        latest = result.get("latest_metrics", {})
        series = result.get("longitudinal_series", {})
        recommendations = result.get("recommendations", [])
        visualized = result.get("visualized_dimensions", [])

        def esc(value):
            return _html.escape(str(value))

        def metric_rows(metrics):
            rows = []
            for key, value in sorted(metrics.items()):
                if isinstance(value, (int, float)):
                    label = esc(key)
                    pct = max(0.0, min(100.0, float(value) * 100.0))
                    rows.append(
                        "<tr><td>{}</td><td>{:.6f}</td><td>"
                        "<div class='bar'><span style='width:{:.2f}%'></span></div>"
                        "</td></tr>".format(label, float(value), pct)
                    )
                elif isinstance(value, str):
                    rows.append("<tr><td>{}</td><td colspan='2'>{}</td></tr>".format(esc(key), esc(value)))
            return "\n".join(rows) or "<tr><td colspan='3'>No latest metric available</td></tr>"

        def series_rows(series_data):
            rows = []
            for key, values in sorted(series_data.items()):
                if isinstance(values, list):
                    rows.append(
                        "<tr><td>{}</td><td>{}</td><td><code>{}</code></td></tr>".format(
                            esc(key),
                            len(values),
                            esc(_json.dumps(values[-8:], ensure_ascii=False)),
                        )
                    )
            return "\n".join(rows) or "<tr><td colspan='3'>No longitudinal series available</td></tr>"

        def recommendation_items(items):
            if not isinstance(items, list) or not items:
                return "<li>No preventive recommendation available.</li>"
            rendered = []
            for item in items:
                if isinstance(item, dict):
                    title = item.get("title") or item.get("recommendation") or item.get("action") or "recommendation"
                    priority = item.get("priority") or item.get("priority_score") or item.get("score") or ""
                    rendered.append("<li><strong>{}</strong> {}</li>".format(esc(title), esc(priority)))
                else:
                    rendered.append("<li>{}</li>".format(esc(item)))
            return "\n".join(rendered)

        generated = esc(result.get("timestamp_utc", ""))
        status = esc(result.get("dashboard_status", "unknown"))
        visualized_text = esc(", ".join(visualized))

        return """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Longitudinal Civilizational Stability Dashboard</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; background: #fafafa; color: #222; }
h1, h2 { color: #1f2933; }
section { background: white; border: 1px solid #d8dee4; border-radius: 8px; padding: 16px; margin: 16px 0; }
table { border-collapse: collapse; width: 100%; }
td, th { border: 1px solid #d8dee4; padding: 8px; text-align: left; vertical-align: top; }
th { background: #eef2f7; }
code { white-space: pre-wrap; }
.bar { width: 100%; background: #edf2f7; border-radius: 4px; height: 14px; overflow: hidden; }
.bar span { display: block; height: 14px; background: #4b5563; }
.meta { color: #586069; }
</style>
</head>
<body>
<h1>Longitudinal Civilizational Stability Dashboard</h1>
<p class="meta">Generated: """ + generated + """ — status: """ + status + """</p>
<section>
<h2>Visualized dimensions</h2>
<p>""" + visualized_text + """</p>
</section>
<section>
<h2>Latest metric bars</h2>
<table>
<tr><th>Metric</th><th>Value</th><th>Bar</th></tr>
""" + metric_rows(latest) + """
</table>
</section>
<section>
<h2>Longitudinal history</h2>
<table>
<tr><th>Series</th><th>Samples</th><th>Recent values</th></tr>
""" + series_rows(series) + """
</table>
</section>
<section>
<h2>Preventive recommendations</h2>
<ul>
""" + recommendation_items(recommendations) + """
</ul>
</section>
<section>
<h2>Governance</h2>
<p>Observation-only dashboard. No direct identity, memory, or strategy modification is performed.</p>
</section>
</body>
</html>"""
    def step(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        history_limit: int = 120,
        persist: bool = True,
    ) -> Dict[str, Any]:
        inputs = inputs or {}
        latest = inputs.get("latest") if isinstance(inputs.get("latest"), dict) else self._latest_sources()
        history = inputs.get("history") if isinstance(inputs.get("history"), dict) else self._history_sources(limit=history_limit)

        metrics = self._extract_metrics(latest)
        history_lengths = self._history_lengths(history)
        source_availability = {name: bool(data) for name, data in latest.items()}
        status = self._classify_dashboard_status(metrics)

        key_map = {
            "identity": "identity_drift_score",
            "strategy": "strategic_drift_score",
            "memory": "memory_drift_score",
            "correlation": "systemic_drift_coupling_index",
            "cascade": "cascade_risk_index",
            "stability": "civilizational_stability_index",
            "forecast": "forecast_risk_index",
            "recommendation": "recommendation_priority_score",
        }
        longitudinal_series = self._series(history, key_map)

        rec_data = latest.get("recommendation", {})
        recs: List[str] = []
        action_items = rec_data.get("recommended_actions", [])
        if isinstance(action_items, list):
            for item in action_items:
                if isinstance(item, dict):
                    recs.append(str(item.get("title") or item.get("recommendation") or item.get("action") or item))
                else:
                    recs.append(str(item))

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": self._now(),
            "monitor_ready": True,
            "dashboard_status": status,
            "latest_source_timestamp": self._latest_timestamp(latest),
            "latest_metrics": metrics,
            "source_availability": source_availability,
            "history_lengths": history_lengths,
            "longitudinal_series": longitudinal_series,
            "recommendations": recs,
            "dashboard_html_path": str(self.dashboard_html),
            "dashboard_json_path": str(self.latest_json),
            "visualized_dimensions": [
                "identity_drift",
                "strategic_drift",
                "memory_drift",
                "drift_correlation",
                "drift_cascade",
                "civilizational_stability",
                "drift_forecast",
                "preventive_recommendations",
            ],
            "governance": {
                "observational_only": True,
                "does_not_modify_identity": True,
                "does_not_modify_strategy": True,
                "does_not_modify_memory": True,
                "does_not_execute_actions": True,
                "does_not_authorize_mutation": True,
                "does_not_merge_ontology_inventory_and_global_catalog": True,
            },
        }

        if persist:
            self.drift_dir.mkdir(parents=True, exist_ok=True)
            self.latest_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            with self.history_jsonl.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result, ensure_ascii=False) + "\\n")
            self.dashboard_html.write_text(self._render_html(result), encoding="utf-8")

        return result
