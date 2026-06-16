from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


ROOT = Path.home() / "open-cognitive-ecology"


class ExternalValidationDashboard:
    """H0.4-R1 unified external validation dashboard.

    Aggregates H0.1, H0.2 and H0.3 outputs into a single local,
    read-only, non-networked external validation dashboard.
    """

    primitive = "external_validation_dashboard"
    refinement = "H0.4-R1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.base = self.root / "external_validation"
        self.out_dir = self.base / "external_validation_dashboard"

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _score(self, value: Any, default: float = 0.0) -> float:
        try:
            x = float(value)
        except Exception:
            x = default
        return max(0.0, min(1.0, x))

    def _read_baseline_context(self) -> Dict[str, Any]:
        h01 = self._load_json(
            self.base
            / "open_source_repository_governance"
            / "latest_open_source_repository_governance.json"
        )
        h02 = self._load_json(
            self.base
            / "open_source_replication_readiness"
            / "latest_open_source_replication_readiness.json"
        )
        h03 = self._load_json(
            self.base
            / "scientific_publication_traceability"
            / "latest_scientific_publication_traceability.json"
        )

        return {
            "h0_1": {
                "present": bool(h01),
                "success": bool(h01.get("success")),
                "repository_governance_score": self._score(h01.get("repository_governance_score")),
                "github_governance_score": self._score(h01.get("github_governance_score")),
                "external_validation_readiness": self._score(h01.get("external_validation_readiness")),
            },
            "h0_2": {
                "present": bool(h02),
                "success": bool(h02.get("success")),
                "replication_readiness_score": self._score(h02.get("replication_readiness_score")),
                "external_reproduction_preparedness": self._score(h02.get("external_reproduction_preparedness")),
                "replication_package_completeness": self._score(h02.get("replication_package_completeness")),
            },
            "h0_3": {
                "present": bool(h03),
                "success": bool(h03.get("success")),
                "publication_traceability_score": self._score(h03.get("publication_traceability_score")),
                "publication_confidence_index": self._score(h03.get("publication_confidence_index")),
                "git_publication_traceability_score": self._score(h03.get("git_publication_traceability_score")),
            },
        }

    def _normalize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "h0_1": {
                "present": bool(context.get("h0_1", {}).get("present", False)),
                "success": bool(context.get("h0_1", {}).get("success", False)),
                "repository_governance_score": self._score(context.get("h0_1", {}).get("repository_governance_score")),
                "github_governance_score": self._score(context.get("h0_1", {}).get("github_governance_score")),
                "external_validation_readiness": self._score(context.get("h0_1", {}).get("external_validation_readiness")),
            },
            "h0_2": {
                "present": bool(context.get("h0_2", {}).get("present", False)),
                "success": bool(context.get("h0_2", {}).get("success", False)),
                "replication_readiness_score": self._score(context.get("h0_2", {}).get("replication_readiness_score")),
                "external_reproduction_preparedness": self._score(context.get("h0_2", {}).get("external_reproduction_preparedness")),
                "replication_package_completeness": self._score(context.get("h0_2", {}).get("replication_package_completeness")),
            },
            "h0_3": {
                "present": bool(context.get("h0_3", {}).get("present", False)),
                "success": bool(context.get("h0_3", {}).get("success", False)),
                "publication_traceability_score": self._score(context.get("h0_3", {}).get("publication_traceability_score")),
                "publication_confidence_index": self._score(context.get("h0_3", {}).get("publication_confidence_index")),
                "git_publication_traceability_score": self._score(context.get("h0_3", {}).get("git_publication_traceability_score")),
            },
        }

    def _component_scores(self, context: Dict[str, Any]) -> Dict[str, float]:
        h01 = context["h0_1"]
        h02 = context["h0_2"]
        h03 = context["h0_3"]

        repository_governance = self._score(h01["repository_governance_score"])
        github_governance = self._score(h01["github_governance_score"])
        replication_readiness = self._score(h02["replication_readiness_score"])
        reproduction_preparedness = self._score(h02["external_reproduction_preparedness"])
        publication_traceability = self._score(h03["publication_traceability_score"])
        publication_confidence = self._score(h03["publication_confidence_index"])

        evidence_completeness = (
            (1.0 if h01["present"] else 0.0)
            + (1.0 if h02["present"] else 0.0)
            + (1.0 if h03["present"] else 0.0)
        ) / 3.0

        operational_success = (
            (1.0 if h01["success"] else 0.0)
            + (1.0 if h02["success"] else 0.0)
            + (1.0 if h03["success"] else 0.0)
        ) / 3.0

        external_validation_readiness = (
            repository_governance
            + replication_readiness
            + publication_traceability
            + operational_success
        ) / 4.0

        scientific_traceability = (
            publication_traceability
            + publication_confidence
            + replication_readiness
        ) / 3.0

        dashboard_integrity = (
            evidence_completeness
            + operational_success
            + github_governance
        ) / 3.0

        external_validation_composite_index = (
            repository_governance * 0.25
            + replication_readiness * 0.25
            + publication_traceability * 0.25
            + scientific_traceability * 0.15
            + dashboard_integrity * 0.10
        )

        return {
            "repository_governance_score": round(repository_governance, 6),
            "github_governance_score": round(github_governance, 6),
            "replication_readiness_score": round(replication_readiness, 6),
            "external_reproduction_preparedness": round(reproduction_preparedness, 6),
            "publication_traceability_score": round(publication_traceability, 6),
            "publication_confidence_index": round(publication_confidence, 6),
            "evidence_completeness": round(evidence_completeness, 6),
            "operational_success": round(operational_success, 6),
            "external_validation_readiness": round(external_validation_readiness, 6),
            "scientific_traceability": round(scientific_traceability, 6),
            "dashboard_integrity": round(dashboard_integrity, 6),
            "external_validation_composite_index": round(external_validation_composite_index, 6),
        }

    def _write_prometheus(self, path: Path, scores: Dict[str, float]) -> None:
        lines = []
        metric_map = {
            "external_validation_composite_index": "oce_external_validation_composite_index",
            "external_validation_readiness": "oce_external_validation_readiness",
            "repository_governance_score": "oce_external_repository_governance_score",
            "replication_readiness_score": "oce_external_replication_readiness_score",
            "publication_traceability_score": "oce_external_publication_traceability_score",
            "scientific_traceability": "oce_external_scientific_traceability_score",
            "dashboard_integrity": "oce_external_validation_dashboard_integrity",
        }
        for key, metric in metric_map.items():
            lines.append(f"# TYPE {metric} gauge")
            lines.append(f"{metric} {scores[key]:.6f}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_html(self, path: Path, result: Dict[str, Any]) -> None:
        scores = result["component_scores"]
        rows = "\n".join(
            f"<tr><td>{key}</td><td>{value:.4f}</td></tr>"
            for key, value in scores.items()
        )
        html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>External Validation Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; }}
h1 {{ margin-bottom: 0.2rem; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
td, th {{ border: 1px solid #ddd; padding: 0.55rem; }}
th {{ text-align: left; }}
.badge {{ display: inline-block; padding: 0.25rem 0.5rem; border: 1px solid #999; border-radius: 0.25rem; }}
</style>
</head>
<body>
<h1>External Validation Dashboard</h1>
<p><span class="badge">primitive: {result["primitive"]}</span>
<span class="badge">refinement: {result["refinement"]}</span>
<span class="badge">success: {result["success"]}</span></p>
<p>Generated at {result["timestamp_utc"]}. This dashboard aggregates H0.1 repository governance,
H0.2 replication readiness and H0.3 scientific publication traceability without network side effects.</p>
<table>
<thead><tr><th>Metric</th><th>Value</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
</body>
</html>
"""
        path.write_text(html, encoding="utf-8")

    def _write_grafana_json(self, path: Path) -> None:
        dashboard = {
            "title": "Open Cognitive Ecology - External Validation",
            "schemaVersion": 39,
            "version": 1,
            "panels": [
                {
                    "type": "stat",
                    "title": "External Validation Composite Index",
                    "targets": [{"expr": "oce_external_validation_composite_index"}],
                },
                {
                    "type": "stat",
                    "title": "External Validation Readiness",
                    "targets": [{"expr": "oce_external_validation_readiness"}],
                },
                {
                    "type": "stat",
                    "title": "Replication Readiness",
                    "targets": [{"expr": "oce_external_replication_readiness_score"}],
                },
                {
                    "type": "stat",
                    "title": "Publication Traceability",
                    "targets": [{"expr": "oce_external_publication_traceability_score"}],
                },
            ],
        }
        path.write_text(json.dumps(dashboard, indent=2, sort_keys=True), encoding="utf-8")

    def step(
        self,
        external_validation_context: Optional[Dict[str, Any]] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        context = (
            self._normalize_context(external_validation_context)
            if external_validation_context is not None
            else self._read_baseline_context()
        )
        scores = self._component_scores(context)

        success = (
            scores["external_validation_composite_index"] >= 0.75
            and scores["external_validation_readiness"] >= 0.75
            and scores["evidence_completeness"] >= 1.0
            and scores["operational_success"] >= 1.0
        )

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": self._now(),
            "success": bool(success),
            "external_validation_composite_index": scores["external_validation_composite_index"],
            "external_validation_readiness": scores["external_validation_readiness"],
            "repository_governance_score": scores["repository_governance_score"],
            "replication_readiness_score": scores["replication_readiness_score"],
            "publication_traceability_score": scores["publication_traceability_score"],
            "component_scores": scores,
            "source_states": context,
            "governance": {
                "traceability_enabled": True,
                "html_dashboard_export_enabled": True,
                "prometheus_export_enabled": True,
                "grafana_export_enabled": True,
                "no_network_side_effects": True,
                "read_only_external_validation_aggregation": True,
                "non_closure_compliant": True,
            },
            "diagnostics": {
                "external_validation_context_override_used": external_validation_context is not None,
                "closure_pressure_increase": 0.0,
                "persist_requested": bool(persist),
                "warnings": [],
            },
            "state_path": None,
            "history_path": None,
            "prometheus_path": None,
            "dashboard_path": None,
            "grafana_dashboard_path": None,
        }

        if persist:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            state_path = self.out_dir / "latest_external_validation_dashboard.json"
            history_path = self.out_dir / "external_validation_dashboard_history.jsonl"
            prom_path = self.out_dir / "external_validation_dashboard.prom"
            dashboard_path = self.out_dir / "external_validation_dashboard.html"
            grafana_path = self.out_dir / "external_validation_dashboard_grafana.json"

            result.update(
                {
                    "state_path": str(state_path),
                    "history_path": str(history_path),
                    "prometheus_path": str(prom_path),
                    "dashboard_path": str(dashboard_path),
                    "grafana_dashboard_path": str(grafana_path),
                }
            )

            state_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            with history_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result, sort_keys=True) + "\n")
            self._write_prometheus(prom_path, scores)
            self._write_html(dashboard_path, result)
            self._write_grafana_json(grafana_path)

        return result


if __name__ == "__main__":
    print(json.dumps(ExternalValidationDashboard().step(), indent=2, sort_keys=True))
