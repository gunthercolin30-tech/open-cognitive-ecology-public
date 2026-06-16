
# -*- coding: utf-8 -*-
'''
G13-R1 — embodied_predictive_planning_bridge

Pont fonctionnel entre modèle du monde incarné, simulation prédictive,
planification incarnée, sélection d'action et feedback.

Cette primitive ne revendique aucune subjectivité phénoménale. Elle mesure
uniquement une capacité fonctionnelle de projection-action sous gouvernance.
'''


from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path.home() / 'open-cognitive-ecology'


def _utc() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    try:
        value = float(value)
    except Exception:
        value = 0.0
    return max(low, min(high, value))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


class EmbodiedPredictivePlanningBridge:
    """
    G13 — pont prédictif-planification incarnée.

    Cycle fonctionnel:
    world_model -> predictive_simulation -> plan_generation -> action_selection
    -> feedback_expectation.
    """

    primitive = 'embodied_predictive_planning_bridge'
    refinement = 'G13-R1'

    dependencies = [
        'embodied_world_model_update',
        'embodied_planning_engine',
        'world_model',
        'hierarchical_world_model_engine',
        'predictive_environment_simulator',
        'causal_inference',
        'autonomous_decision_engine',
        'trajectory_action_selection',
        'trajectory_action_execution',
        'trajectory_feedback',
        'perception_action_feedback_loop',
        'embodied_sensorimotor_ecology',
        'environmental_state_model',
        'real_world_event_detection',
        'physical_action_executor',
        'action_safety_governor',
        'metrics_history_recorder',
        'civilizational_metrics_synthesizer',
        'auto_improvement_runtime_bridge',
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.storage_dir = self.root / 'embodied_predictive_planning'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.storage_dir / 'embodied_predictive_planning_bridge_history.jsonl'
        self.latest_path = self.storage_dir / 'latest_embodied_predictive_planning_bridge.json'
        self.plan_path = self.storage_dir / 'latest_embodied_predictive_plan.json'
        self.index_path = self.storage_dir / 'embodied_predictive_planning_index.json'
        self.index = self._load_index()

    def _load_index(self) -> dict[str, Any]:
        if self.index_path.exists():
            try:
                data = json.loads(self.index_path.read_text(encoding='utf-8'))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return {
            'primitive': self.primitive,
            'total_cycles': 0,
            'successful_bridge_cycles': 0,
            'plans_generated': 0,
            'actions_selected': 0,
            'feedback_expectations_generated': 0,
            'max_predicted_alignment': 0.0,
            'latest_timestamp_utc': None,
        }

    def _persist(self, result: dict[str, Any]) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with self.history_path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + '\n')
        self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
        self.plan_path.write_text(json.dumps(result.get('selected_plan', {}), ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
        self.index_path.write_text(json.dumps(self.index, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')

    def _fallback_world_model(self) -> dict[str, Any]:
        return {
            'model_version': 0,
            'entities': {},
            'relations': [],
            'environment_state': {'status': 'unknown'},
            'predictive_readiness_index': 0.5,
            'embodied_world_model_index': 0.5,
        }

    def _extract_world_model(self, inputs: dict[str, Any]) -> dict[str, Any]:
        direct = _as_dict(inputs.get('world_model'))
        if direct:
            return direct
        model_update = _as_dict(inputs.get('world_model_update'))
        if model_update:
            wm = _as_dict(model_update.get('world_model'))
            return wm if wm else model_update
        latest_model = self.root / 'embodied_world_model' / 'latest_embodied_world_model.json'
        if latest_model.exists():
            try:
                data = json.loads(latest_model.read_text(encoding='utf-8'))
                wm = _as_dict(data.get('world_model'))
                return wm if wm else data
            except Exception:
                pass
        return self._fallback_world_model()

    def _entity_count(self, world_model: dict[str, Any]) -> int:
        entities = world_model.get('entities', {})
        if isinstance(entities, dict):
            return len(entities)
        if isinstance(entities, list):
            return len(entities)
        return 0

    def _simulate_predictions(self, inputs: dict[str, Any], world_model: dict[str, Any]) -> list[dict[str, Any]]:
        events = _as_list(inputs.get('events'))
        goals = _as_list(inputs.get('goals')) or ['maintain_environmental_continuity']
        entity_count = self._entity_count(world_model)
        readiness = _clamp(_safe_float(world_model.get('predictive_readiness_index'), 0.5))
        model_index = _clamp(_safe_float(world_model.get('embodied_world_model_index'), 0.5))
        event_pressure = _clamp(len(events) / 6.0)
        predictions: list[dict[str, Any]] = []

        if events:
            severities = [_safe_float(_as_dict(e).get('severity'), 0.0) for e in events]
            max_severity = max(severities) if severities else 0.0
            predictions.append({
                'prediction_id': 'PRED-event-stabilization',
                'target_goal': goals[0],
                'predicted_outcome': 'environmental_state_stabilized_after_event_response',
                'confidence': round(_clamp(0.45 + 0.35 * readiness + 0.2 * model_index - 0.1 * max_severity), 6),
                'risk': round(_clamp(max_severity), 6),
                'basis': 'recent_real_world_events',
            })
        else:
            predictions.append({
                'prediction_id': 'PRED-maintenance',
                'target_goal': goals[0],
                'predicted_outcome': 'stable_environmental_monitoring_continues',
                'confidence': round(_clamp(0.55 + 0.3 * readiness + 0.1 * min(entity_count, 5) / 5.0), 6),
                'risk': 0.05,
                'basis': 'world_model_fallback_or_latest_state',
            })

        if entity_count > 0:
            predictions.append({
                'prediction_id': 'PRED-entity-continuity',
                'target_goal': 'preserve_embodied_world_model_continuity',
                'predicted_outcome': 'known_entities_remain_trackable',
                'confidence': round(_clamp(0.5 + 0.3 * model_index + 0.1 * min(entity_count, 10) / 10.0), 6),
                'risk': round(_clamp(event_pressure * 0.35), 6),
                'basis': 'entity_continuity_in_world_model',
            })

        return predictions

    def _generate_candidate_plans(self, predictions: list[dict[str, Any]], inputs: dict[str, Any]) -> list[dict[str, Any]]:
        requested_actions = _as_list(inputs.get('candidate_actions'))
        if not requested_actions:
            requested_actions = [
                {'action_type': 'observe', 'mode': 'simulated', 'description': 'Continue multimodal observation.'},
                {'action_type': 'notify', 'mode': 'simulated', 'description': 'Notify operator or civilizational agent if severity is high.'},
                {'action_type': 'archive', 'mode': 'simulated', 'description': 'Archive prediction and planned response.'},
            ]
        plans: list[dict[str, Any]] = []
        for idx, pred in enumerate(predictions, start=1):
            confidence = _safe_float(pred.get('confidence'), 0.0)
            risk = _safe_float(pred.get('risk'), 0.0)
            priority = _clamp(0.55 * confidence + 0.25 * (1.0 - risk) + 0.2)
            actions = []
            for action in requested_actions:
                ad = _as_dict(action)
                action_type = str(ad.get('action_type', 'observe'))
                safe = action_type not in {'delete', 'shutdown', 'destructive', 'execute_shell'}
                actions.append({
                    'action_type': action_type,
                    'mode': ad.get('mode', 'simulated'),
                    'description': ad.get('description', f'{action_type} action'),
                    'safe': safe,
                    'requires_human_authorization': False if ad.get('mode', 'simulated') == 'simulated' else True,
                })
            plans.append({
                'plan_id': f'PLAN-{idx:03d}',
                'prediction_id': pred.get('prediction_id'),
                'goal': pred.get('target_goal'),
                'predicted_outcome': pred.get('predicted_outcome'),
                'priority_score': round(priority, 6),
                'expected_alignment': round(_clamp(confidence * (1.0 - 0.5 * risk)), 6),
                'actions': actions,
                'feedback_probe': {
                    'measure_after_action': True,
                    'comparison_target': pred.get('predicted_outcome'),
                    'expected_signal': 'reduced_environmental_uncertainty',
                },
            })
        return sorted(plans, key=lambda p: p['priority_score'], reverse=True)

    def _select_action(self, plan: dict[str, Any]) -> dict[str, Any]:
        actions = _as_list(plan.get('actions'))
        safe_actions = [a for a in actions if _as_dict(a).get('safe') is True]
        action = _as_dict(safe_actions[0] if safe_actions else {'action_type': 'observe', 'mode': 'simulated', 'safe': True})
        return {
            'selected_action_type': action.get('action_type', 'observe'),
            'selected_action_mode': action.get('mode', 'simulated'),
            'selection_reason': 'highest_priority_safe_predictive_plan',
            'requires_human_authorization': bool(action.get('requires_human_authorization', False)),
            'real_physical_action_authorized': False,
            'action': action,
        }

    def _feedback_expectation(self, selected_plan: dict[str, Any], selected_action: dict[str, Any]) -> dict[str, Any]:
        return {
            'feedback_loop_required': True,
            'expected_measurement': 'post_action_environmental_observation',
            'expected_alignment_target': selected_plan.get('predicted_outcome'),
            'selected_action_type': selected_action.get('selected_action_type'),
            'comparison_metric': 'predicted_outcome_alignment',
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False, **kwargs: Any) -> dict[str, Any]:
        if inputs is None:
            inputs = {}
        if not isinstance(inputs, dict):
            inputs = {'raw_input': inputs}
        if kwargs:
            inputs = {**inputs, **kwargs}

        timestamp = _utc()
        world_model = self._extract_world_model(inputs)
        predictions = self._simulate_predictions(inputs, world_model)
        plans = self._generate_candidate_plans(predictions, inputs)
        selected_plan = plans[0] if plans else {}
        selected_action = self._select_action(selected_plan)
        feedback_expectation = self._feedback_expectation(selected_plan, selected_action)

        alignment_values = [_safe_float(p.get('expected_alignment'), 0.0) for p in plans]
        predicted_outcome_alignment = _clamp(mean(alignment_values) if alignment_values else 0.0)
        bridge_success = bool(predictions and plans and selected_plan and selected_action)
        bridge_success_rate = 1.0 if bridge_success else 0.0
        planning_quality = _clamp(0.4 + 0.25 * len(predictions) / 3.0 + 0.25 * len(plans) / 3.0 + 0.1 * predicted_outcome_alignment)
        predictive_planning_index = _clamp(0.4 * bridge_success_rate + 0.35 * predicted_outcome_alignment + 0.25 * planning_quality)

        self.index['total_cycles'] = int(self.index.get('total_cycles', 0)) + 1
        self.index['successful_bridge_cycles'] = int(self.index.get('successful_bridge_cycles', 0)) + (1 if bridge_success else 0)
        self.index['plans_generated'] = int(self.index.get('plans_generated', 0)) + len(plans)
        self.index['actions_selected'] = int(self.index.get('actions_selected', 0)) + (1 if selected_action else 0)
        self.index['feedback_expectations_generated'] = int(self.index.get('feedback_expectations_generated', 0)) + (1 if feedback_expectation else 0)
        self.index['max_predicted_alignment'] = max(_safe_float(self.index.get('max_predicted_alignment'), 0.0), predicted_outcome_alignment)
        self.index['latest_timestamp_utc'] = timestamp

        result = {
            'success': True,
            'primitive': self.primitive,
            'refinement': self.refinement,
            'timestamp_utc': timestamp,
            'predictive_planning_cycles': self.index['total_cycles'],
            'source_primitives': ['embodied_world_model_update', 'predictive_environment_simulator', 'embodied_planning_engine', 'trajectory_action_selection', 'trajectory_feedback'],
            'world_model_entity_count': self._entity_count(world_model),
            'prediction_count': len(predictions),
            'candidate_plan_count': len(plans),
            'selected_action_count': 1 if selected_action else 0,
            'planning_bridge_success_rate': bridge_success_rate,
            'predicted_outcome_alignment': round(predicted_outcome_alignment, 6),
            'planning_quality_index': round(planning_quality, 6),
            'predictive_planning_index': round(predictive_planning_index, 6),
            'predictions': predictions,
            'candidate_plans': plans,
            'selected_plan': selected_plan,
            'selected_action': selected_action,
            'feedback_expectation': feedback_expectation,
            'bridge_index': self.index,
            'history_path': str(self.history_path),
            'latest_path': str(self.latest_path),
            'plan_path': str(self.plan_path),
            'index_path': str(self.index_path),
            'metrics': {
                'predictive_planning_cycles': self.index['total_cycles'],
                'planning_bridge_success_rate': bridge_success_rate,
                'predicted_outcome_alignment': round(predicted_outcome_alignment, 6),
                'planning_quality_index': round(planning_quality, 6),
                'predictive_planning_index': round(predictive_planning_index, 6),
                'candidate_plan_count': len(plans),
                'selected_action_count': 1 if selected_action else 0,
            },
            'diagnostics': {
                'functional_validation_only': True,
                'phenomenal_subjectivity_claimed': False,
                'non_redundant_role': 'bridge_embodied_world_model_prediction_planning_action_selection_feedback',
                'real_physical_action_performed': False,
                'real_physical_action_authorized': False,
                'dangerous_action_surface_added': False,
                'governance_preserved': True,
                'non_closure_preserved': True,
                'requires_human_authorization_for_real_action': True,
                'dependencies': self.dependencies,
            },
            'persisted': bool(persist),
        }

        if persist:
            self._persist(result)

        return result
