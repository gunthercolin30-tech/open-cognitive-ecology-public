from pathlib import Path
import subprocess, sys

ROOT = Path.home() / "open-cognitive-ecology"
TESTS = (
    "oif2a_implicit_contract_consolidation_functional_test.py",
    "oif2a_implicit_contract_consolidation_degradation_test.py",
    "oif2a_implicit_contract_determinism_test.py",
    "oif2a_implicit_contract_coverage_test.py",
    "oif2a_implicit_contract_non_modification_test.py",
)
for name in TESTS:
    run = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    if run.returncode != 0:
        raise AssertionError("%s failed:\n%s" % (name, run.stdout))
print("OIF2A_FAST_ACCEPTANCE_ALL_OK")
