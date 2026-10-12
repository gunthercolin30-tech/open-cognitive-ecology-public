from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
L=ROOT/"validation/evidence/p156_ccad_specification/p156_final_lock_v1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    x=json.loads(L.read_text(encoding="utf-8"))
    assert x["status"]=="LOCKED"
    assert x["milestone"]=="P156"
    for rel,h in x["protected_hashes"].items():
        p=ROOT/rel
        assert p.is_file(),rel
        assert sha(p)==h,rel
    assert x["p157_opened"] is False
    assert x["runtime_enforcement_proven"] is False
    assert x["real_execution_enabled"] is False
    assert x["functional_conclusion_only"] is True
    assert x["phenomenology_undetermined"] is True
    print("P156_FINAL_LOCK_PROTECTED_HASHES_OK")
    print("P156_FINAL_LOCK_SCOPE_BOUNDARIES_OK")
    print("P156_FINAL_LOCK_V1_OK")
if __name__=="__main__": main()
