# -*- coding: utf-8 -*-
"""
D5 — Terminal Communication Runtime.

This primitive is a terminal-facing adapter. It does not replace the existing
civilizational runtimes. It delegates event detection, initiative decision,
notification generation and persistence to PersistentCivilizationalConversationalAgent,
then emits authorised autonomous messages to stdout and records terminal metrics.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PRIMITIVE = "terminal_conversation_runtime"
DEPENDENCIES = [
    "persistent_civilizational_conversational_agent",
    "conversational_event_detector",
    "proactive_conversational_initiative",
    "civilizational_notification_engine",
    "persistent_civilizational_runtime",
    "autonomous_runtime_service",
]


class TerminalConversationRuntime:
    """Emit governed autonomous civilizational messages in the terminal."""

    def __init__(self, log_dir: Optional[Path] = None, prefix: str = "[Open Cognitive Ecology]") -> None:
        self.root = Path.home() / "open-cognitive-ecology"
        self.log_dir = Path(log_dir) if log_dir else self.root / "terminal_conversation_runtime"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / "terminal_messages.jsonl"
        self.state_path = self.log_dir / "terminal_runtime_state.json"
        self.prefix = prefix
        self.history: List[Dict[str, Any]] = []
        self.spontaneous_message_count = 0
        self.successful_emissions = 0
        self.failed_emissions = 0

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _bounded(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        return max(0.0, min(1.0, number))

    def _load_agent(self):
        from ontology.persistent_civilizational_conversational_agent import (
            PersistentCivilizationalConversationalAgent,
        )
        return PersistentCivilizationalConversationalAgent()

    def _build_default_event(self) -> Dict[str, Any]:
        return {
            "type": "runtime_state",
            "description": "Terminal communication runtime cycle executed",
            "severity": "normal",
            "score": 0.72,
            "source": "terminal_conversation_runtime",
        }

    def _normalise_inputs(self, inputs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        payload = dict(inputs or {})
        if "events" not in payload and "sources" not in payload:
            payload["events"] = [self._build_default_event()]
        payload.setdefault("user_message", "")
        payload.setdefault("governance", {"noise_ratio": 0.0})
        return payload

    def _emit(self, message: str, emit_to_stdout: bool = True) -> bool:
        if not message:
            return False
        try:
            if emit_to_stdout:
                print(f"{self.prefix} {message}", flush=True)
            return True
        except Exception:
            return False

    def _append_log(self, record: Dict[str, Any]) -> None:
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _save_state(self, state: Dict[str, Any]) -> None:
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def step(self, inputs: Optional[Dict[str, Any]] = None, emit_to_stdout: bool = True) -> Dict[str, Any]:
        payload = self._normalise_inputs(inputs)
        timestamp = self._now()
        agent = self._load_agent()
        agent_result = agent.step(payload)

        notification = agent_result.get("notification_result", {}) if isinstance(agent_result, dict) else {}
        initiative = agent_result.get("initiative_result", {}) if isinstance(agent_result, dict) else {}
        event_result = agent_result.get("event_result", {}) if isinstance(agent_result, dict) else {}

        notification_emitted = bool(notification.get("notification_emitted"))
        should_initiate = bool(initiative.get("should_initiate_dialogue"))
        terminal_ready = notification_emitted and should_initiate
        message = notification.get("notification_message") or agent_result.get("agent_response", "")

        emitted = False
        if terminal_ready:
            emitted = self._emit(message, emit_to_stdout=emit_to_stdout)

        if terminal_ready:
            self.spontaneous_message_count += 1
        if emitted:
            self.successful_emissions += 1
        elif terminal_ready:
            self.failed_emissions += 1

        attempted = self.successful_emissions + self.failed_emissions
        spontaneous_message_success_rate = (
            round(self.successful_emissions / attempted, 3)
            if attempted
            else 1.0
        )
        terminal_conversation_index = round(
            0.35 * (1.0 if terminal_ready else 0.0)
            + 0.30 * (1.0 if emitted or not terminal_ready else 0.0)
            + 0.20 * self._bounded(agent_result.get("conversation_continuity_score", 0.0))
            + 0.15 * self._bounded(agent_result.get("context_retention_score", 0.0)),
            3,
        )

        record = {
            "primitive": "TERMINAL_CONVERSATION_RUNTIME",
            "timestamp": timestamp,
            "terminal_ready": terminal_ready,
            "terminal_message_emitted": emitted,
            "spontaneous_message_count": self.spontaneous_message_count,
            "spontaneous_message_success_rate": spontaneous_message_success_rate,
            "terminal_conversation_index": terminal_conversation_index,
            "message": message if terminal_ready else "",
            "agent_result": agent_result,
            "event_ready": bool(event_result.get("conversation_ready")),
            "initiative_allowed": should_initiate,
            "notification_emitted": notification_emitted,
            "suppression_reasons": initiative.get("suppression_reasons", []),
            "log_path": str(self.log_path),
            "state_path": str(self.state_path),
            "diagnostics": {
                "terminal_adapter": True,
                "does_not_replace_runtime": True,
                "d1_d2_d3_d4_chain_enabled": True,
                "stdout_emission_enabled": bool(emit_to_stdout),
                "history_length": len(self.history) + 1,
            },
        }

        self.history.append(record)
        self._append_log(record)
        # E1 METRICS HISTORY RECORDER HOOK
        try:
            from ontology.metrics_history_recorder import record_metrics
            record_metrics(
                record,
                primitive="terminal_conversation_runtime",
                validation_status="validated" if record.get("terminal_conversation_index", 0.0) >= 0.0 else "unknown",
                governance_status="governed" if record.get("initiative_allowed", False) else "observed",
                runtime_status="operational",
            )
        except Exception:
            pass
        self._save_state(record)
        return record

    def run_once(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.step(inputs=inputs, emit_to_stdout=True)

    def run_loop(self, cycles: int = 3, sleep_seconds: float = 1.0, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        results = []
        safe_cycles = max(1, int(cycles))
        safe_sleep = max(0.0, float(sleep_seconds))
        for _ in range(safe_cycles):
            results.append(self.step(inputs=inputs, emit_to_stdout=True))
            if safe_sleep:
                time.sleep(safe_sleep)
        return {
            "primitive": "TERMINAL_CONVERSATION_RUNTIME",
            "cycles_executed": safe_cycles,
            "spontaneous_message_count": self.spontaneous_message_count,
            "spontaneous_message_success_rate": results[-1]["spontaneous_message_success_rate"] if results else 1.0,
            "latest_result": results[-1] if results else None,
            "results": results,
        }


ENGINE = TerminalConversationRuntime()


def step(inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return ENGINE.step(inputs=inputs, emit_to_stdout=True)
