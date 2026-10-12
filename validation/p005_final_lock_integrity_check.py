from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/"evidence"/"p005"/"p005_final_lock.json").read_text())
assert lock["canonical_id"]=="P005" and lock["status"]=="LOCKED"
for rel,expected in lock["protected_hashes"].items(): assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected
print("P005_FINAL_LOCK_INTEGRITY_OK")
