from __future__ import annotations

import json
import gzip
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

PRIMITIVE = "metrics_anomaly_detection_engine"

DEPENDENCIES = [
    "metrics_history_recorder",
    "longitudinal_metrics_archive",
    "metrics_aggregation_engine",
    "metrics_statistical_significance_engine",
    "scientific_anomaly_detector",
    "structural_anomaly_detection",
    "longitudinal_drift_detection",
    "longitudinal_trend_stability_analyzer",
]


class MetricsAnomalyDetectionEngine:
    """Metrics-specific anomaly detection layer for Open Cognitive Ecology.

    This class consumes E3/E4 outputs and E1 time series. It does not replace
    scientific_anomaly_detector; it creates a bounded, auditable, metrics-only
    anomaly report suitable for downstream E6/E7/E8/E10 stages.
    """

    def __init__(
        self,
        root: Optional[Path] = None,
        z_threshold: float = 2.5,
        collapse_threshold: float = 0.50,
        continuity_drop_threshold: float = 0.10,
        noise_threshold: float = 0.10,
        drift_slope_threshold: float = 0.02,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.metrics_root = self.root / "metrics"
        self.history_path = self.metrics_root / "metrics_history.jsonl"
        self.aggregation_path = self.metrics_root / "metrics_aggregation_summary.json"
        self.significance_path = self.metrics_root / "metrics_statistical_significance_summary.json"
        self.summary_path = self.metrics_root / "metrics_anomaly_detection_summary.json"
        self.state_path = self.metrics_root / "metrics_anomaly_detection_engine_state.json"
        self.z_threshold = float(z_threshold)
        self.collapse_threshold = float(collapse_threshold)
        self.continuity_drop_threshold = float(continuity_drop_threshold)
        self.noise_threshold = float(noise_threshold)
        self.drift_slope_threshold = float(drift_slope_threshold)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        try:
            if value is None or isinstance(value, bool):
                return None
            f = float(value)
            if math.isnan(f) or math.isinf(f):
                return None
            return f
        except Exception:
            return None

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
        if not path.exists():
            return []
        def _gen() -> Iterable[Dict[str, Any]]:
            try:
                opener = gzip.open if path.suffix == ".gz" else open
                with opener(path, "rt", encoding="utf-8") as handle:  # type: ignore[arg-type]
                    for line in handle:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        if isinstance(obj, dict):
                            yield obj
            except Exception:
                return
        return _gen()

    def _load_timeseries(self) -> Dict[str, List[float]]:
        series: Dict[str, List[float]] = {}
        source_paths = [self.history_path]
        source_paths.extend(sorted((self.metrics_root / "daily").glob("*.jsonl.gz")))
        for path in source_paths:
            for record in self._iter_jsonl(path):
                metrics = record.get("metrics", {})
                if not isinstance(metrics, dict):
                    continue
                for key, value in metrics.items():
                    f = self._safe_float(value)
                    if f is None:
                        continue
                    series.setdefault(str(key), []).append(f)
                err = self._safe_float(record.get("error_count"))
                if err is not None:
                    series.setdefault("error_count", []).append(err)
        return series

    @staticmethod
    def _z_score(last: float, mean: float, std: float) -> float:
        if std <= 0:
            return 0.0
        return (last - mean) / std

    @staticmethod
    def _linear_slope(values: List[float]) -> float:
        n = len(values)
        if n < 3:
            return 0.0
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(values) / n
        denom = sum((x - mean_x) ** 2 for x in xs)
        if denom <= 0:
            return 0.0
        return sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values)) / denom

    def _classify_metric(
        self,
        name: str,
        agg: Dict[str, Any],
        sig: Dict[str, Any],
        values: List[float],
    ) -> List[Dict[str, Any]]:
        anomalies: List[Dict[str, Any]] = []
        sample_count = int(agg.get("sample_count") or sig.get("sample_count") or len(values) or 0)
        mean = self._safe_float(agg.get("mean"))
        std = self._safe_float(agg.get("standard_deviation")) or 0.0
        min_v = self._safe_float(agg.get("min"))
        max_v = self._safe_float(agg.get("max"))
        stability = self._safe_float(agg.get("stability_index"))
        trend = str(agg.get("trend") or sig.get("trend") or "unknown")
        trend_slope = self._safe_float(agg.get("trend_slope")) or self._safe_float(sig.get("trend_slope")) or 0.0
        trend_p = self._safe_float(sig.get("trend_p_value"))
        anomaly_p = self._safe_float(sig.get("anomaly_p_value"))
        anomaly_significant = bool(sig.get("anomaly_significant", False))

        if values and mean is not None:
            last = values[-1]
            z = self._z_score(last, mean, std)
            if abs(z) >= self.z_threshold and sample_count >= 3:
                anomalies.append({
                    "metric": name,
                    "type": "outlier",
                    "severity": "high" if abs(z) >= 3.5 else "moderate",
                    "value": last,
                    "z_score": z,
                    "sample_count": sample_count,
                    "message": "Latest value is far from its historical mean.",
                })

        if anomaly_significant:
            anomalies.append({
                "metric": name,
                "type": "statistically_significant_anomaly",
                "severity": "high" if (anomaly_p is not None and anomaly_p < 0.01) else "moderate",
                "p_value": anomaly_p,
                "sample_count": sample_count,
                "message": "E4 marked this metric as anomaly-significant.",
            })

        lower_name = name.lower()
        if mean is not None:
            if any(token in lower_name for token in ["continuity", "stability", "autonomy", "viability", "success", "integrity"]):
                if sample_count > 0 and mean < self.collapse_threshold:
                    anomalies.append({
                        "metric": name,
                        "type": "metric_collapse",
                        "severity": "critical" if mean < 0.25 else "high",
                        "mean": mean,
                        "threshold": self.collapse_threshold,
                        "message": "Core positive metric is below collapse threshold.",
                    })
                if values and len(values) >= 2 and values[-2] - values[-1] >= self.continuity_drop_threshold:
                    anomalies.append({
                        "metric": name,
                        "type": "continuity_drop",
                        "severity": "high",
                        "previous": values[-2],
                        "current": values[-1],
                        "drop": values[-2] - values[-1],
                        "message": "Continuity-like metric dropped sharply.",
                    })
            if "noise" in lower_name and mean > self.noise_threshold:
                anomalies.append({
                    "metric": name,
                    "type": "noise_increase",
                    "severity": "high" if mean > 0.25 else "moderate",
                    "mean": mean,
                    "threshold": self.noise_threshold,
                    "message": "Noise metric exceeds acceptable threshold.",
                })
            if "error" in lower_name and (max_v is not None and max_v > 0):
                anomalies.append({
                    "metric": name,
                    "type": "error_presence",
                    "severity": "moderate" if max_v <= 1 else "high",
                    "max": max_v,
                    "mean": mean,
                    "message": "Non-zero error count observed in metric history.",
                })

        if abs(trend_slope) >= self.drift_slope_threshold and sample_count >= 3:
            anomalies.append({
                "metric": name,
                "type": "slow_drift",
                "severity": "moderate",
                "trend": trend,
                "trend_slope": trend_slope,
                "trend_p_value": trend_p,
                "message": "Metric exhibits sustained drift above slope threshold.",
            })

        if trend_p is not None and trend_p < 0.05 and abs(trend_slope) > 0 and sample_count >= 3:
            # Trend significance is recorded as a signal, not automatically severe.
            anomalies.append({
                "metric": name,
                "type": "trend_break_candidate",
                "severity": "informational" if abs(trend_slope) < self.drift_slope_threshold else "moderate",
                "trend": trend,
                "trend_slope": trend_slope,
                "trend_p_value": trend_p,
                "message": "E4 marked trend as statistically significant; monitor for regime break.",
            })

        if stability is not None and stability < 0.80 and sample_count >= 3:
            anomalies.append({
                "metric": name,
                "type": "low_stability",
                "severity": "high" if stability < 0.60 else "moderate",
                "stability_index": stability,
                "message": "Metric stability index is below the target stability zone.",
            })

        # Deduplicate by type/metric while preserving first evidence.
        seen = set()
        unique: List[Dict[str, Any]] = []
        for item in anomalies:
            key = (item.get("metric"), item.get("type"))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique

    @staticmethod
    def _severity_score(severity: str) -> float:
        return {
            "informational": 0.10,
            "low": 0.20,
            "moderate": 0.45,
            "high": 0.75,
            "critical": 1.0,
        }.get(str(severity), 0.25)

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.metrics_root.mkdir(parents=True, exist_ok=True)
        aggregation = self._load_json(self.aggregation_path)
        significance = self._load_json(self.significance_path)
        series = self._load_timeseries()

        aggregations = aggregation.get("aggregations", {}) if isinstance(aggregation.get("aggregations", {}), dict) else {}
        sigs = significance.get("significance", {}) if isinstance(significance.get("significance", {}), dict) else {}
        metric_names = sorted(set(aggregations.keys()) | set(sigs.keys()) | set(series.keys()))

        anomalies: List[Dict[str, Any]] = []
        for name in metric_names:
            agg = aggregations.get(name, {}) if isinstance(aggregations.get(name, {}), dict) else {}
            sig = sigs.get(name, {}) if isinstance(sigs.get(name, {}), dict) else {}
            values = series.get(name, [])
            anomalies.extend(self._classify_metric(name, agg, sig, values))

        severity_counts: Dict[str, int] = {}
        for item in anomalies:
            sev = str(item.get("severity", "unknown"))
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        anomaly_score = 0.0
        if anomalies:
            anomaly_score = min(1.0, sum(self._severity_score(str(a.get("severity"))) for a in anomalies) / max(1.0, len(metric_names)))

        critical_anomaly_count = severity_counts.get("critical", 0)
        high_anomaly_count = severity_counts.get("high", 0)
        anomaly_detection_success = bool(aggregation.get("aggregation_success", True)) and bool(significance.get("statistical_analysis_success", True))

        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "phase": "E5_METRICS_ANOMALY_DETECTION_ENGINE",
            "timestamp": self._now(),
            "anomaly_detection_success": anomaly_detection_success,
            "metrics_anomaly_detection_engine_operational": anomaly_detection_success,
            "metric_count": len(metric_names),
            "anomaly_count": len(anomalies),
            "critical_anomaly_count": critical_anomaly_count,
            "high_anomaly_count": high_anomaly_count,
            "severity_counts": severity_counts,
            "anomaly_score": anomaly_score,
            "anomalies": anomalies,
            "source_paths": {
                "history": str(self.history_path),
                "aggregation": str(self.aggregation_path),
                "significance": str(self.significance_path),
            },
            "summary_path": str(self.summary_path),
            "state_path": str(self.state_path),
            "diagnostics": {
                "consumes_e3_aggregation": True,
                "consumes_e4_significance": True,
                "uses_e1_time_series": True,
                "does_not_replace_scientific_anomaly_detector": True,
                "does_not_replace_alerting_or_notification": True,
                "detects_trend_breaks": True,
                "detects_noise_increase": True,
                "detects_continuity_drop": True,
                "detects_metric_collapse": True,
                "detects_slow_drift": True,
                "detects_outliers": True,
                "stdlib_only": True,
            },
            "next_step": "E6_metrics_html_report_generator",
            "error_count": 0,
        }

        with self.summary_path.open("w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
        with self.state_path.open("w", encoding="utf-8") as handle:
            json.dump({
                "last_run": result["timestamp"],
                "anomaly_count": result["anomaly_count"],
                "critical_anomaly_count": critical_anomaly_count,
                "high_anomaly_count": high_anomaly_count,
                "anomaly_score": anomaly_score,
            }, handle, indent=2, sort_keys=True, allow_nan=False)
        return result


ENGINE = MetricsAnomalyDetectionEngine()


def step(inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return ENGINE.step(inputs)


if __name__ == "__main__":
    print(json.dumps(MetricsAnomalyDetectionEngine().step(), indent=2, sort_keys=True, allow_nan=False))
