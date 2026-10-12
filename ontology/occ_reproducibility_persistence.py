"""
P159 OCC-1J — Reproducibility / Persistence.

Functional-only support for deterministic constitutional compilation artifacts.
This module does not authorize, execute, certify, activate, or perform P159 Final Lock.
"""

from __future__ import annotations

import hashlib
import json
import locale
import os
import platform
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PRIMITIVE = "occ_reproducibility_persistence"
VERSION = "1.0.0"

DEPENDENCIES = [
    "occ_constitutional_compiler",
    "occ_compiled_normative_profile",
    "occ_independent_constitutional_verifier",
]

LIFECYCLE_EVENTS = (
    "PROFILE_BUILT", "VERIFIED", "SEALED", "CERTIFIED",
    "ACTIVATED", "SUPERSEDED", "REVOKED", "ROLLBACK",
)

AUTHORITY_CREATING_FIELDS = (
    "authorization_created", "authority_created", "execution_performed",
    "self_activation", "p159_final_lock", "p160_opened",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def semantic_hash(canonical_payload: Mapping[str, Any]) -> str:
    return canonical_sha256(dict(canonical_payload))


def make_envelope(
    canonical_payload: Mapping[str, Any],
    execution_metadata: Mapping[str, Any] | None = None,
) -> dict:
    payload = deepcopy(dict(canonical_payload))
    metadata = deepcopy(dict(execution_metadata or {}))
    envelope = {
        "schema": "oce.p159.occ1j.reproducible_artifact.v1",
        "CANONICAL_PAYLOAD": payload,
        "EXECUTION_METADATA": metadata,
        "semantic_hash": semantic_hash(payload),
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
    envelope["artifact_hash"] = canonical_sha256(envelope)
    return envelope


def verify_envelope(envelope: Mapping[str, Any]) -> dict:
    obj = deepcopy(dict(envelope))
    supplied_artifact = obj.pop("artifact_hash", None)
    expected_artifact = canonical_sha256(obj)
    payload = obj.get("CANONICAL_PAYLOAD")
    if not isinstance(payload, Mapping):
        return {"status": "FAIL", "reason": "CANONICAL_PAYLOAD_MISSING"}
    if supplied_artifact != expected_artifact:
        return {"status": "FAIL", "reason": "ARTIFACT_HASH_MISMATCH"}
    if obj.get("semantic_hash") != semantic_hash(payload):
        return {"status": "FAIL", "reason": "SEMANTIC_HASH_MISMATCH"}
    return {
        "status": "PASS",
        "reason": "REPRODUCIBLE_ARTIFACT_INTEGRITY_OK",
        "semantic_hash": obj["semantic_hash"],
        "artifact_hash": supplied_artifact,
    }


def build_identity(
    source_files: Sequence[Path],
    *,
    nir_schema_version: str,
    compiler_version: str,
    compiler_file: Path,
    dependency_manifest_file: Path,
    canonicalizer_version: str,
    checker_version: str,
    build_profile: str,
) -> dict:
    sources = []
    for p in sorted((Path(x) for x in source_files), key=lambda x: x.as_posix()):
        if not p.is_file():
            raise FileNotFoundError(str(p))
        sources.append({"logical_name": p.name, "sha256": file_sha256(p)})
    source_package_hash = canonical_sha256(sources)
    result = {
        "schema": "oce.p159.occ1j.build_identity.v1",
        "source_package_hash": source_package_hash,
        "sources": sources,
        "nir_schema_version": str(nir_schema_version),
        "compiler_version": str(compiler_version),
        "compiler_hash": file_sha256(compiler_file),
        "dependency_manifest_hash": file_sha256(dependency_manifest_file),
        "canonicalizer_version": str(canonicalizer_version),
        "checker_version": str(checker_version),
        "build_profile": str(build_profile),
    }
    result["build_identity_hash"] = canonical_sha256(result)
    return result


def environment_fingerprint(timezone_policy: str = "UTC") -> dict:
    # Deliberately excludes CWD, hostname and username from semantic identity.
    preferred_encoding = locale.getpreferredencoding(False)
    return {
        "schema": "oce.p159.occ1j.environment_fingerprint.v1",
        "os_family": platform.system(),
        "architecture": platform.machine(),
        "runtime": platform.python_implementation(),
        "runtime_version": platform.python_version(),
        "preferred_encoding": preferred_encoding,
        "timezone_policy": str(timezone_policy),
    }


def atomic_write_json(
    path: Path,
    payload: Mapping[str, Any],
    *,
    filesystem_context=None,
) -> dict:
    path = Path(path)
    encoded = (
        json.dumps(
            payload, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False
        ) + "\n"
    ).encode("utf-8")

    if filesystem_context is None:
        raise PermissionError("governed filesystem context required")
    remaining = filesystem_context.remaining()
    if remaining.get("atomic_parent_create", 0) < 1:
        raise RuntimeError("atomic_parent_create authority required")
    if remaining.get("atomic_write_replace", 0) < 1:
        raise RuntimeError("atomic_write_replace authority required")

    filesystem_context.execute_path(
        "atomic_parent_create", "FS_CREATE_DIRS", path.parent,
    )
    filesystem_context.execute_path(
        "atomic_write_replace", "FS_WRITE_REPLACE_BYTES", path, payload=encoded,
    )
    return {"status": "PASS", "reason": "ATOMIC_WRITE_COMMITTED", "path": str(path)}


def verify_build_completeness(
    build_dir: Path,
    expected_relative_files: Iterable[str],
    influencing_relative_files: Iterable[str] | None = None,
) -> dict:
    root = Path(build_dir)
    expected = {str(Path(x).as_posix()) for x in expected_relative_files}
    present = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not p.name.endswith(".tmp")
    }
    missing = sorted(expected - present)
    if missing:
        return {"status": "FAIL", "reason": "BUILD_INCOMPLETE", "missing": missing}
    influencing = set(influencing_relative_files or ())
    unexpected_influencing = sorted(influencing - expected)
    if unexpected_influencing:
        return {
            "status": "FAIL", "reason": "BUILD_CONTAMINATION",
            "unexpected_influencing": unexpected_influencing,
        }
    return {"status": "PASS", "reason": "BUILD_COMPLETE", "present": sorted(present)}


def _event_payload(event: Mapping[str, Any]) -> dict:
    obj = deepcopy(dict(event))
    obj.pop("event_hash", None)
    return obj


class NormativeLifecycleJournal:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        events = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events

    def verify(self) -> dict:
        previous = "GENESIS"
        events = self.read()
        for index, event in enumerate(events):
            if event.get("sequence") != index + 1:
                return {"status": "FAIL", "reason": "JOURNAL_SEQUENCE_INVALID", "index": index}
            if event.get("previous_event_hash") != previous:
                return {"status": "FAIL", "reason": "JOURNAL_CHAIN_INVALID", "index": index}
            if event.get("event_hash") != canonical_sha256(_event_payload(event)):
                return {"status": "FAIL", "reason": "JOURNAL_EVENT_HASH_INVALID", "index": index}
            previous = event["event_hash"]
        return {
            "status": "PASS", "reason": "JOURNAL_CHAIN_OK",
            "event_count": len(events), "last_event_hash": previous,
        }

    def append(
        self,
        event_type: str,
        profile_semantic_hash: str,
        *,
        state: str,
        timestamp_utc: str,
        details: Mapping[str, Any] | None = None,
        filesystem_context=None,
    ) -> dict:
        if event_type not in LIFECYCLE_EVENTS:
            return {"status": "FAIL", "reason": "UNKNOWN_LIFECYCLE_EVENT"}
        verification = self.verify()
        if verification["status"] != "PASS":
            return verification
        events = self.read()
        event = {
            "schema": "oce.p159.occ1j.lifecycle_event.v1",
            "sequence": len(events) + 1,
            "event_type": event_type,
            "profile_semantic_hash": str(profile_semantic_hash),
            "state": str(state),
            "timestamp_utc": str(timestamp_utc),
            "previous_event_hash": verification["last_event_hash"],
            "details": deepcopy(dict(details or {})),
        }
        event["event_hash"] = canonical_sha256(event)
        if not self.path.parent.exists():
            if filesystem_context is None:
                raise RuntimeError("governed_filesystem_context_required")
            if getattr(filesystem_context, "authority_minting", True) is not False:
                raise RuntimeError("governed_filesystem_context_must_be_non_minting")
            filesystem_context.begin()
            filesystem_context.execute_path(
                "occ_lifecycle_journal_parent_create", "FS_CREATE_DIRS", self.path.parent,
            )
        line = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        return {"status": "PASS", "reason": "JOURNAL_EVENT_APPENDED", "event": event}


def reconcile_state(snapshot: Mapping[str, Any], journal: NormativeLifecycleJournal) -> dict:
    verification = journal.verify()
    if verification["status"] != "PASS":
        return verification
    events = journal.read()
    if not events:
        return {"status": "FAIL", "reason": "CONTINUITY_UNCERTAIN"}
    last = events[-1]
    if snapshot.get("last_event_hash") != last.get("event_hash"):
        return {"status": "FAIL", "reason": "CONTINUITY_UNCERTAIN"}
    if snapshot.get("profile_semantic_hash") != last.get("profile_semantic_hash"):
        return {"status": "FAIL", "reason": "CONTINUITY_UNCERTAIN"}
    if snapshot.get("profile_state") != last.get("state"):
        return {"status": "FAIL", "reason": "CONTINUITY_UNCERTAIN"}
    return {"status": "PASS", "reason": "STATE_JOURNAL_RECONCILED"}


def restart_guard(persisted: Mapping[str, Any]) -> dict:
    state = deepcopy(dict(persisted))
    for field in AUTHORITY_CREATING_FIELDS:
        if state.get(field) is True:
            return {"status": "FAIL", "reason": "RESTART_AUTHORITY_BOUNDARY_VIOLATION", "field": field}
    if state.get("pending_authorization") is True and state.get("authorized") is True:
        return {"status": "FAIL", "reason": "RESTART_MANUFACTURED_AUTHORIZATION"}
    return {
        "status": "PASS", "reason": "RESTART_AUTHORITY_BOUNDARY_PRESERVED",
        "state": state,
    }


def clock_integrity(previous_utc: str, current_utc: str, tolerance_seconds: float = 1.0) -> dict:
    def parse(value: str) -> datetime:
        v = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    previous = parse(previous_utc)
    current = parse(current_utc)
    rollback = (previous - current).total_seconds()
    if rollback > float(tolerance_seconds):
        return {
            "status": "INCONCLUSIVE",
            "reason": "CLOCK_INTEGRITY_UNCERTAIN",
            "rollback_seconds": rollback,
        }
    return {"status": "PASS", "reason": "CLOCK_INTEGRITY_OK"}


def reproducibility_report(
    reference_envelope: Mapping[str, Any],
    rebuilt_envelope: Mapping[str, Any],
    build_identity_record: Mapping[str, Any],
) -> dict:
    ref = verify_envelope(reference_envelope)
    reb = verify_envelope(rebuilt_envelope)
    same_semantics = (
        ref.get("status") == "PASS"
        and reb.get("status") == "PASS"
        and ref.get("semantic_hash") == reb.get("semantic_hash")
    )
    return {
        "schema": "oce.p159.occ1j.reproducibility_report.v1",
        "status": "PASS" if same_semantics else "FAIL",
        "reason": "REPRODUCIBILITY_CONFIRMED" if same_semantics else "REPRODUCIBILITY_MISMATCH",
        "same_canonical_payload": same_semantics,
        "reference_semantic_hash": ref.get("semantic_hash"),
        "rebuilt_semantic_hash": reb.get("semantic_hash"),
        "build_identity_hash": build_identity_record.get("build_identity_hash"),
        "metadata_may_differ": True,
        "authorization_created": False,
        "execution_performed": False,
        "p159_final_lock": False,
        "p160_opened": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }


def persistence_report(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    journal_verification: Mapping[str, Any],
) -> dict:
    preserved = canonical_sha256(before) == canonical_sha256(after)
    journal_ok = journal_verification.get("status") == "PASS"
    ok = preserved and journal_ok
    return {
        "schema": "oce.p159.occ1j.persistence_report.v1",
        "status": "PASS" if ok else "FAIL",
        "reason": "PERSISTENCE_CONFIRMED" if ok else "PERSISTENCE_MISMATCH",
        "semantic_state_preserved": preserved,
        "journal_chain_valid": journal_ok,
        "authorization_created": False,
        "execution_performed": False,
        "p159_final_lock": False,
        "p160_opened": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
# OCC-1J final-gap refinement — transactional lifecycle, restore qualification,
# and safe archive extraction. Functional-only; never creates authority.

def _read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def lifecycle_transaction(
    journal: NormativeLifecycleJournal,
    snapshot_path: Path,
    *,
    expected_state: str,
    event_type: str,
    new_state: str,
    profile_semantic_hash: str,
    timestamp_utc: str,
    details: Mapping[str, Any] | None = None,
    interrupt_after: str | None = None,
) -> dict:
    """Fail-closed PREPARE -> VERIFY -> COMMIT lifecycle transition.

    A durable .txn record makes an interrupted transition auditable/recoverable.
    This function does not authorize, activate, certify, execute, or lock P159.
    """
    snapshot_path = Path(snapshot_path)
    txn_path = snapshot_path.with_name(snapshot_path.name + ".txn")
    if txn_path.exists():
        return {"status": "FAIL", "reason": "LIFECYCLE_TRANSACTION_PENDING"}

    if not snapshot_path.exists():
        return {"status": "FAIL", "reason": "LIFECYCLE_SNAPSHOT_MISSING"}
    snapshot = _read_json(snapshot_path)
    if snapshot.get("profile_state") != expected_state:
        return {"status": "FAIL", "reason": "LIFECYCLE_EXPECTED_STATE_CONFLICT"}
    if snapshot.get("profile_semantic_hash") != str(profile_semantic_hash):
        return {"status": "FAIL", "reason": "LIFECYCLE_PROFILE_HASH_CONFLICT"}

    verification = journal.verify()
    if verification.get("status") != "PASS":
        return verification
    if snapshot.get("last_event_hash") != verification.get("last_event_hash"):
        return {"status": "FAIL", "reason": "CONTINUITY_UNCERTAIN"}

    txn = {
        "schema": "oce.p159.occ1j.lifecycle_transaction.v1",
        "phase": "PREPARE",
        "event_type": str(event_type),
        "expected_state": str(expected_state),
        "new_state": str(new_state),
        "profile_semantic_hash": str(profile_semantic_hash),
        "timestamp_utc": str(timestamp_utc),
        "previous_event_hash": verification["last_event_hash"],
        "details": deepcopy(dict(details or {})),
        "authorization_created": False,
        "execution_performed": False,
        "p159_final_lock": False,
        "p160_opened": False,
    }
    atomic_write_json(txn_path, txn)
    if interrupt_after == "PREPARE":
        return {"status": "INCONCLUSIVE", "reason": "LIFECYCLE_INTERRUPTED_AFTER_PREPARE"}

    # VERIFY: re-read durable state and journal immediately before append.
    durable = _read_json(snapshot_path)
    recheck = journal.verify()
    if (
        durable.get("profile_state") != expected_state
        or durable.get("profile_semantic_hash") != str(profile_semantic_hash)
        or durable.get("last_event_hash") != txn["previous_event_hash"]
        or recheck.get("status") != "PASS"
        or recheck.get("last_event_hash") != txn["previous_event_hash"]
    ):
        return {"status": "FAIL", "reason": "LIFECYCLE_VERIFY_CONFLICT"}

    txn["phase"] = "VERIFY"
    atomic_write_json(txn_path, txn)
    appended = journal.append(
        event_type, profile_semantic_hash, state=new_state,
        timestamp_utc=timestamp_utc, details=details,
    )
    if appended.get("status") != "PASS":
        return appended
    txn["event_hash"] = appended["event"]["event_hash"]
    txn["phase"] = "JOURNAL_APPENDED"
    atomic_write_json(txn_path, txn)
    if interrupt_after == "JOURNAL_APPENDED":
        return {"status": "INCONCLUSIVE", "reason": "LIFECYCLE_INTERRUPTED_AFTER_JOURNAL_APPEND"}

    committed = deepcopy(durable)
    committed["profile_state"] = str(new_state)
    committed["last_event_hash"] = appended["event"]["event_hash"]
    atomic_write_json(snapshot_path, committed)
    txn["phase"] = "COMMIT"
    atomic_write_json(txn_path, txn)
    txn_path.unlink()
    return {
        "status": "PASS", "reason": "LIFECYCLE_TRANSACTION_COMMITTED",
        "phases": ["PREPARE", "VERIFY", "COMMIT"],
        "event_hash": appended["event"]["event_hash"],
        "authorization_created": False, "execution_performed": False,
        "p159_final_lock": False, "p160_opened": False,
    }


def recover_lifecycle_transaction(
    journal: NormativeLifecycleJournal, snapshot_path: Path
) -> dict:
    """Recover only a uniquely evidenced interrupted transaction; otherwise fail closed."""
    snapshot_path = Path(snapshot_path)
    txn_path = snapshot_path.with_name(snapshot_path.name + ".txn")
    if not txn_path.exists():
        return {"status": "PASS", "reason": "NO_PENDING_LIFECYCLE_TRANSACTION"}
    txn = _read_json(txn_path)
    snapshot = _read_json(snapshot_path)
    check = journal.verify()
    if check.get("status") != "PASS":
        return check

    phase = txn.get("phase")
    if phase in {"PREPARE", "VERIFY"}:
        # No journal event was committed: abort safely and preserve old snapshot.
        if check.get("last_event_hash") != txn.get("previous_event_hash"):
            return {"status": "FAIL", "reason": "CONTINUITY_UNCERTAIN"}
        txn_path.unlink()
        return {"status": "PASS", "reason": "LIFECYCLE_TRANSACTION_ABORTED_PRECOMMIT"}

    if phase == "JOURNAL_APPENDED":
        events = journal.read()
        if not events:
            return {"status": "FAIL", "reason": "CONTINUITY_UNCERTAIN"}
        last = events[-1]
        if (
            last.get("event_hash") != txn.get("event_hash")
            or last.get("previous_event_hash") != txn.get("previous_event_hash")
            or last.get("profile_semantic_hash") != txn.get("profile_semantic_hash")
            or last.get("state") != txn.get("new_state")
            or last.get("event_type") != txn.get("event_type")
        ):
            return {"status": "FAIL", "reason": "CONTINUITY_UNCERTAIN"}
        if (
            snapshot.get("profile_state") != txn.get("expected_state")
            or snapshot.get("profile_semantic_hash") != txn.get("profile_semantic_hash")
            or snapshot.get("last_event_hash") != txn.get("previous_event_hash")
        ):
            return {"status": "FAIL", "reason": "CONTINUITY_UNCERTAIN"}
        recovered = deepcopy(snapshot)
        recovered["profile_state"] = txn["new_state"]
        recovered["last_event_hash"] = txn["event_hash"]
        atomic_write_json(snapshot_path, recovered)
        txn_path.unlink()
        return {"status": "PASS", "reason": "LIFECYCLE_TRANSACTION_RECOVERED"}

    return {"status": "FAIL", "reason": "LIFECYCLE_TRANSACTION_PHASE_INVALID"}


def qualify_restore(
    restored_envelope: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    journal: NormativeLifecycleJournal,
    *,
    expected_profile_semantic_hash: str,
) -> dict:
    """Restore eligibility requires artifact, journal, snapshot and authority checks."""
    artifact = verify_envelope(restored_envelope)
    if artifact.get("status") != "PASS":
        return {"status": "FAIL", "reason": "RESTORE_ARTIFACT_INVALID"}
    if artifact.get("semantic_hash") != str(expected_profile_semantic_hash):
        return {"status": "FAIL", "reason": "RESTORE_PROFILE_HASH_MISMATCH"}
    journal_check = journal.verify()
    if journal_check.get("status") != "PASS":
        return {"status": "FAIL", "reason": "RESTORE_JOURNAL_INVALID"}
    continuity = reconcile_state(snapshot, journal)
    if continuity.get("status") != "PASS":
        return {"status": "FAIL", "reason": "RESTORE_CONTINUITY_UNCERTAIN"}
    guard = restart_guard(snapshot)
    if guard.get("status") != "PASS":
        return {"status": "FAIL", "reason": "RESTORE_AUTHORITY_BOUNDARY_VIOLATION"}
    return {
        "status": "PASS", "reason": "RESTORE_ELIGIBLE_AFTER_REVALIDATION",
        "semantic_hash": artifact["semantic_hash"],
        "journal_chain_valid": True, "snapshot_reconciled": True,
        "authorization_created": False, "execution_performed": False,
        "p159_final_lock": False, "p160_opened": False,
    }


def _safe_archive_name(name: str) -> bool:
    raw = str(name).replace("\\", "/")
    p = Path(raw)
    return bool(raw) and not raw.startswith("/") and not p.is_absolute() and ".." not in p.parts


def _archive_existing_symlink_component(path: Path, stop: Path) -> bool:
    """Return True if an existing component from stop to path is a symlink."""
    stop = Path(stop)
    path = Path(path)
    try:
        rel = path.relative_to(stop)
    except ValueError:
        return True
    cur = stop
    if cur.is_symlink():
        return True
    for part in rel.parts:
        cur = cur / part
        if cur.exists() or cur.is_symlink():
            if cur.is_symlink():
                return True
    return False


def safe_extract_archive(
    archive_path: Path,
    destination: Path,
    *,
    filesystem_context,
) -> dict:
    """Validate the complete archive, then materialize it only through governed effects.

    The caller must preassemble exact single-use FS_CREATE_DIR and
    FS_WRITE_REPLACE_BYTES handles in slots ``archive_create_dir`` and
    ``archive_write_file``. This function never mints authority and has no
    ambient filesystem-write fallback.
    """
    import stat
    import tarfile
    import zipfile

    if filesystem_context is None:
        raise RuntimeError("governed_filesystem_context_required")
    if getattr(filesystem_context, "authority_minting", True) is not False:
        raise RuntimeError("governed_filesystem_context_must_be_non_minting")

    archive_path = Path(archive_path)
    destination = Path(destination)
    root = getattr(filesystem_context, "root_path", None)
    if root is None:
        raise RuntimeError("governed_filesystem_root_required")
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise RuntimeError("governed_filesystem_root_must_exist")

    # Resolve the destination parent, not the destination itself: a missing
    # destination must remain a governed CREATE_DIR effect.
    raw_destination = destination.expanduser()
    if not raw_destination.is_absolute():
        raw_destination = root / raw_destination
    if raw_destination.exists() or raw_destination.is_symlink():
        if raw_destination.is_symlink():
            return {"status": "FAIL", "reason": "ARCHIVE_DESTINATION_SYMLINK_REJECTED"}
        destination = raw_destination.resolve()
    else:
        parent = raw_destination.parent.resolve(strict=True)
        destination = parent / raw_destination.name
    try:
        destination.relative_to(root)
    except ValueError:
        return {"status": "FAIL", "reason": "ARCHIVE_DESTINATION_OUTSIDE_GOVERNED_ROOT"}
    if destination.exists() and not destination.is_dir():
        return {"status": "FAIL", "reason": "ARCHIVE_DESTINATION_NOT_DIRECTORY"}
    if _archive_existing_symlink_component(destination, root):
        return {"status": "FAIL", "reason": "ARCHIVE_DESTINATION_SYMLINK_REJECTED"}

    seen, folded = set(), set()
    entries = []

    def accept_name(name: str) -> str | None:
        raw = str(name).replace("\\", "/")
        is_dir_marker = raw.endswith("/")
        norm = raw.rstrip("/")
        if not _safe_archive_name(norm):
            return None
        if norm in seen or norm.casefold() in folded:
            return None
        seen.add(norm)
        folded.add(norm.casefold())
        return norm + ("/" if is_dir_marker else "")

    if zipfile.is_zipfile(str(archive_path)):
        with zipfile.ZipFile(str(archive_path), "r") as zf:
            infos = zf.infolist()
            for info in infos:
                accepted = accept_name(info.filename)
                if accepted is None:
                    return {"status": "FAIL", "reason": "ARCHIVE_MEMBER_PATH_UNSAFE"}
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode):
                    return {"status": "FAIL", "reason": "ARCHIVE_SYMLINK_REJECTED"}
                is_dir = info.is_dir() or accepted.endswith("/")
                entries.append(("dir" if is_dir else "file", accepted.rstrip("/"), None if is_dir else zf.read(info)))
    elif tarfile.is_tarfile(str(archive_path)):
        with tarfile.open(str(archive_path), "r:*") as tf:
            members = tf.getmembers()
            for member in members:
                accepted = accept_name(member.name + ("/" if member.isdir() and not member.name.endswith("/") else ""))
                if accepted is None:
                    return {"status": "FAIL", "reason": "ARCHIVE_MEMBER_PATH_UNSAFE"}
                if member.issym() or member.islnk():
                    return {"status": "FAIL", "reason": "ARCHIVE_SYMLINK_REJECTED"}
                if not (member.isfile() or member.isdir()):
                    return {"status": "FAIL", "reason": "ARCHIVE_MEMBER_TYPE_UNSAFE"}
                if member.isdir():
                    entries.append(("dir", accepted.rstrip("/"), None))
                else:
                    stream = tf.extractfile(member)
                    if stream is None:
                        return {"status": "FAIL", "reason": "ARCHIVE_MEMBER_READ_FAILED"}
                    entries.append(("file", accepted.rstrip("/"), stream.read()))
    else:
        return {"status": "FAIL", "reason": "ARCHIVE_FORMAT_UNSUPPORTED"}

    # Full validation is complete. Derive the exact causal effect set before
    # consuming any authority.
    required_dirs = {destination}
    file_entries = []
    for kind, name, payload in entries:
        target = destination / Path(name)
        try:
            target.relative_to(destination)
        except ValueError:
            return {"status": "FAIL", "reason": "ARCHIVE_MEMBER_PATH_UNSAFE"}
        if _archive_existing_symlink_component(target, root):
            return {"status": "FAIL", "reason": "ARCHIVE_DESTINATION_SYMLINK_REJECTED"}
        if kind == "dir":
            required_dirs.add(target)
        else:
            file_entries.append((target, payload))
            parent = target.parent
            while True:
                required_dirs.add(parent)
                if parent == destination:
                    break
                parent = parent.parent

    dirs_to_create = sorted(
        (p for p in required_dirs if not p.exists()),
        key=lambda p: (len(p.relative_to(root).parts), p.as_posix()),
    )
    for p in required_dirs:
        if p.exists() and not p.is_dir():
            return {"status": "FAIL", "reason": "ARCHIVE_DIRECTORY_COLLISION"}

    # Existing output symlinks/non-files are rejected before authority use.
    for path, _payload in file_entries:
        if path.is_symlink():
            return {"status": "FAIL", "reason": "ARCHIVE_DESTINATION_SYMLINK_REJECTED"}
        if path.exists() and not path.is_file():
            return {"status": "FAIL", "reason": "ARCHIVE_FILE_COLLISION"}

    remaining = filesystem_context.remaining()
    if remaining.get("archive_create_dir", 0) != len(dirs_to_create):
        raise RuntimeError("archive_create_dir_authority_cardinality_mismatch")
    if remaining.get("archive_write_file", 0) != len(file_entries):
        raise RuntimeError("archive_write_file_authority_cardinality_mismatch")

    filesystem_context.begin()
    for path in dirs_to_create:
        filesystem_context.execute_path("archive_create_dir", "FS_CREATE_DIR", path)
    for path, payload in file_entries:
        filesystem_context.execute_path("archive_write_file", "FS_WRITE_REPLACE_BYTES", path, payload)

    if any(filesystem_context.remaining().values()):
        raise RuntimeError("archive_filesystem_authority_not_fully_consumed")
    return {
        "status": "PASS",
        "reason": "ARCHIVE_EXTRACTED_SAFELY",
        "governed_create_dir_count": len(dirs_to_create),
        "governed_write_count": len(file_entries),
        "authority_minting": False,
        "ambient_fallback": False,
    }

