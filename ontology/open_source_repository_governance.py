from __future__ import annotations

import html
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class RepositoryGovernanceWeights:
    remote_configuration: float = 0.14
    branch_release_traceability: float = 0.16
    documentation_completeness: float = 0.18
    ci_and_quality: float = 0.14
    collaboration_readiness: float = 0.14
    reproducibility_readiness: float = 0.14
    non_closure_governance: float = 0.10


class OpenSourceRepositoryGovernance:
    """H0.1-R2: local governance assessment for the open-source repository.

    The primitive measures whether the local Git/GitHub repository is ready to
    support public scientific replication. It is deliberately non-invasive: no
    network calls, no push, no release creation, and no repository mutation.
    """

    primitive = 'open_source_repository_governance'
    refinement = 'H0.1-R2'

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root).expanduser() if root else Path.home() / 'open-cognitive-ecology'
        self.output_dir = self.root / 'external_validation' / 'open_source_repository_governance'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.weights = RepositoryGovernanceWeights()

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _ratio(count: int, target: int) -> float:
        return 1.0 if target <= 0 else max(0.0, min(1.0, count / target))

    def _run_git(self, *args: str) -> str:
        try:
            result = subprocess.run(
                ['git', *args],
                cwd=self.root,
                text=True,
                capture_output=True,
                check=False,
                timeout=8,
            )
        except Exception:
            return ''
        return result.stdout.strip() if result.returncode == 0 else ''

    def _count_existing(self, paths: Iterable[str]) -> int:
        return sum(1 for p in paths if (self.root / p).exists())

    def _read_text(self, path: str, limit: int = 200_000) -> str:
        p = self.root / path
        if not p.exists() or not p.is_file():
            return ''
        try:
            return p.read_text(encoding='utf-8', errors='replace')[:limit]
        except Exception:
            return ''

    def _git_status_counts(self) -> dict[str, int]:
        status = self._run_git('status', '--short')
        counts = {'modified': 0, 'deleted': 0, 'untracked': 0, 'other': 0, 'total': 0}
        for line in status.splitlines():
            if not line.strip():
                continue
            counts['total'] += 1
            code = line[:2]
            if 'D' in code:
                counts['deleted'] += 1
            elif 'M' in code:
                counts['modified'] += 1
            elif code == '??':
                counts['untracked'] += 1
            else:
                counts['other'] += 1
        return counts

    def _collect_repository_state(self) -> dict[str, Any]:
        remotes_raw = self._run_git('remote', '-v')
        branches_raw = self._run_git('branch', '-a')
        tags_raw = self._run_git('tag', '--list')
        log_raw = self._run_git('log', '--oneline', '-20')
        current_branch = self._run_git('branch', '--show-current')
        workflow_root = self.root / '.github' / 'workflows'
        issue_root = self.root / '.github' / 'ISSUE_TEMPLATE'
        workflow_files = sorted(str(p.relative_to(self.root)) for p in workflow_root.glob('*') if p.is_file()) if workflow_root.exists() else []
        issue_templates = sorted(str(p.relative_to(self.root)) for p in issue_root.glob('*') if p.is_file()) if issue_root.exists() else []
        return {
            'current_branch': current_branch,
            'remote_lines': [line for line in remotes_raw.splitlines() if line.strip()],
            'branch_lines': [line.strip() for line in branches_raw.splitlines() if line.strip()],
            'tag_lines': [line.strip() for line in tags_raw.splitlines() if line.strip()],
            'recent_commits': [line.strip() for line in log_raw.splitlines() if line.strip()],
            'workflow_files': workflow_files,
            'issue_templates': issue_templates,
            'status_counts': self._git_status_counts(),
        }

    def _apply_repository_context(self, state: dict[str, Any], repository_context: dict[str, Any] | None) -> dict[str, Any]:
        if not repository_context:
            return state
        degraded = json.loads(json.dumps(state))
        if repository_context.get('has_git_repository') is False:
            degraded.update({'current_branch': '', 'branch_lines': [], 'tag_lines': [], 'recent_commits': [], 'remote_lines': []})
        if repository_context.get('has_remote_origin') is False:
            degraded['remote_lines'] = [line for line in degraded['remote_lines'] if 'origin' not in line.lower()]
        if repository_context.get('has_public_remote') is False:
            degraded['remote_lines'] = [line for line in degraded['remote_lines'] if 'public' not in line.lower() and 'open-cognitive-ecology-public' not in line.lower()]
        if repository_context.get('has_tags') is False:
            degraded['tag_lines'] = []
        if repository_context.get('has_ci') is False:
            degraded['workflow_files'] = []
        if repository_context.get('has_docs') is False:
            degraded['_force_documentation_absent'] = True
            degraded['_force_reproducibility_docs_absent'] = True
        if repository_context.get('has_collaboration_templates') is False:
            degraded['issue_templates'] = []
            degraded['_force_collaboration_templates_absent'] = True
        return degraded

    def _score_remote_configuration(self, state: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        remotes = '\n'.join(state['remote_lines']).lower()
        has_origin = 'origin' in remotes
        has_public = 'public' in remotes or 'open-cognitive-ecology-public' in remotes
        has_github = 'github.com' in remotes
        score = 0.40 * has_origin + 0.35 * has_public + 0.25 * has_github
        return self._clamp(score), {'has_origin': has_origin, 'has_public_remote': has_public, 'has_github_remote': has_github}

    def _score_branch_release_traceability(self, state: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        branches = '\n'.join(state['branch_lines']).lower()
        tags = state['tag_lines']
        commits = state['recent_commits']
        has_main = 'main' in branches
        has_development = any(name in branches for name in ('development', 'development-clean', 'cognitive-runtime'))
        tag_score = self._ratio(len(tags), 10)
        history_score = self._ratio(len(commits), 20)
        score = 0.25 * has_main + 0.25 * has_development + 0.30 * tag_score + 0.20 * history_score
        return self._clamp(score), {'has_main_branch': has_main, 'has_development_branch': has_development, 'tag_count': len(tags), 'recent_commit_count': len(commits)}

    def _score_documentation(self, state: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        doc_paths = ['README.md', 'docs/index.md', 'docs/architecture.md', 'docs/architecture_summary.md', 'docs/roadmap.md', 'docs/validation_guide.md', 'docs/coding_conventions.md', 'docs/ontology_organization_inventory.md', 'docs/primitives_by_level.md']
        if state.get('_force_documentation_absent'):
            existing = 0
            has_validation_language = False
        else:
            existing = self._count_existing(doc_paths)
            readme = self._read_text('README.md').lower()
            has_validation_language = any(term in readme for term in ('validation', 'replication', 'reproduc', 'scientific'))
        completeness = self._ratio(existing, len(doc_paths))
        score = 0.80 * completeness + 0.20 * has_validation_language
        return self._clamp(score), {'documentation_files_expected': len(doc_paths), 'documentation_files_present': existing, 'has_validation_language': has_validation_language}

    def _score_ci_and_quality(self, state: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        workflows = state['workflow_files']
        workflow_text = '\n'.join(self._read_text(p) for p in workflows).lower()
        has_workflow = bool(workflows)
        mentions_validation = 'validation.main' in workflow_text or 'pytest' in workflow_text or 'python -m validation' in workflow_text
        has_dependabot = (self.root / '.github' / 'dependabot.yml').exists() or (self.root / '.github' / 'dependabot.yaml').exists()
        if not has_workflow:
            has_dependabot = False
        score = 0.45 * has_workflow + 0.35 * mentions_validation + 0.20 * has_dependabot
        return self._clamp(score), {'workflow_count': len(workflows), 'mentions_validation': mentions_validation, 'has_dependabot': has_dependabot}

    def _score_collaboration(self, state: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        files = ['CONTRIBUTING.md', 'CODE_OF_CONDUCT.md', 'SECURITY.md', '.github/pull_request_template.md']
        existing = 0 if state.get('_force_collaboration_templates_absent') else self._count_existing(files)
        issue_template_count = 0 if state.get('_force_collaboration_templates_absent') else len(state['issue_templates'])
        base = self._ratio(existing, len(files))
        issue_score = self._ratio(issue_template_count, 2)
        score = 0.65 * base + 0.35 * issue_score
        return self._clamp(score), {'collaboration_files_present': existing, 'issue_template_count': issue_template_count}

    def _score_reproducibility(self, state: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        files = ['requirements.txt', 'pyproject.toml', 'setup.py', 'setup.cfg', 'README.md', 'docs/validation_guide.md']
        existing = 0 if state.get('_force_reproducibility_docs_absent') else self._count_existing(files)
        has_validation_guide = False if state.get('_force_reproducibility_docs_absent') else (self.root / 'docs' / 'validation_guide.md').exists()
        score = 0.75 * self._ratio(existing, len(files)) + 0.25 * has_validation_guide
        return self._clamp(score), {'reproducibility_files_present': existing, 'has_validation_guide': has_validation_guide}

    def _score_non_closure(self) -> tuple[float, dict[str, Any]]:
        readme = self._read_text('README.md').lower()
        docs = (self._read_text('docs/architecture.md') + '\n' + self._read_text('docs/roadmap.md')).lower()
        text = readme + '\n' + docs
        terms = ['non-closure', 'non_closure', 'open-ended', 'replication', 'external validation', 'reversibility', 'traceability']
        matches = sum(1 for term in terms if term in text)
        score = self._ratio(matches, 5)
        return self._clamp(score), {'non_closure_terms_matched': matches, 'terms_checked': terms}

    def _compose_scores(self, state: dict[str, Any]) -> tuple[dict[str, float], dict[str, Any]]:
        score_funcs = {
            'remote_configuration': self._score_remote_configuration,
            'branch_release_traceability': self._score_branch_release_traceability,
            'documentation_completeness': self._score_documentation,
            'ci_and_quality': self._score_ci_and_quality,
            'collaboration_readiness': self._score_collaboration,
            'reproducibility_readiness': self._score_reproducibility,
            'non_closure_governance': lambda s: self._score_non_closure(),
        }
        scores: dict[str, float] = {}
        details: dict[str, Any] = {}
        for name, func in score_funcs.items():
            score, detail = func(state)
            scores[name] = round(self._clamp(score), 4)
            details[name] = detail
        return scores, details

    def _weighted_score(self, scores: dict[str, float]) -> float:
        weights = self.weights
        total = (
            scores['remote_configuration'] * weights.remote_configuration
            + scores['branch_release_traceability'] * weights.branch_release_traceability
            + scores['documentation_completeness'] * weights.documentation_completeness
            + scores['ci_and_quality'] * weights.ci_and_quality
            + scores['collaboration_readiness'] * weights.collaboration_readiness
            + scores['reproducibility_readiness'] * weights.reproducibility_readiness
            + scores['non_closure_governance'] * weights.non_closure_governance
        )
        return round(self._clamp(total), 4)

    def _write_json(self, result: dict[str, Any]) -> Path:
        path = self.output_dir / 'latest_open_source_repository_governance.json'
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        history = self.output_dir / 'open_source_repository_governance_history.jsonl'
        with history.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + '\n')
        return path

    def _write_prometheus(self, result: dict[str, Any]) -> Path:
        path = self.output_dir / 'open_source_repository_governance.prom'
        lines = [
            '# HELP oce_repository_governance_score Repository governance score for external validation readiness.',
            '# TYPE oce_repository_governance_score gauge',
            f'oce_repository_governance_score {result["repository_governance_score"]}',
            '# HELP oce_github_governance_score GitHub governance score.',
            '# TYPE oce_github_governance_score gauge',
            f'oce_github_governance_score {result["github_governance_score"]}',
            '# HELP oce_replication_readiness_score Replication readiness score.',
            '# TYPE oce_replication_readiness_score gauge',
            f'oce_replication_readiness_score {result["replication_readiness_score"]}',
            '# HELP oce_external_validation_readiness External validation readiness score.',
            '# TYPE oce_external_validation_readiness gauge',
            f'oce_external_validation_readiness {result["external_validation_readiness"]}',
        ]
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return path

    def _write_html_dashboard(self, result: dict[str, Any]) -> Path:
        path = self.output_dir / 'open_source_repository_governance_dashboard.html'
        rows = []
        for key, value in result['component_scores'].items():
            rows.append(f'<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>')
        html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Open Source Repository Governance</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;}}table{{border-collapse:collapse;width:100%;}}td,th{{border:1px solid #ccc;padding:8px;text-align:left;}}th{{background:#f2f2f2;}}</style>
</head><body>
<h1>Open Source Repository Governance</h1>
<p>Generated at: {html.escape(result['timestamp_utc'])}</p>
<table><tr><th>Metric</th><th>Value</th></tr>
<tr><td>repository_governance_score</td><td>{result['repository_governance_score']}</td></tr>
<tr><td>github_governance_score</td><td>{result['github_governance_score']}</td></tr>
<tr><td>replication_readiness_score</td><td>{result['replication_readiness_score']}</td></tr>
<tr><td>external_validation_readiness</td><td>{result['external_validation_readiness']}</td></tr>
</table>
<h2>Component Scores</h2><table><tr><th>Component</th><th>Score</th></tr>{''.join(rows)}</table>
</body></html>"""
        path.write_text(html_doc, encoding='utf-8')
        return path

    def step(self, repository_context: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        raw_state = self._collect_repository_state()
        state = self._apply_repository_context(raw_state, repository_context)
        component_scores, component_details = self._compose_scores(state)
        repository_governance_score = self._weighted_score(component_scores)
        github_governance_score = round(self._clamp((component_scores['remote_configuration'] + component_scores['ci_and_quality'] + component_scores['collaboration_readiness']) / 3), 4)
        replication_readiness_score = round(self._clamp((component_scores['documentation_completeness'] + component_scores['reproducibility_readiness'] + component_scores['branch_release_traceability']) / 3), 4)
        external_validation_readiness = round(self._clamp((repository_governance_score + github_governance_score + replication_readiness_score + component_scores['non_closure_governance']) / 4), 4)
        success = repository_governance_score >= 0.5
        result: dict[str, Any] = {
            'primitive': self.primitive,
            'refinement': self.refinement,
            'timestamp_utc': self._utc_now(),
            'success': success,
            'repository_governance_score': repository_governance_score,
            'github_governance_score': github_governance_score,
            'replication_readiness_score': replication_readiness_score,
            'external_validation_readiness': external_validation_readiness,
            'component_scores': component_scores,
            'component_details': component_details,
            'repository_state_summary': {
                'current_branch': state.get('current_branch', ''),
                'remote_count': len(state.get('remote_lines', [])),
                'branch_count': len(state.get('branch_lines', [])),
                'tag_count': len(state.get('tag_lines', [])),
                'workflow_count': len(state.get('workflow_files', [])),
                'issue_template_count': len(state.get('issue_templates', [])),
                'status_counts': state.get('status_counts', {}),
            },
            'governance': {
                'no_network_side_effects': True,
                'read_only_git_inspection': True,
                'html_dashboard_export_enabled': True,
                'prometheus_export_enabled': True,
                'traceability_enabled': True,
                'non_closure_compliant': True,
            },
            'diagnostics': {
                'repository_context_override_used': repository_context is not None,
                'persist_requested': persist,
                'closure_pressure_increase': 0.0,
                'warnings': [],
            },
        }
        if persist:
            result['state_path'] = str(self._write_json(result))
            result['prometheus_path'] = str(self._write_prometheus(result))
            result['dashboard_path'] = str(self._write_html_dashboard(result))
        else:
            result['state_path'] = None
            result['prometheus_path'] = None
            result['dashboard_path'] = None
        return result


if __name__ == '__main__':
    print(json.dumps(OpenSourceRepositoryGovernance().step(), ensure_ascii=False, indent=2))
