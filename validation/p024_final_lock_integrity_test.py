"""P024 Final Lock integrity test."""
from pathlib import Path
import hashlib,json
ROOT=Path.home()/"open-cognitive-ecology"
REPORT=ROOT/"validation_evidence/p024_final_lock_report.json"
def main():
 r=json.loads(REPORT.read_text(encoding="utf-8"))
 assert r["milestone"]=="P024" and r["status"]=="LOCKED" and r["scope"]=="P024_ONLY"
 assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
 assert r["p023_preserved"] is True and r["absolute_security_claimed"] is False
 current={}
 for rel,expected in r["protected_hashes"].items():
  p=ROOT/rel; assert p.is_file(),rel
  got=hashlib.sha256(p.read_bytes()).hexdigest(); assert got==expected,rel
  current[rel]=got
 identity=hashlib.sha256(json.dumps(current,sort_keys=True,separators=(",",":")).encode()).hexdigest()
 assert identity==r["lock_identity_sha256"]
 print("P024_FINAL_LOCK_INTEGRITY_OK")
 print("lock_identity_sha256="+identity)
 print("protected_file_count="+str(len(current)))
if __name__=="__main__": main()
