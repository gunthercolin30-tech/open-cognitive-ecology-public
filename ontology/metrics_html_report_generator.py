from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import html

PRIMITIVE = "metrics_html_report_generator"
DEPENDENCIES = [
    "metrics_history_recorder",
    "longitudinal_metrics_archive",
    "metrics_aggregation_engine",
    "metrics_statistical_significance_engine",
    "metrics_anomaly_detection_engine",
    "civilizational_web_dashboard",
    "web_dashboard_exporter",
    "experiment_stability_dashboard",
]

ROOT = Path.home() / "open-cognitive-ecology"
METRICS_DIR = ROOT / "metrics"
REPORTS_DIR = METRICS_DIR / "reports"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path, default):
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return default
    return default


def _safe(value) -> str:
    return html.escape(str(value), quote=True)


def _fmt_float(value) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return _safe(value)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _page(title: str, body: str) -> str:
    generated = _utc_now()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_safe(title)}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2933; background: #fafafa; }}
h1, h2 {{ color: #111827; }}
.card {{ background: white; border: 1px solid #d8dee4; border-radius: 10px; padding: 16px; margin: 16px 0; box-shadow: 0 1px 2px rgba(0,0,0,.04); }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; background: white; }}
th, td {{ border: 1px solid #d8dee4; padding: 8px; text-align: left; vertical-align: top; }}
th {{ background: #eef2f7; }}
.badge {{ display:inline-block; padding: 2px 8px; border-radius: 999px; background:#eef2f7; }}
.ok {{ color: #166534; font-weight: bold; }}
.warn {{ color: #92400e; font-weight: bold; }}
.critical {{ color: #991b1b; font-weight: bold; }}
.small {{ color:#667085; font-size: 0.9em; }}
pre {{ white-space: pre-wrap; background: #f3f4f6; padding: 12px; border-radius: 8px; }}
</style>
</head>
<body>
<h1>{_safe(title)}</h1>
<p class="small">Generated at {generated}. Open Cognitive Ecology metrics instrumentation report.</p>
{body}
</body>
</html>"""


def _summary_cards(aggregation, significance, anomalies):
    return f"""
<div class="card"><h2>Pipeline status</h2>
<table>
<tr><th>Layer</th><th>Status</th></tr>
<tr><td>E3 aggregation</td><td>{_safe(aggregation.get('aggregation_success'))}</td></tr>
<tr><td>E4 statistical significance</td><td>{_safe(significance.get('statistical_analysis_success'))}</td></tr>
<tr><td>E5 anomaly detection</td><td>{_safe(anomalies.get('anomaly_detection_success'))}</td></tr>
<tr><td>Metric count</td><td>{_safe(aggregation.get('metric_count', significance.get('metric_count', anomalies.get('metric_count', 0))))}</td></tr>
<tr><td>Anomaly count</td><td>{_safe(anomalies.get('anomaly_count', 0))}</td></tr>
<tr><td>Critical anomalies</td><td>{_safe(anomalies.get('critical_anomaly_count', 0))}</td></tr>
<tr><td>High anomalies</td><td>{_safe(anomalies.get('high_anomaly_count', 0))}</td></tr>
</table></div>
"""


def _aggregation_table(aggregation, limit: int = 50):
    rows = []
    aggs = aggregation.get("aggregations", {}) if isinstance(aggregation, dict) else {}
    for name, data in sorted(aggs.items())[:limit]:
        rows.append(
            "<tr>"
            f"<td>{_safe(name)}</td>"
            f"<td>{_safe(data.get('sample_count'))}</td>"
            f"<td>{_fmt_float(data.get('mean'))}</td>"
            f"<td>{_fmt_float(data.get('standard_deviation'))}</td>"
            f"<td>{_fmt_float(data.get('min'))}</td>"
            f"<td>{_fmt_float(data.get('max'))}</td>"
            f"<td>{_safe(data.get('trend'))}</td>"
            f"<td>{_fmt_float(data.get('stability_index'))}</td>"
            "</tr>"
        )
    return """
<div class="card"><h2>Aggregated metrics</h2>
<table><tr><th>Metric</th><th>n</th><th>Mean</th><th>Std dev</th><th>Min</th><th>Max</th><th>Trend</th><th>Stability</th></tr>
""" + "\n".join(rows) + "</table></div>"


def _significance_table(significance, limit: int = 50):
    rows = []
    sig = significance.get("significance", {}) if isinstance(significance, dict) else {}
    for name, data in sorted(sig.items())[:limit]:
        ci = data.get("confidence_interval_95")
        rows.append(
            "<tr>"
            f"<td>{_safe(name)}</td>"
            f"<td>{_safe(data.get('sample_count'))}</td>"
            f"<td>{_safe(data.get('statistically_supported'))}</td>"
            f"<td>{_fmt_float(data.get('p_value'))}</td>"
            f"<td>{_fmt_float(data.get('effect_size'))}</td>"
            f"<td>{_safe(ci)}</td>"
            f"<td>{_safe(data.get('trend_significant'))}</td>"
            f"<td>{_fmt_float(data.get('trend_p_value'))}</td>"
            "</tr>"
        )
    return """
<div class="card"><h2>Statistical significance</h2>
<table><tr><th>Metric</th><th>n</th><th>Supported</th><th>p-value</th><th>Effect size</th><th>95% CI</th><th>Trend significant</th><th>Trend p-value</th></tr>
""" + "\n".join(rows) + "</table></div>"


def _anomaly_table(anomalies, limit: int = 80):
    rows = []
    anomaly_list = anomalies.get("anomalies", []) if isinstance(anomalies, dict) else []
    severity_class = {"critical":"critical", "high":"critical", "moderate":"warn", "informational":"ok"}
    for item in anomaly_list[:limit]:
        severity = str(item.get("severity", "informational"))
        cls = severity_class.get(severity, "")
        rows.append(
            "<tr>"
            f"<td>{_safe(item.get('metric'))}</td>"
            f"<td>{_safe(item.get('type'))}</td>"
            f"<td class='{cls}'>{_safe(severity)}</td>"
            f"<td>{_safe(item.get('message'))}</td>"
            "</tr>"
        )
    return """
<div class="card"><h2>Anomaly detection</h2>
<table><tr><th>Metric</th><th>Type</th><th>Severity</th><th>Message</th></tr>
""" + "\n".join(rows) + "</table></div>"


class MetricsHTMLReportGenerator:
    def __init__(self, metrics_dir: Path | None = None, reports_dir: Path | None = None):
        self.metrics_dir = Path(metrics_dir) if metrics_dir else METRICS_DIR
        self.reports_dir = Path(reports_dir) if reports_dir else REPORTS_DIR

    def _load_inputs(self):
        aggregation = _read_json(self.metrics_dir / "metrics_aggregation_summary.json", {})
        significance = _read_json(self.metrics_dir / "metrics_statistical_significance_summary.json", {})
        anomalies = _read_json(self.metrics_dir / "metrics_anomaly_detection_summary.json", {})
        archive_manifest = _read_json(self.metrics_dir / "longitudinal_metrics_archive_manifest.json", {})
        return aggregation, significance, anomalies, archive_manifest

    def step(self, inputs: dict | None = None) -> dict:
        aggregation, significance, anomalies, archive_manifest = self._load_inputs()
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        common = _summary_cards(aggregation, significance, anomalies)

        metrics_report = _page(
            "Open Cognitive Ecology — Metrics Report",
            common + _aggregation_table(aggregation) + _significance_table(significance) + _anomaly_table(anomalies),
        )
        longitudinal_report = _page(
            "Open Cognitive Ecology — Longitudinal Metrics Dashboard",
            common + f"<div class='card'><h2>Archive manifest</h2><pre>{_safe(json.dumps(archive_manifest, indent=2, ensure_ascii=False)[:12000])}</pre></div>" + _aggregation_table(aggregation),
        )
        conversation_report = _page(
            "Open Cognitive Ecology — Conversation Metrics Report",
            common + self._filtered_metrics(aggregation, significance, anomalies, ["conversation", "conversational", "spontaneous", "noise", "terminal"]),
        )
        runtime_report = _page(
            "Open Cognitive Ecology — Runtime Metrics Report",
            common + self._filtered_metrics(aggregation, significance, anomalies, ["runtime", "cycle", "error", "stability", "mutation", "orchestration"]),
        )

        paths = {
            "metrics_report": self.reports_dir / "metrics_report.html",
            "longitudinal_metrics_dashboard": self.reports_dir / "longitudinal_metrics_dashboard.html",
            "conversation_metrics_report": self.reports_dir / "conversation_metrics_report.html",
            "runtime_metrics_report": self.reports_dir / "runtime_metrics_report.html",
        }
        _write(paths["metrics_report"], metrics_report)
        _write(paths["longitudinal_metrics_dashboard"], longitudinal_report)
        _write(paths["conversation_metrics_report"], conversation_report)
        _write(paths["runtime_metrics_report"], runtime_report)

        state = {
            "primitive": PRIMITIVE,
            "phase": "E6_METRICS_HTML_REPORT_GENERATOR",
            "timestamp": _utc_now(),
            "html_report_generated": True,
            "report_count": len(paths),
            "reports": {k: str(v) for k, v in paths.items()},
            "source_files": {
                "aggregation": str(self.metrics_dir / "metrics_aggregation_summary.json"),
                "significance": str(self.metrics_dir / "metrics_statistical_significance_summary.json"),
                "anomalies": str(self.metrics_dir / "metrics_anomaly_detection_summary.json"),
                "archive_manifest": str(self.metrics_dir / "longitudinal_metrics_archive_manifest.json"),
            },
        }
        state_path = self.metrics_dir / "metrics_html_report_generator_state.json"
        _write(state_path, json.dumps(state, indent=2, ensure_ascii=False))

        success = all(p.exists() and p.stat().st_size > 0 for p in paths.values())
        return {
            "primitive": PRIMITIVE,
            "phase": "E6_METRICS_HTML_REPORT_GENERATOR",
            "metrics_html_report_generator_operational": success,
            "html_report_generated": success,
            "report_count": len(paths),
            "reports": {k: str(v) for k, v in paths.items()},
            "metrics_report_path": str(paths["metrics_report"]),
            "longitudinal_metrics_dashboard_path": str(paths["longitudinal_metrics_dashboard"]),
            "conversation_metrics_report_path": str(paths["conversation_metrics_report"]),
            "runtime_metrics_report_path": str(paths["runtime_metrics_report"]),
            "state_path": str(state_path),
            "aggregation_success": bool(aggregation.get("aggregation_success")),
            "statistical_analysis_success": bool(significance.get("statistical_analysis_success")),
            "anomaly_detection_success": bool(anomalies.get("anomaly_detection_success")),
            "diagnostics": {
                "consumes_e1_to_e5_outputs": True,
                "does_not_replace_existing_dashboards": True,
                "stdlib_only": True,
                "html_escaped": True,
                "report_directory": str(self.reports_dir),
            },
            "next_step": "E7_prometheus_metrics_exporter",
            "error_count": 0 if success else 1,
        }

    def _filtered_metrics(self, aggregation, significance, anomalies, keywords):
        keywords = [k.lower() for k in keywords]
        aggs = aggregation.get("aggregations", {}) if isinstance(aggregation, dict) else {}
        filtered_agg = {k: v for k, v in aggs.items() if any(word in k.lower() for word in keywords)}
        sig = significance.get("significance", {}) if isinstance(significance, dict) else {}
        filtered_sig = {k: v for k, v in sig.items() if any(word in k.lower() for word in keywords)}
        anoms = anomalies.get("anomalies", []) if isinstance(anomalies, dict) else []
        filtered_anoms = [a for a in anoms if any(word in str(a.get("metric", "")).lower() for word in keywords)]
        return (
            _aggregation_table({"aggregations": filtered_agg})
            + _significance_table({"significance": filtered_sig})
            + _anomaly_table({"anomalies": filtered_anoms})
        )


ENGINE = MetricsHTMLReportGenerator()

if __name__ == "__main__":
    print(json.dumps(ENGINE.step(), indent=2, ensure_ascii=False))
