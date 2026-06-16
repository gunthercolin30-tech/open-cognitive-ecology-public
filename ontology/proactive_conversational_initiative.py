from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

PRIMITIVE = "proactive_conversational_initiative"

DEPENDENCIES = [
    "monitoring",
    "alerting_and_notification_system",
    "constitutional_alert_system",
    "conversational_context_manager",
    "conversation_memory_archive",
    "opportunity_detection_engine",
    "proactive_assistance_workflows",
    "proactive_research_suggestions",
]


class ProactiveConversationalInitiative:
    """
    Gouverne l'initiative conversationnelle autonome.

    Cette primitive ne produit un message spontané que si un événement
    franchit un seuil de pertinence et si les contraintes de gouvernance
    conversationnelle n'indiquent pas un risque de bruit excessif.
    """

    def __init__(
        self,
        relevance_threshold: float = 0.75,
        noise_threshold: float = 0.10,
        history_limit: int = 200,
    ) -> None:
        self.relevance_threshold = self._clamp(relevance_threshold)
        self.noise_threshold = self._clamp(noise_threshold)
        self.history_limit = max(20, int(history_limit))
        self.root = Path.home() / "open-cognitive-ecology"
        self.history_dir = self.root / "conversation_initiatives"
        self.history_path = (
            self.history_dir / "proactive_conversational_initiative_history.jsonl"
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _clamp(self, value: Any, low: float = 0.0, high: float = 1.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return low
        return max(low, min(high, number))

    def _as_list(self, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _normalize_event(self, event: Any) -> dict[str, Any]:
        if isinstance(event, dict):
            return dict(event)
        return {
            "type": "unstructured_event",
            "description": str(event),
            "severity": "low",
        }

    def _severity_score(self, severity: Any) -> float:
        table = {
            "critical": 1.0,
            "high": 0.88,
            "medium": 0.62,
            "normal": 0.48,
            "low": 0.30,
            "info": 0.22,
        }
        return table.get(str(severity).lower(), self._clamp(severity, 0.30, 1.0))

    def _type_score(self, event_type: Any) -> float:
        normalized = str(event_type or "").lower()
        table = {
            "critical_failure": 1.0,
            "anomaly": 0.94,
            "closure_risk": 0.94,
            "risk_of_closure": 0.94,
            "certification_reached": 0.92,
            "certification": 0.88,
            "beneficial_mutation": 0.88,
            "mutation_benefique": 0.88,
            "runtime_failure": 0.86,
            "validation_failure": 0.84,
            "governance_alert": 0.82,
            "civilizational_event": 0.78,
            "opportunity": 0.66,
            "project_follow_up": 0.58,
            "status_update": 0.44,
            "heartbeat": 0.18,
        }
        if normalized in table:
            return table[normalized]
        if "failure" in normalized or "critical" in normalized:
            return 0.92
        if "certification" in normalized:
            return 0.88
        if "mutation" in normalized:
            return 0.82
        if "risk" in normalized or "closure" in normalized:
            return 0.86
        if "anomal" in normalized:
            return 0.88
        return 0.42

    def _event_score(self, event: dict[str, Any]) -> float:
        explicit = event.get("relevance_score")
        if explicit is not None:
            return self._clamp(explicit)

        event_type_score = self._type_score(event.get("type"))
        severity_score = self._severity_score(event.get("severity"))
        confidence = self._clamp(event.get("confidence", 0.90), 0.0, 1.0)

        return self._clamp(
            (0.50 * event_type_score)
            + (0.35 * severity_score)
            + (0.15 * confidence)
        )

    def _extract_events(self, inputs: Any) -> list[dict[str, Any]]:
        if inputs is None:
            return []

        if isinstance(inputs, dict):
            events = []
            events.extend(self._as_list(inputs.get("events")))
            if "event" in inputs:
                events.extend(self._as_list(inputs.get("event")))
            return [self._normalize_event(event) for event in events]

        return [self._normalize_event(event) for event in self._as_list(inputs)]

    def _governance(self, inputs: Any) -> dict[str, Any]:
        if isinstance(inputs, dict) and isinstance(inputs.get("governance"), dict):
            return dict(inputs["governance"])
        return {}

    def _message_for(self, event: dict[str, Any], score: float) -> str:
        event_type = str(event.get("type", "event"))
        description = str(event.get("description") or "événement pertinent détecté")
        severity = str(event.get("severity", "unspecified"))
        return (
            "Initiative conversationnelle autonome : "
            f"{description} "
            f"(type={event_type}, sévérité={severity}, pertinence={score:.3f}). "
            "Je recommande d'examiner cet événement avant de poursuivre le runtime."
        )

    def _load_recent_history(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []
        records: list[dict[str, Any]] = []
        try:
            for line in self.history_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(json.loads(line))
        except Exception:
            return []
        return records[-self.history_limit :]

    def _precision_rate(self, history: list[dict[str, Any]], current_triggered: bool) -> float:
        if not history and not current_triggered:
            return 1.0
        triggered = [record for record in history if record.get("should_initiate_dialogue")]
        if current_triggered:
            triggered.append({"should_initiate_dialogue": True, "governance_allowed": True})
        if not triggered:
            return 1.0
        allowed = [record for record in triggered if record.get("governance_allowed", True)]
        return self._clamp(len(allowed) / len(triggered))

    def _append_history(self, record: dict[str, Any]) -> None:
        try:
            self.history_dir.mkdir(parents=True, exist_ok=True)
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        except Exception:
            pass

    def step(self, inputs: Any = None) -> dict[str, Any]:
        events = self._extract_events(inputs)
        governance = self._governance(inputs)

        noise_ratio = self._clamp(governance.get("noise_ratio", 0.0))
        frequency_limited = bool(governance.get("frequency_limited", False))
        repetition_risk = self._clamp(governance.get("repetition_risk", 0.0))

        scored_events = [
            {
                "event": event,
                "score": self._event_score(event),
            }
            for event in events
        ]
        scored_events.sort(key=lambda item: item["score"], reverse=True)

        top = scored_events[0] if scored_events else None
        top_event = top["event"] if top else None
        relevance_score = self._clamp(top["score"] if top else 0.0)

        governance_allowed = (
            noise_ratio <= self.noise_threshold
            and not frequency_limited
            and repetition_risk < 0.50
        )
        should_initiate = (
            top_event is not None
            and relevance_score >= self.relevance_threshold
            and governance_allowed
        )

        message = self._message_for(top_event, relevance_score) if should_initiate else ""

        history = self._load_recent_history()
        previous_trigger_count = sum(
            1 for record in history if record.get("should_initiate_dialogue")
        )
        initiative_trigger_count = previous_trigger_count + (1 if should_initiate else 0)
        initiative_precision_rate = self._precision_rate(history, should_initiate)

        suppression_reasons: list[str] = []
        if top_event is None:
            suppression_reasons.append("no_event")
        if relevance_score < self.relevance_threshold:
            suppression_reasons.append("below_relevance_threshold")
        if noise_ratio > self.noise_threshold:
            suppression_reasons.append("noise_ratio_above_threshold")
        if frequency_limited:
            suppression_reasons.append("frequency_limited")
        if repetition_risk >= 0.50:
            suppression_reasons.append("repetition_risk")

        result = {
            "primitive": "PROACTIVE_CONVERSATIONAL_INITIATIVE",
            "timestamp": self._now(),
            "events_observed": len(events),
            "selected_event": top_event,
            "initiative_trigger_count": initiative_trigger_count,
            "initiative_relevance_score": relevance_score,
            "initiative_precision_rate": initiative_precision_rate,
            "proactive_initiative_score": relevance_score,
            "should_initiate_dialogue": should_initiate,
            "initiative_message": message,
            "suppression_reasons": suppression_reasons,
            "governance_allowed": governance_allowed,
            "noise_ratio": noise_ratio,
            "diagnostics": {
                "relevance_threshold": self.relevance_threshold,
                "noise_threshold": self.noise_threshold,
                "scored_event_count": len(scored_events),
                "top_score": relevance_score,
                "event_driven": True,
                "anti_spam_enabled": True,
                "anti_repetition_enabled": True,
            },
        }

        self._append_history(result)
        return result


ENGINE = ProactiveConversationalInitiative()


def step(inputs: Any = None) -> dict[str, Any]:
    return ENGINE.step(inputs)
