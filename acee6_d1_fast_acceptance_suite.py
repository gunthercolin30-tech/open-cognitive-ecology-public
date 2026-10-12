import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
TESTS = (
    "acee6_d1_existing_target_backup_test.py",
    "acee6_d1_new_target_test.py",
    "acee6_d1_idempotence_test.py",
    "acee6_d1_source_divergence_test.py",
    "acee6_d1_non_regression_test.py",
    "acee6_d1_final_lock.py",
)
for name in TESTS:
    completed = subprocess.run([sys.executable, str(ROOT/name)], cwd=str(ROOT), text=True, capture_output=True, timeout=30)
    if completed.returncode:
        print(completed.stdout, end=""); print(completed.stderr, end="", file=sys.stderr)
        raise SystemExit(f"ACEE6_D1_FAST_ACCEPTANCE_FAILED:{name}")
print("ACEE6_D1_FAST_ACCEPTANCE_OK")
