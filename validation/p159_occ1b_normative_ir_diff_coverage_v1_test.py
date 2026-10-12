from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_normative_ir_diff_coverage as d
from ontology import occ_normative_ir_real_builder as b
from ontology import occ_normative_ir_semantic_preservation_validator as v4
SOURCE=ROOT/"normative"/"occ1a"

def base():
    r=b.build_real_nir(SOURCE); assert r["status"]=="PASS",r
    return deepcopy(r["package"]["graph"])

def run():
    g=base()
    sf=v4.independent_source_fingerprint(SOURCE); assert sf["status"]=="PASS",sf

    zero=d.normative_ir_diff(g,deepcopy(g)); assert zero["change_count"]==0
    assert zero["diff_sha256"]==d.normative_ir_diff(g,deepcopy(g))["diff_sha256"]

    g2=deepcopy(g); n=next(x for x in g2["nodes"] if x["node_id"]=="DNA.H1"); n["formalization_level"]="F2"
    x=d.normative_ir_diff(g,g2)
    assert any(c["kind"]=="FORMALIZATION_PROMOTION" for c in x["changes"])

    xrev=d.normative_ir_diff(g2,g)
    assert any(c["kind"]=="FORMALIZATION_DEMOTION" for c in xrev["changes"])
    assert x["diff_sha256"]!=xrev["diff_sha256"]

    g3=deepcopy(g); g3["nodes"]=g3["nodes"][1:]
    assert any(c["kind"]=="NODE_REMOVED" for c in d.normative_ir_diff(g,g3)["changes"])

    g4=deepcopy(g); g4["metadata"]["ignored_nonsemantic"]="x"
    assert d.normative_ir_diff(g,g4)["change_count"]==0

    cov=d.semantic_coverage_report(sf["fingerprint"],g)
    assert cov["object_count"]==48
    assert cov["dimensions"]["principal_object_presence"]["represented"]==48
    assert cov["presence_is_not_full_semantic_coverage"] is True
    assert cov["full_semantic_coverage_claimed"] is False
    assert cov["dimensions"]["scope"]["status"]=="NOT_APPLICABLE"
    assert cov["dimensions"]["temporal"]["status"]=="NOT_APPLICABLE"
    assert sum(cov["coverage_counts"].values())==48
    assert cov["coverage_counts"]["HUMAN_JUDGMENT_REQUIRED"]>=1
    assert cov["coverage_sha256"]==d.semantic_coverage_report(sf["fingerprint"],g)["coverage_sha256"]

    print("P159_OCC1B_NIR_DIFF_FUNCTIONAL_OK")
    print("P159_OCC1B_NIR_DIFF_DIRECTIONALITY_OK")
    print("P159_OCC1B_NIR_DIFF_NODE_LOSS_OK")
    print("P159_OCC1B_NIR_DIFF_DETERMINISM_OK")
    print("P159_OCC1B_SEMANTIC_COVERAGE_FUNCTIONAL_OK")
    print("P159_OCC1B_SEMANTIC_COVERAGE_48_OBJECTS_OK")
    print("P159_OCC1B_PRESENCE_NOT_FULL_COVERAGE_OK")
    print("P159_OCC1B_SCOPE_TEMPORAL_NOT_APPLICABLE_OK")
    print("P159_OCC1B_DIFF_COVERAGE_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
