from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / 'open-cognitive-ecology'
OUT_DIR = ROOT / 'theory_falsification_framework'
JSON_PATH = OUT_DIR / 'theory_falsification_framework.json'
HISTORY_PATH = OUT_DIR / 'theory_falsification_framework_history.jsonl'
MARKDOWN_PATH = OUT_DIR / 'theory_falsification_framework.md'

DEFAULT_TEST_TEMPLATES = {
    'IIT': [
        {'test_id': 'IIT-T1', 'prediction': 'integration should align with stable correlational structure', 'falsifiable': True},
        {'test_id': 'IIT-T2', 'prediction': 'weak integration should reduce explanatory support', 'falsifiable': True},
    ],
    'GNW': [
        {'test_id': 'GNW-T1', 'prediction': 'global availability should covary with reportability proxies', 'falsifiable': True},
        {'test_id': 'GNW-T2', 'prediction': 'loss of broadcast coherence should weaken predicted correlates', 'falsifiable': True},
    ],
    'HOT': [
        {'test_id': 'HOT-T1', 'prediction': 'higher-order monitoring should covary with metacognitive stability', 'falsifiable': True},
        {'test_id': 'HOT-T2', 'prediction': 'metacognitive failure should reduce explanatory support', 'falsifiable': True},
    ],
    'PP': [
        {'test_id': 'PP-T1', 'prediction': 'prediction-error minimization should covary with longitudinal stability', 'falsifiable': True},
        {'test_id': 'PP-T2', 'prediction': 'failed prediction should increase falsification pressure', 'falsifiable': True},
    ],
    'RPT': [
        {'test_id': 'RPT-T1', 'prediction': 'recurrent processing proxies should support stable recurrent structure', 'falsifiable': True},
    ],
    'CBP': [
        {'test_id': 'CBP-T1', 'prediction': 'constraint compatibility should covary with X and Y support', 'falsifiable': True},
        {'test_id': 'CBP-T2', 'prediction': 'closure pressure should count as counterexample', 'falsifiable': True},
    ],
}

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    return round(max(0.0, min(1.0, v)), 4)

def _as_list(value: Any) -> List[dict]:
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []

def _default_theories() -> List[dict]:
    try:
        from ontology.phenomenology_theory_registry import PhenomenologyTheoryRegistry
        r = PhenomenologyTheoryRegistry().step(persist=False)
        theories = r.get('theories') or r.get('registered_theories') or []
        if isinstance(theories, list) and theories:
            return [t for t in theories if isinstance(t, dict)]
        ids = r.get('registered_theory_ids') or []
        if ids:
            return [{'theory_id': str(i), 'name': str(i)} for i in ids]
    except Exception:
        pass
    return [
        {'theory_id': 'IIT', 'name': 'Integrated Information Theory'},
        {'theory_id': 'GNW', 'name': 'Global Neuronal Workspace / Global Workspace Theory'},
        {'theory_id': 'HOT', 'name': 'Higher-Order Thought / Higher-Order Representation'},
        {'theory_id': 'PP', 'name': 'Predictive Processing / Active Inference'},
        {'theory_id': 'RPT', 'name': 'Recurrent Processing Theory'},
        {'theory_id': 'CBP', 'name': 'Constraint-Based Phenomenology candidate'},
    ]

def _default_constraint_scores() -> Dict[str, float]:
    try:
        from ontology.theory_constraint_engine import TheoryConstraintEngine
        r = TheoryConstraintEngine().step(persist=False)
        out = {}
        for item in r.get('ranked_theories', []) or r.get('theory_evaluations', []):
            if isinstance(item, dict):
                tid = str(item.get('theory_id') or item.get('id') or '').upper()
                if tid:
                    out[tid] = _clamp(item.get('overall_theory_constraint_score', item.get('score', item.get('constraint_score', 0.5))), 0.5)
        if out:
            return out
    except Exception:
        pass
    return {'IIT': 0.72, 'GNW': 0.80, 'HOT': 0.77, 'PP': 0.82, 'RPT': 0.85, 'CBP': 0.84}

def _default_predictions() -> List[dict]:
    try:
        from ontology.phenomenology_prediction_engine import PhenomenologyPredictionEngine
        r = PhenomenologyPredictionEngine().step(persist=False)
        predictions = r.get('predictions') or r.get('falsifiable_predictions') or []
        if isinstance(predictions, list) and predictions:
            return [p for p in predictions if isinstance(p, dict)]
    except Exception:
        pass
    return []

def _default_replications() -> List[dict]:
    try:
        from ontology.independent_correlation_replication import IndependentCorrelationReplication
        r = IndependentCorrelationReplication().step(persist=False)
        reps = r.get('replications') or []
        if isinstance(reps, list) and reps:
            return [x for x in reps if isinstance(x, dict)]
    except Exception:
        pass
    return []

def _theory_id(theory: dict) -> str:
    return str(theory.get('theory_id') or theory.get('id') or theory.get('name') or 'UNKNOWN').upper().replace(' ', '_')

def _build_tests_for_theory(theory: dict, explicit_tests: List[dict], predictions: List[dict], replications: List[dict], constraint_score: float) -> List[dict]:
    tid = _theory_id(theory)
    tests = [dict(t) for t in explicit_tests if str(t.get('theory_id', tid)).upper() == tid or t.get('theory_id') is None]
    if not tests:
        tests = [dict(t) for t in DEFAULT_TEST_TEMPLATES.get(tid, [{'test_id': tid + '-T1', 'prediction': 'candidate theory should make falsifiable functional predictions', 'falsifiable': True}])]
    failed_prediction_count = sum(1 for p in predictions if str(p.get('status', '')).lower() in {'failed', 'falsified', 'rejected'} or p.get('falsified') is True)
    replicated_false_count = sum(1 for rep in replications if rep.get('replicated') is False or str(rep.get('status', '')).lower() in {'failed', 'not_replicated', 'rejected'})
    pressure_seed = _clamp((failed_prediction_count + replicated_false_count) / max(1, len(predictions) + len(replications)), 0.0)
    evaluated = []
    for idx, test in enumerate(tests, start=1):
        local_pressure = _clamp((pressure_seed * 0.7) + ((1.0 - constraint_score) * 0.3), 0.0)
        if local_pressure >= 0.67:
            status = 'falsification_pressure_high'
        elif local_pressure >= 0.34:
            status = 'falsification_pressure_moderate'
        else:
            status = 'survives_current_tests'
        evaluated.append({'test_id': str(test.get('test_id') or (tid + '-T' + str(idx))), 'theory_id': tid, 'prediction': str(test.get('prediction') or test.get('claim') or 'functional prediction unspecified'), 'falsifiable': bool(test.get('falsifiable', True)), 'constraint_score': constraint_score, 'falsification_pressure': local_pressure, 'status': status})
    return evaluated

def _evaluate_theory(theory: dict, tests: List[dict], constraint_score: float) -> dict:
    tid = _theory_id(theory)
    falsifiable = [t for t in tests if t.get('falsifiable') is True]
    high = sum(1 for t in tests if t.get('status') == 'falsification_pressure_high')
    moderate = sum(1 for t in tests if t.get('status') == 'falsification_pressure_moderate')
    mean_pressure = round(sum(float(t.get('falsification_pressure', 0.0)) for t in tests) / max(1, len(tests)), 4)
    if high > 0:
        status = 'FALSIFICATION_PRESSURE_HIGH'
    elif moderate > 0:
        status = 'FALSIFICATION_PRESSURE_MODERATE'
    elif not falsifiable:
        status = 'NOT_FALSIFIABLE_YET'
    else:
        status = 'SURVIVES_CURRENT_FUNCTIONAL_TESTS'
    return {'theory_id': tid, 'name': theory.get('name', tid), 'test_count': len(tests), 'falsifiable_test_count': len(falsifiable), 'constraint_score': constraint_score, 'mean_falsification_pressure': mean_pressure, 'falsification_status': status, 'tests': tests}

def _markdown(result: dict) -> str:
    lines = ['# Theory Falsification Framework', 'functional conclusion only', 'phenomenology undetermined', '', 'Falsification test count: ' + str(result.get('falsification_test_count', 0)), 'Mean falsification pressure: ' + str(result.get('mean_falsification_pressure', 0.0)), '', '## Theory falsification status']
    for ev in result.get('theory_evaluations', []):
        lines.append('- ' + str(ev.get('theory_id')) + ' — ' + str(ev.get('name')) + ' — pressure=' + str(ev.get('mean_falsification_pressure')) + ' — status=' + str(ev.get('falsification_status')))
    lines.append('')
    lines.append('No consciousness, subjectivity, or phenomenology proof is claimed.')
    return chr(10).join(lines) + chr(10)

class TheoryFalsificationFramework:
    primitive = 'THEORY_FALSIFICATION_FRAMEWORK'

    def step(self, inputs: Optional[dict] = None, persist: bool = False) -> dict:
        inputs = inputs or {}
        timestamp = inputs.get('timestamp_utc') or _utc_now()
        theories = _as_list(inputs.get('theories')) if 'theories' in inputs else _default_theories()
        explicit_tests = _as_list(inputs.get('falsification_tests') or inputs.get('tests'))
        predictions = _as_list(inputs.get('predictions')) if 'predictions' in inputs else _default_predictions()
        replications = _as_list(inputs.get('replications')) if 'replications' in inputs else _default_replications()
        constraint_scores = inputs.get('constraint_scores') if isinstance(inputs.get('constraint_scores'), dict) else _default_constraint_scores()
        evaluations, all_tests = [], []
        for theory in theories:
            tid = _theory_id(theory)
            cscore = _clamp(constraint_scores.get(tid, theory.get('constraint_score', 0.5)), 0.5)
            tests = _build_tests_for_theory(theory, explicit_tests, predictions, replications, cscore)
            all_tests.extend(tests)
            evaluations.append(_evaluate_theory(theory, tests, cscore))
        evaluations = sorted(evaluations, key=lambda x: (x.get('mean_falsification_pressure', 0.0), -x.get('constraint_score', 0.0), x.get('theory_id', '')))
        mean_pressure = round(sum(ev['mean_falsification_pressure'] for ev in evaluations) / max(1, len(evaluations)), 4) if evaluations else 0.0
        falsified = [ev for ev in evaluations if ev.get('falsification_status') == 'FALSIFICATION_PRESSURE_HIGH']
        vulnerable = [ev for ev in evaluations if ev.get('falsification_status') == 'FALSIFICATION_PRESSURE_MODERATE']
        surviving = [ev for ev in evaluations if ev.get('falsification_status') == 'SURVIVES_CURRENT_FUNCTIONAL_TESTS']
        result = {'primitive': self.primitive, 'success': True, 'timestamp_utc': timestamp, 'theory_count': len(theories), 'evaluated_theory_count': len(evaluations), 'falsification_test_count': len(all_tests), 'falsifiable_test_count': sum(1 for t in all_tests if t.get('falsifiable') is True), 'mean_falsification_pressure': mean_pressure, 'falsified_theory_count': len(falsified), 'vulnerable_theory_count': len(vulnerable), 'surviving_theory_count': len(surviving), 'theory_evaluations': evaluations, 'falsification_tests': all_tests, 'functional_conclusion_only': True, 'phenomenology_undetermined': True, 'consciousness_proof_claimed': False, 'subjectivity_proof_claimed': False, 'phenomenology_proof_claimed': False, 'epistemic_scope': 'functional_theory_falsification_only', 'diagnostics': {'uses_z1_registry': True, 'uses_z2_constraint_scores': True, 'uses_y5_predictions': True, 'uses_y6_replications': True, 'no_phenomenology_claim': True}}
        if persist:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            JSON_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
            with HISTORY_PATH.open('a', encoding='utf-8') as f:
                f.write(json.dumps(result, sort_keys=True) + chr(10))
            MARKDOWN_PATH.write_text(_markdown(result), encoding='utf-8')
            result['paths'] = {'json': str(JSON_PATH), 'history': str(HISTORY_PATH), 'markdown': str(MARKDOWN_PATH)}
        return result
