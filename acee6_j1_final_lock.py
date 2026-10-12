#!/usr/bin/env python3
from __future__ import annotations
import hashlib, subprocess, sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
for path in (ROOT / "ontology" / "acee_installation_executor.py", ROOT / "acee6_j1_fast_acceptance_suite.py", ROOT / "acee6_j1_extended_final_report_suite.py"):
    assert path.is_file(), path
    assert hashlib.sha256(path.read_bytes()).hexdigest()
for test in ("acee6_j1_fast_acceptance_suite.py", "acee6_j1_extended_final_report_suite.py", "acee6_i2_final_lock.py"):
    subprocess.run([sys.executable, str(ROOT / test)], cwd=str(ROOT), check=True)
print("ACEE6_J1_FINAL_LOCK_OK")
