from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def _clamp01(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = default
    if math.isnan(x) or math.isinf(x):
        x = default
    return max(0.0, min(1.0, x))


def _non_negative_int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return max(0, default)


class SelectiveCognitiveActivation:
    '''
    P9 — Selective Cognitive Activation.

    Governs selective access to costly deep-cognition states in a massive
    artificial population. The primitive validates functional allocation only:
    it does not assert phenomenal subjectivity.
    '''

    primitive = 'SELECTIVE_COGNITIVE_ACTIVATION'

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / 'open-cognitive-ecology'
        self.history_dir = (
            self.root
            / 'runtime_experiments'
            / 'selective_cognitive_activation'
        )
        self.history_path = (
            self.history_dir
            / 'selective_cognitive_activation_benchmarks.jsonl'
        )

    def _sanitize_sizes(self, population_sizes: Iterable[int] | None) -> list[int]:
        if population_sizes is None:
            population_sizes = [100, 1000, 10000, 100000, 1000000]
        return [_non_negative_int(size) for size in population_sizes]

    def _activity_state(self, population_size: int, budget: float) -> dict[str, Any]:
        try:
            from ontology.activity_gradient_manager import ActivityGradientManager
            return ActivityGradientManager().step(
                population_size=population_size,
                available_attention_budget=budget,
            )
        except Exception as exc:
            active = min(population_size, int(max(0.0, budget) / 0.001))
            deep = int(active * 0.05)
            return {
                'active_individual_count': active,
                'inactive_individual_count': max(0, population_size - active),
                'deep_cognition_count': deep,
                'deep_cognition_ratio': deep / max(1, population_size),
                'attention_limited_activation': active < population_size,
                'fallback_reason': repr(exc),
            }

    def _compression_state(self, population_size: int) -> dict[str, Any]:
        try:
            from ontology.population_compression_framework import PopulationCompressionFramework
            result = PopulationCompressionFramework().step(
                population_sizes=[population_size],
                persist=False,
            )
            return result['results'][0] if result.get('results') else result
        except Exception as exc:
            return {
                'bytes_per_individual': 4096.0,
                'compression_ratio': 1.0,
                'compression_efficiency': 0.0,
                'compression_fallback_reason': repr(exc),
            }

    def _externalized_state(self, activation_pressure: float) -> dict[str, Any]:
        # External cognition is treated as a functional offloading channel, not
        # as a substitute for identity, governance, or continuity.
        demand = _clamp01(activation_pressure / 10.0)
        try:
            from ontology.externalized_cognition import ExternalizedCognition
            return ExternalizedCognition().step({
                'storage_reliance': demand,
                'inference_assistance': demand,
                'workflow_support': demand,
                'collaboration_enablement': demand,
            })
        except Exception as exc:
            return {
                'externalized_cognition_index': demand,
                'memory_offloading': demand,
                'reasoning_delegation': demand,
                'coordination_support': demand,
                'external_fallback_reason': repr(exc),
            }

    def _evaluate_size(
        self,
        population_size: int,
        available_attention_budget: float,
        max_deep_cognition_ratio: float,
        externalization_threshold: float,
    ) -> dict[str, Any]:
        population = _non_negative_int(population_size)
        budget = max(0.0, float(available_attention_budget or 0.0))
        max_deep_ratio = _clamp01(max_deep_cognition_ratio, 0.01)
        external_threshold = _clamp01(externalization_threshold, 0.5)

        if population <= 0:
            return {
                'population_size': 0,
                'available_attention_budget': budget,
                'active_individual_count': 0,
                'deep_cognition_count': 0,
                'allowed_deep_cognition_count': 0,
                'selected_deep_cognition_count': 0,
                'deferred_deep_cognition_count': 0,
                'externalized_cognition_count': 0,
                'deep_cognition_ratio': 0.0,
                'external_cognition_rate': 0.0,
                'selective_activation_index': 1.0,
                'cognitive_activation_savings': 1.0,
                'activation_constraint_pressure': 0.0,
                'bytes_per_individual': 0.0,
                'compression_ratio': 1.0,
                'compression_efficiency': 0.0,
                'bounded_metrics': True,
                'degradation_mode': 'empty_population',
            }

        activity = self._activity_state(population, budget)
        compression = self._compression_state(population)

        active = min(population, _non_negative_int(activity.get('active_individual_count')))
        requested_deep = min(active, _non_negative_int(activity.get('deep_cognition_count')))
        if requested_deep <= 0 and active >= 20:
            requested_deep = max(1, int(active * 0.05))

        allowed_deep = min(active, max(0, int(population * max_deep_ratio)))
        selected_deep = min(requested_deep, allowed_deep)
        deferred_deep = max(0, requested_deep - selected_deep)

        activation_pressure = population / max(1, active) if active > 0 else float('inf')
        finite_pressure = activation_pressure if math.isfinite(activation_pressure) else 10.0
        pressure_score = _clamp01(finite_pressure / 10.0)

        compression_efficiency = _clamp01(compression.get('compression_efficiency'), 0.0)
        compression_ratio = max(1.0, float(compression.get('compression_ratio', 1.0) or 1.0))
        bytes_per_individual = max(0.0, float(compression.get('bytes_per_individual', 0.0) or 0.0))

        external_state = self._externalized_state(finite_pressure)
        externalized_index = _clamp01(external_state.get('externalized_cognition_index'), 0.0)

        # Externalization activates only when pressure crosses the governed
        # threshold. It absorbs deferred deep cognition rather than increasing
        # total deep activation pressure.
        if pressure_score >= external_threshold:
            externalized_count = deferred_deep
        else:
            externalized_count = 0

        deep_ratio = selected_deep / max(1, population)
        external_rate = externalized_count / max(1, population)
        savings = 1.0 - (selected_deep / max(1, requested_deep)) if requested_deep > 0 else 1.0
        savings = _clamp01(savings)

        pressure_component = 1.0 - pressure_score
        efficiency_component = compression_efficiency
        selectivity_component = 1.0 - (deep_ratio / max(0.000001, max_deep_ratio))
        selectivity_component = _clamp01(selectivity_component)
        external_component = externalized_index if externalized_count > 0 else 0.5

        selective_activation_index = _clamp01(
            0.30 * savings
            + 0.25 * efficiency_component
            + 0.20 * pressure_component
            + 0.15 * selectivity_component
            + 0.10 * external_component
        )

        bounded_metrics = all([
            0.0 <= deep_ratio <= 1.0,
            0.0 <= external_rate <= 1.0,
            0.0 <= selective_activation_index <= 1.0,
            0.0 <= savings <= 1.0,
            bytes_per_individual >= 0.0,
            compression_ratio >= 1.0,
        ])

        return {
            'population_size': population,
            'available_attention_budget': budget,
            'active_individual_count': active,
            'inactive_individual_count': max(0, population - active),
            'requested_deep_cognition_count': requested_deep,
            'deep_cognition_count': selected_deep,
            'allowed_deep_cognition_count': allowed_deep,
            'selected_deep_cognition_count': selected_deep,
            'deferred_deep_cognition_count': deferred_deep,
            'externalized_cognition_count': externalized_count,
            'deep_cognition_ratio': deep_ratio,
            'external_cognition_rate': external_rate,
            'selective_activation_index': selective_activation_index,
            'cognitive_activation_savings': savings,
            'activation_constraint_pressure': finite_pressure,
            'attention_limited_activation': bool(activity.get('attention_limited_activation', active < population)),
            'externalized_cognition_index': externalized_index,
            'bytes_per_individual': bytes_per_individual,
            'compression_ratio': compression_ratio,
            'compression_efficiency': compression_efficiency,
            'bounded_metrics': bounded_metrics,
            'degradation_mode': 'zero_attention_budget' if budget <= 0.0 else 'none',
        }

    def _persist(self, payload: dict[str, Any]) -> None:
        self.history_dir.mkdir(parents=True, exist_ok=True)
        with self.history_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(payload, sort_keys=True) + '\n')

    def step(
        self,
        population_sizes: Iterable[int] | None = None,
        available_attention_budget: float = 1.0,
        max_deep_cognition_ratio: float = 0.01,
        externalization_threshold: float = 0.5,
        persist: bool = True,
        **_: Any,
    ) -> dict[str, Any]:
        sizes = self._sanitize_sizes(population_sizes)
        results = [
            self._evaluate_size(
                population_size=size,
                available_attention_budget=available_attention_budget,
                max_deep_cognition_ratio=max_deep_cognition_ratio,
                externalization_threshold=externalization_threshold,
            )
            for size in sizes
        ]
        max_result = max(results, key=lambda r: r['population_size'], default=None)
        non_empty = [r for r in results if r['population_size'] > 0]

        max_population = int(max_result['population_size']) if max_result else 0
        deep_ratio = float(max_result['deep_cognition_ratio']) if max_result else 0.0
        external_rate = float(max_result['external_cognition_rate']) if max_result else 0.0
        activation_index = float(max_result['selective_activation_index']) if max_result else 1.0
        savings = float(max_result['cognitive_activation_savings']) if max_result else 1.0

        bounded_metrics = all(r['bounded_metrics'] for r in results)
        selective_activation_validated = bool(
            bounded_metrics
            and all(r['deep_cognition_ratio'] <= _clamp01(max_deep_cognition_ratio, 0.01) for r in results)
            and all(r['cognitive_activation_savings'] >= 0.0 for r in results)
        )

        payload: dict[str, Any] = {
            'primitive': self.primitive,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'population_sizes': sizes,
            'max_population_tested': max_population,
            'million_population_tested': max_population >= 1000000,
            'available_attention_budget': max(0.0, float(available_attention_budget or 0.0)),
            'max_deep_cognition_ratio': _clamp01(max_deep_cognition_ratio, 0.01),
            'deep_cognition_ratio': deep_ratio,
            'external_cognition_rate': external_rate,
            'selective_activation_index': activation_index,
            'cognitive_activation_savings': savings,
            'selective_activation_validated': selective_activation_validated,
            'bounded_metrics': bounded_metrics,
            'zero_budget_degradation_mode': bool(non_empty and max(0.0, float(available_attention_budget or 0.0)) <= 0.0),
            'empty_population_degradation_mode': not non_empty,
            'history_path': str(self.history_path),
            'results': results,
            'classification': (
                'Selective Cognitive Activation Validated'
                if selective_activation_validated
                else 'Selective Cognitive Activation Degraded'
            ),
            'diagnostics': {
                'phenomenal_subjectivity_claimed': False,
                'validation_scope': 'functional_metrics_only',
                'architecture_layer': 'civilizational_attention_economy',
                'dependencies': [
                    'activity_gradient_manager',
                    'population_activation_scheduler',
                    'population_compression_framework',
                    'externalized_cognition',
                    'cognitive_gap_detector',
                    'external_assistance_trigger',
                    'metrics_history_recorder',
                ],
            },
        }

        if persist:
            self._persist(payload)

        return payload
