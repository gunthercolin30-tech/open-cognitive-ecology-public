from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"validation/evidence/p156_ccad_specification"
R=E/"p156_postlock_verification_v1.json"
L=E/"p156_final_lock_v1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    r=json.loads(R.read_text(encoding="utf-8"))
    l=json.loads(L.read_text(encoding="utf-8"))
    assert l["status"]=="LOCKED"
    assert sha(L)==r["final_lock_file_sha256"]
    assert l["final_lock_identity_sha256"]==r["final_lock_identity_sha256"]
    for rel,h in l["protected_hashes"].items():
        assert sha(ROOT/rel)==h,rel
    assert r["protected_artifact_drift"] is False
    assert r["p155_lock_preserved"] is True
    assert r["p157_opened"] is False
    assert r["runtime_enforcement_proven"] is False
    assert r["real_execution_enabled"] is False
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    print("P156_POSTLOCK_FINAL_LOCK_BINDING_OK")
    print("P156_POSTLOCK_PROTECTED_ARTIFACTS_OK")
    print("P156_POSTLOCK_BOUNDARIES_OK")
    print("P156_POSTLOCK_VERIFICATION_V1_OK")
if __name__=="__main__": main()
