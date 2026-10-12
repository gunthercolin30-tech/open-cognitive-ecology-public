#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,tempfile,shutil
ROOT=Path(__file__).resolve().parents[1]; data=json.loads((ROOT/"evidence"/"p002"/"p002_final_lock.json").read_text()); protected=data["protected_hashes"]
rel=sorted(protected)[0]; src=ROOT/rel
with tempfile.TemporaryDirectory(prefix="p002_tamper_") as td:
 dst=Path(td)/src.name; shutil.copy2(src,dst); assert hashlib.sha256(dst.read_bytes()).hexdigest()==protected[rel]
 with dst.open("ab") as f: f.write(b"\n# P002_TAMPER_PROBE\n")
 assert hashlib.sha256(dst.read_bytes()).hexdigest()!=protected[rel]
print("P002_FINAL_LOCK_TAMPER_OK")
