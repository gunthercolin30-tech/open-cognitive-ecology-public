from __future__ import annotations
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PROTECTED = (
    "oif/application/shell_service.py",
    "oif/application/default_providers.py",
    "oif/ui/navigation_model.py",
    "oif/ui/navigation_preferences.py",
    "ontology_inventory.txt",
)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

before = {name: digest(ROOT / name) for name in PROTECTED if (ROOT / name).is_file()}
run = subprocess.run(
    [sys.executable, str(ROOT / "oif2b_property_campaign_test.py")],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=180,
)
if run.returncode:
    raise AssertionError(run.stdout)
after = {name: digest(ROOT / name) for name in before}
assert before == after
print("OIF2B_NON_MODIFICATION_OK", len(before))
