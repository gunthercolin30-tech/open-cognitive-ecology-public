from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
tests=["p006_functional_test.py","p006_degradation_test.py","p006_adversarial_test.py","p006_non_regression_test.py",
"p006_cwd_test.py","p006_adversarial_crown_test.py","p006_temporal_preregistration_crown_test.py","p006_evidence_report.py","p006_final_lock.py",
"p006_final_lock_integrity_check.py","p006_final_lock_tamper_test.py"]
for name in tests:
    p=subprocess.run([sys.executable,str(ROOT/"validation"/name)],cwd=str(ROOT))
    if p.returncode: raise SystemExit(p.returncode)
print("P006_CAMPAIGN_OK")
