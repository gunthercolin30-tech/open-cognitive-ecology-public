from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
BOUND = (
    "oif/schemas/__init__.py",
    "oif/schemas/oif_interface_schema_v1.json",
    "oif/schemas/examples/minimal_interface.json",
    "oif/schemas/examples/minimal_interface.yaml",
    "oif/schemas/examples/complete_interface.json",
    "oif/schemas/examples/complete_interface.yaml",
    "oif/interface/serialization.py",
    "oif2c_json_schema_yaml_functional_test.py",
    "oif2c_json_schema_yaml_degradation_test.py",
    "oif2c_json_schema_yaml_security_test.py",
    "oif2c_json_schema_yaml_determinism_test.py",
    "oif2c_json_schema_yaml_cross_version_test.py",
    "oif2c_json_schema_yaml_non_regression_test.py",
    "oif2c_fast_acceptance_suite.py",
)
run = subprocess.run(
    [sys.executable, str(ROOT / "oif2c_fast_acceptance_suite.py")],
    cwd=str(ROOT), text=True, stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT, timeout=3600,
)
if run.returncode:
    raise AssertionError(run.stdout)

rows = []
for relative in BOUND:
    path = ROOT / relative
    assert path.is_file(), relative
    rows.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))

payload = {
    "status": "OIF2C_FINAL_LOCK_OK",
    "oif2c_complete": True,
    "oif2d_started": False,
    "oif2d_authorized": False,
    "schema_dialect": "https://json-schema.org/draft/2020-12/schema",
    "bound_files": rows,
}
canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
payload["lock_sha256"] = hashlib.sha256(canonical).hexdigest()
report = ROOT / "oif2c_json_schema_yaml_final_lock_report.json"
report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("OIF2C_FINAL_LOCK_OK", payload["lock_sha256"])
