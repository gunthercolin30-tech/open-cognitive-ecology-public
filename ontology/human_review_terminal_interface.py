from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

try:
    from ontology.human_review_response_interpreter import HumanReviewResponseInterpreter
except Exception:  # pragma: no cover - fallback for direct local execution
    from human_review_response_interpreter import HumanReviewResponseInterpreter


class HumanReviewTerminalInterface:
    """Terminal-facing human review interface for governed execution.

    It can either run non-interactively with a supplied human_response, or
    interactively prompt a terminal user when interactive=True.
    """

    primitive = "human_review_terminal_interface"

    def __init__(self, state_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.state_dir = Path(state_dir) if state_dir else root / "governance" / "human_review"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.interpreter = HumanReviewResponseInterpreter()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_id(self, value: Any, fallback: str = "review") -> str:
        text = str(value or fallback).strip() or fallback
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in text)[:120]

    def _persist(self, review_id: str, payload: dict[str, Any]) -> Path:
        path = self.state_dir / f"{self._safe_id(review_id)}.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        latest = self.state_dir / "latest_human_review_terminal_interaction.json"
        latest.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return path

    def _build_prompt(self, request: dict[str, Any]) -> str:
        review_id = request.get("human_review_id") or request.get("execution_request_id") or request.get("execution_id") or "unknown"
        action_type = request.get("action_type") or request.get("risk_class") or request.get("action") or "unspecified_action"
        rationale = request.get("dispatch_rationale") or request.get("rationale") or request.get("reason") or "No rationale provided."
        return (
            "\n=== OPEN COGNITIVE ECOLOGY — HUMAN REVIEW REQUIRED ===\n"
            f"Review ID: {review_id}\n"
            f"Action type: {action_type}\n"
            f"Risk class: {request.get('risk_class', 'unspecified')}\n"
            f"Request status: {request.get('execution_status', request.get('dispatch_status', 'pending'))}\n"
            f"Rationale: {rationale}\n\n"
            "Reply with one of:\n"
            "  authorized — reason: ...\n"
            "  rejected — reason: ...\n"
            "  deferred — reason: ...\n"
            "========================================================\n"
        )

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        request = dict(inputs.get("review_request") or inputs.get("execution_request") or inputs)
        review_id = request.get("human_review_id") or request.get("execution_request_id") or request.get("execution_id") or f"HR-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        prompt = self._build_prompt(request)

        human_response = inputs.get("human_response") or request.get("human_response")
        interactive = bool(inputs.get("interactive", False))
        if interactive and not human_response:
            print(prompt)
            try:
                human_response = input("Human review response: ").strip()
            except EOFError:
                human_response = ""

        interpretation = self.interpreter.step({
            "human_response": human_response or "",
            "rationale_required": inputs.get("rationale_required", True),
        })

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": self._now(),
            "human_review_id": review_id,
            "prompt": prompt,
            "interactive": interactive,
            "response_received": bool(human_response),
            "interpretation": interpretation,
            "human_review_status": interpretation["human_review_status"],
            "human_review_rationale": interpretation["human_review_rationale"],
            "machine_actionable": interpretation["machine_actionable"],
            "clarification_required": interpretation["clarification_required"],
        }
        result["state_path"] = str(self._persist(str(review_id), result))
        return result
