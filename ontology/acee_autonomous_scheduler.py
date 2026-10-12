"""ACEE15 — governed autonomous scheduling facade for ACEE cycles.

Plans and dispatches cycle orders without executing ACEE4 or any runtime.
Reuses existing scheduler policies conceptually while preserving non-closure,
governance, persistence, restart continuity, and transaction idempotence.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_AUTONOMOUS_SCHEDULER"
STATUS_READY = "ACEE_AUTONOMOUS_SCHEDULER_READY"
STATUS_DEGRADED = "ACEE_AUTONOMOUS_SCHEDULER_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
ALLOWED_OPERATIONS = {
    "schedule_cycle", "reschedule_cycle", "cancel_cycle",
    "suspend_scheduler", "resume_scheduler", "dispatch_due_cycles",
    "inspect_schedule", "list_pending_cycles",
}
SCHEDULER_REGISTRY = {
    "asynchronous_pluralistic_scheduler": {
        "temporal_policy": "asynchronous", "coordination_mode": "distributed"
    },
    "fragmented_resilience_scheduler": {
        "temporal_policy": "fragmented", "coordination_mode": "partitioned"
    },
    "historical_divergence_scheduler": {
        "temporal_policy": "multi_history", "coordination_mode": "branching"
    },
    "autonomous_runtime_scheduler": {
        "temporal_policy": "autonomous", "coordination_mode": "local_runtime"
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _finite(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _clean_id(value: Any) -> str:
    raw = str(value or "").strip()
    return "".join(ch if ch.isalnum() or ch in "_-." else "_" for ch in raw)


def _parse_utc(value: Any) -> Optional[datetime]:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class AceeAutonomousScheduler:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (Path(root) if root is not None else Path.home() / "open-cognitive-ecology").expanduser().resolve()

    def _paths(self) -> Tuple[Path, Path, Path, Path]:
        runtime = self.root / "acee_runtime" / "ACEE15_acee_autonomous_scheduler"
        return runtime / "schedule_state.json", runtime / "schedule_history.jsonl", runtime / "latest_dispatch.json", runtime / ".scheduler.lock"

    def _empty(self) -> Dict[str, Any]:
        return {"schema_version": PUBLIC_SCHEMA_VERSION, "suspended": False, "cycles": {}, "processed_transactions": {}}

    def _load(self, path: Path) -> Tuple[Dict[str, Any], bool]:
        if not path.is_file():
            return self._empty(), False
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or not isinstance(payload.get("cycles"), dict):
                return self._empty(), True
            payload.setdefault("processed_transactions", {})
            payload.setdefault("suspended", False)
            return payload, False
        except (OSError, json.JSONDecodeError, TypeError):
            return self._empty(), True

    def _history(self, path: Path) -> Tuple[List[Dict[str, Any]], bool]:
        if not path.is_file():
            return [], False
        records: List[Dict[str, Any]] = []
        try:
            previous = None
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                expected = _sha({k: v for k, v in record.items() if k != "event_hash"})
                if record.get("previous_event_hash") != previous or record.get("event_hash") != expected:
                    return records, True
                previous = record["event_hash"]
                records.append(record)
            return records, False
        except (OSError, json.JSONDecodeError, TypeError):
            return records, True

    def _select_scheduler(self, context: Mapping[str, Any]) -> Tuple[str, Dict[str, Any]]:
        fragmentation = _finite(context.get("fragmentation_pressure")) or 0.0
        divergence = _finite(context.get("historical_divergence")) or 0.0
        autonomy = _finite(context.get("autonomy_pressure")) or 0.0
        if fragmentation >= 0.75:
            selected = "fragmented_resilience_scheduler"
        elif divergence >= 0.70:
            selected = "historical_divergence_scheduler"
        elif autonomy >= 0.70:
            selected = "autonomous_runtime_scheduler"
        else:
            selected = "asynchronous_pluralistic_scheduler"
        return selected, dict(SCHEDULER_REGISTRY[selected])

    def _base(self, inputs: Mapping[str, Any], operation: str) -> Dict[str, Any]:
        return {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "status": STATUS_READY,
            "autonomous_scheduler_ready": True,
            "operation": operation,
            "timestamp_utc": str(inputs.get("timestamp_utc") or _now()),
            "cycle_id": _clean_id(inputs.get("cycle_id")) or None,
            "transaction_id": _clean_id(inputs.get("transaction_id")) or None,
            "cycle_dispatched": False,
            "cycle_executed_by_scheduler": False,
            "acee4_executed_by_scheduler": False,
            "validation_main_executed": False,
            "rollback_executed": False,
            "selection_executed": False,
            "lineage_modified": False,
            "archive_modified": False,
            "network_operation_executed": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
        }

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        operation = str(supplied.get("operation") or "inspect_schedule")
        result = self._base(supplied, operation)
        blocking: List[str] = []
        if operation not in ALLOWED_OPERATIONS:
            blocking.append("operation_not_allowed")

        state_path, history_path, dispatch_path, lock_path = self._paths()
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+", encoding="utf-8") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            state, state_corrupted = self._load(state_path)
            records, history_corrupted = self._history(history_path)
            if state_corrupted:
                blocking.append("schedule_state_corrupted")
            if history_corrupted:
                blocking.append("schedule_history_corrupted")

            transaction_id = result["transaction_id"]
            if transaction_id and transaction_id in state["processed_transactions"]:
                cached = dict(state["processed_transactions"][transaction_id])
                cached["idempotent_replay"] = True
                return cached

            now_dt = _parse_utc(supplied.get("now_utc") or supplied.get("timestamp_utc") or _now())
            if now_dt is None:
                blocking.append("timestamp_invalid")
                now_dt = datetime.now(timezone.utc)

            cycles = state["cycles"]
            cycle_id = result["cycle_id"]
            selected, scheduler_config = self._select_scheduler(_mapping(supplied.get("scheduler_context")))
            result["selected_scheduler"] = selected
            result["scheduler_configuration"] = scheduler_config
            result["scheduler_suspended"] = bool(state.get("suspended"))

            if operation in {"schedule_cycle", "reschedule_cycle"}:
                if not cycle_id:
                    blocking.append("cycle_id_missing")
                due = _parse_utc(supplied.get("due_at_utc"))
                if due is None:
                    blocking.append("due_at_utc_invalid")
                priority = _finite(supplied.get("priority", 0.5))
                if priority is None or not 0.0 <= priority <= 1.0:
                    blocking.append("priority_invalid")
                governance = _mapping(supplied.get("governance_authorization"))
                constitutional = _mapping(supplied.get("constitutional_authorization"))
                if governance.get("approved") is not True:
                    blocking.append("governance_not_approved")
                if constitutional.get("approved") is not True:
                    blocking.append("constitutional_not_approved")
                if operation == "schedule_cycle" and cycle_id in cycles:
                    blocking.append("cycle_id_already_exists")
                if operation == "reschedule_cycle" and cycle_id not in cycles:
                    blocking.append("cycle_not_found")
                if not blocking:
                    existing = dict(cycles.get(cycle_id, {}))
                    cycle = {
                        **existing,
                        "cycle_id": cycle_id,
                        "due_at_utc": due.isoformat().replace("+00:00", "Z"),
                        "priority": round(float(priority), 6),
                        "status": "pending",
                        "selected_scheduler": selected,
                        "scheduler_configuration": scheduler_config,
                        "cycle_request": _mapping(supplied.get("cycle_request")),
                        "created_at_utc": existing.get("created_at_utc") or result["timestamp_utc"],
                        "updated_at_utc": result["timestamp_utc"],
                    }
                    cycles[cycle_id] = cycle
                    result["scheduled_cycle"] = cycle
                    result["schedule_updated"] = True

            elif operation == "cancel_cycle":
                if not cycle_id or cycle_id not in cycles:
                    blocking.append("cycle_not_found")
                elif cycles[cycle_id].get("status") == "dispatched":
                    blocking.append("cycle_already_dispatched")
                else:
                    cycles[cycle_id]["status"] = "cancelled"
                    cycles[cycle_id]["updated_at_utc"] = result["timestamp_utc"]
                    result["schedule_updated"] = True

            elif operation == "suspend_scheduler":
                state["suspended"] = True
                result["scheduler_suspended"] = True
                result["schedule_updated"] = True

            elif operation == "resume_scheduler":
                state["suspended"] = False
                result["scheduler_suspended"] = False
                result["schedule_updated"] = True

            elif operation == "dispatch_due_cycles":
                if state.get("suspended"):
                    blocking.append("scheduler_suspended")
                max_dispatch = supplied.get("max_dispatch", 1)
                try:
                    max_dispatch = max(1, int(max_dispatch))
                except (TypeError, ValueError):
                    max_dispatch = 1
                due_cycles = []
                for item in cycles.values():
                    due_dt = _parse_utc(item.get("due_at_utc"))
                    if item.get("status") == "pending" and due_dt is not None and due_dt <= now_dt:
                        due_cycles.append(item)
                due_cycles.sort(key=lambda item: (-float(item.get("priority", 0.0)), item.get("due_at_utc", ""), item.get("cycle_id", "")))
                dispatches = []
                if not blocking:
                    for item in due_cycles[:max_dispatch]:
                        order = {
                            "dispatch_id": _sha({"cycle_id": item["cycle_id"], "timestamp": result["timestamp_utc"]})[:24],
                            "cycle_id": item["cycle_id"],
                            "requested_phases": item.get("cycle_request", {}).get("requested_phases", []),
                            "cycle_inputs": item.get("cycle_request", {}),
                            "target_primitive": "acee_autonomous_cycle_manager",
                            "target_step": "step",
                            "execution_authorized": False,
                            "scheduler_policy": item.get("selected_scheduler"),
                        }
                        item["status"] = "dispatched"
                        item["dispatched_at_utc"] = result["timestamp_utc"]
                        item["dispatch_order"] = order
                        dispatches.append(order)
                    result["dispatch_orders"] = dispatches
                    result["cycle_dispatched"] = bool(dispatches)
                    result["dispatch_count"] = len(dispatches)
                    result["cycle_dispatch_ready"] = bool(dispatches)
                    result["schedule_updated"] = bool(dispatches)

            elif operation == "inspect_schedule":
                result["schedule"] = dict(cycles)
                result["cycle"] = dict(cycles.get(cycle_id, {})) if cycle_id else None

            elif operation == "list_pending_cycles":
                pending = [dict(item) for item in cycles.values() if item.get("status") == "pending"]
                pending.sort(key=lambda item: (-float(item.get("priority", 0.0)), item.get("due_at_utc", ""), item.get("cycle_id", "")))
                result["pending_cycles"] = pending
                result["pending_count"] = len(pending)

            result["blocking_reasons"] = sorted(set(blocking))
            result["schedule_state_corrupted"] = state_corrupted
            result["schedule_history_corrupted"] = history_corrupted
            result["persisted"] = False
            result["operation_applied"] = not blocking and operation not in {"inspect_schedule", "list_pending_cycles"}
            if blocking:
                result["status"] = STATUS_DEGRADED
                result["autonomous_scheduler_ready"] = False

            if persist and not blocking and operation not in {"inspect_schedule", "list_pending_cycles"}:
                previous_hash = records[-1]["event_hash"] if records else None
                event = {k: v for k, v in result.items() if k not in {"persisted", "event_hash"}}
                event["previous_event_hash"] = previous_hash
                event["event_hash"] = _sha(event)
                result["previous_event_hash"] = previous_hash
                result["event_hash"] = event["event_hash"]
                result["persisted"] = True
                state["processed_transactions"][transaction_id or event["event_hash"]] = dict(result)
                temp = state_path.with_suffix(".json.tmp")
                temp.write_text(json.dumps(state, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")
                temp.replace(state_path)
                with history_path.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")
                if result.get("cycle_dispatched"):
                    dispatch_path.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")

            result["schedule_path"] = str(state_path)
            result["history_path"] = str(history_path)
            return result
