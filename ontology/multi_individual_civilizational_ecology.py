# -*- coding: utf-8 -*-
'''''
Ontology bridge for multi_individual_civilizational_ecology.

The canonical implementation exists in:
    cognition.multi_individual_civilizational_ecology

This bridge keeps ontology-level dependency resolution stable for F3
(inter_individual_coordination_protocol) and future distributed phases while
avoiding a duplicate implementation.
'''''

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import importlib.util

PRIMITIVE = 'multi_individual_civilizational_ecology'
DEPENDENCIES: List[str] = [
    'individual_lifecycle_management',
    'collective_intelligence',
    'intra_species_social_interaction',
    'shared_symbolic_reference',
    'distributed_knowledge_access',
    'inter_individual_coordination_protocol',
]


def _load_cognition_class():
    root = Path.home() / 'open-cognitive-ecology'
    source_path = root / 'cognition' / 'multi_individual_civilizational_ecology.py'

    if not source_path.exists():
        return None

    spec = importlib.util.spec_from_file_location(
        'cognition.multi_individual_civilizational_ecology',
        str(source_path),
    )
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, 'MultiIndividualCivilizationalEcology', None)


_CognitionEcology = _load_cognition_class()


class MultiIndividualCivilizationalEcology:
    '''''
    Ontology-facing bridge around the cognition implementation.

    The bridge is intentionally thin: it delegates evaluate_ecology() to the
    cognition module when available and adds a validation-friendly step().
    '''''

    def __init__(self) -> None:
        self._delegate = _CognitionEcology() if _CognitionEcology else None

    def evaluate_ecology(self, state: Dict[str, Any] | None = None) -> Dict[str, Any]:
        state = state or self._default_state()

        if self._delegate is not None and hasattr(self._delegate, 'evaluate_ecology'):
            result = self._delegate.evaluate_ecology(state)
            if isinstance(result, dict):
                result = dict(result)
                result.setdefault('primitive', PRIMITIVE)
                result.setdefault('bridge_active', True)
                result.setdefault('source_module', 'cognition.multi_individual_civilizational_ecology')
                return result

        # Safe fallback: keeps validation error-free if cognition source is absent.
        agents = state.get('agents', []) if isinstance(state, dict) else []
        agent_count = len(agents)
        ecological_diversity = sum(
            float(a.get('trajectory_diversity', 0.0)) for a in agents
        ) / max(1, agent_count)
        fragmentation_risk = float(state.get('fragmentation_index', 0.0)) if isinstance(state, dict) else 0.0
        coordination_viability = float(state.get('coordination_stability', 0.0)) if isinstance(state, dict) else 0.0
        closure_pressure = float(state.get('closure_pressure', 0.0)) if isinstance(state, dict) else 0.0
        openness = ecological_diversity * coordination_viability * (1.0 - fragmentation_risk) * (1.0 - closure_pressure)

        return {
            'primitive': PRIMITIVE,
            'bridge_active': False,
            'source_module': None,
            'ecological_diversity': round(max(0.0, min(1.0, ecological_diversity)), 4),
            'fragmentation_risk': round(max(0.0, min(1.0, fragmentation_risk)), 4),
            'coordination_viability': round(max(0.0, min(1.0, coordination_viability)), 4),
            'closure_pressure': round(max(0.0, min(1.0, closure_pressure)), 4),
            'civilizational_openness_index': round(max(0.0, min(1.0, openness)), 4),
            'ecological_viability': openness >= 0.25,
        }

    def step(self, inputs: Dict[str, Any] | None = None) -> Dict[str, Any]:
        state = inputs if isinstance(inputs, dict) else self._default_state()
        ecology = self.evaluate_ecology(state)
        openness = float(ecology.get('civilizational_openness_index', 0.0))

        return {
            'primitive': PRIMITIVE,
            'bridge_ready': bool(self._delegate is not None),
            'ontology_bridge_active': True,
            'source_module': ecology.get('source_module'),
            'civilizational_openness_index': openness,
            'ecological_viability': bool(ecology.get('ecological_viability', False)),
            'import_path_supported': 'ontology.multi_individual_civilizational_ecology',
            'canonical_source_path': 'cognition/multi_individual_civilizational_ecology.py',
            'diagnostics': {
                'closure_pressure_added': 0.0,
                'non_redundant_role': 'ontology_import_bridge_to_cognition_ecology',
                'delegates_to_cognition': bool(self._delegate is not None),
                'dependencies': DEPENDENCIES,
            },
            'ecology': ecology,
        }

    def _default_state(self) -> Dict[str, Any]:
        return {
            'agents': [
                {'trajectory_diversity': 0.82},
                {'trajectory_diversity': 0.78},
                {'trajectory_diversity': 0.74},
            ],
            'fragmentation_index': 0.08,
            'coordination_stability': 0.91,
            'closure_pressure': 0.04,
        }
