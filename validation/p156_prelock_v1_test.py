from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
M=ROOT/"validation/evidence/p156_ccad_specification/p156_prelock_manifest_v1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=json.loads(M.read_text(encoding="utf-8"))
    assert m["status"]=="PRELOCK_READY"
    assert m["milestone"]=="P156"
    for rel,h in m["protected_hashes"].items():
        p=ROOT/rel
        assert p.is_file(),rel
        assert sha(p)==h,rel
    assert m["runtime_enforcement_proven"] is False
    assert m["real_execution_enabled"] is False
    assert m["functional_conclusion_only"] is True
    assert m["phenomenology_undetermined"] is True
    assert m["p157_opened"] is False
    print("P156_PRELOCK_PROTECTED_HASHES_OK")
    print("P156_PRELOCK_SCOPE_BOUNDARIES_OK")
    print("P156_PRELOCK_V1_OK")
if __name__=="__main__": main()
