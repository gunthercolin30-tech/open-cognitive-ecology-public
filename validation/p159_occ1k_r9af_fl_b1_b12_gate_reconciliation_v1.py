from pathlib import Path
from copy import deepcopy
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R4=ROOT/"validation_artifacts/p159/occ1k_r4/fl_b1_b12_independent_semantic_resolution_v1.json"
R9AE=ROOT/"validation_artifacts/p159/occ1k_r9ae/fl_b3_independent_reevaluation_v1.json"
RISK=ROOT/"validation_artifacts/p159/occ1k_r1/occ_residual_risk_register_v1.json"
DEBT=ROOT/"validation_artifacts/p159/occ1k_r1/occ_assurance_debt_registry_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9af/fl_b1_b12_gate_reconciliation_v1.json"
def load(p):
 if not p.is_file(): raise RuntimeError("MISSING:"+str(p))
 return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def reconcile(r4=None,ae=None,risk=None,debt=None):
 a=deepcopy(r4 if r4 is not None else load(R4)); e=deepcopy(ae if ae is not None else load(R9AE))
 rr=deepcopy(risk if risk is not None else load(RISK)); dd=deepcopy(debt if debt is not None else load(DEBT))
 old={g["gate_id"]:g for g in a["gates"]}
 if set(old)!={f"FL-B{i}" for i in range(1,13)}: raise RuntimeError("R4_GATE_SET_NOT_12")
 if e.get("fl_b3")!="PASS" or e.get("status")!="FL_B3_SUPERSEDING_EVIDENCE_PASS": raise RuntimeError("R9AE_NOT_PASS")
 gates={}
 for gid,g in sorted(old.items()):
  gates[gid]={"historical_verdict":g["verdict"],"current_verdict":g["verdict"],"basis":"R4_PRESERVED"}
 gates["FL-B3"].update(current_verdict="PASS",basis="R9AE_SUPERSEDING_EVIDENCE",evidence_sha256=sha(R9AE))
 # B10 remains inconclusive until exhaustive final-lock evidence bundle + independent cross-binding exists.
 gates["FL-B10"].update(current_verdict="INCONCLUSIVE",basis="EXHAUSTIVE_FINAL_LOCK_BUNDLE_NOT_YET_MATERIALIZED")
 open_root=[x for x in rr.get("items",[]) if x.get("status")=="OPEN" and x.get("severity")=="ROOT"]
 open_blocking=[x for x in dd.get("items",[]) if x.get("status")=="OPEN" and x.get("blocks_lock") is True]
 gates["FL-B11"].update(current_verdict="BLOCKED" if (open_root or open_blocking) else "PASS",
   basis="OPEN_ROOT_RISK_OR_LOCK_BLOCKING_ASSURANCE_DEBT" if (open_root or open_blocking) else "NO_OPEN_ROOT_RISK_OR_BLOCKING_DEBT")
 # B12 remains inconclusive: historical global receipt predates exhaustive revision.
 gates["FL-B12"].update(current_verdict="INCONCLUSIVE",basis="FRESH_POST_R9AF_NONREGRESSION_GLOBAL_RECEIPT_REQUIRED")
 blockers=[k for k,v in gates.items() if v["current_verdict"]!="PASS"]
 return {"schema":"oce.p159.occ1k.r9af.fl_b1_b12.gate_reconciliation.v1","milestone":"P159/OCC-1K-R9AF",
  "status":"RECONCILED_WITH_REMAINING_BLOCKERS" if blockers else "ALL_BLOCKER_GATES_PASS",
  "inputs":{"r4_sha256":sha(R4),"r9ae_sha256":sha(R9AE),"risk_registry_sha256":sha(RISK),"debt_registry_sha256":sha(DEBT)},
  "gates":gates,"pass_count":sum(v["current_verdict"]=="PASS" for v in gates.values()),
  "remaining_blockers":blockers,"open_root_risks":[x["risk_id"] for x in open_root],
  "open_lock_blocking_debts":[x["debt_id"] for x in open_blocking],
  "historical_r4_rewritten":False,"historical_risk_registry_rewritten":False,"historical_debt_registry_rewritten":False,
  "lock_ready":not blockers,"lock_granted":False,"p160b_opened":False,
  "authorization_created":False,"execution_performed":False,
  "next_required_step":"R9AG_FINAL_LOCK_EVIDENCE_BUNDLE_AND_CROSS_BINDING" if blockers else "R9_NEXT_META_ASSURANCE",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 r=reconcile();OUT.parent.mkdir(parents=True,exist_ok=True);b=(canon(r)+"\n").encode();OUT.write_bytes(b);return r,hashlib.sha256(b).hexdigest()
def main():
 r,h=write();print("P159_OCC1K_R9AF_FL_B1_B12_GATE_RECONCILIATION_COMPLETE")
 print("STATUS="+r["status"]);print("PASS_COUNT="+str(r["pass_count"])+"/12")
 for gid in sorted(r["gates"],key=lambda x:int(x.split("B")[1])): print(gid+"="+r["gates"][gid]["current_verdict"])
 print("REMAINING_BLOCKERS="+",".join(r["remaining_blockers"]))
 print("OPEN_ROOT_RISKS="+str(len(r["open_root_risks"])));print("OPEN_LOCK_BLOCKING_DEBTS="+str(len(r["open_lock_blocking_debts"])))
 print("HISTORICAL_R4_REWRITTEN=false");print("LOCK_READY="+str(r["lock_ready"]).lower());print("LOCK_GRANTED=false");print("P160B_OPENED=false")
 print("NEXT="+r["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
