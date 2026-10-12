from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ClosureCascadeDetector:
    """
    K6 — Closure Cascade Detector.

    Observational primitive detecting temporal and structural cascades of
    closure pressure across K2 rigidity, K3 homogenization, K4 exploratory
    reduction and K5 aggregate closure pressure.

    It is deliberately distinct from drift_cascade_detector: this module does
    not monitor identity, memory or strategic drift. It only detects closure
    cascades such as rigidity -> homogenization -> exploratory reduction ->
    closure pressure.

    It does not decide, execute, regulate, mutate identity, mutate memory,
    mutate strategy, or apply recommendations. It only measures and persists.
    """

    primitive = "closure_cascade_detector"

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
            "closure_pressure_monitor": self.root / "closure_pressure" / "closure_pressure_monitor" / "latest_closure_pressure_monitor.json",
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

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

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

    def _history_values(self, history: list[dict[str, Any]], key: str) -> list[float]:
        values: list[float] = []
        for item in history:
            if isinstance(item, dict) and key in item:
                values.append(self._clamp(item.get(key), default=0.5))
        return values

    def _trend_score(self, values: list[float]) -> float:
        """Return 0.0 stable/decreasing to 1.0 strong increasing trend."""
        if len(values) < 2:
            return 0.5
        first = values[0]
        last = values[-1]
        span = max(1, len(values) - 1)
        slope = (last - first) / span
        positive_steps = 0
        comparisons = 0
        for before, after in zip(values, values[1:]):
            comparisons += 1
            if after >= before:
                positive_steps += 1
        monotonicity = positive_steps / comparisons if comparisons else 0.5
        return self._clamp(0.5 + slope * 2.0 + (monotonicity - 0.5) * 0.5, default=0.5)

    def _coupling_score(
        self,
        rigidity_index: float,
        homogenization_index: float,
        exploratory_reduction_index: float,
        closure_pressure_index: float,
    ) -> float:
        pairwise = (
            rigidity_index * homogenization_index
            + homogenization_index * exploratory_reduction_index
            + exploratory_reduction_index * closure_pressure_index
            + rigidity_index * closure_pressure_index
        ) / 4.0
        sequential_minimum = min(
            rigidity_index,
            homogenization_index,
            exploratory_reduction_index,
            closure_pressure_index,
        )
        return self._clamp(0.7 * pairwise + 0.3 * sequential_minimum)

    def _order_score(
        self,
        rigidity_values: list[float],
        homogenization_values: list[float],
        exploratory_values: list[float],
        closure_values: list[float],
    ) -> float:
        """Estimate whether rigidity precedes homogenization precedes exploratory reduction precedes closure."""
        lengths = [len(rigidity_values), len(homogenization_values), len(exploratory_values), len(closure_values)]
        if min(lengths) < 2:
            return 0.5
        n = min(lengths)
        rv = rigidity_values[-n:]
        hv = homogenization_values[-n:]
        ev = exploratory_values[-n:]
        cv = closure_values[-n:]
        score = 0.0
        comparisons = 0
        for idx in range(1, n):
            dr = rv[idx] - rv[idx - 1]
            dh = hv[idx] - hv[idx - 1]
            de = ev[idx] - ev[idx - 1]
            dc = cv[idx] - cv[idx - 1]
            comparisons += 3
            if dr >= 0.0 and dh >= 0.0 and dh <= dr + 0.25:
                score += 1.0
            if dh >= 0.0 and de >= 0.0 and de <= dh + 0.25:
                score += 1.0
            if de >= 0.0 and dc >= 0.0 and dc <= de + 0.25:
                score += 1.0
        return self._clamp(score / comparisons if comparisons else 0.5, default=0.5)

    def _classification(self, risk: float) -> str:
        if risk >= 0.78:
            return "critical_closure_cascade"
        if risk >= 0.58:
            return "high_closure_cascade_watch"
        if risk >= 0.36:
            return "moderate_closure_cascade_signal"
        return "closure_cascade_low"

    def _cascade_type(
        self,
        rigidity_index: float,
        homogenization_index: float,
        exploratory_reduction_index: float,
        closure_pressure_index: float,
    ) -> str:
        values = {
            "rigidity": rigidity_index,
            "homogenization": homogenization_index,
            "exploratory_reduction": exploratory_reduction_index,
            "closure_pressure": closure_pressure_index,
        }
        high = {key for key, value in values.items() if value >= 0.58}
        if {"rigidity", "homogenization", "exploratory_reduction", "closure_pressure"}.issubset(high):
            return "full_closure_cascade"
        if {"rigidity", "homogenization", "exploratory_reduction"}.issubset(high):
            return "rigidity_homogenization_exploration_cascade"
        if {"exploratory_reduction", "homogenization", "closure_pressure"}.issubset(high):
            return "exploration_loss_homogenization_closure_cascade"
        if {"rigidity", "closure_pressure"}.issubset(high):
            return "rigidity_driven_closure_cascade"
        if {"homogenization", "closure_pressure"}.issubset(high):
            return "homogenization_driven_closure_cascade"
        if {"exploratory_reduction", "closure_pressure"}.issubset(high):
            return "exploratory_reduction_driven_closure_cascade"
        return "no_dominant_closure_cascade"

    def _cascade_stage(self, risk: float, cascade_type: str) -> str:
        if risk >= 0.78:
            return "critical_propagation"
        if risk >= 0.58:
            return "active_propagation"
        if risk >= 0.36:
            return "early_coupling"
        if cascade_type != "no_dominant_closure_cascade":
            return "latent_coupling"
        return "no_cascade_detected"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}

        baseline = self._source(inputs, "closure_pressure_baseline")
        rigidity = self._source(inputs, "rigidity_monitor")
        homogenization = self._source(inputs, "homogenization_monitor")
        exploratory_reduction = self._source(inputs, "exploratory_reduction_monitor")
        closure_pressure = self._source(inputs, "closure_pressure_monitor")

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
        closure_pressure_index = self._clamp(
            inputs.get("closure_pressure_index"),
            default=self._metric(closure_pressure, ["closure_pressure_index", "baseline_closure_pressure"], default=0.5),
        )

        history = self._as_list(inputs.get("history"))
        if not history:
            sequence = self._as_list(inputs.get("sequence"))
            history = [item for item in sequence if isinstance(item, dict)]

        rigidity_values = self._history_values(history, "rigidity_index") or [rigidity_index]
        homogenization_values = self._history_values(history, "homogenization_index") or [homogenization_index]
        exploratory_values = self._history_values(history, "exploratory_reduction_index") or [exploratory_reduction_index]
        closure_values = self._history_values(history, "closure_pressure_index") or [closure_pressure_index]

        current_coupling = self._coupling_score(
            rigidity_index,
            homogenization_index,
            exploratory_reduction_index,
            closure_pressure_index,
        )
        trend_alignment = self._clamp(
            (
                self._trend_score(rigidity_values)
                + self._trend_score(homogenization_values)
                + self._trend_score(exploratory_values)
                + self._trend_score(closure_values)
            ) / 4.0,
            default=0.5,
        )
        sequential_order_score = self._order_score(
            rigidity_values,
            homogenization_values,
            exploratory_values,
            closure_values,
        )
        direct_pressure = self._clamp(
            (rigidity_index + homogenization_index + exploratory_reduction_index + closure_pressure_index) / 4.0,
            default=0.5,
        )

        closure_cascade_risk = self._clamp(
            0.40 * current_coupling
            + 0.25 * direct_pressure
            + 0.20 * trend_alignment
            + 0.15 * sequential_order_score,
            default=0.5,
        )
        cascade_type = self._cascade_type(
            rigidity_index,
            homogenization_index,
            exploratory_reduction_index,
            closure_pressure_index,
        )
        cascade_stage = self._cascade_stage(closure_cascade_risk, cascade_type)
        cascade_confidence = self._clamp(
            0.5 * current_coupling + 0.25 * trend_alignment + 0.25 * sequential_order_score,
            default=0.5,
        )
        openness_preservation_warning = closure_cascade_risk >= 0.58

        result = {
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "success": True,
            "rigidity_index": rigidity_index,
            "homogenization_index": homogenization_index,
            "exploratory_reduction_index": exploratory_reduction_index,
            "closure_pressure_index": closure_pressure_index,
            "direct_pressure_score": direct_pressure,
            "current_coupling_score": current_coupling,
            "trend_alignment_score": trend_alignment,
            "sequential_order_score": sequential_order_score,
            "closure_cascade_risk": closure_cascade_risk,
            "cascade_type": cascade_type,
            "cascade_stage": cascade_stage,
            "cascade_confidence": cascade_confidence,
            "closure_cascade_classification": self._classification(closure_cascade_risk),
            "openness_preservation_warning": openness_preservation_warning,
            "history_points_observed": max(
                len(rigidity_values),
                len(homogenization_values),
                len(exploratory_values),
                len(closure_values),
            ),
            "baseline_integrated": bool(baseline),
            "rigidity_integrated": bool(rigidity) or "rigidity_index" in inputs,
            "homogenization_integrated": bool(homogenization) or "homogenization_index" in inputs,
            "exploratory_reduction_integrated": bool(exploratory_reduction) or "exploratory_reduction_index" in inputs,
            "closure_pressure_integrated": bool(closure_pressure) or "closure_pressure_index" in inputs,
            "observational_only": True,
            "recommendations_only": False,
            "executes_actions": False,
            "modifies_identity": False,
            "modifies_memory": False,
            "modifies_strategy": False,
            "diagnostics": {
                "closure_axis": "K6",
                "distinction_from_drift_cascade_detector": "closure_pressure_only_not_identity_memory_strategy_drift",
                "detects_rigidity_to_homogenization_to_exploration_loss": True,
                "detects_exploration_loss_to_homogenization_to_closure": True,
                "ready_for_openness_preservation_index": True,
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
