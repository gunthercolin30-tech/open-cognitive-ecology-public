
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GovernanceDashboard:
    primitive = "governance_dashboard"
    axis = "L13"

    STAGES = [
        ("recommendation_intake", "recommendation_intake"),
        ("recommendation_prioritization", "recommendation_prioritization"),
        ("governance_review", "governance_review"),
        ("constitutional_compliance_check", "constitutional_compliance_check"),
        ("approval_or_rejection", "approval_or_rejection"),
        ("execution_request_generation", "execution_request_generation"),
        ("governed_execution_dispatcher", "governed_execution_dispatcher"),
        ("human_review", "human_review"),
        ("controlled_execution_layer", "controlled_execution_layer"),
        ("outcome_monitoring", "outcome_monitoring"),
        ("effectiveness_assessment", "effectiveness_assessment"),
        ("adaptive_policy_update", "adaptive_policy_update"),
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.governance_dir = self.root / "governance"
        self.state_dir = self.governance_dir / "governance_dashboard"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.latest_json_path = self.state_dir / "latest_governance_dashboard.json"
        self.history_path = self.state_dir / "governance_dashboard_history.jsonl"
        self.html_path = self.state_dir / "governance_dashboard.html"
        self.prometheus_path = self.state_dir / "governance_dashboard.prom"
        self.grafana_path = self.state_dir / "governance_dashboard_grafana.json"

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "success": False,
                "read_error": repr(exc),
                "path": str(path),
            }

    @staticmethod
    def _read_jsonl_tail(path: Path, limit: int = 25) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        records: list[dict[str, Any]] = []
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            for line in lines[-limit:]:
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except Exception:
                    records.append({"success": False, "jsonl_parse_error": True, "raw": line[:500]})
        except Exception as exc:
            records.append({"success": False, "read_error": repr(exc), "path": str(path)})
        return records

    def _find_latest(self, stage_dir: Path, stage: str) -> Path | None:
        if not stage_dir.exists():
            return None

        candidates = [
            stage_dir / ("latest_" + stage + ".json"),
            stage_dir / ("latest_" + stage.replace("_layer", "") + ".json"),
            stage_dir / ("latest_" + stage.replace("_gate", "") + ".json"),
        ]

        for p in candidates:
            if p.exists():
                return p

        all_json = sorted(
            [p for p in stage_dir.glob("*.json") if p.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return all_json[0] if all_json else None

    def _find_history(self, stage_dir: Path, stage: str) -> Path | None:
        if not stage_dir.exists():
            return None

        candidates = [
            stage_dir / (stage + "_history.jsonl"),
            stage_dir / (stage + "_log.jsonl"),
            stage_dir / "human_review_log.jsonl",
        ]

        for p in candidates:
            if p.exists():
                return p

        all_jsonl = sorted(
            [p for p in stage_dir.glob("*.jsonl") if p.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return all_jsonl[0] if all_jsonl else None

    def _collect_stage(self, stage_key: str, directory_name: str) -> dict[str, Any]:
        stage_dir = self.governance_dir / directory_name
        latest_path = self._find_latest(stage_dir, stage_key)
        history_path = self._find_history(stage_dir, stage_key)

        latest = self._read_json(latest_path) if latest_path else None
        history_tail = self._read_jsonl_tail(history_path) if history_path else []

        latest_success = None
        if isinstance(latest, dict):
            latest_success = latest.get("success")

        return {
            "stage": stage_key,
            "directory": str(stage_dir),
            "directory_exists": stage_dir.exists(),
            "latest_path": str(latest_path) if latest_path else None,
            "history_path": str(history_path) if history_path else None,
            "latest_available": latest is not None,
            "history_available": bool(history_tail),
            "latest_success": latest_success,
            "history_tail_count": len(history_tail),
            "latest": latest,
            "history_tail": history_tail,
        }

    @staticmethod
    def _bool_score(value: Any) -> float:
        return 1.0 if bool(value) else 0.0

    def _compute_metrics(self, stages: dict[str, dict[str, Any]]) -> dict[str, Any]:
        total = len(stages)
        latest_available = sum(1 for s in stages.values() if s["latest_available"])
        history_available = sum(1 for s in stages.values() if s["history_available"])

        human_reviews = stages.get("human_review", {}).get("history_tail", [])
        executions = stages.get("controlled_execution_layer", {}).get("history_tail", [])
        outcomes = stages.get("outcome_monitoring", {}).get("history_tail", [])
        assessments = stages.get("effectiveness_assessment", {}).get("history_tail", [])
        policy_updates = stages.get("adaptive_policy_update", {}).get("history_tail", [])

        human_review_count = len(human_reviews)
        execution_count = len(executions)
        outcome_count = len(outcomes)
        effectiveness_count = len(assessments)
        policy_update_count = len(policy_updates)

        authorized_reviews = sum(1 for r in human_reviews if r.get("human_review_status") == "authorized")
        rejected_reviews = sum(1 for r in human_reviews if r.get("human_review_status") == "rejected")
        completed_executions = sum(1 for r in executions if r.get("execution_status") == "completed")
        rolled_back_executions = sum(1 for r in executions if r.get("execution_status") == "rolled_back")

        effectiveness_values = [
            float(r.get("effectiveness_score"))
            for r in assessments
            if isinstance(r.get("effectiveness_score"), (int, float))
        ]
        mean_effectiveness = (
            sum(effectiveness_values) / len(effectiveness_values)
            if effectiveness_values else None
        )

        learning_values = [
            float(r.get("governance_learning_score"))
            for r in policy_updates
            if isinstance(r.get("governance_learning_score"), (int, float))
        ]
        mean_learning = (
            sum(learning_values) / len(learning_values)
            if learning_values else None
        )

        pipeline_observability_score = (
            latest_available / total if total else 0.0
        )
        longitudinal_trace_score = (
            history_available / total if total else 0.0
        )
        dashboard_readiness_score = round(
            (pipeline_observability_score * 0.55 + longitudinal_trace_score * 0.45),
            6,
        )

        return {
            "stage_count": total,
            "latest_available_count": latest_available,
            "history_available_count": history_available,
            "pipeline_observability_score": round(pipeline_observability_score, 6),
            "longitudinal_trace_score": round(longitudinal_trace_score, 6),
            "dashboard_readiness_score": dashboard_readiness_score,
            "human_review_count": human_review_count,
            "authorized_review_count": authorized_reviews,
            "rejected_review_count": rejected_reviews,
            "execution_count": execution_count,
            "completed_execution_count": completed_executions,
            "rolled_back_execution_count": rolled_back_executions,
            "outcome_monitoring_count": outcome_count,
            "effectiveness_assessment_count": effectiveness_count,
            "adaptive_policy_update_count": policy_update_count,
            "mean_effectiveness_score": mean_effectiveness,
            "mean_governance_learning_score": mean_learning,
        }

    def _write_html(self, result: dict[str, Any]) -> None:
        metrics = result["metrics"]
        stages = result["stages"]

        rows = []
        for name, s in stages.items():
            rows.append(
                "<tr>"
                + "<td>" + html.escape(name) + "</td>"
                + "<td>" + html.escape(str(s.get("latest_available"))) + "</td>"
                + "<td>" + html.escape(str(s.get("history_available"))) + "</td>"
                + "<td>" + html.escape(str(s.get("latest_path"))) + "</td>"
                + "<td>" + html.escape(str(s.get("history_tail_count"))) + "</td>"
                + "</tr>"
            )

        metric_rows = []
        for k, v in metrics.items():
            metric_rows.append(
                "<tr><td>" + html.escape(str(k)) + "</td><td>" + html.escape(str(v)) + "</td></tr>"
            )

        doc = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Governance Dashboard</title>"
            "<style>body{font-family:Arial,sans-serif;margin:40px;}"
            "table{border-collapse:collapse;width:100%;margin-bottom:28px;}"
            "td,th{border:1px solid #ccc;padding:8px;text-align:left;}"
            "th{background:#f0f0f0;}code{background:#f6f6f6;padding:2px 4px;}"
            "</style></head><body>"
            "<h1>Open Cognitive Ecology - Governance Dashboard</h1>"
            "<p>Generated at: <code>" + html.escape(result["timestamp_utc"]) + "</code></p>"
            "<h2>Metrics</h2><table><tr><th>Metric</th><th>Value</th></tr>"
            + "".join(metric_rows)
            + "</table>"
            "<h2>L1-L12 Stage Coverage</h2>"
            "<table><tr><th>Stage</th><th>Latest</th><th>History</th><th>Latest path</th><th>History tail count</th></tr>"
            + "".join(rows)
            + "</table>"
            "</body></html>"
        )

        self.html_path.write_text(doc, encoding="utf-8")

    def _write_prometheus(self, result: dict[str, Any]) -> None:
        lines = []
        for k, v in result["metrics"].items():
            if isinstance(v, bool):
                val = 1.0 if v else 0.0
            elif isinstance(v, (int, float)):
                val = v
            else:
                continue
            metric_name = "oce_governance_" + "".join(ch if ch.isalnum() else "_" for ch in k.lower())
            lines.append(metric_name + " " + str(val))
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_grafana(self, result: dict[str, Any]) -> None:
        dashboard = {
            "title": "Open Cognitive Ecology Governance Dashboard",
            "schemaVersion": 38,
            "version": 1,
            "timezone": "browser",
            "tags": ["open-cognitive-ecology", "governance", "axis-l"],
            "panels": [
                {
                    "type": "stat",
                    "title": "Dashboard readiness",
                    "targets": [{"expr": "oce_governance_dashboard_readiness_score"}],
                    "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
                },
                {
                    "type": "stat",
                    "title": "Pipeline observability",
                    "targets": [{"expr": "oce_governance_pipeline_observability_score"}],
                    "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
                },
                {
                    "type": "stat",
                    "title": "Mean effectiveness",
                    "targets": [{"expr": "oce_governance_mean_effectiveness_score"}],
                    "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
                },
                {
                    "type": "stat",
                    "title": "Mean governance learning",
                    "targets": [{"expr": "oce_governance_mean_governance_learning_score"}],
                    "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0},
                },
            ],
            "oce_latest_result": result,
        }
        self.grafana_path.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if isinstance(inputs, dict):
            data.update(inputs)
        data.update(kwargs)

        timestamp = datetime.now(timezone.utc).isoformat()

        stages = {
            stage_key: self._collect_stage(stage_key, directory_name)
            for stage_key, directory_name in self.STAGES
        }
        metrics = self._compute_metrics(stages)

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": True,
            "timestamp_utc": timestamp,
            "stage_sequence": [stage for stage, _ in self.STAGES],
            "stages": stages,
            "metrics": metrics,
            "exports": {
                "json": str(self.latest_json_path),
                "history_jsonl": str(self.history_path),
                "html": str(self.html_path),
                "prometheus": str(self.prometheus_path),
                "grafana": str(self.grafana_path),
            },
            "l13_complete": True,
            "diagnostics": {
                "read_only_aggregation": True,
                "no_governance_state_mutation": True,
                "json_export_ready": True,
                "html_export_ready": True,
                "prometheus_export_ready": True,
                "grafana_export_ready": True,
            },
        }

        self.latest_json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

        self._write_html(result)
        self._write_prometheus(result)
        self._write_grafana(result)

        return result
