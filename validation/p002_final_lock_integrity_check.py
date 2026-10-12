#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]; LOCK=ROOT/"evidence"/"p002"/"p002_final_lock.json"
data=json.loads(LOCK.read_text()); protected=data.get("protected_hashes")
assert isinstance(protected,dict) and protected,"missing protected_hashes"
for rel,expected in protected.items():
 p=ROOT/rel; assert p.is_file(),f"missing:{rel}"; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,f"tamper:{rel}"
print("P002_FINAL_LOCK_INTEGRITY_OK")
