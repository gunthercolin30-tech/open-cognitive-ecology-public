
from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class ExternalValidationRequestManager:
    """H6-R1 local manager for external validation requests.

    The module prepares, scores, records and exports external validation request
    campaigns. It is intentionally offline: no email, GitHub, Zenodo or network
    action is performed. The goal is to turn H4/H5 artifacts into a governed
    request management layer for later independent replication tracking.
    """

    primitive = "external_validation_request_manager"
    refinement = "H6-R1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base = self.root / "external_validation" / self.primitive

    def step(
        self,
        validation_request_context: Optional[Mapping[str, Any]] = None,
        persist: bool = True,
        fs_context: GovernedFilesystemEffectContext | None = None,
    ) -> Dict[str, Any]:
        timestamp = self._utc_now()
        context = self._context(validation_request_context)
        scores = self._scores(context)

        request_management_score = self._round(
            0.20 * scores["protocol_basis"]
            + 0.18 * scores["package_basis"]
            + 0.16 * scores["request_template_quality"]
            + 0.14 * scores["campaign_governance"]
            + 0.12 * scores["candidate_replicator_readiness"]
            + 0.10 * scores["evidence_intake_readiness"]
            + 0.06 * scores["traceability"]
            + 0.04 * scores["non_closure_governance"]
        )

        external_validation_request_readiness = self._round(
            0.45 * request_management_score
            + 0.25 * scores["candidate_replicator_readiness"]
            + 0.20 * scores["evidence_intake_readiness"]
            + 0.10 * scores["traceability"]
        )

        campaign_count = int(context.get("campaign_count", 1 if context.get("h5_success") else 0))
        candidate_replicator_count = int(context.get("candidate_replicator_count", 3 if context.get("h5_success") else 0))
        request_template_count = int(context.get("request_template_count", 4 if context.get("h5_success") else 0))

        success = (
            request_management_score >= 0.70
            and external_validation_request_readiness >= 0.70
            and context.get("h5_success", False)
            and context.get("has_replication_protocol", False)
            and context.get("has_replication_package", False)
        )

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": timestamp,
            "success": bool(success),
            "external_validation_request_management_score": request_management_score,
            "external_validation_request_readiness": external_validation_request_readiness,
            "request_template_completeness": scores["request_template_quality"],
            "campaign_governance_score": scores["campaign_governance"],
            "candidate_replicator_readiness": scores["candidate_replicator_readiness"],
            "evidence_intake_readiness": scores["evidence_intake_readiness"],
            "traceability_score": scores["traceability"],
            "campaign_count": campaign_count,
            "candidate_replicator_count": candidate_replicator_count,
            "request_template_count": request_template_count,
            "component_scores": scores,
            "component_details": {
                "h5": {
                    "success": bool(context.get("h5_success")),
                    "protocol_score": float(context.get("h5_score", 0.0)),
                    "has_replication_protocol": bool(context.get("has_replication_protocol")),
                    "has_execution_plan": bool(context.get("has_execution_plan")),
                    "has_validation_matrix": bool(context.get("has_validation_matrix")),
                },
                "h4": {
                    "success": bool(context.get("h4_success")),
                    "package_score": float(context.get("h4_score", 0.0)),
                    "has_package_zip": bool(context.get("has_package_zip")),
                    "has_package_manifest": bool(context.get("has_package_manifest")),
                    "has_package_checksums": bool(context.get("has_package_checksums")),
                },
                "request_management": {
                    "campaign_count": campaign_count,
                    "candidate_replicator_count": candidate_replicator_count,
                    "request_template_count": request_template_count,
                    "external_validation_file_count": int(context.get("external_validation_file_count", 0)),
                },
                "context_override_used": bool(validation_request_context),
            },
            "governance": {
                "no_network_side_effects": True,
                "no_credentials_required": True,
                "no_email_sent": True,
                "no_external_request_sent": True,
                "no_github_issue_created": True,
                "no_zenodo_action_performed": True,
                "traceability_enabled": True,
                "reversibility_enabled": True,
                "non_closure_compliant": True,
            },
            "diagnostics": {
                "warnings": self._warnings(context, scores),
                "closure_pressure_increase": 0.0,
                "persist_requested": bool(persist),
                "validation_request_context_override_used": bool(validation_request_context),
            },
            "request_campaign_registry_path": None,
            "external_validation_request_templates_path": None,
            "replicator_candidate_matrix_path": None,
            "validation_response_intake_schema_path": None,
            "state_path": None,
            "prometheus_path": None,
            "dashboard_path": None,
        }

        if persist:
            self._persist(result, fs_context=fs_context)

        return result

    def _context(self, override: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if override is not None:
            ctx = {
                "h5_success": False,
                "h5_score": 0.0,
                "h4_success": False,
                "h4_score": 0.0,
                "has_replication_protocol": False,
                "has_replication_protocol_md": False,
                "has_replication_checklist": False,
                "has_execution_plan": False,
                "has_validation_matrix": False,
                "has_replication_package": False,
                "has_package_zip": False,
                "has_package_manifest": False,
                "has_package_checksums": False,
                "has_readme": False,
                "has_citation_cff": False,
                "has_zenodo_json": False,
                "has_external_validation_dashboard": False,
                "external_validation_file_count": 0,
                "candidate_replicator_count": 0,
                "request_template_count": 0,
                "campaign_count": 0,
                "has_public_remote": False,
                "h_success_count": 0,
            }
            ctx.update(dict(override))
            return ctx

        h5_base = self.root / "external_validation" / "replication_protocol_generator"
        h4_base = self.root / "external_validation" / "open_source_replication_package_builder"
        dashboard_base = self.root / "external_validation" / "external_validation_dashboard"

        h5_latest = self._read_json(h5_base / "latest_replication_protocol_generator.json")
        h4_latest = self._read_json(h4_base / "latest_open_source_replication_package_builder.json")

        h5_success = bool(h5_latest.get("success"))
        h4_success = bool(h4_latest.get("success"))

        protocol_score = float(h5_latest.get("replication_protocol_score", 0.0) or 0.0)
        package_score = float(h4_latest.get("replication_package_score", 0.0) or 0.0)

        git_remotes = self._git_remotes_text()

        return {
            "h5_success": h5_success,
            "h5_score": protocol_score,
            "h4_success": h4_success,
            "h4_score": package_score,
            "has_replication_protocol": (h5_base / "replication_protocol.json").exists(),
            "has_replication_protocol_md": (h5_base / "replication_protocol.md").exists(),
            "has_replication_checklist": (h5_base / "replication_checklist.json").exists(),
            "has_execution_plan": (h5_base / "replication_execution_plan.json").exists(),
            "has_validation_matrix": (h5_base / "replication_validation_matrix.json").exists(),
            "has_replication_package": bool(h4_latest.get("package_zip_path")) and Path(str(h4_latest.get("package_zip_path"))).exists(),
            "has_package_zip": bool(h4_latest.get("package_zip_path")) and Path(str(h4_latest.get("package_zip_path"))).exists(),
            "has_package_manifest": (h4_base / "replication_package_manifest.json").exists(),
            "has_package_checksums": (h4_base / "replication_package_checksums.json").exists(),
            "has_readme": (self.root / "README.md").exists(),
            "has_citation_cff": (self.root / "CITATION.cff").exists(),
            "has_zenodo_json": (self.root / ".zenodo.json").exists(),
            "has_external_validation_dashboard": (dashboard_base / "external_validation_dashboard.html").exists(),
            "external_validation_file_count": self._count_files(self.root / "external_validation"),
            "candidate_replicator_count": 3 if h5_success else 0,
            "request_template_count": 4 if h5_success else 0,
            "campaign_count": 1 if (h5_success and h4_success) else 0,
            "has_public_remote": "open-cognitive-ecology-public" in git_remotes,
            "h_success_count": self._h_success_count(),
        }

    def _scores(self, context: Mapping[str, Any]) -> Dict[str, float]:
        protocol_basis = self._clip(
            0.25 * float(bool(context.get("h5_success")))
            + 0.25 * float(bool(context.get("has_replication_protocol")))
            + 0.15 * float(bool(context.get("has_replication_protocol_md")))
            + 0.15 * float(bool(context.get("has_execution_plan")))
            + 0.10 * float(bool(context.get("has_validation_matrix")))
            + 0.10 * float(context.get("h5_score", 0.0))
        )

        package_basis = self._clip(
            0.25 * float(bool(context.get("h4_success")))
            + 0.20 * float(bool(context.get("has_replication_package")))
            + 0.20 * float(bool(context.get("has_package_manifest")))
            + 0.15 * float(bool(context.get("has_package_checksums")))
            + 0.20 * float(context.get("h4_score", 0.0))
        )

        request_template_quality = self._clip(
            min(int(context.get("request_template_count", 0)), 4) / 4.0
            * (0.65 + 0.35 * protocol_basis)
        )

        campaign_governance = self._clip(
            0.30 * float(int(context.get("campaign_count", 0)) > 0)
            + 0.20 * float(bool(context.get("has_readme")))
            + 0.15 * float(bool(context.get("has_citation_cff")))
            + 0.15 * float(bool(context.get("has_zenodo_json")))
            + 0.10 * float(bool(context.get("has_public_remote")))
            + 0.10 * min(int(context.get("h_success_count", 0)), 6) / 6.0
        )

        candidate_replicator_readiness = self._clip(
            min(int(context.get("candidate_replicator_count", 0)), 3) / 3.0
            * (0.55 + 0.25 * package_basis + 0.20 * protocol_basis)
        )

        evidence_intake_readiness = self._clip(
            0.25 * float(bool(context.get("has_replication_checklist")))
            + 0.25 * float(bool(context.get("has_validation_matrix")))
            + 0.20 * float(bool(context.get("has_external_validation_dashboard")))
            + 0.15 * min(int(context.get("external_validation_file_count", 0)), 40) / 40.0
            + 0.15 * package_basis
        )

        traceability = self._clip(
            0.25 * float(bool(context.get("has_public_remote")))
            + 0.25 * float(bool(context.get("has_citation_cff")))
            + 0.20 * float(bool(context.get("has_zenodo_json")))
            + 0.15 * min(int(context.get("h_success_count", 0)), 6) / 6.0
            + 0.15 * evidence_intake_readiness
        )

        non_closure_governance = 0.95

        return {
            "protocol_basis": self._round(protocol_basis),
            "package_basis": self._round(package_basis),
            "request_template_quality": self._round(request_template_quality),
            "campaign_governance": self._round(campaign_governance),
            "candidate_replicator_readiness": self._round(candidate_replicator_readiness),
            "evidence_intake_readiness": self._round(evidence_intake_readiness),
            "traceability": self._round(traceability),
            "non_closure_governance": self._round(non_closure_governance),
        }

    def _persist(self, result: Dict[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
        self.base.mkdir(parents=True, exist_ok=True)

        request_campaign_registry = self._request_campaign_registry(result)
        request_templates = self._request_templates(result)
        candidate_matrix = self._candidate_matrix(result)
        response_schema = self._response_intake_schema(result)

        campaign_path = self.base / "external_validation_request_campaign_registry.json"
        templates_path = self.base / "external_validation_request_templates.json"
        candidate_path = self.base / "replicator_candidate_matrix.json"
        response_schema_path = self.base / "validation_response_intake_schema.json"

        self._write_json(campaign_path, request_campaign_registry, fs_context)
        self._write_json(templates_path, request_templates, fs_context)
        self._write_json(candidate_path, candidate_matrix, fs_context)
        self._write_json(response_schema_path, response_schema, fs_context)

        result["request_campaign_registry_path"] = str(campaign_path)
        result["external_validation_request_templates_path"] = str(templates_path)
        result["replicator_candidate_matrix_path"] = str(candidate_path)
        result["validation_response_intake_schema_path"] = str(response_schema_path)

        state_path = self.base / "latest_external_validation_request_manager.json"
        history_path = self.base / "external_validation_request_manager_history.jsonl"
        prom_path = self.base / "external_validation_request_manager.prom"
        dashboard_path = self.base / "external_validation_request_manager_dashboard.html"

        result["state_path"] = str(state_path)
        result["prometheus_path"] = str(prom_path)
        result["dashboard_path"] = str(dashboard_path)

        self._write_json(state_path, result, fs_context)
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        dashboard_path.write_text(self._dashboard(result), encoding="utf-8")

    def _request_campaign_registry(self, result: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "campaigns": [
                {
                    "campaign_id": "H6-CAMPAIGN-001",
                    "status": "prepared_not_sent",
                    "purpose": "independent replication of Open Cognitive Ecology",
                    "replication_protocol": "external_validation/replication_protocol_generator/replication_protocol.md",
                    "replication_package": "external_validation/open_source_replication_package_builder/",
                    "evidence_intake_schema": "validation_response_intake_schema.json",
                    "network_side_effects": False,
                    "credentials_required": False,
                }
            ],
            "score": result.get("external_validation_request_management_score"),
            "generated_at_utc": result.get("timestamp_utc"),
        }

    def _request_templates(self, result: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "templates": [
                {"template_id": "H6-TEMPLATE-EMAIL", "channel": "email", "status": "draft_only", "subject": "Independent replication request for Open Cognitive Ecology"},
                {"template_id": "H6-TEMPLATE-GITHUB-ISSUE", "channel": "github_issue", "status": "draft_only", "title": "Independent replication request"},
                {"template_id": "H6-TEMPLATE-ACADEMIC-REVIEW", "channel": "academic_review", "status": "draft_only"},
                {"template_id": "H6-TEMPLATE-COMMUNITY-NODE", "channel": "community_node", "status": "draft_only"},
            ],
            "score": result.get("request_template_completeness"),
        }

    def _candidate_matrix(self, result: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "candidate_categories": [
                {"category": "academic_replicator", "required_capabilities": ["python", "git", "scientific_reporting"], "credential_required_now": False},
                {"category": "open_source_replicator", "required_capabilities": ["git", "github", "ci"], "credential_required_now": False},
                {"category": "independent_compute_node", "required_capabilities": ["linux_or_macos", "python_env", "artifact_upload"], "credential_required_now": False},
            ],
            "candidate_replicator_count": result.get("candidate_replicator_count"),
            "score": result.get("candidate_replicator_readiness"),
        }

    def _response_intake_schema(self, result: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "schema_name": "external_validation_response_intake",
            "required_fields": [
                "replicator_id", "timestamp_utc", "repository_url", "commit_or_release",
                "environment", "commands_executed", "validation_result", "errors",
                "artifacts", "notes",
            ],
            "evidence_types": ["terminal_log", "validation_report", "dashboard_export", "prometheus_export", "replication_package_checksum"],
            "score": result.get("evidence_intake_readiness"),
        }

    def _prometheus(self, result: Mapping[str, Any]) -> str:
        metrics = {
            "oce_external_validation_request_management_score": result.get("external_validation_request_management_score", 0.0),
            "oce_external_validation_request_readiness": result.get("external_validation_request_readiness", 0.0),
            "oce_request_template_completeness": result.get("request_template_completeness", 0.0),
            "oce_candidate_replicator_readiness": result.get("candidate_replicator_readiness", 0.0),
            "oce_evidence_intake_readiness": result.get("evidence_intake_readiness", 0.0),
            "oce_validation_request_campaign_count": result.get("campaign_count", 0),
            "oce_candidate_replicator_count": result.get("candidate_replicator_count", 0),
        }
        lines: List[str] = []
        for name, value in metrics.items():
            lines.append("# TYPE " + name + " gauge")
            lines.append(name + " " + str(float(value)))
        return "\n".join(lines) + "\n"

    def _dashboard(self, result: Mapping[str, Any]) -> str:
        rows = []
        for key, value in result.get("component_scores", {}).items():
            rows.append("<tr><td>" + self._escape(str(key)) + "</td><td>" + self._escape(str(value)) + "</td></tr>")
        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>External Validation Request Manager</title></head><body>"
            "<h1>External Validation Request Manager</h1>"
            "<p>Primitive: " + self._escape(str(result.get("primitive"))) + "</p>"
            "<p>Success: " + self._escape(str(result.get("success"))) + "</p>"
            "<p>Request management score: " + self._escape(str(result.get("external_validation_request_management_score"))) + "</p>"
            "<p>External validation request readiness: " + self._escape(str(result.get("external_validation_request_readiness"))) + "</p>"
            "<p>No network side effects: " + self._escape(str(result.get("governance", {}).get("no_network_side_effects"))) + "</p>"
            "<h2>Component scores</h2><table><tr><th>Component</th><th>Score</th></tr>"
            + "".join(rows)
            + "</table></body></html>"
        )

    def _warnings(self, context: Mapping[str, Any], scores: Mapping[str, float]) -> List[str]:
        warnings: List[str] = []
        if not context.get("h5_success"):
            warnings.append("missing_h5_protocol_success")
        if not context.get("h4_success"):
            warnings.append("missing_h4_package_success")
        if scores.get("request_template_quality", 0.0) < 0.5:
            warnings.append("low_request_template_quality")
        if scores.get("candidate_replicator_readiness", 0.0) < 0.5:
            warnings.append("low_candidate_replicator_readiness")
        if not context.get("has_public_remote"):
            warnings.append("missing_public_remote")
        return warnings

    def _h_success_count(self) -> int:
        count = 0
        names = [
            ("open_source_repository_governance", "latest_open_source_repository_governance.json"),
            ("open_source_replication_readiness", "latest_open_source_replication_readiness.json"),
            ("scientific_publication_traceability", "latest_scientific_publication_traceability.json"),
            ("external_validation_dashboard", "latest_external_validation_dashboard.json"),
            ("scientific_publication_registry", "latest_scientific_publication_registry.json"),
            ("github_release_orchestrator", "latest_github_release_orchestrator.json"),
            ("zenodo_publication_orchestrator", "latest_zenodo_publication_orchestrator.json"),
            ("open_source_replication_package_builder", "latest_open_source_replication_package_builder.json"),
            ("replication_protocol_generator", "latest_replication_protocol_generator.json"),
        ]
        for folder, fname in names:
            data = self._read_json(self.root / "external_validation" / folder / fname)
            if data.get("success"):
                count += 1
        return count

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _git_remotes_text(self) -> str:
        try:
            from ontology.governed_git_exact_process import governed_git_subprocess as subprocess
            proc = subprocess.run(
                ["git", "remote", "-v"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return (proc.stdout or "") + "\n" + (proc.stderr or "")
        except Exception:
            return ""

    def _count_files(self, path: Path) -> int:
        try:
            if not path.exists():
                return 0
            return sum(1 for p in path.rglob("*") if p.is_file())
        except Exception:
            return 0

    def _write_json(self, path: Path, data: dict[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
        if fs_context is None:
            raise PermissionError("persisted JSON requires preissued filesystem effect context")
        payload = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        fs_context.execute_path("json_parent_create", "FS_CREATE_DIR", path.parent)
        fs_context.execute_path("json_write", "FS_WRITE_BYTES", path, payload)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value), 6)

    @staticmethod
    def _clip(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _escape(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
