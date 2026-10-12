import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTS = (
    "acee6_c_functional_test.py",
    "acee6_c_no_candidate_mutation_test.py",
    "acee6_c_snapshot_integrity_test.py",
    "acee6_c_idempotence_test.py",
    "acee6_c_journal_chain_test.py",
    "acee6_c_corruption_fail_closed_test.py",
    "acee6_c_lock_collision_test.py",
    "acee6_c_non_regression_test.py",
    "acee6_c_final_lock.py",
)
for test_name in TESTS:
    completed = subprocess.run([sys.executable, str(ROOT / test_name)], cwd=str(ROOT), text=True, capture_output=True, timeout=30, check=False)
    if completed.returncode != 0:
        print(completed.stdout, end="")
        print(completed.stderr, end="", file=sys.stderr)
        raise SystemExit(f"ACEE6_C_FAST_ACCEPTANCE_FAILED:{test_name}")
print("ACEE6_C_FAST_ACCEPTANCE_OK")
