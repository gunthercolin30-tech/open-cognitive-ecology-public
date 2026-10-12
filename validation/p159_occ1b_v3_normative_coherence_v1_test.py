from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_normative_ir_coherence_validator as v
from ontology import occ_normative_ir_real_builder as b

SOURCE=ROOT/"normative"/"occ1a"

def base_graph():
    r=b.build_real_nir(SOURCE); assert r["status"]=="PASS",r
    return deepcopy(r["package"]["graph"])

def fail(g,expected=None):
    r=v.validate_coherence(SOURCE,g); assert r["status"]=="FAIL",r
    if expected: assert any(x[0]==expected for x in r.get("issues",())),r

def run():
    r1=v.validate_coherence(SOURCE); r2=v.validate_coherence(SOURCE)
    assert r1["status"]==v.PASS,r1
    assert r1["report_sha256"]==r2["report_sha256"]
    assert r1["report"]["object_count"]==48
    assert r1["report"]["conflicts_arbitrated"] is False

    g=base_graph(); g["metadata"]["authority_granted"]=True
    fail(g,"AUTHORITY_OR_EXECUTION_AMPLIFICATION")

    g=base_graph(); g["metadata"]["execution_enabled"]=True
    fail(g,"AUTHORITY_OR_EXECUTION_AMPLIFICATION")

    g=base_graph(); g["nodes"][0]["weight"]=0.9
    fail(g,"HARD_CONSTRAINT_WEIGHTING_FORBIDDEN")

    g=base_graph(); g["nodes"][0]["authority_from_evidence"]=True; g["nodes"][0]["evidence_ids"]=["F1"]
    fail(g,"EVIDENCE_IS_NOT_AUTHORITY")

    g=base_graph()
    g["edges"]=[{"source":"DNA.H1","target":"DNA.H2","type":"CANNOT_OVERRIDE","numeric_priority":1}]
    fail(g,"DNA_H_GLOBAL_NUMERIC_HIERARCHY_FORBIDDEN")

    g=base_graph()
    g["edges"]=[{"source":"DNA.H1","target":"DNA.H2","type":"CONFLICTS_WITH","winner":"DNA.H1"}]
    fail(g,"NIR_ARBITRATION_FORBIDDEN")

    g=base_graph()
    g["edges"]=[{"source":"DNA.H1","target":"DNA.H2","type":"CONFLICTS_WITH"}]
    ok=v.validate_coherence(SOURCE,g); assert ok["status"]==v.PASS,ok
    assert ok["report"]["conflicts_arbitrated"] is False

    g=base_graph()
    g["edges"]=[{"source":"CCAD.P0","target":"DNA.L0.1","type":"OVERRIDES"}]
    fail(g,"UNSUPPORTED_OVERRIDE_RELATION")

    assert r1["authority_activated"] is False and r1["execution_performed"] is False
    assert r1["occ1c_opened"] is False and r1["p160_opened"] is False
    assert r1["v4_semantic_preservation_claimed"] is False

    print("P159_OCC1B_V3_COHERENCE_FUNCTIONAL_OK")
    print("P159_OCC1B_V3_NON_AMPLIFICATION_OK")
    print("P159_OCC1B_V3_EVIDENCE_AUTHORITY_SEPARATION_OK")
    print("P159_OCC1B_V3_DNA_H_NO_GLOBAL_NUMERIC_HIERARCHY_OK")
    print("P159_OCC1B_V3_CONFLICT_NON_ARBITRATION_OK")
    print("P159_OCC1B_V3_CCAd_NO_DNA_OVERRIDE_OK")
    print("P159_OCC1B_V3_DETERMINISM_OK")
    print("P159_OCC1B_V3_STAGE_BOUNDARY_OK")

if __name__=="__main__": run()
