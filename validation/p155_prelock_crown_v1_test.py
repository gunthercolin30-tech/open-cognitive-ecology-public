from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"validation"/"evidence"/"p155_constitutional_architecture_v2"
M=E/"p155_prelock_manifest_v1.json"
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=json.loads(M.read_text(encoding="utf-8"))
    assert m["status"]=="PRELOCK_READY_NOT_LOCKED"
    assert m["deterministic_core_identity_sha256"]
    for rel,expected in m["artifact_hashes"].items():
        assert h(ROOT/rel)==expected, "artifact drift: "+rel
    for rel,expected in m["protected_hashes"].items():
        assert h(ROOT/rel)==expected, "protected drift: "+rel
    assert m["runtime_enforcement_proven"] is False
    assert m["real_execution_enabled"] is False
    assert m["functional_conclusion_only"] is True
    assert m["phenomenology_undetermined"] is True
    print("P155_PRELOCK_MANIFEST_INTEGRITY_OK")
    print("P155_PRELOCK_PROTECTED_NON_MUTATION_OK")
    print("P155_PRELOCK_SCOPE_BOUNDARY_OK")
    print("P155_PRELOCK_CROWN_V1_OK")
if __name__=="__main__": main()
