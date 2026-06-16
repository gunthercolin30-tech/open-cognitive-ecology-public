
# -*- coding: utf-8 -*-
"""
F3 — Inter Individual Coordination Protocol.

This primitive coordinates multiple artificial individuals and distributed
civilizational nodes. It uses node existence (F1), node capabilities (F2),
collective/social primitives from the multi-individual phase, and distributed
runtime coordination primitives to produce measurable task allocation,
knowledge exchange, and consensus indicators.

The validation target is functional and measurable only: coordination
readiness, capability-based task distribution, knowledge sharing, consensus
ratio, and bounded coordination efficiency. No phenomenal subjectivity is
asserted.
"""


from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import importlib.util
import json
import os

PRIMITIVE = 'inter_individual_coordination_protocol'

DEPENDENCIES = [
    'distributed_civilizational_node',
    'node_capability_registry',
    'multi_individual_civilizational_ecology',
    'individual_lifecycle_management',
    'individual_dialogue_interface',
    'collective_intelligence',
    'collective_deliberation_engine',
    'intra_species_social_interaction',
    'shared_symbolic_reference',
    'distributed_knowledge_access',
    'trajectory_coordination',
    'long_term_coordination',
    'distributed_runtime_coordination',
    'distributed_runtime_coordinator',
    'autonomous_inter_node_civilizational_coordination',
    'heterogeneous_node_coordination',
    'artificial_society_runtime',
    'autonomous_society_scheduler',
    'metrics_history_recorder',
]

DEFAULT_TASKS = [
    {
        'task_id': 'coordination_monitoring',
        'required_capability': 'cpu',
        'priority': 0.82,
        'knowledge_payload': 'node_state_and_capability_summary',
    },
    {
        'task_id': 'distributed_memory_preparation',
        'required_capability': 'storage',
        'priority': 0.86,
        'knowledge_payload': 'memory_replication_candidate_set',
    },
    {
        'task_id': 'governance_consensus_probe',
        'required_capability': 'platform',
        'priority': 0.78,
        'knowledge_payload': 'constitutional_alignment_signal',
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if number != number or number in (float('inf'), float('-inf')):
        return default
    return max(0.0, min(1.0, number))


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_text(value: Any, default: str = 'unknown') -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _module_available(root: Path, primitive: str) -> bool:
    path = root / 'ontology' / f'{primitive}.py'
    if path.exists():
        return True
    return importlib.util.find_spec(f'ontology.{primitive}') is not None


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _write_json(path: Path, payload: Dict[str, Any]) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
        return True
    except Exception:
        return False


def _append_jsonl(path: Path, payload: Dict[str, Any], max_lines: int = 5000) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + '\n')
        try:
            lines = path.read_text(encoding='utf-8').splitlines()
            if len(lines) > max_lines:
                path.write_text('\n'.join(lines[-max_lines:]) + '\n', encoding='utf-8')
        except Exception:
            pass
        return True
    except Exception:
        return False


def _stable_id(parts: List[str], prefix: str) -> str:
    joined = '|'.join(_safe_text(p) for p in parts)
    digest = hashlib.sha256(joined.encode('utf-8')).hexdigest()[:16]
    return f'{prefix}-{digest}'


@dataclass
class CoordinationIndividual:
    individual_id: str
    node_id: str
    role: str
    capability_score: float
    availability: float
    trust_score: float

    def readiness(self) -> float:
        return _bounded((self.capability_score * 0.45) + (self.availability * 0.35) + (self.trust_score * 0.20))


class InterIndividualCoordinationProtocol:
    # Coordinate artificial individuals and distributed nodes.

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / 'open-cognitive-ecology'
        self.state_dir = self.root / 'distributed_nodes'
        self.protocol_path = self.state_dir / 'inter_individual_coordination_protocol.json'
        self.history_path = self.state_dir / 'inter_individual_coordination_history.jsonl'
        self.node_registry_path = self.state_dir / 'node_registry.json'
        self.capability_registry_path = self.state_dir / 'node_capability_registry.json'

    def _load_node_state(self) -> Dict[str, Any]:
        node_registry = _read_json(self.node_registry_path)
        capability_registry = _read_json(self.capability_registry_path)
        node_id = _safe_text(
            capability_registry.get('node_id') or node_registry.get('node_id') or os.environ.get('OCE_NODE_ID'),
            default=_stable_id([os.uname().nodename if hasattr(os, 'uname') else 'local'], 'oce-node')
        )
        node_name = _safe_text(
            capability_registry.get('node_name') or node_registry.get('node_name') or node_id,
            default=node_id,
        )
        capability_index = _bounded(capability_registry.get('global_capability_index'), 0.5)
        node_availability = _bounded(node_registry.get('node_availability_ratio'), 1.0)
        active_node_count = max(1, _safe_int(node_registry.get('active_node_count'), 1))
        return {
            'node_id': node_id,
            'node_name': node_name,
            'global_capability_index': capability_index,
            'node_availability_ratio': node_availability,
            'active_node_count': active_node_count,
        }

    def _dependency_status(self) -> Dict[str, Any]:
        available: List[str] = []
        missing: List[str] = []
        for dep in DEPENDENCIES:
            if _module_available(self.root, dep):
                available.append(dep)
            else:
                missing.append(dep)
        return {
            'available_dependencies': available,
            'missing_dependencies': missing,
            'available_dependency_count': len(available),
            'missing_dependency_count': len(missing),
            'dependency_readiness': _bounded(len(available) / max(1, len(DEPENDENCIES))),
        }

    def _default_individuals(self, node_state: Dict[str, Any]) -> List[CoordinationIndividual]:
        base_capability = _bounded(node_state.get('global_capability_index'), 0.5)
        availability = _bounded(node_state.get('node_availability_ratio'), 1.0)
        node_id = _safe_text(node_state.get('node_id'))
        return [
            CoordinationIndividual(
                individual_id=_stable_id([node_id, 'coordinator'], 'oce-individual'),
                node_id=node_id,
                role='coordination_steward',
                capability_score=_bounded(base_capability + 0.08),
                availability=availability,
                trust_score=0.93,
            ),
            CoordinationIndividual(
                individual_id=_stable_id([node_id, 'memory'], 'oce-individual'),
                node_id=node_id,
                role='memory_steward',
                capability_score=_bounded(base_capability + 0.04),
                availability=availability,
                trust_score=0.91,
            ),
            CoordinationIndividual(
                individual_id=_stable_id([node_id, 'governance'], 'oce-individual'),
                node_id=node_id,
                role='governance_steward',
                capability_score=_bounded(base_capability + 0.02),
                availability=availability,
                trust_score=0.94,
            ),
        ]

    def _individuals_from_input(self, inputs: Dict[str, Any], node_state: Dict[str, Any]) -> List[CoordinationIndividual]:
        raw = inputs.get('individuals')
        if not isinstance(raw, list) or not raw:
            count = _safe_int(inputs.get('individual_count'), 0)
            if count <= 0:
                return self._default_individuals(node_state)
            generated: List[CoordinationIndividual] = []
            for index in range(max(1, min(count, 50))):
                generated.append(CoordinationIndividual(
                    individual_id=_stable_id([node_state['node_id'], str(index)], 'oce-individual'),
                    node_id=_safe_text(inputs.get('node_id'), node_state['node_id']),
                    role=f'participant_{index + 1}',
                    capability_score=_bounded(inputs.get('capability_score'), 0.65),
                    availability=_bounded(inputs.get('availability'), 0.8),
                    trust_score=_bounded(inputs.get('trust_score'), 0.85),
                ))
            return generated
        individuals: List[CoordinationIndividual] = []
        for index, item in enumerate(raw[:50]):
            if not isinstance(item, dict):
                continue
            individual_id = _safe_text(item.get('individual_id'), _stable_id([node_state['node_id'], str(index)], 'oce-individual'))
            individuals.append(CoordinationIndividual(
                individual_id=individual_id,
                node_id=_safe_text(item.get('node_id'), node_state['node_id']),
                role=_safe_text(item.get('role'), f'participant_{index + 1}'),
                capability_score=_bounded(item.get('capability_score'), 0.5),
                availability=_bounded(item.get('availability'), 0.7),
                trust_score=_bounded(item.get('trust_score'), 0.8),
            ))
        return individuals or self._default_individuals(node_state)

    def _tasks_from_input(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw = inputs.get('tasks')
        if isinstance(raw, list) and raw:
            tasks: List[Dict[str, Any]] = []
            for index, item in enumerate(raw[:100]):
                if isinstance(item, dict):
                    task = dict(item)
                    task.setdefault('task_id', f'task_{index + 1}')
                    task.setdefault('required_capability', 'general')
                    task['priority'] = _bounded(task.get('priority'), 0.5)
                    task.setdefault('knowledge_payload', 'coordination_signal')
                    tasks.append(task)
            if tasks:
                return tasks
        task_count = _safe_int(inputs.get('task_count'), 0)
        if task_count > 0:
            return [
                {
                    'task_id': f'simulated_task_{i + 1}',
                    'required_capability': 'general',
                    'priority': _bounded(inputs.get('task_priority'), 0.6),
                    'knowledge_payload': 'simulated_coordination_payload',
                }
                for i in range(min(task_count, 100))
            ]
        return list(DEFAULT_TASKS)

    def _assign_tasks(self, individuals: List[CoordinationIndividual], tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        assignments: List[Dict[str, Any]] = []
        ranked = sorted(individuals, key=lambda item: item.readiness(), reverse=True)
        for index, task in enumerate(tasks):
            if not ranked:
                break
            assignee = ranked[index % len(ranked)]
            priority = _bounded(task.get('priority'), 0.5)
            assignment_quality = _bounded((assignee.readiness() * 0.75) + (priority * 0.25))
            assignments.append({
                'task_id': _safe_text(task.get('task_id'), f'task_{index + 1}'),
                'assignee_id': assignee.individual_id,
                'assignee_node_id': assignee.node_id,
                'assignee_role': assignee.role,
                'required_capability': _safe_text(task.get('required_capability'), 'general'),
                'priority': priority,
                'assignment_quality': assignment_quality,
            })
        return assignments

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = _now()
        node_state = self._load_node_state()
        deps = self._dependency_status()
        individuals = self._individuals_from_input(inputs, node_state)
        tasks = self._tasks_from_input(inputs)

        assignments = self._assign_tasks(individuals, tasks)

        individual_count = len(individuals)
        task_count = len(tasks)
        assigned_task_count = len(assignments)
        readiness_values = [person.readiness() for person in individuals]
        mean_individual_readiness = _bounded(sum(readiness_values) / max(1, len(readiness_values)))
        task_distribution_score = _bounded(assigned_task_count / max(1, task_count))
        fairness_score = _bounded(len(set(a['assignee_id'] for a in assignments)) / max(1, min(individual_count, assigned_task_count or 1)))

        consensus_signal = _bounded(inputs.get('consensus_signal'), mean_individual_readiness)
        symbolic_alignment = _bounded(inputs.get('symbolic_alignment'), 0.88)
        governance_alignment = _bounded(inputs.get('governance_alignment'), 0.9)
        distributed_consensus_ratio = _bounded(
            (consensus_signal * 0.40) +
            (symbolic_alignment * 0.25) +
            (governance_alignment * 0.25) +
            (deps['dependency_readiness'] * 0.10)
        )

        knowledge_exchange_count = _safe_int(inputs.get('knowledge_exchange_count'), assigned_task_count)
        knowledge_exchange_score = _bounded(knowledge_exchange_count / max(1, task_count))

        coordination_efficiency = _bounded(
            (mean_individual_readiness * 0.25) +
            (task_distribution_score * 0.25) +
            (fairness_score * 0.15) +
            (distributed_consensus_ratio * 0.20) +
            (knowledge_exchange_score * 0.10) +
            (deps['dependency_readiness'] * 0.05)
        )

        min_required_individuals = max(2, _safe_int(inputs.get('min_required_individuals'), 2))
        forced_degraded = bool(inputs.get('force_degraded', False))
        protocol_ready = (
            individual_count >= min_required_individuals and
            task_distribution_score >= 0.5 and
            distributed_consensus_ratio >= 0.55 and
            coordination_efficiency >= 0.55 and
            not forced_degraded
        )

        status = 'coordinated' if protocol_ready else 'degraded'

        payload: Dict[str, Any] = {
            'primitive': PRIMITIVE,
            'timestamp_utc': timestamp,
            'protocol_ready': protocol_ready,
            'status': status,
            'node_id': node_state['node_id'],
            'node_name': node_state['node_name'],
            'active_node_count': node_state['active_node_count'],
            'individual_count': individual_count,
            'task_count': task_count,
            'assigned_task_count': assigned_task_count,
            'knowledge_exchange_count': knowledge_exchange_count,
            'coordination_efficiency': round(coordination_efficiency, 4),
            'distributed_consensus_ratio': round(distributed_consensus_ratio, 4),
            'task_distribution_score': round(task_distribution_score, 4),
            'capability_matching_score': round(sum(a['assignment_quality'] for a in assignments) / max(1, len(assignments)), 4),
            'coordination_fairness_score': round(fairness_score, 4),
            'mean_individual_readiness': round(mean_individual_readiness, 4),
            'knowledge_exchange_score': round(knowledge_exchange_score, 4),
            'dependency_readiness': round(deps['dependency_readiness'], 4),
            'available_dependency_count': deps['available_dependency_count'],
            'missing_dependency_count': deps['missing_dependency_count'],
            'missing_dependencies': deps['missing_dependencies'],
            'assignments': assignments,
            'individuals': [asdict(person) for person in individuals],
            'protocol_path': str(self.protocol_path),
            'history_path': str(self.history_path),
            'diagnostics': {
                'primitive': PRIMITIVE,
                'non_redundant_role': 'capability_based_inter_individual_coordination',
                'scoring_model': 'bounded_distributed_coordination_index_v1',
                'closure_pressure_added': 0.0,
                'supports_future_phases': ['F4', 'F5', 'F6', 'F7', 'F8', 'F12'],
                'dependencies': DEPENDENCIES,
            },
        }

        payload['protocol_written'] = _write_json(self.protocol_path, payload)
        payload['history_written'] = _append_jsonl(self.history_path, payload)
        return payload
