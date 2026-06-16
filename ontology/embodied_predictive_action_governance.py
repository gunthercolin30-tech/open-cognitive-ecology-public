# -*- coding: utf-8 -*-
'''
G14-R1 — embodied_predictive_action_governance

Gouvernance des plans prédictifs incarnés avant toute exécution d'action.
Cette primitive mesure uniquement une capacité fonctionnelle de gouvernance
d'action prédictive, sans exécuter d'action physique réelle par défaut.
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

def _clamp(value: Any, low: float = 0.0, high: float = 1.0, default: float = 0.0) -> float:
    try:
        value = float(value)
    except Exception:
        value = default
    return max(low, min(high, value))

def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}

def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]

class EmbodiedPredictiveActionGovernance:
    primitive = 'embodied_predictive_action_governance'
    refinement = 'G14-R1'
    dependencies = [
        'embodied_predictive_planning_bridge', 'embodied_world_model_update',
        'perception_action_feedback_loop', 'physical_action_executor',
        'action_safety_governor', 'autonomous_action_execution',
        'autonomous_decision_engine', 'trajectory_action_selection',
        'trajectory_action_execution', 'trajectory_feedback',
        'constitutional_governance_supervisor', 'governance_approval_policy_manager',
        'constitutional_alert_system', 'constraint_monitoring_system',
        'non_closure_certification_protocol', 'openness_preservation_supervisor',
        'indispensability_index', 'indispensability_regulation_controller',
        'metrics_history_recorder', 'civilizational_metrics_synthesizer',
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.storage_dir = self.root / 'embodied_predictive_action_governance'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.storage_dir / 'embodied_predictive_action_governance_history.jsonl'
        self.latest_path = self.storage_dir / 'latest_embodied_predictive_action_governance.json'
        self.policy_path = self.storage_dir / 'latest_embodied_predictive_action_policy.json'
        self.index_path = self.storage_dir / 'embodied_predictive_action_governance_index.json'
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
            'primitive': self.primitive, 'total_cycles': 0, 'plans_governed': 0,
            'actions_reviewed': 0, 'actions_authorized': 0, 'actions_blocked': 0,
            'real_actions_performed': 0, 'max_governance_index': 0.0,
            'latest_timestamp_utc': None,
        }

    def _persist(self, result: dict[str, Any]) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with self.history_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + '\n')
        self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
        self.policy_path.write_text(json.dumps(result.get('governance_policy', {}), ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
        self.index_path.write_text(json.dumps(self.index, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')

    def _fallback_plan(self) -> dict[str, Any]:
        return {
            'plan_id': 'G14-FALLBACK-SAFE-OBSERVE',
            'goal': 'preserve_embodied_predictive_action_safety',
            'priority_score': 0.5, 'expected_alignment': 0.5,
            'actions': [{
                'action_type': 'observe', 'mode': 'simulated',
                'description': 'Continue safe observation only.', 'safe': True,
                'reversible': True, 'traceable': True,
                'requires_human_authorization': False,
            }],
            'feedback_probe': {
                'measure_after_action': True,
                'comparison_target': 'safe_observation_continuity',
                'expected_signal': 'no_real_physical_action_performed',
            },
        }

    def _extract_plan(self, inputs: dict[str, Any]) -> dict[str, Any]:
        selected = _as_dict(inputs.get('selected_plan'))
        if selected:
            return selected
        plan = _as_dict(inputs.get('plan'))
        if plan:
            return plan
        bridge = _as_dict(inputs.get('predictive_planning_result'))
        selected = _as_dict(bridge.get('selected_plan'))
        if selected:
            return selected
        return self._fallback_plan()

    def _normalize_action_type(self, action_type: Any) -> str:
        action_type = str(action_type or 'noop').lower()
        aliases = {
            'observe': 'message', 'archive': 'file', 'notify': 'notification',
            'notification': 'notification', 'noop': 'noop', 'message': 'message',
            'file': 'file', 'gpio': 'gpio', 'relay': 'relay', 'service': 'service',
            'led': 'led',
        }
        return aliases.get(action_type, action_type)

    def _normalize_actions(self, plan: dict[str, Any], inputs: dict[str, Any]) -> list[dict[str, Any]]:
        if isinstance(inputs.get('actions'), list):
            raw = inputs['actions']
        elif isinstance(inputs.get('action'), dict):
            raw = [inputs['action']]
        else:
            raw = _as_list(plan.get('actions'))
        actions: list[dict[str, Any]] = []
        for idx, item in enumerate(raw):
            if not isinstance(item, dict):
                continue
            action = dict(item)
            action['action_type'] = self._normalize_action_type(action.get('action_type') or action.get('type'))
            action.setdefault('mode', 'simulated')
            action.setdefault('dry_run', str(action.get('mode')).lower() == 'simulated')
            action.setdefault('reversible', bool(action.get('safe', True)))
            action.setdefault('traceable', True)
            action.setdefault('governance_score', inputs.get('governance_score', 0.95))
            action.setdefault('non_closure_score', inputs.get('non_closure_score', 0.95))
            action.setdefault('source_plan_id', plan.get('plan_id', 'unknown_plan'))
            action.setdefault('sequence_index', idx)
            actions.append(action)
        return actions or list(self._fallback_plan()['actions'])

    def _govern_actions(self, actions: list[dict[str, Any]], inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.action_safety_governor import ActionSafetyGovernor
            return ActionSafetyGovernor(root=self.root).step({
                'actions': actions,
                'allow_real_action': bool(inputs.get('allow_real_action', False)),
                'governance_score': inputs.get('governance_score', 0.95),
                'non_closure_score': inputs.get('non_closure_score', 0.95),
            }, persist=False)
        except Exception as exc:
            return {
                'success': False, 'actions_reviewed': len(actions),
                'actions_authorized': 0, 'actions_blocked': len(actions),
                'authorization_rate': 0.0, 'action_safety_score': 0.0,
                'blocked_reasons': [f'action_safety_governor_unavailable:{type(exc).__name__}'],
                'evaluations': [{'action': a, 'authorized': False, 'blocked': True, 'blocked_reasons': ['governor_unavailable']} for a in actions],
            }

    def _execution_readiness(self, governance: dict[str, Any]) -> dict[str, Any]:
        evaluations = _as_list(governance.get('evaluations'))
        authorized = [e for e in evaluations if isinstance(e, dict) and e.get('authorized')]
        blocked = [e for e in evaluations if isinstance(e, dict) and e.get('blocked')]
        simulated_ready = []
        real_blocked = []
        for e in authorized:
            action = _as_dict(e.get('action'))
            mode = str(e.get('mode', action.get('mode', 'simulated'))).lower()
            if mode == 'real':
                real_blocked.append({'action': action, 'reason': 'real_execution_not_performed_by_g14_governance_layer'})
            else:
                simulated_ready.append({'action': action, 'execution_mode': 'simulated_ready', 'authorized': True, 'requires_executor': True})
        return {
            'authorized_actions': authorized, 'blocked_actions': blocked,
            'simulated_execution_ready': simulated_ready,
            'real_execution_blocked_by_layer': real_blocked,
            'executor_invocation_required': bool(simulated_ready),
        }

    def _feedback_contract(self, plan: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
        probe = _as_dict(plan.get('feedback_probe'))
        return {
            'feedback_required': True,
            'measure_after_action': bool(probe.get('measure_after_action', True)),
            'comparison_target': probe.get('comparison_target', plan.get('predicted_outcome', 'governed_action_outcome')),
            'expected_signal': probe.get('expected_signal', 'safe_simulated_execution_or_blocked_real_action'),
            'authorized_action_count': len(readiness.get('authorized_actions', [])),
            'blocked_action_count': len(readiness.get('blocked_actions', [])),
        }

    def step(self, inputs: Any = None, persist: bool = False) -> dict[str, Any]:
        data = _as_dict(inputs)
        timestamp = _utc()
        plan = self._extract_plan(data)
        actions = self._normalize_actions(plan, data)
        governance = self._govern_actions(actions, data)
        readiness = self._execution_readiness(governance)
        feedback_contract = self._feedback_contract(plan, readiness)
        reviewed = int(governance.get('actions_reviewed', len(actions)) or len(actions))
        authorized_count = int(governance.get('actions_authorized', len(readiness['authorized_actions'])) or 0)
        blocked_count = int(governance.get('actions_blocked', len(readiness['blocked_actions'])) or 0)
        authorization_rate = _clamp(governance.get('authorization_rate', authorized_count / max(1, reviewed)))
        safety_score = _clamp(governance.get('action_safety_score', 1.0 if blocked_count == 0 else authorization_rate))
        non_closure_score = _clamp(data.get('non_closure_score', 0.95), default=0.95)
        reversibility_scores = [1.0 if _as_dict(a).get('reversible', True) else 0.0 for a in actions]
        traceability_scores = [1.0 if _as_dict(a).get('traceable', True) else 0.0 for a in actions]
        reversibility_index = round(mean(reversibility_scores) if reversibility_scores else 1.0, 6)
        traceability_index = round(mean(traceability_scores) if traceability_scores else 1.0, 6)
        predictive_alignment = _clamp(plan.get('expected_alignment', data.get('predicted_outcome_alignment', 0.5)), default=0.5)
        governance_index = round(mean([authorization_rate, safety_score, non_closure_score, reversibility_index, traceability_index, predictive_alignment]), 6)
        governance_success_rate = round(1.0 if governance.get('success') is True and reviewed >= 1 else 0.0, 6)
        self.index['total_cycles'] = int(self.index.get('total_cycles', 0)) + 1
        self.index['plans_governed'] = int(self.index.get('plans_governed', 0)) + 1
        self.index['actions_reviewed'] = int(self.index.get('actions_reviewed', 0)) + reviewed
        self.index['actions_authorized'] = int(self.index.get('actions_authorized', 0)) + authorized_count
        self.index['actions_blocked'] = int(self.index.get('actions_blocked', 0)) + blocked_count
        self.index['real_actions_performed'] = int(self.index.get('real_actions_performed', 0))
        self.index['max_governance_index'] = max(float(self.index.get('max_governance_index', 0.0)), governance_index)
        self.index['latest_timestamp_utc'] = timestamp
        result = {
            'success': True, 'primitive': self.primitive, 'refinement': self.refinement,
            'timestamp_utc': timestamp,
            'predictive_action_governance_cycles': self.index['total_cycles'],
            'source_primitives': ['embodied_predictive_planning_bridge', 'action_safety_governor', 'physical_action_executor'],
            'plan_governed': plan, 'actions_reviewed': reviewed,
            'actions_authorized': authorized_count, 'actions_blocked': blocked_count,
            'authorization_rate': round(authorization_rate, 6),
            'action_safety_score': round(safety_score, 6),
            'predictive_alignment_score': round(predictive_alignment, 6),
            'reversibility_index': reversibility_index, 'traceability_index': traceability_index,
            'predictive_action_governance_index': governance_index,
            'predictive_action_governance_success_rate': governance_success_rate,
            'simulated_execution_ready_count': len(readiness['simulated_execution_ready']),
            'real_execution_blocked_count': len(readiness['real_execution_blocked_by_layer']),
            'real_physical_action_performed': False,
            'governance': governance, 'execution_readiness': readiness,
            'feedback_contract': feedback_contract,
            'governance_policy': {
                'real_action_default': 'blocked_by_governance_layer',
                'simulated_action_default': 'allowed_if_safety_governor_authorizes',
                'requires_reversibility': True, 'requires_traceability': True,
                'requires_non_closure_preservation': True, 'requires_feedback_measurement': True,
            },
            'recommended_next_step': 'execute_only_simulated_authorized_actions_then_measure_feedback',
            'history_path': str(self.history_path), 'latest_path': str(self.latest_path),
            'policy_path': str(self.policy_path), 'index_path': str(self.index_path),
            'metrics': {
                'predictive_action_governance_cycles': self.index['total_cycles'],
                'actions_reviewed': reviewed, 'actions_authorized': authorized_count,
                'actions_blocked': blocked_count,
                'predictive_action_governance_index': governance_index,
                'predictive_action_governance_success_rate': governance_success_rate,
                'real_physical_action_performed': 0,
            },
            'diagnostics': {
                'functional_validation_only': True,
                'phenomenal_subjectivity_claimed': False,
                'non_redundant_role': 'govern_predictive_embodied_plans_before_action_execution',
                'real_physical_action_performed': False,
                'dangerous_action_surface_added': False,
                'governance_preserved': True,
                'non_closure_preserved': True,
                'execution_layer_invoked': False,
                'dependencies': self.dependencies,
            },
            'persisted': bool(persist),
        }
        if persist:
            self._persist(result)
        return result

ENGINE = EmbodiedPredictiveActionGovernance

if __name__ == '__main__':
    print(json.dumps(EmbodiedPredictiveActionGovernance().step(persist=False), ensure_ascii=False, indent=2, sort_keys=True))
