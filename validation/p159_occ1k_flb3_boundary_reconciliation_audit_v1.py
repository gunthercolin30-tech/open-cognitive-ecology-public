from pathlib import Path
import json, hashlib
ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p159/occ1k_r5"

def load(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def txt(rel): return (ROOT/rel).read_text(encoding="utf-8")
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    static=load("validation_artifacts/p159/occ1d/static_constitutional_check_report_v1_2.json")
    cov=load("validation_artifacts/p159/occ1d/s7_s8_s10_executable_coverage_v1.json")
    r4=load("validation_artifacts/p159/occ1k_r4/fl_b1_b12_independent_semantic_resolution_v1.json")
    a081=txt("ontology/occ1h_a081_rrpv21_macros_a_to_e_registry_binding_gap.py")
    auth=txt("ontology/occ1h_a081_rrp17_20_bounded_registry_assurance_authorization.py")
    findings={x["finding_id"]:x for x in static["findings"]}
    required=("S7.CCAD","S8.COMPOSITION","S10.ENFORCEMENT")
    states={k:{"severity":findings[k]["severity"],"result":findings[k]["result"],
               "disposition":findings[k]["disposition"],"evidence":findings[k].get("evidence",{})} for k in required}
    facts={
      "s7_unresolved":states["S7.CCAD"]["result"]=="UNRESOLVED",
      "s8_unresolved":states["S8.COMPOSITION"]["result"]=="UNRESOLVED",
      "s10_root_unresolved":states["S10.ENFORCEMENT"]["severity"]=="ROOT" and states["S10.ENFORCEMENT"]["result"]=="UNRESOLVED",
      "real_candidate_unresolved_preserved":cov.get("unresolved_promoted_to_pass") is False,
      "no_runtime_consumers_created":cov.get("runtime_consumers_created") is False,
      "p160_not_opened_by_occ1d":cov.get("p160_opened") is False,
      "p159_boundary_explicit":'boundary":"P160_BOUNDARY_CANDIDATE"' in a081,
      "no_p159_real_runtime_binding_remediation":'NO_P159_REMEDIATION_WITHOUT_CREATING_NEW_RUNTIME_BINDING' in a081,
      "technical_remediation_not_authorized_within_p159":'TECHNICAL_REMEDIATION_NOT_AUTHORIZED_WITHIN_P159' in a081,
      "bounded_fixture_not_real_runtime":'"real_runtime_consumer_graph_materialized":False' in auth,
      "r4_fl_b3_blocked":next(g for g in r4["gates"] if g["gate_id"]=="FL-B3")["verdict"]=="BLOCKED",
    }
    ok=all(facts.values())
    result={
      "schema":"oce.p159.occ1k.flb3.boundary_reconciliation_audit.v1",
      "milestone":"P159/OCC-1K-R5",
      "status":"CANONICAL_BOUNDARY_RECONCILIATION_REQUIRED" if ok else "EVIDENCE_INCOMPLETE",
      "facts":facts,"static_findings":states,
      "conclusion":{
        "fl_b3":"BLOCKED",
        "p159_new_runtime_binding_authorized":False,
        "p160b_opened":False,
        "lock_ready":False,"lock_granted":False,
        "historical_lock_modified":False,
        "runtime_binding_created":False,
        "required_governed_resolution":"RECONCILE_P159_FINAL_LOCK_RUNTIME_DEPENDENCY_WITH_P160_BOUNDARY_BEFORE_ANY_PROMOTION"
      },
      "non_claims":["NO_STATIC_PASS_MANUFACTURED","NO_RUNTIME_GRAPH_INVENTED","NO_P159_LOCK_REISSUED","NO_P160_AUTHORIZATION_CREATED"],
      "functional_conclusion_only":True,"phenomenology_undetermined":True
    }
    result["semantic_hash"]=hashlib.sha256(canon(result)).hexdigest()
    return result

def write():
    OUT.mkdir(parents=True,exist_ok=True)
    r=build(); p=OUT/"fl_b3_boundary_reconciliation_audit_v1.json"
    p.write_bytes(canon(r)+b"\n")
    m={"schema":"oce.p159.occ1k.r5.manifest.v1","artifact":p.relative_to(ROOT).as_posix(),"sha256":sha(p)}
    mp=OUT/"occ1k_r5_sha256_manifest_v1.json"; mp.write_bytes(canon(m)+b"\n")
    return r,p,mp

def main():
    r,p,mp=write()
    print("P159_OCC1K_R5_BOUNDARY_RECONCILIATION_AUDIT_COMPLETE")
    print("STATUS="+r["status"])
    print("FL_B3=BLOCKED")
    print("RUNTIME_BINDING_CREATED=false")
    print("P160B_OPENED=false")
    print("LOCK_READY=false")
    print("LOCK_GRANTED=false")
    print("ARTIFACT_SHA256="+sha(p))
    print("MANIFEST_SHA256="+sha(mp))
if __name__=="__main__": main()
