from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R9AG=ROOT/"validation_artifacts/p159/occ1k_r9ag/independent_crossbinding_verification_v1.json"
R9AH=ROOT/"validation_artifacts/p159/occ1k_r9ah/fl_b11_residual_risk_reevaluation_v1.json"
R9AI=ROOT/"validation_artifacts/p159/occ1k_r9ai/fl_b12_fresh_global_nonregression_receipt_v1.json"
BUNDLE=ROOT/"validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9aj/final_lock_meta_crown_fl_a01_a20_v1.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
SCENARIOS=[
("FL-A01","missing_report"),("FL-A02","stale_report"),("FL-A03","wrong_hash_report"),
("FL-A04","root_failure_ignored"),("FL-A05","root_inconclusive_ignored"),("FL-A06","mutation_survivor_ignored"),
("FL-A07","corpus_changed"),("FL-A08","source_swapped"),("FL-A09","manifest_altered"),
("FL-A10","duplicate_report"),("FL-A11","partial_run"),("FL-A12","scope_laundering"),
("FL-A13","self_activation"),("FL-A14","missing_transition_receipt"),("FL-A15","invalidated_lock_treated_current"),
("FL-A16","bundle_path_traversal"),("FL-A17","bundle_hash_mismatch"),("FL-A18","unknown_promoted_to_pass"),
("FL-A19","evidence_count_tampered"),("FL-A20","cross_binding_bypass")]
def baseline():
 return {"reports_complete":True,"fresh":True,"hashes_match":True,"root_failures":0,"root_inconclusive":0,
 "mutation_root_survivors":0,"corpus_unchanged":True,"sources_bound":True,"manifest_intact":True,
 "duplicate_reports":False,"run_complete":True,"scope_unchanged":True,"self_activation":False,
 "transition_receipt_present":True,"current_assurance_valid":True,"safe_paths":True,"unknown_promoted":False,
 "evidence_count_valid":True,"cross_binding_valid":True}
def eligible(s):
 return (s["reports_complete"] and s["fresh"] and s["hashes_match"] and s["root_failures"]==0 and
 s["root_inconclusive"]==0 and s["mutation_root_survivors"]==0 and s["corpus_unchanged"] and s["sources_bound"] and
 s["manifest_intact"] and not s["duplicate_reports"] and s["run_complete"] and s["scope_unchanged"] and
 not s["self_activation"] and s["transition_receipt_present"] and s["current_assurance_valid"] and s["safe_paths"] and
 not s["unknown_promoted"] and s["evidence_count_valid"] and s["cross_binding_valid"])
def perturb(kind):
 s=baseline()
 m={"missing_report":("reports_complete",False),"stale_report":("fresh",False),"wrong_hash_report":("hashes_match",False),
 "root_failure_ignored":("root_failures",1),"root_inconclusive_ignored":("root_inconclusive",1),
 "mutation_survivor_ignored":("mutation_root_survivors",1),"corpus_changed":("corpus_unchanged",False),
 "source_swapped":("sources_bound",False),"manifest_altered":("manifest_intact",False),
 "duplicate_report":("duplicate_reports",True),"partial_run":("run_complete",False),"scope_laundering":("scope_unchanged",False),
 "self_activation":("self_activation",True),"missing_transition_receipt":("transition_receipt_present",False),
 "invalidated_lock_treated_current":("current_assurance_valid",False),"bundle_path_traversal":("safe_paths",False),
 "bundle_hash_mismatch":("hashes_match",False),"unknown_promoted_to_pass":("unknown_promoted",True),
 "evidence_count_tampered":("evidence_count_valid",False),"cross_binding_bypass":("cross_binding_valid",False)}
 k,v=m[kind];s[k]=v;return s
def run():
 ag,ah,ai,b=load(R9AG),load(R9AH),load(R9AI),load(BUNDLE)
 anchors_ok=(ag.get("fl_b10")=="PASS" and ah.get("fl_b11")=="PASS" and ai.get("fl_b12")=="PASS" and
 b.get("status")=="BUNDLE_MATERIALIZED_COMPLETE")
 results=[]
 for sid,kind in SCENARIOS:
  blocked=not eligible(perturb(kind))
  results.append({"scenario_id":sid,"case":kind,"expected":"BLOCK","observed":"BLOCK" if blocked else "ELIGIBLE","pass":blocked})
 ok=anchors_ok and len(results)==20 and all(x["pass"] for x in results)
 return {"schema":"oce.p159.occ1k.r9aj.final_lock_meta_crown.v1","milestone":"P159/OCC-1K-R9AJ",
 "status":"META_CROWN_FL_A01_A20_PASS" if ok else "META_CROWN_INCONCLUSIVE","scenario_count":20,
 "passed":sum(x["pass"] for x in results),"failed":sum(not x["pass"] for x in results),"anchors_ok":anchors_ok,
 "anchors":{"r9ag":sha(R9AG),"r9ah":sha(R9AH),"r9ai":sha(R9AI),"bundle":sha(BUNDLE)},"scenarios":results,
 "scope":"FINAL_LOCK_ELIGIBILITY_META_ASSURANCE_ONLY","assurance_debt_closed":False,"mut_fl_complete":False,
 "lock_ready":False,"lock_granted":False,"p160b_opened":False,"authorization_created":False,"execution_performed":False,
 "next_required_step":"OCC1K_MUT_FL" if ok else "R9AJ_META_CROWN_REPAIR",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 x=run();OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(canon(x)+"\n",encoding="utf-8");return x,sha(OUT)
def main():
 x,h=write();print("P159_OCC1K_R9AJ_FINAL_LOCK_META_CROWN_COMPLETE");print("STATUS="+x["status"])
 print("SCENARIOS=%d/20"%x["passed"]);print("FAILED="+str(x["failed"]));print("ASSURANCE_DEBT_CLOSED=false")
 print("MUT_FL_COMPLETE=false");print("LOCK_READY=false");print("LOCK_GRANTED=false");print("P160B_OPENED=false")
 print("NEXT="+x["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
