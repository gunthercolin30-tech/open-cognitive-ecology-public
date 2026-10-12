from __future__ import annotations
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
TESTS = [
    "acee6_j2_double_escalation_test.py",
    "acee6_j2_concurrent_escalation_test.py",
    "acee6_j2_gate_corruption_matrix_test.py",
    "acee6_j2_legacy_transaction_compatibility_test.py",
    "acee6_j2_restart_persistence_test.py",
    "acee6_j2_persist_false_tree_hash_test.py",
    "acee6_j2_diagnostic_tamper_test.py",
    "acee6_j2_gate_priority_test.py",
]
for name in TESTS:
    completed = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), text=True, capture_output=True, timeout=120)
    if completed.returncode != 0:
        raise SystemExit(f"{name} failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
    print(completed.stdout.strip())
print("ACEE6_J2_EXTENDED_HARDENING_SUITE_OK")
