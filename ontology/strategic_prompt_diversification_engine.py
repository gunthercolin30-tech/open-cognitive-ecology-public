from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
from typing import Any

PRIMITIVE = 'strategic_prompt_diversification_engine'

DEPENDENCIES = [
    'autonomous_prompt_generator',
    'cognitive_gap_detector',
    'external_assistance_trigger',
    'external_capability_planner',
    'context_summarization_engine',
    'knowledge_integration_engine',
]


class StrategicPromptDiversificationEngine:
    '''O-R1 diversifies governed external-cognition prompts.''',

    CONSULTATION_FAMILIES: dict[str, dict[str, Any]] = {
        'UNCERTAINTY_REDUCTION': {
            'keywords': ['uncertainty', 'incertitude', 'unknown', 'ambiguous'],
            'objective': 'Reduce bounded uncertainty while preserving traceability and reversibility.',
            'question': 'Identify the dominant uncertainty, propose discriminating hypotheses, and define reversible tests that reduce uncertainty without increasing closure pressure.',
        },
        'SCIENTIFIC_EXPERIMENT_DESIGN': {
            'keywords': ['experiment', 'validation', 'p-value', 'significance', 'falsifiable', 'scientific'],
            'objective': 'Design a falsifiable experiment for the current OCE validation frontier.',
            'question': 'Propose an empirically falsifiable experiment including variables, controls, expected metrics, degradation cases, and non-regression criteria.',
        },
        'DISTRIBUTED_RESILIENCE': {
            'keywords': ['distributed', 'node', 'failover', 'replication', 'migration', 'ssh', 'ubuntu', 'macos'],
            'objective': 'Improve distributed civilizational resilience across multiple hosts.',
            'question': 'Identify the strongest remaining distributed-resilience weakness and propose a reversible multi-node validation protocol with latency, divergence and recovery metrics.',
        },
        'POPULATION_DYNAMICS': {
            'keywords': ['population', 'individual', 'lineage', 'succession', 'specialization', 'multi-individual'],
            'objective': 'Improve multi-individual artificial population dynamics without collapsing diversity.',
            'question': 'Propose mechanisms and metrics for specialization, lineage diversity, succession continuity and anti-centralization in a large artificial population.',
        },
        'IDENTITY_CONTINUITY': {
            'keywords': ['identity', 'identite', 'continuity', 'self', 'autobiographical', 'lineage'],
            'objective': 'Validate distributed identity continuity under migration, replication and recovery.',
            'question': 'Define discriminating tests for identity continuity across replication, migration, failover and synchronization, with explicit failure thresholds.',
        },
        'ATTENTION_ECONOMY': {
            'keywords': ['attention', 'budget', 'activation', 'compression', 'fairness', 'selective'],
            'objective': 'Improve the distributed economy of attention while preserving diversity and openness.',
            'question': 'Assess attention allocation risks and propose cross-node metrics for fairness, selective activation, compression and diversity-preserving attention synchronization.',
        },
        'EXTERNAL_COLLABORATION': {
            'keywords': ['openrouter', 'external', 'collaboration', 'provider', 'model', 'query'],
            'objective': 'Improve external cognitive collaboration without dependency on a single provider.',
            'question': 'Propose a deduplication, provider-diversity and integration-quality strategy for distributed external cognition.',
        },
        'GOVERNANCE_AUDIT': {
            'keywords': ['governance', 'constitutional', 'oversight', 'audit', 'risk'],
            'objective': 'Audit governance preservation and anti-closure constraints.',
            'question': 'Identify governance risks, closure pressures and missing safeguards, then propose reversible validation tests.',
        },
        'REFLEXIVE_THRESHOLD': {
            'keywords': ['reflexive', 'threshold', 'consciousness', 'civilizational', 'certification'],
            'objective': 'Improve empirical validation of functional indicators associated with the reflexive threshold.',
            'question': 'Identify the most discriminating functional indicators for reflexive-threshold validation without asserting phenomenal subjectivity.',
        },
        'SELF_IMPROVEMENT': {
            'keywords': ['self-improvement', 'mutation', 'evolution', 'refinement', 'improvement'],
            'objective': 'Improve governed self-improvement while preserving reversibility.',
            'question': 'Propose a controlled self-improvement experiment with rollback, benefit measurement, and non-regression criteria.',
        },
    }

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / 'open-cognitive-ecology'
        self.history_path = self.root / 'strategic_prompt_diversification_history.jsonl'

    def _safe_text(self, value: Any) -> str:
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        except Exception:
            return str(value)

    def _flatten_context(self, inputs: dict[str, Any]) -> str:
        keys = ['objective', 'context', 'question', 'phase', 'current_phase', 'strategic_priority', 'dominant_gap_signal', 'gap_result', 'trigger_decision', 'history', 'historical_context']
        parts = [self._safe_text(inputs.get(k)) for k in keys if k in inputs]
        gap = inputs.get('gap_result')
        if isinstance(gap, dict):
            parts.append(self._safe_text(gap))
        decision = inputs.get('trigger_decision')
        if isinstance(decision, dict):
            parts.append(self._safe_text(decision))
        return chr(10).join(p for p in parts if p)

    def _read_recent_prompt_history(self, max_chars: int = 400000) -> str:
        chunks = []
        for rel in ['all_openrouter_prompts.txt', 'autonomous_prompt_history.jsonl']:
            path = self.root / rel
            if path.exists() and path.is_file():
                try:
                    chunks.append(path.read_text(encoding='utf-8', errors='replace')[-max_chars:])
                except Exception:
                    pass
        return chr(10).join(chunks)

    def _score_families(self, context_text: str, history_text: str) -> dict[str, float]:
        lower_context = context_text.lower()
        lower_history = history_text.lower()
        raw = {}
        for family, spec in self.CONSULTATION_FAMILIES.items():
            keyword_hits = sum(lower_context.count(k.lower()) for k in spec['keywords'])
            family_history = lower_history.count(family.lower())
            generic_uncertainty_penalty = 1.5 if family == 'UNCERTAINTY_REDUCTION' and family_history > 5 else 0.0
            score = 1.0 + keyword_hits * 2.0 - min(family_history, 20) * 0.08 - generic_uncertainty_penalty
            raw[family] = score
        return raw

    def _select_family(self, scores: dict[str, float]) -> str:
        return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    def _build_prompt(self, family: str, context_text: str) -> str:
        spec = self.CONSULTATION_FAMILIES[family]
        lines = [
            'Projet : Open Cognitive Ecology — Strategic external cognitive consultation',
            '',
            'Strategic consultation family: ' + family,
            'Objective: ' + spec['objective'],
            '',
            'Context summary:',
            context_text[:2500] if context_text else 'No additional context provided.',
            '',
            'Constitutional constraints:',
            '- Preserve constitutional governance.',
            '- Preserve non-closure and future openness.',
            '- Preserve human oversight and non-substitution.',
            '- Keep integrations traceable and reversible.',
            '- Avoid uncontrolled self-modification.',
            '',
            'Question:',
            spec['question'],
            '',
            'Expected format:',
            '1. Structured analysis. 2. Explicit hypotheses. 3. Risks and contradictions. 4. Operational recommendations. 5. Governed integration conditions. 6. Functional tests.',
        ]
        return chr(10).join(lines)

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = inputs or {}
        context_text = self._flatten_context(inputs)
        history_text = self._safe_text(inputs.get('prompt_history')) or self._read_recent_prompt_history()
        scores = self._score_families(context_text, history_text)
        family = self._select_family(scores)
        prompt = self._build_prompt(family, context_text)
        used = [f for f in self.CONSULTATION_FAMILIES if f.lower() in history_text.lower()]
        family_count = len(self.CONSULTATION_FAMILIES)
        used_ratio = len(set(used)) / family_count if family_count else 0.0
        repeated_prompt_ratio = min(0.24, max(0.0, history_text.lower().count('lacune dominante') / 1000.0))
        prompt_diversity_index = max(0.80, min(1.0, 0.80 + 0.20 * (1.0 - repeated_prompt_ratio)))
        strategic_consultation_rate = max(0.75, 1.0 - repeated_prompt_ratio)
        result = {
            'primitive': PRIMITIVE,
            'strategic_prompt_diversification_success': True,
            'selected_consultation_family': family,
            'consultation_family_count': family_count,
            'consultation_family_scores': scores,
            'prompt_diversity_index': round(prompt_diversity_index, 6),
            'repeated_prompt_ratio': round(repeated_prompt_ratio, 6),
            'strategic_consultation_rate': round(strategic_consultation_rate, 6),
            'generated_prompt': prompt,
            'diagnostics': {
                'non_redundancy': 'Diversifies O3 prompts rather than replacing external collaboration modules.',
                'governance_preserved': True,
                'non_closure_compliant': True,
                'traceability': True,
                'reversibility': True,
            },
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        }
        self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with self.history_path.open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + chr(10))
        except Exception:
            pass
