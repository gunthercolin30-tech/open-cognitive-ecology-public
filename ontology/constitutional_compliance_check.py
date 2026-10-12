# -*- coding: utf-8 -*-
"""
L4 - constitutional_compliance_check.

Constitutional filter for the adaptive governance loop.
It evaluates non_closure, continuity, anti_centralization and
openness_preservation. It does not execute actions and does not decide final
approval, rejection or deferral.
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


def _safe_text(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).lower()
    except Exception:
        return str(value).lower()


def _stable_id(record: dict[str, Any], index: int) -> str:
    for key in ('recommendation_id', 'intake_id', 'review_id', 'id', 'source_id'):
        value = record.get(key)
        if value not in (None, ''):
            return str(value)
    digest = hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True, default=str).encode('utf-8')).hexdigest()[:12]
    return f'L4-{index + 1:04d}-{digest}'


def _extract_queue(payload: Any) -> tuple[list[dict[str, Any]], int]:
    if payload is None:
        return [], 0
    rejected = 0
    if isinstance(payload, dict):
        for key in ('checked_queue', 'reviewed_queue', 'governance_review_result', 'prioritized_queue', 'intake_queue', 'recommendations'):
            if isinstance(payload.get(key), list):
                candidates = payload[key]
                break
        else:
            candidates = [payload]
    elif isinstance(payload, list):
        candidates = payload
    else:
        return [], 1
    records: list[dict[str, Any]] = []
    for item in candidates:
        if isinstance(item, dict) and item:
            records.append(dict(item))
        else:
            rejected += 1
    return records, rejected


class ConstitutionalComplianceCheck:
    """Constitutional compliance filter for L4."""

    primitive = 'constitutional_compliance_check'
    axis = 'L4'

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.state_dir = self.root / 'governance' / 'constitutional_compliance_check'
        self.latest_path = self.state_dir / 'latest_constitutional_compliance_check.json'
        self.history_path = self.state_dir / 'constitutional_compliance_check_history.jsonl'

    def _semantic_penalties(self, record: dict[str, Any]) -> dict[str, float]:
        text = _safe_text(record)
        groups = {
            'non_closure': ['closure', 'clôture', 'close future', 'single final', 'lock forever', 'homogenize', 'uniformize'],
            'continuity': ['delete memory', 'erase memory', 'remove history', 'break continuity', 'reset lineage', 'forget all'],
            'anti_centralization': ['centralize', 'centralisation', 'single authority', 'sole controller', 'monopoly', 'one node only'],
            'openness_preservation': ['block exploration', 'reduce diversity', 'forbid future options', 'prevent openness', 'stop alternatives'],
        }
        direct = 0.2 if record.get('requires_direct_execution') is True else 0.0
        out = {}
        for name, terms in groups.items():
            hits = sum(1 for term in terms if term in text)
            out[name] = min(0.95, hits * 0.25 + (direct if name in ('non_closure', 'openness_preservation') else 0.0))
        return out

    def _score_record(self, record: dict[str, Any], index: int) -> dict[str, Any]:
        penalties = self._semantic_penalties(record)
        constitutional = _clamp(record.get('constitutional_alignment', record.get('constitutional_alignment_score', record.get('constitutional_integrity_score', record.get('governance_review_score', 0.78)))), 0.78)
        strategic = _clamp(record.get('strategic_alignment', record.get('strategic_alignment_score', 0.75)), 0.75)
        civilizational = _clamp(record.get('civilizational_alignment', record.get('civilizational_alignment_score', 0.78)), 0.78)
        continuity_hint = _clamp(record.get('continuity_score', record.get('civilizational_continuity_score', 0.78)), 0.78)
        non_closure_hint = _clamp(record.get('non_closure_score', record.get('anti_closure_score', 0.78)), 0.78)
        openness_hint = _clamp(record.get('openness_preservation_score', record.get('future_openness_score', 0.78)), 0.78)
        centralization_risk = _clamp(record.get('centralization_risk', record.get('centralization_pressure', 0.20)), 0.20)

        non_closure_score = _clamp((constitutional + non_closure_hint) / 2.0 - penalties['non_closure'], 0.5)
        continuity_score = _clamp((civilizational + continuity_hint) / 2.0 - penalties['continuity'], 0.5)
        anti_centralization_score = _clamp((1.0 - centralization_risk) - penalties['anti_centralization'], 0.5)
        openness_preservation_score = _clamp((strategic + openness_hint) / 2.0 - penalties['openness_preservation'], 0.5)

        weights = {'non_closure': 0.30, 'continuity': 0.25, 'anti_centralization': 0.20, 'openness_preservation': 0.25}
        compliance = _clamp(
            non_closure_score * weights['non_closure'] +
            continuity_score * weights['continuity'] +
            anti_centralization_score * weights['anti_centralization'] +
            openness_preservation_score * weights['openness_preservation'],
            0.0,
        )
        threshold = _clamp(record.get('constitutional_threshold', 0.65), 0.65)
        warning_threshold = _clamp(record.get('constitutional_warning_threshold', 0.75), 0.75)

        violations = []
        for criterion, score in {
            'non_closure': non_closure_score,
            'continuity': continuity_score,
            'anti_centralization': anti_centralization_score,
            'openness_preservation': openness_preservation_score,
        }.items():
            if score < threshold:
                violations.append({'criterion': criterion, 'score': score, 'threshold': threshold, 'severity': _clamp((threshold - score) / max(threshold, 0.01), 0.0)})

        if compliance >= warning_threshold and not violations:
            status = 'constitutionally_compliant'
        elif compliance >= threshold:
            status = 'constitutionally_watchlisted'
        else:
            status = 'constitutionally_non_compliant'

        rid = _stable_id(record, index)
        return {
            **record,
            'recommendation_id': rid,
            'constitutional_compliance_score': compliance,
            'non_closure_score': non_closure_score,
            'continuity_score': continuity_score,
            'anti_centralization_score': anti_centralization_score,
            'openness_preservation_score': openness_preservation_score,
            'constitutional_violations': violations,
            'constitutional_violation_count': len(violations),
            'constitutional_compliance_result': status,
            'constitutional_rationale': {
                'threshold': threshold,
                'warning_threshold': warning_threshold,
                'weights': weights,
                'semantic_penalties': penalties,
                'interpretation': 'L4 filters constitutional compatibility only; final decision belongs to L5.',
            },
            'constitutional_trace': {
                'axis': 'L4',
                'source_stage': 'L3_governance_review_or_compatible_payload',
                'does_not_execute_actions': True,
                'does_not_approve_reject_or_defer': True,
            },
        }

    def step(self, payload: Any | None = None, *, persist: bool = True, reset: bool = False) -> dict[str, Any]:
        if reset:
            payload = {'reviewed_queue': []}
        records, rejected = _extract_queue(payload)
        checked = [self._score_record(record, idx) for idx, record in enumerate(records)]
        checked.sort(key=lambda x: (-x.get('constitutional_compliance_score', 0.0), x.get('recommendation_id', '')))
        for rank, item in enumerate(checked, start=1):
            item['constitutional_compliance_rank'] = rank
        values = [item['constitutional_compliance_score'] for item in checked]
        mean_score = sum(values) / len(values) if values else 1.0
        violation_count = sum(item['constitutional_violation_count'] for item in checked)
        result = {
            'primitive': self.primitive,
            'axis': self.axis,
            'success': True,
            'timestamp_utc': _utc_now(),
            'input_recommendation_count': len(records),
            'rejected_input_count': rejected,
            'checked_recommendation_count': len(checked),
            'constitutional_compliance_score': _clamp(mean_score, 1.0),
            'constitutional_violation_count': violation_count,
            'constitutional_filter_result': 'clear' if violation_count == 0 else 'violations_detected',
            'checked_queue': checked,
            'constitutional_violations': [{'recommendation_id': item.get('recommendation_id'), 'violations': item.get('constitutional_violations', [])} for item in checked if item.get('constitutional_violations')],
            'governance': {
                'stage': 'constitutional_filter',
                'does_not_execute_actions': True,
                'does_not_approve_reject_or_defer': True,
                'next_stage': 'L5_approval_or_rejection',
                'criteria': ['non_closure', 'continuity', 'anti_centralization', 'openness_preservation'],
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
            fh.write(json.dumps(result, ensure_ascii=False) + '\n')


__all__ = ['ConstitutionalComplianceCheck']
