#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"; MANIFEST=ROOT/"acee6_i1_extended_suite_manifest.json"
FILES=[ROOT/"ontology"/"acee_installation_executor.py",ROOT/"acee6_i1_fast_acceptance_suite.py",ROOT/"acee6_i1_extended_recovery_suite.py",ROOT/"acee6_i1_suite_integration_maintenance_test.py",MANIFEST]
for p in FILES: assert p.is_file(),p; assert hashlib.sha256(p.read_bytes()).hexdigest()
data=json.loads(MANIFEST.read_text(encoding="utf-8"))
for name,wanted in sorted(data["files"].items()):
 p=ROOT/name; assert p.is_file(),p; assert hashlib.sha256(p.read_bytes()).hexdigest()==wanted,name
for name in ["acee6_i1_fast_acceptance_suite.py","acee6_i1_extended_recovery_suite.py","acee6_i1_suite_integration_maintenance_test.py"]: subprocess.run([sys.executable,str(ROOT/name)],cwd=str(ROOT),check=True)
print("ACEE6_I1_FINAL_LOCK_OK")
