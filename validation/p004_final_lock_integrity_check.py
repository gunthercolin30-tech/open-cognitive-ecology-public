from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/"evidence"/"p004"/"p004_final_lock.json").read_text(encoding="utf-8"))
assert d["status"]=="LOCKED"
for rel,h in d["protected_hashes"].items(): assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
print("P004_FINAL_LOCK_INTEGRITY_OK")
