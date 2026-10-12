import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TESTS=("acee6_d2_existing_target_test.py","acee6_d2_new_target_test.py","acee6_d2_hash_divergence_test.py","acee6_d2_missing_content_test.py","acee6_d2_idempotence_test.py","acee6_d2_non_regression_test.py","acee6_d2_final_lock.py")
for name in TESTS:
    result=subprocess.run([sys.executable,str(ROOT/name)],cwd=str(ROOT),capture_output=True,text=True,timeout=30)
    if result.returncode:
        print(result.stdout,end=""); print(result.stderr,end="",file=sys.stderr); raise SystemExit(f"ACEE6_D2_FAST_ACCEPTANCE_FAILED:{name}")
print("ACEE6_D2_FAST_ACCEPTANCE_OK")
