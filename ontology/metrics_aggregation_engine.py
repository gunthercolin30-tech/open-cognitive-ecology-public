from __future__ import annotations

import gzip
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

PRIMITIVE = "metrics_aggregation_engine"
DEPENDENCIES = [
    "metrics_history_recorder",
    "longitudinal_metrics_archive",
    "civilizational_metrics_synthesizer",
    "enhanced_civilizational_metrics",
    "scientific_meta_analysis_engine",
    "scientific_anomaly_detector",
]


class MetricsAggregationEngine:
    """Aggregate longitudinal metrics produced by E1 and archived by E2.

    This primitive intentionally remains a pure aggregation layer. It does not
    replace statistical significance, anomaly detection, dashboards, Prometheus,
    or Grafana export. It prepares a stable quantitative substrate for E4-E10.
    """

    DEFAULT_METRICS = [
        "conversational_initiative_index",
        "noise_ratio",
        "conversation_continuity_score",
        "spontaneous_message_success_rate",
        "mutation_rate",
        "beneficial_mutation_ratio",
        "founder_independence_index",
        "civilizational_autonomy_score",
        "error_count",
    ]

    def __init__(
        self,
        root: Optional[Path] = None,
        metrics_dir: Optional[Path] = None,
        minimum_samples_for_trend: int = 3,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.metrics_dir = Path(metrics_dir) if metrics_dir is not None else self.root / "metrics"
        self.history_path = self.metrics_dir / "metrics_history.jsonl"
        self.output_path = self.metrics_dir / "metrics_aggregation_summary.json"
        self.state_path = self.metrics_dir / "metrics_aggregation_engine_state.json"
        self.minimum_samples_for_trend = int(max(2, minimum_samples_for_trend))

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _read_jsonl(self, path: Path) -> Iterable[Dict[str, Any]]:
        if not path.exists() or not path.is_file():
            return []
        records: List[Dict[str, Any]] = []
        try:
            opener = gzip.open if path.suffix == ".gz" else open
            with opener(path, "rt", encoding="utf-8") as fh:  # type: ignore[arg-type]
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if isinstance(obj, dict):
                        records.append(obj)
        except Exception:
            return []
        return records

    def _candidate_history_paths(self) -> List[Path]:
        paths: List[Path] = []
        paths.append(self.history_path)
        for pattern in ["daily/*.jsonl.gz", "weekly/*.jsonl.gz", "monthly/*.jsonl.gz"]:
            paths.extend(sorted(self.metrics_dir.glob(pattern)))
        # Keep order while removing duplicates.
        seen = set()
        unique: List[Path] = []
        for path in paths:
            key = str(path.resolve()) if path.exists() else str(path)
            if key not in seen:
                seen.add(key)
                unique.append(path)
        return unique

    def _flatten_numeric(self, obj: Any, prefix: str = "") -> Dict[str, float]:
        values: Dict[str, float] = {}
        if isinstance(obj, dict):
            for key, value in obj.items():
                key_str = str(key)
                next_prefix = f"{prefix}.{key_str}" if prefix else key_str
                values.update(self._flatten_numeric(value, next_prefix))
        elif isinstance(obj, bool):
            values[prefix] = 1.0 if obj else 0.0
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            number = float(obj)
            if math.isfinite(number):
                values[prefix] = number
        return values

    def _extract_metric_values(self, records: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, List[float]], int]:
        series: Dict[str, List[float]] = {}
        record_count = 0
        for record in records:
            record_count += 1
            metric_payload = record.get("metrics", {})
            flattened = self._flatten_numeric(metric_payload)
            if "error_count" in record and "error_count" not in flattened:
                try:
                    flattened["error_count"] = float(record.get("error_count", 0))
                except Exception:
                    pass
            for key, value in flattened.items():
                series.setdefault(key, []).append(float(value))
        return series, record_count

    def _mean(self, values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def _variance(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = self._mean(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

    def _sample_variance(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = self._mean(values)
        return sum((x - mean) ** 2 for x in values) / (len(values) - 1)

    def _trend_slope(self, values: List[float]) -> float:
        n = len(values)
        if n < self.minimum_samples_for_trend:
            return 0.0
        xs = list(range(n))
        x_mean = self._mean([float(x) for x in xs])
        y_mean = self._mean(values)
        denom = sum((x - x_mean) ** 2 for x in xs)
        if denom == 0:
            return 0.0
        return sum((xs[i] - x_mean) * (values[i] - y_mean) for i in range(n)) / denom

    def _trend_label(self, values: List[float]) -> str:
        if len(values) < self.minimum_samples_for_trend:
            return "insufficient_data"
        slope = self._trend_slope(values)
        scale = max(abs(self._mean(values)), 1.0)
        normalized = slope / scale
        if normalized > 0.01:
            return "increasing"
        if normalized < -0.01:
            return "decreasing"
        return "stable"

    def _stability_index(self, values: List[float]) -> float:
        if not values:
            return 0.0
        if len(values) == 1:
            return 1.0
        mean = abs(self._mean(values))
        std = math.sqrt(self._variance(values))
        scale = max(mean, 1.0)
        instability = min(1.0, std / scale)
        return max(0.0, min(1.0, 1.0 - instability))

    def _aggregate_series(self, values: List[float]) -> Dict[str, Any]:
        clean = [float(v) for v in values if math.isfinite(float(v))]
        if not clean:
            return {
                "sample_count": 0,
                "mean": 0.0,
                "variance": 0.0,
                "sample_variance": 0.0,
                "standard_deviation": 0.0,
                "min": 0.0,
                "max": 0.0,
                "trend": "insufficient_data",
                "trend_slope": 0.0,
                "stability_index": 0.0,
            }
        variance = self._variance(clean)
        return {
            "sample_count": len(clean),
            "mean": self._mean(clean),
            "variance": variance,
            "sample_variance": self._sample_variance(clean),
            "standard_deviation": math.sqrt(variance),
            "min": min(clean),
            "max": max(clean),
            "trend": self._trend_label(clean),
            "trend_slope": self._trend_slope(clean),
            "stability_index": self._stability_index(clean),
        }

    def _load_records(self, include_archives: bool = True) -> Tuple[List[Dict[str, Any]], List[str]]:
        paths = self._candidate_history_paths() if include_archives else [self.history_path]
        records: List[Dict[str, Any]] = []
        used_paths: List[str] = []
        seen = set()
        for path in paths:
            path_records = list(self._read_jsonl(path))
            if path_records:
                used_paths.append(str(path))
            for record in path_records:
                key = json.dumps(record, sort_keys=True, ensure_ascii=False)
                if key in seen:
                    continue
                seen.add(key)
                records.append(record)
        return records, used_paths

    def step(
        self,
        metric_names: Optional[List[str]] = None,
        include_archives: bool = True,
        write_summary: bool = True,
    ) -> Dict[str, Any]:
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        records, source_paths = self._load_records(include_archives=include_archives)
        series, record_count = self._extract_metric_values(records)

        requested = metric_names or self.DEFAULT_METRICS
        selected_names = list(dict.fromkeys(requested + sorted(series.keys())))
        aggregations = {
            name: self._aggregate_series(series.get(name, []))
            for name in selected_names
            if name in series or name in requested
        }

        populated = {k: v for k, v in aggregations.items() if v.get("sample_count", 0) > 0}
        stability_values = [float(v.get("stability_index", 0.0)) for v in populated.values()]
        global_stability = sum(stability_values) / len(stability_values) if stability_values else 0.0

        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "phase": "E3_METRICS_AGGREGATION_ENGINE",
            "timestamp": self._utc_now(),
            "history_path": str(self.history_path),
            "source_paths": source_paths,
            "record_count": record_count,
            "metric_count": len(populated),
            "requested_metric_count": len(requested),
            "aggregations": aggregations,
            "global_stability_index": global_stability,
            "aggregation_success": bool(record_count > 0 and populated),
            "metrics_aggregation_engine_operational": bool(record_count > 0 and populated),
            "summary_path": str(self.output_path),
            "state_path": str(self.state_path),
            "next_step": "E4_metrics_statistical_significance_engine",
            "error_count": 0,
            "diagnostics": {
                "pure_aggregation_layer": True,
                "does_not_replace_e1_history": True,
                "does_not_replace_e2_archive": True,
                "does_not_replace_e4_significance": True,
                "does_not_replace_e5_anomaly_detection": True,
                "archive_inputs_enabled": include_archives,
                "minimum_samples_for_trend": self.minimum_samples_for_trend,
            },
        }

        if write_summary:
            self.output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            self.state_path.write_text(json.dumps({
                "last_run_at": result["timestamp"],
                "record_count": record_count,
                "metric_count": len(populated),
                "global_stability_index": global_stability,
                "aggregation_success": result["aggregation_success"],
            }, indent=2, sort_keys=True), encoding="utf-8")

        return result


ENGINE = MetricsAggregationEngine()


def step(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    return ENGINE.step(*args, **kwargs)
