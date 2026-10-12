from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class HomogenizationMonitor:
    '''
    K3 — Homogenization Monitor.

    Observational primitive for closure-pressure instrumentation.
    It estimates excessive homogenization without modifying identity, memory,
    strategy, governance state, or any upstream primitive.

    Functional scope:
    - state uniformization;
    - cognitive diversity reduction;
    - pluralism weakening;
    - excessive convergence;
    - rigidity-coupled homogenization pressure.
    '''

    primitive = "homogenization_monitor"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.state_dir = self.root / "closure_pressure" / self.primitive
        self.latest_path = self.state_dir / f"latest_{self.primitive}.json"
        self.history_path = self.state_dir / f"{self.primitive}_history.jsonl"

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
        if isinstance(value, set):
            return list(value)
        return [value]

    @staticmethod
    def _canonical(item: Any) -> str:
        if isinstance(item, dict):
            return json.dumps(item, sort_keys=True, ensure_ascii=False)
        return str(item)

    def _diversity_score(self, items: Iterable[Any], default: float = 0.5) -> float:
        values = [self._canonical(x) for x in items if x is not None]
        if not values:
            return default
        if len(values) == 1:
            return 0.0
        counts = Counter(values)
        richness = len(counts) / len(values)
        probabilities = [count / len(values) for count in counts.values()]
        entropy = -sum(p * math.log(p) for p in probabilities if p > 0.0)
        max_entropy = math.log(len(counts)) if len(counts) > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy else 0.0
        return self._clamp((richness + normalized_entropy) / 2.0)

    def _uniformity_score(self, items: Iterable[Any], default: float = 0.5) -> float:
        values = [self._canonical(x) for x in items if x is not None]
        if not values:
            return default
        if len(values) == 1:
            return 1.0
        counts = Counter(values)
        dominant_share = max(counts.values()) / len(values)
        diversity = self._diversity_score(values, default=0.0)
        return self._clamp((dominant_share + (1.0 - diversity)) / 2.0)

    def _source_metric(self, sources: dict[str, Any], source_name: str, keys: list[str], default: float | None = None) -> float | None:
        source = sources.get(source_name, {}) if isinstance(sources, dict) else {}
        if not isinstance(source, dict):
            return default
        for key in keys:
            if key in source:
                return self._clamp(source[key])
        return default

    def _classification(self, homogenization_index: float) -> str:
        if homogenization_index >= 0.78:
            return "critical_homogenization_pressure"
        if homogenization_index >= 0.58:
            return "high_homogenization_watch"
        if homogenization_index >= 0.36:
            return "moderate_homogenization_signal"
        return "pluralistic_diversity_preserved"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        sources = inputs.get("sources", {}) if isinstance(inputs.get("sources", {}), dict) else {}

        states = self._as_list(
            inputs.get("states")
            or inputs.get("cognitive_states")
            or inputs.get("agent_states")
            or inputs.get("population_states")
        )
        cognitive_profiles = self._as_list(
            inputs.get("cognitive_profiles")
            or inputs.get("agents")
            or inputs.get("individuals")
            or inputs.get("viewpoints")
        )
        strategies = self._as_list(inputs.get("strategies") or inputs.get("strategic_positions"))
        symbols = self._as_list(inputs.get("symbols") or inputs.get("semantic_variants") or inputs.get("languages"))
        decisions = self._as_list(inputs.get("decisions") or inputs.get("choices"))

        state_diversity_score = self._clamp(
            inputs.get("state_diversity_score"),
            default=self._diversity_score(states or cognitive_profiles or decisions, default=0.5),
        )
        state_uniformity_score = self._clamp(
            inputs.get("state_uniformity_score"),
            default=self._uniformity_score(states or decisions or strategies, default=0.5),
        )

        cognitive_diversity_score = self._clamp(
            inputs.get("cognitive_diversity_score"),
            default=self._diversity_score(cognitive_profiles or states or strategies or symbols, default=0.5),
        )

        source_pluralism = self._source_metric(
            sources,
            "distributed_semantic_pluralism",
            [
                "distributed_semantic_pluralism_index",
                "semantic_pluralism_index",
                "pluralism_score",
                "diversity_score",
            ],
            default=None,
        )
        if source_pluralism is None:
            source_pluralism = self._source_metric(
                sources,
                "collective_deliberation_engine",
                ["diversity_score", "deliberative_diversity", "pluralism_score"],
                default=None,
            )
        pluralism_score = self._clamp(
            inputs.get("pluralism_score"),
            default=source_pluralism if source_pluralism is not None else self._diversity_score(symbols or strategies or cognitive_profiles, default=0.5),
        )

        non_convergence_source = self._source_metric(
            sources,
            "non_convergent_intelligence_dynamics",
            ["non_convergence_index", "non_convergent_dynamics_index", "divergence_score"],
            default=None,
        )
        diversification_source = self._source_metric(
            sources,
            "evolutionary_diversification",
            ["evolutionary_diversification_index", "diversification_index", "diversity_score"],
            default=None,
        )
        baseline_source = self._source_metric(
            sources,
            "closure_pressure_baseline",
            ["strategic_plurality", "trajectory_diversity", "baseline_non_closure_index"],
            default=None,
        )
        rigidity_source = self._source_metric(
            sources,
            "rigidity_monitor",
            ["rigidity_index"],
            default=None,
        )

        convergence_signal = self._clamp(
            inputs.get("convergence_score"),
            default=1.0 - (non_convergence_source if non_convergence_source is not None else self._diversity_score(decisions or strategies or states, default=0.5)),
        )
        diversity_support = [state_diversity_score, cognitive_diversity_score, pluralism_score]
        if diversification_source is not None:
            diversity_support.append(diversification_source)
        if baseline_source is not None:
            diversity_support.append(baseline_source)
        diversity_support_score = self._clamp(sum(diversity_support) / len(diversity_support), default=0.5)

        cognitive_diversity_loss = self._clamp(1.0 - cognitive_diversity_score)
        pluralism_weakening = self._clamp(1.0 - pluralism_score)
        excessive_convergence = self._clamp(convergence_signal)
        rigidity_coupling = self._clamp(inputs.get("rigidity_index"), default=rigidity_source if rigidity_source is not None else 0.0)

        homogenization_index = self._clamp(
            (
                0.24 * state_uniformity_score
                + 0.23 * cognitive_diversity_loss
                + 0.22 * pluralism_weakening
                + 0.21 * excessive_convergence
                + 0.10 * rigidity_coupling
            )
        )

        preserved_diversity_index = self._clamp(1.0 - homogenization_index)
        population_sample_size = max(len(states), len(cognitive_profiles), len(strategies), len(symbols), len(decisions))

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "success": True,
            "state_uniformity_score": state_uniformity_score,
            "state_diversity_score": state_diversity_score,
            "cognitive_diversity_score": cognitive_diversity_score,
            "cognitive_diversity_loss": cognitive_diversity_loss,
            "pluralism_score": pluralism_score,
            "pluralism_weakening": pluralism_weakening,
            "excessive_convergence": excessive_convergence,
            "rigidity_coupling": rigidity_coupling,
            "diversity_support_score": diversity_support_score,
            "homogenization_index": homogenization_index,
            "preserved_diversity_index": preserved_diversity_index,
            "homogenization_classification": self._classification(homogenization_index),
            "baseline_integrated": "closure_pressure_baseline" in sources or baseline_source is not None,
            "rigidity_integrated": "rigidity_monitor" in sources or rigidity_source is not None,
            "population_sample_size": population_sample_size,
            "observational_only": True,
            "modifies_identity": False,
            "modifies_memory": False,
            "modifies_strategy": False,
            "diagnostics": {
                "measures_state_uniformization": True,
                "measures_cognitive_diversity_reduction": True,
                "measures_pluralism_weakening": True,
                "measures_excessive_convergence": True,
                "closure_axis": "K3",
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
