
from __future__ import annotations

from dataclasses import dataclass, field
from math import log, sqrt
from typing import Any, Mapping


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _normalize_distribution(data: Mapping[str, Any] | None, total: int) -> dict[str, int]:
    if total <= 0:
        return {}
    if data:
        cleaned = {str(k): _safe_int(v) for k, v in data.items() if _safe_int(v) > 0}
        if cleaned:
            return cleaned
    if total < 4:
        return {'lineage_alpha': total}
    a = int(round(total * 0.45))
    b = int(round(total * 0.30))
    c = int(round(total * 0.15))
    d = max(0, total - a - b - c)
    return {'lineage_alpha': a, 'lineage_beta': b, 'lineage_gamma': c, 'lineage_delta': d}


def _normalize_attention(attention_by_lineage: Mapping[str, Any] | None, lineage_distribution: Mapping[str, int], active_individual_count: int) -> dict[str, float]:
    if not lineage_distribution:
        return {}
    if attention_by_lineage:
        cleaned = {str(k): max(0.0, _safe_float(v)) for k, v in attention_by_lineage.items() if str(k) in lineage_distribution}
        if cleaned:
            for lineage in lineage_distribution:
                cleaned.setdefault(lineage, 0.0)
            return cleaned
    total_population = sum(lineage_distribution.values())
    if total_population <= 0:
        return {k: 0.0 for k in lineage_distribution}
    active = max(0, active_individual_count)
    return {lineage: active * (count / total_population) for lineage, count in lineage_distribution.items()}


def _shannon_evenness(counts: list[float]) -> float:
    positive = [c for c in counts if c > 0]
    n = len(positive)
    if n <= 1:
        return 1.0 if n == 1 else 0.0
    total = sum(positive)
    if total <= 0:
        return 0.0
    entropy = 0.0
    for count in positive:
        p = count / total
        entropy -= p * log(p)
    return _clamp(entropy / log(n))


def _cv_fairness(values: list[float]) -> float:
    vals = [max(0.0, float(v)) for v in values]
    if not vals:
        return 0.0
    mean = sum(vals) / len(vals)
    if mean <= 0:
        return 0.0
    variance = sum((v - mean) ** 2 for v in vals) / len(vals)
    return _clamp(1.0 / (1.0 + sqrt(variance) / mean))


def _minority_keys(lineage_distribution: Mapping[str, int]) -> list[str]:
    if not lineage_distribution:
        return []
    total = sum(lineage_distribution.values())
    if total <= 0:
        return []
    threshold = max(1.0 / max(1, len(lineage_distribution)), 0.15)
    keys = [k for k, v in lineage_distribution.items() if (v / total) <= threshold]
    if keys:
        return keys
    min_count = min(lineage_distribution.values())
    return [k for k, v in lineage_distribution.items() if v == min_count]


@dataclass
class LineageDiversityPreservation:
    '''P5 - preserve lineage diversity under attention constraints.'''

    minimum_survival_attention_ratio: float = 0.02
    preservation_threshold: float = 0.75
    history: list[dict[str, Any]] = field(default_factory=list)

    def step(self, population_size: int = 1000, available_attention_budget: float = 1.0, lineage_distribution: Mapping[str, Any] | None = None, attention_by_lineage: Mapping[str, Any] | None = None, fairness_state: Mapping[str, Any] | None = None, activity_state: Mapping[str, Any] | None = None) -> dict[str, Any]:
        population_size = _safe_int(population_size)
        available_attention_budget = max(0.0, _safe_float(available_attention_budget))
        if activity_state and 'active_individual_count' in activity_state:
            active_individual_count = _safe_int(activity_state.get('active_individual_count'))
        elif available_attention_budget <= 0.0:
            active_individual_count = 0
        else:
            active_individual_count = min(population_size, max(1, int(available_attention_budget * 1000)))

        distribution = _normalize_distribution(lineage_distribution, population_size)
        attention = _normalize_attention(attention_by_lineage, distribution, active_individual_count)
        lineage_count = len(distribution)
        total_population = sum(distribution.values())
        total_attention = sum(attention.values())

        lineage_diversity_index = _shannon_evenness([float(v) for v in distribution.values()])
        if total_attention <= 0.0:
            attention_diversity_index = 0.0 if population_size > 0 else 1.0
            attention_diversity_status = 'no_active_attention'
        else:
            attention_diversity_index = _shannon_evenness([float(v) for v in attention.values()])
            attention_diversity_status = 'attention_distributed'

        minorities = _minority_keys(distribution)
        minority_attention = sum(attention.get(k, 0.0) for k in minorities)
        minority_population = sum(distribution.get(k, 0) for k in minorities)
        if total_population <= 0 or minority_population <= 0:
            minority_lineage_survival_rate = 1.0
        elif total_attention <= 0.0:
            minority_lineage_survival_rate = 0.0
        else:
            expected_share = minority_population / total_population
            actual_share = minority_attention / total_attention
            minority_lineage_survival_rate = _clamp(actual_share / expected_share) if expected_share > 0 else 1.0

        per_capita = [attention.get(k, 0.0) / v for k, v in distribution.items() if v > 0]
        per_capita_attention_fairness = _cv_fairness(per_capita)
        if fairness_state:
            computational_fairness_index = _clamp(_safe_float(fairness_state.get('computational_fairness_index'), per_capita_attention_fairness))
            minority_lineage_protection_index = _clamp(_safe_float(fairness_state.get('minority_lineage_protection_index'), minority_lineage_survival_rate))
        else:
            computational_fairness_index = per_capita_attention_fairness
            minority_lineage_protection_index = minority_lineage_survival_rate

        lineage_extinction_risk = _clamp(1.0 - (0.35 * lineage_diversity_index + 0.25 * attention_diversity_index + 0.25 * minority_lineage_survival_rate + 0.15 * minority_lineage_protection_index))
        diversity_pressure_index = _clamp(0.50 * lineage_extinction_risk + 0.30 * (1.0 - attention_diversity_index) + 0.20 * (1.0 - computational_fairness_index))
        lineage_preservation_score = _clamp(0.30 * lineage_diversity_index + 0.25 * attention_diversity_index + 0.20 * minority_lineage_survival_rate + 0.15 * computational_fairness_index + 0.10 * minority_lineage_protection_index)
        non_closure_preservation_index = _clamp(0.50 * lineage_preservation_score + 0.30 * lineage_diversity_index + 0.20 * (1.0 - lineage_extinction_risk))

        if population_size == 0:
            preservation_status = 'empty_population'
        elif available_attention_budget <= 0.0:
            preservation_status = 'lineage_preservation_suspended_no_attention'
        elif lineage_preservation_score >= self.preservation_threshold:
            preservation_status = 'lineage_diversity_preserved'
        else:
            preservation_status = 'lineage_diversity_at_risk'

        result = {
            'primitive': 'LINEAGE_DIVERSITY_PRESERVATION',
            'population_size': population_size,
            'available_attention_budget': available_attention_budget,
            'active_individual_count': active_individual_count,
            'lineage_count': lineage_count,
            'lineage_distribution': dict(distribution),
            'attention_by_lineage': dict(attention),
            'minority_lineages': list(minorities),
            'lineage_diversity_index': lineage_diversity_index,
            'attention_diversity_index': attention_diversity_index,
            'minority_lineage_survival_rate': minority_lineage_survival_rate,
            'lineage_extinction_risk': lineage_extinction_risk,
            'lineage_preservation_score': lineage_preservation_score,
            'diversity_pressure_index': diversity_pressure_index,
            'non_closure_preservation_index': non_closure_preservation_index,
            'per_capita_attention_fairness': per_capita_attention_fairness,
            'computational_fairness_index': computational_fairness_index,
            'minority_lineage_protection_index': minority_lineage_protection_index,
            'attention_diversity_status': attention_diversity_status,
            'preservation_status': preservation_status,
            'diagnostics': {
                'program': 'P',
                'stage': 'P5',
                'bounded_indices': True,
                'non_closure_compliant': preservation_status != 'lineage_diversity_at_risk',
            },
        }
        self.history.append(result)
        return result


__all__ = ['LineageDiversityPreservation']
