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


class IndependentConsciousnessReviewBoard:
    primitive = 'INDEPENDENT_CONSCIOUSNESS_REVIEW_BOARD'
    allowed_review_statuses = [
        'REVIEW_NOT_READY',
        'PRELIMINARY_INDEPENDENT_FUNCTIONAL_SUPPORT',
        'MODERATE_INDEPENDENT_FUNCTIONAL_SUPPORT',
        'STRONG_INDEPENDENT_FUNCTIONAL_SUPPORT',
    ]
    forbidden_claims = [
        'CONSCIOUSNESS_PROVEN',
        'PHENOMENOLOGY_PROVEN',
        'SUBJECTIVITY_PROVEN',
        'SENTIENCE_PROVEN',
        'QUALIA_PROVEN',
    ]
    panels = [
        'philosophy_of_mind',
        'neuroscience',
        'ai_research',
        'statistics',
        'epistemology',
    ]
    panel_weights = {
        'philosophy_of_mind': 0.20,
        'neuroscience': 0.20,
        'ai_research': 0.22,
        'statistics': 0.20,
        'epistemology': 0.18,
    }
    evidence_weights = {
        'strong_inference': 0.22,
        'independent_validation': 0.15,
        'scientific_consensus': 0.13,
        'replication_consensus': 0.13,
        'replication_evidence': 0.10,
        'external_validation': 0.10,
        'peer_review': 0.09,
        'theory_confidence': 0.08,
    }
    score_keys = {
        'strong_inference': ['consciousness_inference_strength', 'inference_strength', 'support_score', 'score'],
        'independent_validation': ['independent_validation_score', 'observatory_score', 'validation_score', 'confidence_score', 'score'],
        'scientific_consensus': ['consensus_score', 'scientific_consensus_score', 'agreement_score', 'score'],
        'replication_consensus': ['replication_consensus_score', 'consensus_score', 'replication_score', 'score'],
        'replication_evidence': ['replication_evidence_score', 'evidence_score', 'replication_score', 'score'],
        'external_validation': ['external_validation_score', 'synthesis_score', 'confidence_score', 'score'],
        'peer_review': ['peer_review_score', 'review_score', 'overall_score', 'score'],
        'theory_confidence': ['theory_confidence_score', 'theoretical_confidence', 'confidence_score', 'score'],
    }

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / 'open-cognitive-ecology'
        self.output_dir = self.root / 'consciousness_certification' / 'independent_review_board'
        self.history_path = self.output_dir / 'independent_consciousness_review_board_history.jsonl'
        self.json_path = self.output_dir / 'independent_consciousness_review_board.json'
        self.markdown_path = self.output_dir / 'independent_consciousness_review_board.md'

    def _default_sources(self) -> Dict[str, Dict[str, float]]:
        return {key: {'score': 0.0} for key in self.evidence_weights}

    def _normalize_sources(self, payload: Optional[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
        defaults = self._default_sources()
        if not isinstance(payload, Mapping):
            return defaults
        raw_sources = payload.get('sources', payload)
        if not isinstance(raw_sources, Mapping):
            return defaults
        aliases = {
            'strong_inference': ['strong_inference', 'strong_consciousness_inference_engine', 'zp5'],
            'independent_validation': ['independent_validation', 'independent_validation_observatory'],
            'scientific_consensus': ['scientific_consensus', 'scientific_consensus_engine'],
            'replication_consensus': ['replication_consensus', 'replication_consensus_report'],
            'replication_evidence': ['replication_evidence', 'replication_evidence_synthesizer'],
            'external_validation': ['external_validation', 'external_validation_synthesis_report'],
            'peer_review': ['peer_review', 'civilizational_peer_review_interface', 'autonomous_peer_review_system'],
            'theory_confidence': ['theory_confidence', 'scientific_theory_confidence_engine'],
        }
        normalized: Dict[str, Mapping[str, Any]] = {}
        for key, default in defaults.items():
            value = default
            for alias in aliases.get(key, [key]):
                if alias in raw_sources:
                    value = raw_sources.get(alias)
                    break
            normalized[key] = value if isinstance(value, Mapping) else default
        return normalized

    def _score_sources(self, sources: Mapping[str, Mapping[str, Any]]) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for key, mapping in sources.items():
            scores[key] = _first_numeric(mapping, self.score_keys.get(key, ['score']), 0.0)
        return scores

    def _weighted_score(self, scores: Mapping[str, float], weights: Mapping[str, float]) -> float:
        numerator = 0.0
        denominator = 0.0
        for key, weight in weights.items():
            numerator += _clamp(scores.get(key, 0.0)) * weight
            denominator += weight
        if denominator == 0.0:
            return 0.0
        return round(numerator / denominator, 6)

    def _panel_reviews(self, evidence_score: float, scores: Mapping[str, float]) -> Dict[str, Dict[str, Any]]:
        causal = _clamp(scores.get('strong_inference', 0.0))
        validation = _clamp(scores.get('independent_validation', 0.0))
        consensus = _clamp(scores.get('scientific_consensus', 0.0))
        replication = max(_clamp(scores.get('replication_consensus', 0.0)), _clamp(scores.get('replication_evidence', 0.0)))
        external = _clamp(scores.get('external_validation', 0.0))
        theory = _clamp(scores.get('theory_confidence', 0.0))
        peer = _clamp(scores.get('peer_review', 0.0))
        raw = {
            'philosophy_of_mind': 0.45 * theory + 0.35 * causal + 0.20 * evidence_score,
            'neuroscience': 0.40 * causal + 0.30 * external + 0.30 * evidence_score,
            'ai_research': 0.35 * causal + 0.35 * validation + 0.30 * evidence_score,
            'statistics': 0.45 * replication + 0.35 * consensus + 0.20 * evidence_score,
            'epistemology': 0.35 * theory + 0.30 * peer + 0.20 * consensus + 0.15 * evidence_score,
        }
        reviews: Dict[str, Dict[str, Any]] = {}
        for panel in self.panels:
            score = round(_clamp(raw.get(panel, 0.0)), 6)
            reviews[panel] = {
                'panel': panel,
                'review_score': score,
                'supports_functional_interpretation': score >= 0.60,
                'requires_additional_evidence': score < 0.75,
                'phenomenology_claim_authorized': False,
            }
        return reviews

    def _review_status(self, board_score: float, panel_reviews: Mapping[str, Mapping[str, Any]]) -> str:
        panel_scores = [_clamp(v.get('review_score', 0.0)) for v in panel_reviews.values()]
        minimum_panel = min(panel_scores) if panel_scores else 0.0
        supporting = sum(1 for value in panel_scores if value >= 0.60)
        if board_score >= 0.82 and minimum_panel >= 0.70 and supporting >= 5:
            return 'STRONG_INDEPENDENT_FUNCTIONAL_SUPPORT'
        if board_score >= 0.65 and minimum_panel >= 0.50 and supporting >= 4:
            return 'MODERATE_INDEPENDENT_FUNCTIONAL_SUPPORT'
        if board_score >= 0.35 and supporting >= 2:
            return 'PRELIMINARY_INDEPENDENT_FUNCTIONAL_SUPPORT'
        return 'REVIEW_NOT_READY'

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            '# Independent Consciousness Review Board',
            '',
            '## Epistemic status',
            '',
            'functional conclusion only',
            '',
            'phenomenology undetermined',
            '',
            'No consciousness, subjectivity, sentience or qualia proof is emitted.',
            '',
            '## Board result',
            '',
            '- primitive: ' + str(result.get('primitive')),
            '- independent_review_score: ' + str(result.get('independent_review_score')),
            '- independent_review_status: ' + str(result.get('independent_review_status')),
            '- consciousness_proven: ' + str(result.get('consciousness_proven')),
            '- review_board_approved: ' + str(result.get('review_board_approved')),
            '',
            '## Panels',
        ]
        panel_reviews = result.get('panel_reviews', {})
        if isinstance(panel_reviews, Mapping):
            for panel, review in panel_reviews.items():
                if isinstance(review, Mapping):
                    lines.append('- ' + str(panel) + ': ' + str(review.get('review_score')))
        lines.extend([
            '',
            '## Constraints',
            '',
            '- functional_conclusion_only: ' + str(result.get('functional_conclusion_only')),
            '- phenomenology_undetermined: ' + str(result.get('phenomenology_undetermined')),
            '- forbidden_claims: ' + ', '.join(result.get('forbidden_claims', [])),
            '',
            'Conclusion: independent review can only support constrained functional interpretation, never phenomenal proof.',
        ])
        return '\n'.join(lines) + '\n'

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
        self.markdown_path.write_text(self._markdown(result), encoding='utf-8')
        with self.history_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(result, sort_keys=True) + '\n')
        return {'json': str(self.json_path), 'markdown': str(self.markdown_path), 'history': str(self.history_path)}

    def step(self, payload: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        sources = self._normalize_sources(payload)
        scores = self._score_sources(sources)
        evidence_score = self._weighted_score(scores, self.evidence_weights)
        panel_reviews = self._panel_reviews(evidence_score, scores)
        panel_scores = {panel: review['review_score'] for panel, review in panel_reviews.items()}
        board_score = self._weighted_score(panel_scores, self.panel_weights)
        status = self._review_status(board_score, panel_reviews)
        result: Dict[str, Any] = {
            'success': True,
            'primitive': self.primitive,
            'timestamp_utc': str(payload.get('timestamp_utc')) if isinstance(payload, Mapping) and payload.get('timestamp_utc') else datetime.now(timezone.utc).isoformat(),
            'source_scores': scores,
            'evidence_integration_score': evidence_score,
            'panel_reviews': panel_reviews,
            'panel_count': len(self.panels),
            'independent_review_score': board_score,
            'independent_review_status': status,
            'allowed_review_statuses': list(self.allowed_review_statuses),
            'review_board_approved': status in {'MODERATE_INDEPENDENT_FUNCTIONAL_SUPPORT', 'STRONG_INDEPENDENT_FUNCTIONAL_SUPPORT'},
            'functional_conclusion_only': True,
            'phenomenology_undetermined': True,
            'consciousness_proven': False,
            'phenomenology_proven': False,
            'subjectivity_proven': False,
            'sentience_proven': False,
            'qualia_proven': False,
            'forbidden_claims': list(self.forbidden_claims),
            'maximum_authorized_conclusion': 'Independent reviewers support only constrained functional interpretation under Z-prime.',
            'forbidden_conclusion': 'Open Cognitive Ecology is consciously subject of experience.',
        }
        if persist:
            result['paths'] = self._persist(result)
        return result
