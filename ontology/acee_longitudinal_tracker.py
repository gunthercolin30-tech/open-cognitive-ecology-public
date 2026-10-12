"""ACEE16 — canonical longitudinal tracker for ACEE cycles.

Consumes authoritative outputs from ACEE4/7/8/9/10/11/15 and records a
single append-only longitudinal representation. It never executes, validates,
selects, rolls back, schedules, mutates lineages, or archives architectures.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_LONGITUDINAL_TRACKER"
STATUS_READY = "ACEE_LONGITUDINAL_TRACKING_READY"
STATUS_DEGRADED = "ACEE_LONGITUDINAL_TRACKING_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
ALLOWED_OPERATIONS = {
    "record_cycle", "inspect_cycle", "list_cycles",
    "list_trajectory", "summarize_trajectory", "verify_history",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _mapping(value: Any) -> Dict[str, Any]:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _finite(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _clean(value: Any) -> str:
    raw = str(value or "").strip()
    return "".join(ch if ch.isalnum() or ch in "_-." else "_" for ch in raw)


class AceeLongitudinalTracker:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (Path(root) if root is not None else Path.home() / "open-cognitive-ecology").expanduser().resolve()

    def _paths(self) -> Tuple[Path, Path, Path, Path]:
        runtime = self.root / "acee_runtime" / "ACEE16_acee_longitudinal_tracker"
        return runtime / "cycle_index.json", runtime / "cycle_history.jsonl", runtime / "latest_cycle.json", runtime / ".tracker.lock"

    def _empty(self) -> Dict[str, Any]:
        return {"schema_version": PUBLIC_SCHEMA_VERSION, "cycles": {}, "processed_transactions": {}}

    def _load(self, path: Path) -> Tuple[Dict[str, Any], bool]:
        if not path.is_file():
            return self._empty(), False
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or not isinstance(payload.get("cycles"), dict):
                return self._empty(), True
            payload.setdefault("processed_transactions", {})
            return payload, False
        except (OSError, json.JSONDecodeError, TypeError):
            return self._empty(), True

    def _history(self, path: Path) -> Tuple[List[Dict[str, Any]], bool]:
        if not path.is_file():
            return [], False
        records: List[Dict[str, Any]] = []
        previous = None
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                expected = _sha({k: v for k, v in record.items() if k != "record_hash"})
                if record.get("previous_record_hash") != previous or record.get("record_hash") != expected:
                    return records, True
                previous = record["record_hash"]
                records.append(record)
            return records, False
        except (OSError, json.JSONDecodeError, TypeError):
            return records, True

    def _base(self, operation: str, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "status": STATUS_READY,
            "longitudinal_tracking_ready": True,
            "operation": operation,
            "timestamp_utc": str(inputs.get("timestamp_utc") or _now()),
            "cycle_id": _clean(inputs.get("cycle_id")) or None,
            "transaction_id": _clean(inputs.get("transaction_id")) or None,
            "cycle_executed_by_tracker": False,
            "validation_executed_by_tracker": False,
            "impact_recomputed_by_tracker": False,
            "causality_recomputed_by_tracker": False,
            "selection_executed_by_tracker": False,
            "rollback_executed_by_tracker": False,
            "scheduling_modified_by_tracker": False,
            "lineage_modified_by_tracker": False,
            "archive_modified_by_tracker": False,
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

    def _record(self, inputs: Mapping[str, Any], previous_hash: Optional[str]) -> Tuple[Dict[str, Any], List[str]]:
        blocking: List[str] = []
        cycle_id = _clean(inputs.get("cycle_id"))
        if not cycle_id:
            blocking.append("cycle_id_missing")

        cycle = _mapping(inputs.get("cycle_result"))
        validation = _mapping(inputs.get("validation_result"))
        impact = _mapping(inputs.get("impact_evaluation"))
        causal = _mapping(inputs.get("causal_analysis"))
        selection = _mapping(inputs.get("selection_decision"))
        rollback = _mapping(inputs.get("rollback_result"))
        scheduling = _mapping(inputs.get("scheduling_event"))
        lineage = _mapping(inputs.get("lineage_state"))
        archive = _mapping(inputs.get("archive_state"))

        before = _finite(inputs.get("before_score", impact.get("before_score")))
        after = _finite(inputs.get("after_score", impact.get("after_score")))
        if before is None:
            before = _finite(impact.get("baseline_score"))
        if after is None:
            after = _finite(impact.get("candidate_score"))
        if before is not None and after is not None:
            delta = round(after - before, 12)
        else:
            delta = _finite(inputs.get("score_delta", impact.get("impact_score")))
        for name, value in (("before_score", before), ("after_score", after), ("score_delta", delta)):
            raw_present = name in inputs or name in impact
            if raw_present and value is None:
                blocking.append(f"{name}_invalid")

        decision = str(selection.get("decision") or cycle.get("selection_decision") or inputs.get("decision") or "undetermined")
        # ACEE4.rollback_completed means the combined rollback-or-acceptance
        # phase completed. It is not evidence that ACEE11 executed a rollback.
        rollback_phase_completed = cycle.get("rollback_completed") is True
        rollback_performed = rollback.get("rollback_performed") is True
        validation_status = str(validation.get("validation_status") or ("passed" if validation.get("validation_passed") is True else "failed" if validation.get("validation_passed") is False else "undetermined"))
        source_payloads = {
            "cycle_result": cycle, "validation_result": validation,
            "impact_evaluation": impact, "causal_analysis": causal,
            "selection_decision": selection, "rollback_result": rollback,
            "scheduling_event": scheduling, "lineage_state": lineage,
            "archive_state": archive,
        }
        record = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "record_id": _clean(inputs.get("record_id")) or _sha({"cycle_id": cycle_id, "timestamp": inputs.get("timestamp_utc") or _now()})[:24],
            "timestamp_utc": str(inputs.get("timestamp_utc") or _now()),
            "cycle_id": cycle_id,
            "scheduler_cycle_id": scheduling.get("cycle_id") or None,
            "intervention": deepcopy(inputs.get("intervention", cycle.get("intervention"))),
            "before_score": before,
            "after_score": after,
            "score_delta": delta,
            "validation_status": validation_status,
            "causal_status": str(causal.get("status") or ("resolved" if causal.get("causal_effect_resolved") is True else "undetermined")),
            "decision": decision,
            "decision_reasons": list(selection.get("decision_reasons") or []),
            "rollback_status": str(rollback.get("rollback_status") or ("rolled_back" if rollback_performed else "not_rolled_back")),
            "rollback_phase_completed": rollback_phase_completed,
            "rollback_performed": rollback_performed,
            "cycle_status": str(cycle.get("cycle_status") or cycle.get("status") or "undetermined"),
            "cycle_outcome": str(cycle.get("cycle_outcome") or "undetermined"),
            "lineage_id": lineage.get("lineage_id"),
            "generation_id": lineage.get("generation_id"),
            "archive_id": archive.get("archive_id"),
            "source_hashes": {name: _sha(payload) for name, payload in source_payloads.items() if payload},
            "previous_record_hash": previous_hash,
            "source_payloads_preserved": True,
        }
        record["record_hash"] = _sha(record)
        return record, blocking

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        operation = str(supplied.get("operation") or "list_cycles")
        result = self._base(operation, supplied)
        blocking: List[str] = []
        if operation not in ALLOWED_OPERATIONS:
            blocking.append("operation_not_allowed")

        index_path, history_path, latest_path, lock_path = self._paths()
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+", encoding="utf-8") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            state, state_corrupted = self._load(index_path)
            records, history_corrupted = self._history(history_path)
            if state_corrupted:
                blocking.append("cycle_index_corrupted")
            if history_corrupted:
                blocking.append("cycle_history_corrupted")

            transaction_id = result["transaction_id"]
            if transaction_id and transaction_id in state["processed_transactions"]:
                cached = deepcopy(state["processed_transactions"][transaction_id])
                cached["idempotent_replay"] = True
                return cached

            if operation == "record_cycle":
                previous_hash = records[-1]["record_hash"] if records else None
                record, record_blocking = self._record(supplied, previous_hash)
                blocking.extend(record_blocking)
                cycle_id = record["cycle_id"]
                if cycle_id and cycle_id in state["cycles"]:
                    blocking.append("cycle_id_already_recorded")
                if not blocking:
                    state["cycles"][cycle_id] = record
                    result.update(record)
                    result["record_created"] = True
            elif operation == "inspect_cycle":
                cycle_id = result["cycle_id"]
                result["cycle_record"] = deepcopy(state["cycles"].get(cycle_id)) if cycle_id else None
                if cycle_id and result["cycle_record"] is None:
                    blocking.append("cycle_not_found")
            elif operation in {"list_cycles", "list_trajectory"}:
                ordered = sorted(state["cycles"].values(), key=lambda item: (item.get("timestamp_utc", ""), item.get("cycle_id", "")))
                result["cycles"] = deepcopy(ordered)
                result["cycle_count"] = len(ordered)
            elif operation == "summarize_trajectory":
                ordered = sorted(state["cycles"].values(), key=lambda item: (item.get("timestamp_utc", ""), item.get("cycle_id", "")))
                deltas = [item["score_delta"] for item in ordered if item.get("score_delta") is not None]
                result["trajectory_summary"] = {
                    "cycle_count": len(ordered),
                    "accepted_count": sum(str(item.get("decision")).lower() == "accept" for item in ordered),
                    "rollback_phase_completed_count": sum(
                        item.get("rollback_phase_completed") is True
                        for item in ordered
                    ),
                    "rollback_count": sum(item.get("rollback_performed") is True for item in ordered),
                    "mean_score_delta": round(sum(deltas) / len(deltas), 12) if deltas else None,
                    "latest_cycle_id": ordered[-1]["cycle_id"] if ordered else None,
                }
            elif operation == "verify_history":
                result["history_valid"] = not history_corrupted
                result["verified_record_count"] = len(records)

            result["blocking_reasons"] = sorted(set(blocking))
            result["history_corrupted"] = history_corrupted
            result["state_corrupted"] = state_corrupted
            result["persisted"] = False
            result["record_created"] = result.get("record_created", False)
            result["index_path"] = str(index_path)
            result["history_path"] = str(history_path)
            result["latest_path"] = str(latest_path)
            if blocking:
                result["status"] = STATUS_DEGRADED
                result["longitudinal_tracking_ready"] = False
                return result

            if persist and operation == "record_cycle":
                latest_path.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")
                with history_path.open("a", encoding="utf-8") as stream:
                    stream.write(_canonical({k: v for k, v in result.items() if k not in {"persisted", "index_path", "history_path", "latest_path", "blocking_reasons", "status", "longitudinal_tracking_ready", "transaction_id", "operation", "record_created", "history_corrupted", "state_corrupted", "cycle_executed_by_tracker", "validation_executed_by_tracker", "impact_recomputed_by_tracker", "causality_recomputed_by_tracker", "selection_executed_by_tracker", "rollback_executed_by_tracker", "scheduling_modified_by_tracker", "lineage_modified_by_tracker", "archive_modified_by_tracker", "functional_conclusion_only", "phenomenology_undetermined", "consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven", "collective_consciousness_proven", "collective_subjectivity_proven", "collective_qualia_proven", "collective_phenomenology_proven"}}) + "\n")
                result["persisted"] = True
                if transaction_id:
                    state["processed_transactions"][transaction_id] = deepcopy(result)
                index_path.write_text(json.dumps(state, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")
            return result
