from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ClosurePressureMonitor:
    """
    K5 — Closure Pressure Monitor.

    Observational aggregate primitive for the closure-pressure axis.
    It integrates K2 rigidity, K3 homogenization and K4 exploratory reduction
    into a bounded closure_pressure_index and classification.

    It does not decide, execute, regulate, mutate identity, mutate memory,
    mutate strategy, or apply recommendations. It only measures and persists.
    """

    primitive = "closure_pressure_monitor"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.state_dir = self.root / "closure_pressure" / self.primitive
        self.latest_path = self.state_dir / f"latest_{self.primitive}.json"
        self.history_path = self.state_dir / f"{self.primitive}_history.jsonl"
        self.upstream_paths = {
            "closure_pressure_baseline": self.root / "closure_pressure" / "closure_pressure_baseline" / "latest_closure_pressure_baseline.json",
            "rigidity_monitor": self.root / "closure_pressure" / "rigidity_monitor" / "latest_rigidity_monitor.json",
            "homogenization_monitor": self.root / "closure_pressure" / "homogenization_monitor" / "latest_homogenization_monitor.json",
            "exploratory_reduction_monitor": self.root / "closure_pressure" / "exploratory_reduction_monitor" / "latest_exploratory_reduction_monitor.json",
        }

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if math.isnan(number) or math.isinf(number):
            number = default
        return max(0.0, min(1.0, number))

    def _load_latest(self, key: str) -> dict[str, Any]:
        path = self.upstream_paths.get(key)
        if path is None or not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def _source(self, inputs: dict[str, Any], key: str) -> dict[str, Any]:
        sources = inputs.get("sources", {})
        if isinstance(sources, dict) and isinstance(sources.get(key), dict):
            return sources[key]
        if isinstance(inputs.get(key), dict):
            return inputs[key]
        return self._load_latest(key)

    def _metric(self, data: dict[str, Any], keys: list[str], default: float = 0.5) -> float:
        if not isinstance(data, dict):
            return self._clamp(default)
        for key in keys:
            if key in data:
                return self._clamp(data[key], default=default)
        return self._clamp(default)

    def _classification(self, value: float) -> str:
        if value >= 0.78:
            return "critical_closure_pressure"
        if value >= 0.58:
            return "high_closure_pressure_watch"
        if value >= 0.36:
            return "moderate_closure_pressure_signal"
        return "closure_pressure_low"

    def _trend(self, current: float) -> str:
        if not self.history_path.exists():
            return "insufficient_history"
        try:
            lines = [line for line in self.history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if not lines:
                return "insufficient_history"
            previous = json.loads(lines[-1]).get("closure_pressure_index")
            previous = self._clamp(previous, default=current)
        except Exception:
            return "insufficient_history"
        delta = current - previous
        if delta > 0.05:
            return "increasing"
        if delta < -0.05:
            return "decreasing"
        return "stable"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}

        baseline = self._source(inputs, "closure_pressure_baseline")
        rigidity = self._source(inputs, "rigidity_monitor")
        homogenization = self._source(inputs, "homogenization_monitor")
        exploratory_reduction = self._source(inputs, "exploratory_reduction_monitor")

        rigidity_index = self._clamp(
            inputs.get("rigidity_index"),
            default=self._metric(rigidity, ["rigidity_index", "initial_rigidity"], default=0.5),
        )
        homogenization_index = self._clamp(
            inputs.get("homogenization_index"),
            default=self._metric(homogenization, ["homogenization_index", "state_uniformity_score"], default=0.5),
        )
        exploratory_reduction_index = self._clamp(
            inputs.get("exploratory_reduction_index"),
            default=self._metric(exploratory_reduction, ["exploratory_reduction_index", "option_reduction_score"], default=0.5),
        )

        baseline_pressure = self._metric(
            baseline,
            ["initial_closure_pressure", "closure_pressure_index"],
            default=0.5,
        )
        baseline_non_closure = self._metric(
            baseline,
            ["baseline_non_closure_index", "trajectory_diversity", "strategic_plurality"],
            default=1.0 - baseline_pressure,
        )

        weights = inputs.get("weights", {})
        if not isinstance(weights, dict):
            weights = {}
        rigidity_weight = max(0.0, float(weights.get("rigidity", 1.0)))
        homogenization_weight = max(0.0, float(weights.get("homogenization", 1.0)))
        exploration_weight = max(0.0, float(weights.get("exploratory_reduction", 1.0)))
        baseline_weight = max(0.0, float(weights.get("baseline", 0.25)))
        total_weight = rigidity_weight + homogenization_weight + exploration_weight + baseline_weight
        if total_weight <= 0.0:
            rigidity_weight = homogenization_weight = exploration_weight = 1.0
            baseline_weight = 0.25
            total_weight = 3.25

        raw_index = (
            rigidity_index * rigidity_weight
            + homogenization_index * homogenization_weight
            + exploratory_reduction_index * exploration_weight
            + baseline_pressure * baseline_weight
        ) / total_weight

        coupling_amplification = self._clamp(
            (rigidity_index * homogenization_index + homogenization_index * exploratory_reduction_index + rigidity_index * exploratory_reduction_index) / 3.0,
            default=0.0,
        )
        closure_pressure_index = self._clamp(0.85 * raw_index + 0.15 * coupling_amplification)
        openness_preservation_proxy = self._clamp(1.0 - closure_pressure_index)
        trend = self._trend(closure_pressure_index)

        result = {
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "success": True,
            "rigidity_index": rigidity_index,
            "homogenization_index": homogenization_index,
            "exploratory_reduction_index": exploratory_reduction_index,
            "baseline_closure_pressure": baseline_pressure,
            "baseline_non_closure_index": baseline_non_closure,
            "coupling_amplification": coupling_amplification,
            "closure_pressure_index": closure_pressure_index,
            "openness_preservation_proxy": openness_preservation_proxy,
            "closure_pressure_classification": self._classification(closure_pressure_index),
            "closure_pressure_trend": trend,
            "baseline_integrated": bool(baseline),
            "rigidity_integrated": bool(rigidity) or "rigidity_index" in inputs,
            "homogenization_integrated": bool(homogenization) or "homogenization_index" in inputs,
            "exploratory_reduction_integrated": bool(exploratory_reduction) or "exploratory_reduction_index" in inputs,
            "observational_only": True,
            "recommendations_only": False,
            "executes_actions": False,
            "modifies_identity": False,
            "modifies_memory": False,
            "modifies_strategy": False,
            "diagnostics": {
                "closure_axis": "K5",
                "aggregates_rigidity": True,
                "aggregates_homogenization": True,
                "aggregates_exploratory_reduction": True,
                "ready_for_closure_cascade_detector": True,
                "weighting": {
                    "rigidity": rigidity_weight,
                    "homogenization": homogenization_weight,
                    "exploratory_reduction": exploration_weight,
                    "baseline": baseline_weight,
                },
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
