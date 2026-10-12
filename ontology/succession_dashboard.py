from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json


ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
DASHBOARD_DIR = STATE_DIR / "succession_dashboard"
STATE_PATH = DASHBOARD_DIR / "latest_succession_dashboard.json"
HTML_PATH = DASHBOARD_DIR / "succession_dashboard.html"
PROM_PATH = DASHBOARD_DIR / "succession_dashboard.prom"
GRAFANA_PATH = DASHBOARD_DIR / "succession_dashboard_grafana.json"
HISTORY_PATH = DASHBOARD_DIR / "succession_dashboard_history.jsonl"


STATE_FILES = {
    "representative_identity": STATE_DIR / "representative_identity_registry.json",
    "representative_status": STATE_DIR / "representative_status_monitor.json",
    "revocation_conditions": STATE_DIR / "revocation_conditions_engine.json",
    "succession_candidates": STATE_DIR / "succession_candidate_registry.json",
    "succession_readiness": STATE_DIR / "succession_readiness_assessment.json",
    "constitutional_continuity": STATE_DIR / "constitutional_continuity_validation.json",
    "memory_transmission": STATE_DIR / "memory_transmission_protocol.json",
    "succession_execution": STATE_DIR / "succession_execution_protocol.json",
    "post_succession_verification": STATE_DIR / "post_succession_verification.json",
    "continuity_metrics": STATE_DIR / "continuity_metrics_engine.json",
    "civilizational_identity_preservation": STATE_DIR / "civilizational_identity_preservation.json",
    "representative_lineage": STATE_DIR / "representative_lineage_registry.json",
}


@dataclass
class SuccessionDashboardSnapshot:
    primitive: str
    success: bool
    dashboard_event: Dict[str, Any]
    dashboard_ready: bool
    representative_count: int
    revocation_count: int
    succession_event_count: int
    memory_transmission_count: int
    lineage_depth: int
    generation_count: int
    dashboard_health_score: float
    continuity_composite_score: float
    civilizational_identity_preservation_score: float
    latest_representative: Dict[str, Any]
    latest_succession_event: Dict[str, Any]
    succession_history: List[Dict[str, Any]]
    exports: Dict[str, str]
    prometheus_metrics: Dict[str, float]
    grafana_dashboard: Dict[str, Any]
    state_path: str
    html_path: str
    prometheus_path: str
    grafana_path: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except Exception:
        v = default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _stable_id(prefix: str, payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def _load_jsonl(path: Path, limit: int = 50) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    try:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
                try:
                    item = json.loads(line)
                    if isinstance(item, dict):
                        rows.append(item)
                except Exception:
                    continue
    except Exception:
        return []
    return rows


def _nested_get(data: Any, key: str, default: Any = None) -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for value in data.values():
            found = _nested_get(value, key, None)
            if found is not None:
                return found
    elif isinstance(data, list):
        for value in data:
            found = _nested_get(value, key, None)
            if found is not None:
                return found
    return default


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _representative_id(rep: Any) -> Optional[str]:
    if not isinstance(rep, dict):
        return None
    value = rep.get("representative_id") or rep.get("candidate_id") or rep.get("id")
    return str(value) if value is not None else None


def _unique_representatives(payload: Dict[str, Any], states: Dict[str, Dict[str, Any]], lineage_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    reps: List[Dict[str, Any]] = []

    for source in [
        payload.get("representatives"),
        payload.get("representative_identity"),
        states.get("representative_identity"),
        states.get("representative_status"),
    ]:
        if isinstance(source, list):
            reps.extend([x for x in source if isinstance(x, dict)])
        elif isinstance(source, dict):
            if isinstance(source.get("representatives"), list):
                reps.extend([x for x in source["representatives"] if isinstance(x, dict)])
            else:
                reps.append(source)

    for item in lineage_history:
        for key in ("previous_representative", "new_representative", "latest_representative"):
            rep = _nested_get(item, key)
            if isinstance(rep, dict):
                reps.append(rep)

    seen = set()
    unique: List[Dict[str, Any]] = []
    for rep in reps:
        rid = _representative_id(rep)
        if not rid or rid in seen:
            continue
        seen.add(rid)
        unique.append(rep)
    return unique


def _extract_latest_representative(representatives: List[Dict[str, Any]], lineage_state: Dict[str, Any]) -> Dict[str, Any]:
    latest = _nested_get(lineage_state, "latest_representative")
    if isinstance(latest, dict) and latest:
        return latest
    if representatives:
        return representatives[-1]
    return {}


def _extract_succession_history(payload: Dict[str, Any], states: Dict[str, Dict[str, Any]], lineage_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    supplied = payload.get("succession_history")
    if isinstance(supplied, list):
        return [x for x in supplied if isinstance(x, dict)]

    lineage_state = states.get("representative_lineage", {})
    for key in ("succession_history", "lineage_history", "registered_lineage"):
        value = _nested_get(lineage_state, key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]

    compact: List[Dict[str, Any]] = []
    for item in lineage_history:
        event = _nested_get(item, "lineage_event") or _nested_get(item, "succession_event") or item
        if isinstance(event, dict):
            compact.append(event)
    return compact[-50:]


def _render_html(snapshot: Dict[str, Any]) -> str:
    metrics = snapshot.get("prometheus_metrics", {})
    rows = "".join(
        f"<tr><td>{escape(str(k))}</td><td>{escape(str(v))}</td></tr>"
        for k, v in sorted(metrics.items())
    )
    history_rows = "".join(
        f"<tr><td>{escape(str(item.get('event_id', item.get('id', ''))))}</td><td>{escape(str(item.get('event_type', 'succession')))}</td><td>{escape(str(item.get('timestamp_utc', '')))}</td></tr>"
        for item in snapshot.get("succession_history", [])[-20:]
        if isinstance(item, dict)
    )
    latest = json.dumps(snapshot.get("latest_representative", {}), indent=2, ensure_ascii=False)
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>Open Cognitive Ecology — Succession Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; margin: 2rem; background: #f8fafc; color: #0f172a; }}
    h1, h2 {{ color: #111827; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; }}
    .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
    .value {{ font-size: 1.8rem; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; background: white; }}
    td, th {{ border: 1px solid #e5e7eb; padding: .5rem; text-align: left; }}
    pre {{ background: #111827; color: #f9fafb; padding: 1rem; border-radius: 8px; overflow: auto; }}
  </style>
</head>
<body>
  <h1>Open Cognitive Ecology — Succession Dashboard</h1>
  <p>Generated at {escape(str(snapshot.get('dashboard_event', {}).get('timestamp_utc', '')))}</p>
  <div class=\"grid\">
    <div class=\"card\"><div>Dashboard ready</div><div class=\"value\">{escape(str(snapshot.get('dashboard_ready')))}</div></div>
    <div class=\"card\"><div>Representatives</div><div class=\"value\">{snapshot.get('representative_count')}</div></div>
    <div class=\"card\"><div>Succession events</div><div class=\"value\">{snapshot.get('succession_event_count')}</div></div>
    <div class=\"card\"><div>Lineage depth</div><div class=\"value\">{snapshot.get('lineage_depth')}</div></div>
    <div class=\"card\"><div>Generation count</div><div class=\"value\">{snapshot.get('generation_count')}</div></div>
    <div class=\"card\"><div>Dashboard health</div><div class=\"value\">{snapshot.get('dashboard_health_score')}</div></div>
  </div>
  <h2>Latest representative</h2>
  <pre>{escape(latest)}</pre>
  <h2>Metrics</h2>
  <table><tbody>{rows}</tbody></table>
  <h2>Succession history</h2>
  <table><thead><tr><th>Event ID</th><th>Type</th><th>Timestamp</th></tr></thead><tbody>{history_rows}</tbody></table>
</body>
</html>
"""


def _render_prometheus(metrics: Dict[str, float]) -> str:
    lines = ["# HELP oce_succession_dashboard Succession dashboard metrics", "# TYPE oce_succession_dashboard gauge"]
    for key, value in sorted(metrics.items()):
        safe = "oce_succession_" + "".join(ch if ch.isalnum() else "_" for ch in key.lower()).strip("_")
        lines.append(f"{safe} {float(value):.6f}")
    return "\n".join(lines) + "\n"


def _render_grafana(metrics: Dict[str, float], timestamp: str) -> Dict[str, Any]:
    panels = []
    for idx, key in enumerate(sorted(metrics.keys()), start=1):
        panels.append({
            "id": idx,
            "type": "stat",
            "title": key.replace("_", " ").title(),
            "gridPos": {"h": 4, "w": 6, "x": ((idx - 1) % 4) * 6, "y": ((idx - 1) // 4) * 4},
            "targets": [{"expr": "oce_succession_" + "".join(ch if ch.isalnum() else "_" for ch in key.lower()).strip("_")}],
        })
    return {
        "title": "Open Cognitive Ecology — Succession Dashboard",
        "uid": "oce-succession-dashboard",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "30s",
        "time": {"from": "now-24h", "to": "now"},
        "annotations": {"list": []},
        "panels": panels,
        "templating": {"list": []},
        "generated_at_utc": timestamp,
    }


class SuccessionDashboard:
    """Specialized dashboard exporter for representative succession.

    This module is intentionally a specialization of the U-axis. It aggregates
    existing succession, continuity, memory and lineage outputs and exports a
    dashboard snapshot without replacing generic HTML, Prometheus or Grafana
    dashboard infrastructure.
    """

    primitive = "succession_dashboard"

    def step(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(payload or {})
        dry_run = bool(payload.get("dry_run", False))
        timestamp = str(payload.get("timestamp_utc") or _utc_now())
        event_id = str(payload.get("dashboard_event_id") or _stable_id("SDB", {"timestamp": timestamp, "payload": payload}))

        states: Dict[str, Dict[str, Any]] = {}
        for name, path in STATE_FILES.items():
            supplied = payload.get(name)
            if isinstance(supplied, dict):
                states[name] = supplied
            else:
                states[name] = _load_json(path)

        lineage_history = _load_jsonl(STATE_DIR / "representative_lineage_history.jsonl")
        representatives = _unique_representatives(payload, states, lineage_history)
        succession_history = _extract_succession_history(payload, states, lineage_history)
        lineage_state = states.get("representative_lineage", {})
        latest_representative = _extract_latest_representative(representatives, lineage_state)

        latest_succession_event = {}
        if succession_history:
            latest_succession_event = succession_history[-1]
        execution_event = _nested_get(states.get("succession_execution", {}), "succession_event")
        if isinstance(execution_event, dict) and execution_event:
            latest_succession_event = execution_event

        representative_count = int(payload.get("representative_count") or max(len(representatives), _nested_get(lineage_state, "generation_count", 0) or 0))
        revocation_count = int(payload.get("revocation_count") or len(_as_list(_nested_get(states.get("revocation_conditions", {}), "revocation_events", []))))
        succession_event_count = int(payload.get("succession_event_count") or max(len(succession_history), 1 if latest_succession_event else 0))
        memory_transmission_count = int(payload.get("memory_transmission_count") or (1 if states.get("memory_transmission") else 0))
        lineage_depth = int(payload.get("lineage_depth") or _nested_get(lineage_state, "lineage_depth", succession_event_count) or 0)
        generation_count = int(payload.get("generation_count") or _nested_get(lineage_state, "generation_count", representative_count) or 0)

        continuity_composite_score = _clamp(
            payload.get("continuity_composite_score", _nested_get(states.get("continuity_metrics", {}), "continuity_composite_score", 0.0))
        )
        civilizational_identity_preservation_score = _clamp(
            payload.get("civilizational_identity_preservation_score", _nested_get(states.get("civilizational_identity_preservation", {}), "civilizational_identity_preservation_score", 0.0))
        )
        continuity_validation_score = _clamp(
            payload.get("continuity_validation_score", _nested_get(states.get("post_succession_verification", {}), "continuity_validation_score", 0.0))
        )
        lineage_integrity_score = _clamp(
            payload.get("lineage_integrity_score", _nested_get(lineage_state, "lineage_integrity_score", 0.0))
        )

        data_presence_score = _clamp(sum(1 for v in states.values() if v) / max(1, len(states)))
        export_capability_score = 1.0
        dashboard_health_score = _clamp(
            (0.25 * data_presence_score)
            + (0.25 * continuity_composite_score)
            + (0.20 * civilizational_identity_preservation_score)
            + (0.15 * continuity_validation_score)
            + (0.15 * lineage_integrity_score)
        )
        dashboard_ready = dashboard_health_score >= 0.55 or bool(payload.get("force_ready", False))

        metrics = {
            "representative_count": float(representative_count),
            "revocation_count": float(revocation_count),
            "succession_event_count": float(succession_event_count),
            "memory_transmission_count": float(memory_transmission_count),
            "lineage_depth": float(lineage_depth),
            "generation_count": float(generation_count),
            "continuity_composite_score": continuity_composite_score,
            "civilizational_identity_preservation_score": civilizational_identity_preservation_score,
            "continuity_validation_score": continuity_validation_score,
            "lineage_integrity_score": lineage_integrity_score,
            "data_presence_score": data_presence_score,
            "export_capability_score": export_capability_score,
            "dashboard_health_score": dashboard_health_score,
            "dashboard_ready": 1.0 if dashboard_ready else 0.0,
        }

        dashboard_event = {
            "event_id": event_id,
            "event_type": "succession_dashboard_export",
            "timestamp_utc": timestamp,
        }

        snapshot = SuccessionDashboardSnapshot(
            primitive=self.primitive,
            success=True,
            dashboard_event=dashboard_event,
            dashboard_ready=dashboard_ready,
            representative_count=representative_count,
            revocation_count=revocation_count,
            succession_event_count=succession_event_count,
            memory_transmission_count=memory_transmission_count,
            lineage_depth=lineage_depth,
            generation_count=generation_count,
            dashboard_health_score=dashboard_health_score,
            continuity_composite_score=continuity_composite_score,
            civilizational_identity_preservation_score=civilizational_identity_preservation_score,
            latest_representative=latest_representative,
            latest_succession_event=latest_succession_event,
            succession_history=succession_history,
            exports={},
            prometheus_metrics=metrics,
            grafana_dashboard=_render_grafana(metrics, timestamp),
            state_path=str(STATE_PATH),
            html_path=str(HTML_PATH),
            prometheus_path=str(PROM_PATH),
            grafana_path=str(GRAFANA_PATH),
        )

        data = asdict(snapshot)
        data["exports"] = {
            "json": str(STATE_PATH),
            "html": str(HTML_PATH),
            "prometheus": str(PROM_PATH),
            "grafana": str(GRAFANA_PATH),
        }

        if not dry_run:
            DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
            STATE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            HTML_PATH.write_text(_render_html(data), encoding="utf-8")
            PROM_PATH.write_text(_render_prometheus(metrics), encoding="utf-8")
            GRAFANA_PATH.write_text(json.dumps(data["grafana_dashboard"], indent=2, ensure_ascii=False), encoding="utf-8")
            with HISTORY_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n")

        return data
