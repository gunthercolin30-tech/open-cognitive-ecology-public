import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TESTS = (
    "acee6_d1_backup_lock_collision_test.py",
    "acee6_d1_backup_truncation_test.py",
    "acee6_d1_interrupt_before_replace_test.py",
    "acee6_d1_interrupt_after_replace_test.py",
    "acee6_d1_destination_symlink_test.py",
    "acee6_d1_parent_symlink_test.py",
    "acee6_d1_source_hardlink_test.py",
    "acee6_d1_existing_divergent_backup_test.py",
    "acee6_d1_multiprocess_backup_test.py",
    "acee6_d1_permissions_failure_test.py",
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
            f"ACEE6_D1_HARDENING_FAILED:{test_name}"
        )

print("ACEE6_D1_HARDENING_ALL_OK")
