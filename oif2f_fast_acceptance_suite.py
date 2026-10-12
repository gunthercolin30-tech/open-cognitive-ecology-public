import subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SCRIPTS=("oif2f_minimal_manifests_functional_test.py","oif2f_minimal_manifests_degradation_test.py","oif2f_minimal_manifests_round_trip_test.py","oif2f_minimal_manifests_abstract_render_test.py","oif2f_minimal_manifests_security_test.py","oif2f_minimal_manifests_non_modification_test.py","oif2f_minimal_manifests_non_regression_test.py")
start=time.monotonic()
for script in SCRIPTS:
    p=subprocess.run([sys.executable,str(ROOT/script)],cwd=str(ROOT),text=True,capture_output=True)
    if p.returncode:
        print(p.stdout); print(p.stderr,file=sys.stderr); raise SystemExit(p.returncode)
print("OIF2F_FAST_ACCEPTANCE_OK total=%.3fs" % (time.monotonic()-start))
