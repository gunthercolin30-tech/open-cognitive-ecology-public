from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
TESTS = (
    "oif2e_secure_reference_resolver_functional_test.py",
    "oif2e_secure_reference_resolver_degradation_test.py",
    "oif2e_secure_reference_resolver_security_test.py",
    "oif2e_secure_reference_resolver_determinism_test.py",
    "oif2e_secure_reference_resolver_non_modification_test.py",
    "oif2e_secure_reference_resolver_non_regression_test.py",
    "oif2e_fast_acceptance_suite.py",
)
TARGETS = (
    "oif/interface/reference_catalog.py",
    "oif/interface/reference_resolver.py",
    "oif/interface/__init__.py",
) + TESTS
results = []
for script in TESTS:
    result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
    results.append({"script": script, "returncode": result.returncode, "output": result.stdout[-4000:]})
    assert result.returncode == 0, result.stdout
report = {
    "primitive": "OIF2E_SECURE_REFERENCE_RESOLVER_FINAL_LOCK",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "tests": results,
    "sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in TARGETS},
    "locked": True,
}
path = ROOT / "oif2e_secure_reference_resolver_final_lock_report.json"
tmp = path.with_suffix(path.suffix + ".tmp")
tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
tmp.replace(path)
print("OIF2E_FINAL_LOCK_OK")
