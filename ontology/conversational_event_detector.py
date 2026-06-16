# -*- coding: utf-8 -*-
'''
D2 — Conversational Event Detector.

This primitive does not duplicate monitoring, alerting or dashboard modules.
It aggregates heterogeneous observations, normalises them into conversational
candidate events, scores their relevance, and exposes the highest-priority
items to proactive_conversational_initiative.
'''

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

PRIMITIVE = "conversational_event_detector"
DEPENDENCIES = [
    "monitoring",
    "constraint_monitoring_system",
    "constitutional_alert_system",
    "alerting_and_notification_system",
    "runtime_experiment_manager",
    "longitudinal_civilizational_autonomy_tracker",
    "proactive_conversational_initiative",
]


class ConversationalEventDetector:
    """Aggregate, normalise and prioritise events suitable for autonomous dialogue."""

    EVENT_TYPE_WEIGHTS = {
        "critical_failure": 1.00,
        "anomaly": 0.92,
        "closure_risk": 0.91,
        "certification": 0.88,
        "certification_reached": 0.88,
        "beneficial_mutation": 0.86,
        "civilizational_milestone": 0.82,
        "runtime_state": 0.70,
        "monitoring_signal": 0.64,
        "opportunity": 0.62,
        "informational": 0.45,
    }

    SEVERITY_WEIGHTS = {
        "critical": 1.00,
        "high": 0.88,
        "medium": 0.66,
        "normal": 0.50,
        "low": 0.35,
        "info": 0.25,
    }

    RELEVANT_TYPES = {
        "critical_failure",
        "anomaly",
        "closure_risk",
        "certification",
        "certification_reached",
        "beneficial_mutation",
        "civilizational_milestone",
    }

    def __init__(self, relevance_threshold: float = 0.70) -> None:
        self.relevance_threshold = self._bounded(relevance_threshold)
        self.history: List[Dict[str, Any]] = []

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

    def _severity_from_score(self, score: float) -> str:
        score = self._bounded(score)
        if score >= 0.92:
            return "critical"
        if score >= 0.80:
            return "high"
        if score >= 0.60:
            return "medium"
        if score >= 0.35:
            return "normal"
        return "low"

    def _canonical_type(self, raw_type: Any, source: str = "external") -> str:
        text = str(raw_type or "").strip().lower()
        aliases = {
            "failure": "critical_failure",
            "error": "critical_failure",
            "critical": "critical_failure",
            "critical_failure": "critical_failure",
            "alert": "anomaly",
            "warning": "anomaly",
            "anomaly": "anomaly",
            "drift": "anomaly",
            "closure": "closure_risk",
            "closure_risk": "closure_risk",
            "anti_closure": "closure_risk",
            "certification": "certification",
            "certification_reached": "certification_reached",
            "certified": "certification",
            "mutation": "beneficial_mutation",
            "beneficial_mutation": "beneficial_mutation",
            "milestone": "civilizational_milestone",
            "civilizational_milestone": "civilizational_milestone",
            "runtime": "runtime_state",
            "monitoring": "monitoring_signal",
            "opportunity": "opportunity",
        }
        if text in aliases:
            return aliases[text]
        if source in {"constitutional_alert_system", "alerting_and_notification_system", "constraint_monitoring_system"}:
            return "anomaly"
        if source in {"longitudinal_civilizational_autonomy_tracker", "civilizational_dashboard"}:
            return "civilizational_milestone"
        if source in {"runtime_experiment_manager", "experiment_stability_dashboard"}:
            return "runtime_state"
        return "informational"

    def _score_event(self, event: Dict[str, Any]) -> float:
        event_type = event.get("type", "informational")
        severity = event.get("severity", "normal")
        explicit = event.get("score", event.get("priority", event.get("relevance")))
        type_score = self.EVENT_TYPE_WEIGHTS.get(event_type, 0.45)
        severity_score = self.SEVERITY_WEIGHTS.get(str(severity).lower(), 0.50)
        explicit_score = self._bounded(explicit, (type_score + severity_score) / 2.0)
        freshness_score = 0.92 if event.get("timestamp") else 0.78
        traceability_score = 0.94 if event.get("source") else 0.70
        return round(
            0.42 * type_score
            + 0.28 * severity_score
            + 0.20 * explicit_score
            + 0.05 * freshness_score
            + 0.05 * traceability_score,
            3,
        )

    def _normalise_event(self, raw: Any, source: str = "external") -> Optional[Dict[str, Any]]:
        if raw is None:
            return None
        if isinstance(raw, str):
            raw = {"description": raw, "type": "informational"}
        if not isinstance(raw, dict):
            return None

        event_type = self._canonical_type(
            raw.get("type") or raw.get("event_type") or raw.get("category"),
            source=source,
        )
        severity = str(raw.get("severity") or raw.get("level") or "normal").lower()
        if severity not in self.SEVERITY_WEIGHTS:
            if event_type == "critical_failure":
                severity = "critical"
            elif event_type in {"anomaly", "closure_risk", "certification", "certification_reached"}:
                severity = "high"
            else:
                severity = "normal"

        description = (
            raw.get("description")
            or raw.get("message")
            or raw.get("title")
            or raw.get("name")
            or f"Event detected from {source}"
        )
        event = {
            "type": event_type,
            "description": str(description),
            "severity": severity,
            "source": str(raw.get("source") or source),
            "timestamp": raw.get("timestamp") or raw.get("timestamp_utc") or self._now(),
            "raw": raw,
        }
        event["priority_score"] = self._score_event(event)
        event["conversation_relevant"] = (
            event["type"] in self.RELEVANT_TYPES
            and event["priority_score"] >= self.relevance_threshold
        )
        return event

    def _events_from_dict(self, payload: Dict[str, Any], source: str) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        for key in ("events", "alerts", "detected_events", "candidate_events"):
            for raw in self._as_list(payload.get(key)):
                event = self._normalise_event(raw, source=source)
                if event:
                    events.append(event)

        # Convert common scalar diagnostics into event candidates.
        if payload.get("certified") is True or payload.get("certification"):
            event = self._normalise_event(
                {
                    "type": "certification",
                    "description": f"Certification observed: {payload.get('certification', 'validated')}",
                    "severity": "high",
                    "score": payload.get("global_viability_score", payload.get("score", 0.86)),
                    "source": source,
                    "timestamp": payload.get("timestamp") or payload.get("generated_at"),
                },
                source=source,
            )
            if event:
                events.append(event)

        error_count = payload.get("error_count")
        failed_calls = payload.get("failed_calls")
        if isinstance(error_count, (int, float)) and error_count > 0:
            event = self._normalise_event(
                {
                    "type": "critical_failure",
                    "description": f"Execution errors detected: error_count={error_count}",
                    "severity": "critical" if error_count >= 3 else "high",
                    "score": min(1.0, 0.75 + float(error_count) / 10.0),
                    "source": source,
                },
                source=source,
            )
            if event:
                events.append(event)
        if isinstance(failed_calls, (int, float)) and failed_calls > 0:
            event = self._normalise_event(
                {
                    "type": "critical_failure",
                    "description": f"Failed calls detected: failed_calls={failed_calls}",
                    "severity": "high",
                    "score": min(1.0, 0.70 + float(failed_calls) / 10.0),
                    "source": source,
                },
                source=source,
            )
            if event:
                events.append(event)

        for key in ("closure_risk", "semantic_isolation_risk", "collapse_risk"):
            if key in payload:
                score = self._bounded(payload.get(key))
                if score >= 0.50:
                    event = self._normalise_event(
                        {
                            "type": "closure_risk",
                            "description": f"Closure-related risk detected: {key}={score:.3f}",
                            "severity": self._severity_from_score(score),
                            "score": score,
                            "source": source,
                        },
                        source=source,
                    )
                    if event:
                        events.append(event)

        for key in ("beneficial_pipeline_rate", "beneficial_mutation_ratio", "evolvability_index"):
            if key in payload:
                score = self._bounded(payload.get(key))
                if score >= 0.85:
                    event = self._normalise_event(
                        {
                            "type": "beneficial_mutation",
                            "description": f"Beneficial evolution signal detected: {key}={score:.3f}",
                            "severity": "high",
                            "score": score,
                            "source": source,
                        },
                        source=source,
                    )
                    if event:
                        events.append(event)

        return events

    def _safe_call_module(self, module_name: str, class_name: str, source: str) -> List[Dict[str, Any]]:
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            result = instance.step()
        except Exception:
            return []
        if isinstance(result, dict):
            return self._events_from_dict(result, source=source)
        return []

    def _collect_internal_events(self) -> List[Dict[str, Any]]:
        # Only import-safe, no-argument modules are called here. All failures are silent,
        # because the detector must not destabilise global validation.
        calls = [
            ("monitoring", "Monitoring", "monitoring"),
            ("constraint_monitoring_system", "ConstraintMonitoringSystem", "constraint_monitoring_system"),
            ("constitutional_alert_system", "ConstitutionalAlertSystem", "constitutional_alert_system"),
            ("alerting_and_notification_system", "AlertingAndNotificationSystem", "alerting_and_notification_system"),
            ("longitudinal_civilizational_autonomy_tracker", "LongitudinalCivilizationalAutonomyTracker", "longitudinal_civilizational_autonomy_tracker"),
        ]
        events: List[Dict[str, Any]] = []
        for module_name, class_name, source in calls:
            events.extend(self._safe_call_module(module_name, class_name, source))
        return events

    def _deduplicate(self, events: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique: List[Dict[str, Any]] = []
        for event in events:
            key = (
                event.get("type"),
                event.get("description"),
                event.get("source"),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(event)
        return unique

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        timestamp = self._now()
        raw_events: List[Dict[str, Any]] = []

        for raw in self._as_list(inputs.get("events")):
            event = self._normalise_event(raw, source="input.events")
            if event:
                raw_events.append(event)

        for source, payload in (inputs.get("sources") or {}).items():
            if isinstance(payload, dict):
                raw_events.extend(self._events_from_dict(payload, source=str(source)))
            else:
                for item in self._as_list(payload):
                    event = self._normalise_event(item, source=str(source))
                    if event:
                        raw_events.append(event)

        if inputs.get("collect_internal", False):
            raw_events.extend(self._collect_internal_events())

        events = self._deduplicate(raw_events)
        events.sort(key=lambda item: item.get("priority_score", 0.0), reverse=True)
        relevant_events = [event for event in events if event.get("conversation_relevant")]
        top_event = events[0] if events else None
        top_relevant_event = relevant_events[0] if relevant_events else None

        detected_event_count = len(events)
        relevant_event_count = len(relevant_events)
        event_detection_rate = 1.0 if detected_event_count > 0 else 0.0
        relevant_event_ratio = (
            round(relevant_event_count / detected_event_count, 3)
            if detected_event_count
            else 0.0
        )
        event_priority_score = round(
            top_event.get("priority_score", 0.0) if top_event else 0.0,
            3,
        )
        civilizational_event_count = sum(
            1 for event in events
            if event.get("type") in {
                "certification",
                "certification_reached",
                "beneficial_mutation",
                "closure_risk",
                "civilizational_milestone",
            }
        )

        result = {
            "primitive": "CONVERSATIONAL_EVENT_DETECTOR",
            "timestamp": timestamp,
            "detected_events": events,
            "relevant_events": relevant_events,
            "top_event": top_event,
            "top_relevant_event": top_relevant_event,
            "detected_event_count": detected_event_count,
            "relevant_event_count": relevant_event_count,
            "civilizational_event_count": civilizational_event_count,
            "event_detection_rate": round(event_detection_rate, 3),
            "relevant_event_ratio": relevant_event_ratio,
            "event_priority_score": event_priority_score,
            "conversation_ready": top_relevant_event is not None,
            "diagnostics": {
                "aggregation_layer": True,
                "normalization_layer": True,
                "does_not_duplicate_monitoring": True,
                "relevance_threshold": self.relevance_threshold,
                "supported_event_types": sorted(self.EVENT_TYPE_WEIGHTS),
            },
        }
        self.history.append(result)
        return result


ENGINE = ConversationalEventDetector()


def step(inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return ENGINE.step(inputs)
