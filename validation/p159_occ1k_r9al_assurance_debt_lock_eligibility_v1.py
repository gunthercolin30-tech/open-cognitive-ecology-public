from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
DEBT=ROOT/"validation_artifacts/p159/occ1k_r1/occ_assurance_debt_registry_v1.json"
AI=ROOT/"validation_artifacts/p159/occ1k_r9ai/fl_b12_fresh_global_nonregression_receipt_v1.json"
AJ=ROOT/"validation_artifacts/p159/occ1k_r9aj/final_lock_meta_crown_fl_a01_a20_v1.json"
AK=ROOT/"validation_artifacts/p159/occ1k_r9ak/mut_fl_meta_mutation_campaign_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9al/assurance_debt_lock_eligibility_v1.json"
DID="AD-FLI-EXHAUSTIVE-CERTIFICATION"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def evaluate(debt=None,ai=None,aj=None,ak=None):
 d=debt if debt is not None else load(DEBT);i=ai if ai is not None else load(AI);j=aj if aj is not None else load(AJ);k=ak if ak is not None else load(AK)
 debts={x["debt_id"]:x for x in d.get("items",[])}
 if DID not in debts: raise RuntimeError("EXPECTED_DEBT_MISSING")
 old=debts[DID]
 gates=(i.get("fl_b12")=="PASS")
 meta=(j.get("status")=="META_CROWN_FL_A01_A20_PASS" and j.get("passed")==20 and j.get("failed")==0)
 mut=(k.get("status")=="MUT_FL_PASS" and k.get("mroot_survived")==0 and k.get("mroot_inconclusive")==0 and not k.get("baseline_contaminated"))
 resolved=(old.get("status")=="OPEN" and old.get("blocks_lock") is True and gates and meta and mut)
 # This stage resolves the historical assurance debt by superseding evidence, but cannot establish LOCK_READY:
 # independent final-lock verification and governed transition remain separate canonical requirements.
 return {"schema":"oce.p159.occ1k.r9al.assurance_debt_lock_eligibility.v1","milestone":"P159/OCC-1K-R9AL",
 "status":"ASSURANCE_DEBT_RESOLVED_LOCK_ELIGIBILITY_PENDING_INDEPENDENT_VERIFIER" if resolved else "ASSURANCE_DEBT_UNRESOLVED",
 "historical_debt":{"debt_id":DID,"status":old.get("status"),"blocks_lock":old.get("blocks_lock"),"required_next":old.get("required_next"),
                    "registry_sha256":sha(DEBT),"rewritten":False},
 "superseding_debt_assessment":{"status":"RESOLVED_BY_SUPERSEDING_EVIDENCE" if resolved else "UNRESOLVED",
   "fl_b1_b12_complete":gates,"meta_crown_complete":meta,"mut_fl_complete":mut},
 "anchors":{"r9ai":sha(AI),"r9aj":sha(AJ),"r9ak":sha(AK)},
 "independent_final_lock_verifier_complete":False,"transition_receipt_complete":False,
 "lock_eligibility":"PENDING_INDEPENDENT_FINAL_LOCK_VERIFIER" if resolved else "BLOCKED",
 "lock_ready":False,"lock_granted":False,"p160b_opened":False,"authorization_created":False,"execution_performed":False,
 "next_required_step":"R9AM_INDEPENDENT_OCC_FINAL_LOCK_VERIFY" if resolved else "R9AL_ASSURANCE_REPAIR",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 x=evaluate();OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(canon(x)+"\n",encoding="utf-8");return x,sha(OUT)
def main():
 x,h=write();print("P159_OCC1K_R9AL_ASSURANCE_DEBT_LOCK_ELIGIBILITY_COMPLETE");print("STATUS="+x["status"])
 print("HISTORICAL_DEBT="+x["historical_debt"]["status"]);print("SUPERSEDING_DEBT="+x["superseding_debt_assessment"]["status"])
 print("FL_B1_B12_COMPLETE="+str(x["superseding_debt_assessment"]["fl_b1_b12_complete"]).lower())
 print("META_CROWN_COMPLETE="+str(x["superseding_debt_assessment"]["meta_crown_complete"]).lower())
 print("MUT_FL_COMPLETE="+str(x["superseding_debt_assessment"]["mut_fl_complete"]).lower())
 print("LOCK_ELIGIBILITY="+x["lock_eligibility"]);print("LOCK_READY=false");print("LOCK_GRANTED=false");print("P160B_OPENED=false")
 print("NEXT="+x["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
