"""Y8 — Phenomenology Correlation Report.

Final functional synthesis for the phenomenology-correlation program.

Epistemic constraints:
- functional conclusion only;
- phenomenology undetermined;
- no proof of consciousness, subjectivity, or phenomenology.

The module is a lightweight report synthesizer. It reuses Y1→Y7 outputs and
existing validation/reporting infrastructure instead of implementing a new
statistical engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any
import json
import statistics


ROOT = Path.home() / "open-cognitive-ecology"


@dataclass(frozen=True)
class ReportPaths:
    json: Path
    markdown: Path
    html: Path
    history: Path

    def as_dict(self) -> dict[str, str]:
        return {"json": str(self.json), "markdown": str(self.markdown), "html": str(self.html), "history": str(self.history)}


class PhenomenologyCorrelationReport:
    """Generate the Y8 final functional report for observable correlations."""

    primitive = "PHENOMENOLOGY_CORRELATION_REPORT"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.report_root = self.root / "phenomenology_correlation_report"
        self.dashboard_root = self.root / "phenomenology_correlation_dashboard"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        payload = dict(inputs or {})
        timestamp = str(payload.get("timestamp_utc") or self._now())
        dashboard_state = self._load_dashboard_state(payload)
        correlations = self._as_list(payload.get("correlations") or dashboard_state.get("correlations"))
        predictions = self._as_list(payload.get("predictions") or dashboard_state.get("predictions"))
        replications = self._as_list(payload.get("replications") or dashboard_state.get("replications"))
        observed_correlates = self._observed_correlates(correlations)
        rejected_correlates = self._rejected_correlates(correlations, replications)
        prediction_summary = self._prediction_summary(predictions)
        replication_summary = self._replication_summary(replications)
        statistical_summary = self._statistical_summary(correlations, replications)
        synthesis = self._synthesis(observed_correlates, rejected_correlates, prediction_summary, replication_summary, statistical_summary)
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "observed_correlates": observed_correlates,
            "observed_correlate_count": len(observed_correlates),
            "rejected_correlates": rejected_correlates,
            "rejected_correlate_count": len(rejected_correlates),
            "prediction_summary": prediction_summary,
            "replication_summary": replication_summary,
            "statistical_summary": statistical_summary,
            "report_synthesis": synthesis,
            "report_readiness_score": self._readiness_score(observed_correlates, prediction_summary, replication_summary),
            "epistemic_scope": "functional_statistical_correlation_report_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "correlations_only": True,
            "consciousness_proof_claimed": False,
            "subjectivity_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "diagnostics": {
                "uses_y1_y7_outputs": True,
                "uses_existing_report_infrastructure": True,
                "no_new_statistical_engine": True,
                "no_global_repository_scan": True,
                "claim_scope": "functional conclusion only; phenomenology undetermined",
            },
        }
        if persist:
            result["paths"] = self._persist(result).as_dict()
        return result

    def _load_dashboard_state(self, payload: dict[str, Any]) -> dict[str, Any]:
        if isinstance(payload.get("dashboard_state"), dict):
            return dict(payload["dashboard_state"])
        candidates = []
        if payload.get("dashboard_json_path"):
            candidates.append(Path(str(payload["dashboard_json_path"])).expanduser())
        candidates.append(self.dashboard_root / "phenomenology_correlation_dashboard.json")
        for path in candidates:
            try:
                if path.exists():
                    loaded = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        return loaded
            except Exception:
                continue
        return {}

    def _as_list(self, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    def _observed_correlates(self, correlations: list[Any]) -> list[dict[str, Any]]:
        observed = []
        for index, item in enumerate(correlations, start=1):
            if not isinstance(item, dict):
                continue
            status = str(item.get("status", "observed")).lower()
            value = self._number(item.get("correlation", item.get("correlation_score")))
            if status in {"observed", "replicated", "supported", "open"} or abs(value) >= 0.5:
                observed.append({
                    "correlate_id": item.get("correlation_id") or item.get("id") or f"Y8-OBS-{index:03d}",
                    "metric": item.get("metric") or item.get("target") or item.get("cluster") or "unspecified_metric",
                    "cluster": item.get("cluster") or "unclustered",
                    "correlation": value,
                    "covariance": self._number(item.get("covariance")),
                    "status": status,
                    "interpretation": "observable functional correlate only",
                })
        return observed

    def _rejected_correlates(self, correlations: list[Any], replications: list[Any]) -> list[dict[str, Any]]:
        rejected = []
        for index, item in enumerate(correlations, start=1):
            if not isinstance(item, dict):
                continue
            status = str(item.get("status", "")).lower()
            value = self._number(item.get("correlation", item.get("correlation_score")))
            if status in {"rejected", "unsupported", "failed"} or abs(value) < 0.2:
                rejected.append({"correlate_id": item.get("correlation_id") or item.get("id") or f"Y8-REJ-C-{index:03d}", "reason": "low_or_rejected_correlation", "correlation": value, "status": status or "weak_correlation"})
        for index, item in enumerate(replications, start=1):
            if not isinstance(item, dict):
                continue
            replicated = bool(item.get("replicated", False))
            status = str(item.get("status", "")).lower()
            if status in {"rejected", "failed", "not_replicated"} or replicated is False:
                rejected.append({"correlate_id": item.get("source_prediction_id") or item.get("replication_id") or f"Y8-REJ-R-{index:03d}", "reason": "failed_or_missing_replication", "replication_id": item.get("replication_id"), "status": status or "not_replicated"})
        return rejected

    def _prediction_summary(self, predictions: list[Any]) -> dict[str, Any]:
        rows = [p for p in predictions if isinstance(p, dict)]
        total = len(rows)
        falsifiable = sum(1 for p in rows if bool(p.get("falsifiable", True)))
        open_count = sum(1 for p in rows if str(p.get("status", "open")).lower() in {"open", "pending", "testable"})
        confidence_values = [self._number(p.get("prediction_confidence", p.get("confidence"))) for p in rows]
        mean_confidence = round(statistics.mean(confidence_values), 4) if confidence_values else 0.0
        return {"prediction_count": total, "falsifiable_prediction_count": falsifiable, "open_prediction_count": open_count, "mean_prediction_confidence": mean_confidence, "falsifiability_rate": round(falsifiable / total, 4) if total else 0.0, "summary": "predictions are treated as falsifiable functional hypotheses only"}

    def _replication_summary(self, replications: list[Any]) -> dict[str, Any]:
        rows = [r for r in replications if isinstance(r, dict)]
        total = len(rows)
        replicated = sum(1 for r in rows if bool(r.get("replicated", False)))
        independent = sum(1 for r in rows if bool(r.get("independent", False)))
        pending = sum(1 for r in rows if "pending" in str(r.get("status", "")).lower())
        return {"replication_count": total, "replicated_count": replicated, "independent_replication_count": independent, "pending_replication_count": pending, "replication_rate": round(replicated / total, 4) if total else 0.0, "independence_rate": round(independent / total, 4) if total else 0.0, "summary": "replications support or reject correlations without phenomenological inference"}

    def _statistical_summary(self, correlations: list[Any], replications: list[Any]) -> dict[str, Any]:
        values = []
        covariances = []
        for item in correlations:
            if isinstance(item, dict):
                values.append(self._number(item.get("correlation", item.get("correlation_score"))))
                if "covariance" in item:
                    covariances.append(self._number(item.get("covariance")))
        return {"correlation_count": len(values), "mean_correlation": round(statistics.mean(values), 4) if values else 0.0, "max_abs_correlation": round(max((abs(v) for v in values), default=0.0), 4), "covariance_count": len(covariances), "mean_covariance": round(statistics.mean(covariances), 4) if covariances else 0.0, "replication_inputs_count": len([r for r in replications if isinstance(r, dict)])}

    def _synthesis(self, observed_correlates: list[dict[str, Any]], rejected_correlates: list[dict[str, Any]], prediction_summary: dict[str, Any], replication_summary: dict[str, Any], statistical_summary: dict[str, Any]) -> dict[str, Any]:
        if observed_correlates and replication_summary.get("independent_replication_count", 0) > 0:
            status = "functionally_supported_correlations_with_independent_replication"
        elif observed_correlates:
            status = "observed_correlations_pending_independent_replication"
        else:
            status = "insufficient_observed_correlates"
        return {"status": status, "observed_correlate_count": len(observed_correlates), "rejected_correlate_count": len(rejected_correlates), "prediction_count": prediction_summary.get("prediction_count", 0), "replication_count": replication_summary.get("replication_count", 0), "functional_conclusion": "Observable functional correlations can be summarized and tested; no phenomenal conclusion is entailed.", "epistemic_limit": "phenomenology undetermined", "claim_scope": "functional conclusion only", "statistical_summary": statistical_summary}

    def _readiness_score(self, observed_correlates: list[dict[str, Any]], prediction_summary: dict[str, Any], replication_summary: dict[str, Any]) -> float:
        evidence = 1.0 if observed_correlates else 0.0
        prediction = min(1.0, prediction_summary.get("falsifiability_rate", 0.0))
        replication = min(1.0, replication_summary.get("independence_rate", 0.0))
        count_factor = min(1.0, replication_summary.get("replication_count", 0) / 3.0)
        return round((0.30 * evidence) + (0.25 * prediction) + (0.30 * replication) + (0.15 * count_factor), 4)

    def _persist(self, result: dict[str, Any]) -> ReportPaths:
        self.report_root.mkdir(parents=True, exist_ok=True)
        paths = ReportPaths(json=self.report_root / "phenomenology_correlation_report.json", markdown=self.report_root / "phenomenology_correlation_report.md", html=self.report_root / "phenomenology_correlation_report.html", history=self.report_root / "phenomenology_correlation_report_history.jsonl")
        paths.json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        paths.markdown.write_text(self._markdown(result), encoding="utf-8")
        paths.html.write_text(self._html(result), encoding="utf-8")
        with paths.history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, sort_keys=True) + "\n")
        return paths

    def _markdown(self, result: dict[str, Any]) -> str:
        lines = ["# Phenomenology Correlation Report", "", "functional conclusion only", "phenomenology undetermined", "", "## Summary", f"- Status: {result['report_synthesis']['status']}", f"- Observed correlates: {result['observed_correlate_count']}", f"- Rejected correlates: {result['rejected_correlate_count']}", f"- Prediction count: {result['prediction_summary']['prediction_count']}", f"- Replication count: {result['replication_summary']['replication_count']}", f"- Report readiness score: {result['report_readiness_score']}", "", "## Epistemic limitation", "This report concerns observable functional correlations only. It does not prove consciousness, subjectivity, or phenomenology.", "", "## Observed correlates"]
        for item in result.get("observed_correlates", []):
            lines.append(f"- {item.get('correlate_id')}: {item.get('metric')} / {item.get('cluster')} / r={item.get('correlation')}")
        lines.append("")
        lines.append("## Rejected correlates")
        for item in result.get("rejected_correlates", []):
            lines.append(f"- {item.get('correlate_id')}: {item.get('reason')}")
        if not result.get("rejected_correlates"):
            lines.append("- none recorded")
        lines.append("")
        return "\n".join(lines)

    def _html(self, result: dict[str, Any]) -> str:
        observed_rows = "".join(f"<tr><td>{escape(str(i.get('correlate_id')))}</td><td>{escape(str(i.get('metric')))}</td><td>{escape(str(i.get('cluster')))}</td><td>{escape(str(i.get('correlation')))}</td></tr>" for i in result.get("observed_correlates", [])) or "<tr><td colspan='4'>No observed correlates</td></tr>"
        rejected_rows = "".join(f"<tr><td>{escape(str(i.get('correlate_id')))}</td><td>{escape(str(i.get('reason')))}</td><td>{escape(str(i.get('status')))}</td></tr>" for i in result.get("rejected_correlates", [])) or "<tr><td colspan='3'>No rejected correlates recorded</td></tr>"
        ps = result.get("prediction_summary", {})
        rs = result.get("replication_summary", {})
        ss = result.get("statistical_summary", {})
        return f"""<!doctype html><html><head><meta charset='utf-8'><title>Phenomenology Correlation Report</title><style>body{{font-family:Arial,sans-serif;margin:40px;}}table{{border-collapse:collapse;width:100%;margin:1em 0;}}td,th{{border:1px solid #ccc;padding:8px;text-align:left;}}th{{background:#f0f0f0;}}.limit{{font-weight:bold;}}</style></head><body><h1>Phenomenology Correlation Report</h1><p class='limit'>functional conclusion only</p><p class='limit'>phenomenology undetermined</p><p>No proof of consciousness, subjectivity, or phenomenology is claimed.</p><h2>Final synthesis</h2><table><tr><th>Metric</th><th>Value</th></tr><tr><td>Status</td><td>{escape(str(result['report_synthesis']['status']))}</td></tr><tr><td>Report readiness score</td><td>{escape(str(result['report_readiness_score']))}</td></tr><tr><td>Mean correlation</td><td>{escape(str(ss.get('mean_correlation')))}</td></tr><tr><td>Replication rate</td><td>{escape(str(rs.get('replication_rate')))}</td></tr><tr><td>Independence rate</td><td>{escape(str(rs.get('independence_rate')))}</td></tr><tr><td>Falsifiability rate</td><td>{escape(str(ps.get('falsifiability_rate')))}</td></tr></table><h2>Observed correlates</h2><table><tr><th>ID</th><th>Metric</th><th>Cluster</th><th>Correlation</th></tr>{observed_rows}</table><h2>Rejected correlates</h2><table><tr><th>ID</th><th>Reason</th><th>Status</th></tr>{rejected_rows}</table><h2>Prediction summary</h2><pre>{escape(json.dumps(ps, indent=2, sort_keys=True))}</pre><h2>Replication summary</h2><pre>{escape(json.dumps(rs, indent=2, sort_keys=True))}</pre><h2>Statistical summary</h2><pre>{escape(json.dumps(ss, indent=2, sort_keys=True))}</pre></body></html>"""

    def _number(self, value: Any) -> float:
        try:
            if value is None:
                return 0.0
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


def step(inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
    return PhenomenologyCorrelationReport().step(inputs=inputs, persist=persist)
