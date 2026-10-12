#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
MANIFEST = ROOT / "acee6_i2_suite_manifest.json"
assert MANIFEST.is_file(), MANIFEST
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
for name, expected_hash in sorted(manifest["files"].items()):
    path = ROOT / name
    assert path.is_file(), path
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash, name
for test in (
    "acee6_i2_fast_acceptance_suite.py",
    "acee6_i2_extended_replay_suite.py",
    "acee6_i2_closure_micro_crown_suite.py",
    "acee6_i1_final_lock.py",
):
    subprocess.run([sys.executable, str(ROOT / test)], cwd=str(ROOT), check=True)
print("ACEE6_I2_FINAL_LOCK_OK")
