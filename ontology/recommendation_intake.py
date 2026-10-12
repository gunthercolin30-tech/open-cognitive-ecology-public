
"""
L1 — recommendation_intake.

Governed intake layer for recommendations emitted by civilizational
observatories. This module does not execute actions, does not authorize
mutation, and does not modify identity, memory, or strategy. It normalizes
heterogeneous recommendation outputs into a traceable intake queue for L2.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp01(value: Any, default: float = 0.0) -> float:
    try:
        n = float(value)
    except (TypeError, ValueError):
        n = default
    return max(0.0, min(1.0, n))


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _stable_id(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return "REC-" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


@dataclass
class IntakeRecord:
    recommendation_id: str
    recommendation_source: str
    recommendation_type: str
    recommendation_timestamp: str
    recommendation_severity: float
    recommendation_confidence: float
    priority_hint_score: float
    recommendation_code: str
    recommended_action: str
    rationale: str
    target: str | None
    rank: int | None
    raw_payload: dict[str, Any]
    governance_flags: dict[str, bool]


class RecommendationIntake:
    """L1 intake queue. Intake only; no execution or state mutation."""

    primitive = "recommendation_intake"
    axis = "L1"

    DEFAULT_SOURCES = {
        "preventive_stability_recommendation_engine": [
            "civilizational_drift/latest_preventive_stability_recommendation_engine.json",
            "drift_monitoring/latest_preventive_stability_recommendation_engine.json",
            "latest_preventive_stability_recommendation_engine.json",
        ],
        "anti_closure_recommendation_engine": [
            "closure_pressure/latest_anti_closure_recommendation_engine.json",
            "latest_anti_closure_recommendation_engine.json",
        ],
        "paradigm_shift_detection_engine": [
            "paradigm_monitoring/latest_paradigm_shift_detection_engine.json",
            "latest_paradigm_shift_detection_engine.json",
        ],
        "drift_forecasting_engine": [
            "civilizational_drift/latest_drift_forecasting_engine.json",
            "latest_drift_forecasting_engine.json",
        ],
        "closure_pressure_forecasting_engine": [
            "closure_pressure/latest_closure_pressure_forecasting_engine.json",
            "latest_closure_pressure_forecasting_engine.json",
        ],
        "civilizational_stability_index": [
            "civilizational_drift/latest_civilizational_stability_index.json",
            "latest_civilizational_stability_index.json",
        ],
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "governance" / "recommendation_intake"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.state_dir / "latest_recommendation_intake.json"
        self.history_path = self.state_dir / "recommendation_intake_history.jsonl"

    def _load_json_path(self, path: Path) -> dict[str, Any] | None:
        try:
            if path.exists() and path.is_file() and path.stat().st_size <= 10_000_000:
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else None
        except Exception:
            return None
        return None

    def _discover_source_payloads(self) -> list[dict[str, Any]]:
        payloads: list[dict[str, Any]] = []
        for source, candidates in self.DEFAULT_SOURCES.items():
            for rel in candidates:
                data = self._load_json_path(self.root / rel)
                if data is not None:
                    data.setdefault("primitive", source)
                    payloads.append(data)
                    break
        return payloads

    def _extract_recommendation_items(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        for key in ("recommended_actions", "anti_closure_recommendations", "recommendations"):
            if key in payload:
                return [x for x in _as_list(payload.get(key)) if isinstance(x, dict)]
        primitive = str(payload.get("primitive") or "unknown_observatory")
        risk = max(
            _clamp01(payload.get("forecast_risk_index")),
            _clamp01(payload.get("paradigm_shift_confidence")),
            _clamp01(payload.get("current_closure_pressure")),
            _clamp01(payload.get("stability_risk_index")),
        )
        if bool(payload.get("paradigm_shift_detected")) or risk > 0.0:
            return [{
                "code": f"observe_{primitive}",
                "rank": 1,
                "recommendation_type": "observational_signal_intake",
                "recommended_action": f"Route {primitive} signal to governance review without execution.",
                "rationale": "Source emitted a measurable risk, forecast or transition signal.",
                "recommendation_priority_score": risk,
                "recommendation_confidence": _clamp01(payload.get("forecast_confidence", payload.get("input_completeness", 0.5)), 0.5),
                "target": primitive,
                "requires_direct_execution": False,
                "requires_direct_identity_change": False,
                "requires_direct_memory_change": False,
                "requires_direct_strategy_change": False,
            }]
        return []

    def _severity_from_item(self, item: dict[str, Any], source_payload: dict[str, Any]) -> float:
        if item.get("recommendation_severity") is not None:
            return _clamp01(item.get("recommendation_severity"))
        score = item.get("recommendation_priority_score", item.get("priority_score"))
        if score is not None:
            return _clamp01(score)
        label = str(item.get("recommendation_priority", "")).lower()
        if "critical" in label:
            return 0.9
        if "high" in label:
            return 0.75
        if "medium" in label:
            return 0.5
        if "low" in label:
            return 0.25
        return max(
            _clamp01(source_payload.get("forecast_risk_index")),
            _clamp01(source_payload.get("stability_risk_index")),
            _clamp01(source_payload.get("paradigm_shift_confidence")),
        )

    def _normalize_item(self, item: dict[str, Any], source_payload: dict[str, Any]) -> IntakeRecord:
        source = str(source_payload.get("primitive") or item.get("source") or "unknown")
        timestamp = str(item.get("recommendation_timestamp") or source_payload.get("timestamp_utc") or _utc_now())
        rtype = str(item.get("recommendation_type") or "unspecified_recommendation")
        severity = self._severity_from_item(item, source_payload)
        confidence = _clamp01(item.get("recommendation_confidence", source_payload.get("forecast_confidence", 0.5)), 0.5)
        priority_hint = _clamp01(item.get("recommendation_priority_score", item.get("priority_score", severity)), severity)
        code = str(item.get("code") or item.get("id") or rtype)
        action = str(item.get("recommended_action") or item.get("action") or "Preserve for governance review.")
        rationale = str(item.get("rationale") or source_payload.get("detection_class") or "No rationale supplied.")
        target = item.get("target") or item.get("targeted_closure_factor") or item.get("targeted_factor")
        try:
            rank = int(item["rank"]) if item.get("rank") is not None else None
        except (TypeError, ValueError):
            rank = None
        flags = {
            "intake_only": True,
            "requires_direct_execution": bool(item.get("requires_direct_execution", False)),
            "requires_direct_identity_change": bool(item.get("requires_direct_identity_change", False)),
            "requires_direct_memory_change": bool(item.get("requires_direct_memory_change", False)),
            "requires_direct_strategy_change": bool(item.get("requires_direct_strategy_change", False)),
            "execution_authorized": False,
            "identity_change_authorized": False,
            "memory_change_authorized": False,
            "strategy_change_authorized": False,
            "non_closure_compliant": not bool(item.get("requires_direct_execution", False)),
        }
        raw_payload = {"source_summary": {"primitive": source, "success": source_payload.get("success"), "timestamp_utc": source_payload.get("timestamp_utc")}, "item": item}
        identity = {"source": source, "timestamp": timestamp, "type": rtype, "code": code, "action": action, "severity": severity}
        return IntakeRecord(_stable_id(identity), source, rtype, timestamp, severity, confidence, priority_hint, code, action, rationale, str(target) if target is not None else None, rank, raw_payload, flags)

    def _persist(self, result: dict[str, Any]) -> None:
        self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")

    def step(self, inputs: dict[str, Any] | list[dict[str, Any]] | None = None, persist: bool = True, reset: bool = False) -> dict[str, Any]:
        if reset:
            for path in (self.latest_path, self.history_path):
                if path.exists():
                    path.unlink()
        if inputs is None:
            source_payloads = self._discover_source_payloads()
        elif isinstance(inputs, dict):
            source_payloads = [x for x in inputs.get("sources", []) if isinstance(x, dict)] if isinstance(inputs.get("sources"), list) else [inputs]
        elif isinstance(inputs, list):
            source_payloads = [x for x in inputs if isinstance(x, dict)]
        else:
            source_payloads = []

        records: list[IntakeRecord] = []
        rejected_payload_count = 0
        for payload in source_payloads:
            items = self._extract_recommendation_items(payload)
            if not items:
                rejected_payload_count += 1
            for item in items:
                records.append(self._normalize_item(item, payload))

        queue = sorted([asdict(r) for r in records], key=lambda r: (r["priority_hint_score"], r["recommendation_severity"], -(r["rank"] or 999999)), reverse=True)
        max_severity = max([r["recommendation_severity"] for r in queue], default=0.0)
        mean_confidence = sum(r["recommendation_confidence"] for r in queue) / len(queue) if queue else 0.0
        execution_requests = [r for r in queue if r["governance_flags"].get("requires_direct_execution")]
        unsafe_change_requests = [r for r in queue if r["governance_flags"].get("requires_direct_identity_change") or r["governance_flags"].get("requires_direct_memory_change") or r["governance_flags"].get("requires_direct_strategy_change")]

        result = {
            "primitive": self.primitive,
            "axis": self.axis,
            "success": True,
            "timestamp_utc": _utc_now(),
            "source_payload_count": len(source_payloads),
            "rejected_payload_count": rejected_payload_count,
            "recommendation_count": len(queue),
            "intake_queue": queue,
            "queue_metrics": {
                "max_recommendation_severity": round(max_severity, 6),
                "mean_recommendation_confidence": round(mean_confidence, 6),
                "execution_request_count": len(execution_requests),
                "unsafe_change_request_count": len(unsafe_change_requests),
                "source_count": len({r["recommendation_source"] for r in queue}),
            },
            "governance": {
                "observational_only": True,
                "does_not_execute_actions": True,
                "does_not_approve_or_reject": True,
                "does_not_modify_identity": True,
                "does_not_modify_memory": True,
                "does_not_modify_strategy": True,
                "routes_to": "recommendation_prioritization",
                "non_closure_compliant": len(execution_requests) == 0,
                "traceability": True,
                "reversibility": True,
            },
            "state_paths": {"latest": str(self.latest_path), "history": str(self.history_path)},
        }
        if persist:
            self._persist(result)
        return result
