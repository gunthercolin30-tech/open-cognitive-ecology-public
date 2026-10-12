
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class OpennessPreservationIndex:
    """
    K7 — Openness Preservation Index.

    Observational primitive measuring remaining openness after the closure
    pressure pipeline K1-K6. It integrates preserved diversity, plasticity,
    bifurcation margin, exploratory margin and future openness into a bounded
    openness_preservation_index.

    It is deliberately distinct from openness_preservation_supervisor: this
    module does not supervise, approve, reject, mutate, regulate or execute.
    It only measures the preservation of future openness and persists evidence
    for later recommendation-only processing in K8.
    """

    primitive = "openness_preservation_index"

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
            "closure_cascade_detector": self.root / "closure_pressure" / "closure_cascade_detector" / "latest_closure_cascade_detector.json",
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

    def _diversity(self, values: Any, default: float = 0.5) -> float:
        items = [str(v) for v in self._as_list(values) if v is not None]
        if not items:
            return self._clamp(default)
        return self._clamp(len(set(items)) / max(1, len(items)))

    def _coverage(self, values: Any, target: int = 4, default: float = 0.5) -> float:
        items = [v for v in self._as_list(values) if v is not None]
        if not items:
            return self._clamp(default)
        return self._clamp(len(set(map(str, items))) / max(1, target))

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
            return "openness_preserved"
        if value >= 0.58:
            return "openness_stable"
        if value >= 0.36:
            return "openness_fragile_watch"
        return "openness_critically_reduced"

    def _trend(self, current: float) -> str:
        if not self.history_path.exists():
            return "insufficient_history"
        try:
            lines = [line for line in self.history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if not lines:
                return "insufficient_history"
            previous = json.loads(lines[-1]).get("openness_preservation_index")
            previous = self._clamp(previous, default=current)
        except Exception:
            return "insufficient_history"
        delta = current - previous
        if delta > 0.05:
            return "improving"
        if delta < -0.05:
            return "declining"
        return "stable"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}

        baseline = self._source(inputs, "closure_pressure_baseline")
        rigidity = self._source(inputs, "rigidity_monitor")
        homogenization = self._source(inputs, "homogenization_monitor")
        exploratory_reduction = self._source(inputs, "exploratory_reduction_monitor")
        closure_pressure = self._source(inputs, "closure_pressure_monitor")
        cascade = self._source(inputs, "closure_cascade_detector")

        diversity_score = self._clamp(
            inputs.get("diversity_score"),
            default=max(
                self._diversity(inputs.get("states"), default=0.5),
                self._diversity(inputs.get("strategies"), default=0.5),
                self._diversity(inputs.get("cognitive_profiles"), default=0.5),
                self._metric(homogenization, ["state_diversity_score", "cognitive_diversity_score"], default=0.5),
                self._metric(baseline, ["trajectory_diversity", "strategic_plurality"], default=0.5),
            ),
        )

        direct_rigidity = inputs.get("rigidity_index", 0.5)
        rigidity_index = self._metric(rigidity, ["rigidity_index", "initial_rigidity"], default=direct_rigidity)
        plasticity_score = self._clamp(
            inputs.get("plasticity_score"),
            default=max(
                1.0 - rigidity_index,
                self._metric(rigidity, ["plasticity_score"], default=0.5),
                self._metric(baseline, ["baseline_non_closure_index"], default=0.5),
            ),
        )

        bifurcation_margin = self._clamp(
            inputs.get("bifurcation_margin"),
            default=max(
                self._coverage(inputs.get("bifurcations"), target=4, default=0.5),
                self._metric(exploratory_reduction, ["bifurcation_score"], default=0.5),
            ),
        )

        exploratory_margin = self._clamp(
            inputs.get("exploratory_margin"),
            default=max(
                self._coverage(inputs.get("explored_options"), target=5, default=0.5),
                self._metric(exploratory_reduction, ["option_exploration_score", "novelty_score", "hypothesis_alternativity_score", "morphospace_coverage_score"], default=0.5),
                self._metric(baseline, ["exploratory_openness", "response_variability"], default=0.5),
            ),
        )

        future_openness_score = self._clamp(
            inputs.get("future_openness_score"),
            default=max(
                self._metric(baseline, ["baseline_non_closure_index"], default=0.5),
                self._metric(closure_pressure, ["openness_preservation_proxy"], default=0.5),
                1.0 - self._metric(closure_pressure, ["closure_pressure_index"], default=0.5),
                1.0 - self._metric(cascade, ["closure_cascade_risk"], default=0.5),
            ),
        )

        closure_pressure_index = self._clamp(
            inputs.get("closure_pressure_index"),
            default=self._metric(closure_pressure, ["closure_pressure_index"], default=0.5),
        )
        closure_cascade_risk = self._clamp(
            inputs.get("closure_cascade_risk"),
            default=self._metric(cascade, ["closure_cascade_risk"], default=0.5),
        )
        closure_penalty = self._clamp((closure_pressure_index + closure_cascade_risk) / 2.0, default=0.5)

        raw_openness = (
            diversity_score
            + plasticity_score
            + bifurcation_margin
            + exploratory_margin
            + future_openness_score
        ) / 5.0

        openness_preservation_index = self._clamp(0.8 * raw_openness + 0.2 * (1.0 - closure_penalty))
        openness_loss_index = self._clamp(1.0 - openness_preservation_index)
        recovery_margin = self._clamp((plasticity_score + exploratory_margin + future_openness_score) / 3.0)
        trend = self._trend(openness_preservation_index)

        result = {
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "success": True,
            "diversity_score": diversity_score,
            "plasticity_score": plasticity_score,
            "bifurcation_margin": bifurcation_margin,
            "exploratory_margin": exploratory_margin,
            "future_openness_score": future_openness_score,
            "closure_pressure_index": closure_pressure_index,
            "closure_cascade_risk": closure_cascade_risk,
            "closure_penalty": closure_penalty,
            "openness_preservation_index": openness_preservation_index,
            "openness_loss_index": openness_loss_index,
            "recovery_margin": recovery_margin,
            "openness_preservation_classification": self._classification(openness_preservation_index),
            "openness_preservation_trend": trend,
            "baseline_integrated": bool(baseline),
            "rigidity_integrated": bool(rigidity) or "rigidity_index" in inputs,
            "homogenization_integrated": bool(homogenization),
            "exploratory_reduction_integrated": bool(exploratory_reduction),
            "closure_pressure_integrated": bool(closure_pressure) or "closure_pressure_index" in inputs,
            "closure_cascade_integrated": bool(cascade) or "closure_cascade_risk" in inputs,
            "observational_only": True,
            "recommendations_only": False,
            "executes_actions": False,
            "modifies_identity": False,
            "modifies_memory": False,
            "modifies_strategy": False,
            "diagnostics": {
                "closure_axis": "K7",
                "measures_remaining_openness": True,
                "aggregates_diversity": True,
                "aggregates_plasticity": True,
                "aggregates_bifurcation_margin": True,
                "aggregates_exploratory_margin": True,
                "aggregates_future_openness": True,
                "ready_for_anti_closure_recommendation_engine": True,
            },
        }

        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, sort_keys=True) + "\n")
