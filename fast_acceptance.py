#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from fast_suite_guard import guard_file


ROOT = Path(__file__).resolve().parent

SUITE_PATTERN = re.compile(
    r"^(?P<axis>[a-z]+)"
    r"(?P<step>\d+|_axis)?"
    r"(?P<substeps>(?:_[a-z]\d+[a-z0-9]*)*)"
    r"_fast_acceptance_suite\.py$"
)
AXIS_PATTERN = re.compile(r"^[a-z][a-z0-9]*$")
DEFAULT_TIMEOUT_SECONDS = 10.0


def _natural_substep_key(substeps: str) -> tuple[tuple[str, int, str], ...]:
    if not substeps:
        return ()
    tokens: list[tuple[str, int, str]] = []
    for token in substeps.lstrip("_").split("_"):
        match = re.fullmatch(r"(?P<label>[a-z]+)(?P<number>\d+)(?P<tail>[a-z0-9]*)", token)
        if not match:
            tokens.append((token, 9999, ""))
            continue
        tokens.append((match.group("label"), int(match.group("number")), match.group("tail")))
    return tuple(tokens)


def suite_sort_key(path: Path) -> tuple[str, int, int, tuple[tuple[str, int, str], ...], str]:
    match = SUITE_PATTERN.match(path.name)
    if not match:
        return (path.stem, 9999, 9999, (), path.name)
    axis = match.group("axis")
    step = match.group("step") or ""
    substeps = match.group("substeps") or ""
    if step == "_axis":
        order = 0
    elif step.isdigit():
        order = int(step)
    else:
        order = 5000
    substep_key = _natural_substep_key(substeps)
    return (axis, order, len(substep_key), substep_key, path.name)


def discover_suites() -> dict[str, list[str]]:
    suites: dict[str, list[str]] = {}
    for path in sorted(ROOT.glob("*_fast_acceptance_suite.py"), key=suite_sort_key):
        match = SUITE_PATTERN.match(path.name)
        if not match:
            continue
        axis = match.group("axis")
        suites.setdefault(axis, []).append(path.name)
    all_suites: list[str] = []
    for axis in sorted(suites):
        all_suites.extend(suites[axis])
    suites["all"] = all_suites
    return suites


def axis_artifact_candidates(axis: str) -> list[Path]:
    candidates: list[Path] = []
    prefixes = (f"{axis}_", f"{axis}-", axis)
    for path in ROOT.iterdir():
        if path.name.startswith("."):
            continue
        if path.name.endswith("_fast_acceptance_suite.py"):
            continue
        if any(path.name.startswith(prefix) for prefix in prefixes):
            candidates.append(path)
    return sorted(candidates, key=lambda p: (not p.is_dir(), p.name))


def scaffold_axis_suite(axis: str, overwrite: bool = False) -> Path:
    if not AXIS_PATTERN.match(axis):
        raise SystemExit(f"Invalid axis name: {axis!r}")
    path = ROOT / f"{axis}_axis_fast_acceptance_suite.py"
    if path.exists() and not overwrite:
        return path
    axis_upper = axis.upper()
    content = f'''#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
AXIS = "{axis}"
AXIS_UPPER = "{axis_upper}"


def axis_artifacts() -> list[Path]:
    prefixes = (f"{{AXIS}}_", f"{{AXIS}}-", AXIS)
    return sorted(
        [
            path
            for path in ROOT.iterdir()
            if not path.name.startswith(".")
            and not path.name.endswith("_fast_acceptance_suite.py")
            and any(path.name.startswith(prefix) for prefix in prefixes)
        ],
        key=lambda path: (not path.is_dir(), path.name),
    )


def main() -> None:
    artifacts = axis_artifacts()
    assert artifacts, (
        f"No {{AXIS_UPPER}} axis artifacts found yet. "
        f"Create at least one {{AXIS}}_* module/directory or replace this bootstrap suite "
        "with module-specific checks."
    )
    print(f"{{AXIS_UPPER}}_FAST_ACCEPTANCE_BOOTSTRAP_OK artifacts={{len(artifacts)}}")


if __name__ == "__main__":
    main()
'''
    path.write_text(content, encoding="utf-8")
    return path


def ensure_scope(scope: str, suites: dict[str, list[str]]) -> dict[str, list[str]]:
    if scope in suites:
        return suites
    if scope == "all":
        return suites
    if not AXIS_PATTERN.match(scope):
        raise SystemExit(f"Unknown fast acceptance scope: {scope!r}")
    scaffolded = scaffold_axis_suite(scope)
    print(f"Created {scaffolded.name} for new axis '{scope}'.")
    return discover_suites()


def run_suite(script: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> float:
    issues = guard_file(ROOT / script)
    if issues:
        for line, code, message in issues:
            print(f"{script}:{line}: {code}: {message}")
        raise SystemExit(
            f"{script} violates the fast-suite contract. "
            "Inject ready/synthetic inputs before running acceptance."
        )

    start = time.perf_counter()
    env = os.environ.copy()
    env.setdefault("PYTHONPYCACHEPREFIX", "/private/tmp/oce_pycache")
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / script)],
            cwd=str(ROOT),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start
        partial = (exc.stdout or "").strip() if isinstance(exc.stdout, str) else ""
        if partial:
            print(partial)
        print(f"{script}: TIMEOUT after {elapsed:.3f}s")
        raise SystemExit(
            f"{script} exceeded fast acceptance timeout ({timeout:.1f}s). "
            "Inject ready/synthetic dependencies instead of running full validation."
        )
    elapsed = time.perf_counter() - start
    output = result.stdout.strip()
    if output:
        print(output)
    print(f"{script}: {elapsed:.3f}s")
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    return elapsed


def main() -> None:
    suites = discover_suites()
    parser = argparse.ArgumentParser(
        description="Run optimized axis fast acceptance suites without full repository validation."
    )
    parser.add_argument(
        "scope",
        nargs="?",
        default="all",
        help="suite scope to run; default: all",
    )
    parser.add_argument(
        "--new-axis",
        metavar="AXIS",
        help="create <axis>_axis_fast_acceptance_suite.py if it does not exist",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite an existing scaffold when used with --new-axis",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list discovered scopes and suites without running them",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="per-suite timeout in seconds; default: 10",
    )
    args = parser.parse_args()

    if args.new_axis:
        path = scaffold_axis_suite(args.new_axis, overwrite=args.overwrite)
        print(f"FAST_ACCEPTANCE_AXIS_SCAFFOLD_OK {path.name}")
        return

    if args.list:
        for scope in sorted(suites):
            print(f"{scope}: {', '.join(suites[scope])}")
        return

    suites = ensure_scope(args.scope, suites)
    if args.scope not in suites:
        raise SystemExit(f"Unknown fast acceptance scope: {args.scope!r}")

    total = 0.0
    for script in suites[args.scope]:
        total += run_suite(script, timeout=max(0.5, args.timeout))
    print(f"FAST_ACCEPTANCE_{args.scope.upper()}_OK total={total:.3f}s")


if __name__ == "__main__":
    main()
