from pathlib import Path
import json, hashlib
ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p159/occ1k_r7"

def load(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def text(rel): return (ROOT/rel).read_text(encoding="utf-8")
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    cnp=load("validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json")
    static=load("validation_artifacts/p159/occ1d/static_constitutional_check_report_v1_2.json")
    r6=load("validation_artifacts/p159/occ1k_r6/canonical_dependency_resolution_v1.json")
    nir_src=text("ontology/occ_normative_ir_real_builder.py")
    crown_src=text("validation/p159_occ1e_compiled_normative_profile_crown.py")
    fs={x["finding_id"]:x for x in static["findings"]}
    rel=cnp.get("relations") or []
    has_enforcement=isinstance(cnp.get("enforcement_coverage_map"),dict) and bool(cnp.get("enforcement_coverage_map"))
    expected_consumers=all(x in crown_src for x in ("NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine"))
    semantic_relations_explicitly_deferred=('semantic_relations_compiled": False' in nir_src)
    assessments={
      "S7.CCAD":{
        "historical_result":fs["S7.CCAD"]["result"],
        "pre_runtime_contract":"INCOMPLETE",
        "reason":"SOURCE_CONFLICT_TOPOLOGY_NOT_MATERIALIZED",
        "relations_count":len(rel),
        "runtime_required_for_completion":False,
      },
      "S8.COMPOSITION":{
        "historical_result":fs["S8.COMPOSITION"]["result"],
        "pre_runtime_contract":"INCOMPLETE",
        "reason":"COMPOSITION_GRAPH_NOT_MATERIALIZED",
        "relations_count":len(rel),
        "runtime_required_for_completion":False,
      },
      "S10.ENFORCEMENT":{
        "historical_result":fs["S10.ENFORCEMENT"]["result"],
        "pre_runtime_contract":"PARTIAL",
        "reason":"CONSUMER_IDENTITIES_DECLARED_BUT_RULE_TO_CONSUMER_ENFORCEMENT_MAP_NOT_MATERIALIZED",
        "expected_consumers_declared":expected_consumers,
        "enforcement_coverage_map_present":has_enforcement,
        "actual_runtime_reachability_required_in_p159":False,
      }
    }
    facts={
      "r6_pre_runtime_resolution":r6["resolution_class"]=="PRE_RUNTIME_CONTRACT_OBLIGATION",
      "relations_empty":len(rel)==0,
      "semantic_relations_explicitly_deferred":semantic_relations_explicitly_deferred,
      "enforcement_map_absent":not has_enforcement,
      "expected_consumer_identities_declared":expected_consumers,
      "historical_unresolved_preserved":all(fs[k]["result"]=="UNRESOLVED" for k in assessments),
    }
    assert all(facts.values())
    result={
      "schema":"oce.p159.occ1k.superseding_pre_runtime_static_contract_assessment.v1",
      "milestone":"P159/OCC-1K-R7",
      "status":"PRE_RUNTIME_STATIC_CONTRACT_INCOMPLETE",
      "assessments":assessments,
      "facts":facts,
      "conclusion":{
        "s7_resolved":False,"s8_resolved":False,"s10_resolved":False,
        "fl_b3":"BLOCKED",
        "historical_occ1d_rewritten":False,
        "runtime_graph_invented":False,
        "runtime_binding_created":False,
        "p160b_opened":False,
        "lock_ready":False,"lock_granted":False,
        "next_required_step":"R8_SOURCE_BACKED_PRE_RUNTIME_CONTRACT_MATERIALIZATION"
      },
      "r8_constraints":[
        "Derive S7 conflict topology only from canonical source/NIR evidence; do not invent SAFE relations.",
        "Derive S8 composition relations only from source-backed capability/authority/effect semantics and keep bounded analysis.",
        "For S10, materialize a P159 contract map from normative rule classes to declared runtime consumer interfaces; do not claim actual P160 reachability.",
        "Preserve historical OCC-1D UNRESOLVED artifacts and create distinct replay/superseding evidence.",
        "UNKNOWN/UNRESOLVED remains blocking whenever source semantics are insufficient."
      ],
      "functional_conclusion_only":True,"phenomenology_undetermined":True
    }
    result["semantic_hash"]=hashlib.sha256(canon(result)).hexdigest()
    return result

def write():
    OUT.mkdir(parents=True,exist_ok=True)
    r=build(); p=OUT/"pre_runtime_static_contract_assessment_v1.json"
    p.write_bytes(canon(r)+b"\n")
    m={"schema":"oce.p159.occ1k.r7.manifest.v1","artifact":p.relative_to(ROOT).as_posix(),"sha256":sha(p)}
    mp=OUT/"occ1k_r7_sha256_manifest_v1.json"; mp.write_bytes(canon(m)+b"\n")
    return r,p,mp

def main():
    r,p,mp=write()
    print("P159_OCC1K_R7_PRE_RUNTIME_STATIC_CONTRACT_ASSESSMENT_COMPLETE")
    print("STATUS="+r["status"])
    for k,v in r["assessments"].items(): print(k+"="+v["pre_runtime_contract"])
    print("FL_B3=BLOCKED")
    print("RUNTIME_BINDING_CREATED=false")
    print("P160B_OPENED=false")
    print("LOCK_READY=false")
    print("LOCK_GRANTED=false")
    print("NEXT="+r["conclusion"]["next_required_step"])
    print("ARTIFACT_SHA256="+sha(p)); print("MANIFEST_SHA256="+sha(mp))
if __name__=="__main__": main()
