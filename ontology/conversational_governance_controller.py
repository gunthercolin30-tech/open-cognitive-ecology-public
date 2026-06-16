# -*- coding: utf-8 -*-
"""
D6 — Conversational Governance Controller.

Central governance layer for autonomous conversational initiative.
It does not duplicate D1/D3/D5: it produces a governance decision that can be
consumed by proactive_conversational_initiative, civilizational_notification_engine
and terminal_conversation_runtime.

D6-R.2 correction: when an explicit external governance.noise_ratio is supplied,
it takes precedence over the internally estimated historical noise.
"""


from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

PRIMITIVE = "conversational_governance_controller"
DEPENDENCIES = [
    "proactive_conversational_initiative",
    "civilizational_notification_engine",
    "persistent_civilizational_conversational_agent",
    "terminal_conversation_runtime",
    "conversational_event_detector",
    "constitutional_governance_supervisor",
    "constitutional_alert_system",
    "anti_closure_metaconstraint",
]


class ConversationalGovernanceController:
    """Govern autonomous conversational emission with anti-noise constraints."""

    def __init__(
        self,
        noise_threshold: float = 0.10,
        repetition_threshold: float = 0.92,
        min_quality_threshold: float = 0.75,
        max_messages_per_window: int = 3,
        state_dir: Optional[Path] = None,
    ) -> None:
        self.noise_threshold = self._bounded(noise_threshold)
        self.repetition_threshold = self._bounded(repetition_threshold)
        self.min_quality_threshold = self._bounded(min_quality_threshold)
        self.max_messages_per_window = int(max(1, max_messages_per_window))
        self.root = Path.home() / "open-cognitive-ecology"
        self.state_dir = Path(state_dir) if state_dir else self.root / "conversational_governance"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "governance_state.json"
        self.history: List[Dict[str, Any]] = self._load_history()

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _bounded(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        return max(0.0, min(1.0, number))

    def _as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    def _load_history(self) -> List[Dict[str, Any]]:
        if not self.state_path.exists():
            return []
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            history = data.get("history", [])
            return history if isinstance(history, list) else []
        except Exception:
            return []

    def _save_history(self) -> None:
        payload = {
            "primitive": "CONVERSATIONAL_GOVERNANCE_CONTROLLER",
            "saved_at": self._now(),
            "history": self.history[-50:],
        }
        self.state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _latest_messages(self, count: int = 5) -> List[str]:
        return [str(item.get("message", "")) for item in self.history[-count:] if item.get("message")]

    def _repetition_score(self, message: str) -> float:
        message = str(message or "")
        if not message:
            return 0.0
        scores = [SequenceMatcher(None, message, previous).ratio() for previous in self._latest_messages()]
        return round(max(scores) if scores else 0.0, 3)

    def _rate_pressure(self) -> float:
        recent = self.history[-self.max_messages_per_window:]
        if not recent:
            return 0.0
        emitted = sum(1 for item in recent if item.get("emitted"))
        return round(min(1.0, emitted / float(self.max_messages_per_window)), 3)

    def _internal_noise_ratio(self) -> float:
        recent = self.history[-10:]
        if not recent:
            return 0.0
        suppressed = sum(1 for item in recent if not item.get("emitted"))
        return round(suppressed / len(recent), 3)

    def _external_noise_ratio(self, inputs: Dict[str, Any]) -> Optional[float]:
        governance = inputs.get("governance") or {}
        if isinstance(governance, dict) and "noise_ratio" in governance:
            return self._bounded(governance.get("noise_ratio"))
        if "noise_ratio" in inputs:
            return self._bounded(inputs.get("noise_ratio"))
        return None

    def _initiative_quality(self, inputs: Dict[str, Any], events: List[Any]) -> float:
        notification_quality = self._bounded(inputs.get("notification_quality_score"), 0.80)
        continuity = self._bounded(inputs.get("conversation_continuity_score"), 0.80)
        event_strength = 0.0
        scored_events = []
        for event in events:
            if isinstance(event, dict):
                scored_events.append(self._bounded(event.get("priority_score", event.get("score", 0.0))))
        if scored_events:
            event_strength = max(scored_events)
        else:
            event_strength = 0.50
        return round(0.45 * notification_quality + 0.35 * continuity + 0.20 * event_strength, 3)

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        timestamp = self._now()
        events = self._as_list(inputs.get("events"))
        message = str(inputs.get("message") or inputs.get("notification_message") or "")

        external_noise = self._external_noise_ratio(inputs)
        internal_noise = self._internal_noise_ratio()
        external_noise_ratio_used = external_noise is not None
        noise_ratio = external_noise if external_noise_ratio_used else internal_noise

        repetition_score = self._repetition_score(message)
        rate_pressure = self._rate_pressure()
        initiative_quality_score = self._initiative_quality(inputs, events)

        suppression_reasons: List[str] = []
        if noise_ratio > self.noise_threshold:
            suppression_reasons.append("noise_ratio_above_threshold")
        if repetition_score >= self.repetition_threshold:
            suppression_reasons.append("repetition_above_threshold")
        if rate_pressure >= 1.0:
            suppression_reasons.append("frequency_limit_exceeded")
        if initiative_quality_score < self.min_quality_threshold:
            suppression_reasons.append("initiative_quality_below_threshold")

        governance_allowed = not suppression_reasons
        record = {
            "timestamp": timestamp,
            "message": message,
            "events": len(events),
            "noise_ratio": round(noise_ratio, 3),
            "external_noise_ratio_used": external_noise_ratio_used,
            "repetition_score": repetition_score,
            "rate_pressure": rate_pressure,
            "initiative_quality_score": initiative_quality_score,
            "governance_allowed": governance_allowed,
            "suppression_reasons": suppression_reasons,
            "emitted": governance_allowed,
        }
        self.history.append(record)
        self._save_history()

        emitted_count = sum(1 for item in self.history if item.get("emitted"))
        suppressed_count = sum(1 for item in self.history if not item.get("emitted"))
        total = max(1, emitted_count + suppressed_count)
        noise_ratio_metric = round(suppressed_count / total, 3)
        mean_quality = round(
            sum(self._bounded(item.get("initiative_quality_score")) for item in self.history) / max(1, len(self.history)),
            3,
        )

        return {
            "primitive": "CONVERSATIONAL_GOVERNANCE_CONTROLLER",
            "timestamp": timestamp,
            "governance_allowed": governance_allowed,
            "conversation_allowed": governance_allowed,
            "should_emit": governance_allowed,
            "initiative_quality_score": initiative_quality_score,
            "mean_initiative_quality_score": mean_quality,
            "noise_ratio": round(noise_ratio, 3),
            "external_noise_ratio_used": external_noise_ratio_used,
            "internal_noise_ratio": internal_noise,
            "noise_ratio_metric": noise_ratio_metric,
            "repetition_score": repetition_score,
            "rate_pressure": rate_pressure,
            "suppression_reasons": suppression_reasons,
            "anti_spam_active": True,
            "anti_repetition_active": True,
            "frequency_limiting_active": True,
            "quality_filter_active": True,
            "emitted_count": emitted_count,
            "suppressed_count": suppressed_count,
            "governance_decision_record": record,
            "state_path": str(self.state_path),
            "diagnostics": {
                "central_governance_layer": True,
                "does_not_duplicate_d1_d3_d5": True,
                "external_noise_priority": True,
                "noise_threshold": self.noise_threshold,
                "repetition_threshold": self.repetition_threshold,
                "min_quality_threshold": self.min_quality_threshold,
                "max_messages_per_window": self.max_messages_per_window,
            },
        }


ENGINE = ConversationalGovernanceController()


def step(inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return ENGINE.step(inputs)
