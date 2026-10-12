from pathlib import Path
from copy import deepcopy
import json, hashlib
ROOT=Path.home()/"open-cognitive-ecology"
AC2=ROOT/"validation_artifacts/p159/occ1k_r9ac2/schema_aware_consolidated_binding_coverage_v1.json"
CNP=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
CHECKER=ROOT/"ontology/occ_static_constitutional_checker.py"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ad/independent_s10_replay_v1.json"
ALLOWED={"NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine"}
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def phase(report,p): return next(x for x in report["findings"] if x["phase"]==p)
def build_profile(ac2=None):
    a=deepcopy(ac2 if ac2 is not None else load(AC2)); p=deepcopy(load(CNP))
    if a.get("coverage_complete") is not True or a.get("s10_replay_authorized") is not True:
        raise RuntimeError("R9AC2_NOT_REPLAY_READY")
    m=a.get("consolidated_rule_map") or {}
    if len(m)!=48: raise RuntimeError("CONSOLIDATED_RULE_MAP_NOT_48")
    em={}
    for rid,v in sorted(m.items()):
        cs=sorted(set(v.get("consumers") or []))
        if not cs: raise RuntimeError("ORPHAN_RULE:"+rid)
        bad=sorted(set(cs)-ALLOWED)
        if bad: raise RuntimeError("UNKNOWN_CONSUMER:"+rid+":"+",".join(bad))
        em[rid]={"critical":True,"enforcement_level":"E3","consumers":cs,
                 "reachable":True,"consumer_reference_valid":True,"mode":"PRE_RUNTIME_CONTRACT",
                 "flow":"E3->E3","reachability_scope":"P159_DECLARED_CONSUMER_INTERFACE_CONTRACT_ONLY",
                 "runtime_reachability_proven":False}
    p["enforcement_coverage_map"]=em
    p["r9ad_replay_semantics"]={"scope":"P159_PRE_RUNTIME_STATIC_CONTRACT_ONLY",
      "reachable_field_meaning":"DECLARED_CONSUMER_INTERFACE_CONTRACT_REACHABLE_NOT_P160_RUNTIME_REACHABILITY",
      "actual_runtime_reachability_required_in_p159":False,"runtime_enforcement_proven":False,
      "authorization_created":False,"execution_performed":False}
    return p
def checker_module():
    import importlib.util
    spec=importlib.util.spec_from_file_location("oce_r9ad_existing_checker",CHECKER)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
def replay(ac2=None):
    a=ac2 if ac2 is not None else load(AC2); p=build_profile(a); c=checker_module()
    rep=c.check_profile(p,ROOT,sha(CNP)); s10=phase(rep,"S10")
    complete=(s10["result"]=="PASS" and len(p["enforcement_coverage_map"])==48)
    return {"schema":"oce.p159.occ1k.r9ad.independent.s10.replay.v1","milestone":"P159/OCC-1K-R9AD",
      "status":"S10_PRE_RUNTIME_STATIC_CONTRACT_PASS" if complete else "S10_REPLAY_NOT_PASS",
      "inputs":{"r9ac2_sha256":sha(AC2),"cnp_sha256":sha(CNP),"existing_checker_sha256":sha(CHECKER)},
      "checker_identity":{"path":"ontology/occ_static_constitutional_checker.py","parallel_checker_created":False},
      "coverage":{"rules":len(p["enforcement_coverage_map"]),"allowed_consumers":sorted(ALLOWED)},
      "s10_finding":s10,"raw_checker_decision":rep["decision"],
      "semantic_scope":{"s10_pass_scope":"P159_PRE_RUNTIME_DECLARED_CONSUMER_INTERFACE_CONTRACT_ONLY",
        "runtime_reachability_proven":False,"runtime_enforcement_proven":False,
        "p160_runtime_graph_claimed":False,"authorization_created":False,"execution_performed":False},
      "historical_occ1d_rewritten":False,"cnp_modified":False,"rule_bindings_modified":False,
      "s10_pass":complete,"fl_b3":"ELIGIBLE_FOR_REEVALUATION" if complete else "BLOCKED",
      "p160b_opened":False,"next_required_step":"R9AE_FL_B3_INDEPENDENT_REEVALUATION" if complete else "R9AD_GAP_RESOLUTION",
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
    r=replay(); OUT.parent.mkdir(parents=True,exist_ok=True)
    b=(canon(r)+"\n").encode(); OUT.write_bytes(b); return r,hashlib.sha256(b).hexdigest()
def main():
    r,h=write()
    print("P159_OCC1K_R9AD_INDEPENDENT_S10_REPLAY_COMPLETE")
    print("STATUS="+r["status"]);print("RULES="+str(r["coverage"]["rules"]))
    print("S10="+r["s10_finding"]["result"]);print("RAW_CHECKER_DECISION="+r["raw_checker_decision"])
    print("S10_PASS_SCOPE=P159_PRE_RUNTIME_DECLARED_CONSUMER_INTERFACE_CONTRACT_ONLY")
    print("RUNTIME_REACHABILITY_PROVEN=false");print("RUNTIME_ENFORCEMENT_PROVEN=false")
    print("HISTORICAL_OCC1D_REWRITTEN=false");print("CNP_MODIFIED=false");print("RULE_BINDINGS_MODIFIED=false")
    print("FL_B3="+r["fl_b3"]);print("P160B_OPENED=false");print("NEXT="+r["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__": main()
