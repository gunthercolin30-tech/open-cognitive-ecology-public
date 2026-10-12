from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
E=ROOT/"validation"/"evidence"/"p155_constitutional_architecture_v2"
FILES=[
 "p155_constitutional_architecture_v2.json",
 "p155_historical_dna_traceability_v1.json",
 "p155_nla_non_circularity_v1.json",
 "p155_historical_dna_semantic_binding_v2.json",
]
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for name in FILES:
        json.loads((E/name).read_text(encoding="utf-8"))
    a=json.loads((E/FILES[0]).read_text())
    b=json.loads((E/FILES[3]).read_text())
    assert b["binding_complete"] is True
    assert b["semantic_non_loss_proven"] is True
    assert b["runtime_enforcement_proven"] is False
    assert a["invariants"]["runtime_enforcement_proven"] is False
    for rel,expected in a["protected_hashes"].items():
        assert h(ROOT/rel)==expected, "protected artifact drift: "+rel
    print("P155_CONSOLIDATED_JSON_STRICT_OK")
    print("P155_SEMANTIC_NON_LOSS_CONSOLIDATED_OK")
    print("P155_PROTECTED_HASHES_STABLE_OK")
    print("P155_RUNTIME_SCOPE_BOUNDARY_OK")
    print("P155_CONSOLIDATION_TEST_OK")
if __name__=="__main__": main()
