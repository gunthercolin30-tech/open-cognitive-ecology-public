'''
P3 - Activity Gradient Manager.

This module distributes a population across five functional activity levels:
existence, maintenance, interaction, reflection, and deep_cognition.

The implementation validates functional and measurable properties only. It
makes no claim about phenomenal subjectivity.
'''
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ActivityGradientManager:
    '''Distribute active and inactive individuals across activity levels.'''

    baseline_individual_attention_cost: float = 0.001
    maintenance_share: float = 0.50
    interaction_share: float = 0.30
    reflection_share: float = 0.15
    deep_cognition_share: float = 0.05

    def _clamp_non_negative_int(self, value: int | float | None) -> int:
        try:
            return max(0, int(value or 0))
        except Exception:
            return 0

    def _clamp_non_negative_float(self, value: int | float | None) -> float:
        try:
            return max(0.0, float(value or 0.0))
        except Exception:
            return 0.0

    def _activation_result(self, population_size: int, available_attention_budget: float) -> Dict[str, Any]:
        try:
            from ontology.population_activation_scheduler import PopulationActivationScheduler
            return PopulationActivationScheduler().step(
                population_size=population_size,
                available_attention_budget=available_attention_budget,
            )
        except Exception as exc:
            population = self._clamp_non_negative_int(population_size)
            budget = self._clamp_non_negative_float(available_attention_budget)
            if population <= 0:
                return {
                    'active_individual_count': 0,
                    'inactive_individual_count': 0,
                    'activation_rate': 0.0,
                    'attention_limited_activation': False,
                    'activation_pressure': 0.0,
                    'activation_pressure_status': 'no_population',
                    'scheduler_fallback_reason': repr(exc),
                }
            if budget <= 0.0:
                return {
                    'active_individual_count': 0,
                    'inactive_individual_count': population,
                    'activation_rate': 0.0,
                    'attention_limited_activation': True,
                    'activation_pressure': None,
                    'activation_pressure_status': 'infinite_activation_pressure',
                    'scheduler_fallback_reason': repr(exc),
                }
            capacity = int(budget / self.baseline_individual_attention_cost)
            active = max(1, min(population, capacity))
            pressure = population / max(active, 1)
            return {
                'active_individual_count': active,
                'inactive_individual_count': population - active,
                'activation_rate': active / population,
                'attention_limited_activation': active < population,
                'activation_pressure': pressure,
                'activation_pressure_status': 'finite_activation_pressure',
                'scheduler_fallback_reason': repr(exc),
            }

    def _split_active_levels(self, active_count: int) -> Dict[str, int]:
        active = max(0, int(active_count))
        if active <= 0:
            return {
                'maintenance_count': 0,
                'interaction_count': 0,
                'reflection_count': 0,
                'deep_cognition_count': 0,
            }
        deep = int(active * self.deep_cognition_share)
        reflection = int(active * self.reflection_share)
        interaction = int(active * self.interaction_share)
        if active >= 20:
            deep = max(1, deep)
        if active >= 10:
            reflection = max(deep, max(1, reflection))
        if active >= 2:
            interaction = max(reflection, max(1, interaction))
        deep = min(deep, active)
        reflection = min(reflection, active - deep)
        interaction = min(interaction, active - deep - reflection)
        maintenance = active - deep - reflection - interaction
        if maintenance < interaction and active >= 4:
            deficit = interaction - maintenance
            take_from_interaction = min(deficit, max(0, interaction - reflection))
            interaction -= take_from_interaction
            maintenance += take_from_interaction
        return {
            'maintenance_count': max(0, maintenance),
            'interaction_count': max(0, interaction),
            'reflection_count': max(0, reflection),
            'deep_cognition_count': max(0, deep),
        }

    def step(self, population_size: int = 1000, available_attention_budget: float = 1.0, **kwargs: Any) -> Dict[str, Any]:
        '''Compute the activity gradient for a population and attention budget.'''
        population = self._clamp_non_negative_int(population_size)
        budget = self._clamp_non_negative_float(available_attention_budget)
        activation = self._activation_result(population, budget)
        active = self._clamp_non_negative_int(activation.get('active_individual_count', 0))
        active = min(active, population)
        inactive = max(0, population - active)
        active_levels = self._split_active_levels(active)
        existence_count = inactive
        maintenance_count = active_levels['maintenance_count']
        interaction_count = active_levels['interaction_count']
        reflection_count = active_levels['reflection_count']
        deep_cognition_count = active_levels['deep_cognition_count']
        total_gradient_count = existence_count + maintenance_count + interaction_count + reflection_count + deep_cognition_count
        denominator = max(1, population)
        existence_ratio = existence_count / denominator
        maintenance_ratio = maintenance_count / denominator
        interaction_ratio = interaction_count / denominator
        reflection_ratio = reflection_count / denominator
        deep_cognition_ratio = deep_cognition_count / denominator
        hierarchy_valid = deep_cognition_count <= reflection_count <= interaction_count
        pressure = activation.get('activation_pressure')
        pressure_status = activation.get('activation_pressure_status', 'finite_activation_pressure')
        if pressure is None:
            gradient_pressure = None
            gradient_pressure_status = 'infinite_gradient_pressure'
        elif population <= 0:
            gradient_pressure = 0.0
            gradient_pressure_status = 'no_population'
        else:
            gradient_pressure = float(pressure)
            gradient_pressure_status = 'saturated_gradient' if gradient_pressure >= 10.0 else 'bounded_gradient'
        non_empty_levels = sum(1 for value in [existence_count, maintenance_count, interaction_count, reflection_count, deep_cognition_count] if value > 0)
        activity_gradient_balance = non_empty_levels / 5.0
        all_individuals_have_activity_state = total_gradient_count == population
        return {
            'primitive': 'ACTIVITY_GRADIENT_MANAGER',
            'population_size': population,
            'available_attention_budget': budget,
            'active_individual_count': active,
            'inactive_individual_count': inactive,
            'existence_count': existence_count,
            'maintenance_count': maintenance_count,
            'interaction_count': interaction_count,
            'reflection_count': reflection_count,
            'deep_cognition_count': deep_cognition_count,
            'total_gradient_count': total_gradient_count,
            'existence_ratio': existence_ratio,
            'maintenance_ratio': maintenance_ratio,
            'interaction_ratio': interaction_ratio,
            'reflection_ratio': reflection_ratio,
            'deep_cognition_ratio': deep_cognition_ratio,
            'activity_gradient_balance': activity_gradient_balance,
            'activity_gradient_pressure': gradient_pressure,
            'activity_gradient_pressure_status': gradient_pressure_status,
            'activation_pressure_status': pressure_status,
            'activity_hierarchy_valid': hierarchy_valid,
            'all_individuals_have_activity_state': all_individuals_have_activity_state,
            'attention_limited_activation': bool(activation.get('attention_limited_activation', False)),
            'diagnostics': {
                'phenomenal_subjectivity_claimed': False,
                'validation_scope': 'functional_metrics_only',
                'architecture_layer': 'civilizational_attention_economy',
                'dependencies': ['population_activation_scheduler', 'civilizational_attention_allocator', 'conscious_access', 'conscious_state_regulation', 'autonomous_conscious_cycle', 'meta_cognition', 'reflective_self_assessment_loop', 'governance', 'metrics_history_recorder'],
            },
        }
