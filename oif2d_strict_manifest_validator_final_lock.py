from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
TESTS = (
    "oif2d_strict_manifest_validator_functional_test.py",
    "oif2d_strict_manifest_validator_degradation_test.py",
    "oif2d_strict_manifest_validator_reference_test.py",
    "oif2d_strict_manifest_validator_security_test.py",
    "oif2d_strict_manifest_validator_determinism_test.py",
    "oif2d_strict_manifest_validator_non_modification_test.py",
    "oif2d_strict_manifest_validator_non_regression_test.py",
    "oif2d_fast_acceptance_suite.py",
)
TARGETS = (
    "oif/interface/validation_errors.py",
    "oif/interface/manifest_validator.py",
    "oif/interface/__init__.py",
) + TESTS
results = []
for script in TESTS:
    result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    results.append({"script": script, "returncode": result.returncode, "output": result.stdout[-4000:]})
    assert result.returncode == 0, result.stdout
hashes = {relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() for relative in TARGETS}
report = {
    "primitive": "OIF2D_STRICT_MANIFEST_VALIDATOR_FINAL_LOCK",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "tests": results,
    "sha256": hashes,
    "locked": True,
}
path = ROOT / "oif2d_strict_manifest_validator_final_lock_report.json"
tmp = path.with_suffix(path.suffix + ".tmp")
tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
tmp.replace(path)
print("OIF2D_FINAL_LOCK_OK")
