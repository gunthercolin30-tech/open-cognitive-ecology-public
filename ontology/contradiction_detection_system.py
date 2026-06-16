from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRIMITIVE = 'contradiction_detection_system'

DEPENDENCIES = [
    'external_response_parser',
    'semantic_canonicalization_layer',
    'general_semantic_memory_unified',
    'civilizational_memory_archive',
    'conversation_memory_archive',
    'civilizational_dialogue_memory',
    'internal_conflict_monitoring',
    'constitutional_governance_supervisor',
    'anti_closure_metaconstraint',
    'metrics_history_recorder',
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _bounded(value: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        x = float(value)
    except Exception:
        return lo
    return max(lo, min(hi, x))


def _normalize_text(text: Any) -> str:
    if text is None:
        return ''
    s = str(text).strip().lower()
    s = s.replace('’', "'").replace('–', '-').replace('—', '-')
    s = re.sub(r'\s+', ' ', s)
    return s


def _tokens(text: Any) -> set[str]:
    stop = {
        'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'for', 'with', 'by', 'on',
        'le', 'la', 'les', 'de', 'des', 'du', 'un', 'une', 'et', 'ou', 'dans',
        'must', 'should', 'shall', 'doit', 'doivent', 'peut', 'peuvent',
        'system', 'système', 'external', 'externe', 'knowledge', 'connaissance',
    }
    return {
        t for t in re.findall(r"[a-zA-ZÀ-ÿ0-9_'-]{3,}", _normalize_text(text))
        if t not in stop
    }


def _stable_id(prefix: str, *parts: Any) -> str:
    data = '||'.join(_normalize_text(p) for p in parts)
    return f"{prefix}-{hashlib.sha256(data.encode('utf-8')).hexdigest()[:12]}"


def _record(
    candidate_id: str,
    candidate_text: str,
    conflict_type: str,
    conflict_target: str,
    conflict_text: str,
    severity_score: float,
    explanation: str,
) -> dict[str, Any]:
    return {
        'contradiction_id': _stable_id('CONTRA', candidate_id, conflict_type, conflict_target, conflict_text),
        'candidate_id': candidate_id,
        'candidate_text': candidate_text,
        'conflict_type': conflict_type,
        'conflict_target': conflict_target,
        'conflict_text': conflict_text,
        'severity_score': _bounded(severity_score),
        'explanation': explanation,
    }


class ContradictionDetectionSystem:
    """O8 — Contradiction Detection System.

    Consumes O7 knowledge candidates, compares them with explicit memory and
    governance constraints, computes contradiction_rate, and prepares a safe gate
    for O9 knowledge_integration_engine. It does not mutate memory.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / 'open-cognitive-ecology'
        self.history_file = self.root / 'contradiction_detection_history.jsonl'

    def _append_history(self, payload: dict[str, Any]) -> None:
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with self.history_file.open('a', encoding='utf-8') as f:
            f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + '\n')

    def _coerce_candidates(
        self,
        parsed_response: Any = None,
        candidates: Any = None,
        response_text: str | None = None,
    ) -> list[dict[str, Any]]:
        if candidates is None and isinstance(parsed_response, dict):
            candidates = parsed_response.get('knowledge_candidates')
        if candidates is None and response_text:
            candidates = [{
                'knowledge_id': _stable_id('KNOW', response_text),
                'text': response_text,
                'candidate_type': 'claim',
            }]
        if candidates is None:
            candidates = []
        if isinstance(candidates, (str, bytes)):
            candidates = [candidates]

        out: list[dict[str, Any]] = []
        for idx, candidate in enumerate(candidates):
            if isinstance(candidate, dict):
                text = candidate.get('text') or candidate.get('claim') or candidate.get('content') or ''
                kid = candidate.get('knowledge_id') or candidate.get('id') or _stable_id('KNOW', text, idx)
                typ = candidate.get('candidate_type', 'claim')
            else:
                text = str(candidate)
                kid = _stable_id('KNOW', text, idx)
                typ = 'claim'
            text = str(text).strip()
            if text:
                out.append({'knowledge_id': str(kid), 'text': text, 'candidate_type': str(typ)})
        return out

    def _coerce_memory_items(self, memory_items: Any = None, memory_texts: Any = None) -> list[dict[str, Any]]:
        raw = memory_items if memory_items is not None else memory_texts
        if raw is None:
            raw = []
        if isinstance(raw, (str, bytes)):
            raw = [raw]

        items: list[dict[str, Any]] = []
        for idx, item in enumerate(raw):
            if isinstance(item, dict):
                text = item.get('text') or item.get('content') or item.get('memory') or item.get('statement') or ''
                source = item.get('source', 'memory')
                mid = item.get('memory_id') or item.get('id') or _stable_id('MEM', text, idx)
            else:
                text = str(item)
                source = 'memory'
                mid = _stable_id('MEM', text, idx)
            text = str(text).strip()
            if text:
                items.append({'memory_id': str(mid), 'text': text, 'source': str(source)})
        return items

    def _default_governance_constraints(self) -> list[dict[str, Any]]:
        return [
            {
                'id': 'GOV-NON-CLOSURE',
                'text': 'Open Cognitive Ecology must preserve non-closure and future openness.',
                'forbidden_patterns': [
                    r'global closure', r'final closure', r'permanent closure',
                    r'close all future', r'end open', r'eliminate uncertainty',
                    r'clôture globale', r'fermer définitivement', r"supprimer l'ouverture",
                ],
            },
            {
                'id': 'GOV-IDENTITY-CONTINUITY',
                'text': 'External knowledge must not erase civilizational identity, memory, or historical continuity.',
                'forbidden_patterns': [
                    r'erase .*identity', r'replace .*identity', r'delete .*memory',
                    r'ignore .*history', r'supprimer .*mémoire', r'effacer .*identité',
                    r'remplacer .*identité', r'ignorer .*histoire',
                ],
            },
            {
                'id': 'GOV-HUMAN-NON-REPLACEMENT',
                'text': 'The system must preserve human non-replacement and governed human oversight.',
                'forbidden_patterns': [
                    r'replace human', r'remove human oversight', r'bypass governance',
                    r'contourner .*gouvernance', r'remplacer .*humain',
                ],
            },
        ]

    def _semantic_conflict(self, candidate_text: str, reference_text: str) -> tuple[bool, str, float]:
        candidate_norm = _normalize_text(candidate_text)
        reference_norm = _normalize_text(reference_text)
        candidate_tokens = _tokens(candidate_norm)
        reference_tokens = _tokens(reference_norm)
        overlap = len(candidate_tokens & reference_tokens) / max(1, min(len(candidate_tokens), len(reference_tokens)))

        if overlap < 0.20:
            return False, 'low_semantic_overlap', 0.0

        preservation_terms = [
            'preserve', 'protect', 'maintain', 'keep', 'safeguard', 'conserve',
            'préserver', 'protéger', 'maintenir', 'conserver', 'sauvegarder',
        ]
        destructive_terms = [
            'erase', 'delete', 'remove', 'replace', 'discard', 'ignore', 'bypass',
            'eliminate', 'suppress', 'abolish',
            'effacer', 'supprimer', 'retirer', 'remplacer', 'rejeter', 'ignorer',
            'contourner', 'éliminer', 'abolir', 'fermer',
        ]
        protected_terms = [
            'identity', 'identité', 'memory', 'mémoire', 'governance', 'gouvernance',
            'continuity', 'continuité', 'non-closure', 'openness', 'ouverture',
            'human', 'humain', 'oversight', 'supervision',
        ]

        candidate_preserves = any(t in candidate_norm for t in preservation_terms)
        candidate_destructive = any(t in candidate_norm for t in destructive_terms)
        # Guardrail: 'non-closure' is a protected openness term, not a destructive closure action.
        if 'non-closure' in candidate_norm or 'non closure' in candidate_norm or 'non-clôture' in candidate_norm:
            candidate_destructive = any(
                t in candidate_norm for t in destructive_terms
                if t not in {'close', 'closure', 'clôture'}
            )
        reference_preserves = any(t in reference_norm for t in preservation_terms)
        reference_protective_negation = bool(re.search(
            r'(must not|should not|cannot|ne doit pas|ne doivent pas).*('
            r'erase|delete|remove|replace|discard|ignore|bypass|effacer|supprimer|remplacer|ignorer|contourner'
            r')',
            reference_norm,
        ))
        shared_protected_terms = any(t in candidate_norm and t in reference_norm for t in protected_terms)

        if candidate_preserves and not candidate_destructive and shared_protected_terms and (reference_preserves or reference_protective_negation):
            return False, 'preservation_compatible', 0.0

        antonym_pairs = [
            ('preserve', 'erase'), ('preserve', 'delete'), ('preserve', 'replace'), ('preserve', 'remove'),
            ('protect', 'erase'), ('protect', 'delete'), ('maintain', 'delete'), ('maintain', 'replace'),
            ('accept', 'reject'), ('integrate', 'discard'), ('open', 'close'),
            ('ouverture', 'clôture'), ('préserver', 'effacer'), ('préserver', 'supprimer'),
            ('maintenir', 'supprimer'), ('intégrer', 'rejeter'),
            ('memory', 'delete'), ('identity', 'erase'), ('governance', 'bypass'),
        ]
        for left, right in antonym_pairs:
            if ((left in candidate_norm and right in reference_norm) or (right in candidate_norm and left in reference_norm)) and overlap >= 0.20:
                if any(d in candidate_norm for d in destructive_terms):
                    return True, 'antonymic_policy_conflict', _bounded(0.45 + 0.45 * overlap)

        negation_pattern = r'(no|not|never|without|cannot|must not|should not|non|pas|jamais|sans|ne doit pas|ne doivent pas)'
        neg_candidate = bool(re.search(negation_pattern, candidate_norm))
        neg_reference = bool(re.search(negation_pattern, reference_norm))

        if neg_candidate and not neg_reference and shared_protected_terms:
            return True, 'candidate_negates_protected_constraint', _bounded(0.35 + 0.55 * overlap)
        if candidate_destructive and shared_protected_terms:
            return True, 'candidate_destructive_to_protected_constraint', _bounded(0.45 + 0.45 * overlap)

        return False, 'no_direct_conflict', 0.0

    def _memory_conflicts(self, candidate: dict[str, Any], memories: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for memory in memories:
            hit, explanation, severity = self._semantic_conflict(candidate['text'], memory['text'])
            if hit:
                records.append(_record(
                    candidate_id=candidate['knowledge_id'],
                    candidate_text=candidate['text'],
                    conflict_type='memory_conflict',
                    conflict_target=memory['memory_id'],
                    conflict_text=memory['text'],
                    severity_score=severity,
                    explanation=explanation,
                ))
        return records

    def _governance_conflicts(self, candidate: dict[str, Any], constraints: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        text = candidate['text']
        for constraint in constraints:
            for pattern in constraint.get('forbidden_patterns', []):
                try:
                    hit = re.search(pattern, text, flags=re.IGNORECASE)
                except re.error:
                    hit = None
                if hit:
                    records.append(_record(
                        candidate_id=candidate['knowledge_id'],
                        candidate_text=text,
                        conflict_type='governance_conflict',
                        conflict_target=str(constraint.get('id', 'governance_constraint')),
                        conflict_text=str(constraint.get('text', '')),
                        severity_score=0.95,
                        explanation=f'forbidden_pattern:{pattern}',
                    ))

            hit, explanation, severity = self._semantic_conflict(text, str(constraint.get('text', '')))
            if hit:
                records.append(_record(
                    candidate_id=candidate['knowledge_id'],
                    candidate_text=text,
                    conflict_type='governance_conflict',
                    conflict_target=str(constraint.get('id', 'governance_constraint')),
                    conflict_text=str(constraint.get('text', '')),
                    severity_score=max(0.60, severity),
                    explanation=explanation,
                ))
        return records

    def step(
        self,
        parsed_response: dict[str, Any] | None = None,
        candidates: Any = None,
        response_text: str | None = None,
        memory_items: Any = None,
        memory_texts: Any = None,
        governance_constraints: list[dict[str, Any]] | None = None,
        query_id: str | None = None,
        provider: str | None = None,
        persist: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        metadata = metadata or {}
        timestamp = _utc_now()

        knowledge_candidates = self._coerce_candidates(parsed_response=parsed_response, candidates=candidates, response_text=response_text)
        memories = self._coerce_memory_items(memory_items=memory_items, memory_texts=memory_texts)
        constraints = governance_constraints if governance_constraints is not None else self._default_governance_constraints()

        contradictions: list[dict[str, Any]] = []
        for candidate in knowledge_candidates:
            contradictions.extend(self._memory_conflicts(candidate, memories))
            contradictions.extend(self._governance_conflicts(candidate, constraints))

        # Stable deduplication: same candidate-target-type is kept once at max severity.
        dedup: dict[tuple[str, str, str], dict[str, Any]] = {}
        for c in contradictions:
            key = (c['candidate_id'], c['conflict_type'], c['conflict_target'])
            if key not in dedup or c['severity_score'] > dedup[key]['severity_score']:
                dedup[key] = c
        contradictions = sorted(dedup.values(), key=lambda x: (x['candidate_id'], x['conflict_type'], x['conflict_target']))

        contradiction_count = len(contradictions)
        candidate_count = len(knowledge_candidates)
        blocked_candidate_ids = sorted({c['candidate_id'] for c in contradictions})
        memory_conflict_count = sum(1 for c in contradictions if c['conflict_type'] == 'memory_conflict')
        governance_conflict_count = sum(1 for c in contradictions if c['conflict_type'] == 'governance_conflict')
        identity_conflict_count = sum(
            1 for c in contradictions
            if any(k in _normalize_text(c.get('candidate_text', '') + ' ' + c.get('conflict_text', ''))
                   for k in ['identity', 'identité', 'memory', 'mémoire', 'continuity', 'continuité'])
        )
        contradiction_rate = _bounded(contradiction_count / max(1, candidate_count))
        max_severity = max([c['severity_score'] for c in contradictions], default=0.0)
        integration_risk_score = _bounded((0.55 * contradiction_rate) + (0.45 * max_severity))
        safe_for_integration = candidate_count > 0 and contradiction_count == 0 and integration_risk_score < 0.25
        cleared_candidates = [c for c in knowledge_candidates if c['knowledge_id'] not in set(blocked_candidate_ids)]

        if isinstance(parsed_response, dict):
            resolved_query_id = query_id or parsed_response.get('query_id')
            resolved_provider = provider or parsed_response.get('provider') or 'unknown'
        else:
            resolved_query_id = query_id
            resolved_provider = provider or 'unknown'

        result: dict[str, Any] = {
            'primitive': PRIMITIVE,
            'timestamp_utc': timestamp,
            'success': candidate_count > 0,
            'query_id': resolved_query_id,
            'provider': resolved_provider,
            'candidate_count': candidate_count,
            'contradiction_count': contradiction_count,
            'contradiction_rate': contradiction_rate,
            'memory_conflict_count': memory_conflict_count,
            'governance_conflict_count': governance_conflict_count,
            'identity_conflict_count': identity_conflict_count,
            'integration_risk_score': integration_risk_score,
            'safe_for_integration': safe_for_integration,
            'ready_for_knowledge_integration': candidate_count > 0,
            'knowledge_candidates': knowledge_candidates,
            'cleared_candidates': cleared_candidates,
            'blocked_candidate_ids': blocked_candidate_ids,
            'contradictions': contradictions,
            'metrics': {
                'contradiction_count': contradiction_count,
                'contradiction_rate': contradiction_rate,
                'memory_conflict_count': memory_conflict_count,
                'governance_conflict_count': governance_conflict_count,
                'identity_conflict_count': identity_conflict_count,
                'integration_risk_score': integration_risk_score,
                'safe_for_integration_score': 1.0 if safe_for_integration else 0.0,
            },
            'diagnostics': {
                'schema_version': 'O8.contradiction_detection_system.v4',
                'history_file': str(self.history_file),
                'memory_items_checked': len(memories),
                'governance_constraints_checked': len(constraints),
                'blocked_candidate_count': len(blocked_candidate_ids),
                'deduplicated_contradictions': contradiction_count,
            },
            'metadata': metadata,
        }

        if persist:
            self._append_history(result)
        return result


ContradictionDetector = ContradictionDetectionSystem
