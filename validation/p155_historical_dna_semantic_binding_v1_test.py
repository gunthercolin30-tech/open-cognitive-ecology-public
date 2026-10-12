from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
E=ROOT/"validation"/"evidence"/"p155_constitutional_architecture_v2"
P=E/"p155_historical_dna_semantic_binding_v1.json"
D=ROOT/"ontology"/"dna_f1_f18.py"
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    x=json.loads(P.read_text(encoding="utf-8"))
    assert x["historical_ids"]==[f"F{i}" for i in range(1,19)]
    assert set(x["bindings"])==set(x["historical_ids"])
    assert x["source_sha256"]==h(D)
    for b in x["bindings"].values():
        assert b["source_sha256"]==x["source_sha256"]
        assert b["source_excerpt"]
        assert b["canonical_target_status"]=="REQUIRES_EXPLICIT_SEMANTIC_REVIEW"
        assert b["canonical_targets"]==[]
        assert b["semantic_equivalence_proven"] is False
    assert x["bindings"]["F17"]["required_meaning"]=="human_ecological_and_intergenerational_viability"
    assert x["bindings"]["F18"]["required_meaning"]=="ecological_integrity_biodiversity_and_ecosystems"
    assert x["binding_complete"] is False
    assert x["semantic_non_loss_proven"] is False
    assert x["functional_conclusion_only"] is True
    assert x["phenomenology_undetermined"] is True
    print("P155_DNA_F1_F18_SOURCE_BINDING_OK")
    print("P155_DNA_F17_F18_PRESERVATION_OK")
    print("P155_DNA_SEMANTIC_SCOPE_INFLATION_BLOCKED")
    print("P155_HISTORICAL_DNA_BINDING_STAGE1_OK")
if __name__=="__main__": main()
