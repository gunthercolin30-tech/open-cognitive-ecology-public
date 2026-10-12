from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


class ExternalInfluenceImpactMonitor:
    'Monitor cumulative impact of governed external influences.\n\nThis primitive does not grant any external source direct write authority.\nIt aggregates already-governed events into measurable impact, success,\nand reversibility indices.'

    primitive = "EXTERNAL_INFLUENCE_IMPACT_MONITOR"

    EVENT_TYPES = {
        "knowledge": "knowledge_influence_count",
        "decision": "decision_influence_count",
        "priority": "priority_influence_count",
        "revision": "revision_influence_count",
        "commit": "commit_influence_count",
        "governance": "governance_influence_count",
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "external_influence_impact_monitor"

    def _events_from_inputs(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        events = inputs.get("external_influence_events", [])
        if isinstance(events, list):
            return [e for e in events if isinstance(e, dict)]
        return []

    def _count_events(self, inputs: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, int]:
        counts = {field: int(inputs.get(field, 0) or 0) for field in self.EVENT_TYPES.values()}
        counts["rollback_count"] = int(inputs.get("rollback_count", 0) or 0)
        counts["failed_adoption_count"] = int(inputs.get("failed_adoption_count", 0) or 0)

        for event in events:
            event_type = str(event.get("influence_type", event.get("type", ""))).strip().lower()
            if event_type in self.EVENT_TYPES:
                counts[self.EVENT_TYPES[event_type]] += 1
            if event_type == "rollback" or event.get("rollback") is True:
                counts["rollback_count"] += 1
            decision = str(event.get("decision", event.get("priority_decision", event.get("amendment_decision", "")))).lower()
            failed = bool(event.get("failed", False)) or decision.endswith("rejected") or "rejected" in decision
            if failed:
                counts["failed_adoption_count"] += 1
        return counts

    def _success_rate(self, events: list[dict[str, Any]], failed_adoption_count: int) -> float:
        if not events:
            total = failed_adoption_count
            return 1.0 if total == 0 else 0.0
        successes = 0
        for event in events:
            decision = str(event.get("decision", event.get("priority_decision", event.get("amendment_decision", "")))).lower()
            failed = bool(event.get("failed", False)) or decision.endswith("rejected") or "rejected" in decision
            success = bool(event.get("success", False)) or decision.endswith("adopted") or decision.endswith("allowed") or decision.endswith("complete")
            if success and not failed:
                successes += 1
        return _clamp(successes / max(1, len(events)))

    def _effectiveness(self, events: list[dict[str, Any]], success_rate: float) -> float:
        if not events:
            return success_rate
        scores = [_clamp(e.get("impact_score", e.get("effectiveness", success_rate)), success_rate) for e in events]
        return _clamp(sum(scores) / max(1, len(scores)))

    def _reversibility(self, events: list[dict[str, Any]], rollback_count: int) -> float:
        if not events:
            return 1.0 if rollback_count == 0 else 0.5
        reversible = 0.0
        for event in events:
            if event.get("rollback_available") is True:
                reversible += 1.0
            elif event.get("rollback_plan"):
                reversible += 1.0
            elif "rollback_readiness_score" in event:
                reversible += _clamp(event.get("rollback_readiness_score"))
        return _clamp(reversible / max(1, len(events)))

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs or {}
        events = self._events_from_inputs(inputs)
        counts = self._count_events(inputs, events)

        success_rate = self._success_rate(events, counts["failed_adoption_count"])
        effectiveness = self._effectiveness(events, success_rate)
        reversibility = self._reversibility(events, counts["rollback_count"])

        direct_write_requested = bool(inputs.get("direct_write_requested", False))
        risk_pressure = (1.0 - success_rate) * 0.45 + (1.0 - effectiveness) * 0.35 + (1.0 - reversibility) * 0.20

        if direct_write_requested or success_rate < 0.5 or risk_pressure >= 0.55:
            decision = "influence_risk"
        elif success_rate < 0.8 or effectiveness < 0.65 or reversibility < 0.5:
            decision = "influence_warning"
        else:
            decision = "influence_healthy"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **counts,
            "external_influence_effectiveness": round(effectiveness, 6),
            "external_influence_success_rate": round(success_rate, 6),
            "external_influence_reversibility_index": round(reversibility, 6),
            "external_influence_risk_pressure": round(_clamp(risk_pressure), 6),
            "influence_decision": decision,
            "direct_write_requested": direct_write_requested,
            "direct_write_allowed": False,
            "event_count": len(events),
            "integration_dependencies": [
                "external_influence_adoption_gate",
                "external_priority_influence_layer",
                "external_commit_traceability_hook",
                "external_governance_amendment_gate",
                "outcome_monitoring",
                "effectiveness_assessment",
                "scientific_revision_execution_monitor",
            ],
        }

        if persist:
            self.report_dir.mkdir(parents=True, exist_ok=True)
            path = self.report_dir / "latest_external_influence_impact_monitor.json"
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["report_path"] = str(path)
        else:
            result["report_path"] = None

        return result
