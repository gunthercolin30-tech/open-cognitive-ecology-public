from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class ExploratoryReductionMonitor:
    '''
    K4 — Exploratory Reduction Monitor.

    Observational primitive for closure-pressure instrumentation.
    It estimates reductions in exploration without modifying identity, memory,
    strategy, governance state, upstream recommendations, or execution layers.

    Functional scope:
    - explored option reduction;
    - novelty decline;
    - bifurcation reduction;
    - alternative hypothesis narrowing;
    - morphospace exploration contraction;
    - rigidity and homogenization coupled exploratory pressure.
    '''

    primitive = "exploratory_reduction_monitor"

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

    def _coverage_score(self, items: Iterable[Any], target_count: int | None = None, default: float = 0.5) -> float:
        values = [self._canonical(x) for x in items if x is not None]
        if not values:
            return default
        unique_count = len(set(values))
        if target_count is None:
            target_count = max(4, len(values))
        return self._clamp(unique_count / max(1, target_count))

    def _source_metric(self, sources: dict[str, Any], source_name: str, keys: list[str], default: float | None = None) -> float | None:
        source = sources.get(source_name, {}) if isinstance(sources, dict) else {}
        if not isinstance(source, dict):
            return default
        for key in keys:
            if key in source:
                return self._clamp(source[key])
        return default

    def _classification(self, exploratory_reduction_index: float) -> str:
        if exploratory_reduction_index >= 0.78:
            return "critical_exploratory_reduction_pressure"
        if exploratory_reduction_index >= 0.58:
            return "high_exploratory_reduction_watch"
        if exploratory_reduction_index >= 0.36:
            return "moderate_exploratory_reduction_signal"
        return "exploratory_openness_preserved"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        sources = inputs.get("sources", {}) if isinstance(inputs.get("sources", {}), dict) else {}

        explored_options = self._as_list(
            inputs.get("explored_options")
            or inputs.get("options")
            or inputs.get("alternatives")
            or inputs.get("choices_explored")
        )
        novel_items = self._as_list(
            inputs.get("novel_items")
            or inputs.get("novelties")
            or inputs.get("new_patterns")
            or inputs.get("discoveries")
        )
        bifurcations = self._as_list(
            inputs.get("bifurcations")
            or inputs.get("branch_points")
            or inputs.get("trajectory_branches")
        )
        hypotheses = self._as_list(
            inputs.get("hypotheses")
            or inputs.get("alternative_hypotheses")
            or inputs.get("counterfactuals")
            or inputs.get("possible_worlds")
        )
        morphospace_regions = self._as_list(
            inputs.get("morphospace_regions")
            or inputs.get("morphospace_samples")
            or inputs.get("explored_regions")
        )

        target_option_count = inputs.get("target_option_count") or inputs.get("expected_option_count")
        try:
            target_option_count_int = int(target_option_count) if target_option_count is not None else None
        except (TypeError, ValueError):
            target_option_count_int = None

        option_exploration_score = self._clamp(
            inputs.get("option_exploration_score"),
            default=self._coverage_score(explored_options, target_count=target_option_count_int, default=0.5),
        )

        source_novelty = self._source_metric(
            sources,
            "novelty_emergence",
            ["novelty_emergence_index", "novelty_score", "structural_novelty", "novelty"],
            default=None,
        )
        source_curiosity = self._source_metric(
            sources,
            "intrinsic_curiosity_drive",
            ["intrinsic_curiosity_index", "curiosity_drive", "exploratory_drive"],
            default=None,
        )
        novelty_score = self._clamp(
            inputs.get("novelty_score"),
            default=source_novelty if source_novelty is not None else self._diversity_score(novel_items or explored_options, default=0.5),
        )
        curiosity_score = self._clamp(
            inputs.get("curiosity_score"),
            default=source_curiosity if source_curiosity is not None else novelty_score,
        )

        source_bifurcation = self._source_metric(
            sources,
            "bifurcation_dynamics",
            ["bifurcation_index", "bifurcation_potential", "branching_score", "morphogenetic_bifurcation"],
            default=None,
        )
        if source_bifurcation is None:
            source_bifurcation = self._source_metric(
                sources,
                "adaptive_civilizational_bifurcation",
                ["adaptive_bifurcation_index", "bifurcation_score", "branching_score"],
                default=None,
            )
        bifurcation_score = self._clamp(
            inputs.get("bifurcation_score"),
            default=source_bifurcation if source_bifurcation is not None else self._coverage_score(bifurcations, target_count=4, default=0.5),
        )

        source_possible_worlds = self._source_metric(
            sources,
            "possible_worlds_exploration",
            ["possible_worlds_exploration_index", "world_exploration_score", "alternative_worlds_score"],
            default=None,
        )
        hypothesis_alternativity_score = self._clamp(
            inputs.get("hypothesis_alternativity_score"),
            default=source_possible_worlds if source_possible_worlds is not None else self._coverage_score(hypotheses, target_count=4, default=0.5),
        )

        source_morphospace = self._source_metric(
            sources,
            "morphospace_exploration",
            ["morphospace_exploration_index", "morphospace_coverage", "morphospace_diversity"],
            default=None,
        )
        morphospace_coverage_score = self._clamp(
            inputs.get("morphospace_coverage_score"),
            default=source_morphospace if source_morphospace is not None else self._coverage_score(morphospace_regions or explored_options, target_count=4, default=0.5),
        )

        exploration_balance_source = self._source_metric(
            sources,
            "exploration_exploitation_balance",
            ["exploration_score", "exploration_ratio", "exploration_exploitation_balance_index"],
            default=None,
        )
        baseline_source = self._source_metric(
            sources,
            "closure_pressure_baseline",
            ["exploratory_openness", "baseline_non_closure_index", "trajectory_diversity"],
            default=None,
        )
        rigidity_source = self._source_metric(sources, "rigidity_monitor", ["rigidity_index"], default=None)
        homogenization_source = self._source_metric(sources, "homogenization_monitor", ["homogenization_index"], default=None)

        exploration_support_values = [
            option_exploration_score,
            novelty_score,
            curiosity_score,
            bifurcation_score,
            hypothesis_alternativity_score,
            morphospace_coverage_score,
        ]
        if exploration_balance_source is not None:
            exploration_support_values.append(exploration_balance_source)
        if baseline_source is not None:
            exploration_support_values.append(baseline_source)

        exploration_support_score = self._clamp(sum(exploration_support_values) / len(exploration_support_values), default=0.5)

        option_reduction_score = self._clamp(inputs.get("option_reduction_score"), default=1.0 - option_exploration_score)
        novelty_decline_score = self._clamp(inputs.get("novelty_decline_score"), default=1.0 - novelty_score)
        bifurcation_reduction_score = self._clamp(inputs.get("bifurcation_reduction_score"), default=1.0 - bifurcation_score)
        hypothesis_narrowing_score = self._clamp(inputs.get("hypothesis_narrowing_score"), default=1.0 - hypothesis_alternativity_score)
        morphospace_contraction_score = self._clamp(inputs.get("morphospace_contraction_score"), default=1.0 - morphospace_coverage_score)
        curiosity_decline_score = self._clamp(inputs.get("curiosity_decline_score"), default=1.0 - curiosity_score)

        rigidity_coupling = self._clamp(inputs.get("rigidity_index"), default=rigidity_source if rigidity_source is not None else 0.0)
        homogenization_coupling = self._clamp(
            inputs.get("homogenization_index"),
            default=homogenization_source if homogenization_source is not None else 0.0,
        )

        exploratory_reduction_index = self._clamp(
            0.20 * option_reduction_score
            + 0.18 * novelty_decline_score
            + 0.18 * bifurcation_reduction_score
            + 0.17 * hypothesis_narrowing_score
            + 0.12 * morphospace_contraction_score
            + 0.07 * curiosity_decline_score
            + 0.04 * rigidity_coupling
            + 0.04 * homogenization_coupling
        )

        preserved_exploratory_openness = self._clamp(1.0 - exploratory_reduction_index)
        sample_size = max(
            len(explored_options),
            len(novel_items),
            len(bifurcations),
            len(hypotheses),
            len(morphospace_regions),
        )

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "success": True,
            "option_exploration_score": option_exploration_score,
            "option_reduction_score": option_reduction_score,
            "novelty_score": novelty_score,
            "novelty_decline_score": novelty_decline_score,
            "curiosity_score": curiosity_score,
            "curiosity_decline_score": curiosity_decline_score,
            "bifurcation_score": bifurcation_score,
            "bifurcation_reduction_score": bifurcation_reduction_score,
            "hypothesis_alternativity_score": hypothesis_alternativity_score,
            "hypothesis_narrowing_score": hypothesis_narrowing_score,
            "morphospace_coverage_score": morphospace_coverage_score,
            "morphospace_contraction_score": morphospace_contraction_score,
            "rigidity_coupling": rigidity_coupling,
            "homogenization_coupling": homogenization_coupling,
            "exploration_support_score": exploration_support_score,
            "exploratory_reduction_index": exploratory_reduction_index,
            "preserved_exploratory_openness": preserved_exploratory_openness,
            "exploratory_reduction_classification": self._classification(exploratory_reduction_index),
            "baseline_integrated": "closure_pressure_baseline" in sources or baseline_source is not None,
            "rigidity_integrated": "rigidity_monitor" in sources or rigidity_source is not None,
            "homogenization_integrated": "homogenization_monitor" in sources or homogenization_source is not None,
            "sample_size": sample_size,
            "observational_only": True,
            "modifies_identity": False,
            "modifies_memory": False,
            "modifies_strategy": False,
            "diagnostics": {
                "measures_explored_option_reduction": True,
                "measures_novelty_decline": True,
                "measures_bifurcation_reduction": True,
                "measures_alternative_hypothesis_narrowing": True,
                "measures_morphospace_contraction": True,
                "closure_axis": "K4",
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
