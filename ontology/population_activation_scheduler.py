# -*- coding: utf-8 -*-
'''
P2 — Population Activation Scheduler.

This primitive decides which individuals receive active computational attention
under a finite civilizational attention budget. It operates only on functional
activation metrics and does not assert phenomenal subjectivity.

Core metrics:
- active_individual_count
- inactive_individual_count
- activation_rate
- deactivation_rate
- activation_capacity
- attention_limited_activation
- activation_pressure
- scheduler_fairness_index
'''

from __future__ import annotations

from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PRIMITIVE = "population_activation_scheduler"
PRIMITIVE_NAME = "POPULATION_ACTIVATION_SCHEDULER"
MATURITY_LEVEL = "P2_OPERATIONAL"

DEPENDENCIES = [
    "civilizational_attention_allocator",
    "artificial_society_runtime",
    "autonomous_society_scheduler",
    "individual_lifecycle_management",
    "distributed_population_runtime",
    "multi_individual_civilizational_ecology",
    "longitudinal_society_observatory",
    "metrics_history_recorder",
    "governance",
    "anti_closure_metaconstraint",
    "openness_preservation_supervisor",
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


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _clamp01(value: Any, default: float = 0.0) -> float:
    number = _safe_float(value, default)
    return max(0.0, min(1.0, number))


def _stable_id(index: int) -> str:
    return f"individual_{index:08d}"


def _extract_ids(individuals: Any, population_size: int, sample_limit: int) -> list[str]:
    if individuals is None:
        return [_stable_id(i) for i in range(min(population_size, sample_limit))]
    ids: list[str] = []
    if isinstance(individuals, Mapping):
        iterable = individuals.keys()
    elif isinstance(individuals, Iterable) and not isinstance(individuals, (str, bytes)):
        iterable = individuals
    else:
        return [_stable_id(i) for i in range(min(population_size, sample_limit))]
    for item in iterable:
        if len(ids) >= sample_limit:
            break
        if isinstance(item, Mapping):
            raw = item.get("id") or item.get("name") or item.get("individual_id")
        else:
            raw = item
        ids.append(str(raw))
    if not ids:
        ids = [_stable_id(i) for i in range(min(population_size, sample_limit))]
    return ids


class PopulationActivationScheduler:
    '''Schedule active individuals under finite civilizational attention.'''

    primitive = PRIMITIVE

    def __init__(
        self,
        root: str | Path | None = None,
        nominal_attention_need: float = 0.001,
        max_returned_active_ids: int = 10000,
    ) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.nominal_attention_need = max(1e-12, _safe_float(nominal_attention_need, 0.001))
        self.max_returned_active_ids = max(0, int(max_returned_active_ids))
        self.cycle_count = 0
        self._previous_active_sample: set[str] = set()
        self._round_robin_offset = 0

    def _derive_attention_state(
        self,
        population: int,
        available_attention_budget: float,
        attention_state: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        if attention_state:
            capacity = _safe_int(attention_state.get("active_attention_capacity"), default=-1)
            if capacity < 0:
                capacity = _safe_int(attention_state.get("activation_capacity"), default=-1)
            if capacity >= 0:
                return {
                    "attention_budget": max(0.0, _safe_float(attention_state.get("attention_budget"), available_attention_budget)),
                    "activation_capacity": max(0, min(population, capacity)),
                    "attention_allocation_index": _clamp01(attention_state.get("attention_allocation_index"), 0.0),
                    "attention_pressure_status": str(attention_state.get("attention_pressure_status", "unknown")),
                    "attention_saturation_status": str(attention_state.get("attention_saturation_status", "unknown")),
                }
        budget = max(0.0, _safe_float(available_attention_budget, 0.0))
        capacity = int(budget / self.nominal_attention_need) if budget > 0.0 else 0
        capacity = max(0, min(population, capacity))
        total_need = population * self.nominal_attention_need
        allocation_index = 1.0 if population <= 0 else _clamp01(budget / max(total_need, 1e-12))
        pressure_status = "infinite_pressure" if population > 0 and budget <= 0.0 else "finite_pressure"
        saturation_status = "saturated" if population > 0 and capacity < population else "bounded"
        return {
            "attention_budget": budget,
            "activation_capacity": capacity,
            "attention_allocation_index": allocation_index,
            "attention_pressure_status": pressure_status,
            "attention_saturation_status": saturation_status,
        }

    def _select_active_ids(self, population: int, active_count: int, individuals: Any = None) -> list[str]:
        if population <= 0 or active_count <= 0 or self.max_returned_active_ids <= 0:
            return []
        sample_size = min(population, active_count, self.max_returned_active_ids)
        ids = _extract_ids(individuals, population, min(population, self.max_returned_active_ids))
        if not ids:
            return []
        n = len(ids)
        offset = self._round_robin_offset % max(1, n)
        ordered = ids[offset:] + ids[:offset]
        selected = ordered[:min(sample_size, n)]
        self._round_robin_offset = (self._round_robin_offset + sample_size) % max(1, n)
        return selected

    def step(
        self,
        population_size: int = 1000,
        available_attention_budget: float = 1.0,
        attention_state: Mapping[str, Any] | None = None,
        individuals: Any = None,
        previous_active_individuals: Sequence[str] | set[str] | None = None,
        governance_alignment: float = 0.92,
        non_closure_alignment: float = 0.92,
        fairness_floor: float = 0.75,
        record_metrics: bool = False,
    ) -> dict[str, Any]:
        self.cycle_count += 1
        population = max(0, _safe_int(population_size, 0))
        budget = max(0.0, _safe_float(available_attention_budget, 0.0))
        governance_alignment = _clamp01(governance_alignment, 0.92)
        non_closure_alignment = _clamp01(non_closure_alignment, 0.92)
        fairness_floor = _clamp01(fairness_floor, 0.75)
        derived_attention = self._derive_attention_state(population, budget, attention_state)
        activation_capacity = max(0, min(population, _safe_int(derived_attention["activation_capacity"], 0)))
        active_count = activation_capacity
        inactive_count = max(0, population - active_count)
        active_sample = self._select_active_ids(population, active_count, individuals)
        active_sample_set = set(active_sample)
        previous_set = self._previous_active_sample if previous_active_individuals is None else {str(x) for x in previous_active_individuals}
        activated_now = active_sample_set - previous_set
        deactivated_now = previous_set - active_sample_set
        sample_denominator = max(1, len(active_sample_set | previous_set))
        activation_rate = _clamp01(len(activated_now) / sample_denominator)
        deactivation_rate = _clamp01(len(deactivated_now) / sample_denominator)
        self._previous_active_sample = active_sample_set
        active_ratio = 1.0 if population <= 0 else active_count / max(1, population)
        attention_limited_activation = population > 0 and active_count < population
        if population <= 0:
            activation_pressure = 0.0
            activation_pressure_status = "no_population"
        elif active_count <= 0:
            activation_pressure = None
            activation_pressure_status = "infinite_activation_pressure"
        else:
            activation_pressure = population / max(1, active_count)
            activation_pressure_status = "finite_activation_pressure"
        coverage_score = active_ratio
        rotation_balance = _clamp01(1.0 - abs(activation_rate - deactivation_rate))
        constitutional_score = _clamp01((governance_alignment + non_closure_alignment) / 2.0)
        scheduler_fairness_index = _clamp01(0.45 * coverage_score + 0.25 * rotation_balance + 0.30 * constitutional_score)
        fairness_status = "below_floor" if scheduler_fairness_index < fairness_floor else "within_floor"
        return {
            "primitive": PRIMITIVE_NAME,
            "primitive_key": PRIMITIVE,
            "maturity_level": MATURITY_LEVEL,
            "timestamp_utc": _now(),
            "cycle_count": self.cycle_count,
            "population_size": population,
            "attention_budget": derived_attention["attention_budget"],
            "attention_allocation_index": derived_attention["attention_allocation_index"],
            "attention_pressure_status": derived_attention["attention_pressure_status"],
            "attention_saturation_status": derived_attention["attention_saturation_status"],
            "activation_capacity": activation_capacity,
            "active_individual_count": active_count,
            "inactive_individual_count": inactive_count,
            "active_population_ratio": _clamp01(active_ratio),
            "activation_rate": activation_rate,
            "deactivation_rate": deactivation_rate,
            "activated_sample_count": len(activated_now),
            "deactivated_sample_count": len(deactivated_now),
            "attention_limited_activation": attention_limited_activation,
            "activation_pressure": activation_pressure,
            "activation_pressure_status": activation_pressure_status,
            "scheduler_fairness_index": scheduler_fairness_index,
            "scheduler_fairness_status": fairness_status,
            "governance_alignment": governance_alignment,
            "non_closure_alignment": non_closure_alignment,
            "active_individual_sample": active_sample,
            "sample_truncated": active_count > len(active_sample),
            "activation_governance_ready": True,
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "nominal_attention_need": self.nominal_attention_need,
                "record_metrics_requested": bool(record_metrics),
                "epistemic_status": "functional_metric_only_no_phenomenal_claim",
                "next_recommended_primitive": "activity_gradient_manager",
            },
        }
