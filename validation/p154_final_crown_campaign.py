from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
steps=[
 "validation/p154_functional_test.py",
 "validation/p154_degradation_test.py",
 "validation/p154_adversarial_test.py",
 "validation/p154_adversarial_crown_test.py",
 "validation/p154_final_adversarial_crown_v2_test.py",
 "validation/p154_non_regression_test.py",
 "validation/p154_cwd_independence_test.py",
 "validation/p154_evidence_report.py",
 "validation/p154_final_lock_v2.py",
 "validation/p154_final_lock_v2_integrity_check.py",
 "validation/p154_final_lock_tamper_test.py",
]
for rel in steps:
    cp=subprocess.run([sys.executable,str(ROOT/rel)],cwd=str(ROOT))
    if cp.returncode: raise SystemExit(cp.returncode)
print("P154_FINAL_CROWN_CAMPAIGN_OK")
