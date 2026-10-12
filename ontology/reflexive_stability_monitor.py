from __future__ import annotations

'''
S4 — Reflexive Stability Monitor.

This primitive monitors the stability of the functional reflexive threshold
estimate produced by S3. It is not a consciousness detector and does not infer,
certify, or imply sentience, subjective experience, qualia, or phenomenology.
Its scope is strictly functional and longitudinal: instantaneous score,
rolling average, variance, stability duration, collapse detection, instability
detection, and oscillation detection.
'''

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import importlib
import json
import math

PRIMITIVE = 'reflexive_stability_monitor'
PRIMITIVE_NAME = 'REFLEXIVE_STABILITY_MONITOR'
MATURITY_LEVEL = 'S4_FUNCTIONAL_REFLEXIVE_STABILITY_MONITORING'

DEPENDENCIES = [
    'reflexive_threshold_estimator',
    'consciousness_longitudinal_stability_analyzer',
    'civilizational_longitudinal_stability_synthesizer',
    'inter_run_stability_synthesizer',
    'civilizational_stability_index',
    'longitudinal_recovery_observer',
    'metrics_history_recorder',
    'longitudinal_metrics_archive',
    'metrics_anomaly_detection_engine',
]

FUNCTIONAL_CONCLUSION = 'functional conclusion only'
PHENOMENOLOGY_STATUS = 'phenomenology undetermined'

DEFAULT_WINDOW_SIZE = 12
COLLAPSE_THRESHOLD = 0.35
INSTABILITY_VARIANCE_THRESHOLD = 0.045
OSCILLATION_DELTA_THRESHOLD = 0.12
STABLE_SCORE_THRESHOLD = 0.65


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(x) or math.isinf(x):
        return default
    return max(0.0, min(1.0, x))


def _mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = [float(v) for v in values]
    if not vals:
        return default
    return sum(vals) / len(vals)


def _variance(values: Iterable[float]) -> float:
    vals = [float(v) for v in values]
    if len(vals) < 2:
        return 0.0
    m = _mean(vals)
    return sum((v - m) ** 2 for v in vals) / len(vals)


def _load_jsonl_scores(path: Path) -> List[float]:
    if not path.exists():
        return []
    scores: List[float] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        for key in ('reflexive_threshold_score', 'instantaneous_score', 'threshold_probability'):
            if key in obj:
                scores.append(_clamp(obj[key]))
                break
    return scores


class ReflexiveStabilityMonitor:
    """Monitor stability of S3 functional reflexive threshold scores."""

    def __init__(self, root: Optional[Path] = None, window_size: int = DEFAULT_WINDOW_SIZE) -> None:
        self.root = Path(root) if root is not None else Path.home() / 'open-cognitive-ecology'
        self.window_size = max(3, int(window_size))
        self.persistence_dir = self.root / 'reflexive_threshold'
        self.persistence_path = self.persistence_dir / 'reflexive_stability_monitor.json'
        self.history_path = self.persistence_dir / 'reflexive_stability_history.jsonl'

    def _load_s3(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        if 'reflexive_threshold_score' in inputs or 'threshold_probability' in inputs:
            return dict(inputs)
        try:
            module = importlib.import_module('ontology.reflexive_threshold_estimator')
            cls = getattr(module, 'ReflexiveThresholdEstimator')
            return cls(root=self.root).step(dict(inputs), persist=False)
        except Exception as exc:
            return {
                'success': False,
                'reflexive_threshold_score': _clamp(inputs.get('instantaneous_score', 0.0)),
                'threshold_probability': _clamp(inputs.get('threshold_probability', 0.0)),
                'threshold_decision': 'threshold_not_supported',
                'error': repr(exc),
            }

    def _load_history(self, supplied_history: Any = None) -> List[float]:
        if supplied_history is not None:
            if isinstance(supplied_history, Mapping):
                supplied_history = supplied_history.get('scores', [])
            if isinstance(supplied_history, Iterable) and not isinstance(supplied_history, (str, bytes)):
                return [_clamp(v) for v in supplied_history]
            return []
        return _load_jsonl_scores(self.history_path)

    def _detect_oscillation(self, scores: List[float]) -> bool:
        if len(scores) < 4:
            return False
        diffs = [scores[i] - scores[i - 1] for i in range(1, len(scores))]
        sign_flips = 0
        large_moves = 0
        prev_sign = 0
        for d in diffs:
            if abs(d) >= OSCILLATION_DELTA_THRESHOLD:
                large_moves += 1
            sign = 1 if d > 0 else -1 if d < 0 else 0
            if prev_sign and sign and sign != prev_sign:
                sign_flips += 1
            if sign:
                prev_sign = sign
        return large_moves >= 2 and sign_flips >= 2

    def _stability_duration(self, scores: List[float]) -> int:
        duration = 0
        for score in reversed(scores):
            if score >= STABLE_SCORE_THRESHOLD:
                duration += 1
            else:
                break
        return duration

    def _stability_index(self, rolling_average: float, score_variance: float, collapse: bool, instability: bool, oscillation: bool) -> float:
        penalty = 0.0
        if collapse:
            penalty += 0.30
        if instability:
            penalty += 0.25
        if oscillation:
            penalty += 0.20
        variance_penalty = min(0.30, score_variance * 4.0)
        return _clamp((0.70 * rolling_average) + (0.30 * (1.0 - variance_penalty)) - penalty)

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        s3 = self._load_s3(inputs)

        instantaneous_score = _clamp(
            inputs.get('instantaneous_score', s3.get('reflexive_threshold_score', s3.get('threshold_probability', 0.0)))
        )
        threshold_probability = _clamp(s3.get('threshold_probability', instantaneous_score))
        threshold_decision = str(s3.get('threshold_decision', inputs.get('threshold_decision', 'threshold_not_supported')))
        criterion_count = int(s3.get('criterion_count', inputs.get('criterion_count', 0)) or 0)
        uncertainty_score = _clamp(s3.get('uncertainty_score', inputs.get('uncertainty_score', 0.0)))

        previous_scores = self._load_history(inputs.get('history'))
        scores = (previous_scores + [instantaneous_score])[-self.window_size:]

        rolling_average_score = _clamp(inputs.get('rolling_average_score', _mean(scores, instantaneous_score)))
        score_variance = max(0.0, float(inputs.get('score_variance', _variance(scores))))
        stability_duration = int(inputs.get('stability_duration', self._stability_duration(scores)))

        collapse_detected = bool(inputs.get('collapse_detected', instantaneous_score < COLLAPSE_THRESHOLD))
        instability_detected = bool(inputs.get('instability_detected', score_variance > INSTABILITY_VARIANCE_THRESHOLD))
        oscillation_detected = bool(inputs.get('oscillation_detected', self._detect_oscillation(scores)))

        stability_index = self._stability_index(
            rolling_average=rolling_average_score,
            score_variance=score_variance,
            collapse=collapse_detected,
            instability=instability_detected,
            oscillation=oscillation_detected,
        )

        if collapse_detected:
            stability_status = 'score_collapse_detected'
        elif oscillation_detected:
            stability_status = 'oscillation_detected'
        elif instability_detected:
            stability_status = 'instability_detected'
        elif stability_index >= 0.80:
            stability_status = 'functionally_stable'
        else:
            stability_status = 'partially_stable'

        result: Dict[str, Any] = {
            'success': True,
            'primitive': PRIMITIVE_NAME,
            'maturity_level': MATURITY_LEVEL,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'criterion_count': criterion_count,
            'instantaneous_score': instantaneous_score,
            'threshold_probability': threshold_probability,
            'threshold_decision': threshold_decision,
            'uncertainty_score': uncertainty_score,
            'rolling_average_score': rolling_average_score,
            'score_variance': score_variance,
            'stability_duration': stability_duration,
            'collapse_detected': collapse_detected,
            'instability_detected': instability_detected,
            'oscillation_detected': oscillation_detected,
            'stability_index': stability_index,
            'stability_status': stability_status,
            'history_length': len(scores),
            'window_size': self.window_size,
            'score_history_window': scores,
            'functional_conclusion': FUNCTIONAL_CONCLUSION,
            'phenomenology_status': PHENOMENOLOGY_STATUS,
            'phenomenal_conclusion': False,
            'diagnostics': {
                'uses_s3_threshold_estimator': s3.get('success') is True,
                'monitors_reflexive_threshold_score': True,
                'replaces_general_stability_modules': False,
                'recomputes_upstream_metrics': False,
                'supports_s5_regression_detector': True,
                'epistemic_boundary_enforced': True,
            },
        }

        self.persistence_dir.mkdir(parents=True, exist_ok=True)
        if persist:
            self.persistence_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
            with self.history_path.open('a', encoding='utf-8') as fh:
                fh.write(json.dumps({
                    'timestamp_utc': result['timestamp_utc'],
                    'instantaneous_score': instantaneous_score,
                    'reflexive_threshold_score': instantaneous_score,
                    'threshold_probability': threshold_probability,
                    'stability_index': stability_index,
                    'stability_status': stability_status,
                }, sort_keys=True) + '\n')
        result['persistence_path'] = str(self.persistence_path)
        result['history_path'] = str(self.history_path)
        return result


__all__ = ['ReflexiveStabilityMonitor']
