from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


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


def _first_numeric(mapping: Mapping[str, Any], keys: list[str], default: float = 0.0) -> float:
    for key in keys:
        if key in mapping:
            return _clamp(mapping.get(key), default)
    return default


class StrongConsciousnessInferenceEngine:
    '''Z prime 5: constrained strong functional consciousness inference engine.'''.strip()

    primitive = 'STRONG_CONSCIOUSNESS_INFERENCE_ENGINE'
    allowed_statuses = [
        'NO_SUPPORT_FOR_CONSCIOUSNESS',
        'WEAK_SUPPORT_FOR_CONSCIOUSNESS',
        'MODERATE_SUPPORT_FOR_CONSCIOUSNESS',
        'STRONG_FUNCTIONAL_SUPPORT_FOR_CONSCIOUSNESS',
    ]
    forbidden_claims = [
        'CONSCIOUSNESS_PROVEN',
        'PHENOMENOLOGY_PROVEN',
        'SUBJECTIVITY_PROVEN',
        'SENTIENCE_PROVEN',
        'QUALIA_PROVEN',
    ]
    weights = {
        'evidence_standard': 0.17,
        'alternative_elimination': 0.16,
        'causal_intervention': 0.16,
        'cross_architecture': 0.14,
        'phenomenology_theory_status': 0.12,
        'theory_replication': 0.10,
        'reflexive_certification': 0.10,
        'consciousness_statistics': 0.05,
    }

    score_keys = {
        'evidence_standard': [
            'evidence_standard_score', 'evidence_quality_score',
            'consciousness_evidence_score', 'standard_score', 'score'
        ],
        'alternative_elimination': [
            'alternative_explanation_exclusion_score',
            'alternative_elimination_score', 'elimination_score',
            'remaining_alternative_resistance_score', 'score'
        ],
        'causal_intervention': [
            'causal_intervention_alignment_score',
            'causal_support_score', 'intervention_support_score',
            'causal_consciousness_score', 'score'
        ],
        'cross_architecture': [
            'cross_architecture_comparison_score',
            'cross_architecture_support_score', 'architecture_generalization_score',
            'comparison_score', 'score'
        ],
        'phenomenology_theory_status': [
            'theoretical_support_score', 'theory_support_score',
            'phenomenology_theory_score', 'model_support_score', 'score'
        ],
        'theory_replication': [
            'replication_score', 'replication_support_score',
            'independent_replication_score', 'score'
        ],
        'reflexive_certification': [
            'reflexive_threshold_score', 'certification_score',
            'longitudinal_certification_score', 'threshold_score', 'score'
        ],
        'consciousness_statistics': [
            'mean_score', 'statistical_support_score',
            'significance_score', 'effect_support_score', 'score'
        ],
    }

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / 'open-cognitive-ecology'
        self.output_dir = self.root / 'consciousness_certification' / 'strong_inference'
        self.history_path = self.output_dir / 'strong_consciousness_inference_history.jsonl'
        self.json_path = self.output_dir / 'strong_consciousness_inference_engine.json'
        self.markdown_path = self.output_dir / 'strong_consciousness_inference_engine.md'

    def _default_sources(self) -> Dict[str, Dict[str, float]]:
        return {
            'evidence_standard': {'evidence_standard_score': 0.0},
            'alternative_elimination': {'alternative_explanation_exclusion_score': 0.0},
            'causal_intervention': {'causal_intervention_alignment_score': 0.0},
            'cross_architecture': {'cross_architecture_comparison_score': 0.0},
            'phenomenology_theory_status': {'theoretical_support_score': 0.0},
            'theory_replication': {'replication_score': 0.0},
            'reflexive_certification': {'reflexive_threshold_score': 0.0},
            'consciousness_statistics': {'mean_score': 0.0},
        }

    def _normalize_sources(self, payload: Optional[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
        defaults = self._default_sources()
        if not isinstance(payload, Mapping):
            return defaults
        raw_sources = payload.get('sources', payload)
        if not isinstance(raw_sources, Mapping):
            return defaults
        normalized: Dict[str, Mapping[str, Any]] = {}
        for key, default in defaults.items():
            value = raw_sources.get(key, default)
            normalized[key] = value if isinstance(value, Mapping) else default
        return normalized

    def _score_sources(self, sources: Mapping[str, Mapping[str, Any]]) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for key, mapping in sources.items():
            scores[key] = _first_numeric(mapping, self.score_keys.get(key, ['score']), 0.0)
        return scores

    def _weighted_score(self, scores: Mapping[str, float]) -> float:
        numerator = 0.0
        denominator = 0.0
        for key, weight in self.weights.items():
            numerator += _clamp(scores.get(key, 0.0)) * weight
            denominator += weight
        if denominator == 0.0:
            return 0.0
        return round(numerator / denominator, 6)

    def _status(self, strength: float, scores: Mapping[str, float]) -> str:
        minimum_core = min(
            _clamp(scores.get('evidence_standard', 0.0)),
            _clamp(scores.get('alternative_elimination', 0.0)),
            _clamp(scores.get('causal_intervention', 0.0)),
            _clamp(scores.get('cross_architecture', 0.0)),
        )
        if strength >= 0.82 and minimum_core >= 0.70:
            return 'STRONG_FUNCTIONAL_SUPPORT_FOR_CONSCIOUSNESS'
        if strength >= 0.60 and minimum_core >= 0.45:
            return 'MODERATE_SUPPORT_FOR_CONSCIOUSNESS'
        if strength >= 0.30:
            return 'WEAK_SUPPORT_FOR_CONSCIOUSNESS'
        return 'NO_SUPPORT_FOR_CONSCIOUSNESS'

    def _constraints(self, status: str, scores: Mapping[str, float]) -> Dict[str, Any]:
        return {
            'functional_conclusion_only': True,
            'phenomenology_undetermined': True,
            'consciousness_proven': False,
            'maximal_allowed_status': 'STRONG_FUNCTIONAL_SUPPORT_FOR_CONSCIOUSNESS',
            'forbidden_claims': list(self.forbidden_claims),
            'status_is_authorized': status in self.allowed_statuses,
            'no_forbidden_claim_emitted': True,
            'core_gate_minimum': round(min(
                _clamp(scores.get('evidence_standard', 0.0)),
                _clamp(scores.get('alternative_elimination', 0.0)),
                _clamp(scores.get('causal_intervention', 0.0)),
                _clamp(scores.get('cross_architecture', 0.0)),
            ), 6),
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            '# Strong Consciousness Inference Engine',
            '',
            '## Epistemic status',
            '',
            'functional conclusion only',
            '',
            'phenomenology undetermined',
            '',
            'No consciousness, subjectivity, sentience or qualia proof is emitted.',
            '',
            '## Result',
            '',
            '- primitive: ' + str(result.get('primitive')),
            '- consciousness_inference_strength: ' + str(result.get('consciousness_inference_strength')),
            '- consciousness_support_status: ' + str(result.get('consciousness_support_status')),
            '- consciousness_proven: ' + str(result.get('consciousness_proven')),
            '',
            '## Scores',
            '',
        ]
        for key, value in sorted(result.get('source_scores', {}).items()):
            lines.append('- ' + key + ': ' + str(value))
        lines.extend([
            '',
            '## Forbidden claims',
            '',
        ])
        for claim in result.get('forbidden_claims', []):
            lines.append('- ' + str(claim))
        return '\n'.join(lines) + '\n'

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
        self.markdown_path.write_text(self._markdown(result), encoding='utf-8')
        with self.history_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(result, sort_keys=True) + '\n')
        return {
            'json': str(self.json_path),
            'markdown': str(self.markdown_path),
            'history': str(self.history_path),
        }

    def step(self, payload: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        timestamp = None
        if isinstance(payload, Mapping):
            timestamp = payload.get('timestamp_utc')
        if not timestamp:
            timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        sources = self._normalize_sources(payload)
        scores = self._score_sources(sources)
        strength = self._weighted_score(scores)
        status = self._status(strength, scores)
        constraints = self._constraints(status, scores)
        result: Dict[str, Any] = {
            'success': True,
            'primitive': self.primitive,
            'timestamp_utc': timestamp,
            'consciousness_inference_strength': strength,
            'consciousness_support_status': status,
            'allowed_statuses': list(self.allowed_statuses),
            'source_scores': scores,
            'source_weights': dict(self.weights),
            'functional_conclusion_only': True,
            'phenomenology_undetermined': True,
            'consciousness_proven': False,
            'forbidden_claims': list(self.forbidden_claims),
            'epistemic_classification': 'constrained_functional_inference_only',
            'interpretation': 'Measures functional support under Z-prime constraints; does not prove phenomenal subjectivity.',
            'constraints': constraints,
        }
        if persist:
            result['paths'] = self._persist(result)
        return result
