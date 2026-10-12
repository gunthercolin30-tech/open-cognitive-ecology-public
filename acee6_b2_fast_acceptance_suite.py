import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TESTS = (
    "acee6_b2_functional_test.py",
    "acee6_b2_existing_target_test.py",
    "acee6_b2_zero_write_test.py",
    "acee6_b2_degradation_test.py",
    "acee6_b2_non_regression_test.py",
    "acee6_b2_determinism_test.py",
    "acee6_b2_unchanged_target_test.py",
    "acee6_b2_plan_hash_sensitivity_test.py",
    "acee6_b2_inventory_projection_test.py",
    "acee6_b2_order_stability_test.py",
    "acee6_b2_final_lock.py",
)

for test_name in TESTS:
    completed = subprocess.run(
        [sys.executable, str(ROOT / test_name)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        print(completed.stdout, end="")
        print(completed.stderr, end="", file=sys.stderr)
        raise SystemExit(
            f"ACEE6_B2_FAST_ACCEPTANCE_FAILED:{test_name}"
        )

print("ACEE6_B2_FAST_ACCEPTANCE_OK")
