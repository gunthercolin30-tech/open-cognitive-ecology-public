# -*- coding: utf-8 -*-
# P4 Computational Fairness Engine.
# Functional metric layer only. No phenomenal subjectivity claim.

from __future__ import annotations

from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

PRIMITIVE = 'computational_fairness_engine'
PRIMITIVE_NAME = 'COMPUTATIONAL_FAIRNESS_ENGINE'
MATURITY_LEVEL = 'P4_OPERATIONAL'

DEPENDENCIES = [
    'civilizational_attention_allocator',
    'population_activation_scheduler',
    'activity_gradient_manager',
    'governance',
    'distributed_governance_layer',
    'multi_lineage_topology',
    'genealogical_continuity',
    'inter_lineage_symbolic_exchange',
    'biodiversity_preservation',
    'anti_closure_metaconstraint',
    'openness_preservation_supervisor',
    'metrics_history_recorder',
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _clamp01(value: Any, default: float = 0.0) -> float:
    number = _safe_float(value, default)
    return max(0.0, min(1.0, number))


def _gini(values: Sequence[float]) -> float:
    clean = [max(0.0, _safe_float(v, 0.0)) for v in values]
    if not clean:
        return 0.0
    total = sum(clean)
    if total <= 0.0:
        return 0.0
    ordered = sorted(clean)
    n = len(ordered)
    weighted_sum = sum((i + 1) * value for i, value in enumerate(ordered))
    gini = (2.0 * weighted_sum) / (n * total) - (n + 1.0) / n
    return _clamp01(gini)


def _normalize_distribution(raw: Mapping[str, Any] | None, default_count: int = 4) -> dict[str, float]:
    if raw:
        out: dict[str, float] = {}
        for key, value in raw.items():
            out[str(key)] = max(0.0, _safe_float(value, 0.0))
        if out:
            return out
    count = max(1, int(default_count))
    return {f'lineage_{i+1}': 1.0 for i in range(count)}


def _derive_attention_by_lineage(
    lineage_distribution: Mapping[str, float],
    active_individual_count: int,
    protected_minority_share: float,
) -> dict[str, float]:
    total_lineage_population = sum(lineage_distribution.values())
    if active_individual_count <= 0 or total_lineage_population <= 0.0:
        return {key: 0.0 for key in lineage_distribution}
    base = {key: active_individual_count * (value / total_lineage_population) for key, value in lineage_distribution.items()}
    if len(base) <= 1:
        return base
    minority_key = sorted(lineage_distribution.items(), key=lambda item: item[1])[0][0]
    minimum = active_individual_count * _clamp01(protected_minority_share, 0.05)
    if base[minority_key] >= minimum:
        return base
    delta = minimum - base[minority_key]
    donors = [key for key in base if key != minority_key]
    donor_total = sum(base[key] for key in donors)
    if donor_total <= 0.0:
        return base
    base[minority_key] = minimum
    for key in donors:
        base[key] = max(0.0, base[key] - delta * (base[key] / donor_total))
    return base


class ComputationalFairnessEngine:
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / 'open-cognitive-ecology'
        self.cycle_count = 0

    def _derive_scheduler_state(self, population_size: int, available_attention_budget: float, scheduler_state: Mapping[str, Any] | None) -> dict[str, Any]:
        if scheduler_state:
            population = max(0, _safe_int(scheduler_state.get('population_size'), population_size))
            active = max(0, _safe_int(scheduler_state.get('active_individual_count'), 0))
            inactive = max(0, _safe_int(scheduler_state.get('inactive_individual_count'), max(0, population - active)))
            fairness = _clamp01(scheduler_state.get('scheduler_fairness_index'), 0.75)
            return {
                'population_size': population,
                'active_individual_count': min(population, active),
                'inactive_individual_count': inactive,
                'scheduler_fairness_index': fairness,
                'attention_limited_activation': bool(scheduler_state.get('attention_limited_activation', active < population)),
            }
        population = max(0, _safe_int(population_size, 0))
        budget = max(0.0, _safe_float(available_attention_budget, 0.0))
        active_capacity = int(budget / 0.001) if budget > 0.0 else 0
        active = max(0, min(population, active_capacity))
        inactive = max(0, population - active)
        coverage = 1.0 if population <= 0 else active / max(1, population)
        scheduler_fairness = _clamp01(0.45 * coverage + 0.25 + 0.30 * 0.92)
        return {
            'population_size': population,
            'active_individual_count': active,
            'inactive_individual_count': inactive,
            'scheduler_fairness_index': scheduler_fairness,
            'attention_limited_activation': population > 0 and active < population,
        }

    def step(
        self,
        population_size: int = 10000,
        available_attention_budget: float = 1.0,
        scheduler_state: Mapping[str, Any] | None = None,
        activity_state: Mapping[str, Any] | None = None,
        lineage_distribution: Mapping[str, Any] | None = None,
        attention_by_lineage: Mapping[str, Any] | None = None,
        protected_minority_share: float = 0.05,
        fairness_floor: float = 0.75,
        governance_alignment: float = 0.92,
        non_closure_alignment: float = 0.92,
        record_metrics: bool = False,
    ) -> dict[str, Any]:
        self.cycle_count += 1
        scheduler = self._derive_scheduler_state(population_size, available_attention_budget, scheduler_state)
        population = max(0, _safe_int(scheduler['population_size'], 0))
        active = max(0, min(population, _safe_int(scheduler['active_individual_count'], 0)))
        inactive = max(0, population - active)
        fairness_floor = _clamp01(fairness_floor, 0.75)
        governance_alignment = _clamp01(governance_alignment, 0.92)
        non_closure_alignment = _clamp01(non_closure_alignment, 0.92)
        protected_minority_share = _clamp01(protected_minority_share, 0.05)
        lineages = _normalize_distribution(lineage_distribution, default_count=4)
        lineage_population_values = list(lineages.values())
        if attention_by_lineage:
            lineage_attention = {str(k): max(0.0, _safe_float(v, 0.0)) for k, v in attention_by_lineage.items()}
            for key in lineages:
                lineage_attention.setdefault(key, 0.0)
        else:
            lineage_attention = _derive_attention_by_lineage(lineages, active, protected_minority_share)
        attention_values = [lineage_attention.get(key, 0.0) for key in lineages]
        attention_gini = _gini(attention_values)
        population_gini = _gini(lineage_population_values)
        attention_inequality_index = attention_gini
        lineage_attention_balance = _clamp01(1.0 - attention_gini)
        scheduler_equity_index = _clamp01(scheduler.get('scheduler_fairness_index'), 0.75)
        minority_key = min(lineages, key=lambda key: lineages[key]) if lineages else None
        total_attention = sum(attention_values)
        minority_attention_share = 0.0
        minority_population_share = 0.0
        if minority_key is not None:
            total_pop = sum(lineages.values())
            minority_attention_share = lineage_attention.get(minority_key, 0.0) / total_attention if total_attention > 0 else 0.0
            minority_population_share = lineages[minority_key] / total_pop if total_pop > 0 else 0.0
        if population <= 0:
            minority_lineage_protection_index = 1.0
        elif active <= 0:
            minority_lineage_protection_index = 0.0
        else:
            target = max(protected_minority_share, minority_population_share * 0.5)
            minority_lineage_protection_index = _clamp01(minority_attention_share / max(target, 1e-12))
        violation_flags = [
            attention_inequality_index > (1.0 - fairness_floor),
            lineage_attention_balance < fairness_floor,
            minority_lineage_protection_index < fairness_floor,
            scheduler_equity_index < fairness_floor,
        ]
        fairness_violation_rate = sum(1 for flag in violation_flags if flag) / len(violation_flags)
        constitutional_fairness_alignment = _clamp01((governance_alignment + non_closure_alignment) / 2.0)
        computational_fairness_index = _clamp01(
            0.25 * (1.0 - attention_inequality_index)
            + 0.25 * lineage_attention_balance
            + 0.20 * minority_lineage_protection_index
            + 0.15 * scheduler_equity_index
            + 0.15 * constitutional_fairness_alignment
        )
        if active <= 0 and population > 0:
            fairness_status = 'no_active_attention'
        elif fairness_violation_rate > 0.0:
            fairness_status = 'fairness_pressure_detected'
        else:
            fairness_status = 'fairness_within_bounds'
        if activity_state:
            deep_ratio = _clamp01(activity_state.get('deep_cognition_ratio'), 0.0)
        else:
            deep_ratio = 0.0 if population <= 0 else min(0.05, active * 0.05 / max(1, population))
        return {
            'primitive': PRIMITIVE_NAME,
            'primitive_key': PRIMITIVE,
            'maturity_level': MATURITY_LEVEL,
            'timestamp_utc': _now(),
            'cycle_count': self.cycle_count,
            'population_size': population,
            'active_individual_count': active,
            'inactive_individual_count': inactive,
            'lineage_count': len(lineages),
            'lineage_distribution': dict(lineages),
            'attention_by_lineage': dict(lineage_attention),
            'attention_gini_coefficient': attention_gini,
            'attention_inequality_index': attention_inequality_index,
            'population_lineage_gini_coefficient': population_gini,
            'lineage_attention_balance': lineage_attention_balance,
            'fairness_violation_rate': _clamp01(fairness_violation_rate),
            'minority_lineage_id': minority_key,
            'minority_lineage_attention_share': _clamp01(minority_attention_share),
            'minority_lineage_population_share': _clamp01(minority_population_share),
            'minority_lineage_protection_index': minority_lineage_protection_index,
            'scheduler_equity_index': scheduler_equity_index,
            'computational_fairness_index': computational_fairness_index,
            'constitutional_fairness_alignment': constitutional_fairness_alignment,
            'fairness_status': fairness_status,
            'fairness_floor': fairness_floor,
            'attention_limited_activation': bool(scheduler.get('attention_limited_activation')),
            'deep_cognition_ratio': deep_ratio,
            'governance_alignment': governance_alignment,
            'non_closure_alignment': non_closure_alignment,
            'computational_fairness_ready': True,
            'diagnostics': {
                'dependencies': DEPENDENCIES,
                'record_metrics_requested': bool(record_metrics),
                'epistemic_status': 'functional_metric_only_no_phenomenal_claim',
                'next_recommended_primitive': 'lineage_diversity_preservation',
            },
        }
