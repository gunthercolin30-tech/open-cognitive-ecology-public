from pathlib import Path
import subprocess
import sys
ROOT = Path.home() / "open-cognitive-ecology"
for name in (
    "oif2b_canonical_manifest_model_functional_test.py",
    "oif2b_canonical_manifest_model_degradation_test.py",
    "oif2b_canonical_manifest_model_immutability_test.py",
    "oif2b_canonical_manifest_model_security_test.py",
    "oif2b_canonical_manifest_model_determinism_test.py",
):
    run = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    if run.returncode:
        raise AssertionError("%s failed:\n%s" % (name, run.stdout))
print("OIF2B_FAST_ACCEPTANCE_ALL_OK")
