from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; d=json.loads((ROOT/"evidence"/"p003"/"p003_final_lock.json").read_text())
assert d["milestone"]=="P003" and d["status"]=="LOCKED"
for rel,exp in d["protected_hashes"].items():
 act=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
 if act!=exp: raise AssertionError(f"tamper:{rel} expected={exp} got={act}")
print("P003_FINAL_LOCK_INTEGRITY_OK")
