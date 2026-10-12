#!/usr/bin/env python3
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
for name in (
    "acee6_i2_public_schema_compatibility_test.py",
    "acee6_i2_unicode_casefold_collision_test.py",
    "acee6_i2_suite_integrity_test.py",
):
    completed = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)
print("ACEE6_I2_CLOSURE_MICRO_CROWN_OK")
