
"""
Rigidity Monitor.

K2 of the closure-pressure axis measures functional rigidification:
repetition of the same choices, decline of plasticity, reduction of
available alternatives, and over-stabilization of attractors.

The primitive is observational only. It produces metrics and persisted
records but never modifies identity, memory, strategy, governance, or
runtime configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping, Sequence
import json

PRIMITIVE = "rigidity_monitor"

DEPENDENCIES = [
    "closure_pressure_baseline",
    "choice",
    "decision_making",
    "autonomous_decision_engine",
    "trajectory_decision_policy",
    "trajectory_strategy_selection",
    "trajectory_action_selection",
    "phenotypic_plasticity",
    "constitutional_plasticity",
    "adaptive_capacity",
    "adaptive_landscape",
    "attractor_basin",
    "attractor_persistence_analyzer",
    "attractor_density_balancer",
    "attractor_desaturation",
    "exploration_exploitation_balance",
    "novelty_emergence",
    "open_endedness",
    "future_openness",
    "metrics_history_recorder",
    "longitudinal_metrics_archive",
]

ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "closure_pressure" / "rigidity_monitor"
LATEST_PATH = STATE_DIR / "latest_rigidity_monitor.json"
HISTORY_PATH = STATE_DIR / "rigidity_monitor_history.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if number != number:
        number = default
    return max(0.0, min(1.0, number))


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, (str, bytes)):
        return []
    if isinstance(value, Sequence):
        return value
    return []


def _mean(values: Iterable[float], default: float = 0.0) -> float:
    clean = [_clamp(v, default) for v in values]
    return mean(clean) if clean else default


def _unique_ratio(values: Sequence[Any]) -> float:
    if not values:
        return 0.0
    normalized = [json.dumps(v, sort_keys=True, default=str) for v in values]
    return _clamp(len(set(normalized)) / len(normalized))


def _repetition_rate(values: Sequence[Any]) -> float:
    if not values:
        return 0.0
    return _clamp(1.0 - _unique_ratio(values))


def _metric(source: Mapping[str, Any], names: Sequence[str], default: float = 0.0) -> float:
    for name in names:
        if name in source:
            return _clamp(source.get(name), default)
    diagnostics = source.get("diagnostics")
    if isinstance(diagnostics, Mapping):
        for name in names:
            if name in diagnostics:
                return _clamp(diagnostics.get(name), default)
    return _clamp(default)


@dataclass(frozen=True)
class RigidityWeights:
    choice_repetition: float = 0.26
    inverse_decision_diversity: float = 0.22
    inverse_plasticity: float = 0.22
    inverse_alternative_generation: float = 0.15
    attractor_over_stabilization: float = 0.15

    def normalized(self) -> dict[str, float]:
        raw = {
            "choice_repetition": self.choice_repetition,
            "inverse_decision_diversity": self.inverse_decision_diversity,
            "inverse_plasticity": self.inverse_plasticity,
            "inverse_alternative_generation": self.inverse_alternative_generation,
            "attractor_over_stabilization": self.attractor_over_stabilization,
        }
        total = sum(max(0.0, float(v)) for v in raw.values()) or 1.0
        return {k: max(0.0, float(v)) / total for k, v in raw.items()}


class RigidityMonitor:
    """Measures K2 rigidification without executing any corrective action."""

    primitive = PRIMITIVE

    def __init__(self, state_dir: Path | None = None, weights: RigidityWeights | None = None) -> None:
        self.state_dir = state_dir or STATE_DIR
        self.latest_path = self.state_dir / "latest_rigidity_monitor.json"
        self.history_path = self.state_dir / "rigidity_monitor_history.jsonl"
        self.weights = weights or RigidityWeights()

    def _extract_sources(self, inputs: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
        sources = inputs.get("sources")
        if isinstance(sources, Mapping):
            return {str(k): _as_mapping(v) for k, v in sources.items()}
        return {str(k): _as_mapping(v) for k, v in inputs.items() if isinstance(v, Mapping)}

    def _choice_repetition_rate(self, inputs: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]) -> float:
        choices = _as_sequence(inputs.get("choices") or inputs.get("choice_history") or inputs.get("decisions"))
        explicit = _metric(inputs, ["choice_repetition_rate", "repetition_rate"], 0.0)
        source_choice = _metric(sources.get("choice", {}), ["choice_repetition_rate", "repetition_rate", "commitment_index"], 0.0)
        return _mean([v for v in [_repetition_rate(choices), explicit, source_choice] if v > 0.0], default=0.0)

    def _decision_diversity_score(self, inputs: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]) -> float:
        decisions = _as_sequence(inputs.get("decisions") or inputs.get("decision_history") or inputs.get("choices"))
        strategies = _as_sequence(inputs.get("strategies") or inputs.get("strategy_samples"))
        candidates = [
            _unique_ratio(decisions),
            _unique_ratio(strategies),
            _metric(inputs, ["decision_diversity_score", "decision_diversity", "strategy_diversity"], 0.0),
            _metric(sources.get("closure_pressure_baseline", {}), ["strategic_plurality", "trajectory_diversity"], 0.0),
            _metric(sources.get("trajectory_strategy_selection", {}), ["strategy_diversity", "selection_diversity"], 0.0),
        ]
        return _mean([v for v in candidates if v > 0.0], default=0.5)

    def _plasticity_score(self, inputs: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]) -> float:
        candidates = [
            _metric(inputs, ["plasticity_score", "plasticity", "adaptive_plasticity"], 0.0),
            _metric(sources.get("phenotypic_plasticity", {}), ["phenotypic_plasticity_index", "plasticity_index", "adaptive_range"], 0.0),
            _metric(sources.get("constitutional_plasticity", {}), ["constitutional_plasticity_index", "plasticity_index"], 0.0),
            _metric(sources.get("adaptive_capacity", {}), ["adaptive_capacity_index", "reconfiguration_flexibility", "learning_capacity"], 0.0),
            _metric(sources.get("adaptive_landscape", {}), ["adaptive_potential", "navigation_complexity"], 0.0),
            _metric(sources.get("future_openness", {}), ["future_openness_index"], 0.0),
        ]
        return _mean([v for v in candidates if v > 0.0], default=0.5)

    def _alternative_generation_score(self, inputs: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]) -> float:
        alternatives = _as_sequence(inputs.get("alternatives") or inputs.get("options") or inputs.get("alternative_options"))
        candidate_count_score = _clamp(len(alternatives) / 5.0) if alternatives else 0.0
        candidates = [
            candidate_count_score,
            _metric(inputs, ["alternative_generation_score", "alternative_diversity", "option_generation_score"], 0.0),
            _metric(sources.get("exploration_exploitation_balance", {}), ["balance_index", "exploration_exploitation_balance_index", "exploration_score"], 0.0),
            _metric(sources.get("novelty_emergence", {}), ["novelty_emergence_index", "novelty_score"], 0.0),
            _metric(sources.get("open_endedness", {}), ["open_endedness_index", "open_ended_potential"], 0.0),
            _metric(sources.get("closure_pressure_baseline", {}), ["exploratory_openness"], 0.0),
        ]
        return _mean([v for v in candidates if v > 0.0], default=0.5)

    def _attractor_stability_score(self, inputs: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]) -> float:
        candidates = [
            _metric(inputs, ["attractor_stability_score", "attractor_stability", "attractor_persistence"], 0.0),
            _metric(sources.get("attractor_basin", {}), ["basin_stability", "attractor_basin_strength", "attractor_stability"], 0.0),
            _metric(sources.get("attractor_persistence_analyzer", {}), ["attractor_persistence_index", "persistence_index", "persistence_score"], 0.0),
            _metric(sources.get("attractor_density_balancer", {}), ["attractor_balance_index", "density_balance", "balanced_attractor_density"], 0.0),
            _metric(sources.get("attractor_desaturation", {}), ["desaturation_index", "attractor_desaturation_index"], 0.0),
        ]
        return _mean([v for v in candidates if v > 0.0], default=0.5)

    def _classification(self, rigidity_index: float) -> str:
        if rigidity_index < 0.25:
            return "low_rigidity"
        if rigidity_index < 0.50:
            return "moderate_rigidity"
        if rigidity_index < 0.75:
            return "high_rigidity_watch"
        return "critical_rigidity_pressure"

    def _persist(self, result: Mapping[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(result, sort_keys=True) + "\n")

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        data = _as_mapping(inputs)
        sources = self._extract_sources(data)

        choice_repetition_rate = self._choice_repetition_rate(data, sources)
        decision_diversity_score = self._decision_diversity_score(data, sources)
        plasticity_score = self._plasticity_score(data, sources)
        alternative_generation_score = self._alternative_generation_score(data, sources)
        attractor_stability_score = self._attractor_stability_score(data, sources)

        weights = self.weights.normalized()
        attractor_over_stabilization = attractor_stability_score * (1.0 - alternative_generation_score)
        rigidity_index = _clamp(
            weights["choice_repetition"] * choice_repetition_rate
            + weights["inverse_decision_diversity"] * (1.0 - decision_diversity_score)
            + weights["inverse_plasticity"] * (1.0 - plasticity_score)
            + weights["inverse_alternative_generation"] * (1.0 - alternative_generation_score)
            + weights["attractor_over_stabilization"] * attractor_over_stabilization
        )

        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": _utc_now(),
            "success": True,
            "choice_repetition_rate": choice_repetition_rate,
            "decision_diversity_score": decision_diversity_score,
            "plasticity_score": plasticity_score,
            "alternative_generation_score": alternative_generation_score,
            "attractor_stability_score": attractor_stability_score,
            "attractor_over_stabilization": _clamp(attractor_over_stabilization),
            "rigidity_index": rigidity_index,
            "rigidity_classification": self._classification(rigidity_index),
            "baseline_integrated": "closure_pressure_baseline" in sources or "baseline_non_closure_index" in data,
            "observational_only": True,
            "modifies_identity": False,
            "modifies_memory": False,
            "modifies_strategy": False,
            "executes_recommendations": False,
            "diagnostics": {
                "weights": weights,
                "dependency_count": len(DEPENDENCIES),
                "k_axis_stage": "K2",
                "closure_pressure_role": "rigidity_component_monitor",
            },
        }
        if persist:
            self._persist(result)
        return result
