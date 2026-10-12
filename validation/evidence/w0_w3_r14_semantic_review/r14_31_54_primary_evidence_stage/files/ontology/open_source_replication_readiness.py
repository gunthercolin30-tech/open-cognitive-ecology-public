
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class OpenSourceReplicationReadiness:
    """
    H0.2 - Open Source Replication Readiness.

    Evaluates whether an external researcher can reproduce Open Cognitive
    Ecology from the public repository using documented, versioned,
    traceable and locally executable procedures.

    The primitive is intentionally read-only with respect to Git and never
    performs network operations. It measures functional readiness, not
    actual external replication success.
    """

    primitive = "open_source_replication_readiness"
    refinement = "H0.2-R1"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / self.primitive

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, round(float(value), 4)))

    def _exists_any(self, names: list[str]) -> bool:
        return any((self.root / name).exists() for name in names)

    def _count_existing(self, names: list[str]) -> int:
        return sum(1 for name in names if (self.root / name).exists())

    def _safe_git(self, args: list[str]) -> str:
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=self.root,
                text=True,
                capture_output=True,
                timeout=5,
                check=False,
            )
            if completed.returncode == 0:
                return completed.stdout.strip()
            return ""
        except Exception:
            return ""

    def _read_text(self, relative: str, limit: int = 20000) -> str:
        path = self.root / relative
        try:
            if path.exists() and path.is_file():
                return path.read_text(encoding="utf-8", errors="ignore")[:limit]
        except Exception:
            pass
        return ""

    def _detect_context(self) -> dict[str, Any]:
        docs_dir = self.root / "docs"
        github_dir = self.root / ".github"
        workflows_dir = github_dir / "workflows"
        issue_dir = github_dir / "ISSUE_TEMPLATE"
        validation_dir = self.root / "validation"
        publication_dir = self.root / "publication_archive"
        runtime_service_dir = self.root / "runtime_service"
        runtime_exp_dir = self.root / "runtime_experiments"

        docs = [p for p in docs_dir.rglob("*") if p.is_file()] if docs_dir.exists() else []
        workflows = [p for p in workflows_dir.rglob("*.yml")] + [p for p in workflows_dir.rglob("*.yaml")] if workflows_dir.exists() else []
        issue_templates = [p for p in issue_dir.rglob("*") if p.is_file()] if issue_dir.exists() else []

        requirements_files = [
            p for p in self.root.glob("requirements*.txt")
            if p.is_file()
        ]
        packaging_files = [
            p for p in [self.root / "pyproject.toml", self.root / "setup.py", self.root / "setup.cfg"]
            if p.exists()
        ]
        validation_files = [p for p in validation_dir.rglob("*.py") if p.is_file()] if validation_dir.exists() else []
        publication_files = [p for p in publication_dir.rglob("*") if p.is_file()] if publication_dir.exists() else []
        runtime_files = []
        for d in [runtime_service_dir, runtime_exp_dir]:
            if d.exists():
                runtime_files.extend([p for p in d.rglob("*") if p.is_file()])

        remotes = self._safe_git(["remote", "-v"])
        tags = self._safe_git(["tag", "--list"])
        branches = self._safe_git(["branch", "--list"])

        readme = self._read_text("README.md")
        validation_guide = self._read_text("docs/validation_guide.md")
        ci_text = "\n".join(self._read_text(str(p.relative_to(self.root))) for p in workflows[:5])

        return {
            "has_git_repository": (self.root / ".git").exists(),
            "has_origin_remote": "origin" in remotes,
            "has_public_remote": "open-cognitive-ecology-public" in remotes or "public" in remotes,
            "remote_count": len({line.split()[0] for line in remotes.splitlines() if line.strip()}),
            "tag_count": len([line for line in tags.splitlines() if line.strip()]),
            "branch_count": len([line for line in branches.splitlines() if line.strip()]),
            "has_readme": (self.root / "README.md").exists(),
            "docs_file_count": len(docs),
            "has_validation_guide": (self.root / "docs" / "validation_guide.md").exists(),
            "has_architecture_docs": self._exists_any(["docs/architecture.md", "docs/architecture_summary.md"]),
            "has_roadmap": (self.root / "docs" / "roadmap.md").exists(),
            "requirements_file_count": len(requirements_files),
            "packaging_file_count": len(packaging_files),
            "has_pyproject": (self.root / "pyproject.toml").exists(),
            "has_validation_main": (self.root / "validation" / "main.py").exists(),
            "validation_file_count": len(validation_files),
            "has_scientific_reports": self._exists_any([
                "scientific_validation_report.json",
                "scientific_validation_report.txt",
                "ontology_integration_report.txt",
            ]),
            "workflow_count": len(workflows),
            "has_ci": len(workflows) > 0,
            "has_dependabot": (self.root / ".github" / "dependabot.yml").exists(),
            "issue_template_count": len(issue_templates),
            "has_pr_template": (self.root / ".github" / "pull_request_template.md").exists(),
            "publication_file_count": len(publication_files),
            "runtime_file_count": len(runtime_files),
            "readme_mentions_install": any(term in readme.lower() for term in ["install", "installation", "requirements", "python3 -m validation.main"]),
            "readme_mentions_validation": "validation" in readme.lower(),
            "validation_guide_has_commands": "python" in validation_guide.lower() or "validation.main" in validation_guide,
            "ci_mentions_validation": "validation" in ci_text.lower() or "pytest" in ci_text.lower(),
            "ci_mentions_python_versions": "python-version" in ci_text.lower() or "matrix" in ci_text.lower(),
        }

    def _score(self, context: dict[str, Any]) -> tuple[dict[str, float], dict[str, Any]]:
        install_docs = self._clamp(
            0.25 * bool(context.get("has_readme")) +
            0.25 * bool(context.get("readme_mentions_install")) +
            0.25 * bool(context.get("has_validation_guide")) +
            0.25 * bool(context.get("validation_guide_has_commands"))
        )
        dependency_spec = self._clamp(
            0.45 * min(1.0, context.get("requirements_file_count", 0) / 2) +
            0.35 * bool(context.get("has_pyproject")) +
            0.20 * min(1.0, context.get("packaging_file_count", 0) / 2)
        )
        validation_protocol = self._clamp(
            0.35 * bool(context.get("has_validation_main")) +
            0.25 * min(1.0, context.get("validation_file_count", 0) / 4) +
            0.25 * bool(context.get("has_scientific_reports")) +
            0.15 * bool(context.get("readme_mentions_validation"))
        )
        ci_replication = self._clamp(
            0.35 * bool(context.get("has_ci")) +
            0.25 * bool(context.get("ci_mentions_validation")) +
            0.20 * bool(context.get("ci_mentions_python_versions")) +
            0.20 * bool(context.get("has_dependabot"))
        )
        package_completeness = self._clamp(
            0.18 * bool(context.get("has_git_repository")) +
            0.16 * bool(context.get("has_origin_remote")) +
            0.16 * bool(context.get("has_public_remote")) +
            0.16 * min(1.0, context.get("tag_count", 0) / 3) +
            0.18 * min(1.0, context.get("docs_file_count", 0) / 8) +
            0.16 * (bool(context.get("has_pr_template")) or context.get("issue_template_count", 0) > 0)
        )
        runtime_reproducibility = self._clamp(
            0.35 * min(1.0, context.get("runtime_file_count", 0) / 3) +
            0.25 * min(1.0, context.get("publication_file_count", 0) / 3) +
            0.20 * bool(context.get("has_architecture_docs")) +
            0.20 * bool(context.get("has_roadmap"))
        )

        scores = {
            "installation_documentation_score": install_docs,
            "dependency_specification_score": dependency_spec,
            "validation_protocol_score": validation_protocol,
            "ci_replication_score": ci_replication,
            "replication_package_completeness": package_completeness,
            "runtime_reproducibility_score": runtime_reproducibility,
        }
        details = {
            "install_docs": {
                "has_readme": context.get("has_readme", False),
                "readme_mentions_install": context.get("readme_mentions_install", False),
                "has_validation_guide": context.get("has_validation_guide", False),
                "validation_guide_has_commands": context.get("validation_guide_has_commands", False),
            },
            "dependencies": {
                "requirements_file_count": context.get("requirements_file_count", 0),
                "packaging_file_count": context.get("packaging_file_count", 0),
                "has_pyproject": context.get("has_pyproject", False),
            },
            "validation": {
                "has_validation_main": context.get("has_validation_main", False),
                "validation_file_count": context.get("validation_file_count", 0),
                "has_scientific_reports": context.get("has_scientific_reports", False),
            },
            "ci": {
                "workflow_count": context.get("workflow_count", 0),
                "has_dependabot": context.get("has_dependabot", False),
                "ci_mentions_validation": context.get("ci_mentions_validation", False),
            },
            "package": {
                "tag_count": context.get("tag_count", 0),
                "docs_file_count": context.get("docs_file_count", 0),
                "issue_template_count": context.get("issue_template_count", 0),
                "has_public_remote": context.get("has_public_remote", False),
            },
        }
        return scores, details

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _write_prometheus(self, path: Path, result: dict[str, Any]) -> None:
        lines = [
            "# HELP oce_open_source_replication_readiness_score Open source replication readiness score.",
            "# TYPE oce_open_source_replication_readiness_score gauge",
            f"oce_open_source_replication_readiness_score {result['replication_readiness_score']}",
            "# HELP oce_external_reproduction_preparedness External reproduction preparedness index.",
            "# TYPE oce_external_reproduction_preparedness gauge",
            f"oce_external_reproduction_preparedness {result['external_reproduction_preparedness']}",
            "# HELP oce_replication_protocol_completeness Replication protocol completeness.",
            "# TYPE oce_replication_protocol_completeness gauge",
            f"oce_replication_protocol_completeness {result['replication_protocol_completeness']}",
        ]
        for key, value in result["component_scores"].items():
            metric = "oce_" + key
            lines.append(f"# TYPE {metric} gauge")
            lines.append(f"{metric} {value}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_dashboard(self, path: Path, result: dict[str, Any]) -> None:
        rows = "".join(
            f"<tr><td>{key}</td><td>{value}</td></tr>"
            for key, value in result["component_scores"].items()
        )
        html = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Open Source Replication Readiness</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;}}table{{border-collapse:collapse;width:100%;}}td,th{{border:1px solid #ccc;padding:8px;text-align:left;}}th{{background:#f0f0f0;}}</style></head>
<body><h1>Open Source Replication Readiness</h1>
<p>Primitive: {result['primitive']} | Refinement: {result['refinement']}</p>
<table><tr><th>Metric</th><th>Value</th></tr>
<tr><td>success</td><td>{result['success']}</td></tr>
<tr><td>replication_readiness_score</td><td>{result['replication_readiness_score']}</td></tr>
<tr><td>external_reproduction_preparedness</td><td>{result['external_reproduction_preparedness']}</td></tr>
<tr><td>replication_protocol_completeness</td><td>{result['replication_protocol_completeness']}</td></tr>
{rows}
</table></body></html>"""
        path.write_text(html, encoding="utf-8")

    def _persist(self, result: dict[str, Any]) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        state_path = self.output_dir / "latest_open_source_replication_readiness.json"
        history_path = self.output_dir / "open_source_replication_readiness_history.jsonl"
        prom_path = self.output_dir / "open_source_replication_readiness.prom"
        dashboard_path = self.output_dir / "open_source_replication_readiness_dashboard.html"

        serializable = dict(result)
        serializable["state_path"] = str(state_path)
        serializable["history_path"] = str(history_path)
        serializable["prometheus_path"] = str(prom_path)
        serializable["dashboard_path"] = str(dashboard_path)

        self._write_json(state_path, serializable)
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(serializable, ensure_ascii=False) + "\n")
        self._write_prometheus(prom_path, serializable)
        self._write_dashboard(dashboard_path, serializable)
        return serializable

    def step(
        self,
        replication_context: dict[str, Any] | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        context = self._detect_context()
        override_used = False
        if replication_context:
            context.update(replication_context)
            override_used = True

        scores, details = self._score(context)

        replication_readiness_score = self._clamp(
            0.20 * scores["installation_documentation_score"] +
            0.15 * scores["dependency_specification_score"] +
            0.20 * scores["validation_protocol_score"] +
            0.15 * scores["ci_replication_score"] +
            0.15 * scores["replication_package_completeness"] +
            0.15 * scores["runtime_reproducibility_score"]
        )
        external_reproduction_preparedness = self._clamp(
            0.30 * scores["validation_protocol_score"] +
            0.25 * scores["replication_package_completeness"] +
            0.20 * scores["installation_documentation_score"] +
            0.15 * scores["ci_replication_score"] +
            0.10 * scores["dependency_specification_score"]
        )
        replication_protocol_completeness = self._clamp(
            0.35 * scores["installation_documentation_score"] +
            0.35 * scores["validation_protocol_score"] +
            0.15 * scores["dependency_specification_score"] +
            0.15 * scores["runtime_reproducibility_score"]
        )

        success = (
            replication_readiness_score >= 0.75 and
            external_reproduction_preparedness >= 0.70 and
            scores["validation_protocol_score"] >= 0.60
        )

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": self._now(),
            "success": bool(success),
            "replication_readiness_score": replication_readiness_score,
            "external_reproduction_preparedness": external_reproduction_preparedness,
            "replication_protocol_completeness": replication_protocol_completeness,
            "component_scores": scores,
            "component_details": details,
            "repository_state_summary": {
                "tag_count": context.get("tag_count", 0),
                "branch_count": context.get("branch_count", 0),
                "remote_count": context.get("remote_count", 0),
                "workflow_count": context.get("workflow_count", 0),
                "docs_file_count": context.get("docs_file_count", 0),
                "requirements_file_count": context.get("requirements_file_count", 0),
                "validation_file_count": context.get("validation_file_count", 0),
            },
            "governance": {
                "read_only_git_inspection": True,
                "no_network_side_effects": True,
                "traceability_enabled": True,
                "prometheus_export_enabled": True,
                "html_dashboard_export_enabled": True,
                "non_closure_compliant": True,
            },
            "diagnostics": {
                "replication_context_override_used": override_used,
                "persist_requested": persist,
                "closure_pressure_increase": 0.0,
                "warnings": [] if success else ["replication_readiness_below_certification_threshold"],
            },
            "state_path": None,
            "history_path": None,
            "prometheus_path": None,
            "dashboard_path": None,
        }
        if persist:
            result = self._persist(result)
        return result
