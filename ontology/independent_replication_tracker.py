from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class IndependentReplicationTracker:
    # H7-R1 tracker for independent external replications.
    # Consolidates H4-H6 artifacts into a local, credential-free tracking layer.
    # No GitHub, Zenodo, email, API or external network side effects are performed.

    primitive = "independent_replication_tracker"
    refinement = "H7-R1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base = self.root / "external_validation" / self.primitive

    def step(
        self,
        replication_context: Optional[Mapping[str, Any]] = None,
        persist: bool = True,
        fs_context: GovernedFilesystemEffectContext | None = None,
    ) -> Dict[str, Any]:
        timestamp = self._utc_now()
        context = self._context(replication_context)
        scores = self._scores(context)

        external_replication_count = int(context.get("external_replication_count", 0) or 0)
        successful_replication_count = int(context.get("successful_replication_count", 0) or 0)
        independent_validation_count = int(context.get("independent_validation_count", 0) or 0)
        replicator_count = int(context.get("replicator_count", 0) or 0)
        campaign_count = int(context.get("campaign_count", 0) or 0)

        replication_success_rate = self._ratio(successful_replication_count, external_replication_count)
        independent_reproduction_rate = self._ratio(successful_replication_count, max(replicator_count, external_replication_count))

        replication_tracking_score = self._round(
            0.22 * scores["h6_request_management_basis"]
            + 0.18 * scores["protocol_traceability"]
            + 0.16 * scores["package_traceability"]
            + 0.14 * scores["replicator_registry_completeness"]
            + 0.12 * scores["campaign_registry_completeness"]
            + 0.10 * scores["evidence_history_integrity"]
            + 0.05 * scores["dashboard_export_readiness"]
            + 0.03 * scores["non_closure_governance"]
        )

        # H7 can be operational even before real independent replications exist:
        # it validates the tracker, not external success. Real counts are allowed
        # to remain zero until H14-H15.
        success = bool(
            replication_tracking_score >= 0.70
            and scores["h6_request_management_basis"] >= 0.60
            and scores["protocol_traceability"] >= 0.60
            and scores["package_traceability"] >= 0.50
            and campaign_count >= 1
            and replicator_count >= 1
        )

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": timestamp,
            "success": success,
            "external_replication_count": external_replication_count,
            "successful_replication_count": successful_replication_count,
            "failed_replication_count": max(0, external_replication_count - successful_replication_count),
            "replication_success_rate": self._round(replication_success_rate),
            "independent_reproduction_rate": self._round(independent_reproduction_rate),
            "replicator_count": replicator_count,
            "campaign_count": campaign_count,
            "independent_validation_count": independent_validation_count,
            "replication_tracking_score": replication_tracking_score,
            "replicator_registry_score": scores["replicator_registry_completeness"],
            "campaign_registry_score": scores["campaign_registry_completeness"],
            "evidence_history_integrity": scores["evidence_history_integrity"],
            "dashboard_export_readiness": scores["dashboard_export_readiness"],
            "component_scores": scores,
            "component_details": {
                "h6": {
                    "success": bool(context.get("h6_success")),
                    "external_validation_request_management_score": float(context.get("h6_score", 0.0) or 0.0),
                    "request_campaign_registry_present": bool(context.get("has_h6_campaign_registry")),
                    "response_intake_schema_present": bool(context.get("has_h6_response_schema")),
                },
                "h5": {
                    "success": bool(context.get("h5_success")),
                    "replication_protocol_score": float(context.get("h5_score", 0.0) or 0.0),
                    "replication_protocol_present": bool(context.get("has_replication_protocol")),
                    "validation_matrix_present": bool(context.get("has_validation_matrix")),
                },
                "h4": {
                    "success": bool(context.get("h4_success")),
                    "replication_package_score": float(context.get("h4_score", 0.0) or 0.0),
                    "package_manifest_present": bool(context.get("has_package_manifest")),
                    "package_checksums_present": bool(context.get("has_package_checksums")),
                },
                "context_override_used": bool(replication_context),
            },
            "governance": {
                "no_network_side_effects": True,
                "no_credentials_required": True,
                "no_github_action_performed": True,
                "no_zenodo_action_performed": True,
                "no_email_sent": True,
                "offline_evidence_tracking_only": True,
                "traceability_enabled": True,
                "reversibility_enabled": True,
                "non_closure_compliant": True,
                "closure_pressure_increase": 0.0,
            },
            "diagnostics": {
                "warnings": self._warnings(context, scores, replication_tracking_score),
                "persist_requested": bool(persist),
                "replication_context_override_used": bool(replication_context),
                "real_external_campaign_required_later": True,
            },
            "state_path": None,
            "registry_path": None,
            "history_path": None,
            "dashboard_path": None,
            "prometheus_path": None,
        }

        if persist:
            self._persist(result, context, fs_context=fs_context)

        return result

    def _context(self, override: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if override is not None:
            ctx = self._empty_context()
            ctx.update(dict(override))
            return ctx

        h6_base = self.root / "external_validation" / "external_validation_request_manager"
        h5_base = self.root / "external_validation" / "replication_protocol_generator"
        h4_base = self.root / "external_validation" / "open_source_replication_package_builder"
        h0_base = self.root / "external_validation"

        h6_latest = self._read_json(h6_base / "latest_external_validation_request_manager.json")
        h5_latest = self._read_json(h5_base / "latest_replication_protocol_generator.json")
        h4_latest = self._read_json(h4_base / "latest_open_source_replication_package_builder.json")

        h6_success = bool(h6_latest.get("success"))
        h5_success = bool(h5_latest.get("success"))
        h4_success = bool(h4_latest.get("success"))

        candidate_replicator_count = int(h6_latest.get("candidate_replicator_count", 0) or 0)
        h6_campaign_count = int(h6_latest.get("campaign_count", 0) or 0)

        # Before real H14/H15 campaigns, H7 records prepared independent
        # replicator slots, but keeps external_replication_count at zero.
        return {
            "h6_success": h6_success,
            "h6_score": float(h6_latest.get("external_validation_request_management_score", 0.0) or 0.0),
            "h5_success": h5_success,
            "h5_score": float(h5_latest.get("replication_protocol_score", 0.0) or 0.0),
            "h4_success": h4_success,
            "h4_score": float(h4_latest.get("replication_package_score", 0.0) or 0.0),
            "has_h6_campaign_registry": (h6_base / "external_validation_request_campaign_registry.json").exists(),
            "has_h6_response_schema": (h6_base / "validation_response_intake_schema.json").exists(),
            "has_replication_protocol": (h5_base / "replication_protocol.json").exists() or (h5_base / "replication_protocol.md").exists(),
            "has_validation_matrix": (h5_base / "replication_validation_matrix.json").exists(),
            "has_package_manifest": (h4_base / "replication_package_manifest.json").exists(),
            "has_package_checksums": (h4_base / "replication_package_checksums.json").exists(),
            "has_external_validation_dashboard": (h0_base / "external_validation_dashboard" / "external_validation_dashboard.html").exists(),
            "external_validation_file_count": self._count_files(h0_base),
            "external_replication_count": int(self._existing_registry_counts().get("external_replication_count", 0)),
            "successful_replication_count": int(self._existing_registry_counts().get("successful_replication_count", 0)),
            "independent_validation_count": int(self._existing_registry_counts().get("independent_validation_count", 0)),
            "replicator_count": max(1 if h6_success else 0, candidate_replicator_count),
            "campaign_count": max(1 if h6_success else 0, h6_campaign_count),
            "history_record_count": self._history_line_count(self.base / "replication_campaign_history.jsonl"),
        }

    def _empty_context(self) -> Dict[str, Any]:
        return {
            "h6_success": False,
            "h6_score": 0.0,
            "h5_success": False,
            "h5_score": 0.0,
            "h4_success": False,
            "h4_score": 0.0,
            "has_h6_campaign_registry": False,
            "has_h6_response_schema": False,
            "has_replication_protocol": False,
            "has_validation_matrix": False,
            "has_package_manifest": False,
            "has_package_checksums": False,
            "has_external_validation_dashboard": False,
            "external_validation_file_count": 0,
            "external_replication_count": 0,
            "successful_replication_count": 0,
            "independent_validation_count": 0,
            "replicator_count": 0,
            "campaign_count": 0,
            "history_record_count": 0,
        }

    def _scores(self, context: Mapping[str, Any]) -> Dict[str, float]:
        h6_request_management_basis = self._clip(
            0.35 * float(bool(context.get("h6_success")))
            + 0.25 * float(context.get("h6_score", 0.0) or 0.0)
            + 0.15 * float(bool(context.get("has_h6_campaign_registry")))
            + 0.15 * float(bool(context.get("has_h6_response_schema")))
            + 0.10 * min(int(context.get("external_validation_file_count", 0) or 0), 60) / 60.0
        )
        protocol_traceability = self._clip(
            0.35 * float(bool(context.get("h5_success")))
            + 0.30 * float(context.get("h5_score", 0.0) or 0.0)
            + 0.20 * float(bool(context.get("has_replication_protocol")))
            + 0.15 * float(bool(context.get("has_validation_matrix")))
        )
        package_traceability = self._clip(
            0.35 * float(bool(context.get("h4_success")))
            + 0.30 * float(context.get("h4_score", 0.0) or 0.0)
            + 0.20 * float(bool(context.get("has_package_manifest")))
            + 0.15 * float(bool(context.get("has_package_checksums")))
        )
        replicator_registry_completeness = self._clip(
            0.35 * min(int(context.get("replicator_count", 0) or 0), 3) / 3.0
            + 0.30 * h6_request_management_basis
            + 0.20 * protocol_traceability
            + 0.15 * package_traceability
        )
        campaign_registry_completeness = self._clip(
            0.30 * min(int(context.get("campaign_count", 0) or 0), 3) / 3.0
            + 0.25 * h6_request_management_basis
            + 0.20 * protocol_traceability
            + 0.15 * float(bool(context.get("has_external_validation_dashboard")))
            + 0.10 * package_traceability
        )
        evidence_history_integrity = self._clip(
            0.30 * float(bool(context.get("has_h6_response_schema")))
            + 0.25 * float(bool(context.get("has_validation_matrix")))
            + 0.20 * min(int(context.get("history_record_count", 0) or 0) + 1, 10) / 10.0
            + 0.15 * h6_request_management_basis
            + 0.10 * package_traceability
        )
        dashboard_export_readiness = self._clip(
            0.40 * float(bool(context.get("has_external_validation_dashboard")))
            + 0.20 * h6_request_management_basis
            + 0.15 * protocol_traceability
            + 0.15 * package_traceability
            + 0.10 * min(int(context.get("external_validation_file_count", 0) or 0), 60) / 60.0
        )
        return {
            "h6_request_management_basis": self._round(h6_request_management_basis),
            "protocol_traceability": self._round(protocol_traceability),
            "package_traceability": self._round(package_traceability),
            "replicator_registry_completeness": self._round(replicator_registry_completeness),
            "campaign_registry_completeness": self._round(campaign_registry_completeness),
            "evidence_history_integrity": self._round(evidence_history_integrity),
            "dashboard_export_readiness": self._round(dashboard_export_readiness),
            "non_closure_governance": 0.95,
        }

    def _persist(self, result: Dict[str, Any], context: Mapping[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
        self.base.mkdir(parents=True, exist_ok=True)

        registry_path = self.base / "independent_replication_registry.json"
        history_path = self.base / "replication_campaign_history.jsonl"
        state_path = self.base / "latest_independent_replication_tracker.json"
        dashboard_path = self.base / "independent_replication_dashboard.html"
        prom_path = self.base / "independent_replication.prom"

        registry = self._build_registry(result, context)
        self._write_json(registry_path, registry, fs_context)

        result["state_path"] = str(state_path)
        result["registry_path"] = str(registry_path)
        result["history_path"] = str(history_path)
        result["dashboard_path"] = str(dashboard_path)
        result["prometheus_path"] = str(prom_path)

        self._write_json(state_path, result, fs_context)
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        dashboard_path.write_text(self._dashboard(result, registry), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")

    def _build_registry(self, result: Mapping[str, Any], context: Mapping[str, Any]) -> Dict[str, Any]:
        replicator_count = int(result.get("replicator_count", 0) or 0)
        replicators = []
        for idx in range(max(0, replicator_count)):
            replicators.append({
                "replicator_id": f"H7-REPLICATOR-{idx + 1:03d}",
                "status": "candidate_prepared" if int(result.get("external_replication_count", 0) or 0) == 0 else "evidence_pending",
                "independent": True,
                "credentials_required_now": False,
                "network_side_effects": False,
            })
        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "generated_at_utc": result.get("timestamp_utc"),
            "external_replication_count": result.get("external_replication_count"),
            "successful_replication_count": result.get("successful_replication_count"),
            "independent_validation_count": result.get("independent_validation_count"),
            "replication_tracking_score": result.get("replication_tracking_score"),
            "campaigns": [
                {
                    "campaign_id": "H7-INDEPENDENT-REPLICATION-CAMPAIGN-001",
                    "status": "prepared_not_launched",
                    "depends_on": ["H4", "H5", "H6"],
                    "real_external_launch_required_later": True,
                    "h12_h13_credentials_required": False,
                    "h14_real_campaign_required": True,
                }
            ],
            "replicators": replicators,
            "evidence_records": [],
            "governance": result.get("governance", {}),
            "source_context": {
                "h6_success": bool(context.get("h6_success")),
                "h5_success": bool(context.get("h5_success")),
                "h4_success": bool(context.get("h4_success")),
            },
        }

    def _prometheus(self, result: Mapping[str, Any]) -> str:
        metrics = {
            "oce_external_replication_count": result.get("external_replication_count", 0),
            "oce_successful_replication_count": result.get("successful_replication_count", 0),
            "oce_replication_success_rate": result.get("replication_success_rate", 0.0),
            "oce_independent_reproduction_rate": result.get("independent_reproduction_rate", 0.0),
            "oce_independent_replicator_count": result.get("replicator_count", 0),
            "oce_independent_replication_campaign_count": result.get("campaign_count", 0),
            "oce_independent_validation_count": result.get("independent_validation_count", 0),
            "oce_replication_tracking_score": result.get("replication_tracking_score", 0.0),
            "oce_replicator_registry_score": result.get("replicator_registry_score", 0.0),
            "oce_campaign_registry_score": result.get("campaign_registry_score", 0.0),
            "oce_evidence_history_integrity": result.get("evidence_history_integrity", 0.0),
        }
        lines: List[str] = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value)}")
        return "\n".join(lines) + "\n"

    def _dashboard(self, result: Mapping[str, Any], registry: Mapping[str, Any]) -> str:
        rows = []
        keys = [
            "success", "external_replication_count", "successful_replication_count",
            "replication_success_rate", "independent_reproduction_rate", "replicator_count",
            "campaign_count", "independent_validation_count", "replication_tracking_score",
        ]
        for key in keys:
            rows.append("<tr><td>" + self._escape(key) + "</td><td>" + self._escape(str(result.get(key))) + "</td></tr>")
        score_rows = []
        for key, value in result.get("component_scores", {}).items():
            score_rows.append("<tr><td>" + self._escape(str(key)) + "</td><td>" + self._escape(str(value)) + "</td></tr>")
        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Independent Replication Tracker</title>"
            "<style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ccc;padding:8px;text-align:left;}th{background:#eee;}</style>"
            "</head><body><h1>Independent Replication Tracker</h1>"
            "<p>Primitive: " + self._escape(str(result.get("primitive"))) + "</p>"
            "<p>Generated at UTC: " + self._escape(str(result.get("timestamp_utc"))) + "</p>"
            "<p>No external side effects: " + self._escape(str(result.get("governance", {}).get("no_network_side_effects"))) + "</p>"
            "<h2>Core metrics</h2><table><tr><th>Metric</th><th>Value</th></tr>" + "".join(rows) + "</table>"
            "<h2>Component scores</h2><table><tr><th>Component</th><th>Score</th></tr>" + "".join(score_rows) + "</table>"
            "<h2>Registry</h2><p>Campaigns: " + self._escape(str(len(registry.get("campaigns", [])))) + " | Replicators: " + self._escape(str(len(registry.get("replicators", [])))) + "</p>"
            "</body></html>"
        )

    def _warnings(self, context: Mapping[str, Any], scores: Mapping[str, float], tracking_score: float) -> List[str]:
        warnings: List[str] = []
        if not context.get("h6_success"):
            warnings.append("missing_h6_external_validation_request_management_success")
        if not context.get("h5_success"):
            warnings.append("missing_h5_replication_protocol_success")
        if not context.get("h4_success"):
            warnings.append("missing_h4_replication_package_success")
        if int(context.get("external_replication_count", 0) or 0) == 0:
            warnings.append("no_real_external_replication_recorded_yet")
        if tracking_score < 0.70:
            warnings.append("low_replication_tracking_score")
        if scores.get("replicator_registry_completeness", 0.0) < 0.70:
            warnings.append("replicator_registry_incomplete")
        return warnings

    def _existing_registry_counts(self) -> Dict[str, int]:
        registry = self._read_json(self.base / "independent_replication_registry.json")
        return {
            "external_replication_count": int(registry.get("external_replication_count", 0) or 0),
            "successful_replication_count": int(registry.get("successful_replication_count", 0) or 0),
            "independent_validation_count": int(registry.get("independent_validation_count", 0) or 0),
        }

    def _history_line_count(self, path: Path) -> int:
        try:
            if not path.exists():
                return 0
            return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        except Exception:
            return 0

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _write_json(self, path: Path, data: dict[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
        if fs_context is None:
            raise PermissionError("persisted JSON requires preissued filesystem effect context")
        payload = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        fs_context.execute_path("json_parent_create", "FS_CREATE_DIR", path.parent)
        fs_context.execute_path("json_write", "FS_WRITE_BYTES", path, payload)

    def _count_files(self, path: Path) -> int:
        try:
            if not path.exists():
                return 0
            return sum(1 for p in path.rglob("*") if p.is_file())
        except Exception:
            return 0

    @staticmethod
    def _ratio(num: int, den: int) -> float:
        if den <= 0:
            return 0.0
        return max(0.0, min(1.0, float(num) / float(den)))

    @staticmethod
    def _clip(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value), 6)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _escape(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

