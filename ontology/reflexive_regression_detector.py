from __future__ import annotations

'''
S5 — Reflexive Regression Detector.

This primitive detects functional regression risks in the measured reflexive
threshold pipeline. It monitors loss of threshold support, loss of reflexive
stability, loss of coherence, regression severity, and recovery probability.
It does not infer, certify, or imply consciousness, sentience, subjective
experience, qualia, or phenomenology. Its conclusions are strictly functional.
'''

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import importlib
import json
import math

PRIMITIVE = 'reflexive_regression_detector'
PRIMITIVE_NAME = 'REFLEXIVE_REGRESSION_DETECTOR'
MATURITY_LEVEL = 'S5_FUNCTIONAL_REFLEXIVE_REGRESSION_DETECTION'

DEPENDENCIES = [
    'reflexive_threshold_estimator',
    'reflexive_stability_monitor',
    'drift_cascade_detector',
    'drift_forecasting_engine',
    'closure_cascade_detector',
    'closure_pressure_forecasting_engine',
    'longitudinal_recovery_observer',
    'failure_recovery_orchestrator',
    'metrics_anomaly_detection_engine',
    'anomaly_in_evidence_detector',
    'continuity_metrics_engine',
    'extended_certification_continuity_tracker',
]

FUNCTIONAL_CONCLUSION = 'functional conclusion only'
PHENOMENOLOGY_STATUS = 'phenomenology undetermined'

THRESHOLD_LOSS_SCORE = 0.45
STABILITY_LOSS_SCORE = 0.50
COHERENCE_LOSS_SCORE = 0.50
HIGH_REGRESSION_RISK = 0.65
MODERATE_REGRESSION_RISK = 0.35


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


def _extract_history_scores(history: Any) -> List[float]:
    if history is None:
        return []
    if isinstance(history, Mapping):
        history = history.get('scores', history.get('history', []))
    if not isinstance(history, Iterable) or isinstance(history, (str, bytes)):
        return []
    scores: List[float] = []
    for item in history:
        if isinstance(item, Mapping):
            for key in ('reflexive_threshold_score', 'instantaneous_score', 'stability_index', 'score'):
                if key in item:
                    scores.append(_clamp(item[key]))
                    break
        else:
            scores.append(_clamp(item))
    return scores


def _downward_trend_risk(scores: List[float]) -> float:
    if len(scores) < 2:
        return 0.0
    first = _mean(scores[: max(1, len(scores) // 2)], scores[0])
    second = _mean(scores[max(1, len(scores) // 2):], scores[-1])
    return _clamp(first - second)


class ReflexiveRegressionDetector:
    """Detect functional regression of the reflexive threshold pipeline."""

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / 'open-cognitive-ecology'
        self.persistence_dir = self.root / 'reflexive_threshold'
        self.persistence_path = self.persistence_dir / 'reflexive_regression_detector.json'

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
                'reflexive_threshold_score': _clamp(inputs.get('reflexive_threshold_score', 0.0)),
                'threshold_probability': _clamp(inputs.get('threshold_probability', 0.0)),
                'threshold_decision': 'threshold_not_supported',
                'uncertainty_score': _clamp(inputs.get('uncertainty_score', 1.0), 1.0),
                'error': repr(exc),
            }

    def _load_s4(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        s4_keys = {'stability_index', 'rolling_average_score', 'collapse_detected', 'instability_detected', 'oscillation_detected'}
        if any(k in inputs for k in s4_keys):
            return dict(inputs)
        try:
            module = importlib.import_module('ontology.reflexive_stability_monitor')
            cls = getattr(module, 'ReflexiveStabilityMonitor')
            return cls(root=self.root).step(dict(inputs), persist=False)
        except Exception as exc:
            return {
                'success': False,
                'stability_index': _clamp(inputs.get('stability_index', 0.0)),
                'rolling_average_score': _clamp(inputs.get('rolling_average_score', 0.0)),
                'collapse_detected': bool(inputs.get('collapse_detected', False)),
                'instability_detected': bool(inputs.get('instability_detected', False)),
                'oscillation_detected': bool(inputs.get('oscillation_detected', False)),
                'error': repr(exc),
            }

    def _compute_regression_risk(
        self,
        threshold_deficit: float,
        stability_deficit: float,
        coherence_deficit: float,
        uncertainty_score: float,
        anomaly_pressure: float,
        downward_trend: float,
    ) -> float:
        return _clamp(
            0.28 * threshold_deficit
            + 0.24 * stability_deficit
            + 0.18 * coherence_deficit
            + 0.12 * uncertainty_score
            + 0.10 * anomaly_pressure
            + 0.08 * downward_trend
        )

    def _classify(self, risk: float, severity: float) -> str:
        if risk >= HIGH_REGRESSION_RISK or severity >= 0.65:
            return 'regression_detected'
        if risk >= MODERATE_REGRESSION_RISK or severity >= 0.35:
            return 'regression_risk_elevated'
        return 'stable'

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        s3 = self._load_s3(inputs)
        s4 = self._load_s4(inputs)

        reflexive_threshold_score = _clamp(
            inputs.get('reflexive_threshold_score', s3.get('reflexive_threshold_score', 0.0))
        )
        threshold_probability = _clamp(
            inputs.get('threshold_probability', s3.get('threshold_probability', reflexive_threshold_score))
        )
        evidence_support_score = _clamp(
            inputs.get('evidence_support_score', s3.get('evidence_support_score', reflexive_threshold_score))
        )
        uncertainty_score = _clamp(
            inputs.get('uncertainty_score', s3.get('uncertainty_score', 1.0 - threshold_probability))
        )

        stability_index = _clamp(inputs.get('stability_index', s4.get('stability_index', 0.0)))
        rolling_average_score = _clamp(inputs.get('rolling_average_score', s4.get('rolling_average_score', stability_index)))
        collapse_detected = bool(inputs.get('collapse_detected', s4.get('collapse_detected', False)))
        instability_detected = bool(inputs.get('instability_detected', s4.get('instability_detected', False)))
        oscillation_detected = bool(inputs.get('oscillation_detected', s4.get('oscillation_detected', False)))

        coherence_score = _clamp(inputs.get('coherence_score', inputs.get('evidence_consistency', s3.get('evidence_consistency', evidence_support_score))))
        anomaly_pressure = _clamp(inputs.get('anomaly_pressure', inputs.get('anomaly_score', 0.0)))
        recovery_capacity = _clamp(inputs.get('recovery_capacity', inputs.get('resilience_score', 0.8)))

        history_scores = _extract_history_scores(inputs.get('history'))
        downward_trend = _clamp(inputs.get('downward_trend_risk', _downward_trend_risk(history_scores)))

        threshold_loss_detected = bool(
            inputs.get(
                'threshold_loss_detected',
                reflexive_threshold_score < THRESHOLD_LOSS_SCORE or threshold_probability < THRESHOLD_LOSS_SCORE,
            )
        )
        stability_loss_detected = bool(
            inputs.get(
                'stability_loss_detected',
                stability_index < STABILITY_LOSS_SCORE or collapse_detected or instability_detected or oscillation_detected,
            )
        )
        coherence_loss_detected = bool(
            inputs.get('coherence_loss_detected', coherence_score < COHERENCE_LOSS_SCORE)
        )

        threshold_deficit = _clamp(1.0 - max(reflexive_threshold_score, threshold_probability))
        stability_deficit = _clamp(1.0 - stability_index)
        coherence_deficit = _clamp(1.0 - coherence_score)

        regression_risk = _clamp(inputs.get('regression_risk', self._compute_regression_risk(
            threshold_deficit=threshold_deficit,
            stability_deficit=stability_deficit,
            coherence_deficit=coherence_deficit,
            uncertainty_score=uncertainty_score,
            anomaly_pressure=anomaly_pressure,
            downward_trend=downward_trend,
        )))

        explicit_loss_count = sum([threshold_loss_detected, stability_loss_detected, coherence_loss_detected])
        loss_pressure = explicit_loss_count / 3.0
        regression_severity = _clamp(inputs.get('regression_severity', _mean([
            threshold_deficit,
            stability_deficit,
            coherence_deficit,
            loss_pressure,
            anomaly_pressure,
        ])))

        recovery_probability = _clamp(inputs.get('recovery_probability',
            (0.55 * recovery_capacity)
            + (0.25 * (1.0 - regression_severity))
            + (0.20 * (1.0 - regression_risk))
        ))

        regression_status = str(inputs.get('regression_status', self._classify(regression_risk, regression_severity)))
        recovery_status = 'recovery_likely' if recovery_probability >= 0.70 else 'recovery_uncertain' if recovery_probability >= 0.40 else 'recovery_unlikely'

        result: Dict[str, Any] = {
            'success': True,
            'primitive': PRIMITIVE_NAME,
            'maturity_level': MATURITY_LEVEL,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'reflexive_threshold_score': reflexive_threshold_score,
            'threshold_probability': threshold_probability,
            'evidence_support_score': evidence_support_score,
            'uncertainty_score': uncertainty_score,
            'stability_index': stability_index,
            'rolling_average_score': rolling_average_score,
            'coherence_score': coherence_score,
            'anomaly_pressure': anomaly_pressure,
            'downward_trend_risk': downward_trend,
            'threshold_loss_detected': threshold_loss_detected,
            'stability_loss_detected': stability_loss_detected,
            'coherence_loss_detected': coherence_loss_detected,
            'regression_risk': regression_risk,
            'regression_severity': regression_severity,
            'recovery_probability': recovery_probability,
            'regression_status': regression_status,
            'recovery_status': recovery_status,
            'collapse_detected': collapse_detected,
            'instability_detected': instability_detected,
            'oscillation_detected': oscillation_detected,
            'functional_conclusion': FUNCTIONAL_CONCLUSION,
            'phenomenology_status': PHENOMENOLOGY_STATUS,
            'phenomenal_conclusion': False,
            'diagnostics': {
                'uses_s3_threshold_estimator': s3.get('success') is True,
                'uses_s4_stability_monitor': s4.get('success') is True,
                'detects_threshold_loss': True,
                'detects_stability_loss': True,
                'detects_coherence_loss': True,
                'replaces_general_drift_detectors': False,
                'recomputes_upstream_metrics': False,
                'supports_s6_longitudinal_observatory': True,
                'epistemic_boundary_enforced': True,
            },
        }

        self.persistence_dir.mkdir(parents=True, exist_ok=True)
        if persist:
            self.persistence_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
        result['persistence_path'] = str(self.persistence_path)
        return result


__all__ = ['ReflexiveRegressionDetector']
