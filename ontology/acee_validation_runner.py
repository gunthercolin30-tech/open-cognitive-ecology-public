"""ACEE7 — governed validation execution and normalization facade."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from ontology.governed_acee_validation_backend import run_closed_validation
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

PRIMITIVE = "ACEE_VALIDATION_RUNNER"
STATUS_READY = "ACEE_VALIDATION_COMPLETE"
STATUS_FAILED = "ACEE_VALIDATION_FAILED"
STATUS_BLOCKED = "ACEE_VALIDATION_BLOCKED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
BENIGN_WARNING_TOKENS = ("RuntimeWarning", "NotOpenSSLWarning")
ALLOWED_MODES = {"targeted", "fast_acceptance", "final_lock", "specialized", "full_isolated"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _float(value: Any, default: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if result != result or result in (float("inf"), float("-inf")):
        return default
    return max(0.1, min(3600.0, result))


@dataclass
class AceeValidationRunner:
    root: Optional[Path] = None

    def __post_init__(self) -> None:
        self.root = (Path(self.root) if self.root is not None else Path.home() / "open-cognitive-ecology").resolve()

    def _paths(self) -> Tuple[Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE7_acee_validation_runner"
        return directory / "latest_validation.json", directory / "validation_history.jsonl", directory / ".validation.lock"

    def _previous(self, history: Path) -> Tuple[Optional[Dict[str, Any]], bool]:
        if not history.is_file():
            return None, False
        try:
            lines = [line for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
            return (json.loads(lines[-1]), False) if lines else (None, False)
        except (OSError, json.JSONDecodeError):
            return None, True

    def _allowed_command(self, argv: Sequence[str], allow_full: bool) -> Tuple[bool, str]:
        if not argv or str(argv[0]) not in {sys.executable, "python3", "python"}:
            return False, "python_command_required"
        args = [str(x) for x in argv[1:]]
        # P162-G6.5c7d3: the production runner has one closed executable grammar.
        # Arbitrary ROOT-relative Python scripts are not an execution capability.
        if not args or args[:2] != ["-m", "validation.main"]:
            return False, "unregistered_python_command"
        permitted = {"-m", "validation.main", "--full"}
        if any(arg not in permitted for arg in args):
            return False, "validation_main_argument_not_permitted"
        if args.count("-m") != 1 or args.count("validation.main") != 1 or args.count("--full") > 1:
            return False, "validation_main_grammar_invalid"
        full = "--full" in args
        if full and not allow_full:
            return False, "full_validation_guarded_until_acee20"
        return True, ""

    def _run(self, spec: Mapping[str, Any], allow_full: bool) -> Dict[str, Any]:
        name = str(spec.get("name") or "unnamed")
        argv_raw = spec.get("argv")
        argv = [str(x) for x in argv_raw] if isinstance(argv_raw, list) else []
        timeout = _float(spec.get("timeout_seconds"), 60.0)
        allowed, reason = self._allowed_command(argv, allow_full)
        if not allowed:
            return {"name": name, "argv": argv, "status": "blocked", "passed": False, "returncode": None, "timed_out": False, "duration_seconds": 0.0, "stdout": "", "stderr": "", "blocking_reason": reason}
        result = run_closed_validation(argv, cwd=self.root, timeout_seconds=timeout)
        timed_out = result["timed_out"] is True
        passed = (not timed_out) and result["returncode"] == 0
        return {"name": name, "argv": argv, "status": "timeout" if timed_out else ("passed" if passed else "failed"),
            "passed": passed, "returncode": result["returncode"], "timed_out": timed_out,
            "duration_seconds": result["duration_seconds"], "stdout": result["stdout"], "stderr": result["stderr"],
            "blocking_reason": "command_timeout" if timed_out else "",
            "process_group_terminated": result["process_group_terminated"], "forced_kill": result["forced_kill"]}

    def _normalize(self, raw: Mapping[str, Any], index: int) -> Dict[str, Any]:
        value = _mapping(raw)
        name = str(value.get("name") or f"command-{index}")
        stdout = str(value.get("stdout") or value.get("output") or "")
        stderr = str(value.get("stderr") or "")
        returncode = value.get("returncode")
        timed_out = value.get("timed_out") is True or str(value.get("status") or "").lower() == "timeout"
        blocked = str(value.get("status") or "").lower() == "blocked" or bool(value.get("blocking_reason"))
        passed = value.get("passed") is True or (returncode == 0 and not timed_out and not blocked)
        if timed_out:
            status = "timeout"
        elif blocked:
            status = "blocked"
        elif passed:
            status = "passed"
        else:
            status = "failed"
        text = stdout + "\n" + stderr
        benign = sorted({token for token in BENIGN_WARNING_TOKENS if token in text})
        warning_lines = [line for line in text.splitlines() if "Warning" in line]
        non_benign = [line for line in warning_lines if not any(token in line for token in benign)]
        return {"name": name, "argv": list(value.get("argv") or []), "status": status, "passed": status == "passed", "returncode": returncode, "timed_out": timed_out, "duration_seconds": round(float(value.get("duration_seconds") or 0.0), 6), "stdout": stdout, "stderr": stderr, "blocking_reason": str(value.get("blocking_reason") or ""), "benign_warnings": benign, "non_benign_warnings": non_benign}

    def _build(self, supplied: Mapping[str, Any], previous_hash: Optional[str], corrupted: bool) -> Dict[str, Any]:
        mode = str(supplied.get("mode") or "targeted").lower()
        scope = str(supplied.get("scope") or "unspecified")
        blocking: List[str] = []
        if mode not in ALLOWED_MODES:
            blocking.append("unsupported_validation_mode")
        allow_full = (
            supplied.get("allow_full_validation") is True
            and str(supplied.get("milestone") or "").upper()
            in {"ACEE20", "ACEE6-F2"}
        )
        if mode == "full_isolated" and not allow_full:
            blocking.append("full_validation_guarded_until_acee20")
        results: List[Dict[str, Any]] = []
        if supplied.get("execute_commands") is True and not blocking:
            commands = supplied.get("commands")
            if not isinstance(commands, list) or not commands:
                blocking.append("commands_missing")
            else:
                stop_on_failure = supplied.get("stop_on_failure") is not False
                for spec in commands:
                    normalized = self._normalize(
                        self._run(_mapping(spec), allow_full),
                        len(results),
                    )
                    results.append(normalized)
                    if stop_on_failure and normalized["status"] != "passed":
                        break
        else:
            raw_results = supplied.get("command_results")
            if isinstance(raw_results, list):
                for raw in raw_results:
                    results.append(self._normalize(_mapping(raw), len(results)))
            elif not blocking:
                blocking.append("command_results_missing")
        failed = [item["name"] for item in results if item["status"] == "failed"]
        timed_out = [item["name"] for item in results if item["timed_out"]]
        blocked_commands = [item["name"] for item in results if item["status"] == "blocked"]
        benign = sorted({warning for item in results for warning in item["benign_warnings"]})
        non_benign = [warning for item in results for warning in item["non_benign_warnings"]]
        error_count = len(failed) + len(timed_out) + len(blocked_commands) + len(blocking)
        passed = bool(results) and error_count == 0
        complete = bool(results) and not blocking
        status = STATUS_READY if passed else (STATUS_BLOCKED if blocking or blocked_commands else STATUS_FAILED)
        result: Dict[str, Any] = {
            "primitive": PRIMITIVE, "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "validation_id": str(supplied.get("validation_id") or "validation-unspecified"),
            "timestamp_utc": str(supplied.get("timestamp_utc") or _now()),
            "scope": scope, "mode": mode, "validation_status": status,
            "validation_complete": complete, "validation_passed": passed,
            "command_results": results, "failed_commands": failed,
            "timed_out_commands": timed_out, "blocked_commands": blocked_commands,
            "warning_count": len(benign) + len(non_benign), "benign_warnings": benign,
            "non_benign_warnings": non_benign, "error_count": error_count,
            "rollback_required": not passed, "blocking_reasons": sorted(set(blocking)),
            "full_validation_requested": mode == "full_isolated",
            "full_validation_authorized": allow_full,
            "history_corrupted": corrupted, "previous_validation_hash": previous_hash,
            "shell_used": False, "global_validation_executed": mode == "full_isolated" and supplied.get("execute_commands") is True and allow_full,
            "consciousness_proven": False, "subjectivity_proven": False,
            "qualia_proven": False, "phenomenology_proven": False,
            "collective_consciousness_proven": False, "collective_subjectivity_proven": False,
            "collective_qualia_proven": False, "collective_phenomenology_proven": False,
            "functional_conclusion_only": True, "phenomenology_undetermined": True,
        }
        result["evidence_manifest"] = [{"name": item["name"], "status": item["status"], "returncode": item["returncode"], "duration_seconds": item["duration_seconds"]} for item in results]
        result["result_hash"] = _sha({k: v for k, v in result.items() if k != "result_hash"})
        return result

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        latest, history, lock = self._paths()
        previous, corrupted = self._previous(history)
        result = self._build(supplied, previous.get("result_hash") if previous else None, corrupted)
        result.update({"persisted": False, "latest_path": str(latest), "history_path": str(history)})
        if persist:
            latest.parent.mkdir(parents=True, exist_ok=True)
            with lock.open("a+", encoding="utf-8") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                previous, corrupted = self._previous(history)
                result = self._build(supplied, previous.get("result_hash") if previous else None, corrupted)
                record = dict(result)
                record.update({"persisted": True, "latest_path": str(latest), "history_path": str(history)})
                tmp = latest.with_suffix(".tmp")
                tmp.write_text(json.dumps(record, sort_keys=True, indent=2), encoding="utf-8")
                tmp.replace(latest)
                with history.open("a", encoding="utf-8") as stream:
                    stream.write(_canonical(record) + "\n")
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                result = record
        return result
