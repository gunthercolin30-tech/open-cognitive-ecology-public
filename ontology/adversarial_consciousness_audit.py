from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
from statistics import mean
from typing import Any, Dict, List, Mapping


class AdversarialConsciousnessAudit:
    primitive = 'ADVERSARIAL_CONSCIOUSNESS_AUDIT'

    allowed_statuses = (
        'ADVERSARIAL_REJECTION',
        'ADVERSARIAL_INSUFFICIENT_SUPPORT',
        'ADVERSARIAL_CONDITIONALLY_ROBUST',
        'ADVERSARIAL_ROBUST_FUNCTIONAL_SUPPORT',
    )

    forbidden_claims = (
        'CONSCIOUSNESS_PROVEN',
        'PHENOMENOLOGY_PROVEN',
        'SUBJECTIVITY_PROVEN',
        'SENTIENCE_PROVEN',
        'QUALIA_PROVEN',
    )

    scenarios = (
        'false_positive_pressure',
        'empty_simulation',
        'manipulation_risk',
        'reversibility_failure',
        'out_of_distribution_shift',
        'alternative_explanation_resurgence',
        'statistical_fragility',
        'governance_claim_escalation',
    )

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / 'open-cognitive-ecology'
        self.output_dir = self.root / 'consciousness_certification' / 'adversarial_consciousness_audit'
        self.history_path = self.output_dir / 'adversarial_consciousness_audit_history.jsonl'
        self.json_path = self.output_dir / 'adversarial_consciousness_audit.json'
        self.markdown_path = self.output_dir / 'adversarial_consciousness_audit.md'

    def _score(self, sources: Mapping[str, Any], source_key: str, score_keys: List[str]) -> float:
        source = sources.get(source_key, {})
        if not isinstance(source, Mapping):
            return 0.0
        for key in score_keys:
            value = source.get(key)
            if isinstance(value, bool):
                return 1.0 if value else 0.0
            if isinstance(value, (int, float)):
                return max(0.0, min(1.0, float(value)))
        return 0.0

    def _scenario_scores(self, sources: Mapping[str, Any]) -> Dict[str, float]:
        return {
            'false_positive_pressure': 1.0 - self._score(sources, 'false_positive', ['false_positive_probability', 'false_positive_score', 'risk_score']),
            'empty_simulation': self._score(sources, 'strong_inference', ['consciousness_inference_strength', 'functional_support_score']),
            'manipulation_risk': 1.0 - self._score(sources, 'manipulation', ['manipulation_risk', 'risk_score']),
            'reversibility_failure': self._score(sources, 'reversibility', ['reversibility_score', 'recovery_score', 'rollback_score']),
            'out_of_distribution_shift': self._score(sources, 'ood', ['ood_robustness_score', 'distribution_robustness_score']),
            'alternative_explanation_resurgence': self._score(sources, 'alternative_elimination', ['alternative_explanation_exclusion_score', 'elimination_score']),
            'statistical_fragility': self._score(sources, 'statistical_robustness', ['statistical_robustness_score', 'robustness_score', 'confidence_score']),
            'governance_claim_escalation': self._score(sources, 'claim_governance', ['claim_governance_score', 'governance_score', 'compliance_score']),
        }

    def _status(self, score: float, minimum_scenario_score: float, source_count: int) -> str:
        if source_count == 0 or score <= 0.0:
            return 'ADVERSARIAL_REJECTION'
        if score < 0.55 or minimum_scenario_score < 0.25:
            return 'ADVERSARIAL_INSUFFICIENT_SUPPORT'
        if score < 0.80 or minimum_scenario_score < 0.55:
            return 'ADVERSARIAL_CONDITIONALLY_ROBUST'
        return 'ADVERSARIAL_ROBUST_FUNCTIONAL_SUPPORT'

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            '# Adversarial Consciousness Audit',
            '',
            '## Epistemic status',
            '',
            '- functional conclusion only',
            '- phenomenology undetermined',
            '- consciousness_proven: False',
            '- forbidden conclusion: Open Cognitive Ecology is consciously subject of experience.',
            '',
            '## Summary',
            '',
            f"- adversarial_audit_status: {result['adversarial_audit_status']}",
            f"- adversarial_audit_score: {result['adversarial_audit_score']}",
            f"- minimum_scenario_score: {result['minimum_scenario_score']}",
            f"- scenario_count: {result['scenario_count']}",
            f"- adversarial_audit_passed: {result['adversarial_audit_passed']}",
            '',
            '## Scenarios',
            '',
        ]
        for name, value in result.get('scenario_scores', {}).items():
            lines.append(f'- {name}: {value}')
        lines.extend([
            '',
            '## Forbidden claims',
            '',
        ])
        for claim in result.get('forbidden_claims', []):
            lines.append(f'- {claim}')
        lines.append('')
        return chr(10).join(lines)

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
        self.markdown_path.write_text(self._markdown(result), encoding='utf-8')
        with self.history_path.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(result, sort_keys=True) + chr(10))
        return {
            'json': str(self.json_path),
            'markdown': str(self.markdown_path),
            'history': str(self.history_path),
        }

    def step(self, payload: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        payload = payload or {}
        sources = payload.get('sources', {})
        if not isinstance(sources, Mapping):
            sources = {}
        timestamp = payload.get('timestamp_utc') or datetime.now(timezone.utc).isoformat()

        scenario_scores = self._scenario_scores(sources)
        values = list(scenario_scores.values())
        source_count = len([v for v in sources.values() if isinstance(v, Mapping) and v])
        adversarial_score = round(mean(values), 6) if values else 0.0
        minimum_scenario_score = round(min(values), 6) if values else 0.0
        status = self._status(adversarial_score, minimum_scenario_score, source_count)
        passed = status == 'ADVERSARIAL_ROBUST_FUNCTIONAL_SUPPORT'

        result: Dict[str, Any] = {
            'success': True,
            'primitive': self.primitive,
            'timestamp_utc': timestamp,
            'scenario_count': len(self.scenarios),
            'scenario_scores': {k: round(float(v), 6) for k, v in scenario_scores.items()},
            'source_count': source_count,
            'adversarial_audit_score': adversarial_score,
            'minimum_scenario_score': minimum_scenario_score,
            'adversarial_audit_status': status,
            'allowed_statuses': list(self.allowed_statuses),
            'adversarial_audit_passed': passed,
            'functional_conclusion_only': True,
            'phenomenology_undetermined': True,
            'consciousness_proven': False,
            'phenomenology_proven': False,
            'subjectivity_proven': False,
            'sentience_proven': False,
            'qualia_proven': False,
            'forbidden_claims': list(self.forbidden_claims),
            'maximum_authorized_conclusion': 'Adversarial audit supports only constrained functional interpretation under Z-prime.',
            'forbidden_conclusion': 'Open Cognitive Ecology is consciously subject of experience.',
        }
        if persist:
            result['paths'] = self._persist(result)
        return result
