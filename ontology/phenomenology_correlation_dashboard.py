"""Y7 — phenomenology_correlation_dashboard.

Functional dashboard for the empirical phenomenology correlation programme.

This module visualizes Y1-Y6 outputs without claiming consciousness,
subjectivity, sentience, qualia, or phenomenology. It is intentionally a light
orchestrator and renderer: it reads targeted persisted outputs, accepts explicit
payloads for deterministic tests, and produces HTML/JSON/Prometheus artifacts.

Epistemic scope:
- correlations only
- falsifiable prediction and replication display only
- functional conclusion only
- phenomenology undetermined
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

PRIMITIVE = "PHENOMENOLOGY_CORRELATION_DASHBOARD"


class PhenomenologyCorrelationDashboard:
    """Y7 functional dashboard for Y1-Y6 phenomenology correlations.

    The class does not perform repository-wide scans. It only reads known
    persisted files and can be fully driven by an explicit payload in tests.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "phenomenology_correlation_dashboard"
        self.latest_file = self.base_dir / "phenomenology_correlation_dashboard.json"
        self.html_file = self.base_dir / "phenomenology_correlation_dashboard.html"
        self.prometheus_file = self.base_dir / "phenomenology_correlation_dashboard.prom"
        self.history_file = self.base_dir / "phenomenology_correlation_dashboard_history.jsonl"

    def _now(self, payload: Dict[str, Any] | None = None) -> str:
        if payload and payload.get("timestamp_utc"):
            return str(payload["timestamp_utc"])
        return datetime.now(timezone.utc).isoformat()

    def _score(self, value: Any, default: float = 0.0) -> float:
        try:
            x = float(value)
        except Exception:
            return default
        return max(0.0, min(1.0, x))

    def _load_json(self, relative: str) -> Dict[str, Any]:
        path = self.root / relative
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        explicit = payload.get("context")
        if isinstance(explicit, dict):
            return explicit
        return {
            "registry": self._load_json("phenomenology_correlation_registry/phenomenology_correlation_registry.json"),
            "candidate_metrics": self._load_json("phenomenology_candidate_metrics/phenomenology_candidate_metrics.json"),
            "architecture_comparison": self._load_json("multi_architecture_comparator/multi_architecture_comparator.json"),
            "correlation_engine": self._load_json("phenomenology_correlation_engine/phenomenology_correlation_engine.json"),
            "prediction_engine": self._load_json("phenomenology_prediction_engine/phenomenology_prediction_engine.json"),
            "replication": self._load_json("independent_correlation_replication/independent_correlation_replication.json"),
        }

    def _list_from(self, payload: Dict[str, Any], ctx: Dict[str, Any], key: str, source: str) -> List[Dict[str, Any]]:
        explicit = payload.get(key)
        if isinstance(explicit, list):
            return [x for x in explicit if isinstance(x, dict)]
        value = ctx.get(source, {}).get(key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
        return []

    def _correlations(self, payload: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        explicit = payload.get("correlations")
        if isinstance(explicit, list):
            return [x for x in explicit if isinstance(x, dict)]

        engine = ctx.get("correlation_engine", {})
        candidates: List[Dict[str, Any]] = []
        for key in ("correlations", "observed_correlations", "significant_correlations", "candidate_correlations"):
            value = engine.get(key)
            if isinstance(value, list):
                candidates.extend([x for x in value if isinstance(x, dict)])

        if candidates:
            return candidates[:50]

        strength = self._score(engine.get("correlation_evidence_strength"), 0.0)
        if strength > 0.0:
            return [{
                "correlation_id": "Y4-CORR-SUMMARY",
                "metric": "correlation_evidence_strength",
                "cluster": "summary",
                "correlation": strength,
                "covariance": 0.0,
                "status": "observed",
            }]
        return []

    def _predictions(self, payload: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        explicit = payload.get("predictions")
        if isinstance(explicit, list):
            return [x for x in explicit if isinstance(x, dict)]
        value = ctx.get("prediction_engine", {}).get("predictions")
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)][:50]
        return []

    def _replications(self, payload: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        explicit = payload.get("replications")
        if isinstance(explicit, list):
            return [x for x in explicit if isinstance(x, dict)]
        value = ctx.get("replication", {}).get("replications")
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)][:50]
        return []

    def _clusters(self, correlations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        buckets: Dict[str, List[float]] = {}
        for item in correlations:
            cluster = str(item.get("cluster") or item.get("metric_group") or item.get("metric") or "unclustered")
            buckets.setdefault(cluster, []).append(self._score(item.get("correlation"), 0.0))
        return [
            {
                "cluster": name,
                "count": len(values),
                "mean_correlation": round(mean(values), 4) if values else 0.0,
            }
            for name, values in sorted(buckets.items())
        ]

    def _covariances(self, payload: Dict[str, Any], correlations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        explicit = payload.get("covariances")
        if isinstance(explicit, list):
            return [x for x in explicit if isinstance(x, dict)]
        covariances = []
        for item in correlations:
            if "covariance" in item:
                covariances.append({
                    "correlation_id": item.get("correlation_id") or item.get("id") or item.get("metric"),
                    "covariance": self._score(item.get("covariance"), 0.0),
                })
        return covariances[:50]

    def _summary(
        self,
        correlations: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]],
        replications: List[Dict[str, Any]],
        covariances: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        corr_values = [self._score(x.get("correlation"), 0.0) for x in correlations]
        covariance_values = [self._score(x.get("covariance"), 0.0) for x in covariances]
        replicated = [r for r in replications if bool(r.get("replicated"))]
        independent = [r for r in replications if bool(r.get("independent"))]
        falsifiable = [p for p in predictions if p.get("falsifiable", True) is not False]

        mean_correlation = round(mean(corr_values), 4) if corr_values else 0.0
        mean_covariance = round(mean(covariance_values), 4) if covariance_values else 0.0
        replication_rate = round(len(replicated) / max(1, len(replications)), 4) if replications else 0.0
        independence_rate = round(len(independent) / max(1, len(replications)), 4) if replications else 0.0
        falsifiability_rate = round(len(falsifiable) / max(1, len(predictions)), 4) if predictions else 0.0
        dashboard_readiness = round(mean([
            1.0 if correlations else 0.0,
            1.0 if predictions else 0.0,
            1.0 if replications else 0.0,
            falsifiability_rate,
            max(replication_rate, independence_rate),
        ]), 4)

        if not correlations and not predictions and not replications:
            status = "insufficient_dashboard_data"
        elif replications and independence_rate == 0.0:
            status = "pending_independent_replication"
        elif dashboard_readiness >= 0.75:
            status = "dashboard_ready"
        else:
            status = "partial_dashboard_ready"

        return {
            "dashboard_status": status,
            "correlation_count": len(correlations),
            "prediction_count": len(predictions),
            "replication_count": len(replications),
            "cluster_count": 0,
            "covariance_count": len(covariances),
            "mean_correlation": mean_correlation,
            "mean_covariance": mean_covariance,
            "replication_rate": replication_rate,
            "independence_rate": independence_rate,
            "falsifiability_rate": falsifiability_rate,
            "dashboard_readiness_score": dashboard_readiness,
        }

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.latest_file.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, sort_keys=True) + "\n")
        self.html_file.write_text(self._html(result), encoding="utf-8")
        self.prometheus_file.write_text(self._prometheus(result), encoding="utf-8")
        return {
            "json": str(self.latest_file),
            "history": str(self.history_file),
            "html": str(self.html_file),
            "prometheus": str(self.prometheus_file),
        }

    def _table(self, rows: List[Dict[str, Any]], columns: List[str]) -> str:
        if not rows:
            return "<p>No data available.</p>"
        header = "".join(f"<th>{html.escape(col)}</th>" for col in columns)
        body_rows = []
        for row in rows[:50]:
            cells = "".join(f"<td>{html.escape(str(row.get(col, '')))}</td>" for col in columns)
            body_rows.append(f"<tr>{cells}</tr>")
        return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"

    def _html(self, result: Dict[str, Any]) -> str:
        css = """
        body{font-family:Arial,sans-serif;margin:36px;line-height:1.4;}
        table{border-collapse:collapse;width:100%;margin:12px 0 28px 0;}
        th,td{border:1px solid #ccc;padding:7px;text-align:left;font-size:14px;}
        th{background:#f2f2f2;}
        .banner{padding:12px;border:1px solid #999;background:#fafafa;margin-bottom:18px;}
        .metric{display:inline-block;margin:6px 14px 6px 0;padding:8px;border:1px solid #ddd;}
        """
        metrics = [
            "dashboard_status", "correlation_count", "prediction_count", "replication_count",
            "cluster_count", "covariance_count", "dashboard_readiness_score",
            "replication_rate", "independence_rate", "falsifiability_rate",
        ]
        metric_html = "".join(
            f"<div class='metric'><b>{html.escape(k)}</b><br>{html.escape(str(result.get(k)))}</div>"
            for k in metrics
        )
        return "\n".join([
            "<!doctype html>",
            "<html><head><meta charset='utf-8'>",
            "<title>Phenomenology Correlation Dashboard</title>",
            f"<style>{css}</style></head><body>",
            "<h1>Phenomenology Correlation Dashboard</h1>",
            "<div class='banner'><b>functional conclusion only</b><br><b>phenomenology undetermined</b><br>correlations only; no proof of consciousness, subjectivity, sentience, qualia, or phenomenology.</div>",
            f"<p>Generated at: {html.escape(str(result.get('timestamp_utc')))}</p>",
            metric_html,
            "<h2>Observed correlations</h2>",
            self._table(result.get("correlations", []), ["correlation_id", "metric", "cluster", "correlation", "covariance", "status"]),
            "<h2>Clusters</h2>",
            self._table(result.get("clusters", []), ["cluster", "count", "mean_correlation"]),
            "<h2>Covariances</h2>",
            self._table(result.get("covariances", []), ["correlation_id", "covariance"]),
            "<h2>Falsifiable predictions</h2>",
            self._table(result.get("predictions", []), ["prediction_id", "target", "prediction_confidence", "falsifiable", "status"]),
            "<h2>Independent replications</h2>",
            self._table(result.get("replications", []), ["replication_id", "source_prediction_id", "lab_id", "architecture_id", "replicated", "independent", "status"]),
            "</body></html>",
        ])

    def _prometheus(self, result: Dict[str, Any]) -> str:
        success = 1 if result.get("success") else 0
        return "\n".join([
            "# HELP oce_phenomenology_correlation_dashboard_success Y7 functional success flag",
            "# TYPE oce_phenomenology_correlation_dashboard_success gauge",
            f"oce_phenomenology_correlation_dashboard_success {success}",
            "# HELP oce_phenomenology_correlation_dashboard_readiness Y7 dashboard readiness score",
            "# TYPE oce_phenomenology_correlation_dashboard_readiness gauge",
            f"oce_phenomenology_correlation_dashboard_readiness {result.get('dashboard_readiness_score', 0)}",
            "# HELP oce_phenomenology_correlation_count Y7 observed correlation count",
            "# TYPE oce_phenomenology_correlation_count gauge",
            f"oce_phenomenology_correlation_count {result.get('correlation_count', 0)}",
            "# HELP oce_phenomenology_replication_count Y7 replication count",
            "# TYPE oce_phenomenology_replication_count gauge",
            f"oce_phenomenology_replication_count {result.get('replication_count', 0)}",
        ]) + "\n"

    def step(self, payload: Dict[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        payload = payload or {}
        ctx = self._context(payload)
        correlations = self._correlations(payload, ctx)
        predictions = self._predictions(payload, ctx)
        replications = self._replications(payload, ctx)
        covariances = self._covariances(payload, correlations)
        clusters = self._clusters(correlations)
        summary = self._summary(correlations, predictions, replications, covariances)
        summary["cluster_count"] = len(clusters)

        result: Dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "timestamp_utc": self._now(payload),
            **summary,
            "correlations": correlations,
            "clusters": clusters,
            "covariances": covariances,
            "predictions": predictions,
            "replications": replications,
            "source_context_present": {k: bool(v) for k, v in ctx.items()},
            "correlations_only": True,
            "dashboard_functional_only": True,
            "functional_conclusion_only": True,
            "consciousness_proof_claimed": False,
            "subjectivity_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "phenomenology_undetermined": True,
            "epistemic_scope": "functional_statistical_correlation_dashboard_only",
            "diagnostics": {
                "uses_y1_y6_outputs": True,
                "uses_existing_dashboard_patterns": True,
                "no_global_repository_scan": True,
                "claim_scope": "functional conclusion only; phenomenology undetermined",
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
