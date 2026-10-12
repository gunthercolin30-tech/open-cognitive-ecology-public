import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TESTS = (
    "acee6_c_multiprocess_preparation_test.py",
    "acee6_c_preparing_interruption_recovery_test.py",
    "acee6_c_partial_journal_fail_closed_test.py",
    "acee6_c_snapshot_divergence_test.py",
    "acee6_c_transaction_id_collision_test.py",
    "acee6_c_filesystem_permissions_test.py",
)

for test_name in TESTS:
    completed = subprocess.run(
        [sys.executable, str(ROOT / test_name)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        print(completed.stdout, end="")
        print(completed.stderr, end="", file=sys.stderr)
        raise SystemExit(
            f"ACEE6_C_HARDENING_FAILED:{test_name}"
        )

print("ACEE6_C_HARDENING_ALL_OK")
