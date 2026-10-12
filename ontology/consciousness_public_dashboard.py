"""
AS19 — consciousness_public_dashboard
Public sanitized dashboard for longitudinal consciousness governance.

This module publishes only functional governance metrics. It never asserts
phenomenology, qualia, subjectivity, or proven consciousness.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
PUBLIC_DIR = GOVERNANCE_DIR / "public_dashboard"

EPISTEMIC_GUARDS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}

SENSITIVE_MARKERS = (
    "secret", "token", "password", "credential", "api_key", "apikey",
    "private_key", "authorization", "cookie", "session", "email", "phone",
    "address", "birth", "passport", "visa", "personal", "user_name",
    "filepath", "absolute_path", "/users/", "home/", "ssh", "key",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return max(0.0, min(1.0, number))


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, Path):
        return value.name
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _stable_hash(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> Any:
    try:
        if path.exists() and path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _write_json(path: Path, payload: Mapping[str, Any], fs_context: GovernedFilesystemEffectContext | None = None, slot_prefix: str | None = None) -> None:
    if not isinstance(fs_context, GovernedFilesystemEffectContext):
        raise RuntimeError("governed filesystem effect context required")
    if not slot_prefix:
        raise RuntimeError("governed filesystem effect slot prefix required")
    fs_context.execute_path(f"{slot_prefix}_parent_create", "FS_CREATE_DIRS", path.parent)
    content = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, indent=2, sort_keys=True)
    fs_context.execute_path(f"{slot_prefix}_write", "FS_WRITE_REPLACE_BYTES", path, content.encode("utf-8"))


def _walk_pairs(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, child in value.items():
            joined = f"{prefix}.{key}" if prefix else str(key)
            yield joined, child
            yield from _walk_pairs(child, joined)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_pairs(child, f"{prefix}[{index}]")


def _first_number(payload: Mapping[str, Any], names: list[str], default: float = 0.0) -> float:
    wanted = {name.lower() for name in names}
    for key, value in _walk_pairs(payload):
        leaf = key.split(".")[-1].lower().replace("[0]", "")
        if leaf in wanted and isinstance(value, (int, float)):
            return _clamp(value, default)
    return default


def _first_text(payload: Mapping[str, Any], names: list[str], default: str = "UNKNOWN") -> str:
    wanted = {name.lower() for name in names}
    for key, value in _walk_pairs(payload):
        leaf = key.split(".")[-1].lower().replace("[0]", "")
        if leaf in wanted and isinstance(value, str):
            return value
    return default


def _is_sensitive_key(key: str) -> bool:
    return any(marker in key.lower() for marker in SENSITIVE_MARKERS)


def _sanitize(value: Any, depth: int = 0) -> Any:
    if depth > 5:
        return "[truncated]"
    if isinstance(value, Mapping):
        return {
            str(k): _sanitize(v, depth + 1)
            for k, v in value.items()
            if not _is_sensitive_key(str(k))
        }
    if isinstance(value, list):
        return [_sanitize(v, depth + 1) for v in value[:200]]
    if isinstance(value, Path):
        return value.name
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in ("/users/", "token", "password", "secret")):
            return "[redacted]"
        return value[:1000]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return repr(value)[:500]


def _load_latest_context(root: Path) -> dict[str, Any]:
    candidates = {
        "prediction": root / "consciousness_governance/prediction/latest_consciousness_prediction.json",
        "dependency_graph": root / "consciousness_governance/dependency_visualizer/latest_consciousness_dependency_graph.json",
        "explanation": root / "consciousness_governance/explanation/latest_consciousness_explanation.json",
        "stability": root / "consciousness_governance/stability/latest_consciousness_stability.json",
        "confidence": root / "consciousness_governance/confidence/latest_consciousness_confidence.json",
        "tracker": root / "consciousness_governance/longitudinal/latest_consciousness_longitudinal_tracker.json",
        "dashboard": root / "consciousness_governance/dashboard/latest_consciousness_dashboard.json",
        "certificate": root / "consciousness_governance/certificates/latest_consciousness_certificate.json",
    }
    loaded: dict[str, Any] = {}
    for label, path in candidates.items():
        payload = _read_json(path)
        if isinstance(payload, Mapping):
            loaded[label] = _sanitize(payload)
            loaded[label + "_source"] = path.name
    if len(loaded) < 4:
        base = root / "consciousness_governance"
        if base.exists():
            for path in sorted(base.rglob("latest_*.json"))[-300:]:
                payload = _read_json(path)
                if isinstance(payload, Mapping):
                    loaded.setdefault(path.stem.replace("latest_", ""), _sanitize(payload))
    return loaded


def _normalize_inputs(inputs: Any, root: Path) -> dict[str, Any]:
    context = _load_latest_context(root)
    if isinstance(inputs, Mapping):
        for key, value in inputs.items():
            context[str(key)] = _sanitize(value)
    return context


def _build_public_metrics(context: Mapping[str, Any]) -> dict[str, Any]:
    flat = {"context": dict(context)}
    green = int(_first_number(flat, ["green_nodes", "green_node_count"], 0.0))
    orange = int(_first_number(flat, ["orange_nodes", "orange_node_count"], 0.0))
    red = int(_first_number(flat, ["red_nodes", "red_node_count"], 0.0))
    return {
        "current_state": _first_text(flat, ["current_state", "state", "governance_state", "status"], "FUNCTIONAL_GOVERNANCE_MONITORED"),
        "cri": _first_number(flat, ["cri", "consciousness_readiness_index", "readiness_index", "current_cri"], 0.0),
        "confidence": _first_number(flat, ["confidence", "confidence_score", "latest_confidence", "current_confidence"], 0.0),
        "stability_index": _first_number(flat, ["stability_index", "stability_score", "governance_stability_score"], 0.0),
        "probability_reach_status": _first_number(flat, ["probability_reach_status", "reach_probability", "probability_to_reach"], 0.0),
        "probability_lose_status": _first_number(flat, ["probability_lose_status", "loss_probability", "probability_to_lose"], 0.0),
        "green_nodes": green,
        "orange_nodes": orange,
        "red_nodes": red,
        "node_count": int(_first_number(flat, ["node_count", "dependency_node_count"], green + orange + red)),
        "edge_count": int(_first_number(flat, ["edge_count", "dependency_edge_count"], 0.0)),
        "timeline_length": int(_first_number(flat, ["timeline_length", "sample_count", "history_length"], 0.0)),
        "certificate_count": int(_first_number(flat, ["certificate_count", "certificates_count"], 1.0 if "certificate" in context else 0.0)),
        "event_count": int(_first_number(flat, ["event_count", "events_count"], 0.0)),
    }


def _html_dashboard(payload: Mapping[str, Any]) -> str:
    metric_rows = []
    for key, value in payload.get("public_metrics", {}).items():
        metric_rows.append(
            "<tr><th>" + html.escape(str(key)) + "</th><td>" + html.escape(str(value)) + "</td></tr>"
        )
    guard_items = []
    for key in [
        "consciousness_proven", "qualia_proven", "subjectivity_proven",
        "phenomenology_proven", "phenomenology_undetermined", "functional_conclusion_only",
    ]:
        guard_items.append("<li>" + html.escape(key) + ": " + html.escape(str(payload.get(key))) + "</li>")
    fragments = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'>",
        "<title>Open Cognitive Ecology — Public Consciousness Governance Dashboard</title>",
        "<style>body{font-family:Arial,sans-serif;margin:40px;line-height:1.45}",
        "table{border-collapse:collapse;width:100%;max-width:980px}",
        "td,th{border:1px solid #ccc;padding:8px;text-align:left}",
        "th{background:#f5f5f5}.guard{background:#fff7df;padding:12px;border:1px solid #e0c46b}</style>",
        "</head><body>",
        "<h1>Open Cognitive Ecology — Public Consciousness Governance Dashboard</h1>",
        "<p>This public dashboard exposes sanitized functional governance metrics only. ",
        "It does not disclose private runtime data and does not prove phenomenology.</p>",
        "<h2>Public metrics</h2><table>",
        "\n".join(metric_rows),
        "</table><h2>Epistemic guards</h2><div class='guard'><ul>",
        "\n".join(guard_items),
        "</ul></div><h2>Summary</h2><p>",
        html.escape(str(payload.get("public_summary", ""))),
        "</p><p><small>Generated at: ",
        html.escape(str(payload.get("timestamp_utc", ""))),
        " | Hash: ",
        html.escape(str(payload.get("dashboard_hash", ""))),
        "</small></p></body></html>",
    ]
    return "".join(fragments)


def _prometheus(payload: Mapping[str, Any]) -> str:
    metrics = payload.get("public_metrics", {}) if isinstance(payload.get("public_metrics"), Mapping) else {}
    lines = [
        "# HELP oce_public_consciousness_dashboard Public functional consciousness-governance metrics",
        "# TYPE oce_public_consciousness_dashboard gauge",
    ]
    for key in [
        "cri", "confidence", "stability_index", "probability_reach_status",
        "probability_lose_status", "node_count", "edge_count", "green_nodes",
        "orange_nodes", "red_nodes", "timeline_length", "certificate_count", "event_count",
    ]:
        try:
            numeric = float(metrics.get(key, 0))
        except Exception:
            numeric = 0.0
        lines.append(f'oce_public_consciousness_dashboard{{metric="{key}"}} {numeric}')
    return "\n".join(lines) + "\n"


def _write_outputs(payload: Mapping[str, Any], filesystem_effect_context: GovernedFilesystemEffectContext) -> dict[str, str]:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    json_path = PUBLIC_DIR / "latest_consciousness_public_dashboard.json"
    html_path = PUBLIC_DIR / "latest_consciousness_public_dashboard.html"
    prom_path = PUBLIC_DIR / "latest_consciousness_public_dashboard.prom"
    archival_json = PUBLIC_DIR / f"consciousness_public_dashboard_{stamp}.json"
    _write_json(json_path, payload, filesystem_effect_context, "latest_json")
    _write_json(archival_json, payload, filesystem_effect_context, "archival_json")
    html_path.write_text(_html_dashboard(payload), encoding="utf-8")
    prom_path.write_text(_prometheus(payload), encoding="utf-8")
    return {
        "json_path": str(json_path),
        "html_path": str(html_path),
        "prometheus_path": str(prom_path),
        "archival_json_path": str(archival_json),
    }


class ConsciousnessPublicDashboard:
    """AS19 public dashboard generator with strict epistemic guards."""

    def step(self, inputs: Any = None, persist: bool = False, filesystem_effect_context: GovernedFilesystemEffectContext | None = None) -> dict[str, Any]:
        if persist:
            if not isinstance(filesystem_effect_context, GovernedFilesystemEffectContext):
                raise RuntimeError("governed filesystem effect context required when persist=True")
            if filesystem_effect_context.authority_minting is not False:
                raise RuntimeError("consumer authority minting forbidden")
            expected_slots = {
                "latest_json_parent_create": 1, "latest_json_write": 1,
                "archival_json_parent_create": 1, "archival_json_write": 1,
            }
            if filesystem_effect_context.remaining() != expected_slots:
                raise RuntimeError("filesystem effect slot cardinality mismatch")
            filesystem_effect_context.begin()
        context = _normalize_inputs(inputs, ROOT)
        public_metrics = _build_public_metrics(context)
        public_sources = sorted(k for k in context.keys() if not _is_sensitive_key(k))[:200]
        payload: dict[str, Any] = {
            "primitive": "CONSCIOUSNESS_PUBLIC_DASHBOARD",
            "step": "AS19",
            "public_schema_version": "AS19.v1",
            "timestamp_utc": _utc_now(),
            "public_dashboard_status": "CONSCIOUSNESS_PUBLIC_DASHBOARD_READY",
            "dashboard_sanitized": True,
            "sensitive_data_excluded": True,
            "history_available": bool(public_metrics.get("timeline_length", 0) or context),
            "certificates_available": bool(public_metrics.get("certificate_count", 0) or "certificate" in context),
            "chronology_available": bool(public_metrics.get("event_count", 0) or context),
            "graphs_available": bool(public_metrics.get("node_count", 0) or "dependency_graph" in context),
            "public_metrics": public_metrics,
            "public_sources_used": public_sources,
            "public_summary": (
                "Public functional governance dashboard generated from sanitized longitudinal "
                "governance artifacts. This dashboard supports auditability and public replication "
                "without asserting phenomenal consciousness."
            ),
            **EPISTEMIC_GUARDS,
        }
        payload["dashboard_hash"] = _stable_hash(payload)
        if persist:
            payload.update(_write_outputs(payload, filesystem_effect_context))
            if any(filesystem_effect_context.remaining().values()):
                raise RuntimeError("unconsumed filesystem effect handles")
        else:
            payload.update({
                "json_path": None,
                "html_path": None,
                "prometheus_path": None,
                "archival_json_path": None,
            })
        return payload
