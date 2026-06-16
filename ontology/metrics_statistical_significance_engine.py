
from __future__ import annotations

import gzip
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


PRIMITIVE = "metrics_statistical_significance_engine"

DEPENDENCIES = [
    "metrics_aggregation_engine",
    "metrics_history_recorder",
    "longitudinal_metrics_archive",
    "consciousness_statistical_significance_engine",
    "scientific_meta_analysis_engine",
    "longitudinal_trend_stability_analyzer",
    "inter_run_stability_synthesizer",
    "scientific_anomaly_detector",
]


class MetricsStatisticalSignificanceEngine:
    # E4 statistical significance layer for the Open Cognitive Ecology metric pipeline.
    # This module intentionally does not replace E1, E2, E3 or E5.
    def __init__(
        self,
        root: Optional[Path] = None,
        alpha: float = 0.05,
        minimum_samples: int = 3,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.metrics_dir = self.root / "metrics"
        self.history_path = self.metrics_dir / "metrics_history.jsonl"
        self.summary_path = self.metrics_dir / "metrics_aggregation_summary.json"
        self.output_path = self.metrics_dir / "metrics_statistical_significance_summary.json"
        self.state_path = self.metrics_dir / "metrics_statistical_significance_engine_state.json"
        self.alpha = float(alpha)
        self.minimum_samples = int(minimum_samples)

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        aggregation_summary = self._load_json(self.summary_path)
        aggregations = aggregation_summary.get("aggregations", {}) if isinstance(aggregation_summary, dict) else {}

        records = self._load_records()
        metric_series = self._extract_metric_series(records)

        significance: Dict[str, Any] = {}
        for metric_name, aggregate in sorted(aggregations.items()):
            values = metric_series.get(metric_name, [])
            if not values:
                values = self._fallback_values_from_aggregate(aggregate)

            significance[metric_name] = self._analyze_metric(
                metric_name=metric_name,
                aggregate=aggregate,
                values=values,
            )

        significant_metric_count = sum(
            1 for item in significance.values()
            if item.get("statistically_supported") is True
        )
        trend_significant_count = sum(
            1 for item in significance.values()
            if item.get("trend_significant") is True
        )
        anomaly_significant_count = sum(
            1 for item in significance.values()
            if item.get("anomaly_significant") is True
        )

        analyzed_metric_count = len(significance)
        support_ratio = (
            significant_metric_count / analyzed_metric_count
            if analyzed_metric_count else 0.0
        )

        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "phase": "E4_METRICS_STATISTICAL_SIGNIFICANCE_ENGINE",
            "timestamp": self._utc_now(),
            "statistical_analysis_success": True,
            "metrics_statistical_significance_engine_operational": True,
            "source_summary_path": str(self.summary_path),
            "history_path": str(self.history_path),
            "summary_path": str(self.output_path),
            "state_path": str(self.state_path),
            "metric_count": analyzed_metric_count,
            "significant_metric_count": significant_metric_count,
            "trend_significant_count": trend_significant_count,
            "anomaly_significant_count": anomaly_significant_count,
            "statistical_support_ratio": support_ratio,
            "alpha": self.alpha,
            "minimum_samples": self.minimum_samples,
            "significance": significance,
            "diagnostics": {
                "consumes_e3_aggregation": True,
                "uses_e1_e2_time_series_when_available": True,
                "does_not_replace_e3_aggregation": True,
                "does_not_replace_e5_anomaly_detection": True,
                "stdlib_only": True,
                "normal_approximation_used": True,
                "confidence_level": 0.95,
            },
            "next_step": "E5_metrics_anomaly_detection_engine",
            "error_count": 0,
        }

        self._save_json(self.output_path, result)
        self._save_json(self.state_path, {
            "primitive": PRIMITIVE,
            "last_run": result["timestamp"],
            "metric_count": analyzed_metric_count,
            "statistical_support_ratio": support_ratio,
            "error_count": 0,
        })

        return result

    def _analyze_metric(
        self,
        metric_name: str,
        aggregate: Dict[str, Any],
        values: List[float],
    ) -> Dict[str, Any]:
        clean_values = [float(v) for v in values if self._is_number(v)]
        n = len(clean_values)

        mean = self._number(aggregate.get("mean"), self._mean(clean_values))
        variance = self._number(aggregate.get("variance"), self._variance(clean_values))
        sd = self._number(aggregate.get("standard_deviation"), math.sqrt(max(variance, 0.0)))
        stability_index = self._number(aggregate.get("stability_index"), 0.0)
        trend_slope = self._number(aggregate.get("trend_slope"), 0.0)
        trend_label = str(aggregate.get("trend", "insufficient_data"))

        ci_low, ci_high = self._confidence_interval(mean, sd, n)
        p_value = self._two_sided_p_value(mean, sd, n, baseline=0.0)
        effect_size = self._effect_size(mean, sd, baseline=0.0)

        trend_stats = self._trend_significance(clean_values)
        anomaly_stats = self._anomaly_significance(clean_values, stability_index)

        statistically_supported = (
            n >= self.minimum_samples
            and p_value is not None
            and p_value <= self.alpha
        )

        return {
            "sample_count": n,
            "mean": mean,
            "variance": variance,
            "standard_deviation": sd,
            "confidence_interval_95": [ci_low, ci_high],
            "p_value": p_value,
            "effect_size": effect_size,
            "statistically_supported": statistically_supported,
            "trend": trend_label,
            "trend_slope": trend_slope,
            "trend_p_value": trend_stats["p_value"],
            "trend_effect_size": trend_stats["effect_size"],
            "trend_significant": trend_stats["significant"],
            "anomaly_p_value": anomaly_stats["p_value"],
            "anomaly_effect_size": anomaly_stats["effect_size"],
            "anomaly_significant": anomaly_stats["significant"],
            "stability_index": stability_index,
            "diagnostics": {
                "insufficient_data": n < self.minimum_samples,
                "baseline": 0.0,
                "alpha": self.alpha,
                "metric_name": metric_name,
            },
        }

    def _load_records(self) -> List[Dict[str, Any]]:
        paths: List[Path] = []
        if self.history_path.exists():
            paths.append(self.history_path)
        for sub in ("daily", "weekly", "monthly"):
            directory = self.metrics_dir / sub
            if directory.exists():
                paths.extend(sorted(directory.glob("*.jsonl.gz")))

        records: List[Dict[str, Any]] = []
        seen = set()
        for path in paths:
            for record in self._iter_jsonl(path):
                key = (
                    record.get("timestamp"),
                    record.get("primitive"),
                    json.dumps(record.get("metrics", {}), sort_keys=True, default=str),
                )
                if key in seen:
                    continue
                seen.add(key)
                records.append(record)
        return records

    def _extract_metric_series(self, records: Iterable[Dict[str, Any]]) -> Dict[str, List[float]]:
        series: Dict[str, List[float]] = {}
        for record in records:
            metrics = record.get("metrics", {})
            if not isinstance(metrics, dict):
                continue
            for key, value in metrics.items():
                if self._is_number(value):
                    series.setdefault(str(key), []).append(float(value))
        return series

    def _fallback_values_from_aggregate(self, aggregate: Dict[str, Any]) -> List[float]:
        n = int(self._number(aggregate.get("sample_count"), 0.0))
        mean = aggregate.get("mean")
        if n <= 0 or not self._is_number(mean):
            return []
        return [float(mean)] * n

    def _iter_jsonl(self, path: Path) -> Iterable[Dict[str, Any]]:
        try:
            if path.suffix == ".gz":
                opener = lambda p: gzip.open(p, "rt", encoding="utf-8")
            else:
                opener = lambda p: open(p, "r", encoding="utf-8")
            with opener(path) as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                    except Exception:
                        continue
                    if isinstance(item, dict):
                        yield item
        except Exception:
            return

    def _confidence_interval(self, mean: float, sd: float, n: int) -> Tuple[Optional[float], Optional[float]]:
        if n <= 0:
            return None, None
        if n == 1 or sd == 0.0:
            return mean, mean
        margin = 1.96 * sd / math.sqrt(n)
        return mean - margin, mean + margin

    def _two_sided_p_value(self, mean: float, sd: float, n: int, baseline: float = 0.0) -> Optional[float]:
        if n < self.minimum_samples:
            return None
        if sd == 0.0:
            return 0.0 if mean != baseline else 1.0
        z = abs((mean - baseline) / (sd / math.sqrt(n)))
        return self._normal_two_sided_p(z)

    def _effect_size(self, mean: float, sd: float, baseline: float = 0.0) -> Optional[float]:
        if sd == 0.0:
            if mean == baseline:
                return 0.0
            return float("inf")
        return (mean - baseline) / sd

    def _trend_significance(self, values: List[float]) -> Dict[str, Any]:
        n = len(values)
        if n < self.minimum_samples:
            return {"p_value": None, "effect_size": 0.0, "significant": False}

        xs = list(range(n))
        x_mean = self._mean(xs)
        y_mean = self._mean(values)
        sxx = sum((x - x_mean) ** 2 for x in xs)
        if sxx == 0:
            return {"p_value": None, "effect_size": 0.0, "significant": False}

        slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, values)) / sxx
        residuals = [y - (y_mean + slope * (x - x_mean)) for x, y in zip(xs, values)]
        if n <= 2:
            return {"p_value": None, "effect_size": slope, "significant": False}

        residual_variance = sum(r ** 2 for r in residuals) / max(n - 2, 1)
        if residual_variance == 0.0:
            p_value = 0.0 if slope != 0.0 else 1.0
        else:
            se_slope = math.sqrt(residual_variance / sxx)
            z = abs(slope / se_slope) if se_slope else 0.0
            p_value = self._normal_two_sided_p(z)

        return {
            "p_value": p_value,
            "effect_size": slope,
            "significant": bool(p_value is not None and p_value <= self.alpha),
        }

    def _anomaly_significance(self, values: List[float], stability_index: float) -> Dict[str, Any]:
        n = len(values)
        if n < self.minimum_samples:
            return {"p_value": None, "effect_size": 0.0, "significant": False}

        mean = self._mean(values)
        sd = math.sqrt(self._variance(values))
        if sd == 0.0:
            z_max = 0.0
        else:
            z_max = max(abs(v - mean) / sd for v in values)

        single_tail = self._normal_two_sided_p(z_max)
        p_value = min(1.0, single_tail * n)
        instability_effect = max(0.0, 1.0 - float(stability_index))
        effect_size = max(z_max, instability_effect)

        return {
            "p_value": p_value,
            "effect_size": effect_size,
            "significant": bool(p_value <= self.alpha and effect_size >= 2.0),
        }

    def _normal_two_sided_p(self, z: float) -> float:
        if not math.isfinite(z):
            return 0.0
        return max(0.0, min(1.0, math.erfc(abs(z) / math.sqrt(2.0))))

    def _mean(self, values: Iterable[float]) -> float:
        vals = list(values)
        return sum(vals) / len(vals) if vals else 0.0

    def _variance(self, values: Iterable[float]) -> float:
        vals = list(values)
        if not vals:
            return 0.0
        m = self._mean(vals)
        return sum((v - m) ** 2 for v in vals) / len(vals)

    def _number(self, value: Any, default: float = 0.0) -> float:
        if self._is_number(value):
            return float(value)
        return float(default)

    def _is_number(self, value: Any) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            if not path.exists():
                return {}
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
        tmp.replace(path)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


ENGINE = MetricsStatisticalSignificanceEngine()


def step(inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return ENGINE.step(inputs)


if __name__ == "__main__":
    print(json.dumps(MetricsStatisticalSignificanceEngine().step(), indent=2, sort_keys=True))
