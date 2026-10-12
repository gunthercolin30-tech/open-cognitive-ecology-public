import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TESTS = (
    "acee6_d2_mutation_lock_collision_test.py",
    "acee6_d2_interrupt_before_replace_test.py",
    "acee6_d2_interrupt_after_replace_test.py",
    "acee6_d2_target_divergence_after_d1_test.py",
    "acee6_d2_backup_corruption_before_mutation_test.py",
    "acee6_d2_target_symlink_swap_test.py",
    "acee6_d2_target_hardlink_swap_test.py",
    "acee6_d2_permissions_failure_test.py",
    "acee6_d2_multiprocess_mutation_test.py",
    "acee6_d2_mutated_target_tamper_test.py",
    "acee6_d2_mutation_manifest_tamper_test.py",
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
            f"ACEE6_D2_HARDENING_FAILED:{test_name}"
        )

print("ACEE6_D2_HARDENING_ALL_OK")
