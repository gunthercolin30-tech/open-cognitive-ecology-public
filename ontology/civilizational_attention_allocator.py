# -*- coding: utf-8 -*-
'''
P1 — Civilizational Attention Allocator.

This primitive governs the allocation of finite computational attention across
an artificial civilization under resource, fairness, lineage and non-closure
constraints. It does not assert phenomenal subjectivity. It measures functional
allocation properties only.

Core metrics:
- attention_budget
- attention_allocation_index
- attention_fairness_index
- civilizational_attention_pressure
- attention_saturation_index
- active_attention_capacity
- minimum_attention_floor
'''

from __future__ import annotations

from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

PRIMITIVE = "civilizational_attention_allocator"
PRIMITIVE_NAME = "CIVILIZATIONAL_ATTENTION_ALLOCATOR"
MATURITY_LEVEL = "P1_OPERATIONAL"

DEPENDENCIES = [
    "attention_allocation",
    "cognitive_resource_economy",
    "autonomous_resource_manager",
    "resource_allocation",
    "metrics_history_recorder",
    "governance",
    "carrying_capacity",
    "constraint_monitoring_system",
    "anti_closure_metaconstraint",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def _clamp01(value: Any, default: float = 0.0) -> float:
    number = _safe_float(value, default)
    return max(0.0, min(1.0, number))


def _safe_population(value: Any) -> int:
    try:
        population = int(value)
    except Exception:
        population = 0
    return max(0, population)


def _gini(values: list[float]) -> float:
    cleaned = [max(0.0, _safe_float(v)) for v in values]
    n = len(cleaned)
    if n <= 1:
        return 0.0
    total = sum(cleaned)
    if total <= 0.0:
        return 0.0
    sorted_values = sorted(cleaned)
    weighted_sum = sum((index + 1) * value for index, value in enumerate(sorted_values))
    return max(0.0, min(1.0, (2.0 * weighted_sum) / (n * total) - (n + 1.0) / n))


def _normalized_entropy_from_counts(counts: Mapping[str, int]) -> float:
    total = sum(max(0, int(v)) for v in counts.values())
    if total <= 0 or len(counts) <= 1:
        return 1.0 if total > 0 else 0.0
    entropy = 0.0
    for value in counts.values():
        count = max(0, int(value))
        if count <= 0:
            continue
        p = count / total
        entropy -= p * math.log(p)
    maximum = math.log(len(counts))
    if maximum <= 0.0:
        return 1.0
    return _clamp01(entropy / maximum)


class CivilizationalAttentionAllocator:
    '''Allocate finite attention across a population under governance constraints.'''

    primitive = PRIMITIVE

    def __init__(
        self,
        root: str | Path | None = None,
        nominal_attention_need: float = 0.001,
        minimum_attention_floor: float = 0.000001,
        saturation_reference_population: int = 1000,
    ) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.nominal_attention_need = max(1e-12, _safe_float(nominal_attention_need, 0.001))
        self.minimum_attention_floor = max(0.0, _safe_float(minimum_attention_floor, 0.000001))
        self.saturation_reference_population = max(1, int(saturation_reference_population))
        self.cycle_count = 0

    def _lineage_counts(self, population_size: int, lineages: Any = None) -> dict[str, int]:
        if population_size <= 0:
            return {}
        if isinstance(lineages, Mapping):
            counts: dict[str, int] = {}
            for value in lineages.values():
                key = str(value or "unknown")
                counts[key] = counts.get(key, 0) + 1
            if counts:
                return counts
        if isinstance(lineages, Iterable) and not isinstance(lineages, (str, bytes, dict)):
            counts = {}
            for value in lineages:
                key = str(value or "unknown")
                counts[key] = counts.get(key, 0) + 1
            if counts:
                return counts
        return {"default_lineage": population_size}

    def _sampled_allocations(
        self,
        population_size: int,
        budget: float,
        individual_demands: Any = None,
    ) -> tuple[list[float], float, float]:
        if population_size <= 0 or budget <= 0.0:
            return [], 0.0, 0.0

        if isinstance(individual_demands, Mapping):
            demands = [max(0.0, _safe_float(v, 1.0)) for v in individual_demands.values()]
        elif isinstance(individual_demands, Iterable) and not isinstance(individual_demands, (str, bytes)):
            demands = [max(0.0, _safe_float(v, 1.0)) for v in individual_demands]
        else:
            # Analytical uniform mode for massive populations: no per-individual list is created.
            attention_per_individual = budget / population_size
            effective_floor = min(attention_per_individual, self.minimum_attention_floor)
            return [attention_per_individual], attention_per_individual, effective_floor

        if not demands:
            attention_per_individual = budget / population_size
            return [attention_per_individual], attention_per_individual, min(attention_per_individual, self.minimum_attention_floor)

        # Keep validation and tests lightweight when an explicit huge vector is supplied.
        max_sample = 10000
        if len(demands) > max_sample:
            stride = max(1, len(demands) // max_sample)
            demands = demands[::stride][:max_sample]

        total_demand = sum(demands)
        if total_demand <= 0.0:
            allocations = [budget / max(1, len(demands)) for _ in demands]
        else:
            allocations = [budget * demand / total_demand for demand in demands]

        if self.minimum_attention_floor > 0.0 and allocations:
            floor = min(self.minimum_attention_floor, budget / max(1, population_size))
            allocations = [max(value, floor) for value in allocations]
            total = sum(allocations)
            if total > 0.0:
                allocations = [value * budget / total for value in allocations]

        mean_allocation = sum(allocations) / max(1, len(allocations))
        effective_floor = min(allocations) if allocations else 0.0
        return allocations, mean_allocation, effective_floor

    def step(
        self,
        population_size: int = 1000,
        available_attention_budget: float = 1.0,
        individual_demands: Any = None,
        lineages: Any = None,
        governance_alignment: float = 0.92,
        non_closure_alignment: float = 0.92,
        resource_availability: float = 0.95,
        record_metrics: bool = False,
    ) -> dict[str, Any]:
        self.cycle_count += 1
        population = _safe_population(population_size)
        budget = max(0.0, _safe_float(available_attention_budget, 0.0))
        governance_alignment = _clamp01(governance_alignment, 0.92)
        non_closure_alignment = _clamp01(non_closure_alignment, 0.92)
        resource_availability = _clamp01(resource_availability, 0.95)

        total_nominal_need = population * self.nominal_attention_need
        active_attention_capacity = 0 if self.nominal_attention_need <= 0 else int(budget / self.nominal_attention_need)
        active_attention_capacity = max(0, min(population, active_attention_capacity))

        if population <= 0:
            allocation_index = 1.0 if budget > 0.0 else 0.0
            attention_pressure = 0.0
            attention_pressure_status = "no_population"
            saturation = 0.0
            attention_saturation_status = "unsaturated"
        elif budget <= 0.0:
            allocation_index = 0.0
            attention_pressure = None
            attention_pressure_status = "infinite_pressure"
            saturation = 1.0
            attention_saturation_status = "saturated"
        else:
            allocation_index = _clamp01(budget / max(total_nominal_need, 1e-12))
            attention_pressure = total_nominal_need / budget
            attention_pressure_status = "finite_pressure"
            saturation = _clamp01(attention_pressure / (1.0 + attention_pressure))
            attention_saturation_status = "saturated" if saturation >= 0.95 else "bounded"

        allocations, mean_allocation, effective_floor = self._sampled_allocations(
            population,
            budget,
            individual_demands,
        )
        inequality = _gini(allocations)
        attention_fairness_index = _clamp01(1.0 - inequality)

        lineage_counts = self._lineage_counts(population, lineages)
        lineage_diversity_index = _normalized_entropy_from_counts(lineage_counts)
        lineage_attention_balance = _clamp01((attention_fairness_index + lineage_diversity_index) / 2.0)

        governance_constraint_score = _clamp01((governance_alignment + non_closure_alignment) / 2.0)
        civilizational_attention_viability = _clamp01(
            0.30 * allocation_index
            + 0.25 * attention_fairness_index
            + 0.20 * lineage_attention_balance
            + 0.15 * governance_constraint_score
            + 0.10 * resource_availability
        )

        attention_allocation_ready = (
            population > 0
            and budget > 0.0
            and governance_constraint_score >= 0.75
            and attention_fairness_index >= 0.70
        )

        result = {
            "primitive": PRIMITIVE_NAME,
            "timestamp_utc": _now(),
            "cycle_count": self.cycle_count,
            "population_size": population,
            "attention_budget": budget,
            "available_attention_budget": budget,
            "nominal_attention_need": self.nominal_attention_need,
            "total_nominal_attention_need": total_nominal_need,
            "active_attention_capacity": active_attention_capacity,
            "attention_allocation_index": allocation_index,
            "attention_fairness_index": attention_fairness_index,
            "attention_inequality_index": inequality,
            "lineage_diversity_index": lineage_diversity_index,
            "lineage_attention_balance": lineage_attention_balance,
            "civilizational_attention_pressure": attention_pressure,
            "attention_pressure": attention_pressure,
            "attention_pressure_status": attention_pressure_status,
            "attention_saturation_index": saturation,
            "attention_saturation_status": attention_saturation_status,
            "mean_attention_per_individual": mean_allocation,
            "minimum_attention_floor": effective_floor,
            "governance_constraint_score": governance_constraint_score,
            "resource_availability": resource_availability,
            "civilizational_attention_viability": civilizational_attention_viability,
            "attention_allocation_ready": attention_allocation_ready,
            "record_metrics_requested": bool(record_metrics),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "lineage_count": len(lineage_counts),
                "lineage_counts_sample": dict(list(lineage_counts.items())[:20]),
                "allocation_mode": "sampled" if individual_demands is not None else "analytical_uniform",
                "epistemic_scope": "functional_metrics_only_no_phenomenal_claim",
                "non_closure_compliant": non_closure_alignment >= 0.75,
                "classification": "governed_civilizational_attention_allocation",
            },
        }

        if record_metrics:
            result["metrics_recorded"] = self._record_metrics_safely(result)
        return result

    def _record_metrics_safely(self, result: dict[str, Any]) -> bool:
        try:
            from ontology.metrics_history_recorder import MetricsHistoryRecorder
            recorder = MetricsHistoryRecorder(root=self.root)
            recorder.step(result, primitive=PRIMITIVE)
            return True
        except Exception:
            return False

    def validate(self, **kwargs: Any) -> dict[str, Any]:
        result = self.step(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": bool(result["attention_allocation_ready"]),
            "attention_allocation_index": result["attention_allocation_index"],
            "attention_fairness_index": result["attention_fairness_index"],
            "civilizational_attention_viability": result["civilizational_attention_viability"],
            "diagnostics": result["diagnostics"],
        }
