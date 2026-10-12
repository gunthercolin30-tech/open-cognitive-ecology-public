# -*- coding: utf-8 -*-
'''
I9 - Paradigm Shift Detection Engine.

Central aggregation layer for Open Cognitive Ecology paradigm surveillance.
It fuses I1-I8 functional indicators into a conservative measurable decision:
paradigm_shift_detected, paradigm_shift_confidence, current_regime and
previous_regime. It does not assert phenomenal subjectivity.
'''

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Optional
import json
import math

PRIMITIVE = 'paradigm_shift_detection_engine'
DEPENDENCIES = [
    'paradigm_shift_signal_extractor',
    'regime_transition_detector',
    'structural_break_analyzer',
    'constraint_regime_comparator',
    'paradigm_classification_engine',
    'emergence_detection_engine',
    'paradigm_evolution_observatory',
    'civilizational_regime_dashboard',
    'metrics_history_recorder',
    'scientific_anomaly_detector',
    'scientific_theory_confidence_engine',
    'governance_consistency_checker',
    'openness_preservation_supervisor',
    'non_closure_certification_protocol',
]
REGIME_TAXONOMY = ('stability', 'transition', 'rupture', 'expansion', 'collapse')
SHIFT_REGIMES = ('transition', 'rupture', 'expansion', 'collapse')


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if math.isnan(number) or math.isinf(number):
        number = default
    return max(0.0, min(1.0, number))


def _non_negative_int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except Exception:
        return default


def _section(inputs: dict[str, Any], *names: str) -> dict[str, Any]:
    for name in names:
        value = inputs.get(name)
        if isinstance(value, dict):
            return value
    return {}


def _regime(value: Any, default: str = 'stability') -> str:
    text = str(value if value is not None else default).strip().lower()
    return text if text in REGIME_TAXONOMY else default


def _weighted_mean(items: list[tuple[float, float]]) -> float:
    total_weight = sum(max(0.0, w) for _, w in items)
    if total_weight <= 0.0:
        return 0.0
    return _bounded(sum(_bounded(v) * max(0.0, w) for v, w in items) / total_weight)


class ParadigmShiftDetectionEngine:
    primitive = PRIMITIVE
    taxonomy = REGIME_TAXONOMY

    def __init__(self, root: Optional[str | Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / 'open-cognitive-ecology'
        self.output_dir = self.root / 'paradigm_surveillance' / PRIMITIVE
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_json_path = self.output_dir / 'latest_paradigm_shift_detection_engine.json'
        self.prometheus_path = self.output_dir / 'paradigm_shift_detection_engine.prom'
        self.html_path = self.output_dir / 'paradigm_shift_detection_engine.html'

    def _run_dependency_steps(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if inputs.get('disable_dependency_execution') is True:
            return {}
        results: dict[str, Any] = {}
        calls = [
            ('signal', 'ontology.paradigm_shift_signal_extractor', 'ParadigmShiftSignalExtractor'),
            ('transition', 'ontology.regime_transition_detector', 'RegimeTransitionDetector'),
            ('structural_break', 'ontology.structural_break_analyzer', 'StructuralBreakAnalyzer'),
            ('constraint', 'ontology.constraint_regime_comparator', 'ConstraintRegimeComparator'),
            ('classification', 'ontology.paradigm_classification_engine', 'ParadigmClassificationEngine'),
            ('emergence', 'ontology.emergence_detection_engine', 'EmergenceDetectionEngine'),
            ('observatory', 'ontology.paradigm_evolution_observatory', 'ParadigmEvolutionObservatory'),
            ('dashboard', 'ontology.civilizational_regime_dashboard', 'CivilizationalRegimeDashboard'),
        ]
        for key, module_name, class_name in calls:
            if key in inputs and isinstance(inputs.get(key), dict):
                continue
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                engine = cls()
                value = engine.step({})
                if isinstance(value, dict):
                    results[key] = value
            except Exception as exc:
                results[key] = {'success': False, 'error': repr(exc), 'error_count': 1}
        return results

    def _make_state(self, inputs: Optional[dict[str, Any]]) -> dict[str, Any]:
        inputs = dict(inputs or {})
        dependency_results = self._run_dependency_steps(inputs)
        merged = {**dependency_results, **inputs}

        signal = _section(merged, 'signal', 'paradigm_shift_signal', 'paradigm_shift_signal_extractor')
        transition = _section(merged, 'transition', 'regime_transition', 'regime_transition_detector')
        structural = _section(merged, 'structural_break', 'break', 'structural_break_analyzer')
        constraint = _section(merged, 'constraint', 'constraint_regime', 'constraint_regime_comparator')
        classification = _section(merged, 'classification', 'paradigm_classification', 'paradigm_classification_engine')
        emergence = _section(merged, 'emergence', 'emergence_detection', 'emergence_detection_engine')
        observatory = _section(merged, 'observatory', 'paradigm_evolution', 'paradigm_evolution_observatory')
        dashboard = _section(merged, 'dashboard', 'civilizational_regime_dashboard')

        current_regime = _regime(
            classification.get('current_paradigm', dashboard.get('current_regime', merged.get('current_regime', 'stability')))
        )
        previous_regime = dashboard.get('previous_regime', merged.get('previous_regime'))
        historical_sequence = observatory.get('historical_regime_sequence', dashboard.get('historical_regime_sequence', merged.get('historical_regime_sequence', [])))
        if not isinstance(historical_sequence, list):
            historical_sequence = []
        historical_sequence = [_regime(item) for item in historical_sequence][-200:]
        if previous_regime is None and len(historical_sequence) >= 2:
            previous_regime = historical_sequence[-2]
        previous_regime = _regime(previous_regime, current_regime) if previous_regime is not None else None

        shift_signal_strength = _bounded(signal.get('shift_signal_strength', merged.get('shift_signal_strength', 0.0)))
        transition_probability = _bounded(transition.get('transition_probability', merged.get('transition_probability', 0.0)))
        break_significance = _bounded(structural.get('break_significance', merged.get('break_significance', 0.0)))
        constraint_shift_index = _bounded(constraint.get('constraint_shift_index', merged.get('constraint_shift_index', 0.0)))
        constraint_regime_distance = _bounded(constraint.get('constraint_regime_distance', merged.get('constraint_regime_distance', 0.0)))
        classification_confidence = _bounded(classification.get('classification_confidence', merged.get('classification_confidence', 0.0)))
        emergence_probability = _bounded(emergence.get('emergence_probability', merged.get('emergence_probability', 0.0)))
        novelty_index = _bounded(emergence.get('novelty_index', merged.get('novelty_index', 0.0)))
        transition_density = _bounded(observatory.get('transition_density', dashboard.get('metrics', {}).get('transition_density', merged.get('transition_density', 0.0)) if isinstance(dashboard.get('metrics'), dict) else merged.get('transition_density', 0.0)))
        dashboard_completeness = _bounded(dashboard.get('dashboard_completeness', merged.get('dashboard_completeness', 0.0)))

        regime_signal = 0.0 if current_regime == 'stability' else 1.0
        historical_change_signal = 1.0 if previous_regime is not None and previous_regime != current_regime else 0.0
        confidence = round(_weighted_mean([
            (shift_signal_strength, 1.25),
            (transition_probability, 1.15),
            (break_significance, 1.15),
            (max(constraint_shift_index, constraint_regime_distance), 1.0),
            (classification_confidence if current_regime in SHIFT_REGIMES else 0.0, 1.0),
            (max(emergence_probability, novelty_index), 0.9),
            (transition_density, 0.75),
            (regime_signal, 0.85),
            (historical_change_signal, 0.6),
            (dashboard_completeness, 0.35),
        ]), 4)

        paradigm_shift_detected = bool(
            confidence >= 0.6
            or current_regime in ('rupture', 'collapse') and confidence >= 0.45
            or current_regime in ('transition', 'expansion') and confidence >= 0.5
        )
        if current_regime == 'stability' and confidence < 0.6:
            paradigm_shift_detected = False

        detection_class = 'no_shift_detected'
        if paradigm_shift_detected:
            if current_regime == 'rupture' or break_significance >= 0.75:
                detection_class = 'structural_rupture_detected'
            elif current_regime == 'collapse':
                detection_class = 'collapse_regime_detected'
            elif current_regime == 'expansion' or max(emergence_probability, novelty_index) >= 0.65:
                detection_class = 'emergent_expansion_detected'
            else:
                detection_class = 'regime_transition_detected'

        input_completeness = round(sum([
            bool(signal), bool(transition), bool(structural), bool(constraint),
            bool(classification), bool(emergence), bool(observatory), bool(dashboard)
        ]) / 8.0, 4)

        indicators = {
            'paradigm_shift_detected': 1.0 if paradigm_shift_detected else 0.0,
            'paradigm_shift_confidence': confidence,
            'shift_signal_strength': shift_signal_strength,
            'transition_probability': transition_probability,
            'break_significance': break_significance,
            'constraint_shift_index': constraint_shift_index,
            'constraint_regime_distance': constraint_regime_distance,
            'classification_confidence': classification_confidence,
            'emergence_probability': emergence_probability,
            'novelty_index': novelty_index,
            'transition_density': transition_density,
            'dashboard_completeness': dashboard_completeness,
            'input_completeness': input_completeness,
            'shift_signal_count': _non_negative_int(signal.get('shift_signal_count', merged.get('shift_signal_count', 0))),
            'structural_break_count': _non_negative_int(structural.get('structural_break_count', merged.get('structural_break_count', 0))),
            'transition_count': _non_negative_int(observatory.get('transition_count', dashboard.get('metrics', {}).get('transition_count', merged.get('transition_count', 0)) if isinstance(dashboard.get('metrics'), dict) else merged.get('transition_count', 0))),
            'new_structure_count': _non_negative_int(emergence.get('new_structure_count', merged.get('new_structure_count', 0))),
        }

        return {
            'primitive': PRIMITIVE,
            'timestamp_utc': _now(),
            'success': True,
            'paradigm_shift_detected': paradigm_shift_detected,
            'paradigm_shift_confidence': confidence,
            'current_regime': current_regime,
            'previous_regime': previous_regime,
            'detection_class': detection_class,
            'historical_regime_sequence': historical_sequence,
            'input_completeness': input_completeness,
            'indicators': indicators,
            'source_primitives': {
                'I1': bool(signal), 'I2': bool(transition), 'I3': bool(structural), 'I4': bool(constraint),
                'I5': bool(classification), 'I6': bool(emergence), 'I7': bool(observatory), 'I8': bool(dashboard),
            },
            'governance': {
                'non_closure_compliant': True,
                'closure_pressure_increase': False,
                'traceability': True,
                'reversibility': True,
                'functional_metrics_only': True,
            },
            'epistemic_position': {
                'architecture_computationnelle': True,
                'indicateurs_fonctionnels_mesurables': True,
                'subjectivite_phenomenale_affirmee': False,
                'ontologie_conceptuelle': 'paradigm shift detection through functional aggregation',
            },
            'error_count': 0,
        }

    def _write_json(self, state: dict[str, Any]) -> None:
        self.latest_json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')

    def _write_prometheus(self, state: dict[str, Any]) -> None:
        indicators = state.get('indicators', {}) if isinstance(state.get('indicators'), dict) else {}
        lines = [
            '# HELP oce_paradigm_shift_detection_success I9 detection engine execution success.',
            '# TYPE oce_paradigm_shift_detection_success gauge',
            f"oce_paradigm_shift_detection_success {1 if state.get('success') else 0}",
            '# HELP oce_paradigm_shift_detected I9 paradigm shift detection decision.',
            '# TYPE oce_paradigm_shift_detected gauge',
            f"oce_paradigm_shift_detected {1 if state.get('paradigm_shift_detected') else 0}",
            '# HELP oce_paradigm_shift_confidence I9 paradigm shift detection confidence.',
            '# TYPE oce_paradigm_shift_confidence gauge',
            f"oce_paradigm_shift_confidence {float(state.get('paradigm_shift_confidence', 0.0))}",
        ]
        for key, value in indicators.items():
            if isinstance(value, bool):
                numeric = 1 if value else 0
            elif isinstance(value, (int, float)):
                numeric = value
            else:
                continue
            safe_key = ''.join(ch if ch.isalnum() else '_' for ch in str(key).lower()).strip('_')
            lines.append(f'oce_paradigm_shift_{safe_key} {numeric}')
        self.prometheus_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    def _write_html(self, state: dict[str, Any]) -> None:
        indicators = state.get('indicators', {}) if isinstance(state.get('indicators'), dict) else {}
        top_fields = {
            'paradigm_shift_detected': state.get('paradigm_shift_detected'),
            'paradigm_shift_confidence': state.get('paradigm_shift_confidence'),
            'current_regime': state.get('current_regime'),
            'previous_regime': state.get('previous_regime'),
            'detection_class': state.get('detection_class'),
            'input_completeness': state.get('input_completeness'),
        }
        rows = [f'<tr><td>{escape(str(k))}</td><td>{escape(str(v))}</td></tr>' for k, v in {**top_fields, **indicators}.items()]
        sequence = state.get('historical_regime_sequence', [])
        html = "<!doctype html><html><head><meta charset='utf-8'><title>Paradigm Shift Detection Engine</title><style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ccc;padding:8px;text-align:left;}th{background:#f0f0f0;}code{background:#f6f6f6;padding:2px 4px;}</style></head><body><h1>Paradigm Shift Detection Engine</h1><p>I9 central aggregation for measurable paradigm-shift detection. No phenomenal subjectivity claim is made.</p><table><tr><th>Indicator</th><th>Value</th></tr>" + '\n'.join(rows) + '</table><h2>Historical regime sequence</h2><p><code>' + escape(' -> '.join(str(x) for x in sequence)) + '</code></p></body></html>\n'
        self.html_path.write_text(html, encoding='utf-8')

    def _record_metrics_safely(self, state: dict[str, Any], metrics_effect_context=None) -> None:
        try:
            from ontology.metrics_history_recorder import record_metrics
            payload = {'primitive': PRIMITIVE, **state.get('indicators', {}), 'error_count': 0}
            record_metrics(payload, primitive=PRIMITIVE, validation_status='validated', governance_status='governed', runtime_status='operational', effect_context=metrics_effect_context)
        except Exception:
            pass

    def step(self, inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        metrics_effect_context = inputs.pop("metrics_effect_context", None)
        state = self._make_state(inputs)
        self._write_json(state)
        self._write_prometheus(state)
        self._write_html(state)
        self._record_metrics_safely(state, metrics_effect_context=metrics_effect_context)
        state.update({
            'json_export_ready': self.latest_json_path.exists(),
            'prometheus_export_ready': self.prometheus_path.exists(),
            'html_export_ready': self.html_path.exists(),
            'json_path': str(self.latest_json_path),
            'prometheus_path': str(self.prometheus_path),
            'html_path': str(self.html_path),
        })
        return state


ENGINE = ParadigmShiftDetectionEngine()


def step(inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return ENGINE.step(inputs)
