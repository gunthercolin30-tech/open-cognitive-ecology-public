from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Any


PRIMITIVE = "external_assistance_trigger"

DEPENDENCIES = [
    "cognitive_gap_detector",
    "interaction_queue_manager",
    "autonomous_decision_engine",
    "opportunity_detection_engine",
    "proactive_assistance_workflows",
    "proactive_conversational_initiative",
    "conversational_event_detector",
    "constitutional_governance_supervisor",
    "constitutional_alert_system",
    "metrics_history_recorder",
]


class ExternalAssistanceTrigger:
    # O2 decides whether a cognitive gap warrants external cognitive assistance.
    # It does not detect gaps, generate prompts, call assistants, or manage queues.

    def __init__(
        self,
        root: Path | None = None,
        history_file: Path | None = None,
        default_threshold: float = 0.45,
        governance_threshold: float = 0.80,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.history_file = (
            Path(history_file)
            if history_file is not None
            else self.root / "external_assistance_trigger_history.jsonl"
        )
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.default_threshold = self._bounded(default_threshold)
        self.governance_threshold = self._bounded(governance_threshold)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _bounded(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _count_history(self) -> tuple[int, int]:
        if not self.history_file.exists():
            return 0, 0
        total = 0
        required = 0
        with self.history_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                raw = line.strip()
                if not raw:
                    continue
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if item.get("primitive") == PRIMITIVE:
                    total += 1
                    if item.get("assistance_required") is True:
                        required += 1
        return total, required

    def _extract_gap(self, inputs: dict[str, Any]) -> dict[str, Any]:
        gap = inputs.get("gap_result")
        if isinstance(gap, dict):
            return gap
        if "knowledge_gap_index" in inputs:
            return inputs
        return {}

    def _governance_authorized(self, inputs: dict[str, Any]) -> tuple[bool, float, list[str]]:
        reasons: list[str] = []
        governance_score = self._bounded(
            inputs.get(
                "governance_consistency_score",
                inputs.get(
                    "constitutional_integrity_score",
                    inputs.get("constitutional_alignment", 1.0),
                ),
            )
        )
        closure_pressure = self._bounded(inputs.get("closure_pressure", 0.0))
        identity_continuity = self._bounded(inputs.get("identity_continuity_index", 1.0))

        authorized = True
        if governance_score < self.governance_threshold:
            authorized = False
            reasons.append("governance_score_below_threshold")
        if closure_pressure >= 0.85:
            authorized = False
            reasons.append("closure_pressure_too_high")
        if identity_continuity < 0.80:
            authorized = False
            reasons.append("identity_continuity_too_low")
        return authorized, governance_score, reasons

    def decide(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        gap = self._extract_gap(inputs)

        knowledge_gap_index = self._bounded(gap.get("knowledge_gap_index", inputs.get("knowledge_gap_index", 0.0)))
        external_candidate = bool(
            gap.get("external_assistance_candidate", inputs.get("external_assistance_candidate", False))
        )

        uncertainty_pressure = self._bounded(gap.get("uncertainty_pressure", inputs.get("uncertainty_pressure", 0.0)))
        failure_pressure = self._bounded(gap.get("failure_pressure", inputs.get("failure_pressure", 0.0)))
        knowledge_absence_pressure = self._bounded(gap.get("knowledge_absence_pressure", inputs.get("knowledge_absence_pressure", 0.0)))
        improvement_blockage_pressure = self._bounded(gap.get("improvement_blockage_pressure", inputs.get("improvement_blockage_pressure", 0.0)))
        contradiction_pressure = self._bounded(gap.get("contradiction_pressure", inputs.get("contradiction_pressure", 0.0)))

        opportunity_score = self._bounded(inputs.get("opportunity_score", 0.50))
        urgency_score = self._bounded(inputs.get("urgency_score", max(knowledge_gap_index, failure_pressure)))
        internal_resolution_capacity = self._bounded(inputs.get("internal_resolution_capacity", 0.50))
        resource_availability = self._bounded(inputs.get("resource_availability", 1.0))

        governance_authorized, governance_score, governance_reasons = self._governance_authorized(inputs)

        trigger_confidence = self._bounded(
            0.36 * knowledge_gap_index
            + 0.18 * max(uncertainty_pressure, failure_pressure)
            + 0.14 * knowledge_absence_pressure
            + 0.12 * improvement_blockage_pressure
            + 0.08 * contradiction_pressure
            + 0.07 * opportunity_score
            + 0.05 * urgency_score
        )

        effective_trigger_score = self._bounded(trigger_confidence - 0.15 * internal_resolution_capacity)

        assistance_required = bool(
            governance_authorized
            and resource_availability >= 0.30
            and (
                external_candidate
                or knowledge_gap_index >= self.default_threshold
                or contradiction_pressure >= 0.75
            )
            and effective_trigger_score >= 0.30
        )

        reasons: list[str] = []
        if external_candidate:
            reasons.append("cognitive_gap_detector_candidate")
        if knowledge_gap_index >= self.default_threshold:
            reasons.append("knowledge_gap_above_threshold")
        if contradiction_pressure >= 0.75:
            reasons.append("high_contradiction_pressure")
        if effective_trigger_score >= 0.30:
            reasons.append("trigger_confidence_sufficient")
        if resource_availability < 0.30:
            reasons.append("resource_availability_too_low")
        if internal_resolution_capacity >= 0.80:
            reasons.append("internal_resolution_capacity_high")
        reasons.extend(governance_reasons)
        if not reasons:
            reasons.append("insufficient_external_assistance_pressure")

        total_before, required_before = self._count_history()
        projected_total = total_before + 1
        projected_required = required_before + (1 if assistance_required else 0)
        assistance_request_rate = self._bounded(projected_required / projected_total)

        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": self._utc_now(),
            "assistance_required": assistance_required,
            "assistance_request_rate": assistance_request_rate,
            "trigger_confidence": trigger_confidence,
            "effective_trigger_score": effective_trigger_score,
            "governance_authorized": governance_authorized,
            "governance_score": governance_score,
            "resource_availability": resource_availability,
            "internal_resolution_capacity": internal_resolution_capacity,
            "knowledge_gap_index": knowledge_gap_index,
            "external_assistance_candidate": external_candidate,
            "trigger_reason": ";".join(reasons),
            "recommended_next_step": "generate_external_prompt" if assistance_required else "continue_internal_resolution",
            "diagnostics": {
                "thresholds": {
                    "default_threshold": self.default_threshold,
                    "governance_threshold": self.governance_threshold,
                    "minimum_effective_trigger_score": 0.30,
                    "minimum_resource_availability": 0.30,
                },
                "signals": {
                    "uncertainty_pressure": uncertainty_pressure,
                    "failure_pressure": failure_pressure,
                    "knowledge_absence_pressure": knowledge_absence_pressure,
                    "improvement_blockage_pressure": improvement_blockage_pressure,
                    "contradiction_pressure": contradiction_pressure,
                    "opportunity_score": opportunity_score,
                    "urgency_score": urgency_score,
                },
                "specialization": "external_assistance_decision_gate",
                "non_redundancy": "Decides whether an operational cognitive gap warrants external assistance.",
            },
        }

        self._append_jsonl(self.history_file, result)
        return result

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        if isinstance(inputs, dict):
            merged.update(inputs)
        merged.update(kwargs)
        return self.decide(merged)


if __name__ == "__main__":
    print(json.dumps(ExternalAssistanceTrigger().step({
        "gap_result": {
            "knowledge_gap_index": 0.72,
            "external_assistance_candidate": True,
            "uncertainty_pressure": 0.85,
            "failure_pressure": 0.70,
            "knowledge_absence_pressure": 0.65,
            "improvement_blockage_pressure": 0.60,
        },
        "governance_consistency_score": 0.95,
        "internal_resolution_capacity": 0.20,
    }), ensure_ascii=False, indent=2))
