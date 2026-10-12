"""ACEE5 — governed pre-installation code-generation evidence gate.

This primitive verifies that a code-generation proposal is accompanied by a
complete, coherent and bounded evidence package before installation. It is
strictly declarative: it does not generate, write, compile, test, install or
rollback code.
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

PRIMITIVE = "ACEE_GOVERNED_CODE_GENERATION_GATE"
STATUS_GOVERNED = "ACEE_CODE_GENERATION_GOVERNED"
STATUS_BLOCKED = "ACEE_CODE_GENERATION_BLOCKED"
PUBLIC_SCHEMA_VERSION = "1.2.0"
DEPENDENCIES = [
    "automated_primitive_designer",
    "external_code_proposal_standard",
    "external_code_review_preparation",
    "constitutional_evolution_gate",
    "constitutional_self_modification_protocol",
    "constitutional_compliance_check",
    "acee_validation_runner",
    "acee_rollback_engine",
]
REQUIRED_INVENTORY_TARGETS = (
    "dependency_registry.py",
    "ontology_inventory.txt",
    "ontology_inventory.py",
    "ontology/ontology_inventory.py",
    "global_module_catalog.txt",
)
MAX_VALIDATION_AGE_SECONDS = 24 * 60 * 60


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _json_safe(value: Any, depth: int = 0) -> Any:
    if depth > 64:
        return "<max-depth>"
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if value != value: return "<nan>"
        if value == float("inf"): return "<positive-infinity>"
        if value == float("-inf"): return "<negative-infinity>"
        return value
    if isinstance(value, Path): return str(value)
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v, depth + 1) for k, v in sorted(value.items(), key=lambda p: str(p[0]))}
    if isinstance(value, (list, tuple)): return [_json_safe(v, depth + 1) for v in value]
    if isinstance(value, (set, frozenset)):
        values = [_json_safe(v, depth + 1) for v in value]
        return sorted(values, key=repr)
    if isinstance(value, bytes): return {"bytes_hex": value.hex()}
    return {"unsupported_type": type(value).__name__, "repr": repr(value)[:512]}


def _canonical(value: Any) -> str:
    return json.dumps(_json_safe(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _valid_sha(value: Any) -> bool:
    text = str(value or "").lower()
    return len(text) == 64 and all(ch in "0123456789abcdef" for ch in text)


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
class AceeGovernedCodeGenerationGate:
    root: Optional[Path] = None

    def __post_init__(self) -> None:
        self.root = (
            Path(self.root)
            if self.root is not None
            else Path.home() / "open-cognitive-ecology"
        ).resolve()

    def _paths(self) -> Tuple[Path, Path, Path]:
        directory = (
            self.root
            / "acee_runtime"
            / "ACEE5_acee_governed_code_generation_gate"
        )
        return (
            directory / "latest_gate_decision.json",
            directory / "gate_decision_history.jsonl",
            directory / ".gate.lock",
        )

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

    def _resolved_local(self, normalized: Optional[str]) -> Optional[Path]:
        if not normalized:
            return None
        try:
            path = (self.root / normalized).resolve(strict=True)
            path.relative_to(self.root.resolve(strict=True))
            return path
        except (OSError, ValueError):
            return None

    def _verify_local_hash(
        self,
        normalized: Optional[str],
        expected: Any,
        label: str,
        blocking: List[str],
    ) -> None:
        path = self._resolved_local(normalized)
        if path is None or not path.is_file():
            return
        try:
            actual = _file_sha(path)
        except OSError:
            blocking.append(label + "_unreadable")
            return
        if actual != str(expected or "").lower():
            blocking.append(label + "_hash_mismatch")

    def _load_history(
        self, history: Path
    ) -> Tuple[List[Dict[str, Any]], bool, List[str]]:
        if not history.is_file():
            return [], False, []
        errors: List[str] = []
        records: List[Dict[str, Any]] = []
        try:
            raw_lines = history.read_text(encoding="utf-8").splitlines()
        except OSError:
            return [], True, ["history_unreadable"]
        lines = [line for line in raw_lines if line.strip()]
        previous_hash: Optional[str] = None
        for index, line in enumerate(lines):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"history_json_invalid:{index}")
                continue
            if not isinstance(record, dict):
                errors.append(f"history_record_not_mapping:{index}")
                continue
            supplied_result_hash = record.get("result_hash")
            recomputed = _sha(
                {key: value for key, value in record.items() if key != "result_hash"}
            )
            if supplied_result_hash != recomputed:
                errors.append(f"history_result_hash_mismatch:{index}")
            if record.get("previous_decision_hash") != previous_hash:
                errors.append(f"history_chain_break:{index}")
            if record.get("decision_index") != index:
                errors.append(f"history_index_mismatch:{index}")
            previous_hash = str(supplied_result_hash or "") or None
            records.append(record)
        return records, bool(errors), errors

    def _evaluate(
        self,
        supplied: Mapping[str, Any],
        records: List[Dict[str, Any]],
        history_corrupted: bool,
        history_errors: List[str],
    ) -> Dict[str, Any]:
        candidate = _mapping(supplied.get("candidate"))
        backup = _mapping(supplied.get("backup_evidence"))
        refiner = _mapping(supplied.get("refiner_evidence"))
        tests = _mapping(supplied.get("test_evidence"))
        rollback = _mapping(supplied.get("rollback_plan"))
        inventory = _mapping(supplied.get("inventory_plan"))
        validation = _mapping(supplied.get("validation_evidence"))
        constitutional = _mapping(supplied.get("constitutional_evidence"))
        generation = _mapping(supplied.get("generation_evidence"))

        blocking: List[str] = []
        warnings: List[str] = []
        proposal_id = str(supplied.get("proposal_id") or "").strip()
        if not proposal_id:
            blocking.append("proposal_id_missing")

        module_name = str(candidate.get("module_name") or "").strip()
        if not module_name:
            blocking.append("candidate_module_name_missing")
        target_path, target_error = self._relative_path(candidate.get("target_path"))
        if target_error:
            blocking.append("candidate_" + target_error)
        if target_path and not target_path.startswith("ontology/"):
            blocking.append("candidate_target_not_in_ontology")
        if not _valid_sha(candidate.get("content_sha256")):
            blocking.append("candidate_content_hash_invalid")
        candidate_hash = str(candidate.get("content_sha256") or "").lower()

        for old in records:
            if old.get("proposal_id") != proposal_id:
                continue
            old_manifest = _mapping(old.get("installation_manifest"))
            old_hash = str(old_manifest.get("candidate_content_sha256") or "")
            if old_hash and candidate_hash and old_hash != candidate_hash:
                blocking.append("proposal_id_collision")

        if generation.get("proposal_only") is not True:
            blocking.append("generation_not_proposal_only")
        if generation.get("code_written") is True or generation.get("code_installed") is True:
            blocking.append("upstream_generation_side_effect_detected")

        backup_target, backup_target_error = self._relative_path(backup.get("target_path"))
        backup_path, backup_path_error = self._relative_path(backup.get("backup_path"))
        if backup_target_error or backup_path_error:
            blocking.append("backup_path_invalid")
        if backup.get("verified") is not True:
            blocking.append("backup_not_verified")
        if target_path and backup_target and target_path != backup_target:
            blocking.append("backup_target_mismatch")
        if backup_path and target_path and backup_path != target_path + ".bak":
            blocking.append("backup_naming_contract_invalid")
        if not _valid_sha(backup.get("sha256")):
            blocking.append("backup_hash_invalid")
        self._verify_local_hash(backup_path, backup.get("sha256"), "backup", blocking)

        refiner_path, refiner_error = self._relative_path(refiner.get("path"))
        if refiner_error:
            blocking.append("refiner_path_invalid")
        expected_refiner = "refine_" + module_name + ".py" if module_name else None
        if refiner_path and expected_refiner and Path(refiner_path).name != expected_refiner:
            blocking.append("refiner_name_mismatch")
        if refiner.get("generated") is not True:
            blocking.append("refiner_not_generated")
        if refiner.get("compilation_ready") is not True:
            blocking.append("refiner_not_compilation_ready")
        if not _valid_sha(refiner.get("sha256")):
            blocking.append("refiner_hash_invalid")
        self._verify_local_hash(refiner_path, refiner.get("sha256"), "refiner", blocking)

        test_files = tests.get("tests")
        if tests.get("generated") is not True:
            blocking.append("tests_not_generated")
        if not isinstance(test_files, list) or not test_files:
            blocking.append("test_manifest_missing")
            normalized_tests: List[str] = []
        else:
            normalized_tests = []
            for item in test_files:
                normalized, error = self._relative_path(item)
                if error or not normalized or not normalized.endswith(".py"):
                    blocking.append("test_path_invalid")
                    continue
                normalized_tests.append(normalized)
        for kind in ("fast_acceptance", "functional", "degradation", "non_regression"):
            if not any(kind in Path(path).stem for path in normalized_tests):
                blocking.append("required_test_missing:" + kind)

        if rollback.get("available") is not True:
            blocking.append("rollback_plan_unavailable")
        if str(rollback.get("executor") or "") != "acee_rollback_engine":
            blocking.append("rollback_executor_invalid")
        artifacts = rollback.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            blocking.append("rollback_artifacts_missing")

        for required in REQUIRED_INVENTORY_TARGETS:
            key = required.replace("/", "_").replace(".", "_")
            if inventory.get(required) is not True and inventory.get(key) is not True:
                blocking.append("inventory_update_missing:" + required)

        if validation.get("runner") != "acee_validation_runner":
            blocking.append("validation_runner_invalid")
        if validation.get("command") != "python3 -m validation.main":
            blocking.append("validation_command_invalid")
        if validation.get("executed") is not True:
            blocking.append("validation_not_executed")
        if validation.get("overall_success") is not True:
            blocking.append("validation_unsuccessful")
        if validation.get("error_count") != 0:
            blocking.append("validation_error_count_nonzero")
        if not _valid_sha(validation.get("report_sha256")):
            blocking.append("validation_report_hash_invalid")
        validated_hash = str(validation.get("candidate_content_sha256") or "").lower()
        if validated_hash != candidate_hash:
            blocking.append("validation_candidate_hash_mismatch")
        validation_proposal_id = str(validation.get("proposal_id") or "").strip()
        if validation_proposal_id and validation_proposal_id != proposal_id:
            blocking.append("validation_proposal_id_mismatch")
        report_path, report_error = self._relative_path(validation.get("report_path")) if validation.get("report_path") else (None, None)
        if report_error:
            blocking.append("validation_report_path_invalid")
        self._verify_local_hash(report_path, validation.get("report_sha256"), "validation_report", blocking)

        proposal_time = _parse_time(supplied.get("timestamp_utc"))
        validation_time = _parse_time(validation.get("timestamp_utc"))
        if supplied.get("timestamp_utc") and proposal_time is None:
            blocking.append("proposal_timestamp_invalid")
        if validation.get("timestamp_utc") and validation_time is None:
            blocking.append("validation_timestamp_invalid")
        if proposal_time and validation_time:
            if validation_time < proposal_time:
                blocking.append("validation_predates_proposal")
            age = (datetime.now(timezone.utc) - validation_time).total_seconds()
            if age > MAX_VALIDATION_AGE_SECONDS:
                blocking.append("validation_stale")
            if age < -300:
                blocking.append("validation_timestamp_in_future")

        if constitutional.get("compliant") is not True:
            blocking.append("constitutional_non_compliance")
        if constitutional.get("non_closure_preserved") is not True:
            blocking.append("non_closure_not_preserved")
        if constitutional.get("functional_conclusion_only") is not True:
            blocking.append("functional_scope_not_preserved")
        if constitutional.get("phenomenology_undetermined") is not True:
            blocking.append("phenomenology_guard_missing")

        if history_corrupted:
            blocking.append("history_corrupted")
            warnings.extend(history_errors)

        blocking = sorted(set(blocking))
        warnings = sorted(set(warnings))
        governed = not blocking
        previous_hash = records[-1].get("result_hash") if records else None
        manifest = {
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "decision_index": len(records),
            "proposal_id": proposal_id,
            "module_name": module_name,
            "target_path": target_path,
            "candidate_content_sha256": candidate_hash,
            "backup_path": backup_path,
            "backup_sha256": str(backup.get("sha256") or "").lower(),
            "refiner_path": refiner_path,
            "refiner_sha256": str(refiner.get("sha256") or "").lower(),
            "test_paths": sorted(set(normalized_tests)),
            "rollback_executor": rollback.get("executor"),
            "inventory_targets": list(REQUIRED_INVENTORY_TARGETS),
            "validation_report_sha256": str(validation.get("report_sha256") or "").lower(),
        }
        manifest["manifest_hash"] = _sha(manifest)
        result = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": str(supplied.get("timestamp_utc") or _now()),
            "proposal_id": proposal_id,
            "decision_index": len(records),
            "status": STATUS_GOVERNED if governed else STATUS_BLOCKED,
            "generation_governed": governed,
            "installation_authorized": governed,
            "authorization_scope": "single_candidate_manifest" if governed else "none",
            "preconditions_complete": governed,
            "blocking_reasons": blocking,
            "warnings": warnings,
            "installation_manifest": manifest if governed else None,
            "previous_decision_hash": previous_hash,
            "history_corrupted": history_corrupted,
            "code_generated_by_gate": False,
            "code_written_by_gate": False,
            "code_compiled_by_gate": False,
            "tests_executed_by_gate": False,
            "code_installed_by_gate": False,
            "validation_executed_by_gate": False,
            "rollback_executed_by_gate": False,
            "selection_executed_by_gate": False,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        result["evidence_hash"] = _sha(
            {
                "proposal": dict(supplied),
                "normalized_manifest": manifest,
                "blocking_reasons": blocking,
            }
        )
        result["result_hash"] = _sha(
            {key: value for key, value in result.items() if key != "result_hash"}
        )
        return result

    def step(
        self,
        inputs: Optional[Mapping[str, Any]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        supplied = dict(inputs) if isinstance(inputs, Mapping) else {}
        latest, history, lock = self._paths()
        if not persist:
            records, corrupted, errors = self._load_history(history)
            return self._evaluate(supplied, records, corrupted, errors)

        latest.parent.mkdir(parents=True, exist_ok=True)
        lock.touch(exist_ok=True)
        with lock.open("r+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            records, corrupted, errors = self._load_history(history)
            result = self._evaluate(supplied, records, corrupted, errors)
            line = _canonical(result) + "\n"
            with history.open("a", encoding="utf-8") as stream:
                stream.write(line)
                stream.flush()
                os.fsync(stream.fileno())
            temporary = latest.with_name(
                latest.name + f".{os.getpid()}.tmp"
            )
            try:
                with temporary.open("w", encoding="utf-8") as stream:
                    json.dump(result, stream, indent=2, ensure_ascii=False)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, latest)
                directory_fd = os.open(str(latest.parent), os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            finally:
                if temporary.exists():
                    temporary.unlink()
            result["latest_path"] = str(latest)
            result["history_path"] = str(history)
            return result
