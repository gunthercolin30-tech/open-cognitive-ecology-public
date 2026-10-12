from pathlib import Path
from copy import deepcopy
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
RISK=ROOT/"validation_artifacts/p159/occ1k_r1/occ_residual_risk_register_v1.json"
DEBT=ROOT/"validation_artifacts/p159/occ1k_r1/occ_assurance_debt_registry_v1.json"
R9AF=ROOT/"validation_artifacts/p159/occ1k_r9af/fl_b1_b12_gate_reconciliation_v1.json"
R9AG=ROOT/"validation_artifacts/p159/occ1k_r9ag/independent_crossbinding_verification_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ah/fl_b11_residual_risk_reevaluation_v1.json"
RID="RR-FLI-EXHAUSTIVE-CERTIFICATION"; DID="AD-FLI-EXHAUSTIVE-CERTIFICATION"
def load(p):
 if not p.is_file(): raise RuntimeError("MISSING:"+str(p))
 return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def evaluate(risk=None,debt=None,ag=None):
 rr=deepcopy(risk if risk is not None else load(RISK));dd=deepcopy(debt if debt is not None else load(DEBT));gg=deepcopy(ag if ag is not None else load(R9AG))
 risks={x["risk_id"]:x for x in rr.get("items",[])};debts={x["debt_id"]:x for x in dd.get("items",[])}
 if RID not in risks or DID not in debts: raise RuntimeError("EXPECTED_RISK_OR_DEBT_MISSING")
 r=risks[RID];d=debts[DID]
 # The historical ROOT risk is specifically absence of an exhaustive certification contract.
 # R9AG proves the exhaustive evidence/cross-binding contract is now materially present for B10.
 contract_superseded=(r.get("status")=="OPEN" and r.get("severity")=="ROOT" and
   "lacks exhaustive FL-B1..B12 / FL-A01..A20 / MUT-FL certification contract" in r.get("reason","") and
   gg.get("status")=="FL_B10_PASS" and gg.get("fl_b10")=="PASS" and
   gg.get("missing_files")==[] and gg.get("hash_mismatches")==[])
 other_open_root=[x["risk_id"] for x in rr.get("items",[]) if x.get("status")=="OPEN" and x.get("severity")=="ROOT" and x.get("risk_id")!=RID]
 # Assurance debt is deliberately NOT closed here: its own required_next includes later meta-assurance.
 debt_still_open=d.get("status")=="OPEN" and d.get("blocks_lock") is True
 b11_pass=contract_superseded and not other_open_root
 return {"schema":"oce.p159.occ1k.r9ah.fl_b11.residual_risk_reevaluation.v1","milestone":"P159/OCC-1K-R9AH",
 "status":"FL_B11_PASS_WITH_ASSURANCE_DEBT_PRESERVED" if b11_pass else "FL_B11_BLOCKED",
 "historical_risk":{"risk_id":RID,"status":r.get("status"),"reason":r.get("reason"),"registry_sha256":sha(RISK),"rewritten":False},
 "superseding_risk_assessment":{"status":"RESOLVED_BY_SUPERSEDING_EVIDENCE" if contract_superseded else "UNRESOLVED",
   "evidence":"R9AG_FL_B10_PASS","r9ag_sha256":sha(R9AG)},
 "other_open_root_risks":other_open_root,
 "assurance_debt":{"debt_id":DID,"historical_status":d.get("status"),"blocks_lock":d.get("blocks_lock"),
   "required_next":d.get("required_next"),"superseding_status":"OPEN_PENDING_LATER_META_ASSURANCE" if debt_still_open else d.get("status"),
   "registry_sha256":sha(DEBT),"rewritten":False,"used_as_fl_b11_verdict":False},
 "fl_b11":"PASS" if b11_pass else "BLOCKED",
 "semantic_boundary":"FL_B11_RESIDUAL_CRITICAL_FINDINGS_IS_DISTINCT_FROM_LATER_META_ASSURANCE_DEBT",
 "lock_ready":False,"lock_granted":False,"p160b_opened":False,"authorization_created":False,"execution_performed":False,
 "next_required_step":"R9AI_FL_B12_FRESH_GLOBAL_NONREGRESSION" if b11_pass else "R9AH_RESIDUAL_RISK_REPAIR",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 x=evaluate();OUT.parent.mkdir(parents=True,exist_ok=True);b=(canon(x)+"\n").encode();OUT.write_bytes(b);return x,hashlib.sha256(b).hexdigest()
def main():
 x,h=write();print("P159_OCC1K_R9AH_FL_B11_RESIDUAL_RISK_REEVALUATION_COMPLETE");print("STATUS="+x["status"])
 print("HISTORICAL_ROOT_RISK="+x["historical_risk"]["status"]);print("SUPERSEDING_ROOT_RISK="+x["superseding_risk_assessment"]["status"])
 print("ASSURANCE_DEBT="+x["assurance_debt"]["superseding_status"]);print("ASSURANCE_DEBT_USED_AS_FL_B11_VERDICT=false")
 print("FL_B11="+x["fl_b11"]);print("LOCK_READY=false");print("LOCK_GRANTED=false");print("P160B_OPENED=false")
 print("NEXT="+x["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
