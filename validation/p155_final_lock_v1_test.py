from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"validation"/"evidence"/"p155_constitutional_architecture_v2"
LOCK=E/"p155_final_lock_v1.json"
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    x=json.loads(LOCK.read_text(encoding="utf-8"))
    assert x["status"]=="LOCKED"
    assert x["milestone"]=="P155"
    assert x["final_lock_identity_sha256"]
    for rel,expected in x["locked_artifact_hashes"].items():
        assert h(ROOT/rel)==expected, "locked artifact drift: "+rel
    for rel,expected in x["protected_prior_hashes"].items():
        assert h(ROOT/rel)==expected, "prior protected drift: "+rel
    assert x["semantic_non_loss_f1_f18_proven"] is True
    assert x["runtime_enforcement_proven"] is False
    assert x["real_execution_enabled"] is False
    assert x["functional_conclusion_only"] is True
    assert x["phenomenology_undetermined"] is True
    print("P155_FINAL_LOCK_ARTIFACT_INTEGRITY_OK")
    print("P155_FINAL_LOCK_PRIOR_PROTECTION_OK")
    print("P155_FINAL_LOCK_SEMANTIC_NON_LOSS_OK")
    print("P155_FINAL_LOCK_SCOPE_BOUNDARY_OK")
    print("P155_FINAL_LOCK_OK")
if __name__=="__main__": main()
