from __future__ import annotations

import os
import sys
from pathlib import Path


def _guard_stdin_python() -> None:
    if os.environ.get("OCE_DISABLE_FAST_CONTRACT") == "1":
        return
    if os.environ.get("OCE_ALLOW_STDIN_FINAL_LOCK") == "1":
        return
    if not sys.argv or sys.argv[0] != "-":
        return
    cwd = Path.cwd()
    markers = (
        cwd / "fast_acceptance.py",
        cwd / "final_lock.py",
        cwd / "fast_suite_guard.py",
    )
    if not all(path.exists() for path in markers):
        return
    message = (
        "Inline python final locks are disabled in this repository because they "
        "can bypass the fast execution contract. Create a *_final_lock.py file "
        "and run python3 final_lock.py <axis>. To override once, set "
        "OCE_ALLOW_STDIN_FINAL_LOCK=1."
    )
    os.write(2, (message + "\n").encode("utf-8"))
    os._exit(2)


def _guard_generated_acceptance_script() -> None:
    if os.environ.get("OCE_DISABLE_FAST_CONTRACT") == "1":
        return
    if not sys.argv:
        return
    script = Path(sys.argv[0])
    if script.name.endswith("_fast_acceptance_suite.py") or script.name.endswith("_final_lock.py"):
        try:
            from fast_suite_guard import guard_file, print_issues
        except Exception:
            return
        path = script if script.is_absolute() else Path.cwd() / script
        if not path.exists():
            return
        issues = guard_file(path)
        if issues:
            print_issues(path, issues)
            raise SystemExit(
                f"{script.name} violates the fast execution contract before startup. "
                "Use .step(inputs=ready_or_synthetic_context, ...) or run through "
                "fast_acceptance.py/final_lock.py."
            )


_guard_stdin_python()
_guard_generated_acceptance_script()
