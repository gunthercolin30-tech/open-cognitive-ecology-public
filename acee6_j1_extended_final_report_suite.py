#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
TESTS = [
    "acee6_j1_committed_report_test.py",
    "acee6_j1_rolled_back_report_test.py",
    "acee6_j1_quarantine_report_test.py",
    "acee6_j1_missing_proof_degradation_test.py",
    "acee6_j1_report_replay_determinism_test.py",
    "acee6_j1_persist_false_immutability_test.py",
    "acee6_j1_persisted_report_tamper_test.py",
    "acee6_j1_final_hash_journal_link_test.py",
]
for name in TESTS:
    completed = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), check=False)
    if completed.returncode: raise SystemExit(completed.returncode)
print("ACEE6_J1_EXTENDED_FINAL_REPORT_SUITE_OK")
