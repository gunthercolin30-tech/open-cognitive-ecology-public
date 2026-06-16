from __future__ import annotations

import json
import math
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

PRIMITIVE = "prometheus_metrics_exporter"
DEPENDENCIES = [
    "metrics_history_recorder",
    "longitudinal_metrics_archive",
    "metrics_aggregation_engine",
    "metrics_statistical_significance_engine",
    "metrics_anomaly_detection_engine",
    "metrics_html_report_generator",
    "civilizational_metrics_synthesizer",
    "enhanced_civilizational_metrics",
]

ROOT = Path.home() / "open-cognitive-ecology"
METRICS_DIR = ROOT / "metrics"
PROM_DIR = METRICS_DIR / "prometheus"
PROM_PATH = PROM_DIR / "open_cognitive_ecology.prom"
STATE_PATH = METRICS_DIR / "prometheus_metrics_exporter_state.json"

PRIORITY_DEFAULTS = {
    "conversational_initiative_index": 0.0,
    "noise_ratio": 0.0,
    "error_count": 0.0,
    "runtime_cycle_count": 0.0,
    "spontaneous_message_count": 0.0,
    "spontaneous_message_success_rate": 0.0,
    "conversation_continuity_score": 0.0,
    "civilizational_autonomy_score": 0.0,
    "mutation_rate": 0.0,
    "beneficial_mutation_ratio": 0.0,
    "founder_independence_index": 0.0,
}

PROMETHEUS_NUMBER_RE = re.compile(
    r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?$"
)
PROMETHEUS_LINE_RE = re.compile(
    r"^[a-zA-Z_:][a-zA-Z0-9_:]*(\{[^}]*\})?\s+"
    r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?$"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _safe_metric_name(name: str) -> str:
    name = str(name).strip().lower()
    name = re.sub(r"[^a-zA-Z0-9_:]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "unknown_metric"
    if name[0].isdigit():
        name = "metric_" + name
    if not name.startswith("oce_"):
        name = "oce_" + name
    return name


def _float_or_default(value: Any, default: float | None = None) -> float | None:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if value is None:
        return default
    try:
        v = float(value)
    except Exception:
        return default
    if not math.isfinite(v):
        return default
    return v


def _line(name: str, value: Any, help_text: str = "", default: float | None = None) -> List[str]:
    v = _float_or_default(value, default)
    if v is None:
        return []
    metric = _safe_metric_name(name)
    safe_help = str(help_text or metric).replace("\\", "\\\\").replace("\n", " ")
    return [
        f"# HELP {metric} {safe_help}",
        f"# TYPE {metric} gauge",
        f"{metric} {v}",
    ]


def _collect_latest_history_metrics(history_path: Path) -> Dict[str, float]:
    latest: Dict[str, float] = {}
    if not history_path.exists():
        return latest
    try:
        for raw in history_path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            try:
                rec = json.loads(raw)
            except Exception:
                continue
            if not isinstance(rec, dict):
                continue
            metrics = rec.get("metrics", {})
            if isinstance(metrics, dict):
                for k, v in metrics.items():
                    fv = _float_or_default(v)
                    if fv is not None:
                        latest[str(k)] = fv
            fv = _float_or_default(rec.get("error_count"))
            if fv is not None:
                latest["error_count"] = fv
    except Exception:
        return latest
    return latest


def _validate_prometheus_text(text: str) -> Dict[str, Any]:
    bad = []
    metric_lines = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        metric_lines.append(line)
        if not PROMETHEUS_LINE_RE.match(line):
            bad.append(line)
    return {
        "metric_line_count": len(metric_lines),
        "bad_line_count": len(bad),
        "prometheus_syntax_valid": len(bad) == 0,
        "bad_lines_preview": bad[:10],
    }


class PrometheusMetricsExporter:
    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else ROOT
        self.metrics_dir = self.root / "metrics"
        self.prom_dir = self.metrics_dir / "prometheus"
        self.prom_path = self.prom_dir / "open_cognitive_ecology.prom"
        self.state_path = self.metrics_dir / "prometheus_metrics_exporter_state.json"

    def _build_payload(self) -> Dict[str, Any]:
        aggregation = _load_json(self.metrics_dir / "metrics_aggregation_summary.json", {})
        significance = _load_json(self.metrics_dir / "metrics_statistical_significance_summary.json", {})
        anomalies = _load_json(self.metrics_dir / "metrics_anomaly_detection_summary.json", {})
        html_state = _load_json(self.metrics_dir / "metrics_html_report_generator_state.json", {})
        history_latest = _collect_latest_history_metrics(self.metrics_dir / "metrics_history.jsonl")
        return {
            "aggregation": aggregation,
            "significance": significance,
            "anomalies": anomalies,
            "html_state": html_state,
            "history_latest": history_latest,
        }

    def render(self) -> Tuple[str, Dict[str, Any]]:
        payload = self._build_payload()
        aggregation = payload["aggregation"]
        significance = payload["significance"]
        anomalies = payload["anomalies"]
        html_state = payload["html_state"]
        latest = payload["history_latest"]

        lines: List[str] = [
            "# Open Cognitive Ecology Prometheus exposition",
            f"# Generated at {_utc_now()}",
        ]

        base_metrics = {
            "metrics_pipeline_aggregation_success": aggregation.get("aggregation_success"),
            "metrics_pipeline_statistical_analysis_success": significance.get("statistical_analysis_success"),
            "metrics_pipeline_anomaly_detection_success": anomalies.get("anomaly_detection_success"),
            "metrics_pipeline_html_report_generated": html_state.get("html_report_generated"),
            "metrics_metric_count": aggregation.get("metric_count") or anomalies.get("metric_count"),
            "metrics_record_count": aggregation.get("record_count"),
            "metrics_global_stability_index": aggregation.get("global_stability_index"),
            "metrics_statistical_support_ratio": significance.get("statistical_support_ratio"),
            "metrics_significant_metric_count": significance.get("significant_metric_count"),
            "metrics_trend_significant_count": significance.get("trend_significant_count"),
            "metrics_anomaly_count": anomalies.get("anomaly_count"),
            "metrics_critical_anomaly_count": anomalies.get("critical_anomaly_count"),
            "metrics_high_anomaly_count": anomalies.get("high_anomaly_count"),
            "metrics_anomaly_score": anomalies.get("anomaly_score"),
            "html_report_count": html_state.get("report_count"),
        }
        for key, value in base_metrics.items():
            lines.extend(_line(key, value, f"Open Cognitive Ecology {key}"))

        # E7-R.1: always export the explicit priority contract, with defaults.
        priority_values = dict(PRIORITY_DEFAULTS)
        for key in PRIORITY_DEFAULTS:
            if key in latest:
                priority_values[key] = latest[key]
        if "cycle_count" in latest and "runtime_cycle_count" not in latest:
            priority_values["runtime_cycle_count"] = latest["cycle_count"]

        for key, default_value in PRIORITY_DEFAULTS.items():
            lines.extend(_line(key, priority_values.get(key), f"Latest/default {key} from metrics history", default=default_value))

        aggregations = aggregation.get("aggregations", {}) if isinstance(aggregation, dict) else {}
        if isinstance(aggregations, dict):
            for metric_name, stats in sorted(aggregations.items()):
                if not isinstance(stats, dict):
                    continue
                for suffix in ["mean", "variance", "standard_deviation", "min", "max", "sample_count", "stability_index", "trend_slope"]:
                    if suffix in stats:
                        lines.extend(_line(f"metric_{metric_name}_{suffix}", stats.get(suffix), f"Aggregated {suffix} for {metric_name}"))

        significance_map = significance.get("significance", {}) if isinstance(significance, dict) else {}
        if isinstance(significance_map, dict):
            for metric_name, stats in sorted(significance_map.items()):
                if not isinstance(stats, dict):
                    continue
                for suffix in ["p_value", "trend_p_value", "anomaly_p_value", "effect_size", "trend_effect_size", "sample_count"]:
                    if suffix in stats:
                        lines.extend(_line(f"metric_{metric_name}_{suffix}", stats.get(suffix), f"Statistical {suffix} for {metric_name}"))
                lines.extend(_line(f"metric_{metric_name}_statistically_supported", stats.get("statistically_supported"), f"Statistical support flag for {metric_name}"))
                lines.extend(_line(f"metric_{metric_name}_trend_significant", stats.get("trend_significant"), f"Trend significance flag for {metric_name}"))
                lines.extend(_line(f"metric_{metric_name}_anomaly_significant", stats.get("anomaly_significant"), f"Anomaly significance flag for {metric_name}"))

        severity_counts = anomalies.get("severity_counts", {}) if isinstance(anomalies, dict) else {}
        if isinstance(severity_counts, dict):
            for severity, count in sorted(severity_counts.items()):
                lines.extend(_line(f"anomaly_severity_{severity}_count", count, f"Anomaly count for severity {severity}"))

        text = "\n".join(line for line in lines if line is not None) + "\n"
        validation = _validate_prometheus_text(text)
        exported_names = {line.split()[0] for line in text.splitlines() if line and not line.startswith("#")}
        missing_priority = sorted(_safe_metric_name(k) for k in PRIORITY_DEFAULTS if _safe_metric_name(k) not in exported_names)
        diagnostics = {
            "consumes_e1_to_e6_outputs": True,
            "prometheus_text_exposition": True,
            "does_not_launch_persistent_server": True,
            "future_metrics_endpoint_ready": True,
            "stdlib_only": True,
            "prometheus_metric_prefix": "oce_",
            "priority_defaults_enabled": True,
            "priority_metric_count": len(PRIORITY_DEFAULTS),
            "missing_priority_metrics": missing_priority,
            **validation,
        }
        return text, diagnostics

    def step(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        self.prom_dir.mkdir(parents=True, exist_ok=True)
        text, diagnostics = self.render()
        self.prom_path.write_text(text, encoding="utf-8")
        metric_lines = [line for line in text.splitlines() if line and not line.startswith("#")]
        ready = bool(
            self.prom_path.exists()
            and self.prom_path.stat().st_size > 0
            and diagnostics.get("prometheus_syntax_valid")
            and not diagnostics.get("missing_priority_metrics")
        )
        result = {
            "primitive": PRIMITIVE,
            "phase": "E7_PROMETHEUS_METRICS_EXPORTER_PRIORITY_DEFAULTS",
            "prometheus_metrics_exporter_operational": True,
            "prometheus_export_ready": ready,
            "prometheus_file_generated": self.prom_path.exists() and self.prom_path.stat().st_size > 0,
            "prometheus_path": str(self.prom_path),
            "metrics_endpoint_path": "/metrics",
            "metric_line_count": len(metric_lines),
            "diagnostics": diagnostics,
            "priority_defaults_enabled": True,
            "missing_priority_metrics": diagnostics.get("missing_priority_metrics", []),
            "state_path": str(self.state_path),
            "next_step": "E8_grafana_dashboard_exporter",
            "error_count": 0 if ready else 1,
            "timestamp": _utc_now(),
        }
        self.state_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return result


ENGINE = PrometheusMetricsExporter()


def step(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return ENGINE.step(payload)


if __name__ == "__main__":
    print(json.dumps(step(), indent=2, sort_keys=True))
