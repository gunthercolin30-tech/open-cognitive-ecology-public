"""ACEE13 — active, governed management of architectural lineages.

ACEE13 applies authoritative ACEE10 decisions to lineage state, records actual
ACEE11 rollback outcomes, and emits descriptive events consumable by ACEE12.
It does not select, mutate code, execute rollback, or build genealogy graphs.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_LINEAGE_MANAGER"
STATUS_READY = "ACEE_LINEAGE_MANAGEMENT_READY"
STATUS_DEGRADED = "ACEE_LINEAGE_MANAGEMENT_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
ALLOWED_OPERATIONS = {"register_root", "register_candidate", "apply_selection", "record_rollback", "inspect"}
ALLOWED_DECISIONS = {"accept", "reject", "rollback", "repeat", "sandbox_longer"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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
    return "".join(ch if ch.isalnum() or ch in "_-. :" else "_" for ch in raw).replace(" ", "_")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


class AceeLineageManager:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (Path(root) if root is not None else Path.home() / "open-cognitive-ecology").expanduser().resolve()

    def _paths(self) -> Tuple[Path, Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE13_acee_lineage_manager"
        return (
            directory / "latest_lineage_state.json",
            directory / "lineage_event_history.jsonl",
            directory / "lineages.json",
            directory / ".lineage_manager.lock",
        )

    def _empty_state(self) -> Dict[str, Any]:
        return {"schema_version": PUBLIC_SCHEMA_VERSION, "lineages": {}, "processed_transactions": {}}

    def _load_state(self, path: Path) -> Tuple[Dict[str, Any], bool]:
        if not path.is_file():
            return self._empty_state(), False
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or not isinstance(payload.get("lineages"), dict):
                return self._empty_state(), True
            payload.setdefault("processed_transactions", {})
            return payload, False
        except (OSError, json.JSONDecodeError, TypeError):
            return self._empty_state(), True

    def _load_history(self, path: Path) -> Tuple[List[Dict[str, Any]], bool]:
        if not path.is_file():
            return [], False
        records: List[Dict[str, Any]] = []
        previous_hash = None
        corrupted = False
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                item = json.loads(line)
                if not isinstance(item, dict):
                    corrupted = True
                    continue
                expected = _sha({k: v for k, v in item.items() if k not in {"event_hash", "persisted", "state_path", "history_path", "lineages_path"}})
                if item.get("event_hash") != expected or item.get("previous_event_hash") != previous_hash:
                    corrupted = True
                previous_hash = item.get("event_hash")
                records.append(item)
        except (OSError, json.JSONDecodeError, TypeError):
            return records, True
        return records, corrupted

    def _lineage(self, state: Dict[str, Any], lineage_id: str) -> Dict[str, Any]:
        return _mapping(_mapping(state.get("lineages")).get(lineage_id))

    def _base_result(self, supplied: Mapping[str, Any], operation: str, previous_hash: Optional[str]) -> Dict[str, Any]:
        return {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": str(supplied.get("timestamp_utc") or _now()),
            "operation": operation,
            "lineage_id": _clean_id(supplied.get("lineage_id")) or None,
            "transaction_id": _clean_id(supplied.get("transaction_id")) or None,
            "previous_event_hash": previous_hash,
            "selection_executed_by_lineage_manager": False,
            "rollback_executed_by_lineage_manager": False,
            "mutation_executed_by_lineage_manager": False,
            "genealogy_written_by_lineage_manager": False,
            "best_architecture_archived": False,
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

    def _transition(self, inputs: Mapping[str, Any], state: Dict[str, Any], previous_hash: Optional[str], corrupted: bool) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        supplied = _mapping(inputs)
        operation = str(supplied.get("operation") or "inspect").strip().lower()
        result = self._base_result(supplied, operation, previous_hash)
        blocking: List[str] = []
        if operation not in ALLOWED_OPERATIONS:
            blocking.append("operation_invalid")
        if corrupted:
            blocking.append("persistence_corrupted")

        lineage_id = _clean_id(supplied.get("lineage_id"))
        transaction_id = _clean_id(supplied.get("transaction_id"))
        if operation != "inspect" and not lineage_id:
            blocking.append("lineage_id_required")
        if operation != "inspect" and not transaction_id:
            blocking.append("transaction_id_required")

        processed = _mapping(state.get("processed_transactions"))
        if transaction_id and transaction_id in processed:
            prior = _mapping(processed[transaction_id])
            prior = dict(prior)
            prior.update({"idempotent_replay": True, "persisted": False})
            return prior, state

        lineages = dict(_mapping(state.get("lineages")))
        lineage = dict(_mapping(lineages.get(lineage_id))) if lineage_id else {}
        generations = dict(_mapping(lineage.get("generations")))
        active_id = lineage.get("active_generation_id")
        event_type = "inspection"
        changed = False
        genealogy_event: Optional[Dict[str, Any]] = None

        generation_id_raw = supplied.get("generation_id")
        generation_number = _finite(generation_id_raw)
        generation_id = int(generation_number) if generation_number is not None and generation_number >= 0 and float(generation_number).is_integer() else None
        architecture_id = _clean_id(supplied.get("architecture_id")) or None
        parent_id = _clean_id(supplied.get("parent_id") or supplied.get("parent_architecture_id")) or None
        mutation_id = _clean_id(supplied.get("mutation_id")) or None
        fitness_delta = _finite(supplied.get("fitness_delta"))

        if operation == "register_root" and not blocking:
            if lineage:
                blocking.append("lineage_already_exists")
            if generation_id not in (None, 0):
                blocking.append("root_generation_must_be_zero")
            if parent_id is not None:
                blocking.append("root_parent_must_be_none")
            if not architecture_id:
                blocking.append("architecture_id_required")
            if not blocking:
                record = {"generation_id": 0, "architecture_id": architecture_id, "parent_id": None, "mutation_id": None, "selection_reason": "founding_generation", "rollback_status": "not_rolled_back", "fitness_delta": 0.0 if fitness_delta is None else fitness_delta, "status": "active"}
                lineage = {"lineage_id": lineage_id, "active_generation_id": 0, "generations": {"0": record}}
                lineages[lineage_id] = lineage
                generation_id = 0
                active_id = 0
                event_type = "root_registered"
                changed = True

        elif operation == "register_candidate" and not blocking:
            if not lineage:
                blocking.append("lineage_not_found")
            if generation_id is None:
                blocking.append("generation_id_required_or_invalid")
            if generation_id is not None and str(generation_id) in generations:
                blocking.append("generation_already_exists")
            if not architecture_id:
                blocking.append("architecture_id_required")
            if parent_id is None:
                blocking.append("parent_id_required")
            parent_record = next((g for g in generations.values() if str(g.get("architecture_id")) == parent_id or str(g.get("generation_id")) == str(parent_id)), None)
            if parent_id is not None and parent_record is None:
                blocking.append("parent_not_found")
            if parent_record is not None and generation_id is not None and generation_id <= int(parent_record.get("generation_id", -1)):
                blocking.append("generation_not_monotonic")
            if not mutation_id:
                blocking.append("mutation_id_required")
            if fitness_delta is None:
                blocking.append("finite_fitness_delta_required")
            if not blocking:
                record = {"generation_id": generation_id, "architecture_id": architecture_id, "parent_id": parent_record.get("architecture_id"), "mutation_id": mutation_id, "selection_reason": None, "rollback_status": "not_rolled_back", "fitness_delta": fitness_delta, "status": "candidate"}
                generations[str(generation_id)] = record
                lineage["generations"] = generations
                lineages[lineage_id] = lineage
                event_type = "candidate_registered"
                changed = True

        elif operation == "apply_selection" and not blocking:
            selection = _mapping(supplied.get("selection_decision"))
            if not lineage:
                blocking.append("lineage_not_found")
            if generation_id is None or str(generation_id) not in generations:
                blocking.append("generation_not_found")
            decision = str(selection.get("decision") or "").lower()
            if selection.get("selection_decision_ready") is not True:
                blocking.append("authoritative_selection_not_ready")
            if decision not in ALLOWED_DECISIONS:
                blocking.append("selection_decision_invalid")
            if not selection.get("selection_id"):
                blocking.append("selection_id_required")
            if not blocking:
                target = dict(generations[str(generation_id)])
                reason = ",".join(str(x) for x in selection.get("decision_reasons", []) if x) or decision
                target["selection_reason"] = reason
                if decision == "accept":
                    if active_id is not None and str(active_id) in generations:
                        previous = dict(generations[str(active_id)])
                        previous["status"] = "superseded"
                        generations[str(active_id)] = previous
                    target["status"] = "active"
                    active_id = generation_id
                    event_type = "generation_activated"
                elif decision == "reject":
                    target["status"] = "rejected"
                    event_type = "generation_rejected"
                elif decision == "rollback":
                    target["status"] = "rollback_pending"
                    target["rollback_status"] = "rollback_requested"
                    event_type = "rollback_requested"
                elif decision == "repeat":
                    target["status"] = "repeat_required"
                    event_type = "repeat_required"
                else:
                    target["status"] = "sandbox_longer"
                    event_type = "sandbox_longer_required"
                generations[str(generation_id)] = target
                lineage["generations"] = generations
                lineage["active_generation_id"] = active_id
                lineages[lineage_id] = lineage
                changed = True

        elif operation == "record_rollback" and not blocking:
            rollback = _mapping(supplied.get("rollback_result"))
            if not lineage:
                blocking.append("lineage_not_found")
            if generation_id is None or str(generation_id) not in generations:
                blocking.append("generation_not_found")
            if not rollback.get("transaction_id"):
                blocking.append("rollback_transaction_id_required")
            status = str(rollback.get("rollback_status") or "")
            performed = rollback.get("rollback_performed") is True
            if status == "ACEE_ROLLBACK_ENGINE_READY" and not performed:
                blocking.append("rollback_not_performed")
            if status not in {"ACEE_ROLLBACK_ENGINE_READY", "ACEE_ROLLBACK_BLOCKED", "ACEE_ROLLBACK_FAILED"}:
                blocking.append("rollback_status_invalid")
            if not blocking:
                target = dict(generations[str(generation_id)])
                if performed:
                    target["status"] = "rolled_back"
                    target["rollback_status"] = "rolled_back"
                    parent_arch = target.get("parent_id")
                    parent_record = next((g for g in generations.values() if g.get("architecture_id") == parent_arch), None)
                    if parent_record is not None:
                        restored = dict(parent_record)
                        restored["status"] = "active"
                        generations[str(restored["generation_id"])] = restored
                        active_id = restored["generation_id"]
                    event_type = "rollback_completed"
                elif status == "ACEE_ROLLBACK_BLOCKED":
                    target["status"] = "rollback_blocked"
                    target["rollback_status"] = "rollback_blocked"
                    event_type = "rollback_blocked"
                else:
                    target["status"] = "rollback_failed"
                    target["rollback_status"] = "rollback_failed"
                    event_type = "rollback_failed"
                generations[str(generation_id)] = target
                lineage["generations"] = generations
                lineage["active_generation_id"] = active_id
                lineages[lineage_id] = lineage
                changed = True

        ready = not blocking
        if lineage_id and lineage:
            lineages[lineage_id] = lineage
        new_state = {"schema_version": PUBLIC_SCHEMA_VERSION, "lineages": lineages, "processed_transactions": processed}

        generation_record = _mapping(generations.get(str(generation_id))) if generation_id is not None else {}
        if ready and changed and generation_record:
            genealogy_event = {
                "event_type": event_type,
                "lineage_id": lineage_id,
                "generation_id": generation_id,
                "architecture_id": generation_record.get("architecture_id"),
                "parent_architecture_id": generation_record.get("parent_id"),
                "mutation_id": generation_record.get("mutation_id"),
                "selection_reason": generation_record.get("selection_reason"),
                "rollback_status": generation_record.get("rollback_status"),
                "fitness_delta": generation_record.get("fitness_delta"),
                "active": generation_record.get("status") == "active",
                "lineage_management_executed": True,
                "target_primitive": "ACEE_ARCHITECTURE_GENEALOGY",
            }

        result.update({
            "lineage_management_status": STATUS_READY if ready else STATUS_DEGRADED,
            "lineage_management_ready": ready,
            "operation_applied": ready and changed,
            "event_type": event_type,
            "generation_id": generation_id,
            "architecture_id": architecture_id or generation_record.get("architecture_id"),
            "parent_id": parent_id or generation_record.get("parent_id"),
            "mutation_id": mutation_id or generation_record.get("mutation_id"),
            "selection_reason": generation_record.get("selection_reason"),
            "rollback_status": generation_record.get("rollback_status"),
            "fitness_delta": generation_record.get("fitness_delta"),
            "generation_status": generation_record.get("status"),
            "active_generation_id": active_id,
            "blocking_reasons": sorted(set(blocking)),
            "history_corrupted": corrupted,
            "idempotent_replay": False,
            "genealogy_event": genealogy_event,
        })
        result["event_hash"] = _sha({k: v for k, v in result.items() if k != "event_hash"})
        if ready and transaction_id:
            processed[transaction_id] = dict(result)
            new_state["processed_transactions"] = processed
        return result, new_state

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        latest, history, lineages_path, lock = self._paths()
        state, state_corrupted = self._load_state(lineages_path)
        records, history_corrupted = self._load_history(history)
        previous_hash = records[-1].get("event_hash") if records else None
        result, _ = self._transition(supplied, state, previous_hash, state_corrupted or history_corrupted)
        result.update({"persisted": False, "state_path": str(latest), "history_path": str(history), "lineages_path": str(lineages_path)})
        if not persist or not result.get("lineage_management_ready") or result.get("idempotent_replay"):
            return result

        latest.parent.mkdir(parents=True, exist_ok=True)
        with lock.open("a+", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            state, state_corrupted = self._load_state(lineages_path)
            records, history_corrupted = self._load_history(history)
            previous_hash = records[-1].get("event_hash") if records else None
            result, new_state = self._transition(supplied, state, previous_hash, state_corrupted or history_corrupted)
            result.update({"persisted": False, "state_path": str(latest), "history_path": str(history), "lineages_path": str(lineages_path)})
            if not result.get("lineage_management_ready") or result.get("idempotent_replay"):
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
                return result
            result["persisted"] = True
            result["event_hash"] = _sha({k: v for k, v in result.items() if k not in {"event_hash", "persisted", "state_path", "history_path", "lineages_path"}})
            new_state["processed_transactions"][str(result["transaction_id"])] = dict(result)
            with history.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, sort_keys=True) + "\n")
                handle.flush()
            state_tmp = lineages_path.with_suffix(".tmp")
            state_tmp.write_text(json.dumps(new_state, sort_keys=True, indent=2), encoding="utf-8")
            state_tmp.replace(lineages_path)
            latest_tmp = latest.with_suffix(".tmp")
            latest_tmp.write_text(json.dumps(result, sort_keys=True, indent=2), encoding="utf-8")
            latest_tmp.replace(latest)
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            return result
