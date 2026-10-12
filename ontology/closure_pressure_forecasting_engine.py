from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


class ClosurePressureForecastingEngine:
    """
    K9 — Closure Pressure Forecasting Engine.

    Specialized observational forecaster for closure-pressure dynamics. It
    transforms K5-K8 histories into projected closure pressure, openness loss,
    critical closure horizon and trajectory classification. It does not execute
    recommendations, does not regulate the runtime, does not authorize mutation,
    and does not modify identity, memory or strategy.
    """

    primitive = "closure_pressure_forecasting_engine"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.state_dir = self.root / "closure_pressure" / self.primitive
        self.latest_path = self.state_dir / f"latest_{self.primitive}.json"
        self.history_path = self.state_dir / f"{self.primitive}_history.jsonl"
        self.upstream_paths = {
            "closure_pressure_monitor": self.root / "closure_pressure" / "closure_pressure_monitor" / "latest_closure_pressure_monitor.json",
            "closure_cascade_detector": self.root / "closure_pressure" / "closure_cascade_detector" / "latest_closure_cascade_detector.json",
            "openness_preservation_index": self.root / "closure_pressure" / "openness_preservation_index" / "latest_openness_preservation_index.json",
            "anti_closure_recommendation_engine": self.root / "closure_pressure" / "anti_closure_recommendation_engine" / "latest_anti_closure_recommendation_engine.json",
        }
        self.history_paths = {
            "closure_pressure_monitor": self.root / "closure_pressure" / "closure_pressure_monitor" / "closure_pressure_monitor_history.jsonl",
            "closure_cascade_detector": self.root / "closure_pressure" / "closure_cascade_detector" / "closure_cascade_detector_history.jsonl",
            "openness_preservation_index": self.root / "closure_pressure" / "openness_preservation_index" / "openness_preservation_index_history.jsonl",
            "anti_closure_recommendation_engine": self.root / "closure_pressure" / "anti_closure_recommendation_engine" / "anti_closure_recommendation_engine_history.jsonl",
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

    @staticmethod
    def _safe_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _load_json(self, path: Path) -> dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _read_jsonl(self, path: Path, limit: int = 48) -> list[dict[str, Any]]:
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

    def _history(self, inputs: dict[str, Any], key: str) -> list[dict[str, Any]]:
        history = inputs.get("history", {})
        if isinstance(history, dict) and isinstance(history.get(key), list):
            return [row for row in history[key] if isinstance(row, dict)]
        if isinstance(inputs.get(f"{key}_history"), list):
            return [row for row in inputs[f"{key}_history"] if isinstance(row, dict)]
        return self._read_jsonl(self.history_paths[key])

    @classmethod
    def _extract_series(cls, rows: Iterable[Mapping[str, Any]], keys: list[str]) -> list[float]:
        series: list[float] = []
        for row in rows:
            for key in keys:
                if key in row:
                    series.append(cls._clamp(row.get(key)))
                    break
        return series

    @staticmethod
    def _linear_slope(series: list[float]) -> float:
        n = len(series)
        if n < 2:
            return 0.0
        xs = list(range(n))
        mx = sum(xs) / n
        my = sum(series) / n
        den = sum((x - mx) ** 2 for x in xs)
        if den == 0:
            return 0.0
        return sum((x - mx) * (y - my) for x, y in zip(xs, series)) / den

    def _forecast(self, current: float, slope: float, horizon: int) -> list[float]:
        return [self._clamp(current + slope * step) for step in range(1, horizon + 1)]

    def _closure_horizon(self, trajectory: list[float], threshold: float) -> Any:
        for step, value in enumerate(trajectory, start=1):
            if value >= threshold:
                return step
        return "beyond_forecast_horizon"

    @staticmethod
    def _trajectory_classification(predicted_pressure: float, predicted_loss: float, horizon_estimate: Any) -> str:
        if isinstance(horizon_estimate, int) and horizon_estimate <= 2:
            return "critical_closure_trajectory"
        if predicted_pressure >= 0.78 or predicted_loss >= 0.72:
            return "accelerating_closure_trajectory"
        if predicted_pressure >= 0.58 or predicted_loss >= 0.52:
            return "elevated_closure_watch"
        if predicted_pressure <= 0.32 and predicted_loss <= 0.28:
            return "open_trajectory_stable"
        return "moderate_closure_signal"

    def step(
        self,
        inputs: dict[str, Any] | None = None,
        forecast_horizon_steps: int = 6,
        critical_closure_threshold: float = 0.82,
        persist: bool = True,
    ) -> dict[str, Any]:
        inputs = inputs or {}
        horizon = max(1, min(36, int(forecast_horizon_steps or 6)))
        critical_threshold = self._clamp(critical_closure_threshold, default=0.82)

        pressure = self._source(inputs, "closure_pressure_monitor")
        cascade = self._source(inputs, "closure_cascade_detector")
        openness = self._source(inputs, "openness_preservation_index")
        recommendation = self._source(inputs, "anti_closure_recommendation_engine")

        closure_pressure_index = self._clamp(
            inputs.get("closure_pressure_index"),
            default=self._clamp(pressure.get("closure_pressure_index"), default=0.5),
        )
        closure_cascade_risk = self._clamp(
            inputs.get("closure_cascade_risk"),
            default=self._clamp(cascade.get("closure_cascade_risk"), default=0.5),
        )
        openness_preservation_index = self._clamp(
            inputs.get("openness_preservation_index"),
            default=self._clamp(openness.get("openness_preservation_index"), default=1.0 - closure_pressure_index),
        )
        openness_loss_index = self._clamp(
            inputs.get("openness_loss_index"),
            default=self._clamp(openness.get("openness_loss_index"), default=1.0 - openness_preservation_index),
        )
        rigidity_index = self._clamp(
            inputs.get("rigidity_index"),
            default=self._clamp(pressure.get("rigidity_index"), default=0.5),
        )
        homogenization_index = self._clamp(
            inputs.get("homogenization_index"),
            default=self._clamp(pressure.get("homogenization_index"), default=0.5),
        )
        exploratory_reduction_index = self._clamp(
            inputs.get("exploratory_reduction_index"),
            default=self._clamp(pressure.get("exploratory_reduction_index"), default=0.5),
        )
        anti_closure_recommendation_priority = self._clamp(
            inputs.get("recommendation_priority_score"),
            default=self._clamp(recommendation.get("recommendation_priority_score"), default=0.0),
        )
        expected_openness_gain = self._clamp(
            inputs.get("expected_openness_gain"),
            default=self._clamp(recommendation.get("expected_openness_gain"), default=0.0),
        )

        pressure_history = self._history(inputs, "closure_pressure_monitor")
        cascade_history = self._history(inputs, "closure_cascade_detector")
        openness_history = self._history(inputs, "openness_preservation_index")
        recommendation_history = self._history(inputs, "anti_closure_recommendation_engine")

        closure_series = self._extract_series(pressure_history, ["closure_pressure_index"])
        cascade_series = self._extract_series(cascade_history, ["closure_cascade_risk"])
        openness_loss_series = self._extract_series(openness_history, ["openness_loss_index"])
        openness_preservation_series = self._extract_series(openness_history, ["openness_preservation_index"])
        recommendation_series = self._extract_series(recommendation_history, ["expected_openness_gain", "recommendation_priority_score"])
        rigidity_series = self._extract_series(pressure_history, ["rigidity_index"])
        homogenization_series = self._extract_series(pressure_history, ["homogenization_index"])
        exploratory_series = self._extract_series(pressure_history, ["exploratory_reduction_index"])

        closure_slope = self._linear_slope(closure_series) if closure_series else 0.0
        cascade_slope = self._linear_slope(cascade_series) if cascade_series else 0.0
        openness_loss_slope = self._linear_slope(openness_loss_series) if openness_loss_series else 0.0
        openness_preservation_slope = self._linear_slope(openness_preservation_series) if openness_preservation_series else 0.0
        rigidity_slope = self._linear_slope(rigidity_series) if rigidity_series else 0.0
        homogenization_slope = self._linear_slope(homogenization_series) if homogenization_series else 0.0
        exploratory_slope = self._linear_slope(exploratory_series) if exploratory_series else 0.0
        recommendation_slope = self._linear_slope(recommendation_series) if recommendation_series else 0.0

        adverse_slope = (
            max(0.0, closure_slope) * 0.30
            + max(0.0, cascade_slope) * 0.20
            + max(0.0, openness_loss_slope) * 0.20
            + max(0.0, -openness_preservation_slope) * 0.15
            + max(0.0, rigidity_slope) * 0.05
            + max(0.0, homogenization_slope) * 0.05
            + max(0.0, exploratory_slope) * 0.05
        )
        mitigation_signal = self._clamp(expected_openness_gain * 0.20 + anti_closure_recommendation_priority * 0.10 + max(0.0, recommendation_slope) * 0.05)
        net_pressure_slope = max(-0.20, min(0.20, adverse_slope - mitigation_signal * 0.25))

        current_combined_pressure = self._clamp(
            closure_pressure_index * 0.42
            + closure_cascade_risk * 0.23
            + openness_loss_index * 0.18
            + exploratory_reduction_index * 0.07
            + rigidity_index * 0.05
            + homogenization_index * 0.05
        )

        pressure_trajectory = self._forecast(current_combined_pressure, net_pressure_slope, horizon)
        openness_loss_trajectory = self._forecast(openness_loss_index, max(0.0, openness_loss_slope) + max(0.0, net_pressure_slope) * 0.35, horizon)
        openness_preservation_trajectory = [self._clamp(1.0 - loss - pressure * 0.12) for loss, pressure in zip(openness_loss_trajectory, pressure_trajectory)]
        cascade_trajectory = self._forecast(closure_cascade_risk, max(0.0, cascade_slope) + max(0.0, net_pressure_slope) * 0.20, horizon)

        predicted_closure_pressure = pressure_trajectory[-1]
        predicted_openness_loss = openness_loss_trajectory[-1]
        predicted_openness_preservation = openness_preservation_trajectory[-1]
        closure_horizon_estimate = self._closure_horizon(pressure_trajectory, threshold=critical_threshold)
        closure_trajectory_classification = self._trajectory_classification(
            predicted_closure_pressure,
            predicted_openness_loss,
            closure_horizon_estimate,
        )
        evidence_points = len(closure_series) + len(cascade_series) + len(openness_loss_series) + len(openness_preservation_series)
        historical_samples_used = {
            "closure_pressure": len(closure_series),
            "closure_cascade": len(cascade_series),
            "openness_loss": len(openness_loss_series),
            "openness_preservation": len(openness_preservation_series),
            "anti_closure_recommendation": len(recommendation_series),
        }
        forecast_confidence = self._clamp(0.25 + 0.55 * min(1.0, evidence_points / 18.0) + 0.20 * (1.0 - abs(net_pressure_slope)))

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": self._now(),
            "success": True,
            "forecast_engine_ready": True,
            "observational_only": True,
            "recommendations_only": False,
            "executes_actions": False,
            "modifies_identity": False,
            "modifies_memory": False,
            "modifies_strategy": False,
            "forecast_horizon_steps": horizon,
            "critical_closure_threshold": round(critical_threshold, 6),
            "current_closure_pressure": round(current_combined_pressure, 6),
            "current_observed_closure_pressure_index": round(closure_pressure_index, 6),
            "current_closure_cascade_risk": round(closure_cascade_risk, 6),
            "current_openness_preservation_index": round(openness_preservation_index, 6),
            "current_openness_loss_index": round(openness_loss_index, 6),
            "predicted_closure_pressure": round(predicted_closure_pressure, 6),
            "closure_horizon_estimate": closure_horizon_estimate,
            "predicted_openness_loss": round(predicted_openness_loss, 6),
            "predicted_openness_preservation": round(predicted_openness_preservation, 6),
            "closure_trajectory_classification": closure_trajectory_classification,
            "forecast_confidence": round(forecast_confidence, 6),
            "historical_samples_used": historical_samples_used,
            "closure_pressure_trajectory": [round(x, 6) for x in pressure_trajectory],
            "closure_cascade_trajectory": [round(x, 6) for x in cascade_trajectory],
            "openness_loss_trajectory": [round(x, 6) for x in openness_loss_trajectory],
            "openness_preservation_trajectory": [round(x, 6) for x in openness_preservation_trajectory],
            "forecast_slopes": {
                "closure_pressure_slope": round(closure_slope, 6),
                "closure_cascade_slope": round(cascade_slope, 6),
                "openness_loss_slope": round(openness_loss_slope, 6),
                "openness_preservation_slope": round(openness_preservation_slope, 6),
                "rigidity_slope": round(rigidity_slope, 6),
                "homogenization_slope": round(homogenization_slope, 6),
                "exploratory_reduction_slope": round(exploratory_slope, 6),
                "net_pressure_slope": round(net_pressure_slope, 6),
            },
            "forecast_inputs": {
                "rigidity_index": round(rigidity_index, 6),
                "homogenization_index": round(homogenization_index, 6),
                "exploratory_reduction_index": round(exploratory_reduction_index, 6),
                "anti_closure_recommendation_priority": round(anti_closure_recommendation_priority, 6),
                "expected_openness_gain": round(expected_openness_gain, 6),
            },
            "governance": {
                "observational_only": True,
                "does_not_execute_actions": True,
                "does_not_authorize_mutation": True,
                "does_not_modify_identity": True,
                "does_not_modify_memory": True,
                "does_not_modify_strategy": True,
                "recommendations_deferred_to_k8": True,
                "dashboard_deferred_to_k10": True,
            },
            "diagnostics": {
                "closure_axis": "K9",
                "integrates_closure_pressure_monitor": bool(pressure) or "closure_pressure_index" in inputs,
                "integrates_closure_cascade_detector": bool(cascade) or "closure_cascade_risk" in inputs,
                "integrates_openness_preservation_index": bool(openness) or "openness_preservation_index" in inputs,
                "integrates_anti_closure_recommendation_engine": bool(recommendation) or "expected_openness_gain" in inputs,
                "ready_for_longitudinal_closure_pressure_dashboard": True,
            },
        }

        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n")
