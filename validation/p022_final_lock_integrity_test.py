"""P022 Final Lock integrity test."""
from pathlib import Path
import hashlib, json
ROOT=Path.home()/"open-cognitive-ecology"
REPORT=ROOT/"validation_evidence/p022_final_lock_report.json"
def main():
    r=json.loads(REPORT.read_text(encoding="utf-8"))
    assert r["milestone"]=="P022" and r["status"]=="LOCKED" and r["scope"]=="P022_ONLY"
    assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
    assert r["p021_preserved"] is True and r["p023_defined"] is False and r["p024_defined"] is False
    current={}
    for rel,expected in r["protected_hashes"].items():
        p=ROOT/rel
        assert p.is_file(), rel
        got=hashlib.sha256(p.read_bytes()).hexdigest()
        assert got==expected, rel
        current[rel]=got
    identity=hashlib.sha256(json.dumps(current,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    assert identity==r["lock_identity_sha256"]
    print("P022_FINAL_LOCK_INTEGRITY_OK")
    print("lock_identity_sha256="+identity)
    print("protected_file_count="+str(len(current)))
if __name__=="__main__":
    main()
