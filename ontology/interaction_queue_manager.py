from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Any


PRIMITIVE = "interaction_queue_manager"

DEPENDENCIES = [
    "conversation_memory_archive",
    "civilizational_memory_archive",
    "dialogue_memory_persistence",
    "metrics_history_recorder",
    "autonomous_society_scheduler",
    "continuous_civilizational_scheduler",
]

VALID_STATUSES = {"pending", "sent", "answered", "integrated", "rejected"}


class InteractionQueueManager:
    """
    O6 — Interaction Queue Manager.

    Manages the lifecycle of autonomous external collaboration requests:
    pending -> sent -> answered -> integrated / rejected.

    This primitive deliberately does not call ChatGPT or any external service.
    It provides a governed, reversible, traceable queue compatible with
    human-mediated submission and future external gateways.
    """

    def __init__(
        self,
        root: Path | None = None,
        queue_file: Path | None = None,
        history_file: Path | None = None,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.queue_file = Path(queue_file) if queue_file is not None else self.root / "external_query_queue.jsonl"
        self.history_file = Path(history_file) if history_file is not None else self.root / "collaboration_history.jsonl"
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

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
        records: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
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
                        "line_number": line_number,
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

    def _next_query_id(self, records: list[dict[str, Any]]) -> str:
        highest = 0
        for record in records:
            query_id = str(record.get("query_id", ""))
            if query_id.startswith("EXTQ-"):
                try:
                    highest = max(highest, int(query_id.rsplit("-", 1)[-1]))
                except Exception:
                    pass
        return f"EXTQ-{highest + 1:06d}"

    def _find_record(
        self,
        records: list[dict[str, Any]],
        query_id: str,
    ) -> tuple[int | None, dict[str, Any] | None]:
        for index, record in enumerate(records):
            if record.get("query_id") == query_id:
                return index, record
        return None, None

    def _valid_transition(self, old_status: str, new_status: str) -> bool:
        allowed = {
            "pending": {"sent", "rejected"},
            "sent": {"answered", "rejected"},
            "answered": {"integrated", "rejected"},
            "integrated": set(),
            "rejected": set(),
        }
        return new_status in allowed.get(old_status, set())

    def _history(self, event_type: str, payload: dict[str, Any]) -> None:
        self._append_jsonl(self.history_file, {
            "primitive": PRIMITIVE,
            "event_type": event_type,
            "timestamp_utc": self._utc_now(),
            **payload,
        })

    def _prompt_quality(
        self,
        prompt: str,
        objective: str,
        context: str,
        constraints: list[str],
    ) -> float:
        length_score = min(len(prompt.strip()) / 400.0, 1.0)
        return self._bounded(
            0.35 * length_score
            + 0.25 * bool(objective.strip())
            + 0.20 * bool(context.strip())
            + 0.20 * bool(constraints)
        )

    def enqueue(
        self,
        prompt: str,
        objective: str = "",
        context: str = "",
        constraints: list[str] | None = None,
        source: str = "autonomous_prompt_generator",
        priority: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        records = self._read_jsonl(self.queue_file)
        constraints = list(constraints or [])
        now = self._utc_now()
        query_id = self._next_query_id(records)

        record = {
            "query_id": query_id,
            "primitive": PRIMITIVE,
            "status": "pending",
            "created_at_utc": now,
            "updated_at_utc": now,
            "source": str(source or "unknown"),
            "priority": self._bounded(priority),
            "objective": str(objective or ""),
            "context": str(context or ""),
            "constraints": constraints,
            "prompt": str(prompt or ""),
            "response": "",
            "answer_relevance_score": 0.0,
            "prompt_quality_score": self._prompt_quality(
                str(prompt or ""),
                str(objective or ""),
                str(context or ""),
                constraints,
            ),
            "integration_decision": None,
            "rejection_reason": "",
            "metadata": dict(metadata or {}),
            "transition_history": [
                {
                    "from": None,
                    "to": "pending",
                    "reason": "created",
                    "timestamp_utc": now,
                }
            ],
        }

        records.append(record)
        self._write_jsonl(self.queue_file, records)
        self._history("query_enqueued", {"query_id": query_id, "status": "pending"})
        return record

    def transition(
        self,
        query_id: str,
        new_status: str,
        reason: str = "",
        response: str | None = None,
        answer_relevance_score: float | None = None,
        integration_decision: str | None = None,
    ) -> dict[str, Any]:
        new_status = str(new_status or "").strip()

        if new_status not in VALID_STATUSES:
            return {
                "primitive": PRIMITIVE,
                "success": False,
                "query_id": query_id,
                "error": "invalid_status",
                "valid_statuses": sorted(VALID_STATUSES),
            }

        records = self._read_jsonl(self.queue_file)
        index, record = self._find_record(records, query_id)

        if index is None or record is None:
            return {
                "primitive": PRIMITIVE,
                "success": False,
                "query_id": query_id,
                "error": "query_not_found",
            }

        old_status = str(record.get("status", "pending"))
        if old_status == new_status:
            return {
                "primitive": PRIMITIVE,
                "success": True,
                "query_id": query_id,
                "status": old_status,
                "unchanged": True,
            }

        if not self._valid_transition(old_status, new_status):
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

        if response is not None:
            record["response"] = str(response)
        if answer_relevance_score is not None:
            record["answer_relevance_score"] = self._bounded(answer_relevance_score)
        if integration_decision is not None:
            record["integration_decision"] = str(integration_decision)
        if new_status == "rejected":
            record["rejection_reason"] = str(reason or "rejected_without_reason")
        if new_status == "integrated":
            record["integration_decision"] = "integrated"

        record.setdefault("transition_history", []).append({
            "from": old_status,
            "to": new_status,
            "reason": str(reason or ""),
            "timestamp_utc": now,
        })

        records[index] = record
        self._write_jsonl(self.queue_file, records)
        self._history("query_transitioned", {
            "query_id": query_id,
            "from": old_status,
            "to": new_status,
            "reason": str(reason or ""),
        })

        return {
            "primitive": PRIMITIVE,
            "success": True,
            "query_id": query_id,
            "from": old_status,
            "to": new_status,
            "status": new_status,
        }

    def mark_sent(self, query_id: str) -> dict[str, Any]:
        return self.transition(query_id, "sent", reason="submitted_to_external_assistant")

    def record_answer(
        self,
        query_id: str,
        response: str,
        answer_relevance_score: float = 0.0,
    ) -> dict[str, Any]:
        return self.transition(
            query_id,
            "answered",
            reason="external_answer_received",
            response=response,
            answer_relevance_score=answer_relevance_score,
        )

    def integrate(self, query_id: str, reason: str = "validated_for_integration") -> dict[str, Any]:
        return self.transition(query_id, "integrated", reason=reason, integration_decision="integrated")

    def reject(self, query_id: str, reason: str = "rejected_by_governance") -> dict[str, Any]:
        return self.transition(query_id, "rejected", reason=reason, integration_decision="rejected")

    def summarize(self) -> dict[str, Any]:
        records = [r for r in self._read_jsonl(self.queue_file) if r.get("query_id")]
        counts = {status: 0 for status in sorted(VALID_STATUSES)}

        for record in records:
            status = str(record.get("status", "pending"))
            if status in counts:
                counts[status] += 1

        total = len(records)
        terminal = counts["integrated"] + counts["rejected"]
        answered_or_terminal = counts["answered"] + terminal

        mean_prompt_quality = (
            sum(self._bounded(r.get("prompt_quality_score", 0.0)) for r in records) / total
            if total else 0.0
        )
        mean_answer_relevance = (
            sum(self._bounded(r.get("answer_relevance_score", 0.0)) for r in records) / total
            if total else 0.0
        )

        return {
            "primitive": PRIMITIVE,
            "queue_file": str(self.queue_file),
            "history_file": str(self.history_file),
            "total_queries": total,
            "status_counts": counts,
            "pending_count": counts["pending"],
            "sent_count": counts["sent"],
            "answered_count": counts["answered"],
            "integrated_count": counts["integrated"],
            "rejected_count": counts["rejected"],
            "queue_completion_ratio": self._bounded(terminal / total) if total else 0.0,
            "answer_capture_ratio": self._bounded(answered_or_terminal / total) if total else 0.0,
            "integration_ratio": self._bounded(counts["integrated"] / total) if total else 0.0,
            "mean_prompt_quality_score": self._bounded(mean_prompt_quality),
            "mean_answer_relevance_score": self._bounded(mean_answer_relevance),
            "valid_statuses": sorted(VALID_STATUSES),
            "queue_operational": True,
        }

    def step(self, action: str = "summary", **kwargs: Any) -> dict[str, Any]:
        if action == "enqueue":
            record = self.enqueue(**kwargs)
            return {
                "primitive": PRIMITIVE,
                "success": True,
                "action": action,
                "query_id": record["query_id"],
                "record": record,
                "summary": self.summarize(),
            }

        if action == "mark_sent":
            result = self.mark_sent(str(kwargs.get("query_id", "")))
            result["summary"] = self.summarize()
            return result

        if action == "record_answer":
            result = self.record_answer(
                str(kwargs.get("query_id", "")),
                str(kwargs.get("response", "")),
                self._bounded(kwargs.get("answer_relevance_score", 0.0)),
            )
            result["summary"] = self.summarize()
            return result

        if action == "integrate":
            result = self.integrate(str(kwargs.get("query_id", "")))
            result["summary"] = self.summarize()
            return result

        if action == "reject":
            result = self.reject(
                str(kwargs.get("query_id", "")),
                str(kwargs.get("reason", "rejected_by_governance")),
            )
            result["summary"] = self.summarize()
            return result

        return self.summarize()


if __name__ == "__main__":
    print(json.dumps(InteractionQueueManager().step(), ensure_ascii=False, indent=2))
