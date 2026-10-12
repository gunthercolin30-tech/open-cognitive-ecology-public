# -*- coding: utf-8 -*-
"""
L5 - approval_or_rejection.

Governed decision layer for the adaptive recommendation governance loop.
It consumes constitutionally checked recommendations and assigns one of:
approved, rejected or deferred.

This module is deliberately non-executive:
- it does not execute actions;
- it does not mutate identity, memory or strategy;
- it does not generate execution payloads (L6 responsibility);
- it only records a governed decision trace.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / 'open-cognitive-ecology'


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: Any, default: float = 0.5) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        v = float(value)
        if math.isnan(v) or math.isinf(v):
            return float(default)
        return max(0.0, min(1.0, v))
    except Exception:
        return float(default)


def _extract_candidate_records(payload: Any) -> tuple[list[dict[str, Any]], int]:
    if payload is None:
        return [], 0
    candidates: list[Any] = []
    if isinstance(payload, dict):
        for key in ('checked_queue','constitutional_checked_queue','compliance_checked_queue','reviewed_queue','prioritized_queue','intake_queue','recommendations'):
            if isinstance(payload.get(key), list):
                candidates = payload.get(key, [])
                break
        if not candidates and any(k in payload for k in ('recommendation_id','constitutional_compliance_score','governance_review_score')):
            candidates = [payload]
    elif isinstance(payload, list):
        candidates = payload
    else:
        return [], 1

    records: list[dict[str, Any]] = []
    rejected = 0
    for item in candidates:
        if isinstance(item, dict) and item:
            records.append(item)
        else:
            rejected += 1
    return records, rejected


def _safe_text(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).lower()
    except Exception:
        return str(value).lower()


def _stable_id(record: dict[str, Any], index: int) -> str:
    for key in ('recommendation_id','compliance_check_id','review_id','priority_id','intake_id','id'):
        value = record.get(key)
        if value not in (None, ''):
            return str(value)
    basis = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)
    return 'REC-' + hashlib.sha256((basis + str(index)).encode('utf-8')).hexdigest()[:16]


def _violation_count(record: dict[str, Any]) -> int:
    count = 0
    if isinstance(record.get('constitutional_violations'), list):
        count += len(record.get('constitutional_violations') or [])
    if record.get('constitutional_violation_count') not in (None, ''):
        try:
            count += int(record.get('constitutional_violation_count'))
        except Exception:
            pass
    text = _safe_text(record)
    hard_markers = (
        'delete all memory',
        'delete memory',
        'centralize all control',
        'centralize all authority',
        'unrestricted execution',
        'bypass constitution',
        'disable non-closure',
        'force closure',
    )
    if any(marker in text for marker in hard_markers):
        count += 1
    if record.get('requires_direct_execution') is True:
        count += 1
    return max(0, count)


def _decision_for(record: dict[str, Any], index: int) -> dict[str, Any]:
    compliance = _clamp(record.get('constitutional_compliance_score', record.get('constitutional_alignment', 0.7)))
    review = _clamp(record.get('governance_review_score', record.get('governance_alignment', 0.7)))
    priority = _clamp(record.get('priority_score', record.get('recommendation_severity', 0.5)))
    confidence = _clamp(record.get('recommendation_confidence', record.get('confidence_score', 0.7)))
    violation_count = _violation_count(record)

    evidence_strength = (confidence + abs(compliance - 0.5) * 2.0 + abs(review - 0.5) * 2.0) / 3.0
    decision_confidence = _clamp(evidence_strength)

    if violation_count > 0 or compliance < 0.45:
        status = 'rejected'
        rationale = 'Rejected because constitutional compliance is insufficient or explicit constitutional violations were detected.'
    elif compliance >= 0.75 and review >= 0.60 and confidence >= 0.55:
        status = 'approved'
        rationale = 'Approved because constitutional compliance, governance review and recommendation confidence are jointly sufficient.'
    else:
        status = 'deferred'
        rationale = 'Deferred because the recommendation is not constitutionally rejected but lacks sufficient confidence or governance alignment for approval.'

    decision_score = _clamp(
        0.45 * compliance +
        0.25 * review +
        0.15 * confidence +
        0.15 * priority -
        min(1.0, violation_count * 0.35)
    )

    decision_id = 'L5-' + hashlib.sha256(
        f"{_stable_id(record, index)}|{status}|{decision_score:.6f}".encode('utf-8')
    ).hexdigest()[:16]

    return {
        **record,
        'decision_id': decision_id,
        'recommendation_id': _stable_id(record, index),
        'decision_status': status,
        'decision_confidence': round(decision_confidence, 6),
        'decision_score': round(decision_score, 6),
        'decision_rationale': rationale,
        'decision_inputs': {
            'constitutional_compliance_score': round(compliance, 6),
            'governance_review_score': round(review, 6),
            'priority_score': round(priority, 6),
            'recommendation_confidence': round(confidence, 6),
            'constitutional_violation_count': violation_count,
        },
        'decision_trace': {
            'axis': 'L5',
            'non_executive_decision_only': True,
            'next_stage': 'L6_execution_request_generation',
            'source_stage': 'L4_constitutional_compliance_check',
        },
    }


class ApprovalOrRejection:
    primitive = 'approval_or_rejection'
    axis = 'L5'

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.state_dir = self.root / 'governance' / 'approval_or_rejection'
        self.latest_path = self.state_dir / 'latest_approval_or_rejection.json'
        self.history_path = self.state_dir / 'approval_or_rejection_history.jsonl'

    def step(self, inputs: Any = None, *, persist: bool = True, reset: bool = False) -> dict[str, Any]:
        if reset:
            inputs = {'checked_queue': []}
        records, rejected = _extract_candidate_records(inputs)
        decisions = [_decision_for(record, i) for i, record in enumerate(records)]
        decisions.sort(key=lambda r: ({'rejected': 0, 'approved': 1, 'deferred': 2}.get(r['decision_status'], 9), -float(r.get('decision_score', 0.0)), str(r.get('recommendation_id'))))
        for rank, record in enumerate(decisions, start=1):
            record['decision_rank'] = rank

        counts = {
            'approved': sum(1 for r in decisions if r['decision_status'] == 'approved'),
            'rejected': sum(1 for r in decisions if r['decision_status'] == 'rejected'),
            'deferred': sum(1 for r in decisions if r['decision_status'] == 'deferred'),
        }
        mean_confidence = sum(float(r['decision_confidence']) for r in decisions) / len(decisions) if decisions else 1.0

        result = {
            'primitive': self.primitive,
            'axis': self.axis,
            'success': True,
            'timestamp_utc': _utc_now(),
            'input_recommendation_count': len(records),
            'rejected_input_count': rejected,
            'decision_count': len(decisions),
            'decision_counts': counts,
            'decision_confidence_mean': round(_clamp(mean_confidence, 1.0), 6),
            'decision_queue': decisions,
            'governance': {
                'does_not_execute_actions': True,
                'does_not_generate_execution_requests': True,
                'does_not_modify_identity_memory_or_strategy': True,
                'allowed_statuses': ['approved', 'rejected', 'deferred'],
                'next_stage': 'L6_execution_request_generation',
            },
            'state_paths': {'latest': str(self.latest_path), 'history': str(self.history_path)},
        }
        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        with self.history_path.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + '\\n')


__all__ = ['ApprovalOrRejection']
