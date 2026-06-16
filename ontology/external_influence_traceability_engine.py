# -*- coding: utf-8 -*-

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PRIMITIVE = 'external_influence_traceability_engine'

DEPENDENCIES = [
    'knowledge_integration_engine',
    'external_response_parser',
    'contradiction_detection_system',
    'civilizational_memory_archive',
    'civilizational_state_persistence',
    'scientific_priority_scheduler',
    'civilizational_strategy_orchestrator',
    'civilizational_strategic_planner',
    'autonomous_decision_engine',
    'autonomous_action_execution',
    'experience_integration_loop',
    'metrics_history_recorder',
    'civilizational_metrics_synthesizer',
]

BEHAVIORAL_SOURCES = {
    'priority': ['scientific_priority_scheduler_history.jsonl', 'scientific_priority_queue.json', 'scientific_hypotheses.json'],
    'strategy': ['civilizational_strategy_history.jsonl', 'civilizational_state/latest_state.json', 'runtime_experiments/strategy_history.jsonl'],
    'decision': ['autonomous_decision_history.jsonl', 'runtime_experiments/autonomous_decision_history.jsonl'],
    'action': ['autonomous_action_history.jsonl', 'runtime_experiments/autonomous_action_history.jsonl'],
    'runtime': ['metrics_history.jsonl', 'metrics/metrics_history.jsonl', 'runtime_experiments/runtime_history.jsonl', 'runtime_experiments/experiment_history.jsonl'],
    'revision': ['scientific_self_revision_history.jsonl', 'self_improvement_history.jsonl', 'mutation_history.jsonl', 'capability_discovery_history.jsonl'],
}

INTEGRATION_SOURCES = ['knowledge_integration_history.jsonl', 'integrated_responses_archive.jsonl', 'collaboration_history_repository.jsonl']

STOPWORDS = {
    'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'while',
    'pour', 'avec', 'dans', 'des', 'les', 'une', 'que', 'qui', 'sur', 'aux',
    'open', 'cognitive', 'ecology', 'system', 'response', 'analysis',
    'recommendation', 'recommendations', 'integration', 'external',
}


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def _bounded(value: Any, default: float = 0.0) -> float:
    return max(0.0, min(1.0, _safe_float(value, default)))


def _parse_time(value: Any) -> Optional[datetime]:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    variants = [text, text[:-1] + '+00:00'] if text.endswith('Z') else [text]
    for fmt in ('%Y%m%dT%H%M%SZ', '%Y-%m-%dT%H:%M:%SZ'):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            pass
    for candidate in variants:
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    return None


def _json_text(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def _norm(text: Any) -> str:
    return re.sub(r'\s+', ' ', str(text or '').strip())


def _hash(text: Any) -> str:
    return hashlib.sha256(_norm(text).encode('utf-8')).hexdigest()[:16]


def _tokens(text: Any) -> List[str]:
    raw = re.findall(r'[A-Za-zÀ-ÿ0-9_\-]{4,}', _norm(text).lower())
    return [t for t in raw if t not in STOPWORDS]


def _keywords(text: Any, limit: int = 16) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for token in _tokens(text):
        if token in seen:
            continue
        seen.add(token)
        out.append(token)
        if len(out) >= limit:
            break
    return out


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)


class ExternalInfluenceTraceabilityEngine:
    '''Trace external-knowledge influence on later OCE behavior.

    The engine is observational only: it does not infer phenomenology, modify
    strategy, authorize actions, or change code. It builds reversible
    correlational traces between externally integrated knowledge and later
    priority, strategy, decision, action, revision or runtime events.
    '''

    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / 'open-cognitive-ecology'
        self.trace_dir = self.root / 'external_influence_traces'
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.trace_dir / 'external_influence_traceability_history.jsonl'
        self.latest_report_path = self.trace_dir / 'latest_external_influence_report.json'

    def _read_jsonl(self, path: Path, limit: int = 5000) -> List[Dict[str, Any]]:
        if not path.exists() or not path.is_file():
            return []
        records: List[Dict[str, Any]] = []
        try:
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        except Exception:
            return []
        for line in lines[-limit:]:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except Exception:
                obj = {'raw_text': line}
            if isinstance(obj, dict):
                obj.setdefault('_source_file', _rel(path, self.root))
                records.append(obj)
        return records

    def _read_json_file(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists() or not path.is_file():
            return []
        try:
            data = json.loads(path.read_text(encoding='utf-8', errors='replace'))
        except Exception:
            return []
        if isinstance(data, list):
            return [x if isinstance(x, dict) else {'value': x, '_source_file': _rel(path, self.root)} for x in data]
        if isinstance(data, dict):
            data.setdefault('_source_file', _rel(path, self.root))
            return [data]
        return [{'value': data, '_source_file': _rel(path, self.root)}]

    def _time_from_record(self, record: Dict[str, Any]) -> Optional[datetime]:
        for key in ('timestamp_utc', 'timestamp', 'created_at', 'time', 'generated_at', 'last_execution_utc', 'saved_at', 'recorded_at'):
            dt = _parse_time(record.get(key))
            if dt:
                return dt
        return None

    def _within_window(self, record: Dict[str, Any], since: datetime) -> bool:
        dt = self._time_from_record(record)
        if dt is None:
            return True
        return dt >= since

    def _extract_integrated_records(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        integrated = raw.get('integrated_records')
        if isinstance(integrated, list):
            for item in integrated:
                if isinstance(item, dict):
                    rec = dict(item)
                    rec.setdefault('source_query_id', raw.get('query_id') or raw.get('source_query_id'))
                    rec.setdefault('provider', raw.get('provider'))
                    rec.setdefault('timestamp_utc', raw.get('timestamp_utc') or raw.get('timestamp'))
                    rec.setdefault('_source_file', raw.get('_source_file'))
                    records.append(rec)
        elif raw.get('integration_status') == 'integrated' or raw.get('knowledge_id') or raw.get('text'):
            records.append(dict(raw))
        return records

    def _load_integrations(self, since: datetime) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for relative in INTEGRATION_SOURCES:
            path = self.root / relative
            for raw in self._read_jsonl(path):
                if self._within_window(raw, since):
                    out.extend(self._extract_integrated_records(raw))
        dedup: Dict[str, Dict[str, Any]] = {}
        for rec in out:
            text = rec.get('text') or rec.get('candidate_text') or rec.get('body') or _json_text(rec.get('source_candidate'))
            key = str(rec.get('integration_id') or rec.get('knowledge_id') or rec.get('knowledge_hash') or _hash(text))
            rec['text'] = _norm(text)
            rec['trace_keywords'] = _keywords(text)
            rec['trace_key'] = key
            rec['trace_timestamp'] = (self._time_from_record(rec) or datetime.now(timezone.utc)).isoformat().replace('+00:00', 'Z')
            dedup[key] = rec
        return list(dedup.values())

    def _load_behavioral_events(self, since: datetime) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        for kind, relatives in BEHAVIORAL_SOURCES.items():
            for relative in relatives:
                path = self.root / relative
                raw_records = self._read_jsonl(path) if path.suffix == '.jsonl' else self._read_json_file(path)
                for raw in raw_records:
                    if not isinstance(raw, dict):
                        raw = {'value': raw}
                    if not self._within_window(raw, since):
                        continue
                    event = dict(raw)
                    event['behavioral_kind'] = kind
                    event['_source_file'] = event.get('_source_file') or relative
                    event['event_timestamp'] = (self._time_from_record(event) or datetime.now(timezone.utc)).isoformat().replace('+00:00', 'Z')
                    event['event_text'] = _json_text(event)
                    events.append(event)
        return events

    def _synthetic_integrations(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        records = inputs.get('integrated_records') or inputs.get('integrations') or []
        out: List[Dict[str, Any]] = []
        for raw in records:
            if not isinstance(raw, dict):
                raw = {'text': str(raw)}
            rec = dict(raw)
            text = rec.get('text') or rec.get('candidate_text') or _json_text(rec)
            rec['text'] = _norm(text)
            rec['trace_keywords'] = _keywords(text)
            rec['trace_key'] = str(rec.get('integration_id') or rec.get('knowledge_id') or _hash(text))
            rec['trace_timestamp'] = rec.get('timestamp_utc') or _utc()
            out.append(rec)
        return out

    def _synthetic_events(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        records = inputs.get('behavioral_events') or inputs.get('events') or []
        out: List[Dict[str, Any]] = []
        for raw in records:
            if not isinstance(raw, dict):
                raw = {'value': raw}
            ev = dict(raw)
            ev['behavioral_kind'] = str(ev.get('behavioral_kind') or ev.get('kind') or 'runtime')
            ev['event_timestamp'] = ev.get('timestamp_utc') or ev.get('timestamp') or _utc()
            ev['event_text'] = _json_text(ev)
            out.append(ev)
        return out

    def _match_strength(self, integration: Dict[str, Any], event: Dict[str, Any]) -> Tuple[float, List[str]]:
        event_text = _norm(event.get('event_text') or event)
        event_lower = event_text.lower()
        query_id = integration.get('source_query_id') or integration.get('query_id')
        matched: List[str] = []
        score = 0.0
        if query_id and str(query_id).lower() in event_lower:
            score += 0.55
            matched.append(f'query_id:{query_id}')
        keywords = list(integration.get('trace_keywords') or [])
        keyword_hits = [kw for kw in keywords if kw and kw.lower() in event_lower]
        if keywords:
            ratio = len(keyword_hits) / max(1, min(len(keywords), 10))
            score += min(0.40, ratio * 0.40)
            matched.extend(keyword_hits[:10])
        integration_text = _norm(integration.get('text'))
        if integration_text and len(integration_text) > 40 and integration_text[:80].lower() in event_lower:
            score += 0.35
            matched.append('text_prefix')
        return _bounded(score), matched

    def _build_traces(self, integrations: List[Dict[str, Any]], events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        traces: List[Dict[str, Any]] = []
        for integ in integrations:
            integ_time = _parse_time(integ.get('trace_timestamp') or integ.get('timestamp_utc'))
            for event in events:
                ev_time = _parse_time(event.get('event_timestamp') or event.get('timestamp_utc'))
                if integ_time and ev_time and ev_time < integ_time:
                    continue
                strength, matched = self._match_strength(integ, event)
                if strength < 0.12:
                    continue
                traces.append({
                    'trace_id': 'EIT-' + _hash(f"{integ.get('trace_key')}|{event.get('behavioral_kind')}|{event.get('_source_file')}|{event.get('event_timestamp')}"),
                    'integration_key': integ.get('trace_key'),
                    'knowledge_id': integ.get('knowledge_id'),
                    'source_query_id': integ.get('source_query_id') or integ.get('query_id'),
                    'provider': integ.get('provider', 'unknown'),
                    'behavioral_kind': event.get('behavioral_kind'),
                    'behavioral_source_file': event.get('_source_file'),
                    'integration_timestamp': integ.get('trace_timestamp') or integ.get('timestamp_utc'),
                    'behavioral_timestamp': event.get('event_timestamp'),
                    'influence_strength': strength,
                    'matched_markers': matched,
                    'reversible': True,
                    'causal_status': 'correlational_trace',
                    'interpretation': 'external knowledge appears in a later behavioral trace; causal proof requires controlled comparison',
                })
        traces.sort(key=lambda x: (str(x.get('behavioral_timestamp')), -float(x.get('influence_strength', 0.0))))
        return traces

    def step(self, inputs: Optional[Dict[str, Any]] = None, window_hours: int = 24, persist: bool = True, min_strength: float = 0.12) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        now = datetime.now(timezone.utc)
        since = now - timedelta(hours=max(1, int(window_hours)))
        integrations = self._synthetic_integrations(inputs) if inputs.get('integrated_records') or inputs.get('integrations') else self._load_integrations(since)
        events = self._synthetic_events(inputs) if inputs.get('behavioral_events') or inputs.get('events') else self._load_behavioral_events(since)
        traces = [t for t in self._build_traces(integrations, events) if float(t.get('influence_strength', 0.0)) >= min_strength]

        by_kind: Dict[str, int] = {}
        for trace in traces:
            kind = str(trace.get('behavioral_kind') or 'unknown')
            by_kind[kind] = by_kind.get(kind, 0) + 1

        influence_count = len(traces)
        integration_count = len(integrations)
        event_count = len(events)
        influenced_keys = {str(t.get('integration_key')) for t in traces if t.get('integration_key')}
        influenced_rate = len(influenced_keys) / max(1, integration_count)
        traceability_score = _bounded(0.35 * (integration_count > 0) + 0.25 * (event_count > 0) + 0.40 * influenced_rate)
        mean_strength = sum(_safe_float(t.get('influence_strength')) for t in traces) / max(1, influence_count)
        reversibility_score = 1.0 if all(t.get('reversible') for t in traces) else 0.0

        output = {
            'primitive': PRIMITIVE,
            'timestamp_utc': _utc(),
            'success': True,
            'window_hours': max(1, int(window_hours)),
            'external_integrated_knowledge_count': integration_count,
            'behavioral_event_count': event_count,
            'external_knowledge_influence_count': influence_count,
            'influenced_integration_count': len(influenced_keys),
            'influenced_integration_rate': influenced_rate,
            'external_influence_traceability_score': traceability_score,
            'external_influence_mean_strength': mean_strength,
            'external_influence_reversibility_score': reversibility_score,
            'external_priority_influence_count': by_kind.get('priority', 0),
            'external_strategy_influence_count': by_kind.get('strategy', 0),
            'external_decision_influence_count': by_kind.get('decision', 0),
            'external_action_influence_count': by_kind.get('action', 0),
            'external_runtime_influence_count': by_kind.get('runtime', 0),
            'external_revision_influence_count': by_kind.get('revision', 0),
            'influence_counts_by_kind': by_kind,
            'latest_traces': traces[-50:],
            'metrics': {
                'external_integrated_knowledge_count': integration_count,
                'behavioral_event_count': event_count,
                'external_knowledge_influence_count': influence_count,
                'influenced_integration_rate': influenced_rate,
                'external_influence_traceability_score': traceability_score,
                'external_influence_mean_strength': mean_strength,
                'external_influence_reversibility_score': reversibility_score,
                'external_priority_influence_count': by_kind.get('priority', 0),
                'external_strategy_influence_count': by_kind.get('strategy', 0),
                'external_decision_influence_count': by_kind.get('decision', 0),
                'external_action_influence_count': by_kind.get('action', 0),
                'external_runtime_influence_count': by_kind.get('runtime', 0),
                'external_revision_influence_count': by_kind.get('revision', 0),
            },
            'diagnostics': {
                'schema_version': 'EITE.v1',
                'causal_scope': 'correlational_traceability_not_direct_causation',
                'history_path': str(self.history_path),
                'latest_report_path': str(self.latest_report_path),
                'behavioral_sources': BEHAVIORAL_SOURCES,
                'integration_sources': INTEGRATION_SOURCES,
                'minimum_strength': min_strength,
                'non_closure_compliant': True,
                'observational_only': True,
                'no_code_modification_authorized': True,
            },
        }
        if persist:
            self._persist(output)
        return output

    def _persist(self, output: Dict[str, Any]) -> None:
        try:
            with self.history_path.open('a', encoding='utf-8') as fh:
                fh.write(json.dumps(output, ensure_ascii=False, sort_keys=True) + '\n')
            self.latest_report_path.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
        except Exception:
            pass


if __name__ == '__main__':
    demo = ExternalInfluenceTraceabilityEngine().step(persist=False)
    print(json.dumps(demo, ensure_ascii=False, indent=2, sort_keys=True))
