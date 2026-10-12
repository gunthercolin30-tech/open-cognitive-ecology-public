from __future__ import annotations
import subprocess,sys
TESTS=["acee6_k1_determinism_test.py","acee6_k1_state_transition_property_test.py","acee6_k1_hash_binding_property_test.py","acee6_k1_permutation_property_test.py","acee6_k1_persist_false_immutability_test.py","acee6_k1_counterexample_minimization_test.py","acee6_k1_report_tamper_test.py","acee6_k1_non_regression_test.py"]
for test in TESTS:
    r=subprocess.run([sys.executable,test],capture_output=True,text=True,timeout=120)
    if r.stdout: print(r.stdout,end="")
    if r.returncode: print(r.stderr,end="",file=sys.stderr); raise SystemExit(r.returncode)
print("ACEE6_K1_FAST_ACCEPTANCE_OK")
