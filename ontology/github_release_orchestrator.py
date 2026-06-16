from __future__ import annotations

import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class GitHubReleaseOrchestrator:
    """H2 GitHub release orchestrator.

    Prepares and evaluates a governed GitHub release plan for the public
    Open Cognitive Ecology repository without network side effects, pushes,
    or remote mutations. It links Git state, validation outputs, publication
    registry evidence, and future Zenodo handoff readiness.
    """

    primitive = "github_release_orchestrator"
    refinement = "H2-R1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "external_validation" / "github_release_orchestrator"

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _safe_read(self, path: Path, limit: int = 2_000_000) -> str:
        try:
            if path.exists() and path.is_file():
                return path.read_text(encoding="utf-8", errors="ignore")[:limit]
        except Exception:
            return ""
        return ""

    def _run_git(self, args: List[str], timeout: int = 4) -> str:
        try:
            return subprocess.run(["git"] + args, cwd=str(self.root), text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout).stdout.strip()
        except Exception:
            return ""

    def _count_files(self, base: Path, patterns: List[str]) -> int:
        if not base.exists():
            return 0
        total = 0
        for pattern in patterns:
            try:
                total += len([p for p in base.rglob(pattern) if p.is_file()])
            except Exception:
                pass
        return total

    def _list_files(self, base: Path, patterns: List[str], limit: int = 100) -> List[str]:
        out: List[str] = []
        if not base.exists():
            return out
        for pattern in patterns:
            try:
                for p in base.rglob(pattern):
                    if p.is_file():
                        try:
                            out.append(str(p.relative_to(self.root)))
                        except Exception:
                            out.append(str(p))
            except Exception:
                pass
        return sorted(set(out))[:limit]

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _derive_context(self) -> Dict[str, Any]:
        git_tags_text = self._safe_read(self.root / "git_tags.txt") or self._run_git(["tag", "-l"])
        git_branches_text = self._safe_read(self.root / "git_branches.txt") or self._run_git(["branch", "-a"])
        git_log_text = self._safe_read(self.root / "git_log_120.txt") or self._run_git(["log", "--decorate", "--oneline", "-120"])
        git_remotes_text = self._safe_read(self.root / "git_remotes.txt") or self._run_git(["remote", "-v"])
        git_status_text = self._safe_read(self.root / "git_status_short.txt") or self._run_git(["status", "--short"])

        tags = [x.strip() for x in git_tags_text.splitlines() if x.strip()]
        release_tags = [x for x in tags if x.startswith("v")]
        branches = [x.strip() for x in git_branches_text.splitlines() if x.strip()]
        public_remote_present = "open-cognitive-ecology-public" in git_remotes_text or "public" in git_remotes_text
        private_remote_present = "open-cognitive-ecology.git" in git_remotes_text or "origin" in git_remotes_text
        github_remote_present = "github.com" in git_remotes_text
        public_repo_name = "open-cognitive-ecology-public" if "open-cognitive-ecology-public" in git_remotes_text else ""
        current_branch = self._run_git(["branch", "--show-current"])
        head_commit = self._run_git(["rev-parse", "--short", "HEAD"])

        workflow_files = self._list_files(self.root / ".github", ["*.yml", "*.yaml"], limit=50)
        release_related_files = self._list_files(self.root, ["*release*", "*publication*", "*zenodo*", "*artifact*", "*deploy*"], limit=150)
        docs_files = self._list_files(self.root / "docs", ["*.md", "*.txt", "*.html"], limit=150)
        external_validation_files = self._list_files(self.root / "external_validation", ["*.json", "*.jsonl", "*.prom", "*.html"], limit=300)
        publication_archive_files = self._list_files(self.root / "publication_archive", ["*.json", "*.jsonl", "*.md", "*.txt", "*.html", "*.pdf"], limit=150)

        readme_text = self._safe_read(self.root / "README.md")
        changelog_text = self._safe_read(self.root / "CHANGELOG.md")
        release_notes_text = self._safe_read(self.root / "RELEASE_NOTES.md")
        validation_report_text = self._safe_read(self.root / "ontology_integration_report.txt")
        combined = "\n".join([readme_text, changelog_text, release_notes_text, validation_report_text, git_log_text])

        h_states = {
            "h0_1": self.root / "external_validation" / "open_source_repository_governance" / "latest_open_source_repository_governance.json",
            "h0_2": self.root / "external_validation" / "open_source_replication_readiness" / "latest_open_source_replication_readiness.json",
            "h0_3": self.root / "external_validation" / "scientific_publication_traceability" / "latest_scientific_publication_traceability.json",
            "h0_4": self.root / "external_validation" / "external_validation_dashboard" / "latest_external_validation_dashboard.json",
            "h1": self.root / "external_validation" / "scientific_publication_registry" / "latest_scientific_publication_registry.json",
        }
        validated_upstream_count = 0
        upstream_scores: Dict[str, float] = {}
        for key, path in h_states.items():
            data = self._load_json(path)
            if data.get("success") is True:
                validated_upstream_count += 1
            for score_key in [
                "repository_governance_score",
                "replication_readiness_score",
                "publication_traceability_score",
                "external_validation_composite_index",
                "publication_registry_completeness_score",
            ]:
                if score_key in data:
                    try:
                        upstream_scores[f"{key}_{score_key}"] = float(data[score_key])
                    except Exception:
                        pass

        status_lines = [x for x in git_status_text.splitlines() if x.strip()]
        status_total = len(status_lines)
        status_deleted = len([x for x in status_lines if x.strip().startswith("D")])
        status_modified = len([x for x in status_lines if x.strip().startswith("M")])
        status_untracked = len([x for x in status_lines if x.strip().startswith("??")])

        release_commit_count = len([x for x in git_log_text.splitlines() if any(k in x.lower() for k in ["release", "tag", "publication", "zenodo", "dashboard", "validation", "report"])])
        latest_release_tag = release_tags[-1] if release_tags else ""
        recommended_tag = latest_release_tag or "v1.0-public-replication"
        if latest_release_tag and "public" not in latest_release_tag:
            recommended_public_tag = latest_release_tag + "-public"
        else:
            recommended_public_tag = recommended_tag

        return {
            "has_git_repository": (self.root / ".git").exists() or bool(head_commit),
            "head_commit": head_commit,
            "current_branch": current_branch,
            "has_github_remote": github_remote_present,
            "has_private_remote": private_remote_present,
            "has_public_remote": public_remote_present,
            "public_repo_name": public_repo_name,
            "tag_count": len(tags),
            "release_tag_count": len(release_tags),
            "latest_release_tag": latest_release_tag,
            "recommended_public_release_tag": recommended_public_tag,
            "branch_count": len(branches),
            "workflow_count": len(workflow_files),
            "workflow_files": workflow_files,
            "has_ci": any("ci" in p.lower() or "test" in p.lower() for p in workflow_files),
            "has_release_workflow": any("release" in p.lower() or "publish" in p.lower() for p in workflow_files) or "release" in combined.lower(),
            "has_readme": (self.root / "README.md").exists(),
            "has_changelog": (self.root / "CHANGELOG.md").exists(),
            "has_release_notes": (self.root / "RELEASE_NOTES.md").exists(),
            "release_related_file_count": len(release_related_files),
            "release_related_files_sample": release_related_files[:40],
            "docs_file_count": len(docs_files),
            "external_validation_file_count": len(external_validation_files),
            "publication_archive_file_count": len(publication_archive_files),
            "validated_upstream_count": validated_upstream_count,
            "upstream_scores": upstream_scores,
            "mentions_release": "release" in combined.lower(),
            "mentions_zenodo": "zenodo" in combined.lower(),
            "mentions_validation": "validation" in combined.lower(),
            "mentions_replication": "replication" in combined.lower(),
            "release_commit_count": release_commit_count,
            "working_tree_status_total": status_total,
            "working_tree_status_deleted": status_deleted,
            "working_tree_status_modified": status_modified,
            "working_tree_status_untracked": status_untracked,
            "public_github_tags_visible_count": 0 if public_remote_present else None,
            "public_release_action_required": True,
        }

    def _score(self, ctx: Dict[str, Any]) -> Dict[str, float]:
        repository_release_basis = min(1.0,
            (0.20 if ctx.get("has_git_repository") else 0.0) +
            (0.15 if ctx.get("has_github_remote") else 0.0) +
            (0.20 if ctx.get("has_public_remote") else 0.0) +
            min(0.20, float(ctx.get("release_tag_count", 0)) / 10.0 * 0.20) +
            min(0.15, float(ctx.get("branch_count", 0)) / 5.0 * 0.15) +
            (0.10 if ctx.get("head_commit") else 0.0)
        )
        release_documentation_score = min(1.0,
            (0.20 if ctx.get("has_readme") else 0.0) +
            (0.20 if ctx.get("has_changelog") else 0.0) +
            (0.20 if ctx.get("has_release_notes") else 0.0) +
            min(0.20, float(ctx.get("docs_file_count", 0)) / 10.0 * 0.20) +
            (0.10 if ctx.get("mentions_release") else 0.0) +
            (0.10 if ctx.get("mentions_validation") else 0.0)
        )
        validation_artifact_score = min(1.0,
            min(0.25, float(ctx.get("external_validation_file_count", 0)) / 30.0 * 0.25) +
            min(0.25, float(ctx.get("publication_archive_file_count", 0)) / 20.0 * 0.25) +
            min(0.35, float(ctx.get("validated_upstream_count", 0)) / 5.0 * 0.35) +
            (0.15 if ctx.get("mentions_replication") or ctx.get("mentions_zenodo") else 0.0)
        )
        automation_preparedness_score = min(1.0,
            min(0.25, float(ctx.get("workflow_count", 0)) / 4.0 * 0.25) +
            (0.20 if ctx.get("has_ci") else 0.0) +
            (0.15 if ctx.get("has_release_workflow") else 0.0) +
            min(0.25, float(ctx.get("release_related_file_count", 0)) / 30.0 * 0.25) +
            min(0.15, float(ctx.get("release_commit_count", 0)) / 10.0 * 0.15)
        )
        clean_release_risk_score = max(0.0, min(1.0,
            1.0 - min(0.60, float(ctx.get("working_tree_status_total", 0)) / 5000.0 * 0.60)
                  - min(0.25, float(ctx.get("working_tree_status_deleted", 0)) / 4000.0 * 0.25)
                  - min(0.10, float(ctx.get("working_tree_status_untracked", 0)) / 1000.0 * 0.10)
        ))
        github_release_orchestration_score = round(
            0.24 * repository_release_basis +
            0.18 * release_documentation_score +
            0.24 * validation_artifact_score +
            0.20 * automation_preparedness_score +
            0.14 * clean_release_risk_score,
            6,
        )
        release_readiness_index = round(min(1.0, github_release_orchestration_score * 0.88 + validation_artifact_score * 0.12), 6)
        zenodo_handoff_readiness = round(min(1.0, 0.45 * validation_artifact_score + 0.35 * release_documentation_score + 0.20 * repository_release_basis), 6)
        return {
            "repository_release_basis_score": round(repository_release_basis, 6),
            "release_documentation_score": round(release_documentation_score, 6),
            "validation_artifact_score": round(validation_artifact_score, 6),
            "automation_preparedness_score": round(automation_preparedness_score, 6),
            "clean_release_risk_score": round(clean_release_risk_score, 6),
            "github_release_orchestration_score": github_release_orchestration_score,
            "release_readiness_index": release_readiness_index,
            "zenodo_handoff_readiness": zenodo_handoff_readiness,
        }

    def _build_release_manifest(self, ctx: Dict[str, Any], scores: Dict[str, float]) -> Dict[str, Any]:
        return {
            "release_tag": ctx.get("recommended_public_release_tag") or "v1.0-public-replication",
            "source_branch": ctx.get("current_branch") or "main",
            "head_commit": ctx.get("head_commit") or "unknown",
            "public_repository": ctx.get("public_repo_name") or "open-cognitive-ecology-public",
            "release_title": "Open Cognitive Ecology public replication release",
            "release_mode": "prepared_no_network_side_effects",
            "publish_actions_required": [
                "review working tree cleanliness",
                "create or confirm public release tag",
                "generate GitHub Release from prepared manifest",
                "attach replication and validation artifacts",
                "handoff release metadata to Zenodo orchestrator",
            ],
            "artifact_groups": {
                "external_validation": int(ctx.get("external_validation_file_count", 0)),
                "publication_archive": int(ctx.get("publication_archive_file_count", 0)),
                "release_related": int(ctx.get("release_related_file_count", 0)),
                "documentation": int(ctx.get("docs_file_count", 0)),
            },
            "scores": scores,
        }

    def _write_outputs(self, result: Dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        state_path = self.output_dir / "latest_github_release_orchestrator.json"
        history_path = self.output_dir / "github_release_orchestrator_history.jsonl"
        prom_path = self.output_dir / "github_release_orchestrator.prom"
        html_path = self.output_dir / "github_release_orchestrator_dashboard.html"
        manifest_path = self.output_dir / "github_release_manifest.json"
        state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")
        manifest_path.write_text(json.dumps(result.get("release_manifest", {}), indent=2, ensure_ascii=False), encoding="utf-8")
        scores = result.get("component_scores", {})
        prom_lines = [
            "# TYPE oce_github_release_orchestration_score gauge",
            f"oce_github_release_orchestration_score {result['github_release_orchestration_score']:.6f}",
            "# TYPE oce_github_release_readiness_index gauge",
            f"oce_github_release_readiness_index {result['release_readiness_index']:.6f}",
            "# TYPE oce_zenodo_handoff_readiness gauge",
            f"oce_zenodo_handoff_readiness {result['zenodo_handoff_readiness']:.6f}",
        ]
        for key, value in scores.items():
            prom_lines.append(f"# TYPE oce_{key} gauge")
            prom_lines.append(f"oce_{key} {float(value):.6f}")
        prom_path.write_text("\n".join(prom_lines) + "\n", encoding="utf-8")
        rows = "\n".join(f"<tr><td>{k}</td><td>{v:.6f}</td></tr>" for k, v in scores.items())
        manifest = result.get("release_manifest", {})
        html = f"""<!doctype html>
<html lang='en'>
<head><meta charset='utf-8'><title>GitHub Release Orchestrator</title></head>
<body>
<h1>GitHub Release Orchestrator</h1>
<p>Primitive: {result['primitive']} - {result['refinement']}</p>
<p>Success: {result['success']}</p>
<p>Release orchestration score: {result['github_release_orchestration_score']:.6f}</p>
<p>Release readiness index: {result['release_readiness_index']:.6f}</p>
<p>Zenodo handoff readiness: {result['zenodo_handoff_readiness']:.6f}</p>
<h2>Prepared release manifest</h2>
<pre>{json.dumps(manifest, indent=2, ensure_ascii=False)}</pre>
<h2>Component scores</h2>
<table border='1'><tr><th>Metric</th><th>Value</th></tr>{rows}</table>
</body></html>"""
        html_path.write_text(html, encoding="utf-8")
        result["state_path"] = str(state_path)
        result["history_path"] = str(history_path)
        result["prometheus_path"] = str(prom_path)
        result["dashboard_path"] = str(html_path)
        result["release_manifest_path"] = str(manifest_path)
        state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    def step(self, release_context: Optional[Dict[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        ctx = dict(release_context) if release_context is not None else self._derive_context()
        scores = self._score(ctx)
        release_score = scores["github_release_orchestration_score"]
        readiness = scores["release_readiness_index"]
        zenodo_ready = scores["zenodo_handoff_readiness"]
        success = bool(ctx.get("has_git_repository", False)) and bool(ctx.get("has_public_remote", False)) and readiness >= 0.55
        manifest = self._build_release_manifest(ctx, scores)
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": self._now(),
            "success": success,
            "github_release_orchestration_score": release_score,
            "release_readiness_index": readiness,
            "zenodo_handoff_readiness": zenodo_ready,
            "release_manifest": manifest,
            "recommended_public_release_tag": ctx.get("recommended_public_release_tag"),
            "public_release_action_required": bool(ctx.get("public_release_action_required", True)),
            "public_github_tags_visible_count": ctx.get("public_github_tags_visible_count"),
            "component_scores": scores,
            "release_context": ctx,
            "governance": {
                "no_network_side_effects": True,
                "no_push_performed": True,
                "no_release_published": True,
                "read_only_git_inspection": release_context is None,
                "release_manifest_export_enabled": True,
                "prometheus_export_enabled": True,
                "html_dashboard_export_enabled": True,
                "zenodo_handoff_prepared": True,
                "non_closure_compliant": True,
            },
            "diagnostics": {
                "release_context_override_used": release_context is not None,
                "persist_requested": persist,
                "closure_pressure_increase": 0.0,
                "warnings": [] if success else ["github_release_orchestration_below_certification_threshold"],
            },
            "state_path": None,
            "history_path": None,
            "prometheus_path": None,
            "dashboard_path": None,
            "release_manifest_path": None,
        }
        if persist:
            self._write_outputs(result)
        return result


if __name__ == "__main__":
    print(json.dumps(GitHubReleaseOrchestrator().step(), indent=2, ensure_ascii=False))
