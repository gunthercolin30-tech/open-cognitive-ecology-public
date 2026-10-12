from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_normative_ir_semantic_preservation_validator as v
from ontology import occ_normative_ir_real_builder as b
SOURCE=ROOT/"normative"/"occ1a"

def graph():
    r=b.build_real_nir(SOURCE); assert r["status"]=="PASS",r
    return deepcopy(r["package"]["graph"])
def mutate(cid,key,value):
    g=graph(); n=next(x for x in g["nodes"] if x["node_id"]==cid); n[key]=value; return g
def expect(g,code):
    r=v.validate_semantic_preservation(SOURCE,g); assert r["status"]=="FAIL",r
    flat=[x[0] for x in r.get("issues",())]
    if r.get("reason")=="V3_COHERENCE_REQUIRED":
        inner=r["v3_result"]; flat += [x[0] for x in inner.get("issues",())]
    assert code in flat,(code,r)

def run():
    r1=v.validate_semantic_preservation(SOURCE); r2=v.validate_semantic_preservation(SOURCE)
    assert r1["status"]==v.PASS,r1
    assert r1["report_sha256"]==r2["report_sha256"]
    assert r1["report"]["objects_compared"]==48
    assert r1["report"]["builder_used_as_source_oracle"] is False
    assert r1["report"]["scope_temporal_preservation"]=="NOT_APPLICABLE_SOURCE_ABSENT"

    g=graph(); g["nodes"]=[n for n in g["nodes"] if n["node_id"]!="DNA.H1"]
    expect(g,"SILENT_LOSS")

    g=graph(); extra=deepcopy(g["nodes"][0]); extra["node_id"]="DNA.H999"; g["nodes"].append(extra)
    # V3 may reject broken source-map/reference first; V4 exact-set comparison is
    # tested below using a semantically altered existing node to avoid false proof.
    r=v.validate_semantic_preservation(SOURCE,g); assert r["status"]=="FAIL"

    expect(mutate("DNA.H1","text","semantic extension"),"SILENT_LOSS_OR_SEMANTIC_EXTENSION")
    expect(mutate("DNA.H1","formalization_level","F2"),"FORMALIZATION_PROMOTION_OR_CHANGE")
    expect(mutate("DNA.H1","source_object_id","F999"),"PROVENANCE_BREAK")

    g=graph(); h9=next(n for n in g["nodes"] if n["node_id"]=="DNA.H9")
    h9["source_object_id"]="F12"; h9["evidence_ids"]=["F12"]
    expect(g,"SILENT_LOSS_OR_EXTENSION")

    g=graph(); n=next(n for n in g["nodes"] if n["node_id"]=="DNA.H1")
    n["lineage_artifacts"]=n["lineage_artifacts"][:-1]
    expect(g,"PROVENANCE_BREAK")

    expect(mutate("DNA.H1","partial_formalization_explicit",False),"PARTIAL_FORMALIZATION_LOST")
    expect(mutate("GENESIS.G0","human_judgment_required",False),"HUMAN_JUDGMENT_REQUIREMENT_LOST")

    # Authority/execution amplification is rejected by V3 before V4 comparison:
    # this still demonstrates fail-closed composition of V3 -> V4.
    g=mutate("DNA.H1","runtime_authority_granted",True)
    r=v.validate_semantic_preservation(SOURCE,g); assert r["status"]=="FAIL"

    assert r1["authority_activated"] is False and r1["execution_performed"] is False
    assert r1["occ1c_opened"] is False and r1["p160_opened"] is False
    print("P159_OCC1B_V4_SEMANTIC_PRESERVATION_FUNCTIONAL_OK")
    print("P159_OCC1B_V4_INDEPENDENT_SOURCE_FINGERPRINT_OK")
    print("P159_OCC1B_V4_48_OF_48_EXACT_SEMANTIC_FIELDS_OK")
    print("P159_OCC1B_V4_SILENT_LOSS_DETECTED")
    print("P159_OCC1B_V4_FORMALIZATION_PROMOTION_DETECTED")
    print("P159_OCC1B_V4_H9_F12_F17_LOSS_DETECTED")
    print("P159_OCC1B_V4_PROVENANCE_BREAK_DETECTED")
    print("P159_OCC1B_V4_PARTIAL_FORMALIZATION_LOSS_DETECTED")
    print("P159_OCC1B_V4_DETERMINISM_OK")
    print("P159_OCC1B_V4_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
