import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
BOUND = (
    "oif/interface/__init__.py", "oif/interface/models.py", "oif/interface/specification.py",
    "oif2b_canonical_manifest_model_functional_test.py",
    "oif2b_canonical_manifest_model_degradation_test.py",
    "oif2b_canonical_manifest_model_immutability_test.py",
    "oif2b_canonical_manifest_model_security_test.py",
    "oif2b_canonical_manifest_model_determinism_test.py",
    "oif2b_fast_acceptance_suite.py",
)
for name in ("oif2b_fast_acceptance_suite.py", "oif2b_canonical_manifest_model_non_regression_test.py"):
    run = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1800)
    if run.returncode:
        raise AssertionError("%s failed:\n%s" % (name, run.stdout))
rows = []
for rel in BOUND:
    path = ROOT / rel
    assert path.is_file(), rel
    rows.append((rel, hashlib.sha256(path.read_bytes()).hexdigest()))
payload = {
    "status": "OIF2B_FINAL_LOCK_OK",
    "oif2b_complete": True,
    "oif2c_started": False,
    "oif2c_authorized": False,
    "bound_files": rows,
}
canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
payload["lock_sha256"] = hashlib.sha256(canonical).hexdigest()
report = ROOT / "oif2b_canonical_manifest_model_final_lock_report.json"
report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("OIF2B_FINAL_LOCK_OK", payload["lock_sha256"])
