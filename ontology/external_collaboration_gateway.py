from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Any


PRIMITIVE = "external_collaboration_gateway"

DEPENDENCIES = [
    "interaction_queue_manager",
    "autonomous_prompt_generator",
    "internet_cognitive_interface",
    "internet_controlled_gateway",
    "civilizational_external_relations_manager",
    "internet_resident_agent",
    "internet_external_memory_fabric",
    "persistent_external_memory_fabric",
    "metrics_history_recorder",
]

SUPPORTED_PROVIDERS = ["chatgpt", "claude", "gemini", "manual_external_assistant"]


class ExternalCollaborationGateway:
    # O5 prepares and records controlled external collaboration.
    # It does not automate login, browser control, credential use, or direct API calls.

    def __init__(
        self,
        root: Path | None = None,
        gateway_history_file: Path | None = None,
        provider: str = "chatgpt",
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.queue_file = self.root / "external_query_queue.jsonl"
        self.collaboration_history_file = self.root / "collaboration_history.jsonl"
        self.gateway_history_file = (
            Path(gateway_history_file)
            if gateway_history_file is not None
            else self.root / "external_collaboration_gateway_history.jsonl"
        )
        self.gateway_history_file.parent.mkdir(parents=True, exist_ok=True)
        self.provider = provider if provider in SUPPORTED_PROVIDERS else "manual_external_assistant"

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _bounded(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        records = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                raw = line.strip()
                if not raw:
                    continue
                try:
                    item = json.loads(raw)
                    if isinstance(item, dict):
                        records.append(item)
                except json.JSONDecodeError:
                    records.append({
                        "record_type": "corrupted_jsonl_line",
                        "raw_line": raw[:500],
                        "detected_at_utc": self._utc_now(),
                    })
        return records

    def _write_jsonl(self, path: Path, records: list[dict[str, Any]]) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        tmp.replace(path)

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _record_gateway_event(self, event_type: str, payload: dict[str, Any]) -> None:
        self._append_jsonl(self.gateway_history_file, {
            "primitive": PRIMITIVE,
            "event_type": event_type,
            "timestamp_utc": self._utc_now(),
            **payload,
        })

    def _find_query(self, query_id: str) -> tuple[list[dict[str, Any]], int | None, dict[str, Any] | None]:
        records = self._read_jsonl(self.queue_file)
        for index, record in enumerate(records):
            if record.get("query_id") == query_id:
                return records, index, record
        return records, None, None

    def _next_pending_query(self) -> dict[str, Any] | None:
        records = self._read_jsonl(self.queue_file)
        pending = [r for r in records if r.get("query_id") and r.get("status") == "pending"]
        if not pending:
            return None
        return sorted(pending, key=lambda r: (-self._bounded(r.get("priority", 0.0)), r.get("created_at_utc", "")))[0]

    def _transition_queue_record(
        self,
        query_id: str,
        new_status: str,
        reason: str,
        response: str | None = None,
        answer_relevance_score: float | None = None,
    ) -> dict[str, Any]:
        records, index, record = self._find_query(query_id)
        if index is None or record is None:
            return {
                "primitive": PRIMITIVE,
                "success": False,
                "query_id": query_id,
                "error": "query_not_found",
            }

        old_status = str(record.get("status", "pending"))
        allowed = {
            "pending": {"sent", "rejected"},
            "sent": {"answered", "rejected"},
            "answered": {"integrated", "rejected"},
            "integrated": set(),
            "rejected": set(),
        }
        if new_status not in allowed.get(old_status, set()):
            return {
                "primitive": PRIMITIVE,
                "success": False,
                "query_id": query_id,
                "error": "invalid_transition",
                "from": old_status,
                "to": new_status,
            }

        now = self._utc_now()
        record["status"] = new_status
        record["updated_at_utc"] = now
        record.setdefault("transition_history", []).append({
            "from": old_status,
            "to": new_status,
            "timestamp_utc": now,
            "reason": reason,
        })
        if response is not None:
            record["response"] = str(response)
        if answer_relevance_score is not None:
            record["answer_relevance_score"] = self._bounded(answer_relevance_score)

        records[index] = record
        self._write_jsonl(self.queue_file, records)

        self._append_jsonl(self.collaboration_history_file, {
            "primitive": "interaction_queue_manager",
            "event_type": "query_transitioned",
            "timestamp_utc": self._utc_now(),
            "query_id": query_id,
            "from": old_status,
            "to": new_status,
            "reason": reason,
            "via": PRIMITIVE,
        })

        return {
            "primitive": PRIMITIVE,
            "success": True,
            "query_id": query_id,
            "from": old_status,
            "to": new_status,
            "status": new_status,
        }

    def gateway_status(self) -> dict[str, Any]:
        records = self._read_jsonl(self.queue_file)
        pending = sum(1 for r in records if r.get("status") == "pending")
        sent = sum(1 for r in records if r.get("status") == "sent")
        answered = sum(1 for r in records if r.get("status") == "answered")
        events = self._read_jsonl(self.gateway_history_file)
        return {
            "primitive": PRIMITIVE,
            "gateway_ready": True,
            "external_provider": self.provider,
            "manual_submission_required": True,
            "response_capture_ready": True,
            "pending_queries": pending,
            "sent_queries": sent,
            "answered_queries": answered,
            "gateway_event_count": len([e for e in events if e.get("primitive") == PRIMITIVE]),
            "queue_file": str(self.queue_file),
            "gateway_history_file": str(self.gateway_history_file),
            "supported_providers": SUPPORTED_PROVIDERS,
            "safety_mode": "manual_controlled_no_credentials",
        }

    def prepare_send_package(self, query_id: str | None = None, provider: str | None = None) -> dict[str, Any]:
        provider = provider if provider in SUPPORTED_PROVIDERS else self.provider
        record = None
        if query_id:
            _, _, record = self._find_query(query_id)
        else:
            record = self._next_pending_query()

        if not record:
            result = {
                "primitive": PRIMITIVE,
                "success": False,
                "error": "no_pending_query_found",
                "gateway_ready": True,
            }
            self._record_gateway_event("send_package_failed", result)
            return result

        if record.get("status") != "pending":
            result = {
                "primitive": PRIMITIVE,
                "success": False,
                "query_id": record.get("query_id"),
                "error": "query_not_pending",
                "status": record.get("status"),
            }
            self._record_gateway_event("send_package_failed", result)
            return result

        send_package = {
            "query_id": record.get("query_id"),
            "external_provider": provider,
            "manual_submission_required": True,
            "submission_instructions": [
                "Copy external_prompt to the selected external assistant.",
                "Do not share credentials with OCE.",
                "Paste the external answer back through capture_response().",
                "Preserve identity, governance, historicity and non-closure constraints.",
            ],
            "external_prompt": record.get("prompt", ""),
            "objective": record.get("objective", ""),
            "context": record.get("context", ""),
            "constraints": record.get("constraints", []),
            "priority": record.get("priority", 0.5),
            "created_at_utc": record.get("created_at_utc"),
        }

        result = {
            "primitive": PRIMITIVE,
            "success": True,
            "gateway_ready": True,
            "response_capture_ready": True,
            "external_provider": provider,
            "manual_submission_required": True,
            "query_id": record.get("query_id"),
            "send_package": send_package,
        }
        self._record_gateway_event("send_package_prepared", {
            "query_id": record.get("query_id"),
            "external_provider": provider,
        })
        return result

    def mark_sent(self, query_id: str, provider: str | None = None) -> dict[str, Any]:
        provider = provider if provider in SUPPORTED_PROVIDERS else self.provider
        result = self._transition_queue_record(
            query_id=query_id,
            new_status="sent",
            reason=f"external_prompt_submitted_manually_to_{provider}",
        )
        self._record_gateway_event("query_marked_sent", {
            "query_id": query_id,
            "external_provider": provider,
            "success": result.get("success", False),
        })
        result["external_provider"] = provider
        return result

    def capture_response(
        self,
        query_id: str,
        response: str,
        provider: str | None = None,
        answer_relevance_score: float = 0.0,
    ) -> dict[str, Any]:
        provider = provider if provider in SUPPORTED_PROVIDERS else self.provider
        response = str(response or "").strip()
        if not response:
            result = {
                "primitive": PRIMITIVE,
                "success": False,
                "query_id": query_id,
                "error": "empty_response",
            }
            self._record_gateway_event("response_capture_failed", result)
            return result

        result = self._transition_queue_record(
            query_id=query_id,
            new_status="answered",
            reason=f"external_response_captured_from_{provider}",
            response=response,
            answer_relevance_score=answer_relevance_score,
        )

        self._record_gateway_event("response_captured", {
            "query_id": query_id,
            "external_provider": provider,
            "success": result.get("success", False),
            "response_length": len(response),
            "answer_relevance_score": self._bounded(answer_relevance_score),
        })
        result["external_provider"] = provider
        result["response_capture_ready"] = True
        return result

    def step(self, action: str = "status", **kwargs: Any) -> dict[str, Any]:
        if action == "prepare_send_package":
            return self.prepare_send_package(
                query_id=kwargs.get("query_id"),
                provider=kwargs.get("provider"),
            )
        if action == "mark_sent":
            return self.mark_sent(
                query_id=str(kwargs.get("query_id", "")),
                provider=kwargs.get("provider"),
            )
        if action == "capture_response":
            return self.capture_response(
                query_id=str(kwargs.get("query_id", "")),
                response=str(kwargs.get("response", "")),
                provider=kwargs.get("provider"),
                answer_relevance_score=kwargs.get("answer_relevance_score", 0.0),
            )
        return self.gateway_status()


if __name__ == "__main__":
    print(json.dumps(ExternalCollaborationGateway().step(), ensure_ascii=False, indent=2))
