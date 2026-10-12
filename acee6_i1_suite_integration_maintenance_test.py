#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"; MANIFEST=ROOT/"acee6_i1_extended_suite_manifest.json"; FINAL_LOCK=ROOT/"acee6_i1_final_lock.py"
assert MANIFEST.is_file(),MANIFEST
data=json.loads(MANIFEST.read_text(encoding="utf-8")); assert data["axis"]=="ACEE6-I1"; assert data["runtime_modified"] is False
expected=data.get("files",{}); assert len(expected)==11,len(expected)
for name,wanted in sorted(expected.items()):
 p=ROOT/name; assert p.is_file(),p; assert hashlib.sha256(p.read_bytes()).hexdigest()==wanted,name
source=FINAL_LOCK.read_text(encoding="utf-8")
for required in ["acee6_i1_fast_acceptance_suite.py","acee6_i1_extended_recovery_suite.py","acee6_i1_suite_integration_maintenance_test.py","acee6_i1_extended_suite_manifest.json"]: assert required in source,required
print("ACEE6_I1_SUITE_INTEGRATION_MAINTENANCE_OK")
