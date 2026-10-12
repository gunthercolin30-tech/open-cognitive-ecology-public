from __future__ import annotations
import hashlib, subprocess, sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
WATCHED = (ROOT / "oif", ROOT / "ontology_inventory.txt", ROOT / "oif2b_canonical_manifest_model_final_lock_report.json")
EXCLUDED = {"oif2c_json_schema_yaml_final_lock_report.json"}

def snapshot():
    result = {}
    for item in WATCHED:
        paths = (item,) if item.is_file() else tuple(p for p in item.rglob("*") if p.is_file())
        for path in paths:
            rel = str(path.relative_to(ROOT))
            if rel in EXCLUDED or rel.endswith(".pyc") or "__pycache__" in path.parts:
                continue
            result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

before = snapshot()
run = subprocess.run([sys.executable, str(ROOT / "oif2c_adversarial_validation_crown.py"), "--inner"], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=7200)
if run.returncode:
    raise AssertionError(run.stdout)
after = snapshot()
if before != after:
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    raise AssertionError("repository modification detected: %s" % changed[:20])
print("OIF2C_NON_MODIFICATION_OK", len(before))
