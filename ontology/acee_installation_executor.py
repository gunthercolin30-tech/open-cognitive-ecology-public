"""ACEE6-B1 — read-only admission of an ACEE5 installation manifest.

This first executable slice of ACEE6 validates an ACEE5 authorization envelope
and produces an admission decision. It performs no backup, write, compilation,
test execution, validation execution, installation, or rollback.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import tempfile
import shutil
import sys
import py_compile
import time
import unicodedata
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_INSTALLATION_EXECUTOR"
STAGE = "ACEE6-D2"
PUBLIC_SCHEMA_VERSION = "0.6.0"
DRY_RUN_STATUS = "ACEE6_INSTALLATION_DRY_RUN_READY"
ACCEPTED_ACEE5_SCHEMAS = frozenset({"1.2.0"})
STATUS_ADMISSIBLE = "ACEE6_INSTALLATION_PLAN_ADMISSIBLE"
STATUS_REJECTED = "ACEE6_INSTALLATION_PLAN_REJECTED"
MAX_MANIFEST_AGE_SECONDS = 24 * 60 * 60
MAX_FUTURE_SKEW_SECONDS = 300

FAULT_INJECTION_POINTS = frozenset({
    "backup",
    "write",
    "compile",
    "inventory",
    "tests",
    "validation.main",
    "report",
})
FAULT_INJECTION_STATUS = "ACEE6_G1_FAULT_INJECTION_TRIGGERED"


# ACEE6-J2-ESCALATION-CONSTANTS-BEGIN
J2_PUBLIC_SCHEMA_VERSION = "0.16.0"
J2_GATE_FILENAME = "installation_block_gate.json"
J2_DIAGNOSTIC_FILENAME = "escalation_diagnostic.json"
J2_BLOCKED_STATUS = "ACEE6_J2_INSTALLATION_BLOCKED"
J2_ESCALATED_STATUS = "ACEE6_J2_ESCALATION_COMPLETE"
J2_NOT_REQUIRED_STATUS = "ACEE6_J2_ESCALATION_NOT_REQUIRED"
# ACEE6-J2-ESCALATION-CONSTANTS-END
DEPENDENCIES = [
    "acee_governed_code_generation_gate",
    "constitutional_compliance_check",
    "controlled_execution_layer",
    "acee_rollback_engine",
]

REQUIRED_MANIFEST_FIELDS = (
    "public_schema_version",
    "decision_index",
    "proposal_id",
    "module_name",
    "target_path",
    "candidate_content_sha256",
    "backup_path",
    "backup_sha256",
    "refiner_path",
    "refiner_sha256",
    "test_paths",
    "rollback_executor",
    "inventory_targets",
    "validation_report_sha256",
    "manifest_hash",
)

REQUIRED_INVENTORY_TARGETS = frozenset({
    "dependency_registry.py",
    "ontology_inventory.txt",
    "ontology_inventory.py",
    "ontology/ontology_inventory.py",
    "global_module_catalog.txt",
})


def _json_safe(value: Any, depth: int = 0) -> Any:
    if depth > 64:
        return "<max-depth>"
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if value != value:
            return "<nan>"
        if value == float("inf"):
            return "<positive-infinity>"
        if value == float("-inf"):
            return "<negative-infinity>"
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item, depth + 1)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_json_safe(item, depth + 1) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_json_safe(item, depth + 1) for item in value), key=repr)
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    return {
        "unsupported_type": type(value).__name__,
        "repr": repr(value)[:512],
    }


def _canonical(value: Any) -> str:
    return json.dumps(
        _json_safe(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()



def _collision_key(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def _path_fingerprint(root: Path, relative: str) -> Dict[str, Any]:
    candidate = root / relative
    parent = candidate.parent
    result: Dict[str, Any] = {
        "relative_path": relative,
        "collision_key": _collision_key(relative),
        "root_realpath": str(root.resolve()),
        "path_revalidation_required": True,
        "hardlink_revalidation_required": True,
    }
    try:
        stat = parent.stat()
        result["parent_device"] = int(stat.st_dev)
        result["parent_inode"] = int(stat.st_ino)
    except OSError:
        result["parent_device"] = None
        result["parent_inode"] = None
    return result


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _valid_sha(value: Any) -> bool:
    text = str(value or "").lower()
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text)


def _file_sha(path: Path) -> Optional[str]:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _parse_time(value: Any) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


@dataclass
class AceeInstallationExecutor:
    # P162-G6 C02: consumes externally preissued single-use contexts; never mints authority.
    filesystem_effect_context_provider: Any = None

    def _take_filesystem_effect_context(self, operation_id: str, target: Path):
        provider = self.filesystem_effect_context_provider
        if provider is None or not callable(provider):
            raise RuntimeError("governed_filesystem_effect_context_provider_required")
        context = provider(operation_id, target)
        if context is None:
            raise RuntimeError("preissued_filesystem_effect_context_required")
        return context

    """Read-only ACEE6-B1 admission component."""

    root: Optional[Path] = None
    now_utc: Optional[datetime] = None

    def __post_init__(self) -> None:
        self.root = (
            Path(self.root)
            if self.root is not None
            else Path.home() / "open-cognitive-ecology"
        ).resolve()
        current = self.now_utc or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        self.now_utc = current.astimezone(timezone.utc)

    def _relative_path(self, value: Any) -> Tuple[Optional[str], Optional[str]]:
        text = str(value or "").strip()
        if not text:
            return None, "path_missing"
        raw = Path(text)
        candidate = raw if raw.is_absolute() else self.root / raw
        try:
            resolved_root = self.root.resolve(strict=True)
            resolved = candidate.resolve(strict=False)
            relative = resolved.relative_to(resolved_root)
        except (OSError, ValueError):
            return None, "path_outside_root"
        if any(part == ".." for part in relative.parts):
            return None, "path_traversal"
        return relative.as_posix(), None

    def _extract(self, inputs: Mapping[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if isinstance(inputs.get("acee5_decision"), Mapping):
            decision = _mapping(inputs.get("acee5_decision"))
            context = _mapping(inputs.get("admission_context"))
            return decision, context
        return dict(inputs), {}

    def _decision_hash_valid(self, decision: Mapping[str, Any]) -> bool:
        supplied = decision.get("result_hash")
        if not _valid_sha(supplied):
            return False
        return str(supplied).lower() == _sha(
            {key: value for key, value in decision.items() if key != "result_hash"}
        )

    def _build_dry_run_plan(
        self,
        normalized_plan: Mapping[str, Any],
    ) -> Dict[str, Any]:
        target_relative = str(normalized_plan.get("target_path") or "")
        target = self.root / target_relative
        target_exists = target.is_file()
        before_sha = _file_sha(target) if target_exists else None
        after_sha = str(
            normalized_plan.get("candidate_content_sha256") or ""
        ).lower()
        if not target_exists:
            operation = "create"
        elif before_sha == after_sha:
            operation = "unchanged"
        else:
            operation = "modify"

        candidate_change = {
            "target_path": target_relative,
            "operation": operation,
            "exists_before": target_exists,
            "before_sha256": before_sha,
            "after_sha256": after_sha,
            "content_diff_available": False,
            "diff_basis": "sha256_and_path_metadata",
        }

        inventory_impacts = []
        module_name = str(normalized_plan.get("module_name") or "")
        for relative in normalized_plan.get("inventory_targets", []):
            path = self.root / str(relative)
            current_sha = _file_sha(path) if path.is_file() else None
            contains_module = False
            if path.is_file() and module_name:
                try:
                    contains_module = module_name in path.read_text(
                        encoding="utf-8", errors="replace"
                    )
                except OSError:
                    contains_module = False
            inventory_impacts.append({
                "path": str(relative),
                "exists_before": path.is_file(),
                "before_sha256": current_sha,
                "module_reference_present": contains_module,
                "operation": "verify" if contains_module else "update",
            })

        test_plan = []
        for relative in normalized_plan.get("test_paths", []):
            path = self.root / str(relative)
            test_plan.append({
                "path": str(relative),
                "exists": path.is_file(),
                "sha256": _file_sha(path) if path.is_file() else None,
                "execution_order": len(test_plan),
            })

        rollback_actions = []
        if operation == "create":
            rollback_actions.append({
                "action": "remove_created_file",
                "path": target_relative,
            })
        elif operation == "modify":
            rollback_actions.append({
                "action": "restore_backup",
                "path": target_relative,
                "backup_path": normalized_plan.get("backup_path"),
                "expected_before_sha256": before_sha,
            })
        for impact in inventory_impacts:
            if impact["operation"] == "update":
                rollback_actions.append({
                    "action": "restore_inventory_snapshot",
                    "path": impact["path"],
                    "expected_before_sha256": impact["before_sha256"],
                })

        dry_run = {
            "proposal_id": normalized_plan.get("proposal_id"),
            "manifest_hash": normalized_plan.get("manifest_hash"),
            "candidate_change": candidate_change,
            "files_to_create": [target_relative] if operation == "create" else [],
            "files_to_modify": [target_relative] if operation == "modify" else [],
            "unchanged_files": [target_relative] if operation == "unchanged" else [],
            "inventory_impacts": inventory_impacts,
            "tests_to_execute": test_plan,
            "global_validation_command": "python3 -m validation.main",
            "rollback_plan": {
                "required": operation != "unchanged" or any(
                    item["operation"] == "update" for item in inventory_impacts
                ),
                "executor": "acee_rollback_engine",
                "actions": rollback_actions,
            },
            "summary": {
                "files_created": 1 if operation == "create" else 0,
                "files_modified": 1 if operation == "modify" else 0,
                "files_unchanged": 1 if operation == "unchanged" else 0,
                "inventories_impacted": sum(
                    1 for item in inventory_impacts
                    if item["operation"] == "update"
                ),
                "tests_planned": len(test_plan),
                "writes_performed": 0,
            },
            "read_only": True,
            "write_count": 0,
        }
        dry_run["plan_hash"] = _sha(dry_run)
        return dry_run

    def _admit_and_dry_run(
        self,
        inputs: Optional[Mapping[str, Any]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        original = deepcopy(inputs)
        supplied = dict(inputs) if isinstance(inputs, Mapping) else {}
        decision, context = self._extract(supplied)
        blocking = []

        if persist:
            blocking.append("persistence_not_available_b1")
        if not decision:
            blocking.append("acee5_decision_missing")
        if decision.get("primitive") != "ACEE_GOVERNED_CODE_GENERATION_GATE":
            blocking.append("acee5_primitive_invalid")
        if decision.get("status") != "ACEE_CODE_GENERATION_GOVERNED":
            blocking.append("acee5_status_not_governed")
        if decision.get("installation_authorized") is not True:
            blocking.append("acee5_installation_not_authorized")
        if not self._decision_hash_valid(decision):
            blocking.append("acee5_result_hash_invalid")

        manifest = _mapping(decision.get("installation_manifest"))
        if not manifest:
            blocking.append("installation_manifest_missing")

        missing = [
            field
            for field in REQUIRED_MANIFEST_FIELDS
            if field not in manifest
        ]
        blocking.extend("manifest_field_missing:" + field for field in missing)

        schema = str(manifest.get("public_schema_version") or "")
        if schema not in ACCEPTED_ACEE5_SCHEMAS:
            blocking.append("manifest_schema_unsupported")

        supplied_manifest_hash = str(manifest.get("manifest_hash") or "").lower()
        recomputed_manifest_hash = _sha(
            {
                key: value
                for key, value in manifest.items()
                if key != "manifest_hash"
            }
        )
        if not _valid_sha(supplied_manifest_hash):
            blocking.append("manifest_hash_invalid")
        elif supplied_manifest_hash != recomputed_manifest_hash:
            blocking.append("manifest_hash_mismatch")

        proposal_id = str(manifest.get("proposal_id") or "").strip()
        module_name = str(manifest.get("module_name") or "").strip()
        if not proposal_id:
            blocking.append("proposal_id_missing")
        if not module_name:
            blocking.append("module_name_missing")
        if not isinstance(manifest.get("decision_index"), int) or isinstance(
            manifest.get("decision_index"), bool
        ) or manifest.get("decision_index", -1) < 0:
            blocking.append("decision_index_invalid")

        for field in (
            "candidate_content_sha256",
            "backup_sha256",
            "refiner_sha256",
            "validation_report_sha256",
        ):
            if not _valid_sha(manifest.get(field)):
                blocking.append(field + "_invalid")

        normalized = {}
        for label in ("target_path", "backup_path", "refiner_path"):
            value, error = self._relative_path(manifest.get(label))
            if error:
                blocking.append(label + "_" + error)
            normalized[label] = value

        target = normalized.get("target_path")
        if target and not target.startswith("ontology/"):
            blocking.append("target_not_in_ontology")

        test_paths = manifest.get("test_paths")
        normalized_tests = []
        if not isinstance(test_paths, list) or not test_paths:
            blocking.append("test_paths_invalid")
        else:
            if len(test_paths) != len({str(item) for item in test_paths}):
                blocking.append("test_paths_duplicate")
            for item in test_paths:
                path, error = self._relative_path(item)
                if error or not path or not path.endswith(".py"):
                    blocking.append("test_path_invalid")
                else:
                    normalized_tests.append(path)

        inventory_targets = manifest.get("inventory_targets")
        if not isinstance(inventory_targets, list):
            blocking.append("inventory_targets_invalid")
            inventory_set = set()
        else:
            inventory_values = [str(item) for item in inventory_targets]
            if len(inventory_values) != len(set(inventory_values)):
                blocking.append("inventory_targets_duplicate")
            inventory_set = set(inventory_values)
            if not REQUIRED_INVENTORY_TARGETS.issubset(inventory_set):
                blocking.append("inventory_targets_incomplete")

        if manifest.get("rollback_executor") != "acee_rollback_engine":
            blocking.append("rollback_executor_invalid")

        all_paths = [
            item for item in (
                normalized.get("target_path"),
                normalized.get("backup_path"),
                normalized.get("refiner_path"),
                *normalized_tests,
            )
            if item
        ]
        collision_keys = [_collision_key(item) for item in all_paths]
        if len(collision_keys) != len(set(collision_keys)):
            blocking.append("path_collision")

        envelope_proposal = str(decision.get("proposal_id") or "").strip()
        if envelope_proposal != proposal_id:
            blocking.append("proposal_id_envelope_mismatch")
        if decision.get("decision_index") != manifest.get("decision_index"):
            blocking.append("decision_index_envelope_mismatch")
        if decision.get("public_schema_version") != schema:
            blocking.append("schema_envelope_mismatch")

        timestamp = _parse_time(decision.get("timestamp_utc"))
        if timestamp is None:
            blocking.append("decision_timestamp_invalid")
        else:
            age = (self.now_utc - timestamp).total_seconds()
            if age > MAX_MANIFEST_AGE_SECONDS:
                blocking.append("manifest_stale")
            if age < -MAX_FUTURE_SKEW_SECONDS:
                blocking.append("manifest_timestamp_in_future")

        consumed = context.get("consumed_manifest_hashes", ())
        if isinstance(consumed, (list, tuple, set, frozenset)):
            if supplied_manifest_hash in {str(item).lower() for item in consumed}:
                blocking.append("manifest_replay_detected")
        elif consumed:
            blocking.append("consumed_manifest_hashes_invalid")

        bindings = context.get("proposal_bindings", {})
        if isinstance(bindings, Mapping):
            old = bindings.get(proposal_id)
            if old and str(old).lower() != str(
                manifest.get("candidate_content_sha256") or ""
            ).lower():
                blocking.append("proposal_id_collision")
        elif bindings:
            blocking.append("proposal_bindings_invalid")

        blocking = sorted(set(blocking))
        admissible = not blocking
        normalized_plan = {
            "proposal_id": proposal_id,
            "decision_index": manifest.get("decision_index"),
            "module_name": module_name,
            "target_path": normalized.get("target_path"),
            "backup_path": normalized.get("backup_path"),
            "refiner_path": normalized.get("refiner_path"),
            "test_paths": sorted(set(normalized_tests)),
            "inventory_targets": sorted(inventory_set),
            "candidate_content_sha256": str(
                manifest.get("candidate_content_sha256") or ""
            ).lower(),
            "manifest_hash": supplied_manifest_hash,
            "root_realpath": str(self.root.resolve()),
            "path_revalidation_required": True,
            "hardlink_revalidation_required": True,
            "path_fingerprints": {
                label: _path_fingerprint(self.root, value)
                for label, value in normalized.items()
                if value
            },
        }
        dry_run_plan = (
            self._build_dry_run_plan(normalized_plan) if admissible else None
        )
        result = {
            "primitive": PRIMITIVE,
            "stage": STAGE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "status": STATUS_ADMISSIBLE if admissible else STATUS_REJECTED,
            "admissible": admissible,
            "proposal_id": proposal_id,
            "manifest_hash": supplied_manifest_hash,
            "blocking_reasons": blocking,
            "normalized_plan": normalized_plan if admissible else None,
            "dry_run_status": DRY_RUN_STATUS if admissible else None,
            "dry_run": admissible,
            "dry_run_plan": dry_run_plan,
            "write_count": 0,
            "read_only": True,
            "backup_created": False,
            "candidate_written": False,
            "candidate_compiled": False,
            "tests_executed": False,
            "global_validation_executed": False,
            "rollback_executed": False,
            "inventory_modified": False,
            "persistence_performed": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        result["evidence_hash"] = _sha({
            "decision": decision,
            "admission_context": context,
            "normalized_plan": normalized_plan,
            "dry_run_plan": dry_run_plan,
            "blocking_reasons": blocking,
        })
        result["result_hash"] = _sha({
            key: value for key, value in result.items() if key != "result_hash"
        })

        # Input immutability is verified by dedicated tests for supported mappings.
        return result

    def _transaction_runtime_root(self) -> Path:
        return self.root / "acee6_transactions"

    def _fsync_directory(self, path: Path) -> bool:
        try:
            descriptor = os.open(str(path), os.O_RDONLY)
        except OSError:
            return False
        try:
            os.fsync(descriptor)
            return True
        except OSError:
            return False
        finally:
            os.close(descriptor)

    def _atomic_json_write(self, path: Path, payload: Mapping[str, Any]) -> None:
        data = (json.dumps(_json_safe(payload), sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        if not path.parent.exists():
            create_context = self._take_filesystem_effect_context("FS_CREATE_DIR", path.parent)
            create_context.begin()
            create_context.execute_path("p162g6_c02_parent_create", "FS_CREATE_DIR", path.parent)
        write_context = self._take_filesystem_effect_context("FS_WRITE_REPLACE_BYTES", path)
        write_context.begin()
        write_context.execute_path("p162g6_c02_write_replace", "FS_WRITE_REPLACE_BYTES", path, data)


    def _transaction_id(self, result: Mapping[str, Any]) -> str:
        material = {
            "stage": "ACEE6-C",
            "proposal_id": result.get("proposal_id"),
            "manifest_hash": result.get("manifest_hash"),
        }
        return "acee6c-" + _sha(material)[:32]

    def _snapshot_entry(self, relative: str) -> Dict[str, Any]:
        path = self.root / relative
        exists = path.exists()
        try:
            stat = path.stat() if exists else None
        except OSError:
            stat = None
        return {
            "relative_path": relative,
            "exists": exists,
            "is_file": path.is_file(),
            "is_symlink": path.is_symlink(),
            "sha256": _file_sha(path) if path.is_file() else None,
            "mode": int(stat.st_mode) if stat is not None else None,
            "size": int(stat.st_size) if stat is not None else None,
            "device": int(stat.st_dev) if stat is not None else None,
            "inode": int(stat.st_ino) if stat is not None else None,
        }

    def _build_snapshot(self, result: Mapping[str, Any]) -> Dict[str, Any]:
        plan = _mapping(result.get("normalized_plan"))
        paths = [plan.get("target_path"), plan.get("backup_path"), plan.get("refiner_path"), *list(plan.get("test_paths") or ()), *list(plan.get("inventory_targets") or ())]
        unique = sorted({str(path) for path in paths if isinstance(path, str) and path})
        snapshot = {
            "transaction_contract": "ACEE6-C",
            "root_realpath": str(self.root.resolve()),
            "proposal_id": result.get("proposal_id"),
            "manifest_hash": result.get("manifest_hash"),
            "plan_hash": _mapping(result.get("dry_run_plan")).get("plan_hash"),
            "entries": [self._snapshot_entry(path) for path in unique],
        }
        snapshot["snapshot_hash"] = _sha(snapshot)
        return snapshot

    def _append_journal_record(self, journal: Path, payload: Mapping[str, Any], previous_hash: Optional[str]) -> str:
        record = {**dict(payload), "previous_record_hash": previous_hash}
        record["record_hash"] = _sha(record)
        with journal.open("a", encoding="utf-8") as stream:
            stream.write(_canonical(record) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        self._fsync_directory(journal.parent)
        return str(record["record_hash"])


    def _append_journal_record_governed(self, journal: Path, payload: Mapping[str, Any], previous_hash: Optional[str]) -> str:
        record={**dict(payload), "previous_record_hash":previous_hash}; record["record_hash"]=_sha(record)
        if not journal.parent.exists():
            context=self._take_filesystem_effect_context("FS_CREATE_DIR", journal.parent); context.begin()
            context.execute_path("p162g6_index2_journal_parent_create", "FS_CREATE_DIR", journal.parent)
        context=self._take_filesystem_effect_context("FS_APPEND_BYTES", journal); context.begin()
        context.execute_path("p162g6_index2_journal_append", "FS_APPEND_BYTES", journal, (_canonical(record)+"\n").encode("utf-8"))
        return str(record["record_hash"])

    def _validate_existing_journal(
        self,
        journal_path: Path,
        latest_state: Mapping[str, Any],
    ) -> Tuple[bool, list[str]]:
        if not journal_path.is_file():
            return False, ["existing_transaction_journal_missing"]
        try:
            raw_lines = journal_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return False, ["existing_transaction_journal_unreadable"]
        if not raw_lines:
            return False, ["existing_transaction_journal_empty"]

        previous_hash: Optional[str] = None
        records = []
        for raw_line in raw_lines:
            if not raw_line.strip():
                return False, ["existing_transaction_journal_corrupted"]
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                return False, ["existing_transaction_journal_corrupted"]
            if not isinstance(record, Mapping):
                return False, ["existing_transaction_journal_corrupted"]
            supplied_hash = record.get("record_hash")
            if not _valid_sha(supplied_hash):
                return False, ["existing_transaction_journal_hash_invalid"]
            payload = {k: v for k, v in record.items() if k != "record_hash"}
            if str(supplied_hash).lower() != _sha(payload):
                return False, ["existing_transaction_journal_hash_mismatch"]
            if record.get("previous_record_hash") != previous_hash:
                return False, ["existing_transaction_journal_chain_divergence"]
            previous_hash = str(supplied_hash).lower()
            records.append(dict(record))

        if [item.get("state") for item in records] != ["PREPARING", "PREPARED"]:
            return False, ["existing_transaction_journal_state_divergence"]
        if latest_state.get("latest_record_hash") != previous_hash:
            return False, ["existing_transaction_latest_record_divergence"]
        for record in records:
            checks = (
                ("transaction_id", "existing_transaction_journal_id_divergence"),
                ("proposal_id", "existing_transaction_journal_proposal_divergence"),
                ("manifest_hash", "existing_transaction_journal_manifest_divergence"),
                ("plan_hash", "existing_transaction_journal_plan_divergence"),
                ("snapshot_hash", "existing_transaction_journal_snapshot_divergence"),
            )
            for key, reason in checks:
                if record.get(key) != latest_state.get(key):
                    return False, [reason]
        return True, []

    def _validate_existing_snapshot(
        self,
        snapshot_path: Path,
        expected_snapshot: Mapping[str, Any],
    ) -> Tuple[bool, list[str]]:
        if not snapshot_path.is_file():
            return False, ["existing_transaction_snapshot_missing"]
        try:
            stored = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False, ["existing_transaction_snapshot_corrupted"]
        if not isinstance(stored, Mapping):
            return False, ["existing_transaction_snapshot_corrupted"]
        supplied_hash = stored.get("snapshot_hash")
        if not _valid_sha(supplied_hash):
            return False, ["existing_transaction_snapshot_hash_invalid"]
        payload = {k: v for k, v in stored.items() if k != "snapshot_hash"}
        if str(supplied_hash).lower() != _sha(payload):
            return False, ["existing_transaction_snapshot_hash_mismatch"]
        if supplied_hash != expected_snapshot.get("snapshot_hash"):
            return False, ["existing_transaction_snapshot_divergence"]
        if _canonical(stored) != _canonical(expected_snapshot):
            return False, ["existing_transaction_snapshot_divergence"]
        return True, []


    def _existing_preparation(
        self,
        latest_path: Path,
        journal_path: Path,
        snapshot_path: Path,
        expected_transaction_id: str,
        expected_plan_hash: str,
        expected_snapshot: Mapping[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if not latest_path.exists():
            return None
        try:
            existing = json.loads(latest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"corrupted": True, "blocking_reasons": ["existing_transaction_state_corrupted"]}
        if not isinstance(existing, Mapping):
            return {"corrupted": True, "blocking_reasons": ["existing_transaction_state_corrupted"]}

        reasons = []
        if existing.get("transaction_state") != "PREPARED":
            reasons.append("existing_transaction_state_not_prepared")
        if existing.get("transaction_id") != expected_transaction_id:
            reasons.append("existing_transaction_id_divergence")
        if existing.get("plan_hash") != expected_plan_hash:
            reasons.append("existing_transaction_plan_divergence")
        if existing.get("snapshot_hash") != expected_snapshot.get("snapshot_hash"):
            reasons.append("existing_transaction_snapshot_divergence")

        state_hash = existing.get("state_hash")
        state_payload = {k: v for k, v in existing.items() if k != "state_hash"}
        if not _valid_sha(state_hash):
            reasons.append("existing_transaction_state_hash_invalid")
        elif str(state_hash).lower() != _sha(state_payload):
            reasons.append("existing_transaction_state_hash_mismatch")

        snapshot_valid, snapshot_reasons = self._validate_existing_snapshot(
            snapshot_path,
            expected_snapshot,
        )
        if not snapshot_valid:
            reasons.extend(snapshot_reasons)

        journal_valid, journal_reasons = self._validate_existing_journal(
            journal_path,
            existing,
        )
        if not journal_valid:
            reasons.extend(journal_reasons)

        if reasons:
            return {"corrupted": True, "blocking_reasons": sorted(set(reasons))}
        return dict(existing)

    def _prepare_transaction(self, admitted: Mapping[str, Any]) -> Dict[str, Any]:
        transaction_id = self._transaction_id(admitted)
        replay_integrity_contract = "ACEE6-C-REPLAY-INTEGRITY"
        runtime_root = self._transaction_runtime_root()
        transaction_dir = runtime_root / transaction_id
        journal = transaction_dir / "journal.jsonl"
        latest = transaction_dir / "latest_state.json"
        snapshot_path = transaction_dir / "snapshot.json"
        lock_path = runtime_root / ".prepare.lock"
        runtime_root.mkdir(parents=True, exist_ok=True)
        runtime_root_synced = self._fsync_directory(runtime_root)
        snapshot = self._build_snapshot(admitted)
        snapshot_hash = str(snapshot["snapshot_hash"])
        plan_hash = str(_mapping(admitted.get("dry_run_plan")).get("plan_hash") or "")
        lock_handle = lock_path.open("a+", encoding="utf-8")
        try:
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                blocked = dict(admitted)
                blocked.update({
                    "stage": "ACEE6-C", "public_schema_version": "0.4.0",
                    "status": "ACEE6_TRANSACTION_PREPARATION_BLOCKED", "transaction_state": "ADMISSIBLE",
                    "transaction_id": transaction_id, "transaction_prepared": False,
                    "preparation_replayed": False, "journal_persisted": False, "journal_fsynced": False,
                    "directory_fsynced": runtime_root_synced, "lock_acquired": False, "lock_released": False,
                    "snapshot_hashes_recorded": False,
                    "blocking_reasons": sorted(set(list(admitted.get("blocking_reasons") or ()) + ["transaction_prepare_lock_busy"])),
                    "persistence_performed": False,
                })
                blocked["result_hash"] = _sha({k: v for k, v in blocked.items() if k != "result_hash"})
                return blocked
            transaction_dir.mkdir(parents=True, exist_ok=True)
            transaction_dir_synced = self._fsync_directory(transaction_dir)
            existing = self._existing_preparation(
                latest,
                journal,
                snapshot_path,
                transaction_id,
                plan_hash,
                snapshot,
            )
            if existing is not None:
                if existing.get("corrupted"):
                    rejected = dict(admitted)
                    rejected.update({
                        "stage": "ACEE6-C", "public_schema_version": "0.4.0",
                        "status": "ACEE6_TRANSACTION_PREPARATION_REJECTED", "transaction_state": "STATE_CORRUPTED",
                        "transaction_id": transaction_id, "transaction_prepared": False, "preparation_replayed": False,
                        "journal_persisted": journal.is_file(), "journal_fsynced": False,
                        "directory_fsynced": transaction_dir_synced, "lock_acquired": True, "lock_released": False,
                        "snapshot_hashes_recorded": snapshot_path.is_file(), "snapshot_hash": snapshot_hash,
                        "blocking_reasons": sorted(set(list(admitted.get("blocking_reasons") or ()) + list(existing.get("blocking_reasons") or ()))),
                        "persistence_performed": False,
                    })
                    rejected["result_hash"] = _sha({k: v for k, v in rejected.items() if k != "result_hash"})
                    return rejected
                replayed = dict(admitted)
                replayed.update({
                    "stage": "ACEE6-C", "public_schema_version": "0.4.0", "status": "ACEE6_TRANSACTION_PREPARED",
                    "transaction_state": "PREPARED", "transaction_id": transaction_id, "transaction_prepared": True,
                    "preparation_replayed": True, "transaction_directory": str(transaction_dir),
                    "journal_path": str(journal), "latest_state_path": str(latest), "snapshot_path": str(snapshot_path),
                    "snapshot_hash": snapshot_hash, "journal_persisted": journal.is_file(), "journal_fsynced": True,
                    "directory_fsynced": transaction_dir_synced, "lock_acquired": True, "lock_released": False,
                    "snapshot_hashes_recorded": snapshot_path.is_file(), "persistence_performed": True,
                })
                replayed["result_hash"] = _sha({k: v for k, v in replayed.items() if k != "result_hash"})
                return replayed
            self._atomic_json_write(snapshot_path, snapshot)
            preparing = {"transaction_id": transaction_id, "proposal_id": admitted.get("proposal_id"), "manifest_hash": admitted.get("manifest_hash"), "plan_hash": plan_hash, "snapshot_hash": snapshot_hash, "state": "PREPARING", "timestamp_utc": self.now_utc.isoformat()}
            first_hash = self._append_journal_record(journal, preparing, None)
            prepared_record = {**preparing, "state": "PREPARED", "timestamp_utc": self.now_utc.isoformat()}
            second_hash = self._append_journal_record(journal, prepared_record, first_hash)
            latest_payload = {
                "primitive": PRIMITIVE, "stage": "ACEE6-C", "public_schema_version": "0.4.0",
                "status": "ACEE6_TRANSACTION_PREPARED", "transaction_state": "PREPARED",
                "transaction_id": transaction_id, "proposal_id": admitted.get("proposal_id"),
                "manifest_hash": admitted.get("manifest_hash"), "plan_hash": plan_hash,
                "snapshot_hash": snapshot_hash, "latest_record_hash": second_hash,
                "candidate_written": False, "backup_created": False, "inventory_modified": False,
                "tests_executed": False, "global_validation_executed": False,
                "timestamp_utc": self.now_utc.isoformat(),
            }
            latest_payload["state_hash"] = _sha(latest_payload)
            self._atomic_json_write(latest, latest_payload)
            prepared = dict(admitted)
            prepared.update({
                "stage": "ACEE6-C", "public_schema_version": "0.4.0", "status": "ACEE6_TRANSACTION_PREPARED",
                "transaction_state": "PREPARED", "transaction_id": transaction_id, "transaction_prepared": True,
                "preparation_replayed": False, "transaction_directory": str(transaction_dir),
                "journal_path": str(journal), "latest_state_path": str(latest), "snapshot_path": str(snapshot_path),
                "snapshot_hash": snapshot_hash, "journal_persisted": True, "journal_fsynced": True,
                "directory_fsynced": runtime_root_synced and transaction_dir_synced and self._fsync_directory(transaction_dir),
                "lock_acquired": True, "lock_released": False, "snapshot_hashes_recorded": True,
                "persistence_performed": True, "write_count": 3, "read_only": False,
                "backup_created": False, "candidate_written": False, "candidate_compiled": False,
                "tests_executed": False, "global_validation_executed": False,
                "rollback_executed": False, "inventory_modified": False,
            })
            prepared["result_hash"] = _sha({k: v for k, v in prepared.items() if k != "result_hash"})
            return prepared
        finally:
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            lock_handle.close()


    def _g2_rollback_fault(
        self,
        failure: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Execute and independently verify ACEE6-G2 rollback.

        Existing files are restored through ACEE11. Files proven absent in the
        ACEE6-C snapshot are removed directly. Inventory snapshots are restored
        byte-for-byte. Any missing or divergent proof yields QUARANTINE.
        """
        from ontology.acee_rollback_engine import AceeRollbackEngine

        result = dict(failure)
        transaction_id = str(result.get("transaction_id") or "")
        if not transaction_id:
            result.update({
                "stage": "ACEE6-G2",
                "public_schema_version": "0.12.0",
                "status": "ACEE6_ROLLBACK_QUARANTINED",
                "transaction_state": "QUARANTINE",
                "rollback_executed": False,
                "rollback_verified": False,
                "quarantined": True,
                "blocking_reasons": ["transaction_id_missing"],
                "committed": False,
                "partial_success": False,
            })
            result.pop("result_hash", None)
            result["result_hash"] = _sha(result)
            return result

        transaction_dir = self._transaction_runtime_root() / transaction_id
        journal_path = transaction_dir / "journal.jsonl"
        latest_path = transaction_dir / "latest_state.json"
        latest = self._load_json_mapping(latest_path) or {}
        previous_hash = latest.get("latest_record_hash")

        rolling_hash = self._append_journal_record(
            journal_path,
            {
                "transaction_id": transaction_id,
                "proposal_id": result.get("proposal_id"),
                "state": "ROLLING_BACK",
                "reason": "fault_injection",
                "fault_point": result.get("fault_point"),
                "timestamp_utc": self.now_utc.isoformat(),
            },
            str(previous_hash) if previous_hash else None,
        )

        reasons: list[str] = []
        inventory_restored = True
        target_restored = False
        target_action = "unknown"
        acee11_result: Dict[str, Any] = {}

        inventory_snapshot_path = self._inventory_snapshot_manifest_path(
            transaction_dir
        )
        inventory_snapshot = self._load_json_mapping(inventory_snapshot_path)
        if isinstance(inventory_snapshot, Mapping):
            for item in inventory_snapshot.get("files", []):
                record = _mapping(item)
                relative = str(record.get("path") or "")
                path = self.root / relative
                try:
                    if record.get("existed_before") is True:
                        expected_hex = str(record.get("before_hex") or "")
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(bytes.fromhex(expected_hex))
                        self._fsync_directory(path.parent)
                        expected_hash = record.get("before_sha256")
                        if expected_hash and _file_sha(path) != expected_hash:
                            reasons.append(
                                f"inventory_hash_mismatch:{relative}"
                            )
                            inventory_restored = False
                    elif path.exists() or path.is_symlink():
                        path.unlink()
                        self._fsync_directory(path.parent)
                        if path.exists() or path.is_symlink():
                            reasons.append(
                                f"inventory_created_file_not_removed:{relative}"
                            )
                            inventory_restored = False
                except (OSError, ValueError) as exc:
                    inventory_restored = False
                    reasons.append(
                        f"inventory_restore_failed:{relative}:{type(exc).__name__}"
                    )
        else:
            # Before ACEE6-E, no inventory mutation has happened.
            inventory_restored = result.get("inventory_modified") is not True
            if not inventory_restored:
                reasons.append("inventory_snapshot_missing_after_mutation")

        backup = self._load_json_mapping(
            self._backup_manifest_path(transaction_dir)
        )
        snapshot = self._load_json_mapping(transaction_dir / "snapshot.json")
        if not isinstance(backup, Mapping):
            reasons.append("backup_manifest_missing")
        if not isinstance(snapshot, Mapping):
            reasons.append("transaction_snapshot_missing")

        plan = _mapping(result.get("normalized_plan"))
        relative = str(
            _mapping(backup).get("target_path")
            or plan.get("target_path")
            or ""
        )
        target = self.root / relative if relative else self.root

        if isinstance(backup, Mapping) and relative:
            if backup.get("target_existed_before") is True:
                target_action = "restore_from_backup_via_acee11"
                acee11_result = AceeRollbackEngine(root=self.root).step(
                    inputs={
                        "rollback_request": {
                            "transaction_id": transaction_id,
                            "reason": "validation_failure",
                            "targets": [
                                {
                                    "destination": relative,
                                    "backup_path": str(
                                        backup.get("backup_path") or ""
                                    ),
                                    "expected_backup_sha256": backup.get(
                                        "backup_sha256"
                                    ),
                                }
                            ],
                        },
                        "governance_authorization": {
                            "decision": "approved"
                        },
                        "constitutional_authorization": {
                            "decision": "approved"
                        },
                        "dry_run": False,
                        "execute": True,
                        "timestamp_utc": self.now_utc.isoformat(),
                    },
                    persist=True,
                )
                target_restored = (
                    acee11_result.get("rollback_performed") is True
                )
                expected_before = backup.get("target_sha256_before")
                if target_restored and expected_before:
                    target_restored = (
                        target.is_file()
                        and _file_sha(target) == expected_before
                    )
                if not target_restored:
                    reasons.append("target_restore_not_verified")
            else:
                target_action = "remove_created_file"
                try:
                    if target.exists() or target.is_symlink():
                        target.unlink()
                        self._fsync_directory(target.parent)
                    target_restored = not target.exists() and not target.is_symlink()
                except OSError as exc:
                    reasons.append(
                        f"created_target_removal_failed:{type(exc).__name__}"
                    )
                    target_restored = False
                if not target_restored:
                    reasons.append("created_target_absence_not_verified")
        else:
            reasons.append("target_rollback_contract_missing")

        rollback_verified = inventory_restored and target_restored and not reasons
        state = "ROLLED_BACK" if rollback_verified else "QUARANTINE"
        status = (
            "ACEE6_ROLLBACK_COMPLETE"
            if rollback_verified
            else "ACEE6_ROLLBACK_QUARANTINED"
        )

        report = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-G2",
            "public_schema_version": "0.12.0",
            "transaction_id": transaction_id,
            "proposal_id": result.get("proposal_id"),
            "fault_point": result.get("fault_point"),
            "rollback_state": state,
            "rollback_verified": rollback_verified,
            "inventory_restored": inventory_restored,
            "target_restored": target_restored,
            "target_action": target_action,
            "blocking_reasons": sorted(set(reasons)),
            "timestamp_utc": self.now_utc.isoformat(),
        }
        report["rollback_report_hash"] = _sha(report)
        report_path = transaction_dir / "rollback_report.json"
        self._atomic_json_write(report_path, report)

        final_hash = self._append_journal_record(
            journal_path,
            {
                "transaction_id": transaction_id,
                "proposal_id": result.get("proposal_id"),
                "state": state,
                "fault_point": result.get("fault_point"),
                "rollback_verified": rollback_verified,
                "inventory_restored": inventory_restored,
                "target_restored": target_restored,
                "rollback_report_hash": report["rollback_report_hash"],
                "timestamp_utc": self.now_utc.isoformat(),
            },
            rolling_hash,
        )

        latest.update({
            "primitive": PRIMITIVE,
            "stage": "ACEE6-G2",
            "public_schema_version": "0.12.0",
            "status": status,
            "transaction_state": state,
            "latest_record_hash": final_hash,
            "rollback_required": True,
            "rollback_executed": rollback_verified,
            "rollback_verified": rollback_verified,
            "inventory_restored": inventory_restored,
            "target_restored": target_restored,
            "target_rollback_action": target_action,
            "rollback_report_hash": report["rollback_report_hash"],
            "quarantined": not rollback_verified,
            "retry_allowed": False,
            "partial_success": False,
            "committed": False,
            "timestamp_utc": self.now_utc.isoformat(),
        })
        latest.pop("state_hash", None)
        latest["state_hash"] = _sha(latest)
        self._atomic_json_write(latest_path, latest)

        result.update(latest)
        result["rollback_report_path"] = str(report_path)
        result["rollback_result"] = acee11_result
        result["blocking_reasons"] = sorted(set(reasons))
        result.pop("result_hash", None)
        result["result_hash"] = _sha(result)
        return result

    def _fault_injection_boundary(
        self,
        result: Mapping[str, Any],
        inputs: Optional[Mapping[str, Any]],
        boundary: str,
    ) -> Dict[str, Any]:
        """Inject one explicit, deterministic G1 failure at a completed boundary.

        The feature is inert unless ``admission_context.fault_injection`` is a
        mapping containing ``enabled=True``, one canonical point and
        ``occurrence=1``. G1 records the failure and requires rollback, but does
        not execute rollback; that responsibility belongs to ACEE6-G2/ACEE11.
        """
        unchanged = dict(result)
        if not isinstance(inputs, Mapping):
            return unchanged
        context = _mapping(inputs.get("admission_context"))
        config = context.get("fault_injection")
        if not isinstance(config, Mapping):
            return unchanged
        if config.get("enabled") is not True:
            return unchanged
        point = config.get("point")
        occurrence = config.get("occurrence", 1)
        if not isinstance(point, str) or point not in FAULT_INJECTION_POINTS:
            return unchanged
        if isinstance(occurrence, bool) or occurrence != 1:
            return unchanged
        if point != boundary:
            return unchanged

        transaction_id = str(result.get("transaction_id") or "")
        failure = dict(result)
        failure.update({
            "primitive": PRIMITIVE,
            "stage": "ACEE6-G1",
            "public_schema_version": "0.11.0",
            "status": FAULT_INJECTION_STATUS,
            "transaction_state": "FAULT_INJECTED",
            "installation_completed": False,
            "fault_injection_enabled": True,
            "fault_point": point,
            "fault_triggered": True,
            "fault_occurrence": 1,
            "failure_classification": "INJECTED_TRANSACTIONAL_FAILURE",
            "mutation_started": True,
            "rollback_required": True,
            "rollback_executed": False,
            "retry_allowed": False,
            "partial_success": False,
            "committed": False,
            "quarantined": False,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "timestamp_utc": self.now_utc.isoformat(),
        })
        failure.pop("result_hash", None)

        if transaction_id:
            transaction_dir = self._transaction_runtime_root() / transaction_id
            if transaction_dir.is_dir():
                report = {
                    "primitive": PRIMITIVE,
                    "stage": "ACEE6-G1",
                    "public_schema_version": "0.11.0",
                    "transaction_id": transaction_id,
                    "proposal_id": result.get("proposal_id"),
                    "fault_point": point,
                    "fault_occurrence": 1,
                    "fault_triggered": True,
                    "failure_classification": "INJECTED_TRANSACTIONAL_FAILURE",
                    "rollback_required": True,
                    "rollback_executed": False,
                    "retry_allowed": False,
                    "partial_success": False,
                    "timestamp_utc": self.now_utc.isoformat(),
                }
                report["fault_injection_report_hash"] = _sha(report)
                report_path = transaction_dir / "fault_injection_report.json"
                self._atomic_json_write(report_path, report)

                latest_path = transaction_dir / "latest_state.json"
                latest = self._load_json_mapping(latest_path) or {}
                previous_hash = latest.get("latest_record_hash")
                journal_path = transaction_dir / "journal.jsonl"
                record_hash = self._append_journal_record(
                    journal_path,
                    {
                        "transaction_id": transaction_id,
                        "proposal_id": result.get("proposal_id"),
                        "state": "FAULT_INJECTED",
                        "fault_point": point,
                        "fault_injection_report_hash": report[
                            "fault_injection_report_hash"
                        ],
                        "rollback_required": True,
                        "retry_allowed": False,
                        "timestamp_utc": self.now_utc.isoformat(),
                    },
                    str(previous_hash) if previous_hash else None,
                )
                latest.update({
                    "primitive": PRIMITIVE,
                    "stage": "ACEE6-G1",
                    "public_schema_version": "0.11.0",
                    "status": FAULT_INJECTION_STATUS,
                    "transaction_state": "FAULT_INJECTED",
                    "latest_record_hash": record_hash,
                    "fault_point": point,
                    "fault_triggered": True,
                    "fault_injection_report_hash": report[
                        "fault_injection_report_hash"
                    ],
                    "rollback_required": True,
                    "rollback_executed": False,
                    "retry_allowed": False,
                    "partial_success": False,
                    "committed": False,
                    "timestamp_utc": self.now_utc.isoformat(),
                })
                latest.pop("state_hash", None)
                latest["state_hash"] = _sha(latest)
                self._atomic_json_write(latest_path, latest)
                failure.update({
                    "latest_record_hash": record_hash,
                    "fault_injection_report_path": str(report_path),
                    "fault_injection_report_hash": report[
                        "fault_injection_report_hash"
                    ],
                    "persistence_performed": True,
                })

        failure["result_hash"] = _sha(failure)
        if config.get("execute_rollback") is True:
            return self._g2_rollback_fault(failure)
        return failure

    def _requested_stage(self, inputs: Optional[Mapping[str, Any]]) -> str:
        if not isinstance(inputs, Mapping):
            return ""
        context = inputs.get("admission_context")
        if isinstance(context, Mapping):
            return str(context.get("requested_stage") or "").strip()
        return str(inputs.get("requested_stage") or "").strip()

    def _backup_manifest_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / "backup_manifest.json"

    def _load_json_mapping(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return dict(value) if isinstance(value, Mapping) else None

    def _secure_backup_paths(
        self,
        target_relative: str,
        backup_relative: str,
    ) -> Tuple[Optional[Path], Optional[Path], list[str]]:
        reasons: list[str] = []
        target = self.root / target_relative
        backup = self.root / backup_relative
        try:
            resolved_root = self.root.resolve(strict=True)
            target_parent = target.parent.resolve(strict=True)
            backup_parent = backup.parent.resolve(strict=True)
            target_parent.relative_to(resolved_root)
            backup_parent.relative_to(resolved_root)
        except (OSError, ValueError):
            return None, None, ["backup_path_outside_root"]
        if target.is_symlink():
            reasons.append("backup_target_symlink_rejected")
        if backup.is_symlink():
            reasons.append("backup_destination_symlink_rejected")
        try:
            if target.exists() and target.stat().st_nlink != 1:
                reasons.append("backup_target_hardlink_rejected")
        except OSError:
            reasons.append("backup_target_stat_failed")
        return target, backup, reasons

    def _copy_backup_atomically(
        self,
        source: Path,
        destination: Path,
    ) -> Tuple[str, int, bool, bool]:
        if not destination.parent.exists():
            create_context = self._take_filesystem_effect_context("FS_CREATE_DIR", destination.parent)
            create_context.begin()
            create_context.execute_path("p162g6_index1_backup_parent_create", "FS_CREATE_DIR", destination.parent)
        copy_context = self._take_filesystem_effect_context("FS_COPY2", destination)
        copy_context.begin()
        if not copy_context.root_id:
            raise RuntimeError("filesystem_effect_context_root_id_required")
        copy_context.execute_copy2(
            "p162g6_index1_backup_copy2", str(copy_context.root_id), self.root, source, destination
        )
        final_hash = _file_sha(destination)
        if final_hash is None:
            raise OSError("backup_hash_unavailable")
        return final_hash, int(destination.stat().st_mode), True, True

    def _validate_backed_up_replay(
        self,
        transaction_dir: Path,
        admitted: Mapping[str, Any],
    ) -> Optional[Dict[str, Any]]:
        latest_path = transaction_dir / "latest_state.json"
        manifest_path = self._backup_manifest_path(transaction_dir)
        latest = self._load_json_mapping(latest_path)
        manifest = self._load_json_mapping(manifest_path)
        if latest is None or manifest is None:
            return None
        if latest.get("transaction_state") != "BACKED_UP":
            return None
        reasons: list[str] = []
        for key in ("transaction_id", "proposal_id", "manifest_hash", "plan_hash"):
            expected = (
                self._transaction_id(admitted)
                if key == "transaction_id"
                else admitted.get(key)
                if key in {"proposal_id", "manifest_hash"}
                else _mapping(admitted.get("dry_run_plan")).get("plan_hash")
            )
            if latest.get(key) != expected:
                reasons.append(f"existing_backup_{key}_divergence")
        state_hash = latest.get("state_hash")
        payload = {k: v for k, v in latest.items() if k != "state_hash"}
        if not _valid_sha(state_hash) or str(state_hash).lower() != _sha(payload):
            reasons.append("existing_backup_state_hash_invalid")
        manifest_hash = manifest.get("backup_manifest_hash")
        manifest_payload = {
            k: v for k, v in manifest.items() if k != "backup_manifest_hash"
        }
        if not _valid_sha(manifest_hash) or str(manifest_hash).lower() != _sha(
            manifest_payload
        ):
            reasons.append("existing_backup_manifest_hash_invalid")
        backup_path = self.root / str(manifest.get("backup_path") or "")
        if manifest.get("backup_required"):
            if not backup_path.is_file():
                reasons.append("existing_backup_file_missing")
            elif _file_sha(backup_path) != manifest.get("backup_sha256"):
                reasons.append("existing_backup_file_hash_divergence")
        if reasons:
            rejected = dict(admitted)
            rejected.update({
                "stage": "ACEE6-D1",
                "public_schema_version": "0.5.0",
                "status": "ACEE6_TRANSACTION_BACKUP_REJECTED",
                "transaction_state": "STATE_CORRUPTED",
                "transaction_prepared": True,
                "backup_complete": False,
                "backup_created": False,
                "candidate_written": False,
                "blocking_reasons": sorted(set(reasons)),
            })
            rejected["result_hash"] = _sha({
                k: v for k, v in rejected.items() if k != "result_hash"
            })
            return rejected
        replayed = dict(admitted)
        replayed.update({
            "stage": "ACEE6-D1",
            "public_schema_version": "0.5.0",
            "status": "ACEE6_TRANSACTION_BACKUP_COMPLETE",
            "transaction_state": "BACKED_UP",
            "transaction_id": latest.get("transaction_id"),
            "transaction_prepared": True,
            "backup_complete": True,
            "backup_replayed": True,
            "backup_required": manifest.get("backup_required"),
            "backup_created": manifest.get("backup_created"),
            "backup_path": manifest.get("backup_path"),
            "backup_sha256": manifest.get("backup_sha256"),
            "backup_hash_verified": True,
            "permissions_preserved": True,
            "candidate_written": False,
            "candidate_compiled": False,
            "inventory_modified": False,
            "tests_executed": False,
            "global_validation_executed": False,
            "persistence_performed": True,
        })
        replayed["result_hash"] = _sha({
            k: v for k, v in replayed.items() if k != "result_hash"
        })
        return replayed

    def _backup_transaction(
        self,
        prepared: Mapping[str, Any],
    ) -> Dict[str, Any]:
        transaction_id = str(prepared.get("transaction_id") or "")
        transaction_dir = Path(str(prepared.get("transaction_directory") or ""))
        if not transaction_id or not transaction_dir.is_dir():
            rejected = dict(prepared)
            rejected.update({
                "stage": "ACEE6-D1",
                "public_schema_version": "0.5.0",
                "status": "ACEE6_TRANSACTION_BACKUP_REJECTED",
                "transaction_state": "STATE_CORRUPTED",
                "backup_complete": False,
                "blocking_reasons": ["prepared_transaction_missing"],
            })
            return rejected

        replay = self._validate_backed_up_replay(transaction_dir, prepared)
        if replay is not None:
            return replay

        plan = _mapping(prepared.get("normalized_plan"))
        target_relative = str(plan.get("target_path") or "")
        backup_relative = str(plan.get("backup_path") or "")
        target, backup, reasons = self._secure_backup_paths(
            target_relative,
            backup_relative,
        )
        if target is None or backup is None:
            reasons.append("backup_paths_invalid")

        snapshot_path = transaction_dir / "snapshot.json"
        snapshot = self._load_json_mapping(snapshot_path)
        if snapshot is None:
            reasons.append("backup_snapshot_missing")
            target_entry = {}
        else:
            target_entry = next(
                (
                    item for item in snapshot.get("entries", [])
                    if isinstance(item, Mapping)
                    and item.get("relative_path") == target_relative
                ),
                {},
            )
            current_entry = self._snapshot_entry(target_relative)
            if _canonical(target_entry) != _canonical(current_entry):
                reasons.append("backup_source_snapshot_divergence")

        backup_required = bool(target_entry.get("exists"))
        if backup_required and not bool(target_entry.get("is_file")):
            reasons.append("backup_source_not_regular_file")

        if backup is not None and backup.exists() and not backup.is_symlink():
            if not backup.is_file():
                reasons.append("existing_backup_not_regular_file")
            else:
                existing_backup_hash = _file_sha(backup)
                expected_source_hash = target_entry.get("sha256")
                if (
                    backup_required
                    and existing_backup_hash != expected_source_hash
                ):
                    reasons.append("existing_backup_file_hash_divergence")

        runtime_root = self._transaction_runtime_root()
        lock_path = runtime_root / ".backup.lock"
        self._take_filesystem_effect_context("FS_CREATE_DIR", lock_path.parent)
        lock_handle = lock_path.open("a+", encoding="utf-8")
        try:
            try:
                fcntl.flock(
                    lock_handle.fileno(),
                    fcntl.LOCK_EX | fcntl.LOCK_NB,
                )
            except BlockingIOError:
                blocked = dict(prepared)
                blocked.update({
                    "stage": "ACEE6-D1",
                    "public_schema_version": "0.5.0",
                    "status": "ACEE6_TRANSACTION_BACKUP_BLOCKED",
                    "transaction_state": "PREPARED",
                    "backup_complete": False,
                    "backup_created": False,
                    "lock_acquired": False,
                    "blocking_reasons": ["transaction_backup_lock_busy"],
                })
                return blocked

            if reasons:
                rejected = dict(prepared)
                rejected.update({
                    "stage": "ACEE6-D1",
                    "public_schema_version": "0.5.0",
                    "status": "ACEE6_TRANSACTION_BACKUP_REJECTED",
                    "transaction_state": "STATE_CORRUPTED",
                    "backup_complete": False,
                    "backup_created": False,
                    "candidate_written": False,
                    "blocking_reasons": sorted(set(reasons)),
                })
                return rejected

            latest_path = transaction_dir / "latest_state.json"
            latest = self._load_json_mapping(latest_path) or {}
            previous_hash = latest.get("latest_record_hash")
            journal_path = transaction_dir / "journal.jsonl"
            common = {
                "transaction_id": transaction_id,
                "proposal_id": prepared.get("proposal_id"),
                "manifest_hash": prepared.get("manifest_hash"),
                "plan_hash": _mapping(prepared.get("dry_run_plan")).get("plan_hash"),
                "snapshot_hash": prepared.get("snapshot_hash"),
                "target_path": target_relative,
                "backup_path": backup_relative,
                "timestamp_utc": self.now_utc.isoformat(),
            }
            backing_hash = self._append_journal_record(
                journal_path,
                {**common, "state": "BACKING_UP"},
                str(previous_hash) if previous_hash else None,
            )

            backup_created = False
            backup_sha = None
            source_mode = target_entry.get("mode")
            backup_mode = None
            backup_fsynced = True
            directory_fsynced = True
            if backup_required:
                try:
                    backup_sha, backup_mode, backup_fsynced, directory_fsynced = (
                        self._copy_backup_atomically(target, backup)
                    )
                except PermissionError:
                    rejected = dict(prepared)
                    rejected.update({
                        "stage": "ACEE6-D1",
                        "public_schema_version": "0.5.0",
                        "status": "ACEE6_TRANSACTION_BACKUP_REJECTED",
                        "transaction_state": "STATE_CORRUPTED",
                        "backup_complete": False,
                        "backup_created": False,
                        "candidate_written": False,
                        "blocking_reasons": ["backup_permission_denied"],
                    })
                    rejected["result_hash"] = _sha({
                        k: v for k, v in rejected.items()
                        if k != "result_hash"
                    })
                    return rejected
                except OSError:
                    rejected = dict(prepared)
                    rejected.update({
                        "stage": "ACEE6-D1",
                        "public_schema_version": "0.5.0",
                        "status": "ACEE6_TRANSACTION_BACKUP_REJECTED",
                        "transaction_state": "STATE_CORRUPTED",
                        "backup_complete": False,
                        "backup_created": False,
                        "candidate_written": False,
                        "blocking_reasons": ["backup_write_failed"],
                    })
                    rejected["result_hash"] = _sha({
                        k: v for k, v in rejected.items()
                        if k != "result_hash"
                    })
                    return rejected
                backup_created = True
                if backup_sha != target_entry.get("sha256"):
                    raise RuntimeError("backup_hash_mismatch_after_copy")
                manifest_expected = str(plan.get("backup_sha256") or "").lower()
                if manifest_expected and backup_sha != manifest_expected:
                    raise RuntimeError("backup_manifest_hash_mismatch")

            backup_manifest = {
                "primitive": PRIMITIVE,
                "stage": "ACEE6-D1",
                "transaction_id": transaction_id,
                "proposal_id": prepared.get("proposal_id"),
                "manifest_hash": prepared.get("manifest_hash"),
                "plan_hash": _mapping(prepared.get("dry_run_plan")).get("plan_hash"),
                "snapshot_hash": prepared.get("snapshot_hash"),
                "target_path": target_relative,
                "target_existed_before": backup_required,
                "target_sha256_before": target_entry.get("sha256"),
                "backup_required": backup_required,
                "backup_created": backup_created,
                "backup_path": backup_relative,
                "backup_sha256": backup_sha,
                "source_mode": source_mode,
                "backup_mode": backup_mode,
                "permissions_preserved": (
                    not backup_required or source_mode == backup_mode
                ),
                "backup_fsynced": backup_fsynced,
                "directory_fsynced": directory_fsynced,
                "candidate_written": False,
                "timestamp_utc": self.now_utc.isoformat(),
            }
            backup_manifest["backup_manifest_hash"] = _sha(backup_manifest)
            manifest_path = self._backup_manifest_path(transaction_dir)
            self._atomic_json_write(manifest_path, backup_manifest)

            backed_hash = self._append_journal_record(
                journal_path,
                {**common, "state": "BACKED_UP", "backup_manifest_hash": backup_manifest["backup_manifest_hash"]},
                backing_hash,
            )
            latest_payload = {
                **latest,
                "stage": "ACEE6-D1",
                "public_schema_version": "0.5.0",
                "status": "ACEE6_TRANSACTION_BACKUP_COMPLETE",
                "transaction_state": "BACKED_UP",
                "latest_record_hash": backed_hash,
                "backup_manifest_hash": backup_manifest["backup_manifest_hash"],
                "backup_required": backup_required,
                "backup_created": backup_created,
                "backup_path": backup_relative,
                "backup_sha256": backup_sha,
                "candidate_written": False,
                "timestamp_utc": self.now_utc.isoformat(),
            }
            latest_payload.pop("state_hash", None)
            latest_payload["state_hash"] = _sha(latest_payload)
            self._atomic_json_write(latest_path, latest_payload)

            result = dict(prepared)
            result.update({
                "stage": "ACEE6-D1",
                "public_schema_version": "0.5.0",
                "status": "ACEE6_TRANSACTION_BACKUP_COMPLETE",
                "transaction_state": "BACKED_UP",
                "backup_complete": True,
                "backup_replayed": False,
                "backup_required": backup_required,
                "backup_created": backup_created,
                "new_file_absence_recorded": not backup_required,
                "backup_path": backup_relative,
                "backup_sha256": backup_sha,
                "backup_manifest_path": str(manifest_path),
                "backup_manifest_hash": backup_manifest["backup_manifest_hash"],
                "backup_fsynced": backup_fsynced,
                "directory_fsynced": directory_fsynced,
                "backup_hash_verified": True,
                "permissions_preserved": backup_manifest["permissions_preserved"],
                "candidate_written": False,
                "candidate_compiled": False,
                "inventory_modified": False,
                "tests_executed": False,
                "global_validation_executed": False,
                "rollback_executed": False,
                "persistence_performed": True,
                "write_count": int(prepared.get("write_count") or 0) + 3,
            })
            result["result_hash"] = _sha({
                k: v for k, v in result.items() if k != "result_hash"
            })
            return result
        finally:
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            lock_handle.close()

    def _candidate_content_bytes(
        self,
        inputs: Optional[Mapping[str, Any]],
        admitted: Mapping[str, Any],
    ) -> Tuple[Optional[bytes], list[str]]:
        reasons: list[str] = []
        if not isinstance(inputs, Mapping):
            return None, ["candidate_content_missing"]
        context = inputs.get("admission_context")
        if not isinstance(context, Mapping):
            return None, ["candidate_content_missing"]
        content = context.get("candidate_content")
        if not isinstance(content, str):
            return None, [
                "candidate_content_missing"
                if content is None
                else "candidate_content_type_invalid"
            ]
        try:
            encoded = content.encode("utf-8", errors="strict")
        except UnicodeEncodeError:
            return None, ["candidate_content_utf8_invalid"]
        expected = str(
            _mapping(admitted.get("normalized_plan")).get(
                "candidate_content_sha256"
            )
            or ""
        ).lower()
        actual = hashlib.sha256(encoded).hexdigest()
        if actual != expected:
            reasons.append("candidate_content_hash_divergence")
        return encoded, reasons

    def _mutation_manifest_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / "mutation_manifest.json"

    def _secure_mutation_target(
        self,
        admitted: Mapping[str, Any],
    ) -> Tuple[Optional[Path], list[str]]:
        reasons: list[str] = []
        plan = _mapping(admitted.get("normalized_plan"))
        relative = str(plan.get("target_path") or "")
        if not relative:
            return None, ["mutation_target_missing"]
        target = self.root / relative
        try:
            resolved_root = self.root.resolve(strict=True)
            parent = target.parent.resolve(strict=True)
            parent.relative_to(resolved_root)
        except (OSError, ValueError):
            return None, ["mutation_target_outside_root"]
        fingerprints = _mapping(plan.get("path_fingerprints"))
        expected_parent = _mapping(fingerprints.get("target_path"))
        try:
            stat = target.parent.stat()
            if expected_parent.get("parent_device") is not None and int(
                expected_parent.get("parent_device")
            ) != int(stat.st_dev):
                reasons.append("mutation_target_parent_device_divergence")
            if expected_parent.get("parent_inode") is not None and int(
                expected_parent.get("parent_inode")
            ) != int(stat.st_ino):
                reasons.append("mutation_target_parent_inode_divergence")
        except OSError:
            reasons.append("mutation_target_parent_stat_failed")
        if target.is_symlink():
            reasons.append("mutation_target_symlink_rejected")
        try:
            if target.exists() and target.stat().st_nlink != 1:
                reasons.append("mutation_target_hardlink_rejected")
        except OSError:
            reasons.append("mutation_target_stat_failed")
        return target, reasons

    def _write_candidate_atomically(
        self,
        target: Path,
        content: bytes,
        expected_sha256: str,
    ) -> Tuple[str, bool, bool, int]:
        if not isinstance(content, bytes):
            raise TypeError("candidate_content_must_be_bytes")
        if hashlib.sha256(content).hexdigest() != expected_sha256:
            raise OSError("candidate_temporary_hash_mismatch")
        mode = int(target.stat().st_mode) if target.exists() else 0o100644
        if not target.parent.exists():
            create_context = self._take_filesystem_effect_context("FS_CREATE_DIR", target.parent)
            create_context.begin()
            create_context.execute_path("p162g6_c02_candidate_parent_create", "FS_CREATE_DIR", target.parent)
        write_context = self._take_filesystem_effect_context("FS_WRITE_REPLACE_BYTES", target)
        write_context.begin()
        write_context.execute_path("p162g6_c02_candidate_write_replace", "FS_WRITE_REPLACE_BYTES", target, content)
        final_hash = _file_sha(target)
        if final_hash != expected_sha256:
            raise OSError("candidate_final_hash_mismatch")
        return final_hash, True, True, int(target.stat().st_mode)


    def _validate_mutated_replay(
        self,
        transaction_dir: Path,
        admitted: Mapping[str, Any],
    ) -> Optional[Dict[str, Any]]:
        latest = self._load_json_mapping(transaction_dir / "latest_state.json")
        manifest = self._load_json_mapping(
            self._mutation_manifest_path(transaction_dir)
        )
        if latest is None or manifest is None:
            return None
        if latest.get("transaction_state") != "MUTATED":
            return None
        reasons: list[str] = []
        manifest_hash = manifest.get("mutation_manifest_hash")
        payload = {
            key: value
            for key, value in manifest.items()
            if key != "mutation_manifest_hash"
        }
        if not _valid_sha(manifest_hash) or str(manifest_hash).lower() != _sha(
            payload
        ):
            reasons.append("existing_mutation_manifest_hash_invalid")
        target_relative = str(
            _mapping(admitted.get("normalized_plan")).get("target_path") or ""
        )
        target = self.root / target_relative
        expected = str(
            _mapping(admitted.get("normalized_plan")).get(
                "candidate_content_sha256"
            )
            or ""
        ).lower()
        if not target.is_file() or target.is_symlink():
            reasons.append("existing_mutation_target_missing_or_unsafe")
        elif _file_sha(target) != expected:
            reasons.append("existing_mutation_target_hash_divergence")
        if latest.get("mutation_manifest_hash") != manifest_hash:
            reasons.append("existing_mutation_latest_manifest_divergence")
        if reasons:
            rejected = dict(admitted)
            rejected.update({
                "stage": "ACEE6-D2",
                "public_schema_version": "0.6.0",
                "status": "ACEE6_TRANSACTION_MUTATION_REJECTED",
                "transaction_state": "STATE_CORRUPTED",
                "mutation_complete": False,
                "candidate_written": False,
                "blocking_reasons": sorted(set(reasons)),
            })
            rejected["result_hash"] = _sha({
                k: v for k, v in rejected.items() if k != "result_hash"
            })
            return rejected
        replayed = dict(admitted)
        replayed.update({
            "stage": "ACEE6-D2",
            "public_schema_version": "0.6.0",
            "status": "ACEE6_TRANSACTION_MUTATION_COMPLETE",
            "transaction_state": "MUTATED",
            "transaction_id": latest.get("transaction_id"),
            "mutation_complete": True,
            "mutation_replayed": True,
            "candidate_content_received": True,
            "candidate_hash_verified": True,
            "candidate_written": True,
            "candidate_compiled": False,
            "inventory_modified": False,
            "tests_executed": False,
            "global_validation_executed": False,
            "persistence_performed": True,
            "mutation_manifest_path": str(
                self._mutation_manifest_path(transaction_dir)
            ),
            "mutation_manifest_hash": manifest_hash,
        })
        replayed["result_hash"] = _sha({
            k: v for k, v in replayed.items() if k != "result_hash"
        })
        return replayed

    def _recover_interrupted_mutation(
        self,
        transaction_dir: Path,
        admitted: Mapping[str, Any],
        inputs: Optional[Mapping[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        latest_path = transaction_dir / "latest_state.json"
        journal_path = transaction_dir / "journal.jsonl"
        latest = self._load_json_mapping(latest_path)
        if latest is None or latest.get("transaction_state") != "BACKED_UP":
            return None
        if not journal_path.is_file():
            return None

        try:
            records = [
                json.loads(line)
                for line in journal_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        except (OSError, json.JSONDecodeError):
            return None

        if not records or records[-1].get("state") != "MUTATING":
            return None

        content, reasons = self._candidate_content_bytes(inputs, admitted)
        if reasons or content is None:
            return None

        plan = _mapping(admitted.get("normalized_plan"))
        target_relative = str(plan.get("target_path") or "")
        expected_hash = str(plan.get("candidate_content_sha256") or "").lower()
        target = self.root / target_relative

        if (
            not target.is_file()
            or target.is_symlink()
            or _file_sha(target) != expected_hash
        ):
            return None

        transaction_id = str(latest.get("transaction_id") or "")
        if not transaction_id:
            return None

        mutation_manifest = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-D2",
            "transaction_id": transaction_id,
            "proposal_id": latest.get("proposal_id"),
            "manifest_hash": latest.get("manifest_hash"),
            "plan_hash": latest.get("plan_hash"),
            "target_path": target_relative,
            "candidate_content_sha256": expected_hash,
            "written_sha256": expected_hash,
            "temporary_file_fsynced": True,
            "target_directory_fsynced": self._fsync_directory(target.parent),
            "target_mode": int(target.stat().st_mode),
            "candidate_compiled": False,
            "inventory_modified": False,
            "tests_executed": False,
            "timestamp_utc": self.now_utc.isoformat(),
            "recovery_mode": "post_replace_interruption",
        }
        mutation_manifest["mutation_manifest_hash"] = _sha(mutation_manifest)
        manifest_path = self._mutation_manifest_path(transaction_dir)
        self._atomic_json_write(manifest_path, mutation_manifest)

        previous_hash = str(records[-1].get("record_hash") or "")
        common = {
            "transaction_id": transaction_id,
            "proposal_id": latest.get("proposal_id"),
            "manifest_hash": latest.get("manifest_hash"),
            "plan_hash": latest.get("plan_hash"),
            "snapshot_hash": latest.get("snapshot_hash"),
            "target_path": target_relative,
            "candidate_content_sha256": expected_hash,
            "timestamp_utc": self.now_utc.isoformat(),
        }
        mutated_hash = self._append_journal_record(
            journal_path,
            {
                **common,
                "state": "MUTATED",
                "mutation_manifest_hash": mutation_manifest[
                    "mutation_manifest_hash"
                ],
                "recovery_mode": "post_replace_interruption",
            },
            previous_hash or None,
        )

        latest_payload = {
            **dict(latest),
            "stage": "ACEE6-D2",
            "public_schema_version": "0.6.0",
            "status": "ACEE6_TRANSACTION_MUTATION_COMPLETE",
            "transaction_state": "MUTATED",
            "latest_record_hash": mutated_hash,
            "mutation_manifest_hash": mutation_manifest[
                "mutation_manifest_hash"
            ],
            "candidate_content_sha256": expected_hash,
            "candidate_written": True,
            "candidate_compiled": False,
            "inventory_modified": False,
            "tests_executed": False,
            "timestamp_utc": self.now_utc.isoformat(),
            "recovery_mode": "post_replace_interruption",
        }
        latest_payload.pop("state_hash", None)
        latest_payload["state_hash"] = _sha(latest_payload)
        self._atomic_json_write(latest_path, latest_payload)

        recovered = dict(admitted)
        recovered.update({
            "stage": "ACEE6-D2",
            "public_schema_version": "0.6.0",
            "status": "ACEE6_TRANSACTION_MUTATION_COMPLETE",
            "transaction_state": "MUTATED",
            "transaction_id": transaction_id,
            "mutation_complete": True,
            "mutation_replayed": True,
            "mutation_recovered": True,
            "recovery_mode": "post_replace_interruption",
            "candidate_content_received": True,
            "candidate_hash_verified": True,
            "temporary_file_created": True,
            "temporary_file_fsynced": True,
            "atomic_replace_performed": True,
            "target_directory_fsynced": True,
            "candidate_written": True,
            "candidate_compiled": False,
            "inventory_modified": False,
            "tests_executed": False,
            "global_validation_executed": False,
            "persistence_performed": True,
            "mutation_manifest_path": str(manifest_path),
            "mutation_manifest_hash": mutation_manifest[
                "mutation_manifest_hash"
            ],
        })
        recovered["result_hash"] = _sha({
            key: value
            for key, value in recovered.items()
            if key != "result_hash"
        })
        return recovered

    def _mutate_transaction(
        self,
        backed_up: Mapping[str, Any],
        inputs: Optional[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        transaction_id = str(backed_up.get("transaction_id") or "")
        transaction_dir = Path(
            str(backed_up.get("transaction_directory") or "")
        )
        if not transaction_id or not transaction_dir.is_dir():
            rejected = dict(backed_up)
            rejected.update({
                "stage": "ACEE6-D2",
                "public_schema_version": "0.6.0",
                "status": "ACEE6_TRANSACTION_MUTATION_REJECTED",
                "transaction_state": "STATE_CORRUPTED",
                "mutation_complete": False,
                "candidate_written": False,
                "blocking_reasons": ["backed_up_transaction_missing"],
            })
            return rejected

        replay = self._validate_mutated_replay(transaction_dir, backed_up)
        if replay is not None:
            return replay

        content, reasons = self._candidate_content_bytes(inputs, backed_up)
        target, path_reasons = self._secure_mutation_target(backed_up)
        reasons.extend(path_reasons)

        backup_replay = self._validate_backed_up_replay(
            transaction_dir,
            backed_up,
        )
        if backup_replay is None or backup_replay.get(
            "transaction_state"
        ) != "BACKED_UP":
            reasons.append("mutation_backup_integrity_unavailable")

        snapshot = self._load_json_mapping(transaction_dir / "snapshot.json")
        plan = _mapping(backed_up.get("normalized_plan"))
        target_relative = str(plan.get("target_path") or "")
        target_entry = {}
        if snapshot is None:
            reasons.append("mutation_snapshot_missing")
        else:
            target_entry = next(
                (
                    item
                    for item in snapshot.get("entries", [])
                    if isinstance(item, Mapping)
                    and item.get("relative_path") == target_relative
                ),
                {},
            )
        if target is not None:
            current = self._snapshot_entry(target_relative)
            if _canonical(current) != _canonical(target_entry):
                reasons.append("mutation_target_snapshot_divergence")

        runtime_root = self._transaction_runtime_root()
        lock_path = runtime_root / ".mutation.lock"
        self._take_filesystem_effect_context("FS_CREATE_DIR", lock_path.parent)
        lock_handle = lock_path.open("a+", encoding="utf-8")
        try:
            try:
                fcntl.flock(
                    lock_handle.fileno(),
                    fcntl.LOCK_EX | fcntl.LOCK_NB,
                )
            except BlockingIOError:
                blocked = dict(backed_up)
                blocked.update({
                    "stage": "ACEE6-D2",
                    "public_schema_version": "0.6.0",
                    "status": "ACEE6_TRANSACTION_MUTATION_BLOCKED",
                    "transaction_state": "BACKED_UP",
                    "mutation_complete": False,
                    "candidate_written": False,
                    "blocking_reasons": ["transaction_mutation_lock_busy"],
                })
                return blocked

            if reasons or content is None or target is None:
                rejected = dict(backed_up)
                rejected.update({
                    "stage": "ACEE6-D2",
                    "public_schema_version": "0.6.0",
                    "status": "ACEE6_TRANSACTION_MUTATION_REJECTED",
                    "transaction_state": "STATE_CORRUPTED",
                    "mutation_complete": False,
                    "candidate_written": False,
                    "candidate_compiled": False,
                    "inventory_modified": False,
                    "tests_executed": False,
                    "blocking_reasons": sorted(set(reasons)),
                })
                rejected["result_hash"] = _sha({
                    k: v for k, v in rejected.items() if k != "result_hash"
                })
                return rejected

            latest_path = transaction_dir / "latest_state.json"
            latest = self._load_json_mapping(latest_path) or {}
            previous_hash = latest.get("latest_record_hash")
            journal_path = transaction_dir / "journal.jsonl"
            expected_hash = str(plan.get("candidate_content_sha256") or "").lower()
            common = {
                "transaction_id": transaction_id,
                "proposal_id": backed_up.get("proposal_id"),
                "manifest_hash": backed_up.get("manifest_hash"),
                "plan_hash": _mapping(backed_up.get("dry_run_plan")).get(
                    "plan_hash"
                ),
                "snapshot_hash": backed_up.get("snapshot_hash"),
                "target_path": target_relative,
                "candidate_content_sha256": expected_hash,
                "timestamp_utc": self.now_utc.isoformat(),
            }
            mutating_hash = self._append_journal_record(
                journal_path,
                {**common, "state": "MUTATING"},
                str(previous_hash) if previous_hash else None,
            )
            try:
                final_hash, temp_fsynced, directory_fsynced, target_mode = (
                    self._write_candidate_atomically(
                        target,
                        content,
                        expected_hash,
                    )
                )
            except PermissionError:
                reason = "candidate_permission_denied"
            except OSError:
                reason = "candidate_atomic_write_failed"
            else:
                reason = ""
            if reason:
                rejected = dict(backed_up)
                rejected.update({
                    "stage": "ACEE6-D2",
                    "public_schema_version": "0.6.0",
                    "status": "ACEE6_TRANSACTION_MUTATION_REJECTED",
                    "transaction_state": "STATE_CORRUPTED",
                    "mutation_complete": False,
                    "candidate_written": False,
                    "blocking_reasons": [reason],
                })
                rejected["result_hash"] = _sha({
                    k: v for k, v in rejected.items() if k != "result_hash"
                })
                return rejected

            mutation_manifest = {
                "primitive": PRIMITIVE,
                "stage": "ACEE6-D2",
                "transaction_id": transaction_id,
                "proposal_id": backed_up.get("proposal_id"),
                "manifest_hash": backed_up.get("manifest_hash"),
                "plan_hash": _mapping(backed_up.get("dry_run_plan")).get(
                    "plan_hash"
                ),
                "target_path": target_relative,
                "candidate_content_sha256": expected_hash,
                "written_sha256": final_hash,
                "temporary_file_fsynced": temp_fsynced,
                "target_directory_fsynced": directory_fsynced,
                "target_mode": target_mode,
                "candidate_compiled": False,
                "inventory_modified": False,
                "tests_executed": False,
                "timestamp_utc": self.now_utc.isoformat(),
            }
            mutation_manifest["mutation_manifest_hash"] = _sha(
                mutation_manifest
            )
            manifest_path = self._mutation_manifest_path(transaction_dir)
            self._atomic_json_write(manifest_path, mutation_manifest)
            mutated_hash = self._append_journal_record(
                journal_path,
                {
                    **common,
                    "state": "MUTATED",
                    "mutation_manifest_hash": mutation_manifest[
                        "mutation_manifest_hash"
                    ],
                },
                mutating_hash,
            )
            latest_payload = {
                **latest,
                "stage": "ACEE6-D2",
                "public_schema_version": "0.6.0",
                "status": "ACEE6_TRANSACTION_MUTATION_COMPLETE",
                "transaction_state": "MUTATED",
                "latest_record_hash": mutated_hash,
                "mutation_manifest_hash": mutation_manifest[
                    "mutation_manifest_hash"
                ],
                "candidate_content_sha256": expected_hash,
                "candidate_written": True,
                "candidate_compiled": False,
                "inventory_modified": False,
                "tests_executed": False,
                "timestamp_utc": self.now_utc.isoformat(),
            }
            latest_payload.pop("state_hash", None)
            latest_payload["state_hash"] = _sha(latest_payload)
            self._atomic_json_write(latest_path, latest_payload)

            result = dict(backed_up)
            result.update({
                "stage": "ACEE6-D2",
                "public_schema_version": "0.6.0",
                "status": "ACEE6_TRANSACTION_MUTATION_COMPLETE",
                "transaction_state": "MUTATED",
                "mutation_complete": True,
                "mutation_replayed": False,
                "candidate_content_received": True,
                "candidate_hash_verified": True,
                "temporary_file_created": True,
                "temporary_file_fsynced": temp_fsynced,
                "atomic_replace_performed": True,
                "target_directory_fsynced": directory_fsynced,
                "candidate_written": True,
                "candidate_compiled": False,
                "inventory_modified": False,
                "tests_executed": False,
                "global_validation_executed": False,
                "mutation_manifest_path": str(manifest_path),
                "mutation_manifest_hash": mutation_manifest[
                    "mutation_manifest_hash"
                ],
                "write_count": int(backed_up.get("write_count") or 0) + 3,
                "persistence_performed": True,
            })
            result["result_hash"] = _sha({
                k: v for k, v in result.items() if k != "result_hash"
            })
            return result
        finally:
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            lock_handle.close()


    def _compilation_report_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / "compilation_report.json"

    def _validate_compiled_replay(self, transaction_dir: Path, admitted: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        latest = self._load_json_mapping(transaction_dir / "latest_state.json")
        report = self._load_json_mapping(self._compilation_report_path(transaction_dir))
        if latest is None or report is None or latest.get("transaction_state") != "COMPILED":
            return None
        payload = {k: v for k, v in report.items() if k != "compilation_report_hash"}
        report_hash = report.get("compilation_report_hash")
        plan = _mapping(admitted.get("normalized_plan"))
        target = self.root / str(plan.get("target_path") or "")
        expected = str(plan.get("candidate_content_sha256") or "").lower()
        reasons = []
        if not _valid_sha(report_hash) or str(report_hash).lower() != _sha(payload):
            reasons.append("existing_compilation_report_hash_invalid")
        if latest.get("compilation_report_hash") != report_hash:
            reasons.append("existing_compilation_latest_report_divergence")

        latest_hash = latest.get("state_hash")
        latest_payload = {
            k: v for k, v in latest.items() if k != "state_hash"
        }
        if (
            not _valid_sha(latest_hash)
            or str(latest_hash).lower() != _sha(latest_payload)
        ):
            reasons.append("existing_compilation_latest_state_hash_invalid")

        if not target.is_file() or target.is_symlink() or _file_sha(target) != expected:
            reasons.append("existing_compilation_target_divergence")

        bytecode_relative = str(report.get("bytecode_path") or "")
        bytecode = self.root / bytecode_relative
        compiled_root = transaction_dir / "compiled"
        try:
            bytecode_real = bytecode.resolve(strict=True)
            compiled_real = compiled_root.resolve(strict=True)
            bytecode_real.relative_to(compiled_real)
        except (OSError, RuntimeError, ValueError):
            reasons.append("existing_compilation_bytecode_path_invalid")
        else:
            expected_bytecode = str(
                report.get("bytecode_sha256") or ""
            ).lower()
            if (
                bytecode.is_symlink()
                or not bytecode.is_file()
                or not _valid_sha(expected_bytecode)
                or _file_sha(bytecode) != expected_bytecode
            ):
                reasons.append("existing_compilation_bytecode_divergence")
        if reasons:
            result = dict(admitted)
            result.update({"stage":"ACEE6-D3","public_schema_version":"0.7.0","status":"ACEE6_TRANSACTION_COMPILATION_REJECTED","transaction_state":"STATE_CORRUPTED","candidate_compiled":False,"candidate_executed":False,"inventory_modified":False,"tests_executed":False,"global_validation_executed":False,"blocking_reasons":sorted(set(reasons))})
            result["result_hash"] = _sha({k:v for k,v in result.items() if k != "result_hash"})
            return result
        result = dict(admitted)
        result.update({"stage":"ACEE6-D3","public_schema_version":"0.7.0","status":"ACEE6_TRANSACTION_COMPILATION_COMPLETE","transaction_state":"COMPILED","compilation_complete":True,"compilation_replayed":True,"candidate_written":True,"candidate_compiled":True,"candidate_executed":False,"inventory_modified":False,"tests_executed":False,"global_validation_executed":False,"committed":False,"compilation_report_path":str(self._compilation_report_path(transaction_dir)),"compilation_report_hash":report_hash,"source_sha256":report.get("source_sha256"),"bytecode_sha256":report.get("bytecode_sha256"),"persistence_performed":True})
        result["result_hash"] = _sha({k:v for k,v in result.items() if k != "result_hash"})
        return result

    def _rollback_after_compilation_failure(self, transaction_dir: Path, mutated: Mapping[str, Any], reason: str) -> Dict[str, Any]:
        from ontology.acee_rollback_engine import AceeRollbackEngine
        backup = self._load_json_mapping(self._backup_manifest_path(transaction_dir)) or {}
        plan = _mapping(mutated.get("normalized_plan"))
        relative = str(plan.get("target_path") or "")
        target = self.root / relative
        if bool(backup.get("target_existed_before")):
            rr = AceeRollbackEngine(root=self.root).step(inputs={"rollback_request":{"transaction_id":mutated.get("transaction_id"),"reason":"validation_failure","targets":[{"destination":relative,"backup_path":str(backup.get("backup_path") or ""),"expected_backup_sha256":backup.get("backup_sha256")}]},"governance_authorization":{"decision":"approved"},"constitutional_authorization":{"decision":"approved"},"dry_run":False,"execute":True,"timestamp_utc":self.now_utc.isoformat()},persist=True)
            ok = bool(rr.get("rollback_performed")) and target.is_file()
            if ok and backup.get("target_sha256_before"):
                ok = _file_sha(target) == backup.get("target_sha256_before")
        else:
            try:
                if target.exists() or target.is_symlink(): target.unlink()
                self._fsync_directory(target.parent)
                ok = not target.exists()
                rr = {"rollback_performed":ok,"removed_new_target":ok}
            except OSError as exc:
                ok = False; rr = {"rollback_performed":False,"failure":f"{type(exc).__name__}:{exc}"}
        latest_path = transaction_dir / "latest_state.json"
        latest = self._load_json_mapping(latest_path) or {}
        state = "ROLLED_BACK" if ok else "QUARANTINE"
        status = "ACEE6_TRANSACTION_COMPILATION_ROLLED_BACK" if ok else "ACEE6_TRANSACTION_QUARANTINED"
        record_hash = self._append_journal_record(transaction_dir/"journal.jsonl",{"transaction_id":mutated.get("transaction_id"),"proposal_id":mutated.get("proposal_id"),"state":state,"failure_stage":"ACEE6-D3","failure_reason":reason,"rollback_performed":ok,"timestamp_utc":self.now_utc.isoformat()},str(latest.get("latest_record_hash")) if latest.get("latest_record_hash") else None)
        latest.update({"stage":"ACEE6-D3","public_schema_version":"0.7.0","status":status,"transaction_state":state,"latest_record_hash":record_hash,"candidate_compiled":False,"candidate_executed":False,"inventory_modified":False,"tests_executed":False,"global_validation_executed":False,"rollback_executed":ok,"quarantined":not ok,"timestamp_utc":self.now_utc.isoformat()})
        latest.pop("state_hash",None); latest["state_hash"]=_sha(latest); self._atomic_json_write(latest_path,latest)
        result=dict(mutated); result.update({"stage":"ACEE6-D3","public_schema_version":"0.7.0","status":status,"transaction_state":state,"compilation_complete":False,"candidate_compiled":False,"candidate_executed":False,"inventory_modified":False,"tests_executed":False,"global_validation_executed":False,"committed":False,"rollback_executed":ok,"rollback_result":rr,"quarantined":not ok,"blocking_reasons":[reason],"persistence_performed":True})
        result["result_hash"]=_sha({k:v for k,v in result.items() if k != "result_hash"}); return result

    def _compile_transaction(self, mutated: Mapping[str, Any]) -> Dict[str, Any]:
        transaction_id = str(mutated.get("transaction_id") or "")
        transaction_dir = self._transaction_runtime_root() / transaction_id
        replay = self._validate_compiled_replay(transaction_dir, mutated)
        if replay is not None: return replay
        latest_path = transaction_dir / "latest_state.json"
        latest = self._load_json_mapping(latest_path)
        mutation = self._load_json_mapping(self._mutation_manifest_path(transaction_dir))
        backup = self._load_json_mapping(self._backup_manifest_path(transaction_dir))
        reasons=[]
        if latest is None or latest.get("transaction_state") != "MUTATED": reasons.append("compilation_requires_mutated_state")
        if mutation is None: reasons.append("mutation_manifest_missing")
        else:
            mh=mutation.get("mutation_manifest_hash"); payload={k:v for k,v in mutation.items() if k!="mutation_manifest_hash"}
            if not _valid_sha(mh) or str(mh).lower()!=_sha(payload): reasons.append("mutation_manifest_hash_invalid")
            if latest is not None and latest.get("mutation_manifest_hash")!=mh: reasons.append("mutation_latest_manifest_divergence")
        if backup is None: reasons.append("backup_manifest_missing")
        plan=_mapping(mutated.get("normalized_plan")); relative=str(plan.get("target_path") or "")
        target,target_reasons=self._secure_mutation_target(mutated); reasons.extend(target_reasons)
        expected=str(plan.get("candidate_content_sha256") or "").lower()
        if target is None or not target.is_file() or target.is_symlink(): reasons.append("compilation_target_missing_or_unsafe")
        elif _file_sha(target)!=expected: reasons.append("compilation_target_hash_divergence")
        lock_path=self._transaction_runtime_root()/".compilation.lock"; lock_path.parent.mkdir(parents=True,exist_ok=True); handle=lock_path.open("a+",encoding="utf-8")
        try:
            try: fcntl.flock(handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                result=dict(mutated); result.update({"stage":"ACEE6-D3","public_schema_version":"0.7.0","status":"ACEE6_TRANSACTION_COMPILATION_BLOCKED","transaction_state":"MUTATED","candidate_compiled":False,"candidate_executed":False,"inventory_modified":False,"tests_executed":False,"global_validation_executed":False,"blocking_reasons":["transaction_compilation_lock_busy"]}); return result
            if reasons or target is None:
                result=dict(mutated); result.update({"stage":"ACEE6-D3","public_schema_version":"0.7.0","status":"ACEE6_TRANSACTION_COMPILATION_REJECTED","transaction_state":"STATE_CORRUPTED","candidate_compiled":False,"candidate_executed":False,"inventory_modified":False,"tests_executed":False,"global_validation_executed":False,"blocking_reasons":sorted(set(reasons))}); result["result_hash"]=_sha({k:v for k,v in result.items() if k!="result_hash"}); return result
            journal=transaction_dir/"journal.jsonl"
            compiling_hash=self._append_journal_record(journal,{"transaction_id":transaction_id,"proposal_id":mutated.get("proposal_id"),"state":"COMPILING","target_path":relative,"source_sha256":expected,"candidate_executed":False,"inventory_modified":False,"timestamp_utc":self.now_utc.isoformat()},str(latest.get("latest_record_hash")) if latest and latest.get("latest_record_hash") else None)
            current={**(latest or {}),"stage":"ACEE6-D3","public_schema_version":"0.7.0","status":"ACEE6_TRANSACTION_COMPILING","transaction_state":"COMPILING","latest_record_hash":compiling_hash,"candidate_compiled":False,"candidate_executed":False,"inventory_modified":False,"tests_executed":False,"global_validation_executed":False,"timestamp_utc":self.now_utc.isoformat()}; current.pop("state_hash",None); current["state_hash"]=_sha(current); self._atomic_json_write(latest_path,current)
            compiled_dir=transaction_dir/"compiled"; compiled_dir.mkdir(parents=True,exist_ok=True); bytecode=compiled_dir/f"{target.stem}.pyc"; started=time.monotonic_ns()
            try:
                py_compile.compile(str(target),cfile=str(bytecode),dfile=relative,doraise=True); duration=time.monotonic_ns()-started; bytecode_sha=_file_sha(bytecode)
                with bytecode.open("rb") as stream: os.fsync(stream.fileno())
                dir_sync=self._fsync_directory(compiled_dir)
            except (py_compile.PyCompileError,UnicodeError,OSError) as exc:
                return self._rollback_after_compilation_failure(transaction_dir,mutated,f"candidate_compilation_failed:{type(exc).__name__}")
            report={"primitive":PRIMITIVE,"stage":"ACEE6-D3","public_schema_version":"0.7.0","transaction_id":transaction_id,"proposal_id":mutated.get("proposal_id"),"target_path":relative,"source_sha256":expected,"bytecode_path":str(bytecode.relative_to(self.root)),"bytecode_sha256":bytecode_sha,"compilation_duration_ns":duration,"compiled_directory_fsynced":dir_sync,"candidate_compiled":True,"candidate_executed":False,"inventory_modified":False,"tests_executed":False,"global_validation_executed":False,"committed":False,"timestamp_utc":self.now_utc.isoformat()}; report["compilation_report_hash"]=_sha(report); report_path=self._compilation_report_path(transaction_dir); self._atomic_json_write(report_path,report)
            compiled_hash=self._append_journal_record(journal,{"transaction_id":transaction_id,"proposal_id":mutated.get("proposal_id"),"state":"COMPILED","target_path":relative,"source_sha256":expected,"bytecode_sha256":bytecode_sha,"compilation_report_hash":report["compilation_report_hash"],"candidate_executed":False,"inventory_modified":False,"timestamp_utc":self.now_utc.isoformat()},compiling_hash)
            current.update({"status":"ACEE6_TRANSACTION_COMPILATION_COMPLETE","transaction_state":"COMPILED","latest_record_hash":compiled_hash,"compilation_report_hash":report["compilation_report_hash"],"source_sha256":expected,"bytecode_sha256":bytecode_sha,"candidate_compiled":True,"committed":False}); current.pop("state_hash",None); current["state_hash"]=_sha(current); self._atomic_json_write(latest_path,current)
            result=dict(mutated); result.update({"stage":"ACEE6-D3","public_schema_version":"0.7.0","status":"ACEE6_TRANSACTION_COMPILATION_COMPLETE","transaction_state":"COMPILED","compilation_complete":True,"compilation_replayed":False,"candidate_written":True,"candidate_compiled":True,"candidate_executed":False,"inventory_modified":False,"tests_executed":False,"global_validation_executed":False,"committed":False,"source_sha256":expected,"bytecode_path":str(bytecode),"bytecode_sha256":bytecode_sha,"compilation_duration_ns":duration,"compilation_report_path":str(report_path),"compilation_report_hash":report["compilation_report_hash"],"rollback_executed":False,"persistence_performed":True,"write_count":int(mutated.get("write_count") or 0)+4}); result["result_hash"]=_sha({k:v for k,v in result.items() if k!="result_hash"}); return result
        finally:
            try: fcntl.flock(handle.fileno(),fcntl.LOCK_UN)
            except OSError: pass
            handle.close()


    def _inventory_snapshot_manifest_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / "inventory_snapshot_manifest.json"

    def _inventory_update_manifest_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / "inventory_update_manifest.json"

    def _inventory_validation_report_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / "inventory_validation_report.json"

    def _render_inventory_python(self, path: Path, module_name: str) -> bytes:
        import ast
        source = path.read_text(encoding="utf-8") if path.is_file() else "# Auto-generated ontology inventory\n\nONTOLOGY_INVENTORY = []\n"
        tree = ast.parse(source)
        values = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ONTOLOGY_INVENTORY" for t in node.targets):
                values = ast.literal_eval(node.value)
                break
        if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
            raise ValueError("ontology_inventory_assignment_invalid")
        values = sorted(set(values) | {module_name})
        return ("# Auto-generated ontology inventory\n\nONTOLOGY_INVENTORY = " + repr(values) + "\n").encode("utf-8")

    def _render_inventory_text(self, path: Path, module_name: str) -> bytes:
        values = []
        if path.is_file():
            values = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return ("\n".join(sorted(set(values) | {module_name})) + "\n").encode("utf-8")

    def _render_dependency_registry(self, path: Path, module_name: str, dependencies: Any) -> bytes:
        import ast
        source = path.read_text(encoding="utf-8") if path.is_file() else "# Auto-generated dependency registry\n\nDEPENDENCY_REGISTRY = {}\n"
        tree = ast.parse(source)
        registry = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "DEPENDENCY_REGISTRY" for t in node.targets):
                registry = ast.literal_eval(node.value)
                break
        if not isinstance(registry, dict):
            raise ValueError("dependency_registry_assignment_invalid")
        deps = sorted(set(str(x) for x in (dependencies or []) if str(x).strip()))
        registry[module_name] = deps
        return ("# Auto-generated dependency registry\n\nDEPENDENCY_REGISTRY = " + repr(dict(sorted(registry.items()))) + "\n").encode("utf-8")

    def _render_catalog_text(self, path: Path, module_name: str, target_path: str) -> bytes:
        source = path.read_text(encoding="utf-8") if path.is_file() else "Open Cognitive Ecology — Global Module Catalog\n[modules]\n"
        entry = f"ontology\tontology.{module_name}\t{target_path}"
        lines = source.splitlines()
        matches = [line for line in lines if line.strip() == entry]
        if not matches:
            lines.append(entry)
        elif len(matches) > 1:
            kept = False; cleaned=[]
            for line in lines:
                if line.strip() == entry:
                    if kept: continue
                    kept = True
                cleaned.append(line)
            lines = cleaned
        return ("\n".join(lines).rstrip() + "\n").encode("utf-8")

    def _inventory_cycle(self, registry: Mapping[str, Any]) -> bool:
        graph = {str(k): [str(x) for x in v] for k, v in registry.items() if isinstance(v, (list, tuple))}
        visiting=set(); visited=set()
        def visit(node: str) -> bool:
            if node in visiting: return True
            if node in visited: return False
            visiting.add(node)
            for nxt in graph.get(node, []):
                if nxt in graph and visit(nxt): return True
            visiting.remove(node); visited.add(node); return False
        return any(visit(node) for node in graph)

    def _update_inventories(self, compiled: Mapping[str, Any], inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        import ast
        transaction_id=str(compiled.get("transaction_id") or "")
        transaction_dir=self._transaction_runtime_root()/transaction_id
        latest_path=transaction_dir/"latest_state.json"
        latest=self._load_json_mapping(latest_path)
        if latest is None or latest.get("transaction_state") != "COMPILED":
            result=dict(compiled); result.update({"stage":"ACEE6-E","public_schema_version":"0.8.0","status":"ACEE6_INVENTORY_UPDATE_REJECTED","transaction_state":"STATE_CORRUPTED","inventory_modified":False,"blocking_reasons":["inventory_update_requires_compiled_state"]}); return result
        plan=_mapping(compiled.get("normalized_plan")); module_name=str(plan.get("module_name") or ""); target_path=str(plan.get("target_path") or "")
        context=_mapping(_mapping(inputs or {}).get("admission_context")); dependencies=context.get("inventory_dependencies", [])
        targets=[str(x) for x in plan.get("inventory_targets", [])]
        expected=set(REQUIRED_INVENTORY_TARGETS)
        if set(targets) != expected:
            result=dict(compiled); result.update({"stage":"ACEE6-E","public_schema_version":"0.8.0","status":"ACEE6_INVENTORY_UPDATE_REJECTED","transaction_state":"STATE_CORRUPTED","inventory_modified":False,"blocking_reasons":["inventory_target_set_invalid"]}); return result
        lock=(transaction_dir/"inventory.lock").open("a+b")
        try:
            try: fcntl.flock(lock.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                result=dict(compiled); result.update({"stage":"ACEE6-E","public_schema_version":"0.8.0","status":"ACEE6_INVENTORY_UPDATE_BLOCKED","transaction_state":"COMPILED","inventory_modified":False,"blocking_reasons":["transaction_inventory_lock_busy"]}); return result
            snapshots=[]; rendered={}; seen_inodes=set()
            root_real=self.root.resolve(strict=True)
            for rel in sorted(targets):
                path=self.root/rel
                try:
                    parent_real=path.parent.resolve(strict=True)
                    parent_real.relative_to(root_real)
                except (OSError,RuntimeError,ValueError):
                    raise ValueError("inventory_parent_path_invalid")
                if path.is_symlink():
                    raise ValueError("inventory_symlink_rejected")
                if path.exists():
                    real=path.resolve(strict=True)
                    try: real.relative_to(root_real)
                    except ValueError: raise ValueError("inventory_path_outside_root")
                    stat=path.stat()
                    inode_key=(stat.st_dev,stat.st_ino)
                    if inode_key in seen_inodes:
                        raise ValueError("inventory_hardlink_collision")
                    seen_inodes.add(inode_key)
                before=path.read_bytes() if path.is_file() else None
                snapshots.append({"path":rel,"existed_before":before is not None,"before_sha256":hashlib.sha256(before).hexdigest() if before is not None else None,"before_hex":before.hex() if before is not None else None})
                if rel == "ontology_inventory.txt": rendered[rel]=self._render_inventory_text(path,module_name)
                elif rel in {"ontology_inventory.py","ontology/ontology_inventory.py"}: rendered[rel]=self._render_inventory_python(path,module_name)
                elif rel == "dependency_registry.py": rendered[rel]=self._render_dependency_registry(path,module_name,dependencies)
                elif rel == "global_module_catalog.txt": rendered[rel]=self._render_catalog_text(path,module_name,target_path)
            snapshot={"transaction_id":transaction_id,"proposal_id":compiled.get("proposal_id"),"files":snapshots,"timestamp_utc":self.now_utc.isoformat()}; snapshot["snapshot_manifest_hash"]=_sha(snapshot); self._atomic_json_write(self._inventory_snapshot_manifest_path(transaction_dir),snapshot)
            updating_hash=self._append_journal_record(transaction_dir/"journal.jsonl",{"transaction_id":transaction_id,"proposal_id":compiled.get("proposal_id"),"state":"INVENTORY_UPDATING","timestamp_utc":self.now_utc.isoformat()},str(latest.get("latest_record_hash") or "") or None)
            current={**latest,"stage":"ACEE6-E","public_schema_version":"0.8.0","status":"ACEE6_INVENTORY_UPDATING","transaction_state":"INVENTORY_UPDATING","latest_record_hash":updating_hash,"inventory_modified":False,"timestamp_utc":self.now_utc.isoformat()}; current.pop("state_hash",None); current["state_hash"]=_sha(current); self._atomic_json_write(latest_path,current)
            written=[]
            try:
                for rel in sorted(rendered):
                    path=self.root/rel; path.parent.mkdir(parents=True,exist_ok=True)
                    fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",suffix=".tmp",dir=str(path.parent))
                    try:
                        with os.fdopen(fd,"wb") as stream: stream.write(rendered[rel]); stream.flush(); os.fsync(stream.fileno())
                        os.replace(tmp,path); self._fsync_directory(path.parent); written.append(rel)
                    finally:
                        try: os.unlink(tmp)
                        except FileNotFoundError: pass
                inv_txt=[x for x in (self.root/"ontology_inventory.txt").read_text(encoding="utf-8").splitlines() if x]
                ns={}; exec((self.root/"ontology_inventory.py").read_text(encoding="utf-8"),ns); inv_a=ns.get("ONTOLOGY_INVENTORY")
                ns={}; exec((self.root/"ontology/ontology_inventory.py").read_text(encoding="utf-8"),ns); inv_b=ns.get("ONTOLOGY_INVENTORY")
                ns={}; exec((self.root/"dependency_registry.py").read_text(encoding="utf-8"),ns); registry=ns.get("DEPENDENCY_REGISTRY")
                catalog=(self.root/"global_module_catalog.txt").read_text(encoding="utf-8").splitlines(); entry=f"ontology\tontology.{module_name}\t{target_path}"
                reasons=[]
                if inv_txt != sorted(set(inv_txt)): reasons.append("ontology_inventory_text_duplicates_or_order")
                if inv_a != inv_txt or inv_b != inv_txt: reasons.append("ontology_inventory_cross_view_divergence")
                if not isinstance(registry,dict) or module_name not in registry:
                    reasons.append("dependency_registry_missing_module")
                else:
                    deps=list(registry.get(module_name) or [])
                    if len(deps) != len(set(deps)):
                        reasons.append("dependency_duplicates_detected")
                    unknown=sorted(
                        dep for dep in deps
                        if dep not in set(inv_txt)
                    )
                    if unknown:
                        reasons.append("unknown_dependencies:"+",".join(unknown))
                    if self._inventory_cycle(registry):
                        reasons.append("dependency_cycle_detected")
                if sum(1 for line in catalog if line.strip()==entry) != 1: reasons.append("global_catalog_entry_invalid")
                if reasons: raise ValueError(";".join(reasons))
            except Exception as exc:
                ok=True
                for item in snapshots:
                    path=self.root/item["path"]
                    try:
                        if item["existed_before"]: path.write_bytes(bytes.fromhex(item["before_hex"])); self._fsync_directory(path.parent)
                        elif path.exists(): path.unlink(); self._fsync_directory(path.parent)
                    except OSError: ok=False
                state="ROLLED_BACK" if ok else "QUARANTINE"; status="ACEE6_INVENTORY_UPDATE_ROLLED_BACK" if ok else "ACEE6_TRANSACTION_QUARANTINED"
                result=dict(compiled); result.update({"stage":"ACEE6-E","public_schema_version":"0.8.0","status":status,"transaction_state":state,"inventory_modified":False,"rollback_executed":ok,"quarantined":not ok,"blocking_reasons":[f"inventory_update_failed:{type(exc).__name__}:{exc}"]}); return result
            validation={"transaction_id":transaction_id,"module_name":module_name,"ontology_views_equal":True,"duplicates_detected":False,"dependency_cycle_detected":False,"catalog_entry_count":1,"timestamp_utc":self.now_utc.isoformat()}; validation["validation_report_hash"]=_sha(validation); self._atomic_json_write(self._inventory_validation_report_path(transaction_dir),validation)
            update={"transaction_id":transaction_id,"module_name":module_name,"target_path":target_path,"files":[{"path":rel,"after_sha256":_file_sha(self.root/rel)} for rel in sorted(rendered)],"snapshot_manifest_hash":snapshot["snapshot_manifest_hash"],"validation_report_hash":validation["validation_report_hash"],"timestamp_utc":self.now_utc.isoformat()}; update["inventory_update_manifest_hash"]=_sha(update); self._atomic_json_write(self._inventory_update_manifest_path(transaction_dir),update)
            done_hash=self._append_journal_record(transaction_dir/"journal.jsonl",{"transaction_id":transaction_id,"proposal_id":compiled.get("proposal_id"),"state":"INVENTORIES_UPDATED","inventory_update_manifest_hash":update["inventory_update_manifest_hash"],"timestamp_utc":self.now_utc.isoformat()},updating_hash)
            current.update({"status":"ACEE6_INVENTORY_UPDATE_COMPLETE","transaction_state":"INVENTORIES_UPDATED","latest_record_hash":done_hash,"inventory_modified":True,"inventory_update_manifest_hash":update["inventory_update_manifest_hash"]}); current.pop("state_hash",None); current["state_hash"]=_sha(current); self._atomic_json_write(latest_path,current)
            result=dict(compiled); result.update({"stage":"ACEE6-E","public_schema_version":"0.8.0","status":"ACEE6_INVENTORY_UPDATE_COMPLETE","transaction_state":"INVENTORIES_UPDATED","inventory_update_complete":True,"inventory_modified":True,"candidate_compiled":True,"candidate_executed":False,"tests_executed":False,"global_validation_executed":False,"committed":False,"inventory_snapshot_manifest_path":str(self._inventory_snapshot_manifest_path(transaction_dir)),"inventory_update_manifest_path":str(self._inventory_update_manifest_path(transaction_dir)),"inventory_validation_report_path":str(self._inventory_validation_report_path(transaction_dir)),"persistence_performed":True}); result["result_hash"]=_sha({k:v for k,v in result.items() if k!="result_hash"}); return result
        finally:
            try: fcntl.flock(lock.fileno(),fcntl.LOCK_UN)
            except OSError: pass
            lock.close()


    def _local_validation_report_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / "local_validation_report.json"

    def _validate_f1_command_contract(self, commands: Any) -> Tuple[list[Dict[str, Any]], list[str]]:
        from ontology.f1_validation_command_contract import validate_f1_contract
        reasons: list[str] = []
        if not isinstance(commands, list):
            return [], ["local_validation_commands_missing"]
        if any("argv" in _mapping(raw) for raw in commands):
            return [], ["local_validation_opaque_argv_forbidden"]
        try:
            descriptors = validate_f1_contract([_mapping(raw) for raw in commands])
        except (TypeError, ValueError) as exc:
            return [], [f"local_validation_typed_contract_invalid:{type(exc).__name__}"]
        normalized: list[Dict[str, Any]] = []
        for descriptor in descriptors:
            if descriptor.kind == "VALIDATION_MAIN":
                argv = [sys.executable, "-m", "validation.main"]
                if descriptor.full_validation:
                    argv.append("--full")
            elif descriptor.kind == "REGISTERED_SCRIPT":
                reasons.append(f"local_validation_registered_script_unresolved:{descriptor.script_id}")
                continue
            else:
                reasons.append(f"local_validation_command_kind_unresolved:{descriptor.kind}")
                continue
            normalized.append({"role": descriptor.role, "name": descriptor.role, "argv": argv, "timeout_seconds": 120.0})
        return normalized, sorted(set(reasons))

    def _rollback_after_local_validation_failure(
        self, transaction_dir: Path, inventories_updated: Mapping[str, Any], reason: str,
        runner_result: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        from ontology.acee_rollback_engine import AceeRollbackEngine
        snapshot=self._load_json_mapping(self._inventory_snapshot_manifest_path(transaction_dir)); inventory_ok=isinstance(snapshot,Mapping)
        if inventory_ok:
            for item in snapshot.get("files",[]):
                record=_mapping(item); path=self.root/str(record.get("path") or "")
                try:
                    if record.get("existed_before") is True:
                        if not path.parent.exists():
                            c=self._take_filesystem_effect_context("FS_CREATE_DIR",path.parent);c.begin();c.execute_path("p162g6_index2_inventory_parent_create","FS_CREATE_DIR",path.parent)
                        c=self._take_filesystem_effect_context("FS_WRITE_REPLACE_BYTES",path);c.begin();c.execute_path("p162g6_index2_inventory_restore","FS_WRITE_REPLACE_BYTES",path,bytes.fromhex(str(record.get("before_hex") or "")))
                    elif path.exists() or path.is_symlink():
                        c=self._take_filesystem_effect_context("FS_REMOVE_FILE",path);c.begin();c.execute_path("p162g6_index2_inventory_remove","FS_REMOVE_FILE",path)
                except (OSError,ValueError,RuntimeError,KeyError): inventory_ok=False
        backup=self._load_json_mapping(self._backup_manifest_path(transaction_dir)) or {}; plan=_mapping(inventories_updated.get("normalized_plan")); relative=str(backup.get("target_path") or plan.get("target_path") or ""); target=self.root/relative
        target_result: Dict[str,Any]; target_ok=False
        if bool(backup.get("target_existed_before")):
            target_result=AceeRollbackEngine(root=self.root,filesystem_effect_context_provider=self.filesystem_effect_context_provider).step(inputs={"rollback_request":{"transaction_id":inventories_updated.get("transaction_id"),"reason":"validation_failure","targets":[{"destination":relative,"backup_path":str(backup.get("backup_path") or ""),"expected_backup_sha256":backup.get("backup_sha256")}]},"governance_authorization":{"decision":"approved"},"constitutional_authorization":{"decision":"approved"},"dry_run":False,"execute":True,"timestamp_utc":self.now_utc.isoformat()},persist=True)
            target_ok=target_result.get("rollback_performed") is True or target_result.get("rollback_status") in {"ACEE_ROLLBACK_COMPLETE","rollback_complete"}
            if target_ok and backup.get("target_sha256_before") and target.is_file(): target_ok=_file_sha(target)==backup.get("target_sha256_before")
        else:
            try:
                if target.exists() or target.is_symlink():
                    c=self._take_filesystem_effect_context("FS_REMOVE_FILE",target);c.begin();c.execute_path("p162g6_index2_target_remove","FS_REMOVE_FILE",target)
                target_ok=not target.exists() and not target.is_symlink(); target_result={"rollback_performed":target_ok,"removed_new_target":target_ok,"rollback_status":"ACEE_ROLLBACK_COMPLETE" if target_ok else "ACEE_ROLLBACK_FAILED","rollback_action":"remove_created_file","destination":relative}
            except (OSError,RuntimeError,KeyError) as exc:
                target_ok=False;target_result={"rollback_performed":False,"removed_new_target":False,"rollback_status":"ACEE_ROLLBACK_FAILED","rollback_action":"remove_created_file","destination":relative,"failure":f"{type(exc).__name__}:{exc}"}
        rollback_ok=inventory_ok and target_ok; state="ROLLED_BACK" if rollback_ok else "QUARANTINE"; status="ACEE6_LOCAL_VALIDATION_ROLLED_BACK" if rollback_ok else "ACEE6_LOCAL_VALIDATION_QUARANTINED"
        latest_path=transaction_dir/"latest_state.json"; latest=self._load_json_mapping(latest_path) or {}
        record_hash=self._append_journal_record_governed(transaction_dir/"journal.jsonl",{"transaction_id":inventories_updated.get("transaction_id"),"proposal_id":inventories_updated.get("proposal_id"),"state":state,"reason":reason,"rollback_performed":rollback_ok,"inventory_restored":inventory_ok,"target_restored":target_ok,"timestamp_utc":self.now_utc.isoformat()},str(latest.get("latest_record_hash") or "") or None)
        current={**latest,"stage":"ACEE6-F1","public_schema_version":"0.9.0","status":status,"transaction_state":state,"latest_record_hash":record_hash,"local_validation_complete":False,"local_validation_passed":False,"tests_executed":True,"global_validation_executed":False,"committed":False,"rollback_executed":rollback_ok,"quarantined":not rollback_ok,"timestamp_utc":self.now_utc.isoformat()}; current.pop("state_hash",None); current["state_hash"]=_sha(current); self._atomic_json_write(latest_path,current)
        result=dict(inventories_updated);result.update(current);result["rollback_result"]=target_result
        if isinstance(runner_result,Mapping): result["validation_runner_result"]=dict(runner_result)
        result["inventory_rollback_succeeded"]=inventory_ok;result["target_rollback_succeeded"]=target_ok;result["blocking_reasons"]=[reason];result["result_hash"]=_sha({k:v for k,v in result.items() if k!="result_hash"});return result

    def _validate_local_validation_replay(self, transaction_dir: Path, admitted: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        latest = self._load_json_mapping(transaction_dir / "latest_state.json")
        if not isinstance(latest, Mapping) or latest.get("transaction_state") != "LOCALLY_VALIDATED":
            return None
        reasons: list[str] = []
        latest_hash = latest.get("state_hash")
        latest_payload = {key: value for key, value in latest.items() if key != "state_hash"}
        if not _valid_sha(latest_hash) or str(latest_hash).lower() != _sha(latest_payload):
            reasons.append("existing_local_validation_latest_state_hash_invalid")
        report_path = self._local_validation_report_path(transaction_dir)
        report = self._load_json_mapping(report_path)
        if not isinstance(report, Mapping):
            reasons.append("existing_local_validation_report_missing")
        else:
            report_hash = report.get("local_validation_report_hash")
            report_payload = {key: value for key, value in report.items() if key != "local_validation_report_hash"}
            if not _valid_sha(report_hash) or str(report_hash).lower() != _sha(report_payload):
                reasons.append("existing_local_validation_report_hash_invalid")
            if latest.get("local_validation_report_hash") != report_hash:
                reasons.append("existing_local_validation_latest_report_divergence")
        if reasons:
            result = dict(admitted)
            result.update({"stage": "ACEE6-F1", "public_schema_version": "0.9.0", "status": "ACEE6_LOCAL_VALIDATION_REPLAY_REJECTED", "transaction_state": "STATE_CORRUPTED", "local_validation_complete": False, "local_validation_passed": False, "local_validation_replayed": False, "tests_executed": False, "global_validation_executed": False, "committed": False, "blocking_reasons": sorted(set(reasons))})
            result["result_hash"] = _sha({key: value for key, value in result.items() if key != "result_hash"})
            return result
        result = dict(latest)
        result.update({"primitive": PRIMITIVE, "stage": "ACEE6-F1", "public_schema_version": "0.9.0", "status": "ACEE6_LOCAL_VALIDATION_COMPLETE", "transaction_state": "LOCALLY_VALIDATED", "local_validation_complete": True, "local_validation_passed": True, "local_validation_replayed": True, "tests_executed": True, "global_validation_executed": False, "committed": False, "persistence_performed": False, "local_validation_report_path": str(report_path)})
        result["result_hash"] = _sha({key: value for key, value in result.items() if key != "result_hash"})
        return result

    def _run_local_validation_f1(self, inventories_updated: Mapping[str, Any], inputs: Mapping[str, Any]) -> Dict[str, Any]:
        from ontology.acee_validation_runner import AceeValidationRunner
        transaction_id = str(inventories_updated.get("transaction_id") or "")
        transaction_dir = self._transaction_runtime_root() / transaction_id
        latest_path = transaction_dir / "latest_state.json"
        context = _mapping(inputs.get("admission_context"))
        commands, reasons = self._validate_f1_command_contract(context.get("local_validation_commands"))
        if reasons:
            result = dict(inventories_updated)
            result.update({"stage": "ACEE6-F1", "public_schema_version": "0.9.0", "status": "ACEE6_LOCAL_VALIDATION_REJECTED", "transaction_state": "INVENTORIES_UPDATED", "local_validation_complete": False, "local_validation_passed": False, "tests_executed": False, "global_validation_executed": False, "committed": False, "blocking_reasons": reasons})
            result["result_hash"] = _sha({key: value for key, value in result.items() if key != "result_hash"})
            return result
        lock = (transaction_dir / "local_validation.lock").open("a+b")
        try:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                result = dict(inventories_updated)
                result.update({"stage": "ACEE6-F1", "public_schema_version": "0.9.0", "status": "ACEE6_LOCAL_VALIDATION_BLOCKED", "transaction_state": "INVENTORIES_UPDATED", "local_validation_complete": False, "local_validation_passed": False, "tests_executed": False, "global_validation_executed": False, "committed": False, "blocking_reasons": ["transaction_local_validation_lock_busy"]})
                return result
            latest = self._load_json_mapping(latest_path) or {}
            testing_hash = self._append_journal_record(transaction_dir / "journal.jsonl", {"transaction_id": transaction_id, "proposal_id": inventories_updated.get("proposal_id"), "state": "TESTING", "timestamp_utc": self.now_utc.isoformat()}, str(latest.get("latest_record_hash") or "") or None)
            current = {**latest, "stage": "ACEE6-F1", "public_schema_version": "0.9.0", "status": "ACEE6_LOCAL_VALIDATION_RUNNING", "transaction_state": "TESTING", "latest_record_hash": testing_hash, "local_validation_complete": False, "local_validation_passed": False, "tests_executed": True, "global_validation_executed": False, "committed": False, "timestamp_utc": self.now_utc.isoformat()}
            current.pop("state_hash", None)
            current["state_hash"] = _sha(current)
            self._atomic_json_write(latest_path, current)
            runner_result = AceeValidationRunner(root=self.root).step(inputs={"validation_id": f"{transaction_id}-f1", "timestamp_utc": self.now_utc.isoformat(), "scope": "ACEE6-F1", "mode": "targeted", "execute_commands": True, "commands": [{"name": item["name"], "argv": item["argv"], "timeout_seconds": item["timeout_seconds"]} for item in commands]}, persist=True)
            report = {"primitive": PRIMITIVE, "stage": "ACEE6-F1", "public_schema_version": "0.9.0", "transaction_id": transaction_id, "proposal_id": inventories_updated.get("proposal_id"), "validation_order": [item["role"] for item in commands], "validation_runner_result_hash": runner_result.get("result_hash"), "validation_status": runner_result.get("validation_status"), "validation_complete": runner_result.get("validation_complete"), "validation_passed": runner_result.get("validation_passed"), "error_count": runner_result.get("error_count"), "failed_commands": runner_result.get("failed_commands"), "timed_out_commands": runner_result.get("timed_out_commands"), "blocked_commands": runner_result.get("blocked_commands"), "benign_warnings": runner_result.get("benign_warnings"), "non_benign_warnings": runner_result.get("non_benign_warnings"), "evidence_manifest": runner_result.get("evidence_manifest"), "tests_executed": True, "global_validation_executed": False, "committed": False, "timestamp_utc": self.now_utc.isoformat()}
            report["local_validation_report_hash"] = _sha(report)
            report_path = self._local_validation_report_path(transaction_dir)
            self._atomic_json_write(report_path, report)
            if runner_result.get("validation_complete") is not True or runner_result.get("validation_passed") is not True or int(runner_result.get("error_count") or 0) != 0:
                return self._rollback_after_local_validation_failure(
                    transaction_dir,
                    inventories_updated,
                    "local_validation_failed",
                    runner_result=runner_result,
                )
            complete_hash = self._append_journal_record(transaction_dir / "journal.jsonl", {"transaction_id": transaction_id, "proposal_id": inventories_updated.get("proposal_id"), "state": "LOCALLY_VALIDATED", "local_validation_report_hash": report["local_validation_report_hash"], "timestamp_utc": self.now_utc.isoformat()}, testing_hash)
            latest = self._load_json_mapping(latest_path) or {}
            latest.update({"stage": "ACEE6-F1", "public_schema_version": "0.9.0", "status": "ACEE6_LOCAL_VALIDATION_COMPLETE", "transaction_state": "LOCALLY_VALIDATED", "latest_record_hash": complete_hash, "local_validation_complete": True, "local_validation_passed": True, "local_validation_replayed": False, "local_validation_report_hash": report["local_validation_report_hash"], "tests_executed": True, "global_validation_executed": False, "committed": False, "timestamp_utc": self.now_utc.isoformat()})
            latest.pop("state_hash", None)
            latest["state_hash"] = _sha(latest)
            self._atomic_json_write(latest_path, latest)
            result = dict(inventories_updated)
            result.update(latest)
            result["local_validation_report_path"] = str(report_path)
            result["validation_runner_result"] = runner_result
            result["persistence_performed"] = True
            result["result_hash"] = _sha({key: value for key, value in result.items() if key != "result_hash"})
            return result
        finally:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            finally:
                lock.close()


    def _global_validation_report_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / "global_validation_report.json"

    def _validate_global_validation_replay(
        self,
        transaction_dir: Path,
        admitted: Mapping[str, Any],
    ) -> Optional[Dict[str, Any]]:
        latest = self._load_json_mapping(
            transaction_dir / "latest_state.json"
        )
        if not isinstance(latest, Mapping):
            return None
        if latest.get("transaction_state") != "GLOBALLY_VALIDATED":
            return None

        reasons: list[str] = []
        latest_hash = latest.get("state_hash")
        latest_payload = {
            key: value
            for key, value in latest.items()
            if key != "state_hash"
        }
        if (
            not _valid_sha(latest_hash)
            or str(latest_hash).lower() != _sha(latest_payload)
        ):
            reasons.append(
                "existing_global_validation_latest_state_hash_invalid"
            )

        report_path = self._global_validation_report_path(transaction_dir)
        report = self._load_json_mapping(report_path)
        if not isinstance(report, Mapping):
            reasons.append("existing_global_validation_report_missing")
        else:
            report_hash = report.get("global_validation_report_hash")
            report_payload = {
                key: value
                for key, value in report.items()
                if key != "global_validation_report_hash"
            }
            if (
                not _valid_sha(report_hash)
                or str(report_hash).lower() != _sha(report_payload)
            ):
                reasons.append(
                    "existing_global_validation_report_hash_invalid"
                )
            if latest.get("global_validation_report_hash") != report_hash:
                reasons.append(
                    "existing_global_validation_latest_report_divergence"
                )

            source_relative = str(
                report.get("source_report_relative_path") or ""
            )
            source_report = self.root / source_relative
            try:
                source_real = source_report.resolve(strict=True)
                source_real.relative_to(self.root.resolve(strict=True))
            except (OSError, RuntimeError, ValueError):
                reasons.append(
                    "existing_global_validation_source_path_invalid"
                )
            else:
                expected_source_hash = str(
                    report.get("source_report_sha256") or ""
                ).lower()
                if (
                    source_report.is_symlink()
                    or not source_report.is_file()
                    or not _valid_sha(expected_source_hash)
                    or _file_sha(source_report) != expected_source_hash
                ):
                    reasons.append(
                        "existing_global_validation_source_report_divergence"
                    )

        if reasons:
            result = dict(admitted)
            result.update(
                {
                    "stage": "ACEE6-F2",
                    "public_schema_version": "0.10.1",
                    "status": "ACEE6_GLOBAL_VALIDATION_REPLAY_REJECTED",
                    "transaction_state": "STATE_CORRUPTED",
                    "global_validation_complete": False,
                    "global_validation_passed": False,
                    "global_validation_replayed": False,
                    "global_validation_executed": False,
                    "committed": False,
                    "blocking_reasons": sorted(set(reasons)),
                }
            )
            result["result_hash"] = _sha(
                {
                    key: value
                    for key, value in result.items()
                    if key != "result_hash"
                }
            )
            return result

        result = dict(latest)
        result.update(
            {
                "primitive": PRIMITIVE,
                "stage": "ACEE6-F2",
                "public_schema_version": "0.10.1",
                "status": "ACEE6_GLOBAL_VALIDATION_COMPLETE",
                "transaction_state": "GLOBALLY_VALIDATED",
                "global_validation_complete": True,
                "global_validation_passed": True,
                "global_validation_replayed": True,
                "global_validation_executed": True,
                "committed": False,
                "persistence_performed": False,
                "global_validation_report_path": str(report_path),
            }
        )
        result["result_hash"] = _sha(
            {
                key: value
                for key, value in result.items()
                if key != "result_hash"
            }
        )
        return result

    def _run_global_validation_f2(
        self,
        locally_validated: Mapping[str, Any],
        inputs: Mapping[str, Any],
    ) -> Dict[str, Any]:
        from ontology.acee_validation_runner import AceeValidationRunner

        transaction_id = str(locally_validated.get("transaction_id") or "")
        transaction_dir = self._transaction_runtime_root() / transaction_id
        latest_path = transaction_dir / "latest_state.json"
        journal_path = transaction_dir / "journal.jsonl"
        context = _mapping(inputs.get("admission_context"))
        timeout_seconds = context.get("global_validation_timeout_seconds", 1800.0)
        source_report = self.root / "scientific_validation_report.json"
        before_hash = _file_sha(source_report) if source_report.is_file() else None
        before_mtime = source_report.stat().st_mtime_ns if source_report.is_file() else None

        latest = self._load_json_mapping(latest_path) or {}
        running_hash = self._append_journal_record(
            journal_path,
            {
                "transaction_id": transaction_id,
                "proposal_id": locally_validated.get("proposal_id"),
                "state": "GLOBAL_VALIDATING",
                "timestamp_utc": self.now_utc.isoformat(),
            },
            str(latest.get("latest_record_hash") or "") or None,
        )
        current = {
            **latest,
            "stage": "ACEE6-F2",
            "public_schema_version": "0.10.1",
            "status": "ACEE6_GLOBAL_VALIDATION_RUNNING",
            "transaction_state": "GLOBAL_VALIDATING",
            "latest_record_hash": running_hash,
            "global_validation_complete": False,
            "global_validation_passed": False,
            "global_validation_executed": True,
            "committed": False,
            "timestamp_utc": self.now_utc.isoformat(),
        }
        current.pop("state_hash", None)
        current["state_hash"] = _sha(current)
        self._atomic_json_write(latest_path, current)

        runner_result = AceeValidationRunner(root=self.root).step(
            inputs={
                "validation_id": f"{transaction_id}-f2",
                "timestamp_utc": self.now_utc.isoformat(),
                "scope": "ACEE6-F2",
                "mode": "full_isolated",
                "allow_full_validation": True,
                "milestone": "ACEE6-F2",
                "execute_commands": True,
                "stop_on_failure": True,
                "commands": [{
                    "name": "global_validation",
                    "argv": [sys.executable, "-m", "validation.main", "--full"],
                    "timeout_seconds": timeout_seconds,
                }],
            },
            persist=True,
        )

        source_path_safe = False
        if source_report.is_file() and not source_report.is_symlink():
            try:
                source_report.resolve(strict=True).relative_to(
                    self.root.resolve(strict=True)
                )
                source_path_safe = True
            except (OSError, RuntimeError, ValueError):
                source_path_safe = False

        source = (
            self._load_json_mapping(source_report)
            if source_path_safe
            else None
        )
        after_hash = (
            _file_sha(source_report)
            if source_path_safe and source_report.is_file()
            else None
        )
        report_replaced = (
            source_path_safe
            and after_hash is not None
            and (before_hash is None or after_hash != before_hash)
        )

        diagnostics = (
            _mapping(source.get("diagnostics"))
            if isinstance(source, Mapping)
            else {}
        )
        summary = (
            _mapping(source.get("summary"))
            if isinstance(source, Mapping)
            else {}
        )
        error_count = diagnostics.get("error_count")
        failed_calls = diagnostics.get("failed_calls")
        timeouts = diagnostics.get("timeouts")
        failed_modules = diagnostics.get("failed_modules")
        strict_diagnostics = (
            type(error_count) is int
            and type(failed_calls) is int
            and type(timeouts) is int
            and error_count == 0
            and failed_calls == 0
            and timeouts == 0
            and isinstance(failed_modules, list)
            and not failed_modules
        )
        source_valid = (
            isinstance(source, Mapping)
            and source_path_safe
            and source.get("validation_mode") == "full_isolated"
            and report_replaced
            and strict_diagnostics
            and summary.get("overall_success") is True
        )
        runner_ok = (
            runner_result.get("validation_complete") is True
            and runner_result.get("validation_passed") is True
            and type(runner_result.get("error_count")) is int
            and runner_result.get("error_count") == 0
            and not runner_result.get("non_benign_warnings")
        )

        report = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-F2",
            "public_schema_version": "0.10.1",
            "transaction_id": transaction_id,
            "proposal_id": locally_validated.get("proposal_id"),
            "validation_runner_result_hash": runner_result.get("result_hash"),
            "source_report_path": str(source_report),
            "source_report_relative_path": str(
                source_report.relative_to(self.root)
            ),
            "source_report_sha256": after_hash,
            "source_report_replaced": report_replaced,
            "source_report_path_safe": source_path_safe,
            "validation_mode": source.get("validation_mode") if isinstance(source, Mapping) else None,
            "error_count": diagnostics.get("error_count"),
            "failed_calls": diagnostics.get("failed_calls"),
            "timeouts": diagnostics.get("timeouts"),
            "failed_modules": failed_modules,
            "overall_success": summary.get("overall_success"),
            "runner_passed": runner_ok,
            "source_report_valid": source_valid,
            "global_validation_executed": True,
            "committed": False,
            "timestamp_utc": self.now_utc.isoformat(),
        }
        report["global_validation_report_hash"] = _sha(report)
        report_path = self._global_validation_report_path(transaction_dir)
        self._atomic_json_write(report_path, report)

        if not (runner_ok and source_valid):
            rolled = self._rollback_after_local_validation_failure(
                transaction_dir,
                locally_validated,
                "global_validation_failed",
                runner_result=runner_result,
            )
            rolled.update({
                "stage": "ACEE6-F2",
                "public_schema_version": "0.10.1",
                "status": "ACEE6_GLOBAL_VALIDATION_ROLLED_BACK" if rolled.get("transaction_state") == "ROLLED_BACK" else "ACEE6_GLOBAL_VALIDATION_QUARANTINED",
                "global_validation_complete": False,
                "global_validation_passed": False,
                "global_validation_executed": True,
                "global_validation_report_path": str(report_path),
                "committed": False,
            })
            rolled["result_hash"] = _sha({k: v for k, v in rolled.items() if k != "result_hash"})
            return rolled

        complete_hash = self._append_journal_record(
            journal_path,
            {
                "transaction_id": transaction_id,
                "proposal_id": locally_validated.get("proposal_id"),
                "state": "GLOBALLY_VALIDATED",
                "global_validation_report_hash": report["global_validation_report_hash"],
                "timestamp_utc": self.now_utc.isoformat(),
            },
            running_hash,
        )
        latest = self._load_json_mapping(latest_path) or {}
        latest.update({
            "stage": "ACEE6-F2",
            "public_schema_version": "0.10.1",
            "status": "ACEE6_GLOBAL_VALIDATION_COMPLETE",
            "transaction_state": "GLOBALLY_VALIDATED",
            "latest_record_hash": complete_hash,
            "global_validation_complete": True,
            "global_validation_passed": True,
            "global_validation_replayed": False,
            "global_validation_executed": True,
            "global_validation_report_hash": report["global_validation_report_hash"],
            "committed": False,
            "timestamp_utc": self.now_utc.isoformat(),
        })
        latest.pop("state_hash", None)
        latest["state_hash"] = _sha(latest)
        self._atomic_json_write(latest_path, latest)
        result = dict(locally_validated)
        result.update(latest)
        result["global_validation_report_path"] = str(report_path)
        result["validation_runner_result"] = runner_result
        result["persistence_performed"] = True
        result["result_hash"] = _sha({k: v for k, v in result.items() if k != "result_hash"})
        return result


    # ACEE6-K50-DURABLE-COMMIT-BEGIN
    def _k50_commit_report_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / "commit_report.json"

    def _k50_validate_hashed_payload(
        self,
        path: Path,
        hash_field: str,
    ) -> Tuple[Optional[Dict[str, Any]], list[str]]:
        payload = self._load_json_mapping(path)
        if not isinstance(payload, Mapping):
            return None, [f"{path.name}_missing_or_invalid"]
        supplied = payload.get(hash_field)
        material = {k: v for k, v in payload.items() if k != hash_field}
        if not _valid_sha(supplied) or str(supplied).lower() != _sha(material):
            return dict(payload), [f"{path.name}_{hash_field}_invalid"]
        return dict(payload), []

    def _k50_commit_preconditions(
        self,
        transaction_dir: Path,
        admitted: Mapping[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], list[str]]:
        reasons: list[str] = []
        latest = self._load_json_mapping(transaction_dir / "latest_state.json")
        if not isinstance(latest, Mapping):
            return None, {}, ["commit_latest_state_missing"]
        latest = dict(latest)
        state_hash = latest.get("state_hash")
        state_payload = {k: v for k, v in latest.items() if k != "state_hash"}
        if not _valid_sha(state_hash) or str(state_hash).lower() != _sha(state_payload):
            reasons.append("commit_latest_state_hash_invalid")
        if latest.get("transaction_state") != "GLOBALLY_VALIDATED":
            reasons.append("commit_requires_globally_validated")
        if latest.get("global_validation_passed") is not True:
            reasons.append("commit_global_validation_not_passed")
        if latest.get("local_validation_passed") is not True:
            reasons.append("commit_local_validation_not_passed")
        if latest.get("committed") is True:
            reasons.append("commit_latest_state_already_committed")

        records, journal_reasons = self._i1_validate_journal(transaction_dir)
        reasons.extend(journal_reasons)
        if records:
            if records[-1].get("state") != "GLOBALLY_VALIDATED":
                reasons.append("commit_journal_not_globally_validated")
            if str(records[-1].get("record_hash") or "").lower() != str(latest.get("latest_record_hash") or "").lower():
                reasons.append("commit_latest_record_hash_divergence")

        report_specs = (
            (self._compilation_report_path(transaction_dir), "compilation_report_hash", "compilation_report"),
            (self._inventory_update_manifest_path(transaction_dir), "inventory_update_manifest_hash", "inventory_update_manifest"),
            (self._local_validation_report_path(transaction_dir), "local_validation_report_hash", "local_validation_report"),
            (self._global_validation_report_path(transaction_dir), "global_validation_report_hash", "global_validation_report"),
        )
        proof_hashes: Dict[str, Any] = {}
        for path, hash_field, label in report_specs:
            payload, proof_reasons = self._k50_validate_hashed_payload(path, hash_field)
            reasons.extend(proof_reasons)
            if payload is not None:
                proof_hashes[label] = payload.get(hash_field)
                latest_field = latest.get(hash_field)
                if latest_field is not None and latest_field != payload.get(hash_field):
                    reasons.append(f"commit_{label}_latest_divergence")

        plan = _mapping(admitted.get("normalized_plan"))
        target_relative = str(plan.get("target_path") or "")
        expected_target_sha = str(plan.get("candidate_content_sha256") or "").lower()
        target = self.root / target_relative
        try:
            target_real = target.resolve(strict=True)
            target_real.relative_to(self.root.resolve(strict=True))
        except (OSError, RuntimeError, ValueError):
            reasons.append("commit_target_path_invalid")
        else:
            if target.is_symlink() or not target.is_file():
                reasons.append("commit_target_not_regular_file")
            actual_target_sha = _file_sha(target)
            if not _valid_sha(expected_target_sha) or actual_target_sha != expected_target_sha:
                reasons.append("commit_target_hash_divergence")
            proof_hashes["target_relative_path"] = target_relative
            proof_hashes["target_sha256"] = actual_target_sha

        if latest.get("proposal_id") != admitted.get("proposal_id"):
            reasons.append("commit_proposal_divergence")
        if latest.get("manifest_hash") != admitted.get("manifest_hash"):
            reasons.append("commit_manifest_divergence")
        if self.inspect_escalation_gate().get("installation_blocked") is True:
            reasons.append("commit_j2_gate_blocked")
        return latest, proof_hashes, sorted(set(reasons))

    def _k50_validate_committed_replay(
        self,
        transaction_dir: Path,
        admitted: Mapping[str, Any],
    ) -> Optional[Dict[str, Any]]:
        latest = self._load_json_mapping(transaction_dir / "latest_state.json")
        if not isinstance(latest, Mapping) or latest.get("transaction_state") != "COMMITTED":
            return None
        reasons: list[str] = []
        state_hash = latest.get("state_hash")
        state_payload = {k: v for k, v in latest.items() if k != "state_hash"}
        if not _valid_sha(state_hash) or str(state_hash).lower() != _sha(state_payload):
            reasons.append("committed_replay_latest_state_hash_invalid")
        report, report_reasons = self._k50_validate_hashed_payload(
            self._k50_commit_report_path(transaction_dir),
            "commit_report_hash",
        )
        reasons.extend(report_reasons)
        records, journal_reasons = self._i1_validate_journal(transaction_dir)
        reasons.extend(journal_reasons)
        if records:
            states = [str(item.get("state") or "") for item in records[-2:]]
            if states != ["COMMITTING", "COMMITTED"]:
                reasons.append("committed_replay_terminal_sequence_invalid")
            if str(records[-1].get("record_hash") or "").lower() != str(latest.get("latest_record_hash") or "").lower():
                reasons.append("committed_replay_latest_record_hash_divergence")
        if report is not None:
            if report.get("transaction_id") != latest.get("transaction_id"):
                reasons.append("committed_replay_report_transaction_divergence")
            if report.get("commit_record_hash") != latest.get("latest_record_hash"):
                reasons.append("committed_replay_report_journal_divergence")
        if latest.get("proposal_id") != admitted.get("proposal_id"):
            reasons.append("committed_replay_proposal_divergence")
        if reasons:
            return self._i1_persist_quarantine(transaction_dir, latest, reasons)
        result = dict(latest)
        result.update({
            "primitive": PRIMITIVE,
            "stage": "ACEE6-K5.0",
            "public_schema_version": "0.17.0",
            "status": "ACEE_INSTALLATION_EXECUTION_COMPLETE",
            "transaction_state": "COMMITTED",
            "committed": True,
            "commit_replayed": True,
            "partial_success": False,
            "retry_allowed": False,
            "persistence_performed": False,
            "commit_report_path": str(self._k50_commit_report_path(transaction_dir)),
        })
        result["result_hash"] = _sha({k: v for k, v in result.items() if k != "result_hash"})
        return result

    def _k50_commit_transaction(
        self,
        globally_validated: Mapping[str, Any],
        admitted: Mapping[str, Any],
    ) -> Dict[str, Any]:
        transaction_id = str(globally_validated.get("transaction_id") or self._transaction_id(admitted))
        transaction_dir = self._transaction_runtime_root() / transaction_id
        lock_path = transaction_dir / ".commit.lock"
        self._take_filesystem_effect_context("FS_CREATE_DIR", lock_path.parent)
        lock = lock_path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            replay = self._k50_validate_committed_replay(transaction_dir, admitted)
            if replay is not None:
                return replay
            latest, proof_hashes, reasons = self._k50_commit_preconditions(transaction_dir, admitted)
            if reasons or latest is None:
                base = latest if isinstance(latest, Mapping) else globally_validated
                return self._rollback_after_local_validation_failure(
                    transaction_dir,
                    base,
                    "commit_precondition_failed:" + ",".join(reasons or ["latest_missing"]),
                )

            journal_path = transaction_dir / "journal.jsonl"
            committing_hash = self._append_journal_record(
                journal_path,
                {
                    "transaction_id": transaction_id,
                    "proposal_id": latest.get("proposal_id"),
                    "state": "COMMITTING",
                    "proof_hashes": proof_hashes,
                    "timestamp_utc": self.now_utc.isoformat(),
                },
                str(latest.get("latest_record_hash") or "") or None,
            )
            current = dict(latest)
            current.update({
                "stage": "ACEE6-K5.0",
                "public_schema_version": "0.17.0",
                "status": "ACEE6_COMMITTING",
                "transaction_state": "COMMITTING",
                "latest_record_hash": committing_hash,
                "committed": False,
                "partial_success": False,
                "retry_allowed": False,
                "timestamp_utc": self.now_utc.isoformat(),
            })
            current.pop("state_hash", None)
            current["state_hash"] = _sha(current)
            self._atomic_json_write(transaction_dir / "latest_state.json", current)

            report = {
                "primitive": PRIMITIVE,
                "stage": "ACEE6-K5.0",
                "public_schema_version": "0.17.0",
                "transaction_id": transaction_id,
                "proposal_id": latest.get("proposal_id"),
                "manifest_hash": latest.get("manifest_hash"),
                "precommit_record_hash": committing_hash,
                "proof_hashes": proof_hashes,
                "commit_complete": True,
                "committed": True,
                "partial_success": False,
                "timestamp_utc": self.now_utc.isoformat(),
            }
            report["commit_report_hash"] = _sha(report)
            report_path = self._k50_commit_report_path(transaction_dir)
            self._atomic_json_write(report_path, report)

            committed_hash = self._append_journal_record(
                journal_path,
                {
                    "transaction_id": transaction_id,
                    "proposal_id": latest.get("proposal_id"),
                    "state": "COMMITTED",
                    "commit_report_hash": report["commit_report_hash"],
                    "timestamp_utc": self.now_utc.isoformat(),
                },
                committing_hash,
            )
            report["commit_record_hash"] = committed_hash
            report["commit_report_hash"] = _sha({k: v for k, v in report.items() if k != "commit_report_hash"})
            self._atomic_json_write(report_path, report)

            final = dict(current)
            final.update({
                "stage": "ACEE6-K5.0",
                "public_schema_version": "0.17.0",
                "status": "ACEE_INSTALLATION_EXECUTION_COMPLETE",
                "transaction_state": "COMMITTED",
                "latest_record_hash": committed_hash,
                "commit_report_hash": report["commit_report_hash"],
                "commit_report_path": str(report_path),
                "commit_complete": True,
                "committed": True,
                "commit_replayed": False,
                "partial_success": False,
                "retry_allowed": False,
                "persistence_performed": True,
                "timestamp_utc": self.now_utc.isoformat(),
            })
            final.pop("state_hash", None)
            final["state_hash"] = _sha(final)
            self._atomic_json_write(transaction_dir / "latest_state.json", final)
            final["result_hash"] = _sha({k: v for k, v in final.items() if k != "result_hash"})
            return final
        except OSError as exc:
            latest = self._load_json_mapping(transaction_dir / "latest_state.json") or globally_validated
            return self._i1_persist_quarantine(
                transaction_dir,
                latest,
                [f"commit_io_failure:{type(exc).__name__}"],
            )
        finally:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            finally:
                lock.close()
    # ACEE6-K50-DURABLE-COMMIT-END

    # ACEE6-I1-CRASH-RECOVERY-BEGIN
    def _i1_validate_journal(self, transaction_dir: Path) -> Tuple[list[Dict[str, Any]], list[str]]:
        """Validate the durable journal and its cryptographic chain."""
        journal_path = transaction_dir / "journal.jsonl"
        reasons: list[str] = []
        if not journal_path.is_file():
            return [], ["journal_missing"]
        records: list[Dict[str, Any]] = []
        previous_hash: Optional[str] = None
        try:
            raw_lines = journal_path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            return [], [f"journal_unreadable:{type(exc).__name__}"]
        for index, line in enumerate(raw_lines):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                reasons.append(f"journal_json_invalid:{index}")
                break
            if not isinstance(record, Mapping):
                reasons.append(f"journal_record_not_mapping:{index}")
                break
            record = dict(record)
            stored_hash = str(record.get("record_hash") or "").lower()
            payload = {key: value for key, value in record.items() if key != "record_hash"}
            if not _valid_sha(stored_hash) or stored_hash != _sha(payload):
                reasons.append(f"journal_record_hash_invalid:{index}")
            stored_previous = record.get("previous_record_hash")
            if index == 0:
                if stored_previous not in (None, ""):
                    reasons.append("journal_genesis_previous_hash_invalid")
            elif str(stored_previous or "").lower() != str(previous_hash or "").lower():
                reasons.append(f"journal_chain_divergence:{index}")
            previous_hash = stored_hash
            records.append(record)
        if not records and not reasons:
            reasons.append("journal_empty")
        return records, sorted(set(reasons))

    def _i1_persist_quarantine(
        self,
        transaction_dir: Path,
        latest: Mapping[str, Any],
        reasons: list[str],
    ) -> Dict[str, Any]:
        """Persist STATE_CORRUPTED -> QUARANTINE without claiming rollback."""
        transaction_id = str(latest.get("transaction_id") or transaction_dir.name)
        journal_path = transaction_dir / "journal.jsonl"
        previous_hash = str(latest.get("latest_record_hash") or "") or None
        final_hash = previous_hash
        try:
            corrupted_hash = self._append_journal_record(
                journal_path,
                {
                    "transaction_id": transaction_id,
                    "proposal_id": latest.get("proposal_id"),
                    "state": "STATE_CORRUPTED",
                    "blocking_reasons": sorted(set(reasons)),
                    "timestamp_utc": self.now_utc.isoformat(),
                },
                previous_hash,
            )
            final_hash = self._append_journal_record(
                journal_path,
                {
                    "transaction_id": transaction_id,
                    "proposal_id": latest.get("proposal_id"),
                    "state": "QUARANTINE",
                    "blocking_reasons": sorted(set(reasons)),
                    "timestamp_utc": self.now_utc.isoformat(),
                },
                corrupted_hash,
            )
        except OSError as exc:
            reasons = sorted(set(reasons + [f"quarantine_journal_write_failed:{type(exc).__name__}"]))
        result = dict(latest)
        result.update({
            "primitive": PRIMITIVE,
            "stage": "ACEE6-I1",
            "public_schema_version": "0.13.0",
            "status": "ACEE6_CRASH_RECOVERY_QUARANTINED",
            "transaction_state": "QUARANTINE",
            "transaction_id": transaction_id,
            "crash_recovery_complete": True,
            "crash_recovery_action": "quarantine",
            "rollback_executed": False,
            "rollback_verified": False,
            "quarantined": True,
            "retry_allowed": False,
            "partial_success": False,
            "committed": False,
            "blocking_reasons": sorted(set(reasons)),
            "latest_record_hash": final_hash,
            "timestamp_utc": self.now_utc.isoformat(),
        })
        result.pop("state_hash", None)
        result["state_hash"] = _sha(result)
        try:
            self._atomic_json_write(transaction_dir / "latest_state.json", result)
        except OSError:
            pass
        result["result_hash"] = _sha({k: v for k, v in result.items() if k != "result_hash"})
        return result

    def recover_transaction(
        self,
        transaction_id: str,
        inputs: Optional[Mapping[str, Any]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        """Classify and recover one interrupted ACEE6 transaction.

        Read-only by default. With persist=True, post-mutation states invoke the
        already validated ACEE6-G2/ACEE11 rollback path. Corrupt or unknown
        states are quarantined. PREPARED and other pre-mutation states are left
        resumable and never mutated by recovery itself.
        """
        transaction_id = str(transaction_id or "").strip()
        base: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-I1",
            "public_schema_version": "0.13.0",
            "transaction_id": transaction_id,
            "crash_recovery_complete": False,
            "persistence_performed": False,
            "committed": False,
            "partial_success": False,
        }
        if not transaction_id or Path(transaction_id).name != transaction_id:
            base.update({
                "status": "ACEE6_CRASH_RECOVERY_REJECTED",
                "transaction_state": "STATE_CORRUPTED",
                "blocking_reasons": ["transaction_id_invalid"],
            })
            base["result_hash"] = _sha(base)
            return base
        transaction_dir = self._transaction_runtime_root() / transaction_id
        latest = self._load_json_mapping(transaction_dir / "latest_state.json")
        if latest is None:
            base.update({
                "status": "ACEE6_CRASH_RECOVERY_REJECTED",
                "transaction_state": "STATE_CORRUPTED",
                "blocking_reasons": ["latest_state_missing_or_invalid"],
            })
            base["result_hash"] = _sha(base)
            return base

        records, reasons = self._i1_validate_journal(transaction_dir)
        latest_payload = {k: v for k, v in latest.items() if k != "state_hash"}
        if not _valid_sha(latest.get("state_hash")) or str(latest.get("state_hash")).lower() != _sha(latest_payload):
            reasons.append("latest_state_hash_invalid")
        if records:
            journal_state = str(records[-1].get("state") or "")
            latest_state = str(latest.get("transaction_state") or "")
            if journal_state != latest_state:
                reasons.append("latest_state_journal_divergence")
            if str(latest.get("latest_record_hash") or "").lower() != str(records[-1].get("record_hash") or "").lower():
                reasons.append("latest_record_hash_divergence")
        state = str(latest.get("transaction_state") or "")
        terminal = {"ROLLED_BACK", "QUARANTINE", "COMMITTED", "REJECTED"}
        pre_mutation = {"PREPARING", "PREPARED", "BACKING_UP", "BACKED_UP"}
        post_mutation = {
            "MUTATING", "MUTATED", "COMPILING", "COMPILED",
            "INVENTORY_UPDATING", "INVENTORIES_UPDATED", "TESTING",
            "LOCALLY_VALIDATED", "GLOBAL_VALIDATION_RUNNING", "GLOBAL_VALIDATED",
            "COMMITTING", "REPORTING", "FAULT_INJECTED",
        }
        known = terminal | pre_mutation | post_mutation
        if state not in known:
            reasons.append(f"transaction_state_unknown:{state or '<empty>'}")
        reasons = sorted(set(reasons))
        if reasons:
            if persist:
                return self._i1_persist_quarantine(transaction_dir, latest, reasons)
            result = dict(base)
            result.update({
                "status": "ACEE6_CRASH_RECOVERY_REJECTED",
                "transaction_state": "STATE_CORRUPTED",
                "observed_transaction_state": state,
                "crash_recovery_action": "quarantine_required",
                "blocking_reasons": reasons,
                "quarantined": False,
            })
            result["result_hash"] = _sha(result)
            return result
        if state in terminal:
            result = dict(latest)
            result.update({
                "stage": "ACEE6-I1",
                "public_schema_version": "0.13.0",
                "status": "ACEE6_CRASH_RECOVERY_NOT_REQUIRED",
                "crash_recovery_complete": True,
                "crash_recovery_action": "none_terminal_state",
                "persistence_performed": False,
            })
            result["result_hash"] = _sha({k: v for k, v in result.items() if k != "result_hash"})
            return result
        if state in pre_mutation:
            result = dict(latest)
            result.update({
                "stage": "ACEE6-I1",
                "public_schema_version": "0.13.0",
                "status": "ACEE6_CRASH_RECOVERY_COMPLETE",
                "crash_recovery_complete": True,
                "crash_recovery_action": "resume_safe",
                "resume_from_state": state,
                "rollback_required": False,
                "retry_allowed": True,
                "persistence_performed": False,
            })
            result["result_hash"] = _sha({k: v for k, v in result.items() if k != "result_hash"})
            return result
        if not persist:
            result = dict(latest)
            result.update({
                "stage": "ACEE6-I1",
                "public_schema_version": "0.13.0",
                "status": "ACEE6_CRASH_RECOVERY_ROLLBACK_REQUIRED",
                "crash_recovery_complete": False,
                "crash_recovery_action": "rollback_required",
                "rollback_required": True,
                "retry_allowed": False,
                "persistence_performed": False,
            })
            result["result_hash"] = _sha({k: v for k, v in result.items() if k != "result_hash"})
            return result
        failure = dict(latest)
        failure.update({
            "stage": "ACEE6-I1",
            "status": "ACEE6_CRASH_DETECTED",
            "fault_point": "crash_recovery",
            "rollback_required": True,
            "committed": False,
            "partial_success": False,
        })
        recovered = self._g2_rollback_fault(failure)
        recovered.update({
            "stage": "ACEE6-I1",
            "public_schema_version": "0.13.0",
            "status": (
                "ACEE6_CRASH_RECOVERY_ROLLED_BACK"
                if recovered.get("transaction_state") == "ROLLED_BACK"
                else "ACEE6_CRASH_RECOVERY_QUARANTINED"
            ),
            "crash_recovery_complete": True,
            "crash_recovery_action": (
                "rollback"
                if recovered.get("transaction_state") == "ROLLED_BACK"
                else "quarantine"
            ),
            "retry_allowed": False,
            "partial_success": False,
            "committed": False,
            "persistence_performed": True,
        })
        recovered.pop("result_hash", None)
        recovered["result_hash"] = _sha(recovered)
        return recovered

    def recover_incomplete_transactions(
        self,
        inputs_by_transaction: Optional[Mapping[str, Mapping[str, Any]]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        """Recover all durable non-terminal transactions in lexical order."""
        runtime_root = self._transaction_runtime_root()
        results: list[Dict[str, Any]] = []
        if runtime_root.is_dir():
            for transaction_dir in sorted(runtime_root.iterdir(), key=lambda p: p.name):
                if not transaction_dir.is_dir() or transaction_dir.is_symlink():
                    continue
                supplied = _mapping(_mapping(inputs_by_transaction).get(transaction_dir.name))
                results.append(self.recover_transaction(transaction_dir.name, supplied, persist=persist))
        summary = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-I1",
            "public_schema_version": "0.13.0",
            "status": "ACEE6_CRASH_RECOVERY_SCAN_COMPLETE",
            "transactions_scanned": len(results),
            "transactions": results,
            "persistence_performed": bool(persist),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
        }
        summary["result_hash"] = _sha(summary)
        return summary
    # ACEE6-I1-CRASH-RECOVERY-END

    # ACEE6-I2-REPLAY-BEGIN
    # ACEE6-I2-CANONICAL-IDENTIFIER-BEGIN
    @staticmethod
    def _i2_canonical_identifier(value: Any) -> str:
        """Canonical identifier for duplicate detection only."""
        return unicodedata.normalize("NFC", str(value or "")).casefold()
    # ACEE6-I2-CANONICAL-IDENTIFIER-END

    def _i2_transaction_identity(self, transaction_id: str, latest: Mapping[str, Any]) -> Dict[str, str]:
        return {
            "transaction_id": str(latest.get("transaction_id") or transaction_id),
            "proposal_id": str(latest.get("proposal_id") or ""),
            "proposal_key": self._i2_canonical_identifier(latest.get("proposal_id") or ""),
            "manifest_hash": str(latest.get("manifest_hash") or "").lower(),
            "plan_hash": str(latest.get("plan_hash") or "").lower(),
        }

    def _i2_durable_transaction_index(self) -> Dict[str, Any]:
        runtime_root = self._transaction_runtime_root()
        transactions: Dict[str, Dict[str, str]] = {}
        proposals: Dict[str, list[Dict[str, str]]] = {}
        invalid_entries: list[str] = []
        if runtime_root.is_dir():
            for transaction_dir in sorted(runtime_root.iterdir(), key=lambda path: path.name):
                if not transaction_dir.is_dir() or transaction_dir.is_symlink():
                    continue
                latest = self._load_json_mapping(transaction_dir / "latest_state.json")
                if latest is None:
                    invalid_entries.append(transaction_dir.name)
                    continue
                identity = self._i2_transaction_identity(transaction_dir.name, latest)
                transactions[transaction_dir.name] = identity
                if identity["proposal_key"]:
                    proposals.setdefault(identity["proposal_key"], []).append(identity)
        for proposal_id in proposals:
            proposals[proposal_id] = sorted(
                proposals[proposal_id],
                key=lambda item: (item["transaction_id"], item["manifest_hash"], item["plan_hash"]),
            )
        result: Dict[str, Any] = {
            "transactions": transactions,
            "proposals": proposals,
            "invalid_entries": sorted(invalid_entries),
        }
        result["index_hash"] = _sha(result)
        return result

    def inspect_replay(
        self,
        transaction_id: str,
        proposal_id: Optional[str] = None,
        manifest_hash: Optional[str] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        transaction_id = str(transaction_id or "").strip()
        expected_proposal = str(proposal_id or "").strip()
        expected_manifest = str(manifest_hash or "").strip().lower()
        base: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-I2",
            "public_schema_version": "0.14.0",
            "transaction_id": transaction_id,
            "proposal_id": expected_proposal,
            "manifest_hash": expected_manifest,
            "replay_executed": False,
            "candidate_executed": False,
            "inventory_modified": False,
            "tests_executed": False,
            "global_validation_executed": False,
            "committed": False,
            "partial_success": False,
            "persistence_performed": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
        }
        if not transaction_id or Path(transaction_id).name != transaction_id:
            base.update({
                "status": "ACEE6_REPLAY_REJECTED",
                "replay_classification": "invalid_transaction_id",
                "blocking_reasons": ["transaction_id_invalid"],
            })
            base["result_hash"] = _sha(base)
            return base

        transaction_dir = self._transaction_runtime_root() / transaction_id
        latest = self._load_json_mapping(transaction_dir / "latest_state.json")
        index = self._i2_durable_transaction_index()
        if latest is None:
            proposal_matches = list(index["proposals"].get(self._i2_canonical_identifier(expected_proposal), [])) if expected_proposal else []
            reasons = ["transaction_not_found"]
            classification = "unknown_transaction"
            if proposal_matches:
                reasons.append("duplicate_proposal_different_transaction")
                classification = "proposal_collision"
            base.update({
                "status": "ACEE6_REPLAY_REJECTED",
                "replay_classification": classification,
                "blocking_reasons": sorted(reasons),
                "proposal_matches": proposal_matches,
                "durable_index_hash": index["index_hash"],
            })
            base["result_hash"] = _sha(base)
            return base

        recovery_audit = self.recover_transaction(transaction_id, persist=False)
        if recovery_audit.get("transaction_state") == "STATE_CORRUPTED":
            base.update({
                "status": "ACEE6_REPLAY_REJECTED",
                "replay_classification": "state_divergence",
                "blocking_reasons": sorted(set(list(recovery_audit.get("blocking_reasons") or []))),
                "durable_index_hash": index["index_hash"],
            })
            base["result_hash"] = _sha(base)
            return base

        identity = self._i2_transaction_identity(transaction_id, latest)
        reasons: list[str] = []
        if identity["transaction_id"] != transaction_id:
            reasons.append("duplicate_transaction_identity_divergence")
        if expected_proposal and identity["proposal_key"] != self._i2_canonical_identifier(expected_proposal):
            reasons.append("proposal_id_replay_divergence")
        if expected_manifest and identity["manifest_hash"] != expected_manifest:
            reasons.append("manifest_hash_replay_divergence")
        proposal_matches = list(index["proposals"].get(identity["proposal_key"], []))
        distinct = {
            (item["transaction_id"], item["manifest_hash"], item["plan_hash"])
            for item in proposal_matches
        }
        if len(distinct) > 1:
            reasons.append("duplicate_proposal_collision")
        if reasons:
            result = dict(base)
            result.update({
                "status": "ACEE6_REPLAY_REJECTED",
                "replay_classification": "identity_collision",
                "observed_identity": identity,
                "proposal_matches": proposal_matches,
                "blocking_reasons": sorted(set(reasons)),
                "durable_index_hash": index["index_hash"],
            })
            result["result_hash"] = _sha(result)
            return result

        result = dict(base)
        result.update({
            "status": "ACEE6_REPLAY_VERIFIED",
            "replay_classification": "exact_idempotent_replay",
            "observed_identity": identity,
            "transaction_state": latest.get("transaction_state"),
            "replay_safe": True,
            "duplicate_transaction_detected": True,
            "duplicate_proposal_detected": bool(proposal_matches),
            "blocking_reasons": [],
            "durable_index_hash": index["index_hash"],
        })
        result["result_hash"] = _sha(result)
        return result

    def inspect_replay_registry(self, persist: bool = False) -> Dict[str, Any]:
        index = self._i2_durable_transaction_index()
        collisions = {
            proposal_id: identities
            for proposal_id, identities in sorted(index["proposals"].items())
            if len({
                (item["transaction_id"], item["manifest_hash"], item["plan_hash"])
                for item in identities
            }) > 1
        }
        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-I2",
            "public_schema_version": "0.14.0",
            "status": "ACEE6_REPLAY_REGISTRY_DIVERGED" if collisions or index["invalid_entries"] else "ACEE6_REPLAY_REGISTRY_CONSISTENT",
            "transactions_indexed": len(index["transactions"]),
            "proposals_indexed": len(index["proposals"]),
            "proposal_collisions": collisions,
            "invalid_entries": index["invalid_entries"],
            "durable_index_hash": index["index_hash"],
            "persistence_performed": False,
            "committed": False,
            "partial_success": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
        }
        result["result_hash"] = _sha(result)
        return result
    # ACEE6-I2-REPLAY-END


    # ACEE6-J1-FINAL-REPORT-BEGIN
    @staticmethod
    def _j1_duration_evidence(value: Any, prefix: str = "") -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        if isinstance(value, Mapping):
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0])):
                name = f"{prefix}.{key}" if prefix else str(key)
                lowered = str(key).casefold()
                if isinstance(item, (int, float)) and not isinstance(item, bool) and (
                    "duration" in lowered or "elapsed" in lowered
                    or lowered.endswith("_seconds") or lowered.endswith("_ns")
                ):
                    result[name] = item
                result.update(AceeInstallationExecutor._j1_duration_evidence(item, name))
        elif isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                name = f"{prefix}[{index}]"
                result.update(AceeInstallationExecutor._j1_duration_evidence(item, name))
        return result

    @staticmethod
    def _j1_embedded_hash_status(payload: Mapping[str, Any]) -> Dict[str, Any]:
        checks: Dict[str, Any] = {}
        excluded = {
            "previous_record_hash", "latest_record_hash", "state_hash",
            "result_hash", "manifest_hash", "plan_hash",
            "candidate_content_sha256", "source_sha256", "bytecode_sha256",
        }
        for field in sorted(
            key for key in payload
            if isinstance(key, str) and key.endswith("_hash") and key not in excluded
        ):
            stored = str(payload.get(field) or "").lower()
            body = {key: value for key, value in payload.items() if key != field}
            checks[field] = {
                "stored_hash": stored,
                "valid": bool(_valid_sha(stored) and stored == _sha(body)),
            }
        return checks


    # ACEE6-J1-EXTENDED-REPORT-BEGIN
    def verify_final_report(self, transaction_id: str) -> Dict[str, Any]:
        transaction_id = str(transaction_id or "").strip()
        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-J1",
            "public_schema_version": "0.15.0",
            "transaction_id": transaction_id,
            "report_verified": False,
            "persistence_performed": False,
            "committed": False,
            "partial_success": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
        }
        if not transaction_id or Path(transaction_id).name != transaction_id:
            result.update({
                "status": "ACEE6_FINAL_REPORT_VERIFICATION_REJECTED",
                "blocking_reasons": ["transaction_id_invalid"],
            })
            result["result_hash"] = _sha(result)
            return result

        report_path = self._transaction_runtime_root() / transaction_id / "final_certification_report.json"
        payload = self._load_json_mapping(report_path)
        if payload is None:
            result.update({
                "status": "ACEE6_FINAL_REPORT_VERIFICATION_REJECTED",
                "blocking_reasons": ["final_report_missing_or_invalid"],
            })
            result["result_hash"] = _sha(result)
            return result

        stored_hash = str(payload.get("final_report_hash") or "").lower()
        body = {key: value for key, value in payload.items() if key != "final_report_hash"}
        computed_hash = _sha(body)
        valid = bool(_valid_sha(stored_hash) and stored_hash == computed_hash)
        proofs = payload.get("proofs") if isinstance(payload.get("proofs"), Mapping) else {}
        result.update({
            "status": "ACEE6_FINAL_REPORT_VERIFIED" if valid else "ACEE6_FINAL_REPORT_TAMPERED",
            "report_verified": valid,
            "stored_final_report_hash": stored_hash,
            "computed_final_report_hash": computed_hash,
            "journal_tip_hash": proofs.get("journal_tip_hash"),
            "blocking_reasons": [] if valid else ["final_report_hash_invalid"],
        })
        result["result_hash"] = _sha(result)
        return result
    # ACEE6-J1-EXTENDED-REPORT-END

    def build_final_report(self, transaction_id: str, persist: bool = False) -> Dict[str, Any]:
        transaction_id = str(transaction_id or "").strip()
        base: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-J1",
            "public_schema_version": "0.15.0",
            "transaction_id": transaction_id,
            "report_complete": False,
            "candidate_executed": False,
            "rollback_executed": False,
            "tests_executed": False,
            "global_validation_executed": False,
            "persistence_performed": False,
            "committed": False,
            "partial_success": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
        }
        if not transaction_id or Path(transaction_id).name != transaction_id:
            base.update({"status": "ACEE6_FINAL_REPORT_REJECTED", "blocking_reasons": ["transaction_id_invalid"]})
            base["result_hash"] = _sha(base)
            return base

        transaction_dir = self._transaction_runtime_root() / transaction_id
        latest = self._load_json_mapping(transaction_dir / "latest_state.json")
        if latest is None:
            base.update({"status": "ACEE6_FINAL_REPORT_REJECTED", "blocking_reasons": ["latest_state_missing_or_invalid"]})
            base["result_hash"] = _sha(base)
            return base

        journal_records, journal_reasons = self._i1_validate_journal(transaction_dir)
        blocking_reasons = list(journal_reasons)
        latest_body = {key: value for key, value in latest.items() if key != "state_hash"}
        latest_hash_valid = bool(
            _valid_sha(latest.get("state_hash"))
            and str(latest.get("state_hash")).lower() == _sha(latest_body)
        )
        if not latest_hash_valid:
            blocking_reasons.append("latest_state_hash_invalid")
        if journal_records:
            if str(latest.get("latest_record_hash") or "").lower() != str(journal_records[-1].get("record_hash") or "").lower():
                blocking_reasons.append("latest_record_hash_divergence")
            if str(latest.get("transaction_state") or "") != str(journal_records[-1].get("state") or ""):
                blocking_reasons.append("latest_state_journal_divergence")

        evidence_files = []
        embedded_hash_checks: Dict[str, Any] = {}
        duration_evidence: Dict[str, Any] = {}
        json_payloads: Dict[str, Dict[str, Any]] = {}
        if transaction_dir.is_dir():
            for path in sorted(transaction_dir.rglob("*"), key=lambda item: str(item.relative_to(transaction_dir))):
                if not path.is_file() or path.is_symlink() or path.name.endswith((".lock", ".tmp")) or path.name == "final_certification_report.json":
                    continue
                relative = str(path.relative_to(transaction_dir))
                raw = path.read_bytes()
                evidence_files.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)})
                if path.suffix == ".json":
                    payload = self._load_json_mapping(path)
                    if payload is None:
                        blocking_reasons.append(f"json_evidence_invalid:{relative}")
                        continue
                    json_payloads[relative] = payload
                    checks = self._j1_embedded_hash_status(payload)
                    if checks:
                        embedded_hash_checks[relative] = checks
                        for field, check in checks.items():
                            if check["valid"] is not True:
                                blocking_reasons.append(f"embedded_hash_invalid:{relative}:{field}")
                    duration_evidence.update(self._j1_duration_evidence(payload, relative))

        local_report = json_payloads.get("local_validation_report.json", {})
        global_report = json_payloads.get("global_validation_report.json", {})
        rollback_report = json_payloads.get("rollback_report.json", {})

        test_summary = {
            "report_present": bool(local_report),
            "validation_complete": local_report.get("validation_complete"),
            "validation_passed": local_report.get("validation_passed"),
            "error_count": local_report.get("error_count"),
            "failed_commands": local_report.get("failed_commands", []),
            "timed_out_commands": local_report.get("timed_out_commands", []),
            "blocked_commands": local_report.get("blocked_commands", []),
            "report_hash": local_report.get("local_validation_report_hash"),
        }
        validation_summary = {
            "report_present": bool(global_report),
            "validation_complete": global_report.get("validation_complete"),
            "validation_passed": global_report.get("validation_passed"),
            "error_count": global_report.get("error_count"),
            "failed_calls": global_report.get("failed_calls"),
            "failed_modules": global_report.get("failed_modules", []),
            "report_hash": global_report.get("global_validation_report_hash"),
        }
        rollback_summary = {
            "report_present": bool(rollback_report),
            "rollback_executed": bool(rollback_report.get("rollback_executed") or latest.get("rollback_executed")),
            "rollback_verified": bool(rollback_report.get("rollback_verified") or latest.get("rollback_verified")),
            "rollback_report_hash": rollback_report.get("rollback_report_hash"),
            "transaction_state": latest.get("transaction_state"),
        }
        proofs = {
            "journal_chain_valid": not bool(journal_reasons),
            "journal_record_count": len(journal_records),
            "journal_tip_hash": journal_records[-1].get("record_hash") if journal_records else None,
            "latest_state_hash_valid": latest_hash_valid,
            "latest_state_hash": latest.get("state_hash"),
            "latest_record_hash": latest.get("latest_record_hash"),
            "embedded_hash_checks": embedded_hash_checks,
            "evidence_manifest_hash": _sha(evidence_files),
        }
        terminal_state = str(latest.get("transaction_state") or "")
        if terminal_state in {"GLOBAL_VALIDATED", "COMMITTED"}:
            if not local_report:
                blocking_reasons.append("local_validation_report_missing")
            if not global_report:
                blocking_reasons.append("global_validation_report_missing")
        if terminal_state == "ROLLED_BACK":
            if not rollback_report:
                blocking_reasons.append("rollback_report_missing")
            elif rollback_summary["rollback_verified"] is not True:
                blocking_reasons.append("rollback_not_verified")

        acceptable_states = {"GLOBAL_VALIDATED", "COMMITTED", "ROLLED_BACK", "QUARANTINE", "REJECTED"}
        if terminal_state not in acceptable_states:
            blocking_reasons.append(f"transaction_not_final:{terminal_state or '<empty>'}")
        blocking_reasons = sorted(set(blocking_reasons))

        report = dict(base)
        report.update({
            "status": "ACEE6_FINAL_REPORT_COMPLETE" if not blocking_reasons else "ACEE6_FINAL_REPORT_INCOMPLETE",
            "transaction_state": terminal_state,
            "proposal_id": latest.get("proposal_id"),
            "manifest_hash": latest.get("manifest_hash"),
            "plan_hash": latest.get("plan_hash"),
            "transaction": {
                "transaction_id": transaction_id,
                "proposal_id": latest.get("proposal_id"),
                "transaction_state": terminal_state,
                "latest_record_hash": latest.get("latest_record_hash"),
                "state_hash": latest.get("state_hash"),
            },
            "hashes": {
                "manifest_hash": latest.get("manifest_hash"),
                "plan_hash": latest.get("plan_hash"),
                "latest_record_hash": latest.get("latest_record_hash"),
                "state_hash": latest.get("state_hash"),
                "evidence_manifest_hash": proofs["evidence_manifest_hash"],
            },
            "rollback": rollback_summary,
            "tests": test_summary,
            "validation": validation_summary,
            "durations": duration_evidence,
            "proofs": proofs,
            "evidence_files": evidence_files,
            "blocking_reasons": blocking_reasons,
            "report_complete": not bool(blocking_reasons),
            "tests_executed": bool(local_report or latest.get("tests_executed")),
            "global_validation_executed": bool(global_report or latest.get("global_validation_executed")),
            "rollback_executed": rollback_summary["rollback_executed"],
            "committed": terminal_state == "COMMITTED",
            "timestamp_utc": self.now_utc.isoformat(),
        })
        report["final_report_hash"] = _sha(report)
        if persist:
            report_path = transaction_dir / "final_certification_report.json"
            self._atomic_json_write(report_path, report)
            report["final_report_path"] = str(report_path)
            report["persistence_performed"] = True
        report["result_hash"] = _sha({key: value for key, value in report.items() if key != "result_hash"})
        return report
    # ACEE6-J1-FINAL-REPORT-END


    # ACEE6-J2-ESCALATION-BEGIN
    # ACEE6-J2-HARDENING-V1
    def _j2_gate_path(self) -> Path:
        return self._transaction_runtime_root() / J2_GATE_FILENAME

    def _j2_diagnostic_path(self, transaction_dir: Path) -> Path:
        return transaction_dir / J2_DIAGNOSTIC_FILENAME

    def _j2_verify_hashed_payload(
        self,
        payload: Optional[Mapping[str, Any]],
        hash_field: str,
    ) -> Tuple[bool, list[str]]:
        if payload is None:
            return False, ["payload_missing_or_invalid"]
        supplied = payload.get(hash_field)
        body = {key: value for key, value in payload.items() if key != hash_field}
        if not _valid_sha(supplied):
            return False, [f"{hash_field}_missing_or_invalid"]
        if str(supplied).lower() != _sha(body):
            return False, [f"{hash_field}_mismatch"]
        return True, []

    def inspect_escalation_gate(self) -> Dict[str, Any]:
        """Vérifie le verrou J2 et le diagnostic auquel il est lié.

        Une absence de verrou signifie non-bloqué. Toute corruption du verrou,
        du diagnostic, ou de leur liaison est traitée fail-closed.
        """
        path = self._j2_gate_path()
        base: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-J2",
            "public_schema_version": J2_PUBLIC_SCHEMA_VERSION,
            "gate_path": str(path),
            "persistence_performed": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
        }
        if not path.exists():
            base.update({
                "status": "ACEE6_J2_INSTALLATION_UNBLOCKED",
                "installation_blocked": False,
                "gate_present": False,
                "gate_integrity_verified": True,
                "diagnostic_integrity_verified": True,
                "blocking_reasons": [],
            })
            base["result_hash"] = _sha(base)
            return base

        gate = self._load_json_mapping(path)
        gate_valid, gate_reasons = self._j2_verify_hashed_payload(gate, "gate_hash")
        reasons = list(gate_reasons)
        diagnostic_valid = False
        diagnostic = None
        if gate_valid and gate is not None:
            diagnostic_path_text = str(gate.get("diagnostic_path") or "")
            diagnostic_path = Path(diagnostic_path_text) if diagnostic_path_text else None
            try:
                runtime_root = self._transaction_runtime_root().resolve(strict=True)
                resolved = diagnostic_path.resolve(strict=False) if diagnostic_path is not None else None
                if resolved is None or runtime_root not in resolved.parents:
                    reasons.append("diagnostic_path_invalid")
                else:
                    diagnostic = self._load_json_mapping(resolved)
                    diagnostic_valid, diagnostic_reasons = self._j2_verify_hashed_payload(
                        diagnostic, "diagnostic_hash"
                    )
                    reasons.extend(diagnostic_reasons)
                    if diagnostic_valid and diagnostic is not None:
                        if diagnostic.get("diagnostic_hash") != gate.get("diagnostic_hash"):
                            reasons.append("diagnostic_gate_hash_divergence")
                        if diagnostic.get("transaction_id") != gate.get("transaction_id"):
                            reasons.append("diagnostic_gate_transaction_divergence")
            except OSError:
                reasons.append("diagnostic_path_unresolvable")
        if not gate_valid:
            reasons.insert(0, "escalation_gate_corrupted")
        elif reasons:
            reasons.insert(0, "escalation_diagnostic_corrupted")

        if reasons:
            base.update({
                "status": J2_BLOCKED_STATUS,
                "installation_blocked": True,
                "gate_present": True,
                "gate_integrity_verified": gate_valid,
                "diagnostic_integrity_verified": False,
                "transaction_id": gate.get("transaction_id") if gate else None,
                "blocking_reasons": sorted(set(reasons)),
                "retry_allowed": False,
                "manual_governance_required": True,
            })
            base["result_hash"] = _sha(base)
            return base

        active = gate.get("installation_blocked") is True
        base.update(dict(gate))
        base.update({
            "status": J2_BLOCKED_STATUS if active else "ACEE6_J2_INSTALLATION_UNBLOCKED",
            "installation_blocked": active,
            "gate_present": True,
            "gate_integrity_verified": True,
            "diagnostic_integrity_verified": diagnostic_valid,
            "persistence_performed": False,
        })
        base["result_hash"] = _sha({k: v for k, v in base.items() if k != "result_hash"})
        return base


    def _j2_classify_escalation(
        self,
        transaction_dir: Path,
        latest: Mapping[str, Any],
    ) -> Tuple[list[str], Dict[str, Any]]:
        records, journal_reasons = self._i1_validate_journal(transaction_dir)
        reasons = list(journal_reasons)
        latest_body = {key: value for key, value in latest.items() if key != "state_hash"}
        latest_hash_valid = bool(
            _valid_sha(latest.get("state_hash"))
            and str(latest.get("state_hash")).lower() == _sha(latest_body)
        )
        if not latest_hash_valid:
            reasons.append("latest_state_hash_invalid")
        state = str(latest.get("transaction_state") or "")
        known_states = {
            "PREPARING", "PREPARED", "BACKING_UP", "BACKED_UP",
            "MUTATING", "MUTATED", "COMPILING", "COMPILED",
            "INVENTORY_UPDATING", "INVENTORIES_UPDATED", "TESTING",
            "LOCALLY_VALIDATED", "GLOBAL_VALIDATION_RUNNING", "GLOBAL_VALIDATED",
            "COMMITTING", "COMMITTED", "REPORTING", "FAULT_INJECTED",
            "ROLLED_BACK", "QUARANTINE", "REJECTED", "STATE_CORRUPTED",
        }
        if state not in known_states:
            reasons.append(f"transaction_state_unknown:{state or '<empty>'}")
        if records:
            journal_state = str(records[-1].get("state") or "")
            if journal_state != state:
                reasons.append("latest_state_journal_divergence")
            if str(latest.get("latest_record_hash") or "").lower() != str(records[-1].get("record_hash") or "").lower():
                reasons.append("latest_record_hash_divergence")
        rollback_impossible = bool(
            state == "QUARANTINE"
            and (
                latest.get("rollback_verified") is not True
                or latest.get("rollback_executed") is not True
                or latest.get("quarantined") is True
            )
        )
        if rollback_impossible:
            reasons.append("rollback_impossible_or_unverified")
        if state == "STATE_CORRUPTED":
            reasons.append("state_corrupted")
        classification = {
            "observed_transaction_state": state,
            "journal_chain_valid": not bool(journal_reasons),
            "journal_tip_hash": records[-1].get("record_hash") if records else None,
            "journal_record_count": len(records),
            "latest_state_hash_valid": latest_hash_valid,
            "latest_state_hash": latest.get("state_hash"),
            "latest_record_hash": latest.get("latest_record_hash"),
            "rollback_impossible": rollback_impossible,
        }
        return sorted(set(reasons)), classification

    def escalate_transaction(
        self,
        transaction_id: str,
        persist: bool = False,
    ) -> Dict[str, Any]:
        """Escalade un état irrécupérable avec idempotence et exclusion mutuelle."""
        transaction_id = str(transaction_id or "").strip()
        base: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "stage": "ACEE6-J2",
            "public_schema_version": J2_PUBLIC_SCHEMA_VERSION,
            "transaction_id": transaction_id,
            "installation_blocked": False,
            "quarantined": False,
            "diagnostic_complete": False,
            "rollback_executed": False,
            "rollback_verified": False,
            "retry_allowed": False,
            "manual_governance_required": False,
            "partial_success": False,
            "committed": False,
            "persistence_performed": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
        }
        if not transaction_id or Path(transaction_id).name != transaction_id:
            base.update({
                "status": "ACEE6_J2_ESCALATION_REJECTED",
                "blocking_reasons": ["transaction_id_invalid"],
            })
            base["result_hash"] = _sha(base)
            return base

        transaction_dir = self._transaction_runtime_root() / transaction_id
        latest = self._load_json_mapping(transaction_dir / "latest_state.json")
        if latest is None:
            base.update({
                "status": "ACEE6_J2_ESCALATION_REJECTED",
                "blocking_reasons": ["latest_state_missing_or_invalid"],
                "escalation_required": True,
            })
            base["result_hash"] = _sha(base)
            return base

        reasons, classification = self._j2_classify_escalation(transaction_dir, latest)
        if not reasons:
            base.update(classification)
            base.update({
                "status": J2_NOT_REQUIRED_STATUS,
                "escalation_required": False,
                "blocking_reasons": [],
                "diagnostic_complete": True,
            })
            base["result_hash"] = _sha(base)
            return base

        def build_payloads() -> Tuple[Dict[str, Any], Dict[str, Any]]:
            diagnostic = {
                "primitive": PRIMITIVE,
                "stage": "ACEE6-J2",
                "public_schema_version": J2_PUBLIC_SCHEMA_VERSION,
                "status": J2_ESCALATED_STATUS,
                "transaction_id": transaction_id,
                "proposal_id": latest.get("proposal_id"),
                "manifest_hash": latest.get("manifest_hash"),
                "plan_hash": latest.get("plan_hash"),
                "transaction_state": "QUARANTINE",
                "observed_transaction_state": classification.get("observed_transaction_state"),
                "escalation_required": True,
                "diagnostic_complete": True,
                "installation_blocked": True,
                "quarantined": True,
                "rollback_executed": False,
                "rollback_verified": False,
                "retry_allowed": False,
                "automatic_repair_attempted": False,
                "manual_governance_required": True,
                "partial_success": False,
                "committed": False,
                "blocking_reasons": reasons,
                "evidence": classification,
                "timestamp_utc": self.now_utc.isoformat(),
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "consciousness_proven": False,
                "subjectivity_proven": False,
                "qualia_proven": False,
                "phenomenology_proven": False,
            }
            diagnostic["diagnostic_hash"] = _sha(diagnostic)
            gate = {
                "primitive": PRIMITIVE,
                "stage": "ACEE6-J2",
                "public_schema_version": J2_PUBLIC_SCHEMA_VERSION,
                "status": J2_BLOCKED_STATUS,
                "installation_blocked": True,
                "transaction_id": transaction_id,
                "diagnostic_hash": diagnostic["diagnostic_hash"],
                "diagnostic_path": str(self._j2_diagnostic_path(transaction_dir)),
                "blocking_reasons": reasons,
                "retry_allowed": False,
                "manual_governance_required": True,
                "created_at_utc": self.now_utc.isoformat(),
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
            }
            gate["gate_hash"] = _sha(gate)
            return diagnostic, gate

        def result_from(diagnostic: Mapping[str, Any], gate: Mapping[str, Any], replayed: bool) -> Dict[str, Any]:
            result = dict(base)
            result.update(dict(diagnostic))
            result.update({
                "gate_hash": gate.get("gate_hash"),
                "gate_path": str(self._j2_gate_path()),
                "diagnostic_path": str(self._j2_diagnostic_path(transaction_dir)),
                "escalation_replayed": replayed,
                "persistence_performed": bool(persist and not replayed),
            })
            result["result_hash"] = _sha({k: v for k, v in result.items() if k != "result_hash"})
            return result

        if not persist:
            diagnostic, gate = build_payloads()
            return result_from(diagnostic, gate, False)

        runtime_root = self._transaction_runtime_root()
        self._take_filesystem_effect_context("FS_CREATE_DIR", runtime_root)
        lock_path = runtime_root / ".j2_escalation.lock"
        with lock_path.open("a+", encoding="utf-8") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            try:
                existing_gate = self._load_json_mapping(self._j2_gate_path())
                gate_valid, _ = self._j2_verify_hashed_payload(existing_gate, "gate_hash")
                if gate_valid and existing_gate is not None and existing_gate.get("installation_blocked") is True:
                    existing_diagnostic = self._load_json_mapping(Path(str(existing_gate.get("diagnostic_path") or "")))
                    diagnostic_valid, _ = self._j2_verify_hashed_payload(existing_diagnostic, "diagnostic_hash")
                    if diagnostic_valid and existing_diagnostic is not None and existing_diagnostic.get("diagnostic_hash") == existing_gate.get("diagnostic_hash"):
                        return result_from(existing_diagnostic, existing_gate, True)
                    blocked = self.inspect_escalation_gate()
                    blocked.update({
                        "escalation_replayed": True,
                        "persistence_performed": False,
                    })
                    blocked["result_hash"] = _sha({k: v for k, v in blocked.items() if k != "result_hash"})
                    return blocked

                diagnostic, gate = build_payloads()
                self._atomic_json_write(self._j2_diagnostic_path(transaction_dir), diagnostic)
                self._atomic_json_write(self._j2_gate_path(), gate)
                return result_from(diagnostic, gate, False)
            finally:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)

    # ACEE6-J2-ESCALATION-END

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        requested_stage = self._requested_stage(inputs)
        if requested_stage == "ACEE6-J2":
            context = _mapping(_mapping(inputs).get("admission_context"))
            transaction_id = str(
                context.get("transaction_id")
                or _mapping(inputs).get("transaction_id")
                or ""
            )
            return self.escalate_transaction(transaction_id, persist=persist)
        gate = self.inspect_escalation_gate()
        if gate.get("installation_blocked") is True:
            blocked = dict(gate)
            blocked.update({
                "primitive": PRIMITIVE,
                "stage": "ACEE6-J2",
                "public_schema_version": J2_PUBLIC_SCHEMA_VERSION,
                "status": J2_BLOCKED_STATUS,
                "admissible": False,
                "read_only": not persist,
                "persistence_performed": False,
                "candidate_executed": False,
                "inventory_modified": False,
                "tests_executed": False,
                "global_validation_executed": False,
                "rollback_executed": False,
                "committed": False,
                "partial_success": False,
                "retry_allowed": False,
            })
            blocked["result_hash"] = _sha({k: v for k, v in blocked.items() if k != "result_hash"})
            return blocked
        admitted = self._admit_and_dry_run(inputs=inputs, persist=False)
        if not persist or not admitted.get("admissible"):
            return admitted



        # ACEE6-K50-DURABLE-COMMIT-BRANCH-BEGIN
        if requested_stage == "ACEE6-K5.0":
            transaction_id = self._transaction_id(admitted)
            transaction_dir = self._transaction_runtime_root() / transaction_id
            replay = self._k50_validate_committed_replay(transaction_dir, admitted)
            if replay is not None:
                return replay
            f2_inputs = deepcopy(dict(inputs) if isinstance(inputs, Mapping) else {})
            f2_context = _mapping(f2_inputs.get("admission_context"))
            f2_context["requested_stage"] = "ACEE6-F2"
            f2_inputs["admission_context"] = f2_context
            globally_validated = self.step(inputs=f2_inputs, persist=True)
            if globally_validated.get("transaction_state") == "GLOBALLY_VALIDATED":
                return self._k50_commit_transaction(globally_validated, admitted)
            return globally_validated
        # ACEE6-K50-DURABLE-COMMIT-BRANCH-END

        if requested_stage == "ACEE6-F2":
            transaction_id = self._transaction_id(admitted)
            transaction_dir = self._transaction_runtime_root() / transaction_id
            replay = self._validate_global_validation_replay(transaction_dir, admitted)
            if replay is not None:
                return replay
            f1_inputs = deepcopy(dict(inputs) if isinstance(inputs, Mapping) else {})
            f1_context = _mapping(f1_inputs.get("admission_context"))
            f1_context["requested_stage"] = "ACEE6-F1"
            f1_inputs["admission_context"] = f1_context
            locally_validated = self.step(inputs=f1_inputs, persist=True)
            if locally_validated.get("transaction_state") == "LOCALLY_VALIDATED":
                result = self._run_global_validation_f2(locally_validated, inputs)
                result = self._fault_injection_boundary(result, inputs, "validation.main")
                if result.get("transaction_state") == "FAULT_INJECTED":
                    return result
                return self._fault_injection_boundary(result, inputs, "report")
            return locally_validated

        if requested_stage == "ACEE6-F1":
            transaction_id = self._transaction_id(admitted)
            transaction_dir = self._transaction_runtime_root() / transaction_id
            replay = self._validate_local_validation_replay(transaction_dir, admitted)
            if replay is not None:
                return replay
            e_inputs = deepcopy(dict(inputs) if isinstance(inputs, Mapping) else {})
            e_context = _mapping(e_inputs.get("admission_context"))
            e_context["requested_stage"] = "ACEE6-E"
            e_inputs["admission_context"] = e_context
            inventories_updated = self.step(inputs=e_inputs, persist=True)
            if inventories_updated.get("transaction_state") == "INVENTORIES_UPDATED":
                result = self._run_local_validation_f1(inventories_updated, inputs)
                return self._fault_injection_boundary(result, inputs, "tests")
            return inventories_updated

        if requested_stage == "ACEE6-E":
            transaction_id = self._transaction_id(admitted)
            transaction_dir = (
                self._transaction_runtime_root() / transaction_id
            )
            latest_path = transaction_dir / "latest_state.json"
            latest = self._load_json_mapping(latest_path)

            if (
                latest is not None
                and latest.get("transaction_state")
                == "INVENTORIES_UPDATED"
            ):
                reasons = []

                latest_hash = latest.get("state_hash")
                latest_payload = {
                    key: value
                    for key, value in latest.items()
                    if key != "state_hash"
                }
                if (
                    not _valid_sha(latest_hash)
                    or str(latest_hash).lower()
                    != _sha(latest_payload)
                ):
                    reasons.append(
                        "existing_inventory_latest_state_hash_invalid"
                    )

                snapshot_path = (
                    self._inventory_snapshot_manifest_path(
                        transaction_dir
                    )
                )
                snapshot = self._load_json_mapping(snapshot_path)
                if snapshot is None:
                    reasons.append(
                        "existing_inventory_snapshot_manifest_missing"
                    )
                else:
                    snapshot_hash = snapshot.get(
                        "snapshot_manifest_hash"
                    )
                    snapshot_payload = {
                        key: value
                        for key, value in snapshot.items()
                        if key != "snapshot_manifest_hash"
                    }
                    if (
                        not _valid_sha(snapshot_hash)
                        or str(snapshot_hash).lower()
                        != _sha(snapshot_payload)
                    ):
                        reasons.append(
                            "existing_inventory_snapshot_manifest_hash_invalid"
                        )

                update_path = (
                    self._inventory_update_manifest_path(
                        transaction_dir
                    )
                )
                update = self._load_json_mapping(update_path)
                if update is None:
                    reasons.append(
                        "existing_inventory_update_manifest_missing"
                    )
                else:
                    update_hash = update.get(
                        "inventory_update_manifest_hash"
                    )
                    update_payload = {
                        key: value
                        for key, value in update.items()
                        if key
                        != "inventory_update_manifest_hash"
                    }
                    if (
                        not _valid_sha(update_hash)
                        or str(update_hash).lower()
                        != _sha(update_payload)
                    ):
                        reasons.append(
                            "existing_inventory_update_manifest_hash_invalid"
                        )
                    if (
                        latest.get(
                            "inventory_update_manifest_hash"
                        )
                        != update_hash
                    ):
                        reasons.append(
                            "existing_inventory_latest_manifest_divergence"
                        )

                    for item in update.get("files", []):
                        if not isinstance(item, Mapping):
                            reasons.append(
                                "existing_inventory_file_record_invalid"
                            )
                            continue
                        relative = str(item.get("path") or "")
                        expected = str(
                            item.get("after_sha256") or ""
                        ).lower()
                        path = self.root / relative
                        try:
                            real = path.resolve(strict=True)
                            real.relative_to(
                                self.root.resolve(strict=True)
                            )
                        except (
                            OSError,
                            RuntimeError,
                            ValueError,
                        ):
                            reasons.append(
                                "existing_inventory_path_invalid"
                            )
                            continue
                        if (
                            path.is_symlink()
                            or not path.is_file()
                            or not _valid_sha(expected)
                            or _file_sha(path) != expected
                        ):
                            reasons.append(
                                "existing_inventory_file_divergence"
                            )

                validation_path = (
                    self._inventory_validation_report_path(
                        transaction_dir
                    )
                )
                validation = self._load_json_mapping(
                    validation_path
                )
                if validation is None:
                    reasons.append(
                        "existing_inventory_validation_report_missing"
                    )
                else:
                    validation_hash = validation.get(
                        "validation_report_hash"
                    )
                    validation_payload = {
                        key: value
                        for key, value in validation.items()
                        if key != "validation_report_hash"
                    }
                    if (
                        not _valid_sha(validation_hash)
                        or str(validation_hash).lower()
                        != _sha(validation_payload)
                    ):
                        reasons.append(
                            "existing_inventory_validation_report_hash_invalid"
                        )
                    if (
                        update is not None
                        and update.get(
                            "validation_report_hash"
                        )
                        != validation_hash
                    ):
                        reasons.append(
                            "existing_inventory_validation_manifest_divergence"
                        )

                if reasons:
                    result = dict(admitted)
                    result.update(
                        {
                            "stage": "ACEE6-E",
                            "public_schema_version": "0.8.0",
                            "status": (
                                "ACEE6_INVENTORY_REPLAY_REJECTED"
                            ),
                            "transaction_state": "STATE_CORRUPTED",
                            "transaction_id": transaction_id,
                            "inventory_modified": False,
                            "inventory_update_complete": False,
                            "inventory_replayed": False,
                            "blocking_reasons": sorted(set(reasons)),
                            "candidate_executed": False,
                            "tests_executed": False,
                            "global_validation_executed": False,
                            "committed": False,
                        }
                    )
                    result["result_hash"] = _sha(
                        {
                            key: value
                            for key, value in result.items()
                            if key != "result_hash"
                        }
                    )
                    return result

                result = dict(latest)
                result.update(
                    {
                        "primitive": "ACEE_INSTALLATION_EXECUTOR",
                        "stage": "ACEE6-E",
                        "public_schema_version": "0.8.0",
                        "status": (
                            "ACEE6_INVENTORY_UPDATE_COMPLETE"
                        ),
                        "transaction_state": (
                            "INVENTORIES_UPDATED"
                        ),
                        "transaction_id": transaction_id,
                        "inventory_update_complete": True,
                        "inventory_modified": True,
                        "inventory_replayed": True,
                        "candidate_compiled": True,
                        "candidate_executed": False,
                        "tests_executed": False,
                        "global_validation_executed": False,
                        "committed": False,
                        "persistence_performed": False,
                        "inventory_update_manifest_path": str(
                            update_path
                        ),
                        "inventory_validation_report_path": str(
                            validation_path
                        ),
                    }
                )
                result["result_hash"] = _sha(
                    {
                        key: value
                        for key, value in result.items()
                        if key != "result_hash"
                    }
                )
                return result

            d3_inputs = deepcopy(
                dict(inputs)
                if isinstance(inputs, Mapping)
                else {}
            )
            d3_context = _mapping(
                d3_inputs.get("admission_context")
            )
            d3_context["requested_stage"] = "ACEE6-D3"
            d3_inputs["admission_context"] = d3_context
            compiled = self.step(
                inputs=d3_inputs,
                persist=True,
            )
            if compiled.get("transaction_state") == "COMPILED":
                result = self._update_inventories(
                    compiled,
                    inputs,
                )
                return self._fault_injection_boundary(result, inputs, "inventory")
            return compiled

        if requested_stage == "ACEE6-D3":
            transaction_id = self._transaction_id(admitted)
            transaction_dir = (
                self._transaction_runtime_root() / transaction_id
            )

            compiled_replay = self._validate_compiled_replay(
                transaction_dir,
                admitted,
            )
            if compiled_replay is not None:
                return compiled_replay

            d2_inputs = deepcopy(
                dict(inputs) if isinstance(inputs, Mapping) else {}
            )
            d2_context = _mapping(
                d2_inputs.get("admission_context")
            )
            d2_context["requested_stage"] = "ACEE6-D2"
            d2_inputs["admission_context"] = d2_context

            mutated = self.step(
                inputs=d2_inputs,
                persist=True,
            )
            if mutated.get("transaction_state") == "MUTATED":
                result = self._compile_transaction(mutated)
                return self._fault_injection_boundary(result, inputs, "compile")
            return mutated

        if requested_stage in {"ACEE6-D1", "ACEE6-D2"}:
            transaction_id = self._transaction_id(admitted)
            transaction_dir = self._transaction_runtime_root() / transaction_id
            if requested_stage == "ACEE6-D2":
                mutated = self._validate_mutated_replay(
                    transaction_dir,
                    admitted,
                )
                if mutated is not None:
                    return mutated
                recovered = self._recover_interrupted_mutation(
                    transaction_dir,
                    admitted,
                    inputs,
                )
                if recovered is not None:
                    return recovered
            replay = self._validate_backed_up_replay(transaction_dir, admitted)
            if replay is not None:
                if requested_stage == "ACEE6-D2" and replay.get(
                    "transaction_state"
                ) == "BACKED_UP":
                    result = self._mutate_transaction(replay, inputs)
                    return self._fault_injection_boundary(result, inputs, "write")
                return replay

            latest = self._load_json_mapping(
                transaction_dir / "latest_state.json"
            )
            if (
                isinstance(latest, Mapping)
                and latest.get("transaction_state") == "PREPARED"
            ):
                recoverable = dict(admitted)
                recoverable.update({
                    "stage": "ACEE6-C",
                    "public_schema_version": "0.4.0",
                    "status": "ACEE6_TRANSACTION_PREPARED",
                    "transaction_state": "PREPARED",
                    "transaction_id": transaction_id,
                    "transaction_prepared": True,
                    "transaction_directory": str(transaction_dir),
                    "journal_path": str(transaction_dir / "journal.jsonl"),
                    "latest_state_path": str(
                        transaction_dir / "latest_state.json"
                    ),
                    "snapshot_path": str(transaction_dir / "snapshot.json"),
                    "snapshot_hash": latest.get("snapshot_hash"),
                    "write_count": 3,
                    "candidate_written": False,
                    "inventory_modified": False,
                    "tests_executed": False,
                    "global_validation_executed": False,
                    "recovery_contract": "ACEE6-D1-BACKUP-INTEGRITY",
                })
                backed_up = self._backup_transaction(recoverable)
                if requested_stage == "ACEE6-D2" and backed_up.get(
                    "transaction_state"
                ) == "BACKED_UP":
                    result = self._mutate_transaction(backed_up, inputs)
                    return self._fault_injection_boundary(result, inputs, "write")
                return self._fault_injection_boundary(backed_up, inputs, "backup")

        prepared = self._prepare_transaction(admitted)
        if prepared.get("lock_acquired"):
            prepared["lock_released"] = True
        if requested_stage in {"ACEE6-D1", "ACEE6-D2"} and prepared.get(
            "transaction_state"
        ) == "PREPARED":
            backed_up = self._backup_transaction(prepared)
            if requested_stage == "ACEE6-D2" and backed_up.get(
                "transaction_state"
            ) == "BACKED_UP":
                result = self._mutate_transaction(backed_up, inputs)
                return self._fault_injection_boundary(result, inputs, "write")
            prepared = self._fault_injection_boundary(backed_up, inputs, "backup")
        prepared["result_hash"] = _sha({
            k: v for k, v in prepared.items() if k != "result_hash"
        })
        return prepared
