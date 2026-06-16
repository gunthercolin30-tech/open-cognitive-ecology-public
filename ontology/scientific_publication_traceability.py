
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ScientificPublicationTraceability:
    """
    H0.3 - Scientific Publication Traceability.

    Measures whether scientific outputs can be traced across Git history,
    validation reports, publication archives, release tags and external
    validation artifacts. The primitive is read-only with respect to Git and
    performs no network operations.
    """

    primitive = "scientific_publication_traceability"
    refinement = "H0.3-R1"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / self.primitive

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, round(float(value), 4)))

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
        except Exception:
            pass
        return ""

    def _read_text(self, relative: str, limit: int = 50000) -> str:
        path = self.root / relative
        try:
            if path.exists() and path.is_file():
                return path.read_text(encoding="utf-8", errors="ignore")[:limit]
        except Exception:
            pass
        return ""

    @staticmethod
    def _doi_count(text: str) -> int:
        return len(set(re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text or "")))

    def _detect_context(self) -> dict[str, Any]:
        publication_dir = self.root / "publication_archive"
        docs_dir = self.root / "docs"
        external_validation_dir = self.root / "external_validation"
        github_dir = self.root / ".github"

        publication_files = [p for p in publication_dir.rglob("*") if p.is_file()] if publication_dir.exists() else []
        manuscript_files = [p for p in publication_files if "manuscript" in p.name.lower()]
        bibliography_files = [p for p in publication_files if "bibliography" in p.name.lower() or "citation" in p.name.lower()]
        metrics_files = [p for p in publication_files if "metric" in p.name.lower() or p.suffix.lower() == ".json"]
        docs_files = [p for p in docs_dir.rglob("*") if p.is_file()] if docs_dir.exists() else []
        external_files = [p for p in external_validation_dir.rglob("*") if p.is_file()] if external_validation_dir.exists() else []

        tags = [x for x in self._safe_git(["tag", "--list"]).splitlines() if x.strip()]
        log = self._safe_git(["log", "--decorate", "--oneline", "-50"])
        remotes = self._safe_git(["remote", "-v"])

        report_json_path = self.root / "scientific_validation_report.json"
        report_txt_path = self.root / "scientific_validation_report.txt"
        readme = self._read_text("README.md")
        validation_guide = self._read_text("docs/validation_guide.md")
        scientific_report_txt = self._read_text("scientific_validation_report.txt")
        scientific_report_json = self._read_text("scientific_validation_report.json")
        publication_inventory = "\n".join(str(p.relative_to(self.root)) for p in publication_files[:500])
        docs_inventory = "\n".join(str(p.relative_to(self.root)) for p in docs_files[:500])
        combined = "\n".join([readme, validation_guide, scientific_report_txt, scientific_report_json, publication_inventory, docs_inventory, log])

        return {
            "has_publication_archive": publication_dir.exists(),
            "publication_file_count": len(publication_files),
            "manuscript_file_count": len(manuscript_files),
            "bibliography_file_count": len(bibliography_files),
            "publication_metrics_file_count": len(metrics_files),
            "has_scientific_validation_report_json": report_json_path.exists(),
            "has_scientific_validation_report_txt": report_txt_path.exists(),
            "has_validation_guide": bool(validation_guide),
            "docs_file_count": len(docs_files),
            "external_validation_file_count": len(external_files),
            "has_h0_1_state": (external_validation_dir / "open_source_repository_governance" / "latest_open_source_repository_governance.json").exists(),
            "has_h0_2_state": (external_validation_dir / "open_source_replication_readiness" / "latest_open_source_replication_readiness.json").exists(),
            "has_github_workflow": (github_dir / "workflows").exists(),
            "git_tag_count": len(tags),
            "release_tag_count": len([t for t in tags if t.startswith("v")]),
            "publication_commit_count": len([line for line in log.splitlines() if any(k in line.lower() for k in ["publication", "release", "dashboard", "validation", "report", "zenodo"])]),
            "has_remote": bool(remotes.strip()),
            "has_public_remote": "open-cognitive-ecology-public" in remotes or "public" in remotes,
            "doi_count": self._doi_count(combined),
            "mentions_zenodo": "zenodo" in combined.lower(),
            "mentions_publication": "publication" in combined.lower(),
            "mentions_validation": "validation" in combined.lower(),
            "mentions_replication": "replication" in combined.lower(),
            "mentions_traceability": "traceability" in combined.lower() or "traçabilité" in combined.lower(),
        }

    def _score(self, context: dict[str, Any]) -> tuple[dict[str, float], dict[str, Any]]:
        publication_archive_score = self._clamp(
            (0.25 if context.get("has_publication_archive") else 0.0)
            + min(0.25, context.get("publication_file_count", 0) / 20.0)
            + min(0.20, context.get("manuscript_file_count", 0) / 5.0)
            + min(0.15, context.get("bibliography_file_count", 0) / 5.0)
            + min(0.15, context.get("publication_metrics_file_count", 0) / 5.0)
        )
        validation_linkage_score = self._clamp(
            (0.22 if context.get("has_scientific_validation_report_json") else 0.0)
            + (0.18 if context.get("has_scientific_validation_report_txt") else 0.0)
            + (0.15 if context.get("has_validation_guide") else 0.0)
            + min(0.15, context.get("external_validation_file_count", 0) / 20.0)
            + (0.15 if context.get("has_h0_1_state") else 0.0)
            + (0.15 if context.get("has_h0_2_state") else 0.0)
        )
        git_release_traceability_score = self._clamp(
            min(0.25, context.get("git_tag_count", 0) / 10.0)
            + min(0.20, context.get("release_tag_count", 0) / 8.0)
            + min(0.25, context.get("publication_commit_count", 0) / 10.0)
            + (0.15 if context.get("has_remote") else 0.0)
            + (0.15 if context.get("has_public_remote") else 0.0)
        )
        doi_and_external_publication_score = self._clamp(
            min(0.35, context.get("doi_count", 0) / 10.0)
            + (0.25 if context.get("mentions_zenodo") else 0.0)
            + (0.15 if context.get("mentions_publication") else 0.0)
            + (0.10 if context.get("mentions_replication") else 0.0)
            + (0.15 if context.get("mentions_traceability") else 0.0)
        )
        documentation_traceability_score = self._clamp(
            min(0.30, context.get("docs_file_count", 0) / 20.0)
            + (0.25 if context.get("mentions_validation") else 0.0)
            + (0.20 if context.get("mentions_publication") else 0.0)
            + (0.15 if context.get("mentions_replication") else 0.0)
            + (0.10 if context.get("has_github_workflow") else 0.0)
        )

        scores = {
            "publication_archive_score": publication_archive_score,
            "validation_linkage_score": validation_linkage_score,
            "git_release_traceability_score": git_release_traceability_score,
            "doi_and_external_publication_score": doi_and_external_publication_score,
            "documentation_traceability_score": documentation_traceability_score,
        }
        details = {
            "publication_archive": {
                "has_publication_archive": context.get("has_publication_archive"),
                "publication_file_count": context.get("publication_file_count", 0),
                "manuscript_file_count": context.get("manuscript_file_count", 0),
                "bibliography_file_count": context.get("bibliography_file_count", 0),
                "publication_metrics_file_count": context.get("publication_metrics_file_count", 0),
            },
            "validation_linkage": {
                "has_scientific_validation_report_json": context.get("has_scientific_validation_report_json"),
                "has_scientific_validation_report_txt": context.get("has_scientific_validation_report_txt"),
                "has_validation_guide": context.get("has_validation_guide"),
                "external_validation_file_count": context.get("external_validation_file_count", 0),
                "has_h0_1_state": context.get("has_h0_1_state"),
                "has_h0_2_state": context.get("has_h0_2_state"),
            },
            "git_release_traceability": {
                "git_tag_count": context.get("git_tag_count", 0),
                "release_tag_count": context.get("release_tag_count", 0),
                "publication_commit_count": context.get("publication_commit_count", 0),
                "has_remote": context.get("has_remote"),
                "has_public_remote": context.get("has_public_remote"),
            },
            "doi_and_external_publication": {
                "doi_count": context.get("doi_count", 0),
                "mentions_zenodo": context.get("mentions_zenodo"),
                "mentions_publication": context.get("mentions_publication"),
                "mentions_replication": context.get("mentions_replication"),
                "mentions_traceability": context.get("mentions_traceability"),
            },
            "documentation_traceability": {
                "docs_file_count": context.get("docs_file_count", 0),
                "mentions_validation": context.get("mentions_validation"),
                "has_github_workflow": context.get("has_github_workflow"),
            },
        }
        return scores, details

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def _write_prometheus(self, path: Path, result: dict[str, Any]) -> None:
        metrics = {
            "oce_scientific_publication_traceability_score": result["publication_traceability_score"],
            "oce_publication_archive_score": result["component_scores"]["publication_archive_score"],
            "oce_validation_publication_linkage_score": result["component_scores"]["validation_linkage_score"],
            "oce_git_release_traceability_score": result["component_scores"]["git_release_traceability_score"],
            "oce_external_publication_evidence_score": result["component_scores"]["doi_and_external_publication_score"],
            "oce_publication_confidence_index": result["publication_confidence_index"],
        }
        lines = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value):.6f}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_dashboard(self, path: Path, result: dict[str, Any]) -> None:
        rows = "\n".join(
            f"<tr><td>{key}</td><td>{value:.4f}</td></tr>"
            for key, value in result["component_scores"].items()
        )
        html = f"""<!doctype html>
<html><head><meta charset=\"utf-8\"><title>Scientific Publication Traceability</title>
<style>body{{font-family:Arial,sans-serif;margin:2rem;}}table{{border-collapse:collapse;}}td,th{{border:1px solid #ccc;padding:.45rem .7rem;}}</style></head>
<body>
<h1>Scientific Publication Traceability</h1>
<p>Primitive: {result['primitive']} — {result['refinement']}</p>
<p>Success: {result['success']}</p>
<p>Publication traceability score: {result['publication_traceability_score']:.4f}</p>
<p>Publication confidence index: {result['publication_confidence_index']:.4f}</p>
<table><tr><th>Component</th><th>Score</th></tr>{rows}</table>
</body></html>"""
        path.write_text(html, encoding="utf-8")

    def step(self, publication_context: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        context = self._detect_context()
        override_used = publication_context is not None
        if publication_context:
            context.update(publication_context)

        scores, details = self._score(context)
        publication_traceability_score = self._clamp(
            0.22 * scores["publication_archive_score"]
            + 0.24 * scores["validation_linkage_score"]
            + 0.22 * scores["git_release_traceability_score"]
            + 0.17 * scores["doi_and_external_publication_score"]
            + 0.15 * scores["documentation_traceability_score"]
        )
        publication_confidence_index = self._clamp(
            0.55 * publication_traceability_score
            + 0.25 * scores["validation_linkage_score"]
            + 0.20 * scores["git_release_traceability_score"]
        )
        success = publication_traceability_score >= 0.60 and publication_confidence_index >= 0.60

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": self._now(),
            "success": bool(success),
            "publication_traceability_score": publication_traceability_score,
            "publication_confidence_index": publication_confidence_index,
            "git_publication_traceability_score": scores["git_release_traceability_score"],
            "validation_publication_linkage_score": scores["validation_linkage_score"],
            "external_publication_evidence_score": scores["doi_and_external_publication_score"],
            "component_scores": scores,
            "component_details": details,
            "publication_state_summary": {
                "publication_file_count": int(context.get("publication_file_count", 0)),
                "git_tag_count": int(context.get("git_tag_count", 0)),
                "doi_count": int(context.get("doi_count", 0)),
                "external_validation_file_count": int(context.get("external_validation_file_count", 0)),
            },
            "governance": {
                "no_network_side_effects": True,
                "read_only_git_inspection": True,
                "traceability_enabled": True,
                "prometheus_export_enabled": True,
                "html_dashboard_export_enabled": True,
                "non_closure_compliant": True,
            },
            "diagnostics": {
                "publication_context_override_used": bool(override_used),
                "persist_requested": bool(persist),
                "closure_pressure_increase": 0.0,
                "warnings": [] if success else ["publication_traceability_below_certification_threshold"],
            },
            "state_path": None,
            "prometheus_path": None,
            "dashboard_path": None,
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            state_path = self.output_dir / "latest_scientific_publication_traceability.json"
            history_path = self.output_dir / "scientific_publication_traceability_history.jsonl"
            prometheus_path = self.output_dir / "scientific_publication_traceability.prom"
            dashboard_path = self.output_dir / "scientific_publication_traceability_dashboard.html"
            result["state_path"] = str(state_path)
            result["prometheus_path"] = str(prometheus_path)
            result["dashboard_path"] = str(dashboard_path)
            self._write_json(state_path, result)
            with history_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            self._write_prometheus(prometheus_path, result)
            self._write_dashboard(dashboard_path, result)

        return result


# Backward-compatible alias expected by simple ontology discovery tools.
ScientificPublicationTraceabilityPrimitive = ScientificPublicationTraceability
