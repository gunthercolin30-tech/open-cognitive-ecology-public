from pathlib import Path
import subprocess,sys,time
R=Path(__file__).resolve().parent
tests=("oif2g_complex_manifests_functional_test.py","oif2g_complex_manifests_degradation_test.py","oif2g_complex_manifests_cross_reference_test.py","oif2g_complex_manifests_contract_compatibility_test.py","oif2g_complex_manifests_dormant_operations_test.py","oif2g_complex_manifests_round_trip_test.py","oif2g_complex_manifests_abstract_render_test.py","oif2g_complex_manifests_security_test.py","oif2g_complex_manifests_non_modification_test.py","oif2g_complex_manifests_non_regression_test.py")
s=time.monotonic()
for t in tests: subprocess.run([sys.executable,str(R/t)],cwd=str(R),check=True)
elapsed=time.monotonic()-s
(R/"oif2g_fast_acceptance_report.json").write_text(__import__("json").dumps({"milestone":"OIF-2G","ok":True,"tests":list(tests),"elapsed_seconds":elapsed},sort_keys=True,indent=2)+"\n",encoding="utf-8")
print("OIF2G_FAST_ACCEPTANCE_OK total=%.3fs"%elapsed)
