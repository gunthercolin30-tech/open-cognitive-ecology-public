# -*- coding: utf-8 -*-
"""
D3 — Civilizational Notification Engine.

This primitive does not duplicate alerting, monitoring or conversational agents.
It transforms normalized events and proactive initiative decisions into typed,
contextual, governance-aware civilizational notifications.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

PRIMITIVE = "civilizational_notification_engine"
DEPENDENCIES = [
    "conversational_event_detector",
    "proactive_conversational_initiative",
    "alerting_and_notification_system",
    "constitutional_alert_system",
    "conversation_memory_archive",
]


class CivilizationalNotificationEngine:
    """Convert D2/D1 event decisions into structured notifications."""

    TYPE_TO_NOTIFICATION = {
        "critical_failure": "alert",
        "anomaly": "diagnostic",
        "closure_risk": "alert",
        "certification": "report",
        "certification_reached": "report",
        "beneficial_mutation": "suggestion",
        "civilizational_milestone": "report",
        "runtime_state": "diagnostic",
        "monitoring_signal": "diagnostic",
        "opportunity": "suggestion",
        "informational": "summary",
    }

    TYPE_ACTIONS = {
        "critical_failure": "Suspendre la poursuite automatique et examiner la cause avant tout nouveau cycle.",
        "anomaly": "Examiner le signal, comparer avec l'historique et décider si une correction est nécessaire.",
        "closure_risk": "Réduire la pression de clôture, préserver les alternatives et vérifier les contraintes d'ouverture.",
        "certification": "Archiver la certification, consigner les métriques et poursuivre la validation longitudinale.",
        "certification_reached": "Archiver la certification, consigner les métriques et préparer l'étape suivante.",
        "beneficial_mutation": "Tracer la mutation bénéfique, vérifier sa réversibilité et envisager son intégration gouvernée.",
        "civilizational_milestone": "Historiser le jalon et vérifier sa cohérence avec la trajectoire civilisationnelle.",
        "runtime_state": "Contrôler l'état runtime et décider si une intervention est utile.",
        "monitoring_signal": "Observer l'évolution du signal avant amplification conversationnelle.",
        "opportunity": "Évaluer l'opportunité selon impact, coût, réversibilité et non-clôture.",
        "informational": "Conserver l'information sans interrompre le runtime.",
    }

    PRIORITY_LABELS = [
        (0.92, "critical"),
        (0.82, "high"),
        (0.65, "medium"),
        (0.40, "low"),
        (0.00, "informational"),
    ]

    def __init__(self) -> None:
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

    def _priority_label(self, score: float) -> str:
        score = self._bounded(score)
        for threshold, label in self.PRIORITY_LABELS:
            if score >= threshold:
                return label
        return "informational"

    def _select_event(self, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        candidate = inputs.get("event") or inputs.get("selected_event") or inputs.get("top_relevant_event")
        if isinstance(candidate, dict):
            return candidate

        for key in ("relevant_events", "detected_events", "events"):
            events = [event for event in self._as_list(inputs.get(key)) if isinstance(event, dict)]
            if events:
                return sorted(events, key=lambda event: self._event_score(event), reverse=True)[0]
        return None

    def _event_score(self, event: Dict[str, Any]) -> float:
        return self._bounded(
            event.get("priority_score", event.get("relevance", event.get("score", 0.0)))
        )

    def _notification_type(self, event: Optional[Dict[str, Any]], initiative: Dict[str, Any]) -> str:
        if not event:
            return "summary"
        event_type = str(event.get("type", "informational"))
        if initiative.get("suppression_reasons"):
            return "governance_notice"
        return self.TYPE_TO_NOTIFICATION.get(event_type, "summary")

    def _diagnostic(self, event: Optional[Dict[str, Any]], initiative: Dict[str, Any]) -> str:
        if not event:
            return "Aucun événement conversationnel pertinent n'a été sélectionné."
        event_type = event.get("type", "informational")
        score = self._event_score(event)
        source = event.get("source", "unknown")
        severity = event.get("severity", "normal")
        if initiative.get("suppression_reasons"):
            reasons = ", ".join(str(r) for r in initiative.get("suppression_reasons", []))
            return f"Événement pertinent détecté mais notification gouvernée/supprimée: {reasons}."
        return f"Événement {event_type} détecté depuis {source}, sévérité={severity}, priorité={score:.3f}."

    def _recommended_action(self, event: Optional[Dict[str, Any]], notification_type: str) -> str:
        if not event:
            return "Maintenir l'observation sans générer de notification proactive."
        event_type = str(event.get("type", "informational"))
        if notification_type == "governance_notice":
            return "Respecter la gouvernance conversationnelle et différer l'émission du message."
        return self.TYPE_ACTIONS.get(event_type, "Examiner l'événement avant toute action irréversible.")

    def _message(self, event: Optional[Dict[str, Any]], notification_type: str, diagnostic: str, action: str) -> str:
        if not event:
            return "Aucune notification civilisationnelle n'est nécessaire pour le moment."
        description = str(event.get("description", "Événement non décrit"))
        event_type = str(event.get("type", "informational"))
        priority = self._priority_label(self._event_score(event))
        if notification_type == "governance_notice":
            return f"Notification gouvernée : {description}. {diagnostic} Action recommandée : {action}"
        prefix = {
            "alert": "Alerte civilisationnelle",
            "diagnostic": "Diagnostic civilisationnel",
            "suggestion": "Suggestion civilisationnelle",
            "question": "Question civilisationnelle",
            "report": "Rapport civilisationnel",
            "summary": "Synthèse civilisationnelle",
        }.get(notification_type, "Notification civilisationnelle")
        return (
            f"{prefix} [{priority}] : {description} "
            f"(type={event_type}). {diagnostic} Action recommandée : {action}"
        )

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        timestamp = self._now()
        initiative = inputs.get("initiative") if isinstance(inputs.get("initiative"), dict) else inputs
        event = self._select_event(inputs)

        should_notify = bool(
            event
            and initiative.get("should_initiate_dialogue", inputs.get("conversation_ready", True))
            and not initiative.get("suppression_reasons")
        )
        notification_type = self._notification_type(event, initiative if isinstance(initiative, dict) else {})
        score = self._event_score(event) if event else 0.0
        diagnostic = self._diagnostic(event, initiative if isinstance(initiative, dict) else {})
        action = self._recommended_action(event, notification_type)
        message = self._message(event, notification_type, diagnostic, action) if should_notify else ""

        contextualization_score = self._bounded(
            0.25
            + (0.25 if event and event.get("description") else 0.0)
            + (0.20 if event and event.get("type") else 0.0)
            + (0.15 if event and event.get("source") else 0.0)
            + (0.15 if action else 0.0)
        )
        notification_quality_score = round(
            self._bounded(0.45 * score + 0.30 * contextualization_score + 0.25 * (1.0 if should_notify else 0.0)),
            3,
        )

        result = {
            "primitive": "CIVILIZATIONAL_NOTIFICATION_ENGINE",
            "timestamp": timestamp,
            "notification_emitted": should_notify,
            "notification_type": notification_type,
            "notification_priority": self._priority_label(score),
            "notification_message": message,
            "diagnostic": diagnostic,
            "recommended_action": action,
            "selected_event": event,
            "notification_quality_score": notification_quality_score,
            "contextualization_score": round(contextualization_score, 3),
            "conversation_ready": should_notify,
            "diagnostics": {
                "event_to_notification_layer": True,
                "does_not_duplicate_alerting": True,
                "does_not_duplicate_dialogue_agent": True,
                "governance_aware": True,
                "history_length": len(self.history) + 1,
            },
        }
        self.history.append(result)
        return result


ENGINE = CivilizationalNotificationEngine()


def step(inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return ENGINE.step(inputs)
