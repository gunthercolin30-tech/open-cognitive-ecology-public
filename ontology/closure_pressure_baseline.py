
"""
Closure Pressure Baseline.

K1 of the closure-pressure axis establishes a measurable reference state
for non-closure before rigidity, homogenization, exploratory reduction,
and aggregated closure pressure are monitored downstream.

The primitive is observational only. It does not alter identity, memory,
strategy, governance, or runtime configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable, Mapping, Sequence
import json

PRIMITIVE = "closure_pressure_baseline"

DEPENDENCIES = [
    "future_openness",
    "open_endedness",
    "novelty_emergence",
    "exploration_exploitation_balance",
    "distributed_semantic_pluralism",
    "attractor_density_balancer",
    "attractor_desaturation",
    "architectural_non_closure_index",
    "anti_closure_metaconstraint",
    "historical_open_endedness",
    "distributed_open_ended_pluralistic_evolution",
    "metrics_history_recorder",
    "longitudinal_metrics_archive",
]


ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "closure_pressure" / "closure_pressure_baseline"
LATEST_PATH = STATE_DIR / "latest_closure_pressure_baseline.json"
HISTORY_PATH = STATE_DIR / "closure_pressure_baseline_history.jsonl"


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


def _dispersion(values: Iterable[float]) -> float:
    clean = [_clamp(v) for v in values]
    if len(clean) <= 1:
        return 0.0
    return _clamp(pstdev(clean) * 2.0)


def _unique_ratio(values: Sequence[Any]) -> float:
    if not values:
        return 0.0
    normalized = [json.dumps(v, sort_keys=True, default=str) for v in values]
    return _clamp(len(set(normalized)) / len(normalized))


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
class ClosurePressureBaselineWeights:
    trajectory_diversity: float = 0.22
    strategic_plurality: float = 0.20
    exploratory_openness: float = 0.24
    response_variability: float = 0.17
    inverse_rigidity: float = 0.17

    def normalized(self) -> dict[str, float]:
        raw = {
            "trajectory_diversity": self.trajectory_diversity,
            "strategic_plurality": self.strategic_plurality,
            "exploratory_openness": self.exploratory_openness,
            "response_variability": self.response_variability,
            "inverse_rigidity": self.inverse_rigidity,
        }
        total = sum(max(0.0, float(v)) for v in raw.values()) or 1.0
        return {k: max(0.0, float(v)) / total for k, v in raw.items()}


class ClosurePressureBaseline:
    """
    Establishes the K1 non-closure baseline from already available metrics.

    The baseline is intentionally conservative: when no runtime evidence is
    supplied, it uses neutral values instead of optimistic defaults. This makes
    later K2-K10 monitors comparable against an explicit reference point.
    """

    primitive = PRIMITIVE

    def __init__(
        self,
        state_dir: Path | None = None,
        weights: ClosurePressureBaselineWeights | None = None,
    ) -> None:
        self.state_dir = state_dir or STATE_DIR
        self.latest_path = self.state_dir / "latest_closure_pressure_baseline.json"
        self.history_path = self.state_dir / "closure_pressure_baseline_history.jsonl"
        self.weights = weights or ClosurePressureBaselineWeights()

    def _extract_sources(self, inputs: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
        sources = inputs.get("sources")
        if isinstance(sources, Mapping):
            return {str(k): _as_mapping(v) for k, v in sources.items()}
        return {str(k): _as_mapping(v) for k, v in inputs.items() if isinstance(v, Mapping)}

    def _trajectory_diversity(self, inputs: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]) -> float:
        explicit = inputs.get("trajectories") or inputs.get("trajectory_samples")
        samples = _as_sequence(explicit)
        sample_ratio = _unique_ratio(samples)

        candidates = [
            sample_ratio,
            _metric(inputs, ["trajectory_diversity", "trajectory_diversity_score"], 0.0),
            _metric(sources.get("future_openness", {}), ["trajectory_diversity", "future_openness_index"], 0.0),
            _metric(sources.get("historical_open_endedness", {}), ["historical_diversity_index", "historical_open_endedness_index"], 0.0),
            _metric(sources.get("distributed_open_ended_pluralistic_evolution", {}), ["distributed_open_ended_pluralistic_evolution_index"], 0.0),
        ]
        return _mean([v for v in candidates if v > 0.0], default=0.5)

    def _strategic_plurality(self, inputs: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]) -> float:
        strategies = _as_sequence(inputs.get("strategies") or inputs.get("strategy_samples"))
        options = _as_sequence(inputs.get("options") or inputs.get("alternative_options"))
        candidates = [
            _unique_ratio(strategies),
            _unique_ratio(options),
            _metric(inputs, ["strategic_plurality", "strategy_plurality", "plurality_score"], 0.0),
            _metric(sources.get("distributed_semantic_pluralism", {}), ["distributed_semantic_pluralism_index", "distributed_pluralistic_viability"], 0.0),
            _metric(sources.get("attractor_density_balancer", {}), ["distributed_pluralism_capacity", "distributed_topological_ecology"], 0.0),
        ]
        return _mean([v for v in candidates if v > 0.0], default=0.5)

    def _exploratory_openness(self, inputs: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]) -> float:
        candidates = [
            _metric(inputs, ["exploratory_openness", "exploration_score", "openness_score"], 0.0),
            _metric(sources.get("future_openness", {}), ["future_openness_index", "possibility_preservation"], 0.0),
            _metric(sources.get("open_endedness", {}), ["open_endedness_index", "open_ended_potential"], 0.0),
            _metric(sources.get("novelty_emergence", {}), ["novelty_emergence_index", "novelty_score"], 0.0),
            _metric(sources.get("exploration_exploitation_balance", {}), ["balance_index", "exploration_exploitation_balance_index"], 0.0),
            _metric(sources.get("architectural_non_closure_index", {}), ["architectural_non_closure_index"], 0.0),
            _metric(sources.get("openness_preservation_supervisor", {}), ["openness_preservation_score"], 0.0),
        ]
        return _mean([v for v in candidates if v > 0.0], default=0.5)

    def _response_variability(self, inputs: Mapping[str, Any]) -> float:
        responses = _as_sequence(inputs.get("responses") or inputs.get("response_samples"))
        if responses:
            lengths = [len(str(r)) for r in responses]
            lexical_sets = [set(str(r).lower().split()) for r in responses]
            lexical_diversity = _unique_ratio([sorted(s) for s in lexical_sets])
            length_variability = _dispersion([l / max(lengths or [1]) for l in lengths])
            unique_response_ratio = _unique_ratio(responses)
            return _mean([lexical_diversity, length_variability, unique_response_ratio], default=0.0)
        return _metric(inputs, ["response_variability", "response_variability_score"], 0.5)

    def _initial_rigidity(self, inputs: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]) -> float:
        choices = _as_sequence(inputs.get("choices") or inputs.get("decision_samples"))
        repetition_rigidity = 1.0 - _unique_ratio(choices) if choices else 0.0
        attractors = inputs.get("attractor_strengths")
        attractor_values = [_clamp(v) for v in _as_sequence(attractors)]
        attractor_rigidity = max(attractor_values) if attractor_values else 0.0
        candidates = [
            repetition_rigidity,
            attractor_rigidity,
            _metric(inputs, ["initial_rigidity", "rigidity", "rigidity_score"], 0.0),
            _metric(sources.get("attractor_desaturation", {}), ["basin_rigidity", "historical_inertia"], 0.0),
            _metric(sources.get("anti_reconvergence_instrumentation", {}), ["civilizational_reconvergence_risk", "closure_pressure_score"], 0.0),
        ]
        positive = [v for v in candidates if v > 0.0]
        return _mean(positive, default=0.5)

    def classify(self, baseline_non_closure_index: float, initial_closure_pressure: float) -> str:
        if baseline_non_closure_index >= 0.80 and initial_closure_pressure <= 0.30:
            return "open_baseline"
        if baseline_non_closure_index >= 0.65 and initial_closure_pressure <= 0.45:
            return "stable_non_closure_baseline"
        if baseline_non_closure_index >= 0.50 and initial_closure_pressure <= 0.60:
            return "watch_baseline"
        return "closure_pressure_sensitive_baseline"

    def evaluate(self, inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = _as_mapping(inputs)
        sources = self._extract_sources(inputs)
        weights = self.weights.normalized()

        trajectory_diversity = self._trajectory_diversity(inputs, sources)
        strategic_plurality = self._strategic_plurality(inputs, sources)
        exploratory_openness = self._exploratory_openness(inputs, sources)
        response_variability = self._response_variability(inputs)
        initial_rigidity = self._initial_rigidity(inputs, sources)
        inverse_rigidity = 1.0 - initial_rigidity

        baseline_non_closure_index = _clamp(
            (trajectory_diversity * weights["trajectory_diversity"])
            + (strategic_plurality * weights["strategic_plurality"])
            + (exploratory_openness * weights["exploratory_openness"])
            + (response_variability * weights["response_variability"])
            + (inverse_rigidity * weights["inverse_rigidity"])
        )

        initial_closure_pressure = _clamp(1.0 - baseline_non_closure_index)
        baseline_confidence = _clamp(
            0.45
            + 0.10 * bool(inputs)
            + 0.10 * bool(sources)
            + 0.08 * bool(_as_sequence(inputs.get("trajectories") or inputs.get("trajectory_samples")))
            + 0.08 * bool(_as_sequence(inputs.get("strategies") or inputs.get("strategy_samples")))
            + 0.08 * bool(_as_sequence(inputs.get("responses") or inputs.get("response_samples")))
            + 0.06 * bool(_as_sequence(inputs.get("choices") or inputs.get("decision_samples")))
        )

        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": _utc_now(),
            "success": True,
            "trajectory_diversity": round(trajectory_diversity, 4),
            "strategic_plurality": round(strategic_plurality, 4),
            "exploratory_openness": round(exploratory_openness, 4),
            "response_variability": round(response_variability, 4),
            "initial_rigidity": round(initial_rigidity, 4),
            "inverse_rigidity": round(inverse_rigidity, 4),
            "baseline_non_closure_index": round(baseline_non_closure_index, 4),
            "initial_closure_pressure": round(initial_closure_pressure, 4),
            "closure_pressure_baseline": round(initial_closure_pressure, 4),
            "baseline_confidence": round(baseline_confidence, 4),
            "baseline_classification": self.classify(baseline_non_closure_index, initial_closure_pressure),
            "observational_only": True,
            "modifies_identity": False,
            "modifies_memory": False,
            "modifies_strategy": False,
            "ready_for_k2_rigidity_monitor": True,
            "ready_for_k3_homogenization_monitor": True,
            "ready_for_k4_exploratory_reduction_monitor": True,
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "weights": weights,
                "source_count": len(sources),
                "non_closure_threshold": 0.65,
                "closure_watch_threshold": 0.45,
                "persistence_enabled": bool(persist),
            },
        }

        if persist:
            self.persist(result)
        return result

    def persist(self, result: Mapping[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        payload = dict(result)
        self.latest_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, sort_keys=True) + "\n")

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        return self.evaluate(inputs=inputs, persist=persist)


ENGINE = ClosurePressureBaseline()


def step(inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
    return ENGINE.step(inputs=inputs, persist=persist)
