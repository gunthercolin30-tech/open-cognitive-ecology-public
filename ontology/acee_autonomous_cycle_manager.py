"""ACEE4 — governed autonomous cycle coordination facade.

Orders and evaluates externally supplied phase results. It does not execute
runtime engines, generate/install code, run validation.main, or perform rollback.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_AUTONOMOUS_CYCLE_MANAGER"
STATUS_COMPLETE = "ACEE_AUTONOMOUS_CYCLE_COMPLETE"
STATUS_DEGRADED = "ACEE_AUTONOMOUS_CYCLE_DEGRADED"
STATUS_ROLLBACK = "ACEE_AUTONOMOUS_CYCLE_ROLLBACK_REQUIRED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
PHASES = (
    "snapshot", "diagnostic", "hypothesis", "intervention", "sandbox",
    "validation", "impact_measurement", "selection",
    "rollback_or_acceptance", "history_update",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _number(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if result != result or result in (float("inf"), float("-inf")):
        return default
    return max(0.0, min(1.0, result))


def _passed(value: Mapping[str, Any]) -> Optional[bool]:
    for key in ("passed", "approved", "accepted", "success", "valid", "ready", "completed"):
        if isinstance(value.get(key), bool):
            return bool(value[key])
    status = str(value.get("status") or value.get("decision") or "").lower()
    if any(x in status for x in ("fail", "reject", "block", "invalid", "degrad")):
        return False
    if any(x in status for x in ("pass", "approv", "accept", "valid", "ready", "complete", "success")):
        return True
    return None


@dataclass
class AceeAutonomousCycleManager:
    root: Optional[Path] = None

    def __post_init__(self) -> None:
        self.root = Path(self.root) if self.root is not None else Path.home() / "open-cognitive-ecology"

    def _paths(self) -> Tuple[Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE4_acee_autonomous_cycle_manager"
        return directory / "latest_cycle.json", directory / "cycle_history.jsonl", directory / ".cycle.lock"

    def _previous(self, history: Path) -> Tuple[Optional[Dict[str, Any]], bool]:
        if not history.is_file():
            return None, False
        try:
            lines = [x for x in history.read_text(encoding="utf-8").splitlines() if x.strip()]
            return (json.loads(lines[-1]), False) if lines else (None, False)
        except (OSError, json.JSONDecodeError):
            return None, True

    def _cycle_id_exists(self, history: Path, cycle_id: str) -> bool:
        if not history.is_file():
            return False
        try:
            for line in history.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                if str(record.get("cycle_id")) == cycle_id:
                    return True
        except (OSError, json.JSONDecodeError):
            return False
        return False

    def _apply_cycle_id_collision(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        updated = dict(result)
        blocking = list(updated.get("blocking_reasons", []))
        blocking.append("duplicate_cycle_id")
        updated["blocking_reasons"] = sorted(set(blocking))
        updated["cycle_id_collision"] = True
        updated["duplicate_cycle_id"] = True
        updated["accepted"] = False
        updated["cycle_complete"] = False
        updated["cycle_status"] = STATUS_DEGRADED
        updated["cycle_outcome"] = "degraded"
        updated["current_phase"] = "blocked"
        updated["cycle_hash"] = _sha({
            key: value
            for key, value in updated.items()
            if key != "cycle_hash"
        })
        return updated

    def _build(self, supplied: Mapping[str, Any], previous_hash: Optional[str], corrupted: bool) -> Dict[str, Any]:
        phase_results = _mapping(supplied.get("phase_results"))
        requested = supplied.get("requested_phases", list(PHASES))
        requested = [str(x) for x in requested] if isinstance(requested, list) else list(PHASES)
        blocking: List[str] = []
        warnings: List[str] = []

        unknown = [x for x in requested if x not in PHASES]
        if unknown:
            blocking.append("unknown_phases:" + ",".join(sorted(set(unknown))))
        canonical_requested = [x for x in PHASES if x in requested]
        if canonical_requested != [x for x in requested if x in PHASES]:
            blocking.append("phase_order_invalid")

        completed: List[str] = []
        failed: List[str] = []
        missing: List[str] = []
        phase_scores: Dict[str, float] = {}
        for phase in canonical_requested:
            raw = _mapping(phase_results.get(phase))
            if not raw:
                missing.append(phase)
                continue
            decision = _passed(raw)
            score = _number(raw.get("score", raw.get("confidence", 1.0 if decision is True else 0.0)))
            phase_scores[phase] = score
            if decision is False:
                failed.append(phase)
            elif decision is True:
                completed.append(phase)
            else:
                warnings.append(f"phase_status_undetermined:{phase}")

        allow_partial = supplied.get("allow_partial_cycle") is True
        if missing and not allow_partial:
            blocking.extend(f"phase_missing:{x}" for x in missing)
        if failed:
            blocking.extend(f"phase_failed:{x}" for x in failed)

        governance = _mapping(supplied.get("governance_decision"))
        constitutional = _mapping(supplied.get("constitutional_decision"))
        gov_ok = _passed(governance)
        const_ok = _passed(constitutional)
        if gov_ok is not True:
            blocking.append("governance_not_approved")
        if const_ok is not True:
            blocking.append("constitutional_not_approved")

        validation = _mapping(phase_results.get("validation"))
        sandbox = _mapping(phase_results.get("sandbox"))
        selection = _mapping(phase_results.get("selection"))
        rollback_phase = _mapping(phase_results.get("rollback_or_acceptance"))
        validation_ok = _passed(validation)
        sandbox_ok = _passed(sandbox)
        selection_decision = str(selection.get("decision") or selection.get("status") or "undetermined").lower()
        explicit_rollback = supplied.get("rollback_required") is True
        rollback_required = bool(
            explicit_rollback or validation_ok is False or sandbox_ok is False
            or "rollback" in selection_decision or "reject" in selection_decision
        )
        rollback_result_supplied = bool(rollback_phase)
        rollback_completed = _passed(rollback_phase) is True and (
            rollback_phase.get("rollback_performed") is True
            or str(rollback_phase.get("decision") or "").lower() == "accepted"
        )
        if rollback_required and not rollback_result_supplied:
            blocking.append("rollback_result_missing")

        accepted = (
            not rollback_required and not blocking and
            selection_decision in {"accept", "accepted", "retain", "approved"}
        )
        if not rollback_required and selection_decision not in {"accept", "accepted", "retain", "approved"}:
            blocking.append("selection_not_accepted")

        score = round(sum(phase_scores.values()) / len(phase_scores), 6) if phase_scores else 0.0
        risk = round(1.0 - score, 6)
        closure_pressure = _number(supplied.get("closure_pressure", 0.0))
        if closure_pressure > _number(supplied.get("closure_pressure_threshold", 0.2), 0.2):
            blocking.append("closure_pressure_threshold_exceeded")
            rollback_required = True

        cycle_complete = bool(
            (accepted or (rollback_required and rollback_completed))
            and not [x for x in blocking if x != "phase_failed:validation"]
        )
        if rollback_required:
            status = STATUS_ROLLBACK if not rollback_completed else STATUS_COMPLETE
            outcome = "rolled_back" if rollback_completed else "rollback_required"
        elif cycle_complete:
            status = STATUS_COMPLETE
            outcome = "accepted"
        else:
            status = STATUS_DEGRADED
            outcome = "degraded"

        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "cycle_id": str(supplied.get("cycle_id") or "cycle-unspecified"),
            "timestamp_utc": str(supplied.get("timestamp_utc") or _now()),
            "cycle_status": status,
            "cycle_outcome": outcome,
            "cycle_complete": cycle_complete,
            "current_phase": next((x for x in canonical_requested if x not in completed), "complete" if cycle_complete else "blocked"),
            "requested_phases": canonical_requested,
            "completed_phases": completed,
            "failed_phases": failed,
            "missing_phases": missing,
            "phase_scores": phase_scores,
            "delegation_results": phase_results,
            "selection_decision": selection_decision,
            "accepted": accepted,
            "rollback_required": rollback_required,
            "rollback_result_supplied": rollback_result_supplied,
            "rollback_completed": rollback_completed,
            "cycle_score": score,
            "risk_score": risk,
            "closure_pressure": closure_pressure,
            "governance_compliant": gov_ok is True,
            "constitutional_compliant": const_ok is True,
            "blocking_reasons": sorted(set(blocking)),
            "warnings": sorted(set(warnings)),
            "history_corrupted": corrupted,
            "previous_cycle_hash": previous_hash,
            "execution_dispatched": False,
            "runtime_executed": False,
            "code_generated": False,
            "code_installed": False,
            "validation_main_executed": False,
            "rollback_executed_by_manager": False,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        result["cycle_hash"] = _sha({k: v for k, v in result.items() if k != "cycle_hash"})
        return result

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        latest, history, lock = self._paths()
        previous, corrupted = self._previous(history)
        result = self._build(supplied, previous.get("cycle_hash") if previous else None, corrupted)
        result["persisted"] = False
        result["latest_path"] = str(latest)
        result["history_path"] = str(history)
        if persist:
            latest.parent.mkdir(parents=True, exist_ok=True)
            with lock.open("a+", encoding="utf-8") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                previous, corrupted = self._previous(history)
                result = self._build(supplied, previous.get("cycle_hash") if previous else None, corrupted)
                cycle_id = str(result.get("cycle_id") or "cycle-unspecified")
                if self._cycle_id_exists(history, cycle_id):
                    result = self._apply_cycle_id_collision(result)
                else:
                    result["cycle_id_collision"] = False
                    result["duplicate_cycle_id"] = False
                    result["cycle_hash"] = _sha({
                        key: value
                        for key, value in result.items()
                        if key != "cycle_hash"
                    })
                record = dict(result)
                record["persisted"] = True
                record["latest_path"] = str(latest)
                record["history_path"] = str(history)
                latest_tmp = latest.with_suffix(".tmp")
                latest_tmp.write_text(json.dumps(record, sort_keys=True, indent=2), encoding="utf-8")
                latest_tmp.replace(latest)
                with history.open("a", encoding="utf-8") as stream:
                    stream.write(_canonical(record) + "\n")
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                result = record
        return result
