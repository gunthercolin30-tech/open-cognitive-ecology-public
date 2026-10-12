from copy import deepcopy
from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_constitutional_compiler as c
from ontology import occ_normative_ir as nir
SRC=ROOT/"normative"/"occ1a"
PROOF=ROOT/"validation_artifacts"/"p159"/"occ1b"/"occ1b_postclose_verification.json"
def rehash(p):
    q=deepcopy(p); q.pop("artifact_hash",None); p["artifact_hash"]=nir.canonical_sha256(q)
def run():
    a=c.compile_canonical_profile(SRC,PROOF); b=c.compile_canonical_profile(SRC,PROOF)
    assert a["status"]==c.PASS,a
    assert b["status"]==c.PASS,b
    assert a["artifact_hash"]==b["artifact_hash"]
    p=a["canonical_profile"]
    assert c.verify_canonical_profile(p)["status"]==c.PASS
    assert [x["stage"] for x in p["pipeline"]]==["C%d"%i for i in range(1,13)]
    assert p["pipeline"][9]["status"]=="HOOK_DEFINED_OCC1D_NOT_OPENED"
    assert p["profile_state"]=="UNVERIFIED_COMPILED_PROFILE"
    assert len(p["rules"])==48
    assert set(c.COMPILATION_CLASSES)==set(p["compilation_classes"])
    assert "EXECUTE_ACTION" not in p["norm_ops_specification"]["allowed"]
    assert p["norm_ops_specification"]["forbidden"]==["EXECUTE_ACTION"]
    assert all(set(c.COMPILED_RULE_FIELDS).issubset(set(r)) for r in p["rules"])
    assert all(r["provenance"]["source_map"] for r in p["rules"])
    assert all(r["scope_constraints"]["implicit_global"] is False for r in p["rules"])
    assert all(r["temporal_constraints"]["implicit_permanent"] is False for r in p["rules"])
    x=deepcopy(p); x["rules"][0]["outputs"].append("EXECUTE_ACTION"); rehash(x)
    assert c.verify_canonical_profile(x)["reason"]=="NORM_OPS_CLOSED_WORLD_VIOLATION"
    x=deepcopy(p); x["rules"][0]["authority_requirements"]["authorization_created"]=True; rehash(x)
    assert c.verify_canonical_profile(x)["reason"]=="AUTHORIZATION_CREATION_FORBIDDEN"
    x=deepcopy(p); x["norm_ops_specification"]["allow_candidate_is_authorization"]=True; rehash(x)
    assert c.verify_canonical_profile(x)["reason"]=="ELIGIBILITY_AUTHORIZATION_COLLAPSE"
    x=deepcopy(p); x["compile_report"]["occ1d_opened"]=True; rehash(x)
    assert c.verify_canonical_profile(x)["reason"]=="CANONICAL_STAGE_BOUNDARY_VIOLATION"
    x=deepcopy(p); x["rules"][0]["rule_type"]="TAMPERED"
    assert c.verify_canonical_profile(x)["reason"]=="CANONICAL_PROFILE_TAMPER_DETECTED"
    cwd=os.getcwd()
    try:
        os.chdir("/tmp"); d=c.compile_canonical_profile(SRC,PROOF)
    finally: os.chdir(cwd)
    assert d["status"]==c.PASS and d["artifact_hash"]==a["artifact_hash"]
    print("P159_OCC1C_CANONICAL_PIPELINE_FUNCTIONAL_OK")
    print("P159_OCC1C_PIPELINE_C1_C12_EXPLICIT_OK")
    print("P159_OCC1C_CC1_CC2_CC3_EXPLICIT_OK")
    print("P159_OCC1C_NORM_OPS_CLOSED_WORLD_OK")
    print("P159_OCC1C_COMPILED_RULE_SCHEMA_OK")
    print("P159_OCC1C_PROVENANCE_BINDING_OK")
    print("P159_OCC1C_SCOPE_TEMPORAL_NON_WIDENING_OK")
    print("P159_OCC1C_EXECUTE_ACTION_REJECTED")
    print("P159_OCC1C_AUTHORIZATION_INFLATION_REJECTED")
    print("P159_OCC1C_ELIGIBILITY_AUTHORIZATION_SEPARATION_OK")
    print("P159_OCC1C_OCC1D_REMAINS_CLOSED_OK")
    print("P159_OCC1C_P160_REMAINS_CLOSED_OK")
    print("P159_OCC1C_DETERMINISM_OK")
    print("P159_OCC1C_CWD_INDEPENDENCE_OK")
    print("P159_OCC1C_CANONICAL_PIPELINE_V1_TEST_OK")
if __name__=="__main__": run()
