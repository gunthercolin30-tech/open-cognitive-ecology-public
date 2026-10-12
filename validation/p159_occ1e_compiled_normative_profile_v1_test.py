from copy import deepcopy
import json
from pathlib import Path
from ontology import occ_compiled_normative_profile as cnp
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json"
SCHEMA=ROOT/"schemas/p159_occ1e_compiled_normative_profile_v1.schema.json"
COMPILER=ROOT/"ontology/occ_constitutional_compiler.py"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def build():
 candidates=[ROOT/"validation_artifacts/p159/occ1d/static_constitutional_check_report_v1_2.json",ROOT/"validation_artifacts/p159/occ1d/static_constitutional_check_report_v1.json"]
 static=next((p for p in candidates if p.exists()),None); assert static is not None
 return cnp.build_profile(load(BASE),cnp.file_sha256(BASE),cnp.file_sha256(COMPILER),cnp.file_sha256(SCHEMA),cnp.file_sha256(static))
def rehash(p): p.pop("artifact_hash",None); p["artifact_hash"]=cnp.canonical_sha256(p)
def test_functional_contract():
 p=build(); r=cnp.verify_profile(p); assert r["status"]=="PASS",r; assert r["rule_count"]==48; assert p["profile_state"]=="COMPILED"; assert p["enforcement_map"]["status"]=="UNRESOLVED"; assert p["enforcement_map"]["runtime_consumer_graph_proven"] is False; assert cnp.manifest(p)["artifact_hash"]==p["artifact_hash"]; assert "ALLOW_CANDIDATE is not permission to execute" in cnp.human_explanation(p)
def test_determinism(): assert build()==build()
def test_degradation_rule_authorization():
 p=build(); p["rules"][0]["normative_effect"]["allow_candidate_is_authorization"]=True; rehash(p); assert cnp.verify_profile(p)["status"]=="FAIL"
def test_degradation_source_map():
 p=build(); p["rules"][0]["provenance"].pop("source_map",None); rehash(p); assert cnp.verify_profile(p)["status"]=="FAIL"
def test_degradation_snapshot():
 p=build(); p["constitutional_snapshot"]["source_package_hash"]="0"*64; rehash(p); assert cnp.verify_profile(p)["status"]=="FAIL"
def test_degradation_execution():
 p=build(); p["runtime_interfaces"]["execution_capability"]=True; rehash(p); assert cnp.verify_profile(p)["status"]=="FAIL"
def test_lifecycle_fail_closed():
 p=build(); assert cnp.transition(p,"VERIFIED",False)["status"]=="FAIL"; assert cnp.transition(p,"ACTIVE",True)["status"]=="FAIL"
 for state in ("NON_ACTIVATABLE","REVOKED"):
  q=deepcopy(p); q["profile_state"]=state; rehash(q); assert cnp.transition(q,"ACTIVE",True)["status"]=="FAIL"
