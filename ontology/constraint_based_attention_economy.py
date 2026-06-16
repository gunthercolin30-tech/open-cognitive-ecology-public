from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


@dataclass
class ConstraintBasedAttentionEconomy:
    # P6 - Constraint-Based Attention Economy.
    # P6-R1 integrates diversity_state from LineageDiversityPreservation.
    primitive: str = "CONSTRAINT_BASED_ATTENTION_ECONOMY"
    reference_capacity: int = 1000

    def _attention_state(
        self,
        population_size: int,
        available_attention_budget: float,
        attention_state: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        if attention_state:
            pressure = attention_state.get("civilizational_attention_pressure")
            saturation = _safe_float(
                attention_state.get("attention_saturation_index"),
                1.0,
            )
            reserve = _safe_float(
                attention_state.get("civilizational_attention_reserve"),
                1.0 - saturation,
            )
            status = attention_state.get(
                "attention_pressure_status",
                "finite_constraint_attention_pressure",
            )
            return {
                "pressure": pressure,
                "saturation": _clamp(saturation),
                "reserve": _clamp(reserve),
                "status": status,
            }

        pop = max(0, int(population_size))
        budget = max(0.0, float(available_attention_budget))

        if budget <= 0.0:
            return {
                "pressure": None,
                "saturation": 1.0 if pop > 0 else 0.0,
                "reserve": 0.0 if pop > 0 else 1.0,
                "status": "infinite_constraint_attention_pressure",
            }

        pressure = (pop / max(1, self.reference_capacity)) / budget
        saturation = pressure / (1.0 + pressure)
        return {
            "pressure": pressure,
            "saturation": _clamp(saturation),
            "reserve": _clamp(1.0 - saturation),
            "status": "finite_constraint_attention_pressure",
        }

    def step(
        self,
        population_size: int = 1000,
        available_attention_budget: float = 1.0,
        attention_state: Mapping[str, Any] | None = None,
        scheduler_state: Mapping[str, Any] | None = None,
        activity_state: Mapping[str, Any] | None = None,
        fairness_state: Mapping[str, Any] | None = None,
        diversity_state: Mapping[str, Any] | None = None,
        constraint_intensity: float = 0.2,
        carrying_capacity_index: float = 0.9,
        global_viability_score: float = 0.9,
    ) -> dict[str, Any]:
        pop = max(0, int(population_size))
        budget = max(0.0, float(available_attention_budget))
        attention = self._attention_state(pop, budget, attention_state)

        saturation = _clamp(attention["saturation"])
        reserve = _clamp(attention["reserve"])

        if budget <= 0.0 and pop > 0:
            return {
                "primitive": self.primitive,
                "population_size": pop,
                "available_attention_budget": budget,
                "civilizational_attention_pressure": None,
                "attention_pressure_status": "infinite_constraint_attention_pressure",
                "attention_saturation_index": 1.0,
                "attention_viability_index": 0.0,
                "attention_constraint_compliance": 0.0,
                "attention_resource_efficiency": 0.0,
                "civilizational_attention_reserve": 0.0,
                "attention_economy_balance": 0.0,
                "diversity_modulation_index": 0.0,
                "diversity_integrated": diversity_state is not None,
                "economy_status": "attention_economy_suspended_no_attention",
                "diagnostics": {
                    "budget_zero": True,
                    "p6_r1_diversity_state_supported": True,
                },
            }

        active_count = _safe_float(
            (scheduler_state or {}).get("active_individual_count"),
            min(pop, max(1, int(budget * self.reference_capacity))) if pop else 0,
        )
        activation_rate = _safe_float(
            (scheduler_state or {}).get("activation_rate"),
            active_count / max(1, pop) if pop else 0.0,
        )
        deep_ratio = _safe_float(
            (activity_state or {}).get("deep_cognition_ratio"),
            min(0.05, activation_rate * 0.05),
        )

        fairness_index = _safe_float(
            (fairness_state or {}).get("computational_fairness_index"),
            0.9,
        )
        fairness_violation = _safe_float(
            (fairness_state or {}).get("fairness_violation_rate"),
            1.0 - fairness_index,
        )

        lineage_preservation = _safe_float(
            (diversity_state or {}).get("lineage_preservation_score"),
            0.9,
        )
        lineage_diversity = _safe_float(
            (diversity_state or {}).get("lineage_diversity_index"),
            lineage_preservation,
        )
        extinction_risk = _safe_float(
            (diversity_state or {}).get("lineage_extinction_risk"),
            1.0 - lineage_preservation,
        )
        attention_diversity = _safe_float(
            (diversity_state or {}).get("attention_diversity_index"),
            lineage_preservation,
        )

        constraint = _clamp(constraint_intensity)
        carrying = _clamp(carrying_capacity_index)
        global_viability = _clamp(global_viability_score)

        diversity_modulation = _clamp(
            0.40 * lineage_preservation
            + 0.25 * lineage_diversity
            + 0.20 * attention_diversity
            + 0.15 * (1.0 - extinction_risk)
        )

        attention_viability = _clamp(
            0.35 * (1.0 - saturation)
            + 0.20 * reserve
            + 0.15 * fairness_index
            + 0.15 * diversity_modulation
            + 0.15 * global_viability
        )
        constraint_compliance = _clamp(
            0.35 * (1.0 - constraint)
            + 0.20 * carrying
            + 0.20 * fairness_index
            + 0.15 * diversity_modulation
            + 0.10 * global_viability
        )
        resource_efficiency = _clamp(
            0.40 * (active_count / max(1.0, budget * self.reference_capacity))
            + 0.20 * (1.0 - saturation)
            + 0.15 * (1.0 - fairness_violation)
            + 0.15 * diversity_modulation
            + 0.10 * min(1.0, deep_ratio * 20.0)
        )
        balance = _clamp(
            0.30 * attention_viability
            + 0.25 * constraint_compliance
            + 0.20 * resource_efficiency
            + 0.15 * diversity_modulation
            + 0.10 * reserve
        )

        if balance >= 0.85:
            status = "constraint_based_attention_economy_stable"
        elif balance >= 0.65:
            status = "attention_economy_under_pressure"
        elif balance > 0.0:
            status = "attention_economy_at_risk"
        else:
            status = "attention_economy_collapsed"

        return {
            "primitive": self.primitive,
            "population_size": pop,
            "available_attention_budget": budget,
            "civilizational_attention_pressure": attention["pressure"],
            "attention_pressure_status": attention["status"],
            "attention_saturation_index": saturation,
            "attention_viability_index": attention_viability,
            "attention_constraint_compliance": constraint_compliance,
            "attention_resource_efficiency": resource_efficiency,
            "civilizational_attention_reserve": reserve,
            "attention_economy_balance": balance,
            "diversity_modulation_index": diversity_modulation,
            "diversity_integrated": diversity_state is not None,
            "lineage_preservation_score": _clamp(lineage_preservation),
            "lineage_extinction_risk": _clamp(extinction_risk),
            "economy_status": status,
            "diagnostics": {
                "active_individual_count": active_count,
                "activation_rate": activation_rate,
                "deep_cognition_ratio": deep_ratio,
                "computational_fairness_index": fairness_index,
                "fairness_violation_rate": fairness_violation,
                "constraint_intensity": constraint,
                "carrying_capacity_index": carrying,
                "global_viability_score": global_viability,
                "p6_r1_diversity_state_supported": True,
            },
        }


__all__ = ["ConstraintBasedAttentionEconomy"]
