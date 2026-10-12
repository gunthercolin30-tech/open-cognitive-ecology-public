from pathlib import Path
import subprocess
import sys
ROOT = Path.home() / "open-cognitive-ecology"
for name in (
    "oif2a_fast_acceptance_suite.py",
    "oif2a_implicit_contract_consolidation_non_regression_test.py",
    "oif2a_adversarial_validation_crown.py",
    "oif2a_implicit_contract_consolidation_final_lock.py",
):
    path = ROOT / name
    assert path.is_file(), name
    run = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1200)
    if run.returncode:
        raise AssertionError("%s failed:\n%s" % (name, run.stdout))
print("OIF2B_NON_REGRESSION_OK")
