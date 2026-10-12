"""
AS10 — consciousness_dashboard

Longitudinal dashboard layer for consciousness governance.

This module does not prove consciousness and does not compute new metaphysical
claims. It aggregates persisted outputs from AS7/AS8/AS9 and related governance
artefacts into JSON, HTML and Prometheus-compatible dashboard artefacts.
"""
from __future__ import annotations

import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
DASHBOARD_DIR = GOVERNANCE_DIR / "dashboard"
LONGITUDINAL_DIR = GOVERNANCE_DIR / "longitudinal"
CONFIDENCE_DIR = GOVERNANCE_DIR / "confidence"
READINESS_DIR = GOVERNANCE_DIR / "readiness"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return default
        number = float(value)
        if number != number:  # NaN
            return default
        return max(0.0, min(1.0, number))
    except Exception:
        return default


def _read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists() and path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    return {}


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _hash_payload(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _latest_json(directory: Path, preferred: str | None = None) -> dict[str, Any]:
    if preferred:
        data = _read_json(directory / preferred)
        if data:
            return data
    try:
        candidates = sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for candidate in candidates:
            data = _read_json(candidate)
            if data:
                return data
    except Exception:
        return {}
    return {}


def _collect_dashboard_exports(max_items: int = 12) -> list[dict[str, Any]]:
    export_dir = ROOT / "web_dashboard_exports"
    exports: list[dict[str, Any]] = []
    try:
        candidates = sorted(
            [p for p in export_dir.glob("dashboard_*") if p.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:max_items]
        for p in candidates:
            exports.append({
                "name": p.name,
                "path": str(p),
                "suffix": p.suffix.lower(),
                "size_bytes": p.stat().st_size,
                "mtime_utc": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
    except Exception:
        pass
    return exports


def _derive_latest_state(timeline_record: dict[str, Any], confidence_record: dict[str, Any]) -> dict[str, Any]:
    timeline = timeline_record.get("timeline") or timeline_record.get("time_series") or []
    if not isinstance(timeline, list):
        timeline = []
    latest_entry = timeline[-1] if timeline and isinstance(timeline[-1], dict) else {}

    confidence = _safe_float(
        latest_entry.get("confidence", confidence_record.get("confidence", timeline_record.get("confidence", 0.0)))
    )
    cri = _safe_float(
        latest_entry.get("CRI", latest_entry.get("cri", timeline_record.get("CRI", timeline_record.get("cri", 0.0))))
    )
    state = str(latest_entry.get("state", timeline_record.get("state", confidence_record.get("state", "NOT_EVALUATED"))))
    proof_status = str(latest_entry.get("proof_status", timeline_record.get("proof_status", "FUNCTIONAL_CONCLUSION_ONLY")))

    return {
        "CRI": cri,
        "confidence": confidence,
        "state": state,
        "proof_status": proof_status,
        "latest_entry": latest_entry,
        "sample_count": int(timeline_record.get("sample_count", len(timeline)) or len(timeline)),
        "timeline": timeline,
    }


def _status_color(value: float, high: float = 0.90, medium: float = 0.75) -> str:
    if value >= high:
        return "green"
    if value >= medium:
        return "orange"
    return "red"


def _html_dashboard(record: dict[str, Any]) -> str:
    state = record.get("current_state", {})
    heatmap = record.get("heatmap", {})
    timeline = record.get("timeline", [])
    rows = []
    for entry in timeline[-20:]:
        if not isinstance(entry, dict):
            continue
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(entry.get('timestamp_utc', entry.get('date', ''))))}</td>"
            f"<td>{html.escape(str(entry.get('CRI', entry.get('cri', ''))))}</td>"
            f"<td>{html.escape(str(entry.get('confidence', '')))}</td>"
            f"<td>{html.escape(str(entry.get('state', '')))}</td>"
            f"<td>{html.escape(str(entry.get('proof_status', '')))}</td>"
            "</tr>"
        )
    if not rows:
        rows.append("<tr><td colspan='5'>No longitudinal samples available.</td></tr>")

    heat_rows = []
    for key, value in heatmap.items():
        heat_rows.append(
            "<tr>"
            f"<td>{html.escape(str(key))}</td>"
            f"<td class='{html.escape(str(value.get('color', 'orange')))}'>{html.escape(str(value.get('value', '')))}</td>"
            f"<td>{html.escape(str(value.get('status', '')))}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>AS10 Consciousness Dashboard</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;margin:36px;background:#fafafa;color:#222;}}
.card{{background:white;border:1px solid #ddd;border-radius:10px;padding:18px;margin:14px 0;box-shadow:0 1px 2px rgba(0,0,0,.04);}}
table{{border-collapse:collapse;width:100%;background:white;}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left;}}
th{{background:#f1f1f1;}}
.green{{background:#d9f5df;}}
.orange{{background:#fff0cc;}}
.red{{background:#ffd9d9;}}
.small{{color:#666;font-size:0.9em;}}
</style></head>
<body>
<h1>AS10 — Consciousness Governance Dashboard</h1>
<p class='small'>Functional dashboard only. No phenomenology, qualia, subjectivity or consciousness proof is asserted.</p>
<div class='card'><h2>Current state</h2>
<table><tr><th>Metric</th><th>Value</th></tr>
<tr><td>CRI</td><td>{html.escape(str(state.get('CRI')))}</td></tr>
<tr><td>Confidence</td><td>{html.escape(str(state.get('confidence')))}</td></tr>
<tr><td>State</td><td>{html.escape(str(state.get('state')))}</td></tr>
<tr><td>Proof status</td><td>{html.escape(str(state.get('proof_status')))}</td></tr>
<tr><td>Sample count</td><td>{html.escape(str(state.get('sample_count')))}</td></tr>
</table></div>
<div class='card'><h2>Heatmap</h2><table><tr><th>Component</th><th>Value</th><th>Status</th></tr>{''.join(heat_rows)}</table></div>
<div class='card'><h2>Recent timeline</h2><table><tr><th>Timestamp UTC</th><th>CRI</th><th>Confidence</th><th>State</th><th>Proof status</th></tr>{''.join(rows)}</table></div>
<div class='card'><h2>Artefacts</h2><p>JSON: {html.escape(str(record.get('json_path')))}</p><p>Prometheus: {html.escape(str(record.get('prometheus_path')))}</p></div>
</body></html>"""


def _prometheus_dashboard(record: dict[str, Any]) -> str:
    state = record.get("current_state", {})
    metrics = record.get("dashboard_metrics", {})
    return "\n".join([
        "# HELP consciousness_dashboard_cri Current consciousness readiness index as visualized by AS10",
        "# TYPE consciousness_dashboard_cri gauge",
        f"consciousness_dashboard_cri {_safe_float(state.get('CRI'))}",
        "# HELP consciousness_dashboard_confidence Current consciousness confidence as visualized by AS10",
        "# TYPE consciousness_dashboard_confidence gauge",
        f"consciousness_dashboard_confidence {_safe_float(state.get('confidence'))}",
        "# HELP consciousness_dashboard_sample_count Number of longitudinal samples available",
        "# TYPE consciousness_dashboard_sample_count gauge",
        f"consciousness_dashboard_sample_count {int(state.get('sample_count', 0) or 0)}",
        "# HELP consciousness_dashboard_ready AS10 dashboard readiness flag",
        "# TYPE consciousness_dashboard_ready gauge",
        f"consciousness_dashboard_ready {1 if record.get('dashboard_ready') else 0}",
        "# HELP consciousness_dashboard_export_count Number of prior dashboard exports detected",
        "# TYPE consciousness_dashboard_export_count gauge",
        f"consciousness_dashboard_export_count {int(metrics.get('prior_dashboard_export_count', 0) or 0)}",
        "",
    ])


class ConsciousnessDashboard:
    """Dashboard aggregation layer for AS10."""

    public_schema_version = "AS10.consciousness_dashboard.v1"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs or {}
        timestamp = _utc_now()

        timeline_record = inputs.get("timeline_record") if isinstance(inputs.get("timeline_record"), dict) else {}
        confidence_record = inputs.get("confidence_record") if isinstance(inputs.get("confidence_record"), dict) else {}

        if not timeline_record:
            timeline_record = _latest_json(LONGITUDINAL_DIR, "latest_consciousness_longitudinal_timeline.json")
        if not confidence_record:
            confidence_record = _latest_json(CONFIDENCE_DIR, "latest_consciousness_confidence.json")

        current_state = _derive_latest_state(timeline_record, confidence_record)
        cri = current_state["CRI"]
        confidence = current_state["confidence"]
        timeline = current_state["timeline"]

        dashboard_exports = _collect_dashboard_exports()
        heatmap = {
            "CRI": {"value": cri, "color": _status_color(cri), "status": "ready" if cri >= 0.75 else "watch"},
            "confidence": {"value": confidence, "color": _status_color(confidence), "status": "ready" if confidence >= 0.75 else "watch"},
            "longitudinal_samples": {"value": current_state["sample_count"], "color": "green" if current_state["sample_count"] >= 1 else "red", "status": "available" if current_state["sample_count"] >= 1 else "missing"},
            "timeline_ready": {"value": bool(timeline), "color": "green" if timeline else "red", "status": "available" if timeline else "missing"},
        }

        dashboard_metrics = {
            "cri": cri,
            "confidence": confidence,
            "sample_count": current_state["sample_count"],
            "timeline_length": len(timeline),
            "prior_dashboard_export_count": len(dashboard_exports),
            "green_components": sum(1 for v in heatmap.values() if v.get("color") == "green"),
            "orange_components": sum(1 for v in heatmap.values() if v.get("color") == "orange"),
            "red_components": sum(1 for v in heatmap.values() if v.get("color") == "red"),
        }

        record: dict[str, Any] = {
            "primitive": "CONSCIOUSNESS_DASHBOARD",
            "step": "AS10",
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": timestamp,
            "dashboard_ready": True,
            "dashboard_status": "CONSCIOUSNESS_DASHBOARD_READY",
            "consciousness_dashboard_ready": True,
            "current_state": current_state,
            "CRI": cri,
            "confidence": confidence,
            "state": current_state["state"],
            "proof_status": current_state["proof_status"],
            "timeline": timeline,
            "heatmap": heatmap,
            "dashboard_metrics": dashboard_metrics,
            "dashboard_exports": dashboard_exports,
            "dependency_outputs_available": {
                "AS8_confidence": bool(confidence_record),
                "AS9_longitudinal": bool(timeline_record),
                "prior_dashboard_exports": bool(dashboard_exports),
            },
            "files": {},
            "json_path": None,
            "html_path": None,
            "prometheus_path": None,
            "persisted": False,
            "failure_conditions": [],
            "epistemic_scope": "functional_visualization_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
        }
        record["dashboard_hash"] = _hash_payload({
            "current_state": current_state,
            "dashboard_metrics": dashboard_metrics,
            "heatmap": heatmap,
        })

        if persist:
            DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
            suffix = _stamp()
            json_path = DASHBOARD_DIR / f"consciousness_dashboard_{suffix}.json"
            latest_json_path = DASHBOARD_DIR / "latest_consciousness_dashboard.json"
            html_path = DASHBOARD_DIR / f"consciousness_dashboard_{suffix}.html"
            latest_html_path = DASHBOARD_DIR / "latest_consciousness_dashboard.html"
            prom_path = DASHBOARD_DIR / f"consciousness_dashboard_{suffix}.prom"
            latest_prom_path = DASHBOARD_DIR / "latest_consciousness_dashboard.prom"

            record["json_path"] = str(latest_json_path)
            record["html_path"] = str(latest_html_path)
            record["prometheus_path"] = str(latest_prom_path)
            record["files"] = {
                "json": str(latest_json_path),
                "json_snapshot": str(json_path),
                "html": str(latest_html_path),
                "html_snapshot": str(html_path),
                "prometheus": str(latest_prom_path),
                "prometheus_snapshot": str(prom_path),
            }
            record["persisted"] = True

            json_payload = json.dumps(_json_safe(record), ensure_ascii=False, indent=2, sort_keys=True)
            json_path.write_text(json_payload, encoding="utf-8")
            latest_json_path.write_text(json_payload, encoding="utf-8")
            html_payload = _html_dashboard(record)
            html_path.write_text(html_payload, encoding="utf-8")
            latest_html_path.write_text(html_payload, encoding="utf-8")
            prom_payload = _prometheus_dashboard(record)
            prom_path.write_text(prom_payload, encoding="utf-8")
            latest_prom_path.write_text(prom_payload, encoding="utf-8")

        return record
