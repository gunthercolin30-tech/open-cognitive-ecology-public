from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TESTS=['acee6_k0_contract_test.py','acee6_k0_baseline_test.py','acee6_k0_orchestrator_test.py','acee6_k0_report_tamper_test.py','acee6_k0_non_regression_test.py']
for name in TESTS:
    completed=subprocess.run([sys.executable,str(ROOT/name)],cwd=str(ROOT),text=True,capture_output=True,timeout=120)
    if completed.returncode:
        raise SystemExit(f'{name} failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}')
    print(completed.stdout.strip())
print('ACEE6_K0_FAST_ACCEPTANCE_OK')
