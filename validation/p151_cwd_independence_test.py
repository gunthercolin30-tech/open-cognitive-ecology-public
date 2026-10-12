from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TESTS = [
    "p151_functional_test.py",
    "p151_degradation_test.py",
    "p151_adversarial_test.py",
    "p151_non_regression_test.py",
    "p151_adversarial_crown_test.py",
]

with tempfile.TemporaryDirectory() as directory:
    for name in TESTS:
        result = subprocess.run(
            [sys.executable, str(ROOT / "validation" / name)],
            cwd=directory,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode:
            print(result.stdout)
            raise SystemExit(result.returncode)

print("P151_CWD_INDEPENDENCE_OK")
