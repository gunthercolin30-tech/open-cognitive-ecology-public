from __future__ import annotations

import copy
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
SUITE = ROOT / "acee6_k7_fast_acceptance_suite.py"

EXPECTED_MARKERS = {
    "ACEE6_K7_FUNCTIONAL_OK",
    "ACEE6_K7_HASH_DRIFT_OK",
    "ACEE6_K7_HASH_VIEWS_OK",
    "ACEE6_K7_DECISION_NUMERICAL_OK",
    "ACEE6_K7_RESTART_DRIFT_OK",
    "ACEE6_K7_RESOURCE_PERFORMANCE_OK",
    "ACEE6_K7_TAMPER_OK",
    "ACEE6_K7_CLEANUP_OK",
    "ACEE6_K7_FAST_ACCEPTANCE_OK",
}


def run_suite(cwd: Path, timeout: float = 10.0) -> tuple[float, str]:
    start = time.monotonic()

    completed = subprocess.run(
        [sys.executable, str(SUITE)],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        env=os.environ.copy(),
    )

    elapsed = time.monotonic() - start

    assert completed.returncode == 0, {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

    missing = sorted(
        marker
        for marker in EXPECTED_MARKERS
        if marker not in completed.stdout
    )
    assert not missing, {
        "missing_markers": missing,
        "stdout": completed.stdout,
    }

    return elapsed, completed.stdout


def assert_five_run_budget() -> None:
    durations = []

    for _ in range(5):
        elapsed, _ = run_suite(ROOT)
        durations.append(elapsed)

    assert max(durations) < 10.0, durations

    print(
        "durations_seconds="
        + repr([round(value, 3) for value in durations])
    )
    print(
        "maximum_seconds="
        + repr(round(max(durations), 3))
    )
    print("ACEE6_K7_FIVE_RUN_TIMEOUT_BUDGET_OK")


def assert_cwd_independence() -> None:
    with tempfile.TemporaryDirectory(
        prefix="acee6_k7_cwd_"
    ) as directory:
        elapsed, _ = run_suite(Path(directory))

    assert elapsed < 10.0, elapsed
    print("ACEE6_K7_CWD_INDEPENDENCE_OK")


def assert_no_temp_residue() -> None:
    before = {
        path.resolve()
        for path in Path(tempfile.gettempdir()).glob(
            "acee6_k7_cleanup_*"
        )
    }

    run_suite(ROOT)

    after = {
        path.resolve()
        for path in Path(tempfile.gettempdir()).glob(
            "acee6_k7_cleanup_*"
        )
    }

    assert after == before, {
        "before": sorted(map(str, before)),
        "after": sorted(map(str, after)),
    }

    print("ACEE6_K7_NO_TEMP_RESIDUE_OK")


def assert_shared_result_isolation() -> None:
    from acee6_k7_longitudinal_runner import run_reduced
    from acee6_k7_report_verifier import verify_k7_report

    output = run_reduced(False)
    original = copy.deepcopy(output["report"])

    tampered = copy.deepcopy(output["report"])
    tampered["comparison"]["hash_drift_count"] = 99

    assert not verify_k7_report(tampered)["valid"], tampered
    assert output["report"] == original, {
        "reason": "shared report mutated through tampered copy"
    }
    assert verify_k7_report(output["report"])["valid"], output

    print("ACEE6_K7_SHARED_RESULT_ISOLATION_OK")


def main() -> None:
    assert_five_run_budget()
    assert_cwd_independence()
    assert_no_temp_residue()
    assert_shared_result_isolation()
    print("ACEE6_K7_TIMEOUT_REFINEMENT_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
