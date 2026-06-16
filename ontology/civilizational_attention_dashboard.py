from __future__ import annotations

import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def _clamp01(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = default
    if math.isnan(x) or math.isinf(x):
        x = default
    return max(0.0, min(1.0, x))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(x) or math.isinf(x):
        return default
    return x


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class CivilizationalAttentionDashboard:
    '''P10 — Civilizational Attention Dashboard.

    Specialized dashboard for the civilizational economy of attention.
    It aggregates P1 to P9 functional metrics only and does not make any
    claim of phenomenal subjectivity.
    '''

    primitive = 'CIVILIZATIONAL_ATTENTION_DASHBOARD'

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / 'open-cognitive-ecology'
        self.output_dir = (
            self.root
            / 'runtime_experiments'
            / 'civilizational_attention_dashboard'
        )
        self.dashboard_path = self.output_dir / 'civilizational_attention_dashboard.html'
        self.json_path = self.output_dir / 'civilizational_attention_dashboard.json'
        self.prometheus_path = self.output_dir / 'civilizational_attention_dashboard.prom'
        self.grafana_path = self.output_dir / 'civilizational_attention_dashboard_grafana.json'

    def _sizes(self, population_sizes: Iterable[int] | None) -> list[int]:
        if population_sizes is None:
            population_sizes = [100, 1000, 10000, 100000, 1000000]
        out: list[int] = []
        for size in population_sizes:
            try:
                out.append(max(0, int(size)))
            except (TypeError, ValueError):
                out.append(0)
        return out

    def _call(self, label: str, factory: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            result = factory().step(**kwargs)
            if isinstance(result, dict):
                return result
            return {'success': False, 'error': 'non_dict_result', 'repr': repr(result)}
        except Exception as exc:
            return {'success': False, 'error': repr(exc), 'source': label}

    def _collect_states(
        self,
        population_sizes: list[int],
        available_attention_budget: float,
        max_deep_cognition_ratio: float,
    ) -> dict[str, Any]:
        max_population = max(population_sizes, default=0)
        budget = max(0.0, _safe_float(available_attention_budget, 1.0))

        try:
            from ontology.civilizational_attention_allocator import CivilizationalAttentionAllocator
            p1 = self._call('p1', CivilizationalAttentionAllocator, population_size=max_population, available_attention_budget=budget)
        except Exception as exc:
            p1 = {'success': False, 'error': repr(exc)}

        try:
            from ontology.population_activation_scheduler import PopulationActivationScheduler
            p2 = self._call('p2', PopulationActivationScheduler, population_size=max_population, available_attention_budget=budget)
        except Exception as exc:
            p2 = {'success': False, 'error': repr(exc)}

        try:
            from ontology.activity_gradient_manager import ActivityGradientManager
            p3 = self._call('p3', ActivityGradientManager, population_size=max_population, available_attention_budget=budget)
        except Exception as exc:
            p3 = {'success': False, 'error': repr(exc)}

        try:
            from ontology.computational_fairness_engine import ComputationalFairnessEngine
            p4 = self._call('p4', ComputationalFairnessEngine, population_size=max_population, available_attention_budget=budget)
        except Exception as exc:
            p4 = {'success': False, 'error': repr(exc)}

        try:
            from ontology.lineage_diversity_preservation import LineageDiversityPreservation
            p5 = self._call('p5', LineageDiversityPreservation, population_size=max_population, available_attention_budget=budget)
        except Exception as exc:
            p5 = {'success': False, 'error': repr(exc)}

        try:
            from ontology.constraint_based_attention_economy import ConstraintBasedAttentionEconomy
            p6 = self._call('p6', ConstraintBasedAttentionEconomy, population_size=max_population, available_attention_budget=budget)
        except Exception as exc:
            p6 = {'success': False, 'error': repr(exc)}

        try:
            from ontology.massive_population_simulator import MassivePopulationSimulator
            p7 = self._call('p7', MassivePopulationSimulator, population_sizes=population_sizes, available_attention_budget=budget, persist=False)
        except Exception as exc:
            p7 = {'success': False, 'error': repr(exc), 'results': []}

        try:
            from ontology.population_compression_framework import PopulationCompressionFramework
            p8 = self._call('p8', PopulationCompressionFramework, population_sizes=population_sizes, persist=False)
        except Exception as exc:
            p8 = {'success': False, 'error': repr(exc), 'results': []}

        try:
            from ontology.selective_cognitive_activation import SelectiveCognitiveActivation
            p9 = self._call('p9', SelectiveCognitiveActivation, population_sizes=population_sizes, available_attention_budget=budget, max_deep_cognition_ratio=max_deep_cognition_ratio, persist=False)
        except Exception as exc:
            p9 = {'success': False, 'error': repr(exc), 'results': []}

        return {
            'p1_attention_allocator': p1,
            'p2_activation_scheduler': p2,
            'p3_activity_gradient': p3,
            'p4_fairness_engine': p4,
            'p5_diversity_preservation': p5,
            'p6_attention_economy': p6,
            'p7_massive_population': p7,
            'p8_population_compression': p8,
            'p9_selective_activation': p9,
        }

    def _metric(self, states: dict[str, Any], path: list[str], default: float = 0.0) -> float:
        cur: Any = states
        for key in path:
            if isinstance(cur, dict):
                cur = cur.get(key)
            else:
                return default
        return _safe_float(cur, default)

    def _latest_result(self, state: dict[str, Any]) -> dict[str, Any]:
        results = state.get('results') if isinstance(state, dict) else None
        if isinstance(results, list) and results:
            return results[-1] if isinstance(results[-1], dict) else {}
        return {}

    def _summary(self, states: dict[str, Any], population_sizes: list[int]) -> dict[str, Any]:
        p7_last = self._latest_result(states.get('p7_massive_population', {}))
        p8_last = self._latest_result(states.get('p8_population_compression', {}))
        p9_last = self._latest_result(states.get('p9_selective_activation', {}))

        attention_pressure = max(
            0.0,
            _safe_float(p7_last.get('civilizational_attention_pressure'), 0.0),
            _safe_float(states.get('p6_attention_economy', {}).get('civilizational_attention_pressure'), 0.0),
        )
        attention_saturation = _clamp01(
            p7_last.get('attention_saturation_index', states.get('p6_attention_economy', {}).get('attention_saturation_index', 0.0))
        )
        attention_viability = _clamp01(
            p7_last.get('attention_viability_index', states.get('p6_attention_economy', {}).get('attention_viability_index', 0.0))
        )
        fairness = _clamp01(states.get('p4_fairness_engine', {}).get('computational_fairness_index'), 0.0)
        diversity = _clamp01(states.get('p5_diversity_preservation', {}).get('lineage_preservation_score'), 0.0)
        compression_ratio = max(1.0, _safe_float(p8_last.get('compression_ratio', states.get('p8_population_compression', {}).get('compression_ratio', 1.0)), 1.0))
        bytes_per_individual = max(0.0, _safe_float(p8_last.get('bytes_per_individual', states.get('p8_population_compression', {}).get('bytes_per_individual', 0.0)), 0.0))
        deep_ratio = _clamp01(p9_last.get('deep_cognition_ratio', states.get('p9_selective_activation', {}).get('deep_cognition_ratio', 0.0)))
        external_rate = _clamp01(p9_last.get('external_cognition_rate', states.get('p9_selective_activation', {}).get('external_cognition_rate', 0.0)))
        selective_index = _clamp01(p9_last.get('selective_activation_index', states.get('p9_selective_activation', {}).get('selective_activation_index', 0.0)))
        cpu_percent = max(0.0, _safe_float(p7_last.get('cpu_percent'), 0.0))
        ram_mb = max(0.0, _safe_float(p7_last.get('ram_mb'), 0.0))

        integrated_score = _clamp01(
            0.18 * attention_viability
            + 0.16 * (1.0 - attention_saturation)
            + 0.15 * fairness
            + 0.15 * diversity
            + 0.14 * min(1.0, compression_ratio / 10.0)
            + 0.12 * selective_index
            + 0.10 * (1.0 - deep_ratio)
        )

        bounded_values = [
            attention_saturation,
            attention_viability,
            fairness,
            diversity,
            min(1.0, compression_ratio / 10.0),
            deep_ratio,
            external_rate,
            selective_index,
            integrated_score,
        ]
        bounded_metrics = all(0.0 <= x <= 1.0 for x in bounded_values)

        return {
            'max_population_tested': max(population_sizes, default=0),
            'million_population_tested': max(population_sizes, default=0) >= 1000000,
            'civilizational_attention_pressure': attention_pressure,
            'attention_saturation_index': attention_saturation,
            'attention_viability_index': attention_viability,
            'computational_fairness_index': fairness,
            'lineage_preservation_score': diversity,
            'compression_ratio': compression_ratio,
            'bytes_per_individual': bytes_per_individual,
            'deep_cognition_ratio': deep_ratio,
            'external_cognition_rate': external_rate,
            'selective_activation_index': selective_index,
            'cpu_percent': cpu_percent,
            'ram_mb': ram_mb,
            'civilizational_attention_dashboard_index': integrated_score,
            'bounded_metrics': bounded_metrics,
        }

    def _render_html(self, payload: dict[str, Any]) -> str:
        summary = payload['summary']
        rows = ''.join(
            '<tr><td>{}</td><td>{}</td></tr>'.format(
                html.escape(str(k)),
                html.escape(str(v)),
            )
            for k, v in summary.items()
        )
        cards = ''.join(
            '<div class="card"><h3>{}</h3><pre>{}</pre></div>'.format(
                html.escape(name),
                html.escape(json.dumps(value, indent=2, sort_keys=True)[:4000]),
            )
            for name, value in payload['states'].items()
        )
        return f'''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Civilizational Attention Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; background: #fafafa; color: #222; }}
h1 {{ margin-bottom: 0; }}
.subtitle {{ color: #555; margin-top: 6px; }}
table {{ border-collapse: collapse; width: 100%; background: white; margin-top: 24px; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }}
th {{ background: #f0f0f0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-top: 24px; }}
.card {{ background: white; border: 1px solid #ddd; border-radius: 8px; padding: 12px; overflow: auto; }}
pre {{ white-space: pre-wrap; font-size: 12px; }}
</style>
</head>
<body>
<h1>Civilizational Attention Dashboard</h1>
<p class="subtitle">Generated at {html.escape(payload['timestamp_utc'])}. Functional metrics only; no phenomenal subjectivity claim.</p>
<table><tr><th>Metric</th><th>Value</th></tr>{rows}</table>
<div class="grid">{cards}</div>
</body>
</html>
'''

    def _render_prometheus(self, payload: dict[str, Any]) -> str:
        summary = payload['summary']
        names = {
            'max_population_tested': 'oce_attention_max_population_tested',
            'civilizational_attention_pressure': 'oce_civilizational_attention_pressure',
            'attention_saturation_index': 'oce_attention_saturation_index',
            'attention_viability_index': 'oce_attention_viability_index',
            'computational_fairness_index': 'oce_computational_fairness_index',
            'lineage_preservation_score': 'oce_lineage_preservation_score',
            'compression_ratio': 'oce_population_compression_ratio',
            'bytes_per_individual': 'oce_population_bytes_per_individual',
            'deep_cognition_ratio': 'oce_deep_cognition_ratio',
            'external_cognition_rate': 'oce_external_cognition_rate',
            'selective_activation_index': 'oce_selective_activation_index',
            'cpu_percent': 'oce_population_simulation_cpu_percent',
            'ram_mb': 'oce_population_simulation_ram_mb',
            'civilizational_attention_dashboard_index': 'oce_civilizational_attention_dashboard_index',
        }
        lines = [
            '# Civilizational Attention Dashboard metrics',
            '# Functional metrics only; no phenomenal subjectivity claim.',
        ]
        for key, prom_name in names.items():
            value = summary.get(key)
            if isinstance(value, bool):
                value = 1.0 if value else 0.0
            if isinstance(value, (int, float)):
                lines.append(f'# TYPE {prom_name} gauge')
                lines.append(f'{prom_name} {float(value)}')
        return '\n'.join(lines) + '\n'

    def _render_grafana(self, payload: dict[str, Any]) -> dict[str, Any]:
        panels = []
        metrics = [
            ('Attention Pressure', 'oce_civilizational_attention_pressure'),
            ('Attention Saturation', 'oce_attention_saturation_index'),
            ('Attention Viability', 'oce_attention_viability_index'),
            ('Fairness', 'oce_computational_fairness_index'),
            ('Lineage Preservation', 'oce_lineage_preservation_score'),
            ('Compression Ratio', 'oce_population_compression_ratio'),
            ('Deep Cognition Ratio', 'oce_deep_cognition_ratio'),
            ('Selective Activation', 'oce_selective_activation_index'),
            ('CPU Percent', 'oce_population_simulation_cpu_percent'),
            ('RAM MB', 'oce_population_simulation_ram_mb'),
        ]
        for idx, (title, expr) in enumerate(metrics, start=1):
            panels.append({
                'id': idx,
                'type': 'stat',
                'title': title,
                'targets': [{'expr': expr, 'refId': 'A'}],
                'gridPos': {'h': 4, 'w': 6, 'x': ((idx - 1) % 4) * 6, 'y': ((idx - 1) // 4) * 4},
            })
        return {
            'title': 'Open Cognitive Ecology — Civilizational Attention Dashboard',
            'uid': 'oce-civilizational-attention-dashboard',
            'schemaVersion': 39,
            'version': 1,
            'refresh': '30s',
            'panels': panels,
            'tags': ['open-cognitive-ecology', 'attention-economy', 'P10'],
        }

    def _write_outputs(self, payload: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
        self.dashboard_path.write_text(self._render_html(payload), encoding='utf-8')
        self.prometheus_path.write_text(self._render_prometheus(payload), encoding='utf-8')
        self.grafana_path.write_text(json.dumps(self._render_grafana(payload), indent=2, sort_keys=True), encoding='utf-8')

    def step(
        self,
        population_sizes: Iterable[int] | None = None,
        available_attention_budget: float = 1.0,
        max_deep_cognition_ratio: float = 0.01,
        persist: bool = True,
        **_: Any,
    ) -> dict[str, Any]:
        sizes = self._sizes(population_sizes)
        states = self._collect_states(
            population_sizes=sizes,
            available_attention_budget=available_attention_budget,
            max_deep_cognition_ratio=max_deep_cognition_ratio,
        )
        summary = self._summary(states, sizes)

        payload: dict[str, Any] = {
            'primitive': self.primitive,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'population_sizes': sizes,
            'summary': summary,
            'states': states,
            'dashboard_path': str(self.dashboard_path),
            'json_path': str(self.json_path),
            'prometheus_path': str(self.prometheus_path),
            'grafana_path': str(self.grafana_path),
            'html_dashboard_generated': bool(persist),
            'prometheus_export_generated': bool(persist),
            'grafana_export_generated': bool(persist),
            'population_metrics_integrated': True,
            'attention_metrics_integrated': True,
            'lineage_metrics_integrated': True,
            'resource_metrics_integrated': True,
            'compression_metrics_integrated': True,
            'selective_activation_metrics_integrated': True,
            'dashboard_generated': bool(persist),
            'bounded_metrics': bool(summary['bounded_metrics']),
            'classification': (
                'Civilizational Attention Dashboard Operational'
                if summary['bounded_metrics']
                else 'Civilizational Attention Dashboard Degraded'
            ),
            'diagnostics': {
                'phenomenal_subjectivity_claimed': False,
                'validation_scope': 'functional_metrics_only',
                'architecture_layer': 'civilizational_attention_economy',
                'program': 'P10',
                'dependencies': [
                    'civilizational_attention_allocator',
                    'population_activation_scheduler',
                    'activity_gradient_manager',
                    'computational_fairness_engine',
                    'lineage_diversity_preservation',
                    'constraint_based_attention_economy',
                    'massive_population_simulator',
                    'population_compression_framework',
                    'selective_cognitive_activation',
                ],
            },
        }

        if persist:
            self._write_outputs(payload)

        return payload
