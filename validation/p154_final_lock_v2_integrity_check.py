from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/"evidence/p154/p154_final_lock.json").read_text())
assert lock["lock_revision"]=="FINAL_ADVERSARIAL_CROWN_V2"
assert lock["real_economic_hypotheses_validated"] is False
for rel,expected in lock["protected_hashes"].items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected,rel
body=dict(lock); expected=body.pop("lock_sha256")
got=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
assert got==expected,(expected,got)
print("P154_FINAL_LOCK_V2_INTEGRITY_OK")
