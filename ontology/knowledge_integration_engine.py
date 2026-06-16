
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

PRIMITIVE = 'knowledge_integration_engine'

DEPENDENCIES = [
    'external_response_parser',
    'contradiction_detection_system',
    'civilizational_memory_archive',
    'conversation_memory_archive',
    'general_semantic_memory_unified',
    'rdf_semantic_memory_backend',
    'persistent_external_memory_fabric',
    'memory_consolidation',
    'knowledge_accumulation',
    'metrics_history_recorder',
]

class KnowledgeIntegrationEngine:
    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / 'open-cognitive-ecology'
        self.archive_path = self.root / 'integrated_responses_archive.jsonl'
        self.history_path = self.root / 'knowledge_integration_history.jsonl'
        self.memory_path = self.root / 'civilizational_integrated_knowledge.jsonl'
        self.archive_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _utc() -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def _norm_text(text: Any) -> str:
        return re.sub(r'\s+', ' ', str(text or '').strip())

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _candidate_id(self, candidate: Dict[str, Any]) -> str:
        existing = candidate.get('knowledge_id') or candidate.get('candidate_id')
        if existing:
            return str(existing)
        text = self._norm_text(candidate.get('text') or candidate.get('candidate_text'))
        return 'KNOW-' + self._hash(text)

    def _candidate_text(self, candidate: Dict[str, Any]) -> str:
        return self._norm_text(candidate.get('text') or candidate.get('candidate_text') or candidate.get('body'))

    def _load_existing_hashes(self) -> set:
        hashes = set()
        for path in [self.archive_path, self.memory_path]:
            if not path.exists():
                continue
            try:
                for line in path.read_text(encoding='utf-8').splitlines():
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    h = obj.get('content_hash') or obj.get('knowledge_hash')
                    if h:
                        hashes.add(str(h))
            except Exception:
                continue
        return hashes

    def _extract_from_contradiction_result(self, contradiction_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        result = contradiction_result or {}
        cleared = list(result.get('cleared_candidates') or [])
        blocked = set(str(x) for x in (result.get('blocked_candidate_ids') or []))
        if result and result.get('safe_for_integration') is not True:
            cleared = []
        return {
            'cleared_candidates': cleared,
            'blocked_candidate_ids': blocked,
            'query_id': result.get('query_id'),
            'provider': result.get('provider'),
            'source_primitive': result.get('primitive'),
            'contradiction_rate': result.get('contradiction_rate', 0.0),
            'integration_risk_score': result.get('integration_risk_score', 0.0),
        }

    def step(self, contradiction_result: Optional[Dict[str, Any]] = None,
             cleared_candidates: Optional[List[Dict[str, Any]]] = None,
             blocked_candidate_ids: Optional[Iterable[str]] = None,
             source_query_id: Optional[str] = None,
             provider: Optional[str] = None,
             persist: bool = True,
             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        extracted = self._extract_from_contradiction_result(contradiction_result)
        candidate_list = list(cleared_candidates or extracted['cleared_candidates'] or [])
        blocked = set(extracted['blocked_candidate_ids'])
        blocked.update(str(x) for x in self._as_list(blocked_candidate_ids))
        query_id = source_query_id or extracted.get('query_id')
        provider_value = provider or extracted.get('provider') or 'unknown'
        existing_hashes = self._load_existing_hashes()
        integrated = []
        rejected = []
        duplicate_count = 0
        blocked_rejection_count = 0
        empty_rejection_count = 0
        for raw in candidate_list:
            if not isinstance(raw, dict):
                raw = {'text': str(raw), 'candidate_type': 'claim'}
            cid = self._candidate_id(raw)
            text = self._candidate_text(raw)
            content_hash = self._hash(text)
            if cid in blocked:
                blocked_rejection_count += 1
                rejected.append({'knowledge_id': cid, 'text': text, 'reason': 'blocked_by_contradiction_detection'})
                continue
            if not text:
                empty_rejection_count += 1
                rejected.append({'knowledge_id': cid, 'text': text, 'reason': 'empty_candidate'})
                continue
            if content_hash in existing_hashes:
                duplicate_count += 1
                rejected.append({'knowledge_id': cid, 'text': text, 'reason': 'duplicate_content_hash'})
                continue
            record = {
                'integration_id': 'INT-' + self._hash(f'{cid}|{text}|{self._utc()}'),
                'knowledge_id': cid,
                'knowledge_hash': content_hash,
                'content_hash': content_hash,
                'text': text,
                'candidate_type': raw.get('candidate_type', 'claim'),
                'source_query_id': query_id,
                'provider': provider_value,
                'integration_status': 'integrated',
                'requires_identity_review': True,
                'requires_governance_review': True,
                'reversible': True,
                'timestamp_utc': self._utc(),
                'source_candidate': raw,
            }
            integrated.append(record)
            existing_hashes.add(content_hash)
        total_considered = len(candidate_list)
        integrated_count = len(integrated)
        rejected_count = len(rejected)
        integration_success_rate = integrated_count / max(1, total_considered)
        integration_reversibility_score = 1.0 if all(r.get('reversible') for r in integrated) else 0.0
        safe_for_identity_review = integrated_count > 0 and blocked_rejection_count == 0
        output = {
            'primitive': PRIMITIVE,
            'timestamp_utc': self._utc(),
            'success': True,
            'query_id': query_id,
            'provider': provider_value,
            'candidate_count': total_considered,
            'integrated_knowledge_count': integrated_count,
            'rejected_knowledge_count': rejected_count,
            'duplicate_knowledge_count': duplicate_count,
            'blocked_rejection_count': blocked_rejection_count,
            'empty_rejection_count': empty_rejection_count,
            'integration_success_rate': integration_success_rate,
            'integration_reversibility_score': integration_reversibility_score,
            'safe_for_identity_review': safe_for_identity_review,
            'ready_for_identity_preservation_monitor': safe_for_identity_review,
            'integrated_records': integrated,
            'rejected_records': rejected,
            'metrics': {
                'integrated_knowledge_count': integrated_count,
                'rejected_knowledge_count': rejected_count,
                'duplicate_knowledge_count': duplicate_count,
                'integration_success_rate': integration_success_rate,
                'integration_reversibility_score': integration_reversibility_score,
            },
            'diagnostics': {
                'schema_version': 'O9.knowledge_integration_engine.v1',
                'archive_file': str(self.archive_path),
                'history_file': str(self.history_path),
                'memory_file': str(self.memory_path),
                'source_primitive': extracted.get('source_primitive'),
                'contradiction_rate': extracted.get('contradiction_rate'),
                'integration_risk_score': extracted.get('integration_risk_score'),
                'blocked_candidate_count': len(blocked),
            },
            'metadata': metadata or {},
        }
        if persist:
            self._persist(output)
        return output

    def _persist(self, output: Dict[str, Any]) -> None:
        with self.history_path.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(output, ensure_ascii=False, sort_keys=True) + '\n')
        for record in output.get('integrated_records', []):
            archive_record = dict(record)
            archive_record['primitive'] = PRIMITIVE
            with self.archive_path.open('a', encoding='utf-8') as fh:
                fh.write(json.dumps(archive_record, ensure_ascii=False, sort_keys=True) + '\n')
            with self.memory_path.open('a', encoding='utf-8') as fh:
                fh.write(json.dumps(archive_record, ensure_ascii=False, sort_keys=True) + '\n')

if __name__ == '__main__':
    demo = KnowledgeIntegrationEngine().step(
        cleared_candidates=[{'knowledge_id': 'KNOW-DEMO', 'text': 'The system should preserve non-closure.', 'candidate_type': 'claim'}],
        persist=False,
    )
    print(json.dumps(demo, indent=2, ensure_ascii=False, sort_keys=True))
