#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
AXIS = "acee6"
AXIS_UPPER = "ACEE6"


def axis_artifacts() -> list[Path]:
    prefixes = (f"{AXIS}_", f"{AXIS}-", AXIS)
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
        f"No {AXIS_UPPER} axis artifacts found yet. "
        f"Create at least one {AXIS}_* module/directory or replace this bootstrap suite "
        "with module-specific checks."
    )
    print(f"{AXIS_UPPER}_FAST_ACCEPTANCE_BOOTSTRAP_OK artifacts={len(artifacts)}")


if __name__ == "__main__":
    main()
