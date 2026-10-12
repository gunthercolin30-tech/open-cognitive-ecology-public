"""ACEE11 — governed transactional rollback engine.

Restores explicitly declared files from backups inside the Open Cognitive Ecology
root. It does not decide whether rollback is desirable and never bypasses a
constitutional or governance refusal.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_ROLLBACK_ENGINE"
STATUS_READY = "ACEE_ROLLBACK_ENGINE_READY"
STATUS_BLOCKED = "ACEE_ROLLBACK_BLOCKED"
STATUS_FAILED = "ACEE_ROLLBACK_FAILED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
ALLOWED_REASONS = {
    "error_count_positive", "validation_failure", "stability_regression",
    "identity_regression", "closure_pressure_increase", "governance_violation",
    "explicit_governed_request",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(value: Any) -> str:
    return _sha256_bytes(_canonical(value).encode("utf-8"))


def _canonical_path(path: Path) -> Path:
    """Return a physical absolute path, including macOS /var aliases."""
    return Path(os.path.realpath(os.path.abspath(os.path.expanduser(str(path)))))


def _inside(root: Path, candidate: Path) -> bool:
    try:
        _canonical_path(candidate).relative_to(_canonical_path(root))
        return True
    except ValueError:
        return False


def _decision(raw: Any) -> Optional[bool]:
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, Mapping):
        for key in ("approved", "authorized", "accepted", "compliant", "governance_approved"):
            if key in raw and isinstance(raw[key], bool):
                return raw[key]
        value = str(raw.get("status") or raw.get("decision") or "").lower()
    else:
        value = str(raw or "").lower()
    if any(x in value for x in ("reject", "block", "fail", "declin")):
        return False
    if any(x in value for x in ("approv", "authoriz", "accept", "pass", "compliant")):
        return True
    return None


@dataclass
class AceeRollbackEngine:
    root: Optional[Path] = None
    filesystem_effect_context_provider: Any = None

    def _take_filesystem_effect_context(self, operation_id: str, target: Path):
        provider = self.filesystem_effect_context_provider
        if provider is None or not callable(provider):
            raise RuntimeError("governed_filesystem_effect_context_provider_required")
        context = provider(operation_id, target)
        if context is None:
            raise RuntimeError("preissued_filesystem_effect_context_required")
        return context

    def _ensure_parent_governed(self, path: Path) -> None:
        missing=[]; cursor=path.parent
        while cursor != self.root and not cursor.exists():
            missing.append(cursor); cursor=cursor.parent
        for directory in reversed(missing):
            context=self._take_filesystem_effect_context("FS_CREATE_DIR", directory); context.begin()
            context.execute_path("p162g6_index2_acee11_parent_create", "FS_CREATE_DIR", directory)

    def _governed_path_effect(self, operation_id: str, slot: str, path: Path, payload: Optional[bytes] = None):
        context=self._take_filesystem_effect_context(operation_id, path); context.begin()
        return context.execute_path(slot, operation_id, path, payload)


    def __post_init__(self) -> None:
        configured_root = (
            Path(self.root)
            if self.root is not None
            else Path.home() / "open-cognitive-ecology"
        )
        self.root = _canonical_path(configured_root)

    def _runtime_paths(self) -> Tuple[Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE11_acee_rollback_engine"
        return directory / "latest_rollback.json", directory / "rollback_history.jsonl", directory / ".rollback.lock"

    def _targets(self, inputs: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        request = inputs.get("rollback_request") if isinstance(inputs.get("rollback_request"), Mapping) else inputs
        raw_targets = request.get("targets") if isinstance(request, Mapping) else None
        errors: List[str] = []
        targets: List[Dict[str, Any]] = []
        if not isinstance(raw_targets, list) or not raw_targets:
            return [], ["targets_missing"]
        for index, item in enumerate(raw_targets):
            if not isinstance(item, Mapping):
                errors.append(f"target_{index}_invalid")
                continue
            destination_raw = item.get("destination") or item.get("path")
            backup_raw = item.get("backup") or item.get("backup_path")
            if not isinstance(destination_raw, str) or not destination_raw.strip():
                errors.append(f"target_{index}_destination_missing")
                continue
            destination = (self.root / destination_raw).resolve(strict=False) if not Path(destination_raw).is_absolute() else Path(destination_raw).resolve(strict=False)
            backup = (self.root / backup_raw).resolve(strict=False) if isinstance(backup_raw, str) and not Path(backup_raw).is_absolute() else Path(backup_raw).resolve(strict=False) if isinstance(backup_raw, str) else Path(str(destination) + ".bak").resolve(strict=False)
            if not _inside(self.root, destination) or not _inside(self.root, backup):
                errors.append(f"target_{index}_outside_root")
                continue
            expected_hash = item.get("expected_backup_sha256")
            targets.append({
                "destination": destination,
                "backup": backup,
                "expected_backup_sha256": str(expected_hash) if expected_hash else None,
            })
        destination_indexes: Dict[Path, List[int]] = {}
        for index, target in enumerate(targets):
            canonical_destination = _canonical_path(target["destination"])
            destination_indexes.setdefault(
                canonical_destination,
                [],
            ).append(index)

        for indexes in destination_indexes.values():
            if len(indexes) > 1:
                joined = ",".join(str(index) for index in indexes)
                errors.append(
                    f"duplicate_destination_targets:{joined}"
                )

        canonical_destinations = {
            _canonical_path(target["destination"])
            for target in targets
        }
        for index, target in enumerate(targets):
            canonical_backup = _canonical_path(target["backup"])
            if canonical_backup in canonical_destinations:
                errors.append(
                    f"backup_destination_collision:{index}"
                )

        return targets, errors

    def _build_base(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        request = inputs.get("rollback_request") if isinstance(inputs.get("rollback_request"), Mapping) else inputs
        reason = str(request.get("reason") or "") if isinstance(request, Mapping) else ""
        governance = _decision(inputs.get("governance_authorization"))
        constitutional = _decision(inputs.get("constitutional_authorization"))
        dry_run = bool(inputs.get("dry_run", True))
        execute = bool(inputs.get("execute", False))
        transaction_id = str(request.get("transaction_id") or "") if isinstance(request, Mapping) else ""
        timestamp = str(inputs.get("timestamp_utc") or _utc_now())
        targets, target_errors = self._targets(inputs)
        blocking = list(target_errors)
        if reason not in ALLOWED_REASONS:
            blocking.append("rollback_reason_not_authorized")
        if governance is not True:
            blocking.append("governance_authorization_missing_or_rejected")
        if constitutional is not True:
            blocking.append("constitutional_authorization_missing_or_rejected")
        if not transaction_id:
            blocking.append("transaction_id_missing")
        if execute and dry_run:
            blocking.append("execute_and_dry_run_conflict")
        inspections = []
        for target in targets:
            backup = target["backup"]
            exists = backup.is_file()
            digest = _sha256_bytes(backup.read_bytes()) if exists else None
            valid_hash = target["expected_backup_sha256"] in (None, digest)
            if not exists:
                blocking.append(f"backup_missing:{backup.relative_to(self.root)}")
            if exists and not valid_hash:
                blocking.append(f"backup_hash_mismatch:{backup.relative_to(self.root)}")
            inspections.append({
                "destination": str(target["destination"].relative_to(self.root)),
                "backup": str(backup.relative_to(self.root)),
                "backup_exists": exists,
                "backup_sha256": digest,
                "expected_backup_sha256": target["expected_backup_sha256"],
                "backup_hash_valid": valid_hash,
            })
        blocking = sorted(set(blocking))
        eligible = not blocking
        return {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": timestamp,
            "transaction_id": transaction_id,
            "reason": reason,
            "dry_run": dry_run,
            "execute_requested": execute,
            "governance_authorized": governance is True,
            "constitutional_authorized": constitutional is True,
            "rollback_eligible": eligible,
            "target_count": len(targets),
            "target_inspections": inspections,
            "blocking_reasons": blocking,
            "targets_internal": targets,
        }

    def _restore(self, base: Dict[str, Any]) -> Dict[str, Any]:
        targets = base.pop("targets_internal")
        if not base["rollback_eligible"]:
            base.update({"rollback_status": STATUS_BLOCKED, "rollback_ready": False, "rollback_performed": False, "restored_count": 0, "restored_files": [], "failure": None})
            return base
        if base["dry_run"] or not base["execute_requested"]:
            base.update({"rollback_status": STATUS_READY, "rollback_ready": True, "rollback_performed": False, "restored_count": 0, "restored_files": [], "failure": None})
            return base
        if self.filesystem_effect_context_provider is not None:
            if len(targets) != 1:
                base.update({"rollback_status": STATUS_FAILED, "rollback_ready": False, "rollback_performed": False, "restored_count": 0, "restored_files": [], "failure": "governed_single_target_required"})
                return base
            destination=targets[0]["destination"]; backup=targets[0]["backup"]
            try:
                self._ensure_parent_governed(destination)
                context=self._take_filesystem_effect_context("FS_COPY2", destination); context.begin()
                if not context.root_id: raise RuntimeError("filesystem_effect_context_root_id_required")
                context.execute_copy2("p162g6_index2_acee11_restore_copy2", str(context.root_id), self.root, backup, destination)
                restored=[str(destination.relative_to(self.root))]
                base.update({"rollback_status": STATUS_READY, "rollback_ready": True, "rollback_performed": True, "restored_count": 1, "restored_files": restored, "failure": None})
            except Exception as exc:
                base.update({"rollback_status": STATUS_FAILED, "rollback_ready": False, "rollback_performed": False, "restored_count": 0, "restored_files": [], "failure": f"{type(exc).__name__}:{exc}"})
            return base
        base.update({
            "rollback_status": STATUS_FAILED,
            "rollback_ready": False,
            "rollback_performed": False,
            "restored_count": 0,
            "restored_files": [],
            "failure": "governed_filesystem_effect_context_provider_required",
        })
        return base

    def _persist(self, result: Dict[str, Any]) -> Dict[str, Any]:
        latest, history, lock = self._runtime_paths()
        if self.filesystem_effect_context_provider is not None:
            self._ensure_parent_governed(latest)
            if not lock.exists(): self._governed_path_effect("FS_WRITE_BYTES", "p162g6_index2_acee11_lock_create", lock, b"")
            with lock.open("r+", encoding="utf-8") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                try:
                    previous_hash=None; history_corrupted=False
                    if history.is_file():
                        try:
                            lines=[line for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
                            if lines: previous_hash=json.loads(lines[-1]).get("record_hash")
                        except (OSError,json.JSONDecodeError): history_corrupted=True
                    record={**result,"previous_record_hash":previous_hash,"history_corrupted":history_corrupted}
                    record["record_hash"]=_sha256(record)
                    self._governed_path_effect("FS_APPEND_BYTES", "p162g6_index2_acee11_history_append", history, (_canonical(record)+"\n").encode("utf-8"))
                    self._governed_path_effect("FS_WRITE_REPLACE_BYTES", "p162g6_index2_acee11_latest_replace", latest, (json.dumps(record,indent=2,sort_keys=True)+"\n").encode("utf-8"))
                finally: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            return {**record,"persisted":True,"latest_path":str(latest),"history_path":str(history)}
        latest.parent.mkdir(parents=True, exist_ok=True)
        with lock.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            previous_hash = None
            history_corrupted = False
            if history.is_file():
                try:
                    lines = [line for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
                    if lines:
                        previous_hash = json.loads(lines[-1]).get("record_hash")
                except (OSError, json.JSONDecodeError):
                    history_corrupted = True
            record = {**result, "previous_record_hash": previous_hash, "history_corrupted": history_corrupted}
            record_hash = _sha256(record)
            record["record_hash"] = record_hash
            with history.open("a", encoding="utf-8") as stream:
                stream.write(_canonical(record) + "\n")
                stream.flush(); os.fsync(stream.fileno())
            tmp = latest.with_suffix(".tmp")
            tmp.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
            os.replace(str(tmp), str(latest))
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return {**record, "persisted": True, "latest_path": str(latest), "history_path": str(history)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        supplied = dict(inputs) if isinstance(inputs, Mapping) else {}
        base = self._build_base(supplied)
        result = self._restore(base)
        result.update({
            "rollback_engine_ready": result["rollback_status"] == STATUS_READY,
            "consciousness_proven": False, "subjectivity_proven": False,
            "qualia_proven": False, "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "persisted": False,
        })
        result["result_hash"] = _sha256({k: v for k, v in result.items() if k not in {"result_hash", "persisted"}})
        return self._persist(result) if persist else result
