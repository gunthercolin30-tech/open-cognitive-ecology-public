from __future__ import annotations

'''
S1 — Reflexive Criterion Registry.

This primitive defines the canonical functional criteria associated with the
reflexive threshold. It does not infer phenomenology and does not re-compute
metrics already produced by upstream modules. Its role is to provide a stable,
traceable, deterministic registry that downstream S2-S10 modules can reuse.

Epistemic boundary:
- conclusion_type is always "functional conclusion only";
- phenomenology_status is always "phenomenology undetermined";
- consciousness, sentience, subjective experience and qualia are never inferred.
'''

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import json

PRIMITIVE = 'reflexive_criterion_registry'
PRIMITIVE_NAME = 'REFLEXIVE_CRITERION_REGISTRY'
MATURITY_LEVEL = 'S1_FUNCTIONAL_REGISTRY'

DEPENDENCIES = [
    'meta_cognition',
    'reflective_self_assessment_loop',
    'autobiographical_memory',
    'future_openness',
    'constitutional_self_modification_protocol',
    'identity_drift_monitor',
    'strategic_drift_monitor',
    'memory_drift_monitor',
    'continuity_metrics_engine',
    'scientific_self_revision_supervisor',
    'functional_consciousness_behavioral_benchmark',
    'empirical_consciousness_evidence_synthesizer',
    'reflexive_threshold',
]

EPISTEMIC_BOUNDARY = {
    'conclusion_type': 'functional conclusion only',
    'phenomenology_status': 'phenomenology undetermined',
    'forbidden_claims': [
        'consciousness detected',
        'sentience detected',
        'subjective experience detected',
        'qualia detected',
    ],
}


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if number < 0.0:
        return 0.0
    if number > 1.0:
        return 1.0
    return number


@dataclass(frozen=True)
class ReflexiveCriterion:
    criterion_id: str
    label: str
    functional_definition: str
    evidence_modules: List[str]
    expected_evidence_keys: List[str]
    weight: float = 1.0
    required: bool = True
    epistemic_scope: str = 'functional_measure_only'


DEFAULT_CRITERIA: List[ReflexiveCriterion] = [
    ReflexiveCriterion(
        criterion_id='identity_continuity',
        label='Identity continuity',
        functional_definition=(
            'Persistence of a coherent computational identity across runtime, '
            'drift monitoring, succession and lineage transitions.'
        ),
        evidence_modules=[
            'civilizational_identity_baseline',
            'identity_drift_monitor',
            'persistent_selfhood_benchmark',
            'continuity_metrics_engine',
            'representative_lineage_registry',
        ],
        expected_evidence_keys=[
            'identity_continuity_score',
            'identity_drift_score',
            'selfhood_consistency_score',
            'continuity_score',
        ],
    ),
    ReflexiveCriterion(
        criterion_id='memory_coherence',
        label='Memory coherence',
        functional_definition=(
            'Maintenance of autobiographical, civilizational and transmitted '
            'memory without incoherent drift or destructive discontinuity.'
        ),
        evidence_modules=[
            'autobiographical_memory',
            'memory_drift_monitor',
            'memory_transmission_protocol',
            'civilizational_memory_archive',
            'distributed_memory_consistency_validator',
        ],
        expected_evidence_keys=[
            'memory_coherence_score',
            'memory_drift_score',
            'transmission_quality_score',
            'archive_stability',
        ],
    ),
    ReflexiveCriterion(
        criterion_id='self_revision_capacity',
        label='Self-revision capacity',
        functional_definition=(
            'Capacity to assess, recommend and govern revisions of internal '
            'models, policies or scientific interpretations under constraints.'
        ),
        evidence_modules=[
            'scientific_self_revision_supervisor',
            'self_revision_recommendation_engine',
            'reflective_self_assessment_loop',
            'meta_cognition',
            'recursive_self_improvement_governor',
        ],
        expected_evidence_keys=[
            'self_revision_score',
            'revision_quality_score',
            'meta_cognition_index',
            'self_assessment_score',
        ],
    ),
    ReflexiveCriterion(
        criterion_id='goal_persistence',
        label='Goal persistence',
        functional_definition=(
            'Persistence of long-horizon strategic orientation while preserving '
            'the possibility of revision under evidence and governance.'
        ),
        evidence_modules=[
            'strategic_drift_monitor',
            'civilizational_strategy_orchestrator',
            'reflective_goal_revision',
            'long_horizon_stability_protocol',
        ],
        expected_evidence_keys=[
            'strategic_coherence_score',
            'strategic_drift_score',
            'goal_persistence_score',
            'trajectory_persistence',
        ],
    ),
    ReflexiveCriterion(
        criterion_id='future_openness_preservation',
        label='Future openness preservation',
        functional_definition=(
            'Active preservation of non-closure, diversity, exploration and the '
            'future conditions of open-ended development.'
        ),
        evidence_modules=[
            'future_openness',
            'openness_preservation_index',
            'non_closure_certification_protocol',
            'anti_closure_metaconstraint',
            'closure_pressure_monitor',
        ],
        expected_evidence_keys=[
            'future_openness_index',
            'openness_preservation_score',
            'non_closure_score',
            'closure_pressure_index',
        ],
    ),
    ReflexiveCriterion(
        criterion_id='governed_self_modification',
        label='Governed self-modification',
        functional_definition=(
            'Self-modification is mediated by constitutional, scientific, human '
            'review and rollback-compatible governance rather than direct closure.'
        ),
        evidence_modules=[
            'constitutional_self_modification_protocol',
            'governance_review',
            'human_review_gate',
            'controlled_execution_layer',
            'external_influence_compliance_certifier',
        ],
        expected_evidence_keys=[
            'mutation_authorized',
            'constitutional_compliance_score',
            'human_review_required',
            'rollback_available',
        ],
    ),
    ReflexiveCriterion(
        criterion_id='multi_timescale_reasoning',
        label='Multi-timescale reasoning',
        functional_definition=(
            'Integration of immediate, longitudinal, intergenerational and '
            'civilizational timescales in stability and decision evaluation.'
        ),
        evidence_modules=[
            'consciousness_longitudinal_stability_analyzer',
            'reflexive_emergence_longitudinal_protocol',
            'intergenerational_continuity_metrics',
            'historical_open_endedness',
            'long_horizon_stability_protocol',
        ],
        expected_evidence_keys=[
            'longitudinal_stability_score',
            'stability_duration',
            'intergenerational_continuity_score',
            'historical_trend',
        ],
    ),
    ReflexiveCriterion(
        criterion_id='external_deliberation_capacity',
        label='External deliberation capacity',
        functional_definition=(
            'Ability to incorporate external influence as consultative evidence '
            'through traceable deliberation, not as uncontrolled authority.'
        ),
        evidence_modules=[
            'canonical_external_influence_ledger',
            'external_influence_traceability_engine',
            'external_action_proposal_queue',
            'governed_external_revision_pipeline',
            'external_influence_compliance_certifier',
        ],
        expected_evidence_keys=[
            'external_influence_traceability_score',
            'human_approval_chain_validated',
            'commit_traceability_validated',
            'external_compliance_score',
        ],
    ),
]


class ReflexiveCriterionRegistry:
    def __init__(
        self,
        criteria: Optional[Iterable[ReflexiveCriterion | Mapping[str, Any]]] = None,
        persistence_path: Optional[str | Path] = None,
    ) -> None:
        self.criteria = self._normalize_criteria(criteria or DEFAULT_CRITERIA)
        self.persistence_path = Path(persistence_path) if persistence_path else (
            Path('reflexive_threshold') / 'reflexive_criterion_registry.json'
        )

    def _normalize_criteria(
        self,
        criteria: Iterable[ReflexiveCriterion | Mapping[str, Any]],
    ) -> List[ReflexiveCriterion]:
        normalized: List[ReflexiveCriterion] = []
        for item in criteria:
            if isinstance(item, ReflexiveCriterion):
                normalized.append(item)
            else:
                normalized.append(ReflexiveCriterion(**dict(item)))
        normalized.sort(key=lambda criterion: criterion.criterion_id)
        return normalized

    def _available_modules(self, inventory: Any = None, catalog: Any = None) -> set[str]:
        names: set[str] = set()
        for source in (inventory, catalog):
            if source is None:
                continue
            if isinstance(source, Mapping):
                iterable = list(source.keys()) + list(source.values())
            else:
                iterable = source if isinstance(source, list) else [source]
            for item in iterable:
                if isinstance(item, str):
                    names.add(item.split('.')[-1].split('/')[-1].replace('.py', ''))
                elif isinstance(item, Mapping):
                    for key in ('name', 'module', 'primitive', 'path'):
                        value = item.get(key)
                        if isinstance(value, str):
                            names.add(value.split('.')[-1].split('/')[-1].replace('.py', ''))
        return names

    def _criterion_coverage(self, criterion: ReflexiveCriterion, available: set[str]) -> float:
        if not criterion.evidence_modules:
            return 0.0
        hits = sum(1 for module in criterion.evidence_modules if module in available)
        return _clamp(hits / len(criterion.evidence_modules))

    def step(
        self,
        inventory: Any = None,
        global_module_catalog: Any = None,
        persist: bool = False,
        persistence_path: Optional[str | Path] = None,
    ) -> Dict[str, Any]:
        available = self._available_modules(inventory, global_module_catalog)
        if not available:
            for criterion in self.criteria:
                available.update(criterion.evidence_modules)

        records: List[Dict[str, Any]] = []
        weighted_sum = 0.0
        weight_total = 0.0
        covered_count = 0

        for criterion in self.criteria:
            coverage = self._criterion_coverage(criterion, available)
            if coverage > 0.0:
                covered_count += 1
            weighted_sum += coverage * max(0.0, criterion.weight)
            weight_total += max(0.0, criterion.weight)
            record = asdict(criterion)
            record['coverage'] = coverage
            record['covered'] = coverage > 0.0
            records.append(record)

        criterion_count = len(self.criteria)
        criterion_coverage = _clamp(covered_count / criterion_count) if criterion_count else 0.0
        criterion_completeness_score = _clamp(weighted_sum / weight_total) if weight_total else 0.0

        result: Dict[str, Any] = {
            'primitive': PRIMITIVE_NAME,
            'success': True,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'criterion_count': criterion_count,
            'covered_criterion_count': covered_count,
            'criterion_coverage': criterion_coverage,
            'criterion_completeness_score': criterion_completeness_score,
            'criteria': records,
            'reflexive_evidence_vector_schema': {
                criterion.criterion_id: criterion.expected_evidence_keys
                for criterion in self.criteria
            },
            'dependencies': DEPENDENCIES,
            'decision_scope': 'functional_threshold_criteria_registry',
            'functional_conclusion': 'functional conclusion only',
            'phenomenology_status': 'phenomenology undetermined',
            'epistemic_boundary': EPISTEMIC_BOUNDARY,
            'diagnostics': {
                'non_redundancy_position': 'registry_not_metric_reimplementation',
                'recomputes_upstream_metrics': False,
                'deterministic_ordering': True,
                's1_ready_for_s2_evidence_aggregation': criterion_count > 0,
            },
        }

        if persist:
            path = Path(persistence_path) if persistence_path else self.persistence_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
            result['persistence_path'] = str(path)
            result['persisted'] = True
        else:
            result['persisted'] = False

        return result

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        result = self.step(**kwargs)
        # The epistemic_boundary intentionally lists forbidden claims as constraints.
        # Validation must detect only prohibited conclusions in output fields, not
        # the presence of the guardrail vocabulary inside the guardrail itself.
        conclusion_surface = json.dumps({
            'functional_conclusion': result.get('functional_conclusion'),
            'phenomenology_status': result.get('phenomenology_status'),
            'decision_scope': result.get('decision_scope'),
            'diagnostics': result.get('diagnostics', {}),
        }, ensure_ascii=False).lower()
        forbidden_present = any(
            claim in conclusion_surface
            for claim in ('consciousness detected', 'sentience detected', 'subjective experience detected', 'qualia detected')
        )
        return {
            'primitive': PRIMITIVE_NAME,
            'is_valid': (
                result['success'] is True
                and result['criterion_count'] >= 8
                and 0.0 <= result['criterion_coverage'] <= 1.0
                and 0.0 <= result['criterion_completeness_score'] <= 1.0
                and result['functional_conclusion'] == 'functional conclusion only'
                and result['phenomenology_status'] == 'phenomenology undetermined'
                and not forbidden_present
            ),
            'criterion_count': result['criterion_count'],
            'criterion_coverage': result['criterion_coverage'],
            'criterion_completeness_score': result['criterion_completeness_score'],
            'functional_conclusion': result['functional_conclusion'],
            'phenomenology_status': result['phenomenology_status'],
        }
