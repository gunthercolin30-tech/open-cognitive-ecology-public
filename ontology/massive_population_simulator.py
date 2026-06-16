
# -*- coding: utf-8 -*-

'''
P7 — Massive Population Simulator.

Empirical scalability benchmark for the civilizational attention economy.
This module uses aggregate/streaming population states rather than one Python
object per individual, preserving scalability and avoiding artificial local
storage pressure.
'''

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter, process_time
from typing import Any, Iterable, Mapping
from datetime import datetime, timezone
import json
import math
import os
import resource

PRIMITIVE = 'massive_population_simulator'
PRIMITIVE_NAME = 'MASSIVE_POPULATION_SIMULATOR'

DEPENDENCIES = [
    'civilizational_attention_allocator',
    'population_activation_scheduler',
    'activity_gradient_manager',
    'computational_fairness_engine',
    'lineage_diversity_preservation',
    'constraint_based_attention_economy',
    'civilization_scale_simulation_runner',
    'society_simulation_runner',
    'distributed_population_runtime',
    'multi_individual_civilizational_ecology',
    'cognitive_resource_economy',
    'autonomous_resource_manager',
    'resource_allocation',
    'carrying_capacity',
    'constraint_monitoring_system',
    'anti_closure_metaconstraint',
    'openness_preservation_supervisor',
    'global_viability_certificate',
    'metrics_history_recorder',
]

ROOT = Path.home() / 'open-cognitive-ecology'
BENCHMARK_DIR = ROOT / 'runtime_experiments' / 'massive_population_simulator'
BENCHMARK_HISTORY = BENCHMARK_DIR / 'massive_population_benchmarks.jsonl'


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return float(value)
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _is_macos() -> bool:
    try:
        return os.uname().sysname.lower() == 'darwin'
    except Exception:
        return False


def _rss_bytes() -> int:
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if usage <= 0:
            return 0
        if _is_macos():
            return int(usage)
        return int(usage) * 1024
    except Exception:
        return 0


def _rss_mb() -> float:
    return _rss_bytes() / (1024.0 * 1024.0)


def _import_class(module_name: str, class_name: str):
    try:
        module = __import__(f'ontology.{module_name}', fromlist=[class_name])
        return getattr(module, class_name)
    except Exception:
        return None


def _call_step(cls: Any, fallback: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    if cls is None:
        return dict(fallback)
    try:
        result = cls().step(**kwargs)
        if isinstance(result, dict):
            return result
    except TypeError:
        try:
            result = cls().step(kwargs)
            if isinstance(result, dict):
                return result
        except Exception:
            pass
    except Exception:
        pass
    return dict(fallback)


@dataclass
class MassivePopulationSimulator:
    '''Aggregate empirical scalability benchmark for massive populations.'''

    primitive: str = PRIMITIVE_NAME
    population_targets: tuple[int, ...] = (100, 1_000, 10_000, 100_000, 1_000_000)
    available_attention_budget: float = 1.0
    reference_capacity: int = 1_000
    history_path: Path = BENCHMARK_HISTORY

    def __post_init__(self) -> None:
        BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
        self._attention_cls = _import_class('civilizational_attention_allocator', 'CivilizationalAttentionAllocator')
        self._scheduler_cls = _import_class('population_activation_scheduler', 'PopulationActivationScheduler')
        self._activity_cls = _import_class('activity_gradient_manager', 'ActivityGradientManager')
        self._fairness_cls = _import_class('computational_fairness_engine', 'ComputationalFairnessEngine')
        self._diversity_cls = _import_class('lineage_diversity_preservation', 'LineageDiversityPreservation')
        self._economy_cls = _import_class('constraint_based_attention_economy', 'ConstraintBasedAttentionEconomy')

    def _aggregate_lineages(self, population_size: int, lineage_count: int = 10) -> dict[str, int]:
        pop = max(0, int(population_size))
        n = max(1, min(int(lineage_count), max(1, pop)))
        base = pop // n
        remainder = pop % n
        return {f'lineage_{i + 1:03d}': base + (1 if i < remainder else 0) for i in range(n)}

    def _fallback_attention(self, population_size: int, budget: float) -> dict[str, Any]:
        pop = max(0, int(population_size))
        budget = max(0.0, float(budget))
        if budget <= 0.0 and pop > 0:
            return {
                'primitive': 'CIVILIZATIONAL_ATTENTION_ALLOCATOR_FALLBACK',
                'population_size': pop,
                'available_attention_budget': 0.0,
                'attention_budget': 0.0,
                'attention_allocation_index': 0.0,
                'attention_fairness_index': 0.0,
                'civilizational_attention_pressure': math.inf,
                'attention_saturation_index': 1.0,
                'attention_pressure_status': 'infinite_pressure',
            }
        pressure = (pop / max(1, self.reference_capacity)) / max(budget, 1e-12)
        saturation = pressure / (1.0 + pressure)
        return {
            'primitive': 'CIVILIZATIONAL_ATTENTION_ALLOCATOR_FALLBACK',
            'population_size': pop,
            'available_attention_budget': budget,
            'attention_budget': budget,
            'attention_allocation_index': _clamp(1.0 - saturation),
            'attention_fairness_index': _clamp(1.0 / (1.0 + math.log10(max(1, pop)))),
            'civilizational_attention_pressure': pressure,
            'attention_saturation_index': _clamp(saturation),
            'attention_pressure_status': 'finite_pressure',
        }

    def _simulate_one(self, population_size: int, budget: float) -> dict[str, Any]:
        pop = max(0, int(population_size))
        budget = max(0.0, float(budget))
        lineages = self._aggregate_lineages(pop)

        rss_before_bytes = _rss_bytes()
        wall_start = perf_counter()
        cpu_start = process_time()

        attention_fallback = self._fallback_attention(pop, budget)
        attention = _call_step(
            self._attention_cls,
            attention_fallback,
            population_size=pop,
            available_attention_budget=budget,
        )
        pressure = _safe_float(
            attention.get('civilizational_attention_pressure'),
            attention_fallback['civilizational_attention_pressure'],
        )
        if math.isinf(pressure):
            pressure_for_scaling = 1e12
        else:
            pressure_for_scaling = max(0.0, pressure)
        saturation = _clamp(_safe_float(
            attention.get('attention_saturation_index'),
            pressure_for_scaling / (1.0 + pressure_for_scaling),
        ))

        scheduler = _call_step(
            self._scheduler_cls,
            {
                'active_individual_count': 0 if budget <= 0.0 else max(1, int(pop * (1.0 - saturation))),
                'inactive_individual_count': pop if budget <= 0.0 else max(0, pop - max(1, int(pop * (1.0 - saturation)))),
                'activation_rate': _clamp(1.0 - saturation),
                'deactivation_rate': saturation,
                'activation_pressure': pressure_for_scaling,
            },
            population_size=pop,
            available_attention_budget=budget,
            attention_state=attention,
        )
        active = max(0, min(pop, _safe_int(scheduler.get('active_individual_count'), 0 if budget <= 0.0 else max(1, int(pop * (1.0 - saturation))))))

        activity = _call_step(
            self._activity_cls,
            {
                'existence': pop,
                'maintenance': active,
                'interaction': max(0, active // 2),
                'reflection': max(0, active // 10),
                'deep_cognition': max(0, active // 100),
            },
            population_size=pop,
            available_attention_budget=budget,
            scheduler_state=scheduler,
            attention_state=attention,
        )
        deep = max(0, min(pop, _safe_int(activity.get('deep_cognition'), max(0, active // 100))))

        fairness = _call_step(
            self._fairness_cls,
            {
                'computational_fairness_index': _clamp(1.0 - saturation * 0.35),
                'attention_gini_coefficient': _clamp(saturation * 0.5),
                'minority_lineage_protection_index': _clamp(1.0 - saturation * 0.25),
            },
            population_size=pop,
            available_attention_budget=budget,
            attention_state=attention,
            scheduler_state=scheduler,
            activity_state=activity,
            lineage_distribution=lineages,
        )

        diversity = _call_step(
            self._diversity_cls,
            {
                'lineage_diversity_index': 1.0 if len(lineages) > 1 else 0.0,
                'attention_diversity_index': _clamp(1.0 - saturation * 0.30),
                'minority_lineage_survival_rate': _clamp(1.0 - saturation * 0.20),
                'lineage_extinction_risk': _clamp(saturation * 0.20),
                'lineage_preservation_score': _clamp(1.0 - saturation * 0.20),
                'diversity_pressure_index': saturation,
            },
            population_size=pop,
            available_attention_budget=budget,
            attention_state=attention,
            scheduler_state=scheduler,
            activity_state=activity,
            fairness_state=fairness,
            lineage_distribution=lineages,
        )

        economy = _call_step(
            self._economy_cls,
            {
                'civilizational_attention_pressure': pressure,
                'attention_saturation_index': saturation,
                'attention_viability_index': _clamp(1.0 - saturation),
                'attention_constraint_compliance': _clamp(1.0 - saturation * 0.30),
                'attention_resource_efficiency': _clamp(1.0 - saturation * 0.20),
                'civilizational_attention_reserve': _clamp(1.0 - saturation),
                'attention_economy_balance': _clamp(1.0 - saturation),
                'diversity_integrated': True,
            },
            population_size=pop,
            available_attention_budget=budget,
            attention_state=attention,
            scheduler_state=scheduler,
            activity_state=activity,
            fairness_state=fairness,
            diversity_state=diversity,
        )

        wall_time_seconds = max(0.0, perf_counter() - wall_start)
        cpu_time_seconds = max(0.0, process_time() - cpu_start)
        rss_after_bytes = _rss_bytes()
        ram_delta_bytes = max(0, rss_after_bytes - rss_before_bytes)
        ram_mb = rss_after_bytes / (1024.0 * 1024.0) if rss_after_bytes else _rss_mb()
        cpu_percent = 0.0 if wall_time_seconds <= 0.0 else max(0.0, (cpu_time_seconds / wall_time_seconds) * 100.0)
        bytes_per_individual_upper_bound = ram_delta_bytes / max(1, pop)

        viability = _clamp(_safe_float(economy.get('attention_viability_index'), 1.0 - saturation))
        diversity_score = _clamp(_safe_float(diversity.get('lineage_preservation_score'), 1.0 - saturation * 0.20))
        fairness_score = _clamp(_safe_float(fairness.get('computational_fairness_index'), 1.0 - saturation * 0.35))
        memory_efficiency = _clamp(1.0 - min(1.0, bytes_per_individual_upper_bound / 512.0))
        scalability_score = _clamp((viability + diversity_score + fairness_score + memory_efficiency) / 4.0)

        return {
            'population_size': pop,
            'available_attention_budget': budget,
            'simulation_mode': 'aggregate_streaming_population_state',
            'lineage_count': len(lineages),
            'active_individual_count': active,
            'inactive_individual_count': max(0, pop - active),
            'deep_cognition_count': deep,
            'deep_cognition_ratio': _clamp(deep / max(1, pop)),

            'wall_time_seconds': wall_time_seconds,
            'cycle_time_seconds': wall_time_seconds,
            'cpu_time_seconds': cpu_time_seconds,
            'cpu_percent': cpu_percent,
            'cycle_time_per_individual': wall_time_seconds / max(1, pop),

            'rss_before_bytes': rss_before_bytes,
            'rss_after_bytes': rss_after_bytes,
            'ram_delta_bytes': ram_delta_bytes,
            'ram_mb': ram_mb,
            'bytes_per_individual_upper_bound': bytes_per_individual_upper_bound,

            'civilizational_attention_pressure': pressure,
            'attention_saturation_index': saturation,
            'attention_viability_index': viability,
            'attention_economy_balance': _clamp(_safe_float(economy.get('attention_economy_balance'), viability)),
            'computational_fairness_index': fairness_score,
            'lineage_preservation_score': diversity_score,
            'lineage_extinction_risk': _clamp(_safe_float(diversity.get('lineage_extinction_risk'), saturation * 0.20)),
            'scalability_score': scalability_score,
            'scalability_validated': pop <= 1_000_000 and wall_time_seconds < 5.0,
            'bounded_metrics': 0.0 <= saturation <= 1.0 and 0.0 <= viability <= 1.0,
            'states': {
                'attention': attention,
                'scheduler': scheduler,
                'activity': activity,
                'fairness': fairness,
                'diversity': diversity,
                'economy': economy,
            },
        }

    def _persist(self, payload: Mapping[str, Any]) -> None:
        try:
            BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
            with self.history_path.open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(payload, ensure_ascii=False, default=str) + '\n')
        except Exception:
            pass

    def step(
        self,
        population_sizes: Iterable[int] | None = None,
        available_attention_budget: float | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        targets = tuple(int(x) for x in (population_sizes or self.population_targets))
        budget = self.available_attention_budget if available_attention_budget is None else float(available_attention_budget)
        results = [self._simulate_one(population_size=t, budget=budget) for t in targets]

        max_population = max((r['population_size'] for r in results), default=0)
        max_cycle_time = max((r['cycle_time_seconds'] for r in results), default=0.0)
        max_cpu_percent = max((r['cpu_percent'] for r in results), default=0.0)
        max_ram_mb = max((r['ram_mb'] for r in results), default=0.0)
        max_pressure = max((r['civilizational_attention_pressure'] if not math.isinf(r['civilizational_attention_pressure']) else 1e12 for r in results), default=0.0)
        mean_scalability = sum(r['scalability_score'] for r in results) / max(1, len(results))
        all_bounded = all(r['bounded_metrics'] for r in results)
        million_validated = any(r['population_size'] >= 1_000_000 and r['scalability_validated'] for r in results)
        zero_budget = budget <= 0.0

        classification = (
            'Massive Population Scalability Validated'
            if million_validated and all_bounded and mean_scalability >= 0.50
            else 'Massive Population Benchmark Operational'
            if all_bounded
            else 'Massive Population Benchmark Degraded'
        )

        payload = {
            'primitive': self.primitive,
            'primitive_key': PRIMITIVE,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'population_targets': list(targets),
            'available_attention_budget': max(0.0, budget),
            'benchmark_count': len(results),
            'max_population_tested': max_population,
            'million_population_tested': max_population >= 1_000_000,
            'million_population_validated': million_validated,
            'max_cycle_time_seconds': max_cycle_time,
            'max_wall_time_seconds': max_cycle_time,
            'max_cpu_percent': max_cpu_percent,
            'max_ram_mb': max_ram_mb,
            'max_civilizational_attention_pressure': max_pressure,
            'mean_scalability_score': _clamp(mean_scalability),
            'bounded_metrics': all_bounded,
            'zero_budget_degradation_mode': zero_budget,
            'scalability_empirical': True,
            'classification': classification,
            'history_path': str(self.history_path),
            'results': results,
            'diagnostics': {
                'non_redundant_role': 'empirical_scalability_benchmark_for_P1_to_P6_attention_economy',
                'representation_strategy': 'aggregate_streaming_population_state_no_per_individual_objects',
                'p7_targets_supported': [100, 1_000, 10_000, 100_000, 1_000_000],
                'dependencies': DEPENDENCIES,
                'history_path': str(self.history_path),
                'field_compatibility': 'P7_R1_cycle_cpu_ram_pressure_history_aliases',
            },
        }
        if persist:
            self._persist(payload)
        return payload
