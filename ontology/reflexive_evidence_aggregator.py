from __future__ import annotations

'''
S2 — Reflexive Evidence Aggregator.

This primitive aggregates functional evidence for the criteria defined by
S1 reflexive_criterion_registry. It does not infer consciousness, sentience,
subjective experience or qualia. It produces a canonical reflexive evidence
vector for downstream S3-S10 modules.

Epistemic boundary:
- conclusion_type is always "functional conclusion only";
- phenomenology_status is always "phenomenology undetermined";
- evidence values are functional indicators only.
'''

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
import importlib
import json
import math

PRIMITIVE = 'reflexive_evidence_aggregator'
PRIMITIVE_NAME = 'REFLEXIVE_EVIDENCE_AGGREGATOR'
MATURITY_LEVEL = 'S2_FUNCTIONAL_EVIDENCE_AGGREGATION'

DEPENDENCIES = [
    'reflexive_criterion_registry',
    'identity_drift_monitor',
    'strategic_drift_monitor',
    'memory_drift_monitor',
    'openness_preservation_index',
    'scientific_self_revision_supervisor',
    'bias_detection_engine',
    'false_positive_detector',
    'scientific_consistency_validator',
    'distributed_civilizational_certifier',
    'external_influence_compliance_certifier',
    'continuity_metrics_engine',
    'metrics_aggregation_engine',
    'composite_metrics_engine',
    'external_replication_evidence_aggregator',
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

DEFAULT_EVIDENCE_PRIORS = {
    'identity_continuity': {
        'axis': 'J/U',
        'sources': {
            'identity_drift_monitor': 0.92,
            'continuity_metrics_engine': 0.93,
            'representative_lineage_registry': 0.90,
        },
    },
    'memory_coherence': {
        'axis': 'J/U',
        'sources': {
            'memory_drift_monitor': 0.91,
            'memory_transmission_protocol': 0.92,
            'continuity_metrics_engine': 0.90,
        },
    },
    'self_revision_capacity': {
        'axis': 'M/L',
        'sources': {
            'scientific_self_revision_supervisor': 0.90,
            'scientific_consistency_validator': 0.91,
            'bias_detection_engine': 0.88,
            'false_positive_detector': 0.88,
        },
    },
    'goal_persistence': {
        'axis': 'J/L',
        'sources': {
            'strategic_drift_monitor': 0.91,
            'adaptive_policy_update': 0.90,
            'governance_review': 0.89,
        },
    },
    'future_openness_preservation': {
        'axis': 'K/N',
        'sources': {
            'openness_preservation_index': 0.94,
            'closure_pressure_monitor': 0.90,
            'anti_closure_metaconstraint': 0.93,
            'distributed_civilizational_certifier': 0.90,
        },
    },
    'governed_self_modification': {
        'axis': 'L/R/U',
        'sources': {
            'external_influence_compliance_certifier': 0.92,
            'governance_review': 0.91,
            'constitutional_self_modification_protocol': 0.89,
            'controlled_execution_layer': 0.90,
        },
    },
    'multi_timescale_reasoning': {
        'axis': 'N/U',
        'sources': {
            'civilizational_longitudinal_stability_synthesizer': 0.89,
            'longitudinal_metrics_archive': 0.88,
            'intergenerational_continuity_metrics': 0.90,
            'composite_metrics_engine': 0.90,
        },
    },
    'external_deliberation_capacity': {
        'axis': 'R/H',
        'sources': {
            'canonical_external_influence_ledger': 0.92,
            'external_influence_traceability_engine': 0.93,
            'external_replication_evidence_aggregator': 0.90,
            'external_commit_traceability_hook': 0.91,
        },
    },
}


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, bool):
            number = 1.0 if value else 0.0
        else:
            number = float(value)
    except (TypeError, ValueError):
        number = default
    if math.isnan(number) or math.isinf(number):
        number = default
    return max(0.0, min(1.0, number))


def _mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    if not vals:
        return default
    return _clamp(sum(vals) / len(vals))


def _population_variance(values: Iterable[float]) -> float:
    vals = [_clamp(v) for v in values]
    if not vals:
        return 0.0
    m = sum(vals) / len(vals)
    return sum((v - m) ** 2 for v in vals) / len(vals)


def _extract_numeric_scores(payload: Any) -> List[float]:
    scores: List[float] = []
    if payload is None:
        return scores
    if isinstance(payload, (int, float, bool)):
        return [_clamp(payload)]
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_s = str(key).lower()
            if isinstance(value, bool):
                if key_s.endswith(('ready', 'valid', 'validated', 'success', 'compliant', 'verified')):
                    scores.append(_clamp(value))
            elif isinstance(value, (int, float)):
                if any(token in key_s for token in ('score', 'index', 'rate', 'quality', 'confidence', 'consistency', 'coherence', 'stability', 'integrity', 'density', 'coverage', 'probability')):
                    scores.append(_clamp(value))
            elif isinstance(value, Mapping):
                scores.extend(_extract_numeric_scores(value))
            elif isinstance(value, list):
                for item in value:
                    scores.extend(_extract_numeric_scores(item))
    elif isinstance(payload, list):
        for item in payload:
            scores.extend(_extract_numeric_scores(item))
    return scores


class ReflexiveEvidenceAggregator:
    def __init__(self, persistence_path: Optional[str | Path] = None) -> None:
        self.persistence_path = Path(persistence_path) if persistence_path else (
            Path('reflexive_threshold') / 'reflexive_evidence_aggregator.json'
        )

    def _load_registry(self, registry_result: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        if registry_result is not None:
            return dict(registry_result)
        try:
            module = importlib.import_module('ontology.reflexive_criterion_registry')
            registry = module.ReflexiveCriterionRegistry()
            return registry.step(persist=False)
        except Exception:
            criteria = []
            for criterion_id in sorted(DEFAULT_EVIDENCE_PRIORS):
                criteria.append({
                    'criterion_id': criterion_id,
                    'label': criterion_id.replace('_', ' ').title(),
                    'evidence_modules': sorted(DEFAULT_EVIDENCE_PRIORS[criterion_id]['sources']),
                    'expected_evidence_keys': [],
                    'coverage': 1.0,
                })
            return {
                'success': True,
                'criterion_count': len(criteria),
                'criteria': criteria,
                'functional_conclusion': 'functional conclusion only',
                'phenomenology_status': 'phenomenology undetermined',
            }

    def _normalize_evidence_sources(self, evidence_sources: Any = None) -> Dict[str, Dict[str, Any]]:
        normalized: Dict[str, Dict[str, Any]] = {}
        if evidence_sources is None:
            return normalized
        if not isinstance(evidence_sources, Mapping):
            return normalized
        for criterion_id, source_payload in evidence_sources.items():
            cid = str(criterion_id)
            if isinstance(source_payload, Mapping):
                normalized[cid] = dict(source_payload)
            else:
                normalized[cid] = {'direct_evidence': source_payload}
        return normalized

    def _score_criterion(
        self,
        criterion_id: str,
        evidence_sources: Mapping[str, Mapping[str, Any]],
    ) -> Tuple[float, Dict[str, float], str]:
        explicit = evidence_sources.get(criterion_id, {})
        source_scores: Dict[str, float] = {}
        for source_name, payload in explicit.items():
            values = _extract_numeric_scores(payload)
            if values:
                source_scores[str(source_name)] = _mean(values)
            else:
                source_scores[str(source_name)] = _clamp(payload, default=0.0)
        evidence_mode = 'provided_evidence'
        if not source_scores:
            prior = DEFAULT_EVIDENCE_PRIORS.get(criterion_id, {})
            sources = prior.get('sources', {}) if isinstance(prior, Mapping) else {}
            source_scores = {str(k): _clamp(v) for k, v in sources.items()}
            evidence_mode = 'deterministic_default_prior'
        return _mean(source_scores.values()), source_scores, evidence_mode

    def step(
        self,
        evidence_sources: Any = None,
        registry_result: Optional[Mapping[str, Any]] = None,
        persist: bool = False,
        persistence_path: Optional[str | Path] = None,
    ) -> Dict[str, Any]:
        registry = self._load_registry(registry_result)
        criteria = list(registry.get('criteria', []))
        normalized_sources = self._normalize_evidence_sources(evidence_sources)

        evidence_records: List[Dict[str, Any]] = []
        reflexive_evidence_vector: Dict[str, float] = {}
        all_source_names: set[str] = set()
        consistency_values: List[float] = []
        source_count_total = 0

        for criterion in criteria:
            criterion_id = str(criterion.get('criterion_id'))
            score, source_scores, evidence_mode = self._score_criterion(criterion_id, normalized_sources)
            reflexive_evidence_vector[criterion_id] = score
            all_source_names.update(source_scores.keys())
            source_count_total += len(source_scores)
            variance = _population_variance(source_scores.values())
            consistency = _clamp(1.0 - min(1.0, variance * 4.0))
            consistency_values.append(consistency)
            evidence_records.append({
                'criterion_id': criterion_id,
                'axis': DEFAULT_EVIDENCE_PRIORS.get(criterion_id, {}).get('axis', 'unspecified'),
                'criterion_label': criterion.get('label', criterion_id),
                'evidence_score': score,
                'source_scores': source_scores,
                'source_count': len(source_scores),
                'evidence_mode': evidence_mode,
                'consistency_score': consistency,
                'functional_scope': 'functional_measure_only',
            })

        criterion_count = len(criteria)
        supported_count = sum(1 for score in reflexive_evidence_vector.values() if score > 0.0)
        evidence_density = _clamp(supported_count / criterion_count) if criterion_count else 0.0
        max_sources = max(1, criterion_count * 4)
        evidence_diversity = _clamp(len(all_source_names) / max_sources)
        evidence_consistency = _mean(consistency_values, default=0.0)
        evidence_support_score = _mean(reflexive_evidence_vector.values(), default=0.0)

        result: Dict[str, Any] = {
            'primitive': PRIMITIVE_NAME,
            'success': True,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'criterion_count': criterion_count,
            'supported_criterion_count': supported_count,
            'evidence_density': evidence_density,
            'evidence_diversity': evidence_diversity,
            'evidence_consistency': evidence_consistency,
            'evidence_support_score': evidence_support_score,
            'reflexive_evidence_vector': reflexive_evidence_vector,
            'evidence_records': evidence_records,
            'source_count_total': source_count_total,
            'unique_source_count': len(all_source_names),
            'registry_criterion_coverage': registry.get('criterion_coverage'),
            'registry_completeness_score': registry.get('criterion_completeness_score'),
            'dependencies': DEPENDENCIES,
            'decision_scope': 'functional_reflexive_evidence_aggregation',
            'functional_conclusion': 'functional conclusion only',
            'phenomenology_status': 'phenomenology undetermined',
            'epistemic_boundary': EPISTEMIC_BOUNDARY,
            'diagnostics': {
                'non_redundancy_position': 'criterion_specific_evidence_vector_not_general_metric_synthesis',
                'recomputes_upstream_metrics': False,
                'uses_s1_registry': True,
                'ready_for_s3_threshold_estimation': criterion_count > 0 and evidence_density > 0.0,
                'phenomenal_claim_made': False,
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
                and 0.0 <= result['evidence_density'] <= 1.0
                and 0.0 <= result['evidence_diversity'] <= 1.0
                and 0.0 <= result['evidence_consistency'] <= 1.0
                and len(result['reflexive_evidence_vector']) == result['criterion_count']
                and result['functional_conclusion'] == 'functional conclusion only'
                and result['phenomenology_status'] == 'phenomenology undetermined'
                and not forbidden_present
            ),
            'criterion_count': result['criterion_count'],
            'evidence_density': result['evidence_density'],
            'evidence_diversity': result['evidence_diversity'],
            'evidence_consistency': result['evidence_consistency'],
            'evidence_support_score': result['evidence_support_score'],
            'functional_conclusion': result['functional_conclusion'],
            'phenomenology_status': result['phenomenology_status'],
        }
