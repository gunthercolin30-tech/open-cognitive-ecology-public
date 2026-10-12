from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
E=ROOT/"validation"/"evidence"/"p155_constitutional_architecture_v2"
P=E/"p155_historical_dna_semantic_binding_v2.json"
D=ROOT/"ontology"/"dna_f1_f18.py"
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    x=json.loads(P.read_text(encoding="utf-8"))
    assert x["historical_ids"]==[f"F{i}" for i in range(1,19)]
    assert x["source_sha256"]==h(D)
    assert x["binding_complete"] is True
    assert x["semantic_non_loss_proven"] is True
    assert x["review_basis"]=="EXACT_CANONICAL_DEFINITIONS_PLUS_EXPLICIT_P155_TARGET_MAPPING"
    allowed=set(x["allowed_targets"])
    for fid,b in x["bindings"].items():
        assert b["definition"]
        assert b["canonical_targets"]
        assert set(b["canonical_targets"])<=allowed
        assert b["semantic_coverage_reviewed"] is True
        assert b["source_sha256"]==x["source_sha256"]
    assert "DERIVED_DOCTRINES" in x["bindings"]["F17"]["canonical_targets"]
    assert x["bindings"]["F17"]["distinct_normative_object_preserved"] is True
    assert x["bindings"]["F18"]["canonical_targets"]==["DERIVED_DOCTRINES"]
    assert x["bindings"]["F18"]["distinct_normative_object_preserved"] is True
    assert x["bindings"]["F18"]["not_reduced_to_human_welfare"] is True
    assert x["functional_conclusion_only"] is True
    assert x["phenomenology_undetermined"] is True
    print("P155_DNA_F1_F18_EXACT_DEFINITIONS_OK")
    print("P155_DNA_TARGET_MAPPING_COMPLETE_OK")
    print("P155_DNA_F17_DISTINCTNESS_OK")
    print("P155_DNA_F18_DISTINCT_ECOLOGICAL_OBJECT_OK")
    print("P155_DNA_SEMANTIC_NON_LOSS_V2_OK")
if __name__=="__main__": main()
