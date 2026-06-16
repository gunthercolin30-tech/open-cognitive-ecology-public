
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class OpenSourceReplicationPackageBuilder:
    """
    H4 — Open Source Replication Package Builder.

    Builds a local, reversible, no-network replication package for external
    scientific reproduction of Open Cognitive Ecology.

    This primitive does not publish anything, does not push to GitHub, and
    does not upload to Zenodo. It prepares local manifests, checksums,
    quickstart instructions, validation protocol, dashboard and metrics.
    """

    primitive = "open_source_replication_package_builder"
    refinement = "H4-R1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base = self.root / "external_validation" / self.primitive
        self.package_root = self.root / "replication_packages"

    def step(
        self,
        replication_package_context: Optional[Mapping[str, Any]] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        context = self._collect_context(replication_package_context)
        scores = self._score(context)

        package_completeness_score = round(
            (
                scores["source_package_basis"] * 0.18
                + scores["documentation_bundle"] * 0.15
                + scores["validation_bundle"] * 0.16
                + scores["publication_traceability_bundle"] * 0.12
                + scores["dependency_manifest_quality"] * 0.12
                + scores["checksum_integrity"] * 0.10
                + scores["non_closure_governance"] * 0.09
                + scores["h_chain_readiness"] * 0.08
            ),
            6,
        )

        external_replication_preparedness = round(
            (
                package_completeness_score * 0.55
                + scores["documentation_bundle"] * 0.15
                + scores["validation_bundle"] * 0.15
                + scores["publication_traceability_bundle"] * 0.10
                + scores["non_closure_governance"] * 0.05
            ),
            6,
        )

        replication_package_score = round(
            (package_completeness_score * 0.70 + external_replication_preparedness * 0.30),
            6,
        )

        success = replication_package_score >= 0.70 and external_replication_preparedness >= 0.65

        package_dir = None
        package_zip_path = None
        manifest_path = None
        inventory_path = None
        checksums_path = None
        quickstart_path = None
        protocol_path = None
        metadata_path = None
        state_path = None
        prometheus_path = None
        dashboard_path = None

        materialized: Dict[str, Any] = {}

        if persist:
            self.base.mkdir(parents=True, exist_ok=True)
            self.package_root.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            package_dir_path = self.package_root / f"open_cognitive_ecology_replication_package_{stamp}"
            package_dir_path.mkdir(parents=True, exist_ok=True)

            inventory = self._build_inventory(context)
            manifest = self._build_manifest(timestamp, context, scores, replication_package_score)
            metadata = self._build_metadata(timestamp, context, replication_package_score)
            quickstart = self._render_quickstart(manifest)
            protocol = self._render_validation_protocol(manifest)
            checksums = self._materialize_package_files(package_dir_path, inventory, manifest, metadata, quickstart, protocol)

            manifest_path = package_dir_path / "replication_package_manifest.json"
            inventory_path = package_dir_path / "replication_package_inventory.json"
            checksums_path = package_dir_path / "replication_package_checksums.json"
            quickstart_path = package_dir_path / "replication_quickstart.md"
            protocol_path = package_dir_path / "replication_validation_protocol.md"
            metadata_path = package_dir_path / "replication_bundle_metadata.json"

            self._write_json(manifest_path, manifest)
            self._write_json(inventory_path, inventory)
            self._write_json(checksums_path, checksums)
            quickstart_path.write_text(quickstart, encoding="utf-8")
            protocol_path.write_text(protocol, encoding="utf-8")
            self._write_json(metadata_path, metadata)

            # Recompute checksums after final files exist.
            checksums = self._compute_checksums(package_dir_path)
            self._write_json(checksums_path, checksums)

            package_zip_path = self.package_root / f"{package_dir_path.name}.zip"
            self._zip_directory(package_dir_path, package_zip_path)

            materialized = {
                "manifest_path": str(manifest_path),
                "inventory_path": str(inventory_path),
                "checksums_path": str(checksums_path),
                "quickstart_path": str(quickstart_path),
                "validation_protocol_path": str(protocol_path),
                "metadata_path": str(metadata_path),
                "package_dir": str(package_dir_path),
                "package_zip_path": str(package_zip_path),
                "package_zip_sha256": self._sha256(package_zip_path),
                "package_file_count": len([p for p in package_dir_path.rglob("*") if p.is_file()]),
            }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": timestamp,
            "success": success,
            "replication_package_score": replication_package_score,
            "replication_package_completeness_score": package_completeness_score,
            "external_replication_preparedness": external_replication_preparedness,
            "component_scores": scores,
            "component_details": self._component_details(context),
            "context_summary": self._context_summary(context),
            "package_dir": materialized.get("package_dir"),
            "package_zip_path": materialized.get("package_zip_path"),
            "package_zip_sha256": materialized.get("package_zip_sha256"),
            "manifest_path": materialized.get("manifest_path"),
            "inventory_path": materialized.get("inventory_path"),
            "checksums_path": materialized.get("checksums_path"),
            "quickstart_path": materialized.get("quickstart_path"),
            "validation_protocol_path": materialized.get("validation_protocol_path"),
            "metadata_path": materialized.get("metadata_path"),
            "governance": {
                "no_network_side_effects": True,
                "no_release_published": True,
                "no_zenodo_deposition_uploaded": True,
                "local_package_only": True,
                "traceability_enabled": True,
                "reversibility_enabled": True,
                "non_closure_compliant": True,
            },
            "diagnostics": {
                "persist_requested": bool(persist),
                "replication_package_context_override_used": replication_package_context is not None,
                "closure_pressure_increase": 0.0,
                "warnings": self._warnings(context, scores),
            },
        }

        if persist:
            state_path = self.base / "latest_open_source_replication_package_builder.json"
            history_path = self.base / "open_source_replication_package_builder_history.jsonl"
            prometheus_path = self.base / "open_source_replication_package_builder.prom"
            dashboard_path = self.base / "open_source_replication_package_builder_dashboard.html"
            self._write_json(state_path, result)
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            prometheus_path.write_text(self._render_prometheus(result), encoding="utf-8")
            dashboard_path.write_text(self._render_dashboard(result), encoding="utf-8")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)
            result["prometheus_path"] = str(prometheus_path)
            result["dashboard_path"] = str(dashboard_path)
        else:
            result["state_path"] = None
            result["history_path"] = None
            result["prometheus_path"] = None
            result["dashboard_path"] = None

        return result

    def _collect_context(self, override: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if override is not None:
            default = {
                "has_readme": False,
                "requirements_file_count": 0,
                "packaging_file_count": 0,
                "docs_file_count": 0,
                "validation_file_count": 0,
                "external_validation_file_count": 0,
                "publication_archive_file_count": 0,
                "has_zenodo_json": False,
                "has_citation_cff": False,
                "has_dependency_registry": False,
                "has_ontology_inventory": False,
                "has_integration_report": False,
                "has_scientific_validation_report": False,
                "has_h0_h3_outputs": False,
                "h_success_count": 0,
                "has_github_release_manifest": False,
                "has_zenodo_deposition_manifest": False,
                "has_publication_graph": False,
                "git_tag_count": 0,
                "has_public_remote": False,
                "replication_related_file_count": 0,
                "validation_command_present": False,
                "no_network_mode_supported": True,
            }
            default.update(dict(override))
            return default

        root = self.root
        docs = root / "docs"
        validation = root / "validation"
        external_validation = root / "external_validation"
        publication_archive = root / "publication_archive"

        h_latest_paths = [
            external_validation / "open_source_repository_governance" / "latest_open_source_repository_governance.json",
            external_validation / "open_source_replication_readiness" / "latest_open_source_replication_readiness.json",
            external_validation / "scientific_publication_traceability" / "latest_scientific_publication_traceability.json",
            external_validation / "external_validation_dashboard" / "latest_external_validation_dashboard.json",
            external_validation / "scientific_publication_registry" / "latest_scientific_publication_registry.json",
            external_validation / "github_release_orchestrator" / "latest_github_release_orchestrator.json",
            external_validation / "zenodo_publication_orchestrator" / "latest_zenodo_publication_orchestrator.json",
        ]
        h_success_count = sum(1 for p in h_latest_paths if self._read_json(p).get("success") is True)

        return {
            "has_readme": (root / "README.md").exists(),
            "requirements_file_count": len(list(root.glob("requirements*.txt"))),
            "packaging_file_count": sum(1 for p in ["pyproject.toml", "setup.py", "setup.cfg"] if (root / p).exists()),
            "docs_file_count": self._count_files(docs),
            "validation_file_count": self._count_files(validation),
            "external_validation_file_count": self._count_files(external_validation),
            "publication_archive_file_count": self._count_files(publication_archive),
            "has_zenodo_json": (root / ".zenodo.json").exists(),
            "has_citation_cff": (root / "CITATION.cff").exists(),
            "has_dependency_registry": (root / "ontology" / "dependency_registry.py").exists(),
            "has_ontology_inventory": (root / "ontology_inventory.txt").exists(),
            "has_integration_report": (root / "ontology_integration_report.txt").exists(),
            "has_scientific_validation_report": (root / "scientific_validation_report.json").exists() or (root / "scientific_validation_report.txt").exists(),
            "has_h0_h3_outputs": h_success_count >= 6,
            "h_success_count": h_success_count,
            "has_github_release_manifest": (external_validation / "github_release_orchestrator" / "github_release_manifest.json").exists(),
            "has_zenodo_deposition_manifest": (external_validation / "zenodo_publication_orchestrator" / "zenodo_deposition_manifest.json").exists(),
            "has_publication_graph": (external_validation / "zenodo_publication_orchestrator" / "publication_graph.json").exists(),
            "git_tag_count": self._run_git_tags_count(),
            "has_public_remote": "open-cognitive-ecology-public" in self._run_git_remotes(),
            "replication_related_file_count": len(self._find_related(["replication", "validation", "install", "setup", "quickstart", "manifest", "checksum", "release", "zenodo"])),
            "validation_command_present": self._validation_command_present(),
            "no_network_mode_supported": True,
        }

    def _score(self, context: Mapping[str, Any]) -> Dict[str, float]:
        source_package_basis = self._bounded(
            0.18 * bool(context.get("has_readme"))
            + 0.18 * min(1.0, float(context.get("requirements_file_count", 0)) / 2.0)
            + 0.15 * min(1.0, float(context.get("packaging_file_count", 0)) / 2.0)
            + 0.15 * bool(context.get("has_dependency_registry"))
            + 0.12 * bool(context.get("has_ontology_inventory"))
            + 0.12 * bool(context.get("has_public_remote"))
            + 0.10 * min(1.0, float(context.get("git_tag_count", 0)) / 1.0)
        )

        documentation_bundle = self._bounded(
            0.25 * bool(context.get("has_readme"))
            + 0.35 * min(1.0, float(context.get("docs_file_count", 0)) / 8.0)
            + 0.20 * bool(context.get("has_citation_cff"))
            + 0.20 * bool(context.get("has_zenodo_json"))
        )

        validation_bundle = self._bounded(
            0.30 * min(1.0, float(context.get("validation_file_count", 0)) / 3.0)
            + 0.25 * bool(context.get("has_integration_report"))
            + 0.20 * bool(context.get("has_scientific_validation_report"))
            + 0.15 * bool(context.get("validation_command_present"))
            + 0.10 * min(1.0, float(context.get("external_validation_file_count", 0)) / 30.0)
        )

        publication_traceability_bundle = self._bounded(
            0.18 * bool(context.get("has_zenodo_json"))
            + 0.18 * bool(context.get("has_citation_cff"))
            + 0.16 * bool(context.get("has_github_release_manifest"))
            + 0.16 * bool(context.get("has_zenodo_deposition_manifest"))
            + 0.16 * bool(context.get("has_publication_graph"))
            + 0.16 * min(1.0, float(context.get("publication_archive_file_count", 0)) / 5.0)
        )

        dependency_manifest_quality = self._bounded(
            0.35 * bool(context.get("has_dependency_registry"))
            + 0.25 * min(1.0, float(context.get("requirements_file_count", 0)) / 2.0)
            + 0.20 * min(1.0, float(context.get("packaging_file_count", 0)) / 2.0)
            + 0.20 * bool(context.get("no_network_mode_supported"))
        )

        checksum_integrity = self._bounded(
            0.45 * bool(context.get("has_readme"))
            + 0.25 * bool(context.get("has_ontology_inventory"))
            + 0.15 * bool(context.get("has_dependency_registry"))
            + 0.15 * min(1.0, float(context.get("replication_related_file_count", 0)) / 10.0)
        )

        non_closure_governance = self._bounded(
            0.35 * bool(context.get("no_network_mode_supported"))
            + 0.25 * bool(context.get("has_public_remote"))
            + 0.20 * bool(context.get("has_zenodo_json"))
            + 0.20 * bool(context.get("has_citation_cff"))
        )

        h_chain_readiness = self._bounded(
            0.55 * min(1.0, float(context.get("h_success_count", 0)) / 7.0)
            + 0.45 * bool(context.get("has_h0_h3_outputs"))
        )

        return {
            "source_package_basis": round(source_package_basis, 6),
            "documentation_bundle": round(documentation_bundle, 6),
            "validation_bundle": round(validation_bundle, 6),
            "publication_traceability_bundle": round(publication_traceability_bundle, 6),
            "dependency_manifest_quality": round(dependency_manifest_quality, 6),
            "checksum_integrity": round(checksum_integrity, 6),
            "non_closure_governance": round(non_closure_governance, 6),
            "h_chain_readiness": round(h_chain_readiness, 6),
        }

    def _build_inventory(self, context: Mapping[str, Any]) -> Dict[str, Any]:
        selected = []
        for rel in [
            "README.md",
            "CITATION.cff",
            ".zenodo.json",
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "ontology_inventory.txt",
            "ontology_integration_report.txt",
            "scientific_validation_report.json",
            "scientific_validation_report.txt",
            "ontology/dependency_registry.py",
            "validation/main.py",
        ]:
            p = self.root / rel
            if p.exists() and p.is_file():
                selected.append({"path": rel, "size_bytes": p.stat().st_size, "sha256": self._sha256(p)})
        return {
            "primitive": self.primitive,
            "selected_files": selected,
            "context_summary": self._context_summary(context),
            "directories_referenced": [
                "docs",
                "validation",
                "external_validation",
                "publication_archive",
                "ontology",
            ],
        }

    def _build_manifest(self, timestamp: str, context: Mapping[str, Any], scores: Mapping[str, float], score: float) -> Dict[str, Any]:
        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": timestamp,
            "package_type": "local_open_source_replication_package",
            "repository": "https://github.com/gunthercolin30-tech/open-cognitive-ecology-public",
            "replication_entrypoint": "python3 -m validation.main",
            "no_network_required_for_validation": True,
            "scores": dict(scores),
            "replication_package_score": score,
            "expected_outputs": [
                "ontology_integration_report.txt",
                "external_validation/*/*.json",
                "external_validation/*/*.prom",
                "external_validation/*/*.html",
            ],
            "governance": {
                "local_package_only": True,
                "no_credentials_required": True,
                "no_github_token_required": True,
                "no_zenodo_token_required": True,
                "reversible": True,
            },
            "context_summary": self._context_summary(context),
        }

    def _build_metadata(self, timestamp: str, context: Mapping[str, Any], score: float) -> Dict[str, Any]:
        return {
            "title": "Open Cognitive Ecology Replication Package",
            "timestamp_utc": timestamp,
            "creator": "Gunther, Colin",
            "score": score,
            "description": "Local open-source replication package for independently reproducing Open Cognitive Ecology validation outputs.",
            "context_summary": self._context_summary(context),
        }

    def _materialize_package_files(
        self,
        package_dir: Path,
        inventory: Mapping[str, Any],
        manifest: Mapping[str, Any],
        metadata: Mapping[str, Any],
        quickstart: str,
        protocol: str,
    ) -> Dict[str, str]:
        # Copy a bounded subset of files to avoid large local package growth.
        files_to_copy = [
            "README.md",
            "CITATION.cff",
            ".zenodo.json",
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "ontology_inventory.txt",
            "ontology_integration_report.txt",
            "scientific_validation_report.json",
            "scientific_validation_report.txt",
            "validation/main.py",
            "ontology/dependency_registry.py",
        ]
        for rel in files_to_copy:
            src = self.root / rel
            if src.exists() and src.is_file():
                dst = package_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        # Copy small external validation latest states and prometheus exports.
        ev_src = self.root / "external_validation"
        ev_dst = package_dir / "external_validation"
        if ev_src.exists():
            for p in ev_src.rglob("*"):
                if p.is_file() and p.name.startswith(("latest_",)) or (p.is_file() and p.suffix in {".prom"}):
                    rel = p.relative_to(ev_src)
                    dst = ev_dst / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if p.stat().st_size <= 2_000_000:
                        shutil.copy2(p, dst)

        docs_src = self.root / "docs"
        docs_dst = package_dir / "docs"
        if docs_src.exists():
            for p in docs_src.rglob("*"):
                if p.is_file() and p.stat().st_size <= 1_000_000:
                    dst = docs_dst / p.relative_to(docs_src)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, dst)

        return self._compute_checksums(package_dir)

    def _render_quickstart(self, manifest: Mapping[str, Any]) -> str:
        return "\n".join([
            "# Open Cognitive Ecology — Replication Quickstart",
            "",
            "This package is generated locally by H4 open_source_replication_package_builder.",
            "",
            "## Clone",
            "",
            "```bash",
            "git clone https://github.com/gunthercolin30-tech/open-cognitive-ecology-public.git",
            "cd open-cognitive-ecology-public",
            "```",
            "",
            "## Install",
            "",
            "```bash",
            "python3 -m venv .venv",
            "source .venv/bin/activate",
            "pip install -r requirements.txt",
            "```",
            "",
            "## Validate",
            "",
            "```bash",
            "python3 -m validation.main",
            "```",
            "",
            "## Governance",
            "",
            "No GitHub token, Zenodo token, network publication, DOI creation or release publication is required for local replication.",
            "",
        ])

    def _render_validation_protocol(self, manifest: Mapping[str, Any]) -> str:
        return "\n".join([
            "# Replication Validation Protocol",
            "",
            "1. Install the repository dependencies.",
            "2. Run `python3 -m validation.main`.",
            "3. Confirm `errors: 0` in `ontology_integration_report.txt`.",
            "4. Inspect external validation JSON, Prometheus and HTML exports.",
            "5. Record environment, Python version, warnings and deviations.",
            "",
            "Benign warnings currently include RuntimeWarning and NotOpenSSLWarning.",
            "",
        ])

    def _render_prometheus(self, result: Mapping[str, Any]) -> str:
        values = {
            "oce_open_source_replication_package_score": result.get("replication_package_score", 0.0),
            "oce_replication_package_completeness_score": result.get("replication_package_completeness_score", 0.0),
            "oce_external_replication_preparedness": result.get("external_replication_preparedness", 0.0),
            "oce_replication_package_success": 1.0 if result.get("success") else 0.0,
        }
        lines = []
        for name, value in values.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value):.6f}")
        return "\n".join(lines) + "\n"

    def _render_dashboard(self, result: Mapping[str, Any]) -> str:
        rows = []
        for key, value in result.get("component_scores", {}).items():
            rows.append(f"<tr><td>{key}</td><td>{float(value):.6f}</td></tr>")
        return "\n".join([
            "<!doctype html>",
            "<html><head><meta charset='utf-8'><title>Open Source Replication Package Builder</title></head>",
            "<body>",
            "<h1>Open Source Replication Package Builder</h1>",
            f"<p>Success: {result.get('success')}</p>",
            f"<p>Replication package score: {result.get('replication_package_score')}</p>",
            f"<p>Package ZIP: {result.get('package_zip_path')}</p>",
            "<h2>Component scores</h2>",
            "<table><tr><th>Component</th><th>Score</th></tr>",
            *rows,
            "</table>",
            "</body></html>",
        ])

    def _warnings(self, context: Mapping[str, Any], scores: Mapping[str, float]) -> List[str]:
        warnings: List[str] = []
        if not context.get("has_readme"):
            warnings.append("missing_readme")
        if int(context.get("requirements_file_count", 0)) == 0:
            warnings.append("missing_requirements")
        if not context.get("has_ontology_inventory"):
            warnings.append("missing_ontology_inventory")
        if scores.get("validation_bundle", 0.0) < 0.5:
            warnings.append("weak_validation_bundle")
        if scores.get("publication_traceability_bundle", 0.0) < 0.5:
            warnings.append("weak_publication_traceability_bundle")
        return warnings

    def _component_details(self, context: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "context_override_used": False,
            "requirements_file_count": context.get("requirements_file_count", 0),
            "docs_file_count": context.get("docs_file_count", 0),
            "validation_file_count": context.get("validation_file_count", 0),
            "external_validation_file_count": context.get("external_validation_file_count", 0),
            "h_success_count": context.get("h_success_count", 0),
            "git_tag_count": context.get("git_tag_count", 0),
        }

    def _context_summary(self, context: Mapping[str, Any]) -> Dict[str, Any]:
        keys = [
            "has_readme",
            "requirements_file_count",
            "packaging_file_count",
            "docs_file_count",
            "validation_file_count",
            "external_validation_file_count",
            "has_zenodo_json",
            "has_citation_cff",
            "h_success_count",
            "has_public_remote",
        ]
        return {key: context.get(key) for key in keys}

    def _count_files(self, path: Path) -> int:
        if not path.exists():
            return 0
        return sum(1 for p in path.rglob("*") if p.is_file())

    def _find_related(self, terms: List[str]) -> List[Path]:
        found: List[Path] = []
        for p in self.root.rglob("*"):
            if p.is_file():
                name = p.name.lower()
                if any(term in name for term in terms):
                    found.append(p)
        return found[:500]

    def _validation_command_present(self) -> bool:
        readme = self._read_text(self.root / "README.md")
        guide = ""
        docs = self.root / "docs"
        if docs.exists():
            for p in docs.rglob("*"):
                if p.is_file() and p.stat().st_size <= 1_000_000:
                    guide += "\n" + self._read_text(p)
        combined = (readme + "\n" + guide).lower()
        return "python3 -m validation.main" in combined or "validation.main" in combined

    def _run_git_tags_count(self) -> int:
        import subprocess
        try:
            cp = subprocess.run(["git", "tag", "-l"], cwd=str(self.root), capture_output=True, text=True, timeout=5)
            if cp.returncode == 0:
                return len([x for x in cp.stdout.splitlines() if x.strip()])
        except Exception:
            pass
        return 0

    def _run_git_remotes(self) -> str:
        import subprocess
        try:
            cp = subprocess.run(["git", "remote", "-v"], cwd=str(self.root), capture_output=True, text=True, timeout=5)
            if cp.returncode == 0:
                return cp.stdout
        except Exception:
            pass
        return ""

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _read_text(self, path: Path) -> str:
        try:
            if path.exists():
                return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""
        return ""

    def _write_json(self, path: Path, payload: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def _compute_checksums(self, package_dir: Path) -> Dict[str, Any]:
        entries = []
        for p in sorted(package_dir.rglob("*")):
            if p.is_file():
                entries.append({
                    "path": str(p.relative_to(package_dir)),
                    "sha256": self._sha256(p),
                    "size_bytes": p.stat().st_size,
                })
        return {"algorithm": "sha256", "file_count": len(entries), "files": entries}

    def _sha256(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def _zip_directory(self, source_dir: Path, zip_path: Path) -> None:
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(source_dir.rglob("*")):
                if p.is_file():
                    zf.write(p, p.relative_to(source_dir.parent))

    def _bounded(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


def step() -> Dict[str, Any]:
    return OpenSourceReplicationPackageBuilder().step()
