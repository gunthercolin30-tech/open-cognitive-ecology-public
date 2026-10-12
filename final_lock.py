#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 final_lock.py <axis>")
        return 2
    scope = sys.argv[1].strip().lower()
    candidates = [
        ROOT / (scope + "_final_lock.py"),
        ROOT / (scope.replace("-", "_") + "_final_lock.py"),
    ]
    for path in candidates:
        if path.exists():
            proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT))
            return proc.returncode
    print(f"Unknown final lock scope: {sys.argv[1]!r}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
