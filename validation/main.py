from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "ontology_integration_report.txt"
ACEE6_ALIASES = frozenset({"ACEE6", "acee6", "ACEE6-B1", "acee6-b1"})
GLOBAL_MARKER = "FAST_ACCEPTANCE_ALL_OK"
ACEE6_SUITE = "acee6_b1_fast_acceptance_suite.py"
ACEE6_MARKER = "ACEE6_B1_FAST_ACCEPTANCE_OK"


def _suite_record(name, output, returncode, duration, marker):
    return {
        "name": name,
        "status": "passed" if returncode == 0 and marker in output else "failed",
        "returncode": returncode,
        "duration_seconds": round(duration, 6),
        "marker": marker,
    }


def _write_fast_report(scope, output, returncode, suites):
    report = {
        "validation_mode": "fast_acceptance",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scope": scope,
        "returncode": returncode,
        "success": returncode == 0,
        "full_validation_deferred": True,
        "full_validation_command": "OCE_FULL_VALIDATION=1 python3 -m validation.main",
        "suites": suites,
        "output": output,
    }
    REPORT_PATH.write_text(
        "Open Cognitive Ecology Fast Validation Report\n"
        + json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return REPORT_PATH


def _run(command, env):
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result, time.monotonic() - started


def _extract_global_marker(output):
    lines = output.splitlines()
    markers = [line for line in lines if line.startswith(GLOBAL_MARKER)]
    kept = [line for line in lines if not line.startswith(GLOBAL_MARKER)]
    return "\n".join(kept).strip(), markers[-1] if markers else None


def _fast_validation(scope="all"):
    env = os.environ.copy()
    env.setdefault("PYTHONPYCACHEPREFIX", "/private/tmp/oce_pycache")
    suites = []
    output_parts = []
    final_returncode = 0
    global_marker_line = None

    if scope in ACEE6_ALIASES:
        suite_path = ROOT / ACEE6_SUITE
        if not suite_path.is_file():
            output = "Missing ACEE6-B1 fast acceptance suite: " + str(suite_path)
            final_returncode = 2
        else:
            result, duration = _run([sys.executable, str(suite_path)], env)
            output = result.stdout or ""
            suites.append(_suite_record(
                ACEE6_SUITE, output, result.returncode, duration, ACEE6_MARKER
            ))
            final_returncode = result.returncode
            if final_returncode == 0 and ACEE6_MARKER not in output:
                final_returncode = 3
        output_parts.append(output.strip())
    else:
        historical, duration = _run(
            [sys.executable, str(ROOT / "fast_acceptance.py"), scope],
            env,
        )
        historical_output = historical.stdout or ""
        stripped, global_marker_line = _extract_global_marker(historical_output)
        if stripped:
            output_parts.append(stripped)
        final_returncode = historical.returncode
        suites.append({
            "name": "fast_acceptance.py",
            "status": "passed" if historical.returncode == 0 else "failed",
            "returncode": historical.returncode,
            "duration_seconds": round(duration, 6),
            "marker": GLOBAL_MARKER,
        })

        if scope == "all" and historical.returncode == 0:
            suite_path = ROOT / ACEE6_SUITE
            if not suite_path.is_file():
                output_parts.append("Missing ACEE6-B1 fast acceptance suite: " + str(suite_path))
                final_returncode = 2
            else:
                acee6, acee6_duration = _run([sys.executable, str(suite_path)], env)
                acee6_output = acee6.stdout or ""
                if acee6_output.strip():
                    output_parts.append(acee6_output.strip())
                suites.append(_suite_record(
                    ACEE6_SUITE,
                    acee6_output,
                    acee6.returncode,
                    acee6_duration,
                    ACEE6_MARKER,
                ))
                if acee6.returncode != 0 or ACEE6_MARKER not in acee6_output:
                    final_returncode = acee6.returncode or 3

        if final_returncode == 0 and global_marker_line:
            output_parts.append(global_marker_line)

    combined = "\n".join(part for part in output_parts if part).strip()
    if combined:
        print(combined)

    path = _write_fast_report(scope, combined, final_returncode, suites)
    print("validation_mode=fast_acceptance")
    print("validation_report_saved=" + str(path.name))
    if final_returncode != 0:
        raise SystemExit(final_returncode)
    return {
        "validation_mode": "fast_acceptance",
        "success": True,
        "report_path": str(path),
        "scope": scope,
        "suites": suites,
    }


def _full_validation():
    completed = subprocess.run(
        [sys.executable, "-m", "validation.full_validation_runner"],
        cwd=str(ROOT),
        env=os.environ.copy(),
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return {
        "validation_mode": "full_isolated",
        "success": True,
        "report_path": str(REPORT_PATH),
    }


def main():
    full_requested = (
        os.environ.get("OCE_FULL_VALIDATION") == "1"
        or "--full" in sys.argv[1:]
    )
    if full_requested:
        return _full_validation()
    return _fast_validation(os.environ.get("OCE_FAST_SCOPE", "all"))


if __name__ == "__main__":
    main()
