from pathlib import Path
import hashlib,json
ROOT=Path.home()/"open-cognitive-ecology"
r=json.loads((ROOT/"validation_evidence/p021_final_lock_report.json").read_text())
assert r["milestone"]=="P021" and r["status"]=="LOCKED" and r["scope"]=="P021_ONLY"
assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True and r["p022_defined"] is False
cur={}
for rel,expected in r["protected_hashes"].items():
 p=ROOT/rel; got=hashlib.sha256(p.read_bytes()).hexdigest(); assert got==expected,(rel,expected,got); cur[rel]=got
identity=hashlib.sha256(json.dumps(cur,sort_keys=True,separators=(",",":")).encode()).hexdigest()
assert identity==r["lock_identity_sha256"]
print("P021_FINAL_LOCK_INTEGRITY_OK")
print("lock_identity_sha256="+identity)
print("protected_file_count="+str(len(cur)))
