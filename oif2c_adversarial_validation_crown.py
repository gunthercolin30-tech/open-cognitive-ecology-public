from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INNER = (
    "oif2c_schema_boundary_campaign_test.py",
    "oif2c_yaml_adversarial_campaign_test.py",
    "oif2c_recursive_security_campaign_test.py",
    "oif2c_cross_format_equivalence_campaign_test.py",
    "oif2c_final_lock_tamper_test.py",
)

def run(name):
    proc = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=7200)
    if proc.returncode:
        raise AssertionError("%s failed:\n%s" % (name, proc.stdout))

def gate():
    report = json.loads((ROOT / "oif2c_json_schema_yaml_final_lock_report.json").read_text(encoding="utf-8"))
    assert report.get("oif2c_complete") is True
    assert report.get("oif2d_started") is False
    assert report.get("oif2d_authorized") is False

for name in INNER:
    run(name)
gate()
if "--inner" in sys.argv:
    print("OIF2C_ADVERSARIAL_CROWN_INNER_OK")
else:
    run("oif2c_non_modification_test.py")
    run("oif2c_json_schema_yaml_final_lock.py")
    gate()
    print("OIF2C_ADVERSARIAL_CROWN_OK")
