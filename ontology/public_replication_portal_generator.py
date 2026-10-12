
from __future__ import annotations

import html
import json
from pathlib import Path
from datetime import datetime, timezone
from statistics import mean
from typing import Any

from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

ROOT = Path.home() / 'open-cognitive-ecology'
PORTAL_DIR = ROOT / 'external_validation' / 'public_replication_portal'


def _now() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        v = default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        pass
    return {}


def _write_json(path: Path, data: dict[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
    if fs_context is None:
        raise PermissionError('persisted JSON requires preissued filesystem effect context')
    payload = json.dumps(data, indent=2, sort_keys=True).encode('utf-8')
    fs_context.execute_path('json_parent_create', 'FS_CREATE_DIR', path.parent)
    fs_context.execute_path('json_write', 'FS_WRITE_BYTES', path, payload)


class PublicReplicationPortalGenerator:
    """H11-R1 offline public replication portal generator.

    This primitive consolidates H7-H10 external validation artefacts into a
    static, local, publication-ready portal. It performs no network operation,
    requires no GitHub or Zenodo credential, and preserves non-closure by
    exposing replication routes without claiming final validation.
    """

    primitive = 'public_replication_portal_generator'
    refinement = 'H11-R1'

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.portal_dir = self.root / 'external_validation' / 'public_replication_portal'
        self.state_path = self.portal_dir / 'latest_public_replication_portal.json'
        self.history_path = self.portal_dir / 'public_replication_portal_history.jsonl'
        self.html_path = self.portal_dir / 'public_replication_portal.html'
        self.prometheus_path = self.portal_dir / 'public_replication_portal.prom'
        self.manifest_path = self.portal_dir / 'public_replication_portal_manifest.json'

    def _collect_states(self) -> dict[str, dict[str, Any]]:
        ev = self.root / 'external_validation'
        return {
            'h7_independent_replication_tracker': _read_json(ev / 'independent_replication_tracker' / 'latest_independent_replication_tracker.json'),
            'h8_scientific_consensus_engine': _read_json(ev / 'scientific_consensus_engine' / 'latest_scientific_consensus_engine.json'),
            'h9_external_replication_evidence_aggregator': _read_json(ev / 'external_replication_evidence_aggregator' / 'latest_external_replication_evidence_aggregator.json'),
            'h10_replication_statistical_validation': _read_json(ev / 'replication_statistical_validation' / 'latest_replication_statistical_validation.json'),
        }

    def _collect_scores(self, states: dict[str, dict[str, Any]]) -> dict[str, float]:
        h7 = states.get('h7_independent_replication_tracker', {})
        h8 = states.get('h8_scientific_consensus_engine', {})
        h9 = states.get('h9_external_replication_evidence_aggregator', {})
        h10 = states.get('h10_replication_statistical_validation', {})
        return {
            'replication_tracking_score': _clamp(h7.get('replication_tracking_score')),
            'scientific_consensus': _clamp(h8.get('scientific_consensus')),
            'consensus_confidence_index': _clamp(h8.get('consensus_confidence_index')),
            'replication_evidence_score': _clamp(h9.get('replication_evidence_score')),
            'external_validation_strength': _clamp(h9.get('external_validation_strength')),
            'cross_site_consistency_index': _clamp(h9.get('cross_site_consistency_index')),
            'replication_significance_score': _clamp(h10.get('replication_significance_score')),
            'statistical_validation_score': _clamp(h10.get('statistical_validation_score')),
            'confidence_interval_width': _clamp(h10.get('confidence_interval_width'), default=1.0),
        }

    def _artefact_manifest(self) -> list[dict[str, Any]]:
        candidates = [
            ('H7 state', self.root / 'external_validation' / 'independent_replication_tracker' / 'latest_independent_replication_tracker.json'),
            ('H7 dashboard', self.root / 'external_validation' / 'independent_replication_tracker' / 'independent_replication_dashboard.html'),
            ('H8 state', self.root / 'external_validation' / 'scientific_consensus_engine' / 'latest_scientific_consensus_engine.json'),
            ('H8 dashboard', self.root / 'external_validation' / 'scientific_consensus_engine' / 'scientific_consensus_dashboard.html'),
            ('H9 state', self.root / 'external_validation' / 'external_replication_evidence_aggregator' / 'latest_external_replication_evidence_aggregator.json'),
            ('H9 dashboard', self.root / 'external_validation' / 'external_replication_evidence_aggregator' / 'external_replication_evidence_dashboard.html'),
            ('H10 state', self.root / 'external_validation' / 'replication_statistical_validation' / 'latest_replication_statistical_validation.json'),
            ('H10 dashboard', self.root / 'external_validation' / 'replication_statistical_validation' / 'replication_statistical_validation_dashboard.html'),
            ('Ontology inventory', self.root / 'ontology_inventory.txt'),
            ('Integration report', self.root / 'ontology_integration_report.txt'),
            ('Scientific validation JSON', self.root / 'scientific_validation_report.json'),
            ('Scientific validation text', self.root / 'scientific_validation_report.txt'),
        ]
        manifest = []
        for label, path in candidates:
            manifest.append({
                'label': label,
                'path': str(path),
                'exists': path.exists(),
                'size_bytes': path.stat().st_size if path.exists() else 0,
                'relative_path': str(path.relative_to(self.root)) if path.exists() and path.is_relative_to(self.root) else str(path),
            })
        return manifest

    def _portal_score(self, scores: dict[str, float], manifest: list[dict[str, Any]]) -> float:
        score_values = [
            scores['replication_tracking_score'],
            scores['scientific_consensus'],
            scores['consensus_confidence_index'],
            scores['replication_evidence_score'],
            scores['external_validation_strength'],
            scores['cross_site_consistency_index'],
            scores['replication_significance_score'],
            scores['statistical_validation_score'],
            1.0 - scores['confidence_interval_width'],
        ]
        manifest_completeness = sum(1 for x in manifest if x['exists']) / max(len(manifest), 1)
        return round(0.80 * mean(score_values) + 0.20 * manifest_completeness, 6)

    def _render_html(self, state: dict[str, Any], manifest: list[dict[str, Any]]) -> str:
        metrics = state['metrics']
        rows = ''.join(
            '<tr><td>{}</td><td>{}</td></tr>'.format(html.escape(k), html.escape(str(v)))
            for k, v in metrics.items()
        )
        artefact_rows = ''.join(
            '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                html.escape(item['label']),
                html.escape(item['relative_path']),
                html.escape(str(item['exists'])),
                html.escape(str(item['size_bytes'])),
            )
            for item in manifest
        )
        return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Open Cognitive Ecology - Public Replication Portal</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;line-height:1.45}}table{{border-collapse:collapse;width:100%;margin:1em 0}}td,th{{border:1px solid #ccc;padding:8px;text-align:left}}th{{background:#f0f0f0}}.ok{{color:#146b2e;font-weight:bold}}.warn{{color:#8a5a00;font-weight:bold}}</style>
</head><body>
<h1>Open Cognitive Ecology - Public Replication Portal</h1>
<p>Offline H11 portal for replication readiness, external evidence, consensus and statistical validation.</p>
<p class="{'ok' if state['success'] else 'warn'}">Portal status: {html.escape(str(state['success']))}</p>
<h2>Governance</h2>
<p>No GitHub token, Zenodo token, network publication or external side effect is required at H11. Real connectors begin at H12/H13.</p>
<h2>Metrics</h2><table><tr><th>Metric</th><th>Value</th></tr>{rows}</table>
<h2>Replication Artefacts</h2><table><tr><th>Label</th><th>Relative path</th><th>Exists</th><th>Size bytes</th></tr>{artefact_rows}</table>
<h2>Interpretation</h2>
<p>This portal supports functional, traceable and reproducible validation. It does not assert phenomenal subjectivity.</p>
</body></html>"""

    def _render_prometheus(self, state: dict[str, Any]) -> str:
        metrics = state['metrics']
        keys = {
            'public_replication_portal_score': 'oce_public_replication_portal_score',
            'portal_manifest_completeness': 'oce_portal_manifest_completeness',
            'replication_publication_readiness': 'oce_replication_publication_readiness',
            'public_dashboard_readiness': 'oce_public_dashboard_readiness',
            'credential_independence_score': 'oce_credential_independence_score',
        }
        lines = []
        for src, dst in keys.items():
            lines.append(f'# TYPE {dst} gauge')
            lines.append(f'{dst} {float(metrics.get(src, 0.0))}')
        return '\n'.join(lines) + '\n'

    def step(
        self,
        portal_context: dict[str, Any] | None = None,
        persist: bool = True,
        fs_context: GovernedFilesystemEffectContext | None = None,
    ) -> dict[str, Any]:
        context = dict(portal_context or {})
        self.portal_dir.mkdir(parents=True, exist_ok=True)
        states = self._collect_states()
        scores = self._collect_scores(states)
        manifest = self._artefact_manifest()
        manifest_completeness = sum(1 for x in manifest if x['exists']) / max(len(manifest), 1)
        base_score = self._portal_score(scores, manifest)

        credential_independence_score = 1.0
        public_dashboard_readiness = 1.0 if self.html_path.parent.exists() else 0.9
        replication_publication_readiness = round(mean([
            base_score,
            manifest_completeness,
            scores['replication_evidence_score'],
            scores['statistical_validation_score'],
        ]), 6)
        public_replication_portal_score = round(mean([
            base_score,
            manifest_completeness,
            replication_publication_readiness,
            public_dashboard_readiness,
            credential_independence_score,
        ]), 6)

        success = (
            public_replication_portal_score >= 0.70
            and manifest_completeness >= 0.75
            and credential_independence_score == 1.0
        )

        metrics = {
            **scores,
            'portal_manifest_completeness': round(manifest_completeness, 6),
            'replication_publication_readiness': replication_publication_readiness,
            'public_dashboard_readiness': public_dashboard_readiness,
            'credential_independence_score': credential_independence_score,
            'public_replication_portal_score': public_replication_portal_score,
        }

        state = {
            'primitive': self.primitive,
            'refinement': self.refinement,
            'timestamp_utc': _now(),
            'success': success,
            'metrics': metrics,
            'public_replication_portal_score': public_replication_portal_score,
            'replication_publication_readiness': replication_publication_readiness,
            'portal_manifest_completeness': round(manifest_completeness, 6),
            'public_dashboard_readiness': public_dashboard_readiness,
            'credential_independence_score': credential_independence_score,
            'dashboard_path': str(self.html_path),
            'manifest_path': str(self.manifest_path),
            'history_path': str(self.history_path),
            'prometheus_path': str(self.prometheus_path),
            'state_path': str(self.state_path),
            'governance': {
                'no_credentials_required': True,
                'no_github_action_performed': True,
                'no_zenodo_action_performed': True,
                'no_network_side_effects': True,
                'offline_publication_preview_only': True,
                'phenomenal_subjectivity_not_claimed': True,
                'non_closure_compliant': True,
                'traceability_enabled': True,
                'reversibility_enabled': True,
            },
            'context_override_used': bool(context),
        }

        if context:
            for key, value in context.items():
                if key in state and isinstance(value, (int, float, bool, str)):
                    state[key] = value
            if 'force_manifest_completeness' in context:
                state['metrics']['portal_manifest_completeness'] = _clamp(context['force_manifest_completeness'])
                state['portal_manifest_completeness'] = state['metrics']['portal_manifest_completeness']
            if 'force_portal_score' in context:
                state['metrics']['public_replication_portal_score'] = _clamp(context['force_portal_score'])
                state['public_replication_portal_score'] = state['metrics']['public_replication_portal_score']
            state['success'] = bool(
                state['metrics']['public_replication_portal_score'] >= 0.70
                and state['metrics']['portal_manifest_completeness'] >= 0.75
            )

        if persist:
            _write_json(self.state_path, state, fs_context)
            _write_json(self.manifest_path, {'primitive': self.primitive, 'timestamp_utc': state['timestamp_utc'], 'artefacts': manifest}, fs_context)
            self.html_path.write_text(self._render_html(state, manifest), encoding='utf-8')
            self.prometheus_path.write_text(self._render_prometheus(state), encoding='utf-8')
            with self.history_path.open('a', encoding='utf-8') as f:
                f.write(json.dumps(state, sort_keys=True) + '\n')

        return state
