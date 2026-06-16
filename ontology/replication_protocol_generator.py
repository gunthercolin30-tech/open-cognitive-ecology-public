
from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class ReplicationProtocolGenerator:
    """H5-R1: generate an independently executable replication protocol."""

    primitive = "replication_protocol_generator"
    refinement = "H5-R1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base = self.root / "external_validation" / self.primitive

    def step(self, protocol_context: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        context = self._build_context(protocol_context)
        scores = self._score(context)

        replication_protocol_score = round(
            0.22 * scores["h4_package_basis"]
            + 0.18 * scores["execution_clarity"]
            + 0.18 * scores["validation_matrix_quality"]
            + 0.14 * scores["artifact_integrity"]
            + 0.10 * scores["documentation_basis"]
            + 0.10 * scores["scientific_traceability"]
            + 0.08 * scores["governance_safety"],
            6,
        )
        external_replication_preparedness = round(
            0.55 * replication_protocol_score
            + 0.25 * scores["execution_clarity"]
            + 0.20 * scores["validation_matrix_quality"],
            6,
        )
        success = replication_protocol_score >= 0.70 and external_replication_preparedness >= 0.70

        protocol = self._make_protocol(context, scores, replication_protocol_score)
        checklist = self._make_checklist(context)
        execution_plan = self._make_execution_plan()
        validation_matrix = self._make_validation_matrix()

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": timestamp,
            "success": success,
            "replication_protocol_score": replication_protocol_score,
            "external_replication_preparedness": external_replication_preparedness,
            "component_scores": scores,
            "context_summary": self._context_summary(context),
            "protocol_step_count": len(protocol["steps"]),
            "checklist_item_count": len(checklist["items"]),
            "validation_matrix_item_count": len(validation_matrix["checks"]),
            "governance": {
                "no_network_side_effects": True,
                "no_credentials_required": True,
                "local_protocol_generation_only": True,
                "traceability_enabled": True,
                "reversibility_enabled": True,
                "non_closure_compliant": True,
            },
            "diagnostics": {
                "persist_requested": bool(persist),
                "protocol_context_override_used": protocol_context is not None,
                "warnings": self._warnings(context, scores),
                "closure_pressure_increase": 0.0,
            },
            "state_path": None,
            "prometheus_path": None,
            "dashboard_path": None,
            "protocol_json_path": None,
            "protocol_markdown_path": None,
            "checklist_path": None,
            "execution_plan_path": None,
            "validation_matrix_path": None,
        }

        if persist:
            paths = self._persist(result, protocol, checklist, execution_plan, validation_matrix)
            result.update(paths)
        return result

    def _build_context(self, override: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if override is not None:
            ctx = {
                "has_h4_package": False,
                "h4_success": False,
                "h4_score": 0.0,
                "has_package_zip": False,
                "has_package_manifest": False,
                "has_package_checksums": False,
                "has_quickstart": False,
                "has_validation_protocol": False,
                "has_readme": False,
                "has_requirements": False,
                "has_validation_main": False,
                "docs_file_count": 0,
                "external_validation_file_count": 0,
                "publication_archive_file_count": 0,
                "has_zenodo_json": False,
                "has_citation_cff": False,
                "has_public_remote": False,
                "h_success_count": 0,
            }
            ctx.update(dict(override))
            return ctx

        h4_base = self.root / "external_validation" / "open_source_replication_package_builder"
        h4_latest = self._read_json(h4_base / "latest_open_source_replication_package_builder.json")
        package_zip_path = Path(str(h4_latest.get("package_zip_path", ""))) if h4_latest.get("package_zip_path") else None

        package_members: List[str] = []
        if package_zip_path is not None and package_zip_path.exists() and zipfile.is_zipfile(package_zip_path):
            try:
                with zipfile.ZipFile(package_zip_path) as zf:
                    package_members = zf.namelist()
            except Exception:
                package_members = []

        h_latest_files = list((self.root / "external_validation").glob("*/latest_*.json"))
        h_success_count = 0
        for p in h_latest_files:
            if self._read_json(p).get("success") is True:
                h_success_count += 1

        return {
            "has_h4_package": h4_latest != {},
            "h4_success": h4_latest.get("success") is True,
            "h4_score": float(h4_latest.get("replication_package_score", 0.0) or 0.0),
            "has_package_zip": package_zip_path is not None and package_zip_path.exists(),
            "has_package_manifest": any("replication_package_manifest.json" in x for x in package_members) or (h4_base / "replication_package_manifest.json").exists(),
            "has_package_checksums": any("replication_package_checksums.json" in x for x in package_members) or (h4_base / "replication_package_checksums.json").exists(),
            "has_quickstart": any("replication_quickstart.md" in x for x in package_members) or (h4_base / "replication_quickstart.md").exists(),
            "has_validation_protocol": any("replication_validation_protocol.md" in x for x in package_members) or (h4_base / "replication_validation_protocol.md").exists(),
            "has_readme": (self.root / "README.md").exists(),
            "has_requirements": any(self.root.glob("requirements*.txt")),
            "has_validation_main": (self.root / "validation" / "main.py").exists(),
            "docs_file_count": self._count_files(self.root / "docs"),
            "external_validation_file_count": self._count_files(self.root / "external_validation"),
            "publication_archive_file_count": self._count_files(self.root / "publication_archive"),
            "has_zenodo_json": (self.root / ".zenodo.json").exists(),
            "has_citation_cff": (self.root / "CITATION.cff").exists(),
            "has_public_remote": "open-cognitive-ecology-public" in self._git_remote_text(),
            "h_success_count": h_success_count,
        }

    def _score(self, ctx: Mapping[str, Any]) -> Dict[str, float]:
        h4_basis = (
            0.30 * bool(ctx.get("has_h4_package"))
            + 0.30 * bool(ctx.get("h4_success"))
            + 0.25 * bool(ctx.get("has_package_zip"))
            + 0.15 * min(1.0, float(ctx.get("h4_score", 0.0) or 0.0))
        )
        execution_clarity = (
            0.25 * bool(ctx.get("has_package_manifest"))
            + 0.25 * bool(ctx.get("has_quickstart"))
            + 0.25 * bool(ctx.get("has_validation_protocol"))
            + 0.15 * bool(ctx.get("has_readme"))
            + 0.10 * bool(ctx.get("has_requirements"))
        )
        validation_matrix_quality = (
            0.40 * bool(ctx.get("has_validation_main"))
            + 0.25 * min(1.0, int(ctx.get("external_validation_file_count", 0) or 0) / 40.0)
            + 0.20 * min(1.0, int(ctx.get("h_success_count", 0) or 0) / 8.0)
            + 0.15 * bool(ctx.get("has_package_checksums"))
        )
        artifact_integrity = 0.55 * bool(ctx.get("has_package_checksums")) + 0.45 * bool(ctx.get("has_package_zip"))
        documentation_basis = 0.5 * min(1.0, int(ctx.get("docs_file_count", 0) or 0) / 6.0) + 0.5 * bool(ctx.get("has_readme"))
        scientific_traceability = (
            0.35 * bool(ctx.get("has_zenodo_json"))
            + 0.30 * bool(ctx.get("has_citation_cff"))
            + 0.20 * min(1.0, int(ctx.get("publication_archive_file_count", 0) or 0) / 10.0)
            + 0.15 * bool(ctx.get("has_public_remote"))
        )
        governance_safety = 1.0
        return {
            "h4_package_basis": round(h4_basis, 6),
            "execution_clarity": round(execution_clarity, 6),
            "validation_matrix_quality": round(validation_matrix_quality, 6),
            "artifact_integrity": round(artifact_integrity, 6),
            "documentation_basis": round(documentation_basis, 6),
            "scientific_traceability": round(scientific_traceability, 6),
            "governance_safety": round(governance_safety, 6),
        }

    def _make_protocol(self, ctx: Mapping[str, Any], scores: Mapping[str, float], total_score: float) -> Dict[str, Any]:
        return {
            "protocol_name": "Open Cognitive Ecology independent replication protocol",
            "version": self.refinement,
            "score": total_score,
            "scope": "local offline replication without credentials or network side effects",
            "steps": [
                {"step": 1, "name": "Clone or unpack replication package", "expected_evidence": "source tree and manifest available"},
                {"step": 2, "name": "Create isolated Python environment", "expected_evidence": "python environment created"},
                {"step": 3, "name": "Install requirements", "expected_evidence": "dependencies installed without critical errors"},
                {"step": 4, "name": "Run validation.main", "expected_evidence": "ontology_integration_report.txt with errors: 0"},
                {"step": 5, "name": "Run H0-H4 verification commands", "expected_evidence": "external validation metrics reproduced"},
                {"step": 6, "name": "Archive replication evidence", "expected_evidence": "logs, reports, checksums and environment captured"},
            ],
            "component_scores": dict(scores),
            "context_summary": self._context_summary(ctx),
        }

    def _make_checklist(self, ctx: Mapping[str, Any]) -> Dict[str, Any]:
        items = []
        for key in [
            "has_h4_package", "h4_success", "has_package_zip", "has_package_manifest",
            "has_package_checksums", "has_quickstart", "has_validation_protocol",
            "has_readme", "has_requirements", "has_validation_main", "has_zenodo_json",
            "has_citation_cff", "has_public_remote",
        ]:
            items.append({"item": key, "passed": bool(ctx.get(key))})
        return {"items": items}

    def _make_execution_plan(self) -> Dict[str, Any]:
        return {
            "commands": [
                "python3 -m venv .venv",
                "source .venv/bin/activate",
                "pip install -r requirements.txt",
                "python3 -m validation.main",
            ],
            "expected_result": "errors: 0 in ontology_integration_report.txt",
        }

    def _make_validation_matrix(self) -> Dict[str, Any]:
        checks = [
            {"check": "global_validation", "command": "python3 -m validation.main", "criterion": "errors: 0"},
            {"check": "package_integrity", "command": "verify checksums", "criterion": "all checksums match"},
            {"check": "external_validation_exports", "command": "inspect external_validation/", "criterion": "JSON, Prometheus and HTML exports exist"},
            {"check": "non_network_replication", "command": "review governance flags", "criterion": "no credentials required"},
        ]
        return {"checks": checks}

    def _persist(self, result: Dict[str, Any], protocol: Dict[str, Any], checklist: Dict[str, Any], execution_plan: Dict[str, Any], validation_matrix: Dict[str, Any]) -> Dict[str, str]:
        self.base.mkdir(parents=True, exist_ok=True)
        state_path = self.base / "latest_replication_protocol_generator.json"
        history_path = self.base / "replication_protocol_generator_history.jsonl"
        prom_path = self.base / "replication_protocol_generator.prom"
        dashboard_path = self.base / "replication_protocol_generator_dashboard.html"
        protocol_json_path = self.base / "replication_protocol.json"
        protocol_md_path = self.base / "replication_protocol.md"
        checklist_path = self.base / "replication_checklist.json"
        execution_plan_path = self.base / "replication_execution_plan.json"
        validation_matrix_path = self.base / "replication_validation_matrix.json"

        protocol_json_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
        protocol_md_path.write_text(self._protocol_markdown(protocol), encoding="utf-8")
        checklist_path.write_text(json.dumps(checklist, ensure_ascii=False, indent=2), encoding="utf-8")
        execution_plan_path.write_text(json.dumps(execution_plan, ensure_ascii=False, indent=2), encoding="utf-8")
        validation_matrix_path.write_text(json.dumps(validation_matrix, ensure_ascii=False, indent=2), encoding="utf-8")

        materialized = dict(result)
        materialized.update({
            "state_path": str(state_path),
            "prometheus_path": str(prom_path),
            "dashboard_path": str(dashboard_path),
            "protocol_json_path": str(protocol_json_path),
            "protocol_markdown_path": str(protocol_md_path),
            "checklist_path": str(checklist_path),
            "execution_plan_path": str(execution_plan_path),
            "validation_matrix_path": str(validation_matrix_path),
        })
        state_path.write_text(json.dumps(materialized, ensure_ascii=False, indent=2), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(materialized, ensure_ascii=False) + "\n")
        prom_path.write_text(self._prometheus(materialized), encoding="utf-8")
        dashboard_path.write_text(self._dashboard(materialized), encoding="utf-8")
        return {
            "state_path": str(state_path),
            "prometheus_path": str(prom_path),
            "dashboard_path": str(dashboard_path),
            "protocol_json_path": str(protocol_json_path),
            "protocol_markdown_path": str(protocol_md_path),
            "checklist_path": str(checklist_path),
            "execution_plan_path": str(execution_plan_path),
            "validation_matrix_path": str(validation_matrix_path),
        }

    def _protocol_markdown(self, protocol: Mapping[str, Any]) -> str:
        lines = ["# Open Cognitive Ecology Independent Replication Protocol", ""]
        lines.append("Scope: " + str(protocol.get("scope", "")))
        lines.append("")
        for step in protocol.get("steps", []):
            lines.append(str(step.get("step")) + ". " + str(step.get("name")))
            lines.append("   Evidence: " + str(step.get("expected_evidence")))
        lines.append("")
        lines.append("No credentials are required for this offline replication protocol.")
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Mapping[str, Any]) -> str:
        return "\n".join([
            "# TYPE oce_replication_protocol_score gauge",
            "oce_replication_protocol_score " + format(float(result.get("replication_protocol_score", 0.0)), ".6f"),
            "# TYPE oce_external_replication_preparedness gauge",
            "oce_external_replication_preparedness " + format(float(result.get("external_replication_preparedness", 0.0)), ".6f"),
            "# TYPE oce_replication_protocol_step_count gauge",
            "oce_replication_protocol_step_count " + str(int(result.get("protocol_step_count", 0))),
            "",
        ])

    def _dashboard(self, result: Mapping[str, Any]) -> str:
        rows = []
        for key, value in result.get("component_scores", {}).items():
            rows.append("<tr><td>" + str(key) + "</td><td>" + str(value) + "</td></tr>")
        return (
            "<!doctype html><html><head><meta charset='utf-8'><title>Replication Protocol Generator</title></head><body>"
            + "<h1>Replication Protocol Generator</h1>"
            + "<p>Success: " + str(result.get("success")) + "</p>"
            + "<p>Score: " + str(result.get("replication_protocol_score")) + "</p>"
            + "<table><tr><th>Component</th><th>Score</th></tr>"
            + "".join(rows)
            + "</table></body></html>"
        )

    def _context_summary(self, ctx: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "h4_score": ctx.get("h4_score"),
            "h_success_count": ctx.get("h_success_count"),
            "docs_file_count": ctx.get("docs_file_count"),
            "external_validation_file_count": ctx.get("external_validation_file_count"),
        }

    def _warnings(self, ctx: Mapping[str, Any], scores: Mapping[str, float]) -> List[str]:
        warnings: List[str] = []
        if not ctx.get("has_h4_package"):
            warnings.append("missing_h4_package")
        if not ctx.get("has_package_zip"):
            warnings.append("missing_replication_package_zip")
        if scores.get("execution_clarity", 0.0) < 0.5:
            warnings.append("low_execution_clarity")
        return warnings

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _count_files(self, path: Path) -> int:
        try:
            if path.exists():
                return sum(1 for p in path.rglob("*") if p.is_file())
        except Exception:
            return 0
        return 0

    def _git_remote_text(self) -> str:
        try:
            import subprocess
            out = subprocess.run(["git", "remote", "-v"], cwd=str(self.root), text=True, capture_output=True, timeout=5)
            return (out.stdout or "") + (out.stderr or "")
        except Exception:
            return ""


__all__ = ["ReplicationProtocolGenerator"]
