
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExternalInfluenceDashboard:
    'Dashboard for governed external influence.\n\nThis primitive consolidates the functional state of the governed external\ninfluence regime without giving external sources any direct write authority.\nIt exports HTML, JSON, Prometheus and Grafana-compatible artifacts.\n'

    primitive = "EXTERNAL_INFLUENCE_DASHBOARD"

    dependencies = [
        "external_influence_gap_analysis",
        "external_priority_influence_layer",
        "external_commit_traceability_hook",
        "external_governance_amendment_gate",
        "external_influence_impact_monitor",
    ]

    export_dir = Path("external_influence_dashboard")
    filesystem_effect_context_provider = None

    def _clamp(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        return max(0.0, min(1.0, number))

    def _state(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        payload = inputs or {}
        state = payload.get("component_state", {})
        return state if isinstance(state, dict) else {}

    def _impact(self, state: dict[str, Any]) -> dict[str, Any]:
        impact = state.get("impact_monitor", {})
        return impact if isinstance(impact, dict) else {}

    def _count(self, data: dict[str, Any], key: str) -> int:
        try:
            return max(0, int(data.get(key, 0)))
        except (TypeError, ValueError):
            return 0

    def _extract_metrics(self, state: dict[str, Any]) -> dict[str, Any]:
        gap = state.get("gap_analysis", {}) if isinstance(state.get("gap_analysis", {}), dict) else {}
        priority = state.get("priority_layer", {}) if isinstance(state.get("priority_layer", {}), dict) else {}
        commit = state.get("commit_traceability", {}) if isinstance(state.get("commit_traceability", {}), dict) else {}
        governance = state.get("governance_amendment", {}) if isinstance(state.get("governance_amendment", {}), dict) else {}
        impact = self._impact(state)

        coverage = self._clamp(gap.get("overall_external_influence_coverage", 0.0))
        effective_priority = self._clamp(priority.get("effective_priority", 0.0))
        auditability = self._clamp(commit.get("auditability_score", 0.0))
        governance_risk = self._clamp(governance.get("governance_risk_score", 0.5), 0.5)
        governance_health = 1.0 - governance_risk

        effectiveness = self._clamp(impact.get("external_influence_effectiveness", 0.0))
        success_rate = self._clamp(impact.get("external_influence_success_rate", 0.0))
        reversibility = self._clamp(impact.get("external_influence_reversibility_index", 0.0))

        counts = {
            "knowledge_influence_count": self._count(impact, "knowledge_influence_count"),
            "decision_influence_count": self._count(impact, "decision_influence_count"),
            "priority_influence_count": self._count(impact, "priority_influence_count"),
            "revision_influence_count": self._count(impact, "revision_influence_count"),
            "commit_influence_count": self._count(impact, "commit_influence_count"),
            "governance_influence_count": self._count(impact, "governance_influence_count"),
            "rollback_count": self._count(impact, "rollback_count"),
            "failed_adoption_count": self._count(impact, "failed_adoption_count"),
        }

        dashboard_health_score = round((
            coverage * 0.15
            + effective_priority * 0.10
            + auditability * 0.15
            + governance_health * 0.15
            + effectiveness * 0.20
            + success_rate * 0.15
            + reversibility * 0.10
        ), 6)

        return {
            "overall_external_influence_coverage": coverage,
            "effective_priority": effective_priority,
            "auditability_score": auditability,
            "governance_risk_score": governance_risk,
            "external_influence_effectiveness": effectiveness,
            "external_influence_success_rate": success_rate,
            "external_influence_reversibility_index": reversibility,
            "dashboard_health_score": dashboard_health_score,
            **counts,
        }

    def _decision(self, metrics: dict[str, Any], direct_write_requested: bool) -> str:
        if direct_write_requested:
            return "dashboard_risk"
        if metrics["external_influence_success_rate"] < 0.5:
            return "dashboard_risk"
        if metrics["external_influence_effectiveness"] < 0.5:
            return "dashboard_risk"
        if metrics["dashboard_health_score"] >= 0.75:
            return "dashboard_healthy"
        if metrics["dashboard_health_score"] >= 0.45:
            return "dashboard_warning"
        return "dashboard_risk"

    def _html(self, result: dict[str, Any]) -> str:
        rows = []
        for key in [
            "dashboard_health_score",
            "dashboard_decision",
            "overall_external_influence_coverage",
            "effective_priority",
            "auditability_score",
            "governance_risk_score",
            "external_influence_effectiveness",
            "external_influence_success_rate",
            "external_influence_reversibility_index",
            "knowledge_influence_count",
            "decision_influence_count",
            "priority_influence_count",
            "revision_influence_count",
            "commit_influence_count",
            "governance_influence_count",
            "rollback_count",
            "failed_adoption_count",
        ]:
            rows.append(f"<tr><td>{key}</td><td>{result.get(key)}</td></tr>")
        table = "\n".join(rows)
        return (
            "<!doctype html>\n"
            "<html><head><meta charset='utf-8'>"
            "<title>External Influence Dashboard</title>"
            "<style>body{font-family:Arial,sans-serif;margin:40px;}"
            "table{border-collapse:collapse;width:100%;}"
            "td,th{border:1px solid #ccc;padding:8px;text-align:left;}"
            "th{background:#f0f0f0;}</style></head>"
            "<body><h1>External Influence Dashboard</h1>"
            "<p>Governed external influence regime: sources, adoptions, priorities, revisions, commits, governance, impacts and rollbacks.</p>"
            "<table><tr><th>Metric</th><th>Value</th></tr>"
            f"{table}"
            "</table></body></html>"
        )

    def _prometheus(self, result: dict[str, Any]) -> str:
        keys = [
            "dashboard_health_score",
            "overall_external_influence_coverage",
            "effective_priority",
            "auditability_score",
            "governance_risk_score",
            "external_influence_effectiveness",
            "external_influence_success_rate",
            "external_influence_reversibility_index",
            "knowledge_influence_count",
            "decision_influence_count",
            "priority_influence_count",
            "revision_influence_count",
            "commit_influence_count",
            "governance_influence_count",
            "rollback_count",
            "failed_adoption_count",
        ]
        lines = []
        for key in keys:
            metric = "oce_external_influence_" + key
            lines.append(f"# TYPE {metric} gauge")
            lines.append(f"{metric} {result.get(key, 0)}")
        return "\n".join(lines) + "\n"

    def _grafana(self, result: dict[str, Any]) -> dict[str, Any]:
        panels = []
        titles = [
            "dashboard_health_score",
            "external_influence_effectiveness",
            "external_influence_success_rate",
            "external_influence_reversibility_index",
            "governance_risk_score",
            "rollback_count",
        ]
        for idx, title in enumerate(titles, start=1):
            panels.append({
                "id": idx,
                "type": "stat",
                "title": title,
                "targets": [{"expr": "oce_external_influence_" + title}],
            })
        return {
            "title": "Open Cognitive Ecology - External Influence Dashboard",
            "schemaVersion": 39,
            "version": 1,
            "refresh": "30s",
            "panels": panels,
        }

    def _dashboard_effect(self, operation: str, path: Path, payload: bytes | None = None) -> None:
        provider = getattr(self, "filesystem_effect_context_provider", None)
        if not callable(provider):
            raise PermissionError("preissued_dashboard_effect_context_provider_required")
        slot = "macro04_external_dashboard_" + operation.lower()
        context = provider(operation, path, slot)
        if context is None:
            raise PermissionError("preissued_dashboard_effect_context_required")
        if context.remaining() != {slot: 1}:
            raise PermissionError("exact_dashboard_effect_authority_required")
        context.begin()
        context.execute_path(slot, operation, path, payload=payload)
        if context.remaining() != {slot: 0}:
            raise RuntimeError("dashboard_authority_not_consumed")

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        # Directory creation is itself governed; no implicit ambient mkdir.
        if not self.export_dir.is_dir():
            self._dashboard_effect("FS_CREATE_DIRS", self.export_dir)
        json_path = self.export_dir / "latest_external_influence_dashboard.json"
        html_path = self.export_dir / "external_influence_dashboard.html"
        prometheus_path = self.export_dir / "external_influence_dashboard.prom"
        grafana_path = self.export_dir / "external_influence_dashboard_grafana.json"
        # Refuse missing authority before publishing any file. Each context is
        # single-use; this is not an all-or-nothing multi-file transaction.
        paths = (json_path, html_path, prometheus_path, grafana_path)
        payloads = (
            json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8"),
            self._html(result).encode("utf-8"),
            self._prometheus(result).encode("utf-8"),
            json.dumps(self._grafana(result), indent=2, ensure_ascii=False).encode("utf-8"),
        )
        for path, payload in zip(paths, payloads):
            self._dashboard_effect("FS_WRITE_REPLACE_BYTES", path, payload)
        return {
            "json_export_path": str(json_path),
            "html_export_path": str(html_path),
            "prometheus_export_path": str(prometheus_path),
            "grafana_export_path": str(grafana_path),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        payload = inputs or {}
        state = self._state(payload)
        direct_write_requested = bool(payload.get("direct_write_requested", False))
        metrics = self._extract_metrics(state)
        decision = self._decision(metrics, direct_write_requested)

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "dashboard_decision": decision,
            "exports_generated": False,
            "direct_write_requested": direct_write_requested,
            "direct_write_allowed": False,
            "visualized_domains": [
                "sources",
                "adoptions",
                "priorities",
                "revisions",
                "commits",
                "governance",
                "impacts",
                "rollbacks",
            ],
            "integration_dependencies": list(self.dependencies),
            "json_export_path": None,
            "html_export_path": None,
            "prometheus_export_path": None,
            "grafana_export_path": None,
            **metrics,
        }

        if persist:
            result.update(self._persist(result))
            result["exports_generated"] = True
            self._dashboard_effect("FS_WRITE_REPLACE_BYTES", Path(result["json_export_path"]), json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8"))

        return result
