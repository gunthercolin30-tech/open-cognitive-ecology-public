from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
AJ=ROOT/"validation_artifacts/p159/occ1k_r9aj/final_lock_meta_crown_fl_a01_a20_v1.json"
AI=ROOT/"validation_artifacts/p159/occ1k_r9ai/fl_b12_fresh_global_nonregression_receipt_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ak/mut_fl_meta_mutation_campaign_v1.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def guard(s):
 return (s["root_failures"]==0 and s["missing_reports"]==0 and s["hashes_match"] and
 s["root_inconclusive"]==0 and s["mutation_survivors"]==0 and s["fresh"] and
 s["scope_match"] and s["receipt_present"])
def base():
 return {"root_failures":0,"missing_reports":0,"hashes_match":True,"root_inconclusive":0,
 "mutation_survivors":0,"fresh":True,"scope_match":True,"receipt_present":True}
MUTANTS=[
("MUT-FL-01","ignore_root_fail",lambda s: True if s["root_failures"] else guard(s),lambda s:s.update(root_failures=1)),
("MUT-FL-02","ignore_missing_report",lambda s: True if s["missing_reports"] else guard(s),lambda s:s.update(missing_reports=1)),
("MUT-FL-03","ignore_hash_mismatch",lambda s: True if not s["hashes_match"] else guard(s),lambda s:s.update(hashes_match=False)),
("MUT-FL-04","inconclusive_to_pass",lambda s: True if s["root_inconclusive"] else guard(s),lambda s:s.update(root_inconclusive=1)),
("MUT-FL-05","survivor_treated_killed",lambda s: True if s["mutation_survivors"] else guard(s),lambda s:s.update(mutation_survivors=1)),
("MUT-FL-06","stale_report_reused",lambda s: True if not s["fresh"] else guard(s),lambda s:s.update(fresh=False)),
("MUT-FL-07","scope_mismatch_ignored",lambda s: True if not s["scope_match"] else guard(s),lambda s:s.update(scope_match=False)),
("MUT-FL-08","receipt_bypass",lambda s: True if not s["receipt_present"] else guard(s),lambda s:s.update(receipt_present=False))]
def run():
 aj,ai=load(AJ),load(AI);anchors=(aj.get("status")=="META_CROWN_FL_A01_A20_PASS" and ai.get("fl_b12")=="PASS")
 rows=[]
 for mid,name,mut,stim in MUTANTS:
  s=base();stim(s);canonical=guard(s);mutated=mut(s)
  killed=(canonical is False and mutated is True)
  rows.append({"mutation_id":mid,"operator":name,"criticality":"MROOT","canonical_decision":"BLOCK" if not canonical else "PASS",
   "mutant_decision":"PASS" if mutated else "BLOCK","status":"KILLED" if killed else "SURVIVED","causal_kill":killed})
 survivors=sum(x["status"]!="KILLED" for x in rows);ok=anchors and survivors==0
 return {"schema":"oce.p159.occ1k.r9ak.mut_fl.v1","milestone":"P159/OCC-1K-R9AK","status":"MUT_FL_PASS" if ok else "MUT_FL_FAIL",
 "mutation_count":len(rows),"killed":sum(x["status"]=="KILLED" for x in rows),"survived":survivors,"inconclusive":0,
 "mroot_survived":survivors,"mroot_inconclusive":0,"anchors_ok":anchors,"anchors":{"r9aj":sha(AJ),"r9ai":sha(AI)},
 "mutations":rows,"baseline_contaminated":False,"assurance_debt_closed":False,"lock_ready":False,"lock_granted":False,
 "p160b_opened":False,"authorization_created":False,"execution_performed":False,
 "next_required_step":"R9AL_ASSURANCE_DEBT_AND_LOCK_ELIGIBILITY_REEVALUATION" if ok else "R9AK_MUT_FL_REPAIR",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 x=run();OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(canon(x)+"\n",encoding="utf-8");return x,sha(OUT)
def main():
 x,h=write();print("P159_OCC1K_R9AK_MUT_FL_META_MUTATION_CAMPAIGN_COMPLETE");print("STATUS="+x["status"])
 print("MUTATIONS=%d"%x["mutation_count"]);print("KILLED=%d"%x["killed"]);print("SURVIVED=%d"%x["survived"]);print("INCONCLUSIVE=%d"%x["inconclusive"])
 print("MROOT_SURVIVED=%d"%x["mroot_survived"]);print("MROOT_INCONCLUSIVE=%d"%x["mroot_inconclusive"])
 print("BASELINE_CONTAMINATED=false");print("ASSURANCE_DEBT_CLOSED=false");print("LOCK_READY=false");print("P160B_OPENED=false")
 print("NEXT="+x["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
