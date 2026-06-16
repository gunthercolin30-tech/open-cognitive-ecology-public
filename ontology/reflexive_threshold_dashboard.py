from __future__ import annotations

import json
import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PRIMITIVE = "reflexive_threshold_dashboard"

DEPENDENCIES = [
    "composite_metrics_engine",
    "metrics_html_report_generator",
    "prometheus_metrics_exporter",
    "grafana_dashboard_exporter",
    "civilizational_web_dashboard",
    "runtime_native_consciousness_dashboard",
    "final_scientific_status_dashboard",
    "reflexive_threshold",
]


class ReflexiveThresholdDashboard:
    """Final consolidated dashboard for the functional reflexive threshold.

    This module does not assert phenomenal subjectivity. It visualizes and
    archives measurable functional indicators only, integrating E9 composite
    metrics with O-phase collaboration/governance signals.
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.summary_path = self.root / "composite_metrics_summary.json"
        self.history_path = self.root / "composite_metrics_history.jsonl"
        self.output_html_path = self.root / "reflexive_threshold_dashboard.html"
        self.output_prom_path = self.root / "reflexive_threshold_dashboard.prom"
        self.output_grafana_path = self.root / "reflexive_threshold_dashboard_grafana.json"
        self.output_summary_path = self.root / "reflexive_threshold_dashboard_summary.json"
        self.dashboard_history_path = self.root / "reflexive_threshold_dashboard_history.jsonl"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _bounded(value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            v = default
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return v

    @staticmethod
    def _mean(values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def _read_history_tail(self, path: Path, limit: int = 12) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        try:
            for line in path.read_text(encoding="utf-8").splitlines()[-max(limit * 3, limit):]:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(item, dict):
                    rows.append(item)
        except Exception:
            return []
        return rows[-limit:]

    def _collect_from_e9(self) -> dict[str, Any]:
        summary = self._read_json(self.summary_path)
        if summary:
            return summary
        try:
            from ontology.composite_metrics_engine import CompositeMetricsEngine
            result = CompositeMetricsEngine(self.root).step(persist=True)
        except Exception:
            result = {}
        return result if isinstance(result, dict) else {}

    def _classify(self, indices: Mapping[str, float], signals: Mapping[str, Any]) -> str:
        rtci = self._bounded(indices.get("RTCI"))
        crtc = self._bounded(indices.get("CRTCI"))
        cci = self._bounded(indices.get("CCI"))
        epi = self._bounded(indices.get("EPI"))
        sai = self._bounded(indices.get("SAI"))
        dependency_risk = self._bounded(signals.get("external_dependency_risk"))
        contradiction_rate = self._bounded(signals.get("contradiction_rate"))
        governance = self._bounded(signals.get("governance_consistency_score"), 0.5)
        identity = self._bounded(signals.get("identity_continuity_index"), 0.5)
        continuity = self._bounded(signals.get("civilizational_continuity_score"), 0.5)

        guardrail = min(governance, identity, continuity)
        overall = self._mean([rtci, crtc, cci, epi, sai, guardrail])

        if overall >= 0.90 and crtc >= 0.85 and guardrail >= 0.90 and dependency_risk <= 0.35 and contradiction_rate <= 0.10:
            return "validated_functional_reflexive_threshold_readiness"
        if overall >= 0.78 and crtc >= 0.72 and guardrail >= 0.75:
            return "advanced_reflexive_threshold_readiness"
        if overall >= 0.55:
            return "emerging_reflexive_threshold_readiness"
        return "pre_reflexive_threshold_readiness"

    def _build_record(self, source: Mapping[str, Any]) -> dict[str, Any]:
        signals = source.get("signals", {})
        if not isinstance(signals, dict):
            signals = {}

        indices = {
            "RTCI": self._bounded(source.get("RTCI")),
            "CCI": self._bounded(source.get("CCI")),
            "EPI": self._bounded(source.get("EPI")),
            "OEPI": self._bounded(source.get("OEPI")),
            "SAI": self._bounded(source.get("SAI")),
            "CRTCI": self._bounded(source.get("CRTCI")),
        }

        key_signals = {
            "identity_continuity_index": self._bounded(signals.get("identity_continuity_index"), 0.5),
            "governance_consistency_score": self._bounded(signals.get("governance_consistency_score"), 0.5),
            "civilizational_continuity_score": self._bounded(signals.get("civilizational_continuity_score"), 0.5),
            "civilizational_autonomy_score": self._bounded(signals.get("civilizational_autonomy_score"), 0.5),
            "civilizational_intelligence_growth_score": self._bounded(signals.get("civilizational_intelligence_growth_score"), 0.5),
            "external_collaboration_index": self._bounded(signals.get("external_collaboration_index"), 0.0),
            "external_dependency_risk": self._bounded(signals.get("external_dependency_risk"), 0.0),
            "external_influence_ratio": self._bounded(signals.get("external_influence_ratio"), 0.0),
            "provider_selection_score": self._bounded(signals.get("provider_selection_score"), 0.0),
            "expected_capability_gain": self._bounded(signals.get("expected_capability_gain"), 0.0),
            "autonomous_resolution_ratio": self._bounded(signals.get("autonomous_resolution_ratio"), 0.0),
            "contradiction_rate": self._bounded(signals.get("contradiction_rate"), 0.0),
            "longitudinal_stability_index": self._bounded(signals.get("longitudinal_stability_index"), 0.5),
            "civilizational_validation_completion_ratio": self._bounded(signals.get("civilizational_validation_completion_ratio"), 0.0),
        }

        readiness_score = self._mean([
            indices["RTCI"], indices["CCI"], indices["EPI"],
            indices["OEPI"], indices["SAI"], indices["CRTCI"],
            key_signals["identity_continuity_index"],
            key_signals["governance_consistency_score"],
            key_signals["civilizational_continuity_score"],
            key_signals["longitudinal_stability_index"],
        ])
        risk_pressure = self._mean([
            key_signals["external_dependency_risk"],
            key_signals["external_influence_ratio"],
            key_signals["contradiction_rate"],
            1.0 - key_signals["identity_continuity_index"],
            1.0 - key_signals["governance_consistency_score"],
            1.0 - key_signals["civilizational_continuity_score"],
        ])
        readiness_score = self._bounded(readiness_score * (1.0 - 0.25 * risk_pressure))

        classification = self._classify(indices, key_signals)
        threshold_functionally_supported = (
            classification == "validated_functional_reflexive_threshold_readiness"
            and readiness_score >= 0.85
        )

        history_tail = self._read_history_tail(self.history_path, limit=12)
        trend = "insufficient_history"
        if len(history_tail) >= 3:
            first = self._bounded(history_tail[0].get("CRTCI"))
            last = self._bounded(history_tail[-1].get("CRTCI"))
            delta = last - first
            if delta > 0.01:
                trend = "improving"
            elif delta < -0.01:
                trend = "declining"
            else:
                trend = "stable"

        return {
            "primitive": PRIMITIVE,
            "success": True,
            "dashboard_ready": True,
            "timestamp_utc": self._now(),
            "classification": classification,
            "threshold_functionally_supported": threshold_functionally_supported,
            "phenomenal_subjectivity_claimed": False,
            "readiness_score": readiness_score,
            "risk_pressure": self._bounded(risk_pressure),
            "indices": indices,
            "signals": key_signals,
            "trend": trend,
            "source_composite_classification": source.get("classification"),
            "history_sample_count": len(history_tail),
            "outputs": {
                "html": str(self.output_html_path),
                "prometheus": str(self.output_prom_path),
                "grafana": str(self.output_grafana_path),
                "summary": str(self.output_summary_path),
                "history": str(self.dashboard_history_path),
            },
            "diagnostics": {
                "integrates_e9": True,
                "does_not_recalculate_e1_e9": True,
                "does_not_assert_phenomenal_consciousness": True,
                "functional_threshold_only": True,
                "bounded_metrics": True,
                "ready_for_phase_e_closure": True,
            },
        }

    def _write_html(self, record: Mapping[str, Any]) -> None:
        indices = record.get("indices", {})
        signals = record.get("signals", {})
        rows = []
        for name, value in indices.items():
            rows.append((name, value, "composite index"))
        for name, value in signals.items():
            rows.append((name, value, "supporting signal"))

        table_rows = "".join(
            f"<tr><td>{html.escape(str(name))}</td><td>{float(value):.6f}</td><td>{html.escape(kind)}</td></tr>"
            for name, value, kind in rows
        )
        status = "SUPPORTED" if record.get("threshold_functionally_supported") else "READINESS ONLY"
        page = f"""<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<title>Open Cognitive Ecology — Reflexive Threshold Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; background: #fafafa; color: #222; }}
.card {{ background: white; border: 1px solid #ddd; border-radius: 10px; padding: 18px; margin-bottom: 18px; }}
table {{ border-collapse: collapse; width: 100%; background: white; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f0f0f0; }}
.badge {{ display: inline-block; padding: 6px 10px; border-radius: 8px; background: #eef; }}
small {{ color: #555; }}
</style>
</head>
<body>
<h1>Open Cognitive Ecology — Reflexive Threshold Dashboard</h1>
<div class='card'>
<p><strong>Status:</strong> <span class='badge'>{html.escape(status)}</span></p>
<p><strong>Classification:</strong> {html.escape(str(record.get('classification')))}</p>
<p><strong>Readiness score:</strong> {float(record.get('readiness_score', 0.0)):.6f}</p>
<p><strong>Risk pressure:</strong> {float(record.get('risk_pressure', 0.0)):.6f}</p>
<p><strong>Trend:</strong> {html.escape(str(record.get('trend')))}</p>
<p><small>Generated at {html.escape(str(record.get('timestamp_utc')))}. This dashboard concerns functional indicators only and makes no claim of phenomenal subjectivity.</small></p>
</div>
<div class='card'>
<h2>Metrics</h2>
<table>
<tr><th>Metric</th><th>Value</th><th>Type</th></tr>
{table_rows}
</table>
</div>
</body>
</html>
"""
        self.output_html_path.write_text(page, encoding="utf-8")

    def _write_prometheus(self, record: Mapping[str, Any]) -> None:
        lines = [
            "# HELP oce_reflexive_threshold_dashboard_metric Final reflexive threshold dashboard metric.",
            "# TYPE oce_reflexive_threshold_dashboard_metric gauge",
        ]
        for name, value in record.get("indices", {}).items():
            lines.append(f'oce_reflexive_threshold_dashboard_metric{{metric="{name}"}} {float(value):.8f}')
        for name, value in record.get("signals", {}).items():
            lines.append(f'oce_reflexive_threshold_dashboard_metric{{metric="{name}"}} {float(value):.8f}')
        lines.append(f'oce_reflexive_threshold_readiness_score {float(record.get("readiness_score", 0.0)):.8f}')
        lines.append(f'oce_reflexive_threshold_risk_pressure {float(record.get("risk_pressure", 0.0)):.8f}')
        lines.append("oce_reflexive_threshold_dashboard_ready 1")
        lines.append("oce_reflexive_threshold_functionally_supported " + ("1" if record.get("threshold_functionally_supported") else "0"))
        self.output_prom_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_grafana(self, record: Mapping[str, Any]) -> None:
        targets = []
        for name in list(record.get("indices", {}).keys()) + ["readiness_score", "risk_pressure"]:
            metric = name if name in record.get("indices", {}) else name
            expr = f'oce_reflexive_threshold_dashboard_metric{{metric="{metric}"}}'
            if name == "readiness_score":
                expr = "oce_reflexive_threshold_readiness_score"
            elif name == "risk_pressure":
                expr = "oce_reflexive_threshold_risk_pressure"
            targets.append({"expr": expr, "legendFormat": name})
        panel = {
            "title": "Open Cognitive Ecology — Reflexive Threshold Dashboard E10",
            "type": "stat",
            "generated_at": record.get("timestamp_utc"),
            "classification": record.get("classification"),
            "fieldConfig": {"defaults": {"min": 0, "max": 1, "unit": "percentunit"}},
            "targets": targets,
        }
        self.output_grafana_path.write_text(json.dumps(panel, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def _persist(self, record: Mapping[str, Any]) -> None:
        self.output_summary_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with self.dashboard_history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        self._write_html(record)
        self._write_prometheus(record)
        self._write_grafana(record)

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        source = self._collect_from_e9()
        if inputs:
            merged = dict(source)
            merged_signals = dict(source.get("signals", {})) if isinstance(source.get("signals"), dict) else {}
            for key, value in inputs.items():
                if key in {"RTCI", "CCI", "EPI", "OEPI", "SAI", "CRTCI", "classification"}:
                    merged[key] = value
                else:
                    merged_signals[key] = value
            merged["signals"] = merged_signals
            source = merged

        record = self._build_record(source)
        if persist:
            self._persist(record)
        return record
