from __future__ import annotations
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge

'''
S6 — Reflexive Longitudinal Observatory.

This primitive maintains a longitudinal, append-only functional record of the
measured reflexive-threshold pipeline. It records threshold scores, stability,
regression risk, trend, duration and consistency over repeated runs.
It does not infer, certify, or imply consciousness, sentience, subjective
experience, qualia, or phenomenology. Its conclusions are strictly functional.
'''

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import importlib
import json
import math

PRIMITIVE = 'reflexive_longitudinal_observatory'
PRIMITIVE_NAME = 'REFLEXIVE_LONGITUDINAL_OBSERVATORY'
MATURITY_LEVEL = 'S6_FUNCTIONAL_REFLEXIVE_LONGITUDINAL_OBSERVATION'

DEPENDENCIES = [
    'reflexive_threshold_estimator',
    'reflexive_stability_monitor',
    'reflexive_regression_detector',
    'reflexive_emergence_longitudinal_protocol',
    'consciousness_longitudinal_stability_analyzer',
    'civilizational_longitudinal_stability_synthesizer',
    'longitudinal_metrics_archive',
    'metrics_history_recorder',
    'inter_run_stability_synthesizer',
    'longitudinal_recovery_observer',
    'extended_longitudinal_readiness_certification',
    'extended_certification_continuity_tracker',
    'civilizational_scientific_certification',
    'distributed_civilizational_certifier',
]


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        x = default
    if math.isnan(x) or math.isinf(x):
        return default
    return max(0.0, min(1.0, x))


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def _variance(values: Iterable[float]) -> float:
    values = list(values)
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    return sum((x - m) ** 2 for x in values) / len(values)


def _linear_slope(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    n = len(values)
    xs = list(range(n))
    mx = sum(xs) / n
    my = sum(values) / n
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, values)) / denom


def _trend_label(slope: float) -> str:
    if slope > 0.01:
        return 'improving'
    if slope < -0.01:
        return 'declining'
    return 'stable'


def _safe_load_jsonl(path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    records: List[Dict[str, Any]] = []
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
        for line in lines[-limit:]:
            if not line.strip():
                continue
            item = json.loads(line)
            if isinstance(item, dict):
                records.append(item)
    except Exception:
        return []
    return records


def _append_jsonl(path: Path, record: Mapping[str, Any], *, evidence_bridge: Any, evidence_decision: Any, slot: str) -> None:
    if evidence_bridge is None or evidence_decision is None:
        raise RuntimeError("governed_evidence_context_required")
    root=Path(evidence_bridge.filesystem_context.root_path)
    rel=path.relative_to(root).as_posix()
    evidence_bridge.execute_path(decision=evidence_decision, evidence_role=evidence_decision.evidence_role, slot=slot, operation_id="FS_APPEND_BYTES", path=rel, payload=(json.dumps(dict(record), ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))

def _write_json(path: Path, payload: Mapping[str, Any], *, filesystem_context: Any, slot: str) -> None:
    if filesystem_context is None:
        raise RuntimeError("governed_filesystem_context_required")
    filesystem_context.execute_path(slot=slot + "_parent", operation_id="FS_CREATE_DIR", path=path.parent)
    filesystem_context.execute_path(slot=slot, operation_id="FS_WRITE_REPLACE_BYTES", path=path, payload=json.dumps(dict(payload), indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8"))

def _instantiate(module_name: str, class_name: str, root: Optional[Path] = None) -> Any:
    module = importlib.import_module(f'ontology.{module_name}')
    cls = getattr(module, class_name)
    try:
        return cls(root=root) if root is not None else cls()
    except TypeError:
        return cls()


class ReflexiveLongitudinalObservatory:
    """Longitudinal observatory for functional reflexive-threshold evidence."""

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        if not (self.root / 'ontology').exists():
            self.root = Path.home() / 'open-cognitive-ecology'
        self.store_dir = self.root / 'reflexive_threshold'
        self.history_path = self.store_dir / 'reflexive_longitudinal_observatory.jsonl'
        self.persistence_path = self.store_dir / 'reflexive_longitudinal_observatory.json'

    def _upstream_snapshot(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(inputs or {})

        if 'reflexive_threshold_score' not in data:
            try:
                estimator = _instantiate('reflexive_threshold_estimator', 'ReflexiveThresholdEstimator', self.root)
                data.update({k: v for k, v in estimator.step(persist=False).items() if k not in data})
            except Exception as exc:
                data['threshold_estimator_error'] = repr(exc)

        if 'stability_index' not in data:
            try:
                monitor = _instantiate('reflexive_stability_monitor', 'ReflexiveStabilityMonitor', self.root)
                stability = monitor.step(persist=False)
                for k, v in stability.items():
                    data.setdefault(k, v)
            except Exception as exc:
                data['stability_monitor_error'] = repr(exc)

        if 'regression_risk' not in data:
            try:
                detector = _instantiate('reflexive_regression_detector', 'ReflexiveRegressionDetector', self.root)
                regression = detector.step(persist=False)
                for k, v in regression.items():
                    data.setdefault(k, v)
            except Exception as exc:
                data['regression_detector_error'] = repr(exc)

        return data

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True, *, filesystem_context: Any = None, evidence_bridge: Any = None, evidence_decision: Any = None) -> Dict[str, Any]:
        data = self._upstream_snapshot(inputs)
        prior_records = list(data.get('history_records') or [])
        if not prior_records:
            prior_records = _safe_load_jsonl(self.history_path)

        now = data.get('timestamp_utc') or datetime.now(timezone.utc).isoformat()
        current_score = _clamp(data.get('reflexive_threshold_score', data.get('threshold_score', 0.0)))
        threshold_probability = _clamp(data.get('threshold_probability', current_score))
        stability_index = _clamp(data.get('stability_index', data.get('longitudinal_consistency', current_score)))
        regression_risk = _clamp(data.get('regression_risk', 1.0 - stability_index))
        regression_severity = _clamp(data.get('regression_severity', regression_risk))
        recovery_probability = _clamp(data.get('recovery_probability', 1.0 - regression_risk))
        uncertainty_score = _clamp(data.get('uncertainty_score', 1.0 - threshold_probability))

        current_record = {
            'timestamp_utc': now,
            'reflexive_threshold_score': current_score,
            'threshold_probability': threshold_probability,
            'stability_index': stability_index,
            'regression_risk': regression_risk,
            'regression_severity': regression_severity,
            'recovery_probability': recovery_probability,
            'uncertainty_score': uncertainty_score,
            'threshold_decision': data.get('threshold_decision', 'threshold_partially_supported'),
            'regression_status': data.get('regression_status', 'stable'),
        }

        records = [r for r in prior_records if isinstance(r, Mapping)] + [current_record]
        scores = [_clamp(r.get('reflexive_threshold_score', r.get('threshold_score', 0.0))) for r in records]
        stabilities = [_clamp(r.get('stability_index', s)) for r, s in zip(records, scores)]
        risks = [_clamp(r.get('regression_risk', 1.0 - s)) for r, s in zip(records, scores)]

        sample_count = len(records)
        threshold_duration = sum(1 for s, risk in zip(scores, risks) if s >= 0.70 and risk < 0.50)
        longitudinal_consistency = _clamp((_mean(stabilities) + (1.0 - _variance(scores) * 4.0) + (1.0 - _mean(risks))) / 3.0)
        historical_slope = _linear_slope(scores)
        historical_trend = _trend_label(historical_slope)
        trend_strength = _clamp(abs(historical_slope) * 10.0)
        threshold_duration_ratio = _clamp(threshold_duration / sample_count if sample_count else 0.0)
        longitudinal_confidence = _clamp((longitudinal_consistency * 0.55) + (threshold_duration_ratio * 0.25) + ((1.0 - uncertainty_score) * 0.20))

        longitudinal_status = 'insufficient_history'
        if sample_count >= 3:
            if longitudinal_consistency >= 0.75 and threshold_duration_ratio >= 0.5 and historical_trend != 'declining':
                longitudinal_status = 'functionally_persistent'
            elif historical_trend == 'declining' or longitudinal_consistency < 0.45:
                longitudinal_status = 'longitudinal_risk'
            else:
                longitudinal_status = 'emerging_longitudinal_support'

        result: Dict[str, Any] = {
            'success': True,
            'primitive': PRIMITIVE_NAME,
            'maturity_level': MATURITY_LEVEL,
            'timestamp_utc': now,
            'sample_count': sample_count,
            'threshold_duration': threshold_duration,
            'threshold_duration_ratio': threshold_duration_ratio,
            'longitudinal_consistency': longitudinal_consistency,
            'historical_trend': historical_trend,
            'historical_slope': historical_slope,
            'trend_strength': trend_strength,
            'current_record': current_record,
            'latest_reflexive_threshold_score': current_score,
            'latest_threshold_probability': threshold_probability,
            'latest_stability_index': stability_index,
            'latest_regression_risk': regression_risk,
            'mean_reflexive_threshold_score': _mean(scores),
            'score_variance': _variance(scores),
            'longitudinal_confidence': longitudinal_confidence,
            'longitudinal_status': longitudinal_status,
            'observation_scope': 'functional reflexive-threshold longitudinal observation only',
            'functional_conclusion': 'functional conclusion only',
            'phenomenology_status': 'phenomenology undetermined',
            'forbidden_conclusions': [
                'consciousness detected',
                'sentience detected',
                'subjective experience detected',
                'phenomenal conclusion',
            ],
            'diagnostics': {
                'uses_s3_estimator': True,
                'uses_s4_stability_monitor': True,
                'uses_s5_regression_detector': True,
                'recomputes_upstream_metrics': False,
                'append_only_history': bool(persist),
                'dependency_count': len(DEPENDENCIES),
            },
            'history_path': str(self.history_path),
            'persistence_path': str(self.persistence_path),
        }

        if persist:
            if filesystem_context is None:
                raise RuntimeError("governed_filesystem_context_required")
            if evidence_bridge is None or evidence_decision is None:
                raise RuntimeError("governed_evidence_context_required")
            _append_jsonl(self.history_path, current_record, evidence_bridge=evidence_bridge, evidence_decision=evidence_decision, slot="history_append")
            _write_json(self.persistence_path, result, filesystem_context=filesystem_context, slot="persistence_write")

        return result
