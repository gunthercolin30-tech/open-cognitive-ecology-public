from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


class DriftForecastingEngine:
    """
    J8 — Drift Forecasting Engine.

    Specialized observational forecaster for civilizational drift.
    It does not alter identity, strategy, memory, or governance state.
    It extrapolates future drift pressure and stability from J5-J7 signals.
    """

    primitive = "drift_forecasting_engine"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.output_dir = self.root / "civilizational_drift"
        self.latest_path = self.output_dir / "latest_drift_forecasting_engine.json"
        self.history_path = self.output_dir / "drift_forecasting_engine_history.jsonl"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            x = float(value)
        except (TypeError, ValueError):
            x = default
        if math.isnan(x) or math.isinf(x):
            x = default
        return max(0.0, min(1.0, x))

    @staticmethod
    def _safe_dict(value: Any) -> Dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                return self._safe_dict(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            return {}
        return {}

    def _read_jsonl(self, path: Path, limit: int = 32) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
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

    def _default_inputs(self) -> Dict[str, Any]:
        d = self.output_dir
        return {
            "stability": self._read_json(d / "latest_civilizational_stability_index.json"),
            "cascade": self._read_json(d / "latest_drift_cascade_detector.json"),
            "correlation": self._read_json(d / "latest_drift_correlation_analyzer.json"),
            "history": {
                "stability": self._read_jsonl(d / "civilizational_stability_index_history.jsonl"),
                "cascade": self._read_jsonl(d / "drift_cascade_detector_history.jsonl"),
                "correlation": self._read_jsonl(d / "drift_correlation_analyzer_history.jsonl"),
            },
        }

    @staticmethod
    def _extract_series(rows: Iterable[Mapping[str, Any]], keys: Iterable[str]) -> List[float]:
        series: List[float] = []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            for key in keys:
                if key in row:
                    series.append(DriftForecastingEngine._clamp(row.get(key)))
                    break
        return series

    @staticmethod
    def _linear_slope(series: List[float]) -> float:
        n = len(series)
        if n < 2:
            return 0.0
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(series) / n
        den = sum((x - mean_x) ** 2 for x in xs)
        if den == 0:
            return 0.0
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, series))
        return num / den

    def _forecast(self, current: float, slope: float, horizon: int) -> List[float]:
        return [self._clamp(current + slope * step) for step in range(1, horizon + 1)]

    def _classification(self, risk: float) -> str:
        if risk >= 0.75:
            return "critical_forecast"
        if risk >= 0.55:
            return "elevated_forecast"
        if risk >= 0.35:
            return "watch_forecast"
        return "stable_forecast"

    def _stability_horizon(self, trajectory: List[float], threshold: float = 0.60) -> Any:
        for idx, value in enumerate(trajectory, start=1):
            if value < threshold:
                return idx
        return "beyond_forecast_horizon"

    def step(self, inputs: Optional[Dict[str, Any]] = None, forecast_horizon_steps: int = 6, persist: bool = True) -> Dict[str, Any]:
        data = self._default_inputs()
        if isinstance(inputs, dict):
            for key, value in inputs.items():
                if key == "history" and isinstance(value, dict):
                    merged = dict(data.get("history", {}))
                    merged.update(value)
                    data["history"] = merged
                else:
                    data[key] = value

        stability = self._safe_dict(data.get("stability"))
        cascade = self._safe_dict(data.get("cascade"))
        correlation = self._safe_dict(data.get("correlation"))
        history = self._safe_dict(data.get("history"))

        horizon = max(1, min(24, int(forecast_horizon_steps or 6)))

        current_stability = self._clamp(stability.get("civilizational_stability_index", 0.5), 0.5)
        current_drift_pressure = self._clamp(stability.get("drift_pressure_index", 1.0 - current_stability))
        cascade_risk = self._clamp(cascade.get("cascade_risk_index", cascade.get("cascade_strength", 0.0)))
        early_warning = self._clamp(cascade.get("early_warning_score", 0.0))
        coupling = self._clamp(correlation.get("systemic_drift_coupling_index", 0.0))
        coordinated = self._clamp(correlation.get("coordinated_drift_risk_index", 0.0))

        stability_series = self._extract_series(
            history.get("stability", []),
            ["civilizational_stability_index", "early_warning_adjusted_stability"],
        )
        cascade_series = self._extract_series(
            history.get("cascade", []),
            ["cascade_risk_index", "cascade_strength", "early_warning_score"],
        )
        correlation_series = self._extract_series(
            history.get("correlation", []),
            ["coordinated_drift_risk_index", "systemic_drift_coupling_index"],
        )

        stability_slope = self._linear_slope(stability_series) if stability_series else 0.0
        cascade_slope = self._linear_slope(cascade_series) if cascade_series else 0.0
        correlation_slope = self._linear_slope(correlation_series) if correlation_series else 0.0

        adverse_slope = self._clamp(max(0.0, -stability_slope) + max(0.0, cascade_slope) + max(0.0, correlation_slope))
        pressure_base = (current_drift_pressure + cascade_risk + early_warning + coupling + coordinated) / 5.0
        predicted_drift_pressure = self._forecast(pressure_base, adverse_slope / max(1, horizon), horizon)

        stability_decline_rate = (predicted_drift_pressure[-1] - predicted_drift_pressure[0]) / max(1, horizon - 1) if horizon > 1 else 0.0
        predicted_stability_trajectory = [
            self._clamp(current_stability - (pressure * 0.18) - (stability_decline_rate * idx))
            for idx, pressure in enumerate(predicted_drift_pressure, start=1)
        ]

        forecast_risk_index = self._clamp(
            (predicted_drift_pressure[-1] * 0.45)
            + ((1.0 - predicted_stability_trajectory[-1]) * 0.35)
            + (early_warning * 0.20)
        )
        evidence_points = len(stability_series) + len(cascade_series) + len(correlation_series)
        forecast_confidence = self._clamp(min(1.0, evidence_points / 12.0) * 0.75 + 0.25)
        stability_horizon_estimate = self._stability_horizon(predicted_stability_trajectory)

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": self._now(),
            "monitor_ready": True,
            "forecast_horizon_steps": horizon,
            "current_stability_index": current_stability,
            "current_drift_pressure": current_drift_pressure,
            "forecast_inputs": {
                "cascade_risk_index": cascade_risk,
                "early_warning_score": early_warning,
                "systemic_drift_coupling_index": coupling,
                "coordinated_drift_risk_index": coordinated,
                "history_points": evidence_points,
            },
            "forecast_slopes": {
                "stability_slope": stability_slope,
                "cascade_slope": cascade_slope,
                "correlation_slope": correlation_slope,
                "adverse_slope": adverse_slope,
            },
            "predicted_stability_trajectory": predicted_stability_trajectory,
            "predicted_drift_pressure": predicted_drift_pressure,
            "forecast_risk_index": forecast_risk_index,
            "forecast_confidence": forecast_confidence,
            "stability_horizon_estimate": stability_horizon_estimate,
            "forecast_classification": self._classification(forecast_risk_index),
            "governance": {
                "observational_only": True,
                "does_not_modify_identity": True,
                "does_not_modify_strategy": True,
                "does_not_modify_memory": True,
                "recommendations_deferred_to_j9": True,
            },
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

        return result
