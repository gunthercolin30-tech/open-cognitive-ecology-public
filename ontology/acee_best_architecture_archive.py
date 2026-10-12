"""ACEE14 — immutable archive of accepted, validated architectures.

ACEE14 consumes authoritative ACEE10/11/12/13 evidence and creates a local,
reproducible, checksum-protected bundle. It does not select candidates, execute
rollback, mutate lineages, publish releases, or perform network operations.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_BEST_ARCHITECTURE_ARCHIVE"
STATUS_READY = "ACEE_BEST_ARCHITECTURE_ARCHIVE_READY"
STATUS_DEGRADED = "ACEE_BEST_ARCHITECTURE_ARCHIVE_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
ALLOWED_OPERATIONS = {"archive_architecture", "inspect_archive", "verify_archive", "list_best_architectures"}


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
    return "".join(ch if ch.isalnum() or ch in "_-." else "_" for ch in raw)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


class AceeBestArchitectureArchive:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (Path(root) if root is not None else Path.home() / "open-cognitive-ecology").expanduser().resolve()

    def _paths(self) -> Tuple[Path, Path, Path, Path, Path]:
        runtime = self.root / "acee_runtime" / "ACEE14_acee_best_architecture_archive"
        return (
            runtime,
            runtime / "archives",
            runtime / "best_architectures.json",
            runtime / "archive_history.jsonl",
            runtime / ".archive.lock",
        )

    def _safe_source(self, value: Any) -> Optional[Path]:
        raw = str(value or "").strip()
        if not raw:
            return None
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        try:
            resolved = candidate.expanduser().resolve()
            resolved.relative_to(self.root)
        except (OSError, ValueError):
            return None
        return resolved if resolved.is_file() else None

    def _load_index(self, path: Path) -> Tuple[Dict[str, Any], bool]:
        if not path.is_file():
            return {"schema_version": PUBLIC_SCHEMA_VERSION, "archives": {}, "processed_transactions": {}}, False
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or not isinstance(payload.get("archives"), dict):
                return {"schema_version": PUBLIC_SCHEMA_VERSION, "archives": {}, "processed_transactions": {}}, True
            payload.setdefault("processed_transactions", {})
            return payload, False
        except (OSError, json.JSONDecodeError, TypeError):
            return {"schema_version": PUBLIC_SCHEMA_VERSION, "archives": {}, "processed_transactions": {}}, True

    def _base(self, inputs: Mapping[str, Any], operation: str) -> Dict[str, Any]:
        return {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": str(inputs.get("timestamp_utc") or _now()),
            "operation": operation,
            "archive_id": _clean_id(inputs.get("archive_id")) or None,
            "architecture_id": _clean_id(inputs.get("architecture_id")) or None,
            "transaction_id": _clean_id(inputs.get("transaction_id")) or None,
            "selection_executed_by_archive": False,
            "rollback_executed_by_archive": False,
            "lineage_modified_by_archive": False,
            "genealogy_modified_by_archive": False,
            "publication_executed_by_archive": False,
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

    def _verify_directory(self, directory: Path) -> Tuple[bool, List[str]]:
        manifest_path = directory / "manifest.json"
        sums_path = directory / "SHA256SUMS.txt"
        problems: List[str] = []

        if not manifest_path.is_file():
            problems.append("manifest_missing")
        if not sums_path.is_file():
            problems.append("checksums_missing")
        if problems:
            return False, problems

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            return False, ["manifest_invalid"]

        expected = manifest.get("files", {})
        if not isinstance(expected, dict):
            return False, ["manifest_files_invalid"]

        normalized_expected: Dict[str, str] = {}
        for relative, digest in expected.items():
            relative_text = str(relative)
            digest_text = str(digest).lower()
            if (
                not relative_text
                or relative_text in {"manifest.json", "SHA256SUMS.txt"}
                or Path(relative_text).is_absolute()
                or ".." in Path(relative_text).parts
            ):
                problems.append(f"manifest_path_invalid:{relative_text}")
                continue
            if (
                len(digest_text) != 64
                or any(character not in "0123456789abcdef" for character in digest_text)
            ):
                problems.append(f"manifest_digest_invalid:{relative_text}")
                continue
            normalized_expected[relative_text] = digest_text

        listed: Dict[str, str] = {}
        try:
            lines = sums_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return False, ["checksums_unreadable"]

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            if line.count("  ") != 1:
                problems.append(f"checksums_line_invalid:{line_number}")
                continue
            digest, relative = line.split("  ", 1)
            digest = digest.strip().lower()
            relative = relative.strip()
            if (
                len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                problems.append(f"checksums_digest_invalid:{line_number}")
                continue
            if (
                not relative
                or relative == "SHA256SUMS.txt"
                or Path(relative).is_absolute()
                or ".." in Path(relative).parts
            ):
                problems.append(f"checksums_path_invalid:{line_number}")
                continue
            if relative in listed:
                problems.append(f"checksums_duplicate:{relative}")
                continue
            listed[relative] = digest

        required_listed = dict(normalized_expected)
        required_listed["manifest.json"] = _sha_file(manifest_path)
        if listed != required_listed:
            problems.append("checksums_manifest_mismatch")

        actual_files = {
            str(path.relative_to(directory))
            for path in directory.rglob("*")
            if path.is_file() and path.name != "SHA256SUMS.txt"
        }
        if actual_files != set(required_listed):
            problems.append("archive_file_set_mismatch")

        for relative, digest in required_listed.items():
            target = directory / relative
            if not target.is_file():
                problems.append(f"file_missing:{relative}")
            elif _sha_file(target) != digest:
                problems.append(f"checksum_mismatch:{relative}")

        return not problems, problems

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        operation = str(supplied.get("operation") or "list_best_architectures").strip().lower()
        result = self._base(supplied, operation)
        runtime, archives_root, index_path, history_path, lock_path = self._paths()
        blocking: List[str] = []
        if operation not in ALLOWED_OPERATIONS:
            blocking.append("operation_invalid")

        runtime.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+", encoding="utf-8") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            index, index_corrupted = self._load_index(index_path)
            if index_corrupted:
                blocking.append("index_corrupted")

            if operation == "list_best_architectures":
                ranked = sorted(
                    index.get("archives", {}).values(),
                    key=lambda item: (-float(item.get("architecture_score", 0.0)), str(item.get("archive_id", ""))),
                )
                result.update({"archives": ranked, "archive_count": len(ranked), "best_archive_id": ranked[0]["archive_id"] if ranked else None})

            elif operation in {"inspect_archive", "verify_archive"}:
                archive_id = _clean_id(supplied.get("archive_id"))
                record = _mapping(index.get("archives", {}).get(archive_id))
                if not archive_id:
                    blocking.append("archive_id_required")
                elif not record:
                    blocking.append("archive_not_found")
                else:
                    directory = archives_root / archive_id
                    verified, verification_errors = self._verify_directory(directory)
                    result.update(record)
                    result.update({"archive_verified": verified, "verification_errors": verification_errors, "archive_path": str(directory)})
                    if operation == "verify_archive" and not verified:
                        blocking.append("archive_integrity_failure")

            elif operation == "archive_architecture":
                transaction_id = _clean_id(supplied.get("transaction_id"))
                archive_id = _clean_id(supplied.get("archive_id"))
                architecture_id = _clean_id(supplied.get("architecture_id"))
                score = _finite(supplied.get("architecture_score"))
                selection = _mapping(supplied.get("selection_decision"))
                lineage = _mapping(supplied.get("lineage_state"))
                validation = _mapping(supplied.get("validation_summary"))
                git_context = _mapping(supplied.get("git_context"))
                rollback_package = _mapping(supplied.get("rollback_package"))
                reproduction_command = str(supplied.get("reproduction_command") or "").strip()
                module_inventory = supplied.get("module_inventory")
                if transaction_id and transaction_id in index.get("processed_transactions", {}):
                    prior = dict(index["processed_transactions"][transaction_id])
                    prior.update({"idempotent_replay": True, "persisted": False})
                    return prior
                if not transaction_id:
                    blocking.append("transaction_id_required")
                if not archive_id:
                    blocking.append("archive_id_required")
                if not architecture_id:
                    blocking.append("architecture_id_required")
                if archive_id in index.get("archives", {}):
                    blocking.append("archive_id_already_exists")
                if score is None:
                    blocking.append("architecture_score_invalid")
                if selection.get("selection_decision_ready") is not True or selection.get("decision") != "accept":
                    blocking.append("accepted_selection_required")
                if lineage.get("generation_status") != "active" and lineage.get("active") is not True:
                    blocking.append("active_lineage_generation_required")
                if validation.get("overall_success") is not True:
                    blocking.append("validation_success_required")
                diagnostics = _mapping(validation.get("diagnostics"))
                error_count = diagnostics.get("error_count", validation.get("error_count"))
                if error_count != 0:
                    blocking.append("error_count_must_be_zero")
                if not isinstance(module_inventory, list) or not module_inventory:
                    blocking.append("module_inventory_required")
                if not reproduction_command:
                    blocking.append("reproduction_command_required")
                if any(token in reproduction_command for token in ("curl ", "wget ", "rm -rf", "git push", "gh release", "zenodo")):
                    blocking.append("reproduction_command_unsafe")
                reports: List[Path] = []
                for item in supplied.get("report_files", []) if isinstance(supplied.get("report_files"), list) else []:
                    path = self._safe_source(item)
                    if path is None:
                        blocking.append(f"report_invalid:{item}")
                    else:
                        reports.append(path)
                if not reports:
                    blocking.append("report_files_required")

                if not blocking:
                    archives_root.mkdir(parents=True, exist_ok=True)
                    final_dir = archives_root / archive_id
                    temp_parent = Path(tempfile.mkdtemp(prefix=f".{archive_id}.", dir=str(archives_root)))
                    try:
                        (temp_parent / "reports").mkdir(parents=True)
                        architecture_snapshot = {
                            "archive_id": archive_id,
                            "architecture_id": architecture_id,
                            "architecture_score": score,
                            "lineage_id": supplied.get("lineage_id") or lineage.get("lineage_id"),
                            "generation_id": supplied.get("generation_id") or lineage.get("generation_id"),
                            "parent_id": supplied.get("parent_id") or lineage.get("parent_id"),
                            "mutation_id": supplied.get("mutation_id") or lineage.get("mutation_id"),
                            "selection_id": selection.get("selection_id"),
                            "selection_reason": selection.get("decision_reasons") or selection.get("selection_reason"),
                            "fitness_delta": supplied.get("fitness_delta", lineage.get("fitness_delta")),
                            "module_inventory": list(module_inventory),
                            "git_context": git_context,
                            "rollback_package": rollback_package,
                            "created_at_utc": result["timestamp_utc"],
                        }
                        (temp_parent / "architecture_snapshot.json").write_text(json.dumps(architecture_snapshot, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")
                        (temp_parent / "validation_summary.json").write_text(json.dumps(validation, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")
                        (temp_parent / "rollback_package.json").write_text(json.dumps(rollback_package, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")
                        (temp_parent / "reproduction.sh").write_text("#!/bin/sh\nset -eu\n" + reproduction_command + "\n", encoding="utf-8")
                        os.chmod(temp_parent / "reproduction.sh", 0o755)
                        for source in reports:
                            shutil.copy2(source, temp_parent / "reports" / source.name)
                        files = {}
                        for path in sorted(temp_parent.rglob("*")):
                            if path.is_file() and path.name not in {"manifest.json", "SHA256SUMS.txt"}:
                                files[str(path.relative_to(temp_parent))] = _sha_file(path)
                        manifest = {
                            "primitive": PRIMITIVE,
                            "status": STATUS_READY,
                            "public_schema_version": PUBLIC_SCHEMA_VERSION,
                            "archive_id": archive_id,
                            "architecture_id": architecture_id,
                            "architecture_score": score,
                            "commit": git_context.get("commit"),
                            "branch": git_context.get("branch"),
                            "worktree_clean": bool(git_context.get("worktree_clean")),
                            "release_ready": bool(git_context.get("worktree_clean")),
                            "files": files,
                            "selection_executed_by_archive": False,
                            "rollback_executed_by_archive": False,
                            "publication_executed_by_archive": False,
                        }
                        manifest_path = temp_parent / "manifest.json"
                        manifest_path.write_text(
                            json.dumps(
                                manifest,
                                sort_keys=True,
                                indent=2,
                                ensure_ascii=False,
                            ),
                            encoding="utf-8",
                        )
                        checksums = dict(files)
                        checksums["manifest.json"] = _sha_file(manifest_path)
                        (temp_parent / "SHA256SUMS.txt").write_text(
                            "".join(
                                f"{digest}  {relative}\n"
                                for relative, digest in sorted(checksums.items())
                            ),
                            encoding="utf-8",
                        )
                        if final_dir.exists():
                            blocking.append("archive_directory_already_exists")
                        else:
                            temp_parent.replace(final_dir)
                    finally:
                        if temp_parent.exists():
                            shutil.rmtree(temp_parent, ignore_errors=True)

                    if not blocking:
                        verified, verification_errors = self._verify_directory(final_dir)
                        if not verified:
                            blocking.append("post_write_integrity_failure")
                        else:
                            record = {
                                "archive_id": archive_id,
                                "architecture_id": architecture_id,
                                "architecture_score": score,
                                "lineage_id": architecture_snapshot.get("lineage_id"),
                                "generation_id": architecture_snapshot.get("generation_id"),
                                "commit": git_context.get("commit"),
                                "branch": git_context.get("branch"),
                                "worktree_clean": bool(git_context.get("worktree_clean")),
                                "release_ready": bool(git_context.get("worktree_clean")),
                                "archive_verified": True,
                                "archive_path": str(final_dir),
                                "created_at_utc": result["timestamp_utc"],
                            }
                            archives = dict(index.get("archives", {}))
                            archives[archive_id] = record
                            index["archives"] = archives
                            result.update(record)
                            result.update({"archive_created": True, "archive_verified": True, "verification_errors": []})
                            if persist:
                                index.setdefault("processed_transactions", {})[transaction_id] = dict(result)
                                temporary_index = index_path.with_suffix(".json.tmp")
                                temporary_index.write_text(json.dumps(index, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")
                                temporary_index.replace(index_path)
                                with history_path.open("a", encoding="utf-8") as handle:
                                    handle.write(_canonical({"transaction_id": transaction_id, "archive_id": archive_id, "architecture_id": architecture_id, "architecture_score": score, "timestamp_utc": result["timestamp_utc"]}) + "\n")
                                result["persisted"] = True
                            else:
                                shutil.rmtree(final_dir, ignore_errors=True)
                                result["persisted"] = False

            ranked = sorted(index.get("archives", {}).values(), key=lambda item: (-float(item.get("architecture_score", 0.0)), str(item.get("archive_id", ""))))
            result.setdefault("archive_count", len(ranked))
            result.setdefault("best_archive_id", ranked[0]["archive_id"] if ranked else None)
            result["blocking_reasons"] = sorted(set(blocking))
            result["archive_ready"] = not blocking
            result["status"] = STATUS_READY if not blocking else STATUS_DEGRADED
            result.setdefault("archive_created", False)
            result.setdefault("archive_verified", False)
            result.setdefault("release_ready", False)
            result.setdefault("persisted", False)
            return result
