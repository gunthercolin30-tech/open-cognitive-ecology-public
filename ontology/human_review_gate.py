from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

try:
    from ontology.human_review_terminal_interface import HumanReviewTerminalInterface
except Exception:  # pragma: no cover
    from human_review_terminal_interface import HumanReviewTerminalInterface


class HumanReviewGate:
    """Governed human review gate for high-risk execution requests.

    Functional role:
    - detect whether human review is mandatory;
    - keep risky execution pending until authorized;
    - interpret human responses through the terminal interface;
    - persist an auditable record;
    - never execute risky actions directly.
    """

    primitive = "human_review_gate"

    RISK_TRIGGERS = {
        "external_publication",
        "publication_external",
        "zenodo_publication",
        "github_release",
        "physical_action",
        "actuator_action",
        "self_modification",
        "governance_modification",
        "constitutional_modification",
        "mass_data_deletion",
        "data_deletion",
        "strategic_reorientation",
        "irreversible_action",
        "credential_access",
        "network_deployment",
    }

    def __init__(self, state_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.state_dir = Path(state_dir) if state_dir else root / "governance" / "human_review"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.interface = HumanReviewTerminalInterface(self.state_dir)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_id(self, value: Any, fallback: str = "human_review") -> str:
        text = str(value or fallback).strip() or fallback
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in text)[:120]

    def _persist(self, review_id: str, payload: dict[str, Any]) -> Path:
        path = self.state_dir / f"{self._safe_id(review_id)}_gate.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")

        latest = self.state_dir / "latest_human_review_gate.json"
        latest.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")

        # Longitudinal audit log required for L8 persistence tests and later L10-L13 dashboards.
        history = self.state_dir / "human_review_history.jsonl"
        with history.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

        # Compatibility alias for tests and dashboard collectors expecting an explicit log name.
        log_alias = self.state_dir / "human_review_log.jsonl"
        with log_alias.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

        return path

    def _collect_tokens(self, request: dict[str, Any]) -> set[str]:
        fields = [
            "action_type", "risk_class", "execution_type", "request_type",
            "target", "category", "action", "primitive", "operation",
        ]
        tokens: set[str] = set()
        for field in fields:
            value = request.get(field)
            if value is None:
                continue
            normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
            if normalized:
                tokens.add(normalized)
        for flag in request.get("risk_flags", []) or []:
            normalized = str(flag).strip().lower().replace(" ", "_").replace("-", "_")
            if normalized:
                tokens.add(normalized)
        return tokens

    def requires_review(self, request: dict[str, Any]) -> tuple[bool, list[str]]:
        if bool(request.get("human_review_required")):
            return True, ["explicit_human_review_required"]
        if bool(request.get("requires_human_review")):
            return True, ["explicit_requires_human_review"]
        if request.get("reversibility") == "irreversible" or request.get("rollback_available") is False:
            return True, ["irreversibility_or_no_rollback"]
        if float(request.get("risk_score", 0.0) or 0.0) >= 0.75:
            return True, ["high_risk_score"]
        tokens = self._collect_tokens(request)
        hits = sorted(tokens.intersection(self.RISK_TRIGGERS))
        if hits:
            return True, hits
        return False, []

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        request = dict(inputs.get("execution_request") or inputs.get("dispatch_result") or inputs.get("request") or inputs)
        review_id = request.get("human_review_id") or request.get("execution_request_id") or request.get("execution_id") or f"HR-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

        required, triggers = self.requires_review(request)
        base = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": self._now(),
            "human_review_id": review_id,
            "execution_request_id": request.get("execution_request_id"),
            "human_review_required": required,
            "review_triggers": triggers,
        }

        if not required:
            result = {
                **base,
                "human_review_status": "not_required",
                "execution_release_status": "released_without_human_review",
                "execution_authorized": True,
                "blocked": False,
                "machine_actionable": True,
                "human_review_rationale": "No human review trigger detected.",
            }
            result["state_path"] = str(self._persist(str(review_id), result))
            return result

        terminal_result = self.interface.step({
            "review_request": {**request, "human_review_id": review_id},
            "human_response": inputs.get("human_response") or request.get("human_response"),
            "interactive": bool(inputs.get("interactive", False)),
            "rationale_required": inputs.get("rationale_required", True),
        })
        status = terminal_result.get("human_review_status", "pending")
        machine_actionable = bool(terminal_result.get("machine_actionable", False))

        if status == "authorized" and machine_actionable:
            release_status = "released_after_human_authorization"
            execution_authorized = True
            blocked = False
        elif status == "rejected" and machine_actionable:
            release_status = "blocked_by_human_rejection"
            execution_authorized = False
            blocked = True
        elif status == "deferred" and machine_actionable:
            release_status = "deferred_by_human_review"
            execution_authorized = False
            blocked = True
        else:
            release_status = "pending_human_review_or_clarification"
            execution_authorized = False
            blocked = True

        result = {
            **base,
            "human_review_status": status,
            "human_review_timestamp": terminal_result.get("timestamp_utc"),
            "human_reviewer_id": inputs.get("human_reviewer_id", request.get("human_reviewer_id", "human_operator")),
            "human_review_rationale": terminal_result.get("human_review_rationale", ""),
            "terminal_interaction": terminal_result,
            "machine_actionable": machine_actionable,
            "clarification_required": terminal_result.get("clarification_required", False),
            "execution_release_status": release_status,
            "execution_authorized": execution_authorized,
            "blocked": blocked,
            "audit_trace": {
                "request": request,
                "review_required": required,
                "review_triggers": triggers,
                "response_interpretation": terminal_result.get("interpretation", {}),
            },
        }
        result["state_path"] = str(self._persist(str(review_id), result))
        return result
