import hashlib, json
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
r=json.loads((ROOT/"validation_evidence/p020_final_lock_report.json").read_text(encoding="utf-8"))
assert r["milestone"]=="P020" and r["status"]=="LOCKED" and r["scope"]=="P020_ONLY"
assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
assert all(r["boundaries"].values())
for rel,expected in r["protected_hashes"].items():
    p=ROOT/rel
    assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==expected, rel
payload={"milestone":"P020","scope":"P020_ONLY","protected_hashes":r["protected_hashes"],"tests":r["tests"],"functional_conclusion_only":True,"phenomenology_undetermined":True}
identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
assert identity==r["lock_identity_sha256"]
print("P020_FINAL_LOCK_INTEGRITY_OK")
print("lock_identity_sha256="+identity)
print("protected_file_count="+str(r["protected_file_count"]))
