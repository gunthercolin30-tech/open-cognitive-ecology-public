from __future__ import annotations
import subprocess
import sys

TESTS = [
    "acee6_h_thread_transaction_isolation_test.py",
    "acee6_h_multiprocess_g2_transaction_test.py",
    "acee6_h_lock_contention_and_release_test.py",
    "acee6_h_lock_release_after_exception_test.py",
    "acee6_h_transactional_concurrency_non_regression_test.py",
]

for test in TESTS:
    subprocess.run([sys.executable, test], check=True, timeout=120)

print("ACEE6_H_TRANSACTIONAL_CONCURRENCY_ALL_OK")
