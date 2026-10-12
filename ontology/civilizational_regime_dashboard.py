# -*- coding: utf-8 -*-
'''
I8 - Civilizational Regime Dashboard.

This module visualises measurable paradigm-regime surveillance signals for
Open Cognitive Ecology. It handles functional indicators only and does not
assert phenomenal subjectivity.
'''

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Optional
import json
import math

PRIMITIVE = 'civilizational_regime_dashboard'
DEPENDENCIES = ['paradigm_shift_signal_extractor','regime_transition_detector','structural_break_analyzer','constraint_regime_comparator','paradigm_classification_engine','emergence_detection_engine','paradigm_evolution_observatory','civilizational_web_dashboard','final_scientific_status_dashboard','civilizational_metrics_synthesizer','metrics_history_recorder','governance_consistency_checker','openness_preservation_supervisor','non_closure_certification_protocol']
REGIME_TAXONOMY = ('stability', 'transition', 'rupture', 'expansion', 'collapse')


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


class CivilizationalRegimeDashboard:
    primitive = PRIMITIVE
    taxonomy = REGIME_TAXONOMY

    def __init__(self, root: Optional[str | Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / 'open-cognitive-ecology'
        self.output_dir = self.root / 'paradigm_surveillance' / PRIMITIVE
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_json_path = self.output_dir / 'latest_civilizational_regime_dashboard.json'
        self.html_path = self.output_dir / 'civilizational_regime_dashboard.html'
        self.prometheus_path = self.output_dir / 'civilizational_regime_dashboard.prom'

    def _make_state(self, inputs: Optional[dict[str, Any]]) -> dict[str, Any]:
        inputs = dict(inputs or {})
        signal = _section(inputs, 'signal', 'paradigm_shift_signal', 'paradigm_shift_signal_extractor')
        transition = _section(inputs, 'transition', 'regime_transition', 'regime_transition_detector')
        structural = _section(inputs, 'structural_break', 'break', 'structural_break_analyzer')
        constraint = _section(inputs, 'constraint', 'constraint_regime', 'constraint_regime_comparator')
        classification = _section(inputs, 'classification', 'paradigm_classification', 'paradigm_classification_engine')
        emergence = _section(inputs, 'emergence', 'emergence_detection', 'emergence_detection_engine')
        observatory = _section(inputs, 'observatory', 'paradigm_evolution', 'paradigm_evolution_observatory')

        current_regime = str(classification.get('current_paradigm', inputs.get('current_regime', 'stability'))).strip().lower()
        if current_regime not in REGIME_TAXONOMY:
            current_regime = 'stability'

        historical_sequence = observatory.get('historical_regime_sequence', inputs.get('historical_regime_sequence', []))
        if not isinstance(historical_sequence, list):
            historical_sequence = []
        historical_sequence = [str(item) for item in historical_sequence][-100:]
        if current_regime and (not historical_sequence or historical_sequence[-1] != current_regime):
            historical_sequence.append(current_regime)

        transition_count = _non_negative_int(observatory.get('transition_count', inputs.get('transition_count', 0)))
        if transition_count == 0 and len(historical_sequence) > 1:
            transition_count = sum(1 for a, b in zip(historical_sequence, historical_sequence[1:]) if a != b)
        history_length = max(_non_negative_int(observatory.get('paradigm_history_length', len(historical_sequence)), len(historical_sequence)), len(historical_sequence))
        transition_density = _bounded(observatory.get('transition_density', transition_count / max(1, history_length - 1)))

        metrics = {
            'shift_signal_count': _non_negative_int(signal.get('shift_signal_count', inputs.get('shift_signal_count', 0))),
            'shift_signal_strength': _bounded(signal.get('shift_signal_strength', inputs.get('shift_signal_strength', 0.0))),
            'transition_probability': _bounded(transition.get('transition_probability', inputs.get('transition_probability', 0.0))),
            'transition_duration': _non_negative_int(transition.get('transition_duration', inputs.get('transition_duration', 0))),
            'structural_break_count': _non_negative_int(structural.get('structural_break_count', inputs.get('structural_break_count', 0))),
            'break_significance': _bounded(structural.get('break_significance', inputs.get('break_significance', 0.0))),
            'constraint_regime_distance': _bounded(constraint.get('constraint_regime_distance', inputs.get('constraint_regime_distance', 0.0))),
            'constraint_shift_index': _bounded(constraint.get('constraint_shift_index', inputs.get('constraint_shift_index', 0.0))),
            'classification_confidence': _bounded(classification.get('classification_confidence', inputs.get('classification_confidence', 0.0))),
            'emergence_probability': _bounded(emergence.get('emergence_probability', inputs.get('emergence_probability', 0.0))),
            'novelty_index': _bounded(emergence.get('novelty_index', inputs.get('novelty_index', 0.0))),
            'new_structure_count': _non_negative_int(emergence.get('new_structure_count', inputs.get('new_structure_count', 0))),
            'capability_emergence_score': _bounded(emergence.get('capability_emergence_score', inputs.get('capability_emergence_score', 0.0))),
            'paradigm_history_length': history_length,
            'transition_count': transition_count,
            'transition_density': transition_density,
            'paradigm_evolution_rate': _bounded(observatory.get('paradigm_evolution_rate', inputs.get('paradigm_evolution_rate', transition_density))),
        }
        completeness = round(sum([bool(signal), bool(transition), bool(structural), bool(constraint), bool(classification), bool(emergence), bool(observatory)]) / 7.0, 4)
        return {'primitive': PRIMITIVE,'timestamp_utc': _now(),'success': True,'current_regime': current_regime,'previous_regime': historical_sequence[-2] if len(historical_sequence) >= 2 else None,'historical_regime_sequence': historical_sequence,'transition_visualization_ready': current_regime == 'transition' or metrics['transition_probability'] >= 0.5 or transition_count > 0,'rupture_visualization_ready': current_regime == 'rupture' or metrics['break_significance'] >= 0.7 or metrics['shift_signal_strength'] >= 0.75,'emergence_visualization_ready': current_regime == 'expansion' or metrics['emergence_probability'] >= 0.5 or metrics['novelty_index'] >= 0.5,'historical_regime_visualization_ready': bool(historical_sequence),'dashboard_completeness': completeness,'metrics': metrics,'epistemic_position': {'architecture_computationnelle': True,'indicateurs_fonctionnels_mesurables': True,'subjectivite_phenomenale_affirmee': False,'ontologie_conceptuelle': 'paradigm-regime surveillance dashboard'},'governance': {'non_closure_compliant': True, 'closure_pressure_increase': False, 'traceability': True, 'reversibility': True}}

    def _write_json(self, state: dict[str, Any]) -> None:
        self.latest_json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')

    def _write_prometheus(self, state: dict[str, Any]) -> None:
        metrics = state.get('metrics', {}) if isinstance(state.get('metrics'), dict) else {}
        lines = ['# HELP oce_civilizational_regime_dashboard_success I8 dashboard execution success.','# TYPE oce_civilizational_regime_dashboard_success gauge',f"oce_civilizational_regime_dashboard_success {1 if state.get('success') else 0}",'# HELP oce_civilizational_regime_dashboard_completeness I8 dashboard input completeness.','# TYPE oce_civilizational_regime_dashboard_completeness gauge',f"oce_civilizational_regime_dashboard_completeness {float(state.get('dashboard_completeness', 0.0))}"]
        for key, value in metrics.items():
            if isinstance(value, bool):
                numeric = 1 if value else 0
            elif isinstance(value, (int, float)):
                numeric = value
            else:
                continue
            safe_key = ''.join(ch if ch.isalnum() else '_' for ch in str(key).lower()).strip('_')
            lines.append(f'oce_civilizational_regime_{safe_key} {numeric}')
        self.prometheus_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    def _write_html(self, state: dict[str, Any]) -> None:
        metrics = state.get('metrics', {}) if isinstance(state.get('metrics'), dict) else {}
        top_fields = {'current_regime': state.get('current_regime'),'previous_regime': state.get('previous_regime'),'dashboard_completeness': state.get('dashboard_completeness'),'transition_visualization_ready': state.get('transition_visualization_ready'),'rupture_visualization_ready': state.get('rupture_visualization_ready'),'emergence_visualization_ready': state.get('emergence_visualization_ready'),'historical_regime_visualization_ready': state.get('historical_regime_visualization_ready')}
        rows = [f'<tr><td>{escape(str(k))}</td><td>{escape(str(v))}</td></tr>' for k, v in {**top_fields, **metrics}.items()]
        sequence = state.get('historical_regime_sequence', [])
        html = "<!doctype html><html><head><meta charset='utf-8'><title>Civilizational Regime Dashboard</title><style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ccc;padding:8px;text-align:left;}th{background:#f0f0f0;}code{background:#f6f6f6;padding:2px 4px;}</style></head><body><h1>Civilizational Regime Dashboard</h1><p>I8 dashboard for measurable paradigm-regime surveillance. No phenomenal subjectivity claim is made.</p><table><tr><th>Metric</th><th>Value</th></tr>" + '\n'.join(rows) + '</table><h2>Historical regime sequence</h2><p><code>' + escape(' -> '.join(str(x) for x in sequence)) + '</code></p></body></html>\n'
        self.html_path.write_text(html, encoding='utf-8')

    def _record_metrics_safely(self, state: dict[str, Any], metrics_effect_context=None) -> None:
        try:
            from ontology.metrics_history_recorder import record_metrics
            payload = {'primitive': PRIMITIVE, **state.get('metrics', {}), 'dashboard_completeness': state.get('dashboard_completeness', 0.0), 'error_count': 0}
            record_metrics(payload, primitive=PRIMITIVE, validation_status='validated', governance_status='governed', runtime_status='operational', effect_context=metrics_effect_context)
        except Exception:
            pass

    def step(self, inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        metrics_effect_context = inputs.pop("metrics_effect_context", None)
        state = self._make_state(inputs)
        self._write_json(state); self._write_html(state); self._write_prometheus(state); self._record_metrics_safely(state, metrics_effect_context=metrics_effect_context)
        state.update({'json_export_ready': self.latest_json_path.exists(),'html_export_ready': self.html_path.exists(),'prometheus_export_ready': self.prometheus_path.exists(),'json_path': str(self.latest_json_path),'html_path': str(self.html_path),'prometheus_path': str(self.prometheus_path),'error_count': 0})
        return state


ENGINE = CivilizationalRegimeDashboard()

def step(inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return ENGINE.step(inputs)
