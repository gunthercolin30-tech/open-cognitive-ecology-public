from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
tests=["p005_functional_test.py","p005_degradation_test.py","p005_adversarial_test.py","p005_non_regression_test.py",
"p005_cwd_test.py","p005_adversarial_crown_test.py","p005_external_evidence_integrity_crown_test.py","p005_evidence_report.py","p005_final_lock.py",
"p005_final_lock_integrity_check.py","p005_final_lock_tamper_test.py"]
for name in tests:
    p=subprocess.run([sys.executable,str(ROOT/"validation"/name)],cwd=str(ROOT))
    if p.returncode: raise SystemExit(p.returncode)
print("P005_CAMPAIGN_OK")
