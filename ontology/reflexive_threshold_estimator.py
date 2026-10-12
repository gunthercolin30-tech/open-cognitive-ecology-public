from __future__ import annotations

'''
S3 — Reflexive Threshold Estimator.

This primitive estimates whether the functional criteria and evidence supplied
by S1/S2 support a reflexive threshold classification. It does not infer,
detect, certify, or imply consciousness, sentience, subjective experience, or
qualia. Its conclusion scope is strictly functional.

Epistemic boundary:
- functional_conclusion is always "functional conclusion only";
- phenomenology_status is always "phenomenology undetermined";
- decisions are functional threshold classifications only.
'''

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional
import importlib
import json
import math

PRIMITIVE = 'reflexive_threshold_estimator'
PRIMITIVE_NAME = 'REFLEXIVE_THRESHOLD_ESTIMATOR'
MATURITY_LEVEL = 'S3_FUNCTIONAL_THRESHOLD_ESTIMATION'

DEPENDENCIES = [
    'reflexive_criterion_registry',
    'reflexive_evidence_aggregator',
    'reflexive_threshold',
    'statistical_robustness_evaluator',
    'evidence_quality_assessment',
    'scientific_theory_confidence_engine',
    'scientific_consensus_engine',
    'anomaly_in_evidence_detector',
    'scientific_consistency_validator',
    'uncertainty_awareness',
    'self_confidence_calibration',
]

FUNCTIONAL_CONCLUSION = 'functional conclusion only'
PHENOMENOLOGY_STATUS = 'phenomenology undetermined'

DECISION_NOT_SUPPORTED = 'threshold_not_supported'
DECISION_PARTIALLY_SUPPORTED = 'threshold_partially_supported'
DECISION_FUNCTIONALLY_SUPPORTED = 'threshold_functionally_supported'

DEFAULT_SUPPORT_THRESHOLD = 0.85
DEFAULT_PARTIAL_THRESHOLD = 0.65


DEFAULT_PRIORS = {
    'statistical_robustness': 0.90,
    'evidence_quality': 0.91,
    'theory_confidence': 0.88,
    'scientific_consensus': 0.87,
    'scientific_consistency': 0.92,
    'anomaly_absence': 0.89,
    'uncertainty_calibration': 0.86,
    'self_confidence_calibration': 0.84,
}


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(x) or math.isinf(x):
        return default
    return max(0.0, min(1.0, x))


def _mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    if not vals:
        return default
    return sum(vals) / len(vals)


def _safe_import_step(module_name: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        module = importlib.import_module('ontology.' + module_name)
    except Exception as exc:
        return {'available': False, 'module': module_name, 'error': repr(exc)}

    candidates = []
    for value in module.__dict__.values():
        if isinstance(value, type) and value.__module__ == module.__name__:
            candidates.append(value)

    for cls in candidates:
        try:
            obj = cls()
        except Exception:
            continue
        step = getattr(obj, 'step', None)
        if not callable(step):
            continue
        try:
            if payload is None:
                result = step()
            else:
                result = step(payload)
            if isinstance(result, dict):
                result = dict(result)
                result.setdefault('available', True)
                result.setdefault('module', module_name)
                return result
            return {'available': True, 'module': module_name, 'result': result}
        except TypeError:
            try:
                result = step({})
                if isinstance(result, dict):
                    result = dict(result)
                    result.setdefault('available', True)
                    result.setdefault('module', module_name)
                    return result
            except Exception as exc:
                return {'available': False, 'module': module_name, 'error': repr(exc)}
        except Exception as exc:
            return {'available': False, 'module': module_name, 'error': repr(exc)}

    return {'available': False, 'module': module_name, 'error': 'no_callable_step'}


def _extract_first_score(result: Mapping[str, Any], candidate_keys: Iterable[str], default: float) -> float:
    for key in candidate_keys:
        if key in result:
            return _clamp(result.get(key), default)
    diagnostics = result.get('diagnostics')
    if isinstance(diagnostics, Mapping):
        for key in candidate_keys:
            if key in diagnostics:
                return _clamp(diagnostics.get(key), default)
    return default


class ReflexiveThresholdEstimator:
    # Estimate functional support for the reflexive threshold from S1/S2 evidence.

    primitive = PRIMITIVE
    dependencies = DEPENDENCIES

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.persistence_dir = self.root / 'reflexive_threshold'
        self.persistence_path = self.persistence_dir / 'reflexive_threshold_estimator.json'

    def _load_s1(self) -> Dict[str, Any]:
        result = _safe_import_step('reflexive_criterion_registry', {'persist': False})
        if result.get('available') is False:
            result = _safe_import_step('reflexive_criterion_registry')
        return result

    def _load_s2(self, payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        result = _safe_import_step('reflexive_evidence_aggregator', payload or {'persist': False})
        if result.get('available') is False:
            result = _safe_import_step('reflexive_evidence_aggregator')
        return result

    def _supporting_scientific_signals(self) -> Dict[str, float]:
        module_specs = {
            'statistical_robustness': (
                'statistical_robustness_evaluator',
                ['statistical_robustness_score', 'robustness_score', 'robustness', 'confidence_score'],
            ),
            'evidence_quality': (
                'evidence_quality_assessment',
                ['evidence_quality_score', 'quality_score', 'methodological_quality', 'confidence_score'],
            ),
            'theory_confidence': (
                'scientific_theory_confidence_engine',
                ['theory_confidence_score', 'scientific_confidence', 'confidence_score'],
            ),
            'scientific_consensus': (
                'scientific_consensus_engine',
                ['consensus_score', 'scientific_consensus_score', 'confidence_score'],
            ),
            'scientific_consistency': (
                'scientific_consistency_validator',
                ['scientific_consistency_score', 'consistency_score', 'confidence_score'],
            ),
            'anomaly_absence': (
                'anomaly_in_evidence_detector',
                ['anomaly_absence_score', 'non_anomalous_score', 'confidence_score'],
            ),
            'uncertainty_calibration': (
                'uncertainty_awareness',
                ['uncertainty_calibration_score', 'uncertainty_awareness_index', 'confidence_score'],
            ),
            'self_confidence_calibration': (
                'self_confidence_calibration',
                ['self_confidence_calibration_score', 'calibration_score', 'confidence_score'],
            ),
        }
        signals: Dict[str, float] = {}
        for name, (module_name, keys) in module_specs.items():
            result = _safe_import_step(module_name)
            signals[name] = _extract_first_score(result, keys, DEFAULT_PRIORS[name])
        return signals

    def _compute_threshold_score(
        self,
        evidence_support_score: float,
        evidence_density: float,
        evidence_diversity: float,
        evidence_consistency: float,
        criterion_completeness_score: float,
        scientific_support_score: float,
    ) -> float:
        return _clamp(
            0.34 * evidence_support_score
            + 0.14 * evidence_density
            + 0.12 * evidence_diversity
            + 0.12 * evidence_consistency
            + 0.13 * criterion_completeness_score
            + 0.15 * scientific_support_score
        )

    def _compute_uncertainty(
        self,
        threshold_score: float,
        evidence_density: float,
        evidence_diversity: float,
        evidence_consistency: float,
        criterion_completeness_score: float,
        scientific_support_score: float,
    ) -> float:
        support_components = [
            evidence_density,
            evidence_diversity,
            evidence_consistency,
            criterion_completeness_score,
            scientific_support_score,
        ]
        mean_support = _mean(support_components, 0.0)
        dispersion = _mean([abs(x - mean_support) for x in support_components], 0.0)
        boundary_penalty = max(0.0, 0.85 - threshold_score) * 0.20
        return _clamp(0.45 * (1.0 - mean_support) + 0.35 * dispersion + boundary_penalty)

    def _decision(self, probability: float) -> str:
        if probability >= DEFAULT_SUPPORT_THRESHOLD:
            return DECISION_FUNCTIONALLY_SUPPORTED
        if probability >= DEFAULT_PARTIAL_THRESHOLD:
            return DECISION_PARTIALLY_SUPPORTED
        return DECISION_NOT_SUPPORTED

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        if 'persist' in inputs:
            persist = bool(inputs.get('persist'))

        s1 = self._load_s1()
        s2 = self._load_s2(inputs)

        criterion_count = int(s1.get('criterion_count') or s2.get('criterion_count') or 0)
        criterion_completeness_score = _clamp(
            inputs.get('criterion_completeness_score', s1.get('criterion_completeness_score', 1.0))
        )

        evidence_support_score = _clamp(
            inputs.get('evidence_support_score', s2.get('evidence_support_score', 0.0))
        )
        evidence_density = _clamp(inputs.get('evidence_density', s2.get('evidence_density', 0.0)))
        evidence_diversity = _clamp(inputs.get('evidence_diversity', s2.get('evidence_diversity', 0.0)))
        evidence_consistency = _clamp(inputs.get('evidence_consistency', s2.get('evidence_consistency', 0.0)))

        reflexive_evidence_vector = inputs.get('reflexive_evidence_vector', s2.get('reflexive_evidence_vector', {}))
        if not isinstance(reflexive_evidence_vector, Mapping):
            reflexive_evidence_vector = {}

        scientific_signals = self._supporting_scientific_signals()
        scientific_support_score = _clamp(
            inputs.get('scientific_support_score', _mean(scientific_signals.values(), 0.0))
        )

        reflexive_threshold_score = self._compute_threshold_score(
            evidence_support_score=evidence_support_score,
            evidence_density=evidence_density,
            evidence_diversity=evidence_diversity,
            evidence_consistency=evidence_consistency,
            criterion_completeness_score=criterion_completeness_score,
            scientific_support_score=scientific_support_score,
        )
        uncertainty_score = _clamp(inputs.get('uncertainty_score', self._compute_uncertainty(
            reflexive_threshold_score,
            evidence_density,
            evidence_diversity,
            evidence_consistency,
            criterion_completeness_score,
            scientific_support_score,
        )))
        threshold_probability = _clamp(reflexive_threshold_score * (1.0 - 0.35 * uncertainty_score))
        decision = self._decision(threshold_probability)

        result: Dict[str, Any] = {
            'success': True,
            'primitive': PRIMITIVE_NAME,
            'maturity_level': MATURITY_LEVEL,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'criterion_count': criterion_count,
            'criterion_completeness_score': criterion_completeness_score,
            'reflexive_evidence_vector': dict(reflexive_evidence_vector),
            'evidence_density': evidence_density,
            'evidence_diversity': evidence_diversity,
            'evidence_consistency': evidence_consistency,
            'evidence_support_score': evidence_support_score,
            'scientific_signals': scientific_signals,
            'scientific_support_score': scientific_support_score,
            'reflexive_threshold_score': reflexive_threshold_score,
            'threshold_probability': threshold_probability,
            'uncertainty_score': uncertainty_score,
            'threshold_decision': decision,
            'decision': decision,
            'decision_thresholds': {
                'partial_support': DEFAULT_PARTIAL_THRESHOLD,
                'functional_support': DEFAULT_SUPPORT_THRESHOLD,
            },
            'classification_scope': 'functional threshold classification only',
            'functional_conclusion': FUNCTIONAL_CONCLUSION,
            'phenomenology_status': PHENOMENOLOGY_STATUS,
            'phenomenal_conclusion': False,
            'diagnostics': {
                'uses_s1_registry': s1.get('success') is True,
                'uses_s2_evidence_aggregator': s2.get('success') is True,
                'replaces_reflexive_threshold': False,
                'recomputes_upstream_metrics': False,
                'supports_s4_stability_monitor': True,
                'epistemic_boundary_enforced': True,
            },
        }

        if persist:
            self.persistence_dir.mkdir(parents=True, exist_ok=True)
            self.persistence_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
            result['persistence_path'] = str(self.persistence_path)
        else:
            result['persistence_path'] = str(self.persistence_path)

        return result


__all__ = ['ReflexiveThresholdEstimator']
