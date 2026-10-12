#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
TESTS = [
"acee6_i2_transaction_id_content_divergence_test.py",
"acee6_i2_multiprocess_duplicate_proposal_test.py",
"acee6_i2_corrupted_entry_registry_reconstruction_test.py",
"acee6_i2_persist_false_immutability_test.py",
"acee6_i2_no_double_rollback_test.py",
"acee6_i2_registry_deterministic_order_test.py",
]
for name in TESTS:
    completed = subprocess.run([sys.executable, str(ROOT/name)], cwd=str(ROOT), check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)
print("ACEE6_I2_EXTENDED_REPLAY_SUITE_OK")
