from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validation.integration_report import (
    _compute_statistics,
    discover_modules,
)

ROOT = Path(__file__).resolve().parent.parent
TEXT_REPORT = ROOT / "ontology_integration_report.txt"
JSON_REPORT = ROOT / "scientific_validation_report.json"
SCIENTIFIC_TEXT_REPORT = ROOT / "scientific_validation_report.txt"
CHECKPOINT = ROOT / "full_validation_checkpoint.jsonl"


def _env_float(name: str, default: float) -> float:
    try:
        return max(0.1, float(os.environ.get(name, default)))
    except (TypeError, ValueError):
        return default


def _module_timeout() -> float:
    return _env_float("OCE_FULL_MODULE_TIMEOUT", 20.0)


def _timeout_retry_multiplier() -> float:
    return min(3.0, max(1.0, _env_float("OCE_FULL_TIMEOUT_RETRY_MULTIPLIER", 2.0)))


def _write_checkpoint(record: dict[str, Any]) -> None:
    with CHECKPOINT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def _probe_module(module_name: str, timeout: float) -> tuple[dict[str, Any], str]:
    env = os.environ.copy()
    env.setdefault("PYTHONPYCACHEPREFIX", "/private/tmp/oce_pycache")
    command = [sys.executable, "-m", "validation.module_probe", module_name]

    try:
        completed = subprocess.run(
            command,
            cwd=str(ROOT),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return (
            {
                "module": module_name,
                "import_success": False,
                "import_error": f"ValidationTimeout: exceeded {timeout:.1f}s",
                "classes": [],
                "validation_timeout": True,
                "captured_stdout": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
                "captured_stderr": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
            },
            "timeout",
        )

    raw = completed.stdout.strip().splitlines()
    last_line = raw[-1] if raw else ""
    try:
        payload = json.loads(last_line)
    except json.JSONDecodeError:
        return (
            {
                "module": module_name,
                "import_success": False,
                "import_error": "ProbeProtocolError: invalid JSON response",
                "classes": [],
                "probe_returncode": completed.returncode,
                "captured_stdout": completed.stdout[-4000:],
                "captured_stderr": completed.stderr[-4000:],
            },
            "protocol_error",
        )

    result = payload.get("result")
    if payload.get("success") and isinstance(result, dict):
        result["probe_returncode"] = completed.returncode
        result["captured_stdout"] = payload.get("captured_stdout", "")
        result["captured_stderr"] = payload.get("captured_stderr", "")
        return result, "ok"

    return (
        {
            "module": module_name,
            "import_success": False,
            "import_error": payload.get("error", "ProbeFailure"),
            "classes": [],
            "probe_returncode": completed.returncode,
            "captured_stdout": payload.get("captured_stdout", ""),
            "captured_stderr": payload.get("captured_stderr", "") or completed.stderr[-4000:],
        },
        "probe_error",
    )


def _probe_module_with_retry(
    module_name: str,
    timeout: float,
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    result, status = _probe_module(module_name, timeout)
    metadata: dict[str, Any] = {
        "attempts": 1,
        "initial_status": status,
        "initial_timeout_seconds": timeout,
        "retry_performed": False,
    }
    if status != "timeout":
        return result, status, metadata

    retry_timeout = min(60.0, timeout * _timeout_retry_multiplier())
    metadata.update(
        {
            "attempts": 2,
            "retry_performed": True,
            "retry_timeout_seconds": retry_timeout,
        }
    )
    retry_result, retry_status = _probe_module(module_name, retry_timeout)
    metadata["retry_status"] = retry_status
    if retry_status == "ok":
        retry_result["transient_timeout_recovered"] = True
        retry_result["initial_timeout_seconds"] = timeout
        retry_result["retry_timeout_seconds"] = retry_timeout
    return retry_result, retry_status, metadata


def _render_integration_report(results: list[dict[str, Any]], metadata: dict[str, Any]) -> str:
    stats = _compute_statistics(results)
    timeout_count = sum(1 for item in results if item.get("validation_timeout"))
    probe_error_count = sum(
        1
        for item in results
        if item.get("probe_returncode") not in (None, 0)
    )

    lines = [
        "ONTOLOGY FULL VALIDATION REPORT",
        "=" * 80,
        "",
        "RUN METADATA",
        "-" * 80,
    ]
    for key, value in metadata.items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "GLOBAL STATISTICS", "-" * 80])
    for key, value in stats.items():
        lines.append(f"{key}: {value}")
    lines.append(f"timeouts: {timeout_count}")
    lines.append(f"probe_errors: {probe_error_count}")
    lines.append("")
    lines.append("MODULE DETAILS")
    lines.append("-" * 80)

    for module_result in results:
        lines.append("")
        lines.append(f"Module: {module_result.get('module')}")
        lines.append(f"Import success: {module_result.get('import_success')}")
        if module_result.get("validation_timeout"):
            lines.append("Validation timeout: True")
        if module_result.get("import_error"):
            lines.append(f"Import/probe warning: {module_result.get('import_error')}")
        classes = module_result.get("classes", [])
        lines.append(f"Classes detected: {len(classes)}")
        for class_result in classes:
            lines.append(f"  Class: {class_result.get('class_name')}")
            lines.append(f"    Instantiated: {class_result.get('instantiated')}")
            step = class_result.get("step_analysis", {})
            lines.append(f"    Step executed: {step.get('step_executed')}")
            if step.get("step_warning"):
                lines.append(f"    Step warning: {step.get('step_warning')}")
            if step.get("step_error"):
                lines.append(f"    Step error: {step.get('step_error')}")
    lines.append("")
    return "\n".join(lines)


def _scientific_report(results: list[dict[str, Any]], metadata: dict[str, Any]) -> dict[str, Any]:
    stats = _compute_statistics(results)
    timeout_modules = [item.get("module") for item in results if item.get("validation_timeout")]
    failed_modules: list[str] = []
    for item in results:
        module_name = item.get("module")
        if not isinstance(module_name, str):
            continue

        import_failed = (
            not item.get("import_success")
            and not item.get("validation_timeout")
        )
        probe_failed = item.get("probe_returncode") not in (None, 0)
        step_failed = any(
            bool(
                class_result.get("step_analysis", {}).get("step_error")
            )
            for class_result in item.get("classes", [])
            if isinstance(class_result, dict)
        )

        if import_failed or probe_failed or step_failed:
            failed_modules.append(module_name)

    failed_modules = list(dict.fromkeys(failed_modules))
    error_count = int(stats.get("errors", 0))
    failed_calls = error_count
    overall_success = (
        error_count == 0
        and not timeout_modules
        and not failed_modules
    )
    return {
        "validation_mode": "full_isolated",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata,
        "diagnostics": {
            **stats,
            "error_count": error_count,
            "failed_calls": failed_calls,
            "timeouts": len(timeout_modules),
            "timeout_modules": timeout_modules,
            "failed_modules": failed_modules,
        },
        "tests": [
            {
                "name": "module_discovery",
                "passed": stats.get("modules_discovered", 0) > 0,
                "value": stats.get("modules_discovered", 0),
                "expected": "> 0",
            },
            {
                "name": "error_free_execution",
                "passed": error_count == 0,
                "value": {"error_count": error_count, "failed_calls": failed_calls},
                "expected": {"error_count": 0, "failed_calls": 0},
            },
            {
                "name": "no_timeouts",
                "passed": not timeout_modules,
                "value": timeout_modules,
                "expected": [],
            },
            {
                "name": "imports_complete",
                "passed": not failed_modules,
                "value": failed_modules,
                "expected": [],
            },
        ],
        "summary": {
            "tests_total": 4,
            "tests_passed": sum([
                stats.get("modules_discovered", 0) > 0,
                error_count == 0,
                not timeout_modules,
                not failed_modules,
            ]),
            "tests_failed": 4 - sum([
                stats.get("modules_discovered", 0) > 0,
                error_count == 0,
                not timeout_modules,
                not failed_modules,
            ]),
            "overall_success": overall_success,
        },
    }


def main() -> dict[str, Any]:
    started = time.monotonic()
    timeout = _module_timeout()
    module_names = discover_modules()
    module_filter = os.environ.get("OCE_FULL_MODULE_FILTER", "").strip()
    if module_filter:
        module_names = [
            name for name in module_names
            if module_filter.lower() in name.lower()
        ]
    try:
        max_modules = int(os.environ.get("OCE_FULL_MAX_MODULES", "0"))
    except ValueError:
        max_modules = 0
    if max_modules > 0:
        module_names = module_names[:max_modules]
    total = len(module_names)

    CHECKPOINT.unlink(missing_ok=True)
    print(
        f"FULL_VALIDATION_START modules={total} module_timeout={timeout:.1f}s",
        flush=True,
    )

    results: list[dict[str, Any]] = []
    for index, module_name in enumerate(module_names, start=1):
        module_started = time.monotonic()
        print(
            f"FULL_VALIDATION [{index}/{total}] START {module_name}",
            flush=True,
        )
        result, status, probe_attempts = _probe_module_with_retry(
            module_name,
            timeout,
        )
        elapsed = time.monotonic() - module_started
        results.append(result)
        checkpoint_record = {
            "index": index,
            "total": total,
            "module": module_name,
            "status": status,
            "elapsed_seconds": round(elapsed, 6),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "probe_attempts": probe_attempts,
            "result": result,
        }
        _write_checkpoint(checkpoint_record)
        print(
            f"FULL_VALIDATION [{index}/{total}] {status.upper()} "
            f"{module_name} elapsed={elapsed:.3f}s",
            flush=True,
        )

    total_elapsed = time.monotonic() - started
    metadata = {
        "modules_requested": total,
        "module_filter": module_filter,
        "max_modules": max_modules,
        "module_timeout_seconds": timeout,
        "elapsed_seconds": round(total_elapsed, 6),
        "checkpoint_file": str(CHECKPOINT),
        "full_validation_deferred": False,
    }

    integration_text = _render_integration_report(results, metadata)
    TEXT_REPORT.write_text(integration_text, encoding="utf-8")

    scientific = _scientific_report(results, metadata)
    JSON_REPORT.write_text(
        json.dumps(scientific, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    summary = scientific["summary"]
    diagnostics = scientific["diagnostics"]
    text_lines = [
        "SCIENTIFIC VALIDATION REPORT",
        "=" * 80,
        f"validation_mode: {scientific['validation_mode']}",
        f"modules_discovered: {diagnostics['modules_discovered']}",
        f"active_primitives: {diagnostics['classes_detected']}",
        f"error_count: {diagnostics['error_count']}",
        f"failed_calls: {diagnostics['failed_calls']}",
        f"timeouts: {diagnostics['timeouts']}",
        f"failed_modules: {len(diagnostics['failed_modules'])}",
        f"overall_success: {summary['overall_success']}",
        f"elapsed_seconds: {metadata['elapsed_seconds']}",
        "",
    ]
    SCIENTIFIC_TEXT_REPORT.write_text("\n".join(text_lines), encoding="utf-8")

    print(f"validation_report_saved={TEXT_REPORT.name}", flush=True)
    print(f"scientific_json_report_saved={JSON_REPORT.name}", flush=True)
    print(f"scientific_text_report_saved={SCIENTIFIC_TEXT_REPORT.name}", flush=True)
    print(f"error_count={diagnostics['error_count']}", flush=True)
    print(f"failed_calls={diagnostics['failed_calls']}", flush=True)
    print(f"timeouts={diagnostics['timeouts']}", flush=True)
    print(f"failed_modules={len(diagnostics['failed_modules'])}", flush=True)
    print(f"FULL_VALIDATION_COMPLETE success={summary['overall_success']}", flush=True)

    return scientific


if __name__ == "__main__":
    report = main()
    raise SystemExit(0 if report["summary"]["overall_success"] else 1)
