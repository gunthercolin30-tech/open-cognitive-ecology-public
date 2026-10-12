from pathlib import Path
from copy import deepcopy
import json, hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R4=ROOT/"validation_artifacts/p159/occ1k_r4/fl_b1_b12_independent_semantic_resolution_v1.json"
R9H=ROOT/"validation_artifacts/p159/occ1k_r9h/post_adoption_independent_replay_v1.json"
R9AD=ROOT/"validation_artifacts/p159/occ1k_r9ad/independent_s10_replay_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ae/fl_b3_independent_reevaluation_v1.json"
def load(p):
    if not p.is_file(): raise RuntimeError("MISSING:"+str(p))
    return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def evaluate(r4=None,r9h=None,r9ad=None):
    a=deepcopy(r4 if r4 is not None else load(R4))
    h=deepcopy(r9h if r9h is not None else load(R9H))
    d=deepcopy(r9ad if r9ad is not None else load(R9AD))
    gates={x["gate_id"]:x for x in a.get("gates",[])}
    if "FL-B3" not in gates: raise RuntimeError("R4_FL_B3_MISSING")
    if gates["FL-B3"].get("verdict")!="BLOCKED": raise RuntimeError("HISTORICAL_FL_B3_NOT_BLOCKED")
    checks={
      "S7": h.get("status")=="POST_ADOPTION_REPLAY_COMPLETE" and h.get("s7",{}).get("status")=="PASS",
      "S8": h.get("status")=="POST_ADOPTION_REPLAY_COMPLETE" and h.get("s8",{}).get("status")=="PASS",
      "S10": d.get("status")=="S10_PRE_RUNTIME_STATIC_CONTRACT_PASS" and d.get("s10_pass") is True and d.get("s10_finding",{}).get("result")=="PASS",
      "S10_SCOPE": d.get("semantic_scope",{}).get("s10_pass_scope")=="P159_PRE_RUNTIME_DECLARED_CONSUMER_INTERFACE_CONTRACT_ONLY",
      "NO_RUNTIME_CLAIM": d.get("semantic_scope",{}).get("runtime_reachability_proven") is False and d.get("semantic_scope",{}).get("runtime_enforcement_proven") is False and d.get("semantic_scope",{}).get("p160_runtime_graph_claimed") is False,
      "NO_AUTH_EXEC": h.get("authorization_created") is False and h.get("execution_performed") is False and d.get("semantic_scope",{}).get("authorization_created") is False and d.get("semantic_scope",{}).get("execution_performed") is False,
      "P160B_CLOSED": h.get("p160b_opened") is False and d.get("p160b_opened") is False,
    }
    passed=all(checks.values())
    return {
      "schema":"oce.p159.occ1k.r9ae.flb3.independent.reevaluation.v1",
      "milestone":"P159/OCC-1K-R9AE",
      "status":"FL_B3_SUPERSEDING_EVIDENCE_PASS" if passed else "FL_B3_REEVALUATION_BLOCKED",
      "historical_r4":{"sha256":sha(R4),"fl_b3_verdict":"BLOCKED","rewritten":False},
      "superseding_evidence":{
        "r9h":{"sha256":sha(R9H),"s7":h.get("s7"),"s8":h.get("s8")},
        "r9ad":{"sha256":sha(R9AD),"s10":d.get("s10_finding"),"semantic_scope":d.get("semantic_scope")}
      },
      "checks":checks,
      "fl_b3":"PASS" if passed else "BLOCKED",
      "fl_b3_scope":"P159_STATIC_CONSTITUTIONAL_CHECKS_WITH_SUPERSEDING_S7_S8_S10_EVIDENCE",
      "raw_r9ad_global_checker_decision":d.get("raw_checker_decision"),
      "raw_r9ad_global_checker_decision_used_as_fl_b3_verdict":False,
      "historical_findings_rewritten":False,
      "runtime_reachability_proven":False,"runtime_enforcement_proven":False,
      "authorization_created":False,"execution_performed":False,
      "lock_ready":False,"lock_granted":False,"p160b_opened":False,
      "next_required_step":"R9AF_FL_B1_B12_GATE_RECONCILIATION" if passed else "R9AE_EVIDENCE_GAP_RESOLUTION",
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
    r=evaluate(); OUT.parent.mkdir(parents=True,exist_ok=True)
    b=(canon(r)+"\n").encode(); OUT.write_bytes(b)
    return r,hashlib.sha256(b).hexdigest()
def main():
    r,h=write()
    print("P159_OCC1K_R9AE_FLB3_INDEPENDENT_REEVALUATION_COMPLETE")
    print("STATUS="+r["status"]);print("S7="+str(r["checks"]["S7"]).upper());print("S8="+str(r["checks"]["S8"]).upper());print("S10="+str(r["checks"]["S10"]).upper())
    print("FL_B3="+r["fl_b3"]);print("HISTORICAL_R4_REWRITTEN=false")
    print("RAW_R9AD_GLOBAL_DECISION_USED_AS_FL_B3_VERDICT=false")
    print("RUNTIME_REACHABILITY_PROVEN=false");print("RUNTIME_ENFORCEMENT_PROVEN=false")
    print("LOCK_READY=false");print("LOCK_GRANTED=false");print("P160B_OPENED=false")
    print("NEXT="+r["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
